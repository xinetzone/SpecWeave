import json
import subprocess
import sys

import pytest

from mdi.validator import ValidationReport

from .helpers import SCRIPTS_DIR, SKILLS_DIR, _make_skill_doc


class TestExistingSkills:
    def test_link_check_cmd_passes(self, validator):
        skill_path = SKILLS_DIR / "link-check-cmd" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("link-check-cmd SKILL.md not found")
        report = validator.validate_file(skill_path)
        assert report.passed(), f"link-check-cmd has errors: {[i.message for i in report.errors()]}"
        assert report.score >= 80

    def test_all_existing_skills_have_zero_errors(self, validator):
        if not SKILLS_DIR.exists():
            pytest.skip("skills directory not found")
        total_errors = 0
        for skill_md in sorted(SKILLS_DIR.rglob("SKILL.md")):
            if "SKILL-TEMPLATE" in str(skill_md):
                continue
            report = validator.validate_file(skill_md)
            errs = report.errors()
            if errs:
                total_errors += len(errs)
                print(f"FAIL: {skill_md.parent.name}: {[e.code + ': ' + e.message for e in errs]}")
        assert total_errors == 0, f"Found {total_errors} errors across all skills"


class TestBatchValidation:
    def test_batch_validate_multiple_files(self, validator, tmp_path):
        f1 = tmp_path / "skill1.md"
        f2 = tmp_path / "skill2.md"
        f1.write_text(_make_skill_doc(name="skill-one"), encoding="utf-8")
        f2.write_text(_make_skill_doc(name="skill-two"), encoding="utf-8")
        reports = validator.batch_validate([f1, f2])
        assert len(reports) == 2
        assert all(isinstance(r, ValidationReport) for r in reports)

    def test_batch_validate_directory(self, validator, tmp_path):
        sub = tmp_path / "skills" / "test-skill"
        sub.mkdir(parents=True)
        skill_file = sub / "SKILL.md"
        skill_file.write_text(_make_skill_doc(name="test-skill"), encoding="utf-8")
        reports = validator.batch_validate([tmp_path / "skills"])
        assert len(reports) >= 1


class TestCLI:
    def test_cli_validate_single_file(self, tmp_path):
        md = tmp_path / "test-skill"
        md.mkdir()
        skill_file = md / "SKILL.md"
        skill_file.write_text(_make_skill_doc(name="test-cli-skill"), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "mdi", "validate", str(skill_file)],
            cwd=str(SCRIPTS_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}\n{result.stdout}"

    def test_cli_validate_score_flag(self, tmp_path):
        skill_name = "test-score-skill"
        md = tmp_path / skill_name
        md.mkdir()
        skill_file = md / "SKILL.md"
        skill_file.write_text(_make_skill_doc(name=skill_name), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "mdi", "validate", str(skill_file), "--score"],
            cwd=str(SCRIPTS_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert f"{skill_name}:" in result.stdout

    def test_cli_validate_json_flag(self, tmp_path):
        md = tmp_path / "test-skill"
        md.mkdir()
        skill_file = md / "SKILL.md"
        skill_file.write_text(_make_skill_doc(name="test-json-skill"), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "mdi", "validate", str(skill_file), "--json"],
            cwd=str(SCRIPTS_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "reports" in output
        assert output["count"] == 1

    def test_cli_validate_nonexistent_path(self):
        result = subprocess.run(
            [sys.executable, "-m", "mdi", "validate", "/nonexistent/path/xyz.md"],
            cwd=str(SCRIPTS_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode != 0

    def test_cli_threshold_failure(self, tmp_path):
        bad_doc = """---
name: bad
---

# Bad
"""
        md = tmp_path / "bad.md"
        md.write_text(bad_doc, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "mdi", "validate", str(md), "--threshold", "90"],
            cwd=str(SCRIPTS_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode != 0
