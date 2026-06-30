"""lib.link_fixer 单元测试。

覆盖主要使用场景：
- parse_file_url / extract_filename_from_url: URL解析
- os_path_to_posix: 路径格式转换
- compute_relative_path: 相对路径计算
- is_template_link: 模板链接识别
- is_code_fence_context: 代码块上下文判断
- fix_link_url: 核心链接修复逻辑（绝对路径→相对、层级校正、目录斜杠、同文件锚点）
- fix_file_links: 单文件修复（dry-run/实际写入）
- apply_filename_mapping / apply_line_remap: 映射工具
- try_adjust_relative_depth: 层级深度校正
- _infer_project_root: 项目根推断
"""

import pytest
from pathlib import Path

from lib.link_fixer import (
    parse_file_url,
    extract_filename_from_url,
    os_path_to_posix,
    compute_relative_path,
    is_template_link,
    is_code_fence_context,
    fix_link_url,
    fix_file_links,
    apply_filename_mapping,
    apply_line_remap,
    try_adjust_relative_depth,
    _infer_project_root,
    fix_broken_links,
    _is_excluded_path,
)


class TestParseFileUrl:
    """parse_file_url 测试。"""

    def test_plain_path_no_anchor(self):
        path, anchor = parse_file_url("D:/spaces/SpecWeave/docs/guide.md")
        assert path == "D:/spaces/SpecWeave/docs/guide.md"
        assert anchor == ""

    def test_path_with_anchor(self):
        path, anchor = parse_file_url("D:/spaces/SpecWeave/docs/guide.md#L10-L20")
        assert path == "D:/spaces/SpecWeave/docs/guide.md"
        assert anchor == "#L10-L20"

    def test_unix_path_with_anchor(self):
        path, anchor = parse_file_url("/home/user/project/README.md#section")
        assert path == "/home/user/project/README.md"
        assert anchor == "#section"

    def test_empty_string(self):
        path, anchor = parse_file_url("")
        assert path == ""
        assert anchor == ""


class TestExtractFilenameFromUrl:
    """extract_filename_from_url 测试。"""

    def test_windows_path(self):
        assert extract_filename_from_url("D:/spaces/docs/guide.md") == "guide.md"

    def test_unix_path(self):
        assert extract_filename_from_url("/home/user/README.md") == "README.md"

    def test_filename_only(self):
        assert extract_filename_from_url("guide.md") == "guide.md"


class TestOsPathToPosix:
    """os_path_to_posix 测试。"""

    def test_forward_slashes_unchanged(self):
        assert os_path_to_posix("docs/guide.md") == "docs/guide.md"

    def test_backslashes_converted(self):
        assert os_path_to_posix("docs\\guide.md") == "docs/guide.md"

    def test_mixed_slashes(self):
        assert os_path_to_posix("docs\\sub/guide.md") == "docs/sub/guide.md"

    def test_path_object(self):
        p = Path("docs") / "guide.md"
        result = os_path_to_posix(p)
        assert "\\" not in result


class TestComputeRelativePath:
    """compute_relative_path 测试。"""

    def test_same_directory(self, tmp_path):
        src = tmp_path / "a.md"
        tgt = tmp_path / "b.md"
        src.write_text("a", encoding="utf-8")
        tgt.write_text("b", encoding="utf-8")
        rel = compute_relative_path(src, tgt)
        assert rel == "b.md"

    def test_subdirectory(self, tmp_path):
        src = tmp_path / "a.md"
        sub = tmp_path / "docs"
        sub.mkdir()
        tgt = sub / "b.md"
        src.write_text("a", encoding="utf-8")
        tgt.write_text("b", encoding="utf-8")
        rel = compute_relative_path(src, tgt)
        assert rel == "docs/b.md"

    def test_parent_directory(self, tmp_path):
        sub = tmp_path / "docs"
        sub.mkdir()
        src = sub / "a.md"
        tgt = tmp_path / "b.md"
        src.write_text("a", encoding="utf-8")
        tgt.write_text("b", encoding="utf-8")
        rel = compute_relative_path(src, tgt)
        assert rel == "../b.md"

    def test_readme_directory_link(self, tmp_path):
        src = tmp_path / "index.md"
        sub = tmp_path / "guide"
        sub.mkdir()
        readme = sub / "README.md"
        src.write_text("idx", encoding="utf-8")
        readme.write_text("guide", encoding="utf-8")
        rel = compute_relative_path(src, readme)
        assert rel == "guide/"
        assert rel.endswith("/")

    def test_same_file_returns_empty(self, tmp_path):
        src = tmp_path / "same.md"
        src.write_text("x", encoding="utf-8")
        assert compute_relative_path(src, src) == ""

    def test_directory_target_with_slash(self, tmp_path):
        src = tmp_path / "a.md"
        sub = tmp_path / "mydir"
        sub.mkdir()
        src.write_text("a", encoding="utf-8")
        rel = compute_relative_path(src, sub)
        assert rel == "mydir/"


