---
status: draft
title: openKylin 全功能开发容器镜像（并入 openkylin-wsl-devkit）
source: 用户请求「D:\spaces\SpecWeave\apps 下创建 openKylin podman 镜像」；澄清：全功能开发容器 / 并入 openkylin-wsl-devkit / 构建环境两者兼容
created: 2026-10-08
---

# openkylin-dev-container — openKylin 全功能开发容器镜像（Product Requirements Document）

## Overview

- **Summary**：在 `apps/dev-tools/openkylin-wsl-devkit/` 内新增 `openkylin-dev-container/` 镜像工程，产出一个基于 openKylin 官方基础镜像、内置 **SSH + Jupyter + rootless Podman + supervisord** 的全功能开发容器镜像（对标 `apps/containers/jupyter-podman-rootless` 的能力形态，但以 openKylin 为系统基底），并配套双环境（Windows 原生 Podman machine / openKylin WSL 发行版内）构建与冒烟脚本、应用 README 增补与文档中心指南。
- **Purpose**：openKylin WSL 开发者需要一个基于 openKylin 自身的容器化开发环境，用于在容器内开发、测试 openKylin 软件包与服务；现有 `okw` 工具包已覆盖 WSL 发行版内 rootless Podman 的预检/安装/验收（`okw podman *`），本镜像补齐「容器内开发环境」这一环，与 okw 形成「WSL 发行版 → 容器开发环境」完整链路。
- **Target Users**：openKylin 平台开发者；使用 okw 工具包的 Windows + WSL2 用户；需要在 openKylin 基底容器内做 SSH/Jupyter 开发与 rootless 容器实验的开发者。

## Goals

- 产出可构建、可运行、可验证的 openKylin 全功能开发容器镜像工程（Containerfile + entrypoint + 配置 + 双环境脚本 + 文档），全部资产并入 `openkylin-wsl-devkit` 应用目录。
- 镜像内 SSH（22）、Jupyter（8888）、rootless Podman（devuser 可跑容器）、supervisord 服务栈齐备，中文 locale + Asia/Shanghai 时区。
- 构建与冒烟脚本在 Windows 原生 Podman machine 与 openKylin WSL 发行版内均可运行（自动探测，优先本机可用 podman）。
- 真实构建一次并冒烟通过，产出可复现证据。

## Non-Goals

- 不新增 `okw` CLI 子命令（`okw image build/verify` 等留作后续可选演进，不在本 spec 范围）。
- 不做 Toolbx 兼容（`com.github.containers.toolbox` 标记等，属 jupyter-podman-rootless 特色，openKylin 场景无对应宿主资产）。
- 不做 OMLMD/OLOT/ModelCar（依赖 conda-forge 生态，openKylin 源不提供，非本镜像目标）。
- 不做离线交付链路（`containers/offline-delivery` 职责，不回流）。
- 不新建独立应用、不修改 openKylin 软件源、不添加第三方 apt 源。
- 不承诺 arm64/riscv64 多架构构建（仅 amd64 真实验证；脚本保留 `--platform` 透传但不作为验收项）。

## Background & Context

- openKylin 官方提供基础容器镜像 `openkylin/openkylin`（Gitee 官方仓库 `openkylin/openkylin-docker-images`，`Base/` 已更新至 3.0）；官方 README 说明 tags 为 `2.0` 与 `latest`（`latest` 为最新可用长期稳定镜像），国内拉取建议 `quay.io/openkylin/openkylin:latest`（hub.docker.com 受限）。
- **2026-10-09 实测裁定**：`quay.io/openkylin/openkylin:latest` 的 os-release 为 **openKylin 2.0 SP1 (nile)**（VERSION_ID=2.0，VERSION_CODENAME=nile）——官方 `latest` 指向 LTS 轨（2.0 SP1），3.0 为创新版不在该轨；官方无已验证的 3.0 容器 tag。为满足「openKylin 3.0 基底」目标，用户裁定改用本会话导入的 WSL 3.0 rootfs `localhost/openkylin:3.0` 作为基底（真 3.0；apt 源为 openKylin 3.0 官方源）。
- **2026-10-09 实测裁定**：`quay.io/openkylin/openkylin:latest` 的 os-release 为 **openKylin 2.0 SP1 (nile)**（VERSION_ID=2.0，VERSION_CODENAME=nile）——官方 `latest` 指向 LTS 轨（2.0 SP1），3.0 为创新版不在该轨；官方无已验证的 3.0 容器 tag。为满足「openKylin 3.0 基底」目标，用户裁定改用本会话导入的 WSL 3.0 rootfs `localhost/openkylin:3.0` 作为基底（真 3.0；apt 源为 openKylin 3.0 官方源）。
- openKylin 基于 Debian/Ubuntu 体系，包管理器为 APT；基础镜像内含 python3 与系统工具。
- `openkylin-wsl-devkit`（okw）为 scikit-build-core 纯 Python 包，`okw podman preflight/install/verify` 已实现 WSL 发行版内 rootless Podman 三步流程（零第三方运行时依赖、禁止第三方源、冒烟 `--pull=never`）。
- 镜像构建规范参考：`apps/containers/jupyter-podman-rootless/.agents/rules/containerfile.md`（Containerfile 命名、3 阶段分层、devuser UID 1000、zh_CN.UTF-8、rootless 三必需、构建注释英文、验证清单）。
- 组级共同契约（`apps/containers/AGENTS.md` G3）：容器启动路径携带 `--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`，严禁 `--privileged`。

