"""Integration test cho toàn bộ Pipeline VideoProcessor (End-to-End).

Xác minh:
1. VideoProcessor đọc tuần tự các frame và điều phối toàn bộ các module.
2. Phát hiện đúng hành vi xả rác theo kịch bản: Associated -> Separated -> Stationary -> Possible Littering.
3. Xuất file video annotated .mp4, file sự kiện .json và ảnh bằng chứng .jpg.
"""

import os
import tempfile
import cv2
import numpy as np
import pytest

from pipeline.video_processor import VideoProcessor
from core.tracker import TrackedObject


def test_video_processor_e2e(monkeypatch):
    """Kiểm thử tích hợp E2E của VideoProcessor với kịch bản xả rác hoàn chỉnh."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Tạo video giả lập đầu vào (30 fps, 120 frames = 4.0s, 640x360)
        input_video = os.path.join(tmpdir, "test_input.mp4")
        output_video = os.path.join(tmpdir, "test_output.mp4")
        output_json = os.path.join(tmpdir, "test_events.json")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(input_video, fourcc, 30.0, (640, 360))
        for _ in range(120):
            frame = np.full((360, 640, 3), 120, dtype=np.uint8)
            writer.write(frame)
        writer.release()

        # 2. Khởi tạo VideoProcessor
        processor = VideoProcessor(config_path="config.yaml")
        # Trỏ output evidence tạm thời vào tmpdir
        processor.event_manager.output_evidence_dir = os.path.join(tmpdir, "evidence")
        os.makedirs(processor.event_manager.output_evidence_dir, exist_ok=True)

        # 3. Kịch bản tracking được giả lập qua các frame (120 frames = 4.0s):
        # - Frame 0 đến 25 (0.0s -> 0.8s): Person #1 mang Trash #10 đi từ x=100 đến x=200 (Associated)
        # - Frame 26 đến 60 (0.8s -> 2.0s): Person #1 bước nhanh ra xa từ x=200 đến x=500 (Separated)
        # - Frame 61 đến 119 (2.0s -> 4.0s): Trash #10 nằm yên tại x=200 trong 2.0s (> 0.7s) -> Possible Littering!
        def mock_track(frame, timestamp):
            f_idx = int(round(timestamp * 30.0))
            objs = []

            # Person #1
            if f_idx <= 25:
                px = 100.0 + (f_idx / 25.0) * 100.0
            else:
                px = 200.0 + ((f_idx - 25) / 35.0) * 350.0  # Đi xa nhanh chóng ra khỏi vị trí

            p_bbox = [px - 20, 150, px + 20, 300]
            objs.append(TrackedObject(
                track_id=1,
                class_name="person",
                confidence=0.92,
                bbox=p_bbox,
                center=(px, 225.0),
                timestamp=timestamp
            ))

            # Trash #10
            if f_idx <= 25:
                tx = px + 15
            else:
                tx = 215.0

            t_bbox = [tx - 10, 260, tx + 10, 280]
            objs.append(TrackedObject(
                track_id=10,
                class_name="trash",
                confidence=0.88,
                bbox=t_bbox,
                center=(tx, 270.0),
                timestamp=timestamp
            ))

            return objs

        # Thay thế hàm track của tracker bằng mock_track
        monkeypatch.setattr(processor.tracker, "track", mock_track)

        # 4. Thực thi VideoProcessor
        summary = processor.process_video(
            video_path=input_video,
            output_video_path=output_video,
            events_json_path=output_json,
            show_progress=False
        )

        # 5. Xác minh kết quả
        assert os.path.exists(output_video), "File video output annotated không được tạo!"
        assert os.path.exists(output_json), "File events JSON không được tạo!"
        assert summary["total_frames_processed"] == 120
        assert summary["total_events_detected"] == 1

        # Kiểm tra nội dung JSON
        import json
        with open(output_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["total_events"] == 1
        event = data["events"][0]
        assert event["event_type"] == "POSSIBLE_LITTERING"
        assert event["person_id"] == 1
        assert event["trash_id"] == 10
        assert "associated" in event["evidence"]
        assert "separated" in event["evidence"]
        assert "stationary" in event["evidence"]

        # Kiểm tra ảnh bằng chứng
        evidence_file = os.path.join(processor.event_manager.output_evidence_dir, event["evidence_image"])
        assert os.path.exists(evidence_file), "Ảnh bằng chứng không tồn tại!"
