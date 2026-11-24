"""Test thêm cho quan hệ với Thùng rác (Trash Bin)."""

import pytest
from core.association import AssociationAnalyzer
from core.history import TrackHistoryManager
from core.tracker import TrackedObject
from tests.test_association import make_person, make_trash


def make_bin(track_id: int, cx: float, cy: float, w: float = 80.0, h: float = 120.0, t: float = 0.0) -> TrackedObject:
    x1 = cx - w / 2.0
    y1 = cy - h / 2.0
    x2 = cx + w / 2.0
    y2 = cy + h / 2.0
    return TrackedObject(
        track_id=track_id,
        class_name="trash_bin",
        confidence=0.85,
        bbox=[x1, y1, x2, y2],
        center=(cx, cy),
        timestamp=t
    )


def test_trash_inside_bin_vs_near_bin():
    analyzer = AssociationAnalyzer()
    history = TrackHistoryManager()

    # Thùng rác ở tâm (400, 400), bbox [360, 340, 440, 460]
    tb = make_bin(501, 400.0, 400.0, w=80.0, h=120.0, t=0.0)

    # 1. Rác A nằm TRONG thùng rác: tâm (400, 380)
    tr_inside = make_trash(101, 400.0, 380.0, t=0.0)

    # 2. Rác B rơi NGOÀI thùng rác cạnh đáy: tâm (480, 440)
    tr_near = make_trash(102, 480.0, 440.0, t=0.0)

    history.update([tb, tr_inside, tr_near], 0.0)
    rels = analyzer.analyze([tb, tr_inside, tr_near], history, 0.0)

    rel_map = {r.trash_id: r for r in rels}

    assert rel_map[101].is_inside_bin is True
    assert rel_map[101].nearest_bin_id == 501

    assert rel_map[102].is_inside_bin is False
    assert rel_map[102].is_near_bin is True
    assert rel_map[102].nearest_bin_id == 501
