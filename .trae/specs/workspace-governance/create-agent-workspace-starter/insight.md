---
id: "create-agent-workspace-starter-insight"
title: "I-洞察——产品化取舍标准与体验设计"
source: "facts.md（2026-10-07 实测基线）+ spec.md（AC-5/AC-6/AC-9）"
created_at: "2026-10-07"
content-sensitivity: "public"
related_spec: "spec.md"
related_tasks: "tasks.md#Task 2"
related_facts: "facts.md"
---

# I-洞察 —— 产品化取舍标准与体验设计

> 本文件为 Task 2 产出，输入为 `facts.md` 实测基线与 `spec.md` 验收标准。
> 质量门 G2：四元组洞察每条含「现象 / 根因 / 影响 / 建议」四要素。

## 1. 四元组洞察：什么让「1 小时上手」成为可能 / 不可能

### 洞察 1：体量分布倒置——93%+ 资产是执行体，非入门物料

- **现象**：`.agents/` 实测 6850 文件 / 134,549,228 字节。其中 `skills/`（4378 文件 / 104,116,004 字节）与 `scripts/`（2010 文件 / 27,150,022 字节）合计 6388 文件 / 131,266,026 字节，占字节比 97.6%。其余 25 个顶层类目合计 462 文件 / 3,283,202 字节，字节占比 2.4%。
- **根因**：该体系按「能力全集」累积，规范门面与执行资产（技能实现、验证脚本）同仓共存，缺少面向外部读者的分层门面。
- **影响**：买家面对 6850 个文件缺少数千条起步线索，「1 小时」时间盒内无法完成通读；不先做物理剔除，教程体量必然突破 1500 行硬门。
- **建议**：starter 采用「类目代表文件 + 一句话导览」结构，仅取各类目 README 与 1~2 份代表文件，落地 40 文件（见 §2 与 facts.md §3.2），把 93%+ 体量挡在门外。这是「1 小时上手」成立的先决条件。

### 洞察 2：入口层天然轻量——「1 小时」已有可行基线

- **现象**：`.agents/` 根级 9 个 Markdown 文件合计 503 行（ONBOARDING 84、context-routing 120、README 80、governance-layers 47、global-core-rules 39、capability-registry 32、subdirectory-responsibilities 29、capability-boundaries 28、VENDOR-INTEGRATION 24）；仓库根 `AGENTS.md` 121 行；两类合计 624 行。
- **根因**：既有体系已按「元文档优先」原则（`rules/meta-document-priority-principle.md`，146 行）把入口压在百行量级，且明确要求「入口 <100 行、新增模块先更新索引」。
- **影响**：概览段（10min）与装载段（15min）的内容体量落在可消化区间，「1 小时」具备真实的内容基线，非营销口号。
- **建议**：概览 + 装载段直接复用入口层原件，文件三态取「保留原件」；仅对 `context-routing.md` 与 `capability-registry.md` 做单项目裁剪（三态「精简改写」），把三层路由收敛为单项目路由。

### 洞察 3：既有空骨架模板内容空洞——不能直接交付

- **现象**：`templates/agent-workspace-hub/` 实测 28 文件 / 19,918 字节（spec Background 记 51 文件，实测偏差 23 文件）。其中 `.agents/` 下 25 个 README 为 2 行占位；实质内容仅 `AGENTS.md`（74 行）、`.agents/README.md`（60 行）、`README.md`（41 行）三份，合计 175 行。
- **根因**：该模板定位为「目录结构骨架」，以占位文件宣告类目存在，设计目标不含可读内容与上手路径。
- **影响**：买家直接拷入只会得到空目录，产生不了「首个成功体验」；演练段（25min）将无内容可依，AC-1/AC-6 同步失守。
- **建议**：starter 以骨架的目录结构为「形」、以 `.agents/` 精华内容为「实」。对 `templates/agent-workspace-hub/AGENTS.md` 与 `.agents/README.md` 采取「精简改写」，其余 24 个占位文件「剔除」；根契约改写时保留「启动协议」关键词锚点（AC-3）。

### 洞察 4：1500 行预算是「60 分钟」的硬刻度——需分段设门

