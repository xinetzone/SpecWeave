---
type: Reference
title: TuyaOpen 核心框架源码
description: TuyaOpen 跨平台 AIoT SDK 源码仓库登记，包含核心模块、组件结构、平台支持与构建系统
tags: [tuya, tuyaopen, iot, sdk, source, reference, c]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-tuyaopen-core
    resource: "/references/facts-tuyaopen-core.md"
    title: TuyaOpen 核心框架事实清单
---

# TuyaOpen 核心框架源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | TuyaOpen |
| 定位 | 面向下一代 AI-agent 硬件的跨平台 C/C++ SDK |
| 许可证 | Apache License Version 2.0 |
| 主语言 | C（部分 C++） |
| 构建系统 | CMake >= 3.16 + Kconfig + tos.py |
| 仓库地址 | https://github.com/tuya/TuyaOpen |
| 官方文档 | https://tuyaopen.ai/docs/quick-start |
| 本地路径 | `d:\AI\.chaos\libs\TuyaOpen\` |

## 支持平台

| 平台 | 调试串口 | 波特率 | 说明 |
|------|---------|--------|------|
| Tuya T2 | Uart2 | 115200 | T2-U 模组 |
| Tuya T3 | Uart1 | 460800 | T3 LCD Devkit |
| Tuya T5AI | Uart1 | 460800 | BK7258 双核，AI 能力 |
| ESP32 | Uart0 | 115200 | ESP32/ESP32-S3/ESP32-C3/ESP32-C6 |
| LN882H | Uart1 | 921600 | LN882H/EWT103-W15 |
| BK7231N | Uart2 | 115200 | BK7231X 系列 |
| GD32 | - | - | GD32 系列 |
| Linux (Ubuntu/RPi) | 原生终端 | - | 参考实现，支持 DshanPi |

## 核心源码结构

源码根路径：`src/`

### TAL 系统服务（`src/tal_system/`）

| 路径 | 职责 |
|------|------|
| `include/tal_api.h` | TAL 所有 API 聚合头文件 |
| `include/tal_system.h` | 系统管理（临界区/睡眠/复位/滴答/随机数/PSRAM） |
| `include/tal_log.h` | 日志系统（6 级日志、多终端、模块级级别、颜色） |
| `include/tal_memory.h` | 内存管理（malloc/calloc/realloc/free、PSRAM） |
| `include/tal_thread.h` | 线程管理（创建/启动/删除/状态/诊断，7 级优先级） |
| `include/tal_mutex.h` | 互斥锁（创建/加锁/解锁/释放） |
| `include/tal_queue.h` | 消息队列（创建/投递/获取/释放，永久等待） |
| `include/tal_event.h` | 事件系统（发布/订阅，三种订阅类型） |
| `include/tal_workqueue.h` | 工作队列（即时/延迟任务，单次/循环） |
| `include/tal_sleep.h` | 睡眠与低功耗（回调注册/模式控制） |
| `include/tal_sw_timer.h` | 软件定时器 |
| `include/tal_time_service.h` | 时间服务 |
| `include/tal_ota.h` | OTA 升级（能力查询/开始/数据/结束/断点续传） |
| `include/tal_fs.h` | 文件系统（目录/文件操作，POSIX 风格） |
| `src/tal_api.c` | TAL→TKL 薄封装实现（mutex/ota 等直接转发） |
| `src/tal_system.c` | 系统服务实现（含 malloc 失败日志） |
| `src/tal_thread.c` | 线程实现 |
| `src/tal_workqueue.c` | 工作队列实现（信号量驱动主循环） |
| `src/tal_event.c` | 事件系统实现 |

### TAL 网络层

| 路径 | 职责 |
|------|------|
| `src/tal_wifi/include/tal_wifi.h` | WiFi（Station/AP/Sniffer/管理帧/低功耗/RF校准） |
| `src/tal_wifi/src/tal_wifi.c` | WiFi 实现 |
| `src/tal_bluetooth/` | 蓝牙（NimBLE 协议栈，CONFIG_ENABLE_BLUETOOTH） |
| `src/tal_wired/include/tal_wired.h` | 有线网络（链路状态/IP/MAC） |
| `src/tal_cellular/src/tal_cellular.c` | 蜂窝网络（描述符模式，ENABLE_CELLULAR） |
| `src/tal_network/src/tal_network.c` | 网络抽象（POSIX/LwIP 双后端） |
| `src/tal_network/src/tal_platform.c` | 平台网络适配 |
| `src/tal_network/src/tal_posix.c` | POSIX socket 实现 |

### TAL 安全层（`src/tal_security/`）

| 路径 | 职责 |
|------|------|
| `include/tal_hash.h` | 哈希算法（SHA-256/SHA-224/MD5/SHA-1、HMAC，含自测） |
| `include/tal_x509.h` | X.509 证书（PEM/DER 转换、序列号、指纹） |
| `src/tal_hash.c` | 哈希实现 |
| `src/tal_symmetry.c` | 对称加密（AES ECB/CBC/CTR，128/192/256 位） |
| `src/tal_x509.c` | X.509 实现 |

### TAL KV 存储（`src/tal_kv/`）

| 路径 | 职责 |
|------|------|
| `include/tal_kv.h` | KV 接口（set/get/free/del/批量序列化/CLI/LittleFS） |
| `src/tal_kv.c` | KV 实现（基于 LittleFS，Flash 块设备适配） |
| `src/kv_serialize.c` | JSON 序列化/反序列化 |
| `src/storage_wrapper.c` | 存储包装层 |
| `port/flashdb/` | FlashDB 移植层 |
| `port/lfs_config.h` | LittleFS 配置 |

### TAL CLI 与驱动

| 路径 | 职责 |
|------|------|
| `src/tal_cli/include/tal_cli.h` | 命令行接口（命令注册/初始化/回显） |
| `src/tal_cli/src/tal_cli.c` | CLI 实现（默认 UART0，115200 波特率） |
| `src/tal_cli/src/cli_cmd.c` | 内置 CLI 命令 |
| `src/tal_driver/uart/tal_uart.h` | UART 驱动（阻塞/异步/DMA/流控/中断回调） |
| `src/tal_driver/uart/tal_uart.c` | UART 实现 |
| `src/tal_driver/dma2d/` | DMA2D 硬件加速 |

### 图像处理（`src/tal_image/`）

| 路径 | 职责 |
|------|------|
| `include/tal_image.h` | 图像处理统一入口 |
| `src/tal_image_scale.c` | 图像缩放 |
| `src/tjpgd/` | TJpgDec JPEG 解码 |

### 云服务与 AI

| 路径 | 职责 |
|------|------|
| `src/tuya_cloud_service/` | 涂鸦云服务（4 级安全等级、BLE 配网/控制） |
| `src/tuya_ai_service/` | AI 服务 |
| `src/ai_components/` | AI 组件集合（ai_audio/ai_mcp/ai_mode/ai_ui/ai_video） |
| `src/audio_player/` | 音频播放器 |
| `src/image_album/` | 图像相册 |

### P2P 通信（`src/tuya_p2p/`）

| 路径 | 职责 |
|------|------|
| `base_ice/src/ikcp.c` | KCP 可靠 UDP 实现 |
| `base_ice/src/pj_ice.c` | ICE 协议实现 |
| `base_ice/src/pj_sdp.c` | SDP 处理 |
| `base_ice/src/tuya_media_service_rtc.c` | Tuya 媒体服务 RTC |
| `base_ice/src/tuya_sdp.c` | Tuya SDP 扩展 |
| `base_ice/src/tuya_rtp.h` | RTP 头定义 |
| `lib_rtp/include/rtp.h` | RTP 核心头文件 |
| `lib_rtp/src/` | RTP/RTCP 实现（SR/RR/BYE/APP/XR） |

### 第三方库（`src/lib*/`）

| 路径 | 库 | 版本/说明 |
|------|-----|----------|
| `src/libcjson/` | cJSON | JSON 解析，独立静态库 |
| `src/libmqtt/` | MQTT | AWS coreMQTT + Tuya 封装 |
| `src/libhttp/` | HTTP | HTTP 主机/客户端/下载/门户 |
| `src/libtls/` | mbedTLS | 3.1.0，认证加密/摘要/HMAC 封装 |
| `src/liblwip/` | LwIP | 2.1.2，含 PPP 支持 |
| `src/liblvgl/` | LVGL | v8/v9/simulator 三版本 |
| `src/libu8g2/` | U8g2 | 单色显示屏驱动库 |
| `src/libjpegturbo/` | libjpeg-turbo | JPEG 编解码 |
| `src/micropython/` | MicroPython | T5AI 平台，可配置堆/栈/REPL |
| `src/common/qrcode/` | QR Code | QR 码生成 |
| `src/common/utilities/` | 工具集 | CRC32/CRC16/随机数/混合方法 |

### 外设驱动（`src/peripherals/`）

| 路径 | 外设类型 |
|------|---------|
| `button/` | 按键 |
| `led/` | LED |
| `leds_pixel/` | LED 像素灯（WS2812 等） |
| `display/` | 显示屏 |
| `tp/` | 触摸屏 |
| `audio_codecs/` | 音频编解码器 |
| `camera/` | 摄像头 |
| `encoder/` | 旋转编码器 |
| `joystick/` | 摇杆 |
| `pmic/` | 电源管理 IC |
| `imu/` | 惯性测量单元（BMI270） |
| `ir/` | 红外 |
| `printer/` | 打印机 |

### 板级支持（`boards/`）

| 路径 | 平台 |
|------|------|
| `boards/LINUX/` | Ubuntu/Raspberry Pi/DshanPi |
| `boards/T2/` | Tuya T2 |
| `boards/T3/` | Tuya T3 |
| `boards/T5AI/` | Tuya T5AI |
| `boards/ESP32/` | ESP32 系列（含 common/ 共享驱动） |
| `boards/LN882H/` | LN882H |
| `boards/BK7231X/` | BK7231N |
| `boards/GD32/` | GD32 |

## 构建系统关键文件

| 文件 | 职责 |
|------|------|
| `CMakeLists.txt` | 顶层构建（最低 3.16，组件自动发现，tuyaos/tuyaapp 静态库） |
| `Kconfig` | 顶层 Kconfig 配置 |
| `tos.py` | Python Click 构建工具入口（14 个子命令） |
| `tools/cli_command/cli_new.py` | 项目/板卡/平台创建工具 |
| `tools/cli_command/cli_dev.py` | 批量构建与产品分发 |
| `tools/kconfiglib/` | Kconfig Python 实现 |
| `tools/check_format.py` | 代码格式检查（clang-format/中文/Doxygen 头） |
| `export.sh` / `export.ps1` / `export.bat` | 三平台环境激活脚本 |
| `pyproject.toml` | Python 项目配置 |
| `.clang-format` | LLVM 风格，4 空格缩进 |
| `Dockerfile` | Docker 构建环境 |

## 头文件路径规范

应用代码包含 TAL 头文件路径：

```c
#include "tal_api.h"        // 聚合所有 TAL API
#include "tal_log.h"        // 日志
#include "tal_thread.h"     // 线程
#include "tal_mutex.h"      // 互斥锁
#include "tal_queue.h"      // 消息队列
#include "tal_event.h"      // 事件
#include "tal_workqueue.h"  // 工作队列
#include "tal_wifi.h"       // WiFi
#include "tal_kv.h"         // KV 存储
#include "tal_security.h"   // 安全（注意：实际头文件为 tal_hash.h/tal_x509.h）
#include "tal_cli.h"        // CLI
#include "tal_ota.h"        // OTA
#include "tal_fs.h"         // 文件系统
#include "tal_uart.h"       // UART（路径为 tal_driver/uart/tal_uart.h）
```

## API 命名与返回值规范

- TAL 公开函数统一以 `tal_` 为前缀
- TKL 移植接口统一以 `tkl_` 为前缀
- 大多数函数返回 `OPERATE_RET`（int 类型），成功返回 `OPRT_OK`（0）
- 句柄类型统一使用 `void *` 不透明指针（`THREAD_HANDLE`、`MUTEX_HANDLE`、`QUEUE_HANDLE` 等）
- 头文件使用 `#ifdef __cplusplus extern "C"` 确保 C++ 兼容
- 所有 TAL 头文件包含 `tuya_cloud_types.h` 获取基础类型定义
