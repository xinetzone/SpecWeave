#!/usr/bin/env python3
"""把 xmnn wheel 的打包工具链与 19 个核心运行时依赖装入 base env（cp314 GIL）。

单一事实源：运行时依赖直接读 /opt/xmnn-builder/pyproject.toml 的
[project].dependencies，禁止在 Containerfile 重复维护一份清单。
在叠加镜像构建期以 /opt/conda/bin/python 调用。
"""

import subprocess
import sys
import tomllib
from pathlib import Path

PYPROJECT = Path("/opt/xmnn-builder/pyproject.toml")

# 打包工具链（不进入 wheel 元数据，仅镜像内需要）
BUILD_TOOLS = [
    "nuitka==4.1.3",
    "scikit-build-core>=0.10",
    "build>=1.0",
    "wheel",
    "invoke>=2.0",
    "ipykernel",
]


def main() -> int:
    meta = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    deps = list(meta["project"]["dependencies"])
    print(f"[xmnn] installing {len(BUILD_TOOLS)} build tools + "
          f"{len(deps)} runtime deps into {sys.prefix}")
    cmd = [
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        *BUILD_TOOLS, *deps,
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
