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

import sys
import argparse
from pathlib import Path

if __package__ in (None, ""):
    SCRIPTS_DIR = Path(__file__).resolve().parents[1]
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))

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
from lib import process
from lib import quality_rules
from lib import quality_report


_MODULES = None


def _get_modules():
    global _MODULES
    if _MODULES is not None:
        return _MODULES

    modules = []

    modules.append({
        "num": 1,
        "slug": "project",
        "title": "lib.project — 项目路径解析",
        "filename": "01-project.md",
        "body": [
            "| 函数 | 签名 | 说明 |",
            "|------|------|------|",
            "| `resolve_project_root` | `(anchor: str \\| Path) -> Path` | 从锚点位置向上查找工程根目录（含 AGENTS.md） |",
            "| `resolve_agents_dir` | `(anchor: str \\| Path) -> Path` | 解析 `.agents/` 目录路径 |",
            "| `resolve_scripts_dir` | `(anchor: str \\| Path) -> Path` | 解析 `.agents/scripts/` 目录路径 |\n",
            "**示例**：\n",
            "```python",
            "from lib.project import resolve_project_root",
            "root = resolve_project_root(__file__)  # 返回项目根目录 Path",
            "```\n",
        ],
    })

    modules.append({
        "num": 2,
        "slug": "cli",
        "title": "lib.cli — CLI 输出格式化",
        "filename": "02-cli.md",
        "body": [
            "| 函数 | 签名 | 说明 |",
            "|------|------|------|",
            "| `print_pass` | `(msg: str) -> None` | 打印绿色 [PASS] 通过信息 |",
            "| `print_warn` | `(msg: str) -> None` | 打印黄色 [WARN] 警告信息 |",
            "| `print_error` | `(msg: str) -> None` | 打印红色 [FAIL] 错误信息 |",
            "| `print_header` | `(title: str, width: int = 60) -> None` | 打印等宽分隔标题行 |",
            "| `print_summary` | `(pass_count: int, warn_count: int, error_count: int, width: int = 60) -> None` | 打印彩色检查摘要（通过/警告/错误） |",
            "| `add_common_args` | `(parser: ArgumentParser) -> None` | 注册通用 CLI 参数（--path、--json） |\n",
            "**示例**：\n",
            "```python",
            "from lib.cli import print_pass, print_warn, print_header, add_common_args",
            "import argparse",
            "",
            "parser = argparse.ArgumentParser(description='我的检查脚本')",
            "add_common_args(parser)  # 自动添加 --path 和 --json",
            "args = parser.parse_args()",
            "print_header('开始检查')",
            "print_pass('文件格式正确')",
            "print_summary(pass_count=5, warn_count=1, error_count=0)",
            "```\n",
        ],
    })

    modules.append({
        "num": 3,
        "slug": "frontmatter",
        "title": "lib.frontmatter — Frontmatter 解析",
        "filename": "03-frontmatter.md",
        "body": [
            "解析 Markdown 文件头部的 frontmatter 元数据块，支持 TOML（`+++ ... +++`）和 YAML（`--- ... ---`）两种格式。\n",
            "| 函数 | 签名 | 说明 |",
            "|------|------|------|",
            "| `parse_toml_frontmatter` | `(file_path: str \\| Path) -> str \\| None` | 读取文件并返回 TOML frontmatter 纯文本（不含 +++） |",
            "| `extract_frontmatter_field` | `(frontmatter: str, field_name: str) -> str \\| None` | 从 frontmatter 文本中提取指定字段值（支持带引号/无引号） |",
            "| `extract_all_fields` | `(frontmatter: str) -> dict[str, str]` | 提取 frontmatter 中所有字段为字典 |",
            "| `parse_toml_frontmatter_as_dict` | `(file_path: str \\| Path) -> dict[str, str] \\| None` | 一步读取文件并解析所有 frontmatter 字段为字典（便捷函数，等价于 parse + extract_all_fields） |",
            "| `parse_yaml_frontmatter` | `(file_path: str \\| Path) -> str \\| None` | 读取文件并返回 YAML frontmatter 纯文本（不含 ---） |",
            "| `extract_yaml_field` | `(frontmatter: str, field_name: str) -> str \\| None` | 从 YAML frontmatter 文本中提取指定标量字段值（支持双引号/单引号/无引号） |",
            "| `extract_frontmatter_field_from_file` | `(file_path: str \\| Path, field_name: str) -> str \\| None` | 从文件提取 frontmatter 字段值，自动识别 TOML/YAML 格式 |\n",
            "**示例**：\n",
            "```python",
            "from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, parse_yaml_frontmatter, extract_yaml_field, extract_frontmatter_field_from_file",
            "# TOML frontmatter（.agents/ 文档常用）",
            "fm = parse_toml_frontmatter('docs/retrospective/patterns/mypattern.md')",
            "if fm:",
            "    maturity = extract_frontmatter_field(fm, 'maturity')  # 'L2'",
            "# YAML frontmatter（docs/knowledge/ 文档常用）",
            "yaml_fm = parse_yaml_frontmatter('docs/knowledge/three-layer-routing.md')",
            "if yaml_fm:",
            "    source = extract_yaml_field(yaml_fm, 'source')  # 'vendor/AGENTS.md#三层路由流程图'",
            "# 统一入口：自动识别 TOML/YAML 格式（推荐用于扫描混合文档库）",
            "source = extract_frontmatter_field_from_file('path/to/file.md', 'source')",
            "```\n",
        ],
    })

    modules.append({
        "num": 4,
        "slug": "markdown",
        "title": "lib.markdown — Markdown 文件处理",
        "filename": "04-markdown.md",
        "body": [
            "| 函数 | 签名 | 说明 |",
            "|------|------|------|",
            "| `find_markdown_files` | `(root: Path, exclude_dirs=None) -> list[Path]` | 递归查找 Markdown 文件，默认排除系统目录 |",
            "| `extract_title` | `(path: Path \\| str) -> str` | 提取首个一级标题（# Title）文本 |",
            "| `extract_description` | `(path: Path \\| str) -> str` | 提取标题下首行描述文本 |",
            "| `parse_inline_links` | `(content: str) -> list[tuple[str, str]]` | 提取所有内联链接，返回 [(text, url), ...] |",
            "| `update_marker_region` | `(file_path, marker_start, marker_end, new_content) -> None` | 替换 HTML 注释标记之间的内容 |\n",
            "**常量**：\n",
            "- `TITLE_RE` — 一级标题正则",
            "- `DESC_RE` — 描述段落正则\n",
            "**示例**：\n",
            "```python",
            "from lib.markdown import find_markdown_files, extract_title, update_marker_region",
            "md_files = find_markdown_files(root_dir)",
            "for f in md_files:",
            "    title = extract_title(f)",
            "# 更新自动生成区域",
            "update_marker_region('README.md', '<!-- AUTO-START -->', '<!-- AUTO-END -->', new_content)",
            "```\n",
        ],
    })

    modules.append({
        "num": 5,
        "slug": "link_fixer",
        "title": "lib.link_fixer — 链接修复",
        "filename": "05-link-fixer.md",
        "body": [
            "提供 Markdown 内联链接的解析、有效性校验、自动修复能力。\n",
            "| 函数/类 | 签名 | 说明 |",
            "|---------|------|------|",
            "| `INLINE_LINK_RE` | `Pattern` | 内联链接正则 `[text](url)` |",
            "| `LinkFix` | `class` | 链接修复结果数据类（source, target, new_url, fix_type, line） |",
            "| `parse_file_url` | `(url: str) -> tuple[str, str]` | 解析 file:/// URL 为 (file_path, anchor) |",
            "| `find_file_in_project` | `(url_path, project_root, ...) -> list[Path]` | 在项目中模糊查找目标文件 |",
            "| `compute_relative_path` | `(source_file: Path, target_file: Path) -> str` | 计算源文件到目标文件的相对路径 |",
            "| `fix_file_links` | `(source_file, project_root, dry_run, ...) -> list[LinkFix]` | 修复单个文件中的链接 |",
            "| `fix_directory_links` | `(dir_path, project_root, dry_run, ...) -> list[LinkFix]` | 修复目录下所有 Markdown 文件的链接 |",
            "| `fix_link_url` | `(text, url, source_file, project_root, ...) -> LinkFix \\| None` | 修复单个链接 URL |",
            "| `is_code_fence_context` | `(content: str, pos: int) -> bool` | 判断位置是否在代码块内 |",
            "| `apply_filename_mapping` | `(file_path, rename_map) -> str` | 应用文件重命名映射 |",
            "| `apply_line_remap` | `(anchor, line_remap, source_filename) -> str` | 应用行号重映射 |",
            "| `print_fix_report` | `(fixes: list[LinkFix], dry_run: bool) -> None` | 打印链接修复报告 |",
            "| `fix_broken_links` | `(source_path, project_root, ...) -> list[LinkFix]` | 批量修复断链（综合入口） |\n",
        ],
    })

    modules.append({
        "num": 6,
        "slug": "patterns",
        "title": "lib.patterns — 模式成熟度分析",
        "filename": "06-patterns.md",
        "body": [
            "提供模式文件扫描、frontmatter 解析、成熟度分类、分布统计、README 统计表解析与更新能力。\n",
            "| 常量 | 说明 |",
            "|------|------|",
            "| `REQUIRED_FIELDS` | 模式文件必填字段列表（id/domain/layer/maturity/validation_count/reuse_count/documentation_level/source） |",
            "| `MATURITY_LEVELS` | 成熟度等级：['L1', 'L2', 'L3', 'L4'] |",
            "| `PATTERN_DOMAINS` | 模式子域：['methodology-patterns', 'code-patterns', 'architecture-patterns'] |",
            "| `EXCLUDED_FILENAMES` | 排除文件名：{'README.md', 'CATEGORIES.md'} |\n",
            "| 函数 | 签名 | 说明 |",
            "|------|------|------|",
            "| `parse_pattern_frontmatter` | `(filepath) -> dict \\| None` | 解析模式文件 frontmatter，返回结构化字典（含 int 类型转换） |",
            "| `scan_patterns` | `(base_dir) -> tuple[list, list]` | 递归扫描所有模式文件，返回 (patterns, issues) |",
            "| `classify_pattern` | `(pattern) -> str` | 分类模式状态：'upgrade'/'anomaly'/'ok' |",
            "| `analyze_distribution` | `(patterns) -> tuple[dict, dict]` | 分析成熟度分布与各子域分布 |",
            "| `find_upgrade_candidates` | `(patterns) -> dict` | 找出待升级模式：{'L1_to_L2': [...], 'L2_to_L3': [...]} |",
            "| `count_patterns` | `(dir_path) -> int` | 统计目录中模式文件数（递归，排除README/CATEGORIES） |",
            "| `grep_maturity_per_directory` | `(patterns_root) -> dict` | 按目录统计成熟度分布 |",
            "| `parse_readme_stats_table` | `(readme_path) -> dict` | 解析 patterns/README.md 统计表 |",
            "| `parse_readme_index_table` | `(readme_path) -> OrderedDict` | 解析 patterns/README.md 索引表 |",
            "| `check_stats_consistency` | `(patterns_root, readme_path) -> list` | 比对 grep 统计与 README 声明的差异 |",
            "| `update_readme_index_table` | `(readme_path, declared_stats, actual_counts) -> str` | 更新 README 索引表中的统计数字，返回新内容 |",
            "| `build_report_data` | `(patterns, issues) -> dict` | 构建统一报告数据（供 stats 子命令使用） |\n",
        ],
    })

    modules.append({
        "num": 7,
        "slug": "spec",
        "title": "lib.spec — Spec 文档处理",
        "filename": "07-spec.md",
        "body": [
            "提供 Spec 文件（spec.md / tasks.md / checklist.md）的解析、一致性检查与报告生成能力。\n",
            "| 子模块 | 说明 |",
            "|--------|------|",
            "| `lib.spec.parsers` | Spec 文档解析器：`parse_spec()`、`parse_tasks()`、`parse_checklist()` |",
            "| `lib.spec.models` | Spec 数据模型：`SpecDoc`、`TaskItem`、`CheckItem` 等 |",
            "| `lib.spec.consistency_checkers` | 一致性检查器 |",
            "| `lib.spec.format_checkers` | 格式检查器 |",
            "| `lib.spec.reporters` | 检查报告生成器 |",
            "| `lib.spec.utils` | 工具函数：`discover_spec_dirs()` 等 |\n",
            "**主要入口函数**：\n",
            "```python",
            "from lib.spec.utils import discover_spec_dirs",
            "from lib.spec.parsers import parse_spec, parse_tasks, parse_checklist",
            "spec_dirs = discover_spec_dirs(root)  # 发现所有 .trae/specs/ 下的 spec 目录",
            "```\n",
        ],
    })

    modules.append({
        "num": 8,
        "slug": "checks",
        "title": "lib.checks — 检查器框架",
        "filename": "08-checks.md",
        "body": [
            "提供统一的检查器基类和内置检查器实现。\n",
            "| 子模块 | 说明 |",
            "|--------|------|",
            "| `lib.checks.base` | 检查器基类 `BaseChecker` |",
            "| `lib.checks.filename` | 文件名规范检查 |",
            "| `lib.checks.gitignore` | .gitignore 规则检查 |",
            "| `lib.checks.mermaid` | Mermaid 语法检查 |",
            "| `lib.checks.roles` | 角色权限检查 |",
            "| `lib.checks.vendor` | vendor 目录合规性检查 |\n",
        ],
    })

    modules.append({
        "num": 9,
        "slug": "rules",
        "title": "lib.rules — 误报过滤规则引擎",
        "filename": "09-rules.md",
        "body": [
            "从 `config/false-positive-rules.toml` 加载通用误报过滤规则，提供四层过滤能力（路径排除/文件标记/块过滤/行过滤），供所有 linter/checker 复用。\n",
            "| 函数/类 | 签名 | 说明 |",
            "|---------|------|------|",
            "| `load_rules` | `(rules_file: Path \\| str \\| None = None) -> FalsePositiveRules` | 加载误报过滤规则（默认加载 config/false-positive-rules.toml） |",
            "| `FalsePositiveRules` | `dataclass` | 规则集合，提供各类过滤判断方法 |",
            "| `FalsePositiveRules.should_exclude_dir` | `(dir_name: str) -> bool` | 判断目录名是否应排除 |",
            "| `FalsePositiveRules.should_exclude_file` | `(file_name: str) -> bool` | 判断文件名是否应排除 |",
            "| `FalsePositiveRules.should_exclude_path` | `(rel_path) -> bool` | 判断路径是否命中正则排除 |",
            "| `FalsePositiveRules.is_marked_file` | `(file_path: Path) -> tuple[bool, str]` | 判断文件是否有排除标记（兼容包装/自动生成/第三方） |",
            "| `FalsePositiveRules.is_excluded_line` | `(normalized_line: str) -> bool` | 判断归一化行是否应过滤 |",
            "| `FalsePositiveRules.is_excluded_block` | `(normalized_lines: list[str]) -> tuple[bool, str]` | 判断代码块是否为样板误报 |",
            "| `FalsePositiveRules.filter_lines` | `(lines: list[tuple[int,str]]) -> list[tuple[int,str]]` | 过滤归一化行列表中的排除行 |",
            "| `FalsePositiveRules.should_skip_file` | `(file_path, root_dir=None) -> tuple[bool, str]` | 综合判断文件是否应跳过（路径+文件名+标记三检查） |\n",
            "**规则文件位置**：`config/false-positive-rules.toml`（TOML格式，四层过滤规则）\n",
            "**示例**：\n",
            "```python",
            "from lib.rules import load_rules",
            "",
            "rules = load_rules()  # 加载默认规则",
            "",
            "# 文件扫描时跳过排除项",
            "for py_file in scripts_dir.rglob('*.py'):",
            "    should_skip, reason = rules.should_skip_file(py_file, root_dir=scripts_dir)",
            "    if should_skip:",
            "        continue",
            "    # ... 处理文件",
            "",
            "# 归一化时过滤样板行",
            "norm_lines = rules.filter_lines(norm_lines)",
            "",
            "# 块级别过滤（如 import 样板块）",
            "is_bp, reason = rules.is_excluded_block(block_normalized_lines)",
            "if is_bp:",
            "    continue  # 跳过样板误报",
            "```\n",
        ],
    })

    modules.append({
        "num": 10,
        "slug": "powershell",
        "title": "lib.powershell — PowerShell脚本编码工具",
        "filename": "10-powershell.md",
        "body": [
            "Windows PowerShell 5.x 要求 .ps1 脚本使用 UTF-8 BOM + CRLF 换行，否则含中文时可能报语法错误。本模块提供写入、验证、修复能力。\n",
            "| 函数 | 签名 | 说明 |",
            "|---------|------|------|",
            "| `write_ps1_script` | `(file_path, content, *, add_bom=True, newline='\\r\\n') -> Path` | 以PS兼容编码（UTF-8 BOM + CRLF）写入.ps1文件 |",
            "| `verify_ps1_encoding` | `(file_path) -> tuple[bool, list[str]]` | 验证.ps1文件编码是否合规，返回(是否合规, 问题列表) |",
            "| `fix_ps1_encoding` | `(file_path) -> tuple[bool, list[str]]` | 修复编码问题（添加BOM、统一CRLF），返回(是否修复, 变更列表) |\n",
            "**示例**：\n",
            "```python",
            "from lib.powershell import write_ps1_script, verify_ps1_encoding",
            "",
            "# 写入新的.ps1文件（自动BOM+CRLF，PS5/PS7均兼容）",
            "write_ps1_script('scripts/build.ps1', '''",
            "Write-Host 'Hello World'",
            "$x = 1",
            "''')",
            "",
            "# 验证已有.ps1文件",
            "ok, issues = verify_ps1_encoding('ci-check.ps1')",
            "if not ok:",
            "    print(f'编码问题: {issues}')",
            "```\n",
        ],
    })

    modules.append({
        "num": 11,
        "slug": "process",
        "title": "lib.process — 进程探测与安全终止",
        "filename": "11-process.md",
        "body": [
            "提供跨平台进程存活探测、cmdline 获取、关键字匹配与 kill 前身份校验能力，适合 stop/kill 类脚本复用。\n",
            "| 函数/类 | 签名 | 说明 |",
            "|---------|------|------|",
            "| `CmdlineResult` | `dataclass` | 进程命令行探测结果（ok/cmdline/error/source） |",
            "| `is_process_running` | `(pid: int) -> bool` | 判断 PID 是否仍然存活 |",
            "| `get_process_cmdline` | `(pid: int) -> CmdlineResult` | 获取进程命令行，Windows 优先 WMIC，失败回退 CIM |",
            "| `cmdline_matches` | `(cmdline: str, must_contain: list[str]) -> bool` | 校验命令行是否包含全部关键字 |",
            "| `safe_kill` | `(pid: int, must_contain: list[str], *, kill: bool) -> tuple[bool, str]` | kill 前先校验进程身份；默认可用于 dry-run 校验 |\n",
            "**示例**：\n",
            "```python",
            "from lib.process import safe_kill",
            "",
            "# 先校验，不实际终止",
            "ok, msg = safe_kill(pid=1234, must_contain=['python', 'monitor'], kill=False)",
            "print(ok, msg)",
            "```\n",
        ],
    })

    modules.append({
        "num": 12,
        "slug": "quality_rules",
        "title": "lib.quality_rules — 质量规则复用函数",
        "filename": "12-quality-rules.md",
        "body": [
            "提供质量检查脚本共享的轻量规则函数，避免在多个 checker 中重复实现同一条规则。\n",
            "| 函数/常量 | 签名 | 说明 |",
            "|-----------|------|------|",
            "| `FILE_URL_PATTERN` | `Pattern` | 匹配 Markdown 中的 `file:///` 绝对路径链接 |",
            "| `count_file_urls` | `(content: str) -> int` | 统计文本中的 `file:///` 绝对路径数量 |",
            "| `check_no_file_url` | `(content: str, make_result) -> list` | 生成「禁止 file:/// 绝对路径」检查结果，供不同 Result 类型复用 |\n",
            "**示例**：\n",
            "```python",
            "from lib.quality_rules import check_no_file_url",
            "",
            "results = check_no_file_url(content, lambda **kw: CheckResult(**kw))",
            "```\n",
        ],
    })

    modules.append({
        "num": 13,
        "slug": "quality_report",
        "title": "lib.quality_report — 质量报告聚合与输出",
        "filename": "13-quality-report.md",
        "body": [
            "提供检查报告的分组统计、JSON 构建、彩色打印与汇总输出能力，供质量检查脚本共享。\n",
            "| 函数/类 | 签名 | 说明 |",
            "|---------|------|------|",
            "| `ResultGroupMixin` | `class` | 为报告对象提供 `errors/warnings/passes` 三类结果视图 |",
            "| `score_to_ansi` | `(score: int) -> str` | 根据分数返回 ANSI 颜色码 |",
            "| `print_result_lines` | `(results, *, verbose, print_pass, print_warn, print_error) -> None` | 打印单条检查结果列表 |",
            "| `issue_list` | `(items: Iterable) -> list[dict]` | 将结果对象转为 JSON 友好的 `{name,message}` 列表 |",
            "| `safe_relative_to` | `(path: Path, root_dir: Path) -> Path` | 安全计算相对路径，失败时回退原路径 |",
            "| `aggregate_stats` | `(reports: list) -> dict` | 聚合总错误/警告/通过数与平均分 |",
            "| `build_json_output` | `(reports, root_dir, *, base_dir_key, base_dir_value, count_key, items_key, item_builder) -> dict` | 构建统一 JSON 输出骨架 |",
            "| `common_report_fields` | `(report) -> dict` | 提取通用报告字段（score/errors/warnings/pass_count） |",
            "| `print_scored_report` | `(*, score, header, extra_lines, results, verbose, print_pass, print_warn, print_error) -> None` | 打印带分数标题的报告块 |",
            "| `print_scored_report_cli` | `(*, score, header, extra_lines, results, verbose) -> None` | 使用 CLI 预设样式打印报告块 |",
            "| `print_aggregate_summary` | `(reports: list) -> dict` | 打印平均分与通过/警告/错误摘要，并返回统计值 |\n",
            "**示例**：\n",
            "```python",
            "from lib.quality_report import build_json_output, common_report_fields",
            "",
            "payload = build_json_output(",
            "    reports,",
            "    root_dir,",
            "    base_dir_key='skills_dir',",
            "    base_dir_value=skills_dir,",
            "    count_key='skill_count',",
            "    items_key='skills',",
            "    item_builder=lambda r: {'name': r.skill_name, **common_report_fields(r)},",
            ")",
            "```\n",
        ],
    })

    modules.append({
        "num": 14,
        "slug": "constants",
        "title": "constants.py — 全局常量（scripts/ 根目录）",
        "filename": "14-constants.md",
        "body": [
            "位于 `.agents/scripts/constants.py`，全局共享常量模块，供所有脚本和 lib/ 模块引用。\n",
            "导入方式：`from constants import EXCLUDED_DIRS, ANSI_GREEN, ...`\n",
            "| 常量 | 类型 | 说明 |",
            "|------|------|------|",
            "| `ANSI_GREEN/ANSI_YELLOW/ANSI_RED/ANSI_CYAN/ANSI_RESET` | str | ANSI 颜色代码 |",
            "| `EXCLUDED_DIRS` | set[str] | 文件扫描默认排除目录（.git/vendor/.venv/__pycache__/node_modules/.temp） |",
            "| `REQUIRED_RULES` / `TEMP_PATHS` | list | .gitignore 必需规则与临时路径 |",
            "| `LINK_CHECK_*` | - | check-links.py 默认参数（timeout/workers/user-agent等） |",
            "| `VALID_TIERS` / `ROLE_EXCLUDED_FILES` | - | 角色权限校验常量 |",
            "| `SPEC_MATCH_THRESHOLD` / `META_DOC_KEYWORDS` | - | Spec 一致性检查参数 |",
            "| `SCAN_DIRS` / `TARGETS` / `MANUAL_DESCRIPTIONS` | - | 导航生成器配置 |\n",
        ],
    })

    _MODULES = modules
    return _MODULES


