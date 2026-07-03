class TestFrontmatterParsing:

    def test_toml_ref_string_form(self, parser, tmp_path):
        toml_file = tmp_path / "meta.toml"
        toml_file.write_text('name = "from-toml"\nversion = "2.0.0"\nauthors = ["Tom"]\n', encoding="utf-8")
        md_file = tmp_path / "test.md"
        md_file.write_text('---\nname: from-yaml\ndescription: "Test"\nx-toml-ref: "meta.toml"\n---\n\n# Test\n', encoding="utf-8")
        doc = parser.parse_file(str(md_file))
        assert doc.frontmatter["name"] == "from-yaml"
        assert doc.frontmatter["version"] == "2.0.0"
        assert doc.frontmatter["authors"] == ["Tom"]

    def test_toml_ref_with_key_path(self, parser, tmp_path):
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text('[project]\nname = "myproject"\nversion = "0.1.0"\n[tool.mdi]\nname = "cli-tool"\nversion = "1.0.0"\n', encoding="utf-8")
        md_file = tmp_path / "test.md"
        md_file.write_text('---\ndescription: "CLI"\nx-toml-ref:\n  path: "pyproject.toml"\n  key: "tool.mdi"\n---\n\n# Test\n', encoding="utf-8")
        doc = parser.parse_file(str(md_file))
        assert doc.frontmatter["name"] == "cli-tool"
        assert doc.frontmatter["version"] == "1.0.0"
        assert doc.frontmatter["description"] == "CLI"

    def test_toml_ref_missing_file_warns(self, parser, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text('---\nname: test\nx-toml-ref: "nonexistent.toml"\n---\n\n# Test\n', encoding="utf-8")
        doc = parser.parse_file(str(md_file))
        assert doc.frontmatter["name"] == "test"
        assert len(doc.warnings) > 0
        assert any("不存在" in w for w in doc.warnings)

    def test_toml_ref_parse_text_no_base_dir(self, parser):
        text = '---\nname: test\nx-toml-ref: "some.toml"\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert doc.frontmatter["name"] == "test"
        assert "x-toml-ref" in doc.frontmatter

    def test_yaml_frontmatter(self, parser):
        text = '---\nname: test-skill\nversion: 1.0.0\ndescription: "A test skill"\nuser-invocable: true\n---\n\n# Test Skill\n'
        doc = parser.parse_text(text)
        assert doc.frontmatter["name"] == "test-skill"
        assert doc.frontmatter["version"] == "1.0.0"
        assert doc.frontmatter["description"] == "A test skill"
        assert doc.frontmatter["user-invocable"] is True

    def test_yaml_frontmatter_with_list(self, parser):
        text = '---\nname: test\npaths:\n  - "a.py"\n  - "b.py"\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert "paths" in doc.frontmatter
        assert isinstance(doc.frontmatter["paths"], list)
        assert len(doc.frontmatter["paths"]) == 2

    def test_no_frontmatter(self, parser):
        text = "# Just a title\n\nSome content."
        doc = parser.parse_text(text)
        assert doc.frontmatter == {}

    def test_malformed_yaml_frontmatter_graceful(self, parser):
        text = '---\nname: test\n  invalid: [yaml\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert isinstance(doc.warnings, list)
        assert len(doc.warnings) > 0
