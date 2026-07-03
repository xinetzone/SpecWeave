from .conftest import mf, create_toml_md


class TestExternalTomlContent:
    def test_external_toml_is_exact_copy(self, tmp_path):
        md_path = tmp_path / "exact.md"
        original_fm = 'id = "exact"\ntier = "standard"\nnote = "hello world"'
        original = f"+++\n{original_fm}\n+++\n\n# Body\n"
        md_path.write_text(original, encoding="utf-8")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        toml_path = tmp_path / ".meta" / "toml" / "exact.toml"
        ext_content = toml_path.read_text(encoding="utf-8").strip()
        assert ext_content == original_fm

    def test_mirror_directory_structure(self, tmp_path):
        md_path = tmp_path / "docs" / "retrospective" / "README.md"
        create_toml_md(md_path, {"id": "mirror"}, "# Body\n")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)

        toml_path = tmp_path / ".meta" / "toml" / "docs" / "retrospective" / "README.toml"
        assert toml_path.exists()
