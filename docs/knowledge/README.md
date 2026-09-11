---
type: Reference
title: "项目知识库"
---

# 项目知识库

项目知识库的统一入口页。详细分类条目与标签检索已拆分到独立索引，避免根 README 持续膨胀。

- **总条目数**：248
- **分类数**：18
- **标签数**：527

## 快速导航

| 顶层分类 | 条目数 | 入口 |
|----------|--------|------|
| architecture | 1 | [architecture](categories/architecture.md) |
| best-practices | 48 | [best-practices](best-practices/README.md) |
| decisions | 6 | [decisions](decisions/README.md) |
| docs | 10 | [docs](categories/docs.md) |
| examples | 6 | [examples](categories/examples.md) |
| knowledge | 20 | [knowledge](categories/knowledge.md) |
| operations | 22 | [operations](operations/README.md) |
| platform | 1 | [platform](categories/platform.md) |
| research | 1 | [research](categories/research.md) |
| standards | 1 | [standards](categories/standards.md) |
| tech | 38 | [tech](tech/README.md) |
| troubleshooting | 4 | [troubleshooting](troubleshooting/README.md) |
| unknown | 90 | [unknown](categories/unknown.md) |

## 辅助索引

- [分类总索引](category-index.md)：查看全部分类及条目摘要
- [标签索引](tags/README.md)：按关键词标签分片检索

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [书籍转 Web 教程的原创重写与适当引用编写规范](best-practices/book-to-web-tutorial-citation-guide.md) | 2026-09-11 | best-practices |
| [文档自动化工具链索引：从写文档到过门禁的统一入口](operations/doc-automation-toolchain.md) | 2026-09-11 | operations |
| [free-llm-api-summary](tech/free-llm-api-summary.md) | 2026-09-10 | unknown |
| [贡献指南](best-practices/contributing.md) | 2026-08-22 | knowledge/best-practices |
| [自动化脚本四层日志增强模式](best-practices/four-layer-logging-pattern.md) | 2026-08-22 | knowledge/best-practices |
| [CLI 工具选型二分法：任务编排（invoke）vs 用户接口（typer）](best-practices/cli-task-vs-user-interface-invoke-typer.md) | 2026-08-21 | best-practices |
| [Git 提交中文乱码排查：显示层 vs 存储层分离验证法](best-practices/git-commit-mojibake-diagnosis.md) | 2026-08-21 | best-practices |
| [ADR: torch-dev 双索引下载与 CUDA 硬断言决策](decisions/torch-dev-extra-index-cuda-assertion.md) | 2026-08-20 | decisions |
| [EPUB 转 Markdown 转换方案系统性调研报告](operations/epub-to-markdown-conversion-research.md) | 2026-08-19 | operations |
| [Python 3.14 Free-Threading 适用场景分析](tech/python-314-free-threading-scenario-analysis.md) | 2026-08-19 | tech |

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

*索引自动生成于 2026-09-11 16:02:00*
