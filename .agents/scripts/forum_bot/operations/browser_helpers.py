"""forum-bot 共享浏览器操作辅助函数。"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from ..browser import create_context, safe_navigate
from ..constants import FORUM_URL
from ..logger import fail

if TYPE_CHECKING:
    try:
        from playwright.sync_api import Page
    except ImportError:
        Page = Any


def setup_browser_session(p, headless: bool = True):
    """在已有的 sync_playwright 实例中创建浏览器上下文。

    返回 (browser, context, page) 以供调用方管理浏览器生命周期。

    Args:
        p: sync_playwright() 实例。
        headless: 是否无头模式。

    Returns:
        (browser, context, page) 元组。
    """
    browser, context = create_context(p, headless=headless)
    page = context.new_page()
    return browser, context, page


def navigate_and_check_login(
    page: Page,
    topic_id: int,
    action_name: str = "操作",
) -> bool:
    """导航到指定帖子并检查登录状态。

    Args:
        page: Playwright Page 对象。
        topic_id: 帖子 ID。
        action_name: 操作名称，用于错误消息（如 "编辑"、"回复"）。

    Returns:
        True 表示导航和登录均成功，False 表示失败。
    """
    from ..auth import check_login

    url = f"{FORUM_URL}/t/topic/{topic_id}"
    if not safe_navigate(page, url, "目标帖子"):
        fail(f"导航失败，终止{action_name}")
        return False

    if not check_login(page):
        fail(f"未登录，终止{action_name}")
        return False

    return True