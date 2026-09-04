---
version: 1.0
---

# Caffe Jupyter SSH Dockerfile - Product Requirement Document

## Overview
- **Summary**: 在 `projects/xuanspace/vendor/caffe/docker/origin/` 目录下创建新的 Dockerfile（命名为 `Dockerfile.jupyter-ssh`），基于现有 Caffe CPU-only Dockerfile，整合 jupyter-ssh-base 镜像的 SSH + Jupyter Notebook 双服务功能，形成一个同时支持 Caffe 深度学习框架、SSH 远程登录和 Jupyter Notebook 交互式开发的 Docker 镜像。
- **Purpose**: 为 Caffe 开发者提供一个开箱即用的容器化环境，既保留完整的 Caffe 编译运行环境，又支持通过 SSH 远程连接和 Jupyter Notebook 进行交互式开发调试。
- **Target Users**: Caffe 框架开发者、深度学习研究人员、需要远程交互式开发环境的工程师。

## Goals
- 基于现有 Caffe origin Dockerfile（Ubuntu 22.04 + 系统 Python 3.10）构建，保持 Caffe 编译环境完整性
- 整合 OpenSSH Server 支持 SSH 远程登录
- 整合 Jupyter Notebook/Lab 支持交互式开发
- 使用 supervisord 管理 sshd 和 jupyter 双服务
- 配置中文环境（zh_CN.UTF-8 编码，Asia/Shanghai 时区）
- 使用非 root 用户 `caffe-origin`（UID 1000）运行服务
- 保留原 Dockerfile 的多阶段构建结构，支持构建 builder 和 runtime 两种目标
- 保留原 Dockerfile 的 Aliyun 镜像源配置

## Non-Goals (Out of Scope)
- 不修改现有原始 Dockerfile 文件
- 不支持 GPU 版本（仅 CPU-only）
- 不升级到 Ubuntu 26.04（保持与原 Caffe Dockerfile 一致的 22.04）
- 不使用 Python venv 虚拟环境（沿用系统 Python 3.10）
- 不修改 caffex/ 源码
- 不修改 caffe 其他 docker 配置（local/、standalone/、modules/）

## Background & Context
- **现有 Caffe Dockerfile**: `docker/origin/Dockerfile` 采用 4 阶段多阶段构建（base-system → base-builder → builder → runtime），使用 Ubuntu 22.04 + 系统 Python 3.10，通过 Make 编译 Caffe，用户名为 builder
- **jupyter-ssh-base**: `apps/jupyter-ssh-base/Dockerfile` 是一个标准化的 SSH + Jupyter 基础镜像，使用 Ubuntu 26.04 + venv，用户名为 jupyteruser，通过 supervisord 管理双服务，包含 entrypoint.sh、healthcheck.sh、配置文件等完整组件
- **整合策略**: 以 Caffe 的 runtime 阶段为基础，叠加安装 SSH、supervisor、Jupyter 等组件，复用 jupyter-ssh-base 的配置文件和 entrypoint 逻辑（适配 Ubuntu 22.04 和系统 Python）
- **关键差异处理**: Ubuntu 版本差异（22.04 vs 26.04）导致 sources.list 格式不同；Python 管理方式差异（系统 Python vs venv）需要调整 Jupyter 安装和 PATH 配置；用户名从 builder 改为 caffe-origin

## Functional Requirements
- **FR-1**: 新文件名为 `Dockerfile.jupyter-ssh`，放置于 `projects/xuanspace/vendor/caffe/docker/origin/` 目录
- **FR-2**: 基于 Ubuntu 22.04，保持原 Caffe Dockerfile 的 Aliyun apt/pip 镜像源配置
- **FR-3**: 在 Caffe runtime 基础上安装并配置 OpenSSH Server，支持密码和公钥认证
- **FR-4**: 安装 Jupyter Notebook/Lab，使用系统 Python 3.10（不使用 venv）
- **FR-5**: 使用 supervisord 管理 sshd 和 jupyter 双服务，支持自动重启
- **FR-6**: 配置中文环境（zh_CN.UTF-8 locale，Asia/Shanghai 时区）
- **FR-7**: 创建非 root 用户 `caffe-origin`（UID 1000），拥有 sudo 权限（通过环境变量控制）
- **FR-8**: 容器启动时支持环境变量配置：USER_PASSWORD、ROOT_PASSWORD、JUPYTER_TOKEN、JUPYTER_PASSWORD、SSH_PUBLIC_KEY、GRANT_SUDO、ALLOW_ROOT_SSH 等
- **FR-9**: 支持命令模式（docker run ... bash）直接进入 shell，不启动服务
- **FR-10**: 包含健康检查脚本，同时检测 sshd 和 jupyter 服务状态
- **FR-11**: 使用 tini 作为 init 进程处理信号
- **FR-12**: 保留多阶段构建：base-system → base-builder → builder → runtime-jupyter
- **FR-13**: Caffe 功能完整可用：可正常 import caffe，运行验证脚本
- **FR-14**: Jupyter 可正常访问，Notebook 工作目录为 /workspace
- **FR-15**: SSH 可正常登录，端口映射正常工作

## Non-Functional Requirements
- **NFR-1**: 构建过程有清晰日志输出，关键步骤标记 `[BUILD]` 前缀
- **NFR-2**: Dockerfile 结构清晰，分段注释与原 Dockerfile 风格一致
- **NFR-3**: 镜像大小合理，每个 RUN 指令后清理 apt 缓存和临时文件
- **NFR-4**: pip 安装使用 --no-cache-dir 减少镜像体积
- **NFR-5**: entrypoint.sh 脚本有详细日志输出，包含 6 步初始化流程
- **NFR-6**: 配置文件（sshd_config、supervisord.conf、jupyter 配置）正确部署且权限正确
- **NFR-7**: 支持 docker build 目标选择（--target builder 用于 CI，--target runtime-jupyter 用于运行时）

