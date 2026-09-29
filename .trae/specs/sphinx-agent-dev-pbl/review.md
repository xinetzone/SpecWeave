# 用 Sphinx 实现 AI 智能体开发 — 独立审查与评估标准（review.md）

> methodologies applied: TRAE-spec-mode（Review 独立审查门）+ seven-concepts（V 对抗审查 → I 洞察落地 → C 原子化交付）
> 本文件双重用途：① 作为学生项目的**评估标准/检查点**（对照 spec.md 的 AC）；② 作为对**本 PBL 设计本身**的独立对抗审查（V），暴露可改进点。
>
> 📎 配套文件：`insight.md` — 承载完整的 **V 四视角对抗审查记录**（8 条攻击）与 **I 洞察四元组**（4 条洞察 + 6 项边界条件）。本文件第二节为摘要，详细论证见 `insight.md`。

## 一、学生项目评估检查点（Review Checkpoints）

每条 AC 必须被覆盖；仅当单一可观察检查点能同时验证时才合并。

- [ ] **CP-R1**: 文档站构建成功（`make html` 退出码 0，`index.html` 存在）
  - **Type**: `rule` — **Covers**: AC-1 — **Evidence**: 构建输出 + 文件
- [ ] **CP-R2**: 智能体可运行且含工具调用
  - **Type**: `rule` — **Covers**: AC-2 — **Evidence**: 运行日志
- [ ] **CP-R3**: 密钥安全管理（无明文 Key 入库）
  - **Type**: `rule` — **Covers**: AC-5 — **Evidence**: `.gitignore` + 仓库搜索
- [ ] **CP-U1**: 文档工程质量（结构/导航/API/autodoc）
  - **Type**: `rubric` — **Covers**: AC-3 — **Scale**: 1–5 — **Anchors**: 1=空壳;3=有页面缺 API;5=完整含示例 — **Pass Threshold**: ≥ 4 — **Evidence**: 部署 URL + 截图
- [ ] **CP-U2**: 跨学科融合深度（三视角咬合）
  - **Type**: `rubric` — **Covers**: AC-4 — **Scale**: 1–5 — **Anchors**: 1=孤立;3=拼贴;5=元文档闭环咬合 — **Pass Threshold**: ≥ 4 — **Evidence**: draft + 反思
- [ ] **CP-U3**: 元认知与反思质量
  - **Type**: `rubric` — **Covers**: AC-6 — **Scale**: 1–5 — **Anchors**: 1=套话;3=描述过程;5=真实盲点洞察 — **Pass Threshold**: ≥ 4 — **Evidence**: 反思报告

### 过程性评价量规（占 40%）
| 维度 | 1 分 | 3 分 | 5 分 | 权重 |
|---|---|---|---|---|
| 参与度 | 被动 | 基本参与 | 主动推进并补位 | 15% |
| 协作 | 各自为战 | 有分工 | 高效协作且互评互助 | 15% |
| 探究精神 | 照做 | 会提问 | 主动查证文档并试错 | 10% |

### 终结性评价量规（占 60%）
| 维度 | 对应检查点 | 权重 |
|---|---|---|
| 可运行智能体 | CP-R2 | 20% |
| 文档站质量 | CP-U1 / CP-R1 | 20% |
| 跨学科融合 | CP-U2 | 10% |
| 展示路演 | CP-U1(展示部分) | 5% |
| 反思报告 | CP-U3 | 5% |

---

## 二、对本 PBL 设计的对抗审查（V — Adversarial Review）

> 七概念要求：使用 F（第一性原理）推导方案后，**必须**执行 V 从多视角攻击，暴露隐含假设与落地风险。以下为四视角魔鬼代言人。

