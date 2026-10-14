---
name: openkylin-wsl-devkit
version: 1.0.0
description: "openKylin on WSL 开发链路（okw CLI，apps/dev-tools/openkylin-wsl-devkit）操作与项目开发指南。当用户提到 okw、openKylin WSL 导入/安装/验收、发行版内装 rootless podman、okw podman/compose/image 排错、xuan-compose（xc）引导、openKylin 开发容器镜像构建、deb/dput 脚手架，或要求修改该项目源码与测试时，必须使用此技能。封装双镜像导入、五步环境验收、rootless Podman 三步链、写入类操作 --yes 显式授权门、verify 禁隐式拉取、CLI 快照再生成门禁、Python 3.10 兼容红线与 PATH 裁剪环境全路径调用纪律。不要用于 Windows 宿主 podman machine 运维（路由 jpman-podman-ops）、client podman-compose 叠加栈（compose-overlay-ops）或 WSL VHDX 瘦身（wsl-vhdx-compact-cmd）。"
argument-hint: "<操作> [list|status|import|verify|podman|compose|image|scaffold|ref...] [选项]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/openkylin-wsl-devkit/**"
  - "apps/dev-tools/openkylin-wsl-devkit/**"
title: "openKylin WSL 开发链路 (okw DevKit)"
x-toml-ref: "../../../.meta/toml/.agents/skills/openkylin-wsl-devkit/SKILL.toml"
---
# openKylin WSL 开发链路 (okw DevKit)

## 1. Skill ID

`openkylin-wsl-devkit`

## 2. 功能描述

封装本仓应用 **openkylin-wsl-devkit**（`apps/dev-tools/openkylin-wsl-devkit`，Python ≥3.10、零第三方运行时依赖、MIT 许可）的 CLI `okw`——把 openKylin on WSL 的已验证操作固化为七组命令（发行版生命周期 + podman/compose/image 三个子命令组 + scaffold/ref）。本 Skill 不重复实现 CLI，而是提供**任务路由、命令链顺序、环境纪律与开发门禁**。

核心能力：

- **双镜像导入与五步环境验收**（gzip 魔数校验、超时、中文分诊；os-release/用户/UID/systemd/包数）
- **发行版内 rootless Podman 三步链**与 xuan-compose（xc）用户级引导
- **openKylin 开发容器镜像构建与 P1–P8 探针验收**（全程禁隐式拉取）
- **deb/dput 打包脚手架**与只读知识速记（ref）
- **项目开发门禁**（CLI 快照再生成、Python 3.10 兼容红线、覆盖率基线）

> **为什么需要这个 Skill？** okw 的操作顺序与约束（先 preflight 再 install、verify 宁可 FAIL 不隐式拉取、漏 `--yes` 零写入）分散在 parser 源码、6 篇 guides 与实机踩坑中；没有门面时，Agent 容易手写裸 `wsl --import`、见到退出码 2 就擅自补参、或为让冒烟通过而加隐式 pull——每一种都绕过了 okw 内置的安全契约。

**与姊妹 Skill 的边界**：

| 需求 | 路由 |
|------|------|
| openKylin 发行版内操作 / okw 命令 / 本项目开发 | **本 Skill** |
| Windows 宿主侧 podman machine、Jupyter 容器、嵌套 Podman | [jpman-podman-ops](../jpman-podman-ops/SKILL.md) |
| client 下 quant/native/monetize compose 叠加栈运维 | [compose-overlay-ops](../compose-overlay-ops/SKILL.md) |
| 新建 client 叠加栈 | [client-overlay-scaffold](../client-overlay-scaffold/SKILL.md) |
| WSL 宿主磁盘清理、VHDX 压缩、GPU、自启 | [wsl-ops-cmd](../wsl-ops-cmd/SKILL.md)、[wsl-vhdx-compact-cmd](../wsl-vhdx-compact-cmd/SKILL.md) |
| docker save 镜像转任意 WSL 发行版 | [docker-wsl-bridge-cmd](../docker-wsl-bridge-cmd/SKILL.md) |

## 3. 何时使用本技能

当用户提到以下任何内容时触发：

