"""Unit tests cho TrackHistory, EventManager và trường hợp nhiều người."""

import os
import tempfile
import json
import pytest
import numpy as np

from core.events import EventManager
from core.behavior import BehaviorEvent, DecisionLevel, EvidenceStage
from core.history import TrackHistoryManager
from tests.test_association import make_person, make_trash


def test_track_history_pruning_and_duration():
    manager = TrackHistoryManager(window_seconds=1.0, max_missing_seconds=0.5)

    # Frame 0.0s đến 0.5s: Track xuất hiện đều
    for step in range(6):
        t = step * 0.1
        p = make_person(1, 100.0, 100.0, 150.0, t)
        manager.update([p], t)

    hist = manager.get_track(1)
    assert hist is not None
    assert pytest.approx(hist.duration_seen, rel=1e-2) == 0.5
    assert len(hist.get_trajectory()) > 0

    # Tại t = 1.2s: Không quan sát thấy person 1 nữa (> max_missing_seconds = 0.5s)
    manager.update([], 1.2)
    assert manager.get_track(1) is None


def test_event_manager_duplicate_suppression_and_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        events_dir = os.path.join(tmpdir, "events")
        evidence_dir = os.path.join(tmpdir, "evidence")
        manager = EventManager(
            output_events_dir=events_dir,
            output_evidence_dir=evidence_dir,
            cooldown_seconds=2.0
        )

        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        evt1 = BehaviorEvent(
            event_id="EVT_0001",
            event_type="POSSIBLE_LITTERING",
            timestamp=2.0,
            person_id=1,
            trash_id=10,
            evidence=["associated", "separated", "stationary"],
            status_message="Test alert",
            bbox_person=[100, 100, 150, 250],
            bbox_trash=[200, 200, 220, 220]
        )

        # Ghi nhận lần 1 -> Hợp lệ
        confirmed = manager.filter_and_record([evt1], dummy_frame, save_evidence=True)
        assert len(confirmed) == 1
        assert os.path.exists(os.path.join(evidence_dir, "EVT_0001.jpg"))

        # Gặp lại cùng person 1, trash 10 tại t = 2.5s (trong thời gian cooldown < 2.0s) -> Bị chặn
        evt_dup = BehaviorEvent(
            event_id="EVT_0002",
            event_type="POSSIBLE_LITTERING",
            timestamp=2.5,
            person_id=1,
            trash_id=10,
            evidence=["associated", "separated", "stationary"],
            status_message="Test duplicate"
        )
        confirmed_dup = manager.filter_and_record([evt_dup], dummy_frame, save_evidence=True)
        assert len(confirmed_dup) == 0

        # Sau cooldown (t = 4.5s) -> Hợp lệ trở lại
        evt_new = BehaviorEvent(
            event_id="EVT_0003",
            event_type="POSSIBLE_LITTERING",
            timestamp=4.5,
            person_id=1,
            trash_id=10,
            evidence=["associated", "separated", "stationary"],
            status_message="Test post-cooldown"
        )
        confirmed_new = manager.filter_and_record([evt_new], dummy_frame, save_evidence=False)
        assert len(confirmed_new) == 1

        # Xuất file JSON
        json_path = os.path.join(events_dir, "test_events.json")
        manager.export_json(json_path)
        assert os.path.exists(json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_events"] == 2
        assert data["events"][0]["event_id"] == "EVT_0001"
        assert data["events"][1]["event_id"] == "EVT_0003"


def test_event_manager_generates_multiframe_event_card():
    """Kiểm thử tạo Thẻ sự kiện 3 khung hình (Event Card) cho Giai đoạn 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        events_dir = os.path.join(tmpdir, "events")
        evidence_dir = os.path.join(tmpdir, "evidence")
        manager = EventManager(output_events_dir=events_dir, output_evidence_dir=evidence_dir)
        manager.set_prefix("demo")

        f1 = np.full((360, 640, 3), 50, dtype=np.uint8)
        f2 = np.full((360, 640, 3), 100, dtype=np.uint8)
        f3 = np.full((360, 640, 3), 150, dtype=np.uint8)

        chain = [
            EvidenceStage("ASSOCIATED", 1.0, True, 0.3, [50, 50, 120, 250], [90, 120, 110, 145], f1),
            EvidenceStage("SEPARATED", 2.0, True, 1.2, [200, 50, 270, 250], [95, 220, 115, 245], f2),
            EvidenceStage("STATIONARY", 3.0, True, 2.0, [350, 50, 420, 250], [95, 220, 115, 245], f3),
        ]
        evt = BehaviorEvent(
            event_id="EVT_0001",
            event_type="POSSIBLE_LITTERING",
            timestamp=3.0,
            person_id=1,
            trash_id=10,
            evidence=["associated", "separated", "stationary"],
            status_message="Đủ bằng chứng thị giác",
            bbox_person=[350, 50, 420, 250],
            bbox_trash=[95, 220, 115, 245],
            decision_level=DecisionLevel.CONFIRMED_LITTERING.value,
            evidence_chain=chain
        )

        confirmed = manager.filter_and_record([evt], f3, save_evidence=True)
        assert len(confirmed) == 1
        card_path = os.path.join(evidence_dir, "demo_EVT_0001_card.jpg")
        assert os.path.exists(card_path)
        assert manager.confirmed_events[0]["decision_level"] == DecisionLevel.CONFIRMED_LITTERING.value
        assert len(manager.confirmed_events[0]["evidence_chain"]) == 3
        assert manager.confirmed_events[0]["event_card_image"] == "demo_EVT_0001_card.jpg"
