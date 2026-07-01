"""MDI Validator单元测试。

覆盖frontmatter验证、章节验证、内容质量验证、链接检查、Profile检测、
CLI调用、批量验证等场景。
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from mdi.validator import MDIValidator, ValidationReport, ValidationIssue
from mdi.parser import MDIParser
from mdi.profiles import detect_profile_type, get_profile, SkillProfile, WebApiProfile, CliToolProfile

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
SKILLS_DIR = PROJECT_ROOT / ".agents" / "skills"


@pytest.fixture
def validator():
    return MDIValidator()


@pytest.fixture
def parser():
    return MDIParser()


def _make_skill_doc(
    name: str = "test-skill",
    description: str = "当用户提到测试时，必须使用此技能。这是一个测试用的Skill文档，包含足够的描述信息以通过长度检查。",
    version: str = "1.0.0",
    extra_fm: str = "",
    body: str = "",
) -> str:
    fm = f"""---
name: {name}
version: "{version}"
description: "{description}"
argument-hint: "[test]"
user-invocable: true
paths: []
{extra_fm}
---

# {name}

## 1. 功能描述

这是{name}的功能描述章节。

> **为什么需要此功能？** 为了测试验证器的正确性。

## 2. 何时使用

当用户需要测试时使用本技能。

## 3. 核心步骤

1. 步骤一：准备
2. 步骤二：执行
3. 步骤三：**必须**验证结果

> **为什么步骤三必须验证？** 确保操作成功，避免遗漏。
"""
    return fm + body


class TestValidationIssue:
    def test_to_dict(self):
        issue = ValidationIssue(
            severity="error",
            code="E001",
            message="test message",
            line=10,
            file="test.md",
            suggestion="fix it",
        )
        d = issue.to_dict()
        assert d["severity"] == "error"
        assert d["code"] == "E001"
        assert d["line"] == 10
        assert d["suggestion"] == "fix it"

    def test_to_dict_no_suggestion(self):
        issue = ValidationIssue(
            severity="warn", code="W001", message="msg", line=None, file="f.md"
        )
        d = issue.to_dict()
        assert "suggestion" not in d


class TestValidationReport:
    def test_passed_with_no_errors(self):
        report = ValidationReport(file="test.md")
        report.issues.append(ValidationIssue("warn", "W001", "w", None, "test.md"))
        assert report.passed() is True

    def test_passed_with_errors(self):
        report = ValidationReport(file="test.md")
        report.issues.append(ValidationIssue("error", "E001", "e", None, "test.md"))
        assert report.passed() is False

    def test_errors_warnings_infos(self):
        report = ValidationReport(file="test.md")
        report.issues.append(ValidationIssue("error", "E1", "e", None, "f"))
        report.issues.append(ValidationIssue("warn", "W1", "w", None, "f"))
        report.issues.append(ValidationIssue("warn", "W2", "w", None, "f"))
        report.issues.append(ValidationIssue("info", "I1", "i", None, "f"))
        assert len(report.errors()) == 1
        assert len(report.warnings()) == 2
        assert len(report.infos()) == 1

    def test_score_calculation(self):
        report = ValidationReport(file="test.md")
        report.issues.append(ValidationIssue("error", "E1", "e", None, "f"))
        report.issues.append(ValidationIssue("warn", "W1", "w", None, "f"))
        score = report.calculate_score()
        assert score == 100 - 15 - 5

    def test_score_bounds(self):
        report = ValidationReport(file="test.md")
        for _ in range(20):
            report.issues.append(ValidationIssue("error", "E", "e", None, "f"))
        score = report.calculate_score()
        assert score == 0

    def test_to_dict_and_json(self):
        report = ValidationReport(file="test.md", profile_type="skill")
        report.issues.append(ValidationIssue("warn", "W001", "test warning", 5, "test.md"))
        report.calculate_score()
        d = report.to_dict()
        assert d["file"] == "test.md"
        assert d["profile"] == "skill"
        assert d["errorCount"] == 0
        assert d["warnCount"] == 1
        j = report.to_json()
        parsed = json.loads(j)
        assert parsed["score"] == d["score"]


class TestFrontmatterValidation:
    def test_valid_skill_passes(self, validator):
        doc_text = _make_skill_doc()
        doc = MDIParser().parse_text(doc_text)
        report = validator.validate_document(doc, source_path="<test>")
        assert report.passed(), f"Expected pass, got errors: {[i.message for i in report.errors()]}"

    def test_missing_name(self, validator):
        text = """---
description: "测试描述必须使用此技能且长度足够通过验证"
---

# Test
"""
        doc = MDIParser().parse_text(text)
        report = validator.validate_document(doc, source_path="<test>")
        error_codes = {i.code for i in report.errors()}
        assert "E001" in error_codes
        assert not report.passed()

    def test_missing_description(self, validator):
        text = """---
name: test-skill
---

# Test
"""
        doc = MDIParser().parse_text(text)
        report = validator.validate_document(doc, source_path="<test>")
        error_codes = {i.code for i in report.errors()}
        assert "E001" in error_codes

    def test_missing_recommended_fields_warn(self, validator):
        text = """---
