---
title: "为 okw 增加 openKylin 桌面（UKUI / xrdp）支持 - 实施计划"
status: "implemented"
methodology: "seven-concepts-cmd: F→V→I→C"
content-sensitivity: "public"
source: ".trae/specs/infra-env/extend-okw-openkylin-desktop/spec.md"
---

# 为 okw 增加 openKylin 桌面（UKUI / xrdp）支持 - 实施计划

## Task 1: 增加桌面链路只读预检

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新增 `src/okw/desktop.py` 领域模块与 `src/okw/commands/desktop_cmds.py` 的 `cmd_preflight`；在现有命令树中增加 `desktop preflight <发行版> [--port]`。
  - 复用 `okw.distro` 的发行版检查与 WSL 封装、`okw.podman` 的 `CheckItem`/`PreflightReport` 报告容器与退出码纪律。
  - 结构项：发行版存在、WSL2、openKylin 身份（`ID=openkylin`）、`/etc/wsl.conf` 的 `[boot] systemd=true`（xrdp 依赖 systemd 拉起）。
  - 运行时项以**单批只读探针**获取：xrdp 可执行文件、`xrdp`/`xrdp-sesman` 服务 `is-active`、发行版内 `:<port>` 监听（`ss -ltn`）、默认用户 UID、`~/.xsession` 看门狗标记（`XDG_RUNTIME_DIR`+`kwin_x11`）。
  - 预检不得 apt/写文件/改服务/改默认发行版；缺 xrdp 时提示改用 Desktop WSL 镜像。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-1.1：发行版不存在、WSL1、非 openKylin、`wsl.conf` 不可读/systemd 未启用、xrdp 缺失、服务非 active/unknown、端口未监听、UID 非 1000、看门狗缺失、全通过等场景均有测试并返回预期退出码。
  - `rule` TR-1.2：预检所有 WSL 调用均为只读；无 apt/写入/服务变更；探针为单批调用。
  - `rubric` TR-1.3：结构失败与运行时失败的中文方向可区分（含 `okw desktop install` 与"仅作用于已预装桌面镜像"提示）。
- **Completion Evidence**:
  - `desktop.add_structural_checks`/`add_runtime_checks`/`_probe_runtime`/`parse_runtime_probe` 落地；探针为单批 bash（`__TOKEN__` 占位避免 shell `printf %s` 与 Python `%` 冲突）。
  - `tests/test_desktop.py::TestDesktopPreflight` 与 `TestDesktopBranches`（结构/运行时全分支）全通过。

## Task 2: 显式确认后补齐桌面链路

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `desktop.py`/`desktop_cmds.py` 实现 `okw desktop install <发行版> --yes [--port]`；无 `--yes` 时在任何写入前仅打印编号副作用清单并以退出码 2 中止。
  - `--yes` 后：结构门 + xrdp 已装门（缺则提示改用 Desktop 镜像，不 apt 安装桌面套件）→ root `systemctl enable --now xrdp xrdp-sesman` → 默认用户身份备份并补齐 `~/.xsession`（已含标记则 `unchanged`）→ 只读复验。
  - `~/.xsession` 内容以知识库 §5.1 实测脚本落地：补回 `XDG_RUNTIME_DIR`、前 ~15 秒幂等看门狗、`exec ukui-session`；先 `cp` 备份为 `~/.xsession.bak-<时间戳>`，可逆。
  - 不改软件源/`wsl.conf`/默认发行版/用户，不安装桌面套件，不推送凭据。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-2.1：未提供 `--yes` 时断言零写入（`calls == []`），仅打印副作用清单且退出码 2。
  - `rule` TR-2.2：确认后命令仅针对目标发行版，root 执行 `systemctl enable --now`，默认用户执行 `~/.xsession` 补齐；无源修改、桌面套件安装或默认发行版/用户变更。
  - `rule` TR-2.3：xrdp 缺失、systemd 未启用、`systemctl` 失败、`~/.xsession` 写入失败四类路径均隔离测试，fail-closed。
- **Completion Evidence**:
  - `desktop.install_run`/`_xsession_patch_script`/`XSESSION_WATCHDOG` 落地；备份+幂等+`exec ukui-session` 断言通过。
  - `tests/test_desktop.py::TestDesktopInstall` 与 `TestDesktopBranches`（启用失败/写入失败）覆盖缺 --yes、xrdp 缺失、全成功、幂等、systemd 未启用、失败停止。

## Task 3: 增加桌面链路只读验收

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现 `okw desktop verify <发行版> [--port]`：在 preflight 同批运行时检查之上，附加 Windows 侧 `localhost:<port>` 回环可达性（`socket.create_connection`，只探回环、不触网卡）。
  - 结构失败即返回，不进入运行时/端口探测；全通过退出 0，任一 FAIL 或端口不可达退出 1。
  - `--port` 默认 3390，并透传到检查、示例与提示。
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-3.1：运行时项 FAIL、Windows 端口不可达、全通过、结构失败等矩阵均被覆盖，退出码正确。
  - `rule` TR-3.2：`--port` 正确透传到探测与输出；端口探测可注入，无真实网络依赖。
- **Completion Evidence**:
  - `desktop.verify_run`/`probe_windows_port` 落地；`tests/test_desktop.py::TestDesktopVerify`/`TestDesktopBranches`（结构失败短路、真实端口开关）全通过。

