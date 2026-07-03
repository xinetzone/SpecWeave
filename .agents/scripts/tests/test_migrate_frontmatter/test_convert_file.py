from .conftest import mf, create_toml_md, create_yaml_md


class TestConvertFile:
    def test_single_file_conversion(self, tmp_path):
        md_path = tmp_path / "docs" / "test.md"
        create_toml_md(md_path, {"id": "doc-001", "tier": "standard"}, "# Hello\n\nWorld\n")

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
        md_path = tmp_path / "guide.md"
        create_toml_md(md_path, {"id": "g1", "domain": "tech"}, "# Body\n")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        toml_path = tmp_path / ".meta" / "toml" / "guide.toml"
        assert toml_path.exists()
        toml_content = toml_path.read_text(encoding="utf-8")
        assert 'id = "g1"' in toml_content
        assert 'domain = "tech"' in toml_content

    def test_body_preserved(self, tmp_path):
        body = "# Title\n\nFirst paragraph.\n\n- item 1\n- item 2\n\nCode: `x = 1`\n"
        md_path = tmp_path / "body_test.md"
        create_toml_md(md_path, {"id": "bt"}, body)

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        content = md_path.read_text(encoding="utf-8")
        assert "# Title" in content
        assert "First paragraph." in content
        assert "- item 1" in content
        assert "`x = 1`" in content

    def test_dry_run_no_files_modified(self, tmp_path):
        md_path = tmp_path / "dry.md"
        create_toml_md(md_path, {"id": "dry"}, "# Body\n")
        original_content = md_path.read_text(encoding="utf-8")

        result = mf.convert_file(md_path, tmp_path, dry_run=True, backup=False)
        assert result["status"] == "planned"
        assert "yaml_frontmatter" in result

        assert md_path.read_text(encoding="utf-8") == original_content
        toml_path = tmp_path / ".meta" / "toml" / "dry.toml"
        assert not toml_path.exists()

    def test_backup_created(self, tmp_path):
        md_path = tmp_path / "bak.md"
        create_toml_md(md_path, {"id": "bak"}, "# Original\n")
        original = md_path.read_text(encoding="utf-8")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=True)
        assert result["status"] == "success"
        assert "backup_path" in result

        backup_path = tmp_path / ".meta" / "backup" / "bak.md"
        assert backup_path.exists()
        assert backup_path.read_text(encoding="utf-8") == original

    def test_idempotency_skips_converted(self, tmp_path):
        md_path = tmp_path / "idem.md"
        create_toml_md(md_path, {"id": "idem"}, "# Body\n")

        r1 = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert r1["status"] == "success"

        r2 = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert r2["status"] == "skipped"
        assert r2["reason"] == "already_migrated"

    def test_special_characters_in_id(self, tmp_path):
        md_path = tmp_path / "special.md"
        create_toml_md(md_path, {"id": "a:b#c中文标题"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "success"

        content = md_path.read_text(encoding="utf-8")
        assert 'x-toml-ref:' in content

        parsed = mf.parse_frontmatter_unified(md_path)
        assert parsed is not None
        assert parsed.get("id") == "a:b#c中文标题"

    def test_yaml_string_escapes_double_quotes(self):
        escaped = mf.escape_yaml_string('he said "hi"')
        assert '\\"' in escaped
        assert escaped.startswith('"')
        assert escaped.endswith('"')

    def test_file_without_id(self, tmp_path):
        md_path = tmp_path / "noid.md"
        create_toml_md(md_path, {"tier": "standard", "count": "5"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "success"

        content = md_path.read_text(encoding="utf-8")
        assert "id:" not in content
        assert 'x-toml-ref:' in content

    def test_file_with_source(self, tmp_path):
        md_path = tmp_path / "src.md"
        create_toml_md(md_path, {"id": "s", "source": "lib/foo.py"}, "# Body\n")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        content = md_path.read_text(encoding="utf-8")
        assert 'source: "lib/foo.py"' in content

    def test_no_frontmatter_skipped(self, tmp_path):
        md_path = tmp_path / "plain.md"
        md_path.write_text("# Just markdown\n\nNo frontmatter.\n", encoding="utf-8")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "skipped"

    def test_yaml_without_toml_ref_skipped(self, tmp_path):
        md_path = tmp_path / "pure_yaml.md"
        create_yaml_md(md_path, {"title": "Pure YAML"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert result["status"] == "skipped"

    def test_array_fields_externalized(self, tmp_path):
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
