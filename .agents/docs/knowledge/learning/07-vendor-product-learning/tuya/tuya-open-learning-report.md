---
id: "tuya-open-learning-report"
title: "TuyaOpen 全面学习报告"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/07-vendor-product-learning/tuya/tuya-open-learning-report.toml"
category: "learning"
tags: ["tuya", "tuyaopen", "iot", "sdk", "ai", "embedded", "c", "cpp", "mcu", "esp32", "mcp", "cloud", "tkl", "tal", "tdd", "tdl"]
date: "2026-06-30"
status: "stable"
author: "Tuya"
summary: "TuyaOpen 是涂鸦开源的跨平台、跨芯片、跨操作系统的 AI-IoT SDK，核心目标是用一套灵活的 C/C++ SDK，结合涂鸦云的低延迟多模态 AI 能力，简化开放式 AI-IoT 生态的搭建。"
---
# TuyaOpen 全面学习报告

> 仓库地址：`git@github.com:tuya/TuyaOpen.git`
> 许可证：Apache License 2.0
> 定位：面向下一代 AI 智能体硬件的跨平台 IoT 开发 SDK（C/C++）

---

## 一、项目概述

TuyaOpen 是涂鸦（Tuya）开源的**跨平台、跨芯片、跨操作系统的 AI-IoT SDK**。其核心目标是用一套灵活的 C/C++ SDK，结合涂鸦云的低延迟多模态 AI 能力，简化开放式 AI-IoT 生态的搭建。

### 核心能力
- **AI 语音技术**：ASR（语音识别）、KWS（关键词唤醒）、TTS（语音合成）、STT（语音转文字）
- **主流大模型集成**：Deepseek、ChatGPT、Claude、Gemini 等
- **多模态 AI**：文本、语音、视觉、传感器
- **云端连接**：远程控制、监控、OTA 升级
- **生态兼容**：Google Home、Amazon Alexa
- **多种连接方式**：Wi-Fi、蓝牙（BLE）、以太网、蜂窝（Cellular）
- **内置安全**：设备认证、数据加密（mbedTLS）

### 支持的目标平台
| 平台 | 状态 | 说明 |
| --- | --- | --- |
| Ubuntu / Linux | 支持 | 可直接在 Linux 主机运行（含树莓派、DshanPi、TaishanPi） |
| Tuya T2 / T3 / T5 | 支持 | 涂鸦自研 Wi-Fi/BLE MCU（T5 为 AI 主力芯片） |
| ESP32 / ESP32-C3 / S3 / C6 / P4 | 支持 | 乐鑫系列 |
| BK7231N（BK7231X） | 支持 | 博通集成 Wi-Fi MCU（CBU/CB3S 等模组） |
| LN882H | 支持 | 凌芯 Wi-Fi MCU |
| GD32 | 支持 | 兆易创新 MCU（含 RISC-V VW553） |

---

## 二、顶层目录结构

```
TuyaOpen/
├── apps/            # 完整应用示例（AI 聊天机器人、机器狗、桌面机器人、像素屏等）
├── boards/          # 各芯片平台的开发板定义（板级配置 board_com_api）
├── docs/            # 文档与设计稿（plans/specs/skills）
├── examples/        # 基础功能示例（按类别组织）
├── platform/        # 各平台 SDK（克隆后按需下载，含 toolchain）
├── src/             # SDK 核心源码（分层组件）
├── tests/           # 测试（含 export 流程测试）
├── tools/           # 构建/烧录/配置工具链（tos.py CLI、Kconfig、porting）
├── CMakeLists.txt   # 顶层构建入口
├── tos.py           # 核心命令行工具（Tuya Uart Tool）
├── Dockerfile       # 容器化构建环境
├── AGENTS.md        # AI 智能体协作说明（环境/构建/校验）
└── README.md / README_zh.md
```

---

## 三、核心架构：分层设计

