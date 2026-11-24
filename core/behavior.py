"""Module Máy trạng thái hữu hạn và Suy luận dựa trên Chuỗi bằng chứng (Behavior FSM + Evidence Chain).

Hiện thực hóa cỗ máy trạng thái:
  IDLE -> ASSOCIATED -> SEPARATED -> STATIONARY -> POSSIBLE_LITTERING (hoặc UNCERTAIN / CORRECT_DISPOSAL)

Nâng cấp Giai đoạn 1:
- Phân định 3 mức độ kết luận (DecisionLevel) dựa trên tính đầy đủ của chuỗi bằng chứng:
  1. CONFIRMED_LITTERING: Đủ bằng chứng thị giác trực tiếp qua cả 3 giai đoạn (Mang -> Tách rời -> Nằm yên ngoài thùng).
  2. SUSPICIOUS_NEED_REVIEW: Cần kiểm tra thêm (có giai đoạn bị che khuất hoặc liên kết qua truy vết ngược Backtracking).
  3. INSUFFICIENT_EVIDENCE: Không đủ căn cứ kết luận (rác không rõ nguồn gốc, thiếu lịch sử người mang).
- Lưu giữ chuỗi bằng chứng (EvidenceStage) kèm ảnh chụp (frame snapshot) tại từng mốc chuyển trạng thái
  để xuất Thẻ sự kiện nhiều ảnh (Multi-frame Event Card).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math

from core.association import PersonTrashRelation
from core.geometry import euclidean_distance, normalized_distance, get_box_dimensions
from core.history import TrackHistoryManager
from core.tracker import TrackedObject


class BehaviorState(str, Enum):
    IDLE = "IDLE"
    ASSOCIATED = "ASSOCIATED"
    SEPARATED = "SEPARATED"
    STATIONARY = "STATIONARY"
    POSSIBLE_LITTERING = "POSSIBLE_LITTERING"
    CORRECT_DISPOSAL = "CORRECT_DISPOSAL"
    UNCERTAIN = "UNCERTAIN"


class DecisionLevel(str, Enum):
    """3 mức độ kết luận theo tính đầy đủ của chuỗi bằng chứng thị giác."""
    CONFIRMED_LITTERING = "CONFIRMED_LITTERING"         # Đủ bằng chứng thị giác trực tiếp
    SUSPICIOUS_NEED_REVIEW = "SUSPICIOUS_NEED_REVIEW"   # Cần kiểm tra thêm (bị che khuất / Backtracking)
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"     # Không đủ căn cứ kết luận
    CORRECT_DISPOSAL = "CORRECT_DISPOSAL"               # Bỏ rác đúng vào thùng


@dataclass
class EvidenceStage:
    """Thông tin bằng chứng tại một giai đoạn trong chuỗi hành vi."""
    stage_name: str                             # 'ASSOCIATED', 'SEPARATED', 'STATIONARY'
    timestamp: float
    observed_directly: bool = True              # False nếu suy đoán gián tiếp / bị che khuất
    distance_to_person: Optional[float] = None
    bbox_person: Optional[List[float]] = None
    bbox_trash: Optional[List[float]] = None
    frame_snapshot: Optional[Any] = None        # Bản sao khung hình (np.ndarray) nếu có


@dataclass
class BehaviorEvent:
    """Sự kiện hành vi được trích xuất kèm chuỗi bằng chứng và mức độ kết luận."""
    event_id: str
    event_type: str                             # 'POSSIBLE_LITTERING', 'UNCERTAIN', hoặc 'CORRECT_DISPOSAL'
    timestamp: float
    person_id: Optional[int]
    trash_id: int
    evidence: List[str]                         # ['associated', 'separated', 'stationary', 'near_bin']
    status_message: str
    nearest_bin_id: Optional[int] = None
    bbox_person: Optional[List[float]] = None
    bbox_trash: Optional[List[float]] = None
    decision_level: str = DecisionLevel.CONFIRMED_LITTERING.value
    evidence_chain: List[EvidenceStage] = field(default_factory=list)


class TrashStateMachine:
    """Máy trạng thái cho từng vật thể rác cụ thể."""

    def __init__(self,
                 trash_id: int,
                 start_timestamp: float,
                 separation_ratio: float = 0.95,
                 min_stationary_sec: float = 0.6):
        self.trash_id = trash_id
        self.current_state = BehaviorState.IDLE
        self.associated_person_id: Optional[int] = None

        self.separation_ratio = separation_ratio
        self.min_stationary_sec = min_stationary_sec

        self.state_enter_timestamp: float = start_timestamp
        self.evidence_log: List[str] = []
        self.evidence_chain: List[EvidenceStage] = []
        self.has_alerted: bool = False

        self.associated_via_backtracking: bool = False
        self.separated_directly_observed: bool = True

        self.time_associated: Optional[float] = None
        self.time_separated: Optional[float] = None
        self.time_stationary: Optional[float] = None

        self.last_seen_timestamp: float = start_timestamp
        self.last_near_bin_id: Optional[int] = None
        self.last_bin_distance: float = 999.0
        self.last_trash_bbox: Optional[List[float]] = None
        self.last_person_bbox: Optional[List[float]] = None

    def change_state(self, new_state: BehaviorState, timestamp: float, evidence_tag: Optional[str] = None):
        """Chuyển trạng thái FSM."""
        self.current_state = new_state
        self.state_enter_timestamp = timestamp
        if evidence_tag and evidence_tag not in self.evidence_log:
            self.evidence_log.append(evidence_tag)

    def record_stage(self, stage: EvidenceStage):
        """Lưu thông tin bằng chứng cho một giai đoạn (tránh ghi trùng tên giai đoạn)."""
        for idx, existing in enumerate(self.evidence_chain):
            if existing.stage_name == stage.stage_name:
                self.evidence_chain[idx] = stage
                return
        self.evidence_chain.append(stage)


class BehaviorEngine:
    """Động cơ suy luận quy tắc, FSM và chuỗi bằng chứng cho toàn bộ các vật thể."""

    def __init__(self,
                 separation_distance_ratio: float = 0.95,
                 min_stationary_seconds: float = 0.6,
                 event_cooldown_seconds: float = 3.0):
        self.separation_distance_ratio = separation_distance_ratio
        self.min_stationary_seconds = min_stationary_seconds
        self.event_cooldown_seconds = event_cooldown_seconds

        self.fsm_map: Dict[int, TrashStateMachine] = {}
        self.event_counter: int = 1

    def update(self,
               objects: List[TrackedObject],
               relations: List[PersonTrashRelation],
               history: TrackHistoryManager,
               timestamp: float,
               frame_shape: Tuple[int, int] = (720, 1280),
               current_frame: Optional[Any] = None) -> List[BehaviorEvent]:
        """Cập nhật trạng thái FSM và chuỗi bằng chứng cho tất cả các đối tượng trong frame."""
        frame_h, frame_w = frame_shape
        frame_diag = math.hypot(frame_h, frame_w)

        obj_map = {obj.track_id: obj for obj in objects}
        new_events: List[BehaviorEvent] = []

        for rel in relations:
            tid = rel.trash_id
            trash_obj = obj_map.get(tid)
            if trash_obj is None:
                continue

            if tid not in self.fsm_map:
                self.fsm_map[tid] = TrashStateMachine(
                    trash_id=tid,
                    start_timestamp=timestamp,
                    separation_ratio=self.separation_distance_ratio,
                    min_stationary_sec=self.min_stationary_seconds
                )

            fsm = self.fsm_map[tid]
            trash_hist = history.get_track(tid)
            fsm.last_seen_timestamp = timestamp
            fsm.last_trash_bbox = list(trash_obj.bbox)
            if (rel.is_inside_bin or (rel.is_near_bin and rel.bin_distance <= 0.05 * frame_diag)) and rel.nearest_bin_id is not None:
                fsm.last_near_bin_id = rel.nearest_bin_id
                fsm.last_bin_distance = rel.bin_distance
            p_track_obj = obj_map.get(fsm.associated_person_id or rel.associated_person_id) if (fsm.associated_person_id or rel.associated_person_id) else None
            if p_track_obj is not None:
                fsm.last_person_bbox = list(p_track_obj.bbox)

            # Rác có sẵn từ đầu video -> Bỏ qua
            if rel.is_pre_existing:
                fsm.current_state = BehaviorState.IDLE
                continue

            # Rác nằm trọn vẹn trong thùng rác -> Đúng quy định (ghi nhận sự kiện CORRECT_DISPOSAL)
            if rel.is_inside_bin:
                fsm.current_state = BehaviorState.CORRECT_DISPOSAL
                if not fsm.has_alerted and (fsm.associated_person_id is not None or rel.is_associated):
                    pid = fsm.associated_person_id or rel.associated_person_id
                    fsm.has_alerted = True
                    p_obj = obj_map.get(pid) if pid else None
                    fsm.record_stage(EvidenceStage(
                        stage_name="STATIONARY",
                        timestamp=timestamp,
                        observed_directly=True,
                        distance_to_person=round(rel.normalized_distance, 3) if rel.normalized_distance < 999.0 else None,
                        bbox_person=list(p_obj.bbox) if p_obj else None,
                        bbox_trash=list(trash_obj.bbox),
                        frame_snapshot=current_frame.copy() if current_frame is not None else None
                    ))
                    event = BehaviorEvent(
                        event_id=f"EVT_{self.event_counter:04d}",
                        event_type=BehaviorState.CORRECT_DISPOSAL.value,
                        timestamp=timestamp,
                        person_id=pid,
                        trash_id=tid,
                        evidence=list(fsm.evidence_log) + ["inside_bin"],
                        status_message=f"Bỏ rác đúng nơi quy định: Người #{pid} bỏ vật thể #{tid} vào Thùng rác #{rel.nearest_bin_id}",
                        nearest_bin_id=rel.nearest_bin_id,
                        bbox_person=p_obj.bbox if p_obj else None,
                        bbox_trash=trash_obj.bbox,
                        decision_level=DecisionLevel.CORRECT_DISPOSAL.value,
                        evidence_chain=list(fsm.evidence_chain)
                    )
                    self.event_counter += 1
                    new_events.append(event)
                continue

            # FSM Transitions:
            # 1. IDLE -> ASSOCIATED hoặc UNCERTAIN
            if fsm.current_state == BehaviorState.IDLE:
                if rel.is_associated and rel.associated_person_id is not None:
                    fsm.associated_person_id = rel.associated_person_id
                    fsm.time_associated = timestamp
                    fsm.associated_via_backtracking = rel.associated_via_backtracking
                    tag = "associated_backtrack" if rel.associated_via_backtracking else "associated"
                    fsm.change_state(BehaviorState.ASSOCIATED, timestamp, "associated")
                    if rel.associated_via_backtracking and tag not in fsm.evidence_log:
                        fsm.evidence_log.append(tag)

                    person_obj = obj_map.get(rel.associated_person_id)
                    fsm.record_stage(EvidenceStage(
                        stage_name="ASSOCIATED",
                        timestamp=timestamp,
                        observed_directly=not rel.associated_via_backtracking,
                        distance_to_person=round(rel.normalized_distance, 3),
                        bbox_person=list(person_obj.bbox) if person_obj else None,
                        bbox_trash=list(trash_obj.bbox),
                        frame_snapshot=current_frame.copy() if current_frame is not None else None
                    ))
                else:
                    if trash_hist and trash_hist.duration_seen > 1.0 and trash_hist.is_stationary(min_duration=0.6, frame_diag=frame_diag):
                        if not fsm.has_alerted:
                            fsm.change_state(BehaviorState.UNCERTAIN, timestamp, "uncertain_origin")
                            p_cand = obj_map.get(rel.current_nearest_person_id) if rel.current_nearest_person_id else None
                            stage_final = EvidenceStage(
                                stage_name="STATIONARY",
                                timestamp=timestamp,
                                observed_directly=False,
                                distance_to_person=round(rel.normalized_distance, 3),
                                bbox_person=list(p_cand.bbox) if p_cand else None,
                                bbox_trash=list(trash_obj.bbox),
                                frame_snapshot=current_frame.copy() if current_frame is not None else None
                            )
                            fsm.record_stage(stage_final)
                            event = BehaviorEvent(
                                event_id=f"EVT_{self.event_counter:04d}",
                                event_type=BehaviorState.UNCERTAIN.value,
                                timestamp=timestamp,
                                person_id=rel.current_nearest_person_id,
                                trash_id=tid,
                                evidence=["uncertain_origin", "stationary"],
                                status_message="Không đủ căn cứ kết luận: Rác mới xuất hiện nhưng thiếu lịch sử người mang",
                                nearest_bin_id=rel.nearest_bin_id,
                                bbox_person=p_cand.bbox if p_cand else None,
                                bbox_trash=trash_obj.bbox,
                                decision_level=DecisionLevel.INSUFFICIENT_EVIDENCE.value,
                                evidence_chain=list(fsm.evidence_chain)
                            )
                            self.event_counter += 1
                            fsm.has_alerted = True
                            new_events.append(event)

            # 2. ASSOCIATED -> SEPARATED
            elif fsm.current_state == BehaviorState.ASSOCIATED:
                person_id = fsm.associated_person_id
                person_obj = obj_map.get(person_id) if person_id else None

                separated = False
                direct_sep = True
                norm_d = 999.0
                if person_obj is not None:
                    _, p_h = get_box_dimensions(person_obj.bbox)
                    d = euclidean_distance(trash_obj.center, person_obj.center)
                    norm_d = normalized_distance(d, p_h)
                    if norm_d >= self.separation_distance_ratio:
                        separated = True
                        direct_sep = True
                else:
                    # Người đã rời khỏi khung hình hoặc bị che khuất hoàn toàn
                    separated = True
                    direct_sep = False

                if separated:
                    fsm.time_separated = timestamp
                    fsm.separated_directly_observed = direct_sep
                    fsm.change_state(BehaviorState.SEPARATED, timestamp, "separated")
                    fsm.record_stage(EvidenceStage(
                        stage_name="SEPARATED",
                        timestamp=timestamp,
                        observed_directly=direct_sep and (not fsm.associated_via_backtracking),
                        distance_to_person=round(norm_d, 3) if norm_d < 999.0 else None,
                        bbox_person=list(person_obj.bbox) if person_obj else None,
                        bbox_trash=list(trash_obj.bbox),
                        frame_snapshot=current_frame.copy() if current_frame is not None else None
                    ))

            # 3. SEPARATED -> STATIONARY
            elif fsm.current_state == BehaviorState.SEPARATED:
                time_since_sep = timestamp - (fsm.time_separated if fsm.time_separated is not None else timestamp)
                if time_since_sep >= self.min_stationary_seconds:
                    if trash_hist and trash_hist.is_stationary(min_duration=self.min_stationary_seconds,
                                                               frame_diag=frame_diag):
                        fsm.time_stationary = timestamp
                        fsm.change_state(BehaviorState.STATIONARY, timestamp, "stationary")
                        person_id = fsm.associated_person_id
                        person_obj = obj_map.get(person_id) if person_id else None
                        fsm.record_stage(EvidenceStage(
                            stage_name="STATIONARY",
                            timestamp=timestamp,
                            observed_directly=True,
                            distance_to_person=round(rel.normalized_distance, 3) if rel.normalized_distance < 999.0 else None,
                            bbox_person=list(person_obj.bbox) if person_obj else None,
                            bbox_trash=list(trash_obj.bbox),
                            frame_snapshot=current_frame.copy() if current_frame is not None else None
                        ))

            # 4. STATIONARY -> POSSIBLE_LITTERING (phân định 2 mức: CONFIRMED vs SUSPICIOUS_NEED_REVIEW)
            elif fsm.current_state == BehaviorState.STATIONARY:
                if not fsm.has_alerted:
                    fsm.change_state(BehaviorState.POSSIBLE_LITTERING, timestamp, "littering_confirmed")
                    fsm.has_alerted = True

                    person_id = fsm.associated_person_id
                    person_obj = obj_map.get(person_id) if person_id else None

                    # Đánh giá mức độ đầy đủ của chuỗi bằng chứng (Sáng kiến 1)
                    has_direct_chain = (
                        not fsm.associated_via_backtracking
                        and fsm.separated_directly_observed
                    )
                    if has_direct_chain:
                        decision_level = DecisionLevel.CONFIRMED_LITTERING.value
                        prefix_msg = "Đủ bằng chứng thị giác"
                    else:
                        decision_level = DecisionLevel.SUSPICIOUS_NEED_REVIEW.value
                        prefix_msg = "Cần kiểm tra thêm (có che khuất/truy vết ngược)"

                    evidence_tags = list(fsm.evidence_log)
                    if rel.is_near_bin:
                        evidence_tags.append("near_bin")
                        status_msg = f"{prefix_msg}: Người #{person_id} bỏ lại vật thể #{tid} gần Thùng rác #{rel.nearest_bin_id}"
                    else:
                        status_msg = f"{prefix_msg}: Người #{person_id} bỏ lại vật thể #{tid}"

                    event = BehaviorEvent(
                        event_id=f"EVT_{self.event_counter:04d}",
                        event_type=BehaviorState.POSSIBLE_LITTERING.value,
                        timestamp=timestamp,
                        person_id=person_id,
                        trash_id=tid,
                        evidence=evidence_tags,
                        status_message=status_msg,
                        nearest_bin_id=rel.nearest_bin_id,
                        bbox_person=person_obj.bbox if person_obj else None,
                        bbox_trash=trash_obj.bbox,
                        decision_level=decision_level,
                        evidence_chain=list(fsm.evidence_chain)
                    )
                    self.event_counter += 1
                    new_events.append(event)

        # Nhánh In-Flight / Disappearance-in-Bin:
        # Nếu vật thể đang ASSOCIATED hoặc SEPARATED vừa biến mất >= 0.35s ngay tại vùng thùng rác
        active_trash_ids = {rel.trash_id for rel in relations}
        for tid, fsm in self.fsm_map.items():
            if tid in active_trash_ids or fsm.has_alerted:
                continue
            if fsm.current_state in (BehaviorState.ASSOCIATED, BehaviorState.SEPARATED):
                if fsm.last_near_bin_id is not None and (timestamp - fsm.last_seen_timestamp) >= 0.35:
                    fsm.change_state(BehaviorState.CORRECT_DISPOSAL, timestamp, "disappeared_in_bin")
                    fsm.has_alerted = True
                    pid = fsm.associated_person_id
                    event = BehaviorEvent(
                        event_id=f"EVT_{self.event_counter:04d}",
                        event_type=BehaviorState.CORRECT_DISPOSAL.value,
                        timestamp=timestamp,
                        person_id=pid,
                        trash_id=tid,
                        evidence=list(fsm.evidence_log) + ["disappeared_in_bin"],
                        status_message=f"Bỏ rác đúng nơi quy định: Người #{pid} bỏ vật thể #{tid} vào Thùng rác #{fsm.last_near_bin_id}",
                        nearest_bin_id=fsm.last_near_bin_id,
                        bbox_person=fsm.last_person_bbox,
                        bbox_trash=fsm.last_trash_bbox,
                        decision_level=DecisionLevel.CORRECT_DISPOSAL.value,
                        evidence_chain=list(fsm.evidence_chain)
                    )
                    self.event_counter += 1
                    new_events.append(event)

        return new_events

    def get_fsm_state(self, trash_id: int) -> BehaviorState:
        """Lấy trạng thái hiện tại của một vật thể rác."""
        if trash_id in self.fsm_map:
            return self.fsm_map[trash_id].current_state
        return BehaviorState.IDLE

    def reset(self):
        """Reset toàn bộ FSM khi chuyển video."""
        self.fsm_map.clear()
        self.event_counter = 1
