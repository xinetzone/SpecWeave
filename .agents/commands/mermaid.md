---
id: "mermaid"
source: "AGENTS.md#mermaid指令"
x-toml-ref: "../../.meta/toml/.agents/commands/mermaid.toml"
---
# Mermaid图表管理指令集

## 触发条件

- 用户需要创建流程图、时序图、状态图、类图、ER图、架构图、思维导图、甘特图、饼图等Mermaid图表
- 现有Mermaid代码需要语法检查和修复
- 复杂图表需要多角色协作创建
- 全项目Mermaid质量扫描与修复
- Mermaid模板选择与推荐

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| operation | string | 是 | 操作类型：create/check/fix/template/verify/deliver |
| diagram_type | string | 否 | 图表类型：flowchart/sequenceDiagram/stateDiagram/classDiagram/erDiagram/mindmap/gantt/pie等 |
| target_file | string | 否 | 目标Markdown文件路径 |
| complexity | string | 否 | 复杂度评估：simple(<10节点)/complex(>20节点)，默认simple |
| use_template | boolean | 否 | 是否使用模板起步，默认true |

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，拥有最终决策权，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| Mermaid核心活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 触发与范围确认 | **R/A** | C | C | C | I | I |
| 图表类型选择与架构设计 | C | **R/A** | C | C | I | I |
| Mermaid代码生成/编写 | I | C | **R/A** | I | I | I |
| 语法检查与自动修复 | I | I | R | **A** | I | I |
| 图表渲染验证 | I | C | C | C | **R/A** | I |
| 质量验收与规范审查 | I | C | I | **R/A** | C | I |
| 插入文档与索引更新 | **R/A** | I | C | C | I | I |
| 复杂跨模块架构图审批 | R | C | I | C | I | **A** |

### 审批权限边界

- 简单图表（<10节点）：developer自检后交付，reviewer抽检
- 复杂图表（>20节点、多subgraph）：architect设计→developer编码→reviewer审查→tester渲染验证
- 跨模块架构图：需co-founder最终审批
- 批量质量修复：reviewer审核修复方案，developer执行

## 执行步骤

### S0：启动与范围确认

- 确认操作类型（create/check/fix/verify/deliver）
- 评估图表复杂度（simple/complex）
- 判断是否需要团队协作（complex触发team-mermaid）
- 记录CMD-LOG: CMD_START

### S1：图表设计与类型选择

- 根据需求选择合适的图表类型（参考决策树）
- architect负责复杂图表的结构设计
- 选择合适的起步模板（从templates/mermaid-templates/中选择）
- 记录CMD-LOG: DIAGRAM_DESIGNED

### S2：Mermaid代码生成

- 基于模板起步编写代码
- 遵循Mermaid安全编码六规则：
  - 禁止空行
  - 含中文/空格的文本加双引号
  - 避免列表触发字符（- * + 1.）
  - 换行使用`<br/>`而非`\n`
  - subgraph使用`ID ["标题"]`格式
  - 边标签使用`| "标签" |`格式
- 记录CMD-LOG: CODE_GENERATED

### S3：语法检查

- 运行 `python .agents/scripts/check-mermaid.py` 扫描问题
- 收集error和warning列表
- 记录CMD-LOG: CHECK_COMPLETED（含issues计数）

### S4：自动修复

- 使用 `--fix` 参数修复可自动修复的问题（空行、引号补全等）
- 手动修复无法自动修复的问题
- 记录CMD-LOG: FIX_APPLIED（含fixes计数）

### S5：质量验证

- reviewer审查Mermaid语法规范性
- tester验证图表在目标环境中正确渲染
- 检查图表可读性、准确性、一致性
- 记录CMD-LOG: VERIFY_PASSED/VERIFY_FAILED

### S6：归档交付

- 将Mermaid代码块插入目标文档
- 更新相关索引文件（如需要）
- 记录CMD-LOG: CMD_COMPLETE

