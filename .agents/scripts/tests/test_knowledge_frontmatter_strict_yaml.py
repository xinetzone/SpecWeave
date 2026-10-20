"""知识库 frontmatter 严格 YAML 合法性守护测试。

背景（2026-10-20 修复）：``docs/knowledge/tech/medium-wiki/`` 下 3 个文件与
``tech/openkylin-docs-wiki/references/openkylin-v3-adaptation-assessment.md`` 的
frontmatter 在双引号标量内嵌了未转义的 ASCII 引号（如 ``title: "从"思想之地"到..."``）。
仓库自研解析器（``.agents/scripts/lib/frontmatter.py``）按行取值、只剥外层引号，
因此容错通过；但标准 YAML 解析器直接报 ``expected <block end>, but found '<scalar>'`` ——
同一份元数据在两套解析器下行为分叉，知识包一旦被标准 YAML 工具消费即元数据损坏。

本测试固化的不变量：知识库内所有带 frontmatter 的 Markdown，其 frontmatter 块
必须能被标准 YAML 解析器（PyYAML）成功解析。
"""

from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_DIR = _PROJECT_ROOT / "docs" / "knowledge"


def _frontmatter_block(md: Path) -> str | None:
    """提取 Markdown 的 frontmatter 文本块；无 frontmatter 时返回 None。"""
    txt = md.read_text(encoding="utf-8", errors="replace")
    if not txt.startswith("---"):
        return None
    end = txt.find("\n---", 3)
    if end == -1:
        return None
    return txt[3:end]


def test_knowledge_frontmatter_is_strict_yaml_valid():
    """知识库内所有 frontmatter 块必须通过标准 YAML 解析。"""
    yaml = pytest.importorskip("yaml")

    violations = []
    for md in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        if "scripts" in md.relative_to(KNOWLEDGE_DIR).parts:
            continue
        block = _frontmatter_block(md)
        if block is None:
            continue
        try:
            yaml.safe_load(block)
        except yaml.YAMLError as exc:
            rel = md.relative_to(_PROJECT_ROOT).as_posix()
            problem = getattr(exc, "problem", str(exc)).splitlines()[0]
            violations.append(f"{rel}: {problem}")

    assert not violations, (
        "知识库 frontmatter 存在标准 YAML 解析失败项（双引号标量内嵌未转义引号是常见成因，"
        "应改用单引号标量）：\n" + "\n".join(violations)
    )


def test_quoted_scalar_with_inner_quotes_is_accepted():
    """回归：含内嵌引号的值改用单引号标量后，两套解析器结果一致。"""
    yaml = pytest.importorskip("yaml")

    block = 'title: \'Medium 平台知识包：从"思想之地"到注意力订阅平台\'\n'
    parsed = yaml.safe_load(block)
    assert parsed["title"] == 'Medium 平台知识包：从"思想之地"到注意力订阅平台'


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
