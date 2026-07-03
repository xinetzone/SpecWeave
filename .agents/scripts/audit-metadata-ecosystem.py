#!/usr/bin/env python3
"""
元数据生态健康度审计工具。

从TOML侧反向校验元数据生态健康度，与check-frontmatter.py（MD侧正向检查）形成双向闭环。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.metadata_audit.cli import main

if __name__ == '__main__':
    main()
