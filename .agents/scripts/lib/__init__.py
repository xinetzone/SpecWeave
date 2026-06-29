#!/usr/bin/env python3
"""lib/ — 验证脚本共享工具库

提供项目路径解析、TOML frontmatter 解析、CLI 输出格式化、Markdown 处理、
模式成熟度分析、链接修复、Spec 一致性检查等跨脚本复用的基础函数。

## 使用方式

在 `.agents/scripts/` 下的脚本中直接导入：

```python
from lib.project import resolve_project_root
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args
from lib.markdown import find_markdown_files, extract_title, extract_description
from lib.link_fixer import fix_file_links, fix_directory_links, INLINE_LINK_RE
from lib.patterns import scan_patterns, find_upgrade_candidates, analyze_distribution
from lib import spec
from lib import checks
```

**注意**：运行脚本时需确保工作目录或 sys.path 包含 `.agents/scripts/` 目录。
现有脚本通过在文件开头添加以下代码实现：
```python
import sys
from pathlib import Path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
```

## 模块索引
"""

from lib.project import resolve_project_root, resolve_agents_dir, resolve_scripts_dir
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, extract_all_fields, parse_toml_frontmatter_as_dict, parse_yaml_frontmatter, extract_yaml_field, extract_frontmatter_field_from_file
from lib.markdown import find_markdown_files, extract_title, extract_description, parse_inline_links, update_marker_region
from lib.link_fixer import (
    LinkFix, fix_file_links, fix_directory_links, fix_link_url,
    find_file_in_project, compute_relative_path, apply_filename_mapping,
    apply_line_remap, print_fix_report, parse_file_url, is_code_fence_context,
    fix_broken_links, INLINE_LINK_RE,
)
from lib import patterns
from lib import spec
from lib import checks
from lib import rules
from lib import powershell


