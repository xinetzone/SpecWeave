# openKylin WSL 开发工具包（openkylin-wsl-devkit）- 产品需求文档

> 方法论链路：知识库学习（R→I→E）→ 应用设计（F→V→C）。本 spec 在全面学习 `docs/knowledge/tech/openkylin-docs-wiki/` 知识包（index + 7 概念页 + 5 参考文档）后固化：以 **WSL 作为切入点**，把知识库中已验证的 openKylin 3.0 WSL 实操经验（安装/验收/排障/脚手架）封装为可复用的开发工具。

## Overview

- **Summary**：一个本机 CLI 开发工具包，面向"在 Windows 上通过 WSL 进行 openKylin 开发与应用"的开发者。以 openKylin WSL 发行版为切入点，提供四组能力：① WSL 发行版生命周期管理（list/status/import/export/unregister/exec）；② openKylin 环境五步验收（对应知识库 §3.3 实测验收口径）；③ openKylin 开发脚手架（deb 打包骨架 + OKBS/dput 上传配置生成）；④ 知识库快速参考（版本代号、WSL 排障、OKBS 流程的本地索引）。
- **Purpose**：知识库 `docs/knowledge/tech/openkylin-docs-wiki/` 已沉淀 14 个原子文件与 4 个本机实测/远程核验结论，但都是"读"的资产。本应用把这些经验转成"用"的资产——开发者不必重读文档即可完成 WSL 导入验收、生成 deb 骨架与 dput 配置，降低 openKylin 开发入门摩擦，并让知识库结论以可执行命令的形式落地。
- **Target Users**：Windows 主力机上的 openKylin 开发者/尝鲜者（单用户、本机使用）。

## Goals

- G1：封装 WSL 发行版管理命令，正确处理 PATH 裁剪（全路径 `wsl.exe`）、中文输出（`WSL_UTF8=1`）、默认发行版星标保护（知识库 S26 实测要点）。
- G2：`verify` 子命令按知识库 §3.3 五步验收口径输出可解析结果：发行版在列且 WSL2、`/etc/os-release` 版本、默认用户/UID、systemd 状态、软件包计数（`dpkg-query -W | wc -l` 口径，与 405 包对照）。
- G3：`scaffold deb` 生成合法 debian/ 打包骨架（control/changelog/rules/compat/source 目录），changelog 系列代号参数化（yangtze/nile/huanghe，对应 1.0/2.0/3.0，知识库 F-015）。
- G4：`scaffold dput` 生成 OKBS 上传配置（`~/.dput.cf` 模板：fqdn=upload.build.openkylin.top:2121、method=sftp、incoming=%(okbs)s，对应知识库 D-F-027）。
- G5：`ref` 子命令提供知识库快速参考索引（版本代号表、WSL 排障三问、OKBS 五步流程），每条指向知识库相对路径。
- G6：零第三方运行时依赖（纯标准库：subprocess/argparse/pathlib），scikit-build-core 纯 Python 包（仓库硬约束）。

## Non-Goals

- **不做图形界面**：纯 CLI；不提供 Web UI / GUI。
- **不做 openKylin 容器内开发**：不替代在 WSL 内直接执行构建/编译的工作流，只做 Windows 侧的编排与验收。
- **不做自动安装引导**：不替代 `wsl --install` 系统级配置；import 封装只做参数构造与排障提示，不自动下载镜像、不自动改默认发行版。
- **不做桌面镜像实测**：6.14 GiB Desktop WSL 镜像的运行时行为仍属【待实测】（知识库 F-049/F-050），本工具不把未验证结论固化为默认建议。
- **不做 AI 能力**：不调用任何 LLM/生成式接口；不接入 openKylin AI SDK（那是知识库 05 概念页的开发主题，后续单独立项）。
- **不写入社区**：不自动提交 PR/issue、不调用 OKBS/factory API（dput 配置仅生成文件，上传由开发者自行执行）。
- **不修改知识库**：`ref` 只读引用 `docs/knowledge/tech/openkylin-docs-wiki/`，不复制内容、不改变其结构。

