from lib import patterns as pt


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