### 视角 1：学生（认知负荷）
- **攻击**：同时学 Agent Loop + Sphinx + Git/CI + LLM API，初学者极易在前两周被环境劝退。
- **发现（advisory）**：需在前置微课（FR-B）与 Task1/Task2 之间插入"零代码文档站 30 分钟成功体验"，先建立正反馈再上难度。
- **缓解**：spec.md Non-Goals 已限制框架深度；建议 Task1 拆出"纯写一篇 MyST 文档并构建"作为 0 号热身任务。→ **【已落地】** 见 `tasks.md` Task0（含零代码约束、沙盒一键方案、无环境降级路径与"不教配置"纪律）。

### 视角 2：教师（落地成本）
- **攻击**：CI 部署依赖 GitHub/外网，部分学校机房无法访问；LLM API 配额与费用不可控。
- **发现（actionable→建议固化）**：spec.md Open Questions 未给"无外网"兜底方案。
- **缓解**：明确 ollama 本地模型替代路径 + Read the Docs/内网静态托管替代 GitHub Pages；在 NFR 中标注"离线降级方案"。

### 视角 3：产业/工程真实性
- **攻击**：`autodoc` 把代码抽进文档只是"有文档"，未必"文档好"；学生可能堆函数不写说明。
- **发现（actionable）**：AC-3 仅看 autodoc"生效"，未要求 docstring 质量。
- **缓解**：在 AC-3 锚点 5 中增加"核心函数均有有意义 docstring"；建议在 Task5 加 `rule` TR 校验 docstring 非空。

### 视角 4：教育学有效性
- **攻击**：元文档闭环（agent 生成文档草稿）可能沦为"让 AI 代写文档"，反而弱化人类元认知。
- **发现（advisory）**：须强调"人工审校并入"为必需环节，否则违背 G3 素养目标。
- **缓解**：Task6 描述已注明"学生人工审校后并入"；建议在反思报告中要求对比"AI 草稿 vs 我的最终版"差异。

### V 审查结论
设计本质方向成立（F 推导稳固），但需在 **spec.md** 补充：① 离线降级方案；② AC-3 增加 docstring 质量门槛；③ 前置热身任务。上述 actionable 项已映射为下方 Issue。

> **【第二轮 V 补强·session sc-20260929-sphinx-agent-pbl】** 首轮 V 仅覆盖 4 个教学场景视角，未达 V 门"4 视角 + ≥5 条意见 + 采纳 ≥2 条"标准。第二轮按标准四视角（魔鬼代言人/新人/老板/未来）重新审查，共产出 **8 条实质攻击（含 2 条 P0）**，采纳 7 条，固化为 Issue I-3~I-6，详见 `insight.md`。核心修正：**文档定位从"理解来源"改为"理解检验"（文档先行）**、**AI 协作必须后置**、**增加过程证据防评价失真**。

---

## 三、审查 Issue（由 V 发现的 actionables 固化）

## Issue I-1: 补充离线/无外网降级方案
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review V（视角 2）
- **Description**: spec.md Constraints/Open Questions 未覆盖"机房无法访问 GitHub/LLM API"场景。
- **Acceptance Criteria Addressed**: NFR-1, AC-5
- **Test Requirements**:
  - `rule` TR-I-1.1: spec.md 新增"离线降级"小节，给出 ollama 本地模型与内网静态托管（如 `python -m http.server` 或自建 RTD）路径；Evidence: 文档增补。
- **Completion Evidence**: spec.md Constraints 的 Technical 项已增补"离线降级"路径（ollama + `python -m http.server _build/html`）

## Issue I-2: AC-3 增加 docstring 质量门槛
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review V（视角 3）
- **Description**: 当前 AC-3 仅验证 autodoc 生效，未约束 docstring 质量，可能被"空文档"钻空。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-I-2.1: AC-3 anchor 5 明确"核心函数均有非空、有意义的 docstring"；Evidence: 验收标准文本。
- **Completion Evidence**: spec.md AC-3 anchor 5 已加入"核心函数均有非空且有意义的 docstring"门槛

