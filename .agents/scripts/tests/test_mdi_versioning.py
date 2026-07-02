"""MDI 版本控制与变更管理单元测试。"""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import (
    MDIDocument, Interface, Parameter, Response, ErrorCode,
)
from mdi.versioning import (
    DiffResult, ChangeType, ChangeSeverity,
    diff_documents, diff_strings,
    get_version_bump_recommendation,
    VERSIONING_BEST_PRACTICES,
    _compare_parameters, _compare_responses, _compare_errors,
)


def make_param(name: str, type_: str = "string", required: bool = True,
               location: str = "body", description: str = "desc",
               default: str | None = None) -> Parameter:
    return Parameter(
        name=name, type=type_, required=required,
        description=description, default=default, location=location,
    )


def make_interface(method: str, path: str, name: str = "",
                   summary: str = "summary",
                   parameters: list[Parameter] | None = None,
                   responses: list[Response] | None = None,
                   errors: list[ErrorCode] | None = None) -> Interface:
    return Interface(
        name=name or f"{method.lower()}_{path.replace('/', '_').strip('_')}",
        method=method, path=path, summary=summary,
        parameters=parameters or [], responses=responses or [],
        errors=errors or [],
    )


def make_doc(version: str = "1.0.0",
             interfaces: list[Interface] | None = None,
             extra_fm: dict | None = None) -> MDIDocument:
    fm = {"name": "test-api", "version": version, "description": "Test API"}
    if extra_fm:
        fm.update(extra_fm)
    return MDIDocument(
        frontmatter=fm,
        title="Test API",
        interfaces=interfaces or [],
    )


class TestParameterComparison:
    def test_no_changes(self):
        old = [make_param("id", "string", True, "path")]
        new = [make_param("id", "string", True, "path")]
        changes = _compare_parameters(old, new)
        assert len(changes) == 0

    def test_add_parameter(self):
        old = []
        new = [make_param("name", "string", False, "query")]
        changes = _compare_parameters(old, new)
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.ADDED
        assert changes[0].name == "name"

    def test_remove_parameter(self):
        old = [make_param("id", "string", True, "path")]
        new = []
        changes = _compare_parameters(old, new)
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.REMOVED
        assert changes[0].severity == ChangeSeverity.MAJOR

    def test_modify_type(self):
        old = [make_param("id", "string", True, "path")]
        new = [make_param("id", "integer", True, "path")]
        changes = _compare_parameters(old, new)
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.MODIFIED
        type_change = [fc for fc in changes[0].field_changes if fc.field == "type"]
        assert len(type_change) == 1
        assert type_change[0].severity == ChangeSeverity.MAJOR

    def test_required_to_optional(self):
        old = [make_param("q", "string", True, "query")]
        new = [make_param("q", "string", False, "query")]
        changes = _compare_parameters(old, new)
        assert len(changes) == 1
        req_change = [fc for fc in changes[0].field_changes if fc.field == "required"]
        assert len(req_change) == 1
        assert req_change[0].old_value is True
        assert req_change[0].new_value is False

    def test_optional_to_required_is_major(self):
        old = [make_param("q", "string", False, "query")]
        new = [make_param("q", "string", True, "query")]
        changes = _compare_parameters(old, new)
        assert len(changes) == 1
        req_change = [fc for fc in changes[0].field_changes if fc.field == "required"]
        assert req_change[0].severity == ChangeSeverity.MAJOR


class TestResponseComparison:
    def test_add_response_is_minor(self):
        old = [Response(200, "OK")]
        new = [Response(200, "OK"), Response(201, "Created")]
        changes = _compare_responses(old, new)
        added = [c for c in changes if c.change_type == ChangeType.ADDED]
        assert len(added) == 1
        assert added[0].severity == ChangeSeverity.MINOR

    def test_remove_response_is_major(self):
        old = [Response(200, "OK"), Response(204, "No Content")]
        new = [Response(200, "OK")]
        changes = _compare_responses(old, new)
        removed = [c for c in changes if c.change_type == ChangeType.REMOVED]
        assert len(removed) == 1
        assert removed[0].severity == ChangeSeverity.MAJOR


class TestErrorComparison:
    def test_add_error_is_minor(self):
        old = []
        new = [ErrorCode(404, "Not found", "Resource not found")]
        changes = _compare_errors(old, new)
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.ADDED
        assert changes[0].severity == ChangeSeverity.MINOR


