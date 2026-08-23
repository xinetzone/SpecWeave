---
type: Reference
title: TuyaOpen 技能与生态源码
description: TuyaOpen Dev Skills、OpenClaw 云 API、Home Assistant 集成等生态项目源码登记
tags: [tuya, tuyaopen, skills, openclaw, home-assistant, ecosystem, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-tuya-skills-ecosystem
    resource: "/references/facts-tuya-skills-ecosystem.md"
    title: TuyaOpen 技能与生态事实清单
---

# TuyaOpen 技能与生态源码

## 仓库总览

本信源覆盖 TuyaOpen 生态中的四个关键项目：

| 项目 | 本地路径 | 定位 |
|------|---------|------|
| TuyaOpen Dev Skills | `d:\AI\.chaos\libs\TuyaOpen-dev-skills\` | AI 编码助手结构化知识技能包 |
| tuya-openclaw-skills | `d:\AI\.chaos\libs\tuya-openclaw-skills\` | OpenClaw 平台官方 AI Agent 技能 |
| tuya-home-assistant | `d:\AI\.chaos\libs\tuya-home-assistant\` | Home Assistant 涂鸦集成 |
| tuya-smart-life | `d:\AI\.chaos\libs\tuya-smart-life\` | Smart Life 应用相关 |

---

## 一、TuyaOpen Dev Skills

### 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | TuyaOpen Dev Skills |
| 定位 | 面向 Claude Code、Cursor IDE 及其他 Agent 型 AI 助手的结构化知识文件集合 |
| 许可证 | Apache License 2.0 |
| 标准遵循 | Agent Skills（agentskills.io）开放标准 |
| 主 SDK 仓库 | https://github.com/tuya/TuyaOpen |
| 官方文档 | https://tuyaopen.ai/docs/quick-start |
| 本地路径 | `d:\AI\.chaos\libs\TuyaOpen-dev-skills\` |

### 技能目录结构

每个技能遵循标准三部分结构：
- `SKILL.md`：核心指令，自动加载
- `references/`：详细文档，按需加载
- `scripts/`：Agent 可直接执行的脚本

### 核心开发技能（8 个，位于 `skills/tuyaopen/`）

| 技能名 | 路径 | 职责 |
|--------|------|------|
| `tuyaopen/env-setup` | `skills/tuyaopen/env-setup/` | 环境搭建（Python/git/cmake/ninja、三平台激活脚本、环境检查） |
| `tuyaopen/build` | `skills/tuyaopen/build/` | 构建系统（配置选择、menuconfig、Kconfig 指南、构建/清理/批量构建） |
| `tuyaopen/project-config` | `skills/tuyaopen/project-config/` | 项目配置（new project/board/platform、CMakeLists 模板、tos.py 命令参考） |
| `tuyaopen/code-check` | `skills/tuyaopen/code-check/` | 代码检查（clang-format、中文字符、Doxygen 头、敏感信息占位符） |
| `tuyaopen/add-board` | `skills/tuyaopen/add-board/` | 新板卡移植（目录结构、Kconfig 注册、代码层级规则、ESP32 共享驱动） |
| `tuyaopen/dev-loop` | `skills/tuyaopen/dev-loop/` | 开发迭代循环（Build→Flash→Monitor→Analyze、日志格式、错误码、CLI） |
| `tuyaopen/device-auth` | `skills/tuyaopen/device-auth/` | 设备授权与配网（三凭据、凭据优先级、BLE/AP 配网、CLI 授权） |
| `tuyaopen/debug-helper` | `skills/tuyaopen/debug-helper/` | 调试辅助（非阻塞日志捕获、会话管理、跨平台进程检测） |

### 独立调试技能（2 个，位于 `skills/` 根目录）

| 技能名 | 路径 | 职责 |
|--------|------|------|
| `tuyaopen-crash-decode` | `skills/tuyaopen-crash-decode/` | 崩溃转储解码（PC/LR → 源码行号，支持 ARM/Xtensa 工具链） |
| `tuyaopen-cli-debug` | `skills/tuyaopen-cli-debug/` | CLI 串口调试（自动发现端口、发送命令、JSON 输出） |

### 关键脚本文件

| 脚本 | 所属技能 | 功能 |
|------|---------|------|
| `scripts/check_env.sh` | env-setup | Linux/macOS 环境健康检查（set -euo pipefail） |
| `scripts/check_env.bat` | env-setup | Windows CMD 环境检查 |
| `scripts/check_env.ps1` | env-setup | Windows PowerShell 环境检查 |
| `scripts/check_files.py` | code-check | 跨平台文件格式检查包装器（定位仓库根、路径逃逸防护） |
| `scripts/monitor_helper.py` | debug-helper | 非阻塞串口日志捕获（start/tail/stop/status，跨平台） |
| `scripts/build_run.py` | dev-loop | Linux 快捷构建运行（默认 30 秒超时，日志自动分析） |
| `cli_debug.py` | cli-debug | CLI 串口调试工具（pyserial，自动发现，JSON 输出） |

### 关键参考文档

| 文档 | 所属技能 | 内容 |
|------|---------|------|
| `references/KCONFIG_GUIDE.md` | build | Kconfig 依赖机制（select/depends on/if）、构建系统架构 |
| `references/TOS_COMMANDS.md` | project-config | tos.py 完整命令参考（version/check/new/config/build/flash/monitor/update/dev/idf） |
| `references/BOARD_LAYERS.md` | add-board | 代码层级规则、ESP32 共享驱动清单、板卡 CMake 模板 |
| `references/ERROR_CODES.md` | dev-loop | OPERATE_RET 错误码定义、CLI 内置命令、批量构建参数 |
| `references/PROVISIONING.md` | device-auth | 授权流程、配网模式（BLE/AP）、串口授权注意事项 |

### 环境变量

激活后设置：
- `$OPEN_SDK_ROOT`：SDK 根路径
- `$OPEN_SDK_PYTHON`：venv Python 可执行文件
- `$OPEN_SDK_PIP`：venv pip
- `$VIRTUAL_ENV`：活动 venv 路径
- SDK 根目录加入 `PATH`

---

## 二、tuya-openclaw-skills（OpenClaw 云 API）

### 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | tuya-openclaw-skills |
| 技能名 | `tuya-smart-control` |
| 版本 | 1.0.0 |
| 定位 | OpenClaw 平台官方 AI Agent 技能，基于涂鸦 2C 终端用户 API |
| 覆盖范围 | 3000+ 智能硬件品类、200+ 国家和地区 |
| 许可证 | Apache License 2.0 |
| 依赖 | `requests>=2.28.0`、`websockets>=12.0`、Python 3.7+ |
| 环境变量 | `TUYA_API_KEY`（必需）、`TUYA_BASE_URL`（可选覆盖） |
| 本地路径 | `d:\AI\.chaos\libs\tuya-openclaw-skills\` |

### 认证与数据中心

- 认证方式：HTTP Header `Authorization: Bearer {Api-key}`
- API key 格式：`sk-<PREFIX><rest>`，前两个字符映射数据中心

| 前缀 | 数据中心 | REST Base URL | WebSocket URL |
|------|---------|---------------|---------------|
| AY | 中国 | `https://openapi.tuyacn.com` | `wss://wsmsgs.tuyacn.com` |
| AZ | 美西 | `https://openapi.tuyaus.com` | `wss://wsmsgs.iot-wus.com` |
| EU | 中欧 | `https://openapi.tuyaeu.com` | `wss://wsmsgs.iot-eu.com` |
| IN | 印度 | `https://openapi.tuyain.com` | `wss://wsmsgs.iot-ap.com` |
| UE | 美东 | `https://openapi-ueaz.tuyaus.com` | `wss://wsmsgs.iot-eus.com` |
| WE | 西欧 | `https://openapi-weaz.tuyaeu.com` | `wss://wsmsgs.iot-weu.com` |
| SG | 新加坡 | `https://openapi-sg.iotbing.com` | `wss://wsmsgs.iot-sea.com` |

### 功能模块与 API 端点

| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 家庭管理 | `/v1.0/end-user/homes/all` | GET | 列出所有家庭 |
| 家庭管理 | `/v1.0/end-user/homes/{home_id}/rooms` | GET | 列出家庭内房间 |
| 设备查询 | `/v1.0/end-user/devices/all` | GET | 列出所有设备（无分页） |
| 设备查询 | `/v1.0/end-user/homes/{home_id}/devices` | GET | 家庭内设备 |
| 设备查询 | `/v1.0/end-user/homes/room/{room_id}/devices` | GET | 房间内设备 |
| 设备查询 | `/v1.0/end-user/devices/{device_id}/detail` | GET | 单设备详情（含 properties） |
| 设备控制 | `/v1.0/end-user/devices/{device_id}/model` | GET | 查询物模型 |
| 设备控制 | `/v1.0/end-user/devices/{device_id}/shadow/properties/issue` | POST | 下发属性（双重序列化 JSON） |
| 设备管理 | `/v1.0/end-user/devices/{device_id}/attribute` | POST | 重命名设备 |
| 天气 | `/v1.0/end-user/services/weather/recent` | GET | 天气查询（codes/lat/lon） |
| 通知 | `/v1.0/end-user/services/sms/self-send` | POST | 短信通知（自发自收） |
| 通知 | `/v1.0/end-user/services/voice/self-send` | POST | 语音通知 |
| 通知 | `/v1.0/end-user/services/mail/self-send` | POST | 邮件通知 |
| 通知 | `/v1.0/end-user/services/push/self-send` | POST | App 推送 |
| 统计 | `/v1.0/end-user/statistics/hour/config` | GET | 小时统计配置 |
| 统计 | `/v1.0/end-user/statistics/hour/data` | GET | 小时统计数据（24h 范围限制） |
| IPC 抓拍 | `/v1.0/end-user/ipc/{device_id}/capture/allocate` | POST | 分配抓拍/录像 |
| IPC 抓拍 | `/v1.0/end-user/ipc/{device_id}/capture/resolve` | POST | 轮询获取 URL |
| 消息订阅 | WebSocket | WS | 设备属性变更/上下线事件 |

### API 响应规范

- 成功：`{"success": true, "t": <timestamp>, "result": {...}}`
- 失败：`{"success": false, "code": <code>, "msg": "..."}`
- HTTP 429 和瞬时 5xx 自动带退避重试
- 下发属性请求体中 `properties` 必须是 JSON 字符串（双重序列化）

### 源码文件结构

| 路径 | 职责 |
|------|------|
| `tuya-smart-control/SKILL.md` | 技能核心指令 |
| `tuya-smart-control/scripts/tuya_api.py` | REST API 客户端实现 |
| `tuya-smart-control/scripts/tuya_device_mq_client.py` | WebSocket 消息客户端 |
| `tuya-smart-control/scripts/requirements.txt` | Python 依赖 |
| `tuya-smart-control/references/api-conventions.md` | API 约定（认证/重试/错误处理） |
| `tuya-smart-control/references/device-query.md` | 设备查询 API |
| `tuya-smart-control/references/device-control.md` | 设备控制 API（物模型/属性下发） |
| `tuya-smart-control/references/device-management.md` | 设备管理 API |
| `tuya-smart-control/references/device-message.md` | WebSocket 消息订阅 |
| `tuya-smart-control/references/home-and-space.md` | 家庭与空间管理 |
| `tuya-smart-control/references/weather.md` | 天气服务 |
| `tuya-smart-control/references/notifications.md` | 通知服务 |
| `tuya-smart-control/references/statistics.md` | 数据统计 |
| `tuya-smart-control/references/ipc-cloud-capture.md` | IPC 云抓拍 |
| `tuya-smart-control/references/error-handling.md` | 错误处理 |

---

## 三、tuya-home-assistant

### 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | tuya-home-assistant |
| 定位 | Tuya 设备的 Home Assistant 集成 |
| 许可证 | 见 LICENSE 文件 |
| 本地路径 | `d:\AI\.chaos\libs\tuya-home-assistant\` |

### 文档资源

| 路径 | 内容 |
|------|------|
| `README.md` / `README_zh.md` | 项目说明（中英文） |
| `docs/install.md` | 安装指南 |
| `docs/develop_new_driver.md` | 新驱动开发指南 |
| `docs/error_code.md` | 错误码参考 |
| `docs/faq.md` | 常见问题 |
| `docs/get_log.md` | 日志获取方法 |
| `docs/platform_configuration.md` | 平台配置 |
| `docs/regions_dataCenters.md` | 区域与数据中心 |
| `docs/supported_devices.md` / `supported_devices_cn.md` | 支持设备列表 |
| `docs/not_supported_devices.md` | 不支持设备列表 |
| `docs/raspberryPi_setup.md` | 树莓派设置指南 |
| `.github/workflows/hassfest.yml` | Home Assistant 合规性检查 |
| `.github/workflows/codeql-analysis.yml` | CodeQL 安全分析 |

### 数据中心区域

与 OpenClaw API 使用相同的区域划分，支持中国、美西、中欧、印度、美东、西欧、新加坡等数据中心。

---

## 四、tuya-smart-life

### 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | tuya-smart-life |
| 本地路径 | `d:\AI\.chaos\libs\tuya-smart-life\` |
| 许可证 | 见 LICENSE 文件 |

该仓库为 Smart Life 应用相关资源，与 OpenClaw 云 API 共同构成涂鸦 2C 生态的终端侧组件。
