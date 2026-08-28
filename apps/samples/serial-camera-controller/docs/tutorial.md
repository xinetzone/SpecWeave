# 分步指导教程：从零搭建串口控制摄像头系统

本教程将引导你从零开始，使用 Python + OpenCV + pyserial 搭建一个通过串口命令控制 USB 摄像头抓图/录像的完整系统。

## 前置条件

- Windows 10/11（本教程以 Windows 为例，Linux/macOS 代码兼容但串口设备名不同）
- Python 3.9+
- USB UVC 摄像头（绝大多数 USB 摄像头免驱）
- CH340 USB 转串口模块（或开发板自带的 CH340）

## 第一步：环境准备

### 1.1 安装 Python 依赖

```bash
pip install opencv-python pyserial
```

验证安装：

```bash
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"
python -c "import serial; print(f'pyserial {serial.__version__}')"
```

### 1.2 确认硬件被系统识别

打开设备管理器，确认：
- "图像设备" 或 "照相机" 下出现 USB Camera
- "端口（COM 和 LPT）" 下出现 USB-SERIAL CH340 (COMx)

或使用命令行：

```powershell
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Camera|CH340|USB-SERIAL' } | Format-Table Status, Class, FriendlyName, InstanceId
```

记录 CH340 的 COM 端口号（如 COM4）。

## 第二步：最小化摄像头验证

创建一个简单脚本验证 OpenCV 能否打开摄像头：

```python
import cv2

# 尝试 MediaFoundation 后端（Windows 推荐）
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 设置分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 必须实际读取一帧验证设置是否生效
ret, frame = cap.read()
if ret and frame is not None:
    h, w = frame.shape[:2]
    print(f"摄像头就绪: {w}x{h}")
    cv2.imwrite("test.jpg", frame)
    print("已保存 test.jpg")
else:
    print("读取帧失败")

cap.release()
```

### 关键知识点

- **后端选择**：Windows 上优先使用 `CAP_MSMF`（MediaFoundation），`CAP_DSHOW`（DirectShow）对部分 UVC 设备兼容性差
- **分辨率验证**：`cap.set()` 返回 True 不代表设置成功，必须 `read()` 一帧检查实际尺寸
- **常见问题**：如果 1280x720 崩溃（`_step >= minstep` 断言），说明摄像头不支持该分辨率，降级到 640x480

## 第三步：最小化串口验证

```python
import serial
import serial.tools.list_ports

# 列出所有串口
print("可用串口:")
for p in serial.tools.list_ports.comports():
    print(f"  {p.device}: {p.description} (VID={p.vid:04X}, PID={p.pid:04X})")

# 打开 CH340 所在端口
ser = serial.Serial('COM4', 115200, timeout=1)
print(f"已打开 {ser.port}")

# 发送测试数据
ser.write(b'PING\r\n')
print("已发送 PING")

# 读取回应（如果有设备连接）
response = ser.readline()
print(f"收到: {response}")

ser.close()
```

### 关键知识点

- **CH340 识别**：VID=0x1A86, PID=0x7523 是沁恒 CH340 芯片的 USB 标识
- **Windows 串口独占**：一个 COM 端口同一时刻只能被一个程序打开
- **波特率**：默认 115200，8N1（8数据位、无校验、1停止位）

## 第四步：理解系统架构

在编写完整控制器之前，理解三线程架构：

```
┌─────────────────┐     帧缓存      ┌─────────────────┐
│  camera_worker  │ ──────────────→ │  _latest_frame  │
│  (持续读取摄像头) │  (Lock保护)     │  (最新一帧)      │
└─────────────────┘                 └─────────────────┘
                                           ↑
┌─────────────────┐    字节缓冲     ┌──────┴──────────┐
│  serial_worker  │ ──────────────→ │  _serial_buffer │
│  (读取串口字节)  │  (Lock保护)     │  (deque)        │
└─────────────────┘                 └─────────────────┘
                                           ↓
                                  ┌─────────────────┐
                                  │  parser_worker  │
                                  │ (解析命令+执行)  │
                                  └─────────────────┘
```

