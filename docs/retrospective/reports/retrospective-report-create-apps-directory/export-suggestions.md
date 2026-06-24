+++
id = "retrospective-report-create-apps-directory-export"
date = "2026-06-23"
type = "export-suggestions"
source = "docs/retrospective/reports/retrospective-report-create-apps-directory.md#四"
+++

# 四、导出环节

## 4.1 改进建议

| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| 初版 spec 未主动覆盖 `.agents/` 治理扩展 | 在 spec 设计阶段增加"关联系统影响分析"检查项——当创建新的项目实体（目录、模块、角色）时，强制检查是否需要同步更新 AGENTS.md、.agents/ 规范与项目结构文档 | 中 | 减少因遗漏关联更新导致的迭代轮次 | 已完成 |
| 生命周期协议缺乏"回退"路径 | 在 `app-development-workflow.md` 中补充异常处理流程——当迁移后验证失败时，是否回退到暂存区重新