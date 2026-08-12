"""Calibration data loader built on Pillow + numpy.

Replaces the torchvision-based loader in the original ``data.imagenet``. Loads
image files from a directory, applies resize/center-crop/normalize, and returns
an NCHW float32 numpy array. No torch dependency.
"""

from __future__ import annotations

import os

import numpy as np
from PIL import Image

IMG_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")


def _load_pil(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def _resize_crop(img: Image.Image, input_size):
    """Resize to 256 then center-crop to ``input_size`` (int or (h,w))."""
    if isinstance(input_size, (tuple, list)) and len(input_size) == 2:
        return img.resize((int(input_size[1]), int(input_size[0])), Image.BILINEAR)
    side = int(input_size)
    img = img.resize((256, 256), Image.BILINEAR)
    left = (256 - side) // 2
    top = (256 - side) // 2
    return img.crop((left, top, left + side, top + side))


def _to_numpy(img: Image.Image, input_format: str, mean, std) -> np.ndarray:
    arr = np.asarray(img, dtype=np.float32)  # (H, W, C)
    if arr.ndim == 2:
        arr = arr[..., None]
    if input_format.upper() == "BGR":
        arr = arr[..., ::-1]
    arr = arr.transpose(2, 0, 1).astype(np.float32)  # CHW
    mean = np.asarray(mean, dtype=np.float32).reshape(-1, 1, 1)
    std = np.asarray(std, dtype=np.float32).reshape(-1, 1, 1)
    return (arr - mean) / std


def load_images(data_path: str, input_size=224, input_format: str = "RGB",
                mean=None, std=None) -> np.ndarray:
    """Load all images under ``data_path`` (recursive) into an NCHW array."""
    mean = [0.485, 0.456, 0.406] if mean is None else mean
    std = [0.229, 0.224, 0.225] if std is None else std
    paths = []
    for dirpath, _, filenames in os.walk(data_path):
        for fname in sorted(filenames):
            if fname.lower().endswith(IMG_EXTENSIONS):
                paths.append(os.path.join(dirpath, fname))
    if not paths:
        raise FileNotFoundError(f"在 {data_path} 下未找到任何支持的图像文件")
    tensors = []
    for p in paths:
        img = _resize_crop(_load_pil(p), input_size)
        tensors.append(_to_numpy(img, input_format, mean, std))
    return np.stack(tensors, axis=0)


def load_calibration_data(data_path: str, num_samples: int, input_size=224,
                          input_format: str = "RGB", mean=None, std=None) -> np.ndarray:
    """Load calibration data and truncate to ``num_samples``."""
    data = load_images(data_path, input_size=input_size, input_format=input_format,
                       mean=mean, std=std)
    if data.shape[0] == 0:
        raise RuntimeError("Calibration dataset is empty")
    return data[:num_samples]


def get_train_samples(cali_data: np.ndarray, num_samples: int) -> np.ndarray:
    return cali_data[:num_samples]
