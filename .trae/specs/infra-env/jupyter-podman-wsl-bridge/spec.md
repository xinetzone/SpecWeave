---
title: "jupyter-podman-rootless WSL 桥接转换 - 产品需求文档"
status: "draft"
---

# jupyter-podman-rootless WSL 桥接转换 - 产品需求文档

## Overview
- **Summary**: 明确回答 `.image-cache/` 中的 Podman 镜像 tar.gz 是否可直接通过 `wsl -d` 使用，并提供正确的转换方案；可选地为 `bin/jupyter` CLI 增加 WSL 发行版导出/导入命令。
- **Purpose**: 解决"镜像缓存能否直接作为 WSL 发行版启动"的疑问，避免用户直接导入 OCI 分层镜像导致的 whiteout 文件、权限异常、启动失败等问题。
- **Target Users**: jupyter-podman-rootless 容器用户，希望在没有 Podman 的情况下直接用 WSL 启动开发环境，或在 WSL 重置后快速恢复环境。

## Goals
- ✅ **G1**: 明确回答：`podman save` 格式的 tar.gz **不能**直接 `wsl --import`
- ✅ **G2**: 解释原因（OCI分层格式 vs flat rootfs 格式差异）
- ✅ **G3**: 提供使用 `docker-wsl-bridge-cmd` Skill 的标准转换流程
- 🔲 **G4**（可选增强）: 在 `bin/jupyter` CLI 中添加 `wsl-export` 和 `wsl-import` 命令，一键完成镜像→WSL 发行版转换

## Non-Goals (Out of Scope)
- 不修改现有容器运行逻辑（Podman rootless DinP 模式保持不变）
- 不替代现有的 `save`/`load` 镜像缓存命令
- 不实现纯 Python 的 OCI 解压（已有 docker-wsl-bridge-cmd 的 Podman 桥接方案更可靠）
- 不处理 Windows 版本 WSL1 的兼容性（仅支持 WSL2）

## Background & Context
- 当前 `bin/jupyter` CLI 已有 `save` 命令，通过 `podman save --format docker-archive` 将镜像保存到 `.image-cache/`
- 用户可能误以为这种 tar.gz 可以直接用 `wsl --import` 导入
- `docker-wsl-bridge-cmd` Skill 已实现成熟的 Podman 桥接转换方案（Podman load → create → export → wsl import → wsl.conf 配置）
- 该 Skill 已在 devcontainer-base 镜像上验证通过，流程可复用到 jupyter-podman-rootless
- 镜像中的关键信息：
  - 默认用户：`devuser`（UID=1000）
  - Conda 路径：`/opt/conda`（需要配置非交互 shell 激活）
  - systemd：不需要（容器镜像，`systemd=false`）
  - init：tini

## Functional Requirements
- **FR-1**: 提供清晰的问题解答和原理说明
  - 解释 OCI 分层镜像（docker-archive）与 flat rootfs 的区别
  - 说明直接导入的后果（.wh.* 文件、权限问题、启动失败）
- **FR-2**: 提供基于 docker-wsl-bridge-cmd 的分步转换指南
  - 适配 jupyter-podman-rootless 的参数（用户、conda路径等）
  - 包含验证步骤
- **FR-3**（如果实现G4）: `bin/jupyter wsl-export [--distro-name <name>] [--install-dir <path>]`
  - 将当前已保存的镜像缓存转换为 WSL 发行版
  - 自动探测 UID=1000 用户（devuser）
  - 自动配置 `/etc/wsl.conf`（default user, systemd=false）
  - 自动配置 conda 全局激活（`/etc/profile.d/conda.sh`）
- **FR-4**（如果实现G4）: `bin/jupyter wsl-import <rootfs.tar.gz> [--distro-name <name>]`
  - 从已导出的 rootfs tar.gz 导入 WSL 发行版
- **FR-5**（如果实现G4）: `bin/jupyter wsl-verify [--distro-name <name>]`
  - Smoke Test：启动、用户、可写、D盘挂载、Python/Conda/Jupyter 检查

## Non-Functional Requirements
- **NFR-1**: 转换脚本必须使用 rootful Podman（`sudo podman`）避免 UID 映射偏移
- **NFR-2**: Windows 路径必须正确转换为 WSL `/mnt/` 路径
- **NFR-3**: wsl.conf 配置后必须执行 `wsl --terminate` 生效
- **NFR-4**: Conda 必须通过 `/etc/profile.d/` 配置，确保非交互 shell（`wsl -d -- sh -l -c`）可用
- **NFR-5**: 所有 WSL 操作必须幂等（已存在则提示先 unregister 或使用不同名称）

## Constraints
- **Technical**: 
  - 需要 WSL2（不支持 WSL1）
  - 需要至少一个可用的 WSL Linux 发行版（Ubuntu 推荐）作为转换工作区
  - 转换工作区需要安装 Podman（rootful 模式）
  - 目标安装盘需要有约 1.5-2x rootfs 大小的可用空间
- **Business**: 保持现有 `save`/`load`/`start`/`stop` 等命令的向后兼容性
- **Dependencies**: 
  - `docker-wsl-bridge-cmd` Skill 的转换逻辑
  - WSL2 (`wsl --version` 可用)
  - Podman 在工作区 WSL 中可用

## Assumptions
- 用户已有 WSL2 环境（jupyter-podman-rootless 本身就需要 WSL 运行 Podman）
- 用户在 WSL Ubuntu 中已安装 Podman（项目文档已有说明）
- 默认用户是 devuser（UID=1000），与 Containerfile 一致
- Conda 安装在 `/opt/conda`，与 Containerfile 一致
- 不需要 systemd（容器镜像特性）

## Acceptance Criteria

### AC-1: 核心问题解答清晰
- **Given**: 用户询问 .image-cache 中的 tar.gz 能否直接 wsl -d
- **When**: 用户阅读本 spec 或相关文档
- **Then**: 用户明确知道"不能直接用"，理解原因，知道正确的转换方法
- **Verification**: `human-judgment`
- **Notes**: 这是本任务的核心目标，无论是否实现 CLI 增强都必须完成

### AC-2: 手动转换流程可操作
- **Given**: 用户有 .image-cache 中的镜像 tar.gz
- **When**: 用户按照提供的分步指南操作
- **Then**: 能成功通过 `wsl -d <distro-name>` 进入环境，默认用户是 devuser，python/conda 可用
- **Verification**: `programmatic`
- **Notes**: 使用 docker-wsl-bridge-cmd 的流程，适配 jupyter 镜像参数

### AC-3: wsl-export 命令一键转换（如果实现G4）
- **Given**: 已有镜像缓存（`jupyter save` 已执行）
- **When**: 在 WSL 中执行 `bash bin/jupyter wsl-export`
- **Then**: 
  - 自动创建 `<distro-name>-rootfs.tar.gz`
  - 自动执行 `wsl --import`
  - 自动配置 wsl.conf（default=devuser, systemd=false）
  - 自动配置 conda 全局激活
  - Smoke Test 通过
- **Verification**: `programmatic`

### AC-4: wsl 环境中核心工具可用（如果实现G4）
- **Given**: WSL 发行版已成功导入
- **When**: 执行 `wsl -d <distro-name> -- sh -l -c "jupyter lab --version"`
- **Then**: Jupyter Lab 可正常执行，Python 版本是 3.14t，conda 环境已激活
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要实现 CLI 增强（G4），还是只提供手动操作指南即可？
- [ ] WSL 发行版的默认安装目录应该在哪里？（项目目录下？还是 D:\WSL\？）
- [ ] 是否需要支持从容器直接导出（跳过 save 步骤）？
