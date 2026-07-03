"""forum-bot 认证与登录管理。

提供登录状态检测、用户名提取、首次登录流程。
Playwright通过browser模块延迟导入。
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from .constants import ANSI_BOLD, ANSI_YELLOW, DEFAULT_WAIT, FORUM_URL, STATE_FILE
from .browser import create_context, safe_navigate, _import_pw
from .logger import _color, fail, gate_fail, gate_ok, header, logger, ok, step

if TYPE_CHECKING:
    try:
        from playwright.sync_api import Page
    except ImportError:
        Page = Any


def _get_current_username(page: "Page") -> str | None:
    """从页面中获取当前登录用户名。多信号组合检测。"""
    logger.debug("  🔐 检测当前登录用户名...")

    def _extract_username() -> str | None:
        username = page.evaluate(r"""() => {
            const results = {};
            try {
                if (window.Discourse && window.Discourse.User && window.Discourse.User.current) {
                    const u = window.Discourse.User.current();
                    if (u && u.username) results.discourse_global = u.username;
                }
            } catch(e) { results.discourse_global_err = e.message; }
            const meta = document.querySelector('meta[name="discourse-current-username"]');
            if (meta && meta.content) results.meta_tag = meta.content;
            const avatar = document.querySelector('a[href^="/u/"]');
            if (avatar) {
                const href = avatar.getAttribute('href') || '';
                const match = href.match(/\/u\/([^\/\?#]+)/);
                if (match) results.avatar_link = match[1];
            }
            const userBtn = document.querySelector('.current-user .username, [data-user-id] .username, .user-menu .username');
            if (userBtn && userBtn.textContent) results.user_menu = userBtn.textContent.trim();
            results.has_login_btn = !!Array.from(document.querySelectorAll('a,button'))
                .find(el => (el.textContent||'').includes('登录') || (el.textContent||'').includes('Log In'));
            return results;
        }""")
        logger.debug("  🔍 用户名检测结果: %s", json.dumps(username or {}, ensure_ascii=False))
        if not username:
            return None
        for key in ("discourse_global", "meta_tag", "avatar_link", "user_menu"):
            if key in username and username[key]:
                gate_ok(f"通过 {key} 检测到用户名: {username[key]}")
                return username[key]
        if username.get("has_login_btn"):
            gate_fail("页面包含'登录'按钮，确认未登录")
        else:
            gate_fail("未能从任何信号源获取用户名")
        return None

    current_url = page.url
    if current_url.startswith(FORUM_URL):
        logger.debug("  当前在论坛域名下 (%s)，先尝试直接检测", current_url[:80])
        page.wait_for_timeout(1000)
        result = _extract_username()
        if result:
            return result
        logger.debug("  当前页面检测失败，导航到首页重试")

    try:
        page.goto(FORUM_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(DEFAULT_WAIT)
    except Exception as e:
        gate_fail(f"导航到首页失败: {e}")
        return None

    logger.debug("  📄 已加载首页, 标题: %s, URL: %s", page.title(), page.url)
    if "/login" in page.url:
        gate_fail("当前URL包含/login，未登录")
        return None

    return _extract_username()


def check_login(page: "Page") -> bool:
    """检查是否已登录论坛（多信号组合判断）。"""
    step("检查登录状态")
    saved_url = page.url
    username = _get_current_username(page)
    if username is None and page.url != saved_url and saved_url.startswith(FORUM_URL):
        logger.debug("  🔄 登录检测导致页面跳转，恢复到: %s", saved_url[:80])
        try:
            page.goto(saved_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(DEFAULT_WAIT)
        except Exception as e:
            logger.debug("  恢复URL失败: %s", e)
    if username:
        ok(f"已登录为: {username}")
        return True
    fail("未检测到登录状态")
    return False


def do_login(headless: bool = False, debug: bool = False) -> None:
    """首次登录：打开有头浏览器，用户手动登录后保存状态。"""
    sync_playwright, _ = _import_pw()
    header("首次登录")
    with sync_playwright() as p:
        browser, context = create_context(p, headless=False)
        page = context.new_page()

        if not safe_navigate(page, FORUM_URL, "论坛首页"):
            fail("无法访问论坛首页")
            browser.close()
            return

        print(_color("\n  请在浏览器中手动登录 forum.trae.cn", ANSI_BOLD))
        print(_color("  登录完成后，回到终端按 Enter 保存登录状态...\n", ANSI_YELLOW))
        logger.info("等待用户手动登录...")
        input("  按 Enter 继续...")

        step("验证登录结果")
        username = _get_current_username(page)
        if username:
            context.storage_state(path=str(STATE_FILE))
            ok(f"登录成功！用户: {username}")
            ok(f"状态已保存到: {STATE_FILE}")
            logger.info("  💾 状态文件大小: %d bytes", STATE_FILE.stat().st_size)
        else:
            fail("登录似乎未成功，请重试（检查是否显示了用户名头像）")

        browser.close()
