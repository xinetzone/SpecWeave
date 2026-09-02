"""tvm-ffi 桥接测试：参考实现公式 + 原生 DLL 加载（可用时）。"""

from __future__ import annotations

import math
import os

from agent_monetize.core.ffi_bridge import FfiBridge, _reference_score_opportunity, default_bridge

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
NATIVE_LIB = os.path.join(PROJECT_ROOT, "native", "build", "score_opportunity.dll")


class TestReferenceImpl:
    def test_formula_values(self) -> None:
        # base = 10 * 0.8 * (1 + 1.5) = 20 ; (20 / (1 + 2)) ** 0.8 = (6.6666) ** 0.8
        expected = (10 * 0.8 * (1 + 1.5) / (1 + 2)) ** 0.8
        assert _reference_score_opportunity(10.0, 0.8, 1.5, 2.0) == expected

    def test_clamps(self) -> None:
        assert _reference_score_opportunity(-5.0, 3.0, 5.0, -2.0) <= 100.0
        assert _reference_score_opportunity(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_monotonic_in_return(self) -> None:
        low = _reference_score_opportunity(1.0, 0.9, 1.0, 0.1)
        high = _reference_score_opportunity(100.0, 0.9, 1.0, 0.1)
        assert high > low


class TestFfiBridgeReference:
    def test_fallback_backend(self) -> None:
        bridge = FfiBridge(fallback_to_reference=True)
        bridge.initialize(native_lib_paths=[])
        assert bridge.backend == "reference"

    def test_score_without_native(self) -> None:
        bridge = FfiBridge()
        bridge.initialize(native_lib_paths=[])
        assert bridge.score_opportunity(10.0, 0.8, 1.5, 2.0) > 0

    def test_probe_sets_flag(self) -> None:
        bridge = FfiBridge()
        bridge.probe()
        assert bridge.tvm_ffi_available is True  # py314 环境应已安装 tvm-ffi


class TestFfiBridgeNative:
    def test_native_backend_when_dll_exists(self) -> None:
        if not os.path.exists(NATIVE_LIB):
            return  # 原生未编译则跳过（CI 环境无 MSVC）
        bridge = default_bridge(native_lib_paths=[NATIVE_LIB])
        assert bridge.backend == "native"
        assert bridge.native_lib_path == NATIVE_LIB

    def test_native_matches_reference(self) -> None:
        if not os.path.exists(NATIVE_LIB):
            return
        bridge = default_bridge(native_lib_paths=[NATIVE_LIB])
        for args in [
            (10.0, 0.8, 1.5, 2.0),
            (3.0, 0.5, 0.2, 0.3),
            (50.0, 1.0, 3.0, 5.0),
        ]:
            native = bridge.score_opportunity(*args)
            ref = _reference_score_opportunity(*args)
            assert math.isclose(native, ref, rel_tol=1e-6)

    def test_missing_dll_falls_back(self) -> None:
        bridge = default_bridge(native_lib_paths=["native/build/does-not-exist.dll"])
        assert bridge.backend == "reference"
