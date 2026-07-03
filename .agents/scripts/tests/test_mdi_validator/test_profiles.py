from mdi.validator import MDIValidator
from mdi.parser import MDIParser
from mdi.profiles import detect_profile_type

from .helpers import _make_skill_doc


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