- **现象**：产品硬约束为 starter ≤50 文件、教程 ≤900 行、演练 ≤600 行；spec 时间盒为 10/15/25/10 分钟。facts.md §3.2 建议 starter 40 文件，§3.3 建议教程 900 行 + 演练 600 行 = 1500 行。
- **根因**：60 分钟可消化的阅读量（含照抄块与逐条验收点）存在约 1500 行的上界；阅读量与段位时长呈线性对应。
- **影响**：任一交付段超预算即触发 AC-5 rubric 向 3 分档（1500-3000 行）滑落，Pass Threshold（≥4）失守；交付期追加内容的返工成本高。
- **建议**：采用「分段预算门」——教程总览 ≤100 行、四段各 ≤225 行（合计 ≤900），演练独立 ≤600 行；每份交付物落盘时按实测行数硬校验，超门即裁剪。

## 2. 萃取清单定稿（类目 × 文件 × 行数 × 三态）

> 三态标注：**保留原件**（原样纳入，仅补 `source` frontmatter）/ **精简改写**（压缩或裁剪后纳入）/ **新建**（原创，注明原创）。
> 目标：≥9 个类目各 ≥1 代表文件；总计 ≤50 文件。本设计总计 **40 文件**，预留 10 文件余量。

### 2.1 目标目录树

```
starter/
├── AGENTS.md                                  [精简改写]
├── LICENSE-NOTICE.md                          [新建]
└── .agents/
    ├── README.md                              [精简改写]
    ├── ONBOARDING.md                          [保留原件]
    ├── context-routing.md                     [精简改写]
    ├── global-core-rules.md                   [保留原件]
    ├── capability-registry.md                 [精简改写]
    ├── roles/
    │   ├── README.md                          [保留原件]
    │   ├── developer.md                       [保留原件]
    │   ├── reviewer.md                        [保留原件]
    │   └── tester.md                          [保留原件]
    ├── rules/
    │   ├── README.md                          [精简改写]
    │   ├── ai-coding-guidelines.md            [精简改写]
    │   ├── content-sensitivity-precheck.md    [保留原件]
    │   ├── fix-prevent-close-loop.md          [精简改写]
    │   ├── spec-writing-guide.md              [保留原件]
    │   └── spec-creation-precheck.md          [保留原件]
    ├── protocols/
    │   ├── README.md                          [保留原件]
    │   ├── prompt-bootstrap.md                [精简改写]
    │   └── workspace-discovery.md             [精简改写]
    ├── workflows/
    │   ├── README.md                          [保留原件]
    │   ├── feature-development.md             [保留原件]
    │   └── code-review.md                     [精简改写]
    ├── templates/
    │   ├── README.md                          [精简改写]
    │   ├── task-template.md                   [保留原件]
    │   └── handoff-template.md                [保留原件]
    ├── commands/
    │   ├── README.md                          [精简改写]
    │   └── mermaid.md                         [精简改写]
    ├── checklists/
    │   ├── README.md                          [保留原件]
    │   └── code-review-checklist.md           [精简改写]
    ├── skills/
    │   ├── README.md                          [精简改写]
    │   └── load-specweave/
    │       └── SKILL.md                       [保留原件]
    ├── modules/README.md                      [新建]（导览，≤10 行）
    ├── teams/README.md                        [新建]（导览，≤10 行）
    ├── prompts/README.md                      [新建]（导览，≤10 行）
    ├── tools/README.md                        [新建]（导览，≤10 行）
    ├── worlds/README.md                       [新建]（导览，≤10 行）
    ├── capabilities/README.md                 [新建]（导览，≤10 行）
    ├── cases/README.md                        [新建]（导览，≤10 行）
    └── systems/README.md                      [新建]（导览，≤10 行）
```

### 2.2 文件清单表（类目 × 源文件 × 源行数 × 三态）

