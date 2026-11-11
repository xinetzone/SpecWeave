---
title: "为 okw 增加 openKylin AI 栈支持（OCR 已验证路径） - Independent Review"
status: "reviewed"
methodology: "seven-concepts-cmd: F→V→I→C"
content-sensitivity: "public"
source: ".trae/specs/infra-env/extend-okw-openkylin-ai/spec.md"
---

# 为 okw 增加 openKylin AI 栈支持（OCR 已验证路径） - Independent Review

## 审查范围与方法

- 独立 Review（全新上下文、只读）。审查期间未修改任何源码 / 测试 / 文档；本文件是唯一写入物，未重新实现任何功能。
- 证据获取方式（均为审查者实际执行）：
  1. **独立复跑全量测试与覆盖率**：app 根 `D:\spaces\SpecWeave\apps\dev-tools\openkylin-wsl-devkit` 下执行 `python -m pytest`，环境 Python 3.13.13 / pytest 9.1.1 / pytest-cov 7.1.0；另由独立复核流程在同环境复跑一次，结果一致。
  2. **独立构建 wheel**：`python -m pip wheel . --no-deps -w <TEMP>`，并以 zipfile 读取 wheel 内 `METADATA`。
  3. **真实 WSL 只读实测**：发行版 `openKylin-3.0-desktop`（apt 3.1.16），调用方式 `src` 经 `PYTHONPATH` 注入后 `python -m okw …`；未运行 install、未做任何写入。
  4. **对抗输入与注入反证**：对纯解析函数喂畸形输出；按 okw 的真实 argv 路径喂 shell 元字符载荷。
- 审查对象：新增 `src/okw/ai.py`、`src/okw/commands/ai_cmds.py`、`tests/test_ai.py`、`docs/tech/guides/openkylin-wsl-devkit/07-ai-stack.md`；修改 `commands/__init__.py`、`cli/parser.py`、`cli/main.py`、`ref.py`、四个守卫测试与快照、README、`02-command-reference.md`、`index.md`、`apps/AGENTS.md`、`apps/README.md`。

## Checkpoints

- [x] **CP-R1：preflight 只读、单批 policy、分层语义正确**
  - **Type**：`rule`
  - **Covers**：AC-1；TR-1.1 / TR-1.2 / TR-1.3
  - **Evidence**：
    - 单条批量调用：`ai.py:292-294` 一次 `apt-cache policy *ALL_PACKAGES`（11 包，`ALL_PACKAGES` 见 `ai.py:137`）；测试断言 policy 调用数恰为 1（`tests/test_ai.py:236-238`）。
    - 强制 C locale 且复用资产：经 `podman._apt_argv` → `env LC_ALL=C LANGUAGE=C …`（`podman.py:114-119`；调用点 `ai.py:194,293`）。
    - 完全只读：`preflight_check`（`ai.py:286-313`）仅含结构探针与一次 policy，无 apt update/install、无写文件；结构失败即 return、不出具安装性结论（`ai.py:289-290`）。
    - 状态语义：必选 5 包有候选/已装→PASS（`ai.py:263-268`）；可选 6 项缺失→UNKNOWN 且 `mark_optional` 剔出门控（`ai.py:271-272,310-311`）；policy 网络错误→FAIL、不重试不改源（`ai.py:295-300`）。
    - **真实 WSL 实测（审查者亲跑）**：`python -m okw ai preflight openKylin-3.0-desktop` → 退出 **0**；必选 5 项 PASS（base-dev/base2 2.0.0.0、tesseract 5.3.4-ok4、chi_sim/eng 1:4.1.0），ollama UNKNOWN（不阻断），结论"预检全部通过"。
    - **索引过期路径实证**：apt 3.1.16 下 `apt-cache policy <未知包>`（单查与批量均验证）输出**完全为空、退出 0、无分段** → 解析结果中该包缺省（`info is None`）→ 必选项判 **UNKNOWN** 并输出"APT索引未知；未知：发行版 APT 索引缺失或已过期，建议在发行版内先手动执行 sudo apt update 后重跑 preflight"（`ai.py:275-279`，常量 `podman.py:23-30`），与规格场景逐字一致。分段存在但 `Candidate: (none)` → FAIL（`ai.py:280-283`），用于兼容仍打印 `(none)` 分段的 apt 版本。
  - **Result**：`pass`