**为什么需要三个线程？**

- `cap.read()` 是阻塞调用，耗时不确定（5-33ms），放在独立线程不影响串口响应
- 串口数据可能随时到达，需要持续读取避免缓冲区溢出
- 命令解析可能涉及文件 I/O（抓图保存），不应阻塞串口读取

## 第五步：实现串口自动探测

```python
def _find_ch340():
    """自动查找 CH340 设备"""
    for port in serial.tools.list_ports.comports():
        if port.vid == 0x1A86 and port.pid == 0x7523:
            return port.device
        if 'CH340' in port.description or 'USB-SERIAL' in port.description:
            return port.device
    return None
```

自动探测避免硬编码端口号，换 USB 插口后端口号可能变化。

## 第六步：实现摄像头多后端 + 分辨率降级

核心思路：遍历后端 × 遍历分辨率，找到第一个能成功读取有效帧的组合。

```python
backends = [
    (cv2.CAP_MSMF, "MediaFoundation"),
    (cv2.CAP_DSHOW, "DirectShow"),
    (cv2.CAP_ANY, "Auto"),
]

resolutions = [
    (640, 480),   # 最通用
    (800, 600),
    (1024, 768),
    (1280, 720),
    (320, 240),
]

for backend_id, name in backends:
    cap = cv2.VideoCapture(0, backend_id)
    if not cap.isOpened():
        continue
    for w, h in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        ret, frame = cap.read()
        if ret and frame is not None and frame.size > 0:
            actual_h, actual_w = frame.shape[:2]
            if actual_w >= w // 2 and actual_h >= h // 2:
                return cap  # 成功！
    cap.release()
```

## 第七步：实现双协议解析器

### 文本协议（调试用）

以换行符（`\n` 或 `\r`）分隔，ASCII 编码：

```
CAP\r\n     → 抓图
REC\r\n     → 开始录像
STOP\r\n    → 停止录像
STAT\r\n    → 查询状态
PING\r\n    → 心跳测试
```

### 二进制帧协议（生产用）

```
AA 55 CMD LEN [DATA...] XOR 55 AA
│    │   │   │    │       │   └─ 帧尾
│    │   │   │    │       └───── XOR校验（CMD^LEN^DATA各字节）
│    │   │   │    └───────────── 数据域（0-255字节）
│    │   │   └────────────────── 数据长度
│    │   └────────────────────── 命令码
│    └────────────────────────── 帧头第二字节
└─────────────────────────────── 帧头第一字节
```

### 解析策略

1. 先在缓冲区中查找 `AA 55` 帧头
2. 如果找到完整二进制帧且校验通过，优先处理二进制命令
3. 如果没有匹配的二进制帧，查找换行符并按文本行处理
4. 缓冲区超过 512 字节无有效帧时清空，防止溢出

## 第八步：实现抓图和录像

### 抓图

```python
def _do_capture(self):
    frame, ts = self._get_latest_frame()  # 线程安全获取
    if frame is None:
        return None, "NO_FRAME"
    filename = f"capture_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(str(self.save_dir / filename), frame,
                [cv2.IMWRITE_JPEG_QUALITY, 95])
    return filename, None
```

### 录像

```python
def _do_start_record(self):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(
        str(filepath), fourcc, actual_fps, (actual_w, actual_h)
    )
    self.video_writer = writer
    self.is_recording = True
    # camera_worker 中每帧调用 writer.write(frame)
```

## 第九步：添加异常自恢复

摄像头可能因 USB 挂起、带宽不足等原因临时断流：

```python
consecutive_errors = 0
while self.running:
    try:
        ret, frame = self.cap.read()
        if ret:
            consecutive_errors = 0
            # ... 正常处理
    except cv2.error as e:
        consecutive_errors += 1
        if consecutive_errors > 30:
            self.cap.release()
            self._init_camera()  # 重新初始化
            consecutive_errors = 0
```

