"""tvm-ffi 桥接：原生 C++ FFI 优先，纯 Python 参考实现优雅降级。

调用路径（决策层经本模块调用机会打分，保证代码中真实存在对 tvm-ffi 的调用路径）：
  1. 探测 `import tvm_ffi`；失败 → 直接参考实现 + WARN。
  2. 定位并加载原生模块（`native/build/score_opportunity.dll`，C++ 静态初始化注册
     `score_opportunity` PackedFunc）；加载成功 → 经 `tvm_ffi.get_global_func` 调用。
  3. 原生不可用 → `fallback_to_reference` 时走纯 Python 参考实现 + WARN。
"""

from __future__ import annotations

import ctypes
import logging
import os
from collections.abc import Callable

logger = logging.getLogger(__name__)

_WARNED_REFERENCE = False


def _reference_score_opportunity(
    expected_return: float,
    certainty: float,
    scarcity_factor: float,
    est_cost: float,
) -> float:
    """纯 Python 参考实现（与 C++ 原生版同公式）。

    score = (max(0, 预期收益) * clamp(确定性,0,1) * (1 + clamp(稀缺因子,0,3))) / (1 + max(0, 成本))
    再做 0.8 次幂压缩并 clamp 到 [0, 100]。
    """
    certainty_c = max(0.0, min(1.0, certainty))
    scarcity_c = max(0.0, min(3.0, scarcity_factor))
    ret = max(0.0, expected_return)
    cost = max(0.0, est_cost)
    base = ret * certainty_c * (1.0 + scarcity_c)
    score = (base / (1.0 + cost)) ** 0.8
    return max(0.0, min(100.0, score))


class FfiBridge:
    """机会打分桥接器（可单测、可重置）。"""

    def __init__(self, fallback_to_reference: bool = True) -> None:
        self.fallback_to_reference = fallback_to_reference
        self._native_func: Callable[..., float] | None = None
        self._native_lib_path: str | None = None
        self._load_error: str | None = None
        self._tvm_ffi_available = False
        self._reference_warned = False

    # -- 探测与初始化 -------------------------------------------------
    @property
    def backend(self) -> str:
        """当前打分后端：native（原生 C++ FFI）或 reference（纯 Python 参考实现）。"""
        return "native" if self._native_func is not None else "reference"

    @property
    def tvm_ffi_available(self) -> bool:
        return self._tvm_ffi_available

    @property
    def native_lib_path(self) -> str | None:
        return self._native_lib_path

    @property
    def load_error(self) -> str | None:
        return self._load_error

    def probe(self) -> bool:
        """探测 tvm_ffi 是否可导入（真实存在对 tvm-ffi 的探测/调用路径）。"""
        try:
            import tvm_ffi  # noqa: F401

            self._tvm_ffi_available = True
        except Exception as exc:  # pragma: no cover - 环境相关
            self._tvm_ffi_available = False
            self._load_error = f"tvm_ffi import 失败: {exc}"
            logger.warning("tvm_ffi import 失败，将使用纯 Python 参考实现：%s", exc)
        return self._tvm_ffi_available

    def load_native(self, native_lib_paths: list[str]) -> bool:
        """尝试加载原生 FFI 模块并取回 `score_opportunity` PackedFunc。"""
        if not self.probe():
            return False
        if self._tvm_ffi_available:
            import tvm_ffi  # 在 probe 已确认可用后导入
        else:
            return False

        for path in native_lib_paths:
            if not path or not os.path.exists(path):
                continue
            try:
                # 触发 DLL 静态初始化（TVM_FFI_STATIC_INIT_BLOCK 注册全局函数）
                ctypes.CDLL(path)
                func = tvm_ffi.get_global_func("score_opportunity")
                if func is not None:
                    self._native_func = func
                    self._native_lib_path = path
                    logger.info("已加载原生 tvm-ffi 模块：%s（backend=native）", path)
                    return True
                self._load_error = f"原生模块 {path} 未注册 score_opportunity"
            except Exception as exc:  # pragma: no cover - 环境相关
                self._load_error = f"加载原生模块 {path} 失败: {exc}"
                logger.warning("加载原生模块 %s 失败：%s", path, exc)
        return False

    def initialize(self, native_lib_paths: list[str] | None = None) -> str:
        """一键初始化：探测 → 尝试原生 → 降级参考实现。返回 backend。"""
        paths = [p for p in (native_lib_paths or []) if p]
        if self.load_native(paths):
            return self.backend
        if self.fallback_to_reference:
            if not self._reference_warned:
                self._reference_warned = True
                logger.warning(
                    "原生 tvm-ffi 模块不可用，降级到纯 Python 参考实现（backend=reference）。"
                    "可用 `native/build.ps1` 编译 C++ FFI 模块启用原生打分。"
                )
        return self.backend

    # -- 打分接口 -----------------------------------------------------
    def score_opportunity(
        self,
        expected_return: float,
        certainty: float,
        scarcity_factor: float,
        est_cost: float,
    ) -> float:
        """机会打分：原生可用则走 tvm-ffi，否则走参考实现。"""
        if self._native_func is not None:
            return float(self._native_func(expected_return, certainty, scarcity_factor, est_cost))
        if not self._reference_warned:
            self._reference_warned = True
            logger.warning("打分使用纯 Python 参考实现（原生 tvm-ffi 未启用）")
        return _reference_score_opportunity(expected_return, certainty, scarcity_factor, est_cost)


def default_bridge(
    native_lib_paths: list[str] | None = None, fallback_to_reference: bool = True
) -> FfiBridge:
    """创建并初始化默认桥接器。"""
    bridge = FfiBridge(fallback_to_reference=fallback_to_reference)
    bridge.initialize(native_lib_paths=native_lib_paths)
    return bridge
