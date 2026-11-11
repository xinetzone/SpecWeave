"""check-links.py 反例修复测试。

覆盖CE-01到CE-04四个问题：
- CE-01/02: 图片语法(![alt](img))不应被误判为链接
- CE-03: 行内代码中的链接示例应被忽略
- CE-04: 带标题的链接[text](url "title")URL应正确解析
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def _import_check_links():
    """导入check-links.py中的函数"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_links", Path(__file__).parent.parent / "check-links.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cl = _import_check_links()


class TestPlaceholderPathSegment:
    """模板占位符嵌在相对路径中间时，必须整体视为占位符而非断链。

    背景（2026-11-09 基线复核）：`.trae/skills/pattern-to-methodology-library/
    assets/pattern-template.md` 里的示例链接
    `../../../../knowledge/<域>/<bundle-id>/index.md` 与
    `../<other-area 或本目录>/<id>.md`，其占位段不是整串角括号目标，
    旧判据只认「整串 <...>」而漏检，最终被记进链接基线。
    """

    def test_placeholder_segment_in_relative_path(self):
        assert cl.is_template_placeholder(
            "../../../../knowledge/<域>/<bundle-id>/index.md"
        ) is True
        assert cl.is_template_placeholder("../<other-area 或本目录>/<id>.md") is True
        assert cl.is_template_placeholder("<相对路径>.md") is True

    def test_plain_relative_path_not_placeholder(self):
        assert cl.is_template_placeholder("../../docs/index.md") is False
        assert cl.is_template_placeholder("<path/to/file.md>") is False

    def test_placeholder_link_not_reported_as_broken(self, tmp_path):
        f = tmp_path / "template.md"
        f.write_text(
            "# 模板\n\n"
            "[bundle](../../../../knowledge/<域>/<bundle-id>/index.md)\n"
            "[pattern](../<other-area 或本目录>/<id>.md)\n",
            encoding="utf-8",
        )
        rc = cl.main(["--path", str(f)])
        assert rc == 0


class TestSingleFileInput:
    """--path 传入单个 .md 文件的回归：防止零文件空扫描的假通过。

    背景（2026-10-21 实测）：find_markdown_files 用 rglob，对文件路径返回
    空，旧逻辑打印「找到 0 个 Markdown 文件…校验通过」并返回 0——门禁
    在零工作量下给出通过语义。修复后单文件直接纳入扫描。
    """

    def test_single_md_file_with_broken_link_fails(self, tmp_path):
        f = tmp_path / "single.md"
        f.write_text("# 单文件\n\n[断链](missing-target.md)\n", encoding="utf-8")
        rc = cl.main(["--path", str(f)])
        assert rc == 1, "单文件输入含断链时应返回 1（旧假通过行为返回 0）"

    def test_single_md_file_without_links_passes(self, tmp_path):
        f = tmp_path / "clean.md"
        f.write_text("# 单文件\n\n无链接内容。\n", encoding="utf-8")
        rc = cl.main(["--path", str(f)])
        assert rc == 0

    def test_single_md_file_with_valid_local_link_passes(self, tmp_path):
        target = tmp_path / "target.md"
        target.write_text("# 目标\n", encoding="utf-8")
        f = tmp_path / "linker.md"
        f.write_text("# 链接\n\n[到目标](target.md)\n", encoding="utf-8")
        rc = cl.main(["--path", str(f)])
        assert rc == 0

    def test_non_md_file_input_warns_and_passes(self, tmp_path, capsys):
        f = tmp_path / "notes.txt"
        f.write_text("not markdown", encoding="utf-8")
        rc = cl.main(["--path", str(f)])
        assert rc == 0
        err = capsys.readouterr().err
        assert "非 .md 文件" in err
        assert "未扫描到任何 Markdown 文件" in err


def _write_and_parse(content: str, tmp_path: Path, filename: str = "test.md"):
    """Helper: 写临时文件并解析链接"""
    f = tmp_path / filename
    f.write_text(content, encoding="utf-8")
    return cl.parse_links(f), f