## 第十步：添加 GUI 和 Headless 模式

GUI 模式使用 `cv2.imshow` 显示预览，支持快捷键。Headless 模式只保持线程运行，适合服务器/嵌入式部署：

```python
def run_gui_loop(self):
    if self.headless:
        while self.running:
            time.sleep(0.1)
        return

    cv2.namedWindow("Camera Controller")
    while self.running:
        frame, _ = self._get_latest_frame()
        if frame is not None:
            cv2.imshow("Camera Controller", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            self.cmd_capture()
    cv2.destroyAllWindows()
```

## 第十一步：组装和运行

将所有组件组装到 `SerialCameraController` 类中，参考完整代码：
- [serial_camera_controller.py](../serial_camera_controller.py) — 主控制器
- [run_demo.py](../run_demo.py) — 自动演示启动器

运行：

```bash
# 带 GUI 启动
python serial_camera_controller.py

# 自动演示（3秒后自动抓图）
python run_demo.py

# 无窗口后台运行
python serial_camera_controller.py --headless
```

## 第十二步：与外部 MCU 集成

### Arduino 发送抓图命令（文本协议）

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  // 每5秒发送一次抓图命令
  delay(5000);
  Serial.println("CAP");

  // 读取控制器应答
  while (Serial.available()) {
    String response = Serial.readStringUntil('\n');
    Serial.print("Controller: ");
    Serial.println(response);
  }
}
```

### Arduino 发送抓图命令（二进制协议）

```cpp
void sendBinaryCmd(byte cmd, byte* data, byte len) {
  Serial.write(0xAA);
  Serial.write(0x55);
  Serial.write(cmd);
  Serial.write(len);
  byte xor_chk = cmd ^ len;
  for (byte i = 0; i < len; i++) {
    Serial.write(data[i]);
    xor_chk ^= data[i];
  }
  Serial.write(xor_chk);
  Serial.write(0x55);
  Serial.write(0xAA);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  sendBinaryCmd(0x01, nullptr, 0);  // CMD_CAPTURE
}
```

### 接线方式

```
Arduino/STM32          CH340 (连接PC)
    TX ────────────────── RX
    RX ────────────────── TX
   GND ───────────────── GND
```

> **注意**：CH340 模块插入 PC 后，TX/RX 引脚上的信号是 TTL 电平（3.3V/5V），可直接连接 MCU 的 UART 引脚。

## 常见问题排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| `无法打开摄像头` | 摄像头被其他程序占用 | 关闭 Teams/Zoom/相机等占用摄像头的程序 |
| `_step >= minstep` 崩溃 | 分辨率不支持 | 使用 640x480 或更低分辨率 |
| DSHOW 警告但不崩溃 | DSHOW 后端兼容性问题 | 代码会自动尝试 MSMF，可忽略 |
| `未找到CH340` | 驱动未安装或 USB 接触不良 | 安装 CH341SER 驱动，换 USB 口 |
| 串口助手打不开端口 | 控制器已占用该端口 | 先关闭控制器再用串口助手，或使用 com0com 虚拟串口 |
| 抓图全黑 | 摄像头启动中或曝光不足 | 等待 2-3 秒让摄像头自动曝光完成 |
| 录像文件无法播放 | 编码不兼容 | 使用 mp4v 编码，VLC 播放器兼容性最好 |

## 扩展建议

1. **添加配置文件**：将端口、波特率、分辨率、保存路径等放到 YAML/JSON 配置文件
2. **添加 Web 界面**：使用 Flask/FastAPI 提供 HTTP API，支持网络远程触发
3. **添加时间戳水印**：在帧上叠加时间戳和设备信息
4. **多摄像头支持**：将单实例改为字典管理多个 VideoCapture
5. **图像预处理**：抓图前可进行亮度/对比度调整、ROI 裁剪
6. **OTA 固件升级**：通过串口二进制协议为 MCU 升级固件
