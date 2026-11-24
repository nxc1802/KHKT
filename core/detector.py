"""Module Object Detection và chuẩn hóa nhãn (Class Mapping).

Hỗ trợ:
- Tải model YOLO chính (hỗ trợ auto device: mps, cuda, cpu).
- Tích hợp model phát hiện Thùng rác (Trash Bin / Waste Container).
- Chuẩn hóa các class về:
  1. 'person' (Human Detection)
  2. 'trash' (Trash Detection)
  3. 'trash_bin' (Thùng rác Detection)
"""

from typing import Dict, List, Optional, Tuple, Any
import os
import torch
from ultralytics import YOLO


DEFAULT_COCO_TRASH_CLASSES = [
    24, 25, 26, 28, 39, 40, 41, 42, 43, 44, 45,
    46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
    67, 73, 76
]


def resolve_device(preferred_device: str = "auto") -> str:
    """Tự động phát hiện device tối ưu (mps cho Apple Silicon, cuda cho Nvidia, cpu fallback)."""
    if preferred_device != "auto":
        return preferred_device

    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"


class Detector:
    """Quản lý model YOLO và quy tắc ánh xạ nhãn chuẩn hóa (Person, Trash, Trash Bin)."""

    def __init__(self,
                 model_path: str = "weights/best.pt",
                 confidence_threshold: float = 0.20,
                 imgsz: int = 640,
                 device: str = "auto",
                 class_mode: str = "custom",
                 trash_classes_coco: Optional[List[int]] = None,
                 enable_bin_detection: bool = False,
                 bin_model_path: Optional[str] = "yolov8s-worldv2.pt",
                 bin_classes: Optional[List[str]] = None,
                 bin_confidence: float = 0.30):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.imgsz = imgsz
        self.device = resolve_device(device)
        self.class_mode = class_mode.lower()
        self.trash_classes_coco = set(trash_classes_coco or DEFAULT_COCO_TRASH_CLASSES)

        # Model chính (Person + Trash)
        self.model = self._load_model(model_path)

        # Model phát hiện Thùng rác (Trash Bin Detection)
        self.enable_bin_detection = enable_bin_detection
        self.bin_confidence = bin_confidence
        self.bin_model: Optional[YOLO] = None

        if self.enable_bin_detection and bin_model_path:
            self.bin_model = self._load_bin_model(
                bin_model_path,
                bin_classes or ["waste bin", "trash can"]
            )

    def _load_model(self, path: str) -> YOLO:
        """Tải model YOLO chính."""
        if not os.path.exists(path) and not path.endswith(".pt"):
            path = path + ".pt"
        print(f"[Detector] Loading primary model from '{path}' on device '{self.device}'...")
        model = YOLO(path)
        return model

    def _load_bin_model(self, path: str, target_classes: List[str]) -> YOLO:
        """Tải model phát hiện Thùng rác."""
        print(f"[Detector] Loading trash bin detector from '{path}' for classes {target_classes}...")
        model = YOLO(path)
        if hasattr(model, "set_classes"):
            try:
                model.set_classes(target_classes)
            except Exception as e:
                print(f"[Detector] Note: set_classes failed ({e}), using default classes.")
        return model

    def map_class(self, class_id: int, original_name: str = "") -> Optional[str]:
        """Chuẩn hóa nhãn thành 'person', 'trash' hoặc None (nếu bỏ qua)."""
        orig_lower = original_name.lower()
        if "bin" in orig_lower or "trash can" in orig_lower:
            return "trash_bin"

        if self.class_mode == "custom":
            if "person" in orig_lower or class_id == 0:
                return "person"
            elif "trash" in orig_lower or "litter" in orig_lower or class_id == 1:
                return "trash"
            return None

        # COCO Mode:
        if class_id == 0:
            return "person"
        elif class_id in self.trash_classes_coco:
            return "trash"
        return None
