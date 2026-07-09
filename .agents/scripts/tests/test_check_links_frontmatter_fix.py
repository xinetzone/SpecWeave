"""check-links.py frontmatter 路径自动修复的单元测试。

覆盖 fix_frontmatter_paths() 及其辅助函数：
- _relpath_posix: 相对路径计算
- _classify_path_issue: 问题类型分类
- _replace_path_in_text: 安全文本替换（含 YAML 转义处理）
- _verify_path_candidate: 候选目标验证（避免误匹配）
- _compute_frontmatter_fix: 修复值计算
- fix_frontmatter_paths: 主修复函数
"""

from __future__ import annotations

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


# ========== _relpath_posix ==========


class TestRelpathPosix:
    def test_same_directory(self, tmp_path: Path):
        from_path = tmp_path / "foo.md"
        to_path = tmp_path / "bar.md"
        from_path.write_text("", encoding="utf-8")
        to_path.write_text("", encoding="utf-8")
        result = check_links._relpath_posix(from_path.parent, to_path)
        assert result == "bar.md"

    def test_parent_directory(self, tmp_path: Path):
        from_dir = tmp_path / "subdir"
        from_dir.mkdir()
        to_path = tmp_path / "foo.md"
        to_path.write_text("", encoding="utf-8")
        result = check_links._relpath_posix(from_dir, to_path)
        assert result == "../foo.md"

    def test_sibling_directory(self, tmp_path: Path):
        from_dir = tmp_path / "a"
        from_dir.mkdir()
        to_dir = tmp_path / "b"
        to_dir.mkdir()
        to_path = to_dir / "foo.md"
        to_path.write_text("", encoding="utf-8")
        result = check_links._relpath_posix(from_dir, to_path)
        assert result == "../b/foo.md"

    def test_posix_separator(self, tmp_path: Path):
        from_dir = tmp_path / "deep" / "nested" / "dir"
        from_dir.mkdir(parents=True)
        to_path = tmp_path / "foo.md"
        to_path.write_text("", encoding="utf-8")
        result = check_links._relpath_posix(from_dir, to_path)
        # 必须使用 / 而非 \，无论平台
        assert "\\" not in result
        assert result.count("..") == 3


# ========== _classify_path_issue ==========


class TestClassifyPathIssue:
    def test_docs_prefix(self):
        assert check_links._classify_path_issue("格式问题: 路径使用docs/绝对路径前缀，应使用相对路径") == "docs_prefix"

    def test_missing_file(self):
        assert check_links._classify_path_issue("文件不存在: /path/to/missing.md") == "missing_file"

    def test_unknown(self):
        assert check_links._classify_path_issue("其他错误") == "unknown"


# ========== _replace_path_in_text ==========


class TestReplacePathInText:
    def test_basic_replacement(self):
        text = 'source: "docs/foo/bar.md"'
        result = check_links._replace_path_in_text(text, "docs/foo/bar.md", "../../foo/bar.md")
        assert result == 'source: "../../foo/bar.md"'

    def test_anchor_preserved(self):
        text = 'source: "docs/foo/bar.md#section"'
        result = check_links._replace_path_in_text(text, "docs/foo/bar.md#section", "../../foo/bar.md#section")
        assert result == 'source: "../../foo/bar.md#section"'

    def test_no_substring_match(self):
        """短路径不应误伤包含它的长路径"""
        text = 'source: "docs/foo.md.bak"\nrelated: "docs/foo.md"'
        # 只替换 docs/foo.md（不带 .bak）
        result = check_links._replace_path_in_text(text, "docs/foo.md", "../foo.md")
        # docs/foo.md.bak 不应被改
        assert "docs/foo.md.bak" in result
        # docs/foo.md 应被改
        assert "../foo.md" in result

    def test_yaml_escaped_backslashes(self):
        """YAML 双引号字符串中 \\ 表示单个反斜杠"""
        # YAML 原始文本（含转义）
        raw_text = 'source: "d:\\\\AI\\\\docs\\\\foo.md"'
        # 解析后的值（单反斜杠）
        parsed_value = "d:\\AI\\docs\\foo.md"
        new_value = "../../foo.md"
        result = check_links._replace_path_in_text(raw_text, parsed_value, new_value)
        assert "../../foo.md" in result
        assert "d:\\\\AI\\\\docs\\\\foo.md" not in result

    def test_inline_list_replacement(self):
        text = 'source: ["docs/a.md", "docs/b.md"]'
        result = check_links._replace_path_in_text(text, "docs/a.md", "../a.md")
        assert result == 'source: ["../a.md", "docs/b.md"]'

    def test_unquoted_yaml_value(self):
        text = "source: docs/foo.md"
        result = check_links._replace_path_in_text(text, "docs/foo.md", "../foo.md")
        assert result == "source: ../foo.md"

    def test_no_match_returns_unchanged(self):
        text = 'source: "other.md"'
        result = check_links._replace_path_in_text(text, "docs/foo.md", "../foo.md")
        assert result == text