## Constraints
- **Technical**:
  - 必须使用 Ubuntu 22.04 作为基础镜像（非 26.04）
  - 必须使用系统 Python 3.10（非 venv）
  - 用户名为 caffe-origin（非 builder 或 jupyteruser）
  - 保留原 Caffe Dockerfile 的多阶段构建结构
  - Caffe 源码通过 COPY 从构建上下文获取，保持原有编译方式（Make）
- **Business**:
  - 不得修改现有 Dockerfile
  - 不得修改 caffex/ 目录下的任何源码
  - 不得破坏原有构建流程（build.sh、run.sh 仍可用于原 Dockerfile）
- **Dependencies**:
  - 复用 jupyter-ssh-base 的配置文件和脚本逻辑（需适配 Ubuntu 22.04）
  - Caffe 编译依赖保持不变

## Assumptions
- jupyter-ssh-base 的配置文件（sshd_config、supervisord.conf 等）可以通过 COPY 命令从 `apps/jupyter-ssh-base/config/` 目录引入
- Ubuntu 22.04 的软件源格式为传统 sources.list（非 26.04 的 deb822 格式 .sources 文件）
- 系统 Python 3.10 可以正常安装 Jupyter 相关包
- 用户 caffe-origin 的 UID/GID 为 1000，与原 builder 用户一致，避免权限问题
- entrypoint.sh 和 healthcheck.sh 可复用 jupyter-ssh-base 的逻辑，仅调整路径和用户名为 caffe-origin

## Acceptance Criteria

### AC-1: Dockerfile 文件创建成功
- **Given**: 目标目录 `docker/origin/` 存在且有写入权限
- **When**: 构建任务完成
- **Then**: 文件 `Dockerfile.jupyter-ssh` 存在于该目录，语法正确可被 docker build 解析
- **Verification**: `programmatic`
- **Notes**: 使用 `docker build --target runtime-jupyter -f docker/origin/Dockerfile.jupyter-ssh . --dry-run` 或语法检查验证

### AC-2: 镜像可成功构建
- **Given**: Docker 环境正常，caffex/ 源码完整
- **When**: 执行 `docker build -t caffe-jupyter-ssh:test --target runtime-jupyter -f docker/origin/Dockerfile.jupyter-ssh .`
- **Then**: 构建成功完成，无错误退出
- **Verification**: `programmatic`

### AC-3: Caffe 功能完整可用
- **Given**: 镜像构建成功
- **When**: 运行容器并执行 `python -c "import caffe; print('Caffe imported successfully')"`
- **Then**: 无报错，成功输出导入成功信息
- **Verification**: `programmatic`

### AC-4: SSH 服务可正常工作
- **Given**: 容器以 `-p 2222:22 -e USER_PASSWORD=testpass` 参数启动
- **When**: 等待约 10 秒服务启动后，尝试 SSH 连接 `ssh -o StrictHostKeyChecking=no -p 2222 caffe-origin@localhost`
- **Then**: 密码认证成功，可正常登录进入 shell
- **Verification**: `programmatic`

### AC-5: Jupyter Notebook 可正常访问
- **Given**: 容器以 `-p 8888:8888 -e JUPYTER_TOKEN=testtoken` 参数启动
- **When**: 等待约 10 秒服务启动后，访问 `http://localhost:8888/?token=testtoken`
- **Then**: Jupyter 界面正常加载，可创建 Notebook
- **Verification**: `human-judgment`（可通过 curl 检查 HTTP 200 响应）

### AC-6: supervisord 管理双服务
- **Given**: 容器正常启动（无命令参数）
- **When**: 执行 `supervisorctl status`
- **Then**: sshd 和 jupyter 两个进程均为 RUNNING 状态
- **Verification**: `programmatic`

### AC-7: 中文环境配置正确
- **Given**: 容器正常运行
- **When**: 执行 `echo $LANG` 和 `date`
- **Then**: LANG 为 zh_CN.UTF-8，时区显示为 Asia/Shanghai（CST）
- **Verification**: `programmatic`

### AC-8: 健康检查正常工作
- **Given**: 容器正常运行
- **When**: 执行健康检查脚本
- **Then**: 两个服务均报告健康，退出码为 0
- **Verification**: `programmatic`

### AC-9: 命令模式正常工作
- **Given**: 镜像存在
- **When**: 执行 `docker run --rm caffe-jupyter-ssh:test bash -c "echo hello && whoami"`
- **Then**: 输出 hello，用户为 caffe-origin，不启动 supervisord 服务
- **Verification**: `programmatic`

### AC-10: 非 root 用户权限正确
- **Given**: 容器正常启动
- **When**: 执行 `whoami` 和 `id`
- **Then**: 当前用户为 caffe-origin，UID=1000，/workspace 目录可读写
- **Verification**: `programmatic`

### AC-11: Dockerfile 结构清晰
- **Given**: Dockerfile.jupyter-ssh 文件创建完成
- **When**: 人工检视文件内容
- **Then**: 分段注释清晰，风格与原 Dockerfile 一致，多阶段构建逻辑可追溯
- **Verification**: `human-judgment`

## Open Questions
- 无（已通过用户决策确认所有关键问题：Ubuntu 22.04、文件名 Dockerfile.jupyter-ssh、用户名 caffe-origin、系统 Python）
