---
id: "spec-mode-doc-creation-workflow"
source: "docs/retrospective/reports/task-reports/retrospective-tech-interface-wiki-20260703/insight-extraction.md#关键洞察2; docs/retrospective/reports/competitive-analysis/retrospective-text-to-cad-learning-20260704/insight-extraction.md#洞察2"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/spec-mode-doc-creation-workflow.toml"
maturity: "L2"
validation_count: 2
---
# Spec Mode文档创建工作流：前置规划→原子执行→门禁验证

## 模式概述

使用/spec（Spec Mode）创建结构化文档（如wiki教程、技术文档、知识库条目）时，必须遵循"前置规划→参考先例→原子拆分→子代理执行→自动化门禁验证"的五阶段工作流，而非直接开始写作。跳过前置规划直接写作会导致结构不一致、内容遗漏、返工率高（非线性返工成本：跳过5分钟规范读取可能导致30分钟以上重构）。Spec Mode通过先输出spec.md（PRD）、tasks.md（任务分解）、checklist.md（验证清单）三件套，将"想清楚"与"写出来"分离，确保文档结构清晰、覆盖完整、质量可验证。

## 问题现象

直接开始写文档（不使用Spec Mode）的常见失败模式：

1. **边写边想结构漂移**：写到第三章发现第一章的结构不对，需要大规模重写
2. **内容覆盖不全**：写完才发现遗漏了重要章节（如对比分析、参考资料）
3. **文件大小失控**：单个文件写到500+行，违反原子化原则，难以维护和审查
4. **子代理任务模糊**：委托子代理写章节时没有明确大纲和约束，返回结果不符合预期
5. **链接断裂无人发现**：写完才发现导航链接指向不存在的文件
6. **返工成本非线性**：前期省略5分钟规划，后期花费30分钟以上修复结构性问题
7. **验收标准模糊**：任务完成时没有明确的"做完"标准，不知道是否达标

这些问题的共同根因是：把"规划"和"执行"混在一起，在写作过程中同时做结构决策和内容创作，导致认知负荷过高、决策质量下降、错误累积。

## 解决方案

采用五阶段Spec Mode文档创建工作流，对于"外部网页/文章→wiki教程"类任务，需增加前置阶段0：

### 阶段0：外部内容提取（wiki教程场景专用）

对于"外部网页/文章→结构化wiki教程"类任务，在五阶段工作流之前增加内容提取阶段，完成四层信息加工漏斗的前两层：

- **L1 原始网页层**：使用defuddle提取网页干净Markdown，去除导航/广告/评论等噪音，保留正文核心内容
- **L2 干净文本层**：通读提取内容，标记核心观点、关键概念、结构布局，识别可复用的代码示例和图表说明

L2完成后再进入阶段1的规范阅读和Spec规划。

**说明**：defuddle只解决L1→L2（去噪），L3（结构化大纲）和L4（wiki成品）仍需通过本工作流的阶段2-5完成。

### 阶段1：前置规范阅读（必做，5分钟）

在写任何内容之前：
1. 读取AGENTS.md启动协议，确认任务类型路由
2. 读取目标目录的现有同类文档作为参考先例（reference-as-trigger模式）
3. 读取文档原子化规范和frontmatter模板
4. 确认是否有对应Skill应被加载

**禁止跳过此阶段**：跳过规范读取是最常见的失败原因，导致输出格式错误、路径错误、结构错误三重连锁问题。

### 阶段2：Spec三件套生成（核心规划）

生成三个规划文件到`.trae/specs/{category}/{task-name}/`：

| 文件 | 内容 | 作用 |
|------|------|------|
| spec.md | PRD：功能需求、非功能需求、验收标准（≥8个） | 定义"做什么"和"做完的标准" |
| tasks.md | 原子任务分解：每个任务含优先级、依赖、描述、验收标准映射、测试要求 | 定义"怎么做"和执行顺序 |
| checklist.md | 验证清单：覆盖目录结构、章节内容、代码示例、链接验证、frontmatter合规等（≥50项） | 定义"怎么检查做对了" |

**spec.md关键要素**：
- 目标读者定位（新手/进阶/专家）
- 文档结构大纲（每个文件的主题和预估行数）
- ≥8个可验证的验收标准（不是"写得好"这种主观标准）
- 与现有知识库的关系和导航位置

**tasks.md关键要素**：
- 每个任务对应一个原子文件（一个任务 = 一个文件 = 一次Edit/Write）
- 明确任务间依赖关系（哪些必须先做，哪些可以并行）
- 每个任务映射到spec.md的验收标准编号
- 标注是否可委托子代理执行

### 阶段3：原子任务执行（按tasks.md顺序）

严格按照tasks.md的顺序逐个执行，每个任务完成一个原子文件：

1. 优先创建目录结构和00-overview总览文件
2. 逐章创建内容文件，保持每章<300行
3. 每个文件包含完整YAML frontmatter（id/title/category/tags/date/status/author/summary）
4. 每章添加上一章/下一章/目录的双向导航链接
5. 需要并行的内容（如多个独立章节）可使用多个子代理并行执行

