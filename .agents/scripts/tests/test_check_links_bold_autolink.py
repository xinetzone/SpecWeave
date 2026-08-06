"""check-links.py 加粗包裹尖括号自动链接（**<url>**）识别与规范化修复的单元测试。

覆盖：
- BOLD_AUTOLINK_RE: 正则匹配
- parse_links: 识别 **<url>** 为可检查的外部链接（识别能力）
- fix_bold_autolinks: 规范化修复（**<url>** → **[text](url)**）
  - 代码围栏内不修复
  - 锚点/占位符不修复
  - 已是标准链接不重复处理
  - dry-run 不写入
"""

from __future__ import annotations


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import importlib.util
import sys
from pathlib import Path

import pytest

# 将 .agents/scripts 加入 sys.path 以导入依赖模块（lib, constants 等）
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# 通过 importlib 加载 check-links.py（文件名含连字符，不能直接 import）
_SPEC_PATH = SCRIPTS_DIR / "check-links.py"
_spec = importlib.util.spec_from_file_location("check_links", _SPEC_PATH)
check_links = importlib.util.module_from_spec(_spec)
sys.modules["check_links"] = check_links
_spec.loader.exec_module(check_links)


# ========== BOLD_AUTOLINK_RE ==========


class TestBoldAutolinkRegex:
    def test_matches_bold_autolink(self):
        m = check_links.BOLD_AUTOLINK_RE.search("**<https://mermaid.js.org/>**")
        assert m is not None
        assert m.group(1) == "https://mermaid.js.org/"

    def test_matches_with_context(self):
        m = check_links.BOLD_AUTOLINK_RE.search("域名：**<https://example.com/>**，注意")
        assert m is not None
        assert m.group(1) == "https://example.com/"

    def test_does_not_match_standard_link(self):
        # 标准 markdown 链接不应匹配
        assert check_links.BOLD_AUTOLINK_RE.search("**[text](https://example.com/)**") is None

    def test_does_not_match_plain_autolink(self):
        # 未加粗的尖括号自动链接不应匹配（属另一格式）
        assert check_links.BOLD_AUTOLINK_RE.search("<https://example.com/>") is None

    def test_does_not_match_single_bold_star(self):
        assert check_links.BOLD_AUTOLINK_RE.search("*<https://example.com/>*") is None


# ========== parse_links（识别能力） ==========


class TestParseLinksRecognizesBoldAutolink:
    def test_bold_autolink_counted_as_external(self, tmp_path: Path):
        md = tmp_path / "t.md"
        md.write_text("域名：**<https://mermaid.js.org/>**", encoding="utf-8")
        links = check_links.parse_links(md)
        # 应被识别为一个外部链接
        assert any(url == "https://mermaid.js.org/" for _, url, _ in links)

    def test_external_classification(self, tmp_path: Path):
        md = tmp_path / "t.md"
        md.write_text("**<https://mermaid.js.org/>**", encoding="utf-8")
        links = check_links.parse_links(md)
        urls = [url for _, url, _ in links]
        assert any(check_links.is_external_url(u) for u in urls)

    def test_code_fence_not_counted(self, tmp_path: Path):
        md = tmp_path / "t.md"
        md.write_text(
            "正文\n```markdown\n**<https://example.com/x>**\n```\n",
            encoding="utf-8",
        )
        links = check_links.parse_links(md)
        assert not any("https://example.com/x" in url for _, url, _ in links)

    def test_anchor_and_placeholder_skipped(self, tmp_path: Path):
        md = tmp_path / "t.md"
        md.write_text("**<#section>** **<{{var}}>**", encoding="utf-8")
        links = check_links.parse_links(md)
        assert len(links) == 0


# ========== fix_bold_autolinks ==========


def _single_file_md(tmp_path: Path, content: str) -> Path:
    md = tmp_path / "t.md"
    md.write_text(content, encoding="utf-8")
    return md


class TestFixBoldAutolinks:
    def test_dry_run_does_not_write(self, tmp_path: Path):
        md = _single_file_md(tmp_path, "**<https://example.com/>**")
        original = md.read_text(encoding="utf-8")
        fixes = check_links.fix_bold_autolinks([md], dry_run=True)
        assert len(fixes) == 1
        assert fixes[0][1] == 1
        assert md.read_text(encoding="utf-8") == original

    def test_actual_write_converts(self, tmp_path: Path):
        md = _single_file_md(tmp_path, "**<https://example.com/>**")
        fixes = check_links.fix_bold_autolinks([md], dry_run=False)
        assert len(fixes) == 1
        assert fixes[0][1] == 1
        new_content = md.read_text(encoding="utf-8")
        assert new_content == "**[https://example.com/](https://example.com/)**"

    def test_preserves_leading_trailing_text(self, tmp_path: Path):
        md = _single_file_md(
            tmp_path,
            "前缀 **<https://a.com/>** 后缀",
        )
        check_links.fix_bold_autolinks([md], dry_run=False)
        assert md.read_text(encoding="utf-8") == "前缀 **[https://a.com/](https://a.com/)** 后缀"

    def test_code_fence_not_fixed(self, tmp_path: Path):
        content = (
            "正文 **<https://body.example.com/>**\n"
            "```markdown\n**<https://code.example.com/x>**\n```\n"
            "尾部"
        )
        md = _single_file_md(tmp_path, content)
        fixes = check_links.fix_bold_autolinks([md], dry_run=False)
        # 仅正文处被修复（1 处），代码块内原样保留
        assert len(fixes) == 1
        assert fixes[0][1] == 1
        new_content = md.read_text(encoding="utf-8")
        assert "**[https://body.example.com/](https://body.example.com/)**" in new_content
        assert "**<https://code.example.com/x>**" in new_content

    def test_anchor_and_placeholder_not_fixed(self, tmp_path: Path):
        content = "**<#section>** **<{{var}}>**"
        md = _single_file_md(tmp_path, content)
        fixes = check_links.fix_bold_autolinks([md], dry_run=False)
        assert len(fixes) == 0
        assert md.read_text(encoding="utf-8") == content

    def test_standard_link_untouched(self, tmp_path: Path):
        content = "**[mermaid.live](https://mermaid.live/)**"
        md = _single_file_md(tmp_path, content)
        fixes = check_links.fix_bold_autolinks([md], dry_run=False)
        assert len(fixes) == 0
        assert md.read_text(encoding="utf-8") == content

    def test_multiple_fixes_in_one_file(self, tmp_path: Path):
        content = "**<https://a.com/>** 与 **<https://b.org/>**"
        md = _single_file_md(tmp_path, content)
        fixes = check_links.fix_bold_autolinks([md], dry_run=False)
        assert len(fixes) == 1
        assert fixes[0][1] == 2
        new_content = md.read_text(encoding="utf-8")
        assert "**[https://a.com/](https://a.com/)**" in new_content
        assert "**[https://b.org/](https://b.org/)**" in new_content

    def test_no_change_returns_empty(self, tmp_path: Path):
        md = _single_file_md(tmp_path, "无加粗自动链接")
        fixes = check_links.fix_bold_autolinks([md], dry_run=False)
        assert len(fixes) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])