TuyaOpen 采用经典的**嵌入式分层架构**，自下而上贯通"硬件适配 → 操作系统抽象 → 设备驱动 → 云服务 → AI 组件 → 应用"。命名前缀是理解整个项目的关键钥匙：

### 命名前缀约定（最重要）
| 前缀 | 全称 | 层级 | 职责 |
| --- | --- | --- | --- |
| **TKL** | Tuya Kernel Layer | 内核适配层 | 直接对接芯片/RTOS 的硬件抽象（uart/gpio/timer/wifi…），**移植时必须实现** |
| **TAL** | Tuya Abstract Layer | 抽象层 | 在 TKL 之上提供统一 OS/系统 API（日志、内存、线程、信号量、KV、OTA…） |
| **TDD** | Tuya Device Driver | 设备驱动层 | 具体硬件器件的底层驱动（如 `tdd_button_gpio`） |
| **TDL** | Tuya Device Library | 设备库层 | 对上层提供器件无关的统一接口（如 `tdl_button_manage`） |

> **驱动二层模型**：`TDD`（具体器件实现）+ `TDL`（统一抽象接口）。例如按键：`tdd_button_gpio.c`（GPIO 实现）→ `tdl_button_manage.c`（统一管理），上层应用只调用 TDL 接口，更换硬件只需替换 TDD。

### src/ 核心组件清单
| 组件 | 说明 |
| --- | --- |
| `tal_system` | OS 抽象核心：日志/内存/线程/互斥/信号量/队列/软定时器/OTA/工作队列 |
| `tal_driver` | 驱动抽象（uart、dma2d 等） |
| `tal_kv` | 键值存储（子模块 FlashDB + littlefs） |
| `tal_wifi` / `tal_bluetooth` / `tal_cellular` / `tal_wired` | 各类连接抽象 |
| `tal_network` / `tal_security` | 网络与安全抽象 |
| `tuya_cloud_service` | **涂鸦云服务**：设备认证、MQTT、ATOP、配网、OTA、天气、局域网、证书管理 |
| `tuya_ai_service` | AI 服务接入 |
| `ai_components` | **AI 应用组件**（见下文专章） |
| `audio_player` | 音频播放引擎（解码 mp3/opus/wav、重采样、混音、播放队列） |
| `image_album` / `peripherals` | 图像相册、外设驱动集合 |
| `libtls`（mbedTLS 3.1）/ `liblwip` / `libmqtt`（coreMQTT）/ `libhttp`（coreHTTP）/ `libcjson` / `liblvgl`（v8 & v9）/ `libjpegturbo` | 第三方库集成 |

### Git 子模块（第三方依赖）
- `FlashDB`（armink）— Flash KV 数据库
- `littlefs` — 掉电安全文件系统
- `cJSON`（DaveGamble）— JSON 解析
- `backoffAlgorithm`（FreeRTOS）— 重连退避算法

---

## 四、AI 组件子系统（项目的核心亮点）

`src/ai_components/` 是 TuyaOpen 区别于传统 IoT SDK 的关键，构成完整的"端侧 AI 智能体"框架：

| 子模块 | 职责 |
| --- | --- |
| `ai_agent` | AI 智能体核心 |
| `ai_audio` | 音频输入采集 + 音频播放器 |
| `ai_main` | AI 聊天主流程 + 聊天 UI（`ai_chat_main` / `ai_chat_ui`） |
| `ai_mcp` | **MCP（Model Context Protocol）** 服务端与工具（端侧工具调用） |
| `ai_mode` | 对话模式：free（自由）/ hold（长按）/ oneshot（单次）/ wakeup（唤醒） |
| `ai_picture` | 图片输入/输出（视觉多模态） |
| `ai_video` | 视频输入 |
| `ai_skills` | 技能：云事件、情绪、音乐故事 |
| `ai_ui` | LVGL UI（聊天界面 chatbot/oled/wechat、相册、流式文本、图标字体、中文字体） |
| `assets` | 多语言、媒体资源（提示音）、本地告警 |

---

## 五、云服务子系统（tuya_cloud_service）

