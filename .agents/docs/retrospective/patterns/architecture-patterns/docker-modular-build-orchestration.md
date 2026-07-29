---
id: "docker-modular-build-orchestration"
version: "1.0"
source: "external/chaos/caffe/docker/modules/ 学习沉淀"
---
# Docker 模块化构建编排架构

> 来源：BVLC Caffe 项目的 Docker 模块化构建系统（`external/chaos/caffe/docker/modules/`）
>
> 成熟度：L2（已验证 — 成功构建 3 个镜像目标，含完整验证流水线）

## 概述

将 Docker 多镜像构建定义为 CMake 目标，实现依赖管理、构建上下文组装、验证嵌入式构建、一键运行脚本的四层编排架构。适用于需要同时维护多个 Docker 镜像（基础镜像 + 派生镜像 + 开发镜像）的项目。

## 架构分层

```
┌─────────────────────────────────────────────────────────┐
│ Layer 4: 一键运行脚本 (run-jupyter.sh)                     │
│   9 个子命令：build/run/stop/shell/ssh/logs/verify/clean/  │
│   rebuild/info，用户友好 CLI                               │
├─────────────────────────────────────────────────────────┤
│ Layer 3: CMake 构建编排 (CMakeLists.txt)                   │
│   define_docker_target() 辅助函数，依赖链，验证命令          │
├─────────────────────────────────────────────────────────┤
│ Layer 2: 独立构建上下文 (prepare-pycaffe-context.sh)       │
│   组装源码 + 配置 + 脚本 + Dockerfile + .dockerignore       │
├─────────────────────────────────────────────────────────┤
│ Layer 1: Docker 多阶段构建 (Dockerfile)                    │
│   builder → runtime → jupyter-runtime 三阶段               │
└─────────────────────────────────────────────────────────┘
```

## 核心模式

### 模式 1：CMake 定义 Docker 构建目标

**问题**：多个 Docker 镜像之间存在依赖关系（如 `pycaffe-jupyter` 依赖 `pycaffe` 的构建上下文），直接用 shell 脚本管理构建顺序容易出错。

**方案**：用 CMake 的 `add_custom_target` 将每个 Docker 镜像定义为构建目标，通过 `define_docker_target()` 辅助函数统一管理。

```cmake
function(define_docker_target TARGET_NAME)
    # 参数：IMAGE DOCKERFILE TARGET_STAGE CONTEXT_DIR DEPENDS VERIFY_COMMANDS
    # 生成独立的 shell 脚本避免 Makefile 多行转义问题
    # 每个目标自动生成 build/verify 脚本
endfunction()

# 使用示例
define_docker_target(pycaffe-jupyter
    IMAGE "caffe-cpu:pycaffe-jupyter"
    DOCKERFILE "${PYCAFFE_CONTEXT_DIR}/Dockerfile"
    TARGET_STAGE "jupyter-runtime"
    DEPENDS prepare-pycaffe-context
    VERIFY_COMMANDS
        "docker run -d --name verify ... ${IMAGE}"
        "sleep 8"
        "docker exec verify verify-jupyter.sh"
        "docker rm -f verify"
)
```

**关键决策**：
- 辅助函数生成独立 shell 脚本而非内联 CMake 命令，避免 Makefile 中的多行转义和引号嵌套问题
- 验证命令作为构建步骤的一部分，构建失败即验证失败
- 开发镜像（`pycaffe-jupyter`）不加入默认 `docker-all` 目标，需要手动指定

**何时使用**：项目包含 2 个以上相互依赖的 Docker 镜像，需要自动化构建和验证。

**何时不用**：单镜像项目，直接用 `docker build` 或 `docker compose` 更简单。

---

### 模式 2：独立构建上下文组装

**问题**：Docker 构建需要从项目不同位置收集文件（源码、配置、脚本），`docker build` 的 context 限制为单一目录，导致需要将整个项目作为 context（浪费带宽）或使用复杂的 `.dockerignore`。

**方案**：构建前用脚本将所需文件复制到一个独立目录，同时生成精确的 `.dockerignore`，以该目录作为 Docker 构建上下文。

```bash
# prepare-pycaffe-context.sh 核心逻辑
CTX="build/docker-context/pycaffe"   # 独立上下文目录
rm -rf "$CTX"
mkdir -p "$CTX/ffi" "$CTX/scripts" "$CTX/config"

cp -a project/python   "$CTX/python"          # 源码
cp -a project/ffi/     "$CTX/ffi/tvm-ffi"     # FFI 依赖
cp -a modules/config/  "$CTX/config/"         # 服务配置
cp modules/scripts/*   "$CTX/scripts/"        # 启动脚本
cp modules/Dockerfile  "$CTX/Dockerfile"      # 构建文件

# 生成精确的 .dockerignore
cat > "$CTX/.dockerignore" << 'EOF'
**/__pycache__
**/tests
**/.git
**/build
EOF
```

**关键决策**：
- 上下文目录放在 `build/` 下（CMake 构建产物区），便于清理
- `.dockerignore` 动态生成，精确控制哪些文件进入 context
- 文件计数输出（`$PYCOUNT files`）提供可审计的构建上下文信息

**何时使用**：Docker 构建需要从多个不相关目录收集文件，或需要严格控制构建上下文大小。

**何时不用**：所有文件已在同一目录下，标准的 `docker build .` 即可。

---

### 模式 3：验证嵌入式构建流水线

