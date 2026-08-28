# hardware_io — 可复用硬件 I/O 工具集

从串口摄像头控制器实验中萃取的独立、可复用 Python API。涵盖二进制帧通信、线程安全数据缓存、USB 摄像头健壮初始化、串口设备自动发现四个领域。所有模块均无业务耦合，可直接嵌入任意 Python 项目。

## 模块矩阵

| 模块 | 职责 | 外部依赖 | 需要硬件 |
|------|------|----------|:--------:|
| [frame_protocol](docs/frame-protocol.md) | 二进制帧编解码与流式解析 | 无 | 否 |
| [frame_buffer](docs/frame-buffer.md) | 线程安全的"最新值"缓存 | 无 | 否 |
| [camera_utils](docs/camera-utils.md) | 多后端摄像头发现与分辨率降级 | opencv-python | 是 |
| [serial_utils](docs/serial-utils.md) | 串口枚举、VID/PID 匹配、健壮打开 | pyserial | 是 |

> **设计原则**：纯逻辑模块（frame_protocol、frame_buffer）零依赖，可在 CI 环境中直接测试；硬件模块按需导入，缺少硬件时不会影响纯逻辑模块的使用。

## 安装

```bash
# 全部功能
pip install opencv-python pyserial

# 仅使用纯逻辑模块（帧协议+缓存），无需安装任何依赖
# 直接将 hardware_io/ 目录复制到项目中即可
```

## 30 秒快速上手

### 二进制帧编解码（无需硬件）

```python
from hardware_io import encode_frame, StreamingFrameParser

# 编码一帧：AA 55 CMD LEN DATA XOR 55 AA
frame = encode_frame(cmd=0x01, data=b"hello")
print(frame.hex())  # aa55010568656c6c6f6655aa

# 流式解析（自动处理分片、粘包、垃圾字节）
parser = StreamingFrameParser()
parser.feed(b"\x00\x01")       # 垃圾字节
# 将帧切成分片喂入
parser.feed(frame[:4])         # AA 55 01 05
parser.feed(frame[4:])         # hello + chk + 55 AA

result = parser.get_frame()
print(result.cmd, result.data)  # 1 b'hello'
```

### 线程安全帧缓存（无需硬件）

```python
from hardware_io import FrameBuffer

buf = FrameBuffer()
buf.set({"sensor": "temperature", "value": 23.5})
data, timestamp = buf.get()
print(f"数据年龄: {buf.age_ms:.1f}ms")
```

### 摄像头健壮初始化（需要 USB 摄像头）

```python
from hardware_io.camera_utils import open_camera_robust

info = open_camera_robust(preferred_width=1280, preferred_height=720, verbose=True)
ret, frame = info.cap.read()
print(f"实际分辨率: {info.width}x{info.height}, 后端: {info.backend_name}")
info.cap.release()
```

### 串口自动发现（需要 CH340 等串口设备）

```python
from hardware_io.serial_utils import find_ch340_port, open_serial

port = find_ch340_port()
if port:
    ser = open_serial(port, baudrate=115200)
    ser.write(b"PING\r\n")
    response = ser.read(100)
    ser.close()
```

## 目录结构

```
hardware_io/
├── __init__.py              # 包入口，导出纯逻辑模块的公开 API
├── frame_protocol.py        # 二进制帧编解码 + 流式解析器
├── frame_buffer.py          # 线程安全最新值缓存（泛型）
├── camera_utils.py          # 摄像头发现与健壮初始化
├── serial_utils.py          # 串口设备发现与打开
└── tests/
    ├── __init__.py
    ├── test_frame_protocol.py   # 20 个单元测试
    └── test_frame_buffer.py     # 10 个单元测试
```

## 运行测试

```bash
# 纯逻辑模块测试（无需硬件，30 个测试）
cd apps/tests
python -m pytest hardware_io/tests/ -v

# 验证硬件模块导入（不实际操作硬件）
python -c "from hardware_io.camera_utils import probe_camera; print(probe_camera())"
python -c "from hardware_io.serial_utils import list_ports; print(list_ports())"
```

## 适用场景

- 嵌入式视觉触发系统（串口命令控制摄像头抓拍）
- 工业检测设备的二进制通信协议
- 实时视频流的多线程帧传递
- USB 串口设备（CH340/CP2102/FT232等）的自动发现与连接
- 任意需要"最新值覆盖旧值"语义的生产者-消费者场景

## 不适用场景

- 需要帧队列（不丢帧）的场景——`FrameBuffer` 只保留最新值
- 高吞吐量二进制流（>10MB/s）——纯 Python 解析器性能有限，建议用 C 扩展
- Linux/macOS 的 V4L2/AVFoundation 特定功能——camera_utils 仅封装 OpenCV 跨平台接口
