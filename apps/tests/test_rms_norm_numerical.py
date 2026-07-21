"""Numerical verification for Normalize -> RMSNorm reparameterization.

Reference: L2 normalize: y = x / sqrt(sum(x^2) + eps) * gamma
           RMSNorm reparam: y = x / sqrt(mean(x^2) + eps/d) * (gamma/sqrt(d))
where d is the normalization axis extent.

rms_norm natively supports arbitrary axis, so no transpose is needed.
"""
import math
from dataclasses import dataclass

import numpy as np


def l2_normalize_scale_tensor(x: np.ndarray, gamma: np.ndarray, eps: float, axis: int) -> np.ndarray:
    """Reference L2 normalize with channel scale: x / sqrt(sum(x^2, axis) + eps) * gamma."""
    axis = axis if axis >= 0 else x.ndim + axis
    denom = np.sqrt(np.sum(x * x, axis=axis, keepdims=True) + eps)
    gamma_shape = [1] * x.ndim
    gamma_shape[axis] = gamma.shape[0]
    return (x / denom) * gamma.reshape(gamma_shape)


def rmsnorm_reparam_tensor(x: np.ndarray, gamma: np.ndarray, eps: float, axis: int) -> np.ndarray:
    """RMSNorm reparameterized form: x / sqrt(mean(x^2) + eps/d) * (gamma/sqrt(d)).

    This directly computes on the specified axis without transpose, matching
    TVM's rms_norm operator which supports arbitrary axis natively.
    """
    axis = axis if axis >= 0 else x.ndim + axis
    d = x.shape[axis]
    gamma_rms = gamma / math.sqrt(d)
    eps_rms = eps / d
    rho = np.sqrt(np.mean(x * x, axis=axis, keepdims=True) + eps_rms)
    gamma_shape = [1] * x.ndim
    gamma_shape[axis] = d
    return (x / rho) * gamma_rms.reshape(gamma_shape)


@dataclass
class VerifySummary:
    name: str
    cases: int
    max_abs_diff: float
    threshold: float

    @property
    def passed(self) -> bool:
        return self.max_abs_diff <= self.threshold


def verify_rmsnorm_equivalence(rng: np.random.Generator) -> VerifySummary:
    """Verify L2 normalize + scale == RMSNorm reparameterization across shapes/axes."""
    max_abs_diff = 0.0
    cases = 0
    shapes = [
        (5,),
        (2, 3),
        (2, 3, 4),
        (2, 3, 4, 5),
        (1, 4, 6, 3),
        (2, 5, 3, 4, 2),
        (1, 1, 8),
        (3, 8, 8),
    ]
    for shape in shapes:
        ndim = len(shape)
        for axis in list(range(ndim)) + list(range(-ndim, 0)):
            d = shape[axis % ndim]
            for _ in range(20):
                x = rng.normal(size=shape).astype(np.float32)
                gamma = rng.normal(size=d).astype(np.float32)
                eps = float(10 ** rng.uniform(-10, -2))
                y_l2 = l2_normalize_scale_tensor(x, gamma, eps, axis=axis)
                y_rms = rmsnorm_reparam_tensor(x, gamma, eps, axis=axis)
                max_abs_diff = max(max_abs_diff, float(np.max(np.abs(y_l2 - y_rms))))
                cases += 1
    return VerifySummary("rmsnorm_direct_axis_equivalence", cases, max_abs_diff, 1e-5)


def verify_channel_axis(rng: np.random.Generator) -> VerifySummary:
    """Verify Caffe default channel axis (axis=1) with various 4D/5D shapes."""
    max_abs_diff = 0.0
    cases = 0
    shapes = [
        (1, 3, 8, 8),
        (2, 16, 32, 32),
        (1, 32, 14, 14),
        (1, 64, 7, 7),
        (2, 3, 8, 8, 8),
    ]
    for shape in shapes:
        c = shape[1]
        for _ in range(30):
            x = rng.normal(size=shape).astype(np.float32)
            gamma = rng.normal(size=c).astype(np.float32)
            eps = float(10 ** rng.uniform(-10, -3))
            y_l2 = l2_normalize_scale_tensor(x, gamma, eps, axis=1)
            y_rms = rmsnorm_reparam_tensor(x, gamma, eps, axis=1)
            max_abs_diff = max(max_abs_diff, float(np.max(np.abs(y_l2 - y_rms))))
            cases += 1
    return VerifySummary("channel_axis_equivalence", cases, max_abs_diff, 1e-5)


def verify_channel_shared(rng: np.random.Generator) -> VerifySummary:
    """Verify channel_shared (scalar scale broadcast) works correctly on axis=1."""
    max_abs_diff = 0.0
    cases = 0
    shapes = [(2, 3, 4), (1, 8, 16, 16), (2, 16, 8), (1, 32, 7, 7)]
    for shape in shapes:
        c = shape[1]
        for _ in range(25):
            x = rng.normal(size=shape).astype(np.float32)
            scale_scalar = float(rng.normal())
            gamma = np.full((c,), scale_scalar, dtype=np.float32)
            eps = float(10 ** rng.uniform(-10, -3))
            y_l2 = l2_normalize_scale_tensor(x, gamma, eps, axis=1)
            y_rms = rmsnorm_reparam_tensor(x, gamma, eps, axis=1)
            max_abs_diff = max(max_abs_diff, float(np.max(np.abs(y_l2 - y_rms))))
            cases += 1
    return VerifySummary("channel_shared_equivalence", cases, max_abs_diff, 1e-5)


def main() -> None:
    rng = np.random.default_rng(20260721)
    summaries = [
        verify_rmsnorm_equivalence(rng),
        verify_channel_axis(rng),
        verify_channel_shared(rng),
    ]

    print("NumPy numerical verification for Normalize -> RMSNorm (no transpose)")
    print("-" * 72)
    all_passed = True
    for summary in summaries:
        all_passed = all_passed and summary.passed
        print(
            f"{summary.name:36s} cases={summary.cases:4d} "
            f"max_abs_diff={summary.max_abs_diff:.6e} "
            f"threshold={summary.threshold:.1e} "
            f"status={'PASS' if summary.passed else 'FAIL'}"
        )

    print("-" * 72)
    if not all_passed:
        raise SystemExit("Verification failed.")
    print("All numerical verification checks passed.")


if __name__ == "__main__":
    main()