name: test-skill
description: "当用户提到测试时，必须使用此技能。这是一个测试，描述需要足够长才能通过长度检查。"
---

# Test Skill

## 功能描述
测试描述内容。
"""
        doc = MDIParser().parse_text(text)
        report = validator.validate_document(doc, source_path="<test>")
        warn_codes = {i.code for i in report.warnings()}
        assert "W001" in warn_codes

    def test_name_format_kebab_case(self, validator):
        doc_text = _make_skill_doc(name="BadName")
        doc = MDIParser().parse_text(doc_text)
        report = validator.validate_document(doc, source_path="<test>")
        error_codes = {i.code for i in report.errors()}
        assert "E002" in error_codes

    def test_name_format_with_underscore(self, validator):
        doc_text = _make_skill_doc(name="bad_name")
        doc = MDIParser().parse_text(doc_text)
        report = validator.validate_document(doc, source_path="<test>")
        error_codes = {i.code for i in report.errors()}
        assert "E002" in error_codes

    def test_name_too_long(self, validator):
        long_name = "a" * 65
        doc_text = _make_skill_doc(name=long_name)
        doc = MDIParser().parse_text(doc_text)
        report = validator.validate_document(doc, source_path="<test>")
        error_codes = {i.code for i in report.errors()}
        assert "E002" in error_codes

    def test_valid_kebab_case_name_passes(self, validator):
        doc_text = _make_skill_doc(name="my-awesome-skill")
        doc = MDIParser().parse_text(doc_text)
        report = validator.validate_document(doc, source_path="<test>")
        name_errors = [i for i in report.errors() if i.code == "E002"]
        assert len(name_errors) == 0

    def test_description_too_short(self, validator):
        text = """---
name: test-skill
description: "短描述"
---

# Test
"""
        doc = MDIParser().parse_text(text)
        report = validator.validate_document(doc, source_path="<test>")
        warn_codes = {i.code for i in report.warnings()}
        assert "W002" in warn_codes


class TestMandatoryPhrase:
    def test_missing_mandatory_phrase_is_error(self, validator):
        text = """---
name: test-skill
version: "1.0.0"
description: "这是一个没有强制触发措辞的描述，内容足够长但是缺少应有的触发关键词。描述描述描述描述描述描述描述描述描述描述描述。"
---

# Test Skill

## 功能描述
测试内容。
"""
        doc = MDIParser().parse_text(text)
        report = validator.validate_document(doc, source_path="<test>")
        error_codes = {i.code for i in report.errors()}
        assert "E003" in error_codes

    def test_has_mandatory_phrase_passes(self, validator):
        doc_text = _make_skill_doc()
        doc = MDIParser().parse_text(doc_text)
        report = validator.validate_document(doc, source_path="<test>")
        e003_errors = [i for i in report.errors() if i.code == "E003"]
        assert len(e003_errors) == 0


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


class TestProfileDetection:
    def test_auto_detect_skill(self, parser):
        text = _make_skill_doc()
        doc = parser.parse_text(text)
        ptype = detect_profile_type(doc, source_path="test/SKILL.md")
        assert ptype == "skill"

    def test_auto_detect_webapi(self, parser):
        text = """---
name: test-api
description: "Test API description that is long enough to pass validation checks"
baseUrl: "https://api.example.com"
---

# Test API

## Interfaces

### GET /users

获取用户列表。
"""
        doc = parser.parse_text(text)
        ptype = detect_profile_type(doc, source_path="api.md")
        assert ptype == "webapi"

    def test_auto_detect_from_filename(self, parser):
        text = """---
name: test
description: "A simple test description that is long enough to pass validation checks for the test"
---

# Test
"""
        doc = parser.parse_text(text)
        ptype = detect_profile_type(doc, source_path="skills/my-skill/SKILL.md")
        assert ptype == "skill"

    def test_explicit_profile_type(self):
        v = MDIValidator(profile_type="skill")
        assert v.profile_type == "skill"
        v2 = MDIValidator(profile_type="webapi")
        assert v2.profile_type == "webapi"


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


class TestWebApiProfile:
    def test_webapi_requires_baseurl(self):
        v = MDIValidator(profile_type="webapi")
        text = """---
name: test-api
description: "Test API"
---

# API
"""
        doc = MDIParser(profile_type="webapi").parse_text(text)
        report = v.validate_document(doc, source_path="<test>")
        error_codes = {i.code for i in report.errors()}
        assert "E001" in error_codes

    def test_webapi_with_baseurl_passes(self, validator):
        text = """---
name: test-api
description: "A test API with sufficient description length to pass minimum description validation checks properly"
baseUrl: "https://api.example.com"
version: "1.0.0"
---

# Test API

## Endpoints

### GET /users

Users endpoint.
"""
        doc = MDIParser(profile_type="webapi").parse_text(text)
        report = validator.validate_document(doc, source_path="<test>")
        assert report.profile_type == "webapi"


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
