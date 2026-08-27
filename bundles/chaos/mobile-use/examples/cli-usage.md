---
type: Example
title: CLI 命令使用示例
description: mobile-use CLI 命令的实际用法，涵盖基本任务、trace录制、结构化输出、视频工具、云设备和iOS配置
tags: [mobile-use, cli, typer, example, usage]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: mobile-use-source
    resource: "/references/mobile-use-source.md"
    title: mobile-use 源码
  - id: facts
    resource: "/references/facts.md"
    title: mobile-use 事实清单
---

# CLI 命令使用示例

mobile-use 通过 Typer 框架提供命令行接口，入口点为 `mobile-use`。CLI 仅注册一个 `main` 命令，`goal` 为必填位置参数，其余均为可选选项。

## 命令语法

```bash
mobile-use [OPTIONS] GOAL
```

`GOAL` 是自然语言描述的任务目标，Agent 将自主拆解并执行。

## 选项总览

| 选项 | 简写 | 参数类型 | 默认值 | 说明 |
|------|------|---------|--------|------|
| `--test-name` | `-n` | TEXT | — | 测试名称，提供时启用 trace 录制 |
| `--traces-path` | `-p` | TEXT | `traces` | Trace 文件保存路径 |
| `--output-description` | `-o` | TEXT | — | 输出描述（JSON schema 形式） |
| `--wda-url` | | TEXT | — | 覆盖 WebDriverAgent URL |
| `--wda-timeout` | | FLOAT | — | WDA 操作超时（秒） |
| `--wda-auto-start-iproxy` / `--no-wda-auto-start-iproxy` | | BOOLEAN | — | 是否自动启动 iproxy |
| `--wda-auto-start-wda` / `--no-wda-auto-start-wda` | | BOOLEAN | — | 是否自动构建运行 WDA |
| `--wda-project-path` | | TEXT | — | WebDriverAgent.xcodeproj 路径 |
| `--wda-startup-timeout` | | FLOAT | — | WDA 启动超时（秒） |
| `--idb-host` | | TEXT | — | IDB companion 主机（模拟器用） |
| `--idb-port` | | INTEGER | — | IDB companion 端口 |
| `--with-video-recording-tools` | | BOOLEAN | `False` | 启用视频录制工具 |
| `--device-type` | `-d` | CHOICE | `local` | 设备类型：`local` 或 `limrun` |
| `--limrun-platform` | | CHOICE | — | Limrun 平台：`android` 或 `ios` |
| `--help` | | | | 显示帮助信息 |

## 基本用法

### 简单任务

```bash
mobile-use "打开设置应用"
```

Agent 将自动连接本地 Android 或 iOS 设备，导航到设置应用。默认使用 `llm-config.defaults.jsonc` 中的 OpenAI 配置，需要设置 `OPENAI_API_KEY` 环境变量。

### Android 设备操作

```bash
mobile-use "打开 Chrome 浏览器，搜索 'mobile-use AI agent'，截取搜索结果页面截图"
```

Agent 会自主完成：启动 Chrome → 点击搜索栏 → 输入文本 → 提交搜索 → 等待加载 → 截图。

### iOS 设备操作

对于连接的 iOS 物理设备，CLI 会自动尝试通过 WDA 连接。若 WDA 未运行，需配置自动启动：

```bash
mobile-use \
  --wda-auto-start-iproxy \
  --wda-auto-start-wda \
  --wda-project-path /path/to/WebDriverAgent.xcodeproj \
  "打开邮件应用并刷新收件箱"
```

## Trace 录制

### 启用 trace 录制

使用 `--test-name`（或 `-n`）指定测试名称时，自动启用 trace 录制：

```bash
mobile-use -n "wifi-test" -p ./traces "打开设置并连接 Wi-Fi"
```

Trace 文件将保存到 `./traces/wifi-test/` 目录，包含每步截图、Agent 思考过程和工具调用记录。

### 指定 trace 路径

```bash
mobile-use -n "login-test" -p ./test-results/traces "在应用中使用测试账号登录"
```

`--traces-path`（或 `-p`）指定 trace 根目录，默认为 `traces`。

## 结构化输出

### 使用 output-description

`--output-description`（或 `-o`）用于指定期望的输出格式，以 JSON schema 描述：

