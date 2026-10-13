---
title: "为 okw 增加 openKylin 桌面（UKUI / xrdp）支持"
status: "draft"
methodology: "seven-concepts-cmd: F→V→I→C"
content-sensitivity: "public"
source: "docs/knowledge/tech/openkylin-docs-wiki/concepts/04-desktop-usage.md; docs/knowledge/tech/openkylin-docs-wiki/references/wsl-desktop-startup-tutorial.md; docs/knowledge/tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md (§5.1); apps/dev-tools/openkylin-wsl-devkit/"
---

# 为 okw 增加 openKylin 桌面（UKUI / xrdp）支持

## Overview

- **Summary**：扩展现有 `apps/dev-tools/openkylin-wsl-devkit`（CLI `okw`），新增 `okw desktop preflight|install|verify` 子命令组，对已预装桌面的 openKylin 3.0 Desktop WSL2 发行版做只读预检、显式补齐桌面链路与只读验收；不创建新的并列应用，不安装桌面套件。
- **Purpose**：知识库已完成桌面链路落机实测（2026-10-08）：预装 UKUI 桌面经 xrdp（默认端口 3390）供 Windows 侧 `mstsc` 连接，但**首次登录会纯黑屏**（KWin 窗口管理器冷启动不驻留），需在默认用户 `~/.xsession` 补回 `XDG_RUNTIME_DIR` 并加看门狗。把这条**已验证**路径纳入 `okw`，让开发者可确定性预检、可逆补齐、只读验收，避免"服务 active 即桌面可用"的错觉。
- **Target Users**：在 Windows + WSL2 中使用 openKylin 3.0 Desktop WSL 镜像、希望在 Windows 上获得完整 UKUI 桌面会话的开发者。

## Goals

- G1：新增 `okw desktop preflight <name> [--port]`、`okw desktop install <name> --yes [--port]`、`okw desktop verify <name> [--port]` 三个叶子命令，并在 `cli/main.py` 完成子组分发。
- G2：`preflight` 只读检查结构项（发行版存在/WSL2/openKylin 身份/systemd）与运行时项（xrdp 与 xrdp-sesman 服务、发行版内 `:<port>` 监听、默认用户 UID、`~/.xsession` 看门狗标记），逐项 PASS/FAIL/UNKNOWN。
- G3：`install --yes` 以 root 幂等 `systemctl enable --now xrdp xrdp-sesman`，并以默认用户备份并补齐 `~/.xsession` 看门狗（已含标记则跳过），最后只读复验；不漏 `--yes` 零写入。
- G4：`verify` 只读复验桌面链路，并附加 Windows 侧 `localhost:<port>` 回环可达性；`--port` 默认 3390。
- G5：复用现有 `okw.distro` WSL 封装与 `okw.podman` 的 PASS/FAIL/UNKNOWN 报告容器与退出码纪律，保持零第三方运行时依赖。

## Non-Goals

- 不新建另一个桌面或远程桌面管理应用；不改变 `okw` 包名与入口。
- 不安装桌面套件（xrdp/ukui-session/kwin-x11 等）、不改软件源、不改 `wsl.conf`、不改默认发行版/默认用户；只作用于**已预装**桌面的镜像。
- 不自动下载或导入 Desktop WSL 镜像；不替代 `wsl --import`。
- 不推送、配置或读取任何凭据；不修改 xrdp 自签证书。
- 不实现启动器 GUI、不自动拉起 `mstsc`（连接仍由用户在 Windows 侧发起）。

## Background & Context

- 知识库 `concepts/04-desktop-usage.md` 与 `references/wsl-desktop-startup-tutorial.md`：桌面运行在 WSL2 内，Windows 侧经 `mstsc` 连 `localhost:3390`；登录窗 Session 必须选 `xorg`；弱口令 `openkylin/openkylin` 首登需 `passwd`。
- `references/wsl-dual-image-selection.md` §5.1（2026-10-08 实测）：首登黑屏根因为 KWin `kwin_x11` 冷启动不驻留——`startwm.sh` 会 `unset XDG_RUNTIME_DIR`；修复为改写 `~/.xsession`（先备份）补回该变量并加前 ~15 秒幂等看门狗，脚本原文以本 spec 为证据落地。
- 与 Podman/AI 扩展同构：`okw` 以标准库实现，WSL 调用经 `okw.distro` 统一封装（`WSL_UTF8=1`、错误归一、超时）；`okw.podman` 已沉淀 `CheckItem`/`PreflightReport`/`VerifyReport`/`InstallReport` 与退出码纪律，本变更复用而非重写。