_DEV_WORKFLOW = [
    "## 新增脚本开发流程\n",
    "新建 `.agents/scripts/` 下的脚本前，请遵循以下流程：\n",
    "1. **先查本文件**，确认 lib/ 是否已有可复用的函数",
    "2. **优先使用共享函数**，避免重复实现相同逻辑",
    "3. 如确需新功能，先考虑是否应提取到 lib/ 供其他脚本复用",
    "4. 脚本头部添加 sys.path 设置：",
    "```python",
    "import sys",
    "from pathlib import Path",
    "SCRIPTS_DIR = Path(__file__).resolve().parent",
    "if str(SCRIPTS_DIR) not in sys.path:",
    "    sys.path.insert(0, str(SCRIPTS_DIR))",
    "```",
    "5. 使用 `add_common_args(parser)` 注册通用参数（--path/--json）",
    "6. 使用 `print_pass/print_warn/print_error/print_summary` 输出检查结果",
    "7. 完成后运行 `python check-duplication.py` 检查是否引入新的重复代码\n",
]


def generate_api_docs() -> str:
    """生成单文件 API 参考文档 Markdown 内容（向后兼容）。"""
    modules = _get_modules()
    sections = []

    sections.append("# .agents/scripts/lib/ API 参考\n")
    sections.append("> 本文档由 `lib/__init__.py` 中的 `generate_api_docs()` 自动生成，描述共享库所有公开模块和函数。\n")
    sections.append("## 目录\n")
    for m in modules:
        anchor = m["title"].lower().replace(" — ", "-").replace(" ", "-").replace(".", "").replace("/", "")
        sections.append(f"- [{m['title']}](#{anchor})")
    sections.append("")
    sections.append("## README 生成建议\n")
    sections.append("- **预览输出**：可直接运行 `python .agents/scripts/lib/__init__.py` 查看生成内容。")
    sections.append("- **拆分模式（推荐）**：运行 `python .agents/scripts/lib/__init__.py --split` 自动生成分片文档到 `lib/docs/` 目录。")
    sections.append("- **安全写回单文件**：Windows 下请优先使用 Python 直接写文件，避免 PowerShell 文本管道引发中文编码污染。")
    sections.append("```powershell")
    sections.append('python -X utf8 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path(r\'d:/spaces/SpecWeave/.agents/scripts\'))); import lib; Path(r\'d:/spaces/SpecWeave/.agents/scripts/lib/README.md\').write_text(lib.generate_api_docs(), encoding=\'utf-8\')"')
    sections.append("```")
    sections.append("- **不推荐**：`python .agents/scripts/lib/__init__.py | Set-Content ...`。在 Windows PowerShell 文本管道场景下，中文内容可能被错误转码。\n")

    for m in modules:
        sections.append("---\n")
        sections.append(f"## {m['title']}\n")
        sections.extend(m["body"])

    sections.append("\n---\n")
    sections.extend(_DEV_WORKFLOW)

    sections.append("## 相关模式\n")
    sections.append("- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)")
    sections.append("- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)")

    return "\n".join(sections)