## Task 4: 完成 CLI 装配、命令面守卫与用户文档

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 在 `cli/parser.py` 增加 `desktop` 子命令组（dest `desktop_cmd`，preflight/install/verify，均可选 `--port`）；`cli/main.py` 增加分发分支；`commands/__init__.py` 注册三个 handler。
  - 更新命令面守卫：`test_command_registry.py`（叶子 20→23、键集、导入副作用断言）、`test_cli_surface.py`（期望叶子）、`test_cli_architecture.py`（空组 parametrize 增 `desktop`），再生成 `snapshots/cli_surface.json`。
  - 更新 README（桌面段）、`docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md`，新增 `08-desktop.md` 并在 `index.md` 任务表与 toctree 登记；更新 `apps/AGENTS.md`（两处）与 `apps/README.md` 中现有 okw 描述，不新增应用条目。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-4.1：全量测试通过、总覆盖率 ≥80%、`desktop.py` ≥90%。
  - `rule` TR-4.2：注册表键集、parser 叶子集与快照逐字一致；`okw desktop` 空组回打帮助退出 2；既有子命令无回归；parser 行数预算内。
  - `rule` TR-4.3：README/命令参考/08 指南/`okw desktop --help` 对命令名、`--yes`、只读/可逆、"不安装桌面套件/不改源/不改 wsl.conf"的说明一致。
- **Completion Evidence**:
  - parser/main/注册表装配完成；命令面守卫与快照同步（叶子 23）。
  - 全量测试 **531 项通过**、TOTAL 覆盖率 **97%**、`desktop.py`/`desktop_cmds.py` **100%**；parser.py 390 行（预算 400）、main.py 57 行（预算 300）。
  - 文档：app README、`02-command-reference.md`、新增 `08-desktop.md`、`index.md`（任务表+toctree）、`apps/AGENTS.md`（两处）、`apps/README.md`、本 spec 目录均更新。

## Task 5: 在可用 openKylin Desktop WSL2 环境执行真实验收

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 只读运行 `okw desktop preflight/verify openKylin-3.0-desktop`，真实记录结构项、服务/端口、看门狗与 Windows 侧回环端口。
  - `mstsc` 进入 UKUI 属人工步骤，本次不代操作；`install --yes` 本机无需执行（`~/.xsession` 已含看门狗，`install` 仅在缺失时写入）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-5.1：真实记录发行版身份、结构项、服务/端口、看门狗状态；未执行步骤注明原因。
  - `rule` TR-5.2：真实验证不改默认发行版/软件源/`wsl.conf`；不触其他发行版。
- **Completion Evidence**（2026-10-13，真实 openKylin-3.0-desktop WSL2，只读）:
  - `okw desktop preflight openKylin-3.0-desktop` → 退出 **0**；10 项全 PASS（WSL2/openKylin 身份/systemd/xrdp+xrdp-sesman active/发行版内 :3390 监听/uid 1000/~/.xsession 含 XDG_RUNTIME_DIR 与 kwin_x11）。
  - `okw desktop verify openKylin-3.0-desktop` → 退出 **0**；在 preflight 之上附加「Windows 侧 localhost:3390 回环端口可达」PASS。
  - 全程只读：未改默认发行版/软件源/`wsl.conf`、未触其他发行版；默认发行版星标保持 `podman-machine-default`。
  - 未代操作 `mstsc`（人工步骤）；`install --yes` 未执行（真实 `~/.xsession` 已含看门狗），其写入路径改以 `/tmp` 安全等价验证（见 Issue I-1）。

## Issue I-1: 修复 Windows wsl.exe 桥接下 `$()` 内嵌双引号导致看门狗误判

- **Status**: `completed`
- **Priority**: high
- **Source**: Task 5 真实只读验收（`preflight` 首跑误报「首登黑屏看门狗 FAIL」）→ 直接命中 AC-1/AC-4
- **Description**:
  - 现象：真实发行版 `~/.xsession` 明明含 `XDG_RUNTIME_DIR` 与 `kwin_x11`，探针却恒报 `missing`。
  - 根因（实测定位）：探针把脚本作为**单个 argv** 经 Windows `wsl.exe` 桥接传递，`"$(test -f "$HOME/.xsession" …)"` 中 `$()` 内的双引号被桥接转义吞掉，`test -f`/`grep` 恒为假。对照实验：同语句去掉内层引号（`$HOME/.xsession` 未加引号）后立即返回 `ok`。
  - 修复：探针与 `~/.xsession` 补齐脚本一律**不在 `$()` 内嵌双引号**（家目录无空格，用未加引号的 `$HOME` 路径）；探针加静态回归守卫断言 `"$HOME` 与 `$(test -f "` 不出现。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-I1.1：生成的探针与补齐脚本不含 `$()` 内嵌双引号；补齐脚本在真实桥接下 `patched`→`unchanged` 幂等、备份落盘、写入含标记、以 `exec ukui-session` 收尾。
  - `rule` TR-I1.2：真实 `okw desktop preflight/verify` 对含看门狗的发行版返回全 PASS / 退出 0。
- **Completion Evidence**（2026-10-13）:
  - 对照实验：`A`（嵌套引号）→`missing`；`B`（未加引号）→`ok`。
  - 补齐脚本经 `"$HOME"`→`/tmp/okwtest` 安全等价改写后在真实 WSL 运行：run1 `patched`（生成 `.xsession.bak-<时间戳>`、标记命中 3 处、末行 `exec ukui-session`），run2 `unchanged`（幂等）；全程未触真实家目录。
  - 复跑 `preflight`/`verify` 均退出 0（10/11 项 PASS）；`tests/test_desktop.py` 新增守卫，全量 **532 passed**，`desktop.py` 覆盖 **100%**。

## Task Dependencies

- Task 1 是只读预检基础；Task 2 与 Task 3 依赖 Task 1，可在其完成后并行实施。
- Task 4 依赖 Task 2 和 Task 3。
- Task 5 依赖 Task 4 的可运行实现与文档。