## Background & Context

- **知识库事实（本 spec 的设计依据，F 编号对应知识包 index.md / source-inventory.md）**：
  - WSL 官方指南：Win10 2004（19041）+/Win11；两镜像（最小 `openKylin-3.0-wsl-amd64.wsl` 336M / 桌面 6.14GiB）；`wsl --import openKylin .\openKylin <镜像> --version 2`；预置账号密码 `openkylin/openkylin`；桌面版 xrdp 端口 3390（F-017/F-018）。
  - 本机实测（S26）：Win10 0.19044 + WSL 2.9.3.0；最小镜像导入成功；`.wsl` 本质是 gzip tar（魔数 `1F 8B`）；`E_UNEXPECTED`/`E_ABORT` 与空闲内存强相关（0.8GB 失败 / 4.5GB 成功）；稀疏 VHD 需 `--set-sparse true --allow-unsafe`；验收五步（os-release/用户 UID/systemd/包数 405/默认星标）。
  - 本机现状（S32）：已存在发行版 `openKylin-3.0`（`d:\AI\.chaos\envs\openKylin-3.0`），本工具的真实冒烟对象。
  - OKBS 编译平台（D-F-027）：注册→PPA→SSH/PGP 公钥→`~/.dput.cf`（fqdn=upload.build.openkylin.top:2121, method=sftp）→`dput okbs:~<ID>/ppa <source.changes>`→archive.build.openkylin.top/dput-logs/ 查结果。
  - 版本代号（F-013/F-015）：1.0=yangtze、2.0=nile、3.0=huanghe；changelog 系列代号须与软件源代号一致。
  - 时效纪律（I-2）：新手文档最旧、治理与 AI 板块最新；本工具只固化 2026-09 实测/核验级结论，不固化占位页内容。
- **用户决策（2026-09-30 确认）**：① 全面学习知识库；② 在 `apps/` 下创建子文件夹存放 openKylin 相关开发与应用；③ 以 WSL 作为切入点；④ 应用类型为 dev-tools（开发者工具）。
- **区域决策**：代码落 `apps/dev-tools/openkylin-wsl-devkit/`（主仓库直接管理）；spec 落 `.trae/specs/openkylin-wsl-devkit/`（参照 zhihu-checkin-hub 独立应用 spec 目录形态）。应用无独立 `.agents/` 规范体系需求，遵循根规范（apps/AGENTS.md "简单应用无需独立 AGENTS.md"条款）；在 apps/AGENTS.md 路由表与 apps/README.md 登记。
- **技术栈约束**：AGENTS.md 硬性要求 Python 子项目默认 scikit-build-core（`requires=["scikit-build-core>=0.9"]`、`build-backend="scikit_build_core.build"`、`[tool.scikit-build]` 声明 `wheel.packages`、`build-dir="build/{wheel_tag}"`、`minimum-version="0.9"`；纯 Python 包不写 cmake 段）。参照 `apps/dev-tools/zhihu-checkin-hub/pyproject.toml`。
- **测试纪律**：WSL 调用一律 mock（不真实触发行版变更）；真实冒烟仅对 `list`/`verify` 只读路径，且以本机已有 `openKylin-3.0` 发行版为对象；覆盖率整体 ≥80%、关键模块 ≥90%。

## Functional Requirements

