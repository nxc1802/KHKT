"""Công cụ sinh video mô phỏng hành vi (Synthetic Video Generator).

Sinh ra video thử nghiệm với các tình huống chuẩn để đánh giá hệ thống:
1. Scenario A (True Positive): Người cầm chai nước đi từ trái sang phải, thả chai nước xuống đất rồi bước tiếp rời đi -> Hệ thống phải phát hiện POSSIBLE_LITTERING.
2. Scenario B (Negative Control): Rác có sẵn từ đầu video, một người khác đi ngang qua -> Hệ thống KHÔNG được báo người này xả rác (Pre-existing trash filter).
"""

import os
from typing import Tuple
import cv2
import numpy as np


def draw_human_figure(canvas: np.ndarray,
                      center_x: int,
                      ground_y: int,
                      height: int = 140,
                      color: Tuple[int, int, int] = (180, 100, 50)):
    """Vẽ hình nhân vật đơn giản lên canvas."""
    head_radius = int(height * 0.12)
    head_center = (center_x, ground_y - height + head_radius)
    cv2.circle(canvas, head_center, head_radius, (200, 180, 160), -1)

    # Thân mình
    body_top = head_center[1] + head_radius
    body_bottom = ground_y - int(height * 0.45)
    body_w = int(height * 0.22)
    cv2.rectangle(canvas, (center_x - body_w // 2, body_top), (center_x + body_w // 2, body_bottom), color, -1)

    # Chân
    leg_w = int(body_w * 0.35)
    cv2.rectangle(canvas, (center_x - body_w // 2, body_bottom), (center_x - body_w // 2 + leg_w, ground_y), (40, 40, 40), -1)
    cv2.rectangle(canvas, (center_x + body_w // 2 - leg_w, body_bottom), (center_x + body_w // 2, ground_y), (40, 40, 40), -1)

    # Tay
    hand_y = body_top + int((body_bottom - body_top) * 0.7)
    hand_x = center_x + body_w // 2 + 10
    cv2.line(canvas, (center_x + body_w // 2 - 5, body_top + 10), (hand_x, hand_y), color, 4)
    return hand_x, hand_y


def draw_bottle(canvas: np.ndarray,
                center_x: int,
                center_y: int,
                width: int = 18,
                height: int = 40,
                color: Tuple[int, int, int] = (220, 150, 0)):
    """Vẽ chai nước hoặc lon nước lên canvas."""
    x1 = int(center_x - width // 2)
    y1 = int(center_y - height // 2)
    x2 = int(center_x + width // 2)
    y2 = int(center_y + height // 2)
    # Thân chai
    cv2.rectangle(canvas, (x1, y1 + 8), (x2, y2), color, -1)
    cv2.rectangle(canvas, (x1, y1 + 8), (x2, y2), (255, 255, 255), 1)
    # Nắp chai
    cv2.rectangle(canvas, (center_x - width // 4, y1), (center_x + width // 4, y1 + 8), (0, 0, 200), -1)


def generate_synthetic_littering_video(output_path: str = "inputs/sample_littering_test.mp4",
                                       width: int = 1280,
                                       height: int = 720,
                                       fps: float = 30.0,
                                       duration_sec: float = 8.0):
    """Tạo video giả lập có kịch bản xả rác rõ ràng."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    total_frames = int(fps * duration_sec)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    ground_y = 550
    person_h = 160

    # Lộ trình nhân vật 1 (Xả rác): Đi từ x=100 đến x=1150
    # Thả chai tại frame 90 (khoảng giây 3.0, tại x=480)
    drop_frame = int(fps * 3.0)
    drop_x = 480
    dropped_bottle_pos = None

    # Nhân vật 2 (Negative control): Đi từ phải sang trái qua chai nước có sẵn
    p2_start_frame = int(fps * 4.5)

    print(f"[SyntheticGenerator] Đang tạo video kiểm thử: '{output_path}' ({total_frames} frames)...")

    for f in range(total_frames):
        # Nền đường phố / vỉa hè
        frame = np.full((height, width, 3), 235, dtype=np.uint8)

        # Mặt đường
        cv2.rectangle(frame, (0, ground_y), (width, height), (75, 75, 75), -1)
        # Vạch kẻ đường
        for vx in range(50, width, 120):
            cv2.rectangle(frame, (vx, ground_y + 60), (vx + 60, ground_y + 75), (255, 255, 255), -1)
        # Bãi cỏ lề đường
        cv2.rectangle(frame, (0, ground_y - 20), (width, ground_y), (60, 140, 60), -1)

        t = f / fps

        # Nhân vật 1:
        if t < 5.5:
            p1_x = int(100 + (t / 5.5) * 900)
            hx, hy = draw_human_figure(frame, p1_x, ground_y, height=person_h, color=(160, 80, 40))

            if f < drop_frame:
                # Chai nước cầm trên tay
                draw_bottle(frame, hx, hy)
            elif f == drop_frame:
                # Rơi xuống đất
                dropped_bottle_pos = (hx, ground_y - 15)
                draw_bottle(frame, dropped_bottle_pos[0], dropped_bottle_pos[1])
        
        # Chai nước sau khi đã bị thả rơi nằm yên trên bãi cỏ
        if dropped_bottle_pos is not None:
            draw_bottle(frame, dropped_bottle_pos[0], dropped_bottle_pos[1])

        # Nhân vật 2: Đi ngang qua chai nước có sẵn
        if f >= p2_start_frame:
            t2 = (f - p2_start_frame) / fps
            p2_x = int(1150 - (t2 / 3.0) * 1000)
            draw_human_figure(frame, p2_x, ground_y, height=person_h, color=(40, 90, 160))

        # Viết text chú thích kịch bản góc trên bên phải
        info_text = f"Synthetic Test Video | Frame: {f}/{total_frames} | Time: {t:.2f}s"
        cv2.putText(frame, info_text, (width - 480, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 1)

        writer.write(frame)

    writer.release()
    print(f"[SyntheticGenerator] Đã tạo thành công: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_synthetic_littering_video()
