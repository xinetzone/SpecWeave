---
id: "lib-api-link_fixer"
title: "lib.link_fixer — 链接修复"
source: "lib/api_docs.py#link_fixer"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/05-link-fixer.toml"
---

# lib.link_fixer — 链接修复

提供 Markdown 内联链接的解析、有效性校验、自动修复能力。

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `INLINE_LINK_RE` | `Pattern` | 内联链接正则 `[text](url)` |
| `LinkFix` | `class` | 链接修复结果数据类（source, target, new_url, fix_type, line） |
| `parse_file_url` | `(url: str) -> tuple[str, str]` | 解析 file:/// URL 为 (file_path, anchor) |
| `find_file_in_project` | `(url_path, project_root, ...) -> list[Path]` | 在项目中模糊查找目标文件 |
| `compute_relative_path` | `(source_file: Path, target_file: Path) -> str` | 计算源文件到目标文件的相对路径 |
| `fix_file_links` | `(source_file, project_root, dry_run, ...) -> list[LinkFix]` | 修复单个文件中的链接 |
| `fix_directory_links` | `(dir_path, project_root, dry_run, ...) -> list[LinkFix]` | 修复目录下所有 Markdown 文件的链接 |
| `fix_link_url` | `(text, url, source_file, project_root, ...) -> LinkFix \| None` | 修复单个链接 URL |
| `is_code_fence_context` | `(content: str, pos: int) -> bool` | 判断位置是否在代码块内 |
| `apply_filename_mapping` | `(file_path, rename_map) -> str` | 应用文件重命名映射 |
| `apply_line_remap` | `(anchor, line_remap, source_filename) -> str` | 应用行号重映射 |
| `print_fix_report` | `(fixes: list[LinkFix], dry_run: bool) -> None` | 打印链接修复报告 |
| `fix_broken_links` | `(source_path, project_root, ...) -> list[LinkFix]` | 批量修复断链（综合入口） |

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← Markdown 文件处理](04-markdown.md) | **[返回索引](../README.md)** | 下一章 → [模式成熟度分析 →](06-patterns.md)
