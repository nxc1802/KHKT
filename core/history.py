"""Module quản lý lịch sử vết chuyển động (Track History & Sliding Window).

Lưu trữ quỹ đạo, thời gian xuất hiện, trạng thái mất dấu tạm thời,
và cung cấp các phương thức phân tích chuỗi thời gian cho từng đối tượng (Person / Trash).
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

from core.geometry import (
    euclidean_distance,
    smooth_point_ema,
    get_box_dimensions,
)
from core.tracker import TrackedObject


@dataclass
class TrackObservation:
    """Bản ghi trạng thái đối tượng tại một thời điểm (frame)."""
    timestamp: float
    bbox: List[float]
    center: Tuple[float, float]
    smoothed_center: Tuple[float, float]
    confidence: float
    class_name: str


class TrackHistory:
    """Lịch sử chuyển động của 1 track_id duy nhất."""

    def __init__(self,
                 track_id: int,
                 class_name: str,
                 window_seconds: float = 2.5,
                 smoothing_alpha: float = 0.6):
        self.track_id = track_id
        self.class_name = class_name
        self.window_seconds = window_seconds
        self.smoothing_alpha = smoothing_alpha

        self.observations: deque[TrackObservation] = deque()
        self.first_seen_timestamp: float = 0.0
        self.last_seen_timestamp: float = 0.0
        self.total_detections_count: int = 0

        # Tích lũy phiếu bầu loại rác (Temporal Majority Voting)
        self.category_scores: Dict[str, float] = {"recyclable": 0.0, "non_recyclable": 0.0}
        self.best_raw_label: str = ""
        self.best_raw_conf: float = 0.0

    def add_waste_vote(self, category: str, raw_label: str, conf: float):
        """Cộng dồn điểm bầu chọn loại rác theo thời gian."""
        if category in self.category_scores:
            self.category_scores[category] += conf
            if conf >= self.best_raw_conf:
                self.best_raw_conf = conf
                self.best_raw_label = raw_label

    def get_resolved_waste_category(self, min_score: float = 0.15) -> Tuple[str, float]:
        """Trả về nhãn loại rác ổn định nhất và độ tin cậy tổng hợp."""
        rec = self.category_scores["recyclable"]
        nonrec = self.category_scores["non_recyclable"]
        total = rec + nonrec
        if max(rec, nonrec) < min_score or total <= 0:
            return "unknown", 0.0
        if rec >= nonrec:
            return "recyclable", round(rec / total, 2)
        return "non_recyclable", round(nonrec / total, 2)

    def predict_next_position(self, dt: float = 0.033) -> Optional[Tuple[float, float]]:
        """Dự đoán vị trí tâm tiếp theo theo vận tốc quán tính từ 2 quan sát gần nhất."""
        if not self.observations:
            return None
        if len(self.observations) < 2:
            return self.observations[-1].center
        p1, p2 = self.observations[-2], self.observations[-1]
        obs_dt = p2.timestamp - p1.timestamp
        if obs_dt <= 1e-4:
            return p2.center
        vx = (p2.center[0] - p1.center[0]) / obs_dt
        vy = (p2.center[1] - p1.center[1]) / obs_dt
        return (p2.center[0] + vx * dt, p2.center[1] + vy * dt)

    def add_observation(self, obj: TrackedObject):
        """Thêm một quan sát mới vào sliding window."""
        t = obj.timestamp
        if self.total_detections_count == 0:
            self.first_seen_timestamp = t

        self.last_seen_timestamp = t
        self.total_detections_count += 1
        self.class_name = obj.class_name

        # Làm mượt tọa độ tâm
        prev_smoothed = self.observations[-1].smoothed_center if self.observations else None
        sm_center = smooth_point_ema(obj.center, prev_smoothed, alpha=self.smoothing_alpha)

        obs = TrackObservation(
            timestamp=t,
            bbox=obj.bbox,
            center=obj.center,
            smoothed_center=sm_center,
            confidence=obj.confidence,
            class_name=obj.class_name
        )
        self.observations.append(obs)

        # Cắt tỉa các quan sát cũ hơn window_seconds
        min_allowed_time = t - self.window_seconds
        while len(self.observations) > 1 and self.observations[0].timestamp < min_allowed_time:
            self.observations.popleft()

    @property
    def latest(self) -> Optional[TrackObservation]:
        """Quan sát gần nhất."""
        return self.observations[-1] if self.observations else None

    @property
    def duration_seen(self) -> float:
        """Tổng thời gian đối tượng đã xuất hiện (giây)."""
        return max(0.0, self.last_seen_timestamp - self.first_seen_timestamp)

    def get_trajectory(self, max_points: int = 30) -> List[Tuple[float, float]]:
        """Lấy danh sách các điểm tâm (smoothed) để vẽ quỹ đạo."""
        if not self.observations:
            return []
        pts = [obs.smoothed_center for obs in self.observations]
        if len(pts) > max_points:
            return pts[-max_points:]
        return pts

    def get_displacement(self, duration: Optional[float] = None) -> float:
        """Độ dịch chuyển (Euclid) từ điểm đầu đến điểm cuối trong khoảng thời gian duration."""
        if len(self.observations) < 2:
            return 0.0

        latest_obs = self.observations[-1]
        t_limit = latest_obs.timestamp - (duration if duration is not None else self.window_seconds)

        # Tìm observation cổ nhất trong ngưỡng duration
        target_obs = self.observations[0]
        for obs in self.observations:
            if obs.timestamp >= t_limit:
                target_obs = obs
                break

        return euclidean_distance(latest_obs.smoothed_center, target_obs.smoothed_center)

    def get_average_velocity(self, duration: Optional[float] = None) -> float:
        """Vận tốc trung bình (pixels / giây) trong khoảng thời gian xét."""
        if len(self.observations) < 2:
            return 0.0

        latest_obs = self.observations[-1]
        t_limit = latest_obs.timestamp - (duration if duration is not None else self.window_seconds)

        target_obs = self.observations[0]
        for obs in self.observations:
            if obs.timestamp >= t_limit:
                target_obs = obs
                break

        dt = latest_obs.timestamp - target_obs.timestamp
        if dt <= 1e-4:
            return 0.0

        disp = euclidean_distance(latest_obs.smoothed_center, target_obs.smoothed_center)
        return disp / dt

    def is_stationary(self,
                      min_duration: float = 0.8,
                      max_motion_ratio: float = 0.05,
                      frame_diag: float = 1000.0) -> bool:
        """Kiểm tra xem vật thể có đứng yên trong suốt `min_duration` giây qua không.
        
        Args:
            min_duration: Khoảng thời gian tối thiểu vật thể phải đứng yên.
            max_motion_ratio: Ngưỡng dịch chuyển tối đa tính theo tỷ lệ kích thước khung hình.
            frame_diag: Đường chéo của khung hình dùng để chuẩn hóa (pixel).
        """
        if len(self.observations) < 2:
            return False

        latest_obs = self.observations[-1]
        first_in_window = None

        # Kiểm tra xem lịch sử có đủ dài >= min_duration chưa
        t_threshold = latest_obs.timestamp - min_duration
        if self.observations[0].timestamp > t_threshold:
            # Chưa quan sát đủ min_duration
            return False

        # Kiểm tra độ dịch chuyển tối đa giữa tất cả các điểm trong cửa sổ thời gian
        # so với điểm gần nhất
        pts_in_window = []
        for obs in self.observations:
            if obs.timestamp >= t_threshold:
                pts_in_window.append(obs.smoothed_center)

        if not pts_in_window:
            return False

        # Tính độ dịch chuyển lớn nhất giữa các điểm
        max_dist = 0.0
        anchor = pts_in_window[-1]
        for pt in pts_in_window:
            d = euclidean_distance(pt, anchor)
            if d > max_dist:
                max_dist = d

        max_allowed_motion = max_motion_ratio * frame_diag
        return max_dist <= max_allowed_motion


class TrackHistoryManager:
    """Quản lý lịch sử toàn bộ các đối tượng trong video."""

    def __init__(self,
                 window_seconds: float = 2.5,
                 max_missing_seconds: float = 0.8,
                 smoothing_alpha: float = 0.6):
        self.window_seconds = window_seconds
        self.max_missing_seconds = max_missing_seconds
        self.smoothing_alpha = smoothing_alpha

        self.tracks: Dict[int, TrackHistory] = {}
        self.current_timestamp: float = 0.0

    def update(self, objects: List[TrackedObject], timestamp: float):
        """Cập nhật các quan sát của frame hiện tại vào lịch sử."""
        self.current_timestamp = timestamp
        seen_ids = set()

        for obj in objects:
            seen_ids.add(obj.track_id)
            if obj.track_id not in self.tracks:
                self.tracks[obj.track_id] = TrackHistory(
                    track_id=obj.track_id,
                    class_name=obj.class_name,
                    window_seconds=self.window_seconds,
                    smoothing_alpha=self.smoothing_alpha
                )
            self.tracks[obj.track_id].add_observation(obj)

        # Dọn dẹp các track bị mất dấu quá max_missing_seconds
        dead_ids = []
        for tid, history in self.tracks.items():
            if tid not in seen_ids:
                if timestamp - history.last_seen_timestamp > self.max_missing_seconds:
                    dead_ids.append(tid)

        for tid in dead_ids:
            del self.tracks[tid]

    def get_track(self, track_id: int) -> Optional[TrackHistory]:
        """Lấy lịch sử của 1 track ID."""
        return self.tracks.get(track_id)

    def is_present(self, track_id: int) -> bool:
        """Kiểm tra track có đang xuất hiện trong frame hiện tại không."""
        history = self.tracks.get(track_id)
        if not history or not history.latest:
            return False
        return math.isclose(history.latest.timestamp, self.current_timestamp, abs_tol=1e-3)

    def reset(self):
        """Reset toàn bộ lịch sử khi chuyển video."""
        self.tracks.clear()
        self.current_timestamp = 0.0