- "okw"、`okw list/status/import/export/verify/exec`、"openKylin WSL"、"openKylin 镜像导入"
- "openKylin 验收"、"导入 openKylin 3.0"、"基础镜像/桌面镜像"、"双镜像并存"
- "发行版里装 podman"、"rootless podman"、`okw podman preflight/install/verify`、subuid/subgid 映射
- "xuan-compose"、"xc"、`okw compose`、"uv 装 compose"、"compose 冒烟"
- `okw image build/verify`、"openKylin 开发容器镜像"、"开发容器 HEALTHCHECK"
- `okw scaffold`、"deb 打包骨架"、"OKBS dput"、`okw ref`、openKylin 知识速记
- "改 okw"、"修改 openkylin-wsl-devkit"、"okw 加命令"、"cli_surface 快照"、该应用下的测试失败

> **关于触发**：即使没有明确说"用 skill"，只要涉及 okw CLI 操作或 `apps/dev-tools/openkylin-wsl-devkit` 源码修改，就应使用本技能，不要手写裸 `wsl --import`/`wsl --manage` 或凭 Docker 经验在 openKylin 发行版内排障。okw 不替代 `wsl --install`、不下载镜像、不调用 OKBS/factory API、不负责其他发行版的通用管理。

## 4. 任务路由决策树

```
用户意图是什么？
├─ 导入/查看/验收 openKylin 发行版
│  ├─ 导入镜像            → okw import <镜像.wsl> --name <名称> --location <目录>
│  ├─ 查发行版/状态        → okw list → okw status <name>
│  └─ 五步环境验收         → okw verify <name>
├─ 发行版内 rootless Podman
│  └─ okw podman preflight <name> → install <name> --yes → verify <name>
├─ Podman 就绪后引导 xuan-compose
│  └─ okw compose preflight <name> --source <源> → install <name> --yes --source <源> → verify <name> --smoke
├─ openKylin 开发容器镜像
│  └─ okw image build <name> → okw image verify <name>
├─ 打包骨架 / dput 片段    → okw scaffold deb|dput ...
├─ 知识速记                → okw ref [series|wsl-troubleshoot|okbs|verify]
└─ 注销/导出/进发行版执行  → okw unregister <name> --yes / okw export / okw exec <name> -- <cmd>
```

| 用户意图 | 命令链 | 备注 |
|---|---|---|
| 导入 openKylin 3.0 基础/桌面镜像 | `okw import <镜像.wsl> --name <名称> --location <目录>` | 两镜像并存时 `--name` 必须不同；镜像须用户自行从官网下载，okw 不下载 |
| 查发行版 / 验收环境 | `okw list` → `okw status <name>` → `okw verify <name>` | verify 五步：os-release/用户/UID/systemd/包数 |
| 装 rootless Podman | `okw podman preflight <name>` → `install <name> --yes` → `verify <name>` | 顺序不可跳；install 漏 `--yes` 零写入并以退出码 2 中止 |
| 引导 xuan-compose | `okw compose preflight <name> --source <源>` → `install <name> --yes --source <源>` → `verify <name> --smoke` | `--source` 必填且无内置默认源 |
| 构建/验收开发容器镜像 | `okw image build <name>` → `okw image verify <name>` | 发行版内 root 身份；默认禁拉基底，`--pull-base` 才放行 |
| deb 骨架 / OKBS dput 片段 | `okw scaffold deb --project ...` / `okw scaffold dput --openkylin-id ...` | dput 默认只打印，`--output` 才写文件 |
| 知识速记 | `okw ref [series|wsl-troubleshoot|okbs|verify]` | 只读，无参数时列主题 |
| 注销/导出/执行命令 | `okw unregister <name> --yes`、`okw export <name> --output <f>`、`okw exec <name> -- <cmd>` | unregister 必须 `--yes`；exec 非交互，不能代替 `wsl -d` 登录 |

完整参数签名、默认值与退出码见 [references/command-map.md](references/command-map.md)；双镜像导入的磁盘预留口径见知识库 [03 安装路径全景](../../../docs/knowledge/tech/openkylin-docs-wiki/concepts/03-install-paths.md) §3.2。

## 5. 本机固定事实（先读，避免重复踩坑）

