"""Unit tests cho core/association.py."""

import pytest
from core.association import AssociationAnalyzer
from core.history import TrackHistoryManager
from core.tracker import TrackedObject


def make_person(track_id: int, cx: float, cy: float, h: float, t: float) -> TrackedObject:
    w = h * 0.4
    x1 = cx - w / 2.0
    y1 = cy - h / 2.0
    x2 = cx + w / 2.0
    y2 = cy + h / 2.0
    return TrackedObject(
        track_id=track_id,
        class_name="person",
        confidence=0.9,
        bbox=[x1, y1, x2, y2],
        center=(cx, cy),
        timestamp=t
    )


def make_trash(track_id: int, cx: float, cy: float, t: float) -> TrackedObject:
    size = 20.0
    return TrackedObject(
        track_id=track_id,
        class_name="trash",
        confidence=0.85,
        bbox=[cx - size/2, cy - size/2, cx + size/2, cy + size/2],
        center=(cx, cy),
        timestamp=t
    )


def test_person_trash_association_success():
    analyzer = AssociationAnalyzer(
        near_distance_ratio=0.8,
        min_association_seconds=0.3
    )
    history = TrackHistoryManager()

    # Giây 0.0: Người và rác ở gần nhau (khoảng cách 30px, person height 150px -> d_norm = 0.2 < 0.8)
    t = 0.0
    p = make_person(1, 100.0, 300.0, 150.0, t)
    tr = make_trash(10, 120.0, 300.0, t)
    history.update([p, tr], t)
    rels = analyzer.analyze([p, tr], history, t)
    assert len(rels) == 1
    # Chưa đủ 0.3s -> is_associated = False
    assert rels[0].is_associated is False

    # Giây 0.4: Vẫn ở gần nhau -> đã đủ >= 0.3s -> is_associated = True
    t = 0.4
    p = make_person(1, 150.0, 300.0, 150.0, t)
    tr = make_trash(10, 170.0, 300.0, t)
    history.update([p, tr], t)
    rels = analyzer.analyze([p, tr], history, t)
    assert len(rels) == 1
    assert rels[0].is_associated is True
    assert rels[0].associated_person_id == 1


def test_pre_existing_trash_filter():
    analyzer = AssociationAnalyzer(
        near_distance_ratio=0.8,
        min_association_seconds=0.3,
        pre_existing_buffer_sec=1.0
    )
    history = TrackHistoryManager()

    # Rác đứng yên một mình từ t = 0.0 đến t = 1.2s
    for step in range(13):
        t = step * 0.1
        tr = make_trash(20, 500.0, 500.0, t)
        history.update([tr], t)
        analyzer.analyze([tr], history, t)

    # Tại t = 1.3s: Một người lạ (Person 2) đi ngang qua rất gần rác (d = 10px)
    t = 1.3
    p2 = make_person(2, 510.0, 500.0, 150.0, t)
    tr = make_trash(20, 500.0, 500.0, t)
    history.update([p2, tr], t)
    rels = analyzer.analyze([p2, tr], history, t)

    assert len(rels) == 1
    rel = rels[0]
    # Rác phải được đánh dấu là pre-existing, KHÔNG được liên kết người 2 xả rác
    assert rel.is_pre_existing is True
    assert rel.is_associated is False
    assert rel.associated_person_id is None
