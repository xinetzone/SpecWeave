---
id: create-standardized-agent-exams-okf-wiki
title: Kaggle Standardized Agent Exams (SAE) OKF Wiki 教程
source:
  - https://www.kaggle.com/blog/standardized-agent-exams
  - https://www.kaggle.com/static/experimental/sae/SKILL.md
created: 2026-10-19
methodology: seven-concepts-cmd（知识沉淀 R→I→E→V；博文转 OKF 工作流）
content-sensitivity: public
status: completed
---

# Kaggle Standardized Agent Exams (SAE) OKF Wiki 教程 Spec

## Why

Kaggle 的 Standardized Agent Exams（SAE）提出了一种面向 AI Agent 的标准化考试体验；现有知识库已覆盖 Agent 评测理论和基准构建，但尚无该具体案例的可溯源专题。将公开博文与官方 SAE Skill 中可核实的内容整理为独立 bundle，可补充案例认知，同时避免把实验性产品描述误写成当前服务承诺。

## What Changes

- 在 AI 工程实践分组下新增可独立计数的 SAE 专题 bundle，并从现有 Agent 评测分组提供交叉入口。
- 以事实登记、官方核验和作者观点分层为基础，解释 SAE 的定位、考试流程、评分/成绩呈现、安全边界及已知局限。
- 与通用 Agent 评测和评测方法论专题建立交叉链接，明确内容分工。
- 不创建 Kaggle 顶级分组；不在本任务中注册 Agent、开始考试、提交答案或调用 SAE API。
- 不创建 `examples/`：官方流程虽有操作描述，但本任务没有经用户授权执行考试，且当前 SAE 页面受验证码阻挡，不能声称流程已实测可复现。

## Impact

- **Affected specs**: `.trae/specs/okf-wiki-ecosystem/` 中的本 Spec。
- **Affected systems**: `projects/awesome-okf-xs/doc/bundles/` 的 Agent 评测专题、相关父级导航、bundle 总索引及计数。
- **Proposed bundle**: `jishu/ai/practice/standardized-agent-exams/`
- **位置调整**：原嵌套提案无法被单独计数：`check-bundles-index.py` 将直接包含 `concepts/` 的 `ai-engineering-methodology` 视为锚点束，不再单独计数其内部目录。因此 SAE 改为独立实践束，评测索引保留交叉链接。
- **Related material**:
  - `agent-evaluation-wiki/`：通用 Agent 评测理论、指标与基准构建。
  - `agent-eval-methodology-wiki/`：Agent 评测方法论体系。
- **Workspace constraint**: 子模块现有未提交的 WorkBuddy 变更须原样保留；实施时只对导航和索引做最小增量编辑，不覆盖或重排无关内容。

## Content Sensitivity

来源为 Kaggle 公开博文及公开官方 Skill，无访问控制参数，判定为 **Public**。规划存放于 `.trae/specs/okf-wiki-ecosystem/`；教程按用户指定存放于 `projects/awesome-okf-xs/doc/bundles/`，并遵循该子项目的 OKF 规范。

