---
id: "jupyter-ssh-base"
version: "1.1"
status: "completed"
source: "用户需求+七概念方法论F→V→I链路推导"
x-toml-ref: "../../../.meta/toml/.trae/specs/jupyter-ssh-base/spec.toml"
---
# Jupyter SSH Base - 标准化基础镜像产品需求文档

## Overview
- **Summary**: 基于 Ubuntu 26.04 构建的企业级 Docker 基础镜像，同时集成 OpenSSH Server 和 Jupyter Notebook 服务，通过 supervisord 实现多服务进程管理，遵循 Docker 最佳实践，设计为可复用的基础层镜像，适用于远程开发、数据科学、机器学习实验等场景。
- **Purpose**: 解决现有 Docker 开发环境镜像分散、安全配置不统一、服务管理不规范的问题，提供一个安全、轻量、可复用、配置灵活的标准化基础镜像，作为其他项目的 FROM 基础层。
- **Target Users**: 
  - 需要远程 SSH + Jupyter 开发环境的数据科学家/算法工程师
  - 需要快速搭建可复现实验环境的研究人员
  - 需要基于此镜像构建衍生应用的开发者
  - WSL2 + Docker Desktop 环境用户

## Goals
- 基于固定版本 `ubuntu:26.04` 构建，不使用 `latest` 标签
- 集成企业级安全配置的 SSH 服务（ED25519 密钥、非root用户、禁用root登录）
- 集成安全配置的 Jupyter Notebook（密码/token认证、绑定0.0.0.0、严格CORS）
- 使用 supervisord 统一管理双服务，实现自动重启、健康检查
- 多阶段构建+缓存清理，最终镜像体积 &lt; 800MB
- 完整的中文环境支持（zh_CN.UTF-8 + Asia/Shanghai）
- 所有配置通过环境变量可定制，敏感信息不硬编码
- 提供清晰的文档和使用示例，可直接被其他项目 FROM 复用

## Non-Goals (Out of Scope)
- 不包含 GPU/CUDA 支持（衍生镜像可自行添加）
- 不预装 PyTorch/TensorFlow 等大型 ML 框架（保持基础镜像轻量）
- 不包含 Docker-in-Docker 功能（参考 docker-ssh-dind 项目）
- 不提供 HTTPS/TLS 终止（建议在前端反向代理层处理）
- 不内置多用户支持（单用户 jupyteruser）
- 不包含 conda（使用系统 Python 3 + pip，衍生镜像可自行安装）

## Background & Context
- **现有项目参考**：
  - [docker-ssh-dind](../../apps/docker-ssh-dind/AGENTS.md)：已实现 SSH + DinD 镜像，有成熟的 Containerfile/entrypoint 规范
  - [pytorch-base](../../apps/pytorch-base/AGENTS.md)：已实现 PyTorch 基础镜像，有7阶段构建、国内镜像源、离线包支持经验
- **技术栈一致性**：保持与现有 Docker 项目相同的约定（中文环境、tini init、结构化日志、构建信息文件）
- **WSL 环境兼容**：确保在 WSL2 + Docker Desktop 环境下正常运行（已有 docker-ssh-dind 验证兼容性）
- **进程管理选择**：选择 supervisord 而非 systemd（systemd 在容器中需要特殊权限，supervisord 轻量且成熟稳定）

## 文档元数据格式约定
- **YAML Frontmatter**：仅保留 id/version/source/x-toml-ref 4个核心字段
- **外部 TOML 元数据**：完整元数据存放在 `.meta/toml/.trae/specs/jupyter-ssh-base/` 目录
- **字段合并规则**：渲染时浅层合并，TOML 字段优先级高于 Frontmatter

## Functional Requirements
- **FR-1**: 基础镜像系统配置
  - 使用 `ubuntu:26.04` 固定版本基础镜像
  - 配置中文 locale `zh_CN.UTF-8` 和时区 `Asia/Shanghai`
  - 使用 tini 作为 PID 1 init 进程，处理信号转发和僵尸进程
  - 安装基础工具：ca-certificates、curl、wget、git、vim、nano、sudo、tini、locales、tzdata、supervisor、openssh-server、python3、python3-pip、python3-venv

