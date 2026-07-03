"""forum-bot 读帖操作。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..auth import check_login
from ..browser import create_context, safe_navigate, wait_for_selector, _import_pw
from ..constants import ANSI_BOLD, FORUM_URL
from ..logger import _color, fail, gate_ok, header, logger, ok, step, warn

if TYPE_CHECKING:
    try:
        from playwright.sync_api import Page
    except ImportError:
        Page = Any


def do_read(topic_id: int, headless: bool = True, debug: bool = False) -> None:
    """读取帖子标题和正文。"""
    sync_playwright, PWTimeout = _import_pw()
    header(f"读取帖子 #{topic_id}")
    with sync_playwright() as p:
        browser, context = create_context(p, headless=headless)
        page = context.new_page()

        url = f"{FORUM_URL}/t/topic/{topic_id}"
        if not safe_navigate(page, url, "帖子页面"):
            fail("无法导航到帖子页面")
            browser.close()
            return

        logger.debug("  当前URL: %s", page.url)
        if "/login" in page.url or not check_login(page):
            fail("未登录，请先运行 login 命令")
            browser.close()
            return

        step("获取帖子标题")
        title = page.title().split(" - ")[0] if page.title() else "未知"
        logger.debug("  完整标题: %s", page.title())

        step("获取帖子正文")
        body_text = ""
        try:
            if not wait_for_selector(page, ".cooked", "正文区域 .cooked", timeout=5000):
                warn("正文区域未在预期时间内出现，尝试继续...")
            cooked = page.locator(".cooked").first
            body_text = cooked.inner_text(timeout=5000)
            gate_ok(f"正文获取成功 ({len(body_text)} 字符)")
        except PWTimeout:
            body_text = "(无法获取正文 - 超时)"
            fail("获取正文超时")
        except Exception as e:
            body_text = f"(获取正文异常: {type(e).__name__})"
            fail(f"获取正文异常: {e}")

        print(f"\n  {_color('标题:', ANSI_BOLD)} {title}")
        print(f"  {_color('正文预览:', ANSI_BOLD)}")
        preview = body_text[:500] + ("..." if len(body_text) > 500 else "")
        for line in preview.split("\n")[:20]:
            print(f"    {line}")

        ok(f"帖子读取完成 (正文长度: {len(body_text)} 字符)")
        logger.info("  📊 帖子 #%d: 标题=%s, 正文长度=%d", topic_id, title[:40], len(body_text))
        browser.close()
