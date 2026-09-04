# 验收检查清单

- [x] 顶层 `templates/` 目录已创建，含 `templates/README.md` 索引
- [x] `templates/agent-workspace-hub/AGENTS.md` 通用模板存在，含启动协议、四大区域、路由表骨架，并以占位符参数化
- [x] `templates/agent-workspace-hub/.agents/` 精简骨架覆盖关键子目录（roles/rules/workflows/protocols/templates/scripts/skills/commands/docs）及占位 README
- [x] `templates/agent-workspace-hub/README.md` 使用说明含复制/参数化/装载步骤
- [x] 模式文档归档至 `docs/retrospective/patterns/architecture-patterns/agent-workspace-template.md`，含触发场景/步骤/反模式/迁移验证
- [x] 模式文档 TOML frontmatter 字段完整（id/domain/layer/maturity/validation_count/source）
- [x] 新文件命名符合 kebab-case 规范（AGENTS.md/.agents/ 等结构名豁免）
- [x] 本地链接通过 check-links.py 验证
- [x] 模式库索引与导航已更新，双向链接有效
- [x] G1：R 阶段事实清单 ≥20 条且无因果词
- [x] G2：I 阶段洞察 ≥3 条且四元组完整
- [x] G3：E 阶段模板与模式文档满足可迁移性
- [x] V：审查意见 ≥5 条且采纳 ≥2 条修正
- [x] G4：原子提交完成，符合 Conventional Commits，中文无乱码