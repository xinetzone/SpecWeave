"""lib.patterns 单元测试。"""

from pathlib import Path

import pytest

from lib import patterns as pt


# ── helpers ──────────────────────────────────────────────────

def _write_pattern(base: Path, domain_dir: str, filename: str, fm_lines: list[str], body: str = "# Pattern\n") -> Path:
    """Helper: 在 base/domain_dir/ 下创建一个带 TOML frontmatter 的模式文件。"""
    d = base / domain_dir
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    fm = "\n".join(fm_lines)
    p.write_text(f"+++\n{fm}\n+++\n\n{body}", encoding="utf-8")
    return p


def _complete_fm(**overrides) -> list[str]:
    """返回一份完整的必填字段 frontmatter 行列表。"""
    defaults = {
        "id": "test-pattern",
        "domain": "test",
        "layer": "cognition",
        "maturity": "L1",
        "validation_count": "1",
        "reuse_count": "0",
        "documentation_level": "complete",
        "source": "test.md",
    }
    defaults.update(overrides)
    return [f'{k} = "{v}"' if k not in ("validation_count", "reuse_count") else f"{k} = {v}" for k, v in defaults.items()]


# ── parse_pattern_frontmatter ────────────────────────────────

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


# ── scan_patterns ────────────────────────────────────────────

class TestScanPatterns:

    def test_missing_domain_dir_creates_issue(self, tmp_path):
        for d in pt.PATTERN_DOMAINS:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        patterns, issues = pt.scan_patterns(str(tmp_path))
        assert patterns == []
        assert issues == []

    def test_missing_directory_issue(self, tmp_path):
        """一个域目录不存在时产生 missing_directory issue。"""
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
        """domain 字段去掉 '-patterns' 后缀。"""
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


# ── classify_pattern ─────────────────────────────────────────

class TestClassifyPattern:

    def test_upgrade_l1_vc2(self):
        assert pt.classify_pattern({"maturity": "L1", "validation_count": 2}) == "upgrade"

    def test_upgrade_l1_vc5(self):
        assert pt.classify_pattern({"maturity": "L1", "validation_count": 5}) == "upgrade"

    def test_ok_l1_vc1(self):
        assert pt.classify_pattern({"maturity": "L1", "validation_count": 1}) == "ok"

    def test_ok_l1_vc0(self):
        assert pt.classify_pattern({"maturity": "L1", "validation_count": 0}) == "ok"

    def test_anomaly_l2_vc1(self):
        assert pt.classify_pattern({"maturity": "L2", "validation_count": 1}) == "anomaly"

    def test_anomaly_l3_vc1(self):
        assert pt.classify_pattern({"maturity": "L3", "validation_count": 1}) == "anomaly"

    def test_anomaly_l4_vc1(self):
        assert pt.classify_pattern({"maturity": "L4", "validation_count": 1}) == "anomaly"

    def test_ok_l2_vc2(self):
        assert pt.classify_pattern({"maturity": "L2", "validation_count": 2}) == "ok"

    def test_ok_l3_vc3(self):
        assert pt.classify_pattern({"maturity": "L3", "validation_count": 3}) == "ok"

    def test_ok_defaults(self):
        assert pt.classify_pattern({}) == "ok"


# ── analyze_distribution ─────────────────────────────────────

class TestAnalyzeDistribution:

    def test_empty_patterns(self):
        stats, domain_stats = pt.analyze_distribution([])
        assert stats["total"] == 0
        assert dict(stats["maturity"]) == {}
        assert dict(domain_stats) == {}

    def test_basic_distribution(self):
        patterns = [
            {"maturity": "L1", "domain": "code"},
            {"maturity": "L1", "domain": "code"},
            {"maturity": "L2", "domain": "code"},
            {"maturity": "L3", "domain": "architecture"},
        ]
        stats, domain_stats = pt.analyze_distribution(patterns)
        assert stats["total"] == 4
        assert stats["maturity"]["L1"] == 2
        assert stats["maturity"]["L2"] == 1
        assert stats["maturity"]["L3"] == 1
        assert domain_stats["code"]["total"] == 3
        assert domain_stats["code"]["L1"] == 2
        assert domain_stats["code"]["L2"] == 1
        assert domain_stats["architecture"]["total"] == 1
        assert domain_stats["architecture"]["L3"] == 1


