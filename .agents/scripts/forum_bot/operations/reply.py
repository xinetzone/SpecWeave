"""forum-bot 发布回复操作。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..auth import check_login
from ..browser import create_context, fill_textarea, safe_navigate, wait_for_selector, _import_pw
from ..constants import ANSI_YELLOW, DEFAULT_WAIT, FORUM_URL, STATE_FILE
from ..content import ensure_ai_notice
from ..logger import (
    _color, delay, fail, gate_fail, gate_ok, header, logger, ok, step, warn,
)
from .drafts import clean_drafts

if TYPE_CHECKING:
    try:
        from playwright.sync_api import Page
    except ImportError:
        Page = Any


def _find_reply_open_button(page: "Page"):
    buttons = page.locator("button").all()
    logger.debug("  页面共有 %d 个button元素", len(buttons))
    for i, btn in enumerate(buttons):
        try:
            text = btn.inner_text().strip()
            cls = btn.get_attribute("class") or ""
            visible = btn.is_visible()
            if not visible:
                continue
            if text == "回复" and "create" not in cls:
                logger.debug("  找到打开回复按钮: button[%d] text='%s' class='%s'", i, text, cls[:60])
                return btn
        except Exception as e:
            logger.debug("  button[%d] 检查异常: %s", i, e)
    return None


def _find_reply_submit_button(page: "Page"):
    candidates = [
        (page.locator("button.btn-primary.create").filter(has_text="回复").first, "button.btn-primary.create:has-text('回复')"),
        (page.get_by_role("button", name="回复").last, "role=button name='回复' (last)"),
    ]
    for loc, desc in candidates:
        try:
            if loc.is_visible(timeout=2000):
                cls = loc.get_attribute("class") or ""
                logger.debug("  提交按钮候选: %s class='%s'", desc, cls[:60])
                if "create" in cls:
                    gate_ok(f"找到回复提交按钮: {desc}")
                    return loc
        except Exception:
            continue
    for loc, desc in candidates:
        try:
            if loc.is_visible(timeout=1000):
                gate_ok(f"找到回复提交按钮(兜底): {desc}")
                return loc
        except Exception:
            continue
    return None


def do_reply(
    topic_id: int,
    content: str | None = None,
    content_file: str | None = None,
    dry_run: bool = False,
    headless: bool = False,
    debug: bool = False,
    add_notice: bool = True,
) -> None:
    """发布回复。"""
    sync_playwright, _ = _import_pw()
    action = "发布回复（试运行）" if dry_run else f"发布回复到帖子 #{topic_id}"
    header(action)

    if content_file:
        step(f"从文件读取回复: {content_file}")
        try:
            reply_content = Path(content_file).read_text(encoding="utf-8")
            gate_ok(f"文件读取成功 ({len(reply_content)} 字符)")
        except OSError as e:
            fail(f"读取文件失败: {e}")
            return
    elif content:
        reply_content = content
        logger.info("使用指定的回复内容 (%d 字符)", len(reply_content))
    else:
        fail("必须指定 --content 或 --file")
        return

    if add_notice:
        step("检查并添加AI发布声明")
        reply_content, notice_added = ensure_ai_notice(reply_content)
        if notice_added:
            ok("已自动添加AI发布声明")
        else:
            gate_ok("AI声明已存在，跳过")

    with sync_playwright() as p:
        browser, context = create_context(p, headless=headless)
        page = context.new_page()

        url = f"{FORUM_URL}/t/topic/{topic_id}"
        if not safe_navigate(page, url, "目标帖子"):
            fail("导航失败，终止回复")
            browser.close()
            return

        if not check_login(page):
            fail("未登录，终止回复")
            browser.close()
            return

        safe_navigate(page, url, "重新加载帖子")

        step("滚动到页面底部")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        scroll_y = page.evaluate("window.scrollY")
        scroll_h = page.evaluate("document.body.scrollHeight")
        logger.debug("  滚动位置: scrollY=%d, scrollHeight=%d", scroll_y, scroll_h)

        if dry_run:
            logger.info("[DRY-RUN] 回复内容预览:")
            print(f"\n  {_color('[DRY-RUN] 将要发布的回复:', ANSI_YELLOW)}")
            preview = reply_content[:500] + ("..." if len(reply_content) > 500 else "")
            for line in preview.split("\n")[:20]:
                print(f"    {line}")
            ok("试运行完成，未实际提交")
            browser.close()
            return

        step("1/4 打开回复编辑器")
        open_btn = _find_reply_open_button(page)
        if open_btn:
            open_btn.click()
            gate_ok("回复按钮已点击")
        else:
            warn("未找到精确的回复按钮，尝试get_by_role兜底")
            try:
                page.get_by_role("button", name="回复").first.click(timeout=5000)
                gate_ok("兜底方式点击回复按钮成功")
            except Exception as e:
                fail(f"点击回复按钮失败: {e}")
                browser.close()
                return
        page.wait_for_timeout(DEFAULT_WAIT)

        step("2/4 填写回复内容")
        ta = None
        all_tas = page.locator("textarea.d-editor-input").all()
        logger.debug("  找到 %d 个 textarea.d-editor-input", len(all_tas))
        if all_tas:
            for candidate in reversed(all_tas):
                try:
                    if candidate.is_visible(timeout=2000):
                        ta = candidate
                        gate_ok("选择了最后一个可见编辑器")
                        break
                except Exception:
                    continue

        if ta is None:
            fail("未找到回复编辑器textarea")
            if debug:
                shot_path = STATE_FILE.parent / f"reply-fail-{topic_id}-{int(time.time())}.png"
                page.screenshot(path=str(shot_path))
                logger.info("  📸 已截图保存: %s", shot_path)
            browser.close()
            return

        if not fill_textarea(page, "textarea.d-editor-input", reply_content, "回复编辑器"):
            try:
                ta.fill(reply_content)
                ta.dispatch_event("input")
                gate_ok("兜底方式填写内容成功")
            except Exception as e:
                fail(f"填写回复内容失败: {e}")
                browser.close()
                return

        delay(reason="Discourse回复防抖")

        step("3/4 提交回复")
        submit_btn = _find_reply_submit_button(page)
        if submit_btn is None:
            fail("未找到回复提交按钮")
            browser.close()
            return
        submit_btn.click()
        gate_ok("回复提交按钮已点击")
        page.wait_for_timeout(3000)
        logger.debug("  提交后URL: %s", page.url)

        step("4/4 验证回复结果")
        last_url = f"{url}/last"
        safe_navigate(page, last_url, "帖子最后一页")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

        posts_count = page.locator(".cooked").count()
        logger.debug("  页面共有 %d 条帖子内容", posts_count)

        ok("回复已提交，已导航到帖子最后一页，请检查内容是否正确")

        step("清理自动保存的草稿")
        draft_count = clean_drafts(page, verbose=False)
        if draft_count > 0:
            logger.info("  已自动清理 %d 个草稿", draft_count)

        browser.close()