## Issue I-3: 文档定位修正 + 文档先行任务
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Discovered By**: 第二轮 V（魔鬼代言人 A-1）+ 洞察 I-1
- **Description**: 原 F 推导"文档即调试"存在因果倒置风险，文档可能沦为事后粉饰。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-I-3.1: spec.md 第一性原理附注修正为"文档是理解的检验"；Evidence: 文档文本。
  - `rule` TR-I-3.2: tasks.md Task2 改为"文档先行"，先产出 `api-draft.md` 再实现；Evidence: Task2 描述。
- **Completion Evidence**: spec.md 第 5 条公理已修正；tasks.md Task2 已改为"文档先行"并新增 TR-2.4

## Issue I-4: AI 协作后置（先手写后 AI）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Discovered By**: 第二轮 V（未来视角 A-8）+ 洞察 I-3
- **Description**: 若先引入 AI 生成文档，学生在能力建构期会丧失结构化表达能力。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-I-4.1: tasks.md Task2 标注"禁止使用 AI"，Task6 才引入 AI 协作，且含差异记录要求；Evidence: Task2/Task6 描述。
- **Completion Evidence**: Task2 Notes 已加"必须手写"约束；Task6 新增 TR-6.2 差异记录；tasks.md 顺序约束小节已明确

## Issue I-5: 增加过程证据防评价失真
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Discovered By**: 第二轮 V（老板视角 A-6）+ 洞察 I-4
- **Description**: 若学生用 AI 生成大部分产出，"学生真实能力"评估失真，课程无法持续开设（P0）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-I-5.1: AC-6 增加过程证据（Git 多次原子提交 + 现场口头解释）；Evidence: spec.md AC-6。
  - `rule` TR-I-5.2: tasks.md Task7 增加现场答辩与提交历史检查；Evidence: Task7 TR-7.2/TR-7.3。
- **Completion Evidence**: spec.md AC-6 已增过程证据列；tasks.md Task7 新增 TR-7.2（≥5 次原子提交）与 TR-7.3（现场口头解释）

## Issue I-6: 新人可用性补强（初始化命令 + 术语表）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: 第二轮 V（新人视角 A-3/A-4）
- **Description**: `sphinx-quickstart` 交互式提问会卡住新人；跨学科术语无解释。
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-I-6.1: tasks.md Task1 补充非交互式初始化命令；Evidence: Task1 命令块。
  - `rule` TR-I-6.2: Task2 交付物含 `glossary.md`（≥7 术语）；Evidence: TR-2.2。
- **Completion Evidence**: Task1 已加 `--no-sep -q --language zh_CN` 一键命令；Task2 新增 glossary.md 与 TR-2.2

## Issue I-7: Task0 零代码热身任务
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: 首轮 V（学生视角 A-1，原为 advisory）
- **Description**: 初学者第一次失败点集中在 Task1 环境搭建，易在前两周劝退。
- **Acceptance Criteria Addressed**: AC-3（预备性）
- **Test Requirements**:
  - `rule` TR-I-7.1: `tasks.md` 新增 Task0，须先于 Task1，且含零代码约束与降级路径；Evidence: Task0 描述。
  - `rubric` TR-I-7.2: 验收以"正反馈达成度"为准（TR-0.3），不纳入正式评分权重；Evidence: Task0 Notes。
- **Completion Evidence**: `tasks.md` 已新增 Task0（含 TR-0.1/TR-0.2/TR-0.3、沙盒一键方案、无环境降级、"不教配置"纪律）；依赖图与顺序约束已更新；`review.md` 视角 1 已标注"已落地"

---

## 四、Review History

### Review R1（设计态独立审查）
- **Result**: `fail`（发现 2 条 actionable，已固化为 I-1、I-2；另 2 条 advisory 已写入缓解）
- **Evidence**: 见第二节四视角攻击记录
- **Blocked By**: 无
- **Resume When**: I-1、I-2 在 spec.md 修订完成后，开启 R2 复审

