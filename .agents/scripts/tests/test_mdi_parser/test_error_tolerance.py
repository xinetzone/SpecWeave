import sys
import timeit

import pytest

from mdi.parser import MDIParser
from mdi.models import MDIDocument

from .conftest import PROJECT_ROOT


class TestErrorTolerance:

    def test_missing_frontmatter_no_crash(self, parser):
        text = "# Title\n\nContent without frontmatter."
        doc = parser.parse_text(text)
        assert doc.title == "Title"
        assert doc.frontmatter == {}

    def test_empty_document(self, parser):
        doc = parser.parse_text("")
        assert doc is not None
        assert doc.title == ""
        assert doc.sections == []

    def test_corrupted_frontmatter_graceful(self, parser):
        text = '---\nname: test\n  this is not valid yaml: [\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert doc is not None
        assert doc.title == "Test"

    def test_batch_parse_all_skills_no_crash(self, parser):
        skills_dir = PROJECT_ROOT / ".agents" / "skills"
        if not skills_dir.exists():
            pytest.skip("skills directory not found")
        skill_files = list(skills_dir.glob("*/SKILL.md"))
        if len(skill_files) < 5:
            pytest.skip("not enough skill files")
        docs = parser.batch_parse([str(f) for f in skill_files])
        assert len(docs) == len(skill_files)
        success = 0
        total_warnings = 0
        for doc in docs:
            assert isinstance(doc, MDIDocument)
            assert doc.title
            success += 1
            total_warnings += len(doc.warnings)
        assert success == len(skill_files)


class TestParserAPI:

    def test_to_json(self, parser):
        text = '---\nname: test\nversion: 1.0.0\n---\n\n# Test\n\nHello.\n'
        doc = parser.parse_text(text)
        json_str = parser.to_json(doc)
        assert isinstance(json_str, str)
        import json
        data = json.loads(json_str)
        assert data["title"] == "Test"
        assert data["frontmatter"]["name"] == "test"

    def test_parse_file_vs_parse_text(self, parser, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Test\n\nContent.", encoding="utf-8")
        doc_file = parser.parse_file(str(md))
        doc_text = parser.parse_text("# Test\n\nContent.", source="<string>")
        assert doc_file.title == doc_text.title == "Test"


class TestBlockQuote:

    def test_block_quote_content(self, parser):
        text = "# Doc\n\n> This is a warning note.\n\nRegular paragraph.\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        assert "> This is a warning note." in h1.content


class TestPerformance:

    def test_single_skill_parse_under_50ms(self, parser):
        skill_path = PROJECT_ROOT / ".agents" / "skills" / "link-check-cmd" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("link-check-cmd SKILL.md not found")
        text = skill_path.read_text(encoding="utf-8")

        def parse_one():
            p = MDIParser()
            p.parse_text(text)

        n = 100
        total = timeit.timeit(parse_one, number=n)
        avg_ms = (total / n) * 1000
        assert avg_ms < 50, f"Average parse time {avg_ms:.1f}ms exceeds 50ms threshold"
