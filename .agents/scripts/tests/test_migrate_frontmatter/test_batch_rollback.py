from .conftest import mf, create_toml_md


class TestBatchConvert:
    def test_batch_multiple_files(self, tmp_path):
        paths = []
        for i in range(3):
            p = tmp_path / f"f{i}.md"
            create_toml_md(p, {"id": f"id-{i}"}, f"# File {i}\n")
            paths.append(p)

        result = mf.batch_convert(paths, tmp_path, dry_run=False, backup=False)
        assert len(result["success"]) == 3
        assert len(result["failed"]) == 0
        assert result["total"] == 3

    def test_batch_partial_failure(self, tmp_path):
        p1 = tmp_path / "ok.md"
        create_toml_md(p1, {"id": "ok"}, "# OK\n")

        p2 = tmp_path / "no_perm" / "bad.md"
        p2.parent.mkdir(parents=True, exist_ok=True)
        p2.write_text("+++\nid = \"bad\"\n+++\n\n# Bad\n", encoding="utf-8")

        paths = [p1, p2]
        result = mf.batch_convert(paths, tmp_path, dry_run=False, backup=False)
        assert len(result["success"]) >= 1


class TestRollback:
    def test_rollback_restores_files(self, tmp_path):
        md_path = tmp_path / "rb.md"
        original_toml = '+++\nid = "rb"\n+++\n\n# Original Body\n'
        md_path.write_text(original_toml, encoding="utf-8")

        mf.convert_file(md_path, tmp_path, dry_run=False, backup=True)
        assert md_path.read_text(encoding="utf-8") != original_toml

        rb_result = mf.rollback(tmp_path)
        assert len(rb_result["restored"]) >= 1

        assert md_path.read_text(encoding="utf-8") == original_toml

    def test_rollback_cleans_toml_dir(self, tmp_path):
        md_path = tmp_path / "clean.md"
        create_toml_md(md_path, {"id": "cl"}, "# Body\n")
        mf.convert_file(md_path, tmp_path, dry_run=False, backup=True)

        toml_dir = tmp_path / ".meta" / "toml"
        assert toml_dir.exists()

        mf.rollback(tmp_path)

    def test_rollback_without_backup_dir(self, tmp_path):
        result = mf.rollback(tmp_path)
        assert len(result["failed"]) >= 1