### Review R2（复审）
- **Result**: `pass`
- **Evidence**: I-1、I-2 均已 `completed`（spec.md Constraints 增补离线降级、AC-3 anchor 5 增补 docstring 门槛）；全部 CP（CP-R1~CP-R3、CP-U1~CP-U3）定义完整且阈值明确；无遗留 actionable 发现。
- **Blocked By**: 无

### Review R3（第二轮 V 补强后复审，session sc-20260929-sphinx-agent-pbl）
- **Result**: `pass`
- **Checks Performed**:
  - 核对 V 门标准（4 视角 / ≥5 条意见 / 采纳 ≥2 条）：8 条攻击、7 条采纳 → **达标**
  - 核对 G2 门标准（洞察 ≥3 条 / 四元组完整 / 维度独立）：4 条洞察、四元组完整 → **达标**
  - 核对 Issue I-3~I-6 的 Completion Evidence 是否真实落盘 → **全部落实**
  - 核对 tasks.md 顺序约束（文档先行、先手写后 AI）是否写入 → **已写入**
- **Evidence**:
  - `insight.md` 已创建，含 V 四视角 8 条攻击表 + I 四条洞察四元组 + 6 项边界条件表
  - `spec.md`：第一性原理附注新增第 5/6/7 条（文档定位修正、AI 顺序约束、可评估性前置约束）；AC-6 重写为含过程证据
  - `tasks.md`：Task1 非交互命令、Task2 文档先行+术语表、Task3 一致性校验、Task6 差异记录、Task7 现场答辩、顺序约束小节
  - 格式缺陷修复：Task 5 的 `Priority` 反引号未闭合已修正
- **Checkpoint Results**:
  - CP-R1~CP-R3 (`rule`): `pass`
  - CP-U1~CP-U3 (`rubric`): `pass`（阈值与锚点定义完整，可执行）
- **Findings**: 无遗留 actionable（V 攻击 A-7"过渡形态风险"为部分成立，已作 advisory 处理：明确课程目标上移至信息架构与可解释性设计）
- **Blocked By**: 无

### Review R4（Task0 补丁后复审，session sc-20260929-sphinx-agent-pbl）
- **Result**: `pass`
- **Checks Performed**:
  - 核对 Task0 是否满足原子化（单一职责/可独立验证/可独立交付）→ **达标**
  - 核对 Task0 前置关系是否写入依赖图 → **已更新**
  - 核对 AC 覆盖完整性是否受影响 → **未受影响**（Task0 为预备性达成 AC-1/AC-3，不改变原有映射）
  - 核对是否与 Task1 职责重叠 → **无重叠**（Task0 零代码/不教配置；Task1 才做环境与初始化）
- **Evidence**:
  - `tasks.md` 新增 Task0（含 3 条 TR、零代码约束、沙盒一键方案、无环境降级路径、"不教配置"纪律）
  - 依赖图已插入 `Task0 → Task1` 前置，并新增顺序约束条目
  - `review.md` 视角 1 的 advisory 已标注"【已落地】"并回指 Task0
  - Issue I-7 已固化为 `completed`
- **Checkpoint Results**:
  - CP-R1~CP-R3 (`rule`): `pass`
  - CP-U1~CP-U3 (`rubric`): `pass`
- **Findings**: 无遗留 actionable（首轮 A-1 advisory 已由 Task0 落地，I-7 已完成）
- **Blocked By**: 无

> 完成判定：I-1~I-7 全部 `completed`，R4 结果 `pass`，所有 CP 达标，无遗留 actionable，**设计框架验收通过（含 Task0 补丁）**。

### Review R5（待决问题落定后复审，session sc-20260929-open-questions）

