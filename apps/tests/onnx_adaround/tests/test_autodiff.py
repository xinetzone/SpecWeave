from __future__ import annotations

import numpy as np

from onnx_adaround.autodiff import Adam, Tensor, mse_loss, ops

from .conftest import ref_conv2d


def _numerical_grad(f, x, eps=1e-5):
    grad = np.zeros_like(x)
    it = np.nditer(x, flags=["multi_index"])
    for _ in it:
        idx = it.multi_index
        xp = x.copy()
        xm = x.copy()
        xp[idx] += eps
        xm[idx] -= eps
        grad[idx] = (f(xp) - f(xm)) / (2 * eps)
    return grad


def test_matmul_gradient():
    a = np.random.default_rng(0).standard_normal((3, 4))
    b = np.random.default_rng(1).standard_normal((4, 5))

    def f(x):
        return ((ops.matmul(Tensor(x), Tensor(b)) - 1.0) ** 2).sum().data

    ta = Tensor(a, requires_grad=True)
    loss = (ops.matmul(ta, Tensor(b)) - 1.0) ** 2
    loss.sum().backward()
    analytic = ta.grad
    numerical = _numerical_grad(f, a)
    rel = np.abs(analytic - numerical) / (np.abs(numerical) + 1e-8)
    assert np.max(rel) < 1e-4


def test_conv2d_forward_matches_reference():
    x = np.random.default_rng(2).standard_normal((1, 3, 8, 8))
    w = np.random.default_rng(3).standard_normal((4, 3, 3, 3))
    out = ops.conv2d(Tensor(x), Tensor(w), Tensor(np.zeros(4)), stride=1, padding=1, groups=1)
    ref = ref_conv2d(x, w, np.zeros(4), stride=1, padding=1)
    assert np.allclose(out.data, ref, atol=1e-8)


def test_conv2d_weight_gradient():
    x = np.random.default_rng(4).standard_normal((1, 2, 6, 6))
    w = np.random.default_rng(5).standard_normal((3, 2, 3, 3))

    def f(warr):
        out = ops.conv2d(Tensor(x), Tensor(warr), Tensor(np.zeros(3)), stride=1, padding=1, groups=1)
        return (out ** 2).sum().data

    tw = Tensor(w, requires_grad=True)
    out = ops.conv2d(Tensor(x), tw, Tensor(np.zeros(3)), stride=1, padding=1, groups=1)
    (out ** 2).sum().backward()
    analytic = tw.grad
    numerical = _numerical_grad(f, w)
    rel = np.abs(analytic - numerical) / (np.abs(numerical) + 1e-8)
    assert np.max(rel) < 1e-4


def test_sigmoid_gradient():
    x = np.random.default_rng(6).standard_normal((2, 3))

    def f(xarr):
        return ops.sigmoid(Tensor(xarr)).sum().data

    tx = Tensor(x, requires_grad=True)
    ops.sigmoid(tx).sum().backward()
    analytic = tx.grad
    numerical = _numerical_grad(f, x)
    rel = np.abs(analytic - numerical) / (np.abs(numerical) + 1e-8)
    assert np.max(rel) < 1e-4


def test_adam_decreases_loss():
    target = np.array([1.0, 2.0, 3.0, 4.0])
    x = {"param": {"data": np.zeros(4), "grad": np.zeros(4)}}
    opt = Adam(x, lr=0.1)
    losses = []
    for _ in range(200):
        p = Tensor(x["param"]["data"], requires_grad=True)
        loss = ((p - Tensor(target)) ** 2).sum()
        opt.zero_grad()
        loss.backward()
        x["param"]["grad"] = p.grad
        opt.step()
        losses.append(float(loss.data))
    assert losses[-1] < losses[0]
    assert np.allclose(x["param"]["data"], target, atol=1e-2)


def test_mse_loss_scalar():
    pred = Tensor(np.ones((2, 3)))
    tgt = Tensor(np.zeros((2, 3)))
    loss = mse_loss(pred, tgt, p=2.0)
    assert np.isclose(loss.data, 1.0)