- [x] **CP-R2：install 必须显式确认、root、单直接包、发行版边界**
  - **Type**：`rule`
  - **Covers**：AC-2；TR-2.1 / TR-2.2
  - **Evidence**：
    - 无 `--yes` 零写入：`install_run` 在 yes=False 时立即返回 missing_yes 报告（`ai.py:447-449`），此前不创建任何子进程；handler 打印 3 条编号副作用清单与凭据红线（`ai.py:400-405,500`；`ai_cmds.py:22-25`）。**审查者亲跑** `python -m okw ai install openKylin-3.0-desktop`（无 --yes）→ 仅清单、退出 **2**。
    - `--yes` 流程：结构预检（`ai.py:452-456`）→ root `apt update`（`ai.py:410-413`，`user="root"`、`timeout=APT_MUTATING_TIMEOUT=600`）→ 复查直接包候选（`ai.py:462-469`）→ root `apt install -y --no-install-recommends libkylin-ai-base-dev`（`ai.py:471-476`）→ 默认用户（未传 user）只读 OCR 验收（`ai.py:489`）。
    - 唯一直接包：`DIRECT_PACKAGES=("libkylin-ai-base-dev",)`（`ai.py:96`），安装 argv 中无其他直接包名。
    - 边界：无 sources.list / wsl.conf / 默认发行版 / 默认用户改动，无可选层、模型、ollama 相关命令；测试以禁止子串哨兵断言（`tests/test_ai.py:371-379`）。Gen2 三元包仅出现在只读盘点清单，install 路径从不引用。
  - **Result**：`pass`

- [x] **CP-R3：安装失败分类可区分、写入前停止、不宣称成功/不自动卸载**
  - **Type**：`rule`
  - **Covers**：AC-3；TR-2.3
  - **Evidence**：
    - 分类资产：update 阶段抓取失败/哈希检测（`ai.py:416-439`）；候选复查非 PASS 即停（`ai.py:466-468`，UNKNOWN 同样阻断写入）；install stderr 经 `podman._classify_apt_install_error` 区分网络 / 哈希 / 缺包 / 其他（`podman.py:415-433`；调用点 `ai.py:477-482`），文案禁止第三方源。
    - 失败后非零、报告失败阶段、不宣称事务回滚或自动卸载，并提示"apt update 或部分包安装可能已部分生效"（`ai.py:512-514`）。
    - 测试矩阵 `tests/test_ai.py::TestInstall` 覆盖 update 网络（327-336）、哈希（338-345）、刷新后无候选（347-355）、install 失败（357-369），均 fail-closed、无越界写入。
  - **Result**：`pass`

- [x] **CP-R4：verify 只读反映真实 OCR 上下文、可选层不阻断**
  - **Type**：`rule`
  - **Covers**：AC-4；TR-3.1
  - **Evidence**：
    - 只读探针：`dpkg-query -s *ALL_PACKAGES`（`ai.py:556`，命令不含 `$`/`|`/引号，规避 WSL 桥接元字符处理）+ `parse_dpkg_show`（`ai.py:520-546`，仅 `Status: install ok installed` 判已装）；tesseract 版本/语言探针（`ai.py:370-395`）。
    - 必选缺失→FAIL 并提示先 install、非零；全过→0。实现同时要求 `-dev` 与 base2（`ai.py:560-566`），比规格更严。
    - 可选层不门控：`AiVerifyReport.optional_names` / `_gating_items`（`ai.py:72-87`），可选 UNKNOWN/PASS 均不翻转结论；逐项角色说明见 `ai.py:572-582`。
    - **真实 WSL 实测（审查者亲跑）**：`python -m okw ai verify openKylin-3.0-desktop` → 退出 **0**；base-dev/base2、tesseract 5.3.4、chi_sim+eng 全 PASS；model-manager/engine-plugins/ondevice-nlp/ollama UNKNOWN，结论"OCR 验收通过（默认只读，未执行图片识别）"。
  - **Result**：`pass`