## Functional Requirements

- **FR-1**：`openkylin-dev-container/` 目录包含 `Containerfile`（FROM `localhost/openkylin:3.0`，即本地导入的 openKylin 3.0 WSL rootfs；2026-10-09 用户裁定改用此基底——官方 registry `latest` 实测为 2.0 SP1 (nile) LTS，非 3.0；apt 安装 openssh-server / supervisor / podman / uidmap / slirp4netns / fuse-overlayfs / crun / tini / locales 等，pip 安装 jupyterlab + notebook，zh_CN.UTF-8 + Asia/Shanghai，devuser UID 1000 + subuid/subgid 映射（起点 100000，须高于用户自身 UID））。
- **FR-2**：`entrypoint.sh` 启动 supervisord（管理 sshd + jupyter），`healthcheck.sh` 探测服务存活；sshd_config / supervisord.conf / jupyter 配置 / containers/storage.conf（fuse-overlayfs rootless）随镜像复制。
- **FR-3**：`scripts/build.ps1`（Windows 原生 Podman machine）与 `scripts/build.sh`（openKylin WSL / 任意 Linux）自动探测可用 podman 并执行 `podman build -t localhost/openkylin-dev:3.0`，支持 `--tag` 覆盖。
- **FR-4**：`scripts/smoke.ps1` 与 `scripts/smoke.sh` 对本地已构建镜像执行冒烟（SSH 端口监听、Jupyter 进程、devuser rootless `podman info`、临时容器 `/bin/true`），全部使用 `--pull=never`，不触发外部拉取。
- **FR-5**：openkylin-wsl-devkit 的 `README.md` 增补镜像章节；文档中心新增 `docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md` 并接入 `index.md` toctree。

## Non-Functional Requirements

- **NFR-1**：构建日志与脚本注释使用英文（避免编码问题，沿用 jupyter-podman-rootless 约定）；用户可见的 README/指南使用中文。
- **NFR-2**：镜像内禁止硬编码密码/密钥/token；SSH 主机密钥在容器启动时生成（entrypoint 逻辑），不打包进镜像。
- **NFR-3**：脚本遵循 okw 既有哲学——不修改软件源、不添加第三方源、不隐式拉取、只读冒烟默认不写宿主状态。
- **NFR-4**：单次完整构建在本机 Podman machine 可于合理时间内完成（apt + pip 依赖缓存复用优先）。

## Constraints

- **Technical**：构建宿主为 Windows（Podman machine `podman-machine-default`）+ WSL2（`openKylin-3.0-desktop`）；容器引擎 podman（无 docker）；FROM 固定 `localhost/openkylin:3.0`（本地导入 WSL 3.0 rootfs；官方 registry `latest` 实测为 2.0 SP1 (nile) LTS）。
- **Business**：资产归属 `apps/dev-tools/openkylin-wsl-devkit/`（用户明确选择并入，不新建应用）；对外可读文档一律入根 `docs/`（AGENTS 文档边界）。
- **Dependencies**：openKylin 官方基础镜像可拉取（quay.io 兜底）；openKylin 软件源可提供上述 apt 包；pip 可访问 PyPI（openKylin 3.0 镜像内网络可达性按实际构建结果验证）。

## Assumptions

- ~~openKylin 官方基础镜像 `latest` tag 当前即 3.0 系列~~（**已证伪**：2026-10-09 实测为 2.0 SP1 (nile) LTS；已按用户裁定改用本地导入 WSL 3.0 rootfs，见 Background）；apt 包名与 Debian/Ubuntu 兼容（openssh-server/supervisor/podman/uidmap/slirp4netns/fuse-overlayfs/crun/tini/locales 均可从官方源安装）。
- 容器内 rootless Podman 需要宿主在运行容器时透传 `/dev/fuse` 并配置 subuid/subgid（脚本冒烟默认不强制宿主导通，仅验证镜像内配置与二进制就绪；如需容器内跑容器由运行方按 G3 三必需参数启动）。
- Windows 原生 Podman machine 与 openKylin WSL 内均可用 `podman build`；至少一条真实路径完成构建验证，另一条路径以脚本语法检查 + 探测逻辑 dry-run 覆盖。

## Acceptance Criteria

