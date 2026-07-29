---
version: "1.0"
---

# PyCaffe Jupyter SSH Docker - Product Requirement Document

## Overview
- **Summary**: 在 `projects/xuanspace/vendor/caffe/docker/standalone/` 下创建新目录 `pycaffe-jupyter-ssh/`，基于现有的 `pycaffe/Dockerfile` 构建一个同时支持 SSH 服务和 Jupyter Notebook/Lab 的 PyCaffe 开发环境 Docker 镜像。新镜像复用 `apps/jupyter-ssh-base` 的配置资源和启动逻辑，确保双服务（sshd + jupyter）通过 supervisord 可靠管理。
- **Purpose**: 为 PyCaffe 开发者提供开箱即用的交互式开发环境，支持 SSH 远程登录和 Jupyter Notebook 浏览器交互，同时保持 PyCaffe 原生运行时的完整性和性能。
- **Target Users**: PyCaffe 框架开发者、深度学习研究人员、需要远程交互式 Caffe 开发环境的工程师。

## Goals
- 在 `docker/standalone/pycaffe-jupyter-ssh/` 创建完整的 Docker 构建目录
- 基于 pycaffe runtime 镜像扩展，完整保留 PyCaffe 运行时能力
- 复用 `apps/jupyter-ssh-base/` 的 supervisord 配置、sshd 配置、Jupyter 配置和 entrypoint 启动逻辑
- 集成 OpenSSH Server，支持密码和公钥认证
- 集成 Jupyter Notebook/Lab，支持 Token/Password 认证
- 通过 supervisord 管理 sshd 和 jupyter 双服务，支持自动重启
- 中文环境支持（zh_CN.UTF-8 locale, Asia/Shanghai 时区）
- 提供 README.md 文档说明构建、运行和使用方法
- 支持健康检查（同时检测 sshd 和 jupyter 状态）

## Non-Goals (Out of Scope)
- 不修改现有的 `pycaffe/Dockerfile` 或其目录内容
- 不引入 GPU/CUDA 支持（保持 CPU-only 与现有 pycaffe 一致）
- 不修改 `apps/jupyter-ssh-base/` 中的任何文件（只读复用）
- 不重构 pycaffe 的多阶段构建流程
- 不添加额外的 ML 框架（如 PyTorch、TensorFlow）
- 不创建 docker-compose.yml（保持与现有 pycaffe 结构一致，仅提供 Dockerfile）

## Background & Context
- 现有 `pycaffe/Dockerfile` 使用 4 阶段构建（base-system → base-builder → pycaffe-builder → runtime），最终 runtime 镜像已安装 PyCaffe wheel 和所有科学计算依赖，但仅提供 bash shell，无远程访问能力。
- `apps/jupyter-ssh-base/` 是一个成熟的 SSH + Jupyter 基础镜像项目，包含：
  - 多阶段构建优化（builder/runtime 分离）
  - supervisord 双进程管理配置
  - 完整的 entrypoint.sh 启动脚本（密码设置、host key 生成、Jupyter 动态配置）
  - sshd 安全配置（ED25519 优先、禁用 root 登录）
  - Jupyter 配置文件
  - 健康检查脚本
- pycaffe 的 runtime 使用系统 Python（非 venv），通过 `--break-system-packages` 安装包；用户为 `builder`（UID 1000），工作目录 `/workspace`。
- jupyter-ssh-base 使用 Python venv（`/opt/venv`），用户为 `jupyteruser`（UID 1000），工作目录 `/workspace`。
- 两者都基于 `ubuntu:26.04`，工作目录都是 `/workspace`，默认 UID 都是 1000，这为集成提供了良好基础。

## Functional Requirements
- **FR-1**: 创建目录 `projects/xuanspace/vendor/caffe/docker/standalone/pycaffe-jupyter-ssh/`
- **FR-2**: 创建新的 Dockerfile，在 pycaffe runtime 基础上添加 SSH + Jupyter 服务层
- **FR-3**: 在新目录下创建 `config/` 子目录，包含从 jupyter-ssh-base 适配的配置文件
  - supervisord.conf
  - sshd_config
  - jupyter_notebook_config.py
  - supervisor/conf.d/sshd.conf
  - supervisor/conf.d/jupyter.conf
