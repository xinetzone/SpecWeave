---
version: 1.0
---

# Docker-in-Docker SSH 容器镜像 - Product Requirement Document

## Overview
- **Summary**: 创建一个功能完整的 Containerfile，用于构建包含 Docker 引擎（Docker-in-Docker）和 OpenSSH 服务的 Docker 镜像。该镜像支持在容器内运行 Docker 守护进程，并通过 SSH 远程连接访问。
- **Purpose**: 提供一个可用于 CI/CD 流水线、远程开发环境、容器化构建服务的基础镜像，允许用户通过 SSH 连接后在容器内部使用完整的 Docker 功能。
- **Target Users**: DevOps 工程师、CI/CD 管理员、需要远程容器化开发环境的开发者、测试工程师。

## Goals
- 基于稳定的 Linux 发行版（Ubuntu LTS）构建镜像
- 正确安装和配置 OpenSSH 服务器，支持密钥认证和密码认证两种方式
- 安装 Docker 引擎及其所有依赖组件，确保 Docker daemon 能在容器内正常启动
- 配置 cgroup 和权限，允许 Docker daemon 在特权模式或非特权模式（按需配置）下运行
- 创建 docker 用户组并配置非 root 用户可运行 docker 命令
- 暴露 SSH 默认端口 22，配置 entrypoint 脚本同时启动 sshd 和 dockerd 服务
- 使用多阶段构建减小最终镜像体积
- 提供清晰注释说明各步骤作用，确保镜像可审计、可维护
- 构建过程安全，不硬编码密码、密钥等敏感信息，支持运行时配置

## Non-Goals (Out of Scope)
- 不包含 Kubernetes 或其他容器编排工具
- 不提供 Docker Compose（如需可额外安装，但不在基础镜像中）
- 不配置特定用户的 SSH 公钥（运行时通过挂载或环境变量注入）
- 不优化特定云平台的兼容性（保持通用性）
- 不包含除 Docker 和 SSH 之外的额外开发工具（保持镜像最小化）
- 不支持 rootless Docker 模式（使用标准 Docker daemon）

## Background & Context
- Docker-in-Docker (DinD) 是常见的 CI/CD 场景需求，允许在容器内执行 docker build/run 等操作
- SSH 访问允许远程连接到容器进行交互式操作和调试
- Ubuntu LTS 提供稳定的包管理和较长的支持周期，适合作为基础镜像
- 该镜像需要支持 `--privileged` 标志运行（Docker daemon 需要访问宿主机内核特性）
- 参考项目中已有的 Containerfile 风格（如 vendor/flexloop/apps/chaos/containers/ 下的 Containerfile）

## Functional Requirements
- **FR-1**: 基础镜像使用 Ubuntu 26.04 LTS
- **FR-2**: 安装 openssh-server 并配置：
  - 生成主机 SSH 密钥（rsa, ecdsa, ed25519）
  - 配置 sshd_config 允许 root 登录（可选，通过环境变量控制）
  - 禁用空密码登录
  - 配置 PAM 和登录环境
- **FR-3**: 安装 Docker Engine (docker-ce, docker-ce-cli, containerd.io) 及其依赖
  - 添加 Docker 官方 GPG key 和 apt 仓库
  - 安装指定稳定版本或最新稳定版
  - 配置 Docker daemon（存储驱动、cgroup 驱动等）
- **FR-4**: 创建 docker 用户组，配置适当权限
  - 创建默认非 root 用户（如 `dockeruser`）或允许运行时指定用户
  - 将用户加入 docker 组，允许无需 sudo 运行 docker 命令
- **FR-5**: 配置 entrypoint 启动脚本，使用监督进程（如 tini 或 supervisord）同时管理：
  - sshd 服务（前台或后台模式，由进程管理器监控）
  - dockerd 守护进程
  - 正确处理信号传递和子进程回收
- **FR-6**: 暴露端口 22/tcp 用于 SSH 连接
- **FR-7**: 支持通过环境变量配置：
  - ROOT_PASSWORD：设置 root 用户密码（默认随机生成并在启动日志中显示）
  - SSH_PUBLIC_KEY：注入公钥实现免密登录
  - DOCKER_OPTS：传递额外的 dockerd 启动参数
- **FR-8**: 使用多阶段构建，分离构建依赖和运行时依赖，减小镜像体积
- **FR-9**: 清理 apt 缓存和临时文件，减小镜像层数
- **FR-10**: Containerfile 中每一步关键操作都有注释说明用途和配置原因

## Non-Functional Requirements
- **NFR-1**: 镜像体积控制在合理范围内（多阶段构建后应 < 500MB，理想 < 400MB）
- **NFR-2**: 镜像构建时间应在合理范围内（网络正常情况下 < 10 分钟）
- **NFR-3**: 容器启动后，sshd 和 dockerd 应在 10 秒内就绪
- **NFR-4**: 支持 docker stop 优雅关闭，发送 SIGTERM 给所有子进程
- **NFR-5**: 镜像不包含硬编码的敏感信息（密码、密钥、token 等）
- **NFR-6**: Docker daemon 存储默认使用 overlay2 驱动（需宿主机支持）
- **NFR-7**: 日志输出到 stdout/stderr，便于 docker logs 查看

## Constraints
- **Technical**:
  - 容器必须以 `--privileged` 模式运行（Docker daemon 需要内核权限），或使用官方 DinD 推荐的非特权配置方案
  - 需要挂载 `/var/lib/docker` 卷或绑定挂载以持久化镜像和容器数据
  - 基础镜像仅限 Linux（Ubuntu LTS）
  - 使用 apt 包管理器（Ubuntu）
