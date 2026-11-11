---
title: "为 okw 增加 openKylin AI 栈支持（OCR 已验证路径） - 实施计划"
status: "implemented"
methodology: "seven-concepts-cmd: F→V→I→C"
content-sensitivity: "public"
source: ".trae/specs/infra-env/extend-okw-openkylin-ai/spec.md"
---

# 为 okw 增加 openKylin AI 栈支持（OCR 已验证路径） - 实施计划

## Task 1: 增加 AI 栈只读预检

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新增 `src/okw/ai.py` 领域模块与 `src/okw/commands/ai_cmds.py` 的 `cmd_preflight`；在现有命令树中增加 `ai preflight <发行版>`。
  - 定义分层组件清单（`AiComponent`：key/package/title/required）：OCR 必选为 `libkylin-ai-base-dev`、`libkylin-ai-base2`、`tesseract-ocr`、`tesseract-ocr-chi-sim`、`tesseract-ocr-eng`；可选层为 `kylin-ai-model-manager`、`libkysdk-genai-nlp0`、`kylin-ai-engine-plugins`、`kylin-ondevice-nlp-engine`、`kytensor-server`、`ollama`。
  - 复用 `okw.distro` 的发行版检查与 WSL 封装；结构项检查发行版存在、WSL2、openKylin 身份、dpkg/apt 能力（不强制非 root，OCR 任意用户可用）。
  - 以**单条** `apt-cache policy <全部组件>`（强制 C locale）获取已装/候选版本并按包分段解析；必选组件有候选标 PASS、缺失标 FAIL；可选层已装/有候选标 PASS、缺失标 UNKNOWN（不阻断）。
  - 安装目标无候选（索引缺失/过期）标 UNKNOWN 并输出中文 apt update 行动建议；policy 网络错误标 FAIL 并给网络方向；预检不得 apt update/安装/写文件/改默认发行版。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-1.1：发行版不存在、WSL1、非 openKylin、APT 缺失、索引过期（无候选）、网络错误、OCR 候选齐全、可选层缺失等场景均有测试并返回预期退出码。
  - `rule` TR-1.2：预检所有 WSL 调用均为只读；policy 为单条批量调用；无 update/install、无写入、默认发行版与文件系统前后快照不变。
  - `rubric` TR-1.3：索引未知与网络失败的中文建议可区分；必选与可选组件的状态语义（FAIL vs UNKNOWN）正确。
- **Completion Evidence**:
  - `ai.preflight_check` + `add_structural_checks` + `parse_policy_batch`/`_component_policy_item` 落地；单条批量 policy（C locale argv 经 `podman._apt_argv`）。
  - `tests/test_ai.py::TestPreflight`（含不存在/WSL1/非 openKylin/APT 缺失/网络错误/命令失败/全通过/必选缺失/候选 (none)/单条批量只读断言）与 `TestComponentPolicyItem` 全通过；真实 `okw ai preflight openKylin-3.0-desktop` 退出 0。

## Task 2: 显式确认后安装已验证 OCR 路径

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `ai.py`/`ai_cmds.py` 实现 `okw ai install <发行版> --yes`；无 `--yes` 时在任何 apt update/安装/写入前仅打印编号副作用清单并以退出码 2 中止。
  - 复用 `okw.podman` 的 C locale APT argv、`APT_MUTATING_TIMEOUT` 长超时与网络/哈希/缺包分类资产（同包内复用，不重写）。
  - `--yes` 后：结构预检 → root `apt update` → 复查直接包候选 → `apt install -y --no-install-recommends libkylin-ai-base-dev`（唯一直接包，OCR 运行库/tesseract/语言包由 APT Depends 解析）。
  - 安装后以默认用户执行 OCR 只读子集验收（`tesseract --version`、`--list-langs` 含 chi_sim/eng）。
  - 失败区分包不在源/网络/哈希，写入前停止；安装或验收失败非零退出、报告阶段与可能的部分变更，不宣称事务回滚或自动卸载。
  - 不添加/改写软件源，不改 wsl.conf/默认发行版/默认用户，不安装可选层、模型或 ollama。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8
- **Test Requirements**:
  - `rule` TR-2.1：未提供 `--yes` 时断言零写入（无 update/install），仅打印副作用清单且退出码 2。
  - `rule` TR-2.2：确认后命令仅针对目标发行版、root 执行 apt update 与单包 install（含 `--no-install-recommends`）；无源修改、默认发行版/用户、wsl.conf、可选层或模型相关命令。
  - `rule` TR-2.3：apt update 网络错误、哈希失败、直接包刷新后无候选、apt install 失败四类路径均隔离测试，fail-closed 且无越界写入。