**问题**：Docker 镜像构建成功不代表功能正确，需要运行时验证，但传统 CI 将验证步骤放在构建之后，反馈周期长。

**方案**：在 CMake 构建目标中嵌入验证命令，使验证成为构建步骤的一部分。验证失败即构建失败，实现快速反馈。

```cmake
define_docker_target(pycaffe
    VERIFY_COMMANDS
        "docker run --rm ${IMAGE} verify-pycaffe.sh"
)

define_docker_target(pycaffe-jupyter
    VERIFY_COMMANDS
        # 启动容器 → 等待服务就绪 → 运行验证 → 清理
        "docker run -d --name verify -p 2222:22 -p 8888:8888 ${IMAGE}"
        "sleep 8"
        "docker exec verify verify-jupyter.sh || (docker logs verify; docker rm -f verify; exit 1)"
        "docker rm -f verify"
)
```

**验证脚本设计**（[verify-jupyter.sh](file:///d:/spaces/SpecWeave/external/chaos/caffe/docker/modules/pycaffe-jupyter/scripts/verify-jupyter.sh)）：
- 10 项检查：pycaffe 导入、supervisord 进程、sshd 进程/端口、Jupyter 进程/端口、SSH 配置、Jupyter 配置、/workspace 权限、脚本完整性
- PASS/FAIL/SKIP 计数 + 彩色输出
- 非零退出码表示验证失败

**关键决策**：
- 验证容器使用后自动清理（`docker rm -f`）
- 失败时输出容器日志辅助排查（`docker logs verify`）
- slim 构建跳过不适用检查（如 LeNet 前向传播、Solver 类）

**何时使用**：镜像功能复杂，需要在构建阶段确认服务可用性。

---

### 模式 4：一键运行脚本（多子命令 CLI）

**问题**：用户需要记忆多个命令来构建、运行、调试 Docker 容器，容易出错。

**方案**：提供单一入口脚本，支持 9 个标准子命令，通过 `--option` 参数自定义配置。

**子命令设计**：

| 命令 | 功能 | 典型场景 |
|------|------|---------|
| `build` | 构建镜像 | 首次部署 |
| `run` | 构建 + 启动容器 | 日常使用 |
| `stop` | 停止容器 | 暂停服务 |
| `shell` | 进入容器 bash | 调试 |
| `ssh` | SSH 连接 | 远程开发 |
| `logs` | 查看容器日志 | 排查问题 |
| `verify` | 运行验证脚本 | 确认服务正常 |
| `clean` | 删除容器和镜像 | 彻底清理 |
| `rebuild` | 清理 + 无缓存重建 | 依赖更新后 |
| `info` | 显示访问信息 | 查看 URL/密码 |

**关键设计决策**（[run-jupyter.sh](file:///d:/spaces/SpecWeave/external/chaos/caffe/docker/modules/scripts/run-jupyter.sh)）：
- 密码优先级：`--password` > `JUPYTER_PASSWORD` 环境变量 > 默认 `caffe`
- SSH 公钥自动检测：`~/.ssh/id_rsa.pub` → `~/.ssh/id_ed25519.pub`，支持 `--no-ssh-key` 禁用
- 彩色输出：GREEN=[OK], RED=[ERROR], YELLOW=[WARN], CYAN=步骤, MAGENTA=INFO
- `--no-build` 选项跳过构建（镜像已存在时加速启动）
- 容器状态检测：运行中/已停止/不存在，不同状态不同处理

**何时使用**：Docker 容器需要频繁构建、启动、调试，面向非 Docker 专家的用户。

**何时不用**：一次性部署场景，直接用 `docker compose up -d` 更简单。

---

## 与 jupyter-ssh-base 的对比

| 维度 | caffe docker/modules | jupyter-ssh-base |
|------|---------------------|-----------------|
| 构建编排 | CMake 目标 + 依赖管理 | docker compose + build.sh |
| 配置管理 | 构建时静态配置（generate-jupyter-config.py） | 运行时动态配置（entrypoint.sh + 环境变量） |
| 密钥管理 | 构建时预置密码 | 运行时生成随机密钥 |
| 验证 | 构建时嵌入式验证 | 构建后 healthcheck-test.sh |
| 用户入口 | run-jupyter.sh（9 子命令） | README + docker compose |
| SSH 公钥 | 自动检测 host 公钥 | SSH_PUBLIC_KEY 环境变量 |

## 可迁移到 jupyter-ssh-base 的改进点

1. **一键运行脚本**：参考 `run-jupyter.sh` 为 jupyter-ssh-base 创建 `run.sh`（build/run/stop/shell/ssh/logs/verify/clean/info）
2. **SSH 公钥自动检测**：entrypoint.sh 支持从 host 自动检测 `~/.ssh/id_*.pub`
3. **验证嵌入式构建**：构建步骤中嵌入 `healthcheck-test.sh` 验证
4. **独立构建上下文**：当需要打包额外文件时，可用 prepare-context 模式

## 反模式警示

- **不要**在 CMake 中直接内联多行 Docker 命令 — 转义和引号嵌套极易出错，使用辅助函数生成独立脚本
- **不要**将所有镜像都加入默认构建目标 — 开发镜像（含 Jupyter/SSH）应作为可选目标
- **不要**在验证脚本中 hardcode 密码 — 使用环境变量，参照 [env-var-five-layer-protection.md](file:///d:/spaces/SpecWeave/.agents/docs/retrospective/patterns/code-patterns/env-var-five-layer-protection.md)