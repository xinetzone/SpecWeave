---
id: "three-tier-check-tool"
source: "external: 不存在-docs/retrospective/knowledge-extraction.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/three-tier-check-tool.toml"
---
> **来源**：从 `docs/retrospective/knowledge-extraction.md` 一、可复用代码模式 拆分

# 三段式检查工具架构

## 来源
`check-spec-consistency.py`、`check-gitignore.py`

## 模式
```
输入层（解析器）→ 检查引擎（校验逻辑）→ 输出层（报告渲染）
```

## 代码骨架
```python
#!/usr/bin/env python3
"""工具描述。"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ============================================================================
# ANSI 颜色代码（可复用）
# ============================================================================
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# ============================================================================
# 工具函数
# ============================================================================
# 纯函数，无副作用，可独立测试

# ============================================================================
# 解析器（输入层）
# ============================================================================
def parse_xxx(filepath: Path) -> dict[str, Any]:
    """解析输入文件，返回结构化数据。"""
    ...

# ============================================================================
# 检查引擎
# ============================================================================
def check_xxx(data: dict) -> dict[str, Any]:
    """执行检查逻辑，返回结构化结果。"""
    ...

# ============================================================================
# 输出模块
# ============================================================================
def generate_terminal_report(data: dict) -> None:
    """终端彩色输出。"""
    ...

def generate_json_report(data: dict) -> str:
    """JSON 格式输出。"""
    ...

# ============================================================================
# 主流程
# ============================================================================
def main() -> int:
    parser = argparse.ArgumentParser(description="工具描述")
    parser.add_argument("--input", type=str, help="输入路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()
    # 解析 → 检查 → 输出
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

## 复用场景
任何需要"解析输入→校验逻辑→输出报告"的命令行工具。

> **关联模块**：
> - `patterns/code-patterns/context-aware-path-resolution.md`
> - `patterns/architecture-patterns/perception-check-report-model.md`