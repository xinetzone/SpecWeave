"""forum-bot.py — forum.trae.cn 论坛自动化操作工具。

基于 Playwright 实现 forum.trae.cn（Discourse 论坛）的自动化操作，
支持读取帖子、编辑正文、发布回复、清理草稿等功能。

使用方式：
  # 首次登录（打开有头浏览器，手动登录后按 Enter 保存状态）
  python forum-bot.py login

  # 读取帖子内容
  python forum-bot.py read 44601

  # 编辑帖子（从文件读取内容替换正文）
  python forum-bot.py edit 44601 --file new-content.md

  # 编辑帖子（直接指定文本，追加到开头）
  python forum-bot.py edit 44601 --prepend "📅 最新更新：2026年6月29日"

  # 发布回复
  python forum-bot.py reply 44601 --content "测试回复"

  # 发布回复（从文件读取内容）
  python forum-bot.py reply 44601 --file reply.md

  # 清理所有草稿
  python forum-bot.py clean-drafts

  # 试运行（不实际提交写操作）
  python forum-bot.py edit 44601 --content "测试" --dry-run

  # 调试模式（输出更详细日志）
  python forum-bot.py --debug read 44601
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PWTimeout
except ImportError:
    print("[FAIL] 请先安装 Playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


FORUM_URL = "https://forum.trae.cn"
STATE_FILE = Path(__file__).parent / "config" / "forum-state.json"
DEFAULT_WAIT = 2000  # 毫秒
ACTION_DELAY = 3     # 秒（论坛操作间隔）
ELEMENT_TIMEOUT = 8000  # 毫秒（等待元素出现的超时）
RETRY_MAX = 2       # 关键操作最大重试次数

ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"
ANSI_GREY = "\033[90m"
ANSI_RESET = "\033[0m"

logger = logging.getLogger("forum-bot")


def setup_logging(debug: bool = False) -> None:
    """初始化日志系统：控制台按级别过滤，文件始终记录DEBUG级。"""
    console_level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(logging.DEBUG)  # logger本身始终放行所有级别
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(message)s",
        datefmt="%H:%M:%S",
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(
        log_dir / f"forum-bot-{time.strftime('%Y%m%d')}.log",
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

    logger.debug("日志系统初始化完成 (debug=%s, 文件日志始终为DEBUG)", debug)


def _color(msg: str, code: str) -> str:
    if not sys.stdout.isatty():
        return msg
    return f"{code}{msg}{ANSI_RESET}"


def step(msg: str) -> None:
    """步骤开始日志。"""
    logger.info("▸ %s", msg)


def gate_ok(msg: str) -> None:
    """门禁检查通过日志。"""
    logger.debug("  ✅ %s", msg)


def gate_fail(msg: str) -> None:
    """门禁检查失败日志。"""
    logger.warning("  ❌ %s", msg)


def retry_log(attempt: int, max_attempts: int, action: str) -> None:
    """重试日志。"""
    logger.warning("  🔄 重试 %d/%d: %s", attempt, max_attempts, action)


def ok(msg: str) -> None:
    logger.info("%s %s", _color("[OK]", ANSI_GREEN), msg)


def warn(msg: str) -> None:
    logger.warning("%s %s", _color("[WARN]", ANSI_YELLOW), msg)


def fail(msg: str) -> None:
    logger.error("%s %s", _color("[FAIL]", ANSI_RED), msg)


def header(msg: str) -> None:
    banner = _color(f"\n{'='*60}\n  {msg}\n{'='*60}", ANSI_BOLD)
    logger.info(banner)


def ensure_state_dir() -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("状态文件目录已确认: %s", STATE_FILE.parent)


def delay(seconds: float = ACTION_DELAY, reason: str = "") -> None:
    """操作间隔，遵守论坛频率限制。"""
    if reason:
        logger.debug("  ⏳ 等待 %.1fs (%s)", seconds, reason)
    else:
        logger.debug("  ⏳ 等待 %.1fs", seconds)
    time.sleep(seconds)


def safe_navigate(page: Page, url: str, label: str = "页面") -> bool:
    """安全导航到URL，带超时和错误处理。"""
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


def wait_for_selector(page: Page, selector: str, label: str = "", timeout: int = ELEMENT_TIMEOUT) -> bool:
    """等待元素出现，返回是否可见。门禁条件封装。"""
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


def click_with_retry(page: Page, selector: str, label: str = "", retries: int = RETRY_MAX) -> bool:
    """点击元素，失败时重试（含滚动到视图、JS click兜底）。"""
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


def fill_textarea(page: Page, selector: str, content: str, label: str = "编辑器") -> bool:
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


def create_context(playwright, headless: bool = False) -> tuple:
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
                viewport={"width": 1280, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            )
            gate_ok("已加载持久化登录状态")
            _attach_network_logging(context)
            return browser, context

    logger.info("  🆕 创建新的浏览器上下文（无保存状态）")
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
    )

    _attach_network_logging(context)
    return browser, context


def _attach_network_logging(context: BrowserContext) -> None:
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


def _get_current_username(page: Page) -> str | None:
    """从页面中获取当前登录用户名。多信号组合检测。
    若当前已在 forum.trae.cn 域名下，先尝试不导航直接检测；
    检测失败再导航到首页重试。
    """
    logger.debug("  🔐 检测当前登录用户名...")

    def _extract_username() -> str | None:
        """从当前页面提取用户名，返回None表示未检测到。"""
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

    # 先在当前页面尝试检测（不导航）
    current_url = page.url
    if current_url.startswith(FORUM_URL):
        logger.debug("  当前在论坛域名下 (%s)，先尝试直接检测", current_url[:80])
        page.wait_for_timeout(1000)
        result = _extract_username()
        if result:
            return result
        logger.debug("  当前页面检测失败，导航到首页重试")

    # 导航到首页再检测
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


def check_login(page: Page) -> bool:
    """检查是否已登录论坛（多信号组合判断）。
    检测前保存当前URL，检测失败时若跳转了首页则恢复原URL。
    """
    step("检查登录状态")
    saved_url = page.url
    username = _get_current_username(page)
    # 如果检测导致跳转到首页且失败，恢复原URL
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


def do_read(topic_id: int, headless: bool = True, debug: bool = False) -> None:
    """读取帖子标题和正文。"""
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


def _find_edit_button(page: Page):
    """定位编辑按钮，返回locator或None。"""
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


def _find_save_button(page: Page):
    """定位保存按钮。"""
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
) -> None:
    """编辑帖子正文。"""
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

        # ── prepend模式：先读取当前内容 ──
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

        # ── dry-run模式 ──
        if dry_run:
            logger.info("[DRY-RUN] 内容预览（不提交）:")
            print(f"\n  {_color('[DRY-RUN] 将要发布的内容预览:', ANSI_YELLOW)}")
            preview = new_content[:800] + ("..." if len(new_content) > 800 else "")
            for line in preview.split("\n")[:30]:
                print(f"    {line}")
            ok("试运行完成，未实际提交")
            browser.close()
            return

        # ── 正式编辑流程 ──
        step("1/4 打开编辑器")
        edit_btn = _find_edit_button(page)
        if edit_btn is None:
            fail("未找到编辑按钮")
            # 截图用于排障
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
            # 尝试查找所有btn-primary按钮用于诊断
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
        draft_count = _clean_drafts(page, verbose=False)
        if draft_count > 0:
            logger.info("  已自动清理 %d 个草稿", draft_count)

        browser.close()


def _find_reply_open_button(page: Page):
    """找到打开回复编辑器的按钮（非提交按钮）。"""
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


def _find_reply_submit_button(page: Page):
    """找到回复提交按钮。"""
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
) -> None:
    """发布回复。"""
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

        # ── 正式回复流程 ──
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
        for sel, desc in [
            ("textarea.d-editor-input", "回复编辑器（最后一个）"),
        ]:
            all_tas = page.locator(sel).all()
            logger.debug("  找到 %d 个 %s", len(all_tas), desc)
            if all_tas:
                for candidate in reversed(all_tas):
                    try:
                        if candidate.is_visible(timeout=2000):
                            ta = candidate
                            gate_ok(f"选择了{desc}")
                            break
                    except Exception:
                        continue
                if ta:
                    break

        if ta is None:
            fail("未找到回复编辑器textarea")
            if debug:
                shot_path = STATE_FILE.parent / f"reply-fail-{topic_id}-{int(time.time())}.png"
                page.screenshot(path=str(shot_path))
                logger.info("  📸 已截图保存: %s", shot_path)
            browser.close()
            return

        if not fill_textarea(page, "textarea.d-editor-input", reply_content, "回复编辑器"):
            # fill_textarea用first，需要确保定位到正确的。
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
        draft_count = _clean_drafts(page, verbose=False)
        if draft_count > 0:
            logger.info("  已自动清理 %d 个草稿", draft_count)

        browser.close()


def _clean_drafts(page: Page, username: str | None = None, verbose: bool = True) -> int:
    """清理所有草稿，返回删除的草稿数量。"""
    if username is None:
        username = _get_current_username(page)
    if not username:
        warn("无法获取当前用户名，跳过草稿清理")
        return 0

    drafts_url = f"{FORUM_URL}/u/{username}/activity/drafts"
    logger.debug("  🗑️  访问草稿页: %s", drafts_url)
    page.goto(drafts_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(DEFAULT_WAIT)

    count = 0
    max_drafts = 20  # 安全上限，防止无限循环
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
        count = _clean_drafts(page, username=username, verbose=True)
        ok(f"清理完成，共删除 {count} 个草稿")

        browser.close()


def main() -> None:
    raw_args = sys.argv[1:]
    debug = "--debug" in raw_args or "-d" in raw_args
    if debug:
        raw_args = [a for a in raw_args if a not in ("--debug", "-d")]

    setup_logging(debug=debug)
    logger.info("forum-bot.py 启动 | Python %s | Playwright", sys.version.split()[0])
    logger.debug("命令行参数: %s", raw_args)

    parser = argparse.ArgumentParser(
        description="forum.trae.cn 论坛自动化操作工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式（输出详细日志）")
    subparsers = parser.add_subparsers(dest="command", help="操作命令")

    sub_login = subparsers.add_parser("login", help="首次登录并保存状态")
    sub_login.add_argument("--headless", action="store_true", help="无头模式（不推荐）")

    sub_read = subparsers.add_parser("read", help="读取帖子内容")
    sub_read.add_argument("topic_id", type=int, help="帖子ID（如 44601）")
    sub_read.add_argument("--headless", action="store_true", default=True, help="无头模式（默认开启）")

    sub_edit = subparsers.add_parser("edit", help="编辑帖子正文")
    sub_edit.add_argument("topic_id", type=int, help="帖子ID")
    sub_edit.add_argument("--content", type=str, help="直接指定新内容")
    sub_edit.add_argument("--file", type=str, help="从Markdown文件读取内容")
    sub_edit.add_argument("--prepend", type=str, help="在帖子开头追加文本")
    sub_edit.add_argument("--dry-run", action="store_true", help="试运行，不提交")
    sub_edit.add_argument("--headless", action="store_true", default=False, help="无头模式（默认关闭）")

    sub_reply = subparsers.add_parser("reply", help="发布回复")
    sub_reply.add_argument("topic_id", type=int, help="帖子ID")
    sub_reply.add_argument("--content", type=str, help="回复内容")
    sub_reply.add_argument("--file", type=str, help="从文件读取回复内容")
    sub_reply.add_argument("--dry-run", action="store_true", help="试运行，不提交")
    sub_reply.add_argument("--headless", action="store_true", default=False, help="无头模式（默认关闭）")

    sub_clean = subparsers.add_parser("clean-drafts", help="清理所有草稿")
    sub_clean.add_argument("--headless", action="store_true", default=True, help="无头模式（默认开启）")

    args = parser.parse_args(raw_args)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    start_time = time.time()
    logger.info("执行命令: %s", args.command)

    try:
        if args.command == "login":
            do_login(headless=getattr(args, "headless", False), debug=debug)
        elif args.command == "read":
            do_read(args.topic_id, headless=getattr(args, "headless", True), debug=debug)
        elif args.command == "edit":
            do_edit(
                args.topic_id,
                content=args.content,
                content_file=args.file,
                prepend_text=args.prepend,
                dry_run=args.dry_run,
                headless=args.headless,
                debug=debug,
            )
        elif args.command == "reply":
            do_reply(
                args.topic_id,
                content=args.content,
                content_file=args.file,
                dry_run=args.dry_run,
                headless=args.headless,
                debug=debug,
            )
        elif args.command == "clean-drafts":
            do_clean_drafts(headless=getattr(args, "headless", True), debug=debug)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        logger.warning("用户中断 (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.error("未捕获异常: %s: %s", type(e).__name__, e, exc_info=debug)
        fail(f"脚本异常退出: {e}")
        sys.exit(1)

    elapsed = time.time() - start_time
    logger.info("命令 %s 完成，耗时 %.1fs", args.command, elapsed)


if __name__ == "__main__":
    main()
