---
id: "create-agent-workspace-starter-adversarial-review"
title: "V-对抗审查——四视角攻击与修正记录"
source: "spec.md（AC-5/AC-6/AC-9）+ 产品全量交付物（apps/dev-tools/agent-workspace-starter/）+ 子代理实测走查（2026-10-07）"
created_at: "2026-10-07"
content-sensitivity: "public"
related_spec: "spec.md"
related_tasks: "tasks.md#Task 8"
---

# V-对抗审查 —— 四视角攻击与修正记录

> 本文件为 Task 8 产出。审查对象：产品 `apps/dev-tools/agent-workspace-starter/` 全部交付物（README / starter 40 文件 / guide 5 文件 / walkthrough 4 文件 / bootstrap-prompt.md / skill/SKILL.md / scripts/verify_starter.py）。
> 审查方式：文本审读 + **新手视角实测走查**（在临时目录 `%TEMP%\aws-dress-rehearsal\` 模拟买家项目完整走一遍）。
> 质量门 TR-8.1：≥5 条意见（含视角 / 问题 / 建议），采纳 ≥2 条且修正落地可查。
> 审查基线（修正前）：starter 40 文件 / 1429 行；全产品 52 个 Markdown / 174 条相对链接 / 0 断链；`verify_starter.py` 默认态 exit 0。

## 一、意见总表

| 编号 | 视角 | 严重度 | 问题（含文件与位置证据） | 建议 | 处置 |
|---|---|---|---|---|---|
| A-1 | 新手 / 时间 | **高** | 自检命令的运行位置错误且第二命令根本跑不通。`guide/01-bootstrap.md#L59-L69` 标注「照抄（在套件目录内运行）：`python ..\scripts\verify_starter.py`」——若「套件目录」指产品根 `agent-workspace-starter\`，则 `..\scripts\` 指向不存在的 `dev-tools\scripts\`；紧随其后的「直接对项目目录运行：`python verify_starter.py --target <你的项目>`」更不成立（脚本不在买家项目里）。实测两份命令均以 `Errno 2 No such file or directory` 失败（见 §二）。`README.md#L110` 的「运行 `python scripts/verify_starter.py`」同样未写明「须在套件根目录运行」，`bootstrap-prompt.md#L110` 检查点漏写 `<套件目录>/` 前缀。新手会在此卡壳 3~8 分钟，直接侵蚀 01 段 15 分钟时间盒。 | 明确「自检脚本位于套件根 `scripts/`、不随 starter 拷入项目」；把命令统一为「在套件根运行 `python scripts\verify_starter.py`」，定向核验为「在套件根运行 `python scripts\verify_starter.py --target "<你的项目>"`」，并让 README / guide / bootstrap-prompt 三处口径一致。 | **已采纳并修正**（guide/01、README §四、bootstrap-prompt 完成检查点） |
| A-2 | 运营者 | **中** | 许可覆盖与上游许可冲突、且缺 Apache-2.0 归属声明。上游 SpecWeave 仓库为 **Apache License 2.0**（`LICENSE#L1-L2`），而 starter 规范内容萃取自其 `.agents/`。`starter/LICENSE-NOTICE.md` 与 `README.md §五` 仅写「禁止转售 / 重新分发为同类付费产品」，未说明上游许可与归属：①依 Apache-2.0 §2，被许可人对「Derivative Works」享有 no-charge/royalty-free 的 reproduce/distribute/sublicense 权利，笼统禁止再分发对**源自上游的规范内容**不可执行；②Apache-2.0 §4 要求再分发衍生作品时保留归属声明，当前 LICENSE-NOTICE 未携带，存在合规缺口。 | 在 LICENSE-NOTICE 增加「内容来源与许可」段：指明萃取自 SpecWeave（Apache-2.0）并附许可链接；界定「禁止转售」仅适用于本套件**原创部分**（教程 / 演练 / 提示词 / 脚本 / 编排），源自上游的规范内容仍依 Apache-2.0 授权；要求在再分发时保留本说明与许可链接。README §五 同步一条口径。 | **已采纳并修正**（LICENSE-NOTICE 新增段、README §五新增条） |
| A-3 | 运营者 / 买家 | **低** | Python 版本口径前后矛盾。`README.md#L106` 与 `#L132`、`guide/README.md#L29` 声称 **Python 3.12+**；而产品自身内容 `scripts/verify_starter.py#L21`（「兼容 Python 3.10+」）、`walkthrough/step-2-implement.md#L20`、`starter/.agents/ONBOARDING.md#L47`（实践 17「脚本要求 Python 3.10+」）均为 **3.10+**。脚本仅用标准库（argparse/re/sys/pathlib），实际下限为 3.10；对外宣称 3.12+ 无谓抬高门槛且与套件自述冲突。 | 统一为与脚本自述一致的 **Python 3.10+**，降低买家环境门槛，消除同名不同口径。 | **已采纳并修正**（README ×2、guide/README ×1） |
| A-4 | 新手 | **低** | 演练样例与 spec 验收点不一致，易生「样例对不上」困惑。`walkthrough/step-2-implement.md#L88-L99` 的实测样例目录为 `starter-walkthrough-test/`（含 `docs/guide.md`、`docs/assets/logo.svg`、`src/main.py`），而 spec 的 `AC-1` Given 与 `walkthrough/step-3-verify.md#L18` 用的是 `demo/`（仅 `README.md` + `src/main.py`）。新手严格按 AC-1 建 `demo/`，输出必与样例不同，会误以为实现有误。 | 在样例处补一句说明：样例额外含 `docs/` 子结构以演示多层缩进；按 AC-1 只建 `demo/` 时输出行数相应减少属正常。 | **已采纳并修正**（walkthrough/step-2 补注） |
| A-5 | 时间 | **中** | 时间盒存在失衡点：00/01 偏宽松，**02 段 25 分钟偏紧**。02 段要求：读 `guide/02-first-task.md`（86 行）+ `walkthrough/` 4 文件（336 行）+ 落到 `spec/tree-viewer/spec.md`（照抄块 73 行）+ 写 `tree_view.py`（66 行）+ 运行 + 逐条核对 3 条 AC（含 PowerShell 查 `$LASTEXITCODE`）。若要按演练指引顺带核对 `spec-creation-precheck.md`（65 行）与 `task-template.md`（87 行），实际阅读量超 600 行，25 分钟对**从零照抄型新人**偏紧；一旦叠加 A-1 的命令卡壳，02 段极易超时盒。 | 建议在 02 段增加「卡住时提速提示」（只读 guide/02 与 walkthrough，precheck 与 task-template 留到 03 深潜），或把 02 段预算由 25 分钟上调至 30 分钟并压缩 00/03。 | **记录待办**（涉及四段时间盒再平衡，属 Task 4 教程重构范围，本任务不改时间盒以免牵动 AC-5 行数预算；转 Task 9 前确认） |
| A-6 | 买家 | **低** | 「全貌导览 18 类目」卖点与实物的感知落差。`README.md#L32` 称「18 个规范类目各保留代表文件并附一句话导览」，但 18 类目中的 8 个扩展类目（modules/teams/prompts/tools/worlds/capabilities/cases/systems）仅各 3 行一句话导览（如 `starter/.agents/modules/README.md` 共 3 行，无代表文件），占比 44% 的「类目」实质是占位导览；买家按卖点期待「每类目代表文件」时会有落差。 | 可在 README 卖点处把「18 类目各保留代表文件」精确为「11 个核心类目各留代表文件 + 8 个扩展类目各附一句话导览」。 | **不采纳**（理由：20 文件硬约束下 8 扩展类目无代表文件属 insight.md 洞察 3 的既定设计——以一句话导览规避占位空洞；AC-6 只要求「每类目代表文件含一句话导览」且已达标；改为「11+8」措辞会削弱卖点且需同步多文件口径，收益不抵风险；保留待运营文案微调） |
| A-7 | 运营者 | **低** | 获取方式仍为占位。`README.md#L126` 「获取方式：<待运营者填写>」。 | 上架前由运营者填入收款 / 交付渠道；本次不阻塞。 | **记录待办**（spec Assumptions 已声明「获取 / 收款方式由运营者在站外提供」，属既定占位，非缺陷） |

