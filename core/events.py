"""Module quản lý sự kiện, chống trùng lặp, xuất JSON và Thẻ sự kiện đa khung hình.

Nâng cấp Giai đoạn 1:
- Lưu Thẻ sự kiện nhiều ảnh (Multi-frame Event Card: Trước sự kiện -> Tách rời -> Sau sự kiện)
  thay cho 1 ảnh cảnh báo đơn lẻ, giúp giáo viên và ban giám khảo quan sát rõ toàn bộ diễn biến.
- Tự động làm mờ khuôn mặt học sinh trên tất cả các khung hình bằng chứng.
- Xuất JSON đầy đủ mức độ kết luận (decision_level) và chuỗi bằng chứng theo mốc thời gian.
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any
import cv2
import numpy as np

from core.behavior import BehaviorEvent, DecisionLevel, EvidenceStage


class EventManager:
    """Quản lý, lưu trữ, chống trùng lặp sự kiện và tạo Thẻ sự kiện 3 ảnh."""

    def __init__(self,
                 output_events_dir: str = "outputs/events",
                 output_evidence_dir: str = "outputs/evidence",
                 cooldown_seconds: float = 3.0):
        self.output_events_dir = output_events_dir
        self.output_evidence_dir = output_evidence_dir
        self.cooldown_seconds = cooldown_seconds

        os.makedirs(output_events_dir, exist_ok=True)
        os.makedirs(output_evidence_dir, exist_ok=True)

        self.confirmed_events: List[Dict[str, Any]] = []
        # Key: (person_id, trash_id) -> last alert timestamp
        self._last_alert_map: Dict[Tuple[Optional[int], int], float] = {}
        self.prefix: str = ""

    def set_prefix(self, prefix: str):
        """Đặt tiền tố cho file bằng chứng theo video."""
        self.prefix = prefix

    def filter_and_record(self,
                          raw_events: List[BehaviorEvent],
                          current_frame: np.ndarray,
                          save_evidence: bool = True) -> List[BehaviorEvent]:
        """Lọc sự kiện qua bộ chống trùng lặp, lưu ảnh bằng chứng và Thẻ sự kiện nếu cần."""
        valid_events: List[BehaviorEvent] = []

        for evt in raw_events:
            key = (evt.person_id, evt.event_type) if evt.person_id is not None else (None, evt.trash_id)
            last_time = self._last_alert_map.get(key)

            if last_time is not None and (evt.timestamp - last_time) < self.cooldown_seconds:
                continue

            self._last_alert_map[key] = evt.timestamp
            valid_events.append(evt)

            evidence_filename = f"{self.prefix}_{evt.event_id}.jpg" if self.prefix else f"{evt.event_id}.jpg"
            evidence_rel_path = os.path.join(self.output_evidence_dir, evidence_filename)

            card_filename = f"{self.prefix}_{evt.event_id}_card.jpg" if self.prefix else f"{evt.event_id}_card.jpg"
            card_rel_path = os.path.join(self.output_evidence_dir, card_filename)
            has_card = False

            if save_evidence:
                self._save_evidence_image(current_frame, evt, evidence_rel_path)
                has_card = self._save_event_card(current_frame, evt, card_rel_path)

            chain_summary = [
                {
                    "stage": s.stage_name,
                    "timestamp": round(s.timestamp, 2),
                    "observed_directly": s.observed_directly,
                    "distance_to_person": s.distance_to_person
                }
                for s in evt.evidence_chain
            ]

            event_record = {
                "event_id": evt.event_id,
                "event_type": evt.event_type,
                "decision_level": evt.decision_level,
                "timestamp": round(evt.timestamp, 2),
                "person_id": evt.person_id,
                "trash_id": evt.trash_id,
                "evidence": evt.evidence,
                "evidence_chain": chain_summary,
                "status_message": evt.status_message,
                "evidence_image": evidence_filename if save_evidence else None,
                "event_card_image": card_filename if (save_evidence and has_card) else None,
                "bbox_person": [round(x, 1) for x in evt.bbox_person] if evt.bbox_person else None,
                "bbox_trash": [round(x, 1) for x in evt.bbox_trash] if evt.bbox_trash else None
            }
            self.confirmed_events.append(event_record)

        return valid_events

    @staticmethod
    def _anonymize_and_draw_boxes(frame: np.ndarray,
                                  bbox_person: Optional[List[float]],
                                  bbox_trash: Optional[List[float]],
                                  person_id: Optional[int],
                                  trash_id: int,
                                  trash_color: Tuple[int, int, int] = (0, 0, 255)) -> np.ndarray:
        """Làm mờ vùng mặt người và vẽ khung bao Người + Rác."""
        vis = frame.copy()
        h, w = vis.shape[:2]

        if bbox_person:
            x1, y1, x2, y2 = [int(v) for v in bbox_person]
            head_h = max(15, int((y2 - y1) * 0.28))
            face_y2 = min(y2, y1 + head_h)
            clip_x1, clip_x2 = max(0, x1), min(w, x2)
            clip_y1, clip_y2 = max(0, y1), min(h, face_y2)

            if clip_x2 > clip_x1 and clip_y2 > clip_y1:
                face_roi = vis[clip_y1:clip_y2, clip_x1:clip_x2]
                if face_roi.size > 0:
                    kw = max(15, (face_roi.shape[1] // 2 * 2 + 1))
                    kh = max(15, (face_roi.shape[0] // 2 * 2 + 1))
                    vis[clip_y1:clip_y2, clip_x1:clip_x2] = cv2.GaussianBlur(face_roi, (kw, kh), 25)

            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 140, 255), 3)
            label_p = f"Person #{person_id} (Anonymized)" if person_id is not None else "Person (Anonymized)"
            cv2.putText(vis, label_p, (x1, max(25, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 140, 255), 2)

        if bbox_trash:
            x1, y1, x2, y2 = [int(v) for v in bbox_trash]
            cv2.rectangle(vis, (x1, y1), (x2, y2), trash_color, 3)
            cv2.putText(vis, f"Trash #{trash_id}", (x1, max(25, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, trash_color, 2)

        return vis

    def _save_evidence_image(self, frame: np.ndarray, evt: BehaviorEvent, filepath: str):
        """Lưu ảnh bằng chứng đơn tại thời điểm xác nhận sự kiện (đã làm mờ mặt)."""
        trash_color = (0, 0, 255) if evt.event_type == "POSSIBLE_LITTERING" else (0, 255, 255)
        vis = self._anonymize_and_draw_boxes(
            frame, evt.bbox_person, evt.bbox_trash, evt.person_id, evt.trash_id, trash_color
        )
        w = vis.shape[1]

        if evt.decision_level == DecisionLevel.CONFIRMED_LITTERING.value:
            banner_color = (0, 0, 200)
        elif evt.decision_level == DecisionLevel.SUSPICIOUS_NEED_REVIEW.value:
            banner_color = (0, 140, 230)
        else:
            banner_color = (0, 160, 160)

        cv2.rectangle(vis, (0, 0), (w, 50), banner_color, -1)
        title_text = f"EVIDENCE [{evt.decision_level}]: {evt.event_id} at {evt.timestamp:.2f}s"
        cv2.putText(vis, title_text, (20, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.78, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imwrite(filepath, vis)

    def _save_event_card(self, current_frame: np.ndarray, evt: BehaviorEvent, filepath: str) -> bool:
        """Tạo Thẻ sự kiện nhiều ảnh (3 giai đoạn: Trước -> Tách rời -> Sau sự kiện)."""
        stage_map: Dict[str, EvidenceStage] = {s.stage_name: s for s in evt.evidence_chain}
        if not stage_map:
            return False

        target_h = 360
        orig_h, orig_w = current_frame.shape[:2]
        target_w = max(240, int(orig_w * (target_h / max(1, orig_h))))

        stage_specs = [
            ("ASSOCIATED", "[1] TRUOC: Mang/gan nguoi", (80, 220, 80)),
            ("SEPARATED", "[2] TACH ROI: Roi khoi nguoi", (0, 200, 255)),
            ("STATIONARY", "[3] SAU: Nam lai ngoai thung", (0, 80, 255)),
        ]

        panels: List[np.ndarray] = []
        for stage_key, title_prefix, color in stage_specs:
            stage = stage_map.get(stage_key)
            if stage is not None and stage.frame_snapshot is not None:
                annotated = self._anonymize_and_draw_boxes(
                    stage.frame_snapshot,
                    stage.bbox_person,
                    stage.bbox_trash,
                    evt.person_id,
                    evt.trash_id,
                    trash_color=color
                )
                panel = cv2.resize(annotated, (target_w, target_h))
                obs_tag = "Truc tiep" if stage.observed_directly else "Che khuat/Backtrack"
                caption = f"{title_prefix} | {stage.timestamp:.2f}s ({obs_tag})"
            else:
                # Khung báo thiếu bằng chứng trực tiếp
                panel = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                panel[:] = (45, 45, 50)
                cv2.putText(panel, "THIEU BANG CHUNG TRUC TIEP", (20, target_h // 2 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 255), 2, cv2.LINE_AA)
                cv2.putText(panel, "(Che khuat / Khong quan sat ro)", (20, target_h // 2 + 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
                caption = f"{title_prefix} | Khong co du lieu"

            # Thanh tiêu đề cho từng ảnh con
            bar_h = 36
            bar = np.zeros((bar_h, target_w, 3), dtype=np.uint8)
            bar[:] = (25, 25, 25)
            cv2.putText(bar, caption, (8, 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
            panel_with_bar = np.vstack([bar, panel])
            # Viền trắng mỏng ngăn cách giữa các khung
            panel_bordered = cv2.copyMakeBorder(panel_with_bar, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(220, 220, 220))
            panels.append(panel_bordered)

        strip = np.hstack(panels)
        total_w = strip.shape[1]

        # Header tổng hợp Thẻ sự kiện
        header_h = 68
        header = np.zeros((header_h, total_w, 3), dtype=np.uint8)
        if evt.decision_level == DecisionLevel.CONFIRMED_LITTERING.value:
            header[:] = (35, 35, 130)
            verdict_text = "KET LUAN: DU BANG CHUNG THI GIAC (CONFIRMED_LITTERING)"
        elif evt.decision_level == DecisionLevel.SUSPICIOUS_NEED_REVIEW.value:
            header[:] = (20, 95, 175)
            verdict_text = "KET LUAN: CAN KIEM TRA THEM (SUSPICIOUS_NEED_REVIEW)"
        else:
            header[:] = (80, 80, 80)
            verdict_text = "KET LUAN: KHONG DU CAN CU (INSUFFICIENT_EVIDENCE)"

        cv2.putText(header, f"THE SU KIEN (EVENT CARD): {evt.event_id} | Nguoi #{evt.person_id} -> Rac #{evt.trash_id} | Moc: {evt.timestamp:.2f}s",
                    (16, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(header, verdict_text,
                    (16, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (235, 255, 235), 2, cv2.LINE_AA)

        card = np.vstack([header, strip])
        cv2.imwrite(filepath, card)
        return True

    def export_json(self, output_path: str):
        """Xuất danh sách sự kiện ra file JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "total_events": len(self.confirmed_events),
                "events": self.confirmed_events
            }, f, indent=2, ensure_ascii=False)
        print(f"[EventManager] Exported {len(self.confirmed_events)} events to '{output_path}'")

    def reset(self):
        """Reset bộ nhớ sự kiện."""
        self.confirmed_events.clear()
        self._last_alert_map.clear()