# ========== _verify_path_candidate ==========


class TestVerifyPathCandidate:
    def test_distinctive_keyword_matches(self, tmp_path: Path):
        original = "docs/retrospective/reports/competitive-analysis/retrospective-volcengine-ark-introduction-20260707/README.md"
        candidate = tmp_path / "docs" / "retrospective" / "reports" / "competitive-analysis" / "retrospective-volcengine-ark-introduction-20260707" / "README.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text("", encoding="utf-8")
        assert check_links._verify_path_candidate(original, candidate) is True

    def test_distinctive_keyword_not_in_candidate(self, tmp_path: Path):
        """原路径的特定报告名不应匹配到不同的报告"""
        original = "docs/retrospective/reports/competitive-analysis/retrospective-ian-xiaohei-source-analysis-20260625/insight-extraction.md"
        candidate = tmp_path / "docs" / "retrospective" / "reports" / "competitive-analysis" / "retrospective-ai-regulation-analysis-20260708" / "insight-extraction.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text("", encoding="utf-8")
        assert check_links._verify_path_candidate(original, candidate) is False

    def test_cross_project_path_no_local_match(self, tmp_path: Path):
        """跨项目路径（如 d:/AI/...）搜索到不相关文件应跳过"""
        original = "d:\\AI\\.chaos\\libs\\awesun-usecase-skill-example\\skills\\feishu-install-pc\\SKILL.md"
        candidate = tmp_path / ".agents" / "skills" / "mermaid-cmd" / "SKILL.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text("", encoding="utf-8")
        assert check_links._verify_path_candidate(original, candidate) is False

    def test_cross_project_path_with_local_match(self, tmp_path: Path):
        """跨项目路径，但目标目录在本地存在，应通过验证"""
        original = "d:/AI/docs/retrospective/reports/competitive-analysis/retrospective-volcengine-ark-introduction-20260707/"
        candidate = tmp_path / "docs" / "retrospective" / "reports" / "competitive-analysis" / "retrospective-volcengine-ark-introduction-20260707" / "README.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text("", encoding="utf-8")
        assert check_links._verify_path_candidate(original, candidate) is True

    def test_all_generic_parts_trusts_finder(self, tmp_path: Path):
        """原路径全是通用段时，信任 finder 评分"""
        original = "docs/retrospective/reports/insight-extraction.md"
        candidate = tmp_path / "somewhere" / "insight-extraction.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text("", encoding="utf-8")
        # insight-extraction 是通用文件名，但其父目录 "somewhere" 不是通用名
        # distinctive_parts = ["somewhere"]
        assert check_links._verify_path_candidate(original, candidate) is True

    def test_empty_path_returns_true(self):
        assert check_links._verify_path_candidate("", Path("/foo")) is True

    def test_drive_letter_skipped(self, tmp_path: Path):
        """盘符应被跳过，不作为关键词"""
        original = "C:/Users/test/foo-bar-specific-report-20260709.md"
        candidate = tmp_path / "foo-bar-specific-report-20260709.md"
        candidate.write_text("", encoding="utf-8")
        assert check_links._verify_path_candidate(original, candidate) is True


# ========== _compute_frontmatter_fix ==========


