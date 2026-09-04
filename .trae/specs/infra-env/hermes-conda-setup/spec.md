# Hermes Conda 环境创建与源码安装 - Product Requirement Document

## Overview
- **Summary**: 基于本地 hermes-agent 源码（`.chaos/hermes-agent`），通过 conda 创建隔离的 Python 虚拟环境（Python 3.13），在该环境中以 editable 模式安装 hermes-agent 及必要的 extras 依赖，使 `hermes` CLI 命令可正常使用。
- **Purpose**: 用户需要在独立 conda 环境中从源码安装 hermes-agent，避免与系统 Python（3.14，不兼容 hermes）冲突，确保开发和运行环境的可复现性。
- **Target Users**: 需要从源码开发/运行 hermes-agent 的开发者。

## Goals
- 创建 Python 3.13 的 conda 虚拟环境
- 在该环境中从源码（`.chaos/hermes-agent`）editable 安装 hermes-agent
- 安装必要的 extras（web、mcp 等核心功能依赖）
- 验证 `hermes` CLI 命令可正常执行（至少 `hermes --version` 可用）

## Non-Goals (Out of Scope)
- 不配置 LLM 提供商的 API Key（用户自行通过 `hermes setup` 或 `hermes model` 配置）
- 不安装可选的 heavy extras（如 voice/wake/matrix 等需要特殊系统依赖的扩展）
- 不安装 Docker/Nix 等容器化方案
- 不配置消息平台网关（Telegram/Discord/Slack 等）

## Background & Context
- hermes-agent 源码位于 `c:\Users\admin\Desktop\Dao\flows\SpecWeave\.chaos\hermes-agent`，版本 v0.20.0
- 系统 Python 为 3.14.3，不符合 hermes 的 `requires-python = ">=3.11,<3.14"` 要求；hermes 的 type-check 目标版本为 Python 3.13（`[tool.ty.environment] python-version = "3.13"`）
- 系统已安装 Miniconda3 于 `C:\ProgramData\miniconda3`，但未加入 PATH
- 系统已安装 uv 0.9.13（位于 `C:\AiPyPro\resources\app.asar.unpacked\resources\bin\uv.exe`）
- hermes 推荐使用 uv 进行依赖管理，但用户明确要求使用 conda 创建环境
- Windows 平台，需要注意 Windows 特有依赖（pywinpty、pywin32、tzdata、concurrent-log-handler）
- hermes 的 [web] extra 包含 FastAPI dashboard 依赖，用户之前关注过 web UI 功能

## Functional Requirements
- **FR-1**: 使用 conda 创建名为 `hermes`（或用户指定名称）的虚拟环境，Python 版本为 3.13
- **FR-2**: 在 conda 环境中安装 pip（conda 环境默认包含，但需确保可用）
- **FR-3**: 以 editable 模式（`pip install -e .`）从 `.chaos/hermes-agent` 安装 hermes-agent
- **FR-4**: 安装核心 extras：`[web,mcp]`（包含 dashboard Web UI 和 MCP 支持）
- **FR-5**: 验证 `hermes` 命令可执行，`hermes --version` 返回正确版本号
- **FR-6**: 验证 Python 导入正常（`python -c "import hermes_cli"` 无报错）

## Non-Functional Requirements
- **NFR-1**: 安装过程中的错误信息应清晰可见，便于排查依赖问题
- **NFR-2**: conda 环境应与系统 Python 完全隔离
- **NFR-3**: editable 安装模式下修改源码应立即生效，无需重新安装

## Constraints
- **Technical**: Windows 平台（PowerShell）；Python 版本 3.13（满足 >=3.11,<3.14）；conda 在 `C:\ProgramData\miniconda3` 但不在 PATH 中
- **Business**: 安装应在合理时间内完成（<15 分钟，视网络状况）
- **Dependencies**: 需要网络访问 PyPI 以下载依赖包；uv 可用但安装以 pip 为主（conda 环境内）

## Assumptions
- Miniconda3 功能完整，`conda.exe` 可通过完整路径调用
- 网络可正常访问 PyPI 下载 Python 包
- 用户有 conda 环境的写入权限（`C:\ProgramData\miniconda3\envs\` 或用户目录下）
- `.chaos/hermes-agent` 源码完整，`pyproject.toml` 配置正确
- uv 可以在 conda 环境内使用以加速依赖解析（可选）

## Acceptance Criteria

### AC-1: Conda 环境创建成功
- **Given**: 系统已安装 Miniconda3 于 `C:\ProgramData\miniconda3`
- **When**: 执行 conda create 命令创建 hermes 环境
- **Then**: conda 环境 `hermes` 创建成功，Python 版本为 3.13，环境位于 conda envs 目录
- **Verification**: `programmatic`
- **Notes**: Python 3.13 是 hermes 项目的 type-check 目标版本（[tool.ty.environment] python-version = "3.13"），同时满足 requires-python >=3.11,<3.14

### AC-2: hermes-agent editable 安装成功
- **Given**: conda 环境已激活，位于 `.chaos/hermes-agent` 目录
- **When**: 执行 pip install -e 命令安装 hermes-agent
- **Then**: 安装完成无报错，`hermes` CLI 命令可用，`pip show hermes-agent` 显示 editable 安装路径指向源码目录
- **Verification**: `programmatic`

### AC-3: 核心 extras 安装成功
- **Given**: hermes-agent 基础安装成功
- **When**: 安装 [web,mcp] extras
- **Then**: fastapi、uvicorn、mcp 等依赖安装成功，import 无报错
- **Verification**: `programmatic`

### AC-4: hermes CLI 命令可用
- **Given**: 安装完成，conda 环境已激活
- **When**: 运行 `hermes --version`
- **Then**: 输出版本号 0.20.0（或对应源码版本），无 import 错误
- **Verification**: `programmatic`

### AC-5: hermes 基本命令可运行
- **Given**: 安装完成，conda 环境已激活
- **When**: 运行 `hermes --help`
- **Then**: 输出帮助信息，列出可用子命令
- **Verification**: `programmatic`

## Open Questions
- [ ] conda 环境名称是否使用默认 `hermes`？还是用户有其他偏好？
- [ ] 是否需要安装 [dev] extras（pytest、debugpy 等开发工具）？
