"""Script xử lý hàng loạt tất cả các video trong inputs/."""

import os
import sys
import glob
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.video_processor import VideoProcessor


def run_batch():
    processor = VideoProcessor(config_path="config.yaml")
    video_files = sorted(glob.glob("inputs/sample_*.mp4"))

    print(f"\n=======================================================")
    print(f"  BẮT ĐẦU CHẠY BATCH TOÀN BỘ {len(video_files)} VIDEO TRONG inputs/")
    print(f"=======================================================\n")

    summaries = []
    total_start = time.time()

    for idx, video_path in enumerate(video_files, 1):
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_video = os.path.join("outputs/videos", f"{base_name}_annotated.mp4")
        events_json = os.path.join("outputs/events", f"{base_name}_events.json")

        print(f"\n[{idx}/{len(video_files)}] Đang xử lý: {video_path}")
        start_v = time.time()
        try:
            summary = processor.process_video(
                video_path=video_path,
                output_video_path=output_video,
                events_json_path=events_json,
                show_progress=True
            )
            summaries.append(summary)
        except Exception as e:
            print(f"  [LỖI] Không thể xử lý {video_path}: {e}")
            import traceback
            traceback.print_exc()

    total_elapsed = time.time() - total_start
    print(f"\n=======================================================")
    print(f"  HOÀN THÀNH XỬ LÝ TOÀN BỘ {len(summaries)}/{len(video_files)} VIDEO TRONG {total_elapsed:.2f}s")
    print(f"=======================================================\n")
    print(f"{'STT':<4} | {'Tên Video':<38} | {'Frames':<7} | {'FPS':<6} | {'Sự kiện':<8}")
    print("-" * 72)
    for i, s in enumerate(summaries, 1):
        vname = os.path.basename(s['input_video'])
        print(f"{i:<4} | {vname:<38} | {s['total_frames_processed']:<7} | {s['processing_fps']:<6} | {s['total_events_detected']:<8}")
    print("-" * 72)


if __name__ == "__main__":
    run_batch()
