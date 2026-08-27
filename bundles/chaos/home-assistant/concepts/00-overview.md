---
type: Concept
title: Home Assistant 概览
description: 了解 Home Assistant 是什么、核心能力、架构一览，快速建立对智能家居自动化平台的整体认知
tags: [home-assistant, smart-home, overview, beginner]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: core-source
    resource: "/references/core-source.md"
    title: Home Assistant 核心框架源码
  - id: components-source
    resource: "/references/components-source.md"
    title: Home Assistant Components 集成源码
---

# Home Assistant 概览

## 什么是 Home Assistant

Home Assistant（简称 HA）是一个用 Python 编写的开源智能家居自动化平台。它的核心使命是将家庭中来自不同厂商、使用不同协议的智能设备统一到一个本地运行的系统中，实现设备状态监控、远程控制和场景自动化。

与云端智能家居平台不同，Home Assistant 强调**本地优先**：核心运行时不依赖外部云服务，数据存储在本地，即使互联网中断也能正常工作。同时，它通过 2000+ 集成（integration）连接几乎所有主流智能设备品牌和通信协议，包括 Philips Hue、小米、Z-Wave、Zigbee、MQTT、Matter 等。

从技术角度看，Home Assistant 是一个基于 Python `asyncio` 的**事件驱动系统**。设备状态变化产生事件，自动化规则监听事件并触发动作，所有组件通过事件总线松耦合通信。这种架构使得 HA 能够高效处理大量设备的实时状态更新和服务调用。

## 核心能力

### 1. 设备统一抽象

Home Assistant 将千差万别的设备抽象为标准化的**实体（Entity）**。一盏灯无论来自 Philips Hue 还是小米米家，在 HA 中都是一个 `LightEntity`，具备统一的 `turn_on`/`turn_off` 服务和 `brightness`/`color_mode` 属性。这种抽象层使得自动化规则可以跨品牌编写，用户无需关心底层通信协议。

平台类型覆盖了智能家居的主要设备类别：灯光（light）、传感器（sensor）、开关（switch）、温控器（climate）、窗帘（cover）、摄像头（camera）、媒体播放器（media_player）、锁（lock）、风扇（fan）等 20+ 种。

### 2. 自动化引擎

自动化是 Home Assistant 的灵魂。每个自动化由三要素组成：

- **触发器（Trigger）**：什么条件下启动——状态变化、时间到达、设备发现、地理围栏等
- **条件（Condition）**：启动前检查——时间窗口、设备状态、模板判断等
- **动作（Action）**：执行什么操作——调用服务、等待、条件分支、循环、触发事件

自动化通过 YAML 配置或 Web UI 创建，支持 Blueprint 模板复用和复杂的脚本逻辑（顺序/并行/等待/重复）。

### 3. 事件驱动架构

系统内部的一切交互都通过**事件总线（EventBus）**完成。设备状态变化触发 `state_changed` 事件，服务调用触发 `call_service` 事件，组件加载触发 `component_loaded` 事件。集成可以监听任意事件并做出响应，实现了发布-订阅模式的完全解耦。

### 4. 配置管理

Home Assistant 提供两种配置方式：

- **YAML 配置文件**（`configuration.yaml`）：传统方式，适合高级用户和版本管理
- **ConfigFlow GUI 向导**：现代方式，用户通过 Web UI 分步配置集成，支持发现、OAuth 认证、重新配置

两种方式可以共存，ConfigFlow 完成的配置以 JSON 格式存储在 `.storage/` 目录中。

### 5. Web 界面与 API

Home Assistant 内置一个功能完整的 Web 前端（基于 Polymer/Lit 的 SPA），提供仪表盘、设备管理、自动化编辑器、历史记录等功能。同时提供 REST API 和 WebSocket API，支持移动端 App、第三方集成和外部脚本访问。

### 6. 扩展生态

- **Add-ons**（仅 Home Assistant OS）：容器化扩展，如 Node-RED、AdGuard
- **HACS**（社区商店）：第三方自定义集成和前端卡片
- **语音助手**：内置 Assist 管道，支持本地语音控制（STT/TTS/意图识别）
- **LLM 集成**：支持将 AI 大模型作为工具调用后端

## 架构一览

Home Assistant 的架构可以从两个维度理解：分层结构和运行时对象关系。

### 三层结构

```text
┌─────────────────────────────────────────┐
│           Platforms（平台层）             │  light/sensor/climate/switch...
│    标准化实体类型 + 服务定义 + 状态模型    │
├─────────────────────────────────────────┤
│         Integrations（集成层）            │  hue/tuya/mqtt/zwave_js...
│    设备通信 + 配置流 + 发现 + 实体创建     │
├─────────────────────────────────────────┤
│            Core（核心层）                 │  EventBus/StateMachine/Config...
│    运行时内核 + 事件/状态/服务/配置        │
└─────────────────────────────────────────┘
```