- [x] **CP-R5：OCR 冒烟仅本地、离线、参数固定，且无命令注入**
  - **Type**：`rule`
  - **Covers**：AC-5；TR-3.2
  - **Evidence**：
    - 默认 verify 不识别；冒烟仅在显式 `--smoke-ocr` 时运行，固定 argv `["tesseract", <distro_path>, "stdout", "-l", "chi_sim+eng"]`（`ai.py:597-600`）；前置有 FAIL 即跳过（`ai.py:586-588`）；`ok 且 stdout 非空` 才 PASS（`ai.py:601-605`）；图片 `test -f` 缺失 / 空结果 / 失败 → FAIL（`ai.py:590-608`），全程无网络调用。
    - **真实 WSL 实测（审查者亲跑）**：`verify --smoke-ocr /tmp/okw_smoke.png`（图片已存在）→ 退出 **0**，"本地图片离线识别成功（chi_sim+eng，识别 38 字符）"。
    - **注入反证（审查者亲跑）**：以与 okw 相同的 argv 数组方式执行 tesseract，图片参数为 `/tmp/okw_smoke.png; echo INJ_MARKER_9X7` → RC 1，stderr 为 `Error, cannot read input file /tmp/okw_smoke.png; echo INJ_MARKER_9X7: No such file or directory`，载荷被当作文件名字面量、`INJ_MARKER` 未执行。WSL 调用链全程 `subprocess.run(..., shell=False)`、argv 数组 + `--` 透传（`distro.py:55-65,182-193`），全仓无 `shell=True`/`os.system`。
  - **Result**：`pass`

- [x] **CP-R6：ref ai-stack 可用、无回归、覆盖率达标、wheel 成功、零新增依赖**
  - **Type**：`rule`
  - **Covers**：AC-6；TR-4.1
  - **Evidence**：
    - `ref.py:74-91` 新增 ai-stack 主题：覆盖四层成文、Gen1/Gen2 区别、OCR 已验证事实、凭据/模型红线；3 条来源文件在磁盘逐一存在；主题出现在 `list_topics()` 与 parser topic help（`parser.py:58-60`），`test_ref.py:46-60` 断言内容与来源。
    - **审查者亲跑全量测试两次**：`502 passed`（28.61s；独立复核流程另得 502 passed / 17.95s），无失败无回归。
    - 覆盖率：**TOTAL 97%**（2129 stmts / 72 miss，≥80%）；**`ai.py` 97%**（356/12，≥90%）；`ai_cmds.py` 100%。
    - wheel：独立构建成功，产物 `openkylin_wsl_devkit-0.1.0-py3-none-any.whl`（纯 Python、69766 字节）；wheel 内 `METADATA` 的 **Requires-Dist 计数 = 0**；`pyproject.toml:19` `dependencies = []`。
  - **Result**：`pass`

- [x] **CP-R7：命令面注册表 / parser / 快照逐字一致，空组回打帮助退出 2**
  - **Type**：`rule`
  - **Covers**：AC-7；TR-4.2
  - **Evidence**：
    - 注册表实际枚举 = **20 叶子**，含逐字键 `"ai preflight"`/`"ai install"`/`"ai verify"`（`commands/__init__.py:41-62,51-53`）。
    - parser 实际构建枚举 = 20 叶子，与注册表键集一致（`parser.py:82-127`；交叉守卫 `test_cli_architecture.py:31-32`）。
    - 快照深比较全等：按 `test_cli_surface.py:47-50` 逻辑在内存重新序列化，与 `tests/snapshots/cli_surface.json` 零 diff；ai 三叶子片段见快照 427-552（含 `--yes` / `--smoke-ocr` 与边界 epilog）。快照无自动写回开关，漂移即硬失败。
    - 空组：**审查者亲跑** `python -m okw ai` → 回打 `usage: okw ai …`、退出 **2**（`main.py:22-25`）；空组参数化含 ai（`test_cli_architecture.py:35-40`）。守卫均为硬编码键集的真实校验，未被放松。
  - **Result**：`pass`