- 应用源码：`apps/dev-tools/openkylin-wsl-devkit`（`src/okw`，主仓直接管理，**非 submodule，可直接修改**）；人类文档：`docs/tech/guides/openkylin-wsl-devkit/`（共 6 篇）。
- 本机 shell 的 PATH 被裁剪：`python`、`git`、`okw` 均不可裸调。Python 用全路径 `C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe`（3.14.7，已 editable 安装 okw 0.1.0，用 `& $py -m okw ...` 调用）；git 用 `D:\Program Files\Git\mingw64\bin\git.exe`，或在命令首行临时注入 `$env:PATH = "D:\Program Files\Git\mingw64\bin;" + $env:PATH`。
- 工具安装（其他机器/新环境）：在仓库根执行 `python -m pip install -e apps/dev-tools/openkylin-wsl-devkit`。
- okw 自身已内置 wsl.exe 全路径回退（PATH → `%WINDIR%\System32\wsl.exe`）与 `WSL_UTF8=1`，调用方不要再重复造这层封装。

## 6. 不可违反的硬约束

1. **写入类操作必须显式授权**：`podman install`、`compose install`、`unregister` 必须带 `--yes`；漏参退出码 2 且零写入。先向用户复述副作用清单，不要自行补参重试。

   > **为什么用退出码 2 + 零写入而不是交互式追问？** 非交互执行环境无法可靠承接交互提示，"打印副作用清单后中止"把授权决定交还给用户/上层 Agent，且保证失败路径不产生任何半写状态——可安全原样重放。
2. **禁止隐式拉取镜像**：`podman verify --smoke-image` 只接受发行版内已存在镜像，缺失即 FAIL；`image verify` 全程 `--pull=never`，`image build` 基底默认仅本地，`--pull-base` 才放行。

   > **为什么 verify 宁可 FAIL 也不拉镜像？** 验收的语义是"证明现状符合契约"。隐式 pull 会让缺失基底的环境悄悄转绿，把网络可用性混入验收结论；放行拉取必须是用户对单次操作的显式决定（`--pull-base`）。
3. **不改系统状态**：podman/compose 流程不改软件源、不改 `/etc/wsl.conf`、不切换默认发行版星标；compose 用用户级 uv 托管独立 CPython 3.14，不改系统 Python。
4. **许可证边界**：xuan-compose 是 GPL-2.0-only 第三方，okw（MIT）只做用户显式授权后的 CLI 聚合引导；禁止 import/复制/vendor 其源码，禁止把 xc 加为依赖；okw 保持零运行时依赖、Python ≥3.10 兼容。
5. **apt 调用纪律**（发行版内）：所有 apt 命令统一带 `env LC_ALL=C LANGUAGE=C` 前缀，解析器同时兼容中文候选行；新增 apt 调用点必须遵守并配套测试。
6. **错误收口**：wsl 调用失败由 okw 转成带中文可操作信息的受控错误，不向外抛原始异常；新增外部命令调用走 `distro.run_wsl` 同一封装。

## 7. 在该项目内开发（改源码时的门禁）

1. 测试在应用目录执行（pyproject 已配 `pythonpath=["src"]` 与覆盖率）：`& $py -m pytest -q`（cwd 为 `apps/dev-tools/openkylin-wsl-devkit`）。基线 **442 passed / 覆盖率 96%**（2026-10-13，1696 statements / 60 miss），关键模块 ≥90%，全量测试均 mock WSL、不触真实发行版。
2. **改了 CLI 命令面（`src/okw/cli/parser.py`）必须再生成快照**：`& $py tests/generate_cli_snapshot.py`，产物 `tests/snapshots/cli_surface.json` 人工零编辑，`test_cli_surface.py` 对拍。

   > **为什么快照必须由生成器产出、人工零编辑？** 命令面是对外契约，手改快照会让"测试通过"与"parser 真实形状"脱钩——先改测试再改实现即可骗过对拍。生成器单一事实源保证快照只能是 parser 的机械投影。
3. Python 红线（有 AST 守护测试，变异即红）：禁止 `from __future__ import annotations`；需兼容 3.10 的注解用 `typing.Dict/List/Optional`，不用 PEP 585/604 内建泛型与 `X | Y`；导入时版本守卫放文件顶部、第三方导入之前；类体内自引用注解按既有守卫模式处理。
4. 架构纪律：parser 只描述命令面（纯函数、无子进程）；领域逻辑在 `distro/podman/image/compose/scaffold/verify/ref.py`；处理器在 `commands/*_cmds.py`，经显式注册表装配；禁止用 argparse 下划线私有 API。
5. 构建后端固定 scikit-build-core（纯 Python 包，无 cmake 段）；新模块配套测试，覆盖率不回退。
6. 提交走仓库原子提交流程，中文 Conventional Commit；含中文提交用 `python .agents/scripts/git-commit-utf8.py`（本机需先把 git 目录注入 PATH，见 §5）。

