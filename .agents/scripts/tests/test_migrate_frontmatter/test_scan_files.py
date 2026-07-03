from .conftest import mf, create_toml_md, create_yaml_md


class TestScanFiles:
    def test_finds_toml_files(self, tmp_path):
        create_toml_md(tmp_path / "a.md", {"id": "a"})
        create_toml_md(tmp_path / "sub" / "b.md", {"id": "b"})
        create_yaml_md(tmp_path / "c.md", {"title": "c"})

        files = mf.scan_files(tmp_path)
        rels = sorted(str(f.relative_to(tmp_path)).replace("\\", "/") for f in files)
        assert "a.md" in rels
        assert "sub/b.md" in rels
        assert "c.md" not in rels

    def test_excludes_directories(self, tmp_path):
        create_toml_md(tmp_path / ".git" / "a.md", {"id": "a"})
        create_toml_md(tmp_path / "vendor" / "b.md", {"id": "b"})
        create_toml_md(tmp_path / "node_modules" / "c.md", {"id": "c"})
        create_toml_md(tmp_path / "keep.md", {"id": "keep"})

        files = mf.scan_files(tmp_path)
        rels = [str(f.relative_to(tmp_path)).replace("\\", "/") for f in files]
        assert "keep.md" in rels
        assert ".git/a.md" not in rels
        assert "vendor/b.md" not in rels

    def test_skips_already_migrated(self, tmp_path):
        create_toml_md(tmp_path / "old.md", {"id": "old"})
        create_yaml_md(
            tmp_path / "migrated.md",
            {"id": "m", "x-toml-ref": ".meta/toml/migrated.toml"},
        )

        files = mf.scan_files(tmp_path)
        rels = [str(f.relative_to(tmp_path)).replace("\\", "/") for f in files]
        assert "old.md" in rels
        assert "migrated.md" not in rels

    def test_empty_directory(self, tmp_path):
        assert mf.scan_files(tmp_path) == []
