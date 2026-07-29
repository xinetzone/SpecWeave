import math
from dataclasses import dataclass

import numpy as np


def l2_normalize_scale_vector(x: np.ndarray, gamma: np.ndarray, eps: float) -> np.ndarray:
    """Reference form: x / sqrt(sum(x^2) + eps) * gamma."""
    r = np.sqrt(np.dot(x, x) + eps)
    return (x / r) * gamma


def rmsnorm_reparam_vector(x: np.ndarray, gamma: np.ndarray, eps: float) -> np.ndarray:
    """Reparameterized RMSNorm form with gamma/sqrt(d), eps/d."""
    d = x.shape[0]
    gamma_rms = gamma / math.sqrt(d)
    eps_rms = eps / d
    rho = np.sqrt(np.mean(x * x) + eps_rms)
    return (x / rho) * gamma_rms


def jacobian_l2_closed_form(x: np.ndarray, gamma: np.ndarray, eps: float) -> np.ndarray:
    """Jacobian of z = (x / sqrt(x x^T + eps)) Gamma for row-vector convention."""
    d = x.shape[0]
    r = np.sqrt(np.dot(x, x) + eps)
    base = np.eye(d, dtype=np.float64) / r - np.outer(x, x) / (r**3)
    return base @ np.diag(gamma)


def jacobian_rms_closed_form(x: np.ndarray, gamma: np.ndarray, eps: float) -> np.ndarray:
    """Jacobian of the reparameterized RMSNorm form."""
    d = x.shape[0]
    gamma_rms = gamma / math.sqrt(d)
    eps_rms = eps / d
    rho = np.sqrt(np.mean(x * x) + eps_rms)
    base = np.eye(d, dtype=np.float64) / rho - np.outer(x, x) / (d * rho**3)
    return base @ np.diag(gamma_rms)


def finite_difference_jacobian(func, x: np.ndarray, step: float = 1e-6) -> np.ndarray:
    """Return the standard Jacobian with entries d y_i / d x_j."""
    d = x.shape[0]
    jac = np.zeros((d, d), dtype=np.float64)
    for j in range(d):
        delta = np.zeros_like(x)
        delta[j] = step
        y_pos = func(x + delta)
        y_neg = func(x - delta)
        jac[:, j] = (y_pos - y_neg) / (2.0 * step)
    return jac


def l2_normalize_scale_tensor(x: np.ndarray, gamma: np.ndarray, eps: float, axis: int) -> np.ndarray:
    denom = np.sqrt(np.sum(x * x, axis=axis, keepdims=True) + eps)
    gamma_shape = [1] * x.ndim
    gamma_shape[axis] = gamma.shape[0]
    return (x / denom) * gamma.reshape(gamma_shape)


def rmsnorm_tensor(x: np.ndarray, gamma: np.ndarray, eps: float, axis: int) -> np.ndarray:
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


def verify_forward_vectors(rng: np.random.Generator) -> VerifySummary:
    max_abs_diff = 0.0
    cases = 0
    for d in [1, 2, 3, 4, 8, 16, 32]:
        for _ in range(50):
            x = rng.normal(size=d)
            gamma = rng.normal(size=d)
            eps = float(10 ** rng.uniform(-8, -2))
            y_l2 = l2_normalize_scale_vector(x, gamma, eps)
            y_rms = rmsnorm_reparam_vector(x, gamma, eps)
            max_abs_diff = max(max_abs_diff, float(np.max(np.abs(y_l2 - y_rms))))
            cases += 1
    return VerifySummary("forward_vector_equivalence", cases, max_abs_diff, 1e-12)


