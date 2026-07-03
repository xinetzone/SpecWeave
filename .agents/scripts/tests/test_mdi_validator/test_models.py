import json

from mdi.validator import ValidationIssue, ValidationReport


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
