"""Module phân tích liên kết Người – Rác – Thùng Rác (Person–Trash–Bin Association).

Nhiệm vụ:
- Xác định quan hệ vật thể đang được người mang theo hay không.
- Phân tích tương quan vị trí giữa Rác và Thùng rác (Trash Bin):
  + Rác bỏ đúng vào trong thùng: is_inside_bin = True (Hành vi đúng quy định).
  + Rác rơi ngoài thùng / cạnh thùng: is_inside_bin = False, is_near_bin = True (Xả rác cạnh thùng).
- Cơ chế hồi quy vết không gian - thời gian (Spatio-Temporal Backtracking):
  Khi rác xuất hiện trên sàn (sau khi bị người che khuất lúc thả), thuật toán quét lịch sử
  quỹ đạo các người đã đi qua vị trí đó trong vài giây trước để xác định chính xác người đã bỏ lại.
- Bộ lọc rác có sẵn từ đầu cảnh (Pre-existing Trash Filter).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math

from core.geometry import (
    euclidean_distance,
    normalized_distance,
    point_to_box_distance,
    box_to_box_distance,
    get_box_dimensions,
    compute_iou,
)
from core.history import TrackHistoryManager
from core.tracker import TrackedObject


@dataclass
class PersonTrashRelation:
    """Mối quan hệ không gian - thời gian giữa Rác, Người và Thùng rác."""
    trash_id: int
    associated_person_id: Optional[int]
    current_nearest_person_id: Optional[int]
    distance: float
    normalized_distance: float
    is_near: bool
    is_associated: bool
    is_pre_existing: bool
    association_duration: float
    # Quan hệ với Thùng rác
    nearest_bin_id: Optional[int] = None
    bin_distance: float = 999.0
    is_inside_bin: bool = False
    is_near_bin: bool = False
    associated_via_backtracking: bool = False
    status_text: str = ""


class TrashAssociationState:
    """Lưu giữ tiến trình liên kết theo thời gian cho một vật thể rác cụ thể."""

    def __init__(self, trash_id: int, first_seen_time: float):
        self.trash_id = trash_id
        self.first_seen_time = first_seen_time

        self.associated_person_id: Optional[int] = None
        self.association_start_time: Optional[float] = None
        self.consecutive_associated_seconds: float = 0.0
        self.associated_via_backtracking: bool = False

        self.is_pre_existing: bool = False
        self.checked_pre_existing: bool = False


class AssociationAnalyzer:
    """Phân tích quan hệ không gian - thời gian giữa Person, Trash và Trash Bin."""

    def __init__(self,
                 near_distance_ratio: float = 0.85,
                 separation_distance_ratio: float = 0.95,
                 min_association_seconds: float = 0.3,
                 pre_existing_buffer_sec: float = 1.5,
                 spatial_backtrack_sec: float = 2.5,
                 bin_iou_threshold: float = 0.35):
        self.near_distance_ratio = near_distance_ratio
        self.separation_distance_ratio = separation_distance_ratio
        self.min_association_seconds = min_association_seconds
        self.pre_existing_buffer_sec = pre_existing_buffer_sec
        self.spatial_backtrack_sec = spatial_backtrack_sec
        self.bin_iou_threshold = bin_iou_threshold

        self.trash_states: Dict[int, TrashAssociationState] = {}

    def analyze(self,
                objects: List[TrackedObject],
                history: TrackHistoryManager,
                timestamp: float,
                frame_shape: Tuple[int, int] = (720, 1280)) -> List[PersonTrashRelation]:
        """Phân tích quan hệ giữa Person, Trash và Trash Bin trong frame hiện tại."""
        frame_h, frame_w = frame_shape
        frame_diag = math.hypot(frame_h, frame_w)

        people = [obj for obj in objects if obj.class_name == "person"]
        trashes = [obj for obj in objects if obj.class_name == "trash"]
        bins = [obj for obj in objects if obj.class_name == "trash_bin"]

        relations: List[PersonTrashRelation] = []

        for trash in trashes:
            tid = trash.track_id
            if tid not in self.trash_states:
                self.trash_states[tid] = TrashAssociationState(tid, timestamp)

            state = self.trash_states[tid]
            trash_history = history.get_track(tid)

            # 1. Kiểm tra rác có sẵn từ đầu cảnh (Pre-existing Filter)
            if not state.checked_pre_existing and (timestamp - state.first_seen_time) >= self.pre_existing_buffer_sec:
                state.checked_pre_existing = True
                if state.associated_person_id is None and trash_history is not None:
                    if trash_history.is_stationary(min_duration=self.pre_existing_buffer_sec * 0.8,
                                                   frame_diag=frame_diag):
                        state.is_pre_existing = True

            # 2. Phân tích quan hệ với Thùng rác (Trash Bin)
            nearest_bin_id = None
            min_bin_dist = float("inf")
            is_inside_bin = False
            is_near_bin = False

            for b in bins:
                bin_d = box_to_box_distance(trash.bbox, b.bbox)
                if bin_d < min_bin_dist:
                    min_bin_dist = bin_d
                    nearest_bin_id = b.track_id

                # Kiểm tra rác có nằm bên trong thùng không
                iou = compute_iou(trash.bbox, b.bbox)
                # Hoặc tâm rác nằm lọt vào trong bounding box của thùng
                bx1, by1, bx2, by2 = b.bbox
                tx, ty = trash.center
                inside_box = (bx1 <= tx <= bx2) and (by1 <= ty <= by2)

                if iou >= self.bin_iou_threshold or inside_box:
                    is_inside_bin = True

                if bin_d <= max(150.0, 0.12 * frame_diag) or inside_box:
                    is_near_bin = True

            # 3. Phân tích quan hệ với Người (Person)
            nearest_person_id = None
            min_norm_dist = float("inf")
            min_euclid_dist = float("inf")
            is_near = False

            for person in people:
                pid = person.track_id
                _, person_h = get_box_dimensions(person.bbox)
                euclid_d = euclidean_distance(trash.center, person.center)
                norm_d = normalized_distance(euclid_d, person_h)
                box_d = box_to_box_distance(person.bbox, trash.bbox)

                near_flag = (norm_d <= self.near_distance_ratio) or (box_d <= max(12.0, 0.12 * person_h))

                if norm_d < min_norm_dist:
                    min_norm_dist = norm_d
                    min_euclid_dist = euclid_d
                    nearest_person_id = pid
                    is_near = near_flag

            # 4. Hồi quy vết không gian - thời gian (Spatio-Temporal Backtracking):
            # CHỈ áp dụng khi hiện tại KHÔNG có người nào ở gần (not is_near), rác mới xuất hiện
            # và kiểm tra xem trong vòng spatial_backtrack_sec vừa qua, có người nào từng đi qua tọa độ này không!
            if state.associated_person_id is None and not state.is_pre_existing and not is_near:
                # Quét lịch sử tất cả các người
                for pid_cand, hist_cand in history.tracks.items():
                    if hist_cand.class_name == "person":
                        t_cutoff = timestamp - self.spatial_backtrack_sec
                        for obs in hist_cand.observations:
                            # Chỉ xét các mốc quá khứ
                            if obs.timestamp >= t_cutoff and obs.timestamp < timestamp:
                                _, ph = get_box_dimensions(obs.bbox)
                                dist_obs = point_to_box_distance(trash.center, obs.bbox)
                                if dist_obs <= max(45.0, 0.35 * ph) or normalized_distance(dist_obs, ph) <= self.near_distance_ratio * 1.25:
                                    state.associated_person_id = pid_cand
                                    state.association_start_time = obs.timestamp
                                    state.consecutive_associated_seconds = self.min_association_seconds
                                    state.associated_via_backtracking = True
                                    break
                            if state.associated_person_id is not None:
                                break

            # 5. Logic Association tiêu chuẩn
            if not state.is_pre_existing:
                if state.associated_person_id is None:
                    if is_near and nearest_person_id is not None:
                        if state.association_start_time is None:
                            state.association_start_time = timestamp
                        state.consecutive_associated_seconds = timestamp - state.association_start_time
                        if state.consecutive_associated_seconds >= self.min_association_seconds:
                            state.associated_person_id = nearest_person_id
                    else:
                        state.association_start_time = None
                        state.consecutive_associated_seconds = 0.0
                else:
                    # Đã có người liên kết, cập nhật khoảng cách tới người đó nếu vẫn còn trong frame
                    person_obj = next((p for p in people if p.track_id == state.associated_person_id), None)
                    if person_obj is not None:
                        _, p_h = get_box_dimensions(person_obj.bbox)
                        cur_d = euclidean_distance(trash.center, person_obj.center)
                        cur_norm_d = normalized_distance(cur_d, p_h)
                        min_euclid_dist = cur_d
                        min_norm_dist = cur_norm_d
                        is_near = (cur_norm_d <= self.near_distance_ratio)

            is_associated = (state.associated_person_id is not None)
            assoc_dur = state.consecutive_associated_seconds

            status_text = "Unassociated"
            if state.is_pre_existing:
                status_text = "Pre-existing Trash"
            elif is_inside_bin:
                status_text = "Inside Trash Bin"
            elif is_near_bin:
                status_text = f"Near Bin #{nearest_bin_id}"
            elif is_associated:
                status_text = f"Associated with P#{state.associated_person_id}"

            relations.append(PersonTrashRelation(
                trash_id=tid,
                associated_person_id=state.associated_person_id,
                current_nearest_person_id=nearest_person_id,
                distance=min_euclid_dist if min_euclid_dist != float("inf") else 0.0,
                normalized_distance=min_norm_dist if min_norm_dist != float("inf") else 999.0,
                is_near=is_near,
                is_associated=is_associated,
                is_pre_existing=state.is_pre_existing,
                association_duration=assoc_dur,
                nearest_bin_id=nearest_bin_id,
                bin_distance=min_bin_dist if min_bin_dist != float("inf") else 999.0,
                is_inside_bin=is_inside_bin,
                is_near_bin=is_near_bin,
                associated_via_backtracking=state.associated_via_backtracking,
                status_text=status_text
            ))

        return relations

    def reset(self):
        """Reset toàn bộ trạng thái liên kết."""
        self.trash_states.clear()