class TestComputeFrontmatterFix:
    def test_docs_prefix_with_existing_target(self, tmp_path: Path):
        """docs/ 前缀且目标存在，应转换为相对路径"""
        # 构造项目结构
        (tmp_path / "docs" / "foo").mkdir(parents=True)
        target = tmp_path / "docs" / "foo" / "bar.md"
        target.write_text("", encoding="utf-8")

        # md 文件位于 tmp_path/sub/xxx.md
        md_dir = tmp_path / "sub"
        md_dir.mkdir()
        md_path = md_dir / "xxx.md"

        old_path = "docs/foo/bar.md"
        result = check_links._compute_frontmatter_fix(md_path, old_path, tmp_path, "docs_prefix")
        assert result == "../docs/foo/bar.md"

    def test_docs_prefix_with_nonexistent_target_skips_risky(self, tmp_path: Path):
        """docs/ 前缀但目标不存在，应跳过（不猜测）"""
        md_path = tmp_path / "xxx.md"
        md_path.write_text("", encoding="utf-8")

        old_path = "docs/foo/nonexistent-report-20260709/insight-extraction.md"
        # 项目中没有同名文件
        result = check_links._compute_frontmatter_fix(md_path, old_path, tmp_path, "docs_prefix")
        # 应返回 None（无可信候选）
        assert result is None

    def test_anchor_preserved_in_docs_prefix_fix(self, tmp_path: Path):
        """锚点应在修复后保留"""
        # md 文件位于子目录，使 docs/ 前缀实际产生路径错误
        md_dir = tmp_path / "sub"
        md_dir.mkdir()
        target_dir = tmp_path / "docs"
        target_dir.mkdir()
        target = target_dir / "bar.md"
        target.write_text("", encoding="utf-8")

        md_path = md_dir / "xxx.md"

        old_path = "docs/bar.md#section-1"
        result = check_links._compute_frontmatter_fix(md_path, old_path, tmp_path, "docs_prefix")
        assert result == "../docs/bar.md#section-1"


# ========== fix_frontmatter_paths（端到端） ==========


