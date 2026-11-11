---
id: "mermaid"
title: "Mermaid 图表管理指令集"
source: ".agents/commands/mermaid.md"
---
# Mermaid 图表管理指令集

## 触发条件

- 需要创建流程图、时序图、状态图、类图、ER 图、架构图、思维导图、甘特图、饼图等 Mermaid 图表
- 现有 Mermaid 代码需要语法检查和修复
- 复杂图表需要多角色协作创建

## 输入规范

输入参数：`operation`（操作类型：create/check/fix/verify/deliver）、`diagram_type`（图表类型）、`target_file`（目标文件）、`complexity`（复杂度：simple <10 节点 / complex >20 节点）。

## 执行步骤

1. **S0 启动与范围确认**：确认操作类型，评估图表复杂度。
2. **S1 图表设计与类型选择**：根据需求选择图表类型，选择合适的起步模板。
3. **S2 Mermaid 代码生成**：基于模板编写代码，遵循安全编码六规则。
4. **S3 语法检查**：扫描问题，收集 error 与 warning 列表。
5. **S4 自动修复**：修复可自动修复的问题（空行、引号补全等），手动修复其余。
6. **S5 质量验证**：审查语法规范性，验证图表在目标环境中正确渲染。
7. **S6 归档交付**：将代码块插入目标文档，更新相关索引。

## Mermaid 安全编码六规则

1. 禁止空行
2. 含中文/空格的文本加双引号
3. 避免列表触发字符（`-` `*` `+` `1.`）
4. 节点与标签文本保持单行；需要分隔时用空格，不使用换行标签
5. subgraph 使用 `ID ["标题"]` 格式
6. 边标签使用 `| "标签" |` 格式

## 图表类型决策树

流程/步骤 → flowchart；交互/时序 → sequenceDiagram；状态变迁 → stateDiagram-v2；类关系/继承 → classDiagram；数据模型/关系 → erDiagram；层级/脑图 → mindmap；时间线/进度 → gantt / timeline；占比/分布 → pie。

## 质量验收

- 扫描无 error 级问题
- 遵循安全编码六规则（中文文本加双引号、无空行、无换行标签）
- 图表在目标环境（IDE / GitHub / 飞书）中正确渲染