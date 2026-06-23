# Tasks

- [x] Task 1: 扫描 prompt_extraction/ 核心业务模块硬编码问题
  - [x] SubTask 1.1: 扫描 `prompt_extraction/config.py` 中的配置常量与阈值
  - [x] SubTask 1.2: 扫描 `prompt_extraction/assessment/evaluator.py` 中的评分常量、词汇表、阈值
  - [x] SubTask 1.3: 扫描 `prompt_extraction/optimization/optimizer.py` 中的歧义映射表、输出格式文本
  - [x] SubTask 1.4: 扫描 `prompt_extraction/extraction/extractor.py` 中的关键词列表、类型映射表
  - [x] SubTask 1.5: 扫描 `prompt_extraction/input/parser.py` 与 `input_handler.py` 中的格式映射、编码、ID 长度
  - [x] SubTask 1.6: 扫描 `prompt_extraction/preprocessing/cleaner.py` 与 `normalizer.py` 中的正则模式、Unicode 码点、标点映射
  - [x] SubTask 1.7: 扫描 `prompt_extraction/pipeline.py` 中的 CSV 列名、编码常量
  - [x] SubTask 1.8: 扫描 `prompt_extraction/ui/app.py` 中的页面配置、UI 文本、截断长度
  - [x] SubTask 1.9: 扫描 `prompt_extraction/ui/components/` 下 4 个组件文件中的颜色映射、CSS 样式、图表配置

- [x] Task 2: 扫描 .agents/scripts/ 智能体脚本硬编码问题
  - [x] SubTask 2.1: 扫描 `check-gitignore.py` 中的规则列表、临时路径列表
  - [x] SubTask 2.2: 扫描 `check-links.py` 中的排除目录、超时、并发数、User-Agent
  - [x] SubTask 2.3: 扫描 `check-source-traceability.py` 中的排除目录、正则模式
  - [x] SubTask 2.4: 扫描 `check-spec-consistency.py` 中的 ANSI 颜色、路径前缀、元文档关键词、匹配阈值
  - [x] SubTask 2.5: 扫描 `check-role-permissions.py` 中的合法 tier 值、排除文件
  - [x] SubTask 2.6: 扫描 `check-move.py` 中的排除目录、正则模式
  - [x] SubTask 2.7: 扫描 `generate-nav.py` 中的扫描目录、根文件、目标配置、手动描述表

- [x] Task 3: 扫描 docs/knowledge/scripts/ 知识库脚本硬编码问题
  - [x] SubTask 3.1: 扫描 `generate_index.py` 中的排除文件、默认元数据、描述截断长度、路径常量

- [x] Task 4: 建立结构化硬编码问题清单
  - [x] SubTask 4.1: 按类别归类所有识别出的硬编码问题（业务常量/配置参数/路径/错误信息/UI 文本/第三方服务地址/数据库相关/其他）
  - [x] SubTask 4.2: 为每个问题项标注位置（文件:行号）、类型、内容摘要
  - [x] SubTask 4.3: 标注每个问题的风险等级（高/中/低），考虑修改频率、影响范围、潜在风险

- [x] Task 5: 执行影响分析
  - [x] SubTask 5.1: 分析代码可维护性影响（修改难度、查找复杂度）
  - [x] SubTask 5.2: 分析可扩展性影响（功能扩展限制、多环境适配问题）
  - [x] SubTask 5.3: 分析可配置性影响（动态调整能力、部署灵活性）
  - [x] SubTask 5.4: 分析国际化支持影响（多语言适配障碍）
  - [x] SubTask 5.5: 分析安全性影响（敏感信息暴露风险）

- [x] Task 6: 制定分类型重构方案
  - [x] SubTask 6.1: 为业务常量类硬编码制定重构方案（常量类/枚举定义）
  - [x] SubTask 6.2: 为配置参数类硬编码制定重构方案（配置文件管理/环境变量注入）
  - [x] SubTask 6.3: 为路径类硬编码制定重构方案（路径常量集中管理）
  - [x] SubTask 6.4: 为错误信息类硬编码制定重构方案（资源文件/消息字典）
  - [x] SubTask 6.5: 为 UI 文本类硬编码制定重构方案（国际化资源文件）
  - [x] SubTask 6.6: 为正则模式、Unicode 码点、CSS 样式等其他类型制定重构方案
  - [x] SubTask 6.7: 为每个重构方案标注实施优先级（P0/P1/P2）

- [x] Task 7: 制定预防措施与编码规范
  - [x] SubTask 7.1: 建立明确的编码规范，规定不同类型值的正确存储方式
  - [x] SubTask 7.2: 设计代码审查机制，将硬编码检查纳入常规审查项
  - [x] SubTask 7.3: 提出静态代码分析工具引入建议（如 ruff、bandit、semgrep 自定义规则）

- [x] Task 8: 制定后续改进计划与时间表
  - [x] SubTask 8.1: 按优先级排序重构任务，制定分阶段实施计划
  - [x] SubTask 8.2: 标注每阶段任务的依赖关系与并行可能性
  - [x] SubTask 8.3: 制定验证标准（确保重构后功能等价、测试通过）

- [x] Task 9: 产出完整复盘文档
  - [x] SubTask 9.1: 整合所有分析结果，生成完整的硬编码问题复盘文档
  - [x] SubTask 9.2: 确保文档具备可操作性，便于团队后续实施重构工作

# Task Dependencies

- [Task 4] 依赖于 [Task 1]、[Task 2]、[Task 3]（需先完成扫描才能建立清单）
- [Task 5] 依赖于 [Task 4]（需先有清单才能执行影响分析）
- [Task 6] 依赖于 [Task 5]（需先有影响分析才能制定重构方案）
- [Task 7] 依赖于 [Task 6]（需先有重构方案才能制定预防措施）
- [Task 8] 依赖于 [Task 6]、[Task 7]（需先有方案与预防措施才能制定计划）
- [Task 9] 依赖于 [Task 1] 至 [Task 8] 全部完成
- [Task 1]、[Task 2]、[Task 3] 可并行执行
