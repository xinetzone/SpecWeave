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
- L1→L2：validation_count ≥ 2（至少2次成功验证）
- L2→L3：reuse_count ≥ 1 且 validation_count ≥ 2（已被非原作者复用）
- L3→L4：已集成至CI/工具链自动化验证

> **为什么validation_count和reuse_count要分开计数？** "自己用了两次"和"别人复用了一次"的可信度完全不同。reuse_count是模式通用性的强信号——非原作者能成功复用说明模式的抽象层级合适、文档足够清晰，这是L3（可复用）的核心判断标准。


## 8. 方案三：模式合并/重构

遵循 [pattern-merge-boundary.md](../../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md) 的三维重叠度判断：

```
两个模式是否需要合并？
├─ 场景重叠度 >70% AND 机制重叠度 >70% AND 建议重叠度 >70% → 合并
├─ 三维重叠度均 <30% → 独立创建
└─ 30%-70%重叠 → 独立判断，考虑引用关联而非合并
```

合并后保留更成熟的模式id，将另一个的内容整合进来，更新related_patterns，删除被合并的文件并在索引中标记。


---

## 相关模式

- - [insight-cmd Skill](../../insight-cmd/SKILL.md)
- - [retrospective-cmd Skill](../../retrospective-cmd/SKILL.md)
- - [CMD-LOG日志规范](../../../rules/cmd-log-specification.md)
- - [模式成熟度管理](../../../scripts/pattern-maturity.py)
- - [模式萃取方法论](../../../../docs/retrospective/patterns/README.md)
- - [模式合并边界判断](../../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md)

← 上一章: [核心步骤与全新模式创建方案](02-core-steps-create.md) | **[返回索引](../SKILL.md)** | 下一章 → [CMD-LOG执行日志与质量安全清单](04-cmd-log-quality.md)
