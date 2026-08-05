---
id: p1-06-docker-image-build-run
title: Docker 镜像构建与运行手册摘要
source: d:\spaces\chaos\docker\index.md
source_type: file
category: operations
tags:
  - docker
  - conda
  - podman
  - image-build
  - workspace-operations
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:30:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 docker/index.md、正文为运维操作摘要、元数据与 operations 分类映射核对通过
summary: Conda/Podman 镜像构建与运行手册，覆盖 Dockerfile 片段、构建命令、交互运行与挂载工作目录的标准操作。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p1-06-docker-image-build-run.md
archived_at: 2026-08-02T03:17:49Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:17:49Z archived from d:\spaces\chaos\.agents\knowledge\temp\operations\p1-06-docker-image-build-run.md to D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p1-06-docker-image-build-run.md
---

# Docker 镜像构建与运行手册摘要

## 来源

- 源文件：[docker/index.md](../docs-separation-guide/index.md)
- 上游分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`operations`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\operations\`

## 正文摘要

`docker/index.md` 是工作区镜像库的构建与运行手册，核心操作如下。

### Conda 镜像基础片段

以 `conda_user` 创建专用用户并安装 Miniconda：

```bash
RUN useradd -m conda_user && su - conda_user
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b -p /home/conda_user/miniconda3 \
    && rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH="/home/conda_user/miniconda3/bin:$PATH"
```

### 标准构建与运行（Docker）

- 构建镜像（仓库根目录执行）：`docker build -f client/docker/hub/conda.Containerfile -t ai/miniconda .`
- 交互运行：`docker run -it --rm ai/miniconda bash`
- 可选：项目根放置 `environment.yml` 时，构建自动对 `base` 环境执行 `conda env update -f environment.yml`
- 进入容器后可通过 `conda install <pkg>` 或 `mamba install <pkg>` 安装依赖

### Podman 构建方案（Windows 推荐）

- 首次使用需初始化并启动虚拟机：`podman machine init && podman machine start`
- 构建：`podman build -f client/docker/hub/conda.Containerfile -t ai/miniconda .`
- 交互运行：`podman run -it --rm ai/miniconda bash`
- 挂载当前目录：

```bash
# PowerShell
podman run -it --rm -v ${pwd}:/workspace ai/miniconda bash
# Bash/WSL
podman run -it --rm -v $(pwd):/workspace ai/miniconda bash
```

- 可选构建参数：`--build-arg USERNAME=conda_user`、`USER_UID=1000`、`USER_GID=1000`、`MINICONDA_PREFIX=/home/conda_user/miniconda3`
- 如需独立环境：`conda env create -n your_env -f /workspace/environment.yml`

## 动作边界

本轮为 P1 运维条目。正式归档时以构建/运行命令与前置条件为核心正文，不搬运 Dockerfile 源码或镜像内部实现细节。
