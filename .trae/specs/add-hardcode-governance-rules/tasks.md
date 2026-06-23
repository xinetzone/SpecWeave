# Tasks

- [x] Task 1: 创建 `rules/` 目录与 README 索引文档
  - [x] SubTask 1.1: 创建 `.agents/rules/` 目录
  - [x] SubTask 1.2: 编写 `README.md`，包含规则体系 Mermaid 架构图、各文档链接与简介、按场景和角色分类的快速导航表、不同角色的使用指南

- [x] Task 2: 编写硬编码识别标准文档
  - [x] SubTask 2.1: 编写 `.agents/rules/identification-standards.md`
  - [x] SubTask 2.2: 为 8 大类硬编码（固定字符串、数值、路径、URL/端点、编码值、正则模式、颜色/样式、配置参数）分别提供定义、正例、反例与检测要点
  - [x] SubTask 2.3: 编写"硬编码 vs 合理常量"的区分标准，附带边界情况判断流程图（Mermaid）

- [x] Task 3: 编写允许场景与审批流程文档
  - [x] SubTask 3.1: 编写 `.agents/rules/allowable-scenarios.md`
  - [x] SubTask 3.2: 列出允许硬编码的 4 类场景（数学/物理常量、协议标准固定值、单次临时值、性能关键路径），每类附带边界条件与使用限制
  - [x] SubTask 3.3: 编写例外审批流程（Mermaid 流程图），定义 `HARDCODE-EXCEPTION:` 标记格式、reviewer/architect/orchestrator 角色职责、有效期要求
  - [x] SubTask 3.4: 设计例外清单模板

- [x] Task 4: 编写替代方案指南文档
  - [x] SubTask 4.1: 编写 `.agents/rules/alternatives-guide.md`
  - [x] SubTask 4.2: 制作硬编码类型 → 替代方案的完整映射表
  - [x] SubTask 4.3: 为每种替代方案（配置文件管理、环境变量、常量定义、枚举、资源文件、i18n、设计令牌）编写具体代码示例与实施步骤
  - [x] SubTask 4.4: 提供可复制的模板/脚手架代码片段

- [x] Task 5: 编写检测与报告机制文档
  - [x] SubTask 5.1: 编写 `.agents/rules/detection-and-reporting.md`
  - [x] SubTask 5.2: 定义三层检测体系（自动化扫描、人工审查、定期报告）的详细规范
  - [x] SubTask 5.3: 定义检测结果分级标准（ERROR/WARNING/INFO）与对应的处理策略
  - [x] SubTask 5.4: 定义定期报告的格式模板、数据来源与生成方式

- [x] Task 6: 编写执行与验证规则文档
  - [x] SubTask 6.1: 编写 `.agents/rules/enforcement-guidelines.md`
  - [x] SubTask 6.2: 定义每条规则的"触发条件 → 执行步骤 → 衡量标准"三段式结构
  - [x] SubTask 6.3: 制定验证手段（自动化脚本、检查点清单、基准对比）的具体规范

- [x] Task 7: 更新 AGENTS.md 路由表
  - [x] SubTask 7.1: 在 AGENTS.md 的"协议概要"表格之后新增"规则体系索引"章节
  - [x] SubTask 7.2: 在 AGENTS.md 的"上下文路由表"中新增 `rules/` 相关条目

# Task Dependencies

- [Task 2]、[Task 3]、[Task 4]、[Task 5]、[Task 6] 可并行执行（各文档独立编写）
- [Task 1] 的 SubTask 1.1 是所有文档的前置条件（需先创建目录），SubTask 1.2 依赖于 [Task 2] 至 [Task 6] 完成（需汇总各文档信息）
- [Task 7] 依赖于 [Task 1] 至 [Task 6] 全部完成（需最终确定所有文档文件名与用途）
