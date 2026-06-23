# Tasks

- [x] Task 0: 初始化 Git 版本控制、目录重命名与 .gitignore 配置
  - [x] SubTask 0.1: 将 `d:\AI\libs\` 目录重命名为 `d:\AI\vendor\`（保留所有子文件与子目录结构）
  - [x] SubTask 0.2: 在项目根目录 `d:\AI\` 执行 `git init`（若 `.git` 目录不存在）
  - [x] SubTask 0.3: 创建 `.gitignore` 文件，添加完整忽略规则：`vendor/`、`.temp/`、`__pycache__/`、`*.pyc`、`.venv/`、`node_modules/`、`.env`、`*.log`、`.DS_Store`、`Thumbs.db`
  - [x] SubTask 0.4: 执行 `git status` 验证临时依赖目录被排除，其余文件正常显示为未跟踪
  - [x] SubTask 0.5: 检查并更新所有引用 `libs/` 旧路径的文件（当前仅 `.trae/specs/` 下规格文档），确保引用路径更新为 `vendor/`
  - [x] SubTask 0.6: 创建 `.agents/scripts/check-gitignore.py` 验证脚本，检查 `.gitignore` 规则覆盖所有临时依赖路径，并验证 `git status` 输出不含临时依赖文件
  - [x] SubTask 0.7: 创建 `.git/hooks/pre-commit` hook 脚本，检查暂存区是否包含临时依赖路径，若包含则阻止提交并提示错误

- [x] Task 1: 创建 AGENTS.md 全局契约文件
  - [x] SubTask 1.1: 编写全局核心规则（沟通语言、按需读取、上下文节省、Mermaid 优先）
  - [x] SubTask 1.2: 编写角色定义索引（5 个核心角色的路由表）
  - [x] SubTask 1.3: 编写能力边界声明（各角色 Non-Goals 概要）
  - [x] SubTask 1.4: 编写协作协议概要（交接、消息、冲突解决的路由入口）
  - [x] SubTask 1.5: 编写开发规范（代码风格、提交规范、文档边界）
  - [x] SubTask 1.6: 编写测试要求（单元测试、覆盖率、验收标准）
  - [x] SubTask 1.7: 编写上下文路由表（任务类型到规范文件的映射）

- [x] Task 2: 创建 .agents/ 目录骨架与 README.md
  - [x] SubTask 2.1: 创建 .agents/ 及子目录（roles/、prompts/、tools/、protocols/、workflows/、templates/）
  - [x] SubTask 2.2: 编写 .agents/README.md（目录结构树状图、子目录职责说明表、使用流程示例）

- [x] Task 3: 编写角色定义文件（.agents/roles/）
  - [x] SubTask 3.1: 编写 orchestrator.md（编排协调者：任务分配、流程协调、冲突仲裁）
  - [x] SubTask 3.2: 编写 architect.md（架构师：技术方案设计、架构决策、技术选型）
  - [x] SubTask 3.3: 编写 developer.md（开发者：代码实现、重构、缺陷修复）
  - [x] SubTask 3.4: 编写 reviewer.md（代码审查者：代码质量审查、规范校验、改进建议）
  - [x] SubTask 3.5: 编写 tester.md（测试工程师：测试用例编写、执行、覆盖率保障）
  - [x] SubTask 3.6: 编写 .agents/roles/README.md（角色索引与职责矩阵）

- [x] Task 4: 编写系统提示词与 Few-shot 示例（.agents/prompts/）
  - [x] SubTask 4.1: 编写 orchestrator/system-prompt.md 与 few-shot.md
  - [x] SubTask 4.2: 编写 architect/system-prompt.md 与 few-shot.md
  - [x] SubTask 4.3: 编写 developer/system-prompt.md 与 few-shot.md
  - [x] SubTask 4.4: 编写 reviewer/system-prompt.md 与 few-shot.md
  - [x] SubTask 4.5: 编写 tester/system-prompt.md 与 few-shot.md
  - [x] SubTask 4.6: 编写 .agents/prompts/README.md（提示词使用说明）

- [x] Task 5: 编写工具调用规范（.agents/tools/）
  - [x] SubTask 5.1: 编写 file-operations.md（文件读写、编辑、删除工具规范）
  - [x] SubTask 5.2: 编写 code-execution.md（命令执行、构建、测试工具规范）
  - [x] SubTask 5.3: 编写 search.md（代码搜索、文件查找、语义检索工具规范）
  - [x] SubTask 5.4: 编写 communication.md（消息发送、任务交接、状态同步工具规范）
  - [x] SubTask 5.5: 编写 .agents/tools/README.md（工具规范索引）

- [x] Task 6: 编写协作协议（.agents/protocols/）
  - [x] SubTask 6.1: 编写 handoff.md（任务交接协议：交接格式、字段定义、示例）
  - [x] SubTask 6.2: 编写 messaging.md（消息传递协议：消息格式、类型枚举、优先级）
  - [x] SubTask 6.3: 编写 conflict-resolution.md（冲突解决协议：升级路径、仲裁规则）
  - [x] SubTask 6.4: 编写 dependency-management.md（临时依赖管理流程：存放位置、使用规范、清理机制、禁止提交条款）
  - [x] SubTask 6.5: 编写 .agents/protocols/README.md（协议索引与使用流程）

- [x] Task 7: 编写标准工作流（.agents/workflows/）
  - [x] SubTask 7.1: 编写 feature-development.md（功能开发流程：Mermaid 流程图 + 角色参与）
  - [x] SubTask 7.2: 编写 code-review.md（代码审查流程：Mermaid 流程图 + 检查清单）
  - [x] SubTask 7.3: 编写 testing.md（测试流程：Mermaid 流程图 + 验收标准）
  - [x] SubTask 7.4: 编写 .agents/workflows/README.md（工作流索引）

- [x] Task 8: 编写模板资产（.agents/templates/）
  - [x] SubTask 8.1: 编写 task-template.md（任务模板：任务描述、验收标准、依赖项）
  - [x] SubTask 8.2: 编写 handoff-template.md（交接模板：任务上下文、已完成工作、待办事项、风险提示）
  - [x] SubTask 8.3: 编写 .agents/templates/README.md（模板使用说明）

# Task Dependencies

- Task 0 为前置任务，必须最先执行（确保 git 仓库初始化与 .gitignore 配置完成）
- Task 1、2 可在 Task 0 完成后并行
- Task 2 依赖 Task 1（AGENTS.md 引用 .agents/ 目录）
- Task 3、4、5、6、7、8 依赖 Task 2（需要目录骨架）
- Task 4 依赖 Task 3（提示词引用角色定义）
- Task 6 依赖 Task 3（协议引用角色）
- Task 7 依赖 Task 3、6（工作流引用角色与协议）
- Task 8 依赖 Task 6（交接模板引用交接协议）
- Task 3、5 可并行；Task 4、6 可并行（在 Task 3 完成后）
