# Tasks

- [x] Task 1: 创建 worlds/ 目录结构与 README.md 索引
  - [x] SubTask 1.1: 创建 `.agents/worlds/` 目录及 `collaboration/`、`environments/` 子目录
  - [x] SubTask 1.2: 编写 `worlds/README.md`，包含目录说明、结构图、职责矩阵、Mermaid 关系图、使用流程、与其他模块关系、使用约束
- [x] Task 2: 编写团队协作支持规范（collaboration/）
  - [x] SubTask 2.1: 编写 `collaboration/README.md` 模块索引
  - [x] SubTask 2.2: 编写 `permissions.md`，定义多用户权限管理（RBAC 扩展、与 teams/permission-system.md 衔接、权限分配与回收、操作留痕）
  - [x] SubTask 2.3: 编写 `collaborative-editing.md`，定义协作编辑机制（锁机制、乐观并发控制、冲突解决、回滚策略）
  - [x] SubTask 2.4: 编写 `change-tracking.md`，定义变更追踪（审计日志格式、不可篡改、检索维度、保留策略）
  - [x] SubTask 2.5: 编写 `version-control.md`，定义版本控制集成（Git 工作流、分支策略、标签管理、Conventional Commits 规范）
- [x] Task 3: 编写环境管理规范（environments/）
  - [x] SubTask 3.1: 编写 `environments/README.md` 模块索引
  - [x] SubTask 3.2: 编写 `multi-environment.md`，定义多环境配置与切换（dev/test/prod 配置、切换权限校验、审计日志）
  - [x] SubTask 3.3: 编写 `variables.md`，定义环境变量管理（集中存储、加密机制、注入策略、最小暴露原则）
  - [x] SubTask 3.4: 编写 `resource-isolation.md`，定义资源隔离（命名空间、配额、网络隔离、资源上限）
  - [x] SubTask 3.5: 编写 `status-monitoring.md`，定义环境状态监控（健康指标、告警机制、数据保留、趋势查询）
- [x] Task 4: 同步更新 .agents/README.md 与 AGENTS.md
  - [x] SubTask 4.1: 在 `.agents/README.md` 的目录结构、职责说明表、使用流程中新增 `worlds/` 条目
  - [x] SubTask 4.2: 在 `AGENTS.md` 的上下文路由表中新增 `worlds/` 入口
- [x] Task 5: 验证文档完整性与一致性
  - [x] SubTask 5.1: 运行 `check-links.py` 验证所有新增文档的本地链接有效性
  - [x] SubTask 5.2: 运行 `check-spec-consistency.py` 验证 spec 一致性
  - [x] SubTask 5.3: 人工审查 worlds/ 目录结构与文档内容是否符合 spec 要求

# Task Dependencies

- [Task 2] 依赖于 [Task 1]（需要先建立目录结构）
- [Task 3] 依赖于 [Task 1]（需要先建立目录结构）
- [Task 2] 与 [Task 3] 可并行执行（无相互依赖）
- [Task 4] 依赖于 [Task 1]、[Task 2]、[Task 3]（需要 worlds/ 目录与文档全部就绪后同步更新索引）
- [Task 5] 依赖于 [Task 4]（需要所有文档与索引更新完成后进行验证）