- **FR-2**: 非root用户安全配置
  - 创建 `jupyteruser` 用户（UID 1000，GID 1000）
  - 用户主目录 `/home/jupyteruser`，工作目录 `/workspace`（归属 jupyteruser）
  - 默认禁用 root SSH 登录（可通过环境变量 `ALLOW_ROOT_SSH=yes` 开启）
  - 默认禁用 NOPASSWD sudo（可通过 `ENABLE_SUDO_NOPASSWD=1` 开启）
  - 支持通过 `JUPYTER_PASSWORD` 环境变量设置用户密码
  - 密码未设置时生成16位随机密码并在启动日志高亮输出

- **FR-3**: SSH 服务企业级安全配置
  - 优先使用 ED25519 主机密钥算法，禁用弱算法
  - 容器启动时自动生成主机密钥（不打包进镜像），支持挂载卷持久化
  - 启用密码认证和公钥认证
  - 禁用空密码、禁用 X11 转发
  - 通过 `SSH_PUBLIC_KEY` 环境变量注入公钥到 authorized_keys
  - 开放 22 端口（EXPOSE 22）
  - 配置 SSH 日志输出到 stdout/stderr

- **FR-4**: Jupyter Notebook 安全配置
  - 通过 requirements.txt 固定 Jupyter Notebook 版本
  - 使用 pip 安装，安装后清理 pip 缓存
  - 生成加密配置文件，设置密码哈希或 token 认证
  - 支持 `JUPYTER_TOKEN` 环境变量设置访问 token
  - 支持 `JUPYTER_PASSWORD` 环境变量设置访问密码（自动生成哈希）
  - 绑定 `0.0.0.0:8888`，允许远程访问
  - 默认严格 CORS（仅同源），支持 `JUPYTER_CORS_ORIGIN` 环境变量配置
  - 禁用 Jupyter 的 root 运行警告（容器环境已处理用户切换）
  - 以 jupyteruser 身份运行 Jupyter
  - 开放 8888 端口（EXPOSE 8888）
  - 配置 Jupyter 日志输出到 stdout/stderr

- **FR-5**:  supervisord 多服务管理
  - 配置 supervisord 管理 sshd 和 jupyter-notebook 两个服务
  - 服务配置分离：`/etc/supervisor/conf.d/sshd.conf` 和 `/etc/supervisor/conf.d/jupyter.conf`
  - 配置自动重启策略：进程异常退出时自动重启（startretries=3，autorestart=true）
  - 配置启动优先级：sshd 先启动，jupyter 后启动（无硬依赖，但顺序启动更稳定）
  - 禁用 supervisord 的 web UI 和 inet HTTP server（仅用本地 unix socket）
  - 所有子进程日志输出到 stdout/stderr，统一由 docker logs 收集
  - supervisord 作为前台主进程运行（nodaemon=true）

- **FR-6**: Entrypoint 启动脚本
  - 支持 `DEBUG=1` 开启调试模式（set -x）
  - 启动时执行系统诊断（OS/kernel/arch/版本信息/权限检查）
  - 启动横幅显示关键连接信息（SSH命令、Jupyter URL带token）
  - 按顺序执行：生成主机密钥 → 配置密码 → 注入SSH公钥 → 配置Jupyter → 启动supervisord
  - 支持命令模式：docker run 带命令时，不启动服务直接 exec 命令（用于调试）
  - 优雅关闭：捕获 SIGTERM/SIGINT，通知 supervisord 停止所有服务
  - 支持环境变量配置覆盖：所有关键参数可通过 -e 传入

- **FR-7**: 镜像优化与安全加固
  - 采用多阶段构建（或优化单阶段分层），减少最终镜像层数
  - 所有 apt-get install 使用 `--no-install-recommends`
  - 每个 RUN 指令后立即执行 `apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*`
  - pip 安装使用 `--no-cache-dir`，安装后执行 `pip cache purge`
  - 合并相关 RUN 指令，减少镜像层数
  - 正确设置文件权限（/run/sshd 755，~/.ssh 700，authorized_keys 600）
  - 不安装编译工具链和开发头文件（除非必要）
  - 写入构建信息到 `/etc/jupyter-ssh-build-info`（构建日期、基础镜像版本、Jupyter版本等）

- **FR-8**: 健康检查
  - 配置 HEALTHCHECK 指令：同时检查 TCP 22 和 TCP 8888 端口
  - 健康检查间隔 30s，超时 10s，启动等待 10s，重试 3 次
  - 健康检查失败返回非0状态，便于编排系统（docker-compose/k8s）判断