- **FR-1（WSL 调用封装）**：`distro.py` 统一封装 `wsl.exe` 调用：全路径解析（`$env:WINDIR\System32\wsl.exe`，PATH 裁剪兜底）、`WSL_UTF8=1` 环境变量注入、非零退出码归一为受控结果类型（区分"命令不存在/发行版不存在/执行失败/成功"），不向外抛原始异常。
- **FR-2（发行版管理）**：
  - `okw list`：解析 `wsl -l -v` 输出，列出发行版名、版本（WSL2/WSL1）、运行状态，标注默认发行版星标；输出人类可读中文表格。
  - `okw status <name>`：单发行版状态（在列/WSL2/默认/运行中）。
  - `okw import <镜像> --name <名> --location <目录> [--version 2]`：构造 `wsl --import`；镜像存在性/文件头魔数校验（`1F 8B`，gzip 检测）；失败时给出知识库 §4 排障三问（失败位置是否漂移→查内存→`wsl --shutdown` 后重试；必要时解压为纯 tar 再 import）中文提示。
  - `okw export <name> [--output <路径>]` / `okw unregister <name>`：只读确认后构造命令，unregister 显式要求 `--yes` 二次确认参数。
  - `okw exec <name> -- <cmd...>`：`wsl -d <name> -- <cmd...>` 透传执行。
- **FR-3（五步验收 verify）**：`okw verify <name>` 依次执行知识库 §3.3 五项并输出可解析结果：① `wsl -l -v` 确认在列且 WSL2、默认星标未被本工具改变（对比调用前快照）；② `cat /etc/os-release` 提取 VERSION/ID；③ `/bin/bash -lc 'echo "user=$(whoami) uid=$(id -u)"'` 确认默认用户/UID；④ `cat /etc/wsl.conf` 检查 `[user] default=` 与 `[boot] systemd=true`；⑤ `dpkg-query -W | wc -l` 软件包计数（与 405 对照提示，注明口径 `dpkg -l` 含表头会多 5 行）。单项失败不中断，汇总输出 PASS/FAIL 清单。
- **FR-4（deb 打包骨架 scaffold deb）**：`okw scaffold deb <项目名> --series <yangtze|nile|huanghe> --version <版本>` 生成 `debian/` 骨架：`control`（Package/Version/Architecture=amd64/Maintainer/Description）、`changelog`（Debian 格式头，系列代号参数化，知识库 F-015 纪律）、`rules`（dh 模板）、`compat`（12）、`source/format`（"3.0 (quilt)"）；输出生成文件清单。
- **FR-5（OKBS dput 配置 scaffold dput）**：`okw scaffold dput <openkylin-id> [--output 路径]` 生成 `~/.dput.cf` 可合并片段：`[okbs] fqdn=upload.build.openkylin.top:2121 / method=sftp / incoming=%(okbs)s / login=<ID>`（知识库 D-F-027 口径）；注明 paramiko 前置与 `dput okbs:~<ID>/ppa <source.changes>` 用法。
- **FR-6（知识库参考 ref）**：`okw ref <topic>` 输出主题速查：`series`（版本代号表 yangtze/nile/huanghe + 内核）、`wsl-troubleshoot`（E_UNEXPECTED/E_ABORT 三问 + 稀疏 VHD 纪律）、`okbs`（五步流程）、`verify`（五步验收口径）；每条附知识库相对路径（`docs/knowledge/tech/openkylin-docs-wiki/...`）。`okw ref`（无参数）列出全部主题。
- **FR-7（CLI 装配）**：argparse 入口 `okw`；每个子命令 `--help` 完整；未知子命令/参数给出中文提示与退出码 2；`--version` 输出包版本。

## Non-Functional Requirements

- **NFR-1（技术栈）**：Python ≥3.10；零第三方运行时依赖（标准库 subprocess/argparse/pathlib/re）；包构建 scikit-build-core 纯 Python（wheel.packages、build-dir、minimum-version="0.9"，无 cmake 段）；CLI 经 `[project.scripts] okw = "okw.cli:main"` 暴露。
- **NFR-2（测试）**：整体覆盖率 ≥80%，关键模块（distro/verify/scaffold）≥90%；WSL 调用全部 mock（subprocess 注入假 wsl.exe 脚本或 monkeypatch）；真实冒烟仅只读路径（list/verify）且需发行版存在。
- **NFR-3（平台）**：Windows 本机（WSL2 场景）；命令输出 UTF-8；错误信息中文、可操作。
- **NFR-4（仓库卫生）**：运行时零写文件（工具本身不产生状态文件，不修改用户系统除 scaffold 显式生成的目标外）；不修改知识库；scaffold 生成内容写用户指定目录。
- **NFR-5（文档）**：README.md 覆盖定位/安装/`okw` 全子命令用法/与知识库的映射/安全边界（不改默认发行版、unregister 需二次确认、弱口令提示引用知识库 F-018）。

