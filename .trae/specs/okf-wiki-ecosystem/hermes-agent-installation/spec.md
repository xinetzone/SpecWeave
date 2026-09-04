# Hermes Agent 完整安装方案 - 产品需求文档

## Overview
- **Summary**: 为 Hermes Agent（Nous Research 开发的自进化 AI 代理）提供完整的多平台安装方案，涵盖环境配置、依赖管理、安装步骤、验证方法和常见问题解决方案。
- **Purpose**: 确保用户能够在 Linux、macOS、Windows/WSL2、Termux 等平台上顺利安装并运行 Hermes Agent，覆盖官方脚本安装、手动安装和 Docker 容器化部署三种方式。
- **Target Users**: 需要在本地或服务器上部署 Hermes Agent 的开发者、AI 工程师和技术爱好者。

## Goals
- 提供跨平台（Linux/macOS/Windows/WSL2/Termux）的安装指南
- 覆盖三种安装方式：官方脚本一键安装、手动源码安装、Docker 容器化部署
- 明确环境依赖和版本要求（Python 3.11-3.13、Node.js 22+、uv 等）
- 提供完整的验证方法（hermes doctor、基础功能测试）
- 整理常见问题及解决方案（网络问题、依赖冲突、权限问题等）
- 包含配置说明（.env 环境变量、config.yaml 配置文件）

## Non-Goals (Out of Scope)
- Hermes Agent 的二次开发或功能扩展
- 特定 LLM 提供商的 API Key 申请流程（仅说明配置位置）
- 生产环境的高可用部署架构
- Hermes Agent 的深度使用教程（仅覆盖安装和基础验证）

## Background & Context
- Hermes Agent 是由 Nous Research 开发的自进化 AI 代理（v0.20.0）
- 技术栈：Python 3.11-3.13 + Node.js 22+ + uv 包管理器
- 核心特性：TUI 终端界面、多平台消息网关、技能学习系统、定时任务、子代理委派
- 模块结构：agent/、tools/、hermes_cli/、gateway/、cron/、acp_adapter/、plugins/ 等
- 依赖管理策略：核心依赖精确版本锁定，可选依赖通过 extras 懒加载
- 配置系统：.env 文件存储密钥，config.yaml 存储行为配置

## Functional Requirements
- **FR-1**: 提供 Linux/macOS/WSL2 平台的官方脚本安装步骤
- **FR-2**: 提供 Windows PowerShell 平台的官方脚本安装步骤
- **FR-3**: 提供从源码手动安装的详细步骤（含 uv 环境配置）
- **FR-4**: 提供 Docker 镜像构建和 docker-compose 部署方案
- **FR-5**: 列出所有系统依赖（git、ripgrep、ffmpeg、gcc 等）及安装方法
- **FR-6**: 说明 Python 虚拟环境创建和依赖安装流程
- **FR-7**: 说明 Node.js 依赖安装和前端构建流程
- **FR-8**: 提供 .env 配置模板和关键环境变量说明
- **FR-9**: 提供安装后的验证步骤（版本检查、doctor 诊断、基础对话测试）
- **FR-10**: 整理常见问题及解决方案（网络、依赖、权限、路径等）
- **FR-11**: 提供卸载和升级方法
- **FR-12**: 说明 Termux（Android）特殊安装注意事项

## Non-Functional Requirements
- **NFR-1**: 安装步骤必须可复现，每一步都有明确的命令和预期输出
- **NFR-2**: 文档必须使用中文，技术术语保留英文原文
- **NFR-3**: 常见问题解决方案必须经过验证或有明确的参考来源
- **NFR-4**: 安装方案必须考虑网络受限环境（如国内网络）的替代方案
- **NFR-5**: 安全相关配置（API Key、权限）必须有明确的安全提示

## Constraints
- **Technical**:
  - Python 版本必须 >=3.11 且 <3.14（3.14 因 Rust 扩展无预编译 wheel 暂不支持）
  - Node.js 版本必须 >=22.22.0
  - Windows 原生支持有限，推荐使用 WSL2
  - Docker 镜像基于 Debian 13 (trixie)，使用 s6-overlay 进程管理
- **Business**: 使用 MIT 许可证，可自由使用和修改
- **Dependencies**:
  - uv（Python 包管理器，推荐）
  - git（版本控制）
  - ripgrep（代码搜索工具）
  - ffmpeg（音视频处理）
  - gcc/g++/make（编译原生扩展）

## Assumptions
- 用户具备基本的命令行操作能力
- 用户能够访问 GitHub 和 PyPI（或配置了相应的镜像源）
- 用户拥有至少一个 LLM 提供商的 API Key（如 OpenRouter、Fireworks 等）
- 对于 Docker 安装，用户已安装 Docker 和 docker-compose

## Acceptance Criteria

### AC-1: 官方脚本安装（Linux/macOS/WSL2）
- **Given**: 用户使用 Linux、macOS 或 WSL2 环境
- **When**: 执行官方安装脚本 `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
- **Then**: 安装完成，`hermes` 命令可用，`hermes doctor` 无严重错误
- **Verification**: `programmatic`
- **Notes**: 需验证脚本自动检测平台、安装依赖、克隆仓库、创建虚拟环境的完整流程

### AC-2: Windows PowerShell 安装
- **Given**: 用户使用 Windows PowerShell 环境
- **When**: 执行 `iex (irm https://hermes-agent.nousresearch.com/install.ps1)`
- **Then**: 安装完成，`hermes` 命令在新终端中可用
- **Verification**: `programmatic`
- **Notes**: 需验证 8.3 短路径处理、环境变量配置、pywin32 等 Windows 特有依赖

### AC-3: 手动源码安装
- **Given**: 用户已克隆仓库到本地
- **When**: 按照文档步骤创建虚拟环境并安装依赖
- **Then**: 可通过 `python run_agent.py` 或 `hermes` 命令启动
- **Verification**: `programmatic`
- **Notes**: 需包含 uv 和 venv 两种方式

### AC-4: Docker 部署
- **Given**: 用户已安装 Docker 和 docker-compose
- **When**: 执行 `docker compose up -d`
- **Then**: gateway 和 dashboard 服务正常运行
- **Verification**: `programmatic`
- **Notes**: 需验证卷挂载、权限配置、s6-overlay 服务管理

### AC-5: 环境配置验证
- **Given**: 安装完成后
- **When**: 用户配置 .env 文件并运行 `hermes setup`
- **Then**: 可选择 LLM 提供商、配置工具、完成初始化
- **Verification**: `human-judgment`

### AC-6: 基础功能验证
- **Given**: 安装和配置完成
- **When**: 运行 `hermes` 并发送一条测试消息
- **Then**: Agent 正常响应，工具调用功能可用
- **Verification**: `human-judgment`

### AC-7: 常见问题覆盖
- **Given**: 用户遇到安装问题
- **When**: 查阅文档的"常见问题"章节
- **Then**: 能找到对应问题的原因分析和解决方案
- **Verification**: `human-judgment`
- **Notes**: 至少覆盖网络问题、依赖冲突、权限问题、Python 版本问题、Node.js 版本问题

## Open Questions
- [ ] 是否需要包含国内镜像源的详细配置说明（PyPI、npm、GitHub）？
- [ ] 是否需要提供离线安装包的制作方法？
- [ ] Termux 安装是否需要单独的详细章节？
