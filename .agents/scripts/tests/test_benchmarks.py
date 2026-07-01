"""性能基准测试：高频脚本Skill入口的核心函数性能基线。

本文件使用 pytest-benchmark 建立性能基线，用于：
1. 记录当前版本各核心函数的执行耗时（baseline）
2. 未来优化后可通过 --benchmark-compare 对比前后差异
3. 防止性能回退（可通过 --benchmark-compare-fail 设定阈值）

运行方式：
  pytest .agents/scripts/tests/test_benchmarks.py -v --benchmark-only
  pytest .agents/scripts/tests/test_benchmarks.py -v --benchmark-autosave
  pytest .agents/scripts/tests/test_benchmarks.py -v --benchmark-compare=0001

注意：常规测试运行时（不带 --benchmark-only 或未安装 pytest-benchmark），
本模块的所有测试会被自动跳过，不影响正常测试流程。

覆盖模块与对应Skill：
- lib/link_fixer.py (link-check-cmd): URL解析、路径计算、代码块检测、链接修复
- check-duplication.py (check-duplication-cmd): 行归一化、指纹计算、重复检测
- lib/frontmatter.py (docgen/link-check等共用): TOML/YAML frontmatter解析与字段提取
- lib/markdown.py (docgen-cmd): Markdown链接解析、标题提取
- lib/cli.py (所有脚本共用): 颜色输出、终端能力检测
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.link_fixer import (
    parse_file_url,
    compute_relative_path,
    is_code_fence_context,
    fix_link_url,
    os_path_to_posix,
)
from lib.frontmatter import (
    extract_yaml_field,
    extract_frontmatter_field,
    extract_frontmatter_field_from_file,
)
from lib.markdown import (
    parse_inline_links,
    extract_title,
)
from lib.cli import _supports_unicode, _symbol, _color

_spec = importlib.util.spec_from_file_location(
    "check_duplication", _SCRIPTS_DIR / "check-duplication.py"
)
check_duplication = importlib.util.module_from_spec(_spec)
sys.modules["check_duplication"] = check_duplication
_spec.loader.exec_module(check_duplication)

from check_duplication import (
    normalize_line,
    compute_fingerprint,
    find_duplicates,
)
from lib.rules import FalsePositiveRules


# ── 共享测试数据 ──────────────────────────────────────────

LONG_MARKDOWN = """# Title