- [x] **CP-R8：文档与区域索引一致、链接有效**
  - **Type**：`rule`
  - **Covers**：AC-8；TR-4.3
  - **Evidence**：
    - 实际 `--help` 与 README（`README.md:59-70`）、`02-command-reference.md:90-106`、`07-ai-stack.md`、`index.md:22,34,44-54` 逐项对应：命令名、`--yes`、`--smoke-ocr`、只读/离线、"不碰密钥/不下载模型/不装 ollama/Gen2 仅盘点"无矛盾。
    - `index.md` 任务表与 toctree 已登记 `07-ai-stack.md`，编号标题与实际文件一致。
    - `apps/AGENTS.md`（:62,:292）与 `apps/README.md:103` 为既有 okw 条目就地追加 AI 描述，**未新增并列应用条目**；引用路径均存在。
    - Markdown 本地相对链接（README 8 条、02 7 条、07 3 条、index 10 条及 apps 两索引）逐一解析，**0 条失效**；07 frontmatter `source` 路径存在。
  - **Result**：`pass`

- [x] **CP-U1：首次使用与副作用说明多入口完备（rubric）**
  - **Type**：`rubric`
  - **Covers**：AC-9
  - **核对维度（字段 × 入口）**：规格要求 `okw ai --help`、`okw ai install --help`、README、AI 指南入门段无矛盾地说明 5 个字段。
    - 字段①（四层 + 两代 SDK、本期只装已验证 OCR）、②（install 三阶段副作用）、④（不配密钥/不下载模型/不装 ollama）、⑤（--smoke-ocr 前置、离线）：07/02 完整，组 help/README 简略但无矛盾，视为覆盖。
    - **字段③（如何查发行版名）缺失**：`ai install`/`ai verify` 的 `name` 参数 help 仅为"发行版名称"（`parser.py:105,122`），而 `ai preflight` 的同名参数有"发行版名称（wsl -l -v 查看）"（`parser.py:92`）；README AI 段（`README.md:59-70`）与 07 入门段（`07-ai-stack.md:1-9`）均未给出查名方法。仅 `02-command-reference.md:31` 提到 `okw list` / `wsl -l -v`，但该文档不在 AC-9 列举的入口内。
  - **Pass Condition 适用**：AC-9 明确"任一缺失或多入口不一致即不通过"。
  - **Result (R1)**：`fail`（字段③缺失，即 F-1）。
  - **Result (R2)**：`fail`。字段③已补齐并经审查者亲跑核对（parser 三处统一、快照 479/499/531、README:70、07:24）；但本轮修复在 README:70 新引入"不支持直接给 Windows 盘符路径"，与实现 `ai.py:19-33`、07:66 及审查者实测相矛盾（见 F-2），命中"多入口不一致即不通过"。
  - **Result (R3)**：`pass`。F-2 已修复——README:70 改为"图片可给发行版内路径（/tmp/sample.png），也支持 Windows 盘符路径（自动转 `/mnt/c/...`、经 drvfs）"，与 `07:65-66`、`ai.py:19-33` 及其测试一致；AC-9 三要素（只读离线边界 / 不碰密钥模型 ollama / 如何查发行版名）在 help、README、07 三处齐备且无任何跨入口矛盾；全量 502 passed、正向冒烟 38 字符退出 0。

## Findings