| # | 目标路径 | 源文件（.agents/ 或 templates/） | 源行数 | 三态 | 目标行数上限 |
|---|---|---|---|---|---|
| 1 | `starter/AGENTS.md` | `templates/agent-workspace-hub/AGENTS.md` + 仓库根 `AGENTS.md` | 74 / 121 | 精简改写 | 80 |
| 2 | `starter/LICENSE-NOTICE.md` | — | — | 新建 | 20 |
| 3 | `.agents/README.md` | `templates/agent-workspace-hub/.agents/README.md` + `.agents/README.md` | 60 / 80 | 精简改写 | 50 |
| 4 | `.agents/ONBOARDING.md` | `.agents/ONBOARDING.md` | 84 | 保留原件 | 84 |
| 5 | `.agents/context-routing.md` | `.agents/context-routing.md` | 120 | 精简改写 | 60 |
| 6 | `.agents/global-core-rules.md` | `.agents/global-core-rules.md` | 39 | 保留原件 | 39 |
| 7 | `.agents/capability-registry.md` | `.agents/capability-registry.md` | 32 | 精简改写 | 25 |
| 8 | `.agents/roles/README.md` | `.agents/roles/README.md` | 54 | 保留原件 | 54 |
| 9 | `.agents/roles/developer.md` | `.agents/roles/developer.md` | 27 | 保留原件 | 27 |
| 10 | `.agents/roles/reviewer.md` | `.agents/roles/reviewer.md` | 25 | 保留原件 | 25 |
| 11 | `.agents/roles/tester.md` | `.agents/roles/tester.md` | 23 | 保留原件 | 23 |
| 12 | `.agents/rules/README.md` | `.agents/rules/README.md` | 185 | 精简改写 | 60 |
| 13 | `.agents/rules/ai-coding-guidelines.md` | `.agents/rules/ai-coding-guidelines.md` | 145 | 精简改写 | 70 |
| 14 | `.agents/rules/content-sensitivity-precheck.md` | `.agents/rules/content-sensitivity-precheck.md` | 126 | 保留原件 | 126 |
| 15 | `.agents/rules/fix-prevent-close-loop.md` | `.agents/rules/fix-prevent-close-loop.md` | 172 | 精简改写 | 80 |
| 16 | `.agents/rules/spec-writing-guide.md` | `.agents/rules/spec-writing-guide.md` | 20 | 保留原件 | 20 |
| 17 | `.agents/rules/spec-creation-precheck.md` | `.agents/rules/spec-creation-precheck.md` | 65 | 保留原件 | 65 |
| 18 | `.agents/protocols/README.md` | `.agents/protocols/README.md` | 56 | 保留原件 | 56 |
| 19 | `.agents/protocols/prompt-bootstrap.md` | `.agents/protocols/prompt-bootstrap.md` | 322 | 精简改写 | 90 |
| 20 | `.agents/protocols/workspace-discovery.md` | `.agents/protocols/workspace-discovery.md` | 233 | 精简改写 | 70 |
| 21 | `.agents/workflows/README.md` | `.agents/workflows/README.md` | 24 | 保留原件 | 24 |
| 22 | `.agents/workflows/feature-development.md` | `.agents/workflows/feature-development.md` | 28 | 保留原件 | 28 |
| 23 | `.agents/workflows/code-review.md` | `.agents/workflows/code-review.md` | 95 | 精简改写 | 45 |
| 24 | `.agents/templates/README.md` | `.agents/templates/README.md` | 85 | 精简改写 | 30 |
| 25 | `.agents/templates/task-template.md` | `.agents/templates/task-template.md` | 87 | 保留原件 | 87 |
| 26 | `.agents/templates/handoff-template.md` | `.agents/templates/handoff-template.md` | 32 | 保留原件 | 32 |
| 27 | `.agents/commands/README.md` | `.agents/commands/README.md` | 134 | 精简改写 | 40 |
| 28 | `.agents/commands/mermaid.md` | `.agents/commands/mermaid.md` | 140 | 精简改写 | 45 |
| 29 | `.agents/checklists/README.md` | `.agents/checklists/README.md` | 26 | 保留原件 | 26 |
| 30 | `.agents/checklists/code-review-checklist.md` | `.agents/checklists/code-review-checklist.md` | 120 | 精简改写 | 50 |
| 31 | `.agents/skills/README.md` | `.agents/skills/README.md` | 163 | 精简改写 | 40 |
| 32 | `.agents/skills/load-specweave/SKILL.md` | `.agents/skills/load-specweave/SKILL.md` | 25 | 保留原件 | 25 |
| 33 | `.agents/modules/README.md` | `.agents/modules/README.md` | 66 | 新建（导览） | 10 |
| 34 | `.agents/teams/README.md` | `.agents/teams/README.md` | 100 | 新建（导览） | 10 |
| 35 | `.agents/prompts/README.md` | `.agents/prompts/README.md` | 59 | 新建（导览） | 10 |
| 36 | `.agents/tools/README.md` | `.agents/tools/README.md` | 39 | 新建（导览） | 10 |
| 37 | `.agents/worlds/README.md` | `.agents/worlds/README.md` | 67 | 新建（导览） | 10 |
| 38 | `.agents/capabilities/README.md` | `.agents/capabilities/README.md` | 50 | 新建（导览） | 10 |
| 39 | `.agents/cases/README.md` | `.agents/cases/README.md` | 4 | 新建（导览） | 10 |
| 40 | `.agents/systems/README.md` | `.agents/systems/README.md` | 4 | 新建（导览） | 10 |

