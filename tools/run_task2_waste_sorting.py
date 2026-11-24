"""Script chạy Task 2 (Phân loại rác Tái chế / Không tái chế) thông qua VideoProcessor."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.video_processor import VideoProcessor


def main():
    processor = VideoProcessor(config_path="config.yaml")
    for vname in ["IMG_6820", "IMG_6821", "IMG_6822", "IMG_6823"]:
        print(f"\n--- Running Task 2 on inputs/{vname}.MOV ---")
        processor.process_waste_sorting_video(f"inputs/{vname}.MOV")


if __name__ == "__main__":
    main()