def _make_md(path: Path, source_value: str, x_toml_ref: str | None = None) -> None:
    """辅助：构造带 YAML frontmatter 的 .md 文件"""
    lines = ["---", f'source: "{source_value}"']
    if x_toml_ref:
        lines.append(f'x-toml-ref: "{x_toml_ref}"')
    lines.extend(["---", "", "# Test", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


class TestFixFrontmatterPaths:
    def test_dry_run_does_not_write(self, tmp_path: Path):
        """dry-run 模式不应修改文件"""
        # 项目结构：md 在子目录，使 docs/ 前缀实际产生路径错误
        target_dir = tmp_path / "docs" / "foo"
        target_dir.mkdir(parents=True)
        (target_dir / "bar.md").write_text("", encoding="utf-8")

        md_dir = tmp_path / "sub"
        md_dir.mkdir()
        md_path = md_dir / "test.md"
        _make_md(md_path, "docs/foo/bar.md")

        original_content = md_path.read_text(encoding="utf-8")

        fixes = check_links.fix_frontmatter_paths([md_path], tmp_path, dry_run=True)

        # 应识别出修复需求
        assert len(fixes) == 1
        assert fixes[0].old_value == "docs/foo/bar.md"
        assert fixes[0].new_value == "../docs/foo/bar.md"
        # 但文件不应被修改（dry-run）
        assert md_path.read_text(encoding="utf-8") == original_content

    def test_actual_write_modifies_file(self, tmp_path: Path):
        """非 dry-run 模式应修改文件"""
        # 项目结构：md 在子目录，目标在 docs/
        target_dir = tmp_path / "docs" / "foo"
        target_dir.mkdir(parents=True)
        (target_dir / "bar.md").write_text("", encoding="utf-8")

        md_dir = tmp_path / "sub"
        md_dir.mkdir()
        md_path = md_dir / "test.md"
        _make_md(md_path, "docs/foo/bar.md")

        fixes = check_links.fix_frontmatter_paths([md_path], tmp_path, dry_run=False)

        assert len(fixes) == 1
        new_content = md_path.read_text(encoding="utf-8")
        assert "../docs/foo/bar.md" in new_content
        assert "docs/foo/bar.md" not in new_content or "../docs/foo/bar.md" in new_content

    def test_skip_missing_toml_x_toml_ref(self, tmp_path: Path):
        """x-toml-ref 指向不存在的 TOML 文件，应跳过不修复"""
        md_path = tmp_path / "test.md"
        _make_md(md_path, "docs/foo.md", x_toml_ref="../../missing.toml")

        fixes = check_links.fix_frontmatter_paths([md_path], tmp_path, dry_run=False)

        # source 字段如果目标不存在也会尝试搜索，但 x-toml-ref 的 missing_file 应跳过
        # 仅检查 x-toml-ref 不在修复列表中
        x_toml_fixes = [f for f in fixes if f.field_name == "x-toml-ref"]
        assert len(x_toml_fixes) == 0

    def test_skip_already_valid_paths(self, tmp_path: Path):
        """已有效的路径不应被修复"""
        # 构造有效引用
        target_dir = tmp_path / "foo"
        target_dir.mkdir()
        (target_dir / "bar.md").write_text("", encoding="utf-8")

        md_path = tmp_path / "test.md"
        _make_md(md_path, "foo/bar.md")  # 相对路径有效

        fixes = check_links.fix_frontmatter_paths([md_path], tmp_path, dry_run=False)
        assert len(fixes) == 0

    def test_skip_ambiguous_missing_file(self, tmp_path: Path):
        """多个同名候选但无关键词匹配时应跳过"""
        # 在不同目录创建多个 insight-extraction.md
        (tmp_path / "docs" / "reports" / "report-A-20260701").mkdir(parents=True)
        (tmp_path / "docs" / "reports" / "report-A-20260701" / "insight-extraction.md").write_text("", encoding="utf-8")
        (tmp_path / "docs" / "reports" / "report-B-20260702").mkdir(parents=True)
        (tmp_path / "docs" / "reports" / "report-B-20260702" / "insight-extraction.md").write_text("", encoding="utf-8")

        # md 引用一个不存在的 report-C（同名文件存在但目录不同）
        md_path = tmp_path / "test.md"
        _make_md(md_path, "docs/reports/report-C-20260703/insight-extraction.md")

        fixes = check_links.fix_frontmatter_paths([md_path], tmp_path, dry_run=False)

        # 应跳过（report-C 不在候选路径中）
        assert len(fixes) == 0

    def test_related_fields_also_fixed(self, tmp_path: Path):
        """related_* 字段也应被修复"""
        target_dir = tmp_path / "docs" / "foo"
        target_dir.mkdir(parents=True)
        (target_dir / "bar.md").write_text("", encoding="utf-8")

        md_dir = tmp_path / "sub"
        md_dir.mkdir()
        md_path = md_dir / "test.md"

        # 写入含 related_pattern 字段的 frontmatter
        md_path.write_text(
            "---\n"
            'source: "docs/foo/bar.md"\n'
            'related_pattern: "docs/foo/bar.md"\n'
            "---\n"
            "",
            encoding="utf-8",
        )

        fixes = check_links.fix_frontmatter_paths([md_path], tmp_path, dry_run=False)
        # 应有两条修复：source 和 related_pattern
        field_names = [f.field_name for f in fixes]
        assert "source" in field_names
        assert "related_pattern" in field_names

    def test_no_frontmatter_skipped(self, tmp_path: Path):
        """无 frontmatter 的文件应被跳过"""
        md_path = tmp_path / "test.md"
        md_path.write_text("# No frontmatter\n\nPlain content", encoding="utf-8")

        fixes = check_links.fix_frontmatter_paths([md_path], tmp_path, dry_run=False)
        assert len(fixes) == 0

    def test_multiple_files_batch(self, tmp_path: Path):
        """批量处理多个文件"""
        target_dir = tmp_path / "docs" / "common"
        target_dir.mkdir(parents=True)
        (target_dir / "a.md").write_text("", encoding="utf-8")
        (target_dir / "b.md").write_text("", encoding="utf-8")

        md_dir = tmp_path / "sub"
        md_dir.mkdir()
        md1 = md_dir / "test1.md"
        md2 = md_dir / "test2.md"
        _make_md(md1, "docs/common/a.md")
        _make_md(md2, "docs/common/b.md")

        fixes = check_links.fix_frontmatter_paths([md1, md2], tmp_path, dry_run=False)

        assert len(fixes) == 2
        # 验证两个文件都被修改
        assert "../docs/common/a.md" in md1.read_text(encoding="utf-8")
        assert "../docs/common/b.md" in md2.read_text(encoding="utf-8")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
