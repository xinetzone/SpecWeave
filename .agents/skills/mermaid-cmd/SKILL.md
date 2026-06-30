---
name: mermaid-cmd
version: 1.0.0
description: "当用户提到'mermaid'、'流程图'、'时序图'、'状态图'、'画个图'、'图表'、'架构图'、'思维导图'、'ER图'、'类图'、'甘特图'、'饼图'、'UML图'、'可视化流程'、'画流程图'、'mermaid图'、'可视化'、'流程可视化'时，必须使用此技能。提供标准化的Mermaid图表创建、检查、修复流程，引导完成从设计→编码→检查→修复→验证→交付的完整闭环。不要手写Mermaid代码绕过本Skill——本Skill封装了安全编码六规则、模板选择、自动检查修复流程，确保图表质量可预测。"
argument-hint: "<operation:create/check/fix/verify> [diagram_type] [target_file]"
user-invocable: true
paths:
  - ".agents/commands/mermaid.md"
  - ".agents/templates/mermaid-templates/"
  - ".agents/scripts/lib/checks/mermaid.py"
  - "rules/cmd-log-specification.md"
  - "docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md"
  - ".agents/teams/mermaid-team.md"
---

# Mermaid 图表管理命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/mermaid.md](../../commands/mermaid.md)（完整流程）+ [cmd-log-specification.md](../../rules/cmd-log-specification.md)（日志规范）+ [mermaid-safe-coding-rules.md](../../../docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md)（安全编码规则）

## 1. Skill ID
`mermaid-cmd`

## 2. 功能描述

提供标准化Mermaid图表全生命周期管理能力，三种方案选择：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **快速生成** | ⭐ 简单图表（<10节点、单图层） | 模板起步，快速交付 |
| **检查修复** | ⭐ 已有Mermaid代码需要校验修复 | 自动检测+修复常见问题 |
| **复杂图表协作** | ⭐ 大型架构图（>20节点、多subgraph） | 触发team-mermaid团队多角色协作 |

核心功能：模板推荐 → 代码生成 → 语法检查 → 自动修复 → 质量验证 → 归档交付。

> **为什么用本Skill而非手写Mermaid？** 手写Mermaid容易违反安全编码规则（空行导致解析中断、中文文本无引号、\n换行符不兼容），在不同宿主环境（IDE/GitHub/飞书）渲染不一致。本Skill封装了安全编码六规则和自动检查修复流程，确保图表一次写对、多环境兼容。

## 3. 何时使用本技能

触发词列表（description中的完整列表）：
- "mermaid"、"流程图"、"时序图"、"状态图"、"画个图"
- "图表"、"架构图"、"思维导图"、"ER图"、"类图"
- "甘特图"、"饼图"、"UML图"、"画流程图"、"mermaid图"
- "可视化"、"流程可视化"
- 用户需要创建/检查/修复任何Mermaid图表时

> **关于触发**：即使没有明确说"用mermaid命令"，只要涉及创建图表、可视化流程、画架构图等，就应该使用本Skill。Mermaid是项目首选可视化工具（见AGENTS.md全局规则），不要用其他格式替代。

## 4. 方案选择决策树

```
需要处理Mermaid图表？
├─ 已有Mermaid代码需要校验/修复？ → 检查修复方案
│  └─ 运行 check-mermaid.py → --fix自动修复 → 手动修复剩余问题
├─ 创建新图表，复杂度如何评估？
│  ├─ 节点数<10、单图层、无跨文档引用？ → 快速生成方案（单角色交付）
│  │  └─ 选择模板 → 生成代码 → 自检 → 交付
│  └─ 节点数>20、多subgraph、跨文档引用？ → 复杂图表协作方案
│     └─ 触发 team-mermaid 团队：architect设计→developer编码→reviewer审查→tester渲染验证
└─ 不确定选什么图表类型？ → 参考commands/mermaid.md中的图表类型决策树
```

**图表类型快速决策**：
- 流程/步骤 → flowchart
- 交互/时序 → sequenceDiagram
- 状态变迁 → stateDiagram-v2
- 类关系/继承 → classDiagram
- 数据模型 → erDiagram
- 层级/脑图 → mindmap
- 时间线/进度 → gantt
- 占比/分布 → pie

**与其他Skill的关系**：
- 复杂架构图协作使用 team-mermaid 团队
- Mermaid相关规则沉淀使用 retrospective-cmd 复盘

> **为什么复杂图需要团队协作？** 大型架构图（>20节点、多subgraph）单角色难以兼顾"结构正确性、语法规范性、渲染兼容性"三个维度——architect关注模块关系正确性，developer负责语法细节，reviewer把关规范合规，tester验证多环境渲染。四角色分工协作才能确保复杂图表质量。

