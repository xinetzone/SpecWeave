# 项目知识库

项目知识库的统一入口页。详细分类条目与标签检索已拆分到独立索引，避免根 README 持续膨胀。

- **总条目数**：679
- **分类数**：56
- **标签数**：1449

## 快速导航

| 顶层分类 | 条目数 | 入口 |
|----------|--------|------|
| architecture | 1 | [architecture](category-index.md#architecture) |
| best-practices | 12 | [best-practices](best-practices/README.md) |
| decisions | 1 | [decisions](decisions/README.md) |
| docs | 8 | [docs](category-index.md#docs) |
| knowledge | 346 | [knowledge](category-index.md#knowledge) |
| learning | 211 | [learning](learning/README.md) |
| operations | 11 | [operations](operations/README.md) |
| reference | 3 | [reference](category-index.md#reference) |
| research | 1 | [research](category-index.md#research) |
| standards | 1 | [standards](category-index.md#standards) |
| troubleshooting | 4 | [troubleshooting](troubleshooting/README.md) |
| unknown | 80 | [unknown](category-index.md#unknown) |

## 辅助索引

- [分类总索引](category-index.md)：查看全部分类及条目摘要
- [标签索引](tags/README.md)：按关键词标签分片检索

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [从 Prompt 到 Loop：四层工程打造稳定可控的 AI Agent](learning/02-agent-engineering-methodology/workbuddy-four-layers-seven-concepts-analysis.md) | 2026-07-14 | unknown |
| [七概念×DeepTutor实践教程 - 概述](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/00-overview.md) | 2026-07-14 | unknown |
| [七概念×DeepTutor实践教程 - 术语表](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/glossary.md) | 2026-07-14 | unknown |
| [R - 复盘 (Retrospective)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/01-r-retrospective.md) | 2026-07-14 | unknown |
| [I - 洞察 (Insight)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/02-i-insight.md) | 2026-07-14 | unknown |
| [E - 萃取 (Extraction)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/03-e-extraction.md) | 2026-07-14 | unknown |
| [C - 原子提交 (Atomic Commit)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/04-c-atomic-commit.md) | 2026-07-14 | unknown |
| [A - 原子化 (Atomization)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/05-a-atomization.md) | 2026-07-14 | unknown |
| [F - 第一性原理 (First Principles)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/06-f-first-principles.md) | 2026-07-14 | unknown |
| [V - 对抗性审查 (Adversarial Review)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/07-v-adversarial-review.md) | 2026-07-14 | unknown |

## 相关资源

### 回溯报告

- [七概念方法论体系整合任务复盘](../retrospective/2026-07-10-seven-concepts-methodology-integration.md)
- [元方法论自举验证复盘——seven-concepts-trigger CLI工具](../retrospective/2026-07-11-meta-bootstrap-seven-concepts-trigger.md)
- [原子写入重构性能对比报告](../retrospective/2026-07-12-atomic-write-refactoring.md)
- [文件I/O并发安全统一库架构演进报告](../retrospective/2026-07-12-io-safety-architecture-evolution.md)
- [跨文化第一性原理比较研究 v2.0 — 里程碑复盘报告](../retrospective/2026-07-13-cross-cultural-first-principles.md)
- [七概念视角：《微软Copilot成本困境与多模型时代》深度透视报告](../retrospective/2026-07-13-seven-concepts-copilot-multimodel-analysis.md)
- [Agent App Marketplace Task 0 — 工作区发现协议与提示词自举协议复盘报告](../retrospective/2026-07-13-task0-workspace-protocols.md)
- [竹简悟道·秒悟竞赛冲刺复盘报告——Trae Solo+七概念方法论实战](../retrospective/2026-07-14-meoo-contest-sprint-retro.md)
- [项目硬编码问题系统性复盘报告](../retrospective/hardcode-retrospective-report.md)
- [元方法论自举执行日志](../retrospective/meta-bootstrap-execution-log.md)
- [提示词工程 — 可迁移模式、模板与方法论萃取](../retrospective/prompt-extraction.md)
- [复盘文档体系](../retrospective/README.md)
- [TerminalWorld深度洞察：首个基于真实人类终端轨迹的Agent评测基准](../retrospective/terminalworld-benchmark-analysis.md)

### 任务总结

- [任务总结报告库](../task-summaries/README.md)
- [任务执行总结报告](../task-summaries/task-summary-atomic-commit-20260706.md)
- [任务执行总结报告](../task-summaries/task-summary-git-local-clone-bug-20260701.md)
- [任务执行总结报告](../task-summaries/task-summary-readme-creation-20260623.md)

## 使用指南

### 如何添加知识条目

1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`learning/` 等）
2. 复制 `template.md` 作为模板，创建新的 `.md` 文件
3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）
4. 在正文中按照模板结构编写内容
5. 运行 `python scripts/generate_index.py` 重新生成入口页、分类索引与标签分片

### 如何检索

- **按分类入口**：优先使用上方「快速导航」进入各主题 README
- **按全部分类**：打开 [分类总索引](category-index.md) 查看所有分类及摘要
- **按标签检索**：打开 [标签索引](tags/README.md) 后进入对应分片页面
- **按时间排序**：查看本页「最近更新」章节，了解最新添加的知识条目
- **全文搜索**：在项目根目录使用 `rg "关键词" docs/knowledge/` 进行全文搜索

### 如何维护

- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息
- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）
- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目
- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成全部索引

---

*索引自动生成于 2026-07-14 23:23:55*
