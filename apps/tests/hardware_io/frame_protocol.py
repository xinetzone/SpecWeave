"""通用二进制帧协议编解码.

帧格式::

    +----------+-----+-----+----------+--------+----------+
    | HEADER   | CMD | LEN | DATA     | CHK    | FOOTER   |
    | AA 55    | 1B  | 1B  | 0-255 B  | 1B XOR | 55 AA    |
    +----------+-----+-----+----------+--------+----------+

CHK = CMD XOR LEN XOR all(DATA)  (逐字节异或)

适用于串口 / TCP / 任意字节流上的二进制命令帧通信。文本行协议可与本协议
共存于同一字节流——解析器优先同步二进制帧，未命中帧头时再按换行切分文本。

示例::

    from hardware_io.frame_protocol import encode_frame, StreamingFrameParser

    # 编码一帧
    frame = encode_frame(cmd=0x01, data=b"hello")

    # 流式解析（处理分片/粘包）
    parser = StreamingFrameParser()
    parser.feed(b"\\xaa\\x55\\x01\\x05hello")
    parser.feed(b"\\x0d\\x55\\xaa")  # 剩余分片
    cmd, data = parser.get_frame()  # → (0x01, b"hello")
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional

# 帧定界符
FRAME_HEADER: bytes = bytes([0xAA, 0x55])
FRAME_FOOTER: bytes = bytes([0x55, 0xAA])

# 帧结构常量
_MIN_FRAME_LEN = 7  # header(2) + cmd(1) + len(1) + chk(1) + footer(2)
_MAX_DATA_LEN = 255


class FrameParseError(Exception):
    """帧解析错误."""


@dataclass(frozen=True)
class Frame:
    """解析成功的二进制帧."""

    cmd: int
    data: bytes


def _xor_checksum(cmd: int, data_len: int, data: bytes) -> int:
    """计算 XOR 校验字节."""
    chk = cmd ^ data_len
    for b in data:
        chk ^= b
    return chk & 0xFF


def encode_frame(cmd: int, data: bytes = b"") -> bytes:
    """将命令与数据编码为完整二进制帧.

    Args:
        cmd: 命令字节 (0x00-0xFF).
        data: 负载数据，长度 0-255 字节.

    Returns:
        完整帧字节串.

    Raises:
        ValueError: cmd 超出范围或 data 超过 255 字节.
    """
    if not 0 <= cmd <= 0xFF:
        raise ValueError(f"cmd 超出范围: {cmd}")
    if len(data) > _MAX_DATA_LEN:
        raise ValueError(f"data 长度超过 {_MAX_DATA_LEN}: {len(data)}")

    chk = _xor_checksum(cmd, len(data), data)
    return FRAME_HEADER + bytes([cmd, len(data)]) + data + bytes([chk]) + FRAME_FOOTER


def decode_frame(buf: bytes) -> Optional[tuple[Frame, int]]:
    """从字节缓冲区起始位置尝试解析一帧.

    仅检查缓冲区**开头**是否为完整有效帧。若开头不是帧头但缓冲区中包含
    帧头，调用方应自行丢弃帧头前的垃圾字节后再次调用。

    Args:
        buf: 输入字节缓冲区.

    Returns:
        成功时返回 ``(Frame, consumed_length)``；数据不足时返回 ``None``
        （调用方应等待更多字节）。

    Raises:
        FrameParseError: 帧头匹配但校验失败或帧尾不匹配（调用方应丢弃
            帧头重新同步）。
    """
    if len(buf) < _MIN_FRAME_LEN:
        return None

    # 校验帧头
    if buf[0:2] != FRAME_HEADER:
        raise FrameParseError("缓冲区开头不是帧头")

    cmd = buf[2]
    data_len = buf[3]
    frame_end = 4 + data_len + 1 + 2  # cmd+len + data + chk + footer

    if frame_end > len(buf):
        return None  # 数据不足，等待更多字节

    # 校验帧尾
    if buf[frame_end - 2 : frame_end] != FRAME_FOOTER:
        raise FrameParseError("帧尾不匹配")

    data = buf[4 : 4 + data_len]
    chk_recv = buf[4 + data_len]
    chk_calc = _xor_checksum(cmd, data_len, data)
    if chk_calc != chk_recv:
        raise FrameParseError(
            f"XOR 校验失败: 期望 0x{chk_calc:02X}, 收到 0x{chk_recv:02X}"
        )

    return Frame(cmd=cmd, data=data), frame_end


class StreamingFrameParser:
    """流式帧解析器，处理分片、粘包与垃圾字节.

    内部维护一个 deque 缓冲区。调用 :meth:`feed` 喂入任意数量的字节，
    随后反复调用 :meth:`get_frame` 取出完整帧，直到返回 ``None``。

    特性:
    - 自动跳过帧头前的垃圾字节
    - 校验失败时自动丢弃帧头重新同步
    - 缓冲区上限可配置（默认 4096 字节），防止异常流撑爆内存
    """

    def __init__(self, max_buffer: int = 4096) -> None:
        self._buf: deque[int] = deque(maxlen=max_buffer)
        self._max_buffer = max_buffer

    def feed(self, data: bytes) -> None:
        """喂入接收到的字节."""
        for b in data:
            self._buf.append(b)

    @property
    def buffer_size(self) -> int:
        """当前缓冲区字节数."""
        return len(self._buf)

    def _find_header(self) -> int:
        """返回帧头在缓冲区中的位置，未找到返回 -1."""
        buf_bytes = bytes(self._buf)
        return buf_bytes.find(FRAME_HEADER)

    def get_frame(self) -> Optional[Frame]:
        """尝试从缓冲区取出一帧.

        Returns:
            解析成功的 :class:`Frame`，或 ``None`` 表示当前无完整帧.
        """
        while len(self._buf) > 0:
            header_pos = self._find_header()

            if header_pos < 0:
                # 没有帧头，保留最后 1 字节（可能是帧头的第一个 0xAA）
                # 其余丢弃
                if len(self._buf) > 1:
                    for _ in range(len(self._buf) - 1):
                        self._buf.popleft()
                return None

            if header_pos > 0:
                # 丢弃帧头前的垃圾字节
                for _ in range(header_pos):
                    self._buf.popleft()

            # 尝试解析
            buf_bytes = bytes(self._buf)
            try:
                result = decode_frame(buf_bytes)
            except FrameParseError:
                # 校验失败/帧尾错误：丢弃帧头第一个字节，重新同步
                self._buf.popleft()
                continue

            if result is None:
                return None  # 数据不足

            frame, consumed = result
            for _ in range(consumed):
                self._buf.popleft()
            return frame

        return None

    def reset(self) -> None:
        """清空缓冲区."""
        self._buf.clear()
