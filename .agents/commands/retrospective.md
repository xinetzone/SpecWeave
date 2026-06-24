+++
id = "retrospective"
category = "process"
source = "AGENTS.md#复盘指令"
+++

# 复盘指令集

## 触发条件

- 项目里程碑完成
- 任务迭代周期结束
- 重大问题或故障发生后
- 用户明确请求复盘

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| scope | string | 是 | 复盘范围：`project`/`iteration`/`task`/`incident` |
| time_range | string | 否 | 时间范围，如 `2024-01-01..2024-01-31` |
| participants | list | 否 | 参与角色列表 |
| focus_areas | list | 否 | 重点关注领域 |

## 执行步骤

### 步骤 1：收集事实数据

- 收集项目/任务的执行记录与变更历史
- 提取关键决策节点与时间线
- 汇总问题与异常事件列表
- 整理产出物与交付结果

### 步骤 2：分析过程

- 按「事实→分析→洞察→建议」结构梳理
- 识别成功因素与失败原因
- 分析流程瓶颈与改进机会
- 评估资源配置合理性

### 步骤 3：提炼洞察

- 归纳可复用模式与最佳实践
- 识别系统性问题与根因
- 总结经验教训与知识沉淀
- 提出具体改进建议

### 步骤 4：生成报告

- 撰写结构化复盘报告
- 包含执行摘要与关键发现
- 列出改进行动项与责任人
- 标注优先级与时间计划

### 步骤 5：归档与通知

- 将报告归档至 `docs/retrospective/reports/`
- 更新知识资产索引
- 通知相关角色与利益相关方
- 同步至自我萃取模块

## 输出规范

| 产出物 | 格式 | 存储位置 |
|--------|------|---------|
| 复盘报告 | Markdown | `docs/retrospective/reports/` |
| 可复用模式 | TOML frontmatter + Markdown | `docs/retrospective/patterns/` |
| 改进行动项 | Markdown | `docs/retrospective/actions/` |
| 执行摘要 | Markdown | 报告开头 |

## 质量验收

- 报告结构完整，包含「事实→分析→洞察→建议」四部分
- 改进建议具体可执行，包含责任人与时间计划
- 可复用模式已标注成熟度等级（L1-L4）
- 报告已归档至指定目录，链接有效
- 相关角色已收到通知

## 约束条件

- 复盘分析必须基于事实数据，不得主观臆断
- 报告须遵循统一模板，确保可追溯与可比较
- 不负责改进建议的执行（归对应执行模块）
- 不负责可复用模式的最终入库评估（归自我萃取）

## 关联资源

- [自我复盘模块](../modules/self-retrospective.md)
- [复盘报告模板](../../docs/retrospective/templates/retrospective-report-template.md)
- [模式成熟度标准](../../docs/retrospective/patterns/README.md)