---
title: "devcontainer-win11 - Windows 11 开发容器镜像 产品需求文档"
status: "draft"
---

# devcontainer-win11 - Windows 11 开发容器镜像 产品需求文档

## Overview
- **Summary**: 创建基于 Windows Server 2022 (对应 Windows 11 内核, LTSC2022) 的全功能开发容器镜像 `devcontainer-win11`，提供与 Linux 版 `devcontainer-base` 对等的核心开发体验（SSH + Jupyter + Python 3.14 free-threading/Miniforge + Docker CLI），作为独立 Docker 应用存在于 `apps/docker-images/devcontainer-win11/`
- **Purpose**: 为需要 Windows 原生环境（编译 Windows PE/.NET/PowerShell/Windows SDK）的开发者提供可复现的容器化开发环境，与 Linux 版 devcontainer-base 形成跨平台覆盖
- **Target Users**: Windows 平台开发者、需要构建/测试 Windows 原生应用的 CI/CD 流水线、需要容器化 PowerShell/Windows 管理工具的运维工程师

## Goals
- 提供 OpenSSH Server 远程访问能力（端口 22）
- 提供 JupyterLab 交互式开发环境（端口 8888）
- 安装 Miniforge3（conda-forge）+ Python 3.14 **free-threading (cp314t)** 版本（通过 conda-forge `python-freethreading` 元包安装，与 Linux 版一致）
- 设置 `Py_GIL_DISABLED=1` 环境变量，支持从源码编译 C 扩展时自动启用 free-threading 标记
- 安装 Docker CLI + Compose Plugin，通过 DooD 模式（挂载宿主命名管道）操控宿主 Docker 引擎
- 安装 PowerShell 7（跨平台 PowerShell）
- 配置中文环境（zh-CN 语言 + China Standard Time 时区）
- 创建非管理员用户 `ContainerUser`（或 devuser），避免默认 ContainerAdministrator
- 提供 PowerShell entrypoint 脚本管理多服务启动
- 保持与 Linux 版一致的开发者体验（相同的端口、环境变量命名、构建脚本模式）
- 提供完整的构建、启动、测试脚本

## Non-Goals
- ❌ Docker-in-Docker (DinD)：Windows 容器内嵌套运行 Docker 引擎极不稳定，v1.0 不实现
- ❌ Podman：Podman for Windows 成熟度不足，不包含
- ❌ 双 Python 环境（GIL + free-threading）：v1.0 直接默认 free-threading（与 Linux 版一致），不做双环境切换
- ❌ supervisord：Linux 专属进程管理器，使用 PowerShell 原生方案替代
- ❌ tini init：Windows 容器不需要 tini
- ❌ GPU 直通/CUDA：Windows 容器 GPU 支持复杂，v1.0 不包含
- ❌ 功能与 Linux 版 100% 对等：保持核心开发体验对等，但不强行移植所有 Linux 特性
- ❌ variants/ 子系统：v1.0 只提供基础镜像，变体系统后续迭代

## Background & Context
- 现有 `devcontainer-base` 是 Linux 容器（Ubuntu 26.04），功能完整但无法满足 Windows 原生开发需求
- Windows 容器与 Linux 容器是完全不同的技术栈：基础镜像（servercore vs ubuntu）、Shell（PowerShell vs bash）、包管理、服务模型、路径体系均不同
- 用户明确要求"从零开始设计，可参考现有 Dockerfile"，因此这是独立应用而非 variants/ 下的 Linux 变体追加层
- Windows Server 2022 (LTSC2022) 对应 Windows 11 22H2 内核，是 Windows 容器的推荐基础镜像
- Windows Server 2025 已默认内置 OpenSSH Server，但 Server 2022 需要通过 `Add-WindowsCapability` 安装
- Python 3.14 已将 free-threading（PEP 703/779）从实验性提升为 Phase II 正式支持，Windows CI 测试已全面覆盖；conda-forge 提供 `python-freethreading` 元包（Windows 版已存在，Python 3.14.6 最新）；Windows 上单线程性能损耗约 7-10%，内存开销约 15-20%
- conda-forge free-threading 扩展包生态在 Windows 上仍在建设中，部分包可能无 cp314t Windows wheels，需要通过 pip 从源码编译（需设置 `Py_GIL_DISABLED=1`），不兼容 free-threading 的包会自动回退到 GIL 模式
- 构建环境要求：Windows 宿主 + Docker Desktop 切换到 Windows 容器模式

## Functional Requirements

