"""知识库 frontmatter 分隔符守护测试。

背景（2026-10-20 修复）：``docs/knowledge/cake-cutting-rule/index.md`` 曾用 ``***`` 作
frontmatter 分隔符，而 ``.agents/scripts/lib/frontmatter.py`` 只识别 ``---``（YAML）与
``+++``（TOML），解析器静默返回 ``None`` —— 该知识包元数据被整体丢弃：索引条目从
``categories/cake-cutting-rule.md`` 降级进 ``categories/unknown.md``（元数据全空），
且生成器只报「缺少 frontmatter」，无法定位根因。

本测试固化的不变量：
1. 知识库内不得出现 ``***`` / ``+++`` 作 frontmatter 分隔符（规范要求 YAML ``---``）；
2. 索引生成器必须把非标准分隔符识别为独立告警类型，而非笼统的「缺少 frontmatter」；
3. 曾经受损的知识包必须能被仓库解析器正确解析回原分类。
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_DIR = _PROJECT_ROOT / "docs" / "knowledge"
KNOWLEDGE_SCRIPTS_DIR = KNOWLEDGE_DIR / "scripts"

# 规范允许的分隔符：YAML `---`；非标准分隔符必须被拦截
NONSTANDARD_DELIMITERS = ("***", "+++")


def _load_generator():
    """按文件路径加载知识库索引生成器模块（避免污染 sys.modules 命名空间）。"""
    scripts_dir = str(KNOWLEDGE_SCRIPTS_DIR)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(
        "knowledge_generate_index", KNOWLEDGE_SCRIPTS_DIR / "generate_index.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["knowledge_generate_index"] = module
    spec.loader.exec_module(module)
    return module


def _first_line(path: Path) -> str:
    """读取文件首行（去除 BOM 与首尾空白）。"""
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        return fh.readline().lstrip("﻿").strip()


def _knowledge_markdown_files():
    """遍历知识库 Markdown 文件（排除 scripts/ 工具目录）。"""
    for md in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        rel_parts = md.relative_to(KNOWLEDGE_DIR).parts
        if "scripts" in rel_parts:
            continue
        yield md


def test_no_nonstandard_frontmatter_delimiter_in_knowledge_base():
    """不变量1：知识库内不存在 `***` / `+++` 作 frontmatter 分隔符。"""
    violations = []
    for md in _knowledge_markdown_files():
        line = _first_line(md)
        if line in NONSTANDARD_DELIMITERS:
            rel = md.relative_to(_PROJECT_ROOT).as_posix()
            violations.append(f"{rel}: 首行分隔符 `{line}`（须改为 YAML `---`）")

    assert not violations, (
        "知识库存在非标准 frontmatter 分隔符，元数据会被解析器静默丢弃：\n"
        + "\n".join(violations)
    )


def test_index_generator_reports_nonstandard_delimiter(tmp_path, capsys):
    """不变量2：生成器把非标准分隔符识别为独立告警类型，并给出可定位的提示。"""
    generator = _load_generator()
    generator._frontmatter_warnings.clear()

    broken = tmp_path / "broken-pkg.md"
    broken.write_text(
        '***\n\ntitle: "坏包"\n\ncategory: "demo"\n\ntags: ["a"]\n\n***\n\n# 内容\n',
        encoding="utf-8",
    )

    meta = generator.parse_frontmatter(broken)
    stderr = capsys.readouterr().err

    assert "非标准 frontmatter 分隔符" in stderr, "未输出非标准分隔符的可定位告警"
    nonstandard = [
        w for w in generator._frontmatter_warnings if w["type"] == "nonstandard_delimiter"
    ]
    assert nonstandard, "未记录 nonstandard_delimiter 类型的告警"
    assert nonstandard[0]["delimiter"] == "***"
    assert str(broken) in nonstandard[0]["file"]
    # 降级行为保留（解析器不识别该分隔符），但必须已被显式告警覆盖
    assert meta["category"] == "unknown"


def test_fixed_knowledge_package_parses_to_own_category():
    """不变量3：曾经受损的知识包恢复为自身分类，且标签完整。"""
    generator = _load_generator()
    target = KNOWLEDGE_DIR / "cake-cutting-rule" / "index.md"
    assert target.exists(), f"回归：知识包入口缺失 {target}"

    fields = generator.parse_frontmatter_unified(target)
    assert fields is not None, "回归：仓库解析器仍无法解析该知识包的 frontmatter"
    assert fields.get("category") == "cake-cutting-rule"
    assert fields.get("id") == "cake-cutting-rule"
    assert fields.get("title")
    assert len(fields.get("tags") or []) == 12, "回归：标签数量异常（疑为转义残留）"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