### AC-1: 镜像工程目录完整（rule）
- **Type**: `rule`
- **Given**: `apps/dev-tools/openkylin-wsl-devkit/openkylin-dev-container/`
- **When**: 检查目录内容
- **Then**: 必须存在 Containerfile、entrypoint.sh、healthcheck.sh、conf/（sshd_config、supervisord.conf、jupyter、storage.conf）、scripts/build.ps1、scripts/build.sh、scripts/smoke.ps1、scripts/smoke.sh、README.md
- **Pass Condition**: 上述文件全部存在且非空
- **Evidence**: 目录清单（PowerShell Get-ChildItem 输出）

### AC-2: Containerfile 基底与源约束（rule）
- **Type**: `rule`
- **Given**: Containerfile 全文
- **When**: 静态检查
- **Then**: `FROM` 指向 `localhost/openkylin:3.0`（本地导入 WSL 3.0 rootfs，2026-10-09 用户裁定，取代官方 `latest`=2.0 SP1）；未添加任何第三方 apt 源（无 add-apt-repository / 自定义 sources.list 写入）；构建注释为英文
- **Pass Condition**: 三条件同时成立
- **Evidence**: Containerfile 静态检查记录

### AC-3: 真实构建成功（rule）
- **Type**: `rule`
- **Given**: 本机 Podman machine 可用
- **When**: 运行 `scripts/build.ps1`（或等价 podman build 命令）构建 `localhost/openkylin-dev:3.0`
- **Then**: 构建退出码 0，`podman image exists localhost/openkylin-dev:3.0` 返回 0
- **Pass Condition**: 构建成功且镜像存在
- **Evidence**: 构建日志（退出码、镜像清单）

### AC-4: 镜像内服务组件齐备（rule）
- **Type**: `rule`
- **Given**: 已构建镜像 `localhost/openkylin-dev:3.0`
- **When**: `podman run --rm` 执行组件探针
- **Then**: `sshd -t` 通过且 sshd 可启动；`jupyter --version`（或等效）输出版本；devuser `podman info --format {{.Host.Security.Rootless}}` 为 true（rootless 上下文）；`supervisord --version` 输出版本；`locale -a` 含 `zh_CN.UTF-8`；`date` 时区为 Asia/Shanghai；`id devuser` uid=1000
- **Pass Condition**: 七项探针全部通过
- **Evidence**: 探针命令输出记录

### AC-5: 双环境脚本可运行且禁隐式拉取（rule）
- **Type**: `rule`
- **Given**: build/smoke 脚本（.ps1 与 .sh 成对）
- **When**: 本机执行 `build.ps1` + `smoke.ps1` 真实运行；`build.sh`/`smoke.sh` 通过 bash 语法检查（`bash -n`）与 podman 探测 dry-run
- **Then**: 真实路径冒烟全部使用本地镜像（`--pull=never`），无任何 registry 拉取；.sh 脚本 `bash -n` 通过
- **Pass Condition**: 真实冒烟无拉取 + .sh 语法检查通过
- **Evidence**: 冒烟日志、`bash -n` 输出

### AC-6: 文档质量（rubric）
- **Type**: `rubric`
- **Dimension**: 镜像文档完整性与可操作性
- **Scale**: 1-5
- **Anchors**: 1 = 仅有零散说明，无法按文档构建/运行；3 = 覆盖用途/构建/运行/验证/边界，可复现构建；5 = 五要素齐备且含冒烟示例、故障排查与已知边界，可与 okw 文档互链
- **Pass Threshold**: >= 4
- **Evidence**: README 增补章节 + docs 指南 05 全文

## Open Questions

- [x] 是否需要在后续为 okw 增加 `okw image build/verify` 子命令以接管镜像构建？——**已落地（2026-10-09）**：新增 `okw image build`（发行版内 root 身份构建，基镜像默认禁拉、上下文自动同步发行版内 /tmp、`--format docker`）与 `okw image verify`（本地存在 + 静态探针 P1-P8 + 全量启动健康 + 服务探针含 Jupyter HTTP 200，全程 `--pull=never`）；在 openKylin WSL 发行版内真实端到端验证通过（verify 8 项全 PASS / build 25 步 exit 0，临时 tag smoke-test 与主镜像同 ID fe7b1bb318a6）；`okw image` CLI 见 `apps/dev-tools/openkylin-wsl-devkit/src/okw/image.py`（OQ-1 关闭）
- [x] openKylin WSL 发行版内 podman 是否已安装（`okw podman verify` 可查）？若已安装则补一条 WSL 内真实构建证据；否则以脚本语法检查 + dry-run 覆盖并记录。（2026-10-09 关闭：发行版预装 podman 5.7.0；已在发行版内 rootful 真实构建 + 冒烟全绿，见 review.md R1 F-2 闭合证据 `evidence/build-20261009-openkylin-wsl.log`、`evidence/smoke-20261009-openkylin-wsl.log`）
- [x] 官方 registry 是否存在 3.0 容器 tag？（2026-10-09 关闭：官方 `latest` 实测 2.0 SP1 LTS；已按用户裁定改用本地导入 WSL 3.0 rootfs 作基底，见 Background）