## Constraints

- **Technical**：仅 Windows + WSL2；wsl.exe 输出格式随 WSL 版本变化（解析器对格式漂移 fail-fast 并提示手工查看原始输出）；镜像为 gzip tar（`1F 8B`），import 前做头字节校验。
- **Business**：不承诺替代官方安装流程；Desktop WSL 运行时结论保持【待实测】不固化（知识库 F-049）；默认账号弱口令风险在 ref 与 README 中提示（首次进入即 `passwd`）。
- **Dependencies**：本机 WSL2 与已导入的 `openKylin-3.0` 发行版（仅冒烟需要）；Python 3.10+ 环境。
- **区域**：代码属 `apps/dev-tools/openkylin-wsl-devkit/`（主仓库直接管理，新增后登记 apps 路由表与 README）；spec 属 `.trae/specs/openkylin-wsl-devkit/`；知识库引用仅相对路径、只读。

## Assumptions

- 用户本机已有或愿意导入 openKylin WSL 发行版（最小镜像 336M 路径已实测）。
- wsl.exe 输出在本工具生命周期内保持 `wsl -l -v` 可解析形态；格式漂移按 fail-fast 处理而非静默适配。
- 开发者签了或愿意签 openKylin CLA 后才使用 `scaffold dput`（知识库 06 §6.1 纪律：向仓库提交前必须签 CLA）。
- 单机单用户；无并发写（工具零状态文件，无共享状态）。

## Acceptance Criteria

### AC-1：wsl.exe 调用封装正确
- **Type**：`rule`
- **Given**：注入的假 wsl.exe 脚本（可控制输出与退出码）
- **When**：调用 distro 层的 list/exec/import 命令构造函数
- **Then**：命令数组正确（全路径、参数顺序）；`WSL_UTF8=1` 注入；非零退出码归一为受控结果类型；命令不存在/发行版不存在/执行失败/成功四类可区分
- **Pass Condition**：表驱动测试全部通过（含 PATH 裁剪场景：wsl.exe 不在 PATH 时用 `$env:WINDIR\System32\wsl.exe`）
- **Evidence**：pytest `test_distro_*`；覆盖率高

### AC-2：list/status 解析正确且默认星标保护
- **Type**：`rule`
- **Given**：构造的 `wsl -l -v` 输出（多发行版、含默认星标、WSL2/WSL1 混合）
- **When**：`okw list` / `okw status <name>`
- **Then**：发行版名、版本、状态、默认标记全部解析正确；中英文表格输出；不存在的发行版给中文错误与退出码 1
- **Pass Condition**：快照测试通过；verify 前后默认星标对比无变化（本工具任何路径不得改变默认发行版）
- **Evidence**：pytest

### AC-3：import 封装与排障提示
- **Type**：`rule`
- **Given**：一个真实的最小镜像文件头（`1F 8B` gzip）与一个非 gzip 文件
- **When**：`okw import` 校验与命令构造
- **Then**：gzip 通过并构造正确 `wsl --import <name> <location> <镜像> --version 2`；非 gzip 拒绝并提示文件格式；失败时输出知识库 §4 排障三问中文提示（位置漂移→内存→shutdown 重试→tar 解压路径）
- **Pass Condition**：测试断言命令数组与提示文案；真实镜像头校验通过
- **Evidence**：pytest + 真实头字节核验记录