**Mermaid图表类型决策树**：
- 流程/步骤 → flowchart
- 交互/时序 → sequenceDiagram
- 状态变迁 → stateDiagram-v2
- 类关系/继承 → classDiagram
- 数据模型/关系 → erDiagram
- 层级/脑图 → mindmap
- 时间线/进度 → gantt/timeline
- 占比/分布 → pie
- 架构/模块关系 → flowchart（多subgraph）

## 输出规范

| 产出物 | 格式 | 存储位置 |
|--------|------|---------|
| Mermaid代码块 | ```mermaid ... ``` | 目标Markdown文件中 |
| 检查修复报告 | 控制台输出 | 临时，不归档 |
| 质量验收记录 | CMD-LOG日志 | 控制台输出 |

## 质量验收

- check-mermaid.py扫描无error级问题
- 遵循Mermaid安全编码六规则
- 图表在目标环境（IDE/GitHub/飞书）中正确渲染
- 中文文本均已加双引号
- 无空行、无`\n`换行符
- 边标签和节点文本格式正确

## 约束条件

- 不实现服务端渲染或图片导出（由宿主环境负责）
- 必须遵循安全编码六规则
- 复杂图表必须触发team-mermaid团队协作
- 所有Mermaid代码必须通过check-mermaid.py检查
- 不修改vendor/目录下的任何文件

## CMD-LOG日志规范

- cmd标识：mermaid
- Session ID前缀：merm-
- Session格式：merm-YYYYMMDD-<topic>
- 步骤：S0-S6共7步

**特有事件定义**：

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 图表类型确定 | INFO | DIAGRAM_DESIGNED | 设计完成：<diagram_type>，复杂度：<complexity>，模板：<template> | diagram_type, complexity, template_used |
| 代码生成完成 | INFO | CODE_GENERATED | Mermaid代码生成完成：<节点数>个节点，使用模板：<template> | node_count, edge_count, template_used |
| 语法检查完成 | INFO/WARN | CHECK_COMPLETED | 语法检查完成：发现<N>个错误，<M>个警告 | error_count, warning_count, issues |
| 自动修复应用 | INFO | FIX_APPLIED | 自动修复应用：修复了<N>个问题（空行/引号/换行符） | fixed_count, fix_types |
| 验证通过 | INFO | VERIFY_PASSED | 质量验证通过：渲染正确，规范合规 | validator, render_target |
| 验证失败 | WARN | VERIFY_FAILED | 验证失败：<原因>，需要返工 | failure_reason, failed_step |
| 模板推荐 | INFO | TEMPLATE_RECOMMENDED | 推荐模板：<template_name>，适用场景：<scenario> | template_name, scenario, alternatives |
| 团队协作触发 | INFO | TEAM_COLLABORATION | 触发团队协作：<原因>，参与角色：<roles> | reason, roles, complexity |

**典型日志示例**：

```
[CMD-LOG] | level=INFO | cmd=mermaid | step=S0 | event=CMD_START | session=merm-20260630-architecture | msg=开始创建Mermaid图表：架构流程图，复杂度：complex | ctx={"operation":"create","diagram_type":"flowchart","complexity":"complex","target_file":".agents/capabilities/ARCHITECTURE.md"}
[CMD-LOG] | level=INFO | cmd=mermaid | step=S4 | event=FIX_APPLIED | session=merm-20260630-architecture | msg=自动修复应用：修复了3个问题（空行2处、引号补全1处） | ctx={"fixed_count":3,"fix_types":["空行","引号"]}
[CMD-LOG] | level=INFO | cmd=mermaid | step=S6 | event=CMD_COMPLETE | session=merm-20260630-architecture | msg=Mermaid图表完成：三层架构流程图已插入文档 | ctx={"duration":"~15min","node_count":12,"subgraph_count":3,"verification":"passed"}
```

## 关联资源

- [Mermaid安全编码六规则](../../docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md)
- [Mermaid模板目录](../templates/mermaid-templates/)
- [Mermaid检查脚本](../scripts/lib/checks/mermaid.py)
- [CMD-LOG日志规范](../rules/cmd-log-specification.md)
- [mermaid-cmd Skill门面](../skills/mermaid-cmd/SKILL.md)
- [team-mermaid专项团队](../teams/mermaid-team.md)
