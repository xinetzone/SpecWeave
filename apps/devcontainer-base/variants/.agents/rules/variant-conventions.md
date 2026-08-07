---
id: "variants-shared-conventions"
title: "变体 Dockerfile 共享约定"
source: "variants/conda/Dockerfile, variants/conda-llvm/Dockerfile, variants/_template/Dockerfile"
---
# 变体 Dockerfile 共享约定

本文件定义**所有镜像变体**必须遵循的 Dockerfile 约定。每个变体的 `.agents/rules/dockerfile.md` 在此基础上定义变体特有规则。

## FROM 模式

### 基础语法

所有变体 Dockerfile 必须首行声明 BuildKit 语法：
```dockerfile
# syntax=docker/dockerfile:1.7-labs
```

### FROM 继承模式

根据依赖关系选择 FROM 语句：

| 依赖类型 | FROM 语句 | 示例 |
|---------|----------|------|
| 直接基于基础镜像 | `FROM devcontainer-base:${BASE_TAG}` | conda 变体 |
| 基于其他变体 | `FROM devcontainer-base:<dep>-${BASE_TAG}` | conda-llvm 基于 conda |

`BASE_TAG` 通过构建参数 `--build-arg BASE_TAG=<tag>` 传入，默认 `latest`。

### SHELL 指令重置

**⚠️ FROM 会重置 SHELL 指令**。变体 Dockerfile 必须在 FROM 之后显式重新声明：
```dockerfile
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]
```

## 禁止覆盖的基础镜像设置

以下指令由基础镜像设置，**变体 Dockerfile 中不得重新定义**：

| 指令 | 基础镜像值 | 原因 |
|------|----------|------|
| `ENTRYPOINT` | `["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]` | 保持启动流程一致性 |
| `CMD` | `[]` | 由 entrypoint.sh 决定默认行为 |
| `WORKDIR` | `/workspace` | 统一工作目录 |
| `EXPOSE` | 22, 2375, 8888 | 服务端口声明 |
| `VOLUME` | `/var/lib/docker` | DinD 存储 |

### USER 指令

- 构建过程中默认以 root 执行（基础镜像的 USER 在 FROM 后不自动切换回 root，但 build stage 默认 root）
- 最终镜像不设置 USER（保持基础镜像的 USER 行为）
- 如需切换非 root 用户执行特定操作，操作后必须切回 root（因为后续层可能需要 root）

### 变体可以设置的

- `ARG`：构建参数
- `ENV`：新增环境变量（但不得覆盖基础镜像已有的关键变量如 PATH）
- `LABEL`：元数据标签
- `RUN`：安装软件、配置
- `COPY`：复制文件
- 追加 `ENV PATH`（使用 `${PATH}:` 前置新路径，注意优先级）

## PATH 优先级规则

### 核心原则

变体追加新工具路径时，必须考虑 PATH 优先级：

1. **系统服务优先**：`/opt/venv/bin`（基础镜像 Python 虚拟环境）必须保持在高优先级
2. **变体工具追加**：新增工具路径使用 `ENV PATH="/opt/conda/bin:${PATH}"` 前置（确保 conda 工具在 conda 环境中可用，但不覆盖系统 venv 的 python）
3. **禁止覆盖**：不得使用 `ENV PATH=/some/path` 覆盖式设置，必须使用 `${PATH}` 追加

### 特殊处理：Conda

Conda 变体遵循"不自动激活"原则：
- `/opt/conda/bin` 前置到 PATH（让 conda 命令可用）
- 但设置 `auto_activate_base: false`，不自动激活 base 环境
- 用户需手动 `source /etc/profile.d/conda-init.sh && conda activate base`
- 默认 `python` 仍指向 `/opt/venv/bin/python`

## 构建阶段结构

每个变体 Dockerfile 应采用追加层模式，在基础镜像之上添加功能。建议结构：

```dockerfile
# syntax=docker/dockerfile:1.7-labs
ARG BASE_TAG=latest
FROM devcontainer-base:<base-prefix>${BASE_TAG}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

ARG APT_MIRROR=official
ARG CONDA_MIRROR=official
ARG PIP_MIRROR=official

# Stage 1/N: 前置检查 + 系统依赖（如有需要）
# Stage 2/N: 核心软件安装（conda install/APT/pip等）
# Stage 3/N: 配置（镜像源、配置文件、激活脚本）
# Stage 4/N: 权限 + PATH 配置
# Stage 5/N: 构建元数据 + 清理 + [VALIDATION CHECKPOINT]
```

每个阶段必须：
1. 计时开始时输出 `[TIMER] Stage X/N: <desc> started at <timestamp>`
2. 阶段结束时输出 `[TIMER] Stage X/N: <desc> took <N>s`
3. 关键步骤有动作标记

## 缓存挂载规范

使用 BuildKit 缓存挂载加速重复构建：

| 缓存类型 | 挂载路径 | 共享模式 |
|---------|---------|---------|
| APT 缓存 | `/var/cache/apt` | `locked` |
| APT 列表 | `/var/lib/apt/lists` | `locked` |
| Conda 包缓存 | `/opt/conda/pkgs` | `locked` |
| pip 缓存 | `/root/.cache/pip` | `locked` |

**语法**：
```dockerfile
RUN --mount=type=cache,target=<path>,sharing=locked \
    <install-command>
```

⚠️ 缓存挂载必须配合 `rm -rf /var/lib/apt/lists/*` 等清理命令使用，确保最终镜像不包含缓存数据。

## [VALIDATION CHECKPOINT] 规范

每个变体 Dockerfile 的最后一个阶段必须包含验证检查点：

```dockerfile
RUN echo "┌─────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT]                │" && \
    echo "└─────────────────────────────────────────┘" && \
    # 1. 验证核心工具可执行
    /opt/conda/bin/conda --version && \
    # 2. 验证基础服务未被破坏
    which sshd && which supervisord && which docker && \
    # 3. 验证 PATH 优先级
    test "$(which python)" = "/opt/venv/bin/python" && \
    # 4. 验证非root用户可访问
    su - devuser -c "conda --version" && \
    echo "[OK] All validation checks passed"
```

**验证项必须包含**：
- 变体核心工具的可执行性
- 基础镜像关键服务（sshd/supervisord/docker）未被破坏
- PATH 优先级正确（默认 python 是 /opt/venv/bin/python）
- devuser 可访问新安装的工具

## 构建元数据

每个变体应写入构建信息文件：
```dockerfile
RUN echo "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /etc/devcontainer-variant-<name>-build-info && \
    echo "VARIANT=<name>" >> /etc/devcontainer-variant-<name>-build-info && \
    echo "BASE_IMAGE=devcontainer-base:<base>" >> /etc/devcontainer-variant-<name>-build-info
```

## 中文环境继承

基础镜像已配置中文环境（`zh_CN.UTF-8`/`Asia/Shanghai`），变体不得修改这些设置：
- `LANG=zh_CN.UTF-8`
- `LC_ALL=zh_CN.UTF-8`
- `TZ=Asia/Shanghai`

如需安装额外 locale 包，必须在安装后恢复中文环境设置。