| ID | 类型 | 严重度 | 位置 / 复现 | 期望结果 |
|---|---|---|---|---|
| **F-1** | **actionable** | minor | AC-9 字段③缺失。复现：`python -m okw ai install --help`、`python -m okw ai verify --help` 中 name 仅"发行版名称"；README AI 段与 07 入门段无查名方法 | ① `parser.py:105,122` install/verify 的 name help 与 preflight 对齐为"发行版名称（wsl -l -v 查看）"；② README AI 段与 07 入门段各补一句"发行版名可用 `wsl -l -v` / `okw list` 查看"；③ help 文案变更后须再生成 `tests/snapshots/cli_surface.json` 并复跑全量测试。**R2 核对：已闭环** |
| **F-2** | **actionable** | minor | R2 新发现。`README.md:70` 新增表述"`--smoke-ocr` 的图片路径须位于该发行版内…，**不支持直接给 Windows 盘符路径**"，与三处证据矛盾：实现 `ai.py:19-33`（盘符→`/mnt/<drive>/`，并有测试覆盖）、`07-ai-stack.md:66`（"Windows 盘符路径…自动转换为 /mnt/c/…"）、审查者实测 `verify --smoke-ocr C:\Windows\Web\Wallpaper\Windows\img0.jpg`：路径被转换、`test -f` 通过、tesseract 实际执行（壁纸无文字结果为空，RC1 属正常 fail-closed） | 将 README:70 改为与实现/07 一致，例如："`--smoke-ocr` 图片须在发行版可访问位置：可直接给发行版内路径（如 `/tmp/sample.png`），也支持 Windows 盘符路径（自动转换为 `/mnt/c/…`，经 drvfs 访问）"。纯文档一句，不涉及快照/代码；修复后复跑全量测试并再开 R3。**R3 核对：已闭环** |
| A-1 | advisory | minor | `--smoke-ocr` 图片路径未做 shell 元字符清洗（`ai.py:19-33,589-600`） | 注入反证表明无 shell、元字符仅成为文件名字面量并导向 FAIL，不可利用；建议在 help 中提示路径避免含 `;`/`$()`/反引号即可，无需改动执行模型 |
| A-2 | advisory | minor | `parse_tesseract_version`（`ai.py:343-354`）不匹配古版 banner 行 `Tesseract Open Source OCR Engine vX.Y` | 目标 tesseract 5.3.4 首行为 `tesseract 5.3.4`，未触发；属纵深防御，可让正则兼配 `Engine vX.Y` |
| A-3 | advisory | minor | 测试加固：可选层被标 FAIL（非 UNKNOWN）时的门控、`need_apt=False` 的 WSL1/非 openKylin 分支、`_run_apt_update` "ok 但索引下载不完整"分支（`ai.py:433-437`）、ref ai-stack 更细断言 | 现覆盖率 97%、门控已手工验证；增补用例可防回归，不阻塞本次结论 |
| A-4 | advisory | trivial | `ai.py:166` 提示文案全角括号未闭合：`未注册（wsl -l -v 查看：{exc}` | 顺手补齐为 `（wsl -l -v 查看）：{exc}`，纯 cosmetic |
| A-5 | advisory | minor | `exec_distro` 每条命令前都重查 `wsl -l -v`（`distro.py:185-188`）；审查者首次跑 preflight 时曾在 policy 步骤收到瞬时假失败"apt-cache policy 命令失败（发行版 openKylin-3.0-desktop 不存在）"，热启动后重跑退出 0 | 效果 fail-closed（安全方向），但属环境抖动导致的假阴性；建议未来对列表读取做一次重试或短时缓存（该设计为既有资产，非本次引入） |
| A-6 | advisory | trivial | 快照文件为 CRLF + 尾换行，内存序列化为 LF（内容逐行全等） | 非缺陷；如需字节级门禁可在 CI 加 `git diff --exit-code` 或统一行尾 |

## Recommended Issues

### Issue I-1：补齐"如何查发行版名"的多入口说明
- **Status**：`pending`
- **Priority**：medium
- **Depends On**：None
- **Discovered By**：Review R1（F-1）
- **Description**：
  - AC-9 字段③要求首次使用入口说明如何确定发行版名；当前 install/verify 的 name help、README AI 段、07 入门段均缺失，仅 02 命令参考覆盖，不满足 AC-9"任一缺失即不通过"。
