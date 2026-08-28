"""摄像头设备发现与健壮初始化.

封装了多后端尝试、分辨率自动降级、设置后验证等模式。核心 API:

- :func:`list_backends`: 返回当前平台支持的 OpenCV 后端列表
- :func:`open_camera_robust`: 多后端+多分辨率尝试，返回可用的 VideoCapture
- :func:`probe_camera`: 快速探测摄像头是否可用

这些函数与具体业务逻辑（抓图/录像）无关，可用于任何需要 USB 摄像头的项目。

示例::

    from hardware_io.camera_utils import open_camera_robust

    cap, w, h, fps = open_camera_robust(
        preferred_width=1280, preferred_height=720, fps=30
    )
    ret, frame = cap.read()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class CameraBackend:
    """OpenCV 摄像头后端描述."""

    id: int
    name: str
    available: bool


def list_backends() -> List[CameraBackend]:
    """列出当前平台可用的摄像头后端.

    Returns:
        :class:`CameraBackend` 列表，按推荐优先级排序。
    """
    candidates = [
        (cv2.CAP_MSMF, "MediaFoundation"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_ANY, "Auto"),
    ]
    result = []
    for backend_id, name in candidates:
        # 尝试用该后端打开摄像头以检测可用性
        cap = cv2.VideoCapture(0, backend_id)
        available = cap.isOpened()
        if available:
            cap.release()
        result.append(CameraBackend(id=backend_id, name=name, available=available))
    return result


# 默认分辨率降级列表（从高到低，包含常见稳定分辨率）
DEFAULT_RESOLUTION_FALLBACK: List[Tuple[int, int]] = [
    (1280, 720),
    (1920, 1080),
    (1024, 768),
    (800, 600),
    (640, 480),
    (320, 240),
]

# 默认后端优先级
DEFAULT_BACKEND_ORDER: List[Tuple[int, str]] = [
    (cv2.CAP_MSMF, "MediaFoundation"),
    (cv2.CAP_DSHOW, "DirectShow"),
    (cv2.CAP_ANY, "Auto"),
]


@dataclass
class CameraInfo:
    """成功打开的摄像头信息."""

    cap: cv2.VideoCapture
    width: int
    height: int
    fps: float
    backend_name: str


def open_camera_robust(
    preferred_width: int = 640,
    preferred_height: int = 480,
    fps: int = 30,
    device_index: int = 0,
    backends: Optional[List[Tuple[int, str]]] = None,
    resolutions: Optional[List[Tuple[int, int]]] = None,
    min_frame_ratio: float = 0.5,
    verbose: bool = False,
) -> CameraInfo:
    """多后端+多分辨率尝试打开摄像头.

    对每个后端依次尝试各候选分辨率。设置分辨率后实际读取一帧验证真实
    分辨率（部分 UVC 摄像头的 ``cap.set()`` 会静默失败）。

    Args:
        preferred_width: 首选宽度。
        preferred_height: 首选高度。
        fps: 目标帧率。
        device_index: 摄像头设备索引（默认 0）。
        backends: 后端列表 ``[(id, name), ...]``，为 ``None`` 时使用默认顺序。
        resolutions: 分辨率候选列表，为 ``None`` 时自动生成（首选分辨率+默认降级列表）。
        min_frame_ratio: 实际分辨率至少达到请求分辨率的此比例才算成功。
        verbose: 是否打印尝试过程。

    Returns:
        :class:`CameraInfo`，包含 VideoCapture 和实际参数。

    Raises:
        RuntimeError: 所有后端和分辨率组合均失败。
    """
    if backends is None:
        backends = DEFAULT_BACKEND_ORDER

    if resolutions is None:
        # 首选分辨率排第一，后续接默认降级列表（去重）
        seen: set = set()
        resolutions = []
        for w, h in [(preferred_width, preferred_height)] + DEFAULT_RESOLUTION_FALLBACK:
            if (w, h) not in seen:
                seen.add((w, h))
                resolutions.append((w, h))

    errors: List[str] = []

    for backend_id, backend_name in backends:
        if verbose:
            print(f"[*] 尝试后端: {backend_name}...", end=" ")

        cap = cv2.VideoCapture(device_index, backend_id)
        if not cap.isOpened():
            errors.append(f"{backend_name}: 无法打开设备")
            cap.release()
            if verbose:
                print("失败（无法打开）")
            continue

        # 依次尝试各分辨率
        working_res: Optional[Tuple[int, int]] = None
        for w, h in resolutions:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            cap.set(cv2.CAP_PROP_FPS, fps)

            try:
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    actual_h, actual_w = frame.shape[:2]
                    # 验证实际分辨率达到最低要求
                    if actual_w >= w * min_frame_ratio and actual_h >= h * min_frame_ratio:
                        working_res = (actual_w, actual_h)
                        break
            except cv2.error:
                continue

        if working_res is not None:
            actual_w, actual_h = working_res
            actual_fps = cap.get(cv2.CAP_PROP_FPS) or fps
            if verbose:
                print(f"成功 ({actual_w}x{actual_h} @ {actual_fps:.0f}fps)")
            return CameraInfo(
                cap=cap,
                width=actual_w,
                height=actual_h,
                fps=actual_fps,
                backend_name=backend_name,
            )

        errors.append(f"{backend_name}: 所有分辨率均不兼容")
        cap.release()
        if verbose:
            print("失败（分辨率不兼容）")

    raise RuntimeError(
        "无法打开摄像头！所有后端和分辨率组合均失败。\n"
        + "\n".join(f"  - {e}" for e in errors)
    )


def probe_camera(device_index: int = 0) -> Optional[Tuple[int, int]]:
    """快速探测摄像头是否可读.

    Args:
        device_index: 摄像头设备索引。

    Returns:
        成功时返回 ``(width, height)``，失败返回 ``None``。
    """
    for backend_id, _ in DEFAULT_BACKEND_ORDER:
        cap = cv2.VideoCapture(device_index, backend_id)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                h, w = frame.shape[:2]
                cap.release()
                return (w, h)
        cap.release()
    return None


def save_frame(
    frame: np.ndarray,
    filepath: str,
    jpeg_quality: int = 95,
) -> bool:
    """保存帧为图片文件.

    Args:
        frame: OpenCV 帧（BGR 格式）。
        filepath: 输出路径（扩展名决定编码，如 .jpg/.png）。
        jpeg_quality: JPEG 质量（1-100），仅对 .jpg 有效。

    Returns:
        是否保存成功。
    """
    try:
        params: list = []
        if filepath.lower().endswith((".jpg", ".jpeg")):
            params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
        return bool(cv2.imwrite(filepath, frame, params))
    except Exception:
        return False
