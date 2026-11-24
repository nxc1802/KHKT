"""Module vẽ và trực quan hóa (Visualization & HUD Overlay).

Nhiệm vụ:
- Vẽ Bounding Box phân biệt màu sắc giữa:
  1. Người (Neon Green)
  2. Rác (Mã màu động theo trạng thái FSM)
  3. Thùng rác (Cyan/Blue nổi bật)
- Hiển thị Track ID, Confidence, và Trạng thái hành vi.
- Vẽ quỹ đạo chuyển động (Trajectory trails) mượt mà.
- Vẽ đường liên kết giữa Người và Rác khi đang ở pha ASSOCIATED / NEAR.
- Hiển thị HUD thông số hệ thống (Thời gian, FPS, số lượng Người, Rác và Thùng rác).
- Hiển thị Banner cảnh báo nổi bật khi phát hiện vi phạm xả rác.
"""

from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np

from core.association import PersonTrashRelation
from core.behavior import BehaviorEvent, BehaviorState, BehaviorEngine
from core.history import TrackHistoryManager
from core.tracker import TrackedObject


# Bảng màu trực quan BGR
COLOR_PERSON = (0, 230, 115)           # Xanh lá neon
COLOR_BIN = (255, 180, 0)              # Xanh lam cyan nổi bật
COLOR_ASSOCIATION_LINE = (0, 215, 255) # Vàng cam

COLOR_FSM_MAP = {
    BehaviorState.IDLE: (0, 255, 255),               # Vàng
    BehaviorState.ASSOCIATED: (0, 165, 255),         # Cam
    BehaviorState.SEPARATED: (255, 0, 255),          # Tím hồng
    BehaviorState.STATIONARY: (0, 0, 200),           # Đỏ sẫm
    BehaviorState.POSSIBLE_LITTERING: (0, 0, 255),   # Đỏ tươi
    BehaviorState.CORRECT_DISPOSAL: (0, 200, 0),     # Xanh lục
    BehaviorState.UNCERTAIN: (140, 180, 210),        # Vàng xám
}
COLOR_PRE_EXISTING = (160, 160, 160)                 # Xám tro


