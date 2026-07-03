#!/usr/bin/env python3
"""Spec 文档工具集。

聚合以下 Spec 相关功能：
  check      - 规格文档一致性检查（需求→任务覆盖、场景→检查点覆盖等）
  format     - Spec 文档标准化格式检查（章节完整性、验收标准、版本规范）
  gen-tests  - 从 spec.md 生成 pytest 测试骨架

用法：
  python spec-tool.py check [--spec-dir DIR] [--match-threshold N]
  python spec-tool.py format [--spec-dir DIR] [--check-all] [--format text|json|yaml] [-v]
  python spec-tool.py gen-tests [--spec DIR | --all] [--output FILE] [--output-dir DIR] [--dry-run]
"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.spec_tool.cli import main

if __name__ == "__main__":
    sys.exit(main())
