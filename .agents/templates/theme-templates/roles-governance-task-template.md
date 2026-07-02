---
id: "templates-theme-templates-roles-governance-task-template"
title: "Tasks"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/theme-templates/roles-governance-task-template.toml"
---
# Tasks

> 主题：roles-governance（角色与治理体系）
> 适用场景：新增角色、添加治理规则、同步索引、角色权限管理

- [ ] Task 0: 前置依赖与影响分析
  - [ ] SubTask 0.1: 确认核心角色体系（create-agents-md-and-config）已完成
  - [ ] SubTask 0.2: 分析新增/修改内容对现有角色/规则的影响范围
  - [ ] SubTask 0.3: 检查是否存在职责重叠或权限冲突
  - [ ] SubTask 0.4: 识别需要同步更新的索引文件清单（AGENTS.md、.agents/roles/README.md、.agents/rules/README.md 等）
  - [ ] SubTask 0.5: 确认新增角色/规则的命名和定位与现有体系一致

- [ ] Task 1: 角色/规则定义文件编写
  - [ ] SubTask 1.1: 在 .agents/roles/ 或 .agents/rules/ 下创建定义文件
  - [ ] SubTask 1.2: 编写职责说明（Goals）：该角色/规则的核心目标
  - [ ] SubTask 1.3: 编写能力边界（Non-Goals）：明确不做什么，避免职责蔓延
  - [ ] SubTask 1.4: 定义与其他角色的协作关系/规则适用范围
  - [ ] SubTask 1.5: 编写系统提示词（如新增角色），参照现有提示词风格
  - [ ] SubTask 1.6: 编写 Few-shot 示例（如新增角色，参照 few-shot.md 格式）
  - [ ] SubTask 1.7: 如为治理规则，补充：识别标准、正例/反例、检测方法、执行流程
  - [ ] SubTask 1.8: 如规则涉及流程管控（如阶段守卫、审批拦截），定义结构化日志格式：统一前缀（如`[SG-LOG]`/`[PDR-LOG]`）+ 关键事件（进入/退出/检查/拦截/审批/异常）+ JSON ctx

- [ ] Task 2: 索引与入口同步
  - [ ] SubTask 2.1: 更新 AGENTS.md 角色定义索引表/规则体系索引表
  - [ ] SubTask 2.2: 更新对应子目录的 README.md（如 .agents/roles/README.md）
  - [ ] SubTask 2.3: 在 AGENTS.md 上下文路由表中添加新条目（如需要）
  - [ ] SubTask 2.4: 如有需要，更新协作场景文档（collaboration-scenarios.md）
  - [ ] SubTask 2.5: 如有需要，更新能力边界声明

- [ ] Task 3: 验证
  - [ ] SubTask 3.1: 运行 check-role-permissions.py 验证角色权限配置（如适用）
  - [ ] SubTask 3.2: 确认 AGENTS.md 路由表与实际文件结构一致
  - [ ] SubTask 3.3: 运行 check-links.py 验证所有链接正确
  - [ ] SubTask 3.4: 验证新增系统提示词与现有角色提示词风格一致
  - [ ] SubTask 3.5: 验证治理规则与现有规则无矛盾
  - [ ] SubTask 3.6: 如涉及流程管控规则，确认相关角色system-prompt包含结构化日志输出要求（事件类型、格式、合规红线）
  - [ ] SubTask 3.7: 在对应主题 README.md 的执行看板中登记完成状态

# Task Dependencies

- Task 0 必须最先执行（影响分析是后续工作的基础）
- Task 1 依赖 Task 0 完成
- Task 2 依赖 Task 1 完成（需要定义文件就位才能更新索引）
- Task 3 依赖 Task 1、2 完成
