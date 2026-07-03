from mdi.parser import MDIParser

from .helpers import _make_skill_doc


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
