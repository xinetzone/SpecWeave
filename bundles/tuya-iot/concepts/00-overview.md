---
type: Concept
title: TuyaOpen IoT 框架概览
description: TuyaOpen 跨平台 AIoT SDK 的整体定位、双层架构、平台支持、全栈能力与生态组成
tags: [tuya, tuyaopen, iot, sdk, overview, 嵌入式, aiot]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuyaopen-core-source
    resource: "/references/tuyaopen-core-source.md"
    title: TuyaOpen 核心框架源码
  - id: tuya-skills-source
    resource: "/references/tuya-skills-source.md"
    title: TuyaOpen 技能与生态源码
  - id: facts-tuyaopen-core
    resource: "/references/facts-tuyaopen-core.md"
    title: TuyaOpen 核心框架事实清单
---

# TuyaOpen IoT 框架概览

TuyaOpen 是面向下一代 AI-agent 硬件的跨平台 C/C++ SDK，支持涂鸦 T 系列 WiFi/BT MCU、树莓派、ESP32 等硬件平台。它采用 TAL/TKL 双层抽象架构，提供从底层驱动到云端连接再到 AI 能力的全栈 IoT 开发框架，使应用代码可在 8 款芯片平台间零修改移植。

## 项目定位

TuyaOpen 的核心设计目标是为 AIoT 设备提供统一的开发平台。与传统 IoT SDK 仅提供网络连接能力不同，TuyaOpen 覆盖了智能设备完整技术栈：

- **语音技术**：ASR（自动语音识别）、KWS（关键词唤醒）、TTS（文本转语音）、STT（语音转文本）
- **AI 集成**：可对接 DeepSeek、ChatGPT、Claude、Gemini 等主流 LLM 和 AI 平台
- **生态兼容**：支持 Google Home 和 Amazon Alexa 设备兼容
- **连接方式**：蓝牙、Wi-Fi、以太网等多种网络连接方式

项目采用 Apache License Version 2.0 开源许可证，相关生态项目包括 Arduino for TuyaOpen、Luanode for TuyaOpen、TuyaOpen Dev Skills。

## 支持的硬件平台

TuyaOpen 支持 8 款目标平台，每款平台有固定的调试串口配置：

| 平台 | 调试串口 | 波特率 | 说明 |
|------|---------|--------|------|
| Ubuntu/Linux | 原生终端 | - | 参考实现，支持树莓派/DshanPi |
| Tuya T2 | Uart2 | 115200 | T2-U 模组 |
| Tuya T3 | Uart1 | 460800 | T3 LCD Devkit |
| Tuya T5AI | Uart1 | 460800 | BK7258 双核，AI 能力 |
| ESP32 | Uart0 | 115200 | ESP32/ESP32C3/ESP32S3 |
| LN882H | Uart1 | 921600 | 高波特率平台 |
| BK7231N | Uart2 | 115200 | BK7231X 系列 |
| GD32 | - | - | GD32 系列 |

平台选择通过 Kconfig `choice` 结构配置，确保同一时刻只有一个目标板被编译。每个板级选项对应一个 `BOARD_CHOICE_XXX` 配置项。

## TAL/TKL 双层架构

TuyaOpen 的架构核心是 TAL（Tuya Abstract Layer）与 TKL（Tuya Kernel Layer）的分离：

**TAL（涂鸦抽象层）** 是应用层 API，所有公开函数以 `tal_` 为前缀。`tal_api.h` 是聚合头文件，集中包含 20+ 模块：

- 日志诊断（`tal_log.h`）
- 内存管理（`tal_memory.h`）
- 并发原语（`tal_mutex.h`、`tal_semaphore.h`、`tal_thread.h`）
- OTA 更新（`tal_ota.h`）
- 线程间通信（`tal_queue.h`、`tal_workqueue.h`）
- 时间与定时器（`tal_sleep.h`、`tal_sw_timer.h`、`tal_time_service.h`）
- 系统工具（`tal_system.h`）
- 硬件接口（`tal_uart.h`）
- 配置存储（`tal_kv.h`）
- 安全加密（`tal_security.h`）
- 事件处理（`tal_event.h`）
- 网络抽象（`tal_network.h`）
- CLI 命令行（`tal_cli.h`）

**TKL（涂鸦内核层）** 是移植接口，由各芯片平台厂商实现。TAL 函数通常是 TKL 函数的薄封装——例如 `tal_mutex_create_init()` 直接调用 `tkl_mutex_create_init()`，`tal_ota_data_process()` 直接调用 `tkl_ota_data_process()`。

这种双层设计使得应用代码只需依赖 TAL 头文件，即可在所有支持平台间无缝移植。代码层级规则严格禁止应用层（apps/）和 SDK 组件层（src/）直接调用芯片厂商 SDK，必须通过 TKL/TAL 接口。