**统计**：40 文件（≤50 ✓）。三态分布：保留原件 16、精简改写 15、新建 9。
**类目覆盖**（≥9 ✓）：根契约、入口层、roles、rules、protocols、workflows、templates、commands、checklists、skills、modules、teams、prompts、tools、worlds、capabilities、cases、systems = 18 个类目。

**说明（相对 facts.md 建议的微调）**

- `commands/` 代表文件从 facts 候选池中选定 `mermaid.md`（源 140 行 → 目标 45 行）——其为通用可视化指令，与买家「首个任务」产出物（目录树/流程图）关联度高。
- `checklists/` 代表文件选定 `code-review-checklist.md`（源 120 行 → 目标 50 行）——与 `workflows/code-review.md` 配套，构成审查闭环的最小样例。
- 导览型 8 个 README 采用「新建」态，每份 ≤10 行（一句话定位 + 延伸阅读指向），规避占位文件空洞问题（洞察 3）。

## 3. 60 分钟时间盒分配定稿

| 段位 | 时长 | 目标 | 输出（可观察） | 对应教程文件 |
|---|---|---|---|---|
| 00 概览 | 10 min | 认识工作区结构：根契约 + `.agents/` 类目导览 | 能说出 ≥5 个类目的作用；打开 `starter/.agents/ONBOARDING.md` 定位到「能力速查表」 | `guide/00-overview.md` |
| 01 装载 | 15 min | 用一句话提示词把 starter 拷入自有项目并通过自检 | `python scripts/verify_starter.py` 输出通过报告且 exit 0；根 `AGENTS.md` 命中「启动协议」关键词 | `guide/01-bootstrap.md` |
| 02 首个任务 | 25 min | 按规格驱动完成「目录树查看器」小工具 | `spec/tree-viewer/spec.md` + `tree_view.py` + 运行输出样例 + 3 条验收核对 | `guide/02-first-task.md` + `walkthrough/` |
| 03 进阶 | 10 min | 认识 rules/protocols 深潜入口与后续扩展路径 | 从 `rules/` 或 `protocols/` 选定 1 个深潜条目（如 `fix-prevent-close-loop.md`）并记录阅读计划 | `guide/03-next-steps.md` |
| **合计** | **60 min** | — | — | 总览 `guide/README.md` + 4 段 |

**完成检查点（每段一份）**

- 00：能复述「根契约 → 入口层 → 类目导览」三层结构。
- 01：自检脚本 exit 0；「启动协议」关键词命中（AC-3）。
- 02：`tree_view.py` 对样例目录运行并输出缩进树；3 条 Given/When/Then 验收逐条勾选。
- 03：选定 1 个深潜条目并写下一句话后续动作。

## 4. 演练任务定稿：规格驱动小任务

### 4.1 选题

**「目录树查看器」单文件小工具的规格驱动开发**——先写 spec，再实施，最后验收。

### 4.2 任务书（一句话定义）

> 用 spec 驱动方式实现单文件 Python 小工具 `tree_view.py`：扫描指定目录并按缩进输出目录树，支持 `--max-depth` 限制层级；先写 `spec.md`（目标 + 功能需求 + 验收标准），再实施，最后沙箱运行验证。

