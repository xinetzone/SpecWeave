# Tasks

- [x] Task 1：创建目录结构
  - [x] SubTask 1.1：在 `docs/retrospective/` 下创建 `templates/`、`patterns/code-patterns/`、`patterns/architecture-patterns/`、`patterns/methodology-patterns/`、`frameworks/`、`concepts/`、`reports/`、`assets/` 共 8 个子目录
  - [x] SubTask 1.2：验证所有目录已成功创建

- [x] Task 2：拆分可复用代码模式（5 个文件）
  - [x] SubTask 2.1：创建 `patterns/code-patterns/three-tier-check-tool.md`，提取三段式检查工具架构内容
  - [x] SubTask 2.2：创建 `patterns/code-patterns/context-aware-path-resolution.md`，提取上下文感知路径解析内容
  - [x] SubTask 2.3：创建 `patterns/code-patterns/meta-document-detection.md`，提取元文档识别内容
  - [x] SubTask 2.4：创建 `patterns/code-patterns/gitignore-validation.md`，提取 Git 忽略规则验证内容
  - [x] SubTask 2.5：创建 `patterns/code-patterns/regex-markdown-parsing.md`，提取正则驱动的 Markdown 解析内容

- [x] Task 3：拆分可复用架构模式（3 个文件）
  - [x] SubTask 3.1：创建 `patterns/architecture-patterns/perception-check-report-model.md`，提取感知→检查→报告三层模型内容
  - [x] SubTask 3.2：创建 `patterns/architecture-patterns/multi-agent-parallel-execution.md`，提取多智能体并行执行模式内容
  - [x] SubTask 3.3：创建 `patterns/architecture-patterns/incremental-regression-verification.md`，提取增量验证+回归验证双层策略内容

- [x] Task 4：拆分可复用方法论（2 个文件）
  - [x] SubTask 4.1：创建 `patterns/methodology-patterns/spec-driven-development.md`，提取 Spec-driven 开发流程内容
  - [x] SubTask 4.2：创建 `patterns/methodology-patterns/review-insight-export-loop.md`，提取复盘→洞察→导出知识闭环内容

- [x] Task 5：拆分可复用模板（4 个文件）
  - [x] SubTask 5.1：创建 `templates/spec-template.md`，提取 spec.md 模板内容
  - [x] SubTask 5.2：创建 `templates/tasks-template.md`，提取 tasks.md 模板内容
  - [x] SubTask 5.3：创建 `templates/checklist-template.md`，提取 checklist.md 模板内容
  - [x] SubTask 5.4：创建 `templates/retrospective-report-template.md`，提取复盘报告模板内容

- [x] Task 6：拆分可复用决策框架（4 个文件）
  - [x] SubTask 6.1：创建 `frameworks/directory-naming-matrix.md`，提取目录命名决策矩阵内容
  - [x] SubTask 6.2：创建 `frameworks/dependency-management-matrix.md`，提取临时依赖管理决策矩阵内容
  - [x] SubTask 6.3：创建 `frameworks/meta-document-processing-matrix.md`，提取元文档处理决策矩阵内容
  - [x] SubTask 6.4：创建 `frameworks/semantic-match-threshold-matrix.md`，提取语义匹配阈值决策矩阵内容

- [x] Task 7：拆分可复用知识概念（5 个文件）
  - [x] SubTask 7.1：创建 `concepts/meta-document.md`，提取元文档概念内容
  - [x] SubTask 7.2：创建 `concepts/context-awareness.md`，提取上下文感知概念内容
  - [x] SubTask 7.3：创建 `concepts/orthogonal-verification.md`，提取正交验证概念内容
  - [x] SubTask 7.4：创建 `concepts/zero-dependency-principle.md`，提取零依赖原则概念内容
  - [x] SubTask 7.5：创建 `concepts/semantic-prefix.md`，提取语义前缀概念内容

- [x] Task 8：拆分资产清单（1 个文件）
  - [x] SubTask 8.1：创建 `assets/asset-inventory.md`，提取资产清单与复用指南内容

- [x] Task 9：移动复盘报告至 reports/ 子目录
  - [x] SubTask 9.1：将 `retrospective-report-agents-spec-system.md` 移动至 `reports/` 子目录
  - [x] SubTask 9.2：将 `retrospective-report-check-spec-consistency.md` 移动至 `reports/` 子目录

- [x] Task 10：删除原 knowledge-extraction.md 文件
  - [x] SubTask 10.1：确认所有内容已迁移完毕后，删除 `docs/retrospective/knowledge-extraction.md`

- [x] Task 11：生成 README.md 目录索引
  - [x] SubTask 11.1：创建 `docs/retrospective/README.md`，包含完整的目录树结构
  - [x] SubTask 11.2：在 README.md 中为每个子目录和模块文件编写简要说明
  - [x] SubTask 11.3：在 README.md 中添加指向各子目录和关键文件的 Markdown 链接

- [x] Task 12：验证重构结果
  - [x] SubTask 12.1：确认所有 22 个文件均已创建，内容与原文件一致
  - [x] SubTask 12.2：确认所有文件名符合 kebab-case 命名规范
  - [x] SubTask 12.3：确认每个模块文件包含来源标注和关联模块标注
  - [x] SubTask 12.4：确认 README.md 中的链接均有效

# Task Dependencies

- Task 2-8 依赖于 Task 1（目录结构必须先创建）
- Task 2-8 之间无依赖关系，可并行执行
- Task 9 可与其他任务并行执行
- Task 10 依赖于 Task 2-8（所有内容迁移完成后才能删除原文件）
- Task 11 依赖于 Task 2-9（所有模块文件就位后才能编写索引）
- Task 12 依赖于 Task 1-11（所有任务完成后才能验证）