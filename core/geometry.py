"""Module hình học và tính toán không gian (Spatial Geometry).

Cung cấp các hàm toán học:
- Tính tâm (center), kích thước (width, height) của Bounding Box.
- Khoảng cách Euclid giữa 2 điểm.
- Khoảng cách chuẩn hóa theo chiều cao người (d_norm = dist / h_person).
- Khoảng cách từ một điểm (ví dụ tâm rác) đến Bounding Box của người.
- Khoảng cách giữa 2 Bounding Box.
- Tính chỉ số IoU (Intersection over Union).
- Tính vận tốc chuyển động và làm mượt tọa độ.
"""

from typing import Tuple, List, Optional
import math
import numpy as np


def get_box_center(bbox: List[float]) -> Tuple[float, float]:
    """Tính tọa độ tâm (cx, cy) của bounding box [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    return cx, cy


def get_box_dimensions(bbox: List[float]) -> Tuple[float, float]:
    """Tính chiều rộng (w) và chiều cao (h) của bounding box [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = bbox
    w = max(0.0, float(x2 - x1))
    h = max(0.0, float(y2 - y1))
    return w, h


def euclidean_distance(pt1: Tuple[float, float], pt2: Tuple[float, float]) -> float:
    """Tính khoảng cách Euclid giữa hai điểm (x1, y1) và (x2, y2)."""
    return math.hypot(pt1[0] - pt2[0], pt1[1] - pt2[1])


def normalized_distance(distance: float, reference_height: float) -> float:
    """Chuẩn hóa khoảng cách theo chiều cao tham chiếu (chiều cao bbox người).
    
    Tránh phụ thuộc vào khoảng cách xa/gần của camera.
    """
    if reference_height <= 1e-4:
        return distance
    return distance / reference_height


def point_to_box_distance(pt: Tuple[float, float], bbox: List[float]) -> float:
    """Tính khoảng cách ngắn nhất từ một điểm (px, py) tới cạnh của bounding box [x1, y1, x2, y2].
    
    Nếu điểm nằm bên trong bounding box, khoảng cách bằng 0.
    """
    px, py = pt
    x1, y1, x2, y2 = bbox

    dx = max(0.0, x1 - px, px - x2)
    dy = max(0.0, y1 - py, py - y2)
    return math.hypot(dx, dy)


def box_to_box_distance(bbox1: List[float], bbox2: List[float]) -> float:
    """Tính khoảng cách ngắn nhất giữa hai bounding box.
    
    Nếu hai box giao nhau hoặc lồng nhau, khoảng cách bằng 0.
    """
    x1_a, y1_a, x2_a, y2_a = bbox1
    x1_b, y1_b, x2_b, y2_b = bbox2

    left = x2_a < x1_b
    right = x2_b < x1_a
    bottom = y2_a < y1_b
    top = y2_b < y1_a

    if top and left:
        return euclidean_distance((x1_b, y2_b), (x2_a, y1_a))
    elif left and bottom:
        return euclidean_distance((x1_b, y1_b), (x2_a, y2_a))
    elif bottom and right:
        return euclidean_distance((x2_b, y1_b), (x1_a, y2_a))
    elif right and top:
        return euclidean_distance((x2_b, y2_b), (x1_a, y1_a))
    elif left:
        return float(x1_b - x2_a)
    elif right:
        return float(x1_a - x2_b)
    elif bottom:
        return float(y1_b - y2_a)
    elif top:
        return float(y1_a - y2_b)
    else:
        # Boxes overlap
        return 0.0


def compute_iou(bbox1: List[float], bbox2: List[float]) -> float:
    """Tính chỉ số IoU (Intersection over Union) giữa hai bounding box."""
    x1_a, y1_a, x2_a, y2_a = bbox1
    x1_b, y1_b, x2_b, y2_b = bbox2

    xi1 = max(x1_a, x1_b)
    yi1 = max(y1_a, y1_b)
    xi2 = min(x2_a, x2_b)
    yi2 = min(y2_a, y2_b)

    inter_w = max(0.0, xi2 - xi1)
    inter_h = max(0.0, yi2 - yi1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, x2_a - x1_a) * max(0.0, y2_a - y1_a)
    area_b = max(0.0, x2_b - x1_b) * max(0.0, y2_b - y1_b)
    union_area = area_a + area_b - inter_area

    if union_area <= 1e-6:
        return 0.0
    return inter_area / union_area


def calculate_velocity(pt_curr: Tuple[float, float],
                       pt_prev: Tuple[float, float],
                       dt: float) -> float:
    """Tính vận tốc chuyển động (pixels / second)."""
    if dt <= 1e-5:
        return 0.0
    dist = euclidean_distance(pt_curr, pt_prev)
    return dist / dt


def smooth_point_ema(current_pt: Tuple[float, float],
                     previous_pt: Optional[Tuple[float, float]],
                     alpha: float = 0.6) -> Tuple[float, float]:
    """Làm mượt tọa độ bằng Exponential Moving Average (EMA).
    
    alpha: trọng số của tọa độ hiện tại (0 < alpha <= 1).
    """
    if previous_pt is None:
        return current_pt
    sm_x = alpha * current_pt[0] + (1.0 - alpha) * previous_pt[0]
    sm_y = alpha * current_pt[1] + (1.0 - alpha) * previous_pt[1]
    return sm_x, sm_y
