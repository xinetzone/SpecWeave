"""forum-bot 草稿管理操作。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..auth import _get_current_username, check_login
from ..browser import create_context, safe_navigate, _import_pw
from ..constants import DEFAULT_WAIT, FORUM_URL
from ..logger import fail, gate_ok, header, logger, ok, step

if TYPE_CHECKING:
    try:
        from playwright.sync_api import Page
    except ImportError:
        Page = Any


def clean_drafts(page: "Page", username: str | None = None, verbose: bool = True) -> int:
    """清理所有草稿，返回删除的草稿数量。"""
    if username is None:
        username = _get_current_username(page)
    if not username:
        from ..logger import warn
        warn("无法获取当前用户名，跳过草稿清理")
        return 0

    drafts_url = f"{FORUM_URL}/u/{username}/activity/drafts"
    logger.debug("  🗑️  访问草稿页: %s", drafts_url)
    page.goto(drafts_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(DEFAULT_WAIT)

    count = 0
    max_drafts = 20
    while count < max_drafts:
        remove_btns = page.locator(".remove-draft").all()
        visible_btns = [b for b in remove_btns if b.is_visible()]
        if not visible_btns:
            logger.debug("  🗑️  没有更多草稿按钮 (共删除 %d 个)", count)
            break

        logger.debug("  🗑️  发现 %d 个可见草稿，删除第 %d 个", len(visible_btns), count + 1)
        visible_btns[0].click()
        page.wait_for_timeout(1000)

        confirm_selectors = [
            "button:has-text('删除')",
            "button.btn-danger",
            "button.danger",
        ]
        confirmed = False
        for sel in confirm_selectors:
            try:
                confirm_btn = page.locator(sel).first
                if confirm_btn.is_visible(timeout=2000):
                    confirm_btn.click()
                    page.wait_for_timeout(1500)
                    count += 1
                    confirmed = True
                    logger.debug("  🗑️  已确认删除 (第 %d 个)", count)
                    break
            except Exception:
                continue

        if not confirmed:
            logger.debug("  🗑️  未找到确认删除按钮，停止清理")
            break

    if count > 0 and verbose:
        ok(f"已清理 {count} 个草稿")
    elif verbose:
        logger.debug("  没有需要清理的草稿")
    return count


def do_clean_drafts(headless: bool = True, debug: bool = False) -> None:
    """清理所有草稿。"""
    sync_playwright, _ = _import_pw()
    header("清理草稿")
    with sync_playwright() as p:
        browser, context = create_context(p, headless=headless)
        page = context.new_page()

        if not check_login(page):
            fail("未登录，请先运行 login 命令")
            browser.close()
            return

        username = _get_current_username(page)
        if not username:
            fail("无法获取用户名")
            browser.close()
            return

        drafts_url = f"{FORUM_URL}/u/{username}/activity/drafts"
        if not safe_navigate(page, drafts_url, f"草稿页 ({username})"):
            fail("无法访问草稿页")
            browser.close()
            return

        remove_btns = page.locator(".remove-draft").all()
        visible = [b for b in remove_btns if b.is_visible()]
        logger.debug("  初始检测到 %d 个可见草稿按钮", len(visible))

        if not visible:
            ok("没有需要清理的草稿")
            browser.close()
            return

        logger.info("发现 %d 个草稿，开始清理...", len(visible))
        count = clean_drafts(page, username=username, verbose=True)
        ok(f"清理完成，共删除 {count} 个草稿")

        browser.close()
