# 七概念方法论触发匹配工具（seven-concepts-trigger）

## 功能说明

根据自然语言任务描述，自动推荐七概念方法论的概念组合、执行流程、质量门提醒。3秒判断当前任务该用哪个概念组合，不用翻阅10页文档。

## 用法

```bash
# 基本用法：输入任务描述
python .agents/scripts/seven-concepts-trigger.py "Sprint结束做复盘"

# 返回Top3匹配结果
python .agents/scripts/seven-concepts-trigger.py "重构文档" --top 3

# 列出所有支持的18种典型场景
python .agents/scripts/seven-concepts-trigger.py --list
```

## 输出示例

```
📋 任务描述：Sprint结束了做个复盘
============================================================

🎯 场景：里程碑/迭代完成
   置信度：█████████░ 95%
   概念组合：R → I → E → C
   参考流程：W1 里程碑复盘闭环 [R→I→E→C]
   🚧 质量门：
      • G1:事实无因果词
      • G2:洞察四元组完整可证伪
      • G3:模式通过V审查入库

============================================================
📖 详细规则参考：seven-concepts-quick-reference.md
```

## 支持的18种典型场景

| 场景关键词 | 推荐概念组合 | 参考流程 | AP9预警 |
|-----------|-------------|---------|---------|
| 里程碑/迭代/Sprint结束/版本交付 | R→I→E→C | W1 | — |
| P0故障/线上止血 | （先恢复，事后R+I） | 无 | — |
| P1+故障/Bug根因/问题解决 | F→V→C→R→I→E | W2 | — |
| 新功能开发（默认匹配） | C→V | — | — |
| 重构/技术债/结构优化 | A→V→C→(R) | W3 | — |
| 文档整理/原子化拆分 | A→V→C | W3 | — |
| 知识沉淀/模式入库 | R→I→E→V | W4 | — |
| 架构决策/技术选型 | F→V→I→C | W5 | — |
| 规范制定/规则更新 | F→V→E→C | W5变体 | — |
| 代码审查/PR Review | V→C | — | — |
| 版本发布/打标签 | V→C | — | — |
| P2/P3非紧急小Bug | V→C→(R) | — | — |
| 新人Onboarding/培训 | R→E | — | — |
| 工具链/CI/脚本优化 | V→C→I | — | 规则/检查类脚本触发 |
| **规则引擎/匹配/分类/推荐系统** | **F→V→C** | — | **✅ 默认触发** |
| 跨项目迁移/目录重构 | A→V→C | W3 | — |
| PoC/原型验证/探索 | C | — | — |
| 简单修改/typo/格式调整 | C | — | — |

## 置信度说明

| 置信度 | 含义 |
|-------|------|
| 90%+ | 明确匹配典型场景，直接按推荐执行 |
| 70-89% | 大概率匹配，建议快速验证后执行 |
| 40-69% | 默认匹配（新功能开发），如遇复杂场景追加F第一性原理 |
| <30% | 无匹配/非开发任务，请人工判断或查阅速查手册 |

## 单元测试

```bash
# 运行19场景批量测试（含3个AP9/反向验证场景）
python .agents/scripts/test-seven-concepts-trigger.py
```

## 相关文档

- [七概念速查手册](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/seven-concepts-quick-reference.md)
- [七概念触发决策树](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/seven-concepts-trigger-decision-tree.md)
- [元方法论自举行动计划](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/meta-bootstrap-action-plan.md)

## Changelog

- 2026-07-11：v1.1，新增规则引擎/匹配/分类场景（18种），集成AP9反模式自动预警；测试用例增至19个（100%通过）
- 2026-07-11：初始版本，17种场景支持，V对抗审查修复1个误判Bug（"做个蛋糕"误识别为开发任务）