- **Result**: `pass`
- **Checks Performed**:
  - 核对 `spec.md` 十二节的 3 个 Open Questions 是否全部由 `[ ]` 转为已决 → **3/3 已决**（DQ-1/DQ-2/DQ-3）
  - 核对每条决策是否有"依据 + 被否选项 + 可证伪信号 + 回滚条件"四要素 → **3/3 完整**
  - 核对决策是否回写到 `tasks.md` 与 `handbook/`（避免"文档说 A、课上做 B"）→ **已回写**（Task3/Task4/Task6 + 对应手册 4 处）
  - 核对 G2 门（洞察四元组完整）→ **新增 I-8/I-9/I-10 三条，四元组齐全**
  - 核对 G3 门（模式可迁移：触发条件 + 核心步骤 + 反模式）→ **3 条判据 + 4 条反模式**
  - 核对 G4 门（行动项原子化：单一职责 + 可独立验证）→ **9 条行动项，各绑定单一落点**
  - 核对 G1 门适用性 → **不适用**（决策任务的输入为既有设计文档而非新采集事实，不走 R 阶段）
  - 核对 V 门适用性 → **不强制**（未经 F 自零推导）；但已自查隐含假设并配可证伪信号
  - 核对 AC-4 与该决策的一致性 → **已修正**（AC-4 原为 rubric 硬门槛却由"选做"任务承载，属评估结构自相矛盾，现由 Task6 档 A 保证可达）
  - 核对受影响的 TR 是否更新 → **TR-3.1 改为档位中立、新增 TR-4.2、TR-6.3**
  - 核对手册截图位清单同步 → **新增 S7-5 与 S3-7，总数 35→37，并标注 3 处条件性截图位**
- **Evidence**:
  - 新建 [`decisions.md`](decisions.md)（Decision Log + 3 条决策完整论证 + RACI + G1-G4 记录 + 9 条行动项）
  - `spec.md`：§九 Constraints（ollama 端点 + 内网 Git 方案 + SDK 统一）、§八 NFR-3（三档制）、§十一 AC-4（档位中立 + 折半规则）、§十二 Open Questions → Resolved Decisions
  - `tasks.md`：Task3 三档部署 + 档位中立 TR-3.1、Task4 SDK 统一 + TR-4.2、Task6 三档制 + TR-6.3、依赖图与顺序约束更新
  - `handbook/`：task-4（换厂商只改 .env + 否决 provider 抽象）、task-3（离线章节 + 常见报错新增网络不可达行）、task-6（三档说明 + 诚实性红线 + 档 C 做法）、task-7（api-draft 自测点 + 反思问题 4 + 评价表注解）、README（Task6 必做/选做澄清）、shots/README
- **Checkpoint Results**:
  - CP-R1~CP-R3 (`rule`): `pass`
  - CP-U1~CP-U3 (`rubric`): `pass`
- **Findings**: 无遗留 actionable。发现并修正设计内部矛盾 1 处（AC-4 硬门槛由选做任务承载）；发现并修正问题表述缺陷 1 处（DQ-3 的"必做 vs 选做"实为假二分）。
- **Blocked By**: 无

> **完成判定（R5）**：3 个 Open Questions 全部落定并回写下游，G2/G3/G4 达标，无遗留 actionable。**设计框架（含决策落定）验收通过。**

---

## 五、评估权重与 Task6 档位的关系（R5 补充说明）

| 评价维度 | 权重 | 载体 | 档位敏感性 |
|---|---|---|---|
| 可运行智能体 | 20% | Task4/Task5 | 档位无关 |
| 文档站质量 | 20% | Task1~Task5 | 档位无关 |
| **过程性评价** | **40%** | 全程 | 档位无关 |
| 跨学科融合 | 10% | **Task6** | **档 A/B 全额；档 C 折半** |
| 展示路演 | 5% | Task7 | 档位无关 |
| 反思报告 | 5% | Task7 | 档位无关 |

> ⚠️ **上表是本次决策最重要的产出**：它证明"跨学科融合 10%"这一项**在零 Token 成本下依然可达**（档 A）。
> 这消除了原设计中"AC-4 是硬门槛、Task6 却是选做"的结构性矛盾——
> **如果当时没有发现这个矛盾，没做 Task6 的学生将 100% 拿不到这 10%，
> 而教师会误以为"这是学生自己没做选做题"。**
