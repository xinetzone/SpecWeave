"""支持 python -m lib.link_fixer 调用方式。"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from .cli import main

if __name__ == "__main__":
    main()