def generate_api_docs() -> str:
    """生成 API 参考文档 Markdown 内容。"""
    sections = []

    sections.append("# .agents/scripts/lib/ API 参考\n")
    sections.append("> 本文档由 `lib/__init__.py` 中的 `generate_api_docs()` 自动生成，描述共享库所有公开模块和函数。\n")
    sections.append("## 目录\n")
    sections.append("- [lib.project — 项目路径解析](#libproject--项目路径解析)")
    sections.append("- [lib.cli — CLI 输出格式化](#libcli--cli-输出格式化)")
    sections.append("- [lib.frontmatter — Frontmatter 解析](#libfrontmatter--frontmatter-解析)")
    sections.append("- [lib.markdown — Markdown 文件处理](#libmarkdown--markdown-文件处理)")
    sections.append("- [lib.link_fixer — 链接修复](#liblink_fixer--链接修复)")
    sections.append("- [lib.patterns — 模式成熟度分析](#libpatterns--模式成熟度分析)")
    sections.append("- [lib.spec — Spec 文档处理](#libspec--spec-文档处理)")
    sections.append("- [lib.checks — 检查器框架](#libchecks--检查器框架)")
    sections.append("- [lib.rules — 误报过滤规则引擎](#librules--误报过滤规则引擎)")
    sections.append("- [lib.powershell — PowerShell脚本编码工具](#libpowershell--powershell脚本编码工具)")
    sections.append("- [constants.py — 常量定义](#constantspy--常量定义)\n")

    # lib.project
    sections.append("---\n")
    sections.append("## lib.project — 项目路径解析\n")
    sections.append("| 函数 | 签名 | 说明 |")
    sections.append("|------|------|------|")
    sections.append("| `resolve_project_root` | `(anchor: str \\| Path) -> Path` | 从锚点位置向上查找工程根目录（含 AGENTS.md） |")
    sections.append("| `resolve_agents_dir` | `(anchor: str \\| Path) -> Path` | 解析 `.agents/` 目录路径 |")
    sections.append("| `resolve_scripts_dir` | `(anchor: str \\| Path) -> Path` | 解析 `.agents/scripts/` 目录路径 |\n")
    sections.append("**示例**：\n")
    sections.append("```python")
    sections.append("from lib.project import resolve_project_root")
    sections.append("root = resolve_project_root(__file__)  # 返回项目根目录 Path")
    sections.append("```\n")

    # lib.cli
    sections.append("---\n")
    sections.append("## lib.cli — CLI 输出格式化\n")
    sections.append("| 函数 | 签名 | 说明 |")
    sections.append("|------|------|------|")
    sections.append("| `print_pass` | `(msg: str) -> None` | 打印绿色 [PASS] 通过信息 |")
    sections.append("| `print_warn` | `(msg: str) -> None` | 打印黄色 [WARN] 警告信息 |")
    sections.append("| `print_error` | `(msg: str) -> None` | 打印红色 [FAIL] 错误信息 |")
    sections.append("| `print_header` | `(title: str, width: int = 60) -> None` | 打印等宽分隔标题行 |")
    sections.append("| `print_summary` | `(pass_count: int, warn_count: int, error_count: int, width: int = 60) -> None` | 打印彩色检查摘要（通过/警告/错误） |")
    sections.append("| `add_common_args` | `(parser: ArgumentParser) -> None` | 注册通用 CLI 参数（--path、--json） |\n")
    sections.append("**示例**：\n")
    sections.append("```python")
    sections.append("from lib.cli import print_pass, print_warn, print_header, add_common_args")
    sections.append("import argparse")
    sections.append("")
    sections.append("parser = argparse.ArgumentParser(description='我的检查脚本')")
    sections.append("add_common_args(parser)  # 自动添加 --path 和 --json")
    sections.append("args = parser.parse_args()")
    sections.append("print_header('开始检查')")
    sections.append("print_pass('文件格式正确')")
    sections.append("print_summary(pass_count=5, warn_count=1, error_count=0)")
    sections.append("```\n")

    # lib.frontmatter
    sections.append("---\n")
    sections.append("## lib.frontmatter — Frontmatter 解析\n")
    sections.append("解析 Markdown 文件头部的 frontmatter 元数据块，支持 TOML（`+++ ... +++`）和 YAML（`--- ... ---`）两种格式。\n")
    sections.append("| 函数 | 签名 | 说明 |")
    sections.append("|------|------|------|")
    sections.append("| `parse_toml_frontmatter` | `(file_path: str \\| Path) -> str \\| None` | 读取文件并返回 TOML frontmatter 纯文本（不含 +++） |")
    sections.append("| `extract_frontmatter_field` | `(frontmatter: str, field_name: str) -> str \\| None` | 从 frontmatter 文本中提取指定字段值（支持带引号/无引号） |")
    sections.append("| `extract_all_fields` | `(frontmatter: str) -> dict[str, str]` | 提取 frontmatter 中所有字段为字典 |")
    sections.append("| `parse_toml_frontmatter_as_dict` | `(file_path: str \\| Path) -> dict[str, str] \\| None` | 一步读取文件并解析所有 frontmatter 字段为字典（便捷函数，等价于 parse + extract_all_fields） |")
    sections.append("| `parse_yaml_frontmatter` | `(file_path: str \\| Path) -> str \\| None` | 读取文件并返回 YAML frontmatter 纯文本（不含 ---） |")
    sections.append("| `extract_yaml_field` | `(frontmatter: str, field_name: str) -> str \\| None` | 从 YAML frontmatter 文本中提取指定标量字段值（支持双引号/单引号/无引号） |")
    sections.append("| `extract_frontmatter_field_from_file` | `(file_path: str \\| Path, field_name: str) -> str \\| None` | 从文件提取 frontmatter 字段值，自动识别 TOML/YAML 格式 |\n")
    sections.append("**示例**：\n")
    sections.append("```python")
    sections.append("from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, parse_yaml_frontmatter, extract_yaml_field, extract_frontmatter_field_from_file")
    sections.append("# TOML frontmatter（.agents/ 文档常用）")
    sections.append("fm = parse_toml_frontmatter('docs/retrospective/patterns/mypattern.md')")
    sections.append("if fm:")
    sections.append("    maturity = extract_frontmatter_field(fm, 'maturity')  # 'L2'")
    sections.append("# YAML frontmatter（docs/knowledge/ 文档常用）")
    sections.append("yaml_fm = parse_yaml_frontmatter('docs/knowledge/three-layer-routing.md')")
    sections.append("if yaml_fm:")
    sections.append("    source = extract_yaml_field(yaml_fm, 'source')  # 'vendor/AGENTS.md#三层路由流程图'")
    sections.append("# 统一入口：自动识别 TOML/YAML 格式（推荐用于扫描混合文档库）")
    sections.append("source = extract_frontmatter_field_from_file('path/to/file.md', 'source')")
    sections.append("```\n")

    # lib.markdown
    sections.append("---\n")
    sections.append("## lib.markdown — Markdown 文件处理\n")
    sections.append("| 函数 | 签名 | 说明 |")
    sections.append("|------|------|------|")
    sections.append("| `find_markdown_files` | `(root: Path, exclude_dirs=None) -> list[Path]` | 递归查找 Markdown 文件，默认排除系统目录 |")
    sections.append("| `extract_title` | `(path: Path \\| str) -> str` | 提取首个一级标题（# Title）文本 |")
    sections.append("| `extract_description` | `(path: Path \\| str) -> str` | 提取标题下首行描述文本 |")
    sections.append("| `parse_inline_links` | `(content: str) -> list[tuple[str, str]]` | 提取所有内联链接，返回 [(text, url), ...] |")
    sections.append("| `update_marker_region` | `(file_path, marker_start, marker_end, new_content) -> None` | 替换 HTML 注释标记之间的内容 |\n")
    sections.append("**常量**：\n")
    sections.append("- `TITLE_RE` — 一级标题正则")
    sections.append("- `DESC_RE` — 描述段落正则\n")
    sections.append("**示例**：\n")
    sections.append("```python")
    sections.append("from lib.markdown import find_markdown_files, extract_title, update_marker_region")
    sections.append("md_files = find_markdown_files(root_dir)")
    sections.append("for f in md_files:")
    sections.append("    title = extract_title(f)")
    sections.append("# 更新自动生成区域")
    sections.append("update_marker_region('README.md', '<!-- AUTO-START -->', '<!-- AUTO-END -->', new_content)")
    sections.append("```\n")

    # lib.link_fixer
    sections.append("---\n")
    sections.append("## lib.link_fixer — 链接修复\n")
    sections.append("提供 Markdown 内联链接的解析、有效性校验、自动修复能力。\n")
    sections.append("| 函数/类 | 签名 | 说明 |")
    sections.append("|---------|------|------|")
    sections.append("| `INLINE_LINK_RE` | `Pattern` | 内联链接正则 `[text](url)` |")
    sections.append("| `LinkFix` | `class` | 链接修复结果数据类（source, target, new_url, fix_type, line） |")
    sections.append("| `parse_file_url` | `(url: str) -> tuple[str, str]` | 解析 file:/// URL 为 (file_path, anchor) |")
    sections.append("| `find_file_in_project` | `(url_path, project_root, ...) -> list[Path]` | 在项目中模糊查找目标文件 |")
    sections.append("| `compute_relative_path` | `(source_file: Path, target_file: Path) -> str` | 计算源文件到目标文件的相对路径 |")
    sections.append("| `fix_file_links` | `(source_file, project_root, dry_run, ...) -> list[LinkFix]` | 修复单个文件中的链接 |")
    sections.append("| `fix_directory_links` | `(dir_path, project_root, dry_run, ...) -> list[LinkFix]` | 修复目录下所有 Markdown 文件的链接 |")
    sections.append("| `fix_link_url` | `(text, url, source_file, project_root, ...) -> LinkFix \\| None` | 修复单个链接 URL |")
    sections.append("| `is_code_fence_context` | `(content: str, pos: int) -> bool` | 判断位置是否在代码块内 |")
    sections.append("| `apply_filename_mapping` | `(file_path, rename_map) -> str` | 应用文件重命名映射 |")
    sections.append("| `apply_line_remap` | `(anchor, line_remap, source_filename) -> str` | 应用行号重映射 |")
    sections.append("| `print_fix_report` | `(fixes: list[LinkFix], dry_run: bool) -> None` | 打印链接修复报告 |")
    sections.append("| `fix_broken_links` | `(source_path, project_root, ...) -> list[LinkFix]` | 批量修复断链（综合入口） |\n")

    # lib.patterns
    sections.append("---\n")
    sections.append("## lib.patterns — 模式成熟度分析\n")
    sections.append("提供模式文件扫描、frontmatter 解析、成熟度分类、分布统计、README 统计表解析与更新能力。\n")
    sections.append("| 常量 | 说明 |")
    sections.append("|------|------|")
    sections.append("| `REQUIRED_FIELDS` | 模式文件必填字段列表（id/domain/layer/maturity/validation_count/reuse_count/documentation_level/source） |")
    sections.append("| `MATURITY_LEVELS` | 成熟度等级：['L1', 'L2', 'L3', 'L4'] |")
    sections.append("| `PATTERN_DOMAINS` | 模式子域：['methodology-patterns', 'code-patterns', 'architecture-patterns'] |")
    sections.append("| `EXCLUDED_FILENAMES` | 排除文件名：{'README.md', 'CATEGORIES.md'} |\n")
    sections.append("| 函数 | 签名 | 说明 |")
    sections.append("|------|------|------|")
    sections.append("| `parse_pattern_frontmatter` | `(filepath) -> dict \\| None` | 解析模式文件 frontmatter，返回结构化字典（含 int 类型转换） |")
    sections.append("| `scan_patterns` | `(base_dir) -> tuple[list, list]` | 递归扫描所有模式文件，返回 (patterns, issues) |")
    sections.append("| `classify_pattern` | `(pattern) -> str` | 分类模式状态：'upgrade'/'anomaly'/'ok' |")
    sections.append("| `analyze_distribution` | `(patterns) -> tuple[dict, dict]` | 分析成熟度分布与各子域分布 |")
    sections.append("| `find_upgrade_candidates` | `(patterns) -> dict` | 找出待升级模式：{'L1_to_L2': [...], 'L2_to_L3': [...]} |")
    sections.append("| `count_patterns` | `(dir_path) -> int` | 统计目录中模式文件数（递归，排除README/CATEGORIES） |")
    sections.append("| `grep_maturity_per_directory` | `(patterns_root) -> dict` | 按目录统计成熟度分布 |")
    sections.append("| `parse_readme_stats_table` | `(readme_path) -> dict` | 解析 patterns/README.md 统计表 |")
    sections.append("| `parse_readme_index_table` | `(readme_path) -> OrderedDict` | 解析 patterns/README.md 索引表 |")
    sections.append("| `check_stats_consistency` | `(patterns_root, readme_path) -> list` | 比对 grep 统计与 README 声明的差异 |")
    sections.append("| `update_readme_index_table` | `(readme_path, declared_stats, actual_counts) -> str` | 更新 README 索引表中的统计数字，返回新内容 |")
    sections.append("| `build_report_data` | `(patterns, issues) -> dict` | 构建统一报告数据（供 stats 子命令使用） |\n")

    # lib.spec
    sections.append("---\n")
    sections.append("## lib.spec — Spec 文档处理\n")
    sections.append("提供 Spec 文件（spec.md / tasks.md / checklist.md）的解析、一致性检查与报告生成能力。\n")
    sections.append("| 子模块 | 说明 |")
    sections.append("|--------|------|")
    sections.append("| `lib.spec.parsers` | Spec 文档解析器：`parse_spec()`、`parse_tasks()`、`parse_checklist()` |")
    sections.append("| `lib.spec.models` | Spec 数据模型：`SpecDoc`、`TaskItem`、`CheckItem` 等 |")
    sections.append("| `lib.spec.consistency_checkers` | 一致性检查器 |")
    sections.append("| `lib.spec.format_checkers` | 格式检查器 |")
    sections.append("| `lib.spec.reporters` | 检查报告生成器 |")
    sections.append("| `lib.spec.utils` | 工具函数：`discover_spec_dirs()` 等 |\n")
    sections.append("**主要入口函数**：\n")
    sections.append("```python")
    sections.append("from lib.spec.utils import discover_spec_dirs")
    sections.append("from lib.spec.parsers import parse_spec, parse_tasks, parse_checklist")
    sections.append("spec_dirs = discover_spec_dirs(root)  # 发现所有 .trae/specs/ 下的 spec 目录")
    sections.append("```\n")

    # lib.checks
    sections.append("---\n")
    sections.append("## lib.checks — 检查器框架\n")
    sections.append("提供统一的检查器基类和内置检查器实现。\n")
    sections.append("| 子模块 | 说明 |")
    sections.append("|--------|------|")
    sections.append("| `lib.checks.base` | 检查器基类 `BaseChecker` |")
    sections.append("| `lib.checks.filename` | 文件名规范检查 |")
    sections.append("| `lib.checks.gitignore` | .gitignore 规则检查 |")
    sections.append("| `lib.checks.mermaid` | Mermaid 语法检查 |")
    sections.append("| `lib.checks.roles` | 角色权限检查 |")
    sections.append("| `lib.checks.vendor` | vendor 目录合规性检查 |\n")

    # lib.rules
    sections.append("---\n")
    sections.append("## lib.rules — 误报过滤规则引擎\n")
    sections.append("从 `config/false-positive-rules.toml` 加载通用误报过滤规则，提供四层过滤能力（路径排除/文件标记/块过滤/行过滤），供所有 linter/checker 复用。\n")
    sections.append("| 函数/类 | 签名 | 说明 |")
    sections.append("|---------|------|------|")
    sections.append("| `load_rules` | `(rules_file: Path \\| str \\| None = None) -> FalsePositiveRules` | 加载误报过滤规则（默认加载 config/false-positive-rules.toml） |")
    sections.append("| `FalsePositiveRules` | `dataclass` | 规则集合，提供各类过滤判断方法 |")
    sections.append("| `FalsePositiveRules.should_exclude_dir` | `(dir_name: str) -> bool` | 判断目录名是否应排除 |")
    sections.append("| `FalsePositiveRules.should_exclude_file` | `(file_name: str) -> bool` | 判断文件名是否应排除 |")
    sections.append("| `FalsePositiveRules.should_exclude_path` | `(rel_path) -> bool` | 判断路径是否命中正则排除 |")
    sections.append("| `FalsePositiveRules.is_marked_file` | `(file_path: Path) -> tuple[bool, str]` | 判断文件是否有排除标记（兼容包装/自动生成/第三方） |")
    sections.append("| `FalsePositiveRules.is_excluded_line` | `(normalized_line: str) -> bool` | 判断归一化行是否应过滤 |")
    sections.append("| `FalsePositiveRules.is_excluded_block` | `(normalized_lines: list[str]) -> tuple[bool, str]` | 判断代码块是否为样板误报 |")
    sections.append("| `FalsePositiveRules.filter_lines` | `(lines: list[tuple[int,str]]) -> list[tuple[int,str]]` | 过滤归一化行列表中的排除行 |")
    sections.append("| `FalsePositiveRules.should_skip_file` | `(file_path, root_dir=None) -> tuple[bool, str]` | 综合判断文件是否应跳过（路径+文件名+标记三检查） |\n")
    sections.append("**规则文件位置**：`config/false-positive-rules.toml`（TOML格式，四层过滤规则）\n")
    sections.append("**示例**：\n")
    sections.append("```python")
    sections.append("from lib.rules import load_rules")
    sections.append("")
    sections.append("rules = load_rules()  # 加载默认规则")
    sections.append("")
    sections.append("# 文件扫描时跳过排除项")
    sections.append("for py_file in scripts_dir.rglob('*.py'):")
    sections.append("    should_skip, reason = rules.should_skip_file(py_file, root_dir=scripts_dir)")
    sections.append("    if should_skip:")
    sections.append("        continue")
    sections.append("    # ... 处理文件")
    sections.append("")
    sections.append("# 归一化时过滤样板行")
    sections.append("norm_lines = rules.filter_lines(norm_lines)")
    sections.append("")
    sections.append("# 块级别过滤（如 import 样板块）")
    sections.append("is_bp, reason = rules.is_excluded_block(block_normalized_lines)")
    sections.append("if is_bp:")
    sections.append("    continue  # 跳过样板误报")
    sections.append("```\n")

    # lib.powershell
    sections.append("---\n")
    sections.append("## lib.powershell — PowerShell脚本编码工具\n")
    sections.append("Windows PowerShell 5.x 要求 .ps1 脚本使用 UTF-8 BOM + CRLF 换行，否则含中文时可能报语法错误。本模块提供写入、验证、修复能力。\n")
    sections.append("| 函数 | 签名 | 说明 |")
    sections.append("|---------|------|------|")
    sections.append("| `write_ps1_script` | `(file_path, content, *, add_bom=True, newline='\\r\\n') -> Path` | 以PS兼容编码（UTF-8 BOM + CRLF）写入.ps1文件 |")
    sections.append("| `verify_ps1_encoding` | `(file_path) -> tuple[bool, list[str]]` | 验证.ps1文件编码是否合规，返回(是否合规, 问题列表) |")
    sections.append("| `fix_ps1_encoding` | `(file_path) -> tuple[bool, list[str]]` | 修复编码问题（添加BOM、统一CRLF），返回(是否修复, 变更列表) |\n")
    sections.append("**示例**：\n")
    sections.append("```python")
    sections.append("from lib.powershell import write_ps1_script, verify_ps1_encoding")
    sections.append("")
    sections.append("# 写入新的.ps1文件（自动BOM+CRLF，PS5/PS7均兼容）")
    sections.append("write_ps1_script('scripts/build.ps1', '''")
    sections.append("Write-Host 'Hello World'")
    sections.append("$x = 1")
    sections.append("''')")
    sections.append("")
    sections.append("# 验证已有.ps1文件")
    sections.append("ok, issues = verify_ps1_encoding('ci-check.ps1')")
    sections.append("if not ok:")
    sections.append("    print(f'编码问题: {issues}')")
    sections.append("```\n")

    # constants.py (scripts root level, not in lib/)
    sections.append("---\n")
    sections.append("## constants.py — 全局常量（scripts/ 根目录）\n")
    sections.append("位于 `.agents/scripts/constants.py`，全局共享常量模块，供所有脚本和 lib/ 模块引用。\n")
    sections.append("导入方式：`from constants import EXCLUDED_DIRS, ANSI_GREEN, ...`\n")
    sections.append("| 常量 | 类型 | 说明 |")
    sections.append("|------|------|------|")
    sections.append("| `ANSI_GREEN/ANSI_YELLOW/ANSI_RED/ANSI_CYAN/ANSI_RESET` | str | ANSI 颜色代码 |")
    sections.append("| `EXCLUDED_DIRS` | set[str] | 文件扫描默认排除目录（.git/vendor/.venv/__pycache__/node_modules/.temp） |")
    sections.append("| `REQUIRED_RULES` / `TEMP_PATHS` | list | .gitignore 必需规则与临时路径 |")
    sections.append("| `LINK_CHECK_*` | - | check-links.py 默认参数（timeout/workers/user-agent等） |")
    sections.append("| `VALID_TIERS` / `ROLE_EXCLUDED_FILES` | - | 角色权限校验常量 |")
    sections.append("| `SPEC_MATCH_THRESHOLD` / `META_DOC_KEYWORDS` | - | Spec 一致性检查参数 |")
    sections.append("| `SCAN_DIRS` / `TARGETS` / `MANUAL_DESCRIPTIONS` | - | 导航生成器配置 |")

    sections.append("\n---\n")
    sections.append("## 新增脚本开发流程\n")
    sections.append("新建 `.agents/scripts/` 下的脚本前，请遵循以下流程：\n")
    sections.append("1. **先查本文件**，确认 lib/ 是否已有可复用的函数")
    sections.append("2. **优先使用共享函数**，避免重复实现相同逻辑")
    sections.append("3. 如确需新功能，先考虑是否应提取到 lib/ 供其他脚本复用")
    sections.append("4. 脚本头部添加 sys.path 设置：")
    sections.append("```python")
    sections.append("import sys")
    sections.append("from pathlib import Path")
    sections.append("SCRIPTS_DIR = Path(__file__).resolve().parent")
    sections.append("if str(SCRIPTS_DIR) not in sys.path:")
    sections.append("    sys.path.insert(0, str(SCRIPTS_DIR))")
    sections.append("```")
    sections.append("5. 使用 `add_common_args(parser)` 注册通用参数（--path/--json）")
    sections.append("6. 使用 `print_pass/print_warn/print_error/print_summary` 输出检查结果")
    sections.append("7. 完成后运行 `python check-duplication.py` 检查是否引入新的重复代码\n")

    return "\n".join(sections)


if __name__ == "__main__":
    print(generate_api_docs())
