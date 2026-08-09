---
id: "hermes-agent-integration-03-configuration"
title: "03 配置文件设置"
source: "hermes-agent 插件文档 v2.5.0 + hermes-okf v0.5.9 Wiki（Quick-Start）"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/03-configuration.toml"
type: "Wiki Tutorial"
description: "Hermes 配置文件设置：config.yaml、HERMES_HOME、project 级插件、hermes-okf 自动配置"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "配置 Hermes 以启用 SpecWeave 插件与 hermes-okf 记忆层：config.yaml 的 plugins/memory/context 字段、HERMES_HOME、project 级插件"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 03 配置文件设置

> **⚠️ 版本提示**：以下配置基于 Hermes 插件文档 v2.5.0 与 hermes-okf v0.5.9，落地前验证。

## 3.1 主配置：`~/.hermes/config.yaml`

Hermes 的主配置文件位于 `~/.hermes/config.yaml`（默认）。与集成相关的核心字段：

```yaml
# 插件管理
plugins:
  enabled:              # 允许列表，只有这里列出的插件才会加载
    - specweave          # 自定义 SpecWeave 通用插件
    - hermes-okf         # Hermes OKF 记忆插件（安装插件后自动添加）
  disabled:             # 拒绝列表，强制禁用
    - some-noisy-plugin

# 记忆层（Memory Provider）
memory:
  provider: hermes_okf   # 选用哪个记忆提供者（hermes-okf 安装后自动设置）

# 上下文引擎（Context Engine，可选，单实例）
# context_engine: my_context_engine
```

> **关键点**：插件默认禁用，必须把插件名加入 `plugins.enabled` 才会被加载。`memory.provider` 指定记忆提供者。

## 3.2 HERMES_HOME 环境变量

插件根目录默认 `~/.hermes`，可通过 `HERMES_HOME` 环境变量重定向：

```bash
# Linux/macOS
export HERMES_HOME=/path/to/hermes-home

# Windows PowerShell
$env:HERMES_HOME = "D:\hermes-home"
```

设置后，插件目录变为 `$HERMES_HOME/plugins`，配置为 `$HERMES_HOME/config.yaml`。

## 3.3 项目级插件 `./.hermes/plugins`

除用户级插件外，Hermes 支持**项目级插件**（项目目录 `./.hermes/plugins`），需手动开启权限：

1. 在项目根目录创建 `./.hermes/plugins/`
2. 将 SpecWeave 插件放入该目录
3. 在 Hermes 配置中开启 project 插件权限（按 Hermes 官方指引，需验证）

**适用**：把 SpecWeave 插件与工作区一起版本化，团队共享。

## 3.4 hermes-okf 自动配置

`hermes-okf install-plugin` 会自动完成以下配置（无需手动编辑 YAML）：

```bash
pip install hermes-okf
hermes-okf install-plugin
```

该命令自动：
1. 创建 `~/.hermes/plugins/hermes-okf/`，让 Hermes 发现插件
2. 更新 `~/.hermes/config.yaml`：把 `hermes-okf` 加入 `plugins.enabled`，并设置 `memory.provider`

验证配置：

```bash
hermes-okf validate-config
```

若全部通过，输出类似（示例）：

```
✅ hermes-okf v0.5.9 — all critical checks passed
Hermes should discover hermes-okf on next startup.
Run 'hermes' to start.
```

## 3.5 端到端配置流程（示例）

```bash
# 1. 安装 hermes-okf 记忆层（可选路径二）
pip install hermes-okf
hermes-okf install-plugin
hermes-okf validate-config

# 2. 安装/放置 SpecWeave 插件（路径一）
#    方式 A：从 Git 安装
#    hermes plugins install <owner>/<repo> --enable
#    方式 B：手动放入 ~/.hermes/plugins/specweave/

# 3. 确认 config.yaml 中 plugins.enabled 已包含 specweave 与 hermes-okf

# 4. 重启 Hermes 使配置生效
#    hermes gateway restart   # 如有 gateway
hermes
```

## 3.6 验证配置生效

```bash
# 查看插件列表与启用状态
hermes plugins list

# 在 Hermes 内检查记忆
hermes okf show config/agent
```

## 3.7 相关章节

- 接口规范：[Hermes Agent 插件接口规范](01-hermes-plugin-interface.md)
- 调用示例：[调用方式示例](06-usage-examples.md)
- 故障排查：[常见问题及解决方案](07-troubleshooting.md)
