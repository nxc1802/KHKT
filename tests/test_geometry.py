"""Unit tests cho core/geometry.py."""

import pytest
import math
from core.geometry import (
    get_box_center,
    get_box_dimensions,
    euclidean_distance,
    normalized_distance,
    point_to_box_distance,
    box_to_box_distance,
    compute_iou,
    calculate_velocity,
    smooth_point_ema,
)


def test_box_center_and_dimensions():
    bbox = [100.0, 200.0, 300.0, 400.0]
    cx, cy = get_box_center(bbox)
    w, h = get_box_dimensions(bbox)
    assert cx == 200.0
    assert cy == 300.0
    assert w == 200.0
    assert h == 200.0


def test_euclidean_distance():
    p1 = (0.0, 0.0)
    p2 = (3.0, 4.0)
    assert math.isclose(euclidean_distance(p1, p2), 5.0)


def test_normalized_distance():
    dist = 100.0
    ref_h = 200.0
    assert math.isclose(normalized_distance(dist, ref_h), 0.5)
    # Edge case: zero reference height
    assert math.isclose(normalized_distance(dist, 0.0), 100.0)


def test_point_to_box_distance():
    bbox = [10.0, 10.0, 50.0, 50.0]
    # Point inside box -> distance = 0
    assert point_to_box_distance((20.0, 30.0), bbox) == 0.0
    # Point to the right of box
    assert math.isclose(point_to_box_distance((60.0, 30.0), bbox), 10.0)
    # Point to top-left diagonal
    assert math.isclose(point_to_box_distance((7.0, 6.0), bbox), 5.0)


def test_box_to_box_distance():
    b1 = [0.0, 0.0, 10.0, 10.0]
    # Overlapping boxes
    b2 = [5.0, 5.0, 15.0, 15.0]
    assert box_to_box_distance(b1, b2) == 0.0

    # Separated horizontally
    b3 = [20.0, 0.0, 30.0, 10.0]
    assert math.isclose(box_to_box_distance(b1, b3), 10.0)

    # Separated diagonally
    b4 = [13.0, 14.0, 23.0, 24.0]
    assert math.isclose(box_to_box_distance(b1, b4), 5.0)


def test_compute_iou():
    b1 = [0.0, 0.0, 10.0, 10.0]
    b2 = [0.0, 0.0, 10.0, 10.0]
    assert math.isclose(compute_iou(b1, b2), 1.0)

    b3 = [5.0, 0.0, 15.0, 10.0]
    # Inter area: 5 * 10 = 50. Union area: 100 + 100 - 50 = 150. IoU = 50/150 = 1/3
    assert math.isclose(compute_iou(b1, b3), 1.0 / 3.0)

    b4 = [20.0, 20.0, 30.0, 30.0]
    assert compute_iou(b1, b4) == 0.0


def test_velocity_and_smoothing():
    p1 = (100.0, 100.0)
    p2 = (130.0, 140.0)
    dt = 0.5
    # dist = 50.0, velocity = 50 / 0.5 = 100 px/sec
    assert math.isclose(calculate_velocity(p2, p1, dt), 100.0)

    # Smoothing
    curr = (10.0, 20.0)
    prev = (0.0, 0.0)
    sm = smooth_point_ema(curr, prev, alpha=0.5)
    assert sm == (5.0, 10.0)
