"""发布入口：``python app.py``。

发布平台靠探测项目结构决定怎么启动，根目录的 ``app.py`` 是它识别的标准
形态之一。真正的逻辑在 :mod:`info_butler.asgi`，这里只做四件事：

1. 把 ``src`` 挂到 ``sys.path``——源码布局下平台未必会 ``pip install -e .``，
   少了这一步会直接 ImportError；
2. **确保前端构建产物存在**——平台上传目录时会排除「构建输出」，
   ``_build/`` 很可能被一并排除，于是线上只剩 API 没有页面。这里在启动前
   现场构建一次（产物已在则直接复用），保证页面一定在；
3. 读 ``PORT`` / ``HOST`` 环境变量（平台只暴露一个公网端口并注入 ``PORT``，
   绑死端口号会导致探活失败）；
4. 启动 uvicorn。

启动后同源提供前端站点与 API：``/`` 进工作台，``/api/*`` 是接口。
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.is_dir():
    sys.path.insert(0, str(SRC))

BUILD_DIR = ROOT / "_build" / "html"
DOC_DIR = ROOT / "doc"


def _ensure_frontend() -> None:
    """前端构建产物缺失时就地构建。

    刻意不在导入失败时崩溃——发布环境里 Sphinx 未必已安装，此时应退化为
    「有 API、无页面」并由 :mod:`info_butler.web` 给出说明页，而不是
    整个服务起不来（那等于线上什么都没有）。
    """
    if (BUILD_DIR / "index.html").is_file():
        return
    if not DOC_DIR.is_dir():
        return
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "html",
                "-d",
                str(ROOT / "_build" / "doctrees"),
                "--keep-going",
                str(DOC_DIR),
                str(BUILD_DIR),
            ],
            check=False,
            cwd=str(ROOT),
        )
    except OSError as exc:  # pragma: no cover - 环境缺 sphinx
        print(f"[info-butler] 前端构建跳过：{exc}", file=sys.stderr)


_ensure_frontend()

from info_butler.asgi import app  # noqa: E402  (须在 sys.path 调整与前端构建之后)


def main() -> None:
    import uvicorn

    host = (os.environ.get("HOST") or "0.0.0.0").strip()
    port = int((os.environ.get("PORT") or "8787").strip())
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
