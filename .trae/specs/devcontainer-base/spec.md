# devcontainer-base - Product Requirement Document

## Overview
- **Summary**: 基于 Ubuntu 26.04 的全功能开发容器基础镜像，集成 OpenSSH Server + Docker-in-Docker (DinD) + Podman rootless + Jupyter Notebook/Lab 四大核心服务，通过 supervisord 统一进程管理。支持服务独立启用/禁用、国内镜像源配置、非root用户开发环境，可作为其他容器化开发环境的基础镜像。
- **Purpose**: 现有 jupyter-ssh-base 缺少容器构建能力，docker-ssh-dind 缺少 Jupyter 交互开发环境且无 supervisord 多服务管理。本项目填补这一空白，提供一站式开发容器基础，避免上层应用重复配置环境。
- **Target Users**: 需要在容器内进行容器构建（Docker-in-Docker）、同时需要 Jupyter 交互式开发环境的开发者；CI/CD 环境中需要 rootless Podman 安全构建的用户；作为其他 SpecWeave 应用（如 caffe-ffi-jupyter）的下一代基础镜像。

## Goals
- 提供四服务（SSH/Docker/Podman/Jupyter）可组合的开发容器基础镜像
- 复用 jupyter-ssh-base 成熟的 supervisord 多服务管理、entrypoint 启动脚本、多阶段构建等模式
- 复用 docker-ssh-dind 的 Docker DinD 配置和守护进程设置
- 支持 Docker DinD（privileged模式）和 DooD（挂载宿主机socket）两种容器运行模式
- 提供完善的健康检查（覆盖所有启用的服务）
- 国内APT/PyPI镜像源可配置
- 完整的中文环境（zh_CN.UTF-8 / Asia/Shanghai）

## Non-Goals (Out of Scope)
- 不预装 PyTorch/TensorFlow 等大型ML框架（留给上层应用如 pytorch-base）
- 不预装 Caffe-FFI 等特定项目依赖（留给上层应用如 caffe-ffi-jupyter）
- 不提供 Kubernetes/CRI-O 等容器编排运行时（仅 Docker + Podman）
- 不提供 VS Code Server / code-server（未来可通过新增服务配置扩展，本次不实现）
- 不提供 rootless Docker（只支持 root Docker daemon + docker组 非root访问模式）

