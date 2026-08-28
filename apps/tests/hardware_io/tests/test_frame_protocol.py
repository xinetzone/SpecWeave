"""frame_protocol 编解码与流式解析单元测试."""

import pytest

from hardware_io.frame_protocol import (
    FRAME_FOOTER,
    FRAME_HEADER,
    Frame,
    FrameParseError,
    StreamingFrameParser,
    decode_frame,
    encode_frame,
)


class TestEncodeFrame:
    """encode_frame 测试."""

    def test_empty_data(self):
        frame = encode_frame(0x01, b"")
        assert frame[:2] == FRAME_HEADER
        assert frame[2] == 0x01  # cmd
        assert frame[3] == 0x00  # len
        assert frame[-2:] == FRAME_FOOTER
        assert len(frame) == 7

    def test_with_data(self):
        data = b"hello"
        frame = encode_frame(0x10, data)
        assert frame[2] == 0x10
        assert frame[3] == 5
        assert frame[4:9] == data
        assert len(frame) == 12

    def test_checksum(self):
        # cmd=0x01, len=0x03, data=[0x10, 0x20, 0x30]
        # chk = 0x01 ^ 0x03 ^ 0x10 ^ 0x20 ^ 0x30 = 0x02
        frame = encode_frame(0x01, bytes([0x10, 0x20, 0x30]))
        expected_chk = 0x01 ^ 0x03 ^ 0x10 ^ 0x20 ^ 0x30
        assert frame[-3] == expected_chk

    def test_roundtrip(self):
        for cmd in [0x00, 0x01, 0x10, 0xFF]:
            for data in [b"", b"A", b"hello world", bytes(range(255))]:
                frame = encode_frame(cmd, data)
                result, consumed = decode_frame(frame)
                assert result.cmd == cmd
                assert result.data == data
                assert consumed == len(frame)

    def test_invalid_cmd(self):
        with pytest.raises(ValueError):
            encode_frame(0x100, b"")

    def test_data_too_long(self):
        with pytest.raises(ValueError):
            encode_frame(0x01, b"x" * 256)


class TestDecodeFrame:
    """decode_frame 测试."""

    def test_insufficient_data(self):
        assert decode_frame(b"\xAA\x55\x01") is None

    def test_bad_header(self):
        with pytest.raises(FrameParseError):
            decode_frame(b"\x00\x00\x01\x00\x00\x55\xAA")

    def test_bad_footer(self):
        # 构造一个帧尾错误的帧
        frame = bytearray(encode_frame(0x01, b"test"))
        frame[-1] = 0x00  # 破坏帧尾
        with pytest.raises(FrameParseError):
            decode_frame(bytes(frame))

    def test_bad_checksum(self):
        frame = bytearray(encode_frame(0x01, b"test"))
        frame[-3] ^= 0xFF  # 破坏校验位
        with pytest.raises(FrameParseError):
            decode_frame(bytes(frame))

    def test_partial_frame_returns_none(self):
        frame = encode_frame(0x01, b"data")
        # 只给前半部分
        assert decode_frame(frame[:5]) is None


class TestStreamingParser:
    """StreamingFrameParser 流式解析测试."""

    def test_single_frame(self):
        parser = StreamingFrameParser()
        frame = encode_frame(0x01, b"hello")
        parser.feed(frame)
        result = parser.get_frame()
        assert result == Frame(cmd=0x01, data=b"hello")
        assert parser.get_frame() is None

    def test_multiple_frames(self):
        parser = StreamingFrameParser()
        f1 = encode_frame(0x01, b"first")
        f2 = encode_frame(0x02, b"second")
        parser.feed(f1 + f2)

        r1 = parser.get_frame()
        assert r1.cmd == 0x01 and r1.data == b"first"
        r2 = parser.get_frame()
        assert r2.cmd == 0x02 and r2.data == b"second"
        assert parser.get_frame() is None

    def test_fragmented_frame(self):
        """分片到达测试."""
        parser = StreamingFrameParser()
        frame = encode_frame(0x10, b"fragment")

        # 逐字节喂入
        for byte in frame:
            parser.feed(bytes([byte]))

        result = parser.get_frame()
        assert result.cmd == 0x10
        assert result.data == b"fragment"

    def test_garbage_before_frame(self):
        """帧前有垃圾字节."""
        parser = StreamingFrameParser()
        garbage = b"\x00\x01\x02\x03"
        frame = encode_frame(0x01, b"ok")
        parser.feed(garbage + frame)
        result = parser.get_frame()
        assert result.cmd == 0x01
        assert result.data == b"ok"

    def test_garbage_between_frames(self):
        """帧间有垃圾字节."""
        parser = StreamingFrameParser()
        f1 = encode_frame(0x01, b"a")
        f2 = encode_frame(0x02, b"b")
        parser.feed(f1 + b"\xff\xfe" + f2)
        r1 = parser.get_frame()
        r2 = parser.get_frame()
        assert r1.data == b"a"
        assert r2.data == b"b"

    def test_corrupted_frame_resync(self):
        """校验失败后重新同步到下一帧."""
        parser = StreamingFrameParser()
        good_frame = encode_frame(0x02, b"good")
        # 构造一个帧头正确但校验错误的帧
        bad = bytearray(encode_frame(0x01, b"bad"))
        bad[-3] ^= 0xFF  # 破坏校验

        parser.feed(bytes(bad) + good_frame)
        result = parser.get_frame()
        # 应跳过坏帧，拿到好帧
        assert result.cmd == 0x02
        assert result.data == b"good"

    def test_reset(self):
        parser = StreamingFrameParser()
        parser.feed(encode_frame(0x01, b"data"))
        parser.reset()
        assert parser.buffer_size == 0
        assert parser.get_frame() is None

    def test_empty_feed(self):
        parser = StreamingFrameParser()
        parser.feed(b"")
        assert parser.get_frame() is None

    def test_partial_header_kept(self):
        """只有半个帧头时保留等待."""
        parser = StreamingFrameParser()
        full_frame = encode_frame(0x01, b"")
        # 先喂帧头第一字节
        parser.feed(full_frame[:1])
        assert parser.get_frame() is None
        # 补齐剩余字节
        parser.feed(full_frame[1:])
        result = parser.get_frame()
        assert result is not None
        assert result.cmd == 0x01
        assert result.data == b""