**子代理委托要点**：
- 每个子代理只负责一个原子文件
- 提供精确的文件路径（绝对路径）
- 提供完整的frontmatter模板（不要让子代理猜字段）
- 提供结构化的章节大纲（具体到二级标题）
- 明确导航要求（前一章/后一章文件名必须与规划一致）
- 列出硬约束（行数<300、必须包含代码示例、Mermaid图规范等）

### 阶段4：即时验证与修正

每完成一批文件后立即执行验证，不要等全部写完：

1. **文件大小检查**：运行`check-file-size.py`确认所有文件<300行
2. **链接检查**：运行`check-links.py`确认所有本地引用有效
3. **导航一致性检查**：人工抽查双向导航中的文件名是否与实际文件名一致
4. **frontmatter检查**：确认每个文件的必填字段完整

发现问题立即修正，不要积累到最后。

### 阶段5：最终门禁验证

所有文件写完后执行全量验证：
1. 对照checklist.md逐项打勾检查
2. 全量运行check-file-size.py和check-links.py
3. 运行generate_index.py更新知识库索引（如果是知识库文档）
4. 确认所有验收标准达成

```
┌──────────────────────────────────────────────────────────────────┐
│  Spec Mode文档创建工作流（含wiki教程场景阶段0）                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [wiki教程场景专用]                                               │
│  阶段0: 内容提取 ──→ 阶段1: 规范阅读 ──→ 阶段2: Spec三件套         │
│  (defuddle去噪      (5min)              (spec.md/tasks.md         │
│   L1→L2清洗)         AGENTS.md            /checklist.md)          │
│                       参考先例                  │                 │
│                       模板规范                  ▼                 │
│                                         ┌──────────┐             │
│                                         │ 想清楚了 │             │
│                                         └──────────┘             │
│                                              │                   │
│                                              ▼                   │
│                                       阶段3: 原子执行             │
│                                       (按tasks.md逐个文件创建)     │
│                                              │                   │
│                                              ▼                   │
│                                         ┌──────────┐             │
│                                         │ 写出来了 │             │
│                                         └──────────┘             │
│                                              │                   │
│                                              ▼                   │
│                                       阶段4: 即时验证             │
│                                       (文件大小/链接/导航)        │
│                                              │                   │
│                                              ▼                   │
│                                       阶段5: 门禁验证             │
│                                       (checklist全量检查)        │
│                                              │                   │
│                                              ▼                   │
│                                          ✅ 交付                  │
└──────────────────────────────────────────────────────────────────┘
```

## 适用场景

- ✅ 使用/spec命令创建结构化文档（wiki、教程、技术文档）
- ✅ 多文件原子化文档集（≥3个文件）
- ✅ 需要子代理协助创建内容的任务
- ✅ 知识库条目、技术指南、最佳实践文档
- ✅ 有明确验收标准的文档任务
- ✅ 外部资源学习类wiki教程（网页文章/开源项目→结构化wiki，需defuddle内容提取+四层信息加工漏斗前置）
- ❌ 单文件简短笔记（不需要Spec三件套）
- ❌ 临时笔记/草稿（直接写即可）
- ❌ 纯代码开发任务（使用功能开发Spec工作流而非文档工作流）

## 实际案例

### 案例1：Interface/API/ABI/Protocol技术Wiki（本次验证）

| 阶段 | 耗时 | 产出物 |
|------|------|--------|
| 阶段1 规范阅读 | ~5min | 参考先例：agent-communication-protocols-wiki结构 |
| 阶段2 Spec三件套 | ~10min | spec.md(135行,10个验收标准) + tasks.md(153行,8个任务) + checklist.md(78行,77项检查) |
| 阶段3 原子执行 | ~20min | 7个教程文件870行，主进程创建3个，子代理并行创建4个 |
| 阶段4 即时验证 | ~5min | 发现1处导航文件名不一致（05-practice vs 05-comparison），立即修正 |
| 阶段5 门禁验证 | ~3min | check-file-size通过(最大164行)，check-links通过(20个链接全部有效) |

**总耗时**：约43分钟，产出10个文件1236行（3个Spec + 7个教程），仅1处轻微错误修正，无结构性返工。

**对比无Spec Mode的反事实估计**：如果直接开始写，预计会出现：章节顺序混乱（至少一次大规模重排）、遗漏对比分析章或参考资料章、文件行数超标需要拆分、导航链接多处断裂，总返工时间预计20-30分钟，总耗时可能达到60-70分钟且质量不稳定。

### 案例2：text-to-cad wiki教程（第二次验证）