- **核心层（Core）**：位于 `homeassistant/core.py`，提供运行时基础设施。`HomeAssistant` 类是整个系统的根对象，持有 `EventBus`、`StateMachine`、`ServiceRegistry` 和 `Config` 四大子系统。
- **集成层（Integrations）**：位于 `homeassistant/components/`，每个集成是一个独立的 Python 包，负责与特定设备或服务通信。集成通过 `manifest.json` 自描述，由加载器动态发现和初始化。
- **平台层（Platforms）**：集成创建的实体属于某个平台（如 light、sensor），平台定义了实体的标准接口、属性和服务。一个集成可以同时转发到多个平台（如 Tuya 同时提供 light、switch、sensor 等实体）。

详细说明见[三层架构](/concepts/01-architecture.md)。

### 运行时对象关系

```text
HomeAssistant
├── EventBus          ← 事件发布/订阅
├── StateMachine      ← 实体状态存储与变更
├── ServiceRegistry   ← 服务注册与调用
├── Config            ← 核心配置（位置/时区/单位）
├── AuthManager       ← 用户认证与权限
├── ConfigEntries     ← 配置条目管理
├── Components        ← 已加载的集成
└── Data (hass.data)  ← 集成间共享数据
```

`HomeAssistant` 实例在整个进程中是单例的，所有组件通过依赖注入接收它（通常命名为 `hass`）。集成将运行时数据存入 `hass.data[DOMAIN]`，实现跨平台共享。

### 启动流程

系统启动分为明确的阶段：

1. **Runner 初始化**：设置事件循环策略、单实例锁、信号处理
2. **Bootstrap Stage 0**：加载核心基础设施（HTTP、API、认证等）
3. **Bootstrap Stage 1**：加载日志、发现、前端等基础集成
4. **Bootstrap Stage 2**：加载用户配置的所有集成和 ConfigEntry
5. **HA 启动完成**：触发 `homeassistant_started` 事件

详细说明见[启动流程](/concepts/04-bootstrap-lifecycle.md)。

## 技术栈概览

| 层面 | 技术 |
|------|------|
| 语言 | Python 3.14+ |
| 异步框架 | asyncio（单线程事件循环 + 线程池） |
| Web 服务器 | aiohttp |
| 配置验证 | voluptuous |
| 数据持久化 | JSON 文件（Store 延迟写入） |
| 模板引擎 | Jinja2 |
| 前端框架 | Lit（Web Components） |
| 数据库 | SQLite（默认）/ PostgreSQL / MariaDB（Recorder） |
| 测试框架 | pytest + pytest-asyncio + syrupy |
| 代码质量 | ruff + mypy + pylint + hassfest |

## 代码目录结构

```text
homeassistant/
├── core.py              # HomeAssistant 根对象与核心子系统
├── bootstrap.py         # 启动编排
├── runner.py            # 进程入口与事件循环
├── config.py            # 配置文件路径常量
├── core_config.py       # Config 核心配置对象
├── config_entries.py    # ConfigEntry 生命周期管理
├── setup.py             # 组件设置与依赖解析
├── loader.py            # 集成加载器
├── const.py             # 全局常量
├── exceptions.py        # 异常层次
├── auth/                # 认证子系统
├── helpers/             # 组件开发辅助库
├── util/                # 通用工具函数
├── components/          # 2000+ 设备/服务集成
└── generated/           # hassfest 自动生成文件
```

开发工具和测试位于仓库根目录：

```text
script/
├── hassfest/            # 集成验证与代码生成（29 个插件）
├── scaffold/            # 新集成脚手架
└── translations/        # 翻译管理
tests/
├── conftest.py          # pytest 全局 fixtures
├── common.py            # 测试工具与替身
└── components/          # 各集成测试
```

## 延伸阅读

- [三层架构：核心-集成-平台](/concepts/01-architecture.md)
- [安装与启动](/concepts/02-installation-runner.md)
- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [启动流程详解](/concepts/04-bootstrap-lifecycle.md)
- [配置系统](/concepts/05-configuration.md)
- [事件总线](/concepts/06-event-bus.md)

## 相关概念

- [三层架构：核心-集成-平台](/concepts/01-architecture.md) — 理解 HA 的分层设计与核心子系统组织方式
- [HomeAssistant 核心对象](/concepts/03-core-object.md) — 深入了解运行时根对象及其持有的四大子系统
- [实体模型](/concepts/09-entity-model.md) — 掌握设备能力的标准化抽象与 Entity 基类体系
- [集成架构](/concepts/14-component-architecture.md) — 学习如何开发连接外部设备与服务的集成