**意见覆盖**：买家（A-3、A-6）、时间（A-1、A-5）、新手（A-1、A-4）、运营者（A-2、A-3、A-7）——四视角各 ≥1 条。总计 7 条 ≥5 ✓；采纳 4 条 ≥2 ✓。

## 二、新手视角实测走查记录（模拟买家）

**走查环境**：Windows / Python 3.14；临时目录 `%TEMP%\aws-dress-rehearsal\`（走查后已清理）。**走查角色**：模拟一名「只看教程、照抄命令、不具备 SpecWeave 背景」的买家。

| 步 | 动作（严格照教程） | 观察 / 障碍 | 结果 |
|---|---|---|---|
| 0 | 建空项目 `myproject\` | 无 | 就绪 |
| 1 | 按 `guide/01-bootstrap.md#L20-L24` 三条 `Copy-Item` 拷 starter | 命令可直接跑通；首个 `Copy-Item` 目标 `.agents` 不存在时脚本自动创建并递归拷贝，无报错 | ✅ 项目根出现 `AGENTS.md` / `.agents/` / `LICENSE-NOTICE.md`，共 40 文件 |
| 2 | 读简版装载提示词、模拟智能体读取 | 纯文本步骤，无需命令；提示词措辞清晰 | ✅ 可复述 |
| 3 | 按 `#L59` 「在套件目录内运行 `python ..\scripts\verify_starter.py`」 | **卡壳点**：照字面从产品根运行 → `can't open file '...\apps\dev-tools\scripts\verify_starter.py'`（exit 2）。只有「从 `guide\` 目录运行」或「从产品根运行 `python scripts\verify_starter.py`」才成立，「套件目录」措辞有歧义 | ❌ 失败（A-1 证据） |
| 3b | 按 `#L67` 「直接对项目目录运行 `python verify_starter.py --target <你的项目>`」 | **卡壳点**：脚本不在买家项目内，从项目根运行 → `can't open file '...\myproject\verify_starter.py'`（exit 2） | ❌ 失败（A-1 证据） |
| 3c | 自行改用「从 guide 目录运行 `python ..\scripts\verify_starter.py`」 | 通过：40/40 文件齐备、「启动协议」命中、81 条链接全可达，exit 0 | ✅ 通过 |
| 4 | 按 `walkthrough/step-1` 照抄 `spec/tree-viewer/spec.md`（含 frontmatter + Overview/Goals/FR-1~3/AC-1~3） | 照抄块完整可整体粘贴；预检两问有明确答案 | ✅ 落盘成功 |
| 5 | 按 `walkthrough/step-2` 照抄 `tree_view.py`（66 行，仅 os/argparse） | 照抄后可运行；无第三方依赖 | ✅ 文件就位 |
| 6 | 复现 `walkthrough/step-2#L86-L99` 样例：建 `starter-walkthrough-test/`（README.md + docs/guide.md + docs/assets/logo.svg + src/main.py），运行 `python tree_view.py . --max-depth 2` | 输出与文档样例**逐字一致**（`starter-walkthrough-test/` → README.md / docs/（assets/、guide.md）/ src/（main.py）），exit 0 | ✅ 与样例一致 |
| 7 | 按 `walkthrough/step-3` 核对 AC-3：`python tree_view.py not-exist; $LASTEXITCODE` | 打印「错误：目录不存在 -> not-exist」，退出码 2 | ✅ AC-3 通过（AC-1/AC-2 经步骤 6 复现通过） |
| 8 | 阅 `guide/00`、`03` | 内容与 checkpoint 清晰；「入口层轻量」论证有实测数据支撑 | ✅ |

