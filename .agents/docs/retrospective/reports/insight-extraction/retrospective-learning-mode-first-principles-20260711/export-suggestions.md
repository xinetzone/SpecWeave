---
title: "导出建议"
parent: "README.md"
source: "学习模式第一性原理分析项目复盘"
---
# 导出建议

## 1. 归档状态

- **归档状态**：✅ 已完成归档
- **归档位置**：`docs/retrospective/reports/insight-extraction/standalone/first-principles-learning-mode/`
- **Spec位置**：`.trae/specs/retrospectives-insights/first-principles-learning-mode-analysis/`
- **复盘位置**：本目录

## 2. 产出物清单

| 类型 | 路径 | 状态 |
|------|------|------|
| 分析报告（原子化） | [standalone/first-principles-learning-mode/](../../insight-extraction/standalone/first-principles-learning-mode/README.md) | ✅ 已完成 |
| PRD摘要 | [prd-summary.md](../../../../../../.trae/specs/retrospectives-insights/first-principles-learning-mode-analysis/prd-summary.md) | ✅ 已完成 |
| Spec三件套 | spec.md/tasks.md/checklist.md | ✅ 已完成 |
| 复盘报告 | 本目录（README+execution+insight+export） | ✅ 已完成 |
| 原子提交 | d8fac263 + e17abac7 | ✅ 已完成 |

## 3. 后续行动项

### 高优先级

| 行动项 | 说明 | 验收标准 |
|--------|------|----------|
| 沉淀"第一性原理功能分析法"模式 | 将12章方法论SOP沉淀为可复用模式文件，放到methodology-patterns/research-knowledge/目录 | 模式文件包含：适用场景、四步法详细SOP、检查清单、反模式警告、示例引用 |

### 中优先级

| 行动项 | 说明 | 验收标准 |
|--------|------|----------|
| 更新分析类Spec模板 | 将"PRD摘要提炼"和"功能边界对比框架"纳入分析类任务的标准产出物 | tasks.md模板中增加摘要任务和边界定义任务；checklist.md中增加相关检查点 |
| 更新上下文恢复SOP | 增加"进度对齐检查"步骤（快速扫描最近2-3个task-output） | 在协作协议或工作流文档中增加session continuation后的标准检查流程 |
| 更新原子化工作流文档 | 明确"先完整写作→后原子化拆分"原则，在atomization相关SOP中说明两阶段分离的最佳实践 | atomization命令文档增加"写作与拆分分离"说明项 |

### 低优先级

| 行动项 | 说明 | 验收标准 |
|--------|------|----------|
| 补充"证据反向扫描"到第一性原理分析法 | 在质疑阶段增加"反效果功能扫描"子步骤 | 四步法SOP中包含"反向扫描"环节和四档评估框架（强支持/弱支持/无证据/不利影响） |

## 4. 模式沉淀成果汇总

| 模式 | 操作类型 | 优先级 | 说明 |
|------|----------|--------|------|
| 第一性原理功能分析法 | **新建** | 高 | 悬置→拆解→质疑→重构四步法SOP，含证据反向扫描 |
| 原子化"写作与拆分分离"原则 | 升级现有模式 | 中 | 在atomization工作流中明确两阶段分离 |
| 功能边界对比框架 | 升级PRD/功能定义模板 | 中 | 增加"不是什么"对比章节和多维度判定标准 |
| 上下文恢复进度对齐检查 | 升级协作协议 | 中 | session continuation后增加task-output快速扫描步骤 |
| PRD摘要作为标准产出物 | 升级分析类Spec模板 | 中 | 长篇分析报告后增加摘要提炼任务 |
| 子智能体任务委托边界指南 | 沉淀为经验 | 低 | 机械性任务委托vs深度推理主agent主导的判断标准 |
