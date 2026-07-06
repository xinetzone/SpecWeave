from lib import patterns as pt


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

    def test_l2_vc4_reuse1_not_candidate(self):
        p = [{"id": "b", "maturity": "L2", "validation_count": 4, "reuse_count": 1}]
        result = pt.find_upgrade_candidates(p)
        assert result["L2_to_L3"] == []


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
