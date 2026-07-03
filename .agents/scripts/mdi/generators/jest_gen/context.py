"""Jest测试生成上下文 - _TestContext数据类。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用
"""

from __future__ import annotations

from mdi.models import Interface, Parameter


class _TestContext:
    """测试生成上下文。"""

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
    def all_required(self) -> list[Parameter]:
        return [p for p in self.path_params + self.query_params + self.body_params if p.required]