- **FR-4**: 创建 `entrypoint.sh`，复用 jupyter-ssh-base 的启动逻辑，适配 pycaffe 用户环境
- **FR-5**: 创建 `scripts/healthcheck.sh`，复用 jupyter-ssh-base 的健康检查逻辑
- **FR-6**: 安装必要的运行时系统包：openssh-server, supervisor, tini, pwgen, locales, curl, procps 等
- **FR-7**: 安装 Jupyter 相关 Python 包到系统 Python 环境（notebook, jupyterlab, ipykernel, nbconvert, jupyter_server）
- **FR-8**: 创建/统一非 root 用户（UID 1000），确保与 pycaffe 已有 builder 用户兼容
- **FR-9**: 配置中文环境（zh_CN.UTF-8 locale, Asia/Shanghai 时区）
- **FR-10**: 配置 SSH 服务：默认端口 22，ED25519 密钥优先，禁用 root 登录（可配置），支持密码和公钥认证
- **FR-11**: 配置 Jupyter 服务：默认端口 8888，监听 0.0.0.0，工作目录 /workspace，非 root 运行
- **FR-12**: 集成 supervisord 管理双服务，配置自动重启策略
- **FR-13**: 环境变量支持：USER_PASSWORD, JUPYTER_TOKEN, JUPYTER_PASSWORD, ALLOW_ROOT_SSH, GRANT_SUDO, SSH_PUBLIC_KEY 等
- **FR-14**: 创建 README.md，说明目录结构、构建命令、运行方法、环境变量配置、验证步骤
- **FR-15**: 保留 pycaffe 原有的验证脚本（verify-pycaffe.sh, verify-parity.sh）的可用性
- **FR-16**: 构建上下文仍为 `vendor/` 目录（与 pycaffe 一致），确保能访问 caffe-slim/ 和 tvm-ffi/

## Non-Functional Requirements
- **NFR-1**: 镜像构建成功率：Dockerfile 应能无错误构建完成（docker build 返回 0）
- **NFR-2**: 镜像大小合理：在 pycaffe runtime 基础上增量不超过 500MB
- **NFR-3**: 服务启动时间：容器启动后 30 秒内 sshd 和 jupyter 均应可访问
- **NFR-4**: 构建日志清晰：关键步骤使用 `[BUILD]` 前缀输出日志（遵循 jupyter-ssh-base 风格）
- **NFR-5**: 幂等性：重复构建应产生一致的结果（不依赖网络随机性，除 apt/pip 包版本更新外）
- **NFR-6**: 安全性：不在 Dockerfile 中硬编码密码/密钥；SSH host keys 在容器启动时动态生成；默认禁用 root SSH 登录
- **NFR-7**: 可维护性：Dockerfile 注释清晰，阶段命名明确；配置文件与 jupyter-ssh-base 保持结构一致便于对比和升级
- **NFR-8**: 兼容性：Jupyter kernel 能正常 import pycaffe 和所有已安装的科学计算包

## Constraints
- **Technical**:
  - 基础镜像固定为 pycaffe runtime（ubuntu:26.04 衍生）
  - 构建上下文必须是 `vendor/` 目录（以访问 caffe/caffe-slim/ 和 tvm-ffi/）
  - Python 包安装使用 `--break-system-packages`（与 pycaffe 保持一致，不使用 venv）
  - 必须复用 jupyter-ssh-base 的配置资源（不重复发明轮子）
- **Business**:
  - 新目录命名为 `pycaffe-jupyter-ssh/`（清晰表达功能：pycaffe + jupyter + ssh）
  - 不修改 vendor/caffe/ 外的任何文件（除了 .trae/specs/ 下的规划文档）
- **Dependencies**:
  - Docker 构建环境（用户本地）
  - 网络访问（apt 和 pip 包下载）
  - 现有 pycaffe/Dockerfile 的构建阶段作为基础

## Assumptions
- pycaffe 的 base-builder/runtime 阶段中，builder 用户的 UID 为 1000，HOME 目录需要检查（当前 Dockerfile 中未显式设置 /home/builder，但 useradd -m 会创建）
- 直接在系统 Python 中安装 Jupyter 包不会与 pycaffe 已有的科学计算包产生版本冲突
- supervisord 在 ubuntu:26.04 上的包名为 `supervisor`（已在 jupyter-ssh-base 中验证）
- 用户构建时使用与 pycaffe 相同的命令格式：`cd vendor && docker build -t <tag> -f caffe/docker/standalone/pycaffe-jupyter-ssh/Dockerfile .`
- jupyter-ssh-base 配置文件中的用户路径（/home/jupyteruser）需要适配为 pycaffe 的实际用户 HOME 路径

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 任务完成
- **When**: 列出 `projects/xuanspace/vendor/caffe/docker/standalone/pycaffe-jupyter-ssh/` 目录
- **Then**: 目录包含 Dockerfile、entrypoint.sh、README.md、config/ 子目录（含 supervisord.conf, sshd_config, jupyter_notebook_config.py, supervisor/conf.d/）、scripts/ 子目录（含 healthcheck.sh）
- **Verification**: `programmatic`
- **Notes**: 使用 LS 或 dir 命令验证