## 8. 排障路由（先判层再动手）

- 导入报 `RegisterDistro/E_UNEXPECTED`、`CreateVm/E_ABORT`：空闲内存不足（实测阈值约 0.8GB 失败 / 4GB+ 成功），`wsl --shutdown` 释放后重试；okw 只打印分诊提示，不自动解压 tar。详见 [wsl-install-sparse-vhd-guide](../../../docs/knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md)。
- 双镜像选型/磁盘峰值/xrdp 3390 黑屏：见 [wsl-dual-image-selection](../../../docs/knowledge/tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md) 与桌面启动教程，不要把未验证建议写进 okw。
- podman preflight FAIL：按报告中文项修复后重跑；APT 索引缺失的 UNKNOWN 不是 FAIL，install 会先 `apt update`。
- 领域问题回源：命令疑问读 [01 快速开始](../../../docs/tech/guides/openkylin-wsl-devkit/01-getting-started.md)、[02 命令参考](../../../docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md)、[03 Podman](../../../docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md)、[04 开发边界](../../../docs/tech/guides/openkylin-wsl-devkit/04-development-and-boundaries.md)、[05 开发容器](../../../docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md)、[06 xuan-compose](../../../docs/tech/guides/openkylin-wsl-devkit/06-xuan-compose.md)；签名以 `src/okw/cli/parser.py` 为最终事实源。

## 9. 技能边界（不要越界）

- Windows 宿主侧 podman machine/Jupyter 容器启停、嵌套 Podman → [jpman-podman-ops](../jpman-podman-ops/SKILL.md)；client 下 quant/native/monetize compose 叠加栈 → [compose-overlay-ops](../compose-overlay-ops/SKILL.md)；新建 client 叠加栈 → [client-overlay-scaffold](../client-overlay-scaffold/SKILL.md)。
- WSL 宿主磁盘清理/VHDX 压缩/GPU/自启 → [wsl-ops-cmd](../wsl-ops-cmd/SKILL.md)、[wsl-vhdx-compact-cmd](../wsl-vhdx-compact-cmd/SKILL.md)；docker save 镜像转 WSL 发行版 → [docker-wsl-bridge-cmd](../docker-wsl-bridge-cmd/SKILL.md)。
- okw 不替代 `wsl --install`、`wsl --set-default-version`，不下载镜像，不调用 OKBS/factory API，不负责其他发行版的通用管理。

## 10. 安全检查清单（逐项确认）

- [ ] 执行 install/unregister 前，已向用户复述副作用清单并获得明确确认（授权已确认；无 `--yes` 不得自行补参重试）
- [ ] 写入链已先跑只读预检（`podman/compose preflight`）并按报告修复全部 FAIL（预检已通过，UNKNOWN 项已有处置方案）
- [ ] verify/smoke 使用的镜像已验证为发行版内本地已存在（未加任何隐式拉取，`--pull=never` 保留）
- [ ] unregister/export 的目标名称已核对，默认发行版星标保护快照已确认不受影响
- [ ] 涉及 xuan-compose 时已确认仅做用户授权的 CLI 聚合引导，未 vendor 其 GPL 源码、未加为 Python 依赖
- [ ] 修改 parser.py 后已重生成 `tests/snapshots/cli_surface.json`（人工零编辑），并已验证 test_cli_surface.py 对拍通过
- [ ] 开发门禁已验证：应用目录全量 pytest 通过、覆盖率未回退、Python 红线 AST 守护测试为绿
- [ ] 排障结论已验证与 `docs/knowledge/tech/openkylin-docs-wiki/` 实证口径一致，未把凭记忆的桌面镜像结论写入工具或文档

## 11. Gotchas（陷阱与反直觉行为）

