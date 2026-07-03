from lib import patterns as pt


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
