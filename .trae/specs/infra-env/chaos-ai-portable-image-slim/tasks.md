# Chaos AI Portable 镜像多阶段构建瘦身 - Tasks

## [x] Task 1: 多阶段重构 portable.Dockerfile
- **Priority**: high
- **Depends On**: None
- **Description**: 将 [portable.Dockerfile](file:///d:/spaces/SpecWeave/external/chaos/ai/portable.Dockerfile) 从单阶段重构为 `base` → `deps` → `final` 三阶段：
  - **base 阶段**：`FROM devcontainer-base:onnx-quantized-latest`，保留 ENV/ARG/SHELL，创建 ai 用户（usermod devuser→ai，UID 不变）+ 目录 + sudo + 密码
  - **deps 阶段**：`FROM base`，root 身份安装全部 pip 包（保留现有包列表），清理 conda/pip 缓存
  - **final 阶段**：`FROM deps`，COPY 配置/脚本 + 配置运行时 + 元数据 + 验证
- **关键改动**：在 base 阶段删除 `chown -R ai:${AI_GROUP} "${CONDA_DIR}"`（[原 L133](file:///d:/spaces/SpecWeave/external/chaos/ai/portable.Dockerfile#L133-L133)），conda 保持 root:root
- **关键修复**（PIP_USER）：deps 阶段设置 `ENV PIP_USER=0` 使构建期包写入 `/opt/conda`（root 属主、全局可读），final 阶段恢复 `ENV PIP_USER=1` 支持运行时 `pip install --user`。修复了构建期包误入 `/root/.local` 导致 ai 用户无法 import 的问题
- **Acceptance**: 三阶段构建成功，`docker images chaos-ai:portable` ≤ ~10GB（实测 9.59GB）

## [x] Task 2: 验证 ai 用户 sudo 安装包
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 构建后验证 ai 用户可通过 sudo 在 conda base 安装包：
  - `sudo -u ai bash -c 'sudo pip install numpy'` 可写入 /opt/conda
  - `sudo -u ai python -c "import numpy"` 可用
  - 验证 `pip install --user`（~/.local user site）作为替代方案也可用
- **Acceptance**: ai 用户无需 conda 写权限即可安装包（实测 `sudo pip install flask` 成功，`pip install --user six` 成功）

## [x] Task 3: 验证服务与运行时一致性
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 验证删 chown 后 sshd/dockerd/jupyter 三服务正常：
  - 容器启动 healthy，supervisord 正常
  - jupyter 内 `!pip install` 通过 sudo 可用
  - SSH 登录 ai 用户正常
- **Acceptance**: 三服务正常（实测 sshd/dockerd/jupyter 均 RUNNING），ai 用户可 import deps 阶段全部包，jupyter 以 ai 用户运行于 /opt/conda

## [x] Task 4: 更新安装文档为 sudo 方式
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 更新 [conda-environment-guide.md](file:///d:/spaces/SpecWeave/external/chaos/ai/docs/portable/conda-environment-guide.md) 与 start.sh 提示，说明 conda 属主为 root、ai 需用 `sudo pip install` / `sudo pip install --user`
- **Acceptance**: 文档与实际行为一致（已更新 guide + verify-startup.sh + .env.example 的 py314→base）

## [x] Task 5: 端到端验证镜像缩小
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**: 完整验证：
  - 记录缩小前后镜像大小对比（期望 15.6GB → ≤10GB）
  - 验证 core 功能（torch/onnx/LLVM/CMake/Ninja 可用）
  - 对比旧镜像 `docker images` 大小
- **Acceptance**: 镜像缩小 ≥35%（实测 15.6GB → 9.59GB，降幅 38.5%），核心功能无损

## [x] Task 6: compose 指向 + 缓存保存 + 启动验证
- **Priority**: high
- **Depends On**: Task 1, Task 5
- **Description**: 收尾三件套：
  - [docker-compose.yml](file:///d:/spaces/SpecWeave/external/chaos/ai/docker-compose.yml) 的 `dev-portable` 服务 `image:` 从 `chaos-ai:portable` 改为 `chaos-ai:portable-slim`，并同步 WSL 构建目录
  - 通过 docker-cache skill 执行 `save chaos-ai:portable-slim`，缓存为 2.0GB tar.gz（原子写入 + SHA256 校验）
  - `docker compose up -d dev-portable` 重建容器，验证新镜像正常工作
- **Acceptance**:
  - 镜像 ID `sha256:65cedded9cd07` 已缓存，`list` 状态 `✅ Docker`
  - 容器 healthy，sshd/dockerd/jupyter 三服务 RUNNING
  - 宿主机 2222(SSH) + 8888(Jupyter) 端口映射可达
  - ai 用户可 import 全部 deps 阶段包（transformers/jupyterlab/nuitka）

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 1
- Task 4 依赖 Task 2
- Task 5 依赖 Task 2, Task 3
- Task 6 依赖 Task 1, Task 5