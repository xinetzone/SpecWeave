"""微信文章页 HTML 解析与转换（纯函数层，无网络/无 IO 副作用）。

边界契约（来源：微信公开文章页结构，方案文档 R2 边界标记法）：
- 正文容器为 ``<div id="js_content">``；容器外的导航/脚本/样式均不归档。
- 正文图片使用懒加载：真实地址在 ``data-src``，``src`` 常为占位 ``data:`` URI。
- 以下页面文案与结构为经验值（2025-2026 公开样本），真实实测发现偏差时在
  ``_PAGE_MARKERS`` 校准：删除页、违规拦截页、环境异常（风控验证）页。
"""

from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

from ..exceptions import PayloadError

CONTENT_SELECTOR = "#js_content"

# 页面状态标记（经验值，待真实样本校准）
_PAGE_MARKERS = {
    "deleted": ("该内容已被发布者删除", "此内容已被发布者删除", "内容已被删除"),
    "violation": ("此内容因违规无法查看", "由用户投诉并经平台审核"),
    "risk": ("环境异常", "请在微信客户端打开链接", "去验证", "完成验证后即可继续访问"),
}

_EXT_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}
_EXT_BY_WX_FMT = {
    "jpeg": ".jpg",
    "jpg": ".jpg",
    "png": ".png",
    "gif": ".gif",
    "webp": ".webp",
    "svg": ".svg",
}


class PageUnavailableError(PayloadError):
    """正文不可归档：kind 为 deleted / violation（标记 skipped）或 risk（标记 failed）。"""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


_SUBSTANTIAL_MEDIA_TAGS = (
    "img", "video", "iframe", "mpvoice", "mp-common-videosnap",
)


def _has_substantial_content(content) -> bool:
    """正文容器是否含有实质内容（非空文本或媒体节点）。"""
    if content.get_text(strip=True):
        return True
    return any(content.find(tag) is not None for tag in _SUBSTANTIAL_MEDIA_TAGS)


def classify_page(raw_html: str) -> str:
    """返回页面状态：ok / deleted / violation / risk。

    判定以**页面结构**为准，而非对整页 HTML 做子串匹配——风控标记词
    （如"去验证""环境异常"）可能恰好出现在正常文章正文中，全文匹配会
    误判并触发批次熔断。规则：

    - 正文容器 ``#js_content`` 存在且含实质内容（文本/媒体节点）→ ``ok``，
      即使正文本身引用了这些词；
    - 容器缺失或为空时，只在**容器之外**的页面文本中查找拦截页标记；
    - 容器缺失/为空又查不到任何标记 → ``risk``（疑似改版后的未知验证页，
      由批次熔断保护，可凭日志人工复核后 ``--include-failed``）。
    """
    page = BeautifulSoup(raw_html, "html.parser")
    for tag in page.find_all(["script", "style"]):
        tag.decompose()
    content = page.select_one(CONTENT_SELECTOR)
    if content is not None and _has_substantial_content(content):
        return "ok"
    if content is not None:
        content.extract()
    outside_text = page.get_text(" ", strip=True)
    for kind, markers in _PAGE_MARKERS.items():
        if any(marker in outside_text for marker in markers):
            return kind
    return "risk"


def extract_content_soup(raw_html: str) -> BeautifulSoup:
    """从完整文章页提取正文容器；页面异常或容器缺失时抛出。

    注意：必须在 :func:`classify_page` 判为 ok 后调用本函数。
    """
    page = BeautifulSoup(raw_html, "html.parser")
    content = page.select_one(CONTENT_SELECTOR)
    if content is None:
        raise PageUnavailableError(
            "risk", f"正文容器 {CONTENT_SELECTOR} 缺失（可能是风控验证页或页面结构变更）"
        )
    return content


