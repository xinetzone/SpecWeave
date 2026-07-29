from __future__ import annotations


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

from mdi.models import Interface, Parameter


class _TestContext:
    """测试生成上下文，封装单个接口的参数信息。"""

    def __init__(
        self,
        path: str,
        method: str,
        path_params: list[Parameter],
        query_params: list[Parameter],
        body_params: list[Parameter],
        iface: Interface | None = None,
    ) -> None:
        self.path = path
        self.method = method
        self.path_params = path_params
        self.query_params = query_params
        self.body_params = body_params
        self.iface = iface

    @property
    def summary(self) -> str:
        return self.iface.summary if self.iface else ""

    @property
    def all_required(self) -> list[Parameter]:
        return [p for p in self.path_params + self.query_params + self.body_params if p.required]

