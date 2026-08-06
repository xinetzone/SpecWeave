"""CLI测试生成上下文。"""

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


class _CLITestContext:
    """CLI测试生成上下文，封装单个命令的参数信息。"""

    def __init__(
        self,
        command_name: str,
        method: str,
        iface: Interface | None = None,
    ) -> None:
        self.command_name = command_name
        self.method = method
        self.iface = iface
        self.arguments: list[Parameter] = []
        self.options: list[Parameter] = []
        self.flags: list[Parameter] = []

        if iface:
            is_cli = iface.method.upper() in ("CMD", "CLI", "COMMAND")
            for p in iface.parameters:
                loc = getattr(p, 'location', 'option') or 'option'
                if is_cli and loc == "body":
                    if p.type in ("boolean", "bool"):
                        self.flags.append(p)
                    elif p.required and not p.default:
                        self.arguments.append(p)
                    else:
                        self.options.append(p)
                elif loc in ("arg", "argument", "path"):
                    self.arguments.append(p)
                elif loc in ("flag",):
                    self.flags.append(p)
                else:
                    self.options.append(p)

    @property
    def summary(self) -> str:
        return self.iface.summary if self.iface else ""

    @property
    def required_args(self) -> list[Parameter]:
        return [p for p in self.arguments if p.required]

    @property
    def required_options(self) -> list[Parameter]:
        return [p for p in self.options if p.required]

    @property
    def all_required(self) -> list[Parameter]:
        return [p for p in self.arguments + self.options if p.required]