class TestImageSyntaxIgnored:
    """CE-01/02: 图片语法![alt](img)应被忽略，不是链接。"""

    def test_basic_image_not_treated_as_link(self, tmp_path):
        """![alt](img.png) 不应被识别为链接"""
        links, _ = _write_and_parse("![图片描述](image.png)", tmp_path)
        assert len(links) == 0, f"图片不应被识别为链接，但找到了{len(links)}个链接"

    def test_empty_alt_image_not_treated_as_link(self, tmp_path):
        """![](img.png) 空alt图片也不应被识别"""
        links, _ = _write_and_parse("![](empty-alt.png)", tmp_path)
        assert len(links) == 0, "空alt图片不应被识别为链接"

    def test_image_with_title_not_treated_as_link(self, tmp_path):
        """![alt](img.png "title") 带标题的图片不应被识别"""
        links, _ = _write_and_parse('![图片](image.png "图片标题")', tmp_path)
        assert len(links) == 0, "带标题的图片不应被识别为链接"

    def test_normal_link_still_works(self, tmp_path):
        """正常的链接[text](file.md)应继续正常工作（正向回归）"""
        links, f = _write_and_parse("[正常链接](file.md)", tmp_path)
        assert len(links) == 1
        assert links[0][0] == "正常链接"
        assert links[0][1] == "file.md"

    def test_image_and_link_mixed(self, tmp_path):
        """同一行同时有图片和链接，只应识别链接"""
        links, _ = _write_and_parse("![图片](img.png) 和 [链接](file.md)", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md"
        assert links[0][0] == "链接"


class TestInlineCodeLinksIgnored:
    """CE-03: 行内代码`...`中的链接示例应被忽略。"""

    def test_inline_code_example_ignored(self, tmp_path):
        """行内代码中的链接示例`[text](fake.md)`不应被检查"""
        links, _ = _write_and_parse("使用 `[text](fake-example.md)` 作为示例", tmp_path)
        assert len(links) == 0, "行内代码中的链接示例应被忽略"

    def test_double_backtick_inline_code_ignored(self, tmp_path):
        """双反引号行内代码``[`code`](url)``也应被忽略"""
        links, _ = _write_and_parse("``[`code`](fake-code.md)`` 是代码", tmp_path)
        assert len(links) == 0, "双反引号行内代码中的链接应被忽略"

    def test_link_outside_inline_code_still_works(self, tmp_path):
        """行内代码外的正常链接应继续工作"""
        links, f = _write_and_parse("[真实链接](real.md) 和 `[代码示例](fake.md)`", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "real.md"

    def test_multiple_inline_code_sections(self, tmp_path):
        """多个行内代码块中的链接都应被忽略"""
        content = "`[a](1.md)` 文字 `[b](2.md)` 文字 `[c](3.md)`"
        links, _ = _write_and_parse(content, tmp_path)
        assert len(links) == 0, "所有行内代码块中的链接都应被忽略"

    def test_real_link_after_inline_code(self, tmp_path):
        """行内代码后面的真实链接应被识别"""
        content = "用 `[code](fake.md)` 语法写[真实链接](real.md)"
        links, _ = _write_and_parse(content, tmp_path)
        assert len(links) == 1
        assert links[0][1] == "real.md"


class TestLinkWithTitle:
    """CE-04: 带标题的链接[text](url "title")URL应正确解析（去掉标题部分）。"""

    def test_double_quoted_title_stripped(self, tmp_path):
        """[text](file.md "title") URL应为file.md，不含标题"""
        links, _ = _write_and_parse('[链接](file.md "这是标题")', tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md", f"URL应去掉标题部分，实际是'{links[0][1]}'"

    def test_single_quoted_title_stripped(self, tmp_path):
        """[text](file.md 'title') URL应为file.md"""
        links, _ = _write_and_parse("[链接](file.md '这是标题')", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md"

    def test_link_without_title_unchanged(self, tmp_path):
        """不带标题的普通链接URL应保持不变"""
        links, _ = _write_and_parse("[链接](file.md)", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md"

    def test_external_url_with_title(self, tmp_path):
        """外部URL带标题也应正确解析"""
        links, _ = _write_and_parse('[外部](https://example.com "Example Site")', tmp_path)
        assert len(links) == 1
        assert links[0][1] == "https://example.com"

    def test_url_with_anchor_and_title(self, tmp_path):
        """带锚点和标题的链接应正确处理"""
        links, _ = _write_and_parse('[链接](file.md#section "标题")', tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md#section"

    def test_local_link_check_with_title_passes(self, tmp_path):
        """带标题的本地链接存在时应检查通过（不是误报断链）"""
        target_file = tmp_path / "exists.md"
        target_file.write_text("# exists", encoding="utf-8")
        test_file = tmp_path / "test.md"
        test_file.write_text('[链接](exists.md "标题")', encoding="utf-8")

        links = cl.parse_links(test_file)
        assert len(links) == 1
        url = links[0][1]
        assert url == "exists.md", f"URL应为exists.md，实际是'{url}'"

        checked_url, status, msg = cl.check_local_link(test_file, url)
        assert status == "ok", f"带标题的存在文件应通过检查，status='{status}', msg='{msg}'"


class TestFileUrlPosixResolution:
    """回归：file:/// POSIX 绝对路径不应丢失根斜杠被误判为断链。

    修复前 check_local_link 对 file:/// 执行 parsed.path.lstrip("/")，
    导致 file:///media/... 被解析为相对路径 media/...（丢失前导 /），
    误报"文件不存在"。本测试锁定该场景防止回归。
    """

    def test_posix_absolute_file_url_resolves(self, tmp_path):
        """file:/// 指向的 POSIX 绝对路径文件应检查通过。"""
        target = tmp_path / "posix.md"
        target.write_text("# posix", encoding="utf-8")
        test_file = tmp_path / "test.md"
        test_file.write_text(f"[ref](file:///{target.as_posix()})", encoding="utf-8")

        url = f"file:///{target.as_posix()}"
        checked_url, status, msg = cl.check_local_link(test_file, url)
        assert status == "ok", f"POSIX file:/// 绝对路径应通过，status='{status}', msg='{msg}'"

    def test_posix_absolute_file_url_missing(self, tmp_path):
        """file:/// 指向不存在的 POSIX 路径应如实报告断链（而非路径解析错误）。"""
        test_file = tmp_path / "test.md"
        test_file.write_text("[ref](file:///tmp/definitely-not-exist-xyz.md)", encoding="utf-8")

        url = "file:///tmp/definitely-not-exist-xyz.md"
        checked_url, status, msg = cl.check_local_link(test_file, url)
        assert status == "missing", f"不存在的 POSIX 路径应报告 missing，status='{status}', msg='{msg}'"


class TestBundleRelativeRootResolved:
    """修复：`/` 前缀链接应解析为 bundle 相对路径而非文件系统根路径。

    背景：OKF 工作流反模式4 规定 bundle 内交叉链接统一使用 `/` 开头的
    bundle-relative 路径（如 `/concepts/00-overview.md`）。旧实现用
    `(base_dir / url)` 解析，Windows 路径库把 `/concepts/...` 当作文件系统根，
    丢弃 base_dir 导致误报断链（`D:\\concepts\\...`）。本测试锁定该行为。
    """

    def _build_bundle(self, tmp_path):
        bundle = tmp_path / "bundle"
        bundle.mkdir()
        (bundle / "index.md").write_text("# index", encoding="utf-8")
        (bundle / "log.md").write_text("- log", encoding="utf-8")
        concepts = bundle / "concepts"
        concepts.mkdir()
        (concepts / "target.md").write_text("# target", encoding="utf-8")
        (concepts / "sub-doc.md").write_text("# sub", encoding="utf-8")
        return bundle

    def test_root_prefix_resolves_to_bundle_root(self, tmp_path):
        """`/concepts/target.md` 应解析到 bundle 根下的 concepts/target.md。"""
        bundle = self._build_bundle(tmp_path)
        test_file = bundle / "concepts" / "sub-doc.md"

        checked_url, status, msg = cl.check_local_link(test_file, "/concepts/target.md")
        assert status == "ok", f"bundle 相对链接应通过，status='{status}', msg='{msg}'"

    def test_missing_when_target_absent(self, tmp_path):
        """`/` 前缀指向不存在的文件应如实报告 missing（而非路径解析错误）。"""
        bundle = self._build_bundle(tmp_path)
        test_file = bundle / "concepts" / "sub-doc.md"

        checked_url, status, msg = cl.check_local_link(test_file, "/concepts/not-exist.md")
        assert status == "missing", f"不在的 bundle 目标应报告 missing，status='{status}', msg='{msg}'"

    def test_scan_root_fallback_without_bundle_roots(self, tmp_path):
        """无 bundle 根时，传入 scan_root 应作为 `/` 前缀链接的基准。"""
        root = tmp_path / "scanroot"
        root.mkdir()
        sub = root / "nested"
        sub.mkdir()
        (root / "target.md").write_text("# t", encoding="utf-8")
        (sub / "doc.md").write_text("# d", encoding="utf-8")

        checked_url, status, msg = cl.check_local_link(
            sub / "doc.md", "/target.md", scan_root=root
        )
        assert status == "ok", f"scan_root 回退应通过，status='{status}', msg='{msg}'"

    def test_frontmatter_bundle_root_resolved(self, tmp_path):
        """frontmatter sources 中的 `/references/...` 也应按 bundle 根解析。"""
        bundle = self._build_bundle(tmp_path)
        (bundle / "references").mkdir()
        (bundle / "references" / "facts.md").write_text("# facts", encoding="utf-8")
        sub_doc = bundle / "concepts" / "sub-doc.md"

        result = cl._check_single_path(sub_doc, "source", "/references/facts.md")
        assert result is None, f"frontmatter bundle 相对路径应通过，实际: {result}"


class TestNonPathReferencesIgnored:
    """提取器不应把非路径文本当成链接目标（假阳性）。

    背景：模板里的 `<占位符>`、表格单元里的正文短语曾被当成相对路径，
    报成 missing 后混入真实断链，抬高了存量噪音。
    """

    def test_angle_bracket_placeholder_not_parsed(self, tmp_path):
        links, _ = _write_and_parse(
            "见 [链接](<占位符>) 与 [示例](<url>)\n", tmp_path
        )
        urls = [u for _, u, _ in links]
        assert "<占位符>" not in urls
        assert "<url>" not in urls

    def test_angle_bracket_real_destination_still_parsed(self, tmp_path):
        """带路径分隔符与扩展名的角括号目标是合法 Markdown，必须保留。"""
        links, _ = _write_and_parse(
            "[示例](<docs/guide.md>)\n", tmp_path
        )
        assert [u for _, u, _ in links] == ["<docs/guide.md>"]

    def test_prose_phrase_not_parsed(self, tmp_path):
        links, _ = _write_and_parse(
            "| [见说明](见下方) | [详见](见上文第 3 节) |\n", tmp_path
        )
        assert links == []

    def test_real_relative_refs_still_parsed(self, tmp_path):
        """真实相对引用（目录、上级目录、带扩展名文件）不得被过滤。"""
        links, _ = _write_and_parse(
            "[a](docs/) [b](../guide) [c](a.md) [d](notes#L1)\n", tmp_path
        )
        assert [u for _, u, _ in links] == ["docs/", "../guide", "a.md", "notes#L1"]

    def test_external_urls_unaffected(self, tmp_path):
        links, _ = _write_and_parse(
            "[x](https://example.com/a) [y](mailto:a@b.com)\n", tmp_path
        )
        assert [u for _, u, _ in links] == ["https://example.com/a", "mailto:a@b.com"]


class TestSubmoduleUnknownStates:
    """子模块三态判定：未检出算 unknown，已检出但缺文件仍是断链。

    背景：CI 默认不 `git submodule update --init --recursive`，未检出的
    子模块内目标必然不存在，若一律报断链就把环境缺失当成缺陷；但反过来
    一刀切把子模块内缺失全部吞掉，又会静默掩盖已检出子模块里的真断链。
    因此必须区分三种情形：
      - 子模块目录不存在（未初始化）→ unknown
      - 子模块目录存在但为空（未检出）→ unknown
      - 子模块已检出（目录非空）→ 目标缺失照常报 missing
    """

    SUBMODULE_PATH = "submod/foo"

    def _make_repo(self, tmp_path: Path) -> Path:
        """构造带 .gitmodules 的临时仓库根（不含 git 索引）。"""
        root = tmp_path / "repo"
        root.mkdir()
        (root / ".gitmodules").write_text(
            '[submodule "foo"]\n'
            f"\tpath = {self.SUBMODULE_PATH}\n"
            "\turl = https://example.com/foo.git\n",
            encoding="utf-8",
        )
        (root / "doc.md").write_text("# 文档\n", encoding="utf-8")
        return root

    def test_not_initialized_directory_is_unknown(self, tmp_path):
        """子模块目录根本不存在 → unknown，不报断链。"""
        root = self._make_repo(tmp_path)
        target = root / self.SUBMODULE_PATH / "missing.md"

        assert cl.submodule_check_state(target, root) == "not_initialized"

        _, status, msg = cl.check_local_link(
            root / "doc.md", f"{self.SUBMODULE_PATH}/missing.md", project_root=root
        )
        assert status == "unknown", f"目录不存在应为 unknown，实际 status='{status}', msg='{msg}'"
        assert cl.SUBMODULE_UNKNOWN_NOT_INITIALIZED in msg
        assert cl.SUBMODULE_SKIP_NOTE in msg

    def test_empty_submodule_directory_is_unknown(self, tmp_path):
        """子模块目录存在但为空（未检出）→ unknown，不报断链。"""
        root = self._make_repo(tmp_path)
        (root / self.SUBMODULE_PATH).mkdir(parents=True)
        target = root / self.SUBMODULE_PATH / "missing.md"

        assert cl.submodule_check_state(target, root) == "empty"

        _, status, msg = cl.check_local_link(
            root / "doc.md", f"{self.SUBMODULE_PATH}/missing.md", project_root=root
        )
        assert status == "unknown", f"空子模块应为 unknown，实际 status='{status}', msg='{msg}'"
        assert cl.SUBMODULE_UNKNOWN_EMPTY in msg

    def test_checked_out_submodule_missing_file_is_broken(self, tmp_path):
        """子模块已检出但目标文件缺失 → 仍然是断链（不能被静默吞掉）。"""
        root = self._make_repo(tmp_path)
        sub = root / self.SUBMODULE_PATH
        sub.mkdir(parents=True)
        (sub / "README.md").write_text("# foo\n", encoding="utf-8")
        target = sub / "missing.md"

        assert cl.submodule_check_state(target, root) == "checked_out"

        _, status, msg = cl.check_local_link(
            root / "doc.md", f"{self.SUBMODULE_PATH}/missing.md", project_root=root
        )
        assert status == "missing", f"已检出子模块缺文件应报 missing，实际 status='{status}', msg='{msg}'"
        assert "文件不存在" in msg

    def test_checked_out_submodule_existing_file_is_ok(self, tmp_path):
        """已检出子模块内的现存文件照常通过（正向对照）。"""
        root = self._make_repo(tmp_path)
        sub = root / self.SUBMODULE_PATH
        sub.mkdir(parents=True)
        (sub / "guide.md").write_text("# guide\n", encoding="utf-8")

        _, status, msg = cl.check_local_link(
            root / "doc.md", f"{self.SUBMODULE_PATH}/guide.md", project_root=root
        )
        assert status == "ok", f"现存文件应通过，实际 status='{status}', msg='{msg}'"

    def test_outside_submodule_missing_file_is_broken(self, tmp_path):
        """不在任何子模块内的缺失目标与子模块逻辑无关，照常报断链。"""
        root = self._make_repo(tmp_path)
        target = root / "ordinary" / "missing.md"

        assert cl.submodule_check_state(target, root) == "outside"

        _, status, _ = cl.check_local_link(root / "doc.md", "ordinary/missing.md")
        assert status == "missing"

    def test_frontmatter_path_in_empty_submodule_is_skipped(self, tmp_path):
        """frontmatter 路径同样适用三态：未检出子模块内 → 跳过而非断链。"""
        root = self._make_repo(tmp_path)
        (root / self.SUBMODULE_PATH).mkdir(parents=True)
        bundle = root / "docs" / "bundle"
        bundle.mkdir(parents=True)
        md = bundle / "index.md"
        md.write_text(
            "---\nsource: ../../submod/foo/facts.md\n---\n\n# 索引\n",
            encoding="utf-8",
        )

        skipped: list[tuple[Path, str, str, str]] = []
        broken = cl.check_frontmatter_paths(
            [md], project_root=root, skipped=skipped
        )
        assert broken == [], f"未检出子模块内的 frontmatter 路径不应报断链: {broken}"
        assert len(skipped) == 1
        assert cl.SUBMODULE_UNKNOWN_EMPTY in skipped[0][3]

    def test_main_reports_and_excludes_unknown_from_verdict(self, tmp_path, monkeypatch, capsys):
        """main 输出必须明示跳过数量，且 unknown 不参与断链判定。"""
        root = self._make_repo(tmp_path)
        (root / self.SUBMODULE_PATH).mkdir(parents=True)
        doc = root / "doc.md"
        doc.write_text(
            f"# 文档\n\n[子模块内文件]({self.SUBMODULE_PATH}/missing.md)\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(cl, "resolve_project_root", lambda _p: root)

        rc = cl.main(["--path", str(doc)])
        out = capsys.readouterr().out
        assert rc == 0, f"仅未检出子模块链接时不应失败，rc={rc}"
        assert "跳过 1 条子模块链接（未检出）" in out
        assert "空目录 1" in out
        assert "跳过 1 条未检出子模块链接，未参与校验" in out


class TestFrontmatterPathFormJudgement:
    """按字段分治后的「防吞缺陷」验收。

    背景（2026-11-11）：`source` 允许散文化溯源描述，判据只在「路径形态」时
    校验；但判据一旦写宽，就会把真断链一起吞掉。三条断言分别锁住三个方向：
      1. 路径形态但写错的值仍然报断链——即便它带中文锚点（锚点里的中文
         不应让整串被误判为散文）；
      2. 散文化值不报断链，但必须计入跳过数并在 --json 中单列；
      3. `x-toml-ref` 指向不存在的文件仍然报断链。
    """

    @staticmethod
    def _repo(tmp_path: Path) -> Path:
        root = tmp_path / "repo"
        (root / "docs" / "assets").mkdir(parents=True)
        (root / "docs" / "reports").mkdir(parents=True)
        (root / "docs" / "assets" / "real.md").write_text("# 真实文件\n", encoding="utf-8")
        return root

    @staticmethod
    def _json_of(out: str) -> dict:
        import json

        start = out.find("\n{\n")
        assert start >= 0, f"输出中没有 JSON 段: {out[-500:]}"
        return json.JSONDecoder().raw_decode(out[start + 1:])[0]

    def test_path_form_source_with_chinese_anchor_still_reports_broken(
        self, tmp_path, monkeypatch, capsys
    ):
        """真实文件存在、但 source 写错目录——仍是断链，中文锚点不构成豁免。"""
        root = self._repo(tmp_path)
        doc = root / "docs" / "reports" / "a.md"
        doc.write_text(
            "---\nsource: ../asset/real.md#中文锚点\n---\n\n# 报告\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(cl, "resolve_project_root", lambda _p: root)

        rc = cl.main(["--path", str(doc), "--check-frontmatter-paths"])
        out = capsys.readouterr().out
        assert rc == 1, f"写错的路径形态 source 必须报断链，rc={rc}"
        assert "文件不存在" in out
        assert "散文化" not in out

    def test_prose_source_skipped_but_counted(self, tmp_path, monkeypatch, capsys):
        """散文化 source 不按路径校验，但必须计数且写入 --json 的独立字段。"""
        root = self._repo(tmp_path)
        doc = root / "docs" / "reports" / "b.md"
        doc.write_text(
            "---\nsource: 微信公众号文章《深度复盘》+ 内部访谈记录\n---\n\n# 报告\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(cl, "resolve_project_root", lambda _p: root)

        rc = cl.main(["--path", str(doc), "--check-frontmatter-paths", "--json"])
        out = capsys.readouterr().out
        assert rc == 0, f"散文化 source 不应报断链，rc={rc}"
        assert "跳过 1 条散文化 source" in out
        payload = self._json_of(out)
        skipped = payload["prose_skipped_frontmatter"]
        assert len(skipped) == 1
        assert skipped[0]["field"] == "source"
        assert payload["summary"]["prose_skipped_frontmatter"] == 1

    def test_missing_x_toml_ref_reports_broken(self, tmp_path, monkeypatch, capsys):
        """`x-toml-ref` 不受路径形态豁免：指向不存在的 TOML 必须报断链。"""
        root = self._repo(tmp_path)
        doc = root / "docs" / "reports" / "c.md"
        doc.write_text(
            "---\nx-toml-ref: ../../.meta/toml/docs/reports/c.toml\n---\n\n# 报告\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(cl, "resolve_project_root", lambda _p: root)

        rc = cl.main(["--path", str(doc), "--check-frontmatter-paths"])
        out = capsys.readouterr().out
        assert rc == 1, f"缺失的 x-toml-ref 必须报断链，rc={rc}"
        assert "c.toml" in out