- **Business**:
  - 无商业限制，开源可用
- **Dependencies**:
  - Docker 官方 apt 仓库可访问（构建时）
  - Ubuntu 官方软件源可访问（构建时）
  - tini 初始化进程（作为 init 进程）

## Assumptions
- 用户理解 Docker-in-Docker 的安全风险，仅在可信环境中使用
- 运行容器时会正确配置 `--privileged` 标志或使用适当的 cgroup 权限
- 宿主机运行 Docker 18.09+ 版本以支持 overlay2 和必要的内核特性
- 生产环境使用时会通过环境变量或 volume 挂载注入 SSH 公钥，而非使用密码认证
- 用户会挂载持久化卷到 `/var/lib/docker` 以避免数据丢失

## Acceptance Criteria

### AC-1: Containerfile 语法正确且可构建
- **Given**: 系统安装了 Docker 或 Podman，Containerfile 已存在
- **When**: 执行 `podman build -t docker-ssh -f Containerfile .` 或 `docker build -t docker-ssh -f Containerfile .`
- **Then**: 镜像构建成功完成，无错误，退出码为 0
- **Verification**: `programmatic`
- **Notes**: 构建过程中所有 RUN 步骤成功执行，没有 apt 安装错误

### AC-2: 镜像启动后 SSH 服务可连接
- **Given**: 使用构建的镜像启动容器：`docker run -d --privileged -p 2222:22 --name dind-test docker-ssh`
- **When**: 等待容器启动完成，然后使用 SSH 客户端连接：`ssh -o StrictHostKeyChecking=no -p 2222 root@localhost`（使用启动时生成的密码或注入的密钥）
- **Then**: SSH 连接成功建立，可以获得 shell 会话
- **Verification**: `programmatic`
- **Notes**: 使用 ssh-keyscan 获取主机密钥，使用 sshpass 或密钥进行验证

### AC-3: 容器内 Docker 命令可正常工作
- **Given**: 通过 SSH 连接到运行中的容器，或使用 `docker exec` 进入容器
- **When**: 执行 `docker version`、`docker info`、`docker run --rm hello-world`
- **Then**: 
  - `docker version` 显示 client 和 server 版本信息
  - `docker info` 显示 Docker daemon 配置信息（存储驱动为 overlay2）
  - `docker run hello-world` 成功拉取镜像并输出欢迎信息
- **Verification**: `programmatic`

### AC-4: 非 root 用户可运行 Docker 命令
- **Given**: 默认创建了非 root 用户（如 dockeruser）并加入 docker 组
- **When**: 使用该用户登录 SSH 或 su 切换到该用户，执行 `docker ps`
- **Then**: 命令成功执行，无需输入密码，无权限错误
- **Verification**: `programmatic`

### AC-5: 支持环境变量配置 root 密码
- **Given**: 启动容器时设置环境变量：`docker run -d --privileged -e ROOT_PASSWORD=testpass123 -p 2222:22 docker-ssh`
- **When**: 使用密码 testpass123 通过 SSH 登录 root 用户
- **Then**: 登录成功
- **Verification**: `programmatic`

### AC-6: 支持注入 SSH 公钥免密登录
- **Given**: 启动容器时设置环境变量：`docker run -d --privileged -e SSH_PUBLIC_KEY="$(cat ~/.ssh/id_rsa.pub)" -p 2222:22 docker-ssh`
- **When**: 使用对应的私钥直接 SSH 登录：`ssh -p 2222 root@localhost`
- **Then**: 无需输入密码直接登录成功
- **Verification**: `programmatic`

### AC-7: 多阶段构建已应用，镜像经过清理
- **Given**: 镜像构建完成
- **When**: 检查镜像体积：`docker images docker-ssh`，检查镜像中是否存在构建时依赖
- **Then**: 
  - 镜像体积显著小于单阶段构建（对比不使用多阶段的情况）
  - `/var/cache/apt/archives/` 中无残留 .deb 包
  - 没有构建工具（gcc, make 等）残留（除非运行时必须）
- **Verification**: `programmatic` + `human-judgment`

### AC-8: 容器支持优雅停止
- **Given**: 容器正常运行中
- **When**: 执行 `docker stop dind-test`
- **Then**: 容器在合理时间内（< 30秒）停止，dockerd 和 sshd 收到 SIGTERM 正确关闭
- **Verification**: `programmatic`

### AC-9: Containerfile 包含充分注释
- **Given**: Containerfile 已编写完成
- **When**: 人工审查 Containerfile 内容
- **Then**: 
  - 每个主要部分（基础镜像、SSH安装、Docker安装、配置、entrypoint）都有标题注释
  - 关键配置项有解释说明其用途
  - 包含使用说明注释（如何构建、如何运行、环境变量说明）
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要同时支持 Ubuntu 和 Alpine 两个版本？（当前 PRD 选择 Ubuntu LTS，Alpine 可作为后续扩展）
- [ ] 是否需要在镜像中预装 docker-compose 或 docker buildx？
- [ ] 默认 non-root 用户的用户名和 UID 应如何设置？（建议 dockeruser:1000，但可能需要可配置）
- [ ] 是否需要支持通过 Docker socket 挂载方式（Docker-outside-of-Docker）作为 DinD 的替代方案？（当前仅实现 DinD）