Some intro text with a [link](docs/guide.md) and another [ref](../README.md#section).

```python
def hello():
    # this is a code comment, not a real link: [fake](should-not-match.md)
    print("[not a link](either)")
```

More content with `inline code` and a [relative link](./subdir/file.md#L10-L20).

## Section

- Item with [absolute link](https://example.com/page)
- Item with [file link](/docs/api.md)

```
plain code block without language
[also](not-a-link.md)
```

Final paragraph with [back reference](../other/file.md#anchor).
""" * 20

TOML_FM_RAW = """id = "test-doc"
type = "pattern"
date = "2026-06-30"
source = "README.md#section"
tier = "standard"
"""

YAML_FM = """---
id: test-doc
type: pattern
date: 2026-06-30
source: README.md#yaml-section
tier: "quoted-value"
description: "A description with a # hash inside quotes"
---

# Body content
"""

YAML_FM_RAW = """id: test-doc
type: pattern
date: 2026-06-30
source: README.md#yaml-section
"""

PY_CODE_SAMPLE = """import os
import sys
from pathlib import Path

def find_files(root: Path, pattern: str) -> list[Path]:
    results = []
    for p in root.rglob(pattern):
        if p.is_file():
            results.append(p)
    return results

def read_config(path: Path) -> dict:
    config = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, _, value = line.partition('=')
            config[key.strip()] = value.strip()
    return config

def process_data(items: list, verbose: bool = False) -> list:
    result = []
    for item in items:
        processed = item.strip().lower()
        if verbose:
            print(f'Processing: {processed}')
        result.append(processed)
    return result

class DataProcessor:
    def __init__(self, config: dict):
        self.config = config
        self._cache = {}

    def process(self, items: list) -> list:
        return process_data(items, verbose=self.config.get('verbose', False))

    def get_cache(self) -> dict:
        return self._cache.copy()
""" * 10

PY_CODE_LINES = [
    line for line in PY_CODE_SAMPLE.splitlines()
    if line.strip() and not line.strip().startswith('#')
]


# ── lib/link_fixer.py 基准测试 (link-check-cmd) ──────────

class TestBenchmarkLinkFixer:
    """link-check-cmd Skill 核心函数性能基线。"""

    def test_bench_parse_file_url_with_anchor(self, benchmark):
        benchmark(parse_file_url, "D:/spaces/SpecWeave/docs/guide/intro.md#L100-L120")

    def test_bench_parse_file_url_plain(self, benchmark):
        benchmark(parse_file_url, "docs/guide/intro.md")

    def test_bench_compute_relative_path(self, benchmark, tmp_path):
        source = tmp_path / "docs" / "guide" / "intro.md"
        target = tmp_path / "docs" / "api" / "reference.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("# S", encoding="utf-8")
        target.write_text("# T", encoding="utf-8")
        benchmark(compute_relative_path, source, target)

    def test_bench_is_code_fence_context_inside_code(self, benchmark):
        pos = LONG_MARKDOWN.find("should-not-match")
        benchmark(is_code_fence_context, LONG_MARKDOWN, pos)

    def test_bench_is_code_fence_context_outside_code(self, benchmark):
        pos = LONG_MARKDOWN.find("Some intro")
        benchmark(is_code_fence_context, LONG_MARKDOWN, pos)

    def test_bench_is_code_fence_context_near_end(self, benchmark):
        pos = len(LONG_MARKDOWN) - 50
        benchmark(is_code_fence_context, LONG_MARKDOWN, pos)

    def test_bench_os_path_to_posix(self, benchmark):
        benchmark(os_path_to_posix, Path("D:\\spaces\\SpecWeave\\docs\\guide\\intro.md"))

    def test_bench_fix_link_url_absolute(self, benchmark, tmp_path):
        project = tmp_path
        docs = project / "docs"
        docs.mkdir()
        source = project / "README.md"
        target = docs / "guide.md"
        target.write_text("# Guide", encoding="utf-8")
        source.write_text("idx", encoding="utf-8")
        abs_url = f"file:///{str(target).replace(chr(92), '/')}"
        benchmark(fix_link_url, abs_url, source, project)

    def test_bench_parse_inline_links_large(self, benchmark):
        benchmark(parse_inline_links, LONG_MARKDOWN)


# ── check-duplication.py 基准测试 (check-duplication-cmd) ─

class TestBenchmarkCheckDuplication:
    """check-duplication-cmd Skill 核心函数性能基线。"""

    def test_bench_normalize_line_simple(self, benchmark):
        benchmark(normalize_line, "        result = process_data(items, verbose=True)")

    def test_bench_normalize_line_string_with_hash(self, benchmark):
        benchmark(normalize_line, "s = 'hello # world'  # inline comment")

    def test_bench_normalize_line_inline_comment(self, benchmark):
        benchmark(normalize_line, "config[key.strip()] = value.strip()  # store config")

    def test_bench_compute_fingerprint_10_lines(self, benchmark):
        benchmark(compute_fingerprint, PY_CODE_LINES[:10])

    def test_bench_compute_fingerprint_50_lines(self, benchmark):
        benchmark(compute_fingerprint, PY_CODE_LINES[:50])

    def test_bench_find_duplicates_small_project(self, benchmark, tmp_path):
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        lib = scripts / "lib"
        lib.mkdir()
        for i in range(5):
            (scripts / f"tool_{i}.py").write_text(PY_CODE_SAMPLE, encoding="utf-8")
        (lib / "shared.py").write_text(PY_CODE_SAMPLE[:len(PY_CODE_SAMPLE)//2], encoding="utf-8")
        rules = FalsePositiveRules()
        benchmark(find_duplicates, scripts, rules, threshold=10, window=10)


# ── lib/frontmatter.py 基准测试 (多Skill共用) ────────────

class TestBenchmarkFrontmatter:
    """frontmatter 解析性能基线（docgen/link-check等多个Skill共用）。"""

    def test_bench_extract_yaml_quoted_field(self, benchmark):
        benchmark(extract_yaml_field, YAML_FM, "source")

    def test_bench_extract_yaml_unquoted_field(self, benchmark):
        benchmark(extract_yaml_field, YAML_FM, "id")

    def test_bench_extract_yaml_missing_field(self, benchmark):
        benchmark(extract_yaml_field, YAML_FM, "nonexistent_field")

    def test_bench_extract_toml_field(self, benchmark):
        benchmark(extract_frontmatter_field, TOML_FM_RAW, "source")

    def test_bench_extract_frontmatter_from_file(self, benchmark, tmp_path):
        p = tmp_path / "test.md"
        p.write_text(
            "+++\n" + TOML_FM_RAW + "\n+++\n\n# Body\n",
            encoding="utf-8",
        )
        benchmark(extract_frontmatter_field_from_file, p, "id")


# ── lib/markdown.py 基准测试 (docgen-cmd) ─────────────────

class TestBenchmarkMarkdown:
    """docgen-cmd Skill 依赖的 Markdown 工具性能基线。"""

    def test_bench_extract_title(self, benchmark, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("# My Document Title\n\nSome content.", encoding="utf-8")
        benchmark(extract_title, p)

    def test_bench_parse_inline_links_large_doc(self, benchmark):
        benchmark(parse_inline_links, LONG_MARKDOWN)

    def test_bench_parse_inline_links_small(self, benchmark):
        benchmark(parse_inline_links, "[a](x.md) and [b](y.md) and [c](z.md)")


# ── lib/cli.py 基准测试 (所有脚本共用) ───────────────────

class TestBenchmarkCli:
    """CLI 输出工具性能基线（所有脚本共用）。"""

    def test_bench_supports_unicode(self, benchmark):
        benchmark(_supports_unicode)

    def test_bench_symbol_lookup_pass(self, benchmark):
        benchmark(_symbol, "pass")

    def test_bench_symbol_lookup_error(self, benchmark):
        benchmark(_symbol, "error")

    def test_bench_color_non_tty(self, benchmark, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
        benchmark(_color, "test message", "\033[92m")

    def test_bench_color_tty(self, benchmark, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        benchmark(_color, "test message", "\033[92m")