def _module_frontmatter(module_id, title, source_file, toml_ref):
    return (
        "---\n"
        f'id: "{module_id}"\n'
        f'title: "{title}"\n'
        f'source: "{source_file}"\n'
        f'x-toml-ref: "{toml_ref}"\n'
        "---\n"
    )


def _nav_prev(modules, idx):
    if idx == 0:
        return None
    prev = modules[idx - 1]
    return f"[← {prev['title'].split(' — ')[1] if ' — ' in prev['title'] else prev['title']}]({prev['filename']})"


def _nav_next(modules, idx):
    if idx >= len(modules) - 1:
        return None
    nxt = modules[idx + 1]
    return f"[{nxt['title'].split(' — ')[1] if ' — ' in nxt['title'] else nxt['title']} →]({nxt['filename']})"


def write_split_docs(lib_dir: Path) -> list[Path]:
    """将 API 文档拆分为索引页 + 各模块独立文档，写入 lib/docs/ 目录。

    Returns:
        写入的文件路径列表。
    """
    modules = _get_modules()
    docs_dir = lib_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    written = []

    for idx, m in enumerate(modules):
        doc_id = f"lib-api-{m['slug']}"
        toml_ref = f"../../../../.meta/toml/.agents/scripts/lib/docs/{m['filename'].replace('.md', '.toml')}"
        source_ref = f"lib/__init__.py#{m['slug']}"

        lines = []
        lines.append(_module_frontmatter(doc_id, m["title"], source_ref, toml_ref))
        lines.append(f"# {m['title']}\n")
        lines.extend(m["body"])

        lines.append("---\n")
        lines.append("## 相关模式\n")
        lines.append("- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)")
        lines.append("- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)")
        lines.append("")
        lines.append("---\n")

        nav_parts = []
        prev_link = _nav_prev(modules, idx)
        next_link = _nav_next(modules, idx)
        if prev_link:
            nav_parts.append(f"← 上一章: {prev_link}")
        nav_parts.append("**[返回索引](../README.md)**")
        if next_link:
            nav_parts.append(f"下一章 → {next_link}")
        lines.append(" | ".join(nav_parts) + "\n")

        content = "\n".join(lines)
        out_path = docs_dir / m["filename"]
        out_path.write_text(content, encoding="utf-8")
        written.append(out_path)

    readme_toml_ref = "../../../.meta/toml/.agents/scripts/lib/README.toml"
    index_lines = []
    index_lines.append(_module_frontmatter("lib-api", ".agents/scripts/lib/ API 参考", "lib/__init__.py", readme_toml_ref))
    index_lines.append("# .agents/scripts/lib/ API 参考\n")
    index_lines.append("> 本文档由 `lib/__init__.py` 自动生成，描述共享库所有公开模块和函数。\n")
    index_lines.append("## 文档导航\n")
    index_lines.append("| 文档 | 模块 | 说明 |")
    index_lines.append("|------|------|------|")
    for m in modules:
        short_title = m["title"].split(" — ")[1] if " — " in m["title"] else m["title"]
        mod_name = m["title"].split(" — ")[0]
        index_lines.append(f"| [docs/{m['filename']}](docs/{m['filename']}) | `{mod_name}` | {short_title} |")
    index_lines.append("")
    index_lines.append("## 文档生成\n")
    index_lines.append("- **拆分模式（当前使用）**：索引页 + 14个模块分片文档，位于 `lib/docs/` 目录")
    index_lines.append("- **重新生成**：运行 `python .agents/scripts/lib/__init__.py --split`")
    index_lines.append("- **单文件预览**：运行 `python .agents/scripts/lib/__init__.py` 输出到 stdout\n")
    index_lines.append("---\n")
    index_lines.extend(_DEV_WORKFLOW)
    index_lines.append("## 相关模式\n")
    index_lines.append("- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)")
    index_lines.append("- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)")

    readme_path = lib_dir / "README.md"
    readme_path.write_text("\n".join(index_lines), encoding="utf-8")
    written.insert(0, readme_path)

    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成 lib/ API 参考文档")
    parser.add_argument("--split", action="store_true", help="拆分模式：生成分片文档到 lib/docs/ 并更新 README.md")
    args = parser.parse_args()

    if args.split:
        lib_dir = Path(__file__).resolve().parent
        written = write_split_docs(lib_dir)
        for p in written:
            print(f"  写入: {p.relative_to(lib_dir.parent.parent.parent)}")
        print(f"\n共写入 {len(written)} 个文件（1个索引页 + {len(written)-1}个模块文档）")
    else:
        print(generate_api_docs())
