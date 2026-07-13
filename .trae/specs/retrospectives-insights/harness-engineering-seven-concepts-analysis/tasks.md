# Harness Engineering 七概念分析 — Implementation Plan

## [ ] Task 1: 事实采集（R阶段）— 提取文章核心事实清单
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 从文章中提取≥20条客观事实，严格不含因果词（因为/所以/导致/错误/失误）
  - 事实涵盖：Harness定义、5个设计要点、技术对比、工程类比、学习路径等
  - 输出文件：`facts.md`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实清单≥20条
  - `programmatic` TR-1.2: 清单中不包含"因为/所以/导致/错误/失误"关键词
- **Notes**: 遵循七概念质量门G1

## [ ] Task 2: 洞察分析（I阶段）— 生成核心洞察四元组
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于事实清单，提取至少3条核心洞察
  - 每条洞察包含完整四元组：陈述/证据(Fxx)/反常识/下次行动
  - 输出文件：`insights.md`
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgment` TR-2.1: 每条洞察四元组完整，证据引用事实编号
  - `human-judgment` TR-2.2: 反常识点真实反直觉，非显而易见
- **Notes**: 遵循七概念质量门G2

## [ ] Task 3: 模式萃取（E阶段）— 沉淀可复用方法论模式
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 从洞察中萃取1-2个结构化可复用模式
  - 模式包含：触发场景/步骤/反模式/迁移验证/成熟度标注
  - 输出文件：模式文件存入 `docs/retrospective/patterns/methodology-patterns/governance-strategy/`
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgment` TR-3.1: 模式能迁移到≥1个非Harness领域场景
  - `human-judgment` TR-3.2: 配套≥1个反模式案例
- **Notes**: 遵循七概念质量门G3

## [ ] Task 4: 对抗审查（V阶段）— 验证模式与洞察
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 对洞察结论和模式文档执行对抗审查
  - 生成≥5条具体审查意见，至少采纳2条修正
  - 输出文件：`adversarial-review.md`
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgment` TR-4.1: 审查意见≥5条且具体
  - `human-judgment` TR-4.2: 至少采纳2条审查意见进行修正
- **Notes**: 遵循七概念V门质量标准

## [ ] Task 5: 原子提交（C阶段）— 模式入库与索引更新
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 将模式文件入库到正确目录
  - 更新模式库索引文件 `docs/retrospective/patterns/methodology-patterns/governance-strategy/README.md`
  - 修复交叉引用，验证链接有效性
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 模式文件存在于正确目录
  - `programmatic` TR-5.2: 索引文件包含新模式条目
  - `programmatic` TR-5.3: 所有本地链接验证通过（无断链）
- **Notes**: 遵循原子提交规范，单一职责提交

## [ ] Task 6: 复盘报告整合 — 生成完整分析报告
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 将事实清单、洞察、模式、审查意见整合成完整复盘报告
  - 输出文件：`retrospective-report.md`（存入 `docs/retrospective/reports/competitive-analysis/`）
- **Acceptance Criteria Addressed**: 无新增AC（整合性产出）
- **Test Requirements**:
  - `human-judgment` TR-6.1: 报告结构清晰，包含所有七概念阶段产出
  - `programmatic` TR-6.2: 报告内部链接完整
- **Notes**: 报告作为知识沉淀的完整记录
