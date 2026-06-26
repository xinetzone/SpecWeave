# Tasks

- [x] Task 1: 创建 Spec 编写指南文档
  - [x] SubTask 1.1: 设计标准章节结构（Why、What Changes、Impact、ADDED/MODIFIED/REMOVED Requirements）
  - [x] SubTask 1.2: 定义必需元素与可选元素清单
  - [x] SubTask 1.3: 编写各类型元素的具体示例（Good/Bad 对比）
  - [x] SubTask 1.4: 制定命名规范与格式化要求
  - [x] SubTask 1.5: 在 `.agents/rules/spec-writing-guide.md` 创建完整文档

- [x] Task 2: 创建版本控制规范文档
  - [x] SubTask 2.1: 设计版本号命名规则（主版本号、次版本号定义）
  - [x] SubTask 2.2: 定义变更类型分类（added/modified/removed/deprecated）
  - [x] SubTask 2.3: 设计变更日志格式与记录规范
  - [x] SubTask 2.4: 制定弃用流程与迁移指南要求
  - [x] SubTask 2.5: 在 `.agents/rules/spec-version-control.md` 创建完整文档

- [x] Task 3: 开发 Spec 格式检查脚本
  - [x] SubTask 3.1: 实现 spec.md 核心章节检测器
  - [x] SubTask 3.2: 实现 Requirement 完整性验证器（含 Scenario 结构）
  - [x] SubTask 3.3: 实现验收标准可验证性检查器
  - [x] SubTask 3.4: 实现版本号与变更日志检测器
  - [x] SubTask 3.5: 实现命令行参数支持（--spec-dir, --format, --verbose）
  - [x] SubTask 3.6: 实现结构化输出（JSON/YAML/Text）与退出码
  - [x] SubTask 3.7: 在 `.agents/scripts/check-spec-format.py` 创建完整脚本

- [x] Task 4: 增强 check-spec-consistency.py 检查能力
  - [x] SubTask 4.1: 新增"区分度"检查（同一 spec 内 Requirement 名称唯一性）
  - [x] SubTask 4.2: 新增"清晰度"检查（Requirement 描述不包含重复关键词）
  - [x] SubTask 4.3: 新增"可执行性"检查（Scenario 包含 WHEN/THEN 结构）
  - [x] SubTask 4.4: 更新 `.agents/scripts/check-spec-consistency.py`

- [x] Task 5: 创建规范自验证
  - [x] SubTask 5.1: 为本规范文档添加版本号声明
  - [x] SubTask 5.2: 为本规范文档添加变更日志
  - [x] SubTask 5.3: 执行 check-spec-format.py 验证本规范文档结构
  - [x] SubTask 5.4: 执行 check-spec-consistency.py 验证本规范文档一致性

- [x] Task 6: 文档化与推广与落地验证
  - [x] SubTask 6.1: 在 `.agents/rules/README.md` 中添加 spec 编写指南与版本控制规范入口
  - [x] SubTask 6.2: 创建使用示例与最佳实践总结（已在 spec-writing-guide.md 中包含 Good/Bad 示例与模板）
  - [x] SubTask 6.3: 版本号规范落地验证（通过本 spec v1.1 的 TOML frontmatter 格式验证，检查脚本正确识别）
  - [x] SubTask 6.4: changelog 模板验证（通过本 spec v1.1 的成对标记格式验证，检查脚本正确识别倒序排列）
  - [x] SubTask 6.5: 格式检查脚本边界情况完善（章节标题双语兼容、Scenario WHEN/THEN 双格式兼容、版本号双格式兼容、Requirement 块边界修复、changelog 列表项前缀支持、模糊词汇去重、空章节"无"标记支持、REMOVED 章节 SHALL 豁免、changelog 时间倒序检查）

# Task Dependencies

- Task 1 和 Task 2 可并行执行（独立文档）
- Task 3 依赖 Task 1 的章节结构定义（需先确定标准章节名称）
- Task 4 依赖 Task 3 的部分实现（可复用部分检测逻辑）
- Task 5 必须在 Task 1、2、3、4 完成后执行（本规范需自验证）
- Task 6 必须在 Task 5 完成后执行
