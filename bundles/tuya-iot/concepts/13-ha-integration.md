---
type: Concept
title: Home Assistant 集成
description: 涂鸦 Home Assistant 集成生态，旧版 Tuya v2 与新版 Smart Life 集成对比，支持的设备品类与本地控制
tags: [tuya, home-assistant, smart-life, ha, integration, smart-home, mqtt, local-control]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuya-skills-source
    resource: "/references/tuya-skills-source.md"
    title: TuyaOpen 技能与生态源码
  - id: facts-tuya-skills-ecosystem
    resource: "/references/facts-tuya-skills-ecosystem.md"
    title: 技能与生态事实清单
---

# Home Assistant 集成

涂鸦设备接入 Home Assistant（HA）有两条技术路径：已停止维护的 **Tuya v2 集成**（`tuya-home-assistant` 仓库，仅保留文档）和新一代开源 **Smart Life 集成**（`tuya-smart-life` 仓库，Beta 阶段）。两者均基于涂鸦云 API 实现设备控制，但 Smart Life 集成降低了接入门槛，无需在涂鸦 IoT 平台创建云开发项目，也无需定期续期 IoT Core Service 资源。

## 两代集成对比

| 特性 | Tuya v2（旧版） | Smart Life（新版） |
|------|----------------|-------------------|
| 仓库状态 | 停止维护，仅保留文档 | 活跃开发，Beta 测试 |
| 接入门槛 | 需创建云开发项目、续期资源 | 使用 App 账号直接登录 |
| 开源状态 | 文档开源，核心集成在 HA Core | 完全开源，社区可贡献 |
| 设备兼容性 | 7 大类 50+ 小类 | 与 Tuya 集成相同范围 |
| 本地控制 | 不支持 | 暂不支持（规划中） |
| 与官方 Tuya 集成兼容 | 是 | 不兼容，需重新添加设备 |
| 数据迁移 | - | 不支持从旧版迁移 |

> **重要提示**：新旧两个集成互不兼容，无法迁移设备。用户需使用新插件重新添加设备并配置自动化场景。

## Smart Life 集成架构

`tuya-smart-life` 仓库的代码结构是标准的 Home Assistant 自定义组件（custom_component）：

```text
custom_components/smartlife/
├── __init__.py              # 组件初始化
├── manifest.json            # 组件清单（依赖、版本、域名）
├── config_flow.py           # 配置流程（UI 引导式登录）
├── const.py                 # 常量定义
├── base.py                  # 基类和共享逻辑
├── util.py                  # 工具函数
├── diagnostics.py           # 诊断信息
├── strings.json             # 英文字符串
├── translations/            # 多语言翻译
│   ├── en.json
│   ├── select.en.json
│   └── sensor.en.json
└── [平台文件].py            # 各 HA 平台实现
```

### 支持的 HA 平台

Smart Life 集成为每种设备类型实现了对应的 Home Assistant 平台：

| 文件 | HA 平台 | 设备类型示例 |
|------|---------|-------------|
| `light.py` | Light | 灯具、灯带 |
| `switch.py` | Switch | 智能插座、开关 |
| `climate.py` | Climate | 空调、温控器 |
| `cover.py` | Cover | 窗帘、卷帘 |
| `fan.py` | Fan | 风扇、换气扇 |
| `humidifier.py` | Humidifier | 加湿器、除湿机 |
| `sensor.py` | Sensor | 温湿度、功率、电量传感器 |
| `binary_sensor.py` | Binary Sensor | 门磁、人体感应、水浸 |
| `alarm_control_panel.py` | Alarm Control Panel | 报警器 |
| `camera.py` | Camera | IPC 摄像头 |
| `vacuum.py` | Vacuum | 扫地机器人 |
| `siren.py` | Siren | 警号 |
| `button.py` | Button | 可编程按钮 |
| `number.py` | Number | 数值调节实体 |
| `select.py` | Select | 下拉选择实体 |
| `scene.py` | Scene | 场景 |

共计 16 个 HA 平台，覆盖照明、安防、环境、清洁、能源等主要智能家居品类。

### 配置流程

`config_flow.py` 实现了 Home Assistant 的 UI 配置流程：
1. 用户在 HA 中添加 Smart Life 集成
2. 输入 Smart Life/Tuya App 账号凭据
3. 选择数据中心区域
4. 自动发现并添加账号下的所有设备
5. 设备实体自动出现在 HA 中