# ── find_upgrade_candidates ──────────────────────────────────

class TestFindUpgradeCandidates:

    def test_empty(self):
        result = pt.find_upgrade_candidates([])
        assert result == {"L1_to_L2": [], "L2_to_L3": []}

    def test_l1_vc2_is_candidate(self):
        p = [{"id": "a", "maturity": "L1", "validation_count": 2, "reuse_count": 0}]
        result = pt.find_upgrade_candidates(p)
        assert len(result["L1_to_L2"]) == 1
        assert result["L1_to_L2"][0]["id"] == "a"

    def test_l1_vc1_not_candidate(self):
        p = [{"id": "a", "maturity": "L1", "validation_count": 1}]
        result = pt.find_upgrade_candidates(p)
        assert result["L1_to_L2"] == []

    def test_l2_reuse1_is_candidate(self):
        p = [{"id": "b", "maturity": "L2", "validation_count": 5, "reuse_count": 1}]
        result = pt.find_upgrade_candidates(p)
        assert len(result["L2_to_L3"]) == 1
        assert result["L2_to_L3"][0]["id"] == "b"

    def test_l2_reuse0_not_candidate(self):
        p = [{"id": "b", "maturity": "L2", "reuse_count": 0}]
        result = pt.find_upgrade_candidates(p)
        assert result["L2_to_L3"] == []


# ── build_upgrade_stats ──────────────────────────────────────

class TestBuildUpgradeStats:

    def test_empty(self):
        stats = pt.build_upgrade_stats([])
        assert stats["total"] == 0
        assert stats["validation_total"] == 0
        assert stats["avg_validation"] == 0
        assert stats["upgrades"] == []
        assert stats["anomalies"] == []

    def test_mixed_patterns(self):
        patterns = [
            {"id": "ok1", "maturity": "L1", "validation_count": 1, "reuse_count": 0},
            {"id": "up1", "maturity": "L1", "validation_count": 3, "reuse_count": 0},
            {"id": "an1", "maturity": "L3", "validation_count": 1, "reuse_count": 0},
            {"id": "ok2", "maturity": "L2", "validation_count": 2, "reuse_count": 0},
        ]
        stats = pt.build_upgrade_stats(patterns)
        assert stats["total"] == 4
        assert stats["validation_total"] == 7
        assert stats["avg_validation"] == 1.8
        assert len(stats["upgrades"]) == 1
        assert stats["upgrades"][0]["id"] == "up1"
        assert len(stats["anomalies"]) == 1
        assert stats["anomalies"][0]["id"] == "an1"
        assert stats["maturity_counts"] == {"L1": 2, "L3": 1, "L2": 1}


# ── count_patterns ───────────────────────────────────────────

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


# ── grep_maturity_per_directory ──────────────────────────────

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


# ── parse_readme_stats_table ─────────────────────────────────