class TestDiffDocuments:
    def test_no_changes(self):
        doc = make_doc("1.0.0", [make_interface("GET", "/users")])
        result = diff_documents(doc, doc)
        assert not result.has_changes
        assert result.overall_severity() == ChangeSeverity.NONE

    def test_added_interface(self):
        old = make_doc("1.0.0", [make_interface("GET", "/users")])
        new = make_doc("1.1.0", [
            make_interface("GET", "/users"),
            make_interface("POST", "/users"),
        ])
        result = diff_documents(old, new)
        assert len(result.added_interfaces) == 1
        assert result.added_interfaces[0].method == "POST"
        assert result.overall_severity() == ChangeSeverity.MINOR

    def test_removed_interface_is_major(self):
        old = make_doc("1.0.0", [
            make_interface("GET", "/users"),
            make_interface("DELETE", "/users/{id}"),
        ])
        new = make_doc("2.0.0", [make_interface("GET", "/users")])
        result = diff_documents(old, new)
        assert len(result.removed_interfaces) == 1
        assert result.overall_severity() == ChangeSeverity.MAJOR

    def test_patch_version_change(self):
        old = make_doc("1.0.0")
        new = make_doc("1.0.1", extra_fm={"description": "Updated desc"})
        new.description = "Updated desc"
        result = diff_documents(old, new)
        assert result.overall_severity() == ChangeSeverity.PATCH

    def test_version_bump_patch(self):
        old = make_doc("1.0.0")
        new = make_doc("1.0.1")
        new.description = "fix typo"
        result = diff_documents(old, new)
        assert result.suggest_version_bump("1.0.0") == "1.0.1"

    def test_version_bump_minor(self):
        old = make_doc("1.0.0", [make_interface("GET", "/users")])
        new = make_doc("1.1.0", [
            make_interface("GET", "/users"),
            make_interface("GET", "/users/{id}"),
        ])
        result = diff_documents(old, new)
        assert result.suggest_version_bump("1.0.0") == "1.1.0"

    def test_version_bump_major(self):
        old = make_doc("1.0.0", [
            make_interface("GET", "/users"),
            make_interface("DELETE", "/users/{id}"),
        ])
        new = make_doc("2.0.0", [make_interface("GET", "/users")])
        result = diff_documents(old, new)
        assert result.suggest_version_bump("1.0.0") == "2.0.0"

    def test_frontmatter_description_change(self):
        old = make_doc("1.0.0")
        new = make_doc("1.0.0", extra_fm={"description": "New description"})
        result = diff_documents(old, new)
        fm_changes = [c for c in result.frontmatter_changes if c.key == "description"]
        assert len(fm_changes) == 1
        assert fm_changes[0].change_type == ChangeType.MODIFIED

    def test_parameter_type_change_is_major(self):
        old = make_doc("1.0.0", [
            make_interface("GET", "/users", parameters=[
                make_param("id", "string", True, "path"),
            ]),
        ])
        new = make_doc("2.0.0", [
            make_interface("GET", "/users", parameters=[
                make_param("id", "integer", True, "path"),
            ]),
        ])
        result = diff_documents(old, new)
        assert result.overall_severity() == ChangeSeverity.MAJOR


class TestImpactAnalysis:
    def test_add_interface_impacts_all_generators(self):
        old = make_doc("1.0.0")
        new = make_doc("1.1.0", [make_interface("GET", "/users")])
        result = diff_documents(old, new)
        impacts = result.impact_analysis()
        assert "python_types" in impacts
        assert "openapi_spec" in impacts
        assert "pytest_tests" in impacts

    def test_remove_interface_breaks(self):
        old = make_doc("1.0.0", [make_interface("DELETE", "/users/{id}")])
        new = make_doc("2.0.0")
        result = diff_documents(old, new)
        impacts = result.impact_analysis()
        assert any("破坏性变更" in item for items in impacts.values() for item in items)

    def test_parameter_required_change(self):
        old = make_doc("1.0.0", [
            make_interface("GET", "/users", parameters=[
                make_param("q", "string", False, "query"),
            ]),
        ])
        new = make_doc("2.0.0", [
            make_interface("GET", "/users", parameters=[
                make_param("q", "string", True, "query"),
            ]),
        ])
        result = diff_documents(old, new)
        impacts = result.impact_analysis()
        assert "pytest_tests" in impacts


