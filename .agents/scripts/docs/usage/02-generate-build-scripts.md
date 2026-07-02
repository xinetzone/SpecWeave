---
id: "scripts-usage-generate-build-scripts"
title: "生成与构建脚本使用说明"
source: "README.md#使用说明"
x-toml-ref: "../../../../../.meta/toml/.agents/scripts/docs/usage/02-generate-build-scripts.toml"
---

# 生成与构建脚本使用说明

本文档描述 `.agents/scripts/` 目录下所有生成（generate）、构建（build）、收尾类脚本的用法。

---

## generate-nav.py

扫描 `docs/` 目录下的所有 `.md` 文件，提取标题和描述，自动生成文档导航表，并更新 `README.md` 和 `docs/README.md` 中 `<!-- NAV_TABLE_START -->` 与 `<!-- NAV_TABLE_END -->` 标记之间的内容。

```bash
# 自动生成并更新导航表
python .agents/scripts/generate-nav.py
```

---

## generate-dashboard.py

扫描 `.trae/specs/` 目录下所有 Spec 的 `tasks.md`，自动聚合各主题和 Spec 的完成状态，更新根 `README.md` 中 `<!-- SPEC_DASHBOARD_START -->` 与 `<!-- SPEC_DASHBOARD_END -->` 标记之间的执行进度看板。

判定规则：
1. 优先读取 TOML/YAML frontmatter 中的 `status` 字段，若为 `completed`/`done`/`finished` 则视为已完成
2. 否则检查是否存在未勾选的复选框（`- [ ]` 或 `## [ ]`），无未勾选项则视为已完成
3. 自动跳过代码块中的复选框（避免误判示例代码）

```bash
# 自动扫描并更新 Spec 执行进度看板
python .agents/scripts/generate-dashboard.py
```

---

## finalize-atomization.py

原子化操作一键收尾脚本。在文档/代码原子化拆分、文件移动、目录重构等操作完成后运行，一键执行断链自动修复、导航表更新、Spec 看板刷新等后处理工作，确保原子化完成后项目状态一致。

执行步骤：
1. **自动断链修复**：调用 link_fixer 扫描全项目，自动修复相对路径层级错误、绝对路径转换、目录尾部斜杠补全等
2. **导航表更新**：运行 generate-nav.py 刷新文档导航表
3. **Spec 看板更新**：运行 generate-dashboard.py 刷新 Spec 执行进度看板

```bash
# 完整后处理（实际执行修复）
python .agents/scripts/finalize-atomization.py

# 预览模式，不修改文件
python .agents/scripts/finalize-atomization.py --dry-run

# 跳过链接修复
python .agents/scripts/finalize-atomization.py --no-links

# 指定目标目录（仅修复特定子树）
python .agents/scripts/finalize-atomization.py --target docs/retrospective/
```

---

## build-ref-index.py

构建文件引用反向索引。扫描项目中所有 Markdown 文件提取本地相对链接，建立 `{目标文件: [引用文件列表]}` 的反向映射。在文件移动、删除、大规模重构前，可快速查询受影响的引用方，避免断链遗漏。

功能特性：
- 自动跳过代码块内的示例链接
- 支持文件查询、目录查询、孤立文件检测
- 支持 JSON 格式输出（便于与其他工具集成）
- 自动排除 `.git/`、`vendor/`、`node_modules/` 等目录

```bash
# 构建索引并显示统计摘要 + Top 被引用文件
python .agents/scripts/build-ref-index.py

# 查询哪些文件引用了指定文件（移动前查询影响面）
python .agents/scripts/build-ref-index.py --query AGENTS.md

# 批量查询多个文件
python .agents/scripts/build-ref-index.py --query file1.md path/to/file2.md

# 查询哪些文件引用了指定目录下的任意文件
python .agents/scripts/build-ref-index.py --query-dir docs/retrospective/patterns/

# 显示被引用次数最多的 Top 20 文件
python .agents/scripts/build-ref-index.py --top 20

# 列出未被任何文件引用的孤立文件
python .agents/scripts/build-ref-index.py --orphans

# JSON 格式输出（便于工具集成）
python .agents/scripts/build-ref-index.py --query README.md --json
```

---

## 相关模式

- [工具工作流组合](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/tool-workflow-composition.md)
- [自动生成阈值控制](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/auto-generate-threshold.md)
- [Dry-Run预览优先](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/dry-run-first.md)

---

← 上一章: [检查类脚本](01-check-scripts.md) | **[返回索引](../../README.md)** | 下一章 → [Git与CI脚本](03-git-ci-scripts.md)