## API 设计规范

TAL 层遵循统一的设计规范：

1. **命名前缀**：所有公开函数以 `tal_` 为前缀（如 `tal_thread_create_and_start`、`tal_mutex_lock`）
2. **返回值**：大多数函数返回 `OPERATE_RET`（int 类型），成功返回 `OPRT_OK`（0）
3. **句柄类型**：统一使用 `void *` 不透明指针定义（`THREAD_HANDLE`、`MUTEX_HANDLE`、`QUEUE_HANDLE`、`WORKQUEUE_HANDLE`）
4. **C++ 兼容**：头文件使用 `#ifdef __cplusplus extern "C"` 结构
5. **基础类型**：统一包含 `tuya_cloud_types.h` 获取类型定义

## 全栈能力矩阵

TuyaOpen 在 `src/` 目录下提供 30+ 可裁剪组件：

| 层级 | 组件 | 说明 |
|------|------|------|
| 系统服务 | tal_system | 临界区/睡眠/复位/滴答/随机数/PSRAM |
| 日志 | tal_log | 6 级日志、多终端、模块级级别、ANSI 颜色 |
| 并发 | tal_thread/tal_mutex/tal_queue/tal_semaphore | 线程/互斥锁/队列/信号量 |
| 调度 | tal_workqueue/tal_sw_timer/tal_event | 工作队列/软件定时器/事件系统 |
| 网络 | tal_wifi/tal_bluetooth/tal_wired/tal_cellular | WiFi/BLE/有线/蜂窝 |
| 安全 | tal_hash/tal_x509/tal_symmetry/libtls | SHA/MD5/HMAC/AES/X.509/mbedTLS |
| 存储 | tal_kv | LittleFS KV 存储、JSON 序列化 |
| 文件系统 | tal_fs | POSIX 风格文件/目录操作 |
| OTA | tal_ota | 全量/差分升级、断点续传 |
| CLI | tal_cli | 串口命令行、自定义命令注册 |
| 驱动 | tal_uart/tal_driver | UART/DMA2D 等硬件驱动 |
| 中间件 | libmqtt/libhttp/libcjson/liblwip | MQTT/HTTP/JSON/TCP-IP 协议栈 |
| 图形 | liblvgl/libu8g2 | LVGL v8/v9、U8g2 单色屏库 |
| P2P | tuya_p2p | ICE/KCP/RTP/RTCP 音视频传输 |
| AI | ai_components | ai_audio/ai_video/ai_ui/ai_mcp/ai_agent |
| 云 | tuya_cloud_service | 涂鸦云对接、4 级安全等级 |
| 外设 | peripherals | 13 类驱动（按键/LED/显示/触摸/摄像头等） |
| 脚本 | micropython | MicroPython 运行时（T5AI 平台） |

## 构建系统

TuyaOpen 使用 CMake（>= 3.16）+ Kconfig + tos.py 三位一体构建系统：

- **CMake**：通过 `list_components()` 自动发现 `src/` 下所有含 CMakeLists.txt 的子目录作为组件，最终打包为 `tuyaos` 静态库
- **Kconfig**：通过 menuconfig 配置组件开关和参数，生成 `tuya_kconfig.h`
- **tos.py**：Python Click 命令行工具，提供 14 个子命令（version/prepare/check/config/build/clean/flash/monitor/update/new/dev/idf/hello 等）

配置管道为：`app_default.config` → `.build/cache/using.config` → `.build/cache/using.cmake` → `.build/cache/include/tuya_kconfig.h`。

## 生态组成

TuyaOpen 生态包含多个互补项目：

- **TuyaOpen Dev Skills**：10 个 AI 编码助手技能，覆盖环境搭建、构建、项目配置、代码检查、板卡移植、开发循环、设备授权、调试辅助、崩溃解码、CLI 调试
- **OpenClaw 云 API**：基于涂鸦 2C 终端用户 API，覆盖 3000+ 智能硬件品类，提供家庭/设备/天气/通知/统计/IPC/消息订阅等 10 大功能模块
- **Home Assistant 集成**：Tuya 设备的 Home Assistant 官方集成
- **Arduino for TuyaOpen**：Arduino 框架支持
- **Luanode for TuyaOpen**：Lua 脚本支持

## 相关概念

- [TAL 抽象层架构](/concepts/01-tal-architecture.md)
- [系统服务](/concepts/02-system-services.md)
- [网络栈](/concepts/03-network-stack.md)
- [安全与 KV 存储](/concepts/04-security-kv.md)
- [构建系统](/concepts/06-build-system.md)
- [AI 开发技能体系](/concepts/11-dev-skills.md)