def collect_image_urls(content: BeautifulSoup) -> list[str]:
    """收集正文内全部图片真实地址（去重保序）。

    - ``data-src`` 优先（微信懒加载），其次 ``src``；
    - 过滤 ``data:`` 占位、相对地址与空白值；
    - 同一 URL 在文中多处出现只下载一次。
    """
    seen: set[str] = set()
    urls: list[str] = []
    for img in content.find_all("img"):
        candidate = (img.get("data-src") or img.get("src") or "").strip()
        if not candidate or candidate.startswith("data:"):
            continue
        if not candidate.startswith(("http://", "https://")):
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        urls.append(candidate)
    return urls


def localize_image(content: BeautifulSoup, url: str, relative_path: str) -> None:
    """把正文中引用 ``url`` 的 img 标签改写为本地相对路径。

    匹配（data-src 或 src 任一）后两个属性统一写为本地路径：微信页面常出现
    仅有 data-src 而无 src 的节点，或 src 为 data: 占位，必须双写才能保证
    离线 HTML 与 Markdown 都引用本地文件。
    """
    for img in content.find_all("img"):
        refs = {(img.get("data-src") or "").strip(), (img.get("src") or "").strip()}
        if url in refs:
            img["data-src"] = relative_path
            img["src"] = relative_path


def preserve_remote_image(content: BeautifulSoup, url: str) -> None:
    """图片下载失败时的兜底：让 src 指向远程真实地址（data-src 已是该地址）。

    微信懒加载页的 ``src`` 常是 data: 占位，不处理的话 Markdown/离线 HTML
    中该图既无法本地显示也无法在线回源；把 src 对齐远程 URL 后保留在线可用性。
    """
    for img in content.find_all("img"):
        if (img.get("data-src") or "").strip() == url:
            img["src"] = url


def drop_placeholder_images(content: BeautifulSoup) -> int:
    """移除无真实地址的懒加载占位 img（data: 或空 src/data-src），返回移除数。

    归档流程中真实图片已在本地化/远程兜底两步处理完毕，剩余的纯占位节点
    对阅读与 RAG 均无价值，直接删除。
    """
    removed = 0
    for img in content.find_all("img"):
        candidate = (img.get("data-src") or img.get("src") or "").strip()
        if not candidate or candidate.startswith("data:"):
            img.decompose()
            removed += 1
    return removed


def _code_language(element) -> str:
    """提取围栏语言：markdownify 回调作用于 ``<pre>``，语言类通常在内层 ``<code>``。"""
    target = element
    if hasattr(element, "find"):
        inner_code = element.find("code")
        if inner_code is not None:
            target = inner_code
    classes = target.get("class", []) if hasattr(target, "get") else []
    for cls in classes:
        if cls.startswith("language-"):
            return cls.removeprefix("language-")
    return ""


def guess_image_ext(url: str, content_type: str | None) -> str:
    """推断图片扩展名：URL 的 wx_fmt 参数 → Content-Type → 默认 .jpg。"""
    query = parse_qs(urlsplit(url).query)
    wx_fmt = (query.get("wx_fmt") or [""])[0].lower()
    if wx_fmt in _EXT_BY_WX_FMT:
        return _EXT_BY_WX_FMT[wx_fmt]
    if content_type:
        mime = content_type.split(";", 1)[0].strip().lower()
        if mime in _EXT_BY_CONTENT_TYPE:
            return _EXT_BY_CONTENT_TYPE[mime]
    return ".jpg"


def content_to_markdown(content: BeautifulSoup) -> str:
    """正文 DOM → Markdown（ATX 标题、短横线列表、围栏代码块、引用块）。

    延迟导入 markdownify：仅在正文归档时需要该依赖。
    """
    from markdownify import MarkdownConverter

    converter = MarkdownConverter(
        heading_style="ATX",
        bullets="-",
        code_language_callback=_code_language,
        strip=["script", "style"],
    )
    markdown = converter.convert_soup(content)
    # 收敛微信页面常见的 3+ 连续空行；去掉首尾空白
    lines: list[str] = []
    blank = 0
    for line in markdown.splitlines():
        if line.strip():
            blank = 0
            lines.append(line.rstrip())
        else:
            blank += 1
            if blank <= 1:
                lines.append("")
    return "\n".join(lines).strip() + "\n"
