from lib import patterns as pt


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
