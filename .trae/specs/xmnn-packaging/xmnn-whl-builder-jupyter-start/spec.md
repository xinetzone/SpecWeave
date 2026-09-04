# XMNN Whl-Builder Jupyter 服务启动 Spec

## Why
用户需要在 `xmnn-whl-builder:latest` 镜像中启动一个 Jupyter 服务，并将 `d:\spaces\SpecWeave\external\chaos` 目录挂载进容器，以便在 Notebook 中访问 chaos 下的源码/模型/工具链。此前尝试的 `xmnn-whl-builder-jupyter` 容器因 `Exited(255)`（WSL 回收）且 `/workspace` 挂载错误（使用了匿名 volume 而非 chaos bind mount）而失败，需重新以正确配置启动。

## What Changes
- 复用 `xmnn-whl-builder:latest` 镜像（已内置 JupyterLab≥4.4 于 `/opt/venv`、`xmnn-conda` kernel、xmnn 于 conda）。
- 删除旧的 `xmnn-whl-builder-jupyter` 容器（Exited 255）。
- 以正确配置启动新容器：
  - 镜像：`xmnn-whl-builder:latest`
  - 挂载：`/mnt/d/spaces/SpecWeave/external/chaos` → 容器 `/workspace`（bind mount，覆盖整个 chaos 目录）
  - 端口：容器 8888 → 宿主 `127.0.0.1:8891`（8890 已被 xmnn-runtime-jupyter 占用，8888 宿主被 chaos-ai-portable 占用）
  - 启动命令：`/opt/venv/bin/jupyter lab`，`--ServerApp.allow_root=True`、`--ServerApp.token=devtoken`、`--ServerApp.root_dir=/workspace`，显式 `PATH=/opt/conda/bin:$PATH`
  - 容器名：`xmnn-whl-builder-jupyter`
- 保持 WSL2 会话存活（`sleep infinity` 后台进程），防止容器被回收。

## Impact
- Affected specs: `chaos-ai-xmnn-whl-builder`（复用其构建产物镜像，无代码改动）
- Affected code: 无（纯运行态操作，不修改仓库文件）
- 运行态：复用 `xmnn-whl-builder:latest` 镜像，启动一个 Jupyter 服务容器

## ADDED Requirements

### Requirement: 正确挂载 chaos 目录
系统 SHALL 将宿主 `d:\spaces\SpecWeave\external\chaos`（WSL 路径 `/mnt/d/spaces/SpecWeave/external/chaos`）以 bind mount 挂载到容器 `/workspace`，使 Notebook 可访问 chaos 下的 ai/models/npu_tvm/npuusertools 等内容。

#### Scenario: 挂载生效
- **WHEN** 检查容器挂载
- **THEN** `/workspace` 绑定到 chaos 目录，容器内 `ls /workspace` 可见 ai/models 等子目录

### Requirement: Jupyter 服务可用
系统 SHALL 在容器内以 `/opt/venv/bin/jupyter lab` 启动服务，监听 8888，映射到宿主 `127.0.0.1:8891`，token 为 `devtoken`，root 目录为 `/workspace`，并启用 `xmnn-conda` kernel。

#### Scenario: Jupyter 健康
- **WHEN** 访问 `http://127.0.0.1:8891`
- **THEN** 返回 Jupyter 登录页（HTTP 200/302），`/api/kernelspecs` 可见 `xmnn-conda` kernel

## MODIFIED Requirements
无。

## REMOVED Requirements
无。
