---
title: Hermes Agent 完整安装方案
project: hermes-agent
version: 1.0.0
created: 2026-08-10
source:
  - external/libs/hermes-agent/README.md
  - external/libs/hermes-agent/README.zh-CN.md
  - external/libs/hermes-agent/pyproject.toml
  - external/libs/hermes-agent/package.json
  - external/libs/hermes-agent/Dockerfile
  - external/libs/hermes-agent/docker-compose.yml
  - external/libs/hermes-agent/.env.example
  - external/libs/hermes-agent/AGENTS.md
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/scripts/install.ps1
---

# Hermes Agent 完整安装方案

> **Nous Research Hermes Agent** — 具备内置学习循环的自改进 AI 智能体。支持多模型、多平台，提供终端交互界面、多平台消息网关、定时自动化、委派并行化等能力。

## 文档结构

本方案由 11 个章节组成，覆盖从环境准备到日常维护的完整生命周期：

| 章节 | 文件 | 内容摘要 |
|---|---|---|
| 第1章 | [01-environment.md](01-environment.md) | 环境要求与前置准备：支持的操作系统、硬件需求、系统依赖、Python/Node.js/uv 版本要求 |
| 第2章 | [02-install-script.md](02-install-script.md) | 官方脚本安装指南（Linux/macOS/WSL2）：一键命令、脚本参数、安装流程、目录结构、验证步骤 |
| 第3章 | [03-install-windows.md](03-install-windows.md) | Windows PowerShell 安装指南：执行策略、8.3短路径、长路径、CRLF、pywin32、WSL2建议 |
| 第4章 | [04-install-manual.md](04-install-manual.md) | 手动源码安装指南：克隆仓库、uv/venv虚拟环境、Python extras、Node.js前端构建、开发者模式 |
| 第5章 | [05-install-docker.md](05-install-docker.md) | Docker容器化部署：镜像构建、docker-compose、卷挂载、s6-overlay进程管理、网络模式 |
| 第6章 | [06-configuration.md](06-configuration.md) | 配置说明：.env密钥、config.yaml行为配置、LLM提供商、工具API Key、setup向导、终端后端 |
| 第7章 | [07-verification.md](07-verification.md) | 安装验证：版本检查、doctor诊断、对话测试、工具验证、TUI验证、日志查看 |
| 第8章 | [08-troubleshooting.md](08-troubleshooting.md) | 常见问题与故障排除：网络、Python/Node版本、编译失败、权限、Windows/Docker特有问题 |
| 第9章 | [09-upgrade-uninstall.md](09-upgrade-uninstall.md) | 升级与卸载：hermes update、手动升级、Docker升级、备份、回滚、卸载、数据目录说明 |
| 第10章 | [10-termux.md](10-termux.md) | Termux(Android)特殊说明：Bionic限制、依赖安装、[termux] extras、不支持功能、后台运行 |
| 第11章 | [11-network-china.md](11-network-china.md) | 国内网络优化：PyPI/npm/Docker/HuggingFace镜像、GitHub加速、国内模型API替代方案 |

## 快速开始

### Linux / macOS / WSL2（推荐）

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Windows（PowerShell）

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

### Docker

```bash
docker compose up -d
```

### 安装后

```bash
hermes setup     # 交互式配置
hermes doctor    # 诊断检查
hermes           # 启动对话
```

## 核心特性

- **内置学习循环**：自动从交互中学习，持续改进
- **多模型支持**：OpenRouter、Fireworks、OpenAI、Google Gemini、Anthropic、Kimi、DeepSeek 等
- **多平台消息网关**：Discord、Telegram、Signal、WhatsApp、Matrix、Slack 等
- **终端 TUI 界面**：丰富的交互式终端，支持快捷键、斜杠命令、多行编辑
- **工具生态**：终端执行、文件操作、浏览器自动化、网页搜索、代码执行等
- **定时自动化**：cron 任务调度，无人值守运行
- **委派并行化**：子智能体并行处理任务
- **跨平台**：Linux、macOS、Windows（WSL2）、Termux（Android）、Docker

## 技术栈

| 层级 | 技术 |
|---|---|
| 核心语言 | Python >=3.11,<3.14 |
| 前端/TUI | Node.js >=22.22.0, TypeScript, Ink (React for CLI) |
| 包管理 | uv（Python，推荐）、npm（Node.js） |
| 容器化 | Docker + s6-overlay 进程管理 |
| 数据存储 | SQLite（state.db）、文件系统（~/.hermes/） |

## 系统要求速览

| 项目 | 最低要求 | 推荐配置 |
|---|---|---|
| 操作系统 | Ubuntu 20.04+ / macOS 12+ / Windows 10(WSL2) | Ubuntu 22.04+ / macOS 14+ |
| Python | 3.11 | 3.12 |
| Node.js | 22.22.0 | 22 LTS 最新版 |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 2 GB | 5 GB+（含模型缓存） |
| 网络 | 互联网连接（访问 LLM API） | 稳定宽带 |

## 有用链接

- **官方网站**：https://hermes-agent.nousresearch.com
- **GitHub 仓库**：https://github.com/NousResearch/hermes-agent
- **Nous Research**：https://nousresearch.com
- **文档站点**：https://hermes-agent.nousresearch.com/docs

## 许可证

Hermes Agent 由 Nous Research 开发。具体许可证请参阅项目仓库中的 LICENSE 文件。
