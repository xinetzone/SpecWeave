"""hardware_io — 可复用的硬件 I/O 工具集.

从串口摄像头控制器实验中萃取的独立可复用 API:

- camera_utils:  多后端摄像头发现与健壮初始化（分辨率自动降级）
- serial_utils:  串口设备枚举、VID/PID 自动探测、健壮打开
- frame_protocol: 通用二进制帧编解码与流式解析（AA55 CMD LEN DATA XOR 55AA）
- frame_buffer:  线程安全的"最新值"缓存（生产者-消费者模式）

所有模块均可独立导入，无交叉依赖（frame_protocol 与 frame_buffer 为纯 Python，
camera_utils / serial_utils 分别依赖 opencv-python / pyserial）。
"""

from hardware_io.frame_buffer import FrameBuffer
from hardware_io.frame_protocol import (
    FRAME_FOOTER,
    FRAME_HEADER,
    FrameParseError,
    StreamingFrameParser,
    decode_frame,
    encode_frame,
)

__all__ = [
    "FrameBuffer",
    "FRAME_HEADER",
    "FRAME_FOOTER",
    "FrameParseError",
    "StreamingFrameParser",
    "encode_frame",
    "decode_frame",
]

__version__ = "1.0.0"
