"""Autodiff ops for onnx-adaround (numpy reverse-mode)."""

from __future__ import annotations

import numpy as np

from .tensor import Tensor


def _t(a):
    return a.data if isinstance(a, Tensor) else np.asarray(a, dtype=np.float64)


def _wrap(data, children, grad_fn, requires_grad=False):
    return Tensor(data, requires_grad=requires_grad, grad_fn=grad_fn, children=children)


def add(a, b):
    a_arr, b_arr = _t(a), _t(b)
    out = a_arr + b_arr

    def grad_fn(g):
        ga = _broadcast_grad(g, a_arr.shape)
        gb = _broadcast_grad(g, b_arr.shape)
        return ga, gb

    return _wrap(out, (a, b), grad_fn)


def _broadcast_grad(g, shape):
    if shape == g.shape:
        return g
    # reduce summed axes to match shape
    while g.ndim > len(shape):
        g = g.sum(axis=0)
    for axis, (gdim, sdim) in enumerate(zip(g.shape, shape)):
        if sdim == 1 and gdim != 1:
            g = g.sum(axis=axis, keepdims=True)
    return g


def mul(a, b):
    a_arr, b_arr = _t(a), _t(b)
    out = a_arr * b_arr

    def grad_fn(g):
        return _broadcast_grad(g * b_arr, a_arr.shape), _broadcast_grad(g * a_arr, b_arr.shape)

    return _wrap(out, (a, b), grad_fn)


def div(a, b):
    a_arr, b_arr = _t(a), _t(b)
    out = a_arr / b_arr

    def grad_fn(g):
        ga = _broadcast_grad(g / b_arr, a_arr.shape)
        gb = _broadcast_grad(-g * a_arr / (b_arr ** 2), b_arr.shape)
        return ga, gb

    return _wrap(out, (a, b), grad_fn)


def pow(a, p):
    a_arr = _t(a)
    out = a_arr ** p

    def grad_fn(g):
        return (g * p * a_arr ** (p - 1)).reshape(a_arr.shape),

    return _wrap(out, (a,), grad_fn)


def sum(a, axis=None):
    a_arr = _t(a)
    out = a_arr.sum(axis=axis)

    def grad_fn(g):
        if axis is None:
            return np.broadcast_to(g, a_arr.shape),
        return np.broadcast_to(g, a_arr.shape),

    return _wrap(out, (a,), grad_fn)


def mean(a):
    a_arr = _t(a)
    out = a_arr.mean()

    def grad_fn(g):
        return np.broadcast_to(g / a_arr.size, a_arr.shape),

    return _wrap(out, (a,), grad_fn)


def relu(a):
    a_arr = _t(a)
    out = np.maximum(a_arr, 0.0)

    def grad_fn(g):
        return (g * (a_arr > 0)),

    return _wrap(out, (a,), grad_fn)


def abs(a):
    a_arr = _t(a)
    out = np.abs(a_arr)

    def grad_fn(g):
        return (g * np.sign(a_arr)),

    return _wrap(out, (a,), grad_fn)


def clip(a, lo, hi):
    a_arr = _t(a)
    out = np.clip(a_arr, lo, hi)

    def grad_fn(g):
        mask = (a_arr > lo) & (a_arr < hi)
        return (g * mask),

    return _wrap(out, (a,), grad_fn)


def sigmoid(a):
    a_arr = _t(a)
    s = 1.0 / (1.0 + np.exp(-a_arr))
    out = s

    def grad_fn(g):
        return (g * s * (1.0 - s)),

    return _wrap(out, (a,), grad_fn)


def round_ste(a):
    """Straight-through rounding: forward rounds, backward passes gradient."""
    a_arr = _t(a)
    out = np.round(a_arr)

    def grad_fn(g):
        return g,

    return _wrap(out, (a,), grad_fn)


def floor(a):
    """Floor op (zero gradient)."""
    a_arr = _t(a)
    out = np.floor(a_arr)

    def grad_fn(g):
        return np.zeros_like(a_arr),

    return _wrap(out, (a,), grad_fn)


def matmul(a, b):
    a_arr, b_arr = _t(a), _t(b)
    out = np.matmul(a_arr, b_arr)

    def grad_fn(g):
        ga = np.matmul(g, np.swapaxes(b_arr, -1, -2))
        gb = np.matmul(np.swapaxes(a_arr, -1, -2), g)
        return ga, gb

    return _wrap(out, (a, b), grad_fn)


def conv2d(x, w, b, stride=1, padding=0, groups=1):
    """Numpy conv2d forward/backward on NCHW data.

    Supports stride/padding as ints or 2-tuples, and grouped convolution.
    """
    x_arr, w_arr = _t(x), _t(w)
    b_arr = _t(b)
    out = _conv2d_forward(x_arr, w_arr, b_arr, stride, padding, groups)

    def grad_fn(g):
        gx = _conv2d_input_grad(g, w_arr, stride, padding, groups, x_arr.shape)
        gw = _conv2d_weight_grad(g, x_arr, stride, padding, groups, w_arr.shape)
        gb = _conv2d_bias_grad(g, b_arr.shape)
        return gx, gw, gb

    return _wrap(out, (x, w, b), grad_fn)


