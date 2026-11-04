"""同源 Web 应用：API 与前端静态资源由**同一个** ASGI 服务提供。

## 为什么必须是单端口

发布平台只暴露**一个**公网端口。若前端静态站与后端 API 分处两处：

- 前端要跨域访问 API → 要配 CORS，而平台云服务要求 **Origin 精确匹配**，
  静态站域名与 API 域名不同即被判为非法来源；
- 前端要额外配置 API 基址，用户打开页面却连不上，只能靠手填；
- 混合内容：HTTPS 页面请求 HTTP API 会被浏览器直接拦截。

同源部署把三个问题一次消掉：页面与接口同域，无需 CORS，无需填基址，
浏览器也不会拦。

## 静态资源从哪来

前端是 Sphinx 站点，源码在 ``doc/``，构建产物在 ``_build/html``。本模块
按以下顺序找构建产物：

1. 环境变量 ``BUTLER_STATIC_DIR`` 显式指定；
2. 项目根下的 ``_build/html``（本地构建与容器内构建的常规位置）；
3. 找不到就返回一个**说明页**而不是空白页——空白页会让「部署成功」这件事
   看起来像「产品坏了」。
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .api import create_app
from .config import Settings
from .llm import LLMClient
from .store import Store

#: 站点入口页。Sphinx 把 ``doc/app.md`` 构建成 ``app.html``，那就是工作台。
WORKBENCH_PAGE = "app.html"

_MISSING_STATIC_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>个人信息管家 · 前端尚未构建</title>
<style>
 body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;
      padding:3rem 1.5rem;background:#fbfaf7;color:#2b2a28;line-height:1.7}
 main{max-width:42rem;margin:0 auto;background:#fff;padding:2rem 2.25rem;
      border:1px solid #e6e2da;border-radius:14px}
 h1{font-size:1.5rem;margin:0 0 1rem}
 code{background:#f2efe9;padding:.15rem .4rem;border-radius:5px;font-size:.92em}
 pre{background:#f2efe9;padding:1rem;border-radius:10px;overflow-x:auto}
</style>
</head>
<body><main>
<h1>前端尚未构建</h1>
<p>后端 API 已在运行，但 Sphinx 站点还没构建，所以没有页面可看。</p>
<p>在项目根目录执行：</p>
<pre>pip install -r requirements.txt
python -m sphinx -b html -d _build/doctrees --keep-going -W doc _build/html</pre>
<p>构建完成后刷新本页即可。接口自检：<code>GET /api/health</code></p>
</main></body></html>
"""


def resolve_static_dir(explicit: str | Path | None = None) -> Path | None:
    """定位 Sphinx 构建产物目录；找不到返回 ``None``。

    **显式指定的目录必须严格生效**：若调用方指名了目录却因内容不完整而
    被静默替换成默认目录，服务就会把 A 的请求内容从 B 里发出去——比
    直接报错更难排查。因此显式路径无效时返回 ``None``（走说明页），
    而不是偷偷换一个目录。
    """
    if explicit:
        candidate = Path(explicit)
        if candidate.is_dir() and (candidate / "index.html").is_file():
            return candidate
        return None

    env_dir = (os.environ.get("BUTLER_STATIC_DIR") or "").strip()
    if env_dir:
        candidate = Path(env_dir)
        if candidate.is_dir() and (candidate / "index.html").is_file():
            return candidate

    # src/info_butler/web.py → parents[2] 是项目根
    default = Path(__file__).resolve().parents[2] / "_build" / "html"
    if default.is_dir() and (default / "index.html").is_file():
        return default
    return None


def create_web_app(
    settings: Settings | None = None,
    store: Store | None = None,
    llm: LLMClient | None = None,
    static_dir: str | Path | None = None,
) -> FastAPI:
    """构建同源应用：API 路由 + 前端静态资源。

    路由顺序有意义——API 先注册，静态挂载在后，因此 ``/api/*`` 不会被
    静态资源处理器截走。
    """
    resolved = resolve_static_dir(static_dir)

    if resolved is None:
        # 没有前端也要给出可诊断的响应，而不是 404 谜语
        def _missing_static() -> HTMLResponse:
            return HTMLResponse(_MISSING_STATIC_HTML, status_code=200)

        return create_app(
            settings=settings, store=store, llm=llm, home_handler=_missing_static
        )

    # 首页直接进工作台——产品的主界面不该藏在「文档 → 工作台」两级之下。
    def _home():
        if (resolved / WORKBENCH_PAGE).is_file():
            return RedirectResponse(f"/{WORKBENCH_PAGE}")
        return RedirectResponse("/index.html")

    app = create_app(settings=settings, store=store, llm=llm, home_handler=_home)

    # 静态挂载放在最后：FastAPI 按注册顺序匹配，/api/* 与首页必须先于它命中
    app.mount(
        "/",
        StaticFiles(directory=str(resolved), html=True),
        name="butler-static",
    )
    return app
