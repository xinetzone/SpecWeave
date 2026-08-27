---
type: Concept
title: AI 组件
description: TuyaOpen AI 组件体系，涵盖 ai_audio 语音、ai_video 视频、ai_ui 图形、ai_mcp LLM 协议与 ai_agent 智能体
tags: [tuya, tuyaopen, ai, audio, video, ui, mcp, llm, asr, tts, agent]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuyaopen-core-source
    resource: "/references/tuyaopen-core-source.md"
    title: TuyaOpen 核心框架源码
  - id: facts-tuyaopen-core
    resource: "/references/facts-tuyaopen-core.md"
    title: TuyaOpen 核心框架事实清单
---

# AI 组件

TuyaOpen 的 AI 组件集合（`src/ai_components/`）是面向下一代 AI-agent 硬件的核心能力层，通过总开关 `ENABLE_AI_COMPONENTS`（默认关闭）统一控制。AI 组件集合包含 ai_main、ai_agent、ai_audio、ai_video、ai_picture、ai_mode、ai_mcp、ai_ui 等模块，支持中文（默认）和英文两种语言，可对接 DeepSeek、ChatGPT、Claude、Gemini 等主流 LLM。

## AI 组件架构

AI 组件采用模块化设计，每个子模块通过独立 Kconfig 控制：

```text
┌─────────────────────────────────────────┐
│            应用层（AI 产品）              │
├─────────────────────────────────────────┤
│  ai_agent   │  ai_mode  │  ai_main      │  智能体/模式管理
├─────────────┼───────────┼───────────────┤
│  ai_audio   │ ai_video  │  ai_picture   │  感知层
│  (ASR/TTS)  │ (视觉)    │  (图像)       │
├─────────────┴───────────┴───────────────┤
│  ai_mcp  (Model Context Protocol)       │  LLM 通信层
├─────────────────────────────────────────┤
│  ai_ui  (LVGL 语音交互 UI)               │  交互层
├─────────────────────────────────────────┤
│  tal_system / tal_wifi / libmqtt ...    │  TAL 基础设施
└─────────────────────────────────────────┘
```

各子模块通过 Kconfig `rsource` 引入：
- `ai_mode/Kconfig`：AI 工作模式管理
- `ai_audio/Kconfig`：音频处理
- `ai_mcp/Kconfig`：MCP 协议
- `ai_video/Kconfig`：视频处理
- `ai_picture/Kconfig`：图像处理
- `ai_ui/Kconfig`：AI 图形界面

## 语音技术栈

TuyaOpen 支持完整的语音交互链路：

| 技术 | 缩写 | 功能 |
|------|------|------|
| 自动语音识别 | ASR | 将用户语音转换为文本 |
| 关键词唤醒 | KWS | 检测唤醒词（如"你好涂鸦"） |
| 文本转语音 | TTS | 将 LLM 回复转换为语音输出 |
| 语音转文本 | STT | 语音转文字（ASR 的同义词或扩展） |

语音相关组件分布在多个模块：
- `ai_audio`：AI 音频处理管线，集成 ASR/KWS/TTS
- `audio_player`（`src/audio_player/`）：音频播放器，提供 `ai_player.h` 接口
- `tal_bluetooth`：蓝牙音频相关能力
- 外设 `audio_codecs`（`src/peripherals/audio_codecs/`）：硬件音频编解码器驱动（ES8311/ES8388/ES8389 等，ESP32 平台共享）

典型语音交互流程：
1. KWS 持续监听唤醒词 → 触发唤醒
2. ASR 录制用户语音 → 转换为文本指令
3. 文本指令通过 ai_mcp 发送到 LLM
4. LLM 返回回复文本
5. TTS 将回复合成为语音
6. audio_player 播放 TTS 音频

## ai_mcp：LLM 通信协议

ai_mcp 实现 Model Context Protocol，这是连接 AI 硬件与大语言模型的标准协议层。MCP 使得设备可以：

- 以统一接口对接多种 LLM 提供商（DeepSeek/ChatGPT/Claude/Gemini）
- 向 LLM 暴露设备能力（工具调用）
- 接收 LLM 的结构化指令并执行
- 管理对话上下文和会话状态