### AC-2: Dockerfile 语法正确
- **Given**: Dockerfile 已创建
- **When**: 运行 `docker build` 从 vendor/ 目录构建，目标 runtime 阶段
- **Then**: 构建成功完成，无语法错误，最终镜像生成
- **Verification**: `programmatic`

### AC-3: PyCaffe 在新镜像中可正常导入
- **Given**: 镜像构建成功
- **When**: 运行 `docker run --rm <image> python -c "import pycaffe; print(pycaffe.__version__)"`
- **Then**: 成功输出 pycaffe 版本号，无 ImportError
- **Verification**: `programmatic`

### AC-4: SSH 服务正常运行
- **Given**: 容器以守护模式启动（`-p 2222:22`），设置了 USER_PASSWORD
- **When**: 等待 30 秒后，尝试 SSH 连接 `ssh -p 2222 builder@localhost`（或配置的用户）
- **Then**: SSH 连接成功，可以登录并执行命令
- **Verification**: `programmatic`

### AC-5: Jupyter 服务正常运行
- **Given**: 容器以守护模式启动（`-p 8888:8888`），设置了 JUPYTER_TOKEN
- **When**: 等待 30 秒后，curl 访问 `http://localhost:8888/api`
- **Then**: HTTP 响应码为 200/302/401/403（表示服务在运行），使用 token 可正常访问 Notebook
- **Verification**: `programmatic`

### AC-6: Supervisord 管理双服务
- **Given**: 容器运行中
- **When**: 在容器内执行 `supervisorctl status`
- **Then**: 显示 sshd 和 jupyter 两个服务均为 RUNNING 状态
- **Verification**: `programmatic`

### AC-7: 健康检查通过
- **Given**: 容器运行中，服务已就绪
- **When**: 执行容器内的 healthcheck.sh 脚本
- **Then**: 输出 STATUS: HEALTHY，sshd 和 jupyter 端口检测均 OK
- **Verification**: `programmatic`

### AC-8: Jupyter 中可使用 PyCaffe
- **Given**: Jupyter 服务正常运行
- **When**: 在 Jupyter Notebook 中执行 `import pycaffe; import numpy; import scipy; import matplotlib`
- **Then**: 所有包导入成功，无错误
- **Verification**: `programmatic`

### AC-9: 环境变量配置生效
- **Given**: 启动容器时传入 `USER_PASSWORD=mypass` 和 `JUPYTER_TOKEN=mytoken`
- **When**: 使用指定密码 SSH 登录，使用指定 token 访问 Jupyter
- **Then**: 使用 mypass 可以 SSH 登录成功，使用 mytoken 可以通过 Jupyter 认证
- **Verification**: `programmatic`

### AC-10: 中文环境配置正确
- **Given**: 容器运行中
- **When**: 在容器内执行 `echo $LANG` 和 `date`
- **Then**: LANG 为 zh_CN.UTF-8，时区为 Asia/Shanghai（CST 时区）
- **Verification**: `programmatic`

### AC-11: 调试模式支持
- **Given**: 使用 `docker run -it --rm <image> bash` 启动
- **When**: 容器启动
- **Then**: 直接进入 bash shell，不启动 supervisord 服务（命令模式）
- **Verification**: `human-judgment`

### AC-12: README 文档完整
- **Given**: README.md 已创建
- **When**: 阅读 README.md
- **Then**: 包含：项目说明、目录结构、构建命令、运行示例（SSH/Jupyter 访问）、环境变量列表、验证步骤
- **Verification**: `human-judgment`
- **Notes**: 文档质量需清晰、可操作、与现有 pycaffe README 风格一致

### AC-13: 复用 jupyter-ssh-base 资源
- **Given**: 配置文件已创建
- **When**: 对比新目录 config/ 下的文件与 apps/jupyter-ssh-base/config/ 下的文件
- **Then**: 核心配置（sshd 安全选项、supervisord 进程管理、Jupyter 基础配置）保持一致，仅用户路径等必要适配有差异
- **Verification**: `human-judgment`

## Open Questions
- [ ] 用户命名：保持 pycaffe 的 `builder` 用户名，还是统一为 jupyter-ssh-base 的 `jupyteruser`？（建议保持 `builder` 以兼容 pycaffe 已有文件权限，但 HOME 路径需确认）
- [ ] 是否需要保留 pycaffe 原有的 HEALTHCHECK（检测 pycaffe import），还是替换为新的双服务健康检查？（建议替换为更全面的双服务健康检查）
- [ ] 是否需要在新目录下复制 verify-pycaffe.sh 和 verify-parity.sh 脚本，还是通过 Dockerfile COPY 引用原 pycaffe/scripts/ 下的脚本？（建议直接引用原路径，避免重复）