- **Completion Evidence**:
  - `ai.install_run`/`_run_apt_update` 复用 `podman._apt_argv`、`APT_MUTATING_TIMEOUT` 与网络/哈希/缺包分类；唯一直接包 `libkylin-ai-base-dev`，命令含 `--no-install-recommends`、root 身份。
  - `tests/test_ai.py::TestInstall` 覆盖缺 --yes 零写入、全成功、结构失败、update 网络/哈希、候选复查缺失、install 失败、root+no-install-recommends+边界、tesseract 失败，全通过。

## Task 3: 增加 OCR 只读验收与本地图片冒烟

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现 `okw ai verify <发行版>`：以单条 `dpkg-query -W -f='${Package}|${Status}|${Version}\n' <组件>`（Status 不本地化）取已装状态，再以默认用户跑 `tesseract --version` 与 `--list-langs`。
  - 必选项：`libkylin-ai-base2` 已装、tesseract 可执行、语言列表同时含 chi_sim 与 eng；缺失标 FAIL 并提示先 `okw ai install <name> --yes`。
  - 可选层缺失仅标 UNKNOWN 不阻断；ollama 缺失注明"不在官方源、okw 不自动安装"。
  - 可选 `--smoke-ocr <发行版内图片路径>`：前置无 FAIL 时仅对本地图片执行 `tesseract <图片> stdout -l chi_sim+eng`，非空文本且退出 0 标 PASS；图片缺失/失败标 FAIL；全程离线、不触网。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-3.1：运行库缺失、tesseract 缺失/版本失败、语言缺 chi_sim/eng、全部通过的输出矩阵均被覆盖，退出码正确。
  - `rule` TR-3.2：默认 verify 不执行识别；冒烟仅在显式 `--smoke-ocr` 时运行且参数固定（chi_sim+eng、stdout），图片缺失失败、无任何网络调用；前置 FAIL 时冒烟跳过。
- **Completion Evidence**:
  - 验收改用无元字符的 `dpkg-query -s`（`parse_dpkg_show` 解析 `Package:/Status:/Version:` 块），规避 WSL 命令行桥接对 `$ | 引号` 的展开；tesseract 探针与冒烟参数固定（`stdout -l chi_sim+eng`）。
  - `tests/test_ai.py::TestVerify`/`TestSmokeOcr`/`TestTesseractProbes` 覆盖缺失/版本/语言/全通过矩阵与冒烟成功/缺图/空结果/前置 FAIL/Windows 路径转换，全通过。

## Task 4: 完成 CLI 装配、ref 主题、包构建与用户文档

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 在 `cli/parser.py` 增加 `ai` 子命令组（dest `ai_cmd`，preflight/install/verify，verify 含 `--smoke-ocr`）；`cli/main.py` 增加分发；`commands/__init__.py` 注册三个 ai handler。
  - 在 `ref.py` 新增 `ai-stack` 主题（四层成文、两代 SDK、OCR 已验证、凭据/模型红线、来源），更新 ref 主题 help 文案。
  - 更新命令面守卫：`test_command_registry.py`（叶子 17→20、键集与导入断言）、`test_cli_surface.py`（期望叶子）、`test_cli_architecture.py`（空组 parametrize 增 `ai`、parser 行数预算随命令面合理上调），再生成 `snapshots/cli_surface.json`。
  - 更新 README（AI 入门/边界）、`docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md`，新增 `07-ai-stack.md` 并在 `index.md` 任务表与 toctree 登记；更新 `apps/AGENTS.md`（及如需要 `apps/README.md`）中现有 okw 描述，不新增应用条目。
  - 运行全量测试、覆盖率、wheel 构建与链接检查。
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-4.1：全量测试通过、总覆盖率 ≥80%、ai 模块 ≥90%；wheel 构建成功且无新增 Requires-Dist。
  - `rule` TR-4.2：注册表键集、parser 叶子集与快照逐字一致；`okw ai` 空组回打帮助退出 2；既有子命令无回归。
  - `rule` TR-4.3：README/命令参考/07 指南/`okw ai --help` 对命令名、`--yes`、只读离线、"不碰密钥/不下载模型/不装 ollama"的说明一致；新增 Markdown 本地链接检查通过。
- **Completion Evidence**:
  - parser/main/注册表/ref 装配完成，命令面守卫（registry 20 叶子、surface、architecture、快照再生成）与 `test_ref.py` 同步。
  - 全量 **502 项通过**，TOTAL 覆盖率 **97%**、`ai.py` **97%**；scikit-build-core wheel 构建成功，METADATA **Requires-Dist=0**。
  - 文档：app README、`02-command-reference.md`、新增 `07-ai-stack.md`、`index.md`（任务表+toctree）、`apps/AGENTS.md`（两处）、`apps/README.md` 均更新。