MCP 层位于 ai_audio/ai_video 等感知模块与 ai_agent 智能体之间，是 AI 能力的「神经通路」。通过 MCP，LLM 可以：
- 查询传感器数据（温度、湿度、运动检测等）
- 控制设备状态（灯光、开关、空调等）
- 发起音视频通话
- 查询天气和新闻
- 执行多步复杂任务

## ai_ui：AI 图形交互

ai_ui 基于 LVGL 构建，为带屏 AI 设备提供语音交互的图形界面：

- 语音波形/音量可视化
- 对话文本显示（ASR 识别结果和 LLM 回复）
- 唤醒状态动画
- 设备状态和控制面板
- 多模态交互（触摸 + 语音）

LVGL 版本可通过 Kconfig 选择 v8 或 v9，PC 端可使用 simulator 版本快速开发调试 UI。

## ai_video 与 ai_picture

视频和图像组件为智能摄像头、视觉传感器等设备提供 AI 能力：

**ai_video**：
- 视频采集与编码（H.264/H.265）
- 视频流处理
- 与 P2P 组件协同实现实时视频传输
- 视频帧预处理（缩放、格式转换 YUV→RGB）

**ai_picture**：
- 静态图像采集与处理
- JPEG 编解码（使用 libjpeg-turbo 或 TJpgDec）
- 图像缩放、旋转（tal_image 提供）
- AI 视觉识别结果展示

图像处理基础设施 `tal_image`（`src/tal_image/`）提供：
- YUV422 转 RGB
- YUV422 转二值图
- 图像旋转
- JPEG 编解码
- 图像缩放

## ai_agent 与 ai_mode

**ai_agent** 是智能体核心，负责：
- 对话管理与意图识别
- 工具调用编排（通过 MCP 调用设备能力）
- 多轮对话上下文维护
- 任务规划与执行
- 与云端 AI 服务的会话管理

**ai_mode** 管理 AI 设备的工作模式：
- 不同场景下的行为切换（正常模式/勿扰模式/看护模式等）
- 模式相关的配置和状态管理
- 模式切换时的资源分配

## 音频播放器

`src/audio_player/` 提供统一的音频播放接口 `ai_player.h`，支持：
- TTS 语音播放
- 提示音和音效
- 音乐播放
- 音量控制
- 播放状态管理

## 云端 AI 服务

`src/tuya_ai_service/` 提供涂鸦云端 AI 服务对接：
- 云端 ASR/TTS（当设备本地算力不足时）
- 云端视觉识别
- AI 技能市场接入
- 与涂鸦 IoT 云的深度集成

## 语言配置

AI 组件支持中文和英文两种语言，通过 Kconfig 选择：
- 中文（默认）：适用于中国市场设备
- 英文：适用于国际市场设备

语言配置影响：
- ASR 识别模型语言
- TTS 合成语音语言
- UI 显示文本
- LLM 对话提示词

## 外设协同

AI 组件依赖外设驱动层提供物理输入输出：

| AI 功能 | 所需外设 |
|---------|---------|
| 语音采集 | 麦克风 + audio_codecs |
| 语音输出 | 扬声器 + audio_codecs |
| 视频采集 | camera 外设 |
| 视觉显示 | display + tp（触摸屏） |
| 状态指示 | led / leds_pixel |
| 物理交互 | button / encoder / joystick |

ESP32 平台在 `boards/ESP32/common/audio/` 下提供多种音频编解码器驱动（no-codec/ES8311/ES8388/ES8389/ATK），新板卡可直接复用。

## 编译与配置

启用 AI 组件：

```ini
# app_default.config
ENABLE_AI_COMPONENTS=y
```

根据产品需求选择性启用子模块：
- 智能音箱：启用 ai_audio + ai_mcp + ai_agent + ai_ui + audio_codecs
- 智能摄像头：启用 ai_video + ai_picture + ai_mcp + ai_agent + camera + P2P
- 多模态助手：启用全部 AI 子模块 + display + tp + audio_codecs

AI 组件对资源要求较高，建议在 T5AI 或 ESP32-S3 等具备足够 RAM/Flash 和 AI 加速能力的平台上使用。

## 相关概念

- [TuyaOpen IoT 框架概览](/concepts/00-overview.md)
- [P2P 通信](/concepts/07-p2p-communication.md)
- [外设驱动](/concepts/10-peripherals.md)
- [第三方库集成](/concepts/05-third-party-libs.md)（LVGL/MicroPython）
- [BSP 板级支持](/concepts/09-board-support.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
