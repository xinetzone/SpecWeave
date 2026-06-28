# .agents/scripts/lib/ API 参考

> 本文档由 `lib/__init__.py` 中的 `generate_api_docs()` 自动生成，描述共享库所有公开模块和函数。

## 目录

- [lib.project — 项目路径解析](#libproject--项目路径解析)
- [lib.cli — CLI 输出格式化](#libcli--cli-输出格式化)
- [lib.frontmatter — TOML Frontmatter 解析](#libfrontmatter--toml-frontmatter-解析)
- [lib.markdown — Markdown 文件处理](#libmarkdown--markdown-文件处理)
- [lib.link_fixer — 链接修复](#liblink_fixer--链接修复)
- [lib.patterns — 模式成熟度分析](#libpatterns--模式成熟度分析)
- [lib.spec — Spec 文档处理](#libspec--spec-文档处理)
- [lib.checks — 检查器框架](#libchecks--检查器框架)
- [constants.py — 常量定义](#constantspy--常量定义)

---

## lib.project — 项目路径解析

| 函数 | 签名 | 说明 |
|------|------|------|
| `resolve_project_root` | `(anchor: str \| Path) -> Path` | 从锚点位置向上查找工程根目录（含 AGENTS.md） |
| `resolve_agents_dir` | `(anchor: str \| Path) -> Path` | 解析 `.agents/` 目录路径 |
| `resolve_scripts_dir` | `(anchor: str \| Path) -> Path` | 解析 `.agents/scripts/` 目录路径 |

**示例**：

```python
from lib.project import resolve_project_root
root = resolve_project_root(__file__)  # 返回项目根目录 Path
```

---

## lib.cli — CLI 输出格式化

| 函数 | 签名 | 说明 |
|------|------|------|
| `print_pass` | `(msg: str) -> None` | 打印绿色 [PASS] 通过信息 |
| `print_warn` | `(msg: str) -> None` | 打印黄色 [WARN] 警告信息 |
| `print_error` | `(msg: str) -> None` | 打印红色 [FAIL] 错误信息 |
| `print_header` | `(title: str, width: int = 60) -> None` | 打印等宽分隔标题行 |
| `print_summary` | `(pass_count: int, warn_count: int, error_count: int, width: int = 60) -> None` | 打印彩色检查摘要（通过/警告/错误） |
| `add_common_args` | `(parser: ArgumentParser) -> None` | 注册通用 CLI 参数（--path、--json） |

**示例**：

```python
from lib.cli import print_pass, print_warn, print_header, add_common_args
import argparse

parser = argparse.ArgumentParser(description='我的检查脚本')
add_common_args(parser)  # 自动添加 --path 和 --json
args = parser.parse_args()
print_header('开始检查')
print_pass('文件格式正确')
print_summary(pass_count=5, warn_count=1, error_count=0)
```

---

## lib.frontmatter — TOML Frontmatter 解析

解析 Markdown 文件头部的 `+++ ... +++` TOML 元数据块。

| 函数 | 签名 | 说明 |
|------|------|------|
| `parse_toml_frontmatter` | `(file_path: str \| Path) -> str \| None` | 读取文件并返回 TOML frontmatter 纯文本（不含 +++） |
| `extract_frontmatter_field` | `(frontmatter: str, field_name: str) -> str \| None` | 从 frontmatter 文本中提取指定字段值（支持带引号/无引号） |
| `extract_all_fields` | `(frontmatter: str) -> dict[str, str]` | 提取 frontmatter 中所有字段为字典 |
| `parse_toml_frontmatter_as_dict` | `(file_path: str \| Path) -> dict[str, str] \| None` | 一步读取文件并解析所有 frontmatter 字段为字典（便捷函数，等价于 parse + extract_all_fields） |

**示例**：

```python
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, parse_toml_frontmatter_as_dict
fm = parse_toml_frontmatter('docs/retrospective/patterns/mypattern.md')
if fm:
    maturity = extract_frontmatter_field(fm, 'maturity')  # 'L2'
# 便捷用法：直接获取全部字段字典
fields = parse_toml_frontmatter_as_dict('path/to/file.md') or {}
print(fields.get('maturity'))
```

---

## lib.markdown — Markdown 文件处理

| 函数 | 签名 | 说明 |
|------|------|------|
| `find_markdown_files` | `(root: Path, exclude_dirs=None) -> list[Path]` | 递归查找 Markdown 文件，默认排除系统目录 |
| `extract_title` | `(path: Path \| str) -> str` | 提取首个一级标题（# Title）文本 |
| `extract_description` | `(path: Path \| str) -> str` | 提取标题下首行描述文本 |
| `parse_inline_links` | `(content: str) -> list[tuple[str, str]]` | 提取所有内联链接，返回 [(text, url), ...] |
| `update_marker_region` | `(file_path, marker_start, marker_end, new_content) -> None` | 替换 HTML 注释标记之间的内容 |

**常量**：

- `TITLE_RE` — 一级标题正则
- `DESC_RE` — 描述段落正则

**示例**：

```python
from lib.markdown import find_markdown_files, extract_title, update_marker_region
md_files = find_markdown_files(root_dir)
for f in md_files:
    title = extract_title(f)
# 更新自动生成区域
update_marker_region('README.md', '<!-- AUTO-START -->', '<!-- AUTO-END -->', new_content)
```

---

## lib.link_fixer — 链接修复

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

## lib.patterns — 模式成熟度分析

提供模式文件扫描、frontmatter 解析、成熟度分类、分布统计、README 统计表解析与更新能力。

| 常量 | 说明 |
|------|------|
| `REQUIRED_FIELDS` | 模式文件必填字段列表（id/domain/layer/maturity/validation_count/reuse_count/documentation_level/source） |
| `MATURITY_LEVELS` | 成熟度等级：['L1', 'L2', 'L3', 'L4'] |
| `PATTERN_DOMAINS` | 模式子域：['methodology-patterns', 'code-patterns', 'architecture-patterns'] |
| `EXCLUDED_FILENAMES` | 排除文件名：{'README.md', 'CATEGORIES.md'} |

| 函数 | 签名 | 说明 |
|------|------|------|
| `parse_pattern_frontmatter` | `(filepath) -> dict \| None` | 解析模式文件 frontmatter，返回结构化字典（含 int 类型转换） |
| `scan_patterns` | `(base_dir) -> tuple[list, list]` | 递归扫描所有模式文件，返回 (patterns, issues) |
| `classify_pattern` | `(pattern) -> str` | 分类模式状态：'upgrade'/'anomaly'/'ok' |
| `analyze_distribution` | `(patterns) -> tuple[dict, dict]` | 分析成熟度分布与各子域分布 |
| `find_upgrade_candidates` | `(patterns) -> dict` | 找出待升级模式：{'L1_to_L2': [...], 'L2_to_L3': [...]} |
| `count_patterns` | `(dir_path) -> int` | 统计目录中模式文件数（递归，排除README/CATEGORIES） |
| `grep_maturity_per_directory` | `(patterns_root) -> dict` | 按目录统计成熟度分布 |
| `parse_readme_stats_table` | `(readme_path) -> dict` | 解析 patterns/README.md 统计表 |
| `parse_readme_index_table` | `(readme_path) -> OrderedDict` | 解析 patterns/README.md 索引表 |
| `check_stats_consistency` | `(patterns_root, readme_path) -> list` | 比对 grep 统计与 README 声明的差异 |
| `update_readme_index_table` | `(readme_path, declared_stats, actual_counts) -> str` | 更新 README 索引表中的统计数字，返回新内容 |
| `build_report_data` | `(patterns, issues) -> dict` | 构建统一报告数据（供 stats 子命令使用） |

---

## lib.spec — Spec 文档处理

提供 Spec 文件（spec.md / tasks.md / checklist.md）的解析、一致性检查与报告生成能力。

| 子模块 | 说明 |
|--------|------|
| `lib.spec.parsers` | Spec 文档解析器：`parse_spec()`、`parse_tasks()`、`parse_checklist()` |
| `lib.spec.models` | Spec 数据模型：`SpecDoc`、`TaskItem`、`CheckItem` 等 |
| `lib.spec.consistency_checkers` | 一致性检查器 |
| `lib.spec.format_checkers` | 格式检查器 |
| `lib.spec.reporters` | 检查报告生成器 |
| `lib.spec.utils` | 工具函数：`discover_spec_dirs()` 等 |

**主要入口函数**：

```python
from lib.spec.utils import discover_spec_dirs
from lib.spec.parsers import parse_spec, parse_tasks, parse_checklist
spec_dirs = discover_spec_dirs(root)  # 发现所有 .trae/specs/ 下的 spec 目录
```

---

## lib.checks — 检查器框架

提供统一的检查器基类和内置检查器实现。

| 子模块 | 说明 |
|--------|------|
| `lib.checks.base` | 检查器基类 `BaseChecker` |
| `lib.checks.filename` | 文件名规范检查 |
| `lib.checks.gitignore` | .gitignore 规则检查 |
| `lib.checks.mermaid` | Mermaid 语法检查 |
| `lib.checks.roles` | 角色权限检查 |
| `lib.checks.vendor` | vendor 目录合规性检查 |

---

## constants.py — 全局常量（scripts/ 根目录）

位于 `.agents/scripts/constants.py`，全局共享常量模块，供所有脚本和 lib/ 模块引用。

导入方式：`from constants import EXCLUDED_DIRS, ANSI_GREEN, ...`

| 常量 | 类型 | 说明 |
|------|------|------|
| `ANSI_GREEN/ANSI_YELLOW/ANSI_RED/ANSI_CYAN/ANSI_RESET` | str | ANSI 颜色代码 |
| `EXCLUDED_DIRS` | set[str] | 文件扫描默认排除目录（.git/vendor/.venv/__pycache__/node_modules/.temp） |
| `REQUIRED_RULES` / `TEMP_PATHS` | list | .gitignore 必需规则与临时路径 |
| `LINK_CHECK_*` | - | check-links.py 默认参数（timeout/workers/user-agent等） |
| `VALID_TIERS` / `ROLE_EXCLUDED_FILES` | - | 角色权限校验常量 |
| `SPEC_MATCH_THRESHOLD` / `META_DOC_KEYWORDS` | - | Spec 一致性检查参数 |
| `SCAN_DIRS` / `TARGETS` / `MANUAL_DESCRIPTIONS` | - | 导航生成器配置 |

---

## 新增脚本开发流程

新建 `.agents/scripts/` 下的脚本前，请遵循以下流程：

1. **先查本文件**，确认 lib/ 是否已有可复用的函数
2. **优先使用共享函数**，避免重复实现相同逻辑
3. 如确需新功能，先考虑是否应提取到 lib/ 供其他脚本复用
4. 脚本头部添加 sys.path 设置：
```python
import sys
from pathlib import Path
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
```
5. 使用 `add_common_args(parser)` 注册通用参数（--path/--json）
6. 使用 `print_pass/print_warn/print_error/print_summary` 输出检查结果
7. 完成后运行 `python check-duplication.py` 检查是否引入新的重复代码