相比旧版需要手动创建云项目、获取 Access ID/Secret、关联设备等繁琐步骤，新版显著降低了非技术用户的接入门槛。

### 多语言支持

组件通过 `translations/` 目录提供多语言支持：
- `en.json`：核心实体翻译
- `select.en.json`：选择器实体翻译
- `sensor.en.json`：传感器实体翻译
- `strings.json`：配置和选项字符串

社区可贡献更多语言翻译。

## Tuya v2 文档资源

旧版 `tuya-home-assistant` 仓库虽已停止代码维护，但保留了有价值的文档：

| 文档 | 内容 |
|------|------|
| `docs/platform_configuration.md` | 涂鸦 IoT 平台配置指南 |
| `docs/install.md` | 集成安装步骤 |
| `docs/error_code.md` | 错误码与故障排查 |
| `docs/faq.md` | 常见问题 |
| `docs/regions_dataCenters.md` | 国家/区域与数据中心映射 |
| `docs/not_supported_devices.md` | 不支持的设备品类 |
| `docs/supported_devices.md` | 已支持设备列表（国际） |
| `docs/supported_devices_cn.md` | 已支持设备列表（中国） |
| `docs/develop_new_driver.md` | 新设备驱动开发指南 |
| `docs/get_log.md` | 日志获取方法 |
| `docs/raspberryPi_setup.md` | Raspberry Pi 环境搭建 |

这些文档中的错误码、数据中心映射、设备品类说明等内容对新版集成仍有参考价值。

## 数据中心映射

与 OpenClaw API 类似，HA 集成也需要选择正确的数据中心。涂鸦在全球部署了多个数据中心，用户必须选择与 App 账号注册区域一致的数据中心，否则无法登录或设备不显示。

中国区用户使用「智能生活」App，国际用户使用「Tuya Smart」或「Smart Life」App。不同 App 和区域对应不同的云服务端点。

## 设备前置条件

接入 HA 之前，设备必须满足：
1. 设备已通过 Tuya Smart / Smart Life / 智能生活 App 完成配网
2. 设备在 App 中可正常控制
3. 设备在线且固件版本支持云端 API 访问
4. 使用与 App 相同的账号登录 HA 集成

## 本地控制现状

两代集成都**不支持本地控制**——所有设备指令通过涂鸦云 API 中转，意味着：
- 设备和 HA 必须能访问互联网
- 云端故障或网络中断时无法控制设备
- 存在一定的指令延迟（通常 100ms-1s）
- 设备状态通过云端轮询或推送更新

本地控制是社区高度期待的功能，可能在未来版本中通过涂鸦局域网协议实现。

## 与 TuyaOpen 固件的关系

Home Assistant 集成运行在家庭自动化服务器（如 Home Assistant OS、Hass.io）上，而 TuyaOpen 运行在设备端（MCU/Linux）。两者的关系：

```text
[TuyaOpen 固件设备] ←→ [涂鸦云] ←→ [Smart Life HA 集成] ←→ [Home Assistant]
       ↑                    ↑
  设备端 SDK           云端 API 中转
```

- TuyaOpen 设备通过 MQTT 连接涂鸦云
- HA 集成通过 REST/WebSocket API 访问涂鸦云
- 云端桥接设备端和 HA 端的通信
- 开发者可以使用 TuyaOpen 构建设备，用户通过 HA 集成控制设备

对于需要本地控制的高级用户，TuyaOpen 设备也可以通过原生 MQTT/Modbus 等协议直接与 HA 通信，绕过涂鸦云，但这需要自定义固件和 HA 配置。

## 与 OpenClaw 的协同

OpenClaw 云 API 和 Smart Life HA 集成都基于涂鸦云端能力：
- OpenClaw 面向 AI Agent 和自动化脚本，提供编程接口
- Smart Life 面向 Home Assistant 用户，提供声明式实体和自动化
- 两者可组合使用：HA 负责设备管理和仪表盘，OpenClaw 技能负责 AI 自然语言控制
- 均使用相同的物模型（Thing Model）属性体系

## 相关概念

- [OpenClaw 云 API](/concepts/12-openclaw-api.md)
- [网络栈](/concepts/03-network-stack.md)（MQTT 协议）
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
- [TuyaOpen IoT 框架概览](/concepts/00-overview.md)