- **FR-1**: 基础镜像使用 `mcr.microsoft.com/windows/servercore:ltsc2022`
- **FR-2**: 安装并配置 OpenSSH Server，监听端口 22，支持密码认证和密钥认证
- **FR-3**: 安装 PowerShell 7（最新稳定版），作为默认 Shell
- **FR-4**: 安装 Miniforge3 (conda-forge) 到 `C:\conda`，通过 `python-freethreading` 元包安装 Python 3.14 free-threading (cp314t) 版本
- **FR-4a**: 设置系统环境变量 `Py_GIL_DISABLED=1`，确保 pip 从源码编译 C 扩展时自动定义 free-threading 标记
- **FR-4b**: 安装 C/C++ 编译工具链（MSVC Build Tools 或 conda m2w64-toolchain），支持 pip 从源码编译 C 扩展包
- **FR-5**: 安装 JupyterLab，通过 conda 环境启动，监听端口 8888
- **FR-6**: 安装 Docker CLI 和 Compose Plugin，配置连接宿主 Docker 引擎（`npipe:////./pipe/docker_engine`）
- **FR-7**: 安装常用开发工具（git、curl/wget 等价工具、vim/nano 等价工具）
- **FR-8**: 配置中文语言包（zh-CN）和时区（China Standard Time, UTC+8）
- **FR-9**: 创建非管理员用户 `devuser`，配置必要的文件权限
- **FR-10**: 提供 `entrypoint.ps1` PowerShell 启动脚本，管理 sshd 和 jupyter 服务的启动
- **FR-11**: 构建脚本 `build.ps1`（PowerShell）/`build.sh`（bash，在 WSL/Git Bash 中调用 docker build）
- **FR-12**: 启动脚本 `start.ps1`，提供端口映射、密码设置、卷挂载的一键启动
- **FR-13**: 健康检查脚本 `healthcheck.ps1`，检查 sshd 和 jupyter 服务状态
- **FR-14**: 构建元数据写入 `C:\ProgramData\devcontainer-build-info`（等价 Linux 版 `/etc/devcontainer-build-info`）
- **FR-15**: 构建阶段计时输出 `[TIMER]` 日志，与 Linux 版格式对齐
- **FR-16**: 最终验证检查点 `[VALIDATION CHECKPOINT]`，验证核心工具和服务配置正确
- **FR-17**: 提供 `AGENTS.md` 作为 AI 协作者入口，遵循 SpecWeave 工作区发现协议

## Non-Functional Requirements

- **NFR-1**: 镜像压缩后体积目标 ≤ 6GB（servercore 基础镜像约 2.8GB 压缩）
- **NFR-2**: Dockerfile 遵循分层缓存原则（变化频率分层、缓存挂载、同层修改）
- **NFR-3**: 构建脚本支持国内镜像源参数（`--cn` 或环境变量 `APT_MIRROR` 等价物）
- **NFR-4**: 所有 PowerShell 脚本设置严格模式（`Set-StrictMode -Version Latest`）和错误处理（`$ErrorActionPreference = 'Stop'`）
- **NFR-5**: Dockerfile 和脚本使用 UTF-8 编码，支持中文注释
- **NFR-6**: 健康检查间隔 30s，超时 10s，启动等待期 60s，与 Linux 版一致
- **NFR-7**: 代码遵循 SpecWeave 开发规范（Conventional Commits、原子化操作、单一职责）

## Constraints

- **Technical**:
  - Windows 容器只能在 Windows 宿主（Windows 10/11 Pro/Enterprise、Windows Server 2019+）上构建和运行
  - Docker Desktop 需要切换到 Windows 容器模式
  - Windows 容器 BuildKit 缓存挂载支持有限，可能需要手动管理缓存
  - Windows 容器默认以 ContainerUser 运行（非管理员），但构建时需要管理员权限
  - Miniforge3 Windows 版使用 `.exe` 安装程序，需要静默安装参数
  - free-threading Python (cp314t) 的 conda-forge Windows 扩展包生态仍在建设中，部分包可能无预编译 wheels；不兼容的包会在导入时自动重新启用 GIL（带警告），这是预期行为而非错误
  - Windows 容器从源码编译 C 扩展需要 `Py_GIL_DISABLED=1` 环境变量（系统级设置）
  - Windows 容器不支持 `--privileged` 标志的 Linux 等价物
  - Docker Desktop Windows 容器模式下不支持 Linux 容器的某些特性（如 network=host）
- **Business**:
  - v1.0 必须可独立构建和运行，不依赖 Linux 版镜像
  - 镜像必须推送到容器注册中心（GitHub Container Registry）
