# Tasks

> 主题：standards-tools（规范标准与工具链）
> 适用场景：编写规范文档、开发检查脚本、IDE 适配、CI/CD 配置

- [ ] Task 0: 需求分析与方案设计
  - [ ] SubTask 0.1: 明确规范要解决的具体问题或工具要检查的具体场景（写出 1-2 个具体的问题实例）
  - [ ] SubTask 0.2: 调研现有相关脚本/规范，避免重复建设（检查 .agents/scripts/、.agents/rules/）
  - [ ] SubTask 0.3: 设计规范标准/工具的输入输出与核心逻辑
  - [ ] SubTask 0.4: 确定异常情况处理策略（误报、漏报、边界条件、跨平台兼容）
  - [ ] SubTask 0.5: 确定脚本/工具的存放位置和命名
  - [ ] SubTask 0.6: 编写使用场景示例（作为后续测试用例基础）

- [ ] Task 1: 规范/工具核心实现
  - [ ] SubTask 1.1: 编写规范文档（放在 .agents/rules/ 或 docs/knowledge/ 下），包含：规则说明、正例反例、检测方法、例外处理
  - [ ] SubTask 1.2: 实现核心脚本/工具（放在 .agents/scripts/ 下），遵循现有脚本风格
  - [ ] SubTask 1.3: 脚本头部添加注释说明：用途、用法、参数、示例
  - [ ] SubTask 1.4: 支持命令行参数或配置项（如适用，使用 argparse 或类似库）
  - [ ] SubTask 1.5: 实现清晰的错误提示和帮助信息（`--help`）
  - [ ] SubTask 1.6: 处理跨平台路径问题（Windows 反斜杠/正斜杠兼容）
  - [ ] SubTask 1.7: 定义结构化日志格式（如适用）：统一前缀（如`[SG-LOG]`）+ 键值对 + JSON ctx，覆盖关键事件节点（进入/退出/检查/拦截/审批/异常）

- [ ] Task 2: 测试与验证
  - [ ] SubTask 2.1: 编写正向测试用例（符合规范/正确输入，确认工具不误报）
  - [ ] SubTask 2.2: 编写负向测试用例（违反规范/错误输入，确认工具能检测）
  - [ ] SubTask 2.3: 边界条件测试（空文件、特殊字符、超长行、跨平台路径、编码问题等）
  - [ ] SubTask 2.4: 在现有代码库/文档库上试运行，验证输出结果合理
  - [ ] SubTask 2.5: 记录试运行中发现的问题并修复
  - [ ] SubTask 2.6: 验证工具性能（大文件/大量文件时不会过慢）
  - [ ] SubTask 2.7: 验证结构化日志输出（如适用）：关键事件节点均有日志、格式符合`[前缀] event=EVENT_NAME k=v`规范、ctx JSON合法

- [ ] Task 3: 集成与文档
  - [ ] SubTask 3.1: 将工具加入 CI 检查流程或 pre-commit hook（如适用）
  - [ ] SubTask 3.2: 更新工具索引（.agents/scripts/README.md 或对应规则目录的 README）
  - [ ] SubTask 3.3: 在 AGENTS.md 工具规范索引中登记（如新增工具类型）
  - [ ] SubTask 3.4: 更新 check-spec-consistency 或其他相关工具的规则（如需要）
  - [ ] SubTask 3.5: 编写使用示例文档（在工具脚本注释中或对应 docs/ 下）
  - [ ] SubTask 3.6: 在对应主题 README.md 的执行看板中登记完成状态

# Task Dependencies

- Task 0 必须最先执行（工具/规范设计不当会导致大量返工）
- Task 1 依赖 Task 0 完成
- Task 2 依赖 Task 1 完成（可运行版本就位后才能测试）
- Task 3 依赖 Task 2 完成（测试通过后才能集成）