**走查结论**：产品的**核心链路（拷贝 → 演练 → 验收）可照抄跑通且输出与文档逐字一致**，新手不会在实现环节受阻；**唯一硬卡壳集中在 01 段的「自检命令位置」**（A-1），两处命令照字面均失败，须读者自行猜出正确路径。

**耗时估算（照抄型新人）**：00 概览 8~10 min；01 装载 8 min（**若撞上 A-1 卡壳 +3~8 min 排障**）；02 首个任务 20~28 min（偏紧，见 A-5）；03 进阶 6~8 min。合计 42~54 min（顺利）/ 50~62 min（撞卡壳）——**60 分钟总体成立，但余量薄，A-1 是最大超时变量**（已修正）。

## 三、修正清单（采纳项，前后对照）

| # | 文件 | 修正前 | 修正后 | 对应意见 |
|---|---|---|---|---|
| 1 | `guide/01-bootstrap.md`（§步骤3 + 完成检查点） | `python ..\scripts\verify_starter.py`（标注「在套件目录内运行」，从产品根失败）+ `python verify_starter.py --target <你的项目>`（从项目根失败） | `python scripts\verify_starter.py`（标注「在套件根目录运行，脚本不在你的项目里」）+ `python scripts\verify_starter.py --target "<你的项目>"`；检查点同步改为「在套件根目录运行」 | A-1 |
| 2 | `README.md`（§四 步骤3） | 「运行 `python scripts/verify_starter.py`」 | 「**在套件根目录**运行 `python scripts/verify_starter.py`」 | A-1 |
| 3 | `bootstrap-prompt.md`（完成检查点） | `python scripts/verify_starter.py --target <目标项目>` | `python <套件目录>/scripts/verify_starter.py --target <目标项目>` | A-1 |
| 4 | `starter/LICENSE-NOTICE.md` | 仅 6 条使用边界，无来源与许可声明 | 新增「## 内容来源与许可」段：指明萃取自 SpecWeave（Apache-2.0）+ 许可链接 + 界定「禁止转售」仅适用原创部分 + 再分发须保留归属 | A-2 |
| 5 | `README.md`（§五 许可） | 无上游许可口径 | 新增一条：净化内容依 Apache-2.0；禁止转售仅针对原创部分；链向 LICENSE-NOTICE 新段 | A-2 |
| 6 | `README.md`（§四前置、§七 FAQ）、`guide/README.md`（前置） | Python 3.12+（×3） | Python 3.10+（与脚本自述一致） | A-3 |
| 7 | `walkthrough/step-2-implement.md`（§五 样例说明） | 无样例与 AC-1 差异说明 | 补注：样例含 `docs/` 演示多层级；按 AC-1 只建 `demo/` 时输出行数减少属正常 | A-4 |

