# docs 迁移前基线

## 快照摘要

- 生成时间：`2026-07-15 00:50:45`
- 基线范围：仓库根目录 `docs/`
- 文件总数：`2683`
- 总体积：`86761477` Bytes，约 `82.74 MiB`
- 根级 `.agents/docs/` 状态：目录已存在，但当前盘点未发现根级内容

## 备份位置

- 备份目录：[`../../../../.temp/backup/docs-before-agents-docs-20260715/`](../../../../.temp/backup/docs-before-agents-docs-20260715/)
- 备份方式：在执行任何迁移前，对原 `docs/` 做整目录递归复制
- 恢复方式：如需回滚，将该备份目录完整复制回仓库根目录并恢复为 `docs/`

## 基线产物

| 文件 | 用途 |
|---|---|
| [artifacts/docs-baseline-summary.json](artifacts/docs-baseline-summary.json) | 基线摘要：时间、文件数、体积、顶层入口 |
| [artifacts/docs-baseline-manifest.json](artifacts/docs-baseline-manifest.json) | 全量文件清单：相对路径、大小、SHA256 |
| [artifacts/docs-root-reference-files-all.json](artifacts/docs-root-reference-files-all.json) | 仓库内所有命中 `docs/` 根路径的文件清单（原始版） |
| [artifacts/docs-root-reference-files-outside-docs.json](artifacts/docs-root-reference-files-outside-docs.json) | 仓库内 `docs/` 之外命中 `docs/` 根路径的文件清单（原始版） |
| [artifacts/docs-root-reference-files-outside-docs-clean.json](artifacts/docs-root-reference-files-outside-docs-clean.json) | 去噪后的外部引用清单，排除 `__pycache__`、`.meta/backup`、备份副本等噪音 |
| [artifacts/key-entry-reference-baseline.json](artifacts/key-entry-reference-baseline.json) | 关键入口文件引用关系（原始版） |
| [artifacts/key-entry-reference-baseline-clean.json](artifacts/key-entry-reference-baseline-clean.json) | 关键入口文件引用关系（去噪版） |

## 关键入口文件引用基线

| 目标入口 | 去噪后引用文件数 | 说明 |
|---|---:|---|
| `.agents/docs/README.md` | 48 | 人类文档总入口，受 `docgen`、模板、spec 文档等多侧引用 |
| `.agents/docs/development-standards.md` | 59 | `.agents/` 路由、规则、PDR 文档的核心依赖 |
| `docs/knowledge/README.md` | 217 | 知识库入口，受 `.agents/`、`.trae/specs/`、模板等广泛引用 |
| `docs/retrospective/README.md` | 54 | 复盘体系入口，受 `.agents/` 和 `docs-restructure` 相关 spec 引用 |

## `docs/` 根路径外部引用规模

- 原始扫描命中文件数：`2564`
- 去噪后命中文件数：`1842`
- 典型引用来源：
  - `.agents/context-routing.md`
  - `.agents/global-core-rules.md`
  - `.agents/commands/*.md`
  - `.agents/protocols/pre-document-reading*.md`
  - `.agents/scripts/*.py`
  - `.trae/specs/**/*.md`

## 顶层入口快照

### 主要目录

- `architecture/`
- `code-wiki/`
- `knowledge/`
- `patterns/`
- `quality/`
- `retrospective/`
- `standards/`
- `superpowers/`
- `task-summaries/`
- `templates/`
- `test-plans/`

### 主要文件

- `README.md`
- `project-overview.md`
- `project-highlights.md`
- `project-structure.md`
- `development-standards.md`
- `knowledge-base.md`
- `collaboration.md`
- `agent-roles.md`
- `verification-automation.md`
- `related-links.md`

## Task 2 完成判定

- SubTask 2.1：已生成可恢复备份副本
- SubTask 2.2：已记录文件总数、相对路径、文件大小、内容哈希
- SubTask 2.3：已记录关键入口文件与导航文件的引用基线
- SubTask 2.4：已具备进入迁移阶段所需的备份与基线前置条件
