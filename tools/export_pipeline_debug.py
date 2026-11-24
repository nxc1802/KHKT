"""Xuất đầy đủ 7 ảnh Input/Output trung gian của từng Module để kiểm tra trực quan:
1. 01_raw_4k_input.jpg: Ảnh gốc 4K (3840x2160) đầu vào.
2. 02_resized_global_input.jpg: Ảnh sau khi resize đưa vào YOLO Global Scan.
3. 03_global_yolo_output.jpg: Output Global Detection (tối đa 2 Người >= 0.85 + Thùng rác).
4. 04_4k_roi_crop_input.jpg: Ảnh cắt trực tiếp từ khung gốc 4K (Kính lúp 4K quanh Người/Rác).
5. 05_4k_roi_yolo_output.jpg: Output nhận diện/phân loại rác trên ảnh cắt 4K.
6. 06_projected_global_output.jpg: Ảnh sau khi ánh xạ tọa độ từ Kính lúp 4K về toàn khung hình.
7. 07_final_visualizer_output.jpg: Ảnh kết xuất cuối cùng (làm mờ mặt + nhãn trạng thái).
"""

import os
import sys
import cv2
import numpy as np
from ultralytics import YOLO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.video_processor import VideoProcessor
from core.events import EventManager
from core.geometry import compute_iou


