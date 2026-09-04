# Checklist

## 规范文档结构验证

- [x] spec.md 包含 Why 章节
- [x] spec.md 包含 What Changes 章节
- [x] spec.md 包含 Impact 章节
- [x] spec.md 包含 ADDED Requirements 章节
- [x] spec.md 包含 MODIFIED Requirements 章节
- [x] spec.md 包含 REMOVED Requirements 章节
- [x] spec.md 包含版本号声明
- [x] spec.md 包含变更日志

## 编写指南文档验证

- [x] `.agents/rules/spec-writing-guide.md` 存在
- [x] 包含标准章节结构定义
- [x] 包含必需元素清单
- [x] 包含 Good/Bad 示例
- [x] 包含命名规范
- [x] 包含格式化要求

## 版本控制规范文档验证

- [x] `.agents/rules/spec-version-control.md` 存在
- [x] 包含版本号命名规则
- [x] 包含变更类型分类
- [x] 包含变更日志格式
- [x] 包含弃用流程

## 格式检查脚本验证

- [x] `.agents/scripts/check-spec-format.py` 存在
- [x] 支持核心章节检测
- [x] 支持 Requirement 完整性验证
- [x] 支持 Scenario 结构验证
- [x] 支持版本号与变更日志检测
- [x] 支持命令行参数
- [x] 支持结构化输出

## 一致性检查增强验证

- [x] check-spec-consistency.py 支持区分度检查
- [x] check-spec-consistency.py 支持清晰度检查
- [x] check-spec-consistency.py 支持可执行性检查

## Task 6: 文档化与推广与落地验证

- [x] SubTask 6.1: 在 `.agents/rules/README.md` 中添加 spec 编写指南与版本控制规范入口
- [x] SubTask 6.2: 创建使用示例与最佳实践总结（已在 spec-writing-guide.md 中包含）
- [x] SubTask 6.3: 版本号规范落地验证（TOML frontmatter 格式，check-spec-format.py 可识别）
- [x] SubTask 6.4: changelog 模板验证（成对标记格式 + 时间倒序检查，全 spec 验证通过）
- [x] SubTask 6.5: 格式检查脚本边界情况完善（双语标题、双格式 WHEN/THEN、版本号双格式、Requirement块边界、列表项前缀、模糊词汇去重、空章节"无"标记、REMOVED SHALL 豁免、changelog时间倒序）
- [x] SubTask 6.6: 编写指南与实际项目格式对齐（推荐纯英文章节标题、`- **WHEN**`/`- **THEN**` 列表项加粗格式、更新模板）
- [x] SubTask 6.7: 全项目 spec 检查通过（所有 `.trae/specs/` 下 spec 文件均通过格式检查，评分 97-100 分）