- **Dependencies**:
  - Docker Desktop 4.0+（Windows 容器模式）
  - PowerShell 7+（构建脚本）
  - 网络访问：mcr.microsoft.com（基础镜像）、github.com/conda-forge/miniforge（Miniforge）、pypi.org（pip 包）、aka.ms/vs/17（MSVC Build Tools，若使用）
  - 可选：国内镜像源（清华/中科大 conda 镜像、阿里云 PyPI 镜像）

## Assumptions
- 用户使用 Windows 11 + Docker Desktop 作为主要开发环境
- 构建机器可以访问 mcr.microsoft.com 和 GitHub
- 国内用户可通过 `--cn` 参数或手动配置镜像源加速下载
- Miniforge3 最新 Windows 版支持安装 `python-freethreading` 元包获取 Python 3.14 cp314t
- JupyterLab 在 free-threading Python 上可正常运行（ipykernel 等核心包支持 free-threading）
- OpenSSH Server 通过 `Add-WindowsCapability -Online` 在 servercore:ltsc2022 中可成功安装（若在线安装失败，可使用离线 FoD 包）
- conda-forge free-threading 核心包（python、pip、setuptools、jupyterlab、ipykernel）在 Windows 上有可用构建
- Windows 容器的 GitHub Actions CI/CD 使用 `windows-latest` runner

## Acceptance Criteria

### AC-1: 应用目录结构创建
- **Type**: `rule`
- **Given**: 存在 `apps/docker-images/` 目录
- **When**: 创建 devcontainer-win11 应用
- **Then**: 创建完整的应用目录结构，包含 Dockerfile、entrypoint.ps1、config/、scripts/、AGENTS.md
- **Pass Condition**: `apps/docker-images/devcontainer-win11/` 目录存在且包含所有必需文件
- **Evidence**: 文件系统列表

### AC-2: Dockerfile 可成功构建
- **Type**: `rule`
- **Given**: Windows 宿主 + Docker Desktop 在 Windows 容器模式
- **When**: 执行 `docker build -t devcontainer-win11:latest .`
- **Then**: 镜像构建成功，无错误
- **Pass Condition**: `docker images` 显示 `devcontainer-win11:latest` 镜像存在
- **Evidence**: docker build 输出日志

### AC-3: SSH 服务可用
- **Type**: `rule`
- **Given**: 容器已启动且映射了 22 端口
- **When**: 通过 SSH 客户端连接
- **Then**: SSH 连接成功，可进入 PowerShell 会话
- **Pass Condition**: `ssh -p <port> devuser@localhost` 成功登录
- **Evidence**: SSH 连接测试输出

### AC-4: JupyterLab 服务可用
- **Type**: `rule`
- **Given**: 容器已启动且映射了 8888 端口
- **When**: 访问 http://localhost:8888
- **Then**: JupyterLab 界面可访问，token 认证正常
- **Pass Condition**: HTTP 200 响应，JupyterLab UI 加载
- **Evidence**: curl/wget 测试 + 浏览器验证

### AC-5: Python/Miniforge free-threading 环境可用
- **Type**: `rule`
- **Given**: 容器正在运行
- **When**: 在容器中执行 `python --version`、`conda --version`、`python -c "import sysconfig; print(sysconfig.get_config_var('Py_GIL_DISABLED'))"`
- **Then**: Python 3.14.x free-threading (cp314t) 和 conda 命令可用，`Py_GIL_DISABLED == 1`
- **Pass Condition**: 版本号正确输出，`Py_GIL_DISABLED` 返回 `1`，`python -VV` 输出包含 "free-threading"
- **Evidence**: docker exec 命令输出

### AC-6: Docker CLI (DooD) 可用
- **Type**: `rule`
- **Given**: 容器启动时挂载了 `\\.\pipe\docker_engine`
- **When**: 在容器中执行 `docker --version` 和 `docker ps`
- **Then**: Docker CLI 可连接宿主引擎并列出容器
- **Pass Condition**: docker 命令成功执行，显示宿主容器列表
- **Evidence**: docker exec 命令输出

### AC-7: 中文环境和时区配置正确
- **Type**: `rule`
- **Given**: 容器正在运行
- **When**: 检查时区和 locale 设置
- **Then**: 时区为 China Standard Time (UTC+8)，支持中文显示
- **Pass Condition**: `Get-TimeZone` 显示 China Standard Time，chcp 显示 936/65001
- **Evidence**: PowerShell 命令输出

### AC-8: 非管理员用户权限正确
- **Type**: `rule`
- **Given**: 容器正在运行
- **When**: 以 devuser 身份执行操作
- **Then**: 用户不是管理员，但可以访问工作目录和已安装工具
- **Pass Condition**: `whoami` 显示 devuser，`net user devuser` 显示不在 Administrators 组
- **Evidence**: docker exec 命令输出

