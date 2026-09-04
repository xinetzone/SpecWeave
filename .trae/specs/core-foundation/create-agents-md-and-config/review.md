# Checklist

## Git 版本控制、目录重命名与 .gitignore 配置

- [x] 项目根目录 `d:\AI\` 下原 `libs/` 目录已重命名为 `vendor/`
- [x] `vendor/flexloop/` 目录结构完整，所有子文件与子目录已迁移
- [x] 项目根目录 `d:\AI\` 存在 `.git` 目录（git 仓库已初始化）
- [x] 项目根目录存在 `.gitignore` 文件
- [x] `.gitignore` 文件包含完整忽略规则：`vendor/`、`.temp/`、`__pycache__/`、`*.pyc`、`.venv/`、`node_modules/`、`.env`、`*.log`、`.DS_Store`、`Thumbs.db`
- [x] 执行 `git status` 时，临时依赖目录（`vendor/`、`.temp/`、`__pycache__/` 等）下的文件不出现在未跟踪文件列表中
- [x] 执行 `git status` 时，项目根目录下的其他文件和目录（如 `AGENTS.md`、`.agents/`、`.trae/`、`.gitignore` 等）正常显示为未跟踪或已跟踪状态
- [x] 所有引用旧路径 `libs/` 的文件已更新为 `vendor/`，无残留旧路径引用
- [x] 项目能正常访问 `vendor/flexloop/` 下的内容，无因路径变更导致的引用错误

## 临时依赖管理流程

- [x] `.agents/protocols/dependency-management.md` 文件存在
- [x] `dependency-management.md` 包含存放位置规范（`vendor/` 目录）
- [x] `dependency-management.md` 包含使用规范（按需引入、版本锁定）
- [x] `dependency-management.md` 包含清理机制（定期清理无用依赖）
- [x] `dependency-management.md` 包含禁止提交条款
- [x] AGENTS.md 开发规范章节包含禁止提交临时依赖的明确条款

## Git Hooks 自动化检查

- [x] `.git/hooks/pre-commit` hook 脚本存在
- [x] pre-commit hook 检查暂存区是否包含 `vendor/`、`.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等临时依赖路径
- [x] 当暂存区包含临时依赖时，pre-commit hook 阻止提交并输出错误提示
- [x] `.agents/scripts/check-gitignore.py` 验证脚本存在
- [x] 验证脚本检查 `.gitignore` 规则覆盖所有临时依赖路径
- [x] 验证脚本验证 `git status` 输出中不包含临时依赖文件
- [x] 执行验证脚本输出验证通过信息

## AGENTS.md 全局契约

- [x] AGENTS.md 文件存在于项目根目录 `d:\AI\AGENTS.md`
- [x] 包含全局核心规则（沟通语言、按需读取、上下文节省、Mermaid 优先）
- [x] 包含角色定义索引（5 个核心角色的路由表）
- [x] 包含能力边界声明（各角色 Non-Goals 概要）
- [x] 包含协作协议概要（交接、消息、冲突解决的路由入口）
- [x] 包含开发规范（代码风格、提交规范、文档边界）
- [x] 包含测试要求（单元测试、覆盖率、验收标准）
- [x] 包含上下文路由表（任务类型到规范文件的映射）

## .agents/ 目录骨架

- [x] `.agents/` 目录存在于项目根目录
- [x] 包含子目录：roles/、prompts/、tools/、protocols/、workflows/、templates/
- [x] `.agents/README.md` 包含目录结构树状图
- [x] `.agents/README.md` 包含各子目录职责说明表
- [x] `.agents/README.md` 包含从任务到执行的完整使用流程示例

## 角色定义（.agents/roles/）

- [x] `.agents/roles/orchestrator.md` 存在且包含 TOML frontmatter（id、domain、layer、bindings）
- [x] `.agents/roles/architect.md` 存在且包含 TOML frontmatter
- [x] `.agents/roles/developer.md` 存在且包含 TOML frontmatter
- [x] `.agents/roles/reviewer.md` 存在且包含 TOML frontmatter
- [x] `.agents/roles/tester.md` 存在且包含 TOML frontmatter
- [x] 每个角色文件包含 Description、Responsibilities、Non-Goals 三个章节
- [x] 任意两个角色的 Non-Goals 存在显式职责边界声明，避免重叠
- [x] `.agents/roles/README.md` 包含角色索引与职责矩阵

## 系统提示词与 Few-shot 示例（.agents/prompts/）

- [x] `.agents/prompts/orchestrator/system-prompt.md` 与 `few-shot.md` 存在
- [x] `.agents/prompts/architect/system-prompt.md` 与 `few-shot.md` 存在
- [x] `.agents/prompts/developer/system-prompt.md` 与 `few-shot.md` 存在
- [x] `.agents/prompts/reviewer/system-prompt.md` 与 `few-shot.md` 存在
- [x] `.agents/prompts/tester/system-prompt.md` 与 `few-shot.md` 存在
- [x] 每个系统提示词包含角色定位、能力描述、行为约束、输出格式要求四个部分
- [x] `.agents/prompts/README.md` 包含提示词使用说明

## 工具调用规范（.agents/tools/）

- [x] `.agents/tools/file-operations.md` 存在
- [x] `.agents/tools/code-execution.md` 存在
- [x] `.agents/tools/search.md` 存在
- [x] `.agents/tools/communication.md` 存在
- [x] 每个工具规范包含工具清单、输入参数 schema（表格）、输出格式、使用约束与示例
- [x] `.agents/tools/README.md` 包含工具规范索引

## 协作协议（.agents/protocols/）

- [x] `.agents/protocols/handoff.md` 存在且定义交接格式（任务上下文、已完成工作、待办事项、风险提示）
- [x] `.agents/protocols/messaging.md` 存在且定义消息格式（发送方、接收方、消息类型、内容、优先级）
- [x] `.agents/protocols/conflict-resolution.md` 存在且定义冲突解决路径（升级路径、仲裁规则）
- [x] `.agents/protocols/README.md` 包含协议索引与使用流程

## 标准工作流（.agents/workflows/）

- [x] `.agents/workflows/feature-development.md` 存在且包含至少 1 张 Mermaid 流程图
- [x] `.agents/workflows/code-review.md` 存在且包含至少 1 张 Mermaid 流程图
- [x] `.agents/workflows/testing.md` 存在且包含至少 1 张 Mermaid 流程图
- [x] 每个工作流展示步骤流转与角色参与
- [x] `.agents/workflows/README.md` 包含工作流索引

## 模板资产（.agents/templates/）

- [x] `.agents/templates/task-template.md` 存在且包含任务描述、验收标准、依赖项字段
- [x] `.agents/templates/handoff-template.md` 存在且包含任务上下文、已完成工作、待办事项、风险提示字段
- [x] `.agents/templates/README.md` 包含模板使用说明

## 多智能体协作支持

- [x] 角色定义间存在显式职责边界声明（Non-Goals 互斥）
- [x] 消息传递协议定义了完整的消息格式与类型枚举
- [x] 任务交接协议定义了完整的交接格式与字段
- [x] 工作流展示了多角色参与的步骤流转
- [x] AGENTS.md 路由表覆盖所有任务类型到对应规范文件的映射
