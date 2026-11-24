"""Module điều phối toàn bộ Pipeline xử lý video (Video Processor).

Thực hiện chuỗi xử lý khép kín:
VideoReader -> YOLO+ByteTrack+BinDetector -> History -> Spatial/Temporal Association -> FSM Behavior -> Events & Evidence -> Visualizer -> VideoWriter
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
import yaml
from ultralytics import YOLO

from core.detector import Detector
from core.tracker import ByteTrackerAdapter
from core.history import TrackHistoryManager
from core.association import AssociationAnalyzer
from core.behavior import BehaviorEngine
from core.events import EventManager
from core.geometry import compute_iou
from utils.visualizer import Visualizer


class VideoProcessor:
    """Điều phối toàn bộ quy trình phát hiện hành vi xả rác từ video đầu vào."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config(config_path)

        # 1. Khởi tạo Detector & Tracker
        model_cfg = self.config.get("model", {})
        bin_cfg = self.config.get("bin_detection", {})

        self.detector = Detector(
            model_path=model_cfg.get("path", "weights/best.pt"),
            confidence_threshold=model_cfg.get("confidence", 0.20),
            imgsz=model_cfg.get("imgsz", 640),
            device=model_cfg.get("device", "auto"),
            class_mode=model_cfg.get("class_mode", "custom"),
            trash_classes_coco=model_cfg.get("trash_classes_coco"),
            enable_bin_detection=bin_cfg.get("enabled", True),
            bin_model_path=bin_cfg.get("model_path", "yolov8s-worldv2.pt"),
            bin_classes=bin_cfg.get("classes", ["waste bin", "trash can"]),
            bin_confidence=bin_cfg.get("confidence", 0.30)
        )

        track_cfg = self.config.get("tracking", {})
        self.tracker = ByteTrackerAdapter(
            detector=self.detector,
            tracker_config=track_cfg.get("tracker", "bytetrack.yaml"),
            track_high_thresh=track_cfg.get("track_high_thresh", 0.20),
            person_min_confidence=model_cfg.get("person_min_confidence", 0.85),
            max_persons=model_cfg.get("max_persons", 2)
        )

        # 2. Khởi tạo History Manager
        hist_cfg = self.config.get("history", {})
        self.history = TrackHistoryManager(
            window_seconds=hist_cfg.get("window_seconds", 3.5),
            max_missing_seconds=hist_cfg.get("max_missing_seconds", 1.2),
            smoothing_alpha=hist_cfg.get("smoothing_alpha", 0.6)
        )

        # 3. Khởi tạo Spatial & Association Analyzer
        spat_cfg = self.config.get("spatial", {})
        behav_cfg = self.config.get("behavior", {})
        self.association = AssociationAnalyzer(
            near_distance_ratio=spat_cfg.get("near_distance_ratio", 0.85),
            separation_distance_ratio=spat_cfg.get("separation_distance_ratio", 0.95),
            min_association_seconds=behav_cfg.get("min_association_seconds", 0.3),
            pre_existing_buffer_sec=behav_cfg.get("pre_existing_buffer_sec", 1.5),
            spatial_backtrack_sec=spat_cfg.get("spatial_backtrack_sec", 2.5),
            bin_iou_threshold=bin_cfg.get("bin_iou_threshold", 0.35)
        )

        # 4. Khởi tạo Behavior Engine
        self.behavior = BehaviorEngine(
            separation_distance_ratio=spat_cfg.get("separation_distance_ratio", 0.95),
            min_stationary_seconds=behav_cfg.get("min_stationary_seconds", 0.6),
            event_cooldown_seconds=behav_cfg.get("event_cooldown_seconds", 3.0)
        )

        # 5. Khởi tạo Event Manager
        self.event_manager = EventManager(
            output_events_dir="outputs/events",
            output_evidence_dir="outputs/evidence",
            cooldown_seconds=behav_cfg.get("event_cooldown_seconds", 3.0)
        )

        # 6. Khởi tạo Visualizer
        out_cfg = self.config.get("output", {})
        self.visualizer = Visualizer(
            draw_boxes=out_cfg.get("draw_boxes", True),
            draw_trajectories=out_cfg.get("draw_trajectories", True),
            draw_status_panel=out_cfg.get("draw_status_panel", True)
        )

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Đọc cấu hình từ file YAML."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found at: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def reset(self):
        """Reset trạng thái toàn bộ module trước khi xử lý video mới."""
        self.tracker.reset()
        self.history.reset()
        self.association.reset()
        self.behavior.reset()
        self.event_manager.reset()

    def process_video(self,
                      video_path: str,
                      output_video_path: Optional[str] = None,
                      events_json_path: Optional[str] = None,
                      show_progress: bool = True) -> Dict[str, Any]:
        """Chạy pipeline phát hiện trên một file video."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Input video not found: {video_path}")

        self.reset()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video file: {video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Tối ưu video 4K & 60fps: chuẩn hóa về <= 1920x1080 và ~30 FPS hiệu dụng
        proc_w, proc_h = width, height
        if width > 1920:
            scale = 1920.0 / width
            proc_w = 1920
            proc_h = int(round(height * scale))
        frame_step = 2 if fps >= 50.0 else 1
        eff_fps = fps / frame_step

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        out_cfg = self.config.get("output", {})
        save_video = out_cfg.get("save_video", True)
        save_events = out_cfg.get("save_events", True)
        save_evidence = out_cfg.get("save_evidence", True)

        if output_video_path is None:
            output_video_path = os.path.join("outputs/videos", f"{base_name}_annotated.mp4")
        if events_json_path is None:
            events_json_path = os.path.join("outputs/events", f"{base_name}_events.json")

        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        os.makedirs(os.path.dirname(events_json_path), exist_ok=True)

        self.event_manager.set_prefix(base_name)

        writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_video_path, fourcc, eff_fps, (proc_w, proc_h))

        print(f"\n[VideoProcessor] Bắt đầu xử lý video: {video_path}")
        print(f"  > Độ phân giải gốc: {width}x{height} -> Xử lý: {proc_w}x{proc_h} | FPS hiệu dụng: {eff_fps:.1f} | Tổng frame: {total_frames}")

        frame_idx = 0
        start_time = time.time()
        last_progress_log = 0.0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % frame_step != 0:
                    frame_idx += 1
                    continue

                raw_frame = frame
                if proc_w != width or proc_h != height:
                    frame = cv2.resize(raw_frame, (proc_w, proc_h))

                timestamp = frame_idx / fps

                # 1. Tracking: YOLO + ByteTrack + Bin Detector + Dual-Anchor 4K Magnifier
                if raw_frame.shape[:2] != frame.shape[:2]:
                    objects = self.tracker.track(frame, timestamp, raw_frame=raw_frame)
                else:
                    objects = self.tracker.track(frame, timestamp)

                # 2. History update
                self.history.update(objects, timestamp)

                # 3. Spatial & Association Analysis (Person - Trash - Trash Bin)
                relations = self.association.analyze(objects, self.history, timestamp, (proc_h, proc_w))

                # 4. Behavior Engine FSM update (kèm frame để lưu Thẻ sự kiện nhiều ảnh)
                raw_events = self.behavior.update(
                    objects, relations, self.history, timestamp, (proc_h, proc_w), current_frame=frame
                )

                # 5. Filter duplicates & record events
                confirmed_events = self.event_manager.filter_and_record(raw_events, frame, save_evidence=save_evidence)

                for evt in confirmed_events:
                    if evt.event_type == "POSSIBLE_LITTERING":
                        msg = f"[{evt.decision_level}] Nguoi #{evt.person_id} -> Rac #{evt.trash_id}"
                        if evt.nearest_bin_id:
                            msg += f" (Gan Thung rac #{evt.nearest_bin_id})"
                        self.visualizer.trigger_alert_banner(msg, timestamp, duration=3.0)
                        print(f"  [!] [{timestamp:05.2f}s] {msg}")
                    elif evt.event_type == "CORRECT_DISPOSAL":
                        msg = f"BO RAC DUNG NOI: Nguoi #{evt.person_id} -> Rac #{evt.trash_id}"
                        self.visualizer.trigger_alert_banner(msg, timestamp, duration=2.5)
                        print(f"  [OK] [{timestamp:05.2f}s] {msg}")
                    elif evt.event_type == "UNCERTAIN":
                        msg = f"[{evt.decision_level}] Rac #{evt.trash_id} khong ro nguon goc"
                        print(f"  [?] [{timestamp:05.2f}s] {msg}")

                # 6. Render visualization overlay
                if save_video and writer is not None:
                    vis_frame = self.visualizer.draw(
                        frame=frame,
                        objects=objects,
                        relations=relations,
                        history=self.history,
                        behavior_engine=self.behavior,
                        timestamp=timestamp,
                        fps=fps
                    )
                    writer.write(vis_frame)

                frame_idx += 1

                now = time.time()
                if show_progress and (now - last_progress_log > 1.5 or frame_idx == total_frames):
                    last_progress_log = now
                    pct = (frame_idx / total_frames * 100) if total_frames > 0 else 0
                    elapsed = now - start_time
                    fps_proc = frame_idx / elapsed if elapsed > 0 else 0
                    print(f"  Processing: Frame {frame_idx}/{total_frames} ({pct:.1f}%) — {fps_proc:.1f} fps")

        finally:
            cap.release()
            if writer is not None:
                writer.release()

        # 7. Xuất file kết quả JSON
        if save_events:
            self.event_manager.export_json(events_json_path)

        total_elapsed = time.time() - start_time
        summary = {
            "input_video": video_path,
            "output_video": output_video_path if save_video else None,
            "events_json": events_json_path if save_events else None,
            "total_frames_processed": frame_idx,
            "elapsed_seconds": round(total_elapsed, 2),
            "processing_fps": round(frame_idx / total_elapsed, 2) if total_elapsed > 0 else 0,
            "total_events_detected": len(self.event_manager.confirmed_events)
        }

        print(f"[VideoProcessor] Hoàn tất xử lý video trong {total_elapsed:.2f}s (FPS: {summary['processing_fps']})")
        print(f"  > Đã phát hiện tổng cộng: {summary['total_events_detected']} sự kiện.")
        return summary

    def process_waste_sorting_video(self,
                                    video_path: str,
                                    bin_zones: Optional[List[Dict[str, Any]]] = None,
                                    output_video_path: Optional[str] = None,
                                    events_json_path: Optional[str] = None,
                                    show_progress: bool = True) -> Dict[str, Any]:
        """Task 2: Phát hiện, phân loại rác (Tái chế / Không tái chế) và đánh giá bỏ đúng ngăn thùng."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Input video not found: {video_path}")

        ws_cfg = self.config.get("waste_sorting", {})
        rec_prompts = ws_cfg.get("recyclable_prompts", [])
        nonrec_prompts = ws_cfg.get("non_recyclable_prompts", [])
        rec_set, nonrec_set = set(rec_prompts), set(nonrec_prompts)

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        if bin_zones is None:
            preset_key = ws_cfg.get("video_presets", {}).get(base_name)
            if preset_key:
                bin_zones = ws_cfg.get("presets", {}).get(preset_key, [])
        if not bin_zones:
            raise ValueError(f"Chưa cấu hình bin_zones cho video '{base_name}'")

        if output_video_path is None:
            output_video_path = os.path.join("outputs/videos", f"{base_name}_task2_annotated.mp4")
        if events_json_path is None:
            events_json_path = os.path.join("outputs/events", f"{base_name}_task2_events.json")
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        os.makedirs(os.path.dirname(events_json_path), exist_ok=True)
        os.makedirs("outputs/evidence", exist_ok=True)

        if not hasattr(self, "_ws_world_model") or self._ws_world_model is None:
            self._ws_world_model = YOLO(ws_cfg.get("model_path", "yolov8s-worldv2.pt"))
            self._ws_world_model.set_classes(["person"] + rec_prompts + nonrec_prompts)
        world_model = self._ws_world_model
        if hasattr(world_model, "predictor") and world_model.predictor is not None:
            if hasattr(world_model.predictor, "trackers"):
                world_model.predictor.trackers = []

        cap = cv2.VideoCapture(video_path)
        orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = 2 if orig_fps >= 50.0 else 1
        eff_fps = orig_fps / step
        proc_w, proc_h = 1280, 720
        frame_area = float(proc_w * proc_h)
        max_area_ratio = ws_cfg.get("max_area_ratio", 0.22)
        disappear_sec = ws_cfg.get("disappear_confirm_sec", 0.35)
        min_vote = ws_cfg.get("min_vote_score", 0.15)
        ws_conf = ws_cfg.get("confidence", 0.10)
        ws_imgsz = ws_cfg.get("imgsz", 1280)
        ws_cooldown = ws_cfg.get("event_cooldown_sec", 1.5)

        zones_px = []
        for z in bin_zones:
            nx1, ny1, nx2, ny2 = z["coords"]
            drop_y1 = max(0.0, (ny1 - 0.10) * proc_h)
            zones_px.append({
                **z,
                "bbox_px": [nx1 * proc_w, ny1 * proc_h, nx2 * proc_w, ny2 * proc_h],
                "drop_px": [nx1 * proc_w, drop_y1, nx2 * proc_w, ny2 * proc_h],
            })
        union_bin_box = [
            min(z["bbox_px"][0] for z in zones_px),
            min(z["bbox_px"][1] for z in zones_px),
            max(z["bbox_px"][2] for z in zones_px),
            max(z["bbox_px"][3] for z in zones_px),
        ]
        union_bin_w = max(1.0, union_bin_box[2] - union_bin_box[0])

        writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*"mp4v"), eff_fps, (proc_w, proc_h))
        tracks: Dict[int, Dict[str, Any]] = {}
        events: List[Dict[str, Any]] = []
        last_bin_cat_time: Dict[Tuple[str, str], float] = {}
        event_counter = 1
        banner_text, banner_color, banner_until = "", (0, 180, 0), -1.0

        t0 = time.time()
        frame_idx = 0
        processed = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % step != 0:
                    frame_idx += 1
                    continue

                timestamp = frame_idx / orig_fps
                frame_proc = cv2.resize(frame, (proc_w, proc_h))

                results = world_model.track(
                    frame_proc, persist=True, tracker="bytetrack.yaml",
                    conf=ws_conf, imgsz=ws_imgsz, device=self.detector.device, verbose=False
                )
                best_res = self.detector.model(
                    frame_proc, conf=self.detector.confidence_threshold,
                    imgsz=ws_imgsz, device=self.detector.device, verbose=False
                )[0]

                active_waste_ids = set()
                person_candidates: List[Tuple[float, List[float]]] = []
                p_min_conf = self.config.get("model", {}).get("person_min_confidence", 0.85)
                p_max_cnt = self.config.get("model", {}).get("max_persons", 2)

                # 1. Lấy danh sách Người chính từ weights/best.pt (conf >= 0.85, tối đa 2 người)
                if best_res.boxes is not None:
                    for b in best_res.boxes:
                        if int(b.cls[0].item()) == 0:
                            p_conf = float(b.conf[0].item())
                            pb = [float(v) for v in b.xyxy[0].cpu().numpy()]
                            if p_conf >= p_min_conf and (pb[3] - pb[1]) >= 0.15 * proc_h:
                                person_candidates.append((p_conf, pb))
                person_candidates.sort(key=lambda x: x[0], reverse=True)
                person_bboxes: List[List[float]] = [pb for _, pb in person_candidates[:p_max_cnt]]

                if results and results[0].boxes is not None:
                    boxes = results[0].boxes
                    xyxy_l = boxes.xyxy.cpu().numpy()
                    cls_l = boxes.cls.cpu().numpy().astype(int)
                    conf_l = boxes.conf.cpu().numpy()
                    id_l = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else [-1] * len(cls_l)

                    for xyxy, cls_id, conf, tid_raw in zip(xyxy_l, cls_l, conf_l, id_l):
                        tid = int(tid_raw)
                        raw_name = world_model.names.get(int(cls_id), "")
                        bbox = [float(v) for v in xyxy]
                        if raw_name == "person":
                            continue
                        if raw_name in rec_set:
                            cat = "recyclable"
                        elif raw_name in nonrec_set:
                            cat = "non_recyclable"
                        else:
                            continue

                        area_ratio = ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / frame_area
                        box_w = bbox[2] - bbox[0]
                        if tid < 0 or area_ratio > max_area_ratio:
                            continue
                        # Union-Bin Mask: loại bỏ hoàn toàn box bao trùm lên thân cụm thùng rác
                        if compute_iou(bbox, union_bin_box) > 0.35 or box_w > 0.60 * union_bin_w:
                            continue
                        if any(compute_iou(bbox, z["bbox_px"]) > 0.45 for z in zones_px):
                            continue

                        cx, cy = (bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0
                        active_waste_ids.add(tid)
                        if tid not in tracks:
                            tracks[tid] = {
                                "first_seen": timestamp, "last_seen": timestamp,
                                "bbox": bbox, "center": (cx, cy),
                                "scores": {"recyclable": 0.0, "non_recyclable": 0.0},
                                "best_label": raw_name, "best_conf": float(conf),
                                "bin_id": None, "bin_type": None,
                                "snapshot": None, "person_bbox": None,
                                "evaluated": False, "obs": 0,
                            }
                        st = tracks[tid]
                        st["last_seen"] = timestamp
                        st["bbox"] = bbox
                        st["center"] = (cx, cy)
                        st["obs"] += 1
                        st["scores"][cat] += float(conf)
                        if float(conf) >= st["best_conf"]:
                            st["best_conf"] = float(conf)
                            st["best_label"] = raw_name

                        # Chọn người gần vật thể rác nhất
                        nearest_p = None
                        if person_bboxes:
                            nearest_p = min(
                                person_bboxes,
                                key=lambda pb: ((pb[0] + pb[2]) / 2.0 - cx) ** 2 + ((pb[1] + pb[3]) / 2.0 - cy) ** 2
                            )

                        for z in zones_px:
                            dx1, dy1, dx2, dy2 = z["drop_px"]
                            if (dx1 <= cx <= dx2 and dy1 <= cy <= dy2) or compute_iou(bbox, z["drop_px"]) >= 0.12:
                                st["bin_id"] = z["bin_id"]
                                st["bin_type"] = z["bin_type"]
                                st["snapshot"] = frame_proc.copy()
                                st["person_bbox"] = nearest_p
                                break

                for tid, st in list(tracks.items()):
                    if st["evaluated"]:
                        continue
                    if tid not in active_waste_ids and st["bin_id"] is not None:
                        if (timestamp - st["last_seen"]) >= disappear_sec and st["obs"] >= 1:
                            st["evaluated"] = True
                            rec_s, nonrec_s = st["scores"]["recyclable"], st["scores"]["non_recyclable"]
                            tot_s = rec_s + nonrec_s
                            if max(rec_s, nonrec_s) < min_vote or tot_s <= 0:
                                wcat, cconf = "unknown", 0.0
                                evt_type, is_ok = "DISPOSAL_UNVERIFIED", None
                                msg = f"Chua xac minh loai rac: Vat the #{tid} bo vao {st['bin_id']}"
                                bcol = (140, 140, 140)
                            else:
                                wcat = "recyclable" if rec_s >= nonrec_s else "non_recyclable"
                                cconf = round(max(rec_s, nonrec_s) / tot_s, 2)
                                # Chống nhân bản sự kiện khi ByteTrack nhảy ID trên cùng 1 món đồ
                                cd_key = (st["bin_id"], st["best_label"])
                                prev_t = last_bin_cat_time.get(cd_key)
                                if prev_t is not None and (st["last_seen"] - prev_t) < ws_cooldown:
                                    continue
                                last_bin_cat_time[cd_key] = st["last_seen"]

                                if wcat == st["bin_type"]:
                                    evt_type, is_ok = "CORRECT_SORTING", True
                                    msg = f"DUNG NGAN: Bo {wcat} ({st['best_label']}) vao {st['bin_id']}"
                                    bcol = (0, 160, 0)
                                else:
                                    evt_type, is_ok = "WRONG_BIN_DISPOSAL", False
                                    msg = f"SAI NGAN: Bo {wcat} ({st['best_label']}) vao {st['bin_id']} ({st['bin_type']})"
                                    bcol = (0, 100, 230)

                            evt_id = f"EVT_{event_counter:04d}"
                            event_counter += 1
                            ev_img = f"{base_name}_task2_{evt_id}.jpg"
                            snap = EventManager._anonymize_and_draw_boxes(
                                st["snapshot"] if st["snapshot"] is not None else frame_proc,
                                st["person_bbox"], st["bbox"], None, tid, trash_color=bcol
                            )
                            cv2.rectangle(snap, (0, 0), (proc_w, 46), bcol, -1)
                            cv2.putText(snap, f"{evt_id} [{evt_type}] at {st['last_seen']:.2f}s | {st['best_label']}",
                                        (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
                            cv2.imwrite(os.path.join("outputs/evidence", ev_img), snap)

                            events.append({
                                "event_id": evt_id, "event_type": evt_type, "is_correct_place": is_ok,
                                "timestamp": round(st["last_seen"], 2), "trash_id": tid,
                                "waste_category": wcat, "waste_raw_label": st["best_label"],
                                "waste_category_confidence": cconf,
                                "target_bin_id": st["bin_id"], "target_bin_type": st["bin_type"],
                                "evidence": ["tracked_waste", "entered_bin_zone", "disappeared_in_bin"],
                                "status_message": msg, "evidence_image": ev_img,
                            })
                            banner_text, banner_color, banner_until = msg, bcol, timestamp + 3.0
                            print(f"  [{base_name}] [{st['last_seen']:05.2f}s] {msg}")

                vis = frame_proc.copy()
                overlay = vis.copy()
                for z in zones_px:
                    zx1, zy1, zx2, zy2 = [int(v) for v in z["bbox_px"]]
                    zcol = (0, 200, 0) if z["bin_type"] == "recyclable" else (0, 200, 255)
                    cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), zcol, -1)
                    cv2.rectangle(vis, (zx1, zy1), (zx2, zy2), zcol, 3)
                    cv2.putText(vis, f"[{z['label']}]", (zx1 + 8, max(28, zy1 + 28)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.72, zcol, 2, cv2.LINE_AA)
                cv2.addWeighted(overlay, 0.15, vis, 0.85, 0, vis)

                for pb in person_bboxes:
                    px1, py1, px2, py2 = [int(v) for v in pb]
                    cv2.rectangle(vis, (px1, py1), (px2, py2), (0, 140, 255), 2)
                    cv2.putText(vis, "Person", (px1, max(20, py1 - 8)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 140, 255), 2, cv2.LINE_AA)

                for tid in active_waste_ids:
                    st = tracks[tid]
                    wcat = "recyclable" if st["scores"]["recyclable"] >= st["scores"]["non_recyclable"] else "non_recyclable"
                    bx1, by1, bx2, by2 = [int(v) for v in st["bbox"]]
                    col = (0, 220, 0) if wcat == "recyclable" else (0, 165, 255)
                    cv2.rectangle(vis, (bx1, by1), (bx2, by2), col, 2)
                    cv2.putText(vis, f"#{tid} {wcat}:{st['best_label']}", (bx1, max(20, by1 - 8)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 2, cv2.LINE_AA)

                c_ok = sum(1 for e in events if e["event_type"] == "CORRECT_SORTING")
                c_wrong = sum(1 for e in events if e["event_type"] == "WRONG_BIN_DISPOSAL")
                cv2.rectangle(vis, (10, 10), (440, 48), (20, 20, 20), -1)
                cv2.putText(vis, f"TASK 2 | Dung ngan: {c_ok} | Sai ngan: {c_wrong} | t={timestamp:.1f}s",
                            (18, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
                if timestamp <= banner_until and banner_text:
                    cv2.rectangle(vis, (0, proc_h - 48), (proc_w, proc_h), banner_color, -1)
                    cv2.putText(vis, banner_text, (16, proc_h - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)

                writer.write(vis)
                processed += 1
                frame_idx += 1
        finally:
            cap.release()
            writer.release()

        c_ok = sum(1 for e in events if e["event_type"] == "CORRECT_SORTING")
        c_wrong = sum(1 for e in events if e["event_type"] == "WRONG_BIN_DISPOSAL")
        c_unv = sum(1 for e in events if e["event_type"] == "DISPOSAL_UNVERIFIED")
        denom = c_ok + c_wrong
        acc = round((c_ok / denom) * 100.0, 1) if denom > 0 else None
        elapsed = time.time() - t0
        fps_proc = round(processed / elapsed, 2) if elapsed > 0 else 0

        report = {
            "video": video_path,
            "summary": {
                "total_events": len(events),
                "correct_sorting_count": c_ok,
                "wrong_bin_disposal_count": c_wrong,
                "disposal_unverified_count": c_unv,
                "sorting_accuracy_percent": acc,
                "processing_fps": fps_proc,
                "total_frames_processed": processed,
            },
            "events": events,
        }
        with open(events_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[Task 2 Done] {base_name}.MOV: {processed} frames in {elapsed:.1f}s ({fps_proc} FPS) | Events={len(events)} (Dung={c_ok}, Sai={c_wrong})")
        return report
