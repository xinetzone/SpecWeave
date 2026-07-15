---
id: "pattern-extraction-update-merge"
title: "现有模式更新与模式合并重构方案"
source: "SKILL.md#03-update-merge"
x-toml-ref: "../../../../.meta/toml/.agents/skills/pattern-extraction-cmd/SKILL/03-update-merge.toml"
---
# 现有模式更新与模式合并重构方案

## 7. 方案二：现有模式更新

当模式被成功应用或复用时，更新frontmatter字段：

```bash
cd d:\spaces\SpecWeave

# 验证模式被成功应用后
python .agents/scripts/pattern-maturity.py validate <模式文件路径>

# 模式被其他任务复用后
python .agents/scripts/pattern-maturity.py reuse <模式文件路径>

# 检查并更新索引统计
python .agents/scripts/pattern-maturity.py check-index --fix
```

成熟度升级条件：
- L0→L1：首次成功验证，补充完整文档结构（含反模式章节）
- L1→L2：validation_count ≥ 2（至少2次成功验证，含1次非原作者复用更佳）
- L2→L3：同时满足以下全部条件：
  1. `validation_count ≥ 5`（至少5次成功验证）
  2. **至少2次跨领域场景验证**（不能仅在单一类型任务中重复，例如：不能5次都是文档类治理，必须包含代码重构/配置迁移/CI更新/知识库归档等非文档类场景）
  3. `reuse_count ≥ 1`（已被非原作者成功复用）
  4. 已沉淀为模板/工具/脚本中的标准SOP（零修改可复用）
- L3→L4：已集成至CI/工具链自动化验证，人工干预点为零

> **为什么validation_count和reuse_count要分开计数？** "自己用了两次"和"别人复用了一次"的可信度完全不同。reuse_count是模式通用性的强信号——非原作者能成功复用说明模式的抽象层级合适、文档足够清晰，这是L3（可复用）的核心判断标准。
>
> **为什么L2→L3需要跨领域验证？** 单一类型场景中验证5次可能只是"在同一类问题上重复使用"，并不能证明模式的通用抽象能力。跨领域验证（如文档治理→代码重构→配置迁移）才能暴露模式的适用边界，确保抽象层级足够通用（来源案例：phased-rollout-validation和classification-disposition-decision-tree两个L2模式在3次文档类场景验证后发现仍需补充非文档类验证方可升级L3）。


## 8. 方案三：模式合并/重构

遵循 [pattern-merge-boundary.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md) 的三维重叠度判断：

```
两个模式是否需要合并？
├─ 场景重叠度 >70% AND 机制重叠度 >70% AND 建议重叠度 >70% → 合并
├─ 三维重叠度均 <30% → 独立创建
└─ 30%-70%重叠 → 独立判断，考虑引用关联而非合并
```

合并后保留更成熟的模式id，将另一个的内容整合进来，更新related_patterns，删除被合并的文件并在索引中标记。


## 9. 交叉引用系统化检查（方案二/三必做）

模式升级/合并/重命名后，必须执行交叉引用系统化检查，避免"模式已升级但引用仍指向旧位置"的断链：

1. **关键词搜索**：用中英文双关键词 Grep 搜索所有引用（如"三查"+"three-checks"）
2. **文件分类**：识别三类文件
   - **需更新**：引用了旧位置/旧成熟度的文件
   - **已正确**：引用已指向新位置
   - **不同概念**：关键词相同但语义不同的文件（无需更新，需显式判定避免误更新）
3. **更新方式**：采用"添加更新说明"（blockquote 标注更新时间和背景）而非重写原文，保留决策可审计性
4. **验证**：更新后重新 Grep 确认无遗漏

> **为什么必须执行交叉引用检查？** 模式入库不是"创建文件+提交"就完成，还包括"所有引用同步更新"。交叉引用是隐性债务：模式升级时如果不系统化检查，债务会累积成断链。交叉引用更新的工作量通常与模式入库本身相当（来源案例：三查流程L3升级时交叉引用更新6文件，与模式入库本身3文件量级相当）。

**来源**：[retrospective-pattern-formalization-cross-reference-20260704](../../../docs/retrospective/reports/competitive-analysis/retrospective-pattern-formalization-cross-reference-20260704/insight-extraction.md) 洞察2


---

## 相关模式

- - [insight-cmd Skill](../../insight-cmd/SKILL.md)
- - [retrospective-cmd Skill](../../retrospective-cmd/SKILL.md)
- - [CMD-LOG日志规范](../../../rules/cmd-log-specification.md)
- - [模式成熟度管理](../../../scripts/pattern-maturity.py)
- - [模式萃取方法论](../../../docs/retrospective/patterns/README.md)
- - [模式合并边界判断](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md)

← 上一章: [核心步骤与全新模式创建方案](02-core-steps-create.md) | **[返回索引](../SKILL.md)** | 下一章 → [CMD-LOG执行日志与质量安全清单](04-cmd-log-quality.md)
