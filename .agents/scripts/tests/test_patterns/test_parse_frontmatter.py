from lib import patterns as pt

from .conftest import _complete_fm


class TestParsePatternFrontmatter:

    def test_no_frontmatter_returns_none(self, tmp_path):
        p = tmp_path / "bad.md"
        p.write_text("# No fm\n", encoding="utf-8")
        assert pt.parse_pattern_frontmatter(p) is None

    def test_complete_frontmatter(self, tmp_path):
        p = tmp_path / "good.md"
        fm = _complete_fm(id="my-pattern", maturity="L2", validation_count="3", reuse_count="1")
        p.write_text("+++\n" + "\n".join(fm) + "\n+++\n\n# Body\n", encoding="utf-8")
        result = pt.parse_pattern_frontmatter(p)
        assert result is not None
        assert result["id"] == "my-pattern"
        assert result["maturity"] == "L2"
        assert result["validation_count"] == 3
        assert result["reuse_count"] == 1

    def test_missing_string_fields_omitted(self, tmp_path):
        p = tmp_path / "partial.md"
        p.write_text('+++\nid = "x"\nvalidation_count = 2\n+++\n\n# B\n', encoding="utf-8")
        result = pt.parse_pattern_frontmatter(p)
        assert result is not None
        assert result["id"] == "x"
        assert result["validation_count"] == 2
        assert "domain" not in result
        assert "reuse_count" not in result

    def test_invalid_int_defaults_to_zero(self, tmp_path):
        p = tmp_path / "badint.md"
        p.write_text('+++\nid = "x"\nvalidation_count = "abc"\n+++\n\n# B\n', encoding="utf-8")
        result = pt.parse_pattern_frontmatter(p)
        assert result["validation_count"] == 0
