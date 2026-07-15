---
id: "retrospective-meta-atomization-ian-xiaohei-insights-20260625-export"
title: "insight-extraction.md 原子化归档 — 导出建议"
source: "insight-extraction.md 原子化归档全流程"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/atomization/retrospective-meta-atomization-ian-xiaohei-insights-20260625/export-suggestions.toml"
---
# insight-extraction.md 原子化归档 — 导出建议

> **来源**：对 `insight-extraction.md` 原子化归档全流程的复盘分析
> **导出日期**：2026-06-25

---

## 一、改进建议

| ID | 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|----|------|---------|--------|---------|------|
| IMP-META-001 | methodology-patterns README 的 4 个 Mermaid 关系图未更新（新增 6 个模式未纳入可视化拓扑） | 制定「Mermaid 图批量更新阈值」规则：每新增 ≥ 5 个同领域模式时触发一次关系图更新；本次 6 个均属「AI Skill 工程」领域，已达阈值，应更新知识管理关系图 | 中 | 可视化拓扑反映最新模式关系，降低维护者的定位成本 | 待规划 |
| IMP-META-002 | 7 个新模式文件的反向引用（被引用方的 `[bindings].references`）未更新 | 扫描新模式文件中的「与现有模式的关系」章节，定位被引用的已有模式；更新其 frontmatter 的 `references` 字段，添加对新模式的引用 | 中 | 模式间的双向引用完整性，确保「与现有模式的关系」可被对方发现 | 待规划 |
| IMP-META-003 | 三级分类策略缺少「理论并入」子分类 | 在 `atomization-three-tier-classification.md` 中增加「理论并入」作为「新建模式」的子分类：洞察为已规划模式的理论基础时，并入该模式的「问题背景」或「核心规则」章节，而非独立建文件或原地保留 | 低 | 减少因「不完全满足独立模式价值但又有保留必要」的决策困境 | 待规划 |
| IMP-META-004 | 同日两轮原子化（14 个新模式）缺乏入库后的跨批次去重审核 | 在原子化指令集中增加「批次合并审核」步骤：同一会话中多轮原子化完成后，检查跨批次模式间的重叠（概念域一致、规则重叠 > 70%），必要时合并 | 低 | 防止连续原子化导致模式冗余 | 待规划 |
| IMP-META-005 | 模式文件的 `[bindings].references` 字段维护成本高，手工容易遗漏 | 开发 `scripts/check-cross-references.py` 脚本：(1) 扫描所有模式文件「与现有模式的关系」章节；(2) 提取被引用模式 ID；(3) 验证被引用方的 `references` 字段是否包含反向引用；(4) 输出缺失的反向引用清单 | 低 | 自动化维护双向引用完整性 | 待规划 |

---

## 二、可萃取的模式与模板

### 模式候选 1：原子化执行七步标准流程

**建议归档路径**：`docs/retrospective/patterns/methodology-patterns/atomization-seven-step-workflow.md`

**模式摘要**：将原子化指令集的 6 个抽象步骤细化为 7 个可操作的原子化执行步骤，每步有明确的输入、输出和检查点。

**七步流程**：

| 步骤 | 名称 | 输入 | 输出 | 关键检查 |
|------|------|------|------|---------|
| S1 | 规范对齐 | 源文档 | atomization.md / three-criteria-test / three-tier-classification 已读取 | 确认执行策略 |
| S2 | 三级分类 | 源文档洞察列表 + 已有模式库索引 | 分类结果（新建/已有覆盖/原地保留/理论并入） | 每项洞察有明确分类和理由 |
| S3 | 并行创建 | 分类结果中的「新建模式」清单 | 模式文件（frontmatter + 完整结构） | 每个文件遵循统一模板 |
| S4 | 源文档降级 | 源文档 + 新模式文件路径 | 降级后的引用导航页 | 含洞察索引表 + 归档说明 + 分类统计 |
| S5 | 领域索引更新 | 新模式文件信息 | 对应层级 README 的新增条目 | 表格格式一致 |
| S6 | 总索引统计更新 | 新模式数量统计 | patterns/README.md 统计行 | 数字精确 |
| S7 | 完整性验证 | 全部变更文件 | 验证通过 / 修正清单 | 链接有效 + 文件可读 + 统计一致 |

**成熟度**：L2（本次实践完整验证）

### 模式候选 2：规律认知的处置决策矩阵

**建议归档路径**：`docs/retrospective/patterns/methodology-patterns/principle-disposition-matrix.md`

**模式摘要**：在原子化过程中，规律认知（相对于洞察）通常更抽象、操作步骤更少，需要一个专门的处置决策矩阵来判断其去向。

**决策矩阵**：

| 条件 | 处置 | 示例 |
|------|------|------|
| 有 ≥ 2 个可执行步骤 + 可独立复用 | 独立建模式文件 | — |
| 是某规划中洞察模式的理论基础 + 不可独立复用 | 理论并入（并入该模式的「问题背景」/「核心规则」） | 本轮规律 1 → output-behavior-specification |
| 是一次性经验总结 + 不可独立复用 | 原地保留 | — |
| 已被已有模式充分覆盖 | 已有覆盖（添加引用链接） | — |

**成熟度**：L1

---

## 三、行动计划

| 优先级 | 改进项 | 关联建议 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|---------|------|
| 中 | 更新 methodology-patterns Mermaid 关系图 | IMP-META-001 | 将新增 6 个 AI Skill 工程模式纳入知识管理关系图；为这个新领域新建一个独立的子关系图以保持可读性 | 2026-06-26 | 待规划 |
| 中 | 补充反向引用 | IMP-META-002 | 扫描 7 个新模式文件的「与现有模式的关系」章节；更新被引用模式的 `[bindings].references` 字段 | 2026-06-26 | 待规划 |
| 低 | 更新三级分类策略 | IMP-META-003 | 在 `atomization-three-tier-classification.md` 中增加「理论并入」子分类，含判断条件和处置模板 | 2026-06-27 | 待规划 |
| 低 | 开发跨引用检测脚本 | IMP-META-005 | 编写 `scripts/check-cross-references.py`；在 CI 中集成；首次运行验证全部 63 个模式的引用完整性 | 2026-07-05 | 待规划 |

---

## 四、模式成熟度更新

| 模式 ID | 成熟度变化 | 触发原因 | 更新时间 |
|---------|-----------|---------|---------|
| atomization-seven-step-workflow | 新建 L2 | insight-extraction.md 原子化完整实践验证 | 2026-06-25 |
| principle-disposition-matrix | 新建 L1 | 本轮 2 条规律的处置决策经验 | 2026-06-25 |

---

> **导出说明**：本文档的改进建议和行动计划均基于元级复盘的 5 项洞察发现，每条建议标注了与洞察的关联。
