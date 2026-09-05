#!/usr/bin/env python3
"""Spec 文档工具集。

聚合以下 Spec 相关功能：
  check      - 规格文档一致性与元数据检查
                 --meta-only: 只检查元数据（三件套/frontmatter/status）
                 默认: 内容一致性检查（需求→任务、场景→检查点等）
  format     - Spec 文档格式检查与自动修复
                 --fix-frontmatter: 自动修复 frontmatter（补全/归一化 status）
                 默认: 格式标准化检查
  gen-tests  - 从 spec.md 生成 pytest 测试骨架

用法：
  python spec-tool.py check [--meta-only] [--spec-dir DIR] [--json]
  python spec-tool.py format [--fix-frontmatter] [--dry-run] [--spec-dir DIR] [--json]
  python spec-tool.py gen-tests [--spec DIR | --all] [--output FILE] [--dry-run]

详细文档见 lib/spec_tool/README.md
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.spec_tool.cli import main

if __name__ == "__main__":
    sys.exit(main())

