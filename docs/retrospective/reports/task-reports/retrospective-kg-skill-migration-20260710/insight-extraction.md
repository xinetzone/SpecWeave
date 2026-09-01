---
id: insight-extraction-kg-skill-migration-20260710
title: 知识图谱生成器Skill迁移洞察萃取
source: "retrospective: retrospective-kg-skill-migration-20260710"
type: insight
date: "2026-07-10"
status: completed
---
# 知识图谱生成器Skill迁移洞察萃取

## 根因分析：5-Whys

### INSIGHT-1: Skill位置分裂的根因——规范文档"索引导向"vs"流程导向"定位偏差

**Why-1**: 为什么 knowledge-graph-generator 是唯一在 `.trae/skills/` 的Skill？
→ 该Skill最初通过Trae IDE的Skill加载机制创建，默认放置在 `.trae/skills/`。

**Why-2**: 为什么后续未纳入项目统一管理？
→ 项目没有明确的Skill位置规范，不知道该Skill应该放在哪个目录。

**Why-3**: 为什么没有Skill位置规范？
→ Skill体系是逐步演进的——最初只有 `.trae/skills/`（Trae IDE内置），后来创建了 `.agents/skills/`（项目自定义），但两个目录的边界从未被正式定义。

**Why-4**: 为什么两个目录的边界从未被正式定义？
→ 项目Skill管理规范（`.agents/skills/README.md`）聚焦于"如何组织已有Skill"，未涉及"新Skill应该放在哪里"的入口决策。

**Why-5**: 为什么README.md只关注组织而非入口决策？
→ README.md的设计初衷是"索引已有Skill"而非"指导新建Skill"，缺少"Skill创建规范"章节——这暴露了规范文档的**"索引导向"vs"流程导向"的定位偏差**。

**根本原因**：规范文档偏向"索引已有内容"而非"指导新建流程"。这是项目文档体系的系统性问题——不仅Skill管理如此，命令集管理、模式管理也可能存在类似问题。

### INSIGHT-2: 格式标准化的根因——平台Skill与项目Skill的格式鸿沟

**Why-1**: 为什么旧SKILL.md是通用工具文档而非项目标准Skill？
→ 该Skill由Trae IDE平台生成，遵循平台默认格式。

**Why-2**: 为什么平台默认格式与项目格式不同？
→ 项目五要素模型（frontmatter/决策树/安全检查/Why解释/Gotchas）是项目特有的方法论沉淀，平台无法预知。

**Why-3**: 为什么迁移时才发现格式差异？
→ 该Skill之前未被"作为项目Skill"使用——只是被当作外部工具引用。

**Why-4**: 为什么没有被当作项目Skill使用？
→ 因为它的存放位置（`.trae/skills/`）与项目Skill体系（`.agents/skills/`）不在同一命名空间，自然被排除在Skill管理流程之外。

**Why-5**: 为什么位置决定了管理归属？
→ 因为项目Skill管理流程（README索引、质量检查、changelog维护）的作用域限定在 `.agents/skills/` 目录——位置即边界，位置即归属。

**根本原因**：位置与管理归属的耦合——存放在 `.trae/skills/` 的Skill自动被排除在项目管理流程之外，形成"影子Skill"。

### INSIGHT-3: 对抗性审查协同的深层机制——"自举验证"在Skill层面的应用

**发现**：在SKILL.md中新增§11"与对抗性审查的协同"并非简单的交叉引用，而是"自举验证"原则在Skill层面的应用：
- 知识图谱作为审查工具（帮助识别孤立概念、过度连接、缺失关系）
- 知识图谱自身接受审查（节点覆盖率、关系准确性、偏差识别）

**深层含义**：任何"审查工具"本身也应该接受审查——这是对抗性审查方法论自洽性的要求。这个原则可以推广到所有Skill：安全检查清单本身是否安全？Gotchas列表本身是否有遗漏的陷阱？

## 数据支撑

| 洞察 | 数据点 | 验证方式 |
|------|--------|---------|
| INSIGHT-1 | `.trae/skills/` 仅1个Skill，`.agents/skills/` 14个Skill | `LS` 目录对比 |
| INSIGHT-2 | 旧SKILL.md缺少frontmatter/决策树/安全检查/Gotchas共6个维度 | 新旧SKILL.md逐维对比 |
| INSIGHT-3 | §11对抗性审查协同是新增内容，旧版中不存在 | git diff |

## 改进建议

### REC-001: 建立Skill位置规范（高优先级，对应ACT-001）

- **建议**：在 `.agents/skills/README.md` 中增加"Skill创建规范"章节，明确：所有项目Skill必须放在 `.agents/skills/`，`.trae/skills/` 仅用于Trae IDE平台内置Skill
- **预期收益**：消除位置歧义，防止"影子Skill"再次出现
- **验收标准**：新Skill创建时不再出现位置选择歧义

### REC-002: 建立Skill格式转换检查清单（中优先级）

- **建议**：创建 "Skill格式标准化检查清单"（从平台格式→项目格式的转换项），作为Skill创建流程的一部分
- **预期收益**：新Skill或迁移Skill自动通过格式检查，减少人工审核
- **验收标准**：检查清单包含6个维度（frontmatter/决策树/安全检查/Why解释/Gotchas/关键参考）

### REC-003: 推广"自举验证"到Skill体系（低优先级）

- **建议**：将"任何审查工具本身也应接受审查"的原则推广到所有Skill——安全检查清单本身是否安全？Gotchas列表本身是否有遗漏？
- **预期收益**：提升Skill体系整体质量
- **验收标准**：至少1个Skill完成自举验证

## 可萃取模式

本次洞察识别出以下可复用模式，建议进入萃取流程：

1. **Skill迁移五步法**：分析→决策→迁移→索引更新→旧目录清理
2. **五要素格式标准化**：从平台格式到项目格式的6维度改造清单
3. **位置-管理归属耦合反模式**：识别"位置决定管理归属"导致"影子Skill"的机制
4. **自举验证推广模式**：将对抗性审查方法论中的"自举验证"原则推广到Skill体系