负责设备与涂鸦云的全部交互，是商业化的核心：

| 子目录 | 职责 |
| --- | --- |
| `cloud/` | IoT 核心：`tuya_iot`（设备生命周期）、`mqtt_service`、`atop_service`（涂鸦 API 协议）、`tuya_ota`、`iotdns`、证书管理、设备元数据、健康检查 |
| `authorize/` | 设备授权 |
| `netcfg/` / `netmgr/` | 配网与网络管理 |
| `ble/` | 蓝牙配网/控制 |
| `lan/` | 局域网控制 |
| `weather/` | 天气服务 |
| `protocol/` / `schema/` / `transport/` / `tls/` | 协议、DP 模型、传输层、加密 |

### 关键 API（设备接入主流程）
```c
tuya_iot_init(client, config);        // 初始化（PID、授权信息）
tuya_iot_start(client);               // 启动连云
tuya_iot_dp_report_json(client, dps); // 上报数据点（DP）
```
设备通过 **DP（Data Point，数据点）** 模型与云/APP 交互，支持远程控制、局域网控制、蓝牙控制三种通道。

---

## 六、构建系统与 tos.py 工具链

### 构建核心：CMake + Kconfig
- 顶层 `CMakeLists.txt` 通过 `list_components()` 自动扫描 `src/` 下所有组件并加入构建。
- 使用 **Kconfig**（`tools/kconfiglib`）做可视化配置，生成 `using.config` 和 `tuya_kconfig.h`。
- 每个平台有独立 `toolchain_file.cmake`、`platform_config.cmake`、`build_example.py`。
- 板级配置在 `boards/<平台>/<开发板>/`，应用默认配置为 `app_default.config`。
- 强制 **out-of-source 构建**（禁止在源码目录直接构建）。

### tos.py — 统一命令行工具（基于 click）
| 子命令 | 用途 |
| --- | --- |
| `tos.py prepare` | 安装 SDK 主机工具链 |
| `tos.py check` | 校验工具与子模块 |
| `tos.py config choice` | 交互式选择开发板 |
| `tos.py config menu` | 交互式 menuconfig 修改配置 |
| `tos.py build` | 编译当前工程 |
| `tos.py clean` | 清理 |
| `tos.py flash` | 烧录固件 |
| `tos.py monitor` | 串口监视 |
| `tos.py new` | 从模板创建新工程 |
| `tos.py update` / `idf` / `dev` | 更新 / ESP-IDF 集成 / 开发辅助 |

### 标准开发流程
```bash
# 1. 初始化环境（创建 .venv，uv sync，安装主机工具）
. ./export.sh          # Windows: . .\export.ps1

# 2. 校验环境
tos.py check

# 3. 进入示例工程
cd examples/<category>/<project>   # 或 apps/<...>

# 4. 选板 → 配置 → 编译
tos.py config choice
tos.py config menu      # 可选
tos.py build

# 5. 产物
#   中间产物：<project>/.build/
#   最终固件：<project>/dist/   （LINUX 目标产出原生 ELF）

# 6. 烧录
tos.py flash
```

---

## 七、示例与应用工程

### examples/（基础功能示例，按类别）
`ble` / `wifi`（ap/sta/scan/low_power）/ `protocols` / `peripherals` / `system` / `graphics` / `multimedia` / `e-Paper` / `tflite` / `get-started`（sample_project 入门模板、cxx）

入门模板 `sample_project.c` 展示了最小程序结构：
```c
int user_main() {
    tal_log_init(TAL_LOG_LEVEL_DEBUG, 1024, (TAL_LOG_OUTPUT_CB)tkl_log_output);
    PR_NOTICE("TuyaOpen version: %s", OPEN_VERSION);
    PR_DEBUG("hello world\r\n");
    // ...
}
```
> 应用入口统一为 `user_main()`，通过 `tal_api.h` 一站式引入 TAL 全部能力。

