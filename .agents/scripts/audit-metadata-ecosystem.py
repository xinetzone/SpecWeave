#!/usr/bin/env python3
"""
元数据生态健康度审计工具。

从TOML侧反向校验元数据生态健康度，与check-frontmatter.py（MD侧正向检查）形成双向闭环。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.metadata_audit.cli import main

if __name__ == '__main__':
    main()

