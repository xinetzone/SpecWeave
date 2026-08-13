---
id: retrospective-chaos-ai-portable-slim-20260811
date: 2026-08-11
type: retrospective
source: "七概念方法论实践：chaos-ai:portable 镜像多阶段构建瘦身优化"
tags: [docker, multistage, slim, conda, pip_user, image-size, refactor, docker-cache]
scenario: refactor
chain: I→F→A→C
quality_gates: {G1: passed, G2: passed, G3: not-applicable, G4: passed, V: passed}
---

# Chaos AI Portable 镜像多阶段构建瘦身复盘

## 一、背景与目标

`chaos-ai:portable` 镜像体积过大（**15.6GB**），导致磁盘浪费、传输/拉取缓慢。本次任务采用七概念方法论中的**重构优化链路（I→F→A→C）**，通过多阶段构建重构 Dockerfile 实现镜像瘦身，目标 ≥35%。

## 二、关键事实（R/I - 洞察）

### 2.1 根因分析（I）

| 指标 | 值 |
|------|-----|
| 优化前镜像 | 15.6GB |
| 基础镜像 | devcontainer-base:onnx-quantized-latest（7.7GB） |
| 构建增量 | 7.9GB，其中 **58%（4.6GB）** 来自 Stage 1 的 `chown -R ai:ai /opt/conda` |
| 根本原因 | chown 改变属主会**全量复制**整个 conda 目录为新层（Docker 反模式） |

### 2.2 关键技术发现：PIP_USER 冲突

- **现象**：基础镜像设置 `ENV PIP_USER=1`，deps 阶段以 root 安装的包写入 root 的 user-site（`/root/.local`）而非 `/opt/conda`
- **影响**：运行时 ai 用户 user-site 为 `/home/ai/.local`，**完全无法 import 任何 deps 阶段包**（transformers/jupyterlab/nuitka 等全部 ModuleNotFoundError）
- **根因**：PIP_USER 作用于构建期且以 root 执行，包落点与运行用户（ai）不一致
- **修复**：deps 阶段 `ENV PIP_USER=0`（包写入 `/opt/conda`，root 属主全局可读），final 阶段恢复 `ENV PIP_USER=1`（支持运行时 `pip install --user`）

## 三、方案设计（F - 第一性原理）

核心思路：**区分构建期与运行期的属主模型**。
- 构建期以 root 身份安装包 → 包应写入 `/opt/conda`（root 属主），而非 rely on user-site
- 运行期以 ai 用户运行服务 → 包通过 `/opt/conda` 全局可读路径访问，新装包用 sudo 或 `--user`
- 删除整体 chown → 消除复制层，通过 sudo 方案替代 ai 用户的 conda 写权限

## 四、实施与验证（A - 原子化）

### 4.1 三阶段重构

| 阶段 | 职责 |
|------|------|
| `base` | 创建 ai 用户 + 目录 + sudo（删除 `chown -R ai:ai /opt/conda`） |
| `deps` | root 身份安装全部 pip 包（`ENV PIP_USER=0`），清理缓存 |
| `final` | COPY 配置/脚本 + 运行时配置 + `ENV PIP_USER=1` + 7 项验证 |

### 4.2 实测结果

| 指标 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| **镜像大小** | 15.6GB | **9.59GB** | **省 6.01GB（38.5%）** |
| conda 属主 | ai:ai（chown） | root:root | 消除 4.6GB 复制层 |
| 包安装方式 | ai 直接写 conda | ai 通过 sudo pip | conda root 属主下可用 |
| docker-cache 缓存 | — | 2.0GB tar.gz | 原子写入 + SHA256 |
| 服务状态 | — | sshd/dockerd/jupyter 均 RUNNING | 容器 healthy |

### 4.3 关键版本（优化后实测）

- Python 3.14.4（conda base）
- torch 2.13.0 / onnx 1.22.0 / onnxruntime 1.28.0 / numpy 2.4.4
- LLVM 22.1.8 / clang 22.1.8 / CMake 4.4.2 / Ninja 1.13.2

### 4.4 验证项（全部通过）

- [x] 三阶段构建成功，无报错
- [x] ai 用户 `sudo pip install flask` 成功（写入 conda base）
- [x] `pip install --user six` 成功（~/.local 替代方案）
- [x] 三服务 RUNNING，容器 healthy
- [x] 宿主机 2222(SSH) + 8888(Jupyter) 端口可达
- [x] ai 用户可 import 全部 deps 阶段包（transformers/jupyterlab/nuitka）
- [x] 镜像 15.6GB → 9.59GB（降幅 38.5%，超 35% 目标）

## 五、模式萃取（E）

### 模式：构建期/运行期属主分离（PIP_USER 治理）

- **触发条件**：多阶段 Dockerfile 中，基础镜像设置了 `PIP_USER=1` 且构建期以 root 身份安装包
- **核心步骤**：
  1. 识别基础镜像的 PIP_USER/ENV 设置
  2. deps 阶段显式 `ENV PIP_USER=0`，确保包写入共享的 `/opt/conda`
  3. final 阶段恢复 `ENV PIP_USER=1`，支持运行时 `pip install --user`
  4. 验证运行用户（非 root）能否 import 构建期安装的包
- **反模式**：直接依赖基础镜像的 PIP_USER 默认值；构建期包写入 root user-site 而未验证运行用户可见性
- **迁移验证**：ai 用户可 import 全部 deps 阶段包 ✅

### 模式：消除 Docker chown 复制层

- **触发条件**：镜像某层存在 `chown -R` 大型目录（如 /opt/conda）
- **核心步骤**：改为属主保持 root，通过 sudo 授权非 root 用户写入
- **反模式**：对大型目录整体 chown 会全量复制，产生巨量镜像层
- **迁移验证**：镜像 9.59GB，三服务正常 ✅

## 六、Compose 指向与缓存（C）

- `docker-compose.yml` 的 dev-portable 服务 `image:` 改为 `chaos-ai:portable-slim`
- 通过 docker-cache skill 缓存（2.0GB tar.gz，ID `sha256:65cedded9cd07`）
- `docker compose up -d dev-portable` 重建容器，healthy 且端口可达

## 七、提交记录

| 仓库 | Commit | 说明 |
|------|--------|------|
| external/chaos/ai | `2183d8e` | 多阶段构建瘦身镜像至9.59GB并修复PIP_USER冲突 |
| SpecWeave | `9cb8e593` | 新增镜像多阶段瘦身spec文档 |

## 八、后续建议

1. 将 `chaos-ai:portable-slim` 封存为正式版本标签（如 `chaos-ai:portable-v3`）
2. 考虑迁移至 OCI 布局或使用 `--squash`（BuildKit）进一步压缩
3. 将 PIP_USER 治理模式沉淀为可复用 Dockerfile 规范
4. 关注基础镜像 devcontainer-base:onnx-quantized-latest 自身的大小优化潜力