## Task 5: 在可用 openKylin WSL2 环境执行分层验收

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 确认目标 openKylin 3.0 WSL2 发行版存在且可执行；只读检查其现有源是否提供 `libkylin-ai-base-dev`，不为通过验收添加第三方源。
  - 优先只读运行 `ai preflight`/`ai verify`；只有用户明确授权对指定发行版执行安装时才运行 `ai install --yes`；`--smoke-ocr` 图片须在发行版内、全程离线。
  - 若本机无可用发行版或未授权写入，保留静态与 mock 证据，真实安装/识别项记 `blocked` 与解除条件，不得伪造实测。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1：真实记录覆盖发行版身份、组件候选/已装、安装结果、tesseract 版本/语言、（如授权）冒烟识别；未执行步骤注明 blocked 及原因。
  - `rule` TR-5.2：真实验证不改默认发行版/软件源、不触其他发行版；安装与冒烟无远程拉取、不下载模型。
- **Completion Evidence**（2026-10-13，真实 openKylin-3.0-desktop WSL2；组件为 2026-10-08 POC 已装，故未再运行 install、无写入）:
  - `okw ai preflight openKylin-3.0-desktop` → 退出 **0**；必选 5 项 PASS（libkylin-ai-base-dev/base2 2.0.0.0、tesseract 5.3.4-ok4、chi_sim/eng 4.1.0），ollama UNKNOWN。
  - `okw ai verify openKylin-3.0-desktop` → 退出 **0**；`dpkg-query -s` 与 tesseract 探针一致。
  - `okw ai verify ... --smoke-ocr /tmp/okw_smoke.png` → 退出 **0**，「本地图片离线识别成功（chi_sim+eng，识别 38 字符）」；全程未改源/默认发行版、未触网、未下载模型、未碰密钥。
  - 过程中 WSL 曾因中断 drvfs 访问而卡死，经 `wsl --shutdown` 恢复；该环境插曲不影响上述只读结论。

## Issue I-1: 补齐 AI 命令/文档“如何查发行版名”指引

- **Status**: `completed`
- **Priority**: medium
- **Source**: 独立审查（review.md，F-1）→ 命中 AC-9 字段③“任一缺失即不通过”
- **Description**:
  - `ai install`/`ai verify` 的位置参数 `name` 帮助仅“发行版名称”（preflight 已含“（wsl -l -v 查看）”）；README AI 段与 `07-ai-stack.md` 入门段也未说明如何查发行版名。
  - 修复：两处 name help 补“（wsl -l -v 查看）”；README AI 段与 07 入门段各加一句查名指引；再生成 `tests/snapshots/cli_surface.json`；复跑命令面守卫与全量测试。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-I1.1：`ai preflight|install|verify` 三个 name help 文本一致且均含 `wsl -l -v`；快照与实际逐字一致。
  - `rule` TR-I1.2：README 与 07 指南均给出查名方法；命令面守卫与全量测试通过。
- **Completion Evidence**（2026-10-13）:
  - `parser.py` 三处 AI name help 统一为“发行版名称（wsl -l -v 查看）”；快照 `cli_surface.json` 第 479/499/531 行逐字一致（已再生成）。
  - README AI 段新增“先 `wsl -l -v` 查看 name、图片路径须在发行版内”一段；`07-ai-stack.md` 在三步前新增“先确认 `<name>`”引用块。
  - 全量复跑 **502 项通过**、TOTAL **97%**、`ai.py` **97%**，无回归。

## Issue I-2: 修正 README 冒烟图片路径表述（支持盘符路径）

- **Status**: `completed`
- **Priority**: medium
- **Source**: 独立审查 R2（review.md，F-2）→ 命中 AC-9/AC-8“多入口不一致即不通过”
- **Description**:
  - 修复 I-1 时在 README AI 段误写“`--smoke-ocr` …不支持直接给 Windows 盘符路径”，与实现 `ai.to_distro_image_path`（盘符→`/mnt/<drive>/`，有测试）、`07-ai-stack.md`（记录盘符自动转换）及审查者只读实测相矛盾。
  - 修复：仅改 README 该句为“图片可给发行版内路径，也支持 Windows 盘符路径（自动转 `/mnt/<drive>`、经 drvfs 访问）”；不涉代码/快照。
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-I2.1：README 表述与 ai.py/07 指南一致（均支持盘符路径自动转换）；不引入新的跨入口矛盾。
- **Completion Evidence**（2026-10-13）:
  - README AI 段改为：图片可给发行版内路径（`/tmp/sample.png`），也支持 Windows 盘符路径（`C:\Users\me\sample.png` → `/mnt/c/Users/me/sample.png`、经 drvfs）。
  - 与 `07-ai-stack.md:65-66`、`ai.to_distro_image_path` 及其测试表述逐字一致；本次仅改文档、未改代码/快照，测试结果不变（502 项通过、TOTAL 97%）。

## Task Dependencies

- Task 1 是只读预检基础；Task 2 与 Task 3 依赖 Task 1，可在其完成后并行实施。
- Task 4 依赖 Task 2 和 Task 3。
- Task 5 依赖 Task 4 的可运行实现与文档。