## Background & Placement

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/practice/standardized-agent-exams/` | 选定 | 独立实践束可被目录计数门禁单独识别；评测分组保留导航交叉链接，继续连接通用评测与方法论专题。 |
| `jishu/ai/practice/ai-engineering-methodology/concepts/evaluation/standardized-agent-exams/` | 调整，不采用 | 该目录嵌套在直接含 `concepts/` 的 `ai-engineering-methodology` 锚点束内，按 `check-bundles-index.py` 语义不能作为独立束计数；用户确认改为独立实践束。 |
| 新建 Kaggle 或 Agent 考试顶级分组 | 排除 | 本次只有一个专题，现有评测分组语义匹配；新增分组会造成不必要的目录扩张。 |
| 并入 `agent-evaluation-wiki/03-benchmark-construction.md` | 排除 | 该篇已覆盖通用基准设计；SAE 的产品流程、考试机制与特定安全约束需要独立案例边界。 |

## Goals

- 建立一份适合读者理解和引用的 SAE 专题知识包，所有具体产品声明均能追溯到事实编号及来源。
- 将文章发表时的产品描述与官方 Skill 的操作规则分层呈现，并明确当前可用性未能核实。
- 通过 OKF bundle、导航、链接和计数门禁，使新增内容可从现有知识库入口到达。

## Non-Goals

- 不对 SAE 作独立的 Agent 基准排名或跨平台竞品评测。
- 不推断 Kaggle 当前服务可用、排行榜实时状态、考试内容更新状态或未被官方来源证实的评分算法。
- 不替用户处理 API 凭据，不调用注册、开始考试、提交答案等有副作用或需授权的端点。
- 不修改现有通用 Agent 评测理论以重复 SAE 专题内容。
- 不创建 Git commit 或 push；如需提交，须由用户另行明确授权。

## Functional Requirements

- **FR-1 (Traceable facts)**: 建立连续的 F 编号事实登记；区分博文所述、官方 Skill 所述、作者观点、核验补充及未能核实的声明。数字、日期、产品规则、安全要求等关键声明须核对官方来源；无法独立确认时标注 `SINGLE-SOURCE` 或 `UNVERIFIED`，不得补造证据。
- **FR-2 (Temporal accuracy)**: 把博文页面标注日期及其所述 MVP/产品状态作为有时间边界的历史陈述。将当前服务可用性单独处理；若公开 SAE 页面仍不可访问或返回验证码，应如实记录核验限制，不把它转述为服务已下线或仍可用。
- **FR-3 (Knowledge structure)**: 以 `concepts/` 承载 SAE 定位与评测问题、考试与结果流程、操作安全和评测边界；以 `references/` 保存文章事实清单及核验记录；根 `index.md` 汇总范围、已知边界、交叉链接和完整 toctree。
- **FR-4 (Safe operation)**: 只描述经官方来源支持的交互规则。显著说明 API key 的域名限制、开始考试前的用户明确同意、倒计时和提交次数等约束；不展示真实凭据，不在实施中调用注册或考试 API。
- **FR-5 (Navigable bundle)**: 新 bundle 遵循 OKF v0.2；根与子目录索引覆盖所有实际文档；父级评测导航和适用的总索引/计数保持一致，并与两个相邻专题互链、说明分工。

## Non-Functional Requirements

- **NFR-1 (Evidence integrity)**: 事实、作者观点、分析推论和未核实信息清楚区分；引用采用子项目约定的相对链接和来源字段。
- **NFR-2 (Scope discipline)**: 以最小增量方式新增专题，不复制通用评测章节，不新增无内容的 `examples/`。
- **NFR-3 (Workspace preservation)**: 对实施前已存在的子模块未提交改动进行基线核对，保留其内容和归属；不得通过回滚、清理或覆盖来消除冲突。
- **NFR-4 (Validation honesty)**: 可用时运行子项目规定的 toctree、UTF-8、bundle 计数和文档构建检查；若依赖缺失，执行可行的手工等效核验并明确报告未运行的门禁，不得宣称其通过。

## Constraints

- **Technical**: OKF v0.2 YAML frontmatter；bundle 根与每个含子目录的索引须有完整 toctree；Markdown 交叉引用使用相对路径。
- **Source**: Kaggle 官方博文 `https://www.kaggle.com/blog/standardized-agent-exams`；官方操作说明 `https://www.kaggle.com/static/experimental/sae/SKILL.md`；其他核验来源仅在确认其官方性和可达性后加入。
- **Access and authorization**: 官方 SAE 页面当前因验证码未能直接核实；考试流程包含时限及用户授权要求。本任务限定为只读学习和文档生成。
- **Repository**: 目标位于第一方子项目 `projects/awesome-okf-xs`；实施须遵循根仓库及子项目入口约束。

## Assumptions

- SAE 作为 Agent 评测领域的具体案例，独立落在既有 practice 分组，并由既有 `evaluation/` 索引交叉链接，比新建 Kaggle 分组更合适。
- 文章和官方 Skill 是核心一手来源；来源之间的重叠不视作独立交叉验证。
- 教程将描述官方 Skill 在核验时明确列出的规则，并在文档中记录核验日期，避免将易变规则包装成永久事实。
- 用户的 `/spec` 要求先审阅并批准规格与任务；批准前不修改 bundle。

## Acceptance Criteria

### AC-1: Bundle facts are traceable
- **Type**: `rule`
- **Given** the public Kaggle article and official SAE Skill are the primary sources
- **When** product claims are selected for the bundle
- **Then** each material claim has an F identifier and source attribution; article claims, Skill rules, opinions, corroboration, and unresolved claims are distinguished
- **Pass Condition**: No material number, date, operation limit, security rule, or current-availability assertion appears without a traceable source and an explicit evidence status.
- **Evidence**: Fact register, `references/article-source.md`, `references/verification.md`, and concept-page citations.

### AC-2: Product status is time-bounded
- **Type**: `rule`
- **Given** the article describes an experimental/MVP offering and the SAE page could not be directly verified
- **When** the bundle describes product maturity or availability
- **Then** historical article statements are dated and current availability is marked unverified unless an accessible official source confirms it
- **Pass Condition**: The bundle does not state that SAE is currently available, unavailable, or actively operating solely from the article or a CAPTCHA-blocked page.
- **Evidence**: Source verification record and wording in bundle `index.md`.