class TestIsTemplateLink:
    """is_template_link 测试。"""

    def test_template_text_link(self):
        assert is_template_link("link", "path/to/file.md") is True
        assert is_template_link("path", "some.md") is True
        assert is_template_link("xxx.md", "any.md") is True

    def test_template_url_pattern(self):
        assert is_template_link("see", "path/") is True
        assert is_template_link("ref", "URL") is True

    def test_real_link_not_template(self):
        assert is_template_link("入门指南", "docs/getting-started.md") is False
        assert is_template_link("架构说明", "architecture.md") is False

    def test_arrow_notation_template(self):
        assert is_template_link("old → new", "old_name.md") is True
        assert is_template_link("source → target", "path") is True

    def test_empty_text(self):
        assert is_template_link("", "real.md") is False


class TestIsCodeFenceContext:
    """is_code_fence_context 测试。"""

    def test_outside_code_block(self):
        content = "some text\n[a](b.md)\nmore text"
        pos = content.index("[a]")
        assert is_code_fence_context(content, pos) is False

    def test_inside_code_fence(self):
        content = "text\n```\n[a](b.md)\n```\nmore"
        pos = content.index("[a]")
        assert is_code_fence_context(content, pos) is True

    def test_after_code_fence(self):
        content = "```\ncode\n```\n[a](b.md)"
        pos = content.index("[a]")
        assert is_code_fence_context(content, pos) is False

    def test_inside_inline_code(self):
        content = "use the `[a](b.md)` syntax here"
        pos = content.index("[a]")
        assert is_code_fence_context(content, pos) is True


class TestApplyFilenameMapping:
    """apply_filename_mapping 测试。"""

    def test_no_mapping_returns_original(self):
        assert apply_filename_mapping("old.md", None) == "old.md"
        assert apply_filename_mapping("old.md", {}) == "old.md"

    def test_mapping_applied(self):
        m = {"old.md": "new.md"}
        assert apply_filename_mapping("old.md", m) == "new.md"

    def test_mapping_with_directory(self):
        m = {"old.html": "new.html"}
        result = apply_filename_mapping("docs/old.html", m)
        assert result == "docs/new.html"

    def test_unmapped_file_unchanged(self):
        m = {"old.md": "new.md"}
        assert apply_filename_mapping("other.md", m) == "other.md"


class TestApplyLineRemap:
    """apply_line_remap 测试。"""

    def test_no_remap_returns_original(self):
        assert apply_line_remap("#L10", None, "f.md") == "#L10"
        assert apply_line_remap("#L10", {}, "f.md") == "#L10"

    def test_non_anchor_unchanged(self):
        assert apply_line_remap("section", {"f.md": {10: 20}}, "f.md") == "section"

    def test_single_line_remap(self):
        remap = {"guide.md": {10: 15}}
        assert apply_line_remap("#L10", remap, "guide.md") == "#L15"

    def test_range_remap(self):
        remap = {"guide.md": {10: 12, 20: 25}}
        assert apply_line_remap("#L10-L20", remap, "guide.md") == "#L12-L25"

    def test_unmapped_line_stays(self):
        remap = {"guide.md": {10: 15}}
        assert apply_line_remap("#L99", remap, "guide.md") == "#L99"

    def test_different_file_unmapped(self):
        remap = {"other.md": {10: 15}}
        assert apply_line_remap("#L10", remap, "guide.md") == "#L10"


