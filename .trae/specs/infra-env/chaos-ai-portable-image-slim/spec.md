# Chaos AI Portable 镜像多阶段构建瘦身 Spec

## Why

`chaos-ai:portable` 镜像当前 **15.6GB**（基础镜像 `devcontainer-base:onnx-quantized-latest` 仅 7.7GB）。经层分析，构建增量 7.9GB 的 **58%（4.6GB）** 来自 Stage 1 的 `chown -R ai:ai /opt/conda`——该命令将整个 5.7GB 的 conda 目录复制为新层（Docker 反模式：chown 改变属主会全量复制目录）。镜像过大导致磁盘浪费、传输/拉取缓慢。

## What Changes

- **多阶段构建重组** `portable.Dockerfile`：拆分为 `base` → `deps` → `final` 三阶段，实现层隔离与缓存优化
- **删除 `chown -R ai:ai /opt/conda`**（[portable.Dockerfile#L133](file:///d:/spaces/SpecWeave/external/chaos/ai/portable.Dockerfile#L133-L133)）：conda 保持 root:root，消除 4.6GB 复制层
- **ai 用户改为 sudo 安装包**：ai 通过 `sudo pip install` / `sudo conda install`（已有 NOPASSWD sudo 权限）安装新包，无需 conda 写权限
- **保留全部 pip 包**：Stage 2 包列表不变，仅做结构优化
- 配套更新文档/启动脚本中对 ai 直接写 conda 的假设（改为 sudo 提示）

## Impact

- Affected specs: chaos-ai-portable-docker
- Affected code:
  - `external/chaos/ai/portable.Dockerfile`（多阶段重构 + 删 chown + PIP_USER 修复）
  - `external/chaos/ai/docs/portable/conda-environment-guide.md`（sudo 安装说明）
  - `external/chaos/ai/scripts/start.sh`（如内部有以 ai 直接写 conda 的逻辑则调整，仅当发现时）
  - `external/chaos/ai/docker-compose.yml`（dev-portable 指向 `chaos-ai:portable-slim`）
  - `external/chaos/ai/scripts/verify-startup.sh`、`.env.example`（py314 → base 文案同步）
- 预期结果：镜像从 **15.6GB → ~9.2GB**（省 6.4GB，41%）

## 实际结果（2026-08-11 实测）

| 指标 | 优化前 | 优化后 | 说明 |
|------|--------|--------|------|
| **镜像大小** | 15.6GB | **9.59GB** | 省 6.01GB，**降幅 38.5%**（≥35% 目标达成；略高于预期的 9.2GB，因基础镜像自身较大） |
| **构建阶段** | 单阶段 | base → deps → final 三阶段 | 层隔离 + 缓存优化 |
| **conda 属主** | ai:ai（chown） | root:root | 消除 4.6GB chown 复制层 |
| **包安装方式** | ai 直接写 conda | ai 通过 `sudo pip` | conda root 属主下可用 |
| **docker-cache 缓存** | — | **2.0GB** tar.gz | 原子写入 + SHA256 校验 |
| **服务状态** | — | sshd / dockerd / jupyter 均 RUNNING | 容器 healthy |

### 关键版本（优化后镜像内实测）
- Python 3.14.4（conda base）
- torch 2.13.0 / onnx 1.22.0 / onnxruntime 1.28.0 / numpy 2.4.4
- LLVM 22.1.8 / clang 22.1.8 / CMake 4.4.2 / Ninja 1.13.2
- conda 环境：`base`（默认激活，多入口一致）

### 关键技术发现：PIP_USER 冲突（构建期 → 运行期）
- **现象**：基础镜像设置 `ENV PIP_USER=1`，导致 deps 阶段以 root 安装的包写入 root 的 user-site（`/root/.local`）而非 `/opt/conda`；运行时 ai 用户 user-site 为 `/home/ai/.local`，**无法 import 任何 deps 阶段包**（transformers/jupyterlab/nuitka 等全部 ModuleNotFoundError）
- **根因**：PIP_USER 设置作用于构建期且以 root 身份执行，包落点与运行用户（ai）不一致
- **修复**：deps 阶段加 `ENV PIP_USER=0`（包正确写入 `/opt/conda`，root 属主全局可读），final 阶段恢复 `ENV PIP_USER=1`（支持运行时 `pip install --user`）

## ADDED Requirements

### Requirement: 多阶段构建重组
系统 SHALL 将 `portable.Dockerfile` 重构为至少两个独立构建阶段，实现构建期/运行期层隔离。

#### Scenario: 三阶段构建成功
- **WHEN** 执行 `docker compose build dev-portable`
- **THEN** 构建成功，产出 `chaos-ai:portable`，且各阶段日志清晰

### Requirement: 消除 conda chown 复制层
系统 SHALL 不再对 `/opt/conda` 执行 `chown -R`，避免复制整个 conda 目录。

#### Scenario: 镜像显著变小
- **WHEN** 完成构建后执行 `docker images chaos-ai:portable`
- **THEN** 镜像大小 ≤ ~10GB（相比原 15.6GB 显著减小 ≥35%）

### Requirement: ai 用户 sudo 安装包
系统 SHALL 支持 ai 用户通过 `sudo pip install` / `sudo conda install` 在 conda base 环境安装新包。

#### Scenario: sudo 安装成功
- **WHEN** 以 ai 用户执行 `sudo pip install numpy`
- **THEN** 包成功安装到 conda base，且 `python -c "import numpy"` 可用

## MODIFIED Requirements

### Requirement: 服务启动与运行时一致性
完善运行时服务（sshd/dockerd/jupyter）在 conda root 属主下的可用性，确保 jupyter 内 `!pip install` 通过 sudo 仍可用。

## REMOVED Requirements

### Requirement: 构建时对 /opt/conda 整体 chown
**Reason**: 产生 4.6GB 复制层，是镜像膨胀主因；基础镜像 conda 属主为 root，可通过 sudo 方案替代。
**Migration**: ai 安装包改为 `sudo pip install` / `sudo pip install --user`（~/.local 装载 user site，无需 conda 写权限）。