### AC-4：verify 五步验收可解析输出
- **Type**：`rule`
- **Given**：mock 的五个命令输出（对应知识库 §3.3 验收项）
- **When**：`okw verify <name>`
- **Then**：五步结果以 PASS/FAIL 清单输出；版本/用户/UID/systemd/包数正确提取；包数对照 405 并注明口径；单项失败不中断
- **Pass Condition**：mock 表驱动测试通过；真实发行版 `openKylin-3.0` 冒烟 verify 输出合法（本机已有发行版）
- **Evidence**：pytest + 冒烟记录

### AC-5：scaffold deb 骨架合法
- **Type**：`rule`
- **Given**：`okw scaffold deb demo --series huanghe --version 0.1.0`
- **When**：在临时目录生成
- **Then**：`debian/` 下 control/changelog/rules/compat/source/format 齐备；changelog 首行含 `demo (0.1.0)` 与系列代号；control 必填字段完整；输出文件清单
- **Pass Condition**：生成文件逐项断言；`dpkg-parsechangelog`（若可用）或结构断言通过
- **Evidence**：pytest

### AC-6：scaffold dput 配置合法
- **Type**：`rule`
- **Given**：`okw scaffold dput myid`
- **When**：生成 dput 配置片段
- **Then**：`[okbs]` 段含 fqdn=upload.build.openkylin.top:2121、method=sftp、incoming=%(okbs)s、login=myid；输出 OKBS 上传命令示例与 paramiko 前置提示
- **Pass Condition**：配置字段逐项断言（对应知识库 D-F-027 口径）
- **Evidence**：pytest

### AC-7：ref 知识库索引覆盖
- **Type**：`rule`
- **Given**：`okw ref series|wsl-troubleshoot|okbs|verify` 与 `okw ref`（无参数）
- **Then**：四个主题各有正确速查内容；每条附知识库相对路径（`docs/knowledge/tech/openkylin-docs-wiki/...` 且路径存在）；无参数列出全部主题
- **Pass Condition**：速查内容与知识库事实一致（代号表含 yangtze/nile/huanghe）；路径存在性断言通过
- **Evidence**：pytest + 路径存在检查

### AC-8：CLI 完整性与错误处理
- **Type**：`rule`
- **Given**：安装后的 `okw` 命令
- **Then**：每个子命令 `--help` 输出完整；未知子命令中文提示且退出码 2；`--version` 输出包版本
- **Pass Condition**：CLI 集成测试通过
- **Evidence**：pytest（subprocess 调用已安装入口或 `python -m okw`）

### AC-9：构建与仓库卫生
- **Type**：`rule`
- **Given**：pyproject.toml 与源码
- **When**：`python -m build`（或等效 wheel 构建）
- **Then**：scikit-build-core 成功产出 wheel；包可导入；`okw` console 脚本注册正确；`git status --porcelain` 中除应用目录与 spec 目录外无新增文件（工具零运行时写入）
- **Pass Condition**：构建成功 + wheel 元数据检查 + git status 断言
- **Evidence**：构建输出 + 检查记录

### AC-10：真实发行版冒烟
- **Type**：`rubric`
- **Dimension**：工具在本机真实 openKylin WSL 发行版（`openKylin-3.0`）上的端到端可用度
- **Scale**：1-5
- **Anchors**：1 = 仅 mock 通过，真实环境不可用；3 = list/verify 真实运行成功但部分输出需人工纠偏；5 = list/verify 真实运行全部 PASS，输出与知识库口径一致，无环境报错
- **Pass Threshold**：>= 3（受本机 WSL 版本与发行版状态制约，3 为可接受底线；若发行版被卸载则以 AC-2~AC-9 完整 mock 证据收口并登记 blocked）
- **Evidence**：真实执行记录（list/verify 输出）

## Open Questions

- [ ] 是否需要 `okw scaffold deb` 支持开明包（Kaiming）骨架？当前仅 deb（知识库 D-F-036 开明包为 2.0+ 新形态），留待后续迭代。
- [ ] 是否将 `import` 的桌面镜像（6.14GiB）分支做成显式 `--desktop` 模式？当前仅提示排障与磁盘规划引用，不固化未实测结论（AC 不受影响）。
