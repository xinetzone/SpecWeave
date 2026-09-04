---
version: 1.0
date: 2026-07-09
---

# Best-Practices 目录断链修复与入口文档建设 - Verification Checklist

## 扫描与识别
- [ ] 已扫描 docs/knowledge/best-practices/ 下所有 11 个 .md 文件
- [ ] Grep 搜索覆盖了 Markdown 链接格式 `[text](path)`
- [ ] Grep 搜索覆盖了 YAML frontmatter 中的 source/related_retrospective 字段
- [ ] Grep 搜索覆盖了正文中的路径提及（非链接格式但包含 retrospective 的路径）
- [ ] 每个引用都已验证目标文件是否存在
- [ ] 已区分"路径深度错误"、"目标不存在"、"frontmatter过期"、"有效引用"四类
- [ ] 扫描结果以表格形式记录，包含文件:行号、当前路径、问题类型

## 断链修复
- [ ] b2b-product-info-collection-sop.md 的 `../retrospective/` 路径深度已修正为 `../../retrospective/`
- [ ] cli-setup-in-agent-environment.md 中所有 retrospective 链接已验证（reports/ 和 patterns/ 路径）
- [ ] concurrent-code-safety-review.md 的洞察来源链接已验证
- [ ] eight-dimensions-concurrent-safety-spec.md 的 frontmatter source 字段已更新
- [ ] eight-dimensions-concurrent-safety-spec.md 更新记录中的压力测试报告链接已验证
- [ ] eight-dimensions-concurrent-safety-spec.md 的 related_retrospective 字段已检查
- [ ] mermaid-guide.md 中 mermaid-safe-coding-rules 和 mermaid-trap-cheatsheet 链接已验证
- [ ] multi-file-edit-reliability.md 中所有 patterns/ 和 reports/ 链接已验证
- [ ] parser-complexity-budget.md 中所有 patterns/ 和 reports/ 链接已验证
- [ ] pattern-validation-v3-template-batch-upgrade.md 中所有 patterns/ 和 reports/ 链接已验证
- [ ] 所有 frontmatter source 字段无过期旧路径
- [ ] 不存在 `../retrospective/`（单父目录）错误深度引用
- [ ] 不存在 file:/// 绝对路径引用

## README 创建
- [ ] docs/knowledge/best-practices/README.md 文件已创建
- [ ] README 包含 YAML frontmatter（id、title、date、category、status）
- [ ] README 包含"概述"章节
- [ ] README 包含"核心方法：八维检查法"章节（含8维度速览表格）
- [ ] README 包含"关键应用场景"章节（≥3个场景）
- [ ] README 包含"5分钟快速上手流程"章节（5步流程）
- [ ] README 包含"最佳实践文档索引"章节（覆盖所有11个文档，按类别分组）
- [ ] README 包含"延伸阅读"章节（指向 retrospective 体系）
- [ ] README 总行数 ≤ 200 行
- [ ] README 中所有链接为有效相对路径
- [ ] 八维表格准确反映 eight-dimensions-concurrent-safety-spec.md 中的8个维度信息

## 索引同步
- [ ] docs/knowledge/README.md 中 best-practices 条目数量已更新
- [ ] knowledge/README.md 中包含所有11个 best-practices 文档条目
- [ ] knowledge/README.md 中包含 best-practices/README.md 入口链接
- [ ] 所有新增条目的链接有效
- [ ] 摘要描述准确

## CHANGELOG 更新
- [ ] CHANGELOG.md 在 <!-- changelog --> 标记后新增条目
- [ ] 条目日期为 2026-07-09
- [ ] 条目类型为 docs
- [ ] 描述包含背景说明
- [ ] 描述包含迁移/修复范围
- [ ] 描述包含优化内容
- [ ] 描述包含对文档体系的积极影响
- [ ] 格式与既有条目一致（`- YYYY-MM-DD | type | description`）

## 自动化验证
- [ ] `python .agents/scripts/check-links.py --path docs/knowledge/best-practices` 通过，0 断链
- [ ] `python .agents/scripts/check-links.py --path docs/knowledge` 无新增断链
- [ ] best-practices 目录下 Grep 搜索 `file:///` 返回 0 结果
- [ ] best-practices 目录下 Grep 搜索 `\.\./retrospective/`（单父目录错误）返回 0 结果
- [ ] best-practices 内部互链有效（eight-dimensions ↔ concurrent-code-safety-review 等）

## 复盘报告
- [ ] 复盘报告目录已创建（docs/retrospective/reports/task-reports/retrospective-best-practices-link-fix-20260709/）
- [ ] 包含 README.md（执行概要）
- [ ] 包含 insight-extraction.md（洞察萃取）或等价内容
- [ ] 报告包含事实收集（变更统计数据）
- [ ] 报告包含过程分析（经验教训）
- [ ] 报告包含关键洞察（≥3个）
- [ ] 报告包含最佳实践/标准化操作指南
- [ ] 报告包含后续行动计划（≥2项）
- [ ] 复盘报告命名符合项目规范