- **FR-9**: 项目文件组织
  - `Dockerfile`：多阶段/优化构建文件，包含详细英文注释
  - `requirements.txt`：Jupyter 及依赖版本固定
  - `config/sshd_config`：定制化 SSH 配置片段（追加到默认配置或替换）
  - `config/jupyter_notebook_config.py`：Jupyter 基础配置模板（entrypoint 运行时处理密码/token）
  - `config/supervisord.conf`：supervisord 主配置
  - `config/supervisor/conf.d/sshd.conf`：sshd 服务配置
  - `config/supervisor/conf.d/jupyter.conf`：jupyter 服务配置
  - `entrypoint.sh`：容器启动脚本
  - `.dockerignore`：排除不必要的构建上下文文件
  - `build.sh`：一键构建脚本（支持 --tag、--no-cache 等参数）
  - `README.md`：完整的构建、运行、配置、扩展文档
  - `docker-compose.yml`：docker-compose 示例
  - `AGENTS.md`：AI协作者入口文件（遵循项目规范）

- **FR-10**: 环境变量配置清单
  - `JUPYTER_PASSWORD`：Jupyter 和系统用户密码（未设置则随机生成）
  - `JUPYTER_TOKEN`：Jupyter token（与密码二选一，token优先）
  - `ROOT_PASSWORD`：root 用户密码（默认不设置root密码，因为root SSH默认禁用）
  - `SSH_PUBLIC_KEY`：SSH 公钥内容（追加到 authorized_keys）
  - `ALLOW_ROOT_SSH`：是否允许 root SSH 登录（默认 `no`）
  - `ENABLE_SUDO_NOPASSWD`：是否启用免密 sudo（默认 `0`/禁用）
  - `JUPYTER_CORS_ORIGIN`：Jupyter CORS 允许来源（默认空，仅同源）
  - `DEBUG`：是否开启 entrypoint 调试日志（默认 `0`）
  - `ENTRYPOINT_QUIET`：是否静默启动横幅（默认 `0`）

## Non-Functional Requirements
- **NFR-1（性能）**: 容器启动时间 &lt; 15秒（从docker run到服务就绪）
- **NFR-2（体积）**: 最终镜像体积 &lt; 800MB（docker images 查看）
- **NFR-3（安全）**: 
  - 镜像中无硬编码密码/密钥/token
  - 默认不以 root 运行 Jupyter
  - OpenSSH 配置符合 Mozilla SSH 安全指南（现代兼容性级别）
  - 无高危 CVE 漏洞（构建时可扫描）
- **NFR-4（可复用性）**:
  - 其他项目可直接 `FROM jupyter-ssh-base:latest` 扩展使用
  - 扩展时无需修改 entrypoint，只需：pip install、apt install、添加supervisor配置、挂载卷
  - 提供清晰的扩展示例文档
- **NFR-5（可靠性）**:
  - sshd 或 jupyter 崩溃后 supervisord 5秒内自动重启
  - 容器收到 SIGTERM 后 10秒内优雅关闭
  - 在 WSL2 + Docker Desktop 环境下运行稳定
- **NFR-6（可维护性）**:
  - Dockerfile 每个阶段有清晰注释和日志标记
  - 配置文件分离，便于理解和修改
  - 构建脚本可重复执行（幂等）
- **NFR-7（可观测性）**:
  - 所有服务日志输出到 stdout/stderr，可通过 `docker logs` 查看
  - 启动日志包含关键诊断信息（版本、监听端口、访问方式）
  - 构建日志有清晰的 Stage 标记（[Stage 1/N]、[OK]、[WARN]、[ERROR]）

## Constraints
- **Technical**:
  - 基础镜像：ubuntu:26.04（必须与现有项目一致）
  - 进程管理：supervisord（不用systemd/s6-overlay）
  - init进程：tini（必须）
  - Python：使用 Ubuntu 26.04 系统自带 python3（不额外安装Miniconda）
  - 构建：必须支持 BuildKit（用于缓存挂载）
  - 架构：优先 x86_64，兼容 aarch64（ARM64 Mac）
