"""A tiny reverse-mode autodiff Tensor with a tape-based graph."""

from __future__ import annotations

import numpy as np


class Tensor:
    """Numpy-backed tensor participating in reverse-mode autodiff.

    ``data`` holds the numpy array; ``grad`` accumulates gradients during
    backward. ``_grad_fn`` is a callable ``grad_fn(grad)`` producing the
    upstream gradient (list) for children.
    """

    __slots__ = ("data", "grad", "requires_grad", "_grad_fn", "_children")

    def __init__(self, data, requires_grad: bool = False, grad_fn=None, children=()):
        self.data = np.asarray(data, dtype=np.float64)
        self.grad = None
        self.requires_grad = requires_grad
        self._grad_fn = grad_fn
        self._children = tuple(children)

    # --- arithmetic / ops dispatch ---
    def __add__(self, other):
        from . import ops
        return ops.add(self, _as_tensor(other))

    def __radd__(self, other):
        from . import ops
        return ops.add(_as_tensor(other), self)

    def __sub__(self, other):
        from . import ops
        return ops.add(self, _as_tensor(other) * (-1.0))

    def __rsub__(self, other):
        from . import ops
        return ops.add(_as_tensor(other), self * (-1.0))

    def __mul__(self, other):
        from . import ops
        return ops.mul(self, _as_tensor(other))

    def __rmul__(self, other):
        from . import ops
        return ops.mul(_as_tensor(other), self)

    def __truediv__(self, other):
        from . import ops
        return ops.div(self, _as_tensor(other))

    def __rtruediv__(self, other):
        from . import ops
        return ops.div(_as_tensor(other), self)

    def __neg__(self):
        return self * (-1.0)

    def __pow__(self, p):
        from . import ops
        return ops.pow(self, p)

    def backward(self, grad=None):
        if grad is None:
            grad = np.ones_like(self.data)
        topo = []
        visited = set()

        def _build(node):
            if id(node) in visited:
                return
            visited.add(id(node))
            for c in node._children:
                _build(c)
            topo.append(node)

        _build(self)
        self.grad = np.asarray(grad, dtype=np.float64)
        for node in reversed(topo):
            if node._grad_fn is not None:
                upstream = node._grad_fn(node.grad)
                for child, g in zip(node._children, upstream):
                    if child.grad is None:
                        child.grad = np.zeros_like(child.data)
                    child.grad = child.grad + g

    def numpy(self) -> np.ndarray:
        return self.data

    @property
    def shape(self):
        return self.data.shape

    @property
    def size(self):
        return self.data.size

    def sum(self):
        from . import ops
        return ops.sum(self)

    def mean(self):
        from . import ops
        return ops.mean(self)


def _as_tensor(value):
    if isinstance(value, Tensor):
        return value
    return Tensor(value, requires_grad=False)