### apps/（完整产品级应用）
| 应用 | 说明 |
| --- | --- |
| `tuya.ai/your_chat_bot` | 大模型语音聊天机器人（语音/按键唤醒、表情、LCD/APP 实时聊天、蓝牙配网） |
| `tuya.ai/your_desk_emoji` | 桌面表情机器人 |
| `tuya.ai/your_otto_robot` / `your_robot_dog` | Otto 机器人 / 机器狗 |
| `tuya.ai/your_serial_chat_bot` | 串口聊天机器人 |
| `tuya_cloud/switch_demo` | 跨平台开关示例（远程/局域网/蓝牙三通道控制） |
| `tuya_cloud/camera_demo` / `weather_get_demo` | 摄像头 / 天气示例 |
| `tuya_t5_pixel/*` | T5 像素屏系列（天气、频谱、特效、键盘猫等） |
| `tuya_t5_pocket` | T5 口袋 AI 设备（含硬件原理图） |
| `mimiclaw` | 完整 AI 智能体（含 LLM 代理、记忆、技能、定时、多渠道 Discord/飞书/Telegram bot） |
| `games/lvgl_games` / `micropython/mpy_minimal` | LVGL 游戏 / MicroPython 最小示例 |

---

## 八、硬件移植（Porting）机制

移植到新芯片/新板子时的工作集中在两处：

1. **平台移植**（`tools/porting/`）：
   - `kernel_porting.py` / `porting_new_file.py` 辅助生成适配文件
   - `adapter/` 下按外设给出 TKL 接口头文件模板（uart/wifi/timer/watchdog/vad/wakeup…）
   - **移植 = 实现 TKL 层接口** 对接目标芯片的寄存器/RTOS
2. **板级定义**（`boards/<平台>/<板子>/`）：
   - `board_com_api.c/.h` 定义板级初始化（显示、按键、音频、电源域等）
   - `Kconfig` + `<板子>.config` 定义可选配置与默认值

---

## 九、配套工程与开发辅助

- **Arduino for TuyaOpen**：`github.com/tuya/arduino-TuyaOpen`
- **Luanode for TuyaOpen**：`github.com/tuya/luanode-TuyaOpen`
- **TuyaOpen Dev Skills**：`github.com/tuya/TuyaOpen-dev-skills`（Cursor AI 开发技能：环境/编译/烧录/授权）
- **代码规范**：`tools/check_format.py` + `.clang-format`（基于 clang-format）
- **CI**：GitHub Actions（`check-build-apps`、`release`、`sync-to-gitee`）
- **文档中心**：https://tuyaopen.ai/docs/about-tuyaopen

---

## 十、学习路径建议

1. **入门**：阅读 `README_zh.md` → 跑通 `examples/get-started/sample_project`（建议先用 LINUX 目标本机编译）。
2. **理解分层**：掌握 TKL/TAL/TDD/TDL 四层命名约定，这是阅读全部源码的基础。
3. **连云实战**：研究 `apps/tuya_cloud/switch_demo`，理解 `tuya_iot` 接入与 DP 模型。
4. **AI 进阶**：研究 `apps/tuya.ai/your_chat_bot` + `src/ai_components/`，理解端侧 AI 智能体框架与 MCP 工具调用。
5. **硬件移植**：参考 `tools/porting/` 与 `boards/`，尝试适配新开发板。
6. **构建精通**：吃透 `CMakeLists.txt` + Kconfig + `tos.py` 的协作关系。

---

## 总结

TuyaOpen 是一套**工程化程度很高的 AI-IoT SDK**，三大设计精髓：

1. **严格分层（TKL/TAL/TDD/TDL）**——实现一次开发、跨芯片复用，移植成本集中在 TKL 层。
2. **CMake + Kconfig + tos.py 三位一体的构建体系**——统一了多平台、多开发板、多应用的配置与编译、烧录、监视全流程。
3. **端云一体的 AI 能力**——把云端多模态大模型与端侧语音/视觉/UI/MCP 工具调用打通，是面向"AI 硬件"的差异化竞争力。