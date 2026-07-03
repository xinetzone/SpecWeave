"""forum-bot 浏览器自动化原语。

封装Playwright浏览器上下文创建、导航、元素等待、点击、填写等基础操作。
Playwright在实际使用时延迟导入，避免非浏览器操作（如--help）因依赖缺失而失败。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .constants import (
    DEFAULT_WAIT, ELEMENT_TIMEOUT, FORUM_URL, RETRY_MAX, STATE_FILE,
)
from .logger import (
    delay, ensure_state_dir, gate_fail, gate_ok, logger, retry_log, step, warn,
)

if TYPE_CHECKING:
    try:
        from playwright.sync_api import Browser, BrowserContext, Page, TimeoutError as PWTimeout
    except ImportError:
        Browser = Any
        BrowserContext = Any
        Page = Any
        PWTimeout = Exception


def _import_pw():
    """延迟导入Playwright，首次调用时检查依赖。"""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
        return sync_playwright, PWTimeout
    except ImportError:
        import sys
        print("[FAIL] 请先安装 Playwright: pip install playwright && playwright install chromium")
        sys.exit(1)


def safe_navigate(page: "Page", url: str, label: str = "页面") -> bool:
    """安全导航到URL，带超时和错误处理。"""
    _, PWTimeout = _import_pw()
    step(f"导航到{label}: {url}")
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if resp is None:
            gate_fail(f"导航返回None（页面可能由JS控制）")
            page.wait_for_timeout(DEFAULT_WAIT)
            return True
        status = resp.status
        if status >= 400:
            gate_fail(f"HTTP {status} - {resp.status_text}")
            return False
        gate_ok(f"导航成功 HTTP {status}")
        page.wait_for_timeout(DEFAULT_WAIT)
        logger.debug("  📄 页面标题: %s | URL: %s", page.title(), page.url)
        return True
    except PWTimeout:
        gate_fail(f"导航超时 (30s)")
        return False
    except Exception as e:
        gate_fail(f"导航异常: {type(e).__name__}: {e}")
        return False


def wait_for_selector(page: "Page", selector: str, label: str = "", timeout: int = ELEMENT_TIMEOUT) -> bool:
    """等待元素出现，返回是否可见。门禁条件封装。"""
    _, PWTimeout = _import_pw()
    desc = label or selector
    logger.debug("  🔍 等待元素: %s (超时 %dms)", desc, timeout)
    try:
        loc = page.locator(selector).first
        loc.wait_for(state="visible", timeout=timeout)
        gate_ok(f"元素已出现: {desc}")
        return True
    except PWTimeout:
        count = page.locator(selector).count()
        gate_fail(f"等待超时: {desc} (DOM中匹配数: {count})")
        return False


def click_with_retry(page: "Page", selector: str, label: str = "", retries: int = RETRY_MAX) -> bool:
    """点击元素，失败时重试（含滚动到视图、JS click兜底）。"""
    _, PWTimeout = _import_pw()
    desc = label or selector
    for attempt in range(1, retries + 1):
        logger.debug("  🖱️  点击尝试 %d/%d: %s", attempt, retries, desc)
        try:
            loc = page.locator(selector).first
            if not loc.is_visible():
                gate_fail(f"元素不可见: {desc}")
                if attempt < retries:
                    retry_log(attempt, retries, "滚动到视图后重试")
                    loc.scroll_into_view_if_needed(timeout=3000)
                    page.wait_for_timeout(500)
                    continue
                return False
            loc.click(timeout=5000)
            gate_ok(f"点击成功: {desc}")
            return True
        except PWTimeout:
            gate_fail(f"点击超时: {desc}")
        except Exception as e:
            gate_fail(f"点击异常: {type(e).__name__}: {e}")
            if attempt < retries:
                retry_log(attempt, retries, "JS click兜底")
                try:
                    page.evaluate(f"document.querySelector('{selector}').click()")
                    gate_ok(f"JS click兜底成功: {desc}")
                    return True
                except Exception as e2:
                    gate_fail(f"JS click也失败: {e2}")
        if attempt < retries:
            page.wait_for_timeout(1000)
    return False


def fill_textarea(page: "Page", selector: str, content: str, label: str = "编辑器") -> bool:
    """填写textarea内容并触发input/change事件。"""
    step(f"填写{label}内容 ({len(content)} 字符)")
    try:
        ta = page.locator(selector).first
        if not ta.is_visible():
            gate_fail(f"{label}不可见: {selector}")
            return False
        ta.fill(content)
        ta.dispatch_event("input")
        ta.dispatch_event("change")
        page.wait_for_timeout(500)
        actual = ta.input_value()
        if len(actual) != len(content):
            gate_fail(f"内容长度不匹配: 期望 {len(content)}, 实际 {len(actual)}")
            return False
        gate_ok(f"内容填写成功 (实际长度: {len(actual)})")
        logger.debug("  📝 内容前80字符: %s", content[:80].replace("\n", "\\n"))
        return True
    except Exception as e:
        gate_fail(f"填写内容异常: {type(e).__name__}: {e}")
        return False


def _attach_network_logging(context: "BrowserContext") -> None:
    """为浏览器上下文附加网络请求日志（过滤静态资源）。"""
    def _should_log(url: str) -> bool:
        skip_ext = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".ico")
        return not any(url.split("?")[0].endswith(ext) for ext in skip_ext)

    context.on("request", lambda req: (
        logger.debug("  📤 %s %s", req.method, req.url[:120])
        if _should_log(req.url) else None
    ))
    context.on("response", lambda resp: (
        logger.debug("  📥 %d %s", resp.status, resp.url[:120])
        if resp.status >= 400 or _should_log(resp.url) else None
    ))


def create_context(playwright, headless: bool = False) -> tuple["Browser", "BrowserContext"]:
    """创建浏览器上下文，优先复用已保存的登录状态。"""
    step("创建浏览器上下文")
    ensure_state_dir()

    logger.debug("  🔧 启动 Chromium (headless=%s)", headless)
    browser = playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )
    logger.debug("  ✅ 浏览器已启动")

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    viewport = {"width": 1280, "height": 900}

    if STATE_FILE.exists():
        logger.info("  📂 复用登录状态: %s (大小: %d bytes)", STATE_FILE, STATE_FILE.stat().st_size)
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                storage_state = json.load(f)
            cookies_count = len(storage_state.get("cookies", []))
            origins_count = len(storage_state.get("origins", []))
            logger.debug("  🍪 状态文件包含 %d 个cookies, %d 个origin存储", cookies_count, origins_count)
        except (json.JSONDecodeError, OSError) as e:
            warn(f"状态文件损坏 ({e})，将创建新会话")
            storage_state = None
        else:
            context = browser.new_context(
                storage_state=storage_state,
                viewport=viewport,
                user_agent=user_agent,
            )
            gate_ok("已加载持久化登录状态")
            _attach_network_logging(context)
            return browser, context

    logger.info("  🆕 创建新的浏览器上下文（无保存状态）")
    context = browser.new_context(viewport=viewport, user_agent=user_agent)
    _attach_network_logging(context)
    return browser, context
