---
id: "retrospective-specweave-contest-advantage-analysis-20260624-meta-knowledge-updates"
title: "知识库更新清单"
source: "external: 不存在-retrospective-meta-20260625/ — 元复盘四份产出"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/competitive-analysis/retrospective-specweave-contest-advantage-analysis-20260624/retrospective-meta-20260625/knowledge-updates.toml"
---
# 知识库更新清单

> 本次元复盘完成后，需要在以下位置执行更新操作。

## 一、资产清单更新

文件：[资产清单与复用指南](../../../../assets/asset-inventory.md)

### 1.1 项目复盘报告索引（行 80-81 后插入）

在 `retrospective-specweave-contest-advantage-analysis-20260624/` 条目行末追加元复盘信息：

```markdown
| `retrospective-specweave-contest-advantage-analysis-20260624/` | 竹简悟道 + SpecWeave 双作品参赛策略分析（真实参赛对齐 v11） | ... | → 萃取为方法论模式 ... 及元复盘新增 4 个模式（信息源分层采集/模板同质化避让/反向借势/元复盘双轮法） |
```

### 1.2 可复用模式列表（行 48-58 后插入）

在现有模式表末尾插入 4 个新模式：

```markdown
| 信息源分层采集策略 | 按"规则层优先→操作层次之→品牌层佐证→事实层验证"四层顺序采集信息，避免层级错位导致的策略方向重建 | 竞品分析/政策研判/招投标情报等多源信息采集场景 |
| 模板同质化避让策略 | 在官方提供标准化模板的场景中，通过"内容→结构→品类"三层差异化空间逃离均值区间 | 竞赛/投标/申请等有标准化模板的场景 |
| 反向借势——从规则约束中读出最优解 | 三阶段解读法将限制性规则从障碍转换为策略导航，主动拥抱约束而非绕行 | 赛事策略/招投标/资源分配等有明确限制条款的场景 |
| 元复盘双轮法 | 重大项目结束后执行两层复盘——战役级（存档）+ 方法级（入库），最大化知识跨项目迁移率 | 所有需要做复盘的项目 |
```

### 1.3 关联模块行

追加新模式引用：

```markdown
> - `patterns/methodology-patterns/information-source-tiered-collection.md`
> - `patterns/methodology-patterns/template-homogenization-escape.md`
> - `patterns/methodology-patterns/reverse-leverage-rule-constraints.md`
> - `patterns/methodology-patterns/meta-retrospective-two-round-method.md`
```

## 二、主 README 导航更新

文件：`retrospective-specweave-contest-advantage-analysis-20260624/README.md`

在子模块导航表格中插入元复盘入口：

```markdown
| 元复盘 | [retrospective-meta-20260625/](retrospective-meta-20260625/README.md) | 对分析项目本身的全生命周期元复盘：11轮迭代/12来源/3断裂事件/6条元洞察/4个可复用模式 |
```

同时更新项目概览核心指标：
- 把数据来源数从 12 维持在 12
- 把"识别短板"的描述更新或保持

## 三、可复用模式创建

以下 4 个新方法论模式应创建为独立文件：

| 序号 | 文件名 | 来源 |
|------|--------|------|
| 1 | `patterns/methodology-patterns/information-source-tiered-collection.md` | `retrospective-meta-20260625/pattern-extraction.md#模式-1` |
| 2 | `patterns/methodology-patterns/template-homogenization-escape.md` | `retrospective-meta-20260625/pattern-extraction.md#模式-2` |
| 3 | `patterns/methodology-patterns/reverse-leverage-rule-constraints.md` | `retrospective-meta-20260625/pattern-extraction.md#模式-3` |
| 4 | `patterns/methodology-patterns/meta-retrospective-two-round-method.md` | `retrospective-meta-20260625/pattern-extraction.md#模式-4` |

> ⚠️ 模式 3（反向借势）与既有模式 `zero-sum-rule-inversion.md` 有概念重叠，建议在后续迭代中合并为一个模式，保留更通用的版本并标注演化历史。

## 四、maturity 更新

既有模式 `multi-source-intelligence-iteration.md` 因其在本次元复盘中的再次验证，建议从 L2 保持 L2，但更新 `validation_count` 从 2 到 3。

## 五、关联报告引用链

以下报告之间存在引用关系，确认链接有效性：

```
retrospective-trae-contest-faq-analysis-20260624/  ← 起点（FAQ 单源分析）
        ↓
retrospective-specweave-contest-advantage-analysis-20260624/  ← 延长线（12 源全量分析）
        ├── retrospective-v11-iteration/                       ← 一次复盘（v10→v11 转向）
        └── retrospective-meta-20260625/                       ← 二次复盘（全生命周期元复盘）
                ↓
        patterns/methodology-patterns/ (5 个已有模式 + 4 个新增模式)
```

---
*数据来源：元复盘全部产出 + asset-inventory.md + patterns/ 目录现有状态*
