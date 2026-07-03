import json

from .conftest import mf, create_toml_md


class TestVerifyConsistency:
    def test_verify_passes_after_migration(self, tmp_path):
        md_path = tmp_path / "verify.md"
        create_toml_md(md_path, {"id": "v", "tier": "standard"}, "# Body\n")
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


class TestReportGeneration:
    def test_report_written(self, tmp_path):
        md_path = tmp_path / "rep.md"
        create_toml_md(md_path, {"id": "r"}, "# Body\n")

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
        report_path = tmp_path / "valid.json"
        mf._write_report({"test": True, "count": 42}, str(report_path))
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["test"] is True
        assert data["count"] == 42