| 阶段 | 耗时 | 产出物 |
|------|------|--------|
| 阶段0 内容提取 | ~5min | defuddle提取微信公众号文章→干净Markdown文本 |
| 阶段1 规范阅读+格式检查 | ~3min | 参考先例：the-agency-project-wiki.md确认YAML frontmatter格式 |
| 阶段2 Spec三件套 | ~8min | spec.md(16验收标准) + tasks.md(6任务) + checklist.md(6检查点) |
| 阶段3 原子执行 | ~15min | 主wiki文件text-to-cad-wiki.md(308行,8章节)，子代理委派实施 |
| 阶段4-5 验证+提交 | ~5min | 格式修正(TOML→YAML) + 原子提交 |

**关键发现**：子代理初次创建时因机械遵循project_memory描述使用了TOML frontmatter(+++)，但通过强制前置检查步骤（读取同目录现有文档）在验证阶段发现并修正。这验证了format-evidence-over-memory-pattern的必要性，也说明Spec+checklist机制能有效捕获格式问题。

**总耗时**：约36分钟产出主教程308行+spec三件套，过程中1处格式错误被checklist捕获修正，无结构性返工。

## 反模式

### 反模式1："我先写个草稿再整理"

边写边想结构，写完第一版后发现结构不合理需要大改。由于文档已经写了很多内容，重写的心理阻力大，往往在有缺陷的结构上修补，最终质量低下。

**正确做法**：用spec.md先把结构和验收标准定下来，再按tasks.md逐个文件写。

### 反模式2：Spec三件套写完就扔，不按tasks.md执行

生成了spec.md和tasks.md，但执行时不按计划来，想到哪写到哪，tasks.md成为摆设。

**正确做法**：严格按照tasks.md的任务顺序执行，完成一个标记一个，计划变更时先更新tasks.md。

### 反模式3：子代理任务描述模糊

"帮我写API章节"这种模糊描述，子代理不知道路径、不知道frontmatter格式、不知道章节结构、不知道要写多少行，返回结果几乎肯定需要重写。

**正确做法**：给子代理的任务描述必须包含：精确路径+完整frontmatter模板+结构化大纲+导航约束+硬约束。使用[subagent-atomic-task-template.md](subagent-atomic-task-template.md)模式。

### 反模式4：全部写完才验证

写完所有7个文件才检查链接，发现7个文件之间有5个链接错误，需要逐个修改。如果边写边检查，每个错误在引入时就被发现，修正成本极低。

**正确做法**：每完成1-2个文件就运行一次check-links.py和check-file-size.py。

### 反模式5：凭记忆决定格式不验证

委派子代理创建文件时，依赖project_memory或记忆中的规范描述决定格式（如frontmatter用TOML还是YAML），不读取同目录现有文档验证。

**后果**：格式不一致导致返工，破坏知识库风格统一性。

**正确做法**：使用[format-evidence-over-memory-pattern.md](../governance-strategy/format-evidence-over-memory-pattern.md)，创建新文件前必须读取同目录1-2个现有文档确认实际格式。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [spec-driven-development.md](../creative-design/spec-driven-development.md) | 上位 | 本模式是spec-driven-development在文档创建场景的具体化 |
| [multi-agent-parallel-execution.md](../../architecture-patterns/multi-agent-parallel-execution.md) | 依赖 | 阶段3原子执行时，独立章节可使用多代理并行提高效率 |
| [subagent-atomic-task-template.md](subagent-atomic-task-template.md) | 配套 | 子代理任务描述模板是阶段3的关键支撑模式 |
| [three-layer-spec-constraint.md](../governance-strategy/three-layer-spec-constraint.md) | 相关 | Spec三件套是三层规格约束在文档场景的应用 |
| [atomization-three-criteria-test.md](../document-architecture/atomization-three-criteria-test.md) | 前置 | tasks.md任务拆分时必须用原子化三标准检验 |
| [nonlinear-correction-cost.md](../governance-strategy/nonlinear-correction-cost.md) | 理论基础 | 前期省略规划导致后期非线性返工成本，是本模式要解决的核心问题 |
| [format-evidence-over-memory-pattern.md](../governance-strategy/format-evidence-over-memory-pattern.md) | 前置强制 | 阶段1规范阅读中的格式检查必须遵循此模式，实际文档是格式唯一权威 |

## 边界与选型

**何时使用本模式**：
- 文档任务涉及≥3个文件
- 有明确的质量要求（需要通过链接检查、文件大小检查）
- 需要委托子代理完成部分工作
- 文档需要长期维护（结构化设计便于后续更新）
- 团队协作场景（Spec三件套是团队沟通的契约）

**何时不需要完整五阶段**：
- 单文件文档（<100行） → 直接写，不需要Spec
- 个人临时笔记 → 不用任何流程
- 紧急热修复文档 → 阶段1+阶段4即可（读规范+即时验证）
- 更新已有文档的局部内容 → 只需要阶段4验证修改部分

**与代码开发Spec工作流的区别**：
- 代码开发：spec.md关注接口/行为/测试用例，tasks.md关注编码任务
- 文档创建：spec.md关注结构/覆盖/验收标准，tasks.md关注文件创建任务
- 两者的阶段1-2-3-4-5框架是通用的，但具体产出物不同