## Background & Context
- 现有基础镜像：
  - [apps/jupyter-ssh-base](file:///d:/spaces/SpecWeave/apps/jupyter-ssh-base)：SSH + Jupyter，supervisord管理，多阶段构建，Python venv在/opt/venv，非root用户jupyteruser
  - [apps/docker-ssh-dind](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind)：Docker DinD + SSH，单阶段构建，非root用户ai加入docker组，无supervisord
- 项目约束继承：Ubuntu 26.04基础镜像、中文环境、非root用户默认、敏感信息运行时生成、tini作为init进程
- 七概念方法论指导：通过第一性原理推导7条公理，对抗审查4视角验证，采纳5项关键修正

## Functional Requirements
- **FR-1**: SSH远程登录服务（sshd）
  - 默认监听22端口
  - ED25519密钥优先，host keys每次容器启动重新生成
  - 支持密码认证和公钥认证（SSH_PUBLIC_KEY环境变量注入）
  - 默认禁用root登录（ALLOW_ROOT_SSH=yes可启用）
  - 非root用户devuser（UID 1000）默认创建
- **FR-2**: Docker Engine服务（dockerd）
  - 默认启用（ENABLE_DOCKER=yes），可通过环境变量禁用
  - Docker CE CLI + daemon + containerd.io + buildx-plugin
  - overlay2存储驱动，json-file日志轮转（10MB×3）
  - devuser加入docker组，免sudo使用docker命令
  - 支持DinD模式（--privileged启动独立dockerd）和DooD模式（DOCKER_HOST指向挂载的/var/run/docker.sock）
  - /var/lib/docker作为VOLUME持久化
- **FR-3**: Podman容器引擎
  - 默认禁用（ENABLE_PODMAN=yes显式启用），避免与Docker cgroups冲突
  - 使用Ubuntu 26.04官方源podman包（不依赖第三方Kubic repo）
  - rootless模式为devuser预配置subuid/subgid
  - 支持fuse-overlayfs存储（无根环境）
  - devuser可直接运行podman命令无需sudo
- **FR-4**: Jupyter Notebook/Lab服务
  - 默认启用（ENABLE_JUPYTER=yes），可禁用
  - Python虚拟环境位于/opt/venv（多阶段构建从builder复制）
  - 默认监听0.0.0.0:8888
  - 支持token（JUPYTER_TOKEN）和密码（JUPYTER_PASSWORD）认证
  - Notebook工作目录为/workspace（VOLUME）
  - 预装notebook、jupyterlab、ipykernel、nbconvert、jupyter_server（复用jupyter-ssh-base的requirements.txt）
- **FR-5**: supervisord多服务管理
  - 统一管理sshd、dockerd、jupyter等服务
  - 每个服务独立配置文件（/etc/supervisor/conf.d/*.conf）
  - 根据环境变量ENABLE_*动态决定启动哪些服务
  - 支持supervisorctl状态查询和自动重启
- **FR-6**: entrypoint启动脚本
  - tini作为init进程（PID 1）
  - 6步启动流程：系统诊断→密码设置→host keys生成→SSH配置→Jupyter配置→服务启动（supervisord）
  - 支持命令模式：传入CMD（如bash）直接exec不启动服务
  - 随机密码生成（pwgen）并在启动日志中打印
  - 支持GRANT_SUDO=yes启用NOPASSWD sudo
  - 支持SSH_PUBLIC_KEY注入公钥认证
- **FR-7**: 健康检查
  - 内置healthcheck.sh脚本
  - 分服务检查：sshd（端口+进程）、docker（docker info）、jupyter（HTTP响应）
  - 根据服务启用状态动态调整检查项
  - 合理的start-period等待dockerd初始化
- **FR-8**: 国内镜像源支持
  - APT_MIRROR build-arg：official/aliyun/tuna
  - PIP_MIRROR build-arg：official/aliyun/tuna
  - 构建时自动配置对应镜像源

## Non-Functional Requirements
- **NFR-1**: 镜像构建
  - 多阶段构建（jupyter-builder + runtime），builder阶段含build-essential/python3-dev，runtime阶段仅保留运行时依赖
  - 每个RUN指令后清理apt缓存（rm -rf /var/lib/apt/lists/*）
  - pip安装使用--no-cache-dir
  - 最终镜像不含编译工具链
- **NFR-2**: 镜像体积
  - 预期1.2-1.8GB（四服务全开），禁用Podman约1.0-1.5GB
  - 构建日志输出每个阶段大小
- **NFR-3**: 安全
  - 禁止Dockerfile中硬编码密码/密钥
  - 密码哈希在entrypoint运行时动态生成
  - SSH host keys每次启动重新生成
  - 默认非root用户操作，sudo按需启用
- **NFR-4**: 可复用性
  - WORKDIR=/workspace，ENTRYPOINT使用tini
  - 支持作为其他项目基础镜像（FROM devcontainer-base）
  - 环境变量命名与现有镜像兼容（USER_PASSWORD、JUPYTER_TOKEN等沿用jupyter-ssh-base命名）
- **NFR-5**: 中文环境
  - locale: zh_CN.UTF-8
  - timezone: Asia/Shanghai（三层保证：tzdata配置+ln -sf + ENV TZ）
  - 运行时日志支持中文输出，构建注释使用英文
- **NFR-6**: 可观测性
  - entrypoint详细日志输出（带时间戳和[INFO]/[WARN]/[ERROR]级别）
  - 启动横幅打印访问信息
  - /etc/devcontainer-build-info记录构建元数据

## Constraints
- **Technical**: 
  - 基础镜像固定 ubuntu:26.04
  - Docker DinD必须使用--privileged运行
  - Podman rootless需要uidmap和fuse-overlayfs支持
  - Python虚拟环境路径/opt/venv（与jupyter-ssh-base保持一致）
- **Business**: 
  - 遵循apps/AGENTS.md新增应用规则
  - 复用现有模式而非从零重写（jupyter-ssh-base的supervisord/entrypoint/healthcheck模式，docker-ssh-dind的Docker安装配置）
- **Dependencies**: 
  - 依赖系统包：openssh-server、supervisor、docker-ce、containerd.io、docker-buildx-plugin、podman、fuse-overlayfs、uidmap、python3、python3-venv
  - 依赖Python包：notebook、jupyterlab、ipykernel、nbconvert、jupyter_server（版本固定）

## Assumptions
- Ubuntu 26.04官方源中podman包可用且稳定（已验证：Ubuntu 26.04 universe仓库包含podman 4.9+）
- Docker CE官方Ubuntu 26.04源已可用（docker-ssh-dind已验证ubuntu:26.04可以安装docker-ce）
- Docker和Podman默认不同时启动时不会冲突（默认ENABLE_DOCKER=yes, ENABLE_PODMAN=no）
- devuser用户名不与现有镜像（jupyteruser、ai）冲突，便于上层应用继承时区分

## Acceptance Criteria

### AC-1: 镜像构建成功
- **Given**: 已安装Docker，在apps/devcontainer-base目录
- **When**: 执行 `docker build -t devcontainer-base .` 或 `bash scripts/build.sh`
- **Then**: 镜像构建成功，无错误，构建日志包含各阶段完成标记
- **Verification**: `programmatic`
- **Notes**: 同时验证 `--build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun` 国内源构建

### AC-2: 基础服务启动（默认配置）
- **Given**: 使用默认配置启动容器 `docker run -d --privileged -p 2222:22 -p 8888:8888 -e USER_PASSWORD=test123 -e JUPYTER_TOKEN=test --name dc-test devcontainer-base`
- **When**: 等待60秒服务启动完成
- **Then**: 
  - sshd在22端口监听
  - dockerd正常运行，`docker exec dc-test docker info` 成功
  - jupyter在8888端口可访问
  - podman未启动（默认禁用）
  - `docker exec dc-test supervisorctl status` 显示sshd、dockerd、jupyter均为RUNNING
- **Verification**: `programmatic`

### AC-3: SSH登录验证
- **Given**: 容器已启动，端口映射2222→22
- **When**: 使用 `ssh -p 2222 devuser@localhost` 并输入密码
- **Then**: SSH登录成功，devuser身份正确，`docker ps` 可直接执行（docker组权限），`/workspace`为工作目录
- **Verification**: `programmatic`

### AC-4: Jupyter访问验证
- **Given**: 容器已启动，端口映射8888→8888
- **When**: 访问 `http://localhost:8888/?token=test`
- **Then**: Jupyter界面正常加载，可创建notebook，Python内核可连接
- **Verification**: `programmatic`

### AC-5: Docker DinD功能验证
- **Given**: 容器以--privileged启动
- **When**: 在容器内执行 `docker run --rm hello-world`
- **Then**: 嵌套容器正常运行，输出Hello from Docker!
- **Verification**: `programmatic`

### AC-6: Podman启用验证
- **Given**: 以 `docker run -d --privileged -e ENABLE_DOCKER=no -e ENABLE_PODMAN=yes -p 2222:22 -e USER_PASSWORD=test devcontainer-base` 启动
- **When**: 等待启动后，容器内执行 `podman info` 和 `podman run --rm alpine echo hello`
- **Then**: Podman正常运行，rootless模式下可拉取并运行容器
- **Verification**: `programmatic`

### AC-7: 服务禁用验证
- **Given**: 以 `docker run -d -p 8888:8888 -e ENABLE_SSH=no -e ENABLE_DOCKER=no -e JUPYTER_TOKEN=test devcontainer-base` 启动
- **When**: 检查服务状态
- **Then**: sshd和dockerd未运行，仅Jupyter启动，22端口未监听
- **Verification**: `programmatic`

### AC-8: 命令模式验证
- **Given**: 启动容器时传入bash命令
- **When**: 执行 `docker run -it --rm devcontainer-base bash`
- **Then**: 直接进入bash shell，supervisord和所有服务未启动，exit后容器停止
- **Verification**: `programmatic`

### AC-9: 健康检查验证
- **Given**: 容器正常运行（默认配置）
- **When**: 执行 `docker inspect --format='{{.State.Health.Status}}' dc-test`
- **Then**: 健康状态为healthy
- **Verification**: `programmatic`

### AC-10: 非root用户sudo权限验证
- **Given**: 以 `-e GRANT_SUDO=yes` 启动
- **When**: devuser执行 `sudo -n apt-get update`
- **Then**: sudo免密执行成功，无需输入密码
- **Verification**: `programmatic`

### AC-11: 公钥认证验证
- **Given**: 启动时传入SSH_PUBLIC_KEY环境变量
- **When**: 使用对应私钥SSH登录
- **Then**: 无需密码直接登录成功
- **Verification**: `programmatic`

### AC-12: 中文环境验证
- **Given**: 容器运行中
- **When**: 执行 `locale` 和 `date`
- **Then**: LANG=zh_CN.UTF-8，时区为CST（Asia/Shanghai）
- **Verification**: `programmatic`

### AC-13: 可复用性验证
- **Given**: 创建简单Dockerfile FROM devcontainer-base
- **When**: 构建并运行该派生镜像
- **Then**: 继承所有服务和配置正常工作，ENTRYPOINT和WORKDIR正确
- **Verification**: `programmatic`

### AC-14: 代码结构评审
- **Given**: 所有文件已创建
- **When**: 评审目录结构、Dockerfile多阶段构建、entrypoint.sh脚本质量
- **Then**: 
  - 目录结构与jupyter-ssh-base一致（config/、scripts/、docker-compose.yml等）
  - Dockerfile遵循多阶段构建规范，apt缓存清理到位
  - entrypoint.sh有详细日志和错误处理
  - AGENTS.md包含启动协议和完整路由表
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要预装docker-compose插件？当前方案只装docker-buildx-plugin，compose可通过pip或单独安装
- [ ] Podman是否需要提供podman.socket服务（Docker API兼容）供docker客户端连接？默认不启用，需要时通过环境变量开启？
- [ ] 上层应用caffe-ffi-jupyter是直接FROM devcontainer-base还是继续FROM jupyter-ssh-base？这决定了devcontainer-base的兼容性优先级