class Visualizer:
    """Trực quan hóa toàn bộ thông tin lên frame video."""

    def __init__(self,
                 draw_boxes: bool = True,
                 draw_trajectories: bool = True,
                 draw_status_panel: bool = True):
        self.draw_boxes = draw_boxes
        self.draw_trajectories = draw_trajectories
        self.draw_status_panel = draw_status_panel

        self._active_alert_message: Optional[str] = None
        self._alert_expire_timestamp: float = 0.0

    def trigger_alert_banner(self, message: str, timestamp: float, duration: float = 3.0):
        """Kích hoạt banner cảnh báo trên màn hình trong duration giây."""
        self._active_alert_message = message
        self._alert_expire_timestamp = timestamp + duration

    def draw(self,
             frame: np.ndarray,
             objects: List[TrackedObject],
             relations: List[PersonTrashRelation],
             history: TrackHistoryManager,
             behavior_engine: BehaviorEngine,
             timestamp: float,
             fps: float = 30.0) -> np.ndarray:
        """Vẽ các lớp overlay lên frame."""
        vis = frame.copy()
        h, w = vis.shape[:2]

        obj_map = {obj.track_id: obj for obj in objects}
        rel_map = {rel.trash_id: rel for rel in relations}

        # 1. Vẽ Trajectory trails
        if self.draw_trajectories:
            for obj in objects:
                if obj.class_name == "trash_bin":
                    continue
                hist = history.get_track(obj.track_id)
                if hist:
                    trail = hist.get_trajectory(max_points=25)
                    trail_color = COLOR_PERSON if obj.class_name == "person" else (0, 200, 255)
                    for k in range(1, len(trail)):
                        pt1 = (int(trail[k - 1][0]), int(trail[k - 1][1]))
                        pt2 = (int(trail[k][0]), int(trail[k][1]))
                        thickness = max(1, int(k * 2 / len(trail)))
                        cv2.line(vis, pt1, pt2, trail_color, thickness, cv2.LINE_AA)

        # 2. Vẽ đường nối liên kết Person - Trash
        for rel in relations:
            trash_obj = obj_map.get(rel.trash_id)
            if not trash_obj:
                continue

            target_pid = rel.associated_person_id or (rel.current_nearest_person_id if rel.is_near else None)
            if target_pid and target_pid in obj_map:
                p_obj = obj_map[target_pid]
                pt_p = (int(p_obj.center[0]), int(p_obj.center[1]))
                pt_t = (int(trash_obj.center[0]), int(trash_obj.center[1]))
                cv2.line(vis, pt_p, pt_t, COLOR_ASSOCIATION_LINE, 2, cv2.LINE_AA)
                mid_x = (pt_p[0] + pt_t[0]) // 2
                mid_y = (pt_p[1] + pt_t[1]) // 2
                label_dist = f"d_norm: {rel.normalized_distance:.2f}"
                cv2.putText(vis, label_dist, (mid_x, mid_y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_ASSOCIATION_LINE, 1, cv2.LINE_AA)

        # 3. Vẽ Bounding Boxes & Labels
        if self.draw_boxes:
            for obj in objects:
                x1, y1, x2, y2 = [int(v) for v in obj.bbox]

                if obj.class_name == "person":
                    box_color = COLOR_PERSON
                    label = f"Nguoi #{obj.track_id} ({obj.confidence:.2f})"
                elif obj.class_name == "trash_bin":
                    box_color = COLOR_BIN
                    label = f"Thung rac #{obj.track_id} ({obj.confidence:.2f})"
                else:
                    rel = rel_map.get(obj.track_id)
                    fsm_state = behavior_engine.get_fsm_state(obj.track_id)

                    if rel and rel.is_pre_existing:
                        box_color = COLOR_PRE_EXISTING
                        label = f"Rac #{obj.track_id} [PRE-EXISTING]"
                    elif rel and rel.is_inside_bin:
                        box_color = COLOR_FSM_MAP[BehaviorState.CORRECT_DISPOSAL]
                        label = f"Rac #{obj.track_id} [TRONG THUNG]"
                    else:
                        box_color = COLOR_FSM_MAP.get(fsm_state, (0, 255, 255))
                        state_str = fsm_state.value
                        if rel and rel.is_near_bin:
                            state_str += "-CANH THUNG"
                        label = f"Rac #{obj.track_id} [{state_str}]"

                # Vẽ viền box
                thickness = 3 if obj.class_name == "trash_bin" else 2
                cv2.rectangle(vis, (x1, y1), (x2, y2), box_color, thickness)

                # Vẽ background nhãn
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                label_y1 = max(0, y1 - th - 6)
                label_y2 = y1
                cv2.rectangle(vis, (x1, label_y1), (x1 + tw + 6, label_y2), box_color, -1)
                text_color = (0, 0, 0) if obj.class_name != "trash_bin" else (255, 255, 255)
                cv2.putText(vis, label, (x1 + 3, y1 - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        # 4. HUD Status Panel (Góc trên bên trái)
        if self.draw_status_panel:
            num_people = sum(1 for o in objects if o.class_name == "person")
            num_trash = sum(1 for o in objects if o.class_name == "trash")
            num_bins = sum(1 for o in objects if o.class_name == "trash_bin")

            panel_w = 380
            panel_h = 100
            overlay = vis.copy()
            cv2.rectangle(overlay, (10, 10), (10 + panel_w, 10 + panel_h), (25, 25, 25), -1)
            cv2.addWeighted(overlay, 0.75, vis, 0.25, 0, vis)
            cv2.rectangle(vis, (10, 10), (10 + panel_w, 10 + panel_h), (80, 80, 80), 1)

            cv2.putText(vis, "AI LITTERING DETECTION SYSTEM", (20, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(vis, f"Time: {timestamp:05.2f}s | FPS: {fps:.1f}", (20, 56),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
            cv2.putText(vis, f"Tracks: Nguoi ({num_people}) | Rac ({num_trash}) | Thung rac ({num_bins})", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

        # 5. Alert Banner (khi có sự kiện xả rác)
        if self._active_alert_message and timestamp < self._alert_expire_timestamp:
            banner_h = 55
            overlay = vis.copy()
            cv2.rectangle(overlay, (0, h - banner_h), (w, h), (0, 0, 220), -1)
            cv2.addWeighted(overlay, 0.85, vis, 0.15, 0, vis)
            cv2.putText(vis, f"ALERT: {self._active_alert_message}", (25, h - 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        return vis
