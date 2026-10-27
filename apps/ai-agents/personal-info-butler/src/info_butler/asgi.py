"""ASGI 入口：``info_butler.web:app``。

发布平台（以及 uvicorn 的 ``--factory`` 之外的用法）需要一个模块级可调用
对象。放在这里而不是在 ``api.py``，是因为「同源带前端」是**发布形态**的
选择，而 ``api.py`` 是纯 API 层——本地开发者只调 API 时不必先构建站点。

监听地址与端口由**环境变量**决定（``PORT`` / ``HOST``）：发布平台只暴露
一个公网端口并通过 ``PORT`` 注入，绑死 8787 会导致平台探活失败。
"""

import os

from .web import create_web_app

app = create_web_app()


def main() -> None:  # pragma: no cover - 容器入口
    """以平台约定的方式启动服务。"""
    import uvicorn

    host = (os.environ.get("HOST") or "0.0.0.0").strip()
    port = int((os.environ.get("PORT") or "8787").strip())
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":  # pragma: no cover
    main()