- **裸调 `python`/`git`/`okw` 必失败**：本机 PATH 被裁剪，必须用 §5 的全路径或临时注入；反过来不要在 okw 里再包一层 wsl.exe 路径回退——okw 已内置。
- **退出码 2 不是工具坏了**：漏 `--yes` 时"打印副作用清单 + 零写入中止"是安全设计；擅自补 `--yes` 等于替用户授权写入。
- **verify FAIL 别加 pull**：`--smoke-image` 缺失、基底缺失都是环境事实，隐式 `podman pull` 或删 `--pull=never` 只会制造假绿。
- **改 parser 后只跑相关测试不够**：必须再生成 cli_surface.json；快照人工零编辑，对拍失败先查生成器而非改 JSON。
- **手写裸 `wsl --import` 会丢四件东西**：gzip 魔数校验（`1F 8B`）、600 秒超时、`WSL_UTF8=1`、失败时的中文分诊三问。
- **GPL 边界是硬约束**：把 xuan-compose 源码拷进 okw 或加为依赖，同时引发 GPL 感染与 CPython 3.14 版本冲突；用户级 uv 引导是唯一允许的接触方式。
- **导入 E_ABORT/E_UNEXPECTED 先查内存**：实测空闲内存约 0.8GB 失败、4GB+ 成功；`wsl --shutdown` 释放后重试，okw 不会（也不应）自动解压 tar。
- **ref 主题枚举与 help 文本不一致**：parser help 写作 `wsl-troubles`，实际接受的 key 是 `wsl-troubleshoot`；命令事实以 parser.py 为准。
- **相对链接层数别套用**：本 Skill 内到仓库根是三级（`../../../docs/`），而 `docs/` 内 wiki 文档之间是四级；移动/复制链接时按实际位置重算。
- **跨命令 GUI 验证的发行版"自动关机"不是空闲超时**：工具宿主每条 Shell 命令以 Job Object 托管进程树，命令结束回收 `wsl.exe`/`wslhost.exe`，最后一个 console attach 消失即触发 WSL 干净 poweroff（实测 `vmIdleTimeout=-1` 也挡不住），快速重启还会连累 localhost relay（guest 内自测通、Windows 侧不通）。跨命令 GUI/浸泡验证前先用 WMI 起脱离 Job 的有界 holder：`Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='wsl.exe -d <D> -u root sleep 600'}`（必须非沙箱），以「holder 进程在 / 服务 PID 不变 / 端口可达」三重判据验收，收尾必 `Stop-Process`；relay 已失活则先告知用户影响后 `wsl --shutdown` 冷启。完整 SOP 见 [cases/wsl-distro-holder-keepalive](../../cases/wsl-distro-holder-keepalive.md)。

## 12. 关键参考

| 参考 | 路径 | 何时查阅 |
|------|------|---------|
| 命令签名与退出码对照（按需加载） | [references/command-map.md](references/command-map.md) | 不确定参数、默认 tag（镜像默认 `3.0` 非 `latest`）、退出码语义时 |
| 安装路径全景（双镜像/磁盘口径） | [03-install-paths.md](../../../docs/knowledge/tech/openkylin-docs-wiki/concepts/03-install-paths.md) | 导入前磁盘规划 |
| 稀疏 VHDX 导入排障 | [wsl-install-sparse-vhd-guide.md](../../../docs/knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md) | 导入失败分诊 |
| 双镜像选型 | [wsl-dual-image-selection.md](../../../docs/knowledge/tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md) | 基础/桌面镜像与 xrdp 问题 |
| 人类文档 6 篇 | [docs/tech/guides/openkylin-wsl-devkit/](../../../docs/tech/guides/openkylin-wsl-devkit/01-getting-started.md) | 领域问题回源 |
| 命令面最终事实源 | `apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/parser.py` | 任何签名争议以此为准 |

## Changelog

- **v1.1.0** (2026-10-13): §11 新增「跨命令保活」Gotcha，双向引用 [cases/wsl-distro-holder-keepalive](../../cases/wsl-distro-holder-keepalive.md)；事实底座为当日 okw desktop 零注册表基线端到端验证实测（WMI detached holder 三重存活判据通过）。
- **v1.0.0** (2026-10-13): 按 skill-migration-position-governance 五步 SOP 从 `.trae/skills/openkylin-wsl-devkit/` 迁入主权区并升级为五要素形制（任务路由决策树、4 处 Why 解释、8 项安全检查清单、Gotchas 章节、references/command-map.md 按需加载）；事实底座为 442 passed / 覆盖率 96% 实跑基线与 parser.py 实证签名。
