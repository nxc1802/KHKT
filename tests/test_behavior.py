"""Unit tests cho core/behavior.py và Finite State Machine."""

import pytest
import numpy as np
from core.association import AssociationAnalyzer
from core.behavior import BehaviorEngine, BehaviorState, DecisionLevel
from core.history import TrackHistoryManager
from tests.test_association import make_person, make_trash


def test_fsm_full_littering_lifecycle():
    association = AssociationAnalyzer(
        near_distance_ratio=0.8,
        separation_distance_ratio=1.0,
        min_association_seconds=0.3
    )
    behavior = BehaviorEngine(
        separation_distance_ratio=1.0,
        min_stationary_seconds=0.5,
        event_cooldown_seconds=2.0
    )
    history = TrackHistoryManager()

    # 1. Giai đoạn 1: ASSOCIATED (t = 0.0s đến 0.5s)
    # Người và rác di chuyển cùng nhau từ x=100 đến x=150
    events = []
    for step in range(6):
        t = step * 0.1
        px = 100.0 + step * 10
        p = make_person(1, px, 300.0, 100.0, t)
        tr = make_trash(10, px + 15, 300.0, t)
        history.update([p, tr], t)
        rels = association.analyze([p, tr], history, t)
        evts = behavior.update([p, tr], rels, history, t)
        events.extend(evts)

    # Sau 0.5s, FSM phải ở trạng thái ASSOCIATED
    assert behavior.get_fsm_state(10) == BehaviorState.ASSOCIATED
    assert len(events) == 0

    # 2. Giai đoạn 2: SEPARATED (t = 0.6s đến 0.8s)
    # Người bỏ lại rác tại x=150 và bước ra xa đến x=300 (d = 150px > 100px chiều cao người)
    for step in range(6, 9):
        t = step * 0.1
        px = 150.0 + (step - 5) * 50  # Người đi nhanh ra xa
        p = make_person(1, px, 300.0, 100.0, t)
        tr = make_trash(10, 150.0, 300.0, t)  # Rác dừng tại x=150
        history.update([p, tr], t)
        rels = association.analyze([p, tr], history, t)
        evts = behavior.update([p, tr], rels, history, t)
        events.extend(evts)

    assert behavior.get_fsm_state(10) == BehaviorState.SEPARATED
    assert len(events) == 0

    # 3. Giai đoạn 3 & 4: STATIONARY & POSSIBLE_LITTERING (t = 0.9s đến 1.5s)
    # Rác tiếp tục nằm yên tại x=150 trong hơn 0.5s
    for step in range(9, 16):
        t = step * 0.1
        px = 300.0 + (step - 8) * 30
        p = make_person(1, px, 300.0, 100.0, t)
        tr = make_trash(10, 150.0, 300.0, t)
        history.update([p, tr], t)
        rels = association.analyze([p, tr], history, t)
        evts = behavior.update([p, tr], rels, history, t)
        events.extend(evts)

    # FSM phải chuyển sang POSSIBLE_LITTERING và phát sinh đúng 1 sự kiện
    assert behavior.get_fsm_state(10) == BehaviorState.POSSIBLE_LITTERING
    assert len(events) == 1
    evt = events[0]
    assert evt.event_type == "POSSIBLE_LITTERING"
    assert evt.person_id == 1
    assert evt.trash_id == 10
    assert "associated" in evt.evidence
    assert "separated" in evt.evidence
    assert "stationary" in evt.evidence


def test_fsm_pre_existing_trash_no_alert():
    association = AssociationAnalyzer(
        near_distance_ratio=0.8,
        min_association_seconds=0.3,
        pre_existing_buffer_sec=0.5
    )
    behavior = BehaviorEngine()
    history = TrackHistoryManager()

    # Rác nằm yên sẵn một mình từ t = 0.0s đến 0.6s
    for step in range(7):
        t = step * 0.1
        tr = make_trash(99, 400.0, 400.0, t)
        history.update([tr], t)
        rels = association.analyze([tr], history, t)
        behavior.update([tr], rels, history, t)

    # Người lạ bước ngang qua rất sát rác
    events = []
    for step in range(7, 15):
        t = step * 0.1
        p = make_person(2, 405.0, 400.0, 100.0, t)
        tr = make_trash(99, 400.0, 400.0, t)
        history.update([p, tr], t)
        rels = association.analyze([p, tr], history, t)
        evts = behavior.update([p, tr], rels, history, t)
        events.extend(evts)

    # Không được kích hoạt bất kỳ cảnh báo nào
    assert len(events) == 0
    assert behavior.get_fsm_state(99) == BehaviorState.IDLE


def test_evidence_chain_confirmed_vs_suspicious():
    """Kiểm thử Giai đoạn 1: 3 mức kết luận dựa trên chuỗi bằng chứng."""
    dummy_frame = np.zeros((360, 640, 3), dtype=np.uint8)

    # Case A: Quan sát trực tiếp toàn bộ chuỗi -> CONFIRMED_LITTERING
    assoc_a = AssociationAnalyzer(near_distance_ratio=0.8, separation_distance_ratio=1.0, min_association_seconds=0.3)
    beh_a = BehaviorEngine(separation_distance_ratio=1.0, min_stationary_seconds=0.5)
    hist_a = TrackHistoryManager()

    events_a = []
    for step in range(16):
        t = step * 0.1
        if step < 6:
            px = 100.0 + step * 10
            tx = px + 15.0
        else:
            px = 150.0 + (step - 5) * 40
            tx = 150.0
        p = make_person(1, px, 300.0, 100.0, t)
        tr = make_trash(10, tx, 300.0, t)
        hist_a.update([p, tr], t)
        rels = assoc_a.analyze([p, tr], hist_a, t)
        events_a.extend(beh_a.update([p, tr], rels, hist_a, t, current_frame=dummy_frame))

    assert len(events_a) == 1
    assert events_a[0].decision_level == DecisionLevel.CONFIRMED_LITTERING.value
    stage_names = [s.stage_name for s in events_a[0].evidence_chain]
    assert stage_names == ["ASSOCIATED", "SEPARATED", "STATIONARY"]
    assert all(s.observed_directly for s in events_a[0].evidence_chain)
    assert all(s.frame_snapshot is not None for s in events_a[0].evidence_chain)

    # Case B: Rác chỉ xuất hiện sau khi người đi qua (Backtracking / che khuất) -> SUSPICIOUS_NEED_REVIEW
    assoc_b = AssociationAnalyzer(near_distance_ratio=0.8, separation_distance_ratio=1.0, min_association_seconds=0.3)
    beh_b = BehaviorEngine(separation_distance_ratio=1.0, min_stationary_seconds=0.5)
    hist_b = TrackHistoryManager()

    # Người đi qua x=200 tại t=0.0..0.3, rồi đi xa đến x=500
    for step in range(4):
        t = step * 0.1
        p = make_person(2, 200.0 + step * 10, 300.0, 100.0, t)
        hist_b.update([p], t)
        assoc_b.analyze([p], hist_b, t)

    events_b = []
    for step in range(4, 18):
        t = step * 0.1
        p = make_person(2, 450.0 + step * 10, 300.0, 100.0, t)
        tr = make_trash(20, 205.0, 300.0, t)
        hist_b.update([p, tr], t)
        rels = assoc_b.analyze([p, tr], hist_b, t)
        events_b.extend(beh_b.update([p, tr], rels, hist_b, t, current_frame=dummy_frame))

    assert len(events_b) == 1
    assert events_b[0].decision_level == DecisionLevel.SUSPICIOUS_NEED_REVIEW.value
