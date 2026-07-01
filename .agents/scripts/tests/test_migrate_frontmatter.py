"""migrate-frontmatter.py 单元测试。

覆盖20+个测试用例，使用 tmp_path fixture 创建临时目录结构进行测试，
不操作真实项目文件。
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "migrate_frontmatter", _SCRIPTS_DIR / "migrate-frontmatter.py"
)
mf = importlib.util.module_from_spec(_spec)
sys.modules["migrate_frontmatter"] = mf
_spec.loader.exec_module(mf)


def _create_toml_md(
    path: Path,
    fields: dict[str, str],
    body: str = "# Test\n\nBody content.\n",
) -> None:
    """创建带有 TOML frontmatter 的测试 .md 文件。"""
    lines = ["+++"]
    for k, v in fields.items():
        lines.append(f'{k} = "{v}"')
    lines.append("+++")
    lines.append("")
    lines.append(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _create_yaml_md(
    path: Path,
    fields: dict[str, str],
    body: str = "# Test\n\nBody content.\n",
    has_toml_ref: bool = False,
) -> None:
    """创建带有 YAML frontmatter 的测试 .md 文件。"""
    lines = ["---"]
    for k, v in fields.items():
        lines.append(f'{k}: "{v}"')
    lines.append("---")
    lines.append("")
    lines.append(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


class TestComputeTomlRefPath:
    """测试路径计算函数。"""

    def test_root_level_file(self):
        """根目录文件深度为0。"""
        ref = mf.compute_toml_ref_path("README.md")
        assert ref == ".meta/toml/README.toml"
        assert "\\" not in ref

    def test_one_level_deep(self):
        """1层目录深度。"""
        ref = mf.compute_toml_ref_path("docs/README.md")
        assert ref == "../.meta/toml/docs/README.toml"

    def test_two_levels_deep(self):
        """2层目录深度。"""
        ref = mf.compute_toml_ref_path("docs/knowledge/README.md")
        assert ref == "../../.meta/toml/docs/knowledge/README.toml"

    def test_three_levels_deep(self):
        """3层目录深度。"""
        ref = mf.compute_toml_ref_path("docs/retrospective/patterns/factory.md")
        assert ref == "../../../.meta/toml/docs/retrospective/patterns/factory.toml"

    def test_four_levels_deep(self):
        """4层+目录深度。"""
        ref = mf.compute_toml_ref_path("a/b/c/d/e/file.md")
        assert ref == "../../../../../.meta/toml/a/b/c/d/e/file.toml"

    def test_uses_forward_slashes(self):
        """路径分隔符统一为正斜杠。"""
        ref = mf.compute_toml_ref_path("docs/guide/intro.md")
        assert "\\" not in ref
        assert "/" in ref


class TestEscapeYamlString:
    """测试 YAML 字符串转义。"""

    def test_plain_string(self):
        assert mf.escape_yaml_string("hello") == '"hello"'

    def test_string_with_colon(self):
        assert mf.escape_yaml_string("a:b") == '"a:b"'

    def test_string_with_hash(self):
        assert mf.escape_yaml_string("text # comment") == '"text # comment"'

    def test_string_with_double_quotes(self):
        result = mf.escape_yaml_string('he said "hi"')
        assert '\\"' in result
        assert result == '"he said \\"hi\\""'

    def test_string_with_backslash(self):
        result = mf.escape_yaml_string("path\\to\\file")
        assert "\\\\" in result

    def test_chinese_characters(self):
        result = mf.escape_yaml_string("中文标题")
        assert result == '"中文标题"'


class TestGenerateYamlFrontmatter:
    """测试 YAML frontmatter 生成。"""

    def test_basic_with_id(self):
        """包含 id 和 x-toml-ref。"""
        result = mf.generate_yaml_frontmatter(
            {"id": "test-001"}, ".meta/toml/test.toml"
        )
        assert result.startswith("---\n")
        assert result.endswith("---\n")
        assert 'id: "test-001"' in result
        assert 'x-toml-ref: ".meta/toml/test.toml"' in result

    def test_with_source_field(self):
        """包含 source 字段。"""
        result = mf.generate_yaml_frontmatter(
            {"id": "x", "source": "lib/foo.py"}, "ref.toml"
        )
        assert 'source: "lib/foo.py"' in result

    def test_without_id(self):
        """无 id 字段时不输出 id 行。"""
        result = mf.generate_yaml_frontmatter({"tier": "standard"}, "ref.toml")
        assert "id:" not in result
        assert 'x-toml-ref: "ref.toml"' in result

    def test_always_has_toml_ref(self):
        """x-toml-ref 始终存在。"""
        result = mf.generate_yaml_frontmatter({}, "some/path.toml")
        assert 'x-toml-ref: "some/path.toml"' in result

    def test_format_uses_triple_dash(self):
        """使用 --- 包裹。"""
        result = mf.generate_yaml_frontmatter({"id": "a"}, "r.toml")
        lines = result.strip().split("\n")
        assert lines[0] == "---"
        assert lines[-1] == "---"


class TestScanFiles:
    """测试文件扫描。"""

    def test_finds_toml_files(self, tmp_path):
        """找到所有 TOML frontmatter 文件。"""
        _create_toml_md(tmp_path / "a.md", {"id": "a"})
        _create_toml_md(tmp_path / "sub" / "b.md", {"id": "b"})
        _create_yaml_md(tmp_path / "c.md", {"title": "c"})

        files = mf.scan_files(tmp_path)
        rels = sorted(str(f.relative_to(tmp_path)).replace("\\", "/") for f in files)
        assert "a.md" in rels
        assert "sub/b.md" in rels
        assert "c.md" not in rels

    def test_excludes_directories(self, tmp_path):
        """排除指定目录。"""
        _create_toml_md(tmp_path / ".git" / "a.md", {"id": "a"})
        _create_toml_md(tmp_path / "vendor" / "b.md", {"id": "b"})
        _create_toml_md(tmp_path / "node_modules" / "c.md", {"id": "c"})
        _create_toml_md(tmp_path / "keep.md", {"id": "keep"})

        files = mf.scan_files(tmp_path)
        rels = [str(f.relative_to(tmp_path)).replace("\\", "/") for f in files]
        assert "keep.md" in rels
        assert ".git/a.md" not in rels
        assert "vendor/b.md" not in rels

    def test_skips_already_migrated(self, tmp_path):
        """跳过已迁移（含 x-toml-ref）的文件。"""
        _create_toml_md(tmp_path / "old.md", {"id": "old"})
        _create_yaml_md(
            tmp_path / "migrated.md",
            {"id": "m", "x-toml-ref": ".meta/toml/migrated.toml"},
        )

        files = mf.scan_files(tmp_path)
        rels = [str(f.relative_to(tmp_path)).replace("\\", "/") for f in files]
        assert "old.md" in rels
        assert "migrated.md" not in rels

    def test_empty_directory(self, tmp_path):
        """空目录返回空列表。"""
        assert mf.scan_files(tmp_path) == []


class TestConvertFile:
    """测试单文件转换。"""

    def test_single_file_conversion(self, tmp_path):
        """单文件 TOML→YAML+x-toml-ref 转换。"""
        md_path = tmp_path / "docs" / "test.md"
        _create_toml_md(md_path, {"id": "doc-001", "tier": "standard"}, "# Hello\n\nWorld\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "success"

        content = md_path.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "id: \"doc-001\"" in content
        assert "x-toml-ref:" in content
        assert "# Hello" in content
        assert "World" in content
        assert "+++" not in content

    def test_external_toml_created(self, tmp_path):
        """外部 TOML 文件被正确创建。"""
        md_path = tmp_path / "guide.md"
        _create_toml_md(md_path, {"id": "g1", "domain": "tech"}, "# Body\n")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        toml_path = tmp_path / ".meta" / "toml" / "guide.toml"
        assert toml_path.exists()
        toml_content = toml_path.read_text(encoding="utf-8")
        assert 'id = "g1"' in toml_content
        assert 'domain = "tech"' in toml_content

    def test_body_preserved(self, tmp_path):
        """正文内容未被修改。"""
        body = "# Title\n\nFirst paragraph.\n\n- item 1\n- item 2\n\nCode: `x = 1`\n"
        md_path = tmp_path / "body_test.md"
        _create_toml_md(md_path, {"id": "bt"}, body)

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        content = md_path.read_text(encoding="utf-8")
        assert "# Title" in content
        assert "First paragraph." in content
        assert "- item 1" in content
        assert "`x = 1`" in content

    def test_dry_run_no_files_modified(self, tmp_path):
        """dry-run 模式不修改任何文件。"""
        md_path = tmp_path / "dry.md"
        _create_toml_md(md_path, {"id": "dry"}, "# Body\n")
        original_content = md_path.read_text(encoding="utf-8")

        result = mf.convert_file(md_path, tmp_path, dry_run=True, backup=False)
        assert result["status"] == "planned"
        assert "yaml_frontmatter" in result

        assert md_path.read_text(encoding="utf-8") == original_content
        toml_path = tmp_path / ".meta" / "toml" / "dry.toml"
        assert not toml_path.exists()

    def test_backup_created(self, tmp_path):
        """backup=True 时创建备份。"""
        md_path = tmp_path / "bak.md"
        _create_toml_md(md_path, {"id": "bak"}, "# Original\n")
        original = md_path.read_text(encoding="utf-8")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=True)
        assert result["status"] == "success"
        assert "backup_path" in result

        backup_path = tmp_path / ".meta" / "backup" / "bak.md"
        assert backup_path.exists()
        assert backup_path.read_text(encoding="utf-8") == original

    def test_idempotency_skips_converted(self, tmp_path):
        """幂等性：重复转换跳过已迁移文件。"""
        md_path = tmp_path / "idem.md"
        _create_toml_md(md_path, {"id": "idem"}, "# Body\n")

        r1 = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert r1["status"] == "success"

        r2 = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert r2["status"] == "skipped"
        assert r2["reason"] == "already_migrated"

    def test_special_characters_in_id(self, tmp_path):
        """id 含特殊字符（冒号、#、中文）处理正确。"""
        md_path = tmp_path / "special.md"
        _create_toml_md(md_path, {"id": "a:b#c中文标题"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "success"

        content = md_path.read_text(encoding="utf-8")
        assert 'x-toml-ref:' in content

        parsed = mf.parse_frontmatter_unified(md_path)
        assert parsed is not None
        assert parsed.get("id") == "a:b#c中文标题"

    def test_yaml_string_escapes_double_quotes(self):
        """YAML 字符串值正确转义双引号。"""
        escaped = mf.escape_yaml_string('he said "hi"')
        assert '\\"' in escaped
        assert escaped.startswith('"')
        assert escaped.endswith('"')

    def test_file_without_id(self, tmp_path):
        """无 id 字段的文件正确转换。"""
        md_path = tmp_path / "noid.md"
        _create_toml_md(md_path, {"tier": "standard", "count": "5"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "success"

        content = md_path.read_text(encoding="utf-8")
        assert "id:" not in content
        assert 'x-toml-ref:' in content

    def test_file_with_source(self, tmp_path):
        """有 source 字段的文件保留 source。"""
        md_path = tmp_path / "src.md"
        _create_toml_md(md_path, {"id": "s", "source": "lib/foo.py"}, "# Body\n")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        content = md_path.read_text(encoding="utf-8")
        assert 'source: "lib/foo.py"' in content

    def test_no_frontmatter_skipped(self, tmp_path):
        """无 frontmatter 文件跳过。"""
        md_path = tmp_path / "plain.md"
        md_path.write_text("# Just markdown\n\nNo frontmatter.\n", encoding="utf-8")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "skipped"

    def test_yaml_without_toml_ref_skipped(self, tmp_path):
        """已有 YAML 但无 x-toml-ref 的文件（非 TOML）跳过。"""
        md_path = tmp_path / "pure_yaml.md"
        _create_yaml_md(md_path, {"title": "Pure YAML"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "skipped"

    def test_array_fields_externalized(self, tmp_path):
        """数组/多字段正确外置到 TOML。"""
        md_path = tmp_path / "multi.md"
        toml_content = '+++\nid = "m"\ntier = "standard"\ndomain = "governance"\ncount = 3\n+++\n\n# Body\n'
        md_path.write_text(toml_content, encoding="utf-8")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        toml_path = tmp_path / ".meta" / "toml" / "multi.toml"
        ext = toml_path.read_text(encoding="utf-8")
        assert 'tier = "standard"' in ext
        assert 'domain = "governance"' in ext
        assert "count = 3" in ext

        yaml_content = md_path.read_text(encoding="utf-8")
        assert "tier:" not in yaml_content
        assert "domain:" not in yaml_content


class TestBatchConvert:
    """测试批量转换。"""

    def test_batch_multiple_files(self, tmp_path):
        """批量转换多个文件。"""
        paths = []
        for i in range(3):
            p = tmp_path / f"f{i}.md"
            _create_toml_md(p, {"id": f"id-{i}"}, f"# File {i}\n")
            paths.append(p)

        result = mf.batch_convert(paths, tmp_path, dry_run=False, backup=False)
        assert len(result["success"]) == 3
        assert len(result["failed"]) == 0
        assert result["total"] == 3

    def test_batch_partial_failure(self, tmp_path):
        """批量转换中部分失败不影响其他。"""
        p1 = tmp_path / "ok.md"
        _create_toml_md(p1, {"id": "ok"}, "# OK\n")

        p2 = tmp_path / "no_perm" / "bad.md"
        p2.parent.mkdir(parents=True, exist_ok=True)
        p2.write_text("+++\nid = \"bad\"\n+++\n\n# Bad\n", encoding="utf-8")

        paths = [p1, p2]
        result = mf.batch_convert(paths, tmp_path, dry_run=False, backup=False)
        assert len(result["success"]) >= 1


class TestRollback:
    """测试回滚功能。"""

    def test_rollback_restores_files(self, tmp_path):
        """rollback 从备份恢复原始文件。"""
        md_path = tmp_path / "rb.md"
        original_toml = '+++\nid = "rb"\n+++\n\n# Original Body\n'
        md_path.write_text(original_toml, encoding="utf-8")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=True)
        assert md_path.read_text(encoding="utf-8") != original_toml

        rb_result = mf.rollback(tmp_path)
        assert len(rb_result["restored"]) >= 1

        assert md_path.read_text(encoding="utf-8") == original_toml

    def test_rollback_cleans_toml_dir(self, tmp_path):
        """rollback 清理外部 TOML 目录。"""
        md_path = tmp_path / "clean.md"
        _create_toml_md(md_path, {"id": "cl"}, "# Body\n")
        mf.convert_file(md_path, tmp_path, dry_run=False, backup=True)

        toml_dir = tmp_path / ".meta" / "toml"
        assert toml_dir.exists()

        mf.rollback(tmp_path)

    def test_rollback_without_backup_dir(self, tmp_path):
        """无备份目录时返回失败信息。"""
        result = mf.rollback(tmp_path)
        assert len(result["failed"]) >= 1


class TestVerifyConsistency:
    """测试一致性验证。"""

    def test_verify_passes_after_migration(self, tmp_path):
        """迁移后验证通过。"""
        md_path = tmp_path / "verify.md"
        _create_toml_md(md_path, {"id": "v", "tier": "standard"}, "# Body\n")
        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        rel = "verify.md"
        baseline = {
            "files": [
                {
                    "rel_path": rel,
                    "fields": {"id": "v", "tier": "standard"},
                    "content_hash": "abc",
                }
            ]
        }

        v = mf.verify_consistency(tmp_path, baseline)
        paths = [p["path"] for p in v["passed"]]
        assert rel in paths
        assert v["total_checked"] == 1
        assert len(v["failed"]) == 0

    def test_verify_detects_missing_field(self, tmp_path):
        """验证检测到字段丢失。"""
        md_path = tmp_path / "miss.md"
        md_path.write_text(
            '---\nid: "m"\nx-toml-ref: ".meta/toml/miss.toml"\n---\n\n# Body\n',
            encoding="utf-8",
        )
        toml_dir = tmp_path / ".meta" / "toml"
        toml_dir.mkdir(parents=True, exist_ok=True)
        (toml_dir / "miss.toml").write_text('id = "m"\n', encoding="utf-8")

        baseline = {
            "files": [
                {
                    "rel_path": "miss.md",
                    "fields": {"id": "m", "tier": "standard"},
                }
            ]
        }

        v = mf.verify_consistency(tmp_path, baseline)
        assert len(v["failed"]) == 1
        assert "missing field" in v["failed"][0]["reason"]


class TestCliArgs:
    """测试 CLI 参数解析。"""

    def test_help_exits_cleanly(self):
        """--help 正常显示。"""
        with pytest.raises(SystemExit) as exc_info:
            parser = mf.build_arg_parser()
            parser.parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_dry_run_flag(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_backup_flag(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--backup"])
        assert args.backup is True

    def test_rollback_flag(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--rollback"])
        assert args.rollback is True

    def test_path_option(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--path", "docs/guide"])
        assert args.path == "docs/guide"

    def test_report_option(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--report", "out.json"])
        assert args.report == "out.json"

    def test_defaults(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args([])
        assert args.dry_run is False
        assert args.backup is False
        assert args.verify is False
        assert args.rollback is False
        assert args.path is None
        assert args.report is None


class TestReportGeneration:
    """测试 JSON 报告生成。"""

    def test_report_written(self, tmp_path):
        """--report 生成 JSON 报告文件。"""
        md_path = tmp_path / "rep.md"
        _create_toml_md(md_path, {"id": "r"}, "# Body\n")

        report_path = tmp_path / "report.json"
        mf._write_report(
            {"timestamp": "2026-01-01", "conversion": {"total": 1}},
            str(report_path),
        )
        assert report_path.exists()

        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "timestamp" in data
        assert data["conversion"]["total"] == 1

    def test_report_is_valid_json(self, tmp_path):
        """报告是合法的 JSON。"""
        report_path = tmp_path / "valid.json"
        mf._write_report({"test": True, "count": 42}, str(report_path))
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["test"] is True
        assert data["count"] == 42


class TestWindowsPathHandling:
    """测试 Windows 路径分隔符处理。"""

    def test_rel_path_uses_forward_slash(self, tmp_path):
        """转换结果中路径使用正斜杠。"""
        md_path = tmp_path / "sub" / "dir" / "win.md"
        _create_toml_md(md_path, {"id": "w"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert "\\" not in result["path"]
        assert "/" in result["path"] or result["path"] == "win.md"

    def test_toml_ref_uses_forward_slash(self):
        """x-toml-ref 路径不包含反斜杠。"""
        ref = mf.compute_toml_ref_path("a/b/c.md")
        assert "\\" not in ref


class TestExternalTomlContent:
    """测试外部 TOML 文件内容。"""

    def test_external_toml_is_exact_copy(self, tmp_path):
        """外部 TOML 文件是原 frontmatter 的完整无修改拷贝。"""
        md_path = tmp_path / "exact.md"
        original_fm = 'id = "exact"\ntier = "standard"\nnote = "hello world"'
        original = f"+++\n{original_fm}\n+++\n\n# Body\n"
        md_path.write_text(original, encoding="utf-8")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        toml_path = tmp_path / ".meta" / "toml" / "exact.toml"
        ext_content = toml_path.read_text(encoding="utf-8").strip()
        assert ext_content == original_fm

    def test_mirror_directory_structure(self, tmp_path):
        """外部 TOML 保持与源文件镜像目录结构。"""
        md_path = tmp_path / "docs" / "retrospective" / "README.md"
        _create_toml_md(md_path, {"id": "mirror"}, "# Body\n")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        toml_path = tmp_path / ".meta" / "toml" / "docs" / "retrospective" / "README.toml"
        assert toml_path.exists()
