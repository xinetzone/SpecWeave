# 系统规划章节新增任务复盘萃取 Spec

## Why

本次「系统规划章节新增」任务经历了需求增量式演进（4 模块→8 模块），产生了有价值的执行经验与可复用知识。需按项目"复盘→洞察→导出知识闭环"方法论，对本次任务进行复盘、提取洞察、萃取可复用资产，沉淀为知识库资产。

## What Changes

- **新增复盘报告**：`docs/retrospective/reports/retrospective-report-system-planning.md`，遵循"事实→分析→洞察→建议"四段式结构
- **萃取可复用模式**：提炼功能模块设计的五要素标准结构、四层闭环架构、增量式需求扩展应对策略
- **更新资产清单**：在 `docs/retrospective/assets/asset-inventory.md` 补充本次新增资产
- **更新复盘索引**：在 `docs/retrospective/README.md` 的 reports 索引中补充新报告

## Impact

- **Affected specs**: 无功能变更，纯知识沉淀
- **Affected code**: 无代码变更
- **Affected docs**: 新增复盘报告、更新资产清单与复盘索引

## ADDED Requirements

### Requirement: 复盘报告

SHALL 生成符合项目复盘报告模板的分析报告，涵盖项目概述、复盘环节、洞察环节、导出环节四部分。

#### Scenario: 复盘本次任务
- **WHEN** 读者阅读复盘报告
- **THEN** 能够了解任务背景、执行过程、关键决策、量化数据、成功经验与存在问题

### Requirement: 洞察提取

SHALL 从本次任务中提取至少 3 条核心洞察，每条有支撑事实与深层含义。

#### Scenario: 提取洞察
- **WHEN** 读者阅读洞察环节
- **THEN** 能够看到增量式需求演进、模块化可扩展性、四层闭环架构等规律性认知

### Requirement: 知识萃取

SHALL 萃取至少 2 个可复用模式或模板，沉淀到复盘文档体系。

#### Scenario: 萃取可复用资产
- **WHEN** 读者查阅萃取内容
- **THEN** 能够获得功能模块设计五要素标准结构、四层闭环架构等可直接复用的模式

## MODIFIED Requirements

### Requirement: 资产清单与索引更新

SHALL 同步更新资产清单与复盘索引，确保新增资产可被发现。

## REMOVED Requirements

无。