class TestVersionBumpRecommendation:
    def test_major_recommendation(self):
        old = make_doc("1.0.0", [make_interface("GET", "/old")])
        new = make_doc("2.0.0")
        result = diff_documents(old, new)
        rec = get_version_bump_recommendation(result)
        assert rec["bump_type"] == "major"
        assert rec["has_breaking_changes"] is True
        assert rec["suggested_version"] == "2.0.0"

    def test_minor_recommendation(self):
        old = make_doc("1.0.0")
        new = make_doc("1.1.0", [make_interface("GET", "/new")])
        result = diff_documents(old, new)
        rec = get_version_bump_recommendation(result)
        assert rec["bump_type"] == "minor"
        assert rec["suggested_version"] == "1.1.0"

    def test_patch_recommendation(self):
        old = make_doc("1.0.0")
        new = make_doc("1.0.1")
        new.description = "fix: typo"
        result = diff_documents(old, new)
        rec = get_version_bump_recommendation(result)
        assert rec["bump_type"] == "patch"
        assert rec["should_run_tests"] is True
        assert rec["should_regenerate"] is True


class TestDiffStrings:
    def test_diff_identical_strings(self):
        content = """---
name: test
version: "1.0.0"
---
# Test
"""
        result = diff_strings(content, content)
        assert not result.has_changes

    def test_diff_simple_change(self):
        old = """---
name: test
version: "1.0.0"
---
# Test API

```{endpoint} GET /users
:summary: List users
```
"""
        new = """---
name: test
version: "1.1.0"
---
# Test API

```{endpoint} GET /users
:summary: List all users
```

```{endpoint} POST /users
:summary: Create user
```
"""
        result = diff_strings(old, new)
        assert result.has_changes
        assert len(result.added_interfaces) == 1


class TestSerialization:
    def test_to_dict(self):
        old = make_doc("1.0.0")
        new = make_doc("1.1.0", [make_interface("GET", "/users")])
        result = diff_documents(old, new)
        d = result.to_dict()
        assert "overall_severity" in d
        assert "suggested_version" in d
        assert "added_interfaces" in d
        assert "impact_analysis" in d
        assert d["has_changes"] is True

    def test_format_text(self):
        old = make_doc("1.0.0")
        new = make_doc("1.1.0", [make_interface("GET", "/users")])
        result = diff_documents(old, new)
        text = result.format_text()
        assert "MDI 结构化变更分析报告" in text
        assert "MINOR" in text
        assert "新增接口" in text


class TestBestPractices:
    def test_best_practices_content(self):
        assert "语义化版本" in VERSIONING_BEST_PRACTICES
        assert "MAJOR" in VERSIONING_BEST_PRACTICES
        assert "MINOR" in VERSIONING_BEST_PRACTICES
        assert "PATCH" in VERSIONING_BEST_PRACTICES
        assert "Commit Message" in VERSIONING_BEST_PRACTICES


class TestSeverityEdgeCases:
    def test_no_version_uses_default(self):
        old = MDIDocument(frontmatter={"name": "test"}, interfaces=[])
        new = MDIDocument(frontmatter={"name": "test", "version": "0.1.0"}, interfaces=[])
        result = diff_documents(old, new)
        assert result.suggest_version_bump() == "0.1.1"

    def test_invalid_version_defaults(self):
        old = make_doc("invalid", [make_interface("GET", "/a")])
        new = make_doc("invalid", [make_interface("GET", "/a"), make_interface("POST", "/b")])
        result = diff_documents(old, new)
        suggested = result.suggest_version_bump()
        parts = suggested.split(".")
        assert len(parts) == 3

    def test_add_required_param_is_major(self):
        old = make_doc("1.0.0", [
            make_interface("POST", "/users", parameters=[]),
        ])
        new = make_doc("2.0.0", [
            make_interface("POST", "/users", parameters=[
                make_param("name", "string", True, "body"),
            ]),
        ])
        result = diff_documents(old, new)
        assert result.overall_severity() == ChangeSeverity.MAJOR

    def test_add_optional_param_is_minor(self):
        old = make_doc("1.0.0", [
            make_interface("GET", "/users", parameters=[]),
        ])
        new = make_doc("1.1.0", [
            make_interface("GET", "/users", parameters=[
                make_param("page", "integer", False, "query"),
            ]),
        ])
        result = diff_documents(old, new)
        assert result.overall_severity() == ChangeSeverity.MINOR
