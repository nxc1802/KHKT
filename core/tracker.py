"""Module ByteTrack Tracker tích hợp Ultralytics.

Chạy song song Detection + Tracking:
- Model chính (Person + Trash) theo dõi qua ByteTrack.
- Model Thùng rác (Trash Bin) phát hiện và duy trì ID ổn định.
Trả về danh sách TrackedObject chuẩn hóa gồm 3 loại: 'person', 'trash', 'trash_bin'.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

from core.detector import Detector
from core.geometry import get_box_center, compute_iou


@dataclass
class TrackedObject:
    """Đối tượng được theo dõi trong 1 frame nhất định."""
    track_id: int
    class_name: str          # 'person', 'trash', hoặc 'trash_bin'
    confidence: float
    bbox: List[float]        # [x1, y1, x2, y2]
    center: Tuple[float, float]
    timestamp: float
    raw_class_id: int = -1
    raw_class_name: str = ""
    waste_category: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "bbox": [round(v, 2) for v in self.bbox],
            "center": [round(self.center[0], 2), round(self.center[1], 2)],
            "timestamp": round(self.timestamp, 3),
            "raw_class_name": self.raw_class_name
        }


class ByteTrackerAdapter:
    """Adapter tích hợp YOLOv8/YOLO11 cùng ByteTrack của Ultralytics và phát hiện Thùng rác."""

    def __init__(self,
                 detector: Detector,
                 tracker_config: str = "bytetrack.yaml",
                 track_high_thresh: float = 0.20,
                 person_min_confidence: float = 0.85,
                 max_persons: int = 2):
        self.detector = detector
        self.tracker_config = tracker_config
        self.track_high_thresh = track_high_thresh
        self.person_min_confidence = person_min_confidence
        self.max_persons = max_persons
        self._next_unassigned_id = -1000

        # Quản lý ID ổn định cho Thùng rác (Trash Bins) và Rác bổ trợ (World Trash)
        self._known_bins: List[Dict[str, Any]] = []
        self._next_bin_id = 501
        self._known_world_trash: List[Dict[str, Any]] = []
        self._next_world_trash_id = 701
        # Kính lúp quán tính cho các vật thể rác đang bay/rơi (tid -> {center, vx, vy, last_seen})
        self._active_trash_anchors: Dict[int, Dict[str, Any]] = {}

    @staticmethod
    def _merge_rois(rois: List[List[float]], iou_thresh: float = 0.30) -> List[List[float]]:
        """Gộp các vùng cắt ROI chồng lấn để tránh chạy YOLO trùng lặp."""
        merged: List[List[float]] = []
        for roi in rois:
            was_merged = False
            for idx, m in enumerate(merged):
                if compute_iou(roi, m) > iou_thresh:
                    merged[idx] = [min(m[0], roi[0]), min(m[1], roi[1]), max(m[2], roi[2]), max(m[3], roi[3])]
                    was_merged = True
                    break
            if not was_merged:
                merged.append(list(roi))
        return merged

    def track(self, frame: np.ndarray, timestamp: float, raw_frame: Optional[np.ndarray] = None) -> List[TrackedObject]:
        """Thực hiện phát hiện và tracking các đối tượng trong frame (Person, Trash, Trash Bin)."""
        tracked_objects: List[TrackedObject] = []

        # 1. Tracking đối tượng chuyển động (Person + Trash) qua ByteTrack
        results = self.detector.model.track(
            source=frame,
            persist=True,
            tracker=self.tracker_config,
            conf=self.detector.confidence_threshold,
            imgsz=self.detector.imgsz,
            device=self.detector.device,
            verbose=False
        )

        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes

            if boxes is not None and len(boxes) > 0:
                coords = boxes.xyxy.cpu().numpy()
                confs = boxes.conf.cpu().numpy()
                classes = boxes.cls.cpu().numpy().astype(int)
                names = result.names

                ids = None
                if boxes.id is not None:
                    ids = boxes.id.cpu().numpy().astype(int)

                for i in range(len(boxes)):
                    class_id = int(classes[i])
                    raw_name = names.get(class_id, str(class_id))
                    normalized_class = self.detector.map_class(class_id, raw_name)

                    if normalized_class is None:
                        continue

                    conf = float(confs[i])
                    bbox = [float(c) for c in coords[i]]
                    cx, cy = get_box_center(bbox)

                    if ids is not None and i < len(ids):
                        track_id = int(ids[i])
                    else:
                        track_id = self._next_unassigned_id
                        self._next_unassigned_id -= 1

                    obj = TrackedObject(
                        track_id=track_id,
                        class_name=normalized_class,
                        confidence=conf,
                        bbox=bbox,
                        center=(cx, cy),
                        timestamp=timestamp,
                        raw_class_id=class_id,
                        raw_class_name=raw_name
                    )
                    tracked_objects.append(obj)

        # Lọc chặt đối tượng Người: chỉ giữ conf >= person_min_confidence và tối đa max_persons người
        person_objs = [o for o in tracked_objects if o.class_name == "person" and o.confidence >= self.person_min_confidence]
        person_objs.sort(key=lambda o: o.confidence, reverse=True)
        person_objs = person_objs[:self.max_persons]
        non_person_objs = [o for o in tracked_objects if o.class_name != "person"]
        tracked_objects = person_objs + non_person_objs

        # 2. Phát hiện và duy trì ID Thùng rác (Trash Bin) + Rác bổ trợ từ YOLO-World
        if self.detector.bin_model is not None:
            bin_results = self.detector.bin_model(
                source=frame,
                conf=self.detector.bin_confidence,
                device=self.detector.device,
                verbose=False
            )

            if bin_results and len(bin_results) > 0:
                bin_boxes = bin_results[0].boxes
                if bin_boxes is not None and len(bin_boxes) > 0:
                    b_coords = bin_boxes.xyxy.cpu().numpy()
                    b_confs = bin_boxes.conf.cpu().numpy()
                    b_classes = bin_boxes.cls.cpu().numpy().astype(int)
                    b_names = bin_results[0].names
                    fh, fw = frame.shape[:2]
                    frame_area = float(max(1, fh * fw))

                    # Tách riêng thùng rác và vật thể rác bổ trợ
                    bin_only_indices = []
                    trash_supp_indices = []
                    for j in range(len(bin_boxes)):
                        raw_bname = b_names.get(int(b_classes[j]), "").lower()
                        if "bin" in raw_bname or "trash can" in raw_bname:
                            bin_only_indices.append(j)
                        else:
                            trash_supp_indices.append(j)

                    current_bin_bboxes = []
                    for j in bin_only_indices:
                        bbox = [float(c) for c in b_coords[j]]
                        conf = float(b_confs[j])
                        cx, cy = get_box_center(bbox)
                        current_bin_bboxes.append(bbox)

                        assigned_id = None
                        best_iou = 0.0
                        for known in self._known_bins:
                            iou = compute_iou(bbox, known["bbox"])
                            if iou > 0.3 and iou > best_iou:
                                best_iou = iou
                                assigned_id = known["id"]
                                known["bbox"] = bbox
                                known["last_seen"] = timestamp

                        if assigned_id is None:
                            assigned_id = self._next_bin_id
                            self._next_bin_id += 1
                            self._known_bins.append({
                                "id": assigned_id,
                                "bbox": bbox,
                                "last_seen": timestamp
                            })

                        tracked_objects.append(TrackedObject(
                            track_id=assigned_id,
                            class_name="trash_bin",
                            confidence=conf,
                            bbox=bbox,
                            center=(cx, cy),
                            timestamp=timestamp,
                            raw_class_id=999,
                            raw_class_name="trash_bin"
                        ))

                    existing_trash_bboxes = [o.bbox for o in tracked_objects if o.class_name == "trash"]
                    for j in trash_supp_indices:
                        bbox = [float(c) for c in b_coords[j]]
                        conf = float(b_confs[j])
                        area_ratio = ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / frame_area
                        if area_ratio > 0.12:
                            continue
                        if any(compute_iou(bbox, bb) >= 0.45 for bb in current_bin_bboxes):
                            continue
                        if any(compute_iou(bbox, tb) >= 0.25 for tb in existing_trash_bboxes):
                            continue

                        cx, cy = get_box_center(bbox)
                        assigned_tid = None
                        best_iou = 0.0
                        for kt in self._known_world_trash:
                            iou = compute_iou(bbox, kt["bbox"])
                            if iou > 0.25 and iou > best_iou:
                                best_iou = iou
                                assigned_tid = kt["id"]
                                kt["bbox"] = bbox
                                kt["last_seen"] = timestamp

                        if assigned_tid is None:
                            assigned_tid = self._next_world_trash_id
                            self._next_world_trash_id += 1
                            self._known_world_trash.append({
                                "id": assigned_tid,
                                "bbox": bbox,
                                "last_seen": timestamp
                            })

                        raw_bname = b_names.get(int(b_classes[j]), "trash")
                        tracked_objects.append(TrackedObject(
                            track_id=assigned_tid,
                            class_name="trash",
                            confidence=conf,
                            bbox=bbox,
                            center=(cx, cy),
                            timestamp=timestamp,
                            raw_class_id=int(b_classes[j]),
                            raw_class_name=raw_bname
                        ))

        # 3. Dual-Anchor 4K Magnifier: Cắt vùng ảnh gốc 4K quanh Người chính & Quỹ đạo Rác đang bay
        if raw_frame is not None and raw_frame.shape[:2] != frame.shape[:2]:
            proc_h, proc_w = frame.shape[:2]
            raw_h, raw_w = raw_frame.shape[:2]
            sx, sy = raw_w / float(proc_w), raw_h / float(proc_h)

            rois_proc: List[List[float]] = []
            # Anchor 1: Quanh các bạn học sinh chính (mở rộng 0.85x chiều ngang, kéo xuống dưới chân)
            for obj in tracked_objects:
                if obj.class_name == "person":
                    x1, y1, x2, y2 = obj.bbox
                    pw, ph = x2 - x1, y2 - y1
                    if ph >= 0.15 * proc_h:
                        pad_x, pad_y = 0.85 * pw, 0.35 * ph
                        rois_proc.append([
                            max(0.0, x1 - pad_x), max(0.0, y1 - pad_y * 0.4),
                            min(float(proc_w), x2 + pad_x), min(float(proc_h), y2 + pad_y)
                        ])

            # Anchor 2: Quanh vị trí dự đoán quán tính của rác đang bay/rơi
            half_win = 200.0  # tương đương ~400px trên 1080p = ~800px trên 4K
            for tid_a, anc in list(self._active_trash_anchors.items()):
                dt_a = timestamp - anc["last_seen"]
                if dt_a > 1.0:
                    del self._active_trash_anchors[tid_a]
                    continue
                px_pred = anc["center"][0] + anc["vx"] * dt_a
                py_pred = anc["center"][1] + anc["vy"] * dt_a
                rois_proc.append([
                    max(0.0, px_pred - half_win), max(0.0, py_pred - half_win),
                    min(float(proc_w), px_pred + half_win), min(float(proc_h), py_pred + half_win)
                ])

            merged_rois = self._merge_rois(rois_proc, iou_thresh=0.30)
            bin_bboxes = [o.bbox for o in tracked_objects if o.class_name == "trash_bin"]
            existing_trash = [o.bbox for o in tracked_objects if o.class_name == "trash"]

            for rx1, ry1, rx2, ry2 in merged_rois:
                cx1, cy1 = max(0, int(rx1 * sx)), max(0, int(ry1 * sy))
                cx2, cy2 = min(raw_w, int(rx2 * sx)), min(raw_h, int(ry2 * sy))
                if cx2 - cx1 < 64 or cy2 - cy1 < 64:
                    continue
                crop_4k = raw_frame[cy1:cy2, cx1:cx2]
                crop_candidates = []
                crop_res = self.detector.model(
                    crop_4k, conf=self.detector.confidence_threshold,
                    imgsz=640, device=self.detector.device, verbose=False
                )[0]
                if crop_res.boxes is not None:
                    for b in crop_res.boxes:
                        cid = int(b.cls[0].item())
                        rname = crop_res.names.get(cid, str(cid))
                        if self.detector.map_class(cid, rname) == "trash":
                            crop_candidates.append((b.xyxy[0].cpu().numpy(), float(b.conf[0].item()), cid, rname))

                # Bổ trợ thêm bằng yolov8s-worldv2.pt trên vùng cắt 4K để không sót chai/hộp ngoài sân nắng
                if self.detector.bin_model is not None:
                    w_res = self.detector.bin_model(
                        crop_4k, conf=0.14, imgsz=640, device=self.detector.device, verbose=False
                    )[0]
                    if w_res.boxes is not None:
                        for b in w_res.boxes:
                            cid = int(b.cls[0].item())
                            rname = w_res.names.get(cid, "").lower()
                            if "bin" in rname or "trash can" in rname:
                                continue
                            crop_candidates.append((b.xyxy[0].cpu().numpy(), float(b.conf[0].item()), cid, rname))

                for xyxy_c, conf_c, cid, rname in crop_candidates:
                    bx1, by1, bx2, by2 = xyxy_c
                    gx1 = (bx1 + cx1) / sx
                    gy1 = (by1 + cy1) / sy
                    gx2 = (bx2 + cx1) / sx
                    gy2 = (by2 + cy1) / sy
                    gbbox = [float(gx1), float(gy1), float(gx2), float(gy2)]

                    if any(compute_iou(gbbox, bb) > 0.40 for bb in bin_bboxes):
                        continue
                    if any(compute_iou(gbbox, tb) > 0.35 for tb in existing_trash):
                        continue

                    existing_trash.append(gbbox)
                    gcx, gcy = get_box_center(gbbox)
                    assigned_tid = None
                    best_iou = 0.0
                    for kt in self._known_world_trash:
                        iou = compute_iou(gbbox, kt["bbox"])
                        if iou > 0.20 and iou > best_iou:
                            best_iou = iou
                            assigned_tid = kt["id"]
                            kt["bbox"] = gbbox
                            kt["last_seen"] = timestamp
                    if assigned_tid is None:
                        assigned_tid = self._next_world_trash_id
                        self._next_world_trash_id += 1
                        self._known_world_trash.append({"id": assigned_tid, "bbox": gbbox, "last_seen": timestamp})

                    tracked_objects.append(TrackedObject(
                        track_id=assigned_tid,
                        class_name="trash",
                        confidence=conf_c,
                        bbox=gbbox,
                        center=(gcx, gcy),
                        timestamp=timestamp,
                        raw_class_id=cid,
                        raw_class_name=rname
                    ))

        # Cập nhật vận tốc quán tính cho các track rác đang hoạt động
        for obj in tracked_objects:
            if obj.class_name == "trash":
                prev = self._active_trash_anchors.get(obj.track_id)
                vx, vy = 0.0, 0.0
                if prev is not None:
                    dt_p = timestamp - prev["last_seen"]
                    if dt_p > 1e-4:
                        vx = (obj.center[0] - prev["center"][0]) / dt_p
                        vy = (obj.center[1] - prev["center"][1]) / dt_p
                self._active_trash_anchors[obj.track_id] = {
                    "center": obj.center, "vx": vx, "vy": vy, "last_seen": timestamp
                }

        return tracked_objects

    def reset(self):
        """Reset bộ nhớ tracker khi chuyển video mới."""
        self._next_unassigned_id = -1000
        self._known_bins.clear()
        self._next_bin_id = 501
        self._known_world_trash.clear()
        self._next_world_trash_id = 701
        self._active_trash_anchors.clear()
        try:
            if hasattr(self.detector.model, 'predictor') and self.detector.model.predictor is not None:
                if hasattr(self.detector.model.predictor, 'trackers'):
                    self.detector.model.predictor.trackers = []
        except Exception:
            pass
