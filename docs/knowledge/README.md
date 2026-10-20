---
type: Reference
title: "项目知识库"
---

# 项目知识库

项目知识库的统一入口页。详细分类条目与标签检索已拆分到独立索引，避免根 README 持续膨胀。

- **总条目数**：461
- **分类数**：23
- **标签数**：783

## 快速导航

| 顶层分类 | 条目数 | 入口 |
|----------|--------|------|
| architecture | 1 | [architecture](categories/architecture.md) |
| best-practices | 49 | [best-practices](best-practices/README.md) |
| cake-cutting-rule | 7 | [cake-cutting-rule](categories/cake-cutting-rule.md) |
| decisions | 6 | [decisions](decisions/README.md) |
| docs | 10 | [docs](categories/docs.md) |
| examples | 6 | [examples](categories/examples.md) |
| knowledge | 20 | [knowledge](categories/knowledge.md) |
| mindfulness-positivity | 6 | [mindfulness-positivity](categories/mindfulness-positivity.md) |
| monetization-direction | 11 | [monetization-direction](categories/monetization-direction.md) |
| operations | 26 | [operations](operations/README.md) |
| platform | 1 | [platform](categories/platform.md) |
| research | 1 | [research](categories/research.md) |
| social-relations | 1 | [social-relations](categories/social-relations.md) |
| standards | 1 | [standards](categories/standards.md) |
| tech | 86 | [tech](tech/README.md) |
| troubleshooting | 4 | [troubleshooting](troubleshooting/README.md) |
| unknown | 218 | [unknown](categories/unknown.md) |
| what-is-life | 7 | [what-is-life](categories/what-is-life.md) |

## 辅助索引

- [分类总索引](category-index.md)：查看全部分类及条目摘要
- [标签索引](tags/README.md)：按关键词标签分片检索

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [Medium 平台知识包：从"思想之地"到注意力订阅平台](tech/medium-wiki/index.md) | 2026-10-20 | tech |
| [Medium 知识包变更日志](tech/medium-wiki/log.md) | 2026-10-20 | tech |
| [Medium 平台总览：从"思想之地"到注意力订阅平台](tech/medium-wiki/concepts/00-overview.md) | 2026-10-20 | tech |
| [Medium 历史时间线：2012–2026](tech/medium-wiki/concepts/01-timeline.md) | 2026-10-20 | tech |
| [Medium 产品形态与设计理念：为"深读"而生的交互系统](tech/medium-wiki/concepts/02-product-design.md) | 2026-10-20 | tech |
| [Medium 商业模式：会员订阅 + Partner Program 的分成引擎](tech/medium-wiki/concepts/03-business-model.md) | 2026-10-20 | tech |
| [Medium 技术架构：从 Node.js 单体到 AWS 全栈](tech/medium-wiki/concepts/04-architecture.md) | 2026-10-20 | tech |
| [Medium 内容生态与治理：作者关系、治理实验与全球访问限制](tech/medium-wiki/concepts/05-ecosystem-governance.md) | 2026-10-20 | tech |
| [Medium 竞争格局：与 Substack、Ghost 的范式分岔](tech/medium-wiki/concepts/06-competition.md) | 2026-10-20 | tech |
| [2022–2025 转型复盘：Stubblebine 的扭亏之战](tech/medium-wiki/concepts/07-turnaround.md) | 2026-10-20 | tech |

## 相关资源

### 回溯报告

- [双体系引用收敛台账（ACT-5）](../retrospective/cross-reference-ledger.md)
- [🔄 复盘与模式库](../retrospective/index.md)
- [变更日志](../retrospective/log.md)

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

*索引自动生成于 2026-10-20 11:27:17*
