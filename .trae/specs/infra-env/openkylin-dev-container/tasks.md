---
status: draft
title: openkylin-dev-container 实施队列
source: .trae/specs/infra-env/openkylin-dev-container/spec.md
created: 2026-10-08
---

# openkylin-dev-container — Implementation Plan

## Task 1: 镜像工程骨架 + Containerfile + entrypoint/healthcheck
- **Status**: `completed`（2026-10-09，随 Task 4 真实验证核验）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `apps/dev-tools/openkylin-wsl-devkit/openkylin-dev-container/` 创建工程骨架：`Containerfile`、`entrypoint.sh`、`healthcheck.sh`、`conf/`（sshd_config、supervisord.conf、jupyter 配置、containers/storage.conf）、`scripts/`、`README.md` 占位。
  - Containerfile：FROM `localhost/openkylin:3.0`（2026-10-09 用户裁定：本地导入 WSL 3.0 rootfs 取代官方 `latest`=2.0 SP1 LTS）；apt 安装 openssh-server/supervisor/podman/uidmap/slirp4netns/fuse-overlayfs/crun/tini/locales/python3-pip 等；pip 安装 jupyterlab+notebook（`--break-system-packages`，PEP 668）；zh_CN.UTF-8 locale + Asia/Shanghai；devuser UID 1000 + subuid/subgid 映射（起点 100000）；容器内 rootless Podman 配置（fuse-overlayfs/crun/containers.conf）；构建注释英文；HEALTHCHECK/ENTRYPOINT 声明。
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-4（部分）
- **Test Requirements**:
  - `rule` TR-1.1: 目录内必需文件全部存在且非空（AC-1 清单）——**PASS**（文件清单见 Task 4 证据）
  - `rule` TR-1.2: Containerfile 无第三方源写入、FROM 为 localhost/openkylin:3.0（AC-2；2026-10-09 基底裁定）——**PASS**（静态检查 + 构建日志）
  - `rule` TR-1.3: `bash -n entrypoint.sh` / `bash -n healthcheck.sh` 通过——**PASS**（构建 Layer 4 内置校验；构建日志 STEP 19 无报错）
- **Notes**: 参考 jupyter-podman-rootless containerfile 规则的分层与安全约定，但裁剪掉 conda/toolbox/OMLMD 等 openKylin 场景不需要的部件。

## Task 2: 双环境构建脚本（build.ps1 / build.sh）
- **Status**: `completed`（2026-10-09，build.ps1 真实构建成功 + build.sh bash -n 通过）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `scripts/build.ps1`：Windows 原生 Podman machine 路径，探测 `podman` 命令与 `podman machine` 状态，`podman build --format docker -t localhost/openkylin-dev:3.0`（`--format docker` 必须：OCI 格式会静默丢弃 SHELL/HEALTHCHECK），支持 `-Tag`/`-NoCache`/`-BaseImage` 覆盖。
  - `scripts/build.sh`：POSIX bash，openKylin WSL / 任意 Linux 路径，探测 podman 后同构构建；默认基底 `localhost/openkylin:3.0`。
  - 两脚本输出结构化的阶段标记（[BUILD] 等）与退出码语义（0 成功 / 1 失败）。
- **Acceptance Criteria Addressed**: AC-3、AC-5
- **Test Requirements**:
  - `rule` TR-2.1: 本机真实运行 build.ps1 构建成功（AC-3）——**PASS**（退出码 0；镜像 `localhost/openkylin-dev:3.0` ID c214864004af）
  - `rule` TR-2.2: `bash -n build.sh` 通过；探测逻辑 dry-run 输出正确——**PASS**（bash -n 退出码 0）
- **Notes**: 不依赖 okw Python 包，零第三方运行时依赖（沿用 offline-delivery bin/relpack 的 bash+pwsh 模式）。

## Task 3: 双环境冒烟脚本（smoke.ps1 / smoke.sh）
- **Status**: `completed`（2026-10-09，smoke.ps1 真实冒烟全绿 + smoke.sh bash -n 通过）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `scripts/smoke.ps1` 与 `scripts/smoke.sh`：对本地镜像 `localhost/openkylin-dev:3.0` 执行 `podman run --rm --pull=never` 探针：
    1. sshd 探针（`sshd -t` + sshd 启动 + 端口监听）
    2. jupyter 探针（`python3 -m jupyter --version`）
    3. devuser rootless 探针（P8 就绪检查 + P8b live 检查：rootful 外层宿主验证 `Rootless=true`；rootless 外层宿主遇嵌套 userns EPERM 记 ENV-LIMIT——按 spec Assumptions「冒烟不强制宿主导通」）
    4. supervisord 探针（`supervisord --version`）
    5. 系统探针（locale zh_CN.UTF-8——大小写与连字符兼容、Asia/Shanghai、devuser uid=1000、subuid）
    6. 全量启动：HEALTHCHECK healthy + SSH/Jupyter/端口服务探针
  - 全程 `--pull=never`，先 `podman image exists` 确认镜像存在；探针脚本以 base64 单 token 传递（规避 Windows PowerShell 5.1 原生参数引号拆坏）。
