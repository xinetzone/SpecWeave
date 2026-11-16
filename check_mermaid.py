#!/usr/bin/env python3
"""向后兼容入口：根目录 check_mermaid.py → .agents/scripts/repo-check.py mermaid。

历史：本脚本最初硬编码 wsl-wiki 四个文件的绝对路径（.agents/docs/...，该目录
已于 2026-08-31 整体迁移废止），目标文件迁移后无参运行即 FileNotFoundError。
2026-11-16 起改为委托包装，保留 `python check_mermaid.py` 入口与全部参数转发，
实际检查逻辑统一收敛到受测试覆盖的 repo-check mermaid 子命令；
通用包装见 .agents/scripts/check-mermaid.py。
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / ".agents" / "scripts" / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import os
import subprocess
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parent
    target = repo_root / ".agents" / "scripts" / "repo-check.py"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    args = [sys.executable, "-X", "utf8", str(target), "mermaid"] + sys.argv[1:]
    sys.exit(subprocess.run(args, env=env).returncode)


if __name__ == "__main__":
    main()