- **Acceptance Criteria Addressed**：AC-9
- **Test Requirements**：
  - `rule` TR-I-1.1：`okw ai install --help`、`okw ai verify --help` 的 name 描述含"wsl -l -v"；README AI 段与 07 入门段含 `wsl -l -v` 或 `okw list` 查名指引；快照再生成后 `test_cli_surface`/`test_cli_architecture`/`test_command_registry` 与全量 `python -m pytest` 全部通过。
- **Notes**：改动面小（parser 两行文案 + 两处文档一句 + 快照再生成），不涉及任何功能逻辑。

### Issue I-2：修正 README 关于 smoke 图片 Windows 盘符路径的错误表述
- **Status**：`completed`（R3 核对闭环）
- **Priority**：medium
- **Depends On**：None
- **Discovered By**：Review R2（F-2）
- **Description**：
  - F-1 修复在 `README.md:70` 加入"不支持直接给 Windows 盘符路径"，与实现（`ai.py:19-33` to_distro_image_path，含测试）、07:66 文档及审查者 R2 实测（盘符路径被转换、文件找到、tesseract 执行）相矛盾，属 AC-8/AC-9 的跨入口不一致。
- **Acceptance Criteria Addressed**：AC-8、AC-9
- **Test Requirements**：
  - `rule` TR-I2.1：README:70 不再出现"不支持…盘符路径"，表述与 07:63-67 及实现一致（发行版内路径 + 盘符自动转换 /mnt/c）；全量 `python -m pytest` 通过（纯 README 改动不影响快照，但须确认无回归）。
- **Notes**：仅 README 一句，无需改代码/快照。

## Review History

### Review R1
- **Result**：`fail`
- **Evidence**：
  - CP-R1 ~ CP-R8（AC-1~AC-8）全部 `pass`，且每条均有独立证据：审查者亲跑全量 pytest 两次（502 passed、TOTAL 97%、ai.py 97%）、独立构建 wheel（Requires-Dist=0）、在真实 openKylin-3.0-desktop WSL 只读亲跑 preflight/verify/冒烟（退出均 0，冒烟识别 38 字符）、空组与缺 --yes 退出 2、注入反证不可利用。
  - CP-U1（AC-9）`fail`：字段③"如何查发行版名"在规格指定入口缺失，命中 AC-9"任一缺失即不通过"。
  - 无 blocker、无 major；唯一可行动项 F-1 为 minor 文案/快照补齐，已固化为 Issue I-1，回 Implement 修复后应再开 Review R2 复核。
- **安全边界结论**：preflight/默认 verify 只读、离线；install 四要素（`--yes`、root、`--no-install-recommends`、唯一直接包 libkylin-ai-base-dev）齐备；未触碰密钥、模型下载、ollama、Gen2 全栈，未改源 / 默认发行版 / 默认用户 / wsl.conf；零新增 Requires-Dist。

### Review R2
- **Result**：`fail`
- **触发**：实施方报告 Issue I-1 / F-1 已修复，审查者以全新只读上下文复核。
- **Checks Performed（审查者亲跑，未改任何源码/测试/文档，未运行 install）**：
  1. `parser.py:92,105,122`：AI 三处 name help 逐字统一为"发行版名称（wsl -l -v 查看）"——与修复说明一致。
  2. `snapshots/cli_surface.json:479,499,531`：三处 help 逐字为"发行版名称（wsl -l -v 查看）"；全量 pytest 中 test_cli_surface / architecture / registry 守卫通过，证明快照与 parser 当前状态逐字一致。
  3. `README.md:70`：已新增查名段（`wsl -l -v`、举例 openKylin-3.0-desktop）——字段③在 README 已覆盖；但同句"不支持直接给 Windows 盘符路径"为错误表述（F-2）。
  4. `07-ai-stack.md:24`：三步流程前已新增"先确认 `<name>`"引用块（wsl -l -v、实测机名、ID=openkylin）——字段③在 07 已覆盖。
  5. `tasks.md:110-125`：Issue I-1 置 completed 并附逐字证据。
  6. 全量测试亲跑：`python -m pytest -q` → **502 passed in 15.70s**，TOTAL **97%**、ai.py **97%**，无回归。
  7. Windows 盘符路径只读实测：`verify --smoke-ocr C:\Windows\Web\Wallpaper\Windows\img0.jpg` → 路径经 `to_distro_image_path` 转为 `/mnt/c/...`、`test -f` 通过、tesseract 实际执行（壁纸无文字→结果为空判 FAIL，RC1，fail-closed 正常）。证明盘符路径**确实支持**，反证 README:70 的"不支持"。