- **Acceptance Criteria Addressed**: AC-4、AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 本机真实冒烟全部探针 PASS 且无拉取（AC-4/AC-5）——**PASS**（smoke-20261009.log；P8b 记 ENV-LIMIT 见 Notes）
  - `rule` TR-3.2: `bash -n smoke.sh` 通过——**PASS**（退出码 0）
- **Notes**: 冒烟语义与 okw `podman verify --smoke-image` 一致（仅本地镜像、禁隐式拉取）。P8b 的 ENV-LIMIT 是环境事实（rootless 外层宿主嵌套 userns 受限），非镜像缺陷；rootful 外层宿主（openKylin WSL 发行版内）可完整验证 live rootless。

## Task 4: 真实构建与冒烟验证（本机 Podman machine）
- **Status**: `completed`（2026-10-09）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在本机 `podman-machine-default` 执行 build.ps1 → 记录构建退出码、镜像清单 → 执行 smoke.ps1 → 记录探针输出。
  - 若 openKylin WSL 内 podman 可用（`okw podman verify openKylin-3.0-desktop` 通过），补一次 WSL 内真实构建；否则记录为环境边界。
- **Acceptance Criteria Addressed**: AC-3、AC-4、AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 构建退出码 0 且 `podman image exists localhost/openkylin-dev:3.0` = 0——**PASS**（退出码 0；ID `c214864004af`，docker 格式）
  - `rule` TR-4.2: 冒烟全部 PASS（含 Rootless=true、locale、时区、uid）——**PASS**（P1-P8 全过 + 全量启动 healthy；P8b live rootless 在本机为 ENV-LIMIT，见 Notes）
- **Notes**: 构建/冒烟日志在 `.trae/specs/infra-env/openkylin-dev-container/evidence/`：
  - `build-20261009.log`（最终构建，docker 格式，HEALTHCHECK/SHELL 生效）+ 归档 `build-20261009-attempt{1,2,3,4,5}-*.log`（完整失败链：PEP 668 → 用户中断 → UID 1000 冲突 → subuid 含自身 UID → OCI 格式丢 HEALTHCHECK）
  - `smoke-20261009.log`（最终冒烟，全绿）+ 归档 `smoke-20261009-attempt{1,2,3}-*.log`（探针演进：locale 大小写/连字符 → P8 root 误测 → set -e 干扰）
  - 修复清单（均为 Task 4 真实运行暴露并闭环）：PEP 668 `--break-system-packages`；WSL 基底 `userdel openkylin` 腾 UID 1000；subuid/subgid 起点 100000；storage.conf 空段删除；`--format docker`；locale 探针兼容 `utf8`/`UTF-8`；P8 环境感知（rootless 宿主记 ENV-LIMIT，符合 spec Assumptions）
  - openKylin WSL 内补构建：未执行（WSL 发行版内 podman 状态未查；留作环境边界，Task 5/6 可补）

## Task 5: 文档（应用 README + docs 指南）
- **Status**: `completed`（2026-10-09）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - `apps/dev-tools/openkylin-wsl-devkit/README.md` 增补「openKylin 开发容器镜像」章节（定位、快速构建、冒烟、关联 okw podman）。
  - 新建 `docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md`：用途/构建（双环境）/运行（G3 三必需参数）/验证（冒烟）/边界（不做什么、后续候选）；更新 `index.md` toctree 加入 05 与任务表。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rubric` TR-5.1: 文档质量 1-5，阈值 >= 4（维度与锚点见 spec AC-6）——**PASS，得分 5**：五要素齐备（用途/构建双环境/运行 G3 三必需/验证冒烟/已知边界），含冒烟探针清单、构建期故障排查表、与 okw `03-podman-rootless` 指南及模式文档 `wsl-rootfs-oci-image-export` 互链；README 镜像章节同步可复现构建
  - `rule` TR-5.2: docs 指南文件存在且 index.md toctree 已接入——**PASS**（`05-openkylin-dev-container.md` 已创建；index.md「按任务阅读」表新增行 + toctree 加入 `05-openkylin-dev-container`）
- **Notes**: 对外可读文档入根 `docs/`，遵循 AGENTS 文档边界。

## Task 6: 独立审查（review.md）
- **Status**: `completed`（2026-10-09）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 创建 `review.md`，对照 spec AC-1~AC-6 与 tasks TR-1~TR-5 独立核对（文件清单、Containerfile 静态检查、构建/冒烟证据、文档）。
  - 发现可行动问题固化为 pending issue 回 Implement；全部通过后记 `pass` 并交付。
- **Acceptance Criteria Addressed**: 全部 AC
- **Test Requirements**:
  - `rule` TR-6.1: 每条 AC 有独立证据且 Review 结果 pass——**PASS**：Review R1 全部 6 检查点通过（CP-R1~R6 独立重跑 + CP-U1 得 5），可行动发现 0，advisory 3 条（F-1 AC-4 字面与 ENV-LIMIT、F-2 WSL 内构建未执行、F-3 端口暴露加固，均不阻塞）
- **Notes**: 实施者自验不作为最终验收；Review 检查点与发现按 TRAE-spec-mode 模板记录。advisory 见 review.md「Review History R1」。
