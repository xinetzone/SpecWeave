from lib import patterns as pt

from .conftest import _write_pattern, _complete_fm


class TestCountPatterns:

    def test_nonexistent_dir(self, tmp_path):
        assert pt.count_patterns(tmp_path / "nope") == 0

    def test_empty_dir(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()
        assert pt.count_patterns(d) == 0

    def test_counts_md_files_excluding_readme(self, tmp_path):
        d = tmp_path / "pat"
        d.mkdir()
        (d / "a.md").write_text("x", encoding="utf-8")
        (d / "b.md").write_text("x", encoding="utf-8")
        (d / "README.md").write_text("x", encoding="utf-8")
        (d / "not_md.txt").write_text("x", encoding="utf-8")
        assert pt.count_patterns(d) == 2


class TestGrepMaturityPerDirectory:

    def test_missing_dir_skipped(self, tmp_path):
        result = pt.grep_maturity_per_directory(tmp_path)
        assert result == {}

    def test_counts_maturity_levels(self, tmp_path):
        _write_pattern(tmp_path, "methodology-patterns", "m1.md", _complete_fm(id="m1", maturity="L1"))
        _write_pattern(tmp_path, "methodology-patterns", "m2.md", _complete_fm(id="m2", maturity="L1"))
        _write_pattern(tmp_path, "methodology-patterns", "m3.md", _complete_fm(id="m3", maturity="L2"))
        _write_pattern(tmp_path, "code-patterns", "c1.md", _complete_fm(id="c1", maturity="L3"))
        (tmp_path / "methodology-patterns" / "README.md").write_text("# R\n", encoding="utf-8")
        result = pt.grep_maturity_per_directory(tmp_path)
        assert "methodology-patterns" in result
        assert result["methodology-patterns"]["L1"] == 2
        assert result["methodology-patterns"]["L2"] == 1
        assert result["methodology-patterns"]["_total"] == 3
        assert result["code-patterns"]["L3"] == 1
        assert result["code-patterns"]["_total"] == 1