### 4.3 预期产出物清单（≤25 分钟可完成）

| # | 产出物 | 形态 | 验收方式 |
|---|---|---|---|
| 1 | `spec/tree-viewer/spec.md` | 任务书转写：目标 / 功能需求（FR-1~FR-3）/ 验收标准（AC-1~AC-3，Given-When-Then） | 含三类章节，AC 可勾选 |
| 2 | `tree_view.py` | 单文件实现，纯 Python 标准库（`os` / `argparse`） | 文件存在且无第三方 import |
| 3 | 运行输出样例 | `python tree_view.py . --max-depth 2` 的缩进树文本 | 输出行数与目录层级匹配 |
| 4 | 验收记录 | 3 条 AC 的逐条核对结果 | 3/3 勾选 |

### 4.4 剧本步骤（≥6 步，每步含照抄块 + 验收点）

1. **读任务书**——照抄：任务书一句话；验收点：能复述 1 个目标与 3 条 AC。
2. **写 spec**——照抄：`spec.md` 骨架（Overview / Goals / Functional Requirements / Acceptance Criteria）；验收点：文件落 `spec/tree-viewer/spec.md`。
3. **创建前预检**——照抄：`spec-creation-precheck.md` 的位置核查 + 格式核查两问；验收点：位置与格式两问均通过。
4. **实施**——照抄：`tree_view.py` 参考实现骨架；验收点：文件存在、`import os, argparse` 无第三方依赖。
5. **运行验证**——照抄：`python tree_view.py . --max-depth 2`；验收点：终端输出缩进树，无 traceback。
6. **验收核对**——照抄：AC 逐条 Given/When/Then 表；验收点：3/3 勾选。
7. **（可选）交接**——照抄：`handoff-template.md`；验收点：产出交接记录一份。

## 5. 教程 + 演练行数分配表

| 交付物 | 段位 | 建议行数上限 | 硬门 |
|---|---|---|---|
| `guide/README.md`（学习路径总览 + 时间盒表） | — | 100 | — |
| `guide/00-overview.md` | 概览 10min | 200 | ≤225 |
| `guide/01-bootstrap.md` | 装载 15min | 225 | ≤225 |
| `guide/02-first-task.md` | 首个任务 25min | 225 | ≤225 |
| `guide/03-next-steps.md` | 进阶 10min | 150 | ≤225 |
| **教程小计** | 60min | **900** | **≤900** |
| `walkthrough/`（任务书 → spec → 实施 → 产出物 → 验收） | 25min | **600** | **≤600** |
| **教程 + 演练合计** | — | **1500** | **≤1500（NFR-1）** |

> 校验：教程 900 ≤ 900 ✓；演练 600 ≤ 600 ✓；合计 1500 ≤ 1500 ✓；教程 4 段各 ≤225 ✓；starter 40 文件 ≤50 ✓（与 facts.md §3.2 / §3.3 基线一致）。

## 6. 质量门 G2 自查

| 检查项 | 结果 |
|---|---|
| 四元组洞察条数 | 4 条（≥3 ✓），主题均为「1 小时上手的可能/不可能」 |
| 每条四要素齐备（现象 / 根因 / 影响 / 建议） | 4 条 × 4 要素，全部齐备 ✓ |
| 洞察是否基于 facts.md 实测数据论证 | 是（体量比 97.6%、入口 503 行、骨架 28 文件/19,918 字节等均引 facts.md）✓ |
| 萃取清单（类目 × 文件 × 行数 + 三态标注） | 40 文件，18 类目，每文件带三态 ✓ |
| 时间盒分配表（10/15/25/10 = 60min） | 已产出，含每段目标与输出 ✓ |
| 演练选题 | 「目录树查看器」规格驱动，含一句话任务书 + 4 项产出物 + 7 步剧本 ✓ |
| 行数分配表（教程 ≤900 / 演练 ≤600） | 已产出且校验通过 ✓ |
| 与 facts.md 基线一致性 | starter 40 文件、教程 900 行、演练 600 行，与 facts.md §3.2/§3.3 一致 ✓ |