# 概念文档

## 架构基础（第一批）

* [00 — TuyaOpen IoT 框架概览](00-overview.md) — 跨平台 C/C++ SDK 定位、8 款芯片平台、TAL/TKL 双层架构、全栈能力矩阵与生态组成
* [01 — TAL 抽象层架构](01-tal-architecture.md) — TAL/TKL 双层模型、模块全景、API 命名规范、返回值约定、句柄生命周期、C++ 兼容与代码层级规则
* [02 — 系统服务](02-system-services.md) — 线程/互斥锁/队列/事件/工作队列、内存管理、6 级日志、临界区、睡眠、OTA 与文件系统
* [03 — 网络栈](03-network-stack.md) — WiFi Station/AP/Sniffer、BLE NimBLE、有线/蜂窝网络、POSIX/LwIP 双后端与 MQTT/HTTP/mbedTLS 中间件
* [04 — 安全与 KV 存储](04-security-kv.md) — SHA/MD5/HMAC/AES/X.509/mbedTLS 加密体系与 LittleFS KV 存储、8 种数据类型、批量操作与设备凭据实践
* [05 — 第三方库集成](05-third-party-libs.md) — cJSON/MQTT/HTTP/LwIP/LVGL/U8g2/libjpeg-turbo/MicroPython 等库的集成模式与选择策略
* [06 — 构建系统](06-build-system.md) — CMake+Kconfig+tos.py 三件套、组件自动发现、config/build/clean/new/dev 命令与项目结构

## 应用与生态（第二批）

* [07 — P2P 通信](07-p2p-communication.md) — ICE NAT 穿透、KCP 可靠 UDP、RTP/RTCP 媒体传输、SDP 协商与 IPC 音视频通信架构
* [08 — AI 组件](08-ai-components.md) — ai_audio（ASR/KWS/TTS）、ai_video、ai_picture、ai_mcp（LLM 协议）、ai_agent、ai_ui 与 ai_mode
* [09 — BSP 板级支持](09-board-support.md) — 8 款芯片平台、代码层级隔离、板卡目录结构、ESP32 共享驱动、Kconfig choice 与移植流程
* [10 — 外设驱动](10-peripherals.md) — 13 类外设（按键/LED/显示/触摸/摄像头/音频/IMU/PMIC）、UART 驱动、CLI 命令行与 tal_image 图像处理
* [11 — AI 开发技能体系](11-dev-skills.md) — 10 个 Agent Skills（环境搭建/构建/配置/检查/移植/开发循环/授权/调试/崩溃解码/CLI）与 MCP 协同
* [12 — OpenClaw 云 API](12-openclaw-api.md) — 涂鸦 2C 终端用户 API、7 大数据中心、10 大功能模块、REST/WebSocket 双协议与设备控制工作流
* [13 — Home Assistant 集成](13-ha-integration.md) — Tuya v2 与 Smart Life 两代集成对比、16 个 HA 平台、配置流程与本地控制现状
* [14 — IoT 开发完整工作流](14-iot-workflow.md) — 从环境搭建到 OTA 部署的十阶段流程、AI 技能辅助、嵌入式最佳实践与内存/实时性/功耗优化

```{toctree}
:maxdepth: 2

00-overview
01-tal-architecture
02-system-services
03-network-stack
04-security-kv
05-third-party-libs
06-build-system
07-p2p-communication
08-ai-components
09-board-support
10-peripherals
11-dev-skills
12-openclaw-api
13-ha-integration
14-iot-workflow
```