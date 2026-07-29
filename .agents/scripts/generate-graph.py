#!/usr/bin/env python3
"""通用知识图谱生成器命令行入口。通过TOML配置从Markdown文档集生成交互式HTML知识图谱。

用法:
    python generate-graph.py --config <config.toml>
    python generate-graph.py --config <config.toml> --output <output.html>
    python generate-graph.py --config <config.toml> --input-dir <dir> --json-output <data.json>
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

from lib.knowledge_graph_core import main

if __name__ == "__main__":
    sys.exit(main())
