+++
id = "retrospective-report-refactor-retrospective-docs-overview"
date = "2026-06-23"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-refactor-retrospective-docs.md#一、项目概述"
+++

# 项目概述

## 1.1 项目背景

`docs/retrospective/` 目录此前仅有 3 个大型 Markdown 文件，其中 `knowledge-extraction.md` 长达 598 行，将代码模式、架构模式、方法论、模板、决策框架、知识概念、资产清单等 7 个维度的内容混杂在单一文件中。随着项目规模扩大，这种"大而全"的组织方式暴露出四个核心问题：定位效率低、模块边界模糊、缺乏目录索引、增量维护困难。

## 1.2 项目目标

将 `docs/retrospective/` 文件夹从"3 个巨型文件"重构为"原子化 + 模块化 + 结构化"的文档体系，建立 6 个功能子目录、18 个原子模块文件、统一命名规范、可追溯引用关系及完整的目录索引。

## 1.3 交付物清单

| 类别 | 交付物 | 数量 |
|------|--------|------|
| 子目录 | templates/、patterns/（含 3 个子目录）、frameworks/、concepts/、reports/、assets/ | 8 |
| 原子模块文件 | 代码模式、架构模式、方法论、模板、决策框架、知识概念、资产清单 | 18 |
| 复盘报告迁移 | 2 份原有复盘报告移入 reports/ | 2 |
| 目录索引 | README.md | 1 |
| 原有文件删除 | knowledge-extraction.md | 1 |