### AC-9: 健康检查正常工作
- **Type**: `rule`
- **Given**: 容器已启动且等待 60s 以上
- **When**: 执行 `docker inspect --format='{{.State.Health.Status}}' <container>`
- **Then**: 健康状态为 `healthy`
- **Pass Condition**: health status == healthy
- **Evidence**: docker inspect 输出

### AC-10: 构建日志包含 [TIMER] 和 [VALIDATION CHECKPOINT]
- **Type**: `rule`
- **Given**: 构建已完成
- **When**: 检查构建日志
- **Then**: 日志包含各阶段 [TIMER] 耗时输出和最终 [VALIDATION CHECKPOINT]
- **Pass Condition**: 构建日志中可检索到 `[TIMER]` 和 `[VALIDATION CHECKPOINT]` 标记
- **Evidence**: 构建日志

### AC-11: AGENTS.md 和规范文件完整
- **Type**: `rule`
- **Given**: 应用目录已创建
- **When**: 检查 AGENTS.md 和 .agents/ 规范
- **Then**: AGENTS.md 包含启动协议、上下文路由表、规范入口，遵循工作区发现协议
- **Pass Condition**: AGENTS.md 包含"启动协议"关键词，正确引用父级规范
- **Evidence**: 文件内容检查

### AC-12: Dockerfile 代码质量
- **Type**: `rubric`
- **Dimension**: Dockerfile 结构质量
- **Scale**: 1-5
- **Anchors**: 1 = 单块脚本无注释无分层；3 = 有基本分层但缺少缓存优化和清理；5 = 完美分层、缓存挂载、同层修改、注释完整、构建计时、清理到位
- **Pass Threshold**: >= 4
- **Evidence**: Dockerfile 评审

### AC-13: 开发者体验一致性
- **Type**: `rubric`
- **Dimension**: 与 Linux 版 devcontainer-base 的操作体验一致性
- **Scale**: 1-5
- **Anchors**: 1 = 完全不同的命令/端口/环境变量；3 = 核心功能对齐但细节差异大；5 = 命令模式、端口、环境变量命名、日志格式高度一致（含 free-threading 配置）
- **Pass Threshold**: >= 4
- **Evidence**: 构建/启动/测试脚本对比评审

### AC-14: Free-threading 运行时验证
- **Type**: `rule`
- **Given**: 容器正在运行
- **When**: 在容器中执行 `python -c "import sys; print(sys._is_gil_enabled())"` 并检查环境变量 `Py_GIL_DISABLED`
- **Then**: GIL 默认禁用（`sys._is_gil_enabled()` 返回 `False`），系统环境变量 `Py_GIL_DISABLED=1` 已设置
- **Pass Condition**: `sys._is_gil_enabled()` 返回 `False`，`$env:Py_GIL_DISABLED -eq '1'`（PowerShell）
- **Evidence**: docker exec 命令输出

### AC-15: pip 源码编译 free-threading 扩展能力
- **Type**: `rule`
- **Given**: 容器正在运行，且网络可访问 pypi.org
- **When**: 在容器中执行 `pip install --no-binary :all: <package-with-sdist>`（如一个纯 C 扩展小例子）
- **Then**: pip 可从源码编译安装支持 free-threading 的 C 扩展，无需手动设置 `Py_GIL_DISABLED`
- **Pass Condition**: 编译成功，导入包时不触发 "GIL re-enabled" 警告
- **Evidence**: pip install 输出
- **Notes**: 此 AC 验证编译环境配置正确；对于大型包（numpy/scipy 等），若 conda-forge 无 cp314t Windows 包，pip 源码编译可能耗时较长

## Open Questions
- [ ] Windows Server 2025 已默认内置 OpenSSH，是否需要同时支持 servercore:ltsc2025 基础镜像？（v1.0 先锁定 ltsc2022）
- [ ] 是否需要提供 Chocolatey/Scoop/winget 作为 Windows 包管理器？（v1.0 暂不包含 winget，因为 servercore 不包含 Microsoft Store 依赖）
- [ ] 是否需要安装 .NET SDK / Visual Studio Build Tools？（v1.0 不包含，后续可作为变体添加）
- [ ] 是否需要支持 Windows 容器的 GPU 加速（CUDA on Windows Containers）？（v1.0 不包含）
- [ ] 构建脚本是否需要同时提供 PowerShell (.ps1) 和 bash (.sh) 版本？（推荐两者都提供，bash 版本用于 WSL/Git Bash 环境下调用）
