"""
Unit tests for tools/ft_compat_check.py
Tests cover: dataclasses, FT detection logic, import checking, report generation.
Uses unittest.mock to avoid requiring ONNX packages on the host machine.
"""
from __future__ import annotations

import dataclasses
import importlib
import sys
import types
from unittest import mock

import pytest

# ft_compat_check is imported via conftest.py sys.path setup
import ft_compat_check as ftc


class TestPkgResult:
    """Tests for PkgResult dataclass."""

    def test_pkgresult_ok_defaults(self):
        r = ftc.PkgResult(name="numpy", status="ok", version="2.0.0")
        assert r.name == "numpy"
        assert r.status == "ok"
        assert r.version == "2.0.0"
        assert r.error is None
        assert r.note is None

    def test_pkgresult_all_fields(self):
        r = ftc.PkgResult(
            name="badpkg",
            status="import_error",
            version=None,
            error="No module named 'badpkg'",
            note="known incompatible",
        )
        assert r.error == "No module named 'badpkg'"
        assert r.note == "known incompatible"

    def test_pkgresult_is_frozen_like(self):
        """dataclass should be instantiable; we check it's a proper dataclass."""
        assert dataclasses.is_dataclass(ftc.PkgResult)


class TestFTReport:
    """Tests for FTReport dataclass and its methods."""

    def _make_report(self, results: list[ftc.PkgResult] | None = None, is_ft: bool = True) -> ftc.FTReport:
        return ftc.FTReport(
            is_free_threading=is_ft,
            python_version="3.14.6",
            gil_enabled=False,
            results=results or [],
            known_incompatible=dict(ftc.KNOWN_INCOMPATIBLE),
            alternatives=dict(ftc.ALTERNATIVES),
        )

    def test_summary_counts_correctly(self):
        results = [
            ftc.PkgResult("numpy", "ok", version="2.0"),
            ftc.PkgResult("onnx", "ok", version="1.22"),
            ftc.PkgResult("onnxoptimizer", "absent"),
            ftc.PkgResult("bad", "import_error", error="fail"),
            ftc.PkgResult("unexpected", "present_unexpected", version="1.0"),
            ftc.PkgResult("crash_pkg", "crash", error="segfault"),
        ]
        report = self._make_report(results)
        s = report.summary()
        assert s["ok"] == 2
        assert s["absent"] == 1
        assert s["import_error"] == 1
        assert s["present_unexpected"] == 1
        assert s["crash"] == 1

    def test_passed_all_ok(self):
        results = [
            ftc.PkgResult("numpy", "ok", version="2.0"),
            ftc.PkgResult("onnxoptimizer", "absent"),
        ]
        report = self._make_report(results)
        assert report.passed() is True

    def test_passed_fails_on_import_error(self):
        results = [
            ftc.PkgResult("numpy", "ok"),
            ftc.PkgResult("onnxruntime", "import_error", error="fail"),
        ]
        report = self._make_report(results)
        assert report.passed() is False

    def test_passed_fails_on_present_unexpected(self):
        results = [
            ftc.PkgResult("numpy", "ok"),
            ftc.PkgResult("onnxoptimizer", "present_unexpected", version="0.3"),
        ]
        report = self._make_report(results)
        assert report.passed() is False

    def test_passed_fails_on_crash(self):
        results = [
            ftc.PkgResult("numpy", "ok"),
            ftc.PkgResult("bad", "crash", error="boom"),
        ]
        report = self._make_report(results)
        assert report.passed() is False

    def test_to_dict_serialization(self):
        results = [ftc.PkgResult("numpy", "ok", version="2.0")]
        report = self._make_report(results, is_ft=True)
        d = report.to_dict()
        assert d["is_free_threading"] is True
        assert d["python_version"] == "3.14.6"
        assert d["gil_enabled"] is False
        assert isinstance(d["results"], list)
        assert d["results"][0]["name"] == "numpy"
        assert d["summary"]["ok"] == 1
        assert "known_incompatible" in d
        assert "alternatives" in d


class TestIsFreeThreadingBuild:
    """Tests for is_free_threading_build() detection logic."""

    def test_detects_free_threading_from_soabi(self):
        """SOABI contains 't' suffix like cpython-314t-x86_64-linux-gnu."""
        with mock.patch("sysconfig.get_config_var") as mock_gv:
            def gv_side_effect(key):
                if key == "SOABI":
                    return "cpython-314t-x86_64-linux-gnu"
                return None
            mock_gv.side_effect = gv_side_effect
            is_ft, gil_enabled = ftc.is_free_threading_build()
        assert is_ft is True

    def test_detects_standard_build_from_soabi(self):
        """SOABI without 't' suffix like cpython-314-x86_64-linux-gnu."""
        with mock.patch("sysconfig.get_config_var") as mock_gv:
            mock_gv.return_value = "cpython-314-x86_64-linux-gnu"
            is_ft, _ = ftc.is_free_threading_build()
        assert is_ft is False

    def test_detects_from_py_gil_disabled_flag(self):
        """When SOABI doesn't have info but Py_GIL_DISABLED=1."""
        with mock.patch("sysconfig.get_config_var") as mock_gv:
            def gv_side_effect(key):
                if key == "SOABI":
                    return None
                if key == "Py_GIL_DISABLED":
                    return 1
                return None
            mock_gv.side_effect = gv_side_effect
            is_ft, _ = ftc.is_free_threading_build()
        assert is_ft is True

    def test_gil_enabled_none_on_standard_python(self):
        """On standard Python (no sys._is_gil_enabled), gil_enabled should be None."""
        with mock.patch("sysconfig.get_config_var", return_value="cpython-312-x86_64-linux-gnu"):
            # Standard Python doesn't have _is_gil_enabled
            original = getattr(sys, "_is_gil_enabled", None)
            if hasattr(sys, "_is_gil_enabled"):
                delattr(sys, "_is_gil_enabled")
            try:
                is_ft, gil_enabled = ftc.is_free_threading_build()
                assert is_ft is False
                assert gil_enabled is None
            finally:
                if original is not None:
                    sys._is_gil_enabled = original


