# serial-camera-controller

通过 CH340 串口命令控制 USB 摄像头抓图/录像的 Python 示例项目。

## 概述

本项目演示如何在 Windows 上使用 Python + OpenCV + pyserial 构建一个完整的串口控制摄像头系统。外部 MCU/Arduino 通过串口发送文本或二进制命令，即可触发摄像头拍照或录制视频。适用于嵌入式视觉触发、工业检测抓拍、延时摄影等场景。

## 硬件要求

| 设备 | 说明 |
|------|------|
| USB 摄像头 | 标准 UVC 摄像头（Windows 内置 usbvideo.sys 驱动） |
| CH340 USB转串口 | 沁恒 CH340/CH341 芯片（VID_1A86&PID_7523） |
| USB 数据线 | 连接上述设备到 PC |

> **注意**：实际产品部署时，CH340 的 TX/RX 引脚连接外部 MCU（Arduino/STM32 等），MCU 发送命令到 PC 端控制器。开发调试时也可以用串口助手直接发送文本命令。

## 目录结构

```
serial-camera-controller/
├── README.md                        # 本文件
├── serial_camera_controller.py      # 主控制器（双协议+三线程+自动降级）
├── run_demo.py                      # GUI演示启动器（3秒后自动CAP）
├── captures/                        # 抓图/录像保存目录
└── docs/
    ├── retrospective.md             # 里程碑复盘报告
    ├── tutorial.md                  # 分步指导教程
    └── protocol.md                  # 串口通信协议文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install opencv-python pyserial
```

### 2. 连接硬件

- 将 USB 摄像头插入 PC
- 将 CH340 模块插入 PC（确认设备管理器中出现 COM 端口）

### 3. 运行

```bash
# 带GUI预览启动（推荐）
python serial_camera_controller.py

# 或运行自动演示（启动后3秒自动抓一张图）
python run_demo.py

# 无窗口后台模式（适合服务器/嵌入式部署）
python serial_camera_controller.py --headless

# 指定端口和波特率
python serial_camera_controller.py --port COM4 --baud 115200
```

### 4. 发送命令

GUI 窗口中使用快捷键：

| 按键 | 功能 |
|------|------|
| s | 抓图 |
| r | 开始/停止录像 |
| 空格 | 查询状态 |
| q | 退出 |

或通过串口发送命令（详见 [协议文档](docs/protocol.md)）。

## 核心特性

- **双协议支持**：文本行协议（串口助手直接调试）+ 二进制帧协议（嵌入式可靠通信）
- **三线程架构**：摄像头采集 / 串口读取 / 命令解析 互不阻塞
- **分辨率自动降级**：多后端（MSMF→DSHOW→ANY）+ 多分辨率候选，适配不同UVC摄像头
- **异常自恢复**：摄像头连续读取错误后自动重新初始化
- **线程安全帧缓存**：锁保护的最新帧，子毫秒级延迟
- **Headless 模式**：分离 GUI 与业务逻辑，支持无显示器部署

## 命令列表

### 文本协议（以 `\r\n` 结尾）

| 命令 | 应答 | 说明 |
|------|------|------|
| `CAP` | `OK:capture_xxx.jpg` | 抓图 |
| `REC` | `OK:RECORDING:record_xxx.mp4` | 开始录像 |
| `STOP` | `OK:STOPPED:record_xxx.mp4:3.0s:90frames` | 停止录像 |
| `STAT` | `STATUS:IDLE:OK(5ms_ago):port=COM4` | 查询状态 |
| `PING` | `PONG:SerialCameraController v1.0` | 心跳测试 |
| `HELP` | `HELP:CAP=抓图 REC=录像 ...` | 帮助 |

### 二进制帧协议

帧格式：`AA 55 CMD LEN [DATA...] XOR 55 AA`

| CMD | 方向 | 功能 |
|-----|------|------|
| 0x01 | 主机→控制器 | 抓图 |
| 0x02 | 主机→控制器 | 开始录像 |
| 0x03 | 主机→控制器 | 停止录像 |
| 0x10 | 主机→控制器 | 查询状态 |
| 0x81 | 控制器→主机 | 抓图应答（DATA=文件名UTF-8） |
| 0x82 | 控制器→主机 | 录像控制应答 |
| 0x90 | 控制器→主机 | 状态应答（DATA=[recording, frame_ok]） |
| 0xE0 | 控制器→主机 | 错误应答 |

## 技术说明

- **OpenCV 后端优先级**：MediaFoundation（MSMF）→ DirectShow（DSHOW）→ 自动。部分国产 UVC 摄像头（如 VID_FFFF 设备）在 DSHOW 下无法按索引打开，但 MSMF 正常。
- **分辨率验证**：`cap.set()` 在某些摄像头上会静默失败（不报错但设置不生效），因此代码在设置后实际 `read()` 一帧验证真实分辨率。
- **Windows 串口独占**：同一 COM 端口同一时刻只能被一个进程打开。控制器运行时，外部串口助手无法同时打开该端口——这是 Windows 设计限制，非 Bug。

## 文档

- [分步指导教程](docs/tutorial.md) — 从零开始搭建本项目的完整教程
- [里程碑复盘报告](docs/retrospective.md) — 开发过程复盘、问题记录、经验总结
- [串口通信协议](docs/protocol.md) — 文本协议和二进制帧协议的完整定义

## License

MIT
