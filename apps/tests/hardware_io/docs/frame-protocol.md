# frame_protocol — 二进制帧编解码与流式解析

通用的二进制帧通信原语，适用于串口、TCP、蓝牙等任意字节流。支持帧编码、单次解码、流式解析（自动处理分片/粘包/垃圾字节/损坏重同步）。

## 帧格式

```
+----------+-----+-----+----------+--------+----------+
| HEADER   | CMD | LEN | DATA     | CHK    | FOOTER   |
| AA 55    | 1B  | 1B  | 0-255 B  | 1B XOR | 55 AA    |
+----------+-----+-----+----------+--------+----------+
```

- **HEADER**：`0xAA 0x55`，帧起始标记
- **CMD**：1 字节命令字（0x00-0xFF）
- **LEN**：1 字节数据长度（0-255）
- **DATA**：负载数据，长度由 LEN 指定
- **CHK**：XOR 校验，`CHK = CMD ^ LEN ^ DATA[0] ^ DATA[1] ^ ... ^ DATA[n-1]`
- **FOOTER**：`0x55 0xAA`，帧结束标记

## 何时使用

- 串口/TCP 上需要传输结构化二进制命令
- 接收端字节流可能分片到达（串口常见）
- 数据流中混合了二进制帧与文本行协议
- 需要从噪声字节流中可靠提取完整帧

## API 参考

### `encode_frame(cmd, data=b"")`

编码一帧完整二进制数据。

| 参数 | 类型 | 说明 |
|------|------|------|
| `cmd` | `int` | 命令字节，0-255 |
| `data` | `bytes` | 负载数据，0-255 字节，默认空 |

**返回**：`bytes`，完整帧字节串。

**异常**：
- `ValueError`：cmd 超出 0-255 范围，或 data 超过 255 字节。

```python
from hardware_io.frame_protocol import encode_frame

frame = encode_frame(0x01, b"CAP")
print(frame.hex())  # aa5501034341505055aa
```

### `decode_frame(buf)`

从字节缓冲区**起始位置**尝试解析一帧。

| 参数 | 类型 | 说明 |
|------|------|------|
| `buf` | `bytes` | 输入字节缓冲区 |

**返回**：
- 成功：`(Frame, consumed_length)` —— `Frame` 是含 `cmd` 和 `data` 字段的 dataclass，`consumed_length` 是此帧占用的字节数
- 数据不足：`None`（调用方应等待更多字节）

**异常**：
- `FrameParseError`：缓冲区开头是帧头但帧尾不匹配或校验失败。调用方应丢弃帧头重新同步。

```python
from hardware_io.frame_protocol import decode_frame

result = decode_frame(frame_bytes)
if result is not None:
    frame, consumed = result
    print(f"cmd=0x{frame.cmd:02X}, data={frame.data}")
```

### `StreamingFrameParser(max_buffer=4096)`

流式帧解析器，维护内部缓冲区，自动处理分片、粘包和垃圾字节。

#### 方法

| 方法 | 说明 |
|------|------|
| `feed(data: bytes)` | 喂入接收到的任意数量字节 |
| `get_frame() -> Frame \| None` | 尝试取出一帧，无完整帧时返回 `None` |
| `reset()` | 清空内部缓冲区 |
| `buffer_size` (属性) | 当前缓冲区字节数 |

#### 解析逻辑

1. 在缓冲区中搜索帧头 `AA 55`
2. 找到帧头前的字节作为垃圾丢弃（保留最后 1 字节，防止 `AA` 是帧头首字节）
3. 尝试解析帧：数据不足则返回 `None` 等待更多字节
4. 校验失败/帧尾错误：丢弃帧头首字节，重新搜索下一帧头
5. 解析成功：移除已消费字节，返回 `Frame`

## 使用示例

### 示例 1：基本编码解码

```python
from hardware_io.frame_protocol import encode_frame, decode_frame

# 编码
frame = encode_frame(cmd=0x10, data=b"\x01\x02\x03")

# 解码
result = decode_frame(frame)
assert result is not None
parsed, length = result
assert parsed.cmd == 0x10
assert parsed.data == b"\x01\x02\x03"
assert length == len(frame)
```

### 示例 2：串口流式接收（分片+粘包）

```python
import serial
from hardware_io.frame_protocol import StreamingFrameParser

ser = serial.Serial("COM4", 115200, timeout=0.05)
parser = StreamingFrameParser()

while True:
    chunk = ser.read(256)
    if chunk:
        parser.feed(chunk)
        # 一次 read 可能包含 0 个、1 个或多个帧
        while True:
            frame = parser.get_frame()
            if frame is None:
                break
            print(f"收到命令 0x{frame.cmd:02X}: {frame.data.hex()}")
```

### 示例 3：二进制帧与文本行共存

```python
from hardware_io.frame_protocol import StreamingFrameParser, FRAME_HEADER

parser = StreamingFrameParser()

# 数据流中可能混合文本行和二进制帧
stream = b"READY\r\n" + encode_frame(0x01, b"bin") + b"OK:done\r\n"
parser.feed(stream)

while True:
    frame = parser.get_frame()
    if frame is None:
        break
    print(f"二进制帧: cmd=0x{frame.cmd:02X}, data={frame.data}")

# 文本行由调用方用其他方式从流中提取（帧解析器只处理二进制帧，
# 帧头前的文本会被当作垃圾跳过）
```

### 示例 4：损坏帧自动重同步

```python
parser = StreamingFrameParser()

# 构造一个校验错误的帧 + 一个正确帧
bad = bytearray(encode_frame(0x01, b"bad"))
bad[-3] ^= 0xFF  # 破坏校验位
good = encode_frame(0x02, b"good")

parser.feed(bytes(bad) + good)
frame = parser.get_frame()
# 自动跳过坏帧，拿到好帧
assert frame.cmd == 0x02
assert frame.data == b"good"
```

### 示例 5：逐字节喂入（极端分片）

```python
parser = StreamingFrameParser()
frame = encode_frame(0x10, bytes(range(100)))

for byte in frame:
    parser.feed(bytes([byte]))

result = parser.get_frame()
assert result.cmd == 0x10
assert len(result.data) == 100
```

## 常量

| 常量 | 值 | 说明 |
|------|----|------|
| `FRAME_HEADER` | `b"\xAA\x55"` | 帧头 |
| `FRAME_FOOTER` | `b"\x55\xAA"` | 帧尾 |

## 常见陷阱

1. **LEN 字段最大值 255**：单帧数据不能超过 255 字节。需要传输更大数据时，应在应用层分片。
2. **DATA 中包含 `AA 55` 不会误判**：解析器依赖 LEN 字段定位帧尾，不会因为数据中出现帧头字节而截断。
3. **`decode_frame` 只检查缓冲区开头**：如果开头不是帧头，直接抛异常。从字节流中间解析应使用 `StreamingFrameParser`。
4. **缓冲区上限默认 4096 字节**：如果一帧最大 262 字节（7+255），缓冲区可容纳约 15 帧。异常数据流不会撑爆内存。
