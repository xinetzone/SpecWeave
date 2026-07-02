---
id: "convention-driven-creation"
source: "docs/retrospective/knowledge-extraction.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/convention-driven-creation.toml"
---
# 约定驱动创建模型：范例即模板

## 核心原则
在成熟规范体系内创建新模块时，最优路径是"先读范例、提取模板、填充内容"，而非"先设计结构、再对齐规范"。既有文件本身就是最准确的创建模板，使结构决策成本降为零。

## 成熟度评估
| 维度 | 评估 | 依据 |
|---|---|---|
| 实践验证 | 高 | 6 个文件零结构决策创建 |
| 可复用性 | 高 | 适用于任何成熟规范体系内的扩展 |
| 通用性 | 中 | 依赖体系内已有 ≥3 个同类范例 |

## 流程图
```mermaid
flowchart LR
    A["读取 N 个既有范例"] --> B["提取结构模板"]
    B --> C["填充业务内容"]
    C --> D["零结构决策交付"]
    D --> E["索引同步"]
    E --> F["工具校验"]
```

## 执行步骤

| 步骤 | 动作 | 产出 |
|---|---|---|
| 1. 范例采集 | 读取体系内 ≥3 个同类文件 | 结构特征清单 |
| 2. 模板提取 | 识别 frontmatter 格式、正文结构、图表风格、数据模型规范 | 隐式结构模板 |
| 3. 内容填充 | 按模板填充业务内容，无需任何结构决策 | 新模块文件 |
| 4. 索引同步 | 更新所有引用该类文件的索引 | 可发现的模块 |
| 5. 工具校验 | 运行链接检查器等验证工具 | 质量门禁通过 |

## 成熟度度量

规范体系的成熟度可用"扩展新模块时的结构决策数"来度量：

```
规范成熟度 = 1 / 扩展时的结构决策数
```

- 决策数 = 0：体系完全成熟，范例即模板
- 决策数 ≤ 2：体系高度成熟，少量决策即可
- 决策数 ≥ 5：体系尚未成熟，需先建立范例

## 适用条件

- 体系内已有 ≥ 3 个同类文件可作为范例
- 范例间结构一致性高（如均使用相同的 frontmatter 格式与正文结构）
- 新模块属于既有类别（如新角色、新协议、新工作流）

## 不适用场景

- 体系内无同类范例（首创建模）
- 范例间结构不一致（需先统一规范）
- 新模块跨多个类别（需组合多个模板）

## 与既有方法论的关系

| 方法论 | 关系 |
|---|---|
| `spec-driven-development.md` | 本模型是其补充——当体系成熟度足够高时，"范例即规格"，可跳过显式 spec 阶段 |
| `three-tier-governance.md` | 本模型对应第一层"原子化"的创建阶段 |
| `review-insight-export-loop.md` | 复盘环节识别"零决策"经验后，萃取为本模型 |

## 实践案例

| 案例 | 范例数 | 新建文件数 | 结构决策数 | 成熟度 |
|---|---|---|---|---|
| 团队管理模块创建 | 10 | 6 | 0 | 完全成熟 |

> 来源：来自 retrospective-report-teams-module.md 洞察 1、方法论 1
> 关联模块：`docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.md`、`docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md`
