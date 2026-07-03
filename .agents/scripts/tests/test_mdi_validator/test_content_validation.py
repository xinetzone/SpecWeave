from .helpers import _make_skill_doc


class TestFileUrlDetection:
    def test_file_url_detected(self, validator, tmp_path):
        md = tmp_path / "test.md"
        content = _make_skill_doc() + "\n\n[link](file:///D:/test/file.md)\n"
        md.write_text(content, encoding="utf-8")
        report = validator.validate_file(md)
        warn_codes = {i.code for i in report.warnings()}
        assert "W008" in warn_codes

    def test_no_file_url_passes(self, validator, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(_make_skill_doc(), encoding="utf-8")
        report = validator.validate_file(md)
        w008_warnings = [i for i in report.warnings() if i.code == "W008"]
        assert len(w008_warnings) == 0


class TestRelativeLinkValidation:
    def test_broken_relative_link_detected(self, validator, tmp_path):
        md = tmp_path / "test-skill"
        md.mkdir()
        skill_file = md / "SKILL.md"
        content = _make_skill_doc() + "\n\n[broken](nonexistent-file.md)\n"
        skill_file.write_text(content, encoding="utf-8")
        report = validator.validate_file(skill_file)
        w007 = [i for i in report.warnings() if i.code == "W007"]
        assert len(w007) >= 1


class TestWhyExplanation:
    def test_few_why_explanations_with_must_rules_warns(self, validator, tmp_path):
        content = """---
name: test-why
version: "1.0.0"
description: "当用户提到测试时，必须使用此技能。这是一个测试文档，描述足够长以通过长度验证检查。"
---

# Test

## 1. Rules

**必须**遵守规则一。
**必须**遵守规则二。
**必须**遵守规则三。
**禁止**违反规则四。
"""
        md = tmp_path / "SKILL.md"
        md.write_text(content, encoding="utf-8")
        report = validator.validate_file(md)
        w005 = [i for i in report.warnings() if i.code == "W005"]
        assert len(w005) >= 1