## 5. 核心步骤（快速开始）

```
步骤1：读取 [commands/mermaid.md](../../commands/mermaid.md) 了解完整S0-S6七步流程
步骤2：评估复杂度并选择方案（快速生成/检查修复/复杂协作）
步骤3：快速生成方案：
   - 从 templates/mermaid-templates/ 选择合适模板
   - 基于模板编写代码，遵循安全编码六规则
   - 运行 python .agents/scripts/check-mermaid.py 自检
   - 使用 --fix 自动修复可修复问题
步骤4：检查修复方案：
   - 运行 python .agents/scripts/check-mermaid.py --path <target>
   - 使用 --fix 自动修复（空行/引号/换行符）
   - 手动修复剩余error级问题
步骤5：复杂协作方案：
   - 触发 team-mermaid 团队（参见 teams/mermaid-team.md）
   - 按三阶段工作流（设计→编码→审查验证）执行
步骤6：验证渲染正确性，插入目标文档
```

> 完整RACI矩阵、输入参数规范、约束条件见L2文档 [commands/mermaid.md](../../commands/mermaid.md)。

## 6. Mermaid安全编码六规则（必背）

- [ ] 禁止空行：代码块内不能有空行，空行可能导致解析中断
- [ ] 文本加引号：含中文、空格、特殊字符（@#≥≤+）的节点/标签文本必须用双引号包裹
- [ ] 避免列表触发：文本不要以 `- `、`* `、`+ `、`1. ` 开头，会触发Markdown列表解析
- [ ] 换行用<br/>：文本内换行使用 `<br/>` 而非 `\n`
- [ ] subgraph安全格式：使用 `subgraph EN_ID ["中文标题"]` 格式，不要直接用中文ID
- [ ] 边标签格式：箭头标签使用 `-->| "标签" |` 格式，中文标签加引号

> 完整规则说明和正反例见L2文档 [mermaid-safe-coding-rules.md](../../../docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md)。

## 7. 安全检查清单（Mermaid质量门）

- [ ] 创建前已评估复杂度，确定使用正确方案（快速/检查/协作）
- [ ] 已选择合适的图表类型（参考决策树）
- [ ] 简单图表已基于模板起步，而非从零开始
- [ ] 代码遵循安全编码六规则（空行/引号/列表/换行/subgraph/边标签）
- [ ] 已运行 check-mermaid.py 检查，无error级问题
- [ ] 中文/空格文本均已加双引号
- [ ] 复杂图表（>20节点）已触发team-mermaid团队协作
- [ ] 插入目标文档后链接有效，索引已更新（如需要）

## 8. 执行日志（CMD-LOG）

执行mermaid命令集时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=mermaid`，session前缀 `merm-YYYYMMDD-<topic>`
- 步骤编号 S0-S6（启动→设计→编码→检查→修复→验证→归档）
- 8个特有事件：`DIAGRAM_DESIGNED`、`CODE_GENERATED`、`CHECK_COMPLETED`、`FIX_APPLIED`、`VERIFY_PASSED`、`VERIFY_FAILED`、`TEMPLATE_RECOMMENDED`、`TEAM_COLLABORATION`

> 完整字段说明、事件表格、日志示例见L2文档 [cmd-log-specification.md]（后续将在7.6节更新）和 [commands/mermaid.md §CMD-LOG日志规范](../../commands/mermaid.md#cmd-log日志规范)。

## 9. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/约束/步骤） | L2 | [commands/mermaid.md](../../commands/mermaid.md) | 每次使用必读 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式、事件定义 |
| 安全编码六规则 | L2 | [mermaid-safe-coding-rules.md](../../../docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md) | 编写代码时必读 |
| Mermaid模板目录 | L2 | [templates/mermaid-templates/](../../templates/mermaid-templates/) | 创建新图表时选择模板 |
| Mermaid检查脚本 | L2 | [scripts/lib/checks/mermaid.py](../../scripts/lib/checks/mermaid.py) | 语法检查与自动修复 |
| team-mermaid专项团队 | L2 | [teams/mermaid-team.md](../../teams/mermaid-team.md) | 复杂图表协作 |
| 渐进式披露架构 | L2 | [capabilities/ARCHITECTURE.md](../../capabilities/ARCHITECTURE.md) | 理解三层架构设计 |

## 10. Changelog

- **v1.0.0** (2026-06-30): 初始版本，支持Mermaid图表生成/检查/修复/协作全流程，封装安全编码六规则和自动检查修复。