- **Business**:
  - 作为内部基础镜像，暂不发布到公共 Docker Hub
  - 项目位置：`d:\spaces\SpecWeave\apps\jupyter-ssh-base\`
- **Dependencies**:
  - Docker &gt;= 20.10（BuildKit 支持）
  - docker-compose &gt;= 2.0（可选，用于示例）
  - WSL2（目标运行环境之一）

## Assumptions
- Ubuntu 26.04 官方基础镜像中 python3 版本 &gt;= 3.12，满足 Jupyter Notebook 最新版要求
- WSL2 环境下 Docker Desktop 运行正常，端口映射无问题
- 用户有基本的 Docker 使用知识
- 国内网络环境：构建时使用国内镜像源（参考 pytorch-base 的阿里云 apt 源、清华/阿里 pip 源）
- 容器运行时不需要 --privileged 权限（与 DinD 不同）

## Acceptance Criteria

### AC-1: 基础镜像构建成功
- **Given**: 在 `apps/jupyter-ssh-base/` 目录下
- **When**: 执行 `./build.sh` 或 `docker build -t jupyter-ssh-base .`
- **Then**: 构建成功无错误，有清晰的 Stage 日志标记，最终镜像存在
- **Verification**: `programmatic`
- **Notes**: 检查构建日志中无 ERROR，docker images 能看到镜像

### AC-2: 中文环境配置正确
- **Given**: 镜像已构建
- **When**: 运行容器并执行 `locale` 和 `date`
- **Then**: LANG=zh_CN.UTF-8，时区显示 Asia/Shanghai（CST）
- **Verification**: `programmatic`

### AC-3: 非root用户存在且权限正确
- **Given**: 容器已启动
- **When**: 执行 `docker exec &lt;container&gt; id jupyteruser`
- **Then**: 显示 uid=1000(jupyteruser) gid=1000(jupyteruser)，/workspace 目录归属 jupyteruser
- **Verification**: `programmatic`

### AC-4: SSH 服务可正常连接
- **Given**: 容器已启动并映射端口 -p 2222:22，设置了 JUPYTER_PASSWORD=testpass123
- **When**: 使用 `ssh -p 2222 jupyteruser@localhost` 连接并输入密码
- **Then**: SSH 登录成功，进入 shell 提示符
- **Verification**: `programmatic`
- **Notes**: 使用 sshpass 自动化验证

### AC-5: root SSH 默认禁用
- **Given**: 容器默认启动（未设置 ALLOW_ROOT_SSH=yes）
- **When**: 尝试 `ssh -p 2222 root@localhost`
- **Then**: root 登录被拒绝（Permission denied 或立即断开）
- **Verification**: `programmatic`

### AC-6: Jupyter Notebook 可访问
- **Given**: 容器已启动并映射端口 -p 8888:8888，设置了 JUPYTER_PASSWORD=testpass123
- **When**: 访问 http://localhost:8888 或使用启动日志中的带token URL
- **Then**: Jupyter 登录页面正常显示，输入密码或token后可进入，能创建和运行 notebook
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 用 curl 检查 HTTP 200 响应，人工验证 UI 功能

### AC-7: 双服务同时运行
- **Given**: 容器已启动
- **When**: 执行 `docker exec &lt;container&gt; supervisorctl status`
- **Then**: sshd 和 jupyter 两个进程状态都是 RUNNING
- **Verification**: `programmatic`

### AC-8: 服务崩溃自动重启
- **Given**: 容器已启动，双服务 RUNNING
- **When**: 执行 `docker exec &lt;container&gt; pkill jupyter-notebook` 杀死 jupyter 进程
- **Then**: 10秒内 supervisord 自动重启 jupyter，supervisorctl status 恢复 RUNNING
- **Verification**: `programmatic`

### AC-9: 镜像体积符合要求
- **Given**: 镜像已构建
- **When**: 执行 `docker images jupyter-ssh-base`
- **Then**: SIZE 列显示 &lt; 800MB
- **Verification**: `programmatic`

### AC-10: 健康检查正常工作
- **Given**: 容器已启动并运行正常
- **When**: 执行 `docker inspect --format='{{.State.Health.Status}}' &lt;container&gt;`
- **Then**: 约30秒后状态变为 `healthy`
- **Verification**: `programmatic`

### AC-11: 优雅关闭
- **Given**: 容器已启动
- **When**: 执行 `docker stop &lt;container&gt;`
- **Then**: 容器在10秒内停止（无超时强制杀死），docker logs 最后显示关闭日志
- **Verification**: `programmatic`

### AC-12: 无敏感信息硬编码
- **Given**: Dockerfile 和所有配置文件
- **When**: 检查代码内容
- **Then**: 无硬编码密码、密钥、token，所有敏感配置通过环境变量注入
- **Verification**: `human-judgment` + `programmatic`（grep 检查 password/token/secret 关键词）

### AC-13: 命令模式正常工作
- **Given**: 镜像已构建
- **When**: 执行 `docker run --rm jupyter-ssh-base echo "hello"`
- **Then**: 输出 "hello" 后容器退出，不启动任何服务
- **Verification**: `programmatic`

### AC-14: 作为基础镜像可复用
- **Given**: 已有 jupyter-ssh-base 镜像
- **When**: 创建一个简单的衍生 Dockerfile FROM jupyter-ssh-base 添加一个 pip 包
- **Then**: 衍生镜像构建成功，运行后原有 SSH+Jupyter 功能正常，新增包可用
- **Verification**: `programmatic`

### AC-15: 文档完整清晰
- **Given**: README.md 已编写
- **When**: 阅读 README.md
- **Then**: 包含构建命令、运行命令（docker run 和 docker-compose）、环境变量说明、扩展示例、故障排查
- **Verification**: `human-judgment`

## Open Questions (已解决)
- [x] Ubuntu 26.04 系统 python3 具体版本号是多少？是否需要额外安装 python3-venv？→ Python 3.12.x，需要安装 python3-venv 包
- [x] 是否需要配置国内 pip 镜像源为默认（阿里云/清华）？→ 不默认，通过 build-arg 可选配置（APT_MIRROR/PIP_MIRROR），build.sh --cn 一键启用
- [x] SSH 公钥注入是否需要支持从文件挂载（如挂载 ~/.ssh/authorized_keys）？→ 支持，entrypoint 自动处理挂载的 authorized_keys 权限（600）
- [x] 工作目录 /workspace 是否需要作为 VOLUME 声明？→ 是，已声明 VOLUME ["/workspace"]
- [x] Jupyter 是否需要配置默认 Notebook 目录（/workspace）？→ 是，使用 c.ServerApp.root_dir 配置

---

## Implementation Notes (v1.1 - 实际实现记录)

> 本节记录实施过程中与原始设计的差异和关键决策，供后续维护参考。

### 架构差异
1. **多阶段构建**：原设计建议7阶段单阶段构建，实际采用2阶段（builder → runtime）真正隔离编译工具链，runtime阶段分为6个逻辑Stage块
2. **Python虚拟环境**：新增 /opt/venv 虚拟环境，避免污染系统Python，通过多阶段COPY传递到runtime
3. **UID分配**：原设计固定UID 1000，实际ubuntu:26.04镜像已有ubuntu用户占用UID 1000，改为自动分配（优先1000，回退到自动），实际UID=1001

### 新增功能
1. **国内镜像源build-arg**：APT_MIRROR/PIP_MIRROR（official/aliyun/tuna），build.sh --cn 一键启用
2. **环境变量别名**：ENABLE_SUDO_NOPASSWD→GRANT_SUDO、JUPYTER_CORS_ORIGIN→JUPYTER_ALLOW_ORIGIN，向后兼容
3. **/etc/environment PATH修复**：解决SSH非交互shell无法访问venv PATH的问题
4. **profile.d/venv.sh**：系统级venv环境配置，登录shell自动激活
5. **build.sh增强**：支持--tag/--registry/--no-cache/--cn/--apt-mirror/--pip-mirror参数

### 技术细节修正
1. **Jupyter root_dir**：使用 `c.ServerApp.root_dir` 替代已弃用的 `c.NotebookApp.notebook_dir`（Jupyter Server 2.x）
2. **tini init**：ENTRYPOINT使用tini作为PID 1，正确处理僵尸进程和信号传递
3. **安全加固**：SSH配置禁用TCP/Agent/PermitTunnel/PermitUserEnvironment/Kerberos/GSSAPI/ChrootDirectory/PAM/PrintMotd等不常用功能
4. **日志国际化**：启动日志使用中文输出，便于中文用户理解
5. **实际预装包**：不包含git/nano（精简），新增procps/pwgen/python3-venv（必要依赖）

### 验证结果
- 镜像大小：713MB（< 800MB目标）✓
- 集成测试：16项全部通过 ✓
- 支持SSH密码登录、root拒绝、自动重启、命令模式、sudo授权、CORS配置 ✓
