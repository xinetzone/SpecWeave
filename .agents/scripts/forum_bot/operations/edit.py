"""forum-bot 编辑帖子操作。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..auth import check_login
from ..browser import (
    create_context, fill_textarea, safe_navigate, wait_for_selector, _import_pw,
)
from ..constants import ANSI_YELLOW, DEFAULT_WAIT, FORUM_URL, STATE_FILE
from ..content import ensure_ai_notice
from ..logger import (
    _color, delay, fail, gate_ok, header, logger, ok, step, warn,
)
from .drafts import clean_drafts

if TYPE_CHECKING:
    try:
        from playwright.sync_api import Page
    except ImportError:
        Page = Any


def _find_edit_button(page: "Page"):
    selectors = [
        (".post-action-menu__edit", "class=.post-action-menu__edit"),
        ("button[title*='编辑']", "title含'编辑'的button"),
        ("a[title*='编辑']", "title含'编辑'的a标签"),
    ]
    for sel, desc in selectors:
        logger.debug("  尝试选择器: %s", desc)
        loc = page.locator(sel).first
        try:
            if loc.is_visible(timeout=2000):
                gate_ok(f"找到编辑按钮: {desc}")
                return loc
        except Exception:
            continue
    return None


def _find_save_button(page: "Page"):
    candidates = [
        (page.locator("button.btn-primary").filter(has_text="保存").first, "button.btn-primary:has-text('保存')"),
        (page.get_by_role("button", name="保存").first, "role=button name='保存'"),
    ]
    for loc, desc in candidates:
        try:
            if loc.is_visible(timeout=2000):
                gate_ok(f"找到保存按钮: {desc}")
                return loc
        except Exception:
            continue
    return None


def do_edit(
    topic_id: int,
    content: str | None = None,
    content_file: str | None = None,
    prepend_text: str | None = None,
    dry_run: bool = False,
    headless: bool = False,
    debug: bool = False,
    add_notice: bool = True,
) -> None:
    """编辑帖子正文。"""
    sync_playwright, PWTimeout = _import_pw()
    action = "编辑帖子（试运行）" if dry_run else f"编辑帖子 #{topic_id}"
    header(action)

    if content_file:
        step(f"从文件读取内容: {content_file}")
        try:
            new_content = Path(content_file).read_text(encoding="utf-8")
            gate_ok(f"文件读取成功 ({len(new_content)} 字符)")
        except OSError as e:
            fail(f"读取文件失败: {e}")
            return
    elif content is not None:
        new_content = content
        logger.info("使用直接指定的内容 (%d 字符)", len(new_content))
    elif prepend_text:
        new_content = None
        logger.info("prepend模式: 将在开头追加文本 (%d 字符)", len(prepend_text))
        logger.debug("  追加文本前50字符: %s", prepend_text[:50])
    else:
        fail("必须指定 --content、--file 或 --prepend 之一")
        return

    if add_notice and new_content is not None:
        step("检查并添加AI发布声明")
        new_content, notice_added = ensure_ai_notice(new_content)
        if notice_added:
            ok("已自动添加AI发布声明")
        else:
            gate_ok("AI声明已存在，跳过")

    with sync_playwright() as p:
        browser, context = create_context(p, headless=headless)
        page = context.new_page()

        url = f"{FORUM_URL}/t/topic/{topic_id}"
        if not safe_navigate(page, url, "目标帖子"):
            fail("导航失败，终止编辑")
            browser.close()
            return

        if not check_login(page):
            fail("未登录，终止编辑")
            browser.close()
            return

        safe_navigate(page, url, "重新加载帖子页面")

        if prepend_text and new_content is None:
            step("[prepend] 读取当前正文内容")
            edit_btn = _find_edit_button(page)
            if edit_btn is None:
                fail("未找到编辑按钮，可能没有编辑权限")
                browser.close()
                return
            edit_btn.click()
            page.wait_for_timeout(DEFAULT_WAIT)

            if not wait_for_selector(page, "textarea.d-editor-input", "编辑器textarea"):
                fail("编辑器未加载")
                browser.close()
                return

            ta = page.locator("textarea.d-editor-input").first
            try:
                current = ta.input_value()
                gate_ok(f"读取当前内容 ({len(current)} 字符)")
                logger.debug("  当前内容前80字符: %s", current[:80].replace("\n", "\\n"))
            except Exception as e:
                fail(f"读取当前内容失败: {e}")
                browser.close()
                return

            if current.startswith(prepend_text[:20]):
                warn(f"追加内容已存在于开头（幂等检测），跳过编辑")
                ok("内容已是最新状态，无需编辑")
                page.keyboard.press("Escape")
                browser.close()
                return

            new_content = f"{prepend_text}\n\n{current}"
            gate_ok(f"组装新内容 ({len(new_content)} 字符)")

            step("关闭编辑器（Escape）")
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
            safe_navigate(page, url, "重新加载帖子")

        if dry_run:
            logger.info("[DRY-RUN] 内容预览（不提交）:")
            print(f"\n  {_color('[DRY-RUN] 将要发布的内容预览:', ANSI_YELLOW)}")
            preview = new_content[:800] + ("..." if len(new_content) > 800 else "")
            for line in preview.split("\n")[:30]:
                print(f"    {line}")
            ok("试运行完成，未实际提交")
            browser.close()
            return

        step("1/4 打开编辑器")
        edit_btn = _find_edit_button(page)
        if edit_btn is None:
            fail("未找到编辑按钮")
            if debug:
                shot_path = STATE_FILE.parent / f"edit-fail-{topic_id}-{int(time.time())}.png"
                page.screenshot(path=str(shot_path))
                logger.info("  📸 已截图保存: %s", shot_path)
            browser.close()
            return
        edit_btn.click()
        page.wait_for_timeout(DEFAULT_WAIT)

        step("2/4 填写新内容")
        if not wait_for_selector(page, "textarea.d-editor-input", "编辑器textarea"):
            fail("编辑器textarea未出现")
            browser.close()
            return

        if not fill_textarea(page, "textarea.d-editor-input", new_content, "正文编辑器"):
            fail("填写内容失败")
            browser.close()
            return

        delay(reason="Discourse 内容校验防抖")

        step("3/4 提交保存")
        save_btn = _find_save_button(page)
        if save_btn is None:
            fail("未找到保存按钮，编辑器可能未就绪")
            all_btns = page.locator("button.btn-primary").all()
            for i, btn in enumerate(all_btns):
                try:
                    logger.debug("  btn-primary[%d]: text='%s' class='%s'", i, btn.inner_text().strip()[:30], btn.get_attribute("class") or "")
                except Exception:
                    pass
            browser.close()
            return

        save_btn.click()
        gate_ok("保存按钮已点击")
        page.wait_for_timeout(3000)
        logger.debug("  📄 提交后URL: %s", page.url)

        step("4/4 验证编辑结果")
        safe_navigate(page, url, "验证页面（重新加载）")
        try:
            if wait_for_selector(page, ".cooked", "验证正文区域", timeout=5000):
                cooked = page.locator(".cooked").first
                result_text = cooked.inner_text(timeout=5000)
                logger.debug("  验证内容前100字符: %s", result_text[:100].replace("\n", "\\n"))

                if prepend_text and prepend_text[:20] in result_text:
                    ok("编辑成功！追加内容已生效")
                elif content_file or content:
                    check_text = new_content[:30].strip()
                    if check_text in result_text:
                        ok("编辑成功！新内容已生效")
                    else:
                        warn("编辑可能成功，但未在正文中检测到新内容特征文本，建议人工验证")
                        logger.debug("  特征文本 '%s' 未在结果中找到", check_text)
                else:
                    ok("编辑操作已完成")
            else:
                warn("验证阶段未找到正文区域，请人工确认")
        except PWTimeout:
            warn("验证超时，请人工检查")
        except Exception as e:
            warn(f"验证异常: {type(e).__name__}: {e}")

        step("清理自动保存的草稿")
        draft_count = clean_drafts(page, verbose=False)
        if draft_count > 0:
            logger.info("  已自动清理 %d 个草稿", draft_count)

        browser.close()
