# serial_utils — 串口设备发现与健壮打开

封装了串口枚举、VID/PID 匹配、CH340 自动探测等模式。解决硬编码端口号在不同机器上失效、需要手动查找设备管理器等问题。

## 何时使用

- USB 转串口设备（CH340/CP2102/FT232等）的端口号在不同机器上不固定
- 需要按 USB 厂商/产品 ID 自动定位设备
- 需要快速列出系统中所有串口及其详细信息
- 需要设置合理的串口默认参数（非阻塞读超时等）

## 前置条件

```bash
pip install pyserial
```

## API 参考

### `list_ports()`

列出系统中所有可用串口及其详细信息。

**返回**：[`PortInfo`](#portinfo) 列表。

```python
from hardware_io.serial_utils import list_ports

for p in list_ports():
    print(f"{p.device}: {p.description} (VID={p.vid}, PID={p.pid})")
```

### `PortInfo`

| 字段 | 类型 | 说明 |
|------|------|------|
| `device` | `str` | 端口名（如 `"COM4"`、`"/dev/ttyUSB0"`） |
| `description` | `str` | 设备描述符 |
| `hwid` | `str` | 硬件 ID 字符串 |
| `vid` | `int \| None` | USB 厂商标识 ID |
| `pid` | `int \| None` | USB 产品标识 ID |
| `manufacturer` | `str \| None` | 制造商 |
| `serial_number` | `str \| None` | 序列号 |

### `find_port_by_vid_pid(vid, pid=None)`

按 USB VID/PID 查找串口设备。

| 参数 | 类型 | 说明 |
|------|------|------|
| `vid` | `int` | USB 厂商标识 ID（如 CH340 的 `0x1A86`） |
| `pid` | `int \| None` | USB 产品标识 ID，为 `None` 时仅匹配 VID |

**返回**：`str | None`——设备端口名，未找到返回 `None`。

```python
# 精确匹配 CH340（VID=0x1A86, PID=0x7523）
port = find_port_by_vid_pid(0x1A86, 0x7523)

# 匹配任意 FTDI 设备（VID=0x0403）
port = find_port_by_vid_pid(0x0403)
```

**常见 USB 转串口芯片 VID/PID：**

| 芯片 | VID | PID |
|------|-----|-----|
| CH340/CH341 | `0x1A86` | `0x7523` |
| CP2102 | `0x10C4` | `0xEA60` |
| FT232 | `0x0403` | `0x6001` |
| PL2303 | `0x067B` | `0x2303` |

### `find_port_by_description(keywords)`

按描述符关键词查找串口设备（不区分大小写）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `keywords` | `list[str]` | 关键词列表，描述符包含任一关键词即匹配 |

**返回**：`str | None`。

```python
port = find_port_by_description(["CH340", "USB-SERIAL", "Arduino"])
```

### `find_ch340_port()`

自动查找 CH340/CH341 USB 转串口设备，内置三级回退策略。

**返回**：`str | None`。

**查找顺序：**

1. 精确匹配 VID=`0x1A86`，PID=`0x7523`
2. 描述符包含 `"CH340"`、`"CH341"`、`"USB-SERIAL"`、`"USB2.0-SERIAL"`
3. 回退：若系统中存在 `COM4` 则返回 `"COM4"`（兼容硬编码旧代码）

```python
from hardware_io.serial_utils import find_ch340_port

port = find_ch340_port()
if port is None:
    raise RuntimeError("未找到 CH340 设备，请检查连接")
print(f"CH340 端口: {port}")
```

### `open_serial(port, baudrate=115200, ...)`

打开串口，内置适合非阻塞轮询的默认参数。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `port` | `str` | — | 端口名（如 `"COM4"`） |
| `baudrate` | `int` | `115200` | 波特率 |
| `bytesize` | `int` | `EIGHTBITS` | 数据位 |
| `parity` | `str` | `PARITY_NONE` | 校验位 |
| `stopbits` | `float` | `STOPBITS_ONE` | 停止位 |
| `timeout` | `float` | `0.05` | 读超时（秒），0.05 适合非阻塞轮询 |
| `write_timeout` | `float` | `1.0` | 写超时（秒） |
| `rtscts` | `bool` | `False` | RTS/CTS 硬件流控 |
| `dsrdtr` | `bool` | `False` | DSR/DTR 硬件流控 |

**返回**：已打开的 `serial.Serial` 实例。

**异常**：`serial.SerialException`——端口不存在、被占用或权限不足。

```python
from hardware_io.serial_utils import open_serial

ser = open_serial("COM4", baudrate=9600)
ser.write(b"AT\r\n")
response = ser.read(100)
ser.close()
```

### `get_modem_signals(ser)`

读取串口 MODEM 信号状态（CTS/DSR/RI/CD）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `ser` | `serial.Serial` | 已打开的串口实例 |

**返回**：`dict`，包含 `cts`、`dsr`、`ri`、`cd` 四个布尔值（读取失败为 `None`）。

```python
from hardware_io.serial_utils import get_modem_signals

signals = get_modem_signals(ser)
print(f"CTS={signals['cts']}, DSR={signals['dsr']}")
```

## 使用示例

### 示例 1：自动发现并连接 CH340

```python
from hardware_io.serial_utils import find_ch340_port, open_serial

port = find_ch340_port()
if not port:
    print("未找到 CH340 设备")
    exit(1)

ser = open_serial(port, baudrate=115200)
print(f"已连接 {port}")

try:
    while True:
        data = ser.read(256)
        if data:
            print(f"收到: {data.hex()}")
except KeyboardInterrupt:
    pass
finally:
    ser.close()
```

### 示例 2：按 VID/PID 查找特定设备

```python
from hardware_io.serial_utils import find_port_by_vid_pid, open_serial

# CP2102 设备
port = find_port_by_vid_pid(0x10C4, 0xEA60)
if port:
    ser = open_serial(port)
```

### 示例 3：配合帧协议解析器

```python
from hardware_io.serial_utils import find_ch340_port, open_serial
from hardware_io.frame_protocol import StreamingFrameParser

port = find_ch340_port()
ser = open_serial(port, baudrate=115200)
parser = StreamingFrameParser()

try:
    while True:
        chunk = ser.read(256)
        if chunk:
            parser.feed(chunk)
            while True:
                frame = parser.get_frame()
                if frame is None:
                    break
                print(f"CMD=0x{frame.cmd:02X} DATA={frame.data.hex()}")
finally:
    ser.close()
```

### 示例 4：列出所有串口详情

```python
from hardware_io.serial_utils import list_ports

ports = list_ports()
if not ports:
    print("未发现串口设备")
else:
    print(f"发现 {len(ports)} 个串口:")
    for p in ports:
        vid_str = f"0x{p.vid:04X}" if p.vid else "N/A"
        pid_str = f"0x{p.pid:04X}" if p.pid else "N/A"
        print(f"  {p.device:10s} {p.description}")
        print(f"             VID={vid_str} PID={pid_str}")
        if p.manufacturer:
            print(f"             制造商: {p.manufacturer}")
```

### 示例 5：跨平台设备名处理

```python
import sys
from hardware_io.serial_utils import find_port_by_vid_pid, open_serial

# 代码跨平台运行时，VID/PID 匹配比硬编码端口名更可靠
port = find_port_by_vid_pid(0x1A86, 0x7523)

if port is None:
    # 回退：Linux/macOS 常见命名
    if sys.platform.startswith("linux"):
        port = "/dev/ttyUSB0"
    elif sys.platform == "darwin":
        port = "/dev/tty.wchusbserial*"
    else:
        port = "COM4"

ser = open_serial(port, baudrate=115200)
```

## 常见陷阱

1. **Windows 串口独占**：同一 COM 端口同一时间只能被一个进程打开。如果串口助手已打开 COM4，Python 脚本再打开会抛 `SerialException`。调试时先关闭其他串口程序。
2. **`timeout=0.05` 的含义**：不是"等待 50ms 有数据就返回"，而是"最多等待 50ms，有数据立即返回"。设为 `None` 会永久阻塞，设为 `0` 会完全非阻塞（立即返回）。
3. **VID/PID 为 `None`**：非 USB 串口（如主板原生 RS232 口、蓝牙虚拟串口）没有 VID/PID，`find_port_by_vid_pid()` 无法匹配，应使用 `find_port_by_description()` 或直接指定端口名。
4. **CH340 可能有多个 PID**：不同批次/模式的 CH340 可能使用 `0x7523`、`0x5523` 等 PID。`find_ch340_port()` 的描述符回退策略可覆盖这种情况。
5. **打开后未关闭**：程序异常退出后串口可能短暂处于占用状态，等待数秒或重新插拔 USB 即可恢复。使用 `try/finally` 确保 `ser.close()` 被调用。
