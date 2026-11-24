"""Trích xuất ảnh Key Frame từ các video thực nghiệm đã bám vết (annotated videos).
Tự động làm mờ khuôn mặt học sinh để tuân thủ 100% quy chế bảo vệ danh tính KHKT.
"""

import os
import sys
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.detector import Detector

detector = Detector(model_path="weights/best.pt", confidence_threshold=0.20)


def anonymize(frame):
    vis = frame.copy()
    h, w = vis.shape[:2]
    preds = detector.model(vis, conf=0.20, verbose=False)[0]
    if preds.boxes is not None:
        for box in preds.boxes:
            cls_id = int(box.cls[0].item())
            name = detector.model.names.get(cls_id, "")
            norm_cls = detector.map_class(cls_id, name)
            if norm_cls == "person":
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = [int(v) for v in xyxy]
                head_h = max(20, int((y2 - y1) * 0.35))
                face_y2 = min(y2, y1 + head_h)
                cx1, cx2 = max(0, x1 - 10), min(w, x2 + 10)
                cy1, cy2 = max(0, y1 - 10), min(h, face_y2)
                if cx2 > cx1 and cy2 > cy1:
                    roi = vis[cy1:cy2, cx1:cx2]
                    kw = max(25, (roi.shape[1] // 2 * 2 + 1))
                    kh = max(25, (roi.shape[0] // 2 * 2 + 1))
                    vis[cy1:cy2, cx1:cx2] = cv2.GaussianBlur(roi, (kw, kh), 40)
    return vis


def extract_and_save(video_path, frame_idx, out_path, banner_title=None):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print(f"[LỖI] Không đọc được frame {frame_idx} từ {video_path}")
        return

    anon = anonymize(frame)

    if banner_title:
        h, w = anon.shape[:2]
        # Thêm khung thông tin tóm tắt nhỏ phía dưới
        bar_h = 42
        overlay = anon.copy()
        cv2.rectangle(overlay, (0, h - bar_h), (w, h), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.8, anon, 0.2, 0, anon)
        cv2.putText(anon, banner_title, (15, h - 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, anon)
    print(f"[OK] Đã xuất keyframe: {out_path}")


def main():
    keyframes = [
        ("outputs/videos/sample_01_corridor_littering_annotated.mp4", 160,
         "outputs/evidence/kf_sample_01_carry.jpg",
         "Video 1 (05.3s): Hoc sinh mang chai nuoc di doc hanh lang [FSM: ASSOCIATED]"),

        ("outputs/videos/sample_01_corridor_littering_annotated.mp4", 402,
         "outputs/evidence/kf_sample_01_alert.jpg",
         "Video 1 (13.4s): Phat hien chai nuoc bi bo lai canh Thung rac #501 [CANH BAO]"),

        ("outputs/videos/sample_02_classroom_desk_littering_annotated.mp4", 100,
         "outputs/evidence/kf_sample_02_desk.jpg",
         "Video 2 (03.3s): Hoc sinh nhet rac hoc ban - Rac bi che khuat, khong bao gia"),

        ("outputs/videos/sample_03_corridor_drop_near_bin_annotated.mp4", 28,
         "outputs/evidence/kf_sample_03_drop.jpg",
         "Video 3 (00.9s): Tha chai rac roi canh chan thung rac [CANH BAO TUC THI]"),

        ("outputs/videos/sample_04_schoolyard_tree_bin_annotated.mp4", 200,
         "outputs/evidence/kf_sample_04_tree.jpg",
         "Video 4 (06.7s): San truong goc cay - Nhan dien thung rac, khong bao gia"),

        ("outputs/videos/sample_05_balcony_corridor_walk_annotated.mp4", 180,
         "outputs/evidence/kf_sample_05_balcony.jpg",
         "Video 5 (06.0s): Ban cong lau 2 - Hoc sinh di lai binh thuong [TRANG THAI AN TOAN]"),

        ("outputs/videos/sample_06_schoolyard_distant_angle_annotated.mp4", 200,
         "outputs/evidence/kf_sample_06_distant.jpg",
         "Video 6 (06.7s): San truong goc xa - Quan sat goc rong on dinh [AN TOAN]")
    ]

    for vpath, fidx, outpath, title in keyframes:
        extract_and_save(vpath, fidx, outpath, title)


if __name__ == "__main__":
    main()