class TestTryAdjustRelativeDepth:
    """try_adjust_relative_depth 测试。"""

    def test_correct_path_no_adjustment_needed(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        guide = docs / "guide.md"
        src = tmp_path / "README.md"
        guide.write_text("g", encoding="utf-8")
        src.write_text("idx", encoding="utf-8")
        result = try_adjust_relative_depth("docs/guide.md", src)
        assert result is None

    def test_file_moved_one_level_deeper(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        deep = docs / "deep"
        deep.mkdir()
        target = tmp_path / "target.md"
        source = deep / "source.md"
        target.write_text("t", encoding="utf-8")
        source.write_text("s", encoding="utf-8")
        result = try_adjust_relative_depth("../target.md", source)
        assert result is not None
        assert result.name == "target.md"

    def test_file_moved_one_level_shallower(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        target = sub / "target.md"
        source = tmp_path / "source.md"
        target.write_text("t", encoding="utf-8")
        source.write_text("s", encoding="utf-8")
        result = try_adjust_relative_depth("../target.md", source)
        assert result is None

    def test_absolute_path_returns_none(self, tmp_path):
        src = tmp_path / "a.md"
        src.write_text("a", encoding="utf-8")
        assert try_adjust_relative_depth("/absolute/path.md", src) is None

    def test_empty_url_returns_none(self, tmp_path):
        src = tmp_path / "a.md"
        src.write_text("a", encoding="utf-8")
        assert try_adjust_relative_depth("", src) is None


class TestFixLinkUrlAbsoluteToRelative:
    """fix_link_url: file:/// 绝对路径转换测试。"""

    def test_file_url_to_relative(self, tmp_path):
        project = tmp_path
        docs = project / "docs"
        docs.mkdir()
        target = docs / "guide.md"
        source = project / "README.md"
        target.write_text("# Guide", encoding="utf-8")
        source.write_text("idx", encoding="utf-8")
        abs_url = f"file:///{str(target).replace(chr(92), '/')}"
        result = fix_link_url(abs_url, source, project)
        assert result is not None
        new_url, fix_type, _ = result
        assert fix_type == "absolute_to_relative"
        assert "file:///" not in new_url
        assert "guide.md" in new_url

    def test_file_url_same_file_becomes_anchor(self, tmp_path):
        project = tmp_path
        source = project / "mypage.md"
        source.write_text("# Title\n\ncontent", encoding="utf-8")
        abs_url = f"file:///{str(source).replace(chr(92), '/')}#section"
        result = fix_link_url(abs_url, source, project)
        assert result is not None
        new_url, fix_type, _ = result
        assert fix_type == "same_file_anchor"
        assert new_url == "#section"

    def test_external_url_not_modified(self, tmp_path):
        source = tmp_path / "a.md"
        source.write_text("a", encoding="utf-8")
        assert fix_link_url("https://example.com", source, tmp_path) is None
        assert fix_link_url("http://example.com", source, tmp_path) is None
        assert fix_link_url("mailto:test@example.com", source, tmp_path) is None

    def test_anchor_only_not_modified(self, tmp_path):
        source = tmp_path / "a.md"
        source.write_text("a", encoding="utf-8")
        assert fix_link_url("#section", source, tmp_path) is None

    def test_directory_missing_slash_gets_slash(self, tmp_path):
        project = tmp_path
        docs = project / "docs"
        docs.mkdir()
        (docs / "README.md").write_text("docs index", encoding="utf-8")
        source = project / "README.md"
        source.write_text("idx", encoding="utf-8")
        result = fix_link_url("docs", source, project)
        assert result is not None
        new_url, fix_type, _ = result
        assert fix_type == "dir_slash"
        assert new_url == "docs/"


class TestFixFileLinks:
    """fix_file_links 单文件修复测试。"""

    def test_dry_run_does_not_modify_file(self, tmp_path):
        project = tmp_path
        docs = project / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("# Guide", encoding="utf-8")
        source = project / "README.md"
        abs_url = f"file:///{str(docs / 'guide.md').replace(chr(92), '/')}"
        source.write_text(f"[link]({abs_url})", encoding="utf-8")
        original = source.read_text(encoding="utf-8")
        fixes = fix_file_links(source, project, dry_run=True)
        assert len(fixes) > 0
        assert source.read_text(encoding="utf-8") == original

    def test_apply_modifies_file(self, tmp_path):
        project = tmp_path
        docs = project / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("# Guide", encoding="utf-8")
        source = project / "README.md"
        abs_url = f"file:///{str(docs / 'guide.md').replace(chr(92), '/')}"
        source.write_text(f"[link]({abs_url})", encoding="utf-8")
        fixes = fix_file_links(source, project, dry_run=False)
        assert len(fixes) > 0
        content = source.read_text(encoding="utf-8")
        assert "file:///" not in content
        assert "docs/guide.md" in content

    def test_skips_code_fence_links(self, tmp_path):
        project = tmp_path
        source = project / "README.md"
        source.write_text("```\n[example](file:///D:/fake.md)\n```\n", encoding="utf-8")
        fixes = fix_file_links(source, project, dry_run=True)
        assert len(fixes) == 0

    def test_no_broken_links_returns_empty(self, tmp_path):
        project = tmp_path
        source = project / "README.md"
        source.write_text("[ok](docs/guide.md)", encoding="utf-8")
        fixes = fix_file_links(source, project, dry_run=True)
        assert len(fixes) == 0


class TestInferProjectRoot:
    """_infer_project_root 测试。"""

    def test_finds_agents_directory(self, tmp_path):
        project = tmp_path
        agents = project / ".agents"
        agents.mkdir()
        sub = project / "docs"
        sub.mkdir()
        start = sub / "README.md"
        start.write_text("x", encoding="utf-8")
        root = _infer_project_root(start)
        assert root == project.resolve()

    def test_no_agents_dir_returns_cwd(self, tmp_path):
        isolated = tmp_path / "isolated"
        isolated.mkdir()
        start = isolated / "README.md"
        start.write_text("x", encoding="utf-8")
        root = _infer_project_root(start)
        assert isinstance(root, Path)
        assert root.is_dir()


class TestIsExcludedPath:
    """_is_excluded_path 测试。"""

    def test_vendor_excluded(self, tmp_path):
        project = tmp_path
        vendor = project / "vendor"
        vendor.mkdir()
        assert _is_excluded_path(vendor, project) is True

    def test_git_excluded(self, tmp_path):
        project = tmp_path
        git = project / ".git"
        git.mkdir()
        assert _is_excluded_path(git, project) is True

    def test_normal_dir_not_excluded(self, tmp_path):
        project = tmp_path
        docs = project / "docs"
        docs.mkdir()
        assert _is_excluded_path(docs, project) is False

    def test_path_outside_project_excluded(self, tmp_path):
        project = tmp_path / "project"
        project.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        assert _is_excluded_path(outside, project) is True


class TestFixBrokenLinksIntegration:
    """fix_broken_links 集成测试。"""

    def test_directory_fix_dry_run(self, tmp_path):
        project = tmp_path
        (project / ".agents").mkdir()
        docs = project / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("# Guide", encoding="utf-8")
        readme = project / "README.md"
        readme.write_text("[g](docs/guide.md)", encoding="utf-8")
        fixes = fix_broken_links(str(project), dry_run=True, verbose=False)
        assert isinstance(fixes, list)

    def test_single_file_fix(self, tmp_path):
        project = tmp_path
        (project / ".agents").mkdir()
        f = project / "test.md"
        f.write_text("hello", encoding="utf-8")
        fixes = fix_broken_links(str(f), dry_run=True, verbose=False)
        assert isinstance(fixes, list)