### AC-3: SAE is explained as a distinct evaluation case
- **Type**: `rubric`
- **Dimension**: Explanatory completeness and separation from generic Agent evaluation guidance.
- **Scale**: 1-5
- **Anchors**: 1 = largely paraphrases the article and confuses historical claims with current facts; 3 = explains the main product and flow but leaves material boundaries unclear; 5 = clearly explains the product, evaluation flow, result signals, safety constraints, and limitations, with sourced analysis distinct from facts.
- **Pass Threshold**: >= 4
- **Evidence**: Bundle contents, source cross-references, and independent adversarial review.

### AC-4: Bundle structure is complete and minimal
- **Type**: `rule`
- **Given** the bundle is a standalone member of the existing AI practice group and remains cross-linked from the evaluation group
- **When** the bundle is generated
- **Then** it uses OKF v0.2 frontmatter and complete root/subdirectory indexes and toctrees, is independently countable by the repository bundle counter, and does not include `examples/` unless both reproducibility questions are affirmatively supported by evidence
- **Pass Condition**: Every non-reserved Markdown page has valid frontmatter; every actual content file is reachable from its index; no empty or unverified example directory is introduced.
- **Evidence**: Bundle file inventory, frontmatter checks, toctree gate or documented manual equivalent.

### AC-5: Evaluation navigation is consistent
- **Type**: `rule`
- **Given** the new bundle and its two related Agent evaluation topics
- **When** navigation is updated
- **Then** the new bundle is reachable from the existing evaluation entry and linked to the relevant general evaluation material with a clear scope distinction
- **Pass Condition**: Parent toctrees and human-readable links resolve; all affected bundle/domain/total counts agree with repository ground truth.
- **Evidence**: Navigation diff, link/toctree checks, and bundle count gate or manual reconciliation.

### AC-6: Operational safety is preserved
- **Type**: `rule`
- **Given** the official Skill describes authenticated and time-limited exam actions
- **When** the tutorial explains registration, exam start, answer submission, or credentials
- **Then** it documents the stated authorization and credential boundaries without exposing secrets or presenting unexecuted live requests as tested operations
- **Pass Condition**: The bundle contains no real credential and does not claim that an SAE registration, exam-start, or answer-submission request was tested; current remediation/review actions remain read-only; and the task record explicitly states that no independent durable execution history is available to prove the full earlier execution history. Passing this criterion does not certify the absence of every earlier API request.
- **Evidence**: Read-only review of bundle examples and credential references, current-round action record, source verification, and the explicit historical-evidence limitation in `tasks.md`/`review.md`.

### AC-7: Existing submodule work is preserved
- **Type**: `rule`
- **Given** the submodule currently contains uncommitted WorkBuddy changes, including edits to shared indexes and an untracked bundle
- **When** the current remediation and review are performed
- **Then** the WorkBuddy paths remain present, and this remediation does not modify any submodule file
- **Pass Condition**: Fresh submodule status still lists the WorkBuddy-related modified indexes and untracked bundle; a scoped diff/status comparison across this remediation shows no submodule changes attributable to it. The missing implementation-time baseline is disclosed, and passing this criterion does not claim exact historical before/after preservation.
- **Evidence**: Submodule status and WorkBuddy-scoped diffs captured before and after the current remediation, plus the current-round write scope and the historical-baseline limitation recorded in `tasks.md`/`review.md`.

### Approved Acceptance-Criteria Adjustment

On 2026-10-19, the user approved revising AC-6 and AC-7 after Review R2 found that the original criteria required unavailable historical evidence. The revised criteria test current observable safety and workspace-preservation evidence and require disclosure of the historical limits; they do not infer that earlier actions did or did not occur. Review R2 remains an unchanged historical `blocked` result; the revised criteria are subject to fresh independent Review R3.

### AC-8: Validation results are reported honestly
- **Type**: `rule`
- **Given** the subproject may not have all optional documentation dependencies installed
- **When** validation is performed
- **Then** available official gates are run, or unavailable gates are replaced with explicit manual equivalents and the limitation is reported
- **Pass Condition**: No gate is described as passed unless its command or equivalent check actually ran and its result is recorded.
- **Evidence**: Command outputs and validation summary.

## Open Questions

- None blocking specification. Current SAE service availability remains an evidence limitation to be recorded, not an assumption to resolve through authenticated or exam-start API calls.
