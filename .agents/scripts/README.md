---
id: "scripts"
title: "Scripts 脚本目录"
source: ".agents/scripts/README.md"
x-toml-ref: "../../.meta/toml/.agents/scripts/README.toml"
---

# Scripts 脚本目录

`.agents/scripts/` 目录存放自动化验证与检查脚本。共享库位于 [lib/](lib/)，API参考见 [lib/README.md](lib/README.md)。

## 文档导航

| 文档 | 主题 | 包含脚本数 |
|------|------|-----------|
| [docs/usage/01-check-scripts.md](docs/usage/01-check-scripts.md) | 检查类脚本 | 9个 |
| [docs/usage/02-generate-build-scripts.md](docs/usage/02-generate-build-scripts.md) | 生成与构建脚本 | 5个 |
| [docs/usage/03-git-ci-scripts.md](docs/usage/03-git-ci-scripts.md) | Git与CI脚本 | 2个 |
| [docs/usage/04-fix-scripts.md](docs/usage/04-fix-scripts.md) | 批量修复与分析脚本 | 8个 |
| [docs/maintenance/01-generate-readme-testing.md](docs/maintenance/01-generate-readme-testing.md) | generate-readme.py维护与验证 | 1个维护手册 |
| [mdi/PATTERN-APPLICATION.md](mdi/PATTERN-APPLICATION.md) | MDI模式应用指南 | 3个代码模式 |
| [lib/README.md](lib/README.md) | 共享库API参考（索引） | 14个模块分片 |

## 脚本速查表

| 脚本 | 用途 | 分类 |
|------|------|------|
| `check-gitignore.py` | 验证.gitignore规则覆盖 | [检查](docs/usage/01-check-scripts.md#check-gitignorepy) |
| `check-vendor.py` | 验证vendor目录合规性 | [检查](docs/usage/01-check-scripts.md#check-vendorpy) |
| `check-links.py` | Markdown链接有效性校验+修复 | [检查](docs/usage/01-check-scripts.md#check-linkspy) |
| `check-spec-consistency.py` | spec/tasks/checklist一致性 | [检查](docs/usage/01-check-scripts.md#check-spec-consistencypy) |
| `check-filename-convention.py` | 文件名命名规范检查 | [检查](docs/usage/01-check-scripts.md#check-filename-conventionpy) |
| `check-move.py` | 文件移动时链接路径自动调整 | [检查](docs/usage/01-check-scripts.md#check-movepy) |
| `check-source-traceability.py` | source溯源字段反向索引 | [检查](docs/usage/01-check-scripts.md#check-source-traceabilitypy) |
| `check-role-permissions.py` | 角色tier/权限声明校验 | [检查](docs/usage/01-check-scripts.md#check-role-permissionspy) |
| `check-mermaid.py` | Mermaid语法陷阱检测+修复 | [检查](docs/usage/01-check-scripts.md#check-mermaidpy) |
| `generate-nav.py` | 自动生成文档导航表 | [生成/构建](docs/usage/02-generate-build-scripts.md#generate-navpy) |
| `generate-dashboard.py` | 自动聚合Spec执行看板 | [生成/构建](docs/usage/02-generate-build-scripts.md#generate-dashboardpy) |
| `finalize-atomization.py` | 原子化一键收尾（修链+导航+看板） | [生成/构建](docs/usage/02-generate-build-scripts.md#finalize-atomizationpy) |
| `build-ref-index.py` | 构建文件引用反向索引 | [生成/构建](docs/usage/02-generate-build-scripts.md#build-ref-indexpy) |
| `generate-readme.py` | 目录README自动生成与索引增量更新 | [生成/构建](docs/usage/02-generate-build-scripts.md#generate-readmepy) · [维护验证](docs/maintenance/01-generate-readme-testing.md) |
| `git-commit-utf8.py` | Windows Git UTF-8中文提交 | [Git/CI](docs/usage/03-git-ci-scripts.md#git-commit-utf8py) |
| `ci-check.ps1` | CI流水线全量检查 | [Git/CI](docs/usage/03-git-ci-scripts.md#ci-checkps1) |
| `fix_remaining_frontmatter.py` | 修复模板引用/绝对路径/跨项目路径 frontmatter source | [修复](docs/usage/04-fix-scripts.md#fix_remaining_frontmatterpy) |
| `fix_docs_prefix_paths.py` | 修复 docs/ 前缀 source 路径为相对路径 | [修复](docs/usage/04-fix-scripts.md#fix_docs_prefix_pathspy) |
| `fix_directory_and_missing.py` | 修复目录链接和缺失文件 source 路径 | [修复](docs/usage/04-fix-scripts.md#fix_directory_and_missingpy) |
| `fix_cross_project_temp.py` | 修复跨项目路径和 temp 引用 | [修复](docs/usage/04-fix-scripts.md#fix_cross_project_temppy) |
| `fix_inline_broken_links.py` | 批量修复内联断链（5类分类处理） | [修复](docs/usage/04-fix-scripts.md#fix_inline_broken_linkspy) |
| `fix_directory_link_warnings.py` | 批量修复目录链接为README.md引用 | [修复](docs/usage/04-fix-scripts.md#fix_directory_link_warningspy) |
| `analyze_frontmatter_issues.py` | 分析frontmatter路径问题分类统计 | [分析](docs/usage/04-fix-scripts.md#analyze_frontmatter_issuespy) |
| `analyze_missing_sources.py` | 扫描缺失source目标的文件 | [分析](docs/usage/04-fix-scripts.md#analyze_missing_sourcespy) |

## 相关模式

- [工具工作流组合](../docs/retrospective/patterns/methodology-patterns/tools-automation/tool-workflow-composition.md)
- [工具链成熟度](../docs/retrospective/patterns/methodology-patterns/tools-automation/toolchain-maturity.md)
- [共享库引力定律](../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
