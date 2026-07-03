"""Jest测试骨架生成器子包。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用

为Web API Profile生成Jest测试文件（JavaScript/TypeScript）。
"""

from .generator import JestGenerator
from .context import _TestContext

__all__ = ["JestGenerator"]