def export_debug_for_video(video_path: str, target_sec: float, out_dir: str, is_task2: bool = False):
    os.makedirs(out_dir, exist_ok=True)
    proc = VideoProcessor(config_path="config.yaml")

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 60.0
    fidx = int(target_sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, fidx)
    ret, raw_4k = cap.read()
    cap.release()
    if not ret:
        print(f"[LỖI] Không đọc được frame tại {target_sec}s từ {video_path}")
        return

    # 1. Ảnh gốc 4K
    cv2.imwrite(os.path.join(out_dir, "01_raw_4k_input.jpg"), raw_4k)

    # 2. Ảnh sau khi resize đưa vào YOLO Global Scan
    proc_w, proc_h = (1280, 720) if is_task2 else (1920, 1080)
    resized = cv2.resize(raw_4k, (proc_w, proc_h))
    cv2.imwrite(os.path.join(out_dir, "02_resized_global_input.jpg"), resized)

    # 3. Output Global Detection (lọc Người >= 0.85, tối đa 2 người + Thùng rác)
    global_vis = resized.copy()
    res_best = proc.detector.model(
        resized, conf=proc.detector.confidence_threshold,
        imgsz=proc.detector.imgsz, device=proc.detector.device, verbose=False
    )[0]

    persons = []
    if res_best.boxes is not None:
        for b in res_best.boxes:
            if int(b.cls[0].item()) == 0:
                c = float(b.conf[0].item())
                if c >= 0.85:
                    persons.append((c, [float(v) for v in b.xyxy[0].cpu().numpy()]))
    persons.sort(key=lambda x: x[0], reverse=True)
    persons = persons[:2]

    for c, pb in persons:
        x1, y1, x2, y2 = [int(v) for v in pb]
        cv2.rectangle(global_vis, (x1, y1), (x2, y2), (0, 140, 255), 3)
        cv2.putText(global_vis, f"Person {c:.2f}", (x1, max(25, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)

    bin_boxes = []
    if not is_task2 and proc.detector.bin_model is not None:
        res_bin = proc.detector.bin_model(resized, conf=0.25, device=proc.detector.device, verbose=False)[0]
        if res_bin.boxes is not None:
            for b in res_bin.boxes:
                rname = res_bin.names.get(int(b.cls[0].item()), "").lower()
                if "bin" in rname or "trash can" in rname:
                    bb = [float(v) for v in b.xyxy[0].cpu().numpy()]
                    bin_boxes.append(bb)
                    bx1, by1, bx2, by2 = [int(v) for v in bb]
                    cv2.rectangle(global_vis, (bx1, by1), (bx2, by2), (255, 180, 0), 3)
                    cv2.putText(global_vis, "Trash Bin", (bx1, max(25, by1 - 8)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 180, 0), 2)
    cv2.imwrite(os.path.join(out_dir, "03_global_yolo_output.jpg"), global_vis)

    # 4. Ảnh cắt trực tiếp từ khung hình gốc 4K (Kính lúp 4K quanh Người chính)
    raw_h, raw_w = raw_4k.shape[:2]
    sx, sy = raw_w / float(proc_w), raw_h / float(proc_h)
    if persons:
        _, pb = persons[0]
        x1, y1, x2, y2 = pb
        pw, ph = x2 - x1, y2 - y1
        rx1, ry1 = max(0, int((x1 - 0.35 * pw) * sx)), max(0, int((y1 - 0.12 * ph) * sy))
        rx2, ry2 = min(raw_w, int((x2 + 0.35 * pw) * sx)), min(raw_h, int((y2 + 0.25 * ph) * sy))
    else:
        rx1, ry1, rx2, ry2 = 0, 0, raw_w // 2, raw_h // 2

    crop_4k = raw_4k[ry1:ry2, rx1:rx2].copy()
    cv2.imwrite(os.path.join(out_dir, "04_4k_roi_crop_input.jpg"), crop_4k)

    # 5. Output nhận diện / phân loại rác trên ảnh cắt 4K
    crop_vis = crop_4k.copy()
    projected_vis = global_vis.copy()

    if is_task2:
        ws_cfg = proc.config.get("waste_sorting", {})
        rec_p = ws_cfg.get("recyclable_prompts", [])
        nonrec_p = ws_cfg.get("non_recyclable_prompts", [])
        wm = YOLO(ws_cfg.get("model_path", "yolov8s-worldv2.pt"))
        wm.set_classes(rec_p + nonrec_p)
        crop_res = wm(crop_4k, conf=0.10, imgsz=640, device=proc.detector.device, verbose=False)[0]
    else:
        crop_res = proc.detector.model(crop_4k, conf=0.15, imgsz=640, device=proc.detector.device, verbose=False)[0]

    detected_trash_global = []
    if crop_res.boxes is not None:
        for b in crop_res.boxes:
            cid = int(b.cls[0].item())
            cname = crop_res.names.get(cid, str(cid))
            conf = float(b.conf[0].item())
            if not is_task2 and proc.detector.map_class(cid, cname) != "trash":
                continue
            bx1, by1, bx2, by2 = [int(v) for v in b.xyxy[0].cpu().numpy()]
            cv2.rectangle(crop_vis, (bx1, by1), (bx2, by2), (0, 220, 0), 3)
            cv2.putText(crop_vis, f"{cname} {conf:.2f}", (bx1, max(25, by1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 0), 2)

            # 6. Ánh xạ về tọa độ toàn khung hình
            gx1, gy1 = int((bx1 + rx1) / sx), int((by1 + ry1) / sy)
            gx2, gy2 = int((bx2 + rx1) / sx), int((by2 + ry1) / sy)
            gbbox = [float(gx1), float(gy1), float(gx2), float(gy2)]
            if any(compute_iou(gbbox, bb) > 0.40 for bb in bin_boxes):
                continue
            detected_trash_global.append((cname, conf, gbbox))
            cv2.rectangle(projected_vis, (gx1, gy1), (gx2, gy2), (0, 220, 0), 3)
            cv2.putText(projected_vis, f"Projected: {cname} {conf:.2f}", (gx1, max(25, gy1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 0), 2)

    cv2.imwrite(os.path.join(out_dir, "05_4k_roi_yolo_output.jpg"), crop_vis)
    cv2.imwrite(os.path.join(out_dir, "06_projected_global_output.jpg"), projected_vis)

    # 7. Ảnh kết xuất cuối cùng (làm mờ mặt + nhãn)
    pb_main = persons[0][1] if persons else None
    tb_main = detected_trash_global[0][2] if detected_trash_global else None
    final_vis = EventManager._anonymize_and_draw_boxes(
        resized, pb_main, tb_main, 1, 101, trash_color=(0, 220, 0)
    )
    cv2.imwrite(os.path.join(out_dir, "07_final_visualizer_output.jpg"), final_vis)
    print(f"[OK] Đã xuất 7 ảnh Input/Output trung gian tại: {out_dir}")


if __name__ == "__main__":
    export_debug_for_video("inputs/IMG_6824.MOV", 6.8, "outputs/pipeline_debug/IMG_6824_task1", is_task2=False)
    export_debug_for_video("inputs/IMG_6820.MOV", 5.1, "outputs/pipeline_debug/IMG_6820_task2", is_task2=True)
