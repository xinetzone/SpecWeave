---
title: "Jupyter Podman Rootless"
status: "draft"
---

# Jupyter Podman Rootless - Product Requirement Document

## Overview
- **Summary**: 创建一个基于 Podman rootless 模式的 Jupyter 开发容器镜像，支持 Python 3.14t (free-threading) + Conda (Miniforge3) + SSH + Podman (容器内嵌套容器能力)，全程使用非root用户，通过 invoke 任务统一管理构建/运行/停止等操作，解决传统Docker容器的权限问题和安全隐患。
- **Purpose**: 现有 jupyter-ssh-base 使用 venv + Docker Compose，存在两个核心问题：(1) 不支持 Conda 和 Python 3.14 free-threading；(2) 依赖Docker daemon，root权限带来安全风险和文件权限问题。新方案利用Podman原生rootless能力，实现两层权限隔离，彻底避免宿主机文件权限混乱。
- **Target Users**: 需要安全、隔离的Python/Jupyter开发环境的开发者，特别是使用WSL2/Linux的开发者，以及需要在容器内运行容器（Podman-in-Podman）进行容器化开发的用户。

## Goals
- 基于 Ubuntu 26.04 构建，支持中文环境（zh_CN.UTF-8 / Asia/Shanghai）
- 使用 Miniforge3 (conda-forge) 提供 Python 3.14 cp314t (free-threading) 环境
- 集成 JupyterLab/Notebook + OpenSSH Server，通过 supervisord 管理双服务
- 容器内安装 rootless Podman（podman + crun + conmon + fuse-overlayfs + slirp4netns），支持Podman-in-Podman
- 全程使用非root用户（devuser, UID 1000），正确配置 subuid/subgid 映射
- 使用 invoke 任务框架重写所有操作（build/run/stop/shell/clean等），替代 docker-compose.yml
- 在 `apps/containers/jupyter-podman-rootless/` 下创建独立应用目录
- 提供完善的健康检查和语法验证机制

## Non-Goals (Out of Scope)
- 不包含 Docker DinD（Docker-in-Docker）支持（Podman是唯一容器运行时）
- 不包含GPU/CUDA支持（保持基础镜像轻量，可作为后续变体基础）
- 不包含PyTorch/TensorFlow等大型ML框架预装（用户按需通过conda安装）
- 不支持Windows原生容器（仅支持Linux容器，WSL2/Linux/macOS）
- 不提供Kubernetes/Quadlet集成（保持简单，专注于单机开发场景）
- 不修改现有 jupyter-ssh-base（作为独立新应用存在）

