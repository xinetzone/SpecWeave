"""前端静态资产（web dist）的同源托管。

T2 约定的「资产目录常量 + 缺失时的启动报错文案」在此落地，并实现 T19 的托管语义。

upstream: ``packages/md-cli/server.js:48`` 仅 ``express.static(public)``，其余路径反代
线上站点（``server.js:83-93``）；本仓为自托管形态，改为同源托管 T2 构建的 dist
（SPA 回退 + 哈希资产长缓存，AC-14），属 spec 新增契约（差异登记 T21）。
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, Response

# 构建产物目录常量（scripts/build-web-dist.* 的输出目标；.gitignore 仅放行
# .gitkeep / MANIFEST.sha256 / NOTICE，故 fresh clone 下 dist 不存在）
WEB_DIST_DIR: Path = Path(__file__).resolve().parents[1] / "assets" / "web-dist"

INDEX_FILENAME = "index.html"
# Vite 构建（base=/）把带内容哈希的 JS/CSS 放在 static/ 下
HASHED_ASSET_PREFIX = "static/"
# 哈希资产不可变长缓存（1 年）；其余静态文件（favicon/图片）1 小时；首页禁缓存
HASHED_ASSET_CACHE_CONTROL = "public, max-age=31536000, immutable"
STATIC_ASSET_CACHE_CONTROL = "public, max-age=3600"
INDEX_CACHE_CONTROL = "no-cache"


def web_dist_ready(dist_dir: Path = WEB_DIST_DIR) -> bool:
    """dist 就绪判定：以 index.html 是否存在为准。"""
    return (Path(dist_dir) / INDEX_FILENAME).is_file()


def web_dist_missing_message(dist_dir: Path = WEB_DIST_DIR) -> str:
    """T2 约定的启动报错文案（dist 缺失时输出到 stderr）。"""
    return (
        f"前端静态资产缺失：{Path(dist_dir) / INDEX_FILENAME}\n"
        "请先执行 scripts/build-web-dist.ps1（WSL + podman node:22-alpine）构建 dist；"
        "构建流程与回退预案见应用文档 docs/build-web-dist.md。"
    )


def _cache_control_for(relative: str) -> str:
    if relative.startswith(HASHED_ASSET_PREFIX):
        return HASHED_ASSET_CACHE_CONTROL
    if relative == INDEX_FILENAME:
        return INDEX_CACHE_CONTROL
    return STATIC_ASSET_CACHE_CONTROL


def _has_extension(relative: str) -> bool:
    return "." in relative.rsplit("/", 1)[-1]


def register_web_dist(app: FastAPI, dist_dir: Path = WEB_DIST_DIR) -> None:
    """把 dist 托管到 ``app``。

    必须在全部 API 路由之后调用：SPA 回退是兜底路由，注册在前会遮蔽真实 API
    路由（如 ``/s/<id>`` 的正常 404 语义就来自路由本身而非回退）。
    """
    root = Path(dist_dir).resolve()
    index_file = root / INDEX_FILENAME

    @app.api_route("/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_web_dist(path: str) -> Response:
        relative = path.replace("\\", "/").lstrip("/")
        try:
            candidate = (root / relative).resolve()
        except (ValueError, OSError):
            return Response(status_code=404)
        if relative and candidate.is_relative_to(root) and candidate.is_file():
            return FileResponse(
                candidate, headers={"Cache-Control": _cache_control_for(relative)}
            )
        # SPA 回退：无扩展名的未命中路由回退首页；带扩展名视为缺失资产返 404
        if relative and _has_extension(relative):
            return Response(status_code=404)
        return FileResponse(index_file, headers={"Cache-Control": INDEX_CACHE_CONTROL})
