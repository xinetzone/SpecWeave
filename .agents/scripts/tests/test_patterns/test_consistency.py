from lib import patterns as pt

from .conftest import _write_pattern, _complete_fm


class TestCheckStatsConsistency:

    def _make_env(self, tmp_path, actual, readme_data):
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