## Background & Context
- 现有参考实现：[devcontainer-base](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base) 已实现 Podman + Miniforge3 + Python 3.14t，但它是全功能开发容器，包含Docker DinD和大量额外工具，镜像较重且需要--privileged模式
- 现有基础镜像：[jupyter-ssh-base](file:///d:/spaces/SpecWeave/apps/docker-images/jupyter-ssh-base) 提供SSH+Jupyter基础，但使用venv，无Conda和Podman支持
- Podman rootless技术基础：用户命名空间(UID/GID映射) + fuse-overlayfs存储 + slirp4netns/pasta用户态网络
- Invoke任务框架：awesome-okf-xs项目使用invoke作为任务运行器，结构清晰，可复用相同模式
- 应用目录位置：apps/containers/ 是新的分组（之前容器镜像在apps/docker-images/），按用户要求在apps/containers/下创建

## Functional Requirements
- **FR-1**: 容器基础系统基于ubuntu:26.04，配置apt镜像源选择（官方/阿里云/清华）
- **FR-2**: 安装Miniforge3到/opt/conda，配置conda-forge源和libmamba solver，创建main环境预装Python 3.14 cp314t
- **FR-3**: 在conda main环境中安装JupyterLab/Notebook及常用数据科学包
- **FR-4**: 配置非root用户devuser（UID 1000优先，被占用时自动分配），设置正确的家目录权限
- **FR-5**: 配置/etc/subuid和/etc/subgid（devuser:100000:65536）支持rootless Podman
- **FR-6**: 安装Podman(rootless模式)、crun、conmon、fuse-overlayfs、slirp4netns、uidmap
- **FR-7**: 容器内配置Podman使用fuse-overlayfs存储驱动（无需特权）
- **FR-8**: 安装并配置OpenSSH Server，禁用root登录，支持密码和公钥认证
- **FR-9**: 使用supervisord管理sshd和jupyter两个常驻服务
- **FR-10**: entrypoint.sh支持环境变量配置：USER_PASSWORD、JUPYTER_TOKEN、GRANT_SUDO、SSH_PUBLIC_KEY等
- **FR-11**: 健康检查脚本同时检测sshd和jupyter服务状态
- **FR-12**: 创建invoke任务集合（tasks/），提供build、run、stop、shell、logs、clean、status等命令
- **FR-13**: 支持--build-arg参数切换国内镜像源（apt/pip/conda）
- **FR-14**: Containerfile(Dockerfile)采用多阶段/分层构建，利用BuildKit缓存挂载优化构建速度
- **FR-15**: 构建时进行语法验证（sshd -t、bash -n、python语法检查）

## Non-Functional Requirements
- **NFR-1 (Security)**: 容器内进程全程以devuser（非root）运行；容器本身可用普通用户通过podman运行（rootless on host）；默认禁用sudo
- **NFR-2 (Size)**: 镜像体积控制在2GB以内（Miniforge3+Jupyter+Podman基础集合）
- **NFR-3 (Build Performance)**: 利用BuildKit缓存挂载（apt/pip/conda），增量构建时高耗时层（conda create）不重复执行
- **NFR-4 (Usability)**: invoke命令有清晰的帮助信息；启动后输出明确的SSH和Jupyter访问信息；自动生成随机密码/token（未显式设置时）
- **NFR-5 (Compatibility)**: Containerfile同时兼容podman build和docker build；支持WSL2(rootless Podman)、Linux原生rootless Podman；卷挂载无权限问题
- **NFR-6 (Maintainability)**: 遵循现有项目规范（分层日志、构建计时器、语法验证检查点）；目录结构与现有docker-images应用保持一致

## Constraints
- **Technical**: 
  - 必须使用BuildKit语法（syntax=docker/dockerfile:1.7-labs）
  - Miniforge3是唯一Conda发行版（conda-forge社区推荐，比Anaconda更轻量自由）
  - supervisord作为进程管理器（沿用现有成熟方案）
  - 不依赖--privileged标志运行容器
- **Business**:
  - 作为apps/containers/下第一个应用，建立该分组的规范
- **Dependencies**:
  - 基础镜像：ubuntu:26.04
  - Miniforge3：最新conda-forge发行版
  - Podman：Ubuntu 26.04官方源版本
  - Invoke：Python任务框架（作为开发依赖，pyproject.toml声明）

## Assumptions
- 用户在支持rootless Podman的环境中运行（WSL2+Podman、Linux cgroup v2）
- 用户了解invoke基本用法或能通过--help学习
- /workspace为默认工作目录，挂载卷到此目录持久化数据
- Podman-in-Podman场景下，宿主机需要配置用户命名空间（默认现代发行版已支持）

## Acceptance Criteria

### AC-1: 镜像构建成功
- **Given**: 在apps/containers/jupyter-podman-rootless/目录下
- **When**: 执行 `invoke build` 或 `podman build -t jupyter-podman-rootless .`
- **Then**: 镜像构建成功，无错误退出
- **Verification**: `programmatic`
- **Notes**: 构建过程中所有语法验证检查点通过

### AC-2: Python 3.14t环境正确
- **Given**: 容器已启动
- **When**: 在容器内执行 `python --version` 和 `python -c "import sys; print(sys.free_threaded)"`
- **Then**: 显示Python 3.14.x且free_threaded为True（cp314t free-threading模式）
- **Verification**: `programmatic`

### AC-3: Conda可用且配置正确
- **Given**: 容器内
- **When**: 执行 `conda --version` 和 `which python`
- **Then**: conda命令可用，python路径在/opt/conda/envs/main/bin/下
- **Verification**: `programmatic`

### AC-4: 非root用户运行
- **Given**: 容器运行中
- **When**: 在容器内执行 `whoami` 和 `id`
- **Then**: 当前用户是devuser（非root），UID为1000（或自动分配的非0 UID）
- **Verification**: `programmatic`

### AC-5: SSH服务正常
- **Given**: 容器启动，端口映射（如-p 2222:22）
- **When**: 使用ssh客户端连接 `ssh devuser@localhost -p 2222`
- **Then**: 能成功通过密码或公钥认证登录，获得shell
- **Verification**: `programmatic`
- **Notes**: root登录被明确拒绝

### AC-6: Jupyter服务正常
- **Given**: 容器启动，端口映射（如-p 8888:8888）
- **When**: 访问 `http://localhost:8888` 或curl `http://localhost:8888/api`
- **Then**: Jupyter正常响应，能通过token登录
- **Verification**: `programmatic`

### AC-7: 容器内Podman可运行（rootless模式）
- **Given**: 容器内以devuser身份
- **When**: 执行 `podman info` 和 `podman run --rm docker.io/library/alpine:latest echo hello`
- **Then**: podman命令正常工作，能成功拉取alpine镜像并运行容器输出"hello"
- **Verification**: `programmatic`
- **Notes**: 不需要--privileged标志，使用fuse-overlayfs存储

### AC-8: invoke命令集完整
- **Given**: 在项目目录下，已安装invoke（pip install invoke或pip install -e .）
- **When**: 执行 `invoke --list`
- **Then**: 列出build、run、stop、shell、logs、clean、status等可用任务
- **Verification**: `programmatic`

### AC-9: 卷挂载无权限问题
- **Given**: 启动容器时挂载本地目录：`invoke run --volume ./workspace:/workspace`
- **When**: 在容器内的/workspace目录创建文件 `touch test.txt`
- **Then**: 文件在宿主机上可见，且宿主机用户对该文件有读写权限（UID映射正确）
- **Verification**: `programmatic`
- **Notes**: 这是核心非功能性验证——解决Docker常见的挂载目录权限问题

### AC-10: 健康检查通过
- **Given**: 容器运行中
- **When**: 执行 `podman healthcheck run <container>` 或检查健康状态
- **Then**: 健康检查返回healthy
- **Verification**: `programmatic`

### AC-11: 中文环境配置正确
- **Given**: 容器内shell
- **When**: 执行 `locale` 和 `date`
- **Then**: LANG=zh_CN.UTF-8，时区为Asia/Shanghai
- **Verification**: `programmatic`

### AC-12: 目录结构符合规范
- **Given**: 项目创建完成
- **When**: 检查apps/containers/jupyter-podman-rootless/目录结构
- **Then**: 包含Containerfile、entrypoint.sh、config/、scripts/、tasks/、pyproject.toml等必要文件
- **Verification**: `human-judgment`

## Open Questions
- [ ] 用户是否需要Podman默认启用（即supervisord也管理podman系统服务？）—— 目前设计是Podman由用户按需以rootless方式启动，不常驻服务
- [ ] 默认Jupyter包集合范围？（仅jupyterlab还是包含numpy/pandas等基础数据科学包？）—— 建议最小集合（jupyterlab + notebook），其他用户按需安装
- [ ] 是否需要提供quadlet/systemd单元文件示例？—— 非目标，暂不提供
