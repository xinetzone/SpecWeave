---
id: "docker-buildkit-compliance-checklist"
title: "Dockerfile BuildKit 合规性速查清单"
source:
  - "7个Docker子项目10个Dockerfile BuildKit合规性审计"
  - "docker-buildkit-optimization-best-practices.md"
  - "docker-buildkit-optimization-project-comparison.md"
related_patterns:
  - "docker-buildkit-optimization-best-practices.md"
  - "docker-buildkit-optimization-project-comparison.md"
tags: ["docker", "buildkit", "checklist", "cache-mount", "compliance"]
---

# Dockerfile BuildKit 合规性速查清单

> 新建或修改 Dockerfile/Containerfile 后，花 **30 秒** 逐项打勾，避免 BuildKit 优化静默失效。
>
> **铁律**：三件套（语法声明 + 安全Shell + 缓存挂载）缺一不可。

---

## 🔴 文件头（写完 FROM 之前先检查）

- [ ] **第1行**是 `# syntax=docker/dockerfile:1.7-labs`（不是注释块之后！）
- [ ] 没有任何内容在 syntax 声明之前（空行也不行）

```dockerfile
# syntax=docker/dockerfile:1.7-labs    # ← 必须是第1行
# 我的注释块...
FROM ubuntu:26.04
```

> ⚠️ **踩坑记录**：caffe-ffi-cross 把 syntax 放在了大段注释之后，导致所有 cache mount 静默失效。

---

## 🟡 每个 FROM 阶段（多阶段构建时每个 FROM 都要检查）

- [ ] FROM 之后（ARG/ENV 之后，第一个 RUN 之前）有 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- [ ] 如果是多阶段构建，**第二个及以后的 FROM 也有 SHELL 声明**（FROM 会重置 SHELL）

```dockerfile
FROM builder AS stage2
ARG ...
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]   # ← 不能漏！
ENV ...
RUN ...
```

> ⚠️ **踩坑记录**：Dockerfile.win-cross 的 wine-runtime 阶段漏了 SHELL；虽然镜像继承可能保留 SHELL，但显式声明才是安全做法。

---

## 🟢 包管理器缓存挂载（每个 RUN 都检查）

### APT（Debian/Ubuntu）

- [ ] `apt-get update` / `apt-get install` 的 RUN 有**两个**缓存挂载：
  - [ ] `--mount=type=cache,target=/var/cache/apt,sharing=locked`
  - [ ] `--mount=type=cache,target=/var/lib/apt/lists,sharing=locked`
- [ ] apt 安装后有 `&& rm -rf /var/lib/apt/lists/*`

```dockerfile
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends package1 package2 && \
    rm -rf /var/lib/apt/lists/*
```

### pip（Python）

- [ ] **每一个** `pip install` 的 RUN 都有 `--mount=type=cache,target=/root/.cache/pip,sharing=locked`
- [ ] pip install 使用了 `--no-cache-dir`
- [ ] 如果用了 venv，venv 创建 + `pip install --upgrade pip setuptools wheel` 的 RUN 也要加缓存（不只是 requirements.txt 那一步！）
- [ ] 如果 USER 切换到非 root 用户，缓存路径改为 `/home/<user>/.cache/pip`

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt
```

> ⚠️ **踩坑记录**：devcontainer-base 和 jupyter-ssh-base 的 venv+pip-upgrade 步骤漏掉了缓存挂载，pip/setuptools/wheel 每次构建都重新下载。

### Conda（Miniconda/Miniforge）

- [ ] **每一个** `conda install` / `conda create` 的 RUN 都有 `--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- [ ] conda 安装后有 `&& conda clean -ya`

```dockerfile
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    conda install -y -n base package1 package2 && \
    conda clean -ya
```

> ⚠️ **踩坑记录**：devcontainer-base conda variant 的 `conda install python=${PYTHON_VERSION}` 漏了缓存挂载和 conda clean，Python 包每次构建重新下载。

---

## 🔵 快速验证命令

写完 Dockerfile 后，用以下命令快速验证 BuildKit 是否正确识别了 syntax 和 cache mount：

```bash
# 语法验证（快速，不实际构建）
DOCKER_BUILDKIT=1 docker build --progress=plain -t test --target <first-stage> -f Dockerfile . 2>&1 | head -20
# 第一行应出现：#1 [internal] load build definition from Dockerfile
# 且无 error about 'skip remaining parser directives after first instruction' 警告
```

---

## 📋 一页纸速查（贴在显示器旁）

```
┌─────────────────────────────────────────────────────┐
│  Dockerfile BuildKit 三件套速查                       │
├─────────────────────────────────────────────────────┤
│  □ 第1行: # syntax=docker/dockerfile:1.7-labs       │
│  □ 每个FROM后: SHELL ["/bin/bash","-e","-o",...]    │
│  □ apt:    2个cache(/var/cache/apt+/var/lib/apt/..)  │
│  □ pip:    /root/.cache/pip + --no-cache-dir        │
│  □ conda:  /opt/conda/pkgs + conda clean -ya        │
│  □ 每个pip/conda install的RUN都要有cache mount       │
│  □ pip upgrade步骤也要加缓存！                        │
│  □ 多阶段每个FROM都要重新声明SHELL！                   │
└─────────────────────────────────────────────────────┘
```
