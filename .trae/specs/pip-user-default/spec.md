# Docker 默认 pip install 用户级安装 - 产品需求文档

## Overview
- **Summary**: 为 chaos-ai-npu 开发容器配置 `PIP_USER=1` 环境变量，使 devuser（Jupyter/SSH 用户）直接执行 `pip install` 时默认安装到用户目录（`~/.local/`），无需手动添加 `--user` 或 `sudo`。同时确保 root 运行的 bootstrap 脚本仍能将包装到系统 conda 环境。
- **Purpose**: 解决从 Jupyter Notebook 中执行 `!pip install <pkg>` 因 /opt/conda 目录归 root 所有而权限拒绝的问题，提升开发者体验。
- **Target Users**: 在 Jupyter Notebook 或 SSH 会话中使用 devuser 安装 Python 包的开发者。

## 分析结论：为何当前设计如此

### 事实

| 事实 | 证据 |
|------|------|
| /opt/conda 归 root:root，权限 755 | 容器内 `stat -c '%U:%G %a' /opt/conda` 输出 `root:root 755` |
| devuser 不能直接写 /opt/conda 或 /opt/venv | `test -w /opt/conda/bin` 返回 NO |
| devuser 有 NOPASSWD sudo | `sudo -l -U devuser` 显示 `(ALL) NOPASSWD: ALL` |
| Jupyter kernel 以 devuser 运行 | `ps aux` 显示 ipykernel 进程属主为 devuser |
| PIP_USER 未设置 | 容器内 `echo $PIP_USER` 为空 |
| ENABLE_USER_SITE=True | Python site 模块确认用户 site-packages 可用 |
| 用户 site-packages 路径 | `/home/devuser/.local/lib/python3.14/site-packages` |
| 容器主进程以 root 运行 | PID 1 supervisord 属主为 root |
| bootstrap 以 root 运行 pip install | container-bootstrap.sh 由 entrypoint 调用，运行身份为 root |

### 权限设置的设计意图

1. **root 拥有 /opt/conda**：保证镜像声明状态可复现。如果 devuser 能直接修改系统 conda，容器重建后修改丢失，造成"在我机器上能跑"的漂移问题。
2. **[Dockerfile:173](file:///d:/spaces/SpecWeave/external/chaos/ai/Dockerfile#L173) `chmod a+x`**：pip 在 Docker BuildKit 中安装脚本时偶尔丢失可执行位（umask 问题），此行确保所有 /opt/conda/bin 下的可执行文件对所有用户可执行。这是**放宽权限**而非限制。
3. **[Dockerfile:206](file:///d:/spaces/SpecWeave/external/chaos/ai/Dockerfile#L206) `chown devuser`**：构建时 root 创建的挂载点目录默认归 root，此行将 /workspace/npu_tvm 等目录交给 devuser，使其可写。这也是**放宽权限**。

### 用户当前已有的三种包安装方式

| 方式 | 命令 | 安装位置 | 是否需要 sudo |
|------|------|----------|--------------|
| 用户级安装 | `pip install --user <pkg>` | `~/.local/lib/...` | 否 |
| 系统级安装 | `sudo pip install <pkg>` | `/opt/conda/lib/...` | 是（NOPASSWD） |
| 独立 conda 环境 | `conda create -n myenv && conda activate myenv` | `~/.conda/envs/...` | 否 |

**实际问题**：用户从 Jupyter 执行 `!pip install <pkg>`（不带 `--user`）时，pip 默认尝试写入 root 拥有的 /opt/conda，导致 `PermissionError`。用户需要知道加 `--user` 或 `sudo`，这是不必要的认知负担。

## Goals
- 让 devuser 在 Jupyter/SSH 中执行 `pip install <pkg>` 开箱即用，无需 `--user` 或 `sudo`
- 不影响 root（bootstrap 脚本）将包装到系统 conda 环境的能力
- 不改变 Dockerfile 构建时的包安装行为
- 保持系统 conda 环境的 root 所有权和镜像可复现性

## Non-Goals (Out of Scope)
- 不修改 /opt/conda 的所有权或权限（保持 root:root 755）
- 不移除 devuser 的 sudo 权限
- 不修改 conda 的配置或频道设置
- 不修改 Dockerfile 的构建流程和 Stage 结构
- 不引入 virtualenv 或 conda 环境管理工具

## Functional Requirements
- **FR-1**: devuser 在 Jupyter Notebook 中执行 `!pip install <pkg>` 时，包默认安装到 `/home/devuser/.local/`，不报错
- **FR-2**: root 运行 `pip install <pkg>`（bootstrap 脚本）时，包仍安装到 `/opt/conda/`，不被 PIP_USER 重定向到 /root/.local/
- **FR-3**: Dockerfile 构建阶段（Stage 2）的 pip install 不受影响，包装入镜像层
- **FR-4**: SSH 登录 devuser 后，`pip install` 行为与 Jupyter 中一致

## Non-Functional Requirements
- **NFR-1**: 零额外运行时开销（环境变量配置，无后台进程）
- **NFR-2**: 不增加镜像体积
- **NFR-3**: 不引入新的依赖包

## Constraints
- **技术**: Docker Compose 通过 `command` 调用 container-bootstrap.sh，后者以 root 身份运行；Jupyter kernel 以 devuser 运行
- **依赖**: 容器已有 `/home/devuser/.local/` 目录且 devuser 可写

## Assumptions
- `PIP_USER=1` 对 root 用户的 pip 行为可通过在 bootstrap 脚本中设置 `PIP_USER=0` 覆盖
- Dockerfile 构建阶段不继承运行时的 docker-compose.yml environment 配置
- 用户级安装的包优先级高于系统级包（Python site 模块默认行为：user site 在 system site 之前）

## Acceptance Criteria

### AC-1: devuser pip install 开箱即用
- **Given**: devuser 登录 Jupyter 或 SSH
- **When**: 执行 `pip install <some-package>`（不带 --user 或 sudo）
- **Then**: 包成功安装到 `/home/devuser/.local/lib/python3.14/site-packages/`，无 PermissionError
- **Verification**: `programmatic`

### AC-2: bootstrap 系统级安装不受影响
- **Given**: 容器启动时 container-bootstrap.sh 以 root 运行
- **When**: bootstrap 检测到缺失的 Python 包并执行 pip install
- **Then**: 包安装到 `/opt/conda/lib/python3.14/site-packages/`，所有用户（含 devuser）均可 import
- **Verification**: `programmatic`

### AC-3: Dockerfile 构建不受影响
- **Given**: Docker 镜像构建过程中 Stage 2 执行 pip install
- **When**: 构建 chaos-ai-npu variant 镜像
- **Then**: scikit-build-core、nuitka 等包装入 /opt/conda，镜像层正常生成
- **Verification**: `programmatic`

### AC-4: sudo pip install 仍可系统级安装
- **Given**: devuser 需要安装系统级包
- **When**: 执行 `sudo pip install <pkg>`
- **Then**: 包安装到 /opt/conda（sudo 重置环境变量，PIP_USER=1 不传递给 root shell）
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要同时为 /opt/venv（Jupyter 运行环境）配置 PIP_USER？当前 Jupyter server 使用 /opt/venv/bin/python，但 kernel 使用 /opt/conda/bin/python，需确认用户主要在哪侧安装包。
