# Tasks

- [ ] Task 1: 执行原子提交 — 将洞察库重组变更提交至 Git
  - [ ] SubTask 1.1: 预提交验证 — 检查变更范围，确认无临时文件混入，确认文件列表完整
  - [ ] SubTask 1.2: 构建提交信息 — 按 Conventional Commits 规范编写中文提交信息
  - [ ] SubTask 1.3: 执行提交 — 添加指定文件到暂存区并提交，记录提交哈希
  - [ ] SubTask 1.4: 验证提交 — 确认提交成功，提交信息格式正确，文件列表符合预期

- [ ] Task 2: 生成复盘报告 — 创建复盘报告目录与4个子文件
  - [ ] SubTask 2.1: 创建报告目录 `docs/retrospective/reports/project-governance/retrospective-insights-reorg-20260626/`
  - [ ] SubTask 2.2: 编写 README.md — 项目概览、核心指标、交付物清单、子模块导航
  - [ ] SubTask 2.3: 编写 execution-retrospective.md — 执行过程回顾（6步执行流程）、关键决策分析、问题与解决方案
  - [ ] SubTask 2.4: 编写 insight-extraction.md — 萃取可复用洞察（文件拆分策略、交叉引用管理、结构修复模式等），标注成熟度等级
  - [ ] SubTask 2.5: 编写 export-suggestions.md — 改进行动项、可复用方法论、风险预警

- [ ] Task 3: 结构化导出与归档 — 更新索引并确认归档
  - [ ] SubTask 3.1: 检查并更新 `docs/retrospective/reports/README.md` 索引（如需要）
  - [ ] SubTask 3.2: 验证报告目录结构与文件完整性

# Task Dependencies

- [Task 2] depends on [Task 1]（复盘需要基于已提交的事实数据）
- [Task 3] depends on [Task 2]（导出归档需要报告生成完成）