**改动范围核实**：仅触及 `apps/dev-tools/agent-workspace-starter/` 内 6 个文件（README.md、bootstrap-prompt.md、guide/01-bootstrap.md、guide/README.md、walkthrough/step-2-implement.md、starter/LICENSE-NOTICE.md）。**未触碰 `.agents/`、`templates/`，未删除任何 starter 文件，未引入依赖**。

## 四、修正后复测

| 复测项 | 命令 / 方法 | 结果 |
|---|---|---|
| ① 自检脚本默认态 | `python scripts/verify_starter.py`（套件根） | **exit 0**（40/40 文件齐备、「启动协议」命中、81 条链接全可达） |
| ② 修正后的定向核验命令 | `python scripts\verify_starter.py --target "%TEMP%\aws-dress-rehearsal\myproject"`（套件根） | **exit 0**（对已装载的买家项目同样通过，验证 A-1 修正后的命令确实可用） |
| ③ 全产品相对链接 | 临时 Python 片段复跑全产品链接检查（跑后即弃） | 扫描 52 个 Markdown、核验 **175 条相对链接、0 断链** |
| ④ 规模约束 | 枚举 `starter/` 文件数 | **40 文件 ≤ 50** ✓；starter 行数 1429 不变 |

> 说明：修正使全产品链接数由 174 → 175（README §五 新增 1 条指向 `starter/LICENSE-NOTICE.md#内容来源与许可`），断链仍为 0。
> 附带提示（不影响验收）：`tasks.md` 的 Task 7 证据记「README 132 行」，修正后为 133 行；`walkthrough/` 合计由 336 → 338 行（step-2 +2），教程 + 演练合计 700 行，仍远低于 NFR-1 的 ≤1500 行硬门。上述 tasks.md 证据属 Task 9 收尾时同步范围，本任务不修改 tasks.md。

## 五、四视角小结

- **买家视角**：卖点（60 分钟 / 全貌导览 / 程序化可验证）与实物基本一致，「本套件不包含什么」一节有效预防预期错配；主要瑕疵是 Python 版本口径矛盾（A-3，已修正）与「18 类目」措辞的感知落差（A-6，保留作运营文案微调）。9.9 元价值感知成立：交付物为可拷、可自检、可复用的完整内容包。
- **时间视角**：60 分钟（10/15/25/10）总体成立，实测走查合计 42~54 分钟（顺利态）；但余量薄，02 段（25 min）偏紧（A-5 记录待办），且 A-1 的自检命令卡壳是最大超时变量——修正后此变量消除。
- **新手视角**：核心链路可照抄跑通，样例输出逐字一致，无实现层障碍；唯一硬卡壳（自检命令位置，A-1）与样例/AC 不一致（A-4）均已修正，走查中未发现其余阻断点。
- **运营者视角**：多处口径（README / LICENSE-NOTICE / FAQ / bootstrap-prompt / SKILL.md）整体一致；最大风险是上游 Apache-2.0 与「禁止转售」的许可张力与归属缺口（A-2，已修正）；「获取方式」占位（A-7）属既定待填，不阻塞。更新维护成本低——纯 Markdown + 单标准库脚本，无构建、无依赖。

## 六、结论

Task 8 四视角对抗审查完成：产出 **7 条意见**（四视角各 ≥1 条），**采纳并落地 4 条修正**（A-1/A-2/A-3/A-4，覆盖新手卡壳、许可合规、口径一致、样例一致性），2 条记录待办（A-5 时间盒再平衡、A-7 获取方式填写），1 条不采纳并附理由（A-6）。修正后复测：自检 exit 0、全产品 175 条相对链接 0 断链、starter 40 文件 ≤50，NFR-1 规模约束保持。**TR-8.1 达标**；AC-5 的「模拟新人试走记录」证据已在 §二 补强。产品可进入 Task 9 收尾（区域登记 + 原子提交）。