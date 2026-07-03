from lib import patterns as pt

from .conftest import _write_pattern, _complete_fm


class TestScanPatterns:

    def test_missing_domain_dir_creates_issue(self, tmp_path):
        for d in pt.PATTERN_DOMAINS:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        patterns, issues = pt.scan_patterns(str(tmp_path))
        assert patterns == []
        assert issues == []

    def test_missing_directory_issue(self, tmp_path):
        (tmp_path / "methodology-patterns").mkdir(parents=True)
        patterns, issues = pt.scan_patterns(str(tmp_path))
        assert len(issues) >= 1
        assert any(i["type"] == "missing_directory" for i in issues)

    def test_excludes_readme(self, tmp_path):
        d = tmp_path / "methodology-patterns"
        d.mkdir(parents=True)
        (d / "README.md").write_text("# Index\n", encoding="utf-8")
        _write_pattern(tmp_path, "methodology-patterns", "p1.md", _complete_fm(id="p1"))
        patterns, issues = pt.scan_patterns(str(tmp_path))
        assert len(patterns) == 1
        assert patterns[0]["id"] == "p1"

    def test_missing_frontmatter_issue(self, tmp_path):
        for d in pt.PATTERN_DOMAINS:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        bad = tmp_path / "methodology-patterns" / "bad.md"
        bad.write_text("# No fm\n", encoding="utf-8")
        patterns, issues = pt.scan_patterns(str(tmp_path))
        fm_issues = [i for i in issues if i["type"] == "missing_frontmatter"]
        assert len(fm_issues) == 1

    def test_missing_fields_issue(self, tmp_path):
        for d in pt.PATTERN_DOMAINS:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        p = tmp_path / "methodology-patterns" / "partial.md"
        p.write_text('+++\nid = "x"\n+++\n\n# B\n', encoding="utf-8")
        patterns, issues = pt.scan_patterns(str(tmp_path))
        field_issues = [i for i in issues if i["type"] == "missing_fields"]
        assert len(field_issues) == 1
        assert "domain" in field_issues[0]["fields"]

    def test_domain_stripped_suffix(self, tmp_path):
        _write_pattern(tmp_path, "architecture-patterns", "arch.md", _complete_fm(id="arch1"))
        patterns, _ = pt.scan_patterns(str(tmp_path))
        assert len(patterns) == 1
        assert patterns[0]["domain"] == "architecture"
        assert "file" in patterns[0]

    def test_filepath_added(self, tmp_path):
        _write_pattern(tmp_path, "code-patterns", "c1.md", _complete_fm(id="c1"))
        patterns, _ = pt.scan_patterns(str(tmp_path))
        assert "filepath" in patterns[0]
        assert patterns[0]["filepath"].endswith("c1.md")
