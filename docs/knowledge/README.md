---
type: Reference
title: "项目知识库"
---

# 项目知识库

项目知识库的统一入口页。详细分类条目与标签检索已拆分到独立索引，避免根 README 持续膨胀。

- **总条目数**：361
- **分类数**：21
- **标签数**：637

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
| operations | 26 | [operations](operations/README.md) |
| platform | 1 | [platform](categories/platform.md) |
| research | 1 | [research](categories/research.md) |
| social-relations | 1 | [social-relations](categories/social-relations.md) |
| standards | 1 | [standards](categories/standards.md) |
| tech | 48 | [tech](tech/README.md) |
| troubleshooting | 4 | [troubleshooting](troubleshooting/README.md) |
| unknown | 174 | [unknown](categories/unknown.md) |

## 辅助索引

- [分类总索引](category-index.md)：查看全部分类及条目摘要
- [标签索引](tags/README.md)：按关键词标签分片检索

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [切蛋糕法则：从数学公平分割到机制设计与职场分配（OKF 教程知识包）](cake-cutting-rule/index.md) | 2026-10-07 | cake-cutting-rule |
| [切蛋糕法则 · 数学公平分割理论：定义、算法谱系与局限](cake-cutting-rule/concepts/01-fair-division-theory.md) | 2026-10-07 | cake-cutting-rule |
| [切蛋糕法则 · 机制设计解读：为什么'你切我选'不需要监督](cake-cutting-rule/concepts/02-you-cut-i-choose-mechanism.md) | 2026-10-07 | cake-cutting-rule |
| [切蛋糕法则 · 职场与处世层：做蛋糕的人与切蛋糕的人](cake-cutting-rule/concepts/03-maker-vs-cutter-workplace.md) | 2026-10-07 | cake-cutting-rule |
| [示例：三人合伙创业的动态股权分配（你切我选思想的完整落地）](cake-cutting-rule/examples/01-worked-example-dynamic-equity.md) | 2026-10-07 | cake-cutting-rule |
| [V 对抗审查记录：切蛋糕法则知识包](cake-cutting-rule/references/adversarial-review.md) | 2026-10-07 | cake-cutting-rule |
| [信源台账：切蛋糕法则知识包 S01~S16](cake-cutting-rule/references/source-inventory.md) | 2026-10-07 | cake-cutting-rule |
| [结伴 × AI 变现行动知识包：三域飞轮——群内零交易、站外去赚钱、回站只讲案例](jieban-ai-monetization/index.md) | 2026-10-07 | social-relations |
| [正念 vs 正面：双概念知识包（教程、联系与区别、先接纳后重构整合模式）](mindfulness-positivity/index.md) | 2026-10-03 | mindfulness-positivity |
| [正念教程：觉察、接纳与当下的科学](mindfulness-positivity/concepts/01-zheng-nian-mindfulness.md) | 2026-10-03 | mindfulness-positivity |

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

*索引自动生成于 2026-10-07 19:07:31*