```bash
mobile-use -o '{"type": "object", "properties": {"battery_level": {"type": "string"}, "wifi_status": {"type": "string"}}, "required": ["battery_level", "wifi_status"]}' "查看电池电量和 Wi-Fi 连接状态"
```

Agent 在完成设备操作后，会通过 outputter 生成符合描述的 JSON 输出。

### 数据抓取示例

```bash
mobile-use -o '{"type": "object", "properties": {"app_name": {"type": "string"}, "version": {"type": "string"}}, "required": ["app_name", "version"]}' "打开设置中的应用管理页面，获取 Chrome 浏览器的版本号"
```

## 视频录制工具

启用 `--with-video-recording-tools` 后，Agent 可以使用 `start_video_recording` 和 `stop_video_recording` 工具录制屏幕操作视频，结合 Gemini 视觉模型分析动态内容：

```bash
mobile-use --with-video-recording-tools "录制屏幕操作视频，打开计算器应用，计算 23 乘以 47，然后停止录制并分析结果"
```

注意：视频录制功能需要系统安装 ffmpeg，CLI 会在启用时自动检查 [F-268]。视频分析使用 Gemini 模型，需确保 `GOOGLE_API_KEY` 已配置且 `video_analyzer` 节点已在 LLM 配置中启用。

## 云设备（Limrun）

### 使用 Limrun Android 云设备

```bash
mobile-use -d limrun --limrun-platform android "打开 Gmail 应用并发送一封测试邮件"
```

`--device-type`（或 `-d`）设为 `limrun` 时，必须同时指定 `--limrun-platform`。CLI 会自动创建 Limrun 云设备实例，任务完成后自动销毁 [F-075~F-093]。

### 使用 Limrun iOS 云设备

```bash
mobile-use -d limrun --limrun-platform ios "打开 Safari 并访问 https://minitap.ai"
```

使用云设备时，无需本地连接物理设备或配置 WDA/IDB，但需要 Limrun API 凭据。

## iOS 模拟器（IDB）

对于 iOS 模拟器，通过 IDB companion 连接：

```bash
mobile-use \
  --idb-host localhost \
  --idb-port 10882 \
  "在模拟器上打开地图应用"
```

确保 idb-companion 已在指定主机和端口运行。iOS 模拟器不需要 WDA 配置。

## iOS 物理设备（WDA）

对于 iOS 物理设备，需配置 WebDriverAgent：

```bash
mobile-use \
  --wda-url http://localhost:8100 \
  --wda-timeout 30 \
  "打开照片应用并查看第一张照片"
```

若 WDA 已通过 Xcode 手动启动，直接用 `--wda-url` 指定地址即可。

## 环境变量配置

CLI 启动时自动加载 `.env` 文件。常用环境变量：

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Google Gemini
export GOOGLE_API_KEY="AI..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Minitap 平台
export MINITAP_API_KEY="mntp_..."
export MINITAP_BASE_URL="https://platform.minitap.ai"

# ADB 服务器（非默认地址时）
export ADB_HOST="localhost"
export ADB_PORT="5037"

# 遥测
export MOBILE_USE_TELEMETRY_ENABLED="false"
```

首次运行 CLI 时，会交互式询问是否启用匿名遥测。设置 `MOBILE_USE_TELEMETRY_ENABLED=false` 可跳过此询问。

## 自定义 LLM 配置

在项目根目录创建 `llm-config.override.jsonc` 可覆盖默认 LLM 配置。例如，将所有节点切换到 Anthropic：

```jsonc
{
  "planner": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "fallback": { "provider": "openai", "model": "gpt-5-mini" }
  }
  // 其余节点继承默认配置
}
```

override 文件只需包含需要修改的字段，系统通过深度合并与默认配置组合。未修改的节点继续使用默认值。

## 取消任务

任务运行中按 `Ctrl+C` 可取消。CLI 会捕获 KeyboardInterrupt，结束遥测会话并以退出码 130 退出。Agent 会执行资源清理（包括云设备销毁）。

## 相关概念

- [mobile-use 项目概览](/concepts/00-overview.md)
- [SDK 双层 API 与生命周期](/concepts/05-sdk-layer.md)
- [LLM 配置与可插拔体系](/concepts/04-llm-configuration.md)
- [多 Agent 协作架构](/concepts/01-multi-agent-architecture.md)
