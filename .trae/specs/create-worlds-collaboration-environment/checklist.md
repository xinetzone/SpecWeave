# Checklist

## 目录结构验证

- [ ] `.agents/worlds/` 目录存在
- [ ] `.agents/worlds/README.md` 文件存在且内容完整
- [ ] `.agents/worlds/collaboration/` 子目录存在
- [ ] `.agents/worlds/collaboration/README.md` 文件存在
- [ ] `.agents/worlds/collaboration/permissions.md` 文件存在
- [ ] `.agents/worlds/collaboration/collaborative-editing.md` 文件存在
- [ ] `.agents/worlds/collaboration/change-tracking.md` 文件存在
- [ ] `.agents/worlds/collaboration/version-control.md` 文件存在
- [ ] `.agents/worlds/environments/` 子目录存在
- [ ] `.agents/worlds/environments/README.md` 文件存在
- [ ] `.agents/worlds/environments/multi-environment.md` 文件存在
- [ ] `.agents/worlds/environments/variables.md` 文件存在
- [ ] `.agents/worlds/environments/resource-isolation.md` 文件存在
- [ ] `.agents/worlds/environments/status-monitoring.md` 文件存在

## worlds/README.md 内容验证

- [ ] 包含目录说明（worlds/ 的定位与职责）
- [ ] 包含目录结构图（ASCII 树形图）
- [ ] 包含各子模块职责矩阵（表格形式）
- [ ] 包含核心概念关系图（Mermaid 流程图）
- [ ] 包含使用流程示例（Mermaid 或步骤列表）
- [ ] 包含与其他模块的关系表（teams/、protocols/、workflows/、tools/）
- [ ] 包含使用约束（权限前置、操作留痕、最小权限等）

## collaboration/ 模块内容验证

- [ ] `README.md` 包含模块索引与职责矩阵
- [ ] `permissions.md` 定义 RBAC 扩展模型，与 `teams/permission-system.md` 的 L1/L2/L3 分级衔接
- [ ] `permissions.md` 定义权限分配与回收流程，要求操作留痕
- [ ] `collaborative-editing.md` 定义锁机制或乐观并发控制策略
- [ ] `collaborative-editing.md` 引用 `protocols/conflict-resolution.md` 的冲突仲裁规则
- [ ] `collaborative-editing.md` 定义回滚策略，支持回滚至任意历史版本
- [ ] `change-tracking.md` 定义审计日志格式（操作者、时间戳、操作类型、目标资源、变更前后内容）
- [ ] `change-tracking.md` 声明审计日志不可篡改，支持按时间、操作者、资源类型检索
- [ ] `version-control.md` 定义 Git 工作流（分支、合并、标签）
- [ ] `version-control.md` 要求提交信息遵循 Conventional Commits 规范
- [ ] `version-control.md` 支持基于标签的环境快照（如 `env/dev-v1.0`）

## environments/ 模块内容验证

- [ ] `README.md` 包含模块索引与职责矩阵
- [ ] `multi-environment.md` 定义 dev/test/prod 三种环境的配置规范
- [ ] `multi-environment.md` 定义环境切换的权限校验（生产环境需 L3 特权验证）
- [ ] `multi-environment.md` 要求环境切换记录审计日志
- [ ] `variables.md` 定义集中式环境变量存储机制
- [ ] `variables.md` 定义敏感变量加密存储与解密权限
- [ ] `variables.md` 遵循最小暴露原则，仅注入当前任务所需变量
- [ ] `resource-isolation.md` 定义命名空间、配额、网络隔离机制
- [ ] `resource-isolation.md` 支持按环境配置资源上限（CPU、内存、存储）
- [ ] `status-monitoring.md` 定义健康指标采集（可用性、资源利用率、错误率）
- [ ] `status-monitoring.md` 定义告警机制与可配置告警渠道
- [ ] `status-monitoring.md` 定义监控数据保留周期与历史趋势查询

## 索引同步验证

- [ ] `.agents/README.md` 的目录结构图新增 `worlds/` 条目
- [ ] `.agents/README.md` 的职责说明表新增 `worlds/` 行
- [ ] `.agents/README.md` 的使用流程示例体现 `worlds/` 的协作与环境管理场景
- [ ] `AGENTS.md` 的上下文路由表新增 `worlds/` 入口（团队协作执行、环境管理）

## 一致性与链接验证

- [ ] 运行 `check-links.py` 验证所有新增文档的本地链接有效（退出码为 0）
- [ ] 运行 `check-spec-consistency.py` 验证 spec 一致性（无新增错误）
- [ ] 新增文档中引用的 `teams/permission-system.md`、`protocols/conflict-resolution.md` 等路径正确
- [ ] 所有 Markdown 文档遵循项目既有风格（TOML frontmatter 可选、Mermaid 优先、中文为主）

## 架构规范符合性验证

- [ ] `worlds/` 目录设计与 `.agents/` 既有目录结构风格一致
- [ ] `worlds/` 的职责与 `teams/`（组织治理）清晰区分，无重叠
- [ ] `worlds/` 的协作机制引用 `protocols/` 中已有协议，不重复定义
- [ ] `worlds/` 的环境管理与 `workflows/` 的标准工作流衔接合理
- [ ] 所有新增文档使用中文为主，符合 AGENTS.md 全局核心规则