- **Checkpoint Results**：
  - CP-R1 ~ CP-R8：维持 `pass`（守卫与全量测试复跑一致）。
  - CP-U1（AC-9）：`fail`——字段③（如何查发行版名）已补齐，F-1 闭环；但修复引入新的跨入口矛盾 F-2（README vs 实现/07/实测），命中 AC-9"多入口不一致即不通过"。
- **Findings**：F-1 已闭环；新增 **F-2（actionable，minor）**，已固化为 Issue I-2（medium）。无 blocker、无 major；A-1 ~ A-6 维持 advisory。
- **Resume When**：实施方按 Issue I-2 修正 README:70 一句后，再开 Review R3（核对 README 与 07/实现一致、全量测试通过即可，无需改代码/快照）。

### Review R3（最终轮）
- **Result**：`pass`
- **触发**：实施方报告 Issue I-2 / F-2 已修复（仅文档，未改代码/快照），审查者以全新只读上下文复核。
- **Checks Performed（审查者亲跑，未改任何源码/测试/文档，未运行 install）**：
  1. `README.md:70` 现表述："`--smoke-ocr` 的图片可给发行版内路径（如 `/tmp/sample.png`），也支持 Windows 盘符路径（如 `C:\Users\me\sample.png`，自动转换为 `/mnt/c/Users/me/sample.png`、经 drvfs 访问）"——与 `07-ai-stack.md:65-66`（发行版内路径原样、盘符自动转换）逐字语义一致，与 `ai.py:19-33 to_distro_image_path` 行为及其测试一致。
  2. 盘符路径支持的运行时证据沿用 R2（`C:\...\img0.jpg` 被转换、`test -f` 通过、tesseract 执行；代码本轮未改动）。
  3. `tasks.md:127-140`：Issue I-2 置 completed，附逐字修复证据与一致性结论。
  4. 全量测试亲跑：`python -m pytest -q` → **502 passed in 10.80s**，TOTAL **97%**、ai.py **97%**，无回归。
  5. 正向只读冒烟：`verify --smoke-ocr /tmp/okw_smoke.png` → 退出 **0**，"本地图片离线识别成功（chi_sim+eng，识别 38 字符）"。
- **Checkpoint Results（终态）**：
  - CP-R1 ~ CP-R8：`pass`。
  - CP-U1（AC-9）：`pass`——三要素齐备：只读/离线边界（help epilog、README:61/70/72、07）；不碰密钥/模型/ollama（help epilog、README:72、07 Non-Goals）；如何查发行版名（parser 三处 name help、README:70、07:24）。无任何跨入口矛盾。
- **Findings 终态**：F-1、F-2 均已闭环；无 blocker/major，无未决可行动项。A-1 ~ A-6 为 advisory，不阻塞，可在后续维护中择机处理。
- **最终结论**：本变更 **pass**——AC-1 ~ AC-9 全部满足且每条具备独立证据；命令面、快照、文档、测试/覆盖率、wheel（Requires-Dist=0）与真实 WSL 只读实测均一致，安全边界（只读 preflight/verify、install 四要素、不碰密钥/模型/ollama/Gen2）成立。
