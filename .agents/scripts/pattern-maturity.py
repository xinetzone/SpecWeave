#!/usr/bin/env python3
"""模式成熟度统一工具。

聚合模式成熟度相关的五个功能：
  stats        - 成熟度分布统计报告
  scan-upgrades - 成熟度偏差扫描（识别待升级/异常模式）
  verify       - README 统计表一致性验证
  check-index  - patterns/ 索引一致性检查与修复
  check        - CI 检查模式（结构性验证）

合并自：pattern-maturity-stats.py、scan-maturity-upgrades.py、
       check-atomization-duplication.py --verify-stats、
       check-retrospective-index.py（patterns 索引部分）。
"""

import sys

from lib.pattern_maturity import main

if __name__ == '__main__':
    sys.exit(main())
