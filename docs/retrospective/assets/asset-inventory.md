> **来源**：从 `docs/retrospective/knowledge-extraction.md` 七、资产清单与复用指南 拆分

# 资产清单与复用指南

## 可直接复用的文件

| 文件 | 复用方式 | 适配工作量 |
|------|---------|-----------|
| `check-gitignore.py` | 修改 `REQUIRED_RULES` 和 `TEMP_PATHS` 列表 | 低（5 分钟） |
| `check-spec-consistency.py` | 修改正则模式适配不同文档格式 | 中（30 分钟） |
| `dependency-management.md` | 直接引用或按需裁剪 | 低（5 分钟） |
| `app-development-workflow.md` | 修改应用类型与门禁条件，复用三阶段结构 | 中（30 分钟） |
| `handoff.md`（交接协议） | 直接采用 YAML 格式与交接流程 | 低（5 分钟） |
| `task-template.md` | 直接使用 | 零 |
| `handoff-template.md` | 直接使用 | 零 |
| `directory-readme-template.md` | 填充目录树和模块说明 | 低（5 分钟） |
| 复盘报告模板（3.2 节） | 填充项目数据 | 中（1 小时） |
| `retrospective-report-system-planning.md` | 直接引用增量式需求扩展与四层闭环架构洞察 | 低（5 分钟） |
| `check-action-items.py` | 修改扫描目录路径，直接运行 | 零 |

## 需实例化后复用的模式

| 模式 | 实例化方式 | 典型产出 |
|------|-----------|---------|
| 三段式检查工具架构 | 填充解析器 + 检查逻辑 | 新的验证脚本 |
| 感知→检查→报告模型 | 定义感知维度 + 检查规则 | 领域特定检查工具 |
| Spec-driven 开发流程 | 编写 spec/tasks/checklist | 新项目的规格文档 |
| 复盘→洞察→导出闭环 | 按模板填充数据 | 项目复盘报告 |
| 文档体系原子化重构方法论 | 执行内容审计→原子化拆分→模块化归类→索引生成 | 模块化文档体系 |
| 事实表述一致性闭环 | 执行问题识别→方向确认→增量修正→全局搜索→边界判定 | 一致的文档表述 |
| 正交验证策略 | 应用于多优化迭代 | 验证计划 |
| 功能模块设计五要素标准结构 | 填充技术架构+关键实现步骤+资源需求+时间节点+预期成果指标 | 功能模块规划文档 |
| 四层闭环架构（感知→认知→执行→治理） | 将功能模块按四层归类，建立数据流闭环 | 自我治理系统设计 |
| 双区开发模型（.temp/ → apps/ 迁移） | 定义非正式区路径、正式区路径、质量门禁条件 | 新实体的开发工作流规范 |
| 生命周期协议三阶段结构 | 填充三阶段的进入条件、执行规范、退出标准、门禁条件 | 生命周期管理协议文档 |
| 目录创建"三件套"模式（目录+README+规范+索引同步） | 填充目录内容与规范定义 | 新顶级目录的完整交付物 |
| 短指令模式库 | 填充新经验证的指令模式 | 指令模式参考文档 |

## 需按场景适配的决策框架

| 框架 | 适配方式 | 产出 |
|------|---------|------|
| 目录命名决策矩阵 | 填充项目自身的目录结构 | 项目目录规范 |
| 临时依赖管理决策矩阵 | 调整文件类型和存放位置 | 项目依赖管理规范 |
| 元文档处理决策矩阵 | 扩展元文档类型和关键词 | 文档检查配置 |
| 语义匹配阈值决策矩阵 | 按项目语言和场景调整 | 检查工具配置 |

## 项目复盘报告索引

| 报告 | 关联项目 | 关键洞察 |
|------|---------|---------|
| `retrospective-report-create-apps-directory.md` | apps/ 应用开发工作空间创建 | 双区开发模型、生命周期协议三阶段结构、目录创建三件套模式 |
| `insight-report-create-apps-directory-meta.md` | 单项目全流程协作元洞察 | 拒批精度决定修订成本、四阶段闭环从报告到执行流、自举式知识增长、零延迟行动、短指令低摩擦协作 |
| `retrospective-report-teams-module.md` | 团队管理模块创建 | 约定驱动创建、规范层纵深防御、自举规范 |
| `retrospective-report-cofounder-improvement-execution.md` | 联合创始改进建议执行 | 声明即校验模式、知识形态三阶跃迁 |
| `meta-analysis-cross-project.md` | 跨项目元分析 | 高频模式、顽固问题、演化趋势、资产增长率 |

> **关联模块**：
> - `patterns/code-patterns/three-tier-check-tool.md`
> - `patterns/architecture-patterns/perception-check-report-model.md`
> - `patterns/architecture-patterns/lifecycle-protocol-three-phase.md`
> - `patterns/methodology-patterns/spec-driven-development.md`
> - `patterns/methodology-patterns/review-insight-export-loop.md`
> - `patterns/methodology-patterns/document-system-refactoring.md`
> - `patterns/methodology-patterns/fact-statement-consistency-loop.md`
> - `patterns/methodology-patterns/dual-zone-development-model.md`
> - `templates/directory-readme-template.md`
> - `frameworks/directory-naming-matrix.md`
> - `frameworks/dependency-management-matrix.md`
> - `frameworks/meta-document-processing-matrix.md`
> - `frameworks/semantic-match-threshold-matrix.md`
> - `reports/retrospective-report-create-apps-directory.md`
> - `reports/retrospective-report-teams-module.md`
> - `reports/retrospective-report-cofounder-improvement-execution.md`
> - `concepts/pattern-maturity-levels.md`
> - `patterns/methodology-patterns/short-command-patterns.md`
> - `reports/meta-analysis-cross-project.md`