## Functional Requirements

### Requirement: 只读预检桌面链路

`okw desktop preflight <name>` SHALL 只读盘点结构项与运行时项，SHALL NOT 写文件、改服务、apt、改 `wsl.conf`。

#### Scenario: 链路就绪

- **WHEN** 目标为已注册的 openKylin WSL2、`wsl.conf` 启用 systemd、xrdp 已装且 xrdp/xrdp-sesman active、发行版内 `:<port>` 监听、默认用户 UID 1000、`~/.xsession` 含 `XDG_RUNTIME_DIR` 与 `kwin_x11`
- **THEN** SHALL 逐项输出 PASS 并以 0 结束；SHALL NOT 发生任何写入

#### Scenario: 链路未就绪

- **WHEN** 存在系统/服务/端口/看门狗任一 FAIL
- **THEN** SHALL 标 FAIL 并给出中文修复方向（含 `okw desktop install <name> --yes` 与"仅作用于已预装桌面镜像"提示），以 1 结束

### Requirement: 显式确认后补齐桌面链路

`okw desktop install <name>` SHALL 仅在 `--yes` 时补齐；SHALL NOT 安装桌面套件、改源或改 `wsl.conf`。

#### Scenario: 缺少确认时零写入

- **WHEN** 用户运行 `okw desktop install <name>` 而未提供 `--yes`
- **THEN** SHALL 仅打印编号副作用清单并以退出码 2 结束，不发生任何写入或子进程写操作

#### Scenario: 确认后补齐

- **WHEN** 用户运行 `okw desktop install <name> --yes` 且结构项与 xrdp 已装通过
- **THEN** SHALL 以 root `systemctl enable --now xrdp xrdp-sesman`，并以默认用户备份（`~/.xsession.bak-<时间戳>`）后写入看门狗（已含标记则保持），最后只读复验
- **WHEN** xrdp 缺失或结构项 FAIL
- **THEN** SHALL 停止并提示改用 Desktop WSL 镜像，不尝试 apt 安装桌面套件

### Requirement: 只读验收桌面链路

`okw desktop verify <name>` SHALL 只读复验桌面链路并附加 Windows 侧回环端口可达性。

#### Scenario: 验收通过 / 未通过

- **WHEN** 运行时项全部 PASS 且 Windows 侧 `localhost:<port>` 可连
- **THEN** SHALL 逐项 PASS 并以 0 结束；任一项 FAIL 或端口不可达 SHALL 以 1 结束并说明修复方向

### Requirement: 完成 CLI 装配与文档一致性

桌面能力 SHALL 作为现有 `okw` 子命令实现，更新命令面守卫、用户文档与 apps 索引中的既有应用说明。

#### Scenario: 命令面与既有命令不回归

- **WHEN** 运行 `okw desktop --help`（空组）与既有命令
- **THEN** 空组回打帮助并退出 2；注册表键集、parser 叶子集与快照逐字一致；既有命令参数、默认星标保护与退出码保持兼容

## Non-Functional Requirements

- **NFR-1（运行时依赖）**：仅用 Python 标准库与现有 scikit-build-core 构建，不增加第三方运行时依赖。
- **NFR-2（WSL 调用）**：SHALL 复用 `okw.distro`；需 root 时显式 `-u root`；单批运行时探针只读。
- **NFR-3（测试）**：单测不得真实写系统/触网（Windows 端口探测须可注入）。整体覆盖率 ≥80%。
- **NFR-4（输出）**：错误 SHALL 以中文说明失败阶段与后续动作；不写入凭据。
- **NFR-5（兼容）**：宿主 Windows + WSL2，目标 openKylin 3.0 Desktop WSL2；`--port` 默认 3390。

## Constraints

- **Technical**：只在已预装桌面的镜像上操作；端口以 `/etc/xrdp/xrdp.ini` 为准，`--port` 需与之同步。
- **Security**：preflight/verify 只读；install 必须 `--yes`；`~/.xsession` 改写可逆（备份），不改系统文件与证书。
- **Compatibility**：不要求 GPU/大模型；依赖发行版已导入且 systemd 启用。