def verify_jacobian_closed_forms(rng: np.random.Generator) -> VerifySummary:
    max_abs_diff = 0.0
    cases = 0
    for d in [1, 2, 3, 4, 8, 16]:
        for _ in range(30):
            x = rng.normal(size=d)
            gamma = rng.normal(size=d)
            eps = float(10 ** rng.uniform(-8, -2))
            j_l2 = jacobian_l2_closed_form(x, gamma, eps)
            j_rms = jacobian_rms_closed_form(x, gamma, eps)
            max_abs_diff = max(max_abs_diff, float(np.max(np.abs(j_l2 - j_rms))))
            cases += 1
    return VerifySummary("jacobian_closed_form_equivalence", cases, max_abs_diff, 1e-12)


def verify_jacobian_vs_finite_difference(rng: np.random.Generator) -> VerifySummary:
    max_abs_diff = 0.0
    cases = 0
    for d in [1, 2, 3, 4, 8]:
        for _ in range(20):
            x = rng.normal(size=d)
            gamma = rng.normal(size=d)
            eps = float(10 ** rng.uniform(-8, -2))

            def f_l2(v: np.ndarray) -> np.ndarray:
                return l2_normalize_scale_vector(v, gamma, eps)

            def f_rms(v: np.ndarray) -> np.ndarray:
                return rmsnorm_reparam_vector(v, gamma, eps)

            j_fd_l2 = finite_difference_jacobian(f_l2, x)
            j_fd_rms = finite_difference_jacobian(f_rms, x)
            j_l2 = jacobian_l2_closed_form(x, gamma, eps)
            j_rms = jacobian_rms_closed_form(x, gamma, eps)

            case_diff = max(
                # The closed form in the report uses row-vector convention:
                #   dy = dx J
                # while finite differences here return the standard Jacobian
                #   J_std[i, j] = d y_i / d x_j
                # Hence J_std = J^T.
                float(np.max(np.abs(j_l2.T - j_fd_l2))),
                float(np.max(np.abs(j_rms.T - j_fd_rms))),
            )
            max_abs_diff = max(max_abs_diff, case_diff)
            cases += 1
    return VerifySummary("jacobian_vs_finite_difference", cases, max_abs_diff, 5e-7)


def verify_rmsnorm_tensor(rng: np.random.Generator) -> VerifySummary:
    max_abs_diff = 0.0
    cases = 0
    shapes = [
        (5,),
        (2, 3, 4),
        (2, 3, 4, 5),
        (1, 4, 6, 3),
        (2, 5, 3, 4, 2),
        (1, 1, 8),
    ]
    for shape in shapes:
        ndim = len(shape)
        for axis in list(range(ndim)) + list(range(-ndim, 0)):
            d = shape[axis % ndim]
            for _ in range(10):
                x = rng.normal(size=shape)
                gamma = rng.normal(size=d)
                eps = float(10 ** rng.uniform(-8, -2))
                y_l2 = l2_normalize_scale_tensor(x, gamma, eps, axis=axis)
                y_rms = rmsnorm_tensor(x, gamma, eps, axis=axis)
                max_abs_diff = max(max_abs_diff, float(np.max(np.abs(y_l2 - y_rms))))
                cases += 1
    return VerifySummary("rmsnorm_tensor_equivalence", cases, max_abs_diff, 1e-12)


def main() -> None:
    rng = np.random.default_rng(20260721)
    summaries = [
        verify_forward_vectors(rng),
        verify_jacobian_closed_forms(rng),
        verify_jacobian_vs_finite_difference(rng),
        verify_rmsnorm_tensor(rng),
    ]

    print("NumPy verification for Normalize -> RMSNorm reparameterization")
    print("-" * 72)
    all_passed = True
    for summary in summaries:
        all_passed = all_passed and summary.passed
        print(
            f"{summary.name:32s} cases={summary.cases:4d} "
            f"max_abs_diff={summary.max_abs_diff:.6e} "
            f"threshold={summary.threshold:.1e} "
            f"status={'PASS' if summary.passed else 'FAIL'}"
        )

    print("-" * 72)
    if not all_passed:
        raise SystemExit("Verification failed.")
    print("All verification checks passed.")


if __name__ == "__main__":
    main()
