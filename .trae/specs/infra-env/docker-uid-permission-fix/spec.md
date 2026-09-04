---
title: "Docker 跨 UID 权限问题修复 - 需求规格"
status: "draft"
---

# Docker 跨 UID 权限问题修复 - 需求规格

## 问题描述

当前 devcontainer-base 镜像存在跨 UID/GID 权限不兼容问题：当使用 bind mount 将宿主机目录挂载到容器 `/workspace` 时，如果宿主机用户的 UID/GID 与容器内 `devuser`（默认 UID=1000）不匹配，会出现文件访问权限被拒绝（Permission denied）错误。

典型场景：
- macOS 宿主机用户默认 UID=501
- 某些 Linux 发行版用户 UID 不是 1000
- WSL2 环境中用户 UID 可能与容器不匹配
- 多用户共享服务器环境 UID 各不相同

## 目标用户

- 使用 bind mount 挂载本地代码目录进行开发的用户
- 在 macOS/Linux/WSL2 等不同宿主机环境使用容器的用户
- 需要非 root 用户身份在容器内读写挂载目录的用户

## 核心目标

1. **运行时动态 UID/GID 映射**：容器启动时自动检测或通过环境变量指定宿主机 UID/GID，动态调整容器内 `devuser` 的 UID/GID
2. **安全的权限调整**：仅调整必要目录的权限，避免修改宿主机系统目录或 Docker named volume 之外的文件属主
3. **向后兼容**：保持现有镜像使用方式不变，默认行为保持兼容（默认 UID=1000）
4. **提供多模式控制**：允许用户通过环境变量选择 chown 策略（自动/强制/跳过）
5. **修复现有缺陷**：解决当前 `chown -R devuser:devuser /workspace` 在构建期硬编码导致的运行时问题

## 非目标

1. 不引入 fixuid 等第三方二进制（保持纯 shell 实现，无额外依赖）
2. 不修改 Dockerfile 多阶段构建结构或现有包安装逻辑
3. 不改变容器默认用户（仍以 root 启动，通过 supervisord 或 su 切换到 devuser）
4. 不处理 rootless Docker/Podman 的复杂 cgroup 映射问题

## 功能需求

### FR1: 运行时 UID/GID 环境变量支持

容器需支持以下环境变量（均有合理默认值，可选传入）：

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `LOCAL_USER_ID` | （自动检测） | 宿主机用户 UID，如未设置则尝试自动检测挂载目录属主 |
| `LOCAL_GROUP_ID` | （自动检测） | 宿主机用户 GID，如未设置则尝试自动检测挂载目录属主 |
| `WORKSPACE_CHOWN_MODE` | `auto` | `/workspace` 目录 chown 策略：`auto`/`yes`/`no`/`named-only` |
| `CHOWN_EXTRA` | （空） | 额外需要 chown 的目录列表，空格分隔 |
| `FIXUID_DEBUG` | `0` | 设为 1 输出详细权限调试日志 |

### FR2: 动态用户 UID/GID 调整

entrypoint.sh 启动时执行以下逻辑：
1. 读取目标 UID/GID（环境变量 > 自动检测 > 默认 1000）
2. 如果目标 UID/GID 与 devuser 当前 UID/GID 不同：
   - 调整 devuser 的 UID：`usermod -u <TARGET_UID> devuser`
   - 调整 devuser 组的 GID：`groupmod -g <TARGET_GID> devuser`
   - 更新 devuser 主目录及所有 devuser 拥有的文件属主（容器内部文件，不碰 bind mount）
3. 保持 devuser 在 docker/sudo 等组的成员关系

### FR3: 智能自动检测

当 `LOCAL_USER_ID` 未设置时：
1. 检测 `/workspace` 目录属主（如果是 bind mount 且非 root 拥有）
2. 如果检测到有效 UID（非 0 且非 1000），自动使用该 UID/GID
3. 如果无法检测（如目录是 root:root 或 named volume），回退到默认 UID=1000

### FR4: 分层 chown 策略