## Assumptions

- 面向知识库记录的 openKylin 3.0 Desktop WSL 镜像（huanghe）。
- 默认用户为 `openkylin`（uid 1000），弱口令，首登需 `passwd`。
- xrdp 预装且 systemd 拉起；`--port` 默认为 3390。

## Acceptance Criteria

### AC-1：preflight 只读且判定清晰

- **Type**：`rule`
- **Given**：发行版不存在、systemd 未启用、xrdp 缺失、服务非 active、端口未监听、看门狗缺失、全通过等情形
- **When**：执行 `okw desktop preflight <name>`
- **Then**：每种情形输出可区分的逐项结果与正确退出码；不发生写入、apt、服务变更
- **Pass Condition**：隔离测试断言 WSL 调用序列、退出码与文件系统前后快照全部通过
- **Evidence**：desktop preflight 单元测试与副作用哨兵断言

### AC-2：install 有显式确认与镜像边界

- **Type**：`rule`
- **Given**：已预装桌面的 openKylin WSL2 发行版
- **When**：无 `--yes` 或有 `--yes` 执行补齐
- **Then**：无确认时仅打印副作用清单、零写入（退出码 2）；确认后仅 `systemctl enable --now xrdp xrdp-sesman`（root）与默认用户 `~/.xsession` 补齐（先备份）；不改源/`wsl.conf`/默认发行版/用户，不装桌面套件
- **Pass Condition**：mock WSL 序列与快照断言通过
- **Evidence**：install 单元测试与 CLI 集成测试

### AC-3：看门狗补齐安全可逆且幂等

- **Type**：`rule`
- **Given**：`~/.xsession` 缺失、已有但不含标记、已含标记
- **When**：执行 `okw desktop install <name> --yes`
- **Then**：缺失/不含标记时先备份再写入含 `XDG_RUNTIME_DIR` 与 `kwin_x11` 的脚本；已含标记时保持 `unchanged`；脚本以 `exec ukui-session` 收尾
- **Pass Condition**：补齐脚本参数与幂等分支断言通过
- **Evidence**：`_xsession_patch_script` 与 `XSESSION_WATCHDOG` 断言

### AC-4：verify 确认真实上下文

- **Type**：`rule`
- **Given**：运行时项 FAIL、Windows 端口不可达、全通过等输出
- **When**：执行 `okw desktop verify <name>`
- **Then**：结果准确反映各项，全通过退出 0，任一 FAIL/端口不可达非零退出；`--port` 正确透传到检查与提示
- **Pass Condition**：运行时探针与端口探测 mock 矩阵覆盖每项
- **Evidence**：verify 单元测试

### AC-5：命令面守卫与快照一致

- **Type**：`rule`
- **Given**：parser、注册表、CLI 快照与架构守卫
- **When**：对照注册表键集、parser 叶子集、空组帮助与快照
- **Then**：新增 `desktop preflight/install/verify` 三键在注册表、parser 与快照中逐字一致；`okw desktop` 空组回打帮助并退出 2；快照重新生成且字节稳定
- **Pass Condition**：更新后的命令注册表/架构/快照测试全部通过
- **Evidence**：守卫测试与再生成的 cli_surface.json

### AC-6：文档与区域索引一致

- **Type**：`rule`
- **Given**：CLI help、README、命令参考/新增桌面指南、apps 索引
- **When**：核对各入口
- **Then**：命令名、`--yes`、只读/可逆、"不安装桌面套件/不改源/不改 wsl.conf"边界一致；新增 `08-desktop.md` 入 toctree；`apps/AGENTS.md`（两处）与 `apps/README.md` 更新既有 okw 描述而非新增应用
- **Pass Condition**：文档命令与 `okw desktop --help` 逐项对应、链接有效
- **Evidence**：文档核对与链接检查记录

## Open Questions

- 产品范围无待决项。目标发行版是否为已预装桌面的镜像，是安装前/运行时的门禁。
- 真实桌面联通（`mstsc` 进入 UKUI）需人工交互；2026-10-13 已在 `openKylin-3.0-desktop` 完成只读真实验收（preflight/verify 全 PASS），`mstsc` 人工步骤不代操作、如实标注。
- 真实验收发现并修复一处 Windows `wsl.exe` 桥接问题（`$()` 内嵌双引号被吞）：见 tasks.md Issue I-1。
