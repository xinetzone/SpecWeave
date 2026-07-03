#!/usr/bin/env python3
"""阶段守卫运行时强制执行工具。

运行时实时拦截（操作前检查→拦截/放行→SG-LOG输出），
与离线分析工具 check-stage-guardrails.py 构成"运行时+离线"双层验证闭环。

用法: python check-stage-guardrail-runtime.py --demo|--check|--export-logs|--status
"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.stage_guardrail_runtime.cli import main

if __name__ == '__main__':
    sys.exit(main())
