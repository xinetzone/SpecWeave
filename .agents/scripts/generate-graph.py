#!/usr/bin/env python3
"""通用知识图谱生成器命令行入口。通过TOML配置从Markdown文档集生成交互式HTML知识图谱。

用法:
    python generate-graph.py --config <config.toml>
    python generate-graph.py --config <config.toml> --output <output.html>
    python generate-graph.py --config <config.toml> --input-dir <dir> --json-output <data.json>
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.knowledge_graph_core import main

if __name__ == "__main__":
    sys.exit(main())