class TestTryImport:
    """Tests for try_import() using mocked importlib."""

    def test_absent_when_spec_is_none(self):
        """Package not installed should return status='absent'."""
        with mock.patch("importlib.util.find_spec", return_value=None):
            r = ftc.try_import("nonexistent_pkg")
        assert r.status == "absent"
        assert r.name == "nonexistent_pkg"

    def test_ok_when_import_succeeds(self):
        """Package exists and imports successfully should return status='ok' with version."""
        fake_mod = types.ModuleType("fakepkg")
        fake_mod.__version__ = "1.2.3"
        with mock.patch("importlib.util.find_spec", return_value=mock.MagicMock()):
            with mock.patch("importlib.import_module", return_value=fake_mod):
                r = ftc.try_import("fakepkg")
        assert r.status == "ok"
        assert r.version == "1.2.3"

    def test_ok_without_version_attribute(self):
        """Package imports but has no __version__."""
        fake_mod = types.ModuleType("fakepkg")
        with mock.patch("importlib.util.find_spec", return_value=mock.MagicMock()):
            with mock.patch("importlib.import_module", return_value=fake_mod):
                r = ftc.try_import("fakepkg")
        assert r.status == "ok"
        assert r.version is None

    def test_import_error_status(self):
        """Package spec exists but import raises ImportError."""
        with mock.patch("importlib.util.find_spec", return_value=mock.MagicMock()):
            with mock.patch("importlib.import_module", side_effect=ImportError("DLL load failed")):
                r = ftc.try_import("brokennative")
        assert r.status == "import_error"
        assert "DLL load failed" in (r.error or "")

    def test_crash_status_on_other_exceptions(self):
        """Package spec exists but import raises a non-ImportError exception (e.g., segfault-like)."""
        with mock.patch("importlib.util.find_spec", return_value=mock.MagicMock()):
            with mock.patch("importlib.import_module", side_effect=RuntimeError("crash during init")):
                r = ftc.try_import("crashypkg")
        assert r.status == "crash"
        assert "RuntimeError" in (r.error or "")


class TestCheckPackages:
    """Tests for check_packages() orchestration logic."""

    def test_check_packages_with_mocked_imports(self):
        """Full check_packages run with mocked imports; verifies result types and counts."""
        def fake_find_spec(name):
            if name in ("numpy", "onnx"):
                return mock.MagicMock()  # exists
            return None  # absent

        def fake_import_module(name):
            m = types.ModuleType(name)
            m.__version__ = f"{name}-version"
            return m

        with mock.patch("importlib.util.find_spec", side_effect=fake_find_spec):
            with mock.patch("importlib.import_module", side_effect=fake_import_module):
                report = ftc.check_packages(
                    import_packages=["numpy", "onnx"],
                    expect_absent=["onnxoptimizer"],
                )

        assert report.is_free_threading in (True, False)  # depends on test env
        assert isinstance(report.python_version, str)
        names = [r.name for r in report.results]
        assert "numpy" in names
        assert "onnx" in names
        assert "onnxoptimizer" in names

        numpy_result = [r for r in report.results if r.name == "numpy"][0]
        assert numpy_result.status == "ok"

        onnxopt_result = [r for r in report.results if r.name == "onnxoptimizer"][0]
        assert onnxopt_result.status == "absent"

    def test_extra_incompatible_merged(self):
        """extra_incompatible and extra_alternatives should be merged into the report."""
        with mock.patch("importlib.util.find_spec", return_value=None):
            report = ftc.check_packages(
                import_packages=[],
                expect_absent=[],
                extra_incompatible={"custom_pkg": "test reason"},
                extra_alternatives={"custom_pkg": "test alt"},
            )
        assert "custom_pkg" in report.known_incompatible
        assert report.known_incompatible["custom_pkg"] == "test reason"
        assert "custom_pkg" in report.alternatives


class TestDefaultLists:
    """Tests for default package list constants."""

    def test_default_import_packages_includes_core_onnx(self):
        assert "onnx" in ftc.DEFAULT_IMPORT_PACKAGES
        assert "onnxruntime" in ftc.DEFAULT_IMPORT_PACKAGES
        assert "numpy" in ftc.DEFAULT_IMPORT_PACKAGES

    def test_default_expect_absent_includes_onnxoptimizer(self):
        assert "onnxoptimizer" in ftc.DEFAULT_EXPECT_ABSENT

    def test_known_incompatible_and_alternatives_keys_match(self):
        """Every known_incompatible pkg should have an alternative entry."""
        for pkg in ftc.KNOWN_INCOMPATIBLE:
            assert pkg in ftc.ALTERNATIVES, f"Missing alternative for {pkg}"