def _to_pair(v):
    if isinstance(v, (tuple, list)):
        return int(v[0]), int(v[1])
    return int(v), int(v)


def _pad(x, padding):
    ph, pw = _to_pair(padding)
    if ph == 0 and pw == 0:
        return x
    return np.pad(x, ((0, 0), (0, 0), (ph, ph), (pw, pw)))


def _conv2d_forward(x, w, b, stride, padding, groups):
    xp = _pad(x, padding)
    n, c_in, h, w_in = xp.shape
    sh, sw = _to_pair(stride)
    g = int(groups)
    c_out = w.shape[0]
    c_per_g = c_in // g
    oc_per_g = c_out // g
    kh, kw = w.shape[2], w.shape[3]
    oh = (h - kh) // sh + 1
    ow = (w_in - kw) // sw + 1
    out = np.zeros((n, c_out, oh, ow), dtype=np.float64)
    # im2col over kernel
    cols = _im2col(xp, kh, kw, sh, sw)  # (n, c_in, kh, kw, oh, ow)
    for gg in range(g):
        w_g = w[gg * oc_per_g:(gg + 1) * oc_per_g]  # (oc_per_g, c_per_g, kh, kw)
        w_flat = w_g.reshape(oc_per_g, -1)  # (oc_per_g, c_per_g*kh*kw)
        c_slice = slice(gg * c_per_g, (gg + 1) * c_per_g)
        col_g = cols[:, c_slice].reshape(n, c_per_g * kh * kw, oh * ow)  # (n, K, P)
        res = np.einsum("ok,nkp->nop", w_flat, col_g)  # (n, oc_per_g, P)
        res = res.reshape(n, oc_per_g, oh, ow)
        if b is not None and b.size > 0:
            res += b[gg * oc_per_g:(gg + 1) * oc_per_g].reshape(1, -1, 1, 1)
        out[:, gg * oc_per_g:(gg + 1) * oc_per_g] = res
    return out


def _im2col(xp, kh, kw, sh, sw):
    """Extract patches: xp (n,c,h,w) -> (n, c, kh, kw, oh, ow)."""
    n, c, h, w = xp.shape
    oh = (h - kh) // sh + 1
    ow = (w - kw) // sw + 1
    cols = np.zeros((n, c, kh, kw, oh, ow), dtype=np.float64)
    for ki in range(kh):
        for kj in range(kw):
            cols[:, :, ki, kj] = xp[:, :, ki:ki + oh * sh:sh, kj:kj + ow * sw:sw]
    return cols


def _conv2d_input_grad(g, w, stride, padding, groups, x_shape):
    ph, pw = _to_pair(padding)
    sh, sw = _to_pair(stride)
    g_t = int(groups)
    xp = np.zeros((x_shape[0], x_shape[1], x_shape[2] + 2 * ph, x_shape[3] + 2 * pw),
                  dtype=np.float64)
    c_out = w.shape[0]
    c_in = x_shape[1]
    kh, kw = w.shape[2], w.shape[3]
    n, _, oh, ow = g.shape
    c_per_g = c_in // g_t
    oc_per_g = c_out // g_t
    for gg in range(g_t):
        for oc in range(oc_per_g):
            oc_global = gg * oc_per_g + oc
            w_g = w[oc_global]  # (c_per_g, kh, kw)
            g_g = g[:, oc_global]  # (n, oh, ow)
            for ci in range(c_per_g):
                for ki in range(kh):
                    for kj in range(kw):
                        xp[:, gg * c_per_g + ci, ki:ki + oh * sh:sh,
                           kj:kj + ow * sw:sw] += g_g * w_g[ci, ki, kj]
    # crop padding
    if ph > 0 or pw > 0:
        xp = xp[:, :, ph:ph + x_shape[2], pw:pw + x_shape[3]]
    return xp


def _conv2d_weight_grad(g, x, stride, padding, groups, w_shape):
    xp = _pad(x, padding)
    sh, sw = _to_pair(stride)
    g_t = int(groups)
    c_out = w_shape[0]
    c_in = w_shape[1]
    kh, kw = w_shape[2], w_shape[3]
    n, _, oh, ow = g.shape
    c_per_g = c_in // g_t
    oc_per_g = c_out // g_t
    cols = _im2col(xp, kh, kw, sh, sw)  # (n, c_in, kh, kw, oh, ow)
    gw = np.zeros(w_shape, dtype=np.float64)
    for gg in range(g_t):
        for oc in range(oc_per_g):
            oc_global = gg * oc_per_g + oc
            g_g = g[:, oc_global]  # (n, oh, ow)
            for ci in range(c_per_g):
                for ki in range(kh):
                    for kj in range(kw):
                        gw[oc_global, ci, ki, kj] = np.sum(
                            g_g * cols[:, gg * c_per_g + ci, ki, kj])
    return gw


def _conv2d_bias_grad(g, b_shape):
    if b_shape is None or np.prod(b_shape) == 0:
        return np.zeros(0)
    return g.sum(axis=(0, 2, 3))