| 模式 | 行为 | 适用场景 |
|-----|------|---------|
| `auto`（默认） | 仅 chown Docker named volume 和容器内部目录；bind mount 目录跳过并打印解决方案提示 | 推荐，安全默认 |
| `yes` | 强制 chown 指定目录（⚠️ 会修改宿主机文件属主！需明确警告） | 单用户专用开发环境 |
| `no` | 完全跳过 chown | 用户自行在宿主机处理权限 |
| `named-only` | 仅 chown Docker named volume，bind mount 全部跳过 | 纯 named volume 数据卷 |

### FR5: 安全保护机制

1. **系统目录强制跳过**：`/`、`/home`、`/etc`、`/usr`、`/bin`、`/sbin`、`/dev`、`/proc`、`/sys`、`/var`、`/root`、`/boot` 永远不执行 chown
2. **只读卷检测**：尝试创建临时文件检测是否只读，只读目录跳过 chown
3. **chown 前警告**：当 `CHOWN_MODE=yes` 且检测到 bind mount 时，打印醒目警告提示会修改宿主机文件
4. **错误容忍**：chown 失败不阻塞容器启动，打印警告后继续

## 非功能需求

### NFR1: 启动性能

- UID 调整和权限检查耗时应 < 3 秒（排除大目录 chown 时间）
- 权限检测逻辑不增加显著启动开销

### NFR2: 兼容性

- 与现有镜像完全向后兼容：不传任何新环境变量时，行为保持与修复前一致
- 支持 DinD（Docker-in-Docker）和 DooD（Docker-out-of-Docker）两种模式
- 支持所有现有变体（conda-llvm、onnx-dev、torch-dev、ai-dev 等）

### NFR3: 安全性

- 不引入 SUID 二进制或特权提升漏洞
- 默认配置不修改宿主机文件系统（安全默认）
- 密码、SSH 密钥等敏感文件权限正确（700/600）

### NFR4: 可调试性

- `FIXUID_DEBUG=1` 时输出详细诊断：检测到的 UID/GID、目录类型（bind/named/rootfs）、chown 决策过程
- 权限被跳过时打印清晰的解决方案提示（宿主机 chown 命令、sudo 方案、环境变量配置）

## 验收标准

### AC1: 功能正确性（rule）

- 当使用 `-e LOCAL_USER_ID=$(id -u) -e LOCAL_GROUP_ID=$(id -g)` 启动时，容器内 `devuser` 的 UID/GID 与宿主机用户完全匹配
- 挂载的 `/workspace` 目录中，devuser 可以创建、读取、写入、删除文件，无 Permission denied

### AC2: 默认兼容性（rule）

- 不传任何新环境变量启动容器时，devuser 的 UID=1000，行为与修复前一致
- 现有 Docker run 命令和 docker-compose 配置无需修改即可继续工作

### AC3: macOS 默认场景（rule）

- 在 macOS 上（默认 UID=501）使用 `-v $(pwd):/workspace` 启动时，即使不传 LOCAL_USER_ID，容器也能自动检测到正确 UID 并调整，或者给出清晰提示让用户设置环境变量

### AC4: 安全保护（rule）

- 无论传入什么参数，都不会对 `/etc`、`/usr` 等系统目录执行 chown
- 默认模式（auto）不会修改宿主机文件属主
- `CHOWN_MODE=yes` 时打印醒目警告提示宿主机修改风险

### AC5: DinD/DooD 兼容（rule）

- DinD 模式（`--privileged`）下 Docker daemon 正常启动，devuser 能使用 `docker` 命令
- DooD 模式（挂载 `/var/run/docker.sock`）下 devuser 能访问 docker socket

### AC6: 变体兼容（rubric）

- 所有现有变体（conda-llvm、onnx-dev、onnx-pytorch、onnx-quantized、torch-dev、ai-dev）构建后均继承修复，无需单独修改
- 变体构建脚本继续正常工作，构建日志无错误
- 评分标准：0=变体构建失败；1=部分变体有权限问题；2=所有变体验证通过（阈值≥2）

## 约束条件

1. 修改范围限定于：
   - `entrypoint.sh`：核心 UID 映射逻辑
   - `Dockerfile`：必要的环境变量默认值声明和用户目录准备
   - 可能新增 `scripts/fix-permissions.sh`（可选，如果逻辑复杂需要拆分）
2. 保持现有代码风格和日志格式
3. 不引入新的 apt/pip/conda 依赖
4. 构建时和运行时权限分离：构建期仍保持 root，运行时调整
