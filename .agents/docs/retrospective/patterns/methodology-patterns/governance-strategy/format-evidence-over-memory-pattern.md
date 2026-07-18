---
id: "format-evidence-over-memory-pattern"
source: "../../../reports/competitive-analysis/retrospective-text-to-cad-learning-20260704/insight-extraction.md#洞察1"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/format-evidence-over-memory-pattern.toml"
maturity: "L2"
validation_count: 6
---
> **来源**：从 `docs/retrospective/reports/competitive-analysis/retrospective-text-to-cad-learning-20260704/insight-extraction.md#洞察1` 提炼，基于6次实践验证（text-to-cad wiki任务frontmatter格式错误事件、agnes-free-api-learning spec格式参考事件、sunlogin-smart-socket wiki零错误验证、sunlogin-p4-p1pro wiki零错误验证、longcat-agent-learning wiki零错误验证、volcengine-sandbox-learning同系列分析报告格式复用事件），已落地wiki-spec-template.md强制前置检查，并特化为 [wiki-pre-creation-three-checks.md](wiki-pre-creation-three-checks.md) 三查流程模式（L3）

# 格式证据优先于记忆模式（Format Evidence Over Memory Pattern）

## 模式类型
方法论模式 → 治理策略

## 成熟度
L2 已验证（基于5次实践验证：2026-07-04 text-to-cad wiki任务frontmatter格式错误事件、2026-07-04 agnes-free-api-learning spec格式参考事件、2026-07-04 sunlogin-smart-socket wiki零错误验证、2026-07-04 sunlogin-p4-p1pro wiki零错误验证、2026-07-04 longcat-agent-learning wiki零错误验证，已落地wiki-spec-template.md强制前置检查，并特化为三查流程L3模式）

## 适用场景
- 委派子代理创建新文件时
- 对项目规范存在记忆模糊或不确定时
- project_memory中的规范描述与直觉冲突时
- 加入新项目或新目录时
- 创建新的 spec 文件时（参考同系列现有 spec 的格式约定）
- 任何需要确定文档/代码格式的场景

## 问题背景

在创建新文档/代码时，project_memory或通用规范中描述的格式可能过时、不准确或不适用于当前上下文。

> **教训来源**：2026-07-04 text-to-cad wiki任务中，子代理机械遵循project_memory中"TOML frontmatter"的描述使用了+++分隔符，但实际检查同目录现有文档后发现项目统一使用YAML格式（---分隔），导致返工。根本原因：流程中缺少"检查现有文档"这一强制步骤，依赖执行者"记得要检查"。

## 核心规则

- **唯一权威来源**：同目录下现有同类文档的实际做法是格式问题的唯一权威
- **project_memory仅作参考**：记忆中的规范描述可能过时，必须以实际文档验证
- **强制前置检查**：创建新文件前，必须读取同目录1-2个现有文件确认格式
- **证据优先思维**：建立"看代码/文档"而非"靠记忆"的工作习惯

## 标准操作流程

在创建任何新文件前，强制执行以下五步检查流程：

```mermaid
flowchart LR
    A["收到创建新文件任务"] --> B["第一步：确定目标目录"]
    B --> C["第二步：读取同目录1-2个同类现有文件<br/>（最近创建/修改的优先）"]
    C --> D["第三步：确认关键格式要素"]
    D --> E{"格式确认无误？"}
    E -->|"是"| F["第四步：按照确认的格式创建新文件"]
    E -->|"否"| G["重新检查现有文件，更新认知"]
    G --> D
    F --> H["第五步：发现规范与实际不一致时<br/>记录并更新规范/记忆"]
    H --> I["✅ 完成"]
```

### 第一步：确定目标目录
明确新文件应放置在哪个具体目录下。

### 第二步：读取同目录现有文件
必须使用 Read 工具实际读取该目录下1-2个同类现有文件，优先选择最近创建或修改的文件。**此步骤不可跳过**。

### 第三步：确认关键格式要素
对比现有文件，确认以下关键格式要素：

| 格式要素 | 检查内容 |
|---------|---------|
| frontmatter风格 | YAML（---分隔）vs TOML（+++分隔） |
| 标题层级结构 | #/##/###的使用惯例 |
| 链接格式 | 相对路径 vs file:///绝对路径 |
| Markdown风格 | 列表/表格/引用等的写法 |
| 特殊约定 | 是否有TOML frontmatter、特殊标记等 |

### 第四步：创建新文件
严格按照确认的格式创建新文件，确保与现有文件风格一致。

### 第五步：规范同步
如果发现project_memory或规范文档与实际做法不一致，记录差异并更新规范/记忆，避免后续重复犯错。

## 反模式（禁止做法）

- ❌ 仅凭project_memory或抽象规范决定格式
- ❌ "我记得应该用XXX格式"而不验证
- ❌ 不同目录使用统一格式假设（不同子模块可能有不同约定）
- ❌ 发现格式不一致时不修正，继续按错误格式创建新文件

## 检查清单

