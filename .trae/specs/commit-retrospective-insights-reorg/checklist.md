# Checklist

## 原子提交验证
- [ ] 提交信息遵循 Conventional Commits 格式（`docs(insights): ...`）
- [ ] 提交信息主体使用中文描述"为什么"
- [ ] 提交包含所有12个修改文件，无遗漏
- [ ] 提交包含1个删除文件（insights-31-65.md）
- [ ] 提交包含2个新建文件（insights-31-53.md, insights-54-68.md）
- [ ] 提交包含规划文档（.trae/specs/insights-reorganization/）
- [ ] 无临时文件（vendor/, .temp/, __pycache__/ 等）混入提交
- [ ] 提交后 `git status` 工作区干净（或仅有本次新增的复盘报告文件）

## 复盘报告验证
- [ ] 报告目录存在于 `docs/retrospective/reports/project-governance/retrospective-insights-reorg-20260626/`
- [ ] README.md 包含项目概览、核心指标表、交付物清单、子模块导航
- [ ] execution-retrospective.md 遵循「事实→分析→洞察→建议」四部分结构
- [ ] execution-retrospective.md 包含6步执行过程的时间线
- [ ] execution-retrospective.md 包含关键决策分析（如拆分点选择、标题优化策略）
- [ ] insight-extraction.md 包含至少3条可复用洞察
- [ ] 每条洞察有支撑事实和可迁移性说明
- [ ] 洞察标注成熟度等级（L1-L4）
- [ ] export-suggestions.md 包含改进行动项表格（含优先级）
- [ ] export-suggestions.md 包含可复用方法论总结

## 结构化导出验证
- [ ] 所有报告文件为 Markdown 格式
- [ ] 报告间内部链接有效（README → 子文件的链接）
- [ ] 复盘报告索引已更新（如适用）
- [ ] 报告内容基于事实数据，无主观臆断
