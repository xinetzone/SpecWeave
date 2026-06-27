"""lib.checks.base 单元测试。"""

import pytest

from lib.checks.base import CheckResult


class TestCheckResult:
    """CheckResult 数据类测试。"""

    def test_default_values(self):
        """默认值正确初始化。"""
        r = CheckResult(name="test")
        assert r.name == "test"
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.fixed_count == 0

    def test_error_count_property(self):
        """error_count 属性返回 errors 列表长度。"""
        r = CheckResult(name="test")
        assert r.error_count == 0
        r.errors.append("err1")
        assert r.error_count == 1
        r.errors.append("err2")
        assert r.error_count == 2

    def test_warning_count_property(self):
        """warning_count 属性返回 warnings 列表长度。"""
        r = CheckResult(name="test")
        assert r.warning_count == 0
        r.warnings.append("warn1")
        assert r.warning_count == 1

    def test_custom_values(self):
        """自定义值正确赋值。"""
        r = CheckResult(
            name="custom",
            passed=False,
            errors=["e1", "e2"],
            warnings=["w1"],
            fixed_count=3,
        )
        assert r.name == "custom"
        assert r.passed is False
        assert r.error_count == 2
        assert r.warning_count == 1
        assert r.fixed_count == 3

    def test_independent_instances(self):
        """不同实例的 errors/warnings 列表互不影响（避免 default_factory 共享问题）。"""
        r1 = CheckResult(name="a")
        r2 = CheckResult(name="b")
        r1.errors.append("only-in-r1")
        assert "only-in-r1" not in r2.errors
        assert r2.errors == []
