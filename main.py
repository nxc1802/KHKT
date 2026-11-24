"""Giao diện dòng lệnh CLI chính của hệ thống AI Littering Behavior Detection.

Đề tài KHKT THCS: Phát hiện hành vi xả rác bằng Object Detection, ByteTrack và Spatio-Temporal Reasoning.
"""

import argparse
import sys
import os
import yaml

from pipeline.video_processor import VideoProcessor


BANNER = r"""
========================================================================
   AI LITTERING BEHAVIOR DETECTION SYSTEM — KHKT THCS
   Object Detection + ByteTrack + Spatio-Temporal FSM Engine
========================================================================
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Littering Behavior Detection — Hệ thống phát hiện hành vi xả rác qua video.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input", type=str, default=None,
                        help="Đường dẫn đến file video đầu vào (.mp4, .avi, ...).")
    parser.add_argument("-c", "--config", type=str, default="config.yaml",
                        help="Đường dẫn file cấu hình YAML.")
    parser.add_argument("-o", "--output-video", type=str, default=None,
                        help="Đường dẫn file video kết quả kèm annotation.")
    parser.add_argument("--output-events", type=str, default=None,
                        help="Đường dẫn file JSON lưu trữ các sự kiện phát hiện.")
    parser.add_argument("--weights", type=str, default=None,
                        help="Ghi đè đường dẫn model weights (.pt).")
    parser.add_argument("--device", type=str, default=None, choices=["auto", "mps", "cuda", "cpu"],
                        help="Ghi đè thiết bị tính toán.")
    parser.add_argument("--no-video", action="store_true",
                        help="Không xuất file video (chỉ trích xuất sự kiện JSON và ảnh bằng chứng).")
    parser.add_argument("--generate-sample", action="store_true",
                        help="Tự động sinh video mẫu mô phỏng hành vi xả rác và chạy thử nghiệm ngay.")
    return parser.parse_args()


def main():
    print(BANNER)
    args = parse_args()

    # Nếu người dùng muốn tự động sinh video mẫu và chạy thử
    if args.generate_sample:
        from tools.generate_sample_video import generate_synthetic_littering_video
        sample_path = "inputs/sample_littering_test.mp4"
        print("[Demo] Đang tự động sinh video mô phỏng hành vi xả rác...")
        generate_synthetic_littering_video(sample_path)
        args.input = sample_path

    if not args.input:
        print("[Lỗi] Bạn cần cung cấp video đầu vào qua tham số -i/--input hoặc sử dụng cờ --generate-sample để chạy thử.")
        print("Ví dụ sử dụng:")
        print("  python main.py -i inputs/video_test.mp4")
        print("  python main.py --generate-sample")
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"[Lỗi] File video không tồn tại: {args.input}")
        sys.exit(1)

    # Khởi tạo Processor
    processor = VideoProcessor(config_path=args.config)

    # Ghi đè cấu hình nếu có tham số từ dòng lệnh
    if args.weights:
        processor.detector.model_path = args.weights
        processor.detector.model = processor.detector._load_model(args.weights)
    if args.device:
        processor.detector.device = args.device
    if args.no_video:
        processor.config.setdefault("output", {})["save_video"] = False

    # Thực thi pipeline
    try:
        summary = processor.process_video(
            video_path=args.input,
            output_video_path=args.output_video,
            events_json_path=args.output_events
        )

        print("\n" + "=" * 72)
        print("BÁO CÁO TỔNG HỢP KẾT QUẢ XỬ LÝ:")
        print(f"  • Video đầu vào      : {summary['input_video']}")
        if summary['output_video']:
            print(f"  • Video kết quả      : {summary['output_video']}")
        if summary['events_json']:
            print(f"  • File sự kiện JSON  : {summary['events_json']}")
        print(f"  • Tổng số frame      : {summary['total_frames_processed']}")
        print(f"  • Thời gian xử lý    : {summary['elapsed_seconds']}s")
        print(f"  • Tốc độ trung bình  : {summary['processing_fps']} FPS")
        print(f"  • Số sự kiện phát hiện: {summary['total_events_detected']}")
        print("=" * 72 + "\n")

    except Exception as e:
        print(f"\n[Lỗi ngoại lệ] Pipeline gặp lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