class TestParseReadmeStatsTable:

    def test_bold_format(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "| **dir/** | **总数** | **L1** | **L2** | **L3** | **L4** |\n"
            "|---|---|---|---|---|---|\n"
            "| **methodology-patterns/** | **10** | **5** | **3** | **1** | **1** |\n"
            "| **code-patterns/** | **8** | **4** | **2** | **1** | **1** |\n"
            "| **合计** | **18** | **9** | **5** | **2** | **2** |\n",
            encoding="utf-8",
        )
        result = pt.parse_readme_stats_table(readme)
        assert "methodology-patterns" in result
        assert result["methodology-patterns"]["L1"] == 5
        assert result["methodology-patterns"]["_total"] == 10
        assert "code-patterns" in result
        assert result["code-patterns"]["L4"] == 1
        assert "合计" not in result

    def test_plain_format(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "| dir/ | 总数 | L1 | L2 | L3 | L4 |\n"
            "|---|---|---|---|---|---|\n"
            "| architecture-patterns/ | 5 | 2 | 2 | 1 | 0 |\n",
            encoding="utf-8",
        )
        result = pt.parse_readme_stats_table(readme)
        assert "architecture-patterns" in result
        assert result["architecture-patterns"]["_total"] == 5
        assert result["architecture-patterns"]["L3"] == 1

    def test_no_match_empty(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("# No table\n", encoding="utf-8")
        assert pt.parse_readme_stats_table(readme) == {}


# ── parse_readme_index_table ─────────────────────────────────

class TestParseReadmeIndexTable:

    def test_parses_index_table(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Patterns\n\n"
            "| 目录 | 模式数 | L1 | L2 | L3 | L4 |\n"
            "|---|---|---|---|---|---|\n"
            "| methodology-patterns/ | 10 | 5 | 3 | 1 | 1 |\n"
            "| code-patterns/ | 8 | 4 | 2 | 1 | 1 |\n"
            "| architecture-patterns/ | 5 | 2 | 2 | 1 | 0 |\n"
            "| **合计** | **23** | **11** | **7** | **3** | **2** |\n",
            encoding="utf-8",
        )
        result = pt.parse_readme_index_table(readme)
        assert "methodology-patterns/" in result
        assert result["methodology-patterns/"]["patterns"] == 10
        assert result["code-patterns/"]["L2"] == 2
        assert "architecture-patterns/" in result
        assert len(result) == 3

    def test_no_table_empty(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("# No table\n", encoding="utf-8")
        assert dict(pt.parse_readme_index_table(readme)) == {}

    def test_stops_at_bold_line(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "| 目录 | 模式数 | L1 | L2 | L3 | L4 |\n"
            "|---|---|---|---|---|---|\n"
            "| methodology-patterns/ | 10 | 5 | 3 | 1 | 1 |\n"
            "**after table**\n"
            "| should-not-appear/ | 99 | 0 | 0 | 0 | 0 |\n",
            encoding="utf-8",
        )
        result = pt.parse_readme_index_table(readme)
        assert len(result) == 1


# ── check_stats_consistency ──────────────────────────────────

class TestCheckStatsConsistency:

    def _make_env(self, tmp_path, actual, readme_data):
        """创建 patterns 目录和 README，返回 (patterns_root, readme_path)。"""
        for domain, levels in actual.items():
            d = tmp_path / domain
            d.mkdir(parents=True, exist_ok=True)
            for i in range(levels.get("L1", 0)):
                _write_pattern(tmp_path, domain, f"l1_{i}.md", _complete_fm(id=f"{domain}-l1-{i}", maturity="L1", validation_count="1"))
            for i in range(levels.get("L2", 0)):
                _write_pattern(tmp_path, domain, f"l2_{i}.md", _complete_fm(id=f"{domain}-l2-{i}", maturity="L2", validation_count="2"))
        readme = tmp_path / "README.md"
        header = "| dir/ | 总数 | L1 | L2 | L3 | L4 |\n|---|---|---|---|---|---|\n"
        rows = []
        for domain, levels in readme_data.items():
            total = levels.get("L1", 0) + levels.get("L2", 0) + levels.get("L3", 0) + levels.get("L4", 0)
            rows.append(f"| {domain}/ | {total} | {levels.get('L1',0)} | {levels.get('L2',0)} | {levels.get('L3',0)} | {levels.get('L4',0)} |")
        readme.write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
        return tmp_path, readme

    def test_consistent_no_discrepancies(self, tmp_path):
        actual = {"methodology-patterns": {"L1": 2, "L2": 1}}
        readme_data = {"methodology-patterns": {"L1": 2, "L2": 1, "L3": 0, "L4": 0}}
        root, readme = self._make_env(tmp_path, actual, readme_data)
        result = pt.check_stats_consistency(root, readme)
        assert result == []

    def test_l1_mismatch(self, tmp_path):
        actual = {"methodology-patterns": {"L1": 3, "L2": 1}}
        readme_data = {"methodology-patterns": {"L1": 2, "L2": 1, "L3": 0, "L4": 0}}
        root, readme = self._make_env(tmp_path, actual, readme_data)
        result = pt.check_stats_consistency(root, readme)
        l1_issues = [d for d in result if d["field"] == "L1"]
        assert len(l1_issues) == 1
        assert l1_issues[0]["grep"] == 3
        assert l1_issues[0]["readme"] == 2
        assert l1_issues[0]["diff"] == 1
        assert any(d["field"] == "总计" for d in result)

    def test_total_mismatch(self, tmp_path):
        actual = {"code-patterns": {"L1": 3}}
        readme_data = {"code-patterns": {"L1": 2, "L2": 0, "L3": 0, "L4": 0}}
        root, readme = self._make_env(tmp_path, actual, readme_data)
        result = pt.check_stats_consistency(root, readme)
        assert any(d["field"] == "总计" for d in result)


# ── update_readme_index_table ────────────────────────────────

class TestUpdateReadmeIndexTable:

    def test_updates_counts_and_total(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "| 目录 | 模式数 | L1 | L2 | L3 | L4 |\n"
            "|---|---|---|---|---|---|\n"
            "| methodology-patterns/ | 5 | 3 | 1 | 1 | 0 |\n"
            "| code-patterns/ | 4 | 2 | 1 | 1 | 0 |\n"
            "| architecture-patterns/ | 3 | 1 | 1 | 1 | 0 |\n"
            "| **合计** | **12** | **6** | **3** | **3** | **0** |\n",
            encoding="utf-8",
        )
        declared = pt.parse_readme_index_table(readme)
        actual = {
            "methodology-patterns/": 7,
            "code-patterns/": 5,
            "architecture-patterns/": 3,
        }
        new_content = pt.update_readme_index_table(readme, declared, actual)
        assert "| methodology-patterns/ | 7 |" in new_content
        assert "| code-patterns/ | 5 |" in new_content
        assert "| architecture-patterns/ | 3 |" in new_content
        assert "| **合计** | **15** |" in new_content

    def test_preserves_l_values_from_declared(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "| 目录 | 模式数 | L1 | L2 | L3 | L4 |\n"
            "|---|---|---|---|---|---|\n"
            "| methodology-patterns/ | 5 | 3 | 1 | 1 | 0 |\n"
            "| **合计** | **5** | **3** | **1** | **1** | **0** |\n",
            encoding="utf-8",
        )
        declared = pt.parse_readme_index_table(readme)
        actual = {"methodology-patterns/": 10}
        new_content = pt.update_readme_index_table(readme, declared, actual)
        assert "| methodology-patterns/ | 10 | 3 | 1 | 1 | 0 |" in new_content
        assert "| **合计** | **10** | **3** | **1** | **1** | **0** |" in new_content


# ── build_report_data ────────────────────────────────────────

class TestBuildReportData:

    def test_empty(self):
        data = pt.build_report_data([], [])
        assert data["total"] == 0
        assert data["maturity"] == {"L1": 0, "L2": 0, "L3": 0, "L4": 0}
        assert data["upgrade_candidates"] == {"L1_to_L2": [], "L2_to_L3": []}
        assert data["patterns"] == []
        assert data["issues"] == []
        for domain in ["methodology", "code", "architecture"]:
            assert data["domains"][domain] == {"total": 0, "L1": 0, "L2": 0, "L3": 0, "L4": 0}

    def test_full_report(self):
        patterns = [
            {"id": "a", "domain": "code", "maturity": "L1", "validation_count": 2, "reuse_count": 0},
            {"id": "b", "domain": "code", "maturity": "L2", "validation_count": 3, "reuse_count": 1},
            {"id": "c", "domain": "architecture", "maturity": "L3", "validation_count": 1, "reuse_count": 0},
        ]
        issues = [{"type": "test", "path": "x", "message": "m"}]
        data = pt.build_report_data(patterns, issues)
        assert data["total"] == 3
        assert data["maturity"]["L1"] == 1
        assert data["maturity"]["L2"] == 1
        assert data["maturity"]["L3"] == 1
        assert data["domains"]["code"]["total"] == 2
        assert data["domains"]["code"]["L1"] == 1
        assert data["domains"]["architecture"]["total"] == 1
        assert "a" in data["upgrade_candidates"]["L1_to_L2"]
        assert "b" in data["upgrade_candidates"]["L2_to_L3"]
        assert data["issues"] == issues
        assert data["patterns"][0]["id"] == "c"
