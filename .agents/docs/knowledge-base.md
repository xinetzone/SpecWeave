# 知识库

> **来源**：从 `README.md` "知识库"章节拆分

## 概述

本项目建立了体系化的项目知识库，用于沉淀实践经验、架构决策、复盘洞察与可复用资产：

| 知识库 | 路径 | 内容 |
|--------|------|------|
| 技术知识库 | [docs/knowledge/](knowledge/README.md) | 架构决策记录（ADR）、运维操作手册、故障排查指南 |
| 复盘文档体系 | [docs/retrospective/](retrospective/README.md) | 项目复盘报告、可复用模式（代码/架构/方法论）、模板、决策框架、知识概念 |

## 技术知识库

`docs/knowledge/` 按分类组织，包含以下类别：

- **decisions/** — 架构决策记录（ADR），记录关键技术决策及其理由
- **operations/** — 运维操作手册，记录常用操作的标准流程
- **troubleshooting/** — 故障排查指南，记录常见问题的诊断与解决方案
- **platform/** — 平台相关文档
- **best-practices/** — 最佳实践

详见 [docs/knowledge/README.md](knowledge/README.md)。

## 复盘文档体系

`docs/retrospective/` 是项目中规模最大的知识资产，采用模块化、结构化的方式组织：

- **`reports/`** — 项目复盘分析报告（含初版与深度版）
- **`patterns/`** — 可复用模式（代码模式 + 架构模式 + 方法论）
- **`frameworks/`** — 决策框架矩阵
- **`concepts/`** — 核心知识概念
- **`templates/`** — 可复用文档模板
- **`assets/`** — 资产清单与复用指南
- **`prompt-extraction.md`** — 提示词工程可迁移模式、模板与方法论

详见 [docs/retrospective/README.md](retrospective/README.md)。

> **关联模块**：
> - `../README.md`
> - `knowledge/README.md`
> - `retrospective/README.md`