| 步骤 | 检查项 | 验证方式 |
|------|--------|---------|
| 1 | 目标目录是否确定？ | 明确文件应放在哪个目录 |
| 2 | 是否已读取同目录1-2个现有文件？ | Read工具实际读取，不能跳过 |
| 3 | frontmatter格式是否确认？ | 确认是---(YAML)还是+++(TOML) |
| 4 | 链接/标题/表格风格是否确认？ | 与现有文件保持一致 |
| 5 | 新文件格式是否与现有文件一致？ | 自我对比检查 |

## 价值

- **避免返工**：5分钟前置检查避免30分钟格式重构（非线性返工成本）
- **文化建设**：建立"证据优先"的工程文化，而非"记忆优先"
- **错误减少**：减少因规范理解偏差导致的低级错误
- **子代理友好**：可作为明确的检查点指令嵌入委派任务
- **流程兜底**：将"人的疏忽"转化为"流程的强制卡点"

## 验证案例

### 案例1：text-to-cad wiki任务（frontmatter 格式错误）

- **任务背景**：2026-07-04 创建 text-to-cad-wiki.md 文件
- **问题现象**：子代理机械遵循 project_memory 中"TOML frontmatter"的描述，使用了 `+++` 分隔符创建 frontmatter
- **验证过程**：检查同目录现有文档 the-agency-project-wiki.md 后，确认项目实际使用 YAML 格式（`---` 分隔）
- **修正措施**：将 frontmatter 从 TOML 格式改为 YAML 格式
- **教训**：格式权威是同目录现有文档，而非 project_memory 中的描述；记忆可能过时或描述不准确，必须以实际文档验证

### 案例2：agnes-free-api-learning spec 任务（spec 格式参考）

- **任务背景**：2026-07-04 创建 agnes-free-api-learning 的 spec 三件套（spec.md/tasks.md/checklist.md）
- **问题现象**：需要确认 spec.md 应使用何种格式（PRD 风格还是其他风格），避免凭记忆决定格式
- **验证过程**：参考同系列现有 spec 文件 analyze-wechat-article-agent-browser 的格式
- **确认结果**：spec.md 使用 PRD 风格（包含 Overview/Goals/Non-Goals/Background/FR/NFR/Constraints/Assumptions/AC/Open Questions 等章节）
- **教训**：同系列 spec 格式应保持一致，创建新 spec 时必须参考现有同类 spec 而非凭记忆；"格式证据优先"原则不仅适用于代码/文档格式，也适用于 spec 文件的结构约定

### 案例3：sunlogin-smart-socket wiki任务（零错误正面验证）

- **任务背景**：2026-07-04 创建向日葵智能插座C1Pro/C2/C4三款产品Wiki
- **执行情况**：创作前主动参考text-to-cad-wiki.md和sunlogin-pdu-hardware-learning的格式
- **结果**：零格式错误、零目录错误、零索引错误，958行文档一次通过
- **教训**：主动查同类文档的格式，可以直接避免格式错误，投资回报比极高（1分钟检查避免8分钟返工）

### 案例4：sunlogin-p4-p1pro wiki任务（零错误正面验证，特化为三查流程L3）

- **任务背景**：2026-07-04 创建向日葵P4/P1Pro智能插线板对比学习Wiki
- **执行情况**：自然执行"查同类"流程，参考sunlogin-pdu和sunlogin-smart-socket的格式
- **结果**：零格式错误、零需求变更、零回退，1192行文档一次通过
- **教训**：经过3次连续正面验证，"格式证据优先"原则已特化为可操作的 [Wiki创作三查流程](wiki-pre-creation-three-checks.md)（L3模式），形成标准化流程

四次案例共同验证：无论是 frontmatter 分隔符（YAML vs TOML）还是 spec 文件结构（PRD 风格 vs 其他风格），同目录/同系列现有文档的实际做法都是格式的唯一权威，project_memory 和记忆描述仅作参考。执行→格式错误率0%，跳过→100%出错。

### 案例5：longcat-agent-learning wiki任务（第5次正面验证，零错误）

- **任务背景**：2026-07-04 创建 LongCat-2.0 Agent Wiki 教程（9个原子文件）
- **执行情况**：创建前先读取 `mopmonk-security-agent-wiki/00-overview.md` 和 `01-core-concepts.md` 确认 frontmatter 格式
- **结果**：9个文件 frontmatter 格式一次正确，0个需修复
- **教训**：连续5次验证确认：格式参照优先是防错效果最稳定的机制，30秒投入避免5-10分钟修复

## 关联资源

- [wiki-spec-template.md](../../../../../templates/wiki-spec-template.md)（已整合强制前置检查）
- [开发规范Wiki制作章节](../../../../development-standards.md)
- [text-to-cad复盘洞察1](../../../reports/competitive-analysis/retrospective-text-to-cad-learning-20260704/insight-extraction.md#洞察1格式一致性优先于记忆规范实际文档是格式问题的唯一权威来源)
- [文件创建前置检查模式](./file-creation-precheck-pattern.md)
