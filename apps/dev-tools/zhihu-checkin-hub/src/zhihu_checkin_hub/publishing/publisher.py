"""发布编排器。

状态机：``idle → gate_passed → filled → awaiting_human → confirmed``；
任何填充/回读失败 → ``degraded``（打开目标页 + 草稿入剪贴板 + 中文指引）。

铁律：本模块 **永远不会** 点击知乎的最终发布按钮。自动操作仅限打开编辑入口、
填充标题/正文；发布动作由用户本人在浏览器中完成，应用只在用户点击
「我已发布」后读取 URL 信号并截图存证。
"""

import json
import re
import time
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Callable

from ..errors import BridgeError, PublishError
from ..storage.drafts import Draft, load_draft, save_draft, transition_status
from ..storage.entries import ContentKind, ContentRecord, DayEntry, load_entry, save_entry
from ..storage.workspace import Workspace
from .bridge import BridgeClient

ARTICLE_WRITE_URL = "https://zhuanlan.zhihu.com/write"
ZHIHU_HOME_URL = "https://www.zhihu.com/"
PIN_MIN_CHARS = 20

_TITLE_SELECTORS = [
    "textarea.Input",
    "input[placeholder*='标题']",
    ".WriteIndex-titleInput textarea",
    "[data-zop-item='title']",
]
# 注意（真实冒烟记录，webbridge v1.11.6）：fill 动作对含引号属性选择器（如
# [contenteditable='true']）会在守护端抛 "Unexpected token 'true'" SyntaxError，
# 因此首选选择器一律用纯 class；带属性的选择器仅作末位兜底（失败会被跳过）。
_BODY_SELECTORS = [
    ".public-DraftEditor-content",
    ".DraftEditor-root .public-DraftEditor-content",
    ".AnswerForm-editor .public-DraftEditor-content",
    ".Editable-content",
    "div.Editable-content[contenteditable='true']",
    ".AnswerForm-editor [contenteditable='true']",
    "div[contenteditable='true']",
]
_PIN_SELECTORS = [
    ".DraftEditor-root .public-DraftEditor-content",
    ".InputLike .public-DraftEditor-content",
    ".public-DraftEditor-content",
    ".Editable .public-DraftEditor-content",
    ".Topstory-container [contenteditable='true']",
    ".Input-richInput[contenteditable='true']",
    "textarea.Textarea",
    "div[contenteditable='true']",
]
# 首页想法框默认折叠，需先点开「分享此刻的想法...」入口，轮询等待 DraftEditor 挂载
_PIN_OPEN_JS = r"""
(async () => {
  const entry = [...document.querySelectorAll('div,span,button')]
    .find(el => (el.textContent || '').trim() === '分享此刻的想法...');
  if (entry) entry.click();
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('.DraftEditor-root [contenteditable="true"]')) {
      return JSON.stringify({opened: true});
    }
    await new Promise(r => setTimeout(r, 150));
  }
  return JSON.stringify({opened: false});
})()
""".strip()
# DraftJS（React 受控编辑器）提交式注入（真实冒烟记录，2026-09-28）：
# webbridge 的 fill 对 contenteditable 只改 DOM 文本，不触发 beforeinput，
# DraftJS 内部 editorState 仍为空——失焦/自动保存触发 React 重渲染后正文被清空
# （现象：标题在、正文消失，发布按钮也是禁用态）。必须 focus 后用
# execCommand('insertText'/'insertParagraph')，DraftJS 才能在 beforeinput 中
# 真正提交。选择器列表在调用处注入到 __SELECTORS__；文本经 window.__zch_fill__
# 传递（不在 JS 源码里内嵌用户文本）。
_DRAFTJS_INJECT_JS = r"""
(() => {
  const sels = __SELECTORS__;
  let el = null, used = '';
  for (const s of sels) {
    const nodes = [...document.querySelectorAll(s)];
    const hit = nodes.find(e => e.offsetWidth || e.offsetHeight || e.getClientRects().length);
    if (hit) { el = hit; used = s; break; }
  }
  if (!el) return JSON.stringify({ok: false, why: 'no-visible-editor'});
  el.focus();
  const sel = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(el);
  sel.removeAllRanges();
  sel.addRange(range);
  document.execCommand('delete');
  const lines = String(window.__zch_fill__ == null ? '' : window.__zch_fill__).split('\n');
  lines.forEach((ln, i) => {
    document.execCommand('insertText', false, ln);
    if (i < lines.length - 1) document.execCommand('insertParagraph');
  });
  return JSON.stringify({ok: true, selector: used, len: el.textContent.length});
})()
""".strip()
# ---- CDP 受信输入（真实冒烟定稿，2026-09-28）----
# 知乎专栏/回答/想法正文都是 DraftJS。真实环境结论：
#  1) bridge.fill/execCommand 只改 DOM，DraftJS 模型不接收，失焦/自动保存后被
#     React 回滚（标题在、正文消失）；且一旦被合成注入污染，该草稿模型/DOM 永久脱节；
#  2) 唯一可靠通道是 CDP（chrome.debugger）受信事件：Page.bringToFront →
#     Input.dispatchMouseEvent 点入编辑器（需浏览器窗口在 OS 前台）→
#     Input.insertText 分块上屏（单块 ≤20 字，长文本整块会被截断）；
#  3) 若点击后 document.activeElement 不是 contenteditable（窗口在后台），
#     立即降级，绝不做合成兜底，避免「看起来填上了、实际发空文」。
_CDP_CHUNK = 20
_CDP_LOCATE_JS = r"""
(() => {
  const sels = __SELECTORS__;
  for (const s of sels) {
    const nodes = [...document.querySelectorAll(s)];
    const hit = nodes.find(e => e.offsetWidth || e.offsetHeight || e.getClientRects().length);
    if (hit) {
      const r = hit.getBoundingClientRect();
      return JSON.stringify({
        ok: true, selector: s,
        x: Math.round(r.left + 24),
        y: Math.round(r.top + Math.min(14, Math.max(6, r.height / 2)))
      });
    }
  }
  return JSON.stringify({ok: false});
})()
""".strip()
_CDP_ACTIVE_JS = r"""
(() => {
  const a = document.activeElement;
  return JSON.stringify({
    tag: a ? a.tagName.toLowerCase() : '',
    ce: a ? a.getAttribute('contenteditable') : null,
    cls: a ? (a.className || '').toString().slice(0, 80) : ''
  });
})()
""".strip()
_CDP_LEN_JS = r"""
(() => {
  const sels = __SELECTORS__;
  for (const s of sels) {
    const nodes = [...document.querySelectorAll(s)];
    const hit = nodes.find(e => e.offsetWidth || e.offsetHeight || e.getClientRects().length);
    if (hit) return JSON.stringify({len: hit.textContent.length, preview: hit.textContent.slice(0, 40)});
  }
  return JSON.stringify({len: 0});
})()
""".strip()
# 想法发布后知乎停在首页（原地刷新 feed），URL 不跳详情。
# 用正文前缀在当前页/个人主页想法列表中反查刚发布的 pin，匹配上才导航过去读信号，
# 绝不接受无关 pin。
_PIN_FIND_JS = r"""
(() => {
  const needle = __NEEDLE__;
  const a = [...document.querySelectorAll('a[href*="/pin/"]').values()].find(x => {
    // 真实页面卡片类名多变（主页想法列表无统一容器 class）：向上最多找 12 层祖先
    let node = x;
    for (let i = 0; i < 12 && node; i++) {
      if ((node.textContent || '').includes(needle)) return true;
      node = node.parentElement;
    }
    return false;
  });
  return JSON.stringify({href: a ? a.href : null});
})()
""".strip()
_PROFILE_HREF_JS = r"""
(() => {
  const a = document.querySelector('a[href*="/people/"]');
  return JSON.stringify({href: a ? a.href : null});
})()
""".strip()
# 只允许点「写回答/添加回答/编辑回答」这类编辑入口，绝不匹配最终发布动作
_ANSWER_ENTRY_JS = r"""
(() => {
  const nodes = [...document.querySelectorAll('a,button')];
  const hit = nodes.find(el => /^(写回答|添加回答|编辑回答|回答问题|继续编辑回答)$/.test(
    (el.textContent || '').replace(/\s+/g, '').trim()
  ));
  if (hit) { hit.click(); return JSON.stringify({clicked: true, text: hit.textContent.trim()}); }
  return JSON.stringify({clicked: false});
})()
""".strip()

_PUBLISHED_PATTERNS = {
    ContentKind.ARTICLE: re.compile(r"^https?://(?:zhuanlan\.zhihu\.com|www\.zhihu\.com)/p/\d+"),
    ContentKind.ANSWER: re.compile(r"^https?://www\.zhihu\.com/question/\d+/answer/\d+"),
    ContentKind.PIN: re.compile(r"^https?://www\.zhihu\.com/pin/\d+"),
}

_HUMAN_INSTRUCTIONS = {
    ContentKind.ARTICLE: "请在浏览器中核对标题与正文，确认无误后由你本人点击「发布文章」。",
    ContentKind.ANSWER: "请在浏览器中核对回答正文，确认无误后由你本人点击「发布回答」。",
    ContentKind.PIN: "请自行确认/补挂图片，确认无误后由你本人点击发布想法（想法正文需 ≥20 字）。",
}


class PublishState(StrEnum):
    IDLE = "idle"
    GATE_PASSED = "gate_passed"
    FILLED = "filled"
    AWAITING_HUMAN = "awaiting_human"
    CONFIRMED = "confirmed"
    DEGRADED = "degraded"


@dataclass
class PublishSession:
    kind: str
    draft_slug: str
    state: PublishState = PublishState.IDLE
    target_url: str = ""
    detail: dict[str, Any] = field(default_factory=dict)
    started_at: str = ""
    gate_at: str = ""


@dataclass(frozen=True)
class FillOutcome:
    state: PublishState
    detail: dict[str, Any]


@dataclass(frozen=True)
class ConfirmResult:
    state: PublishState
    published_url: str
    screenshot_path: str
    content_id: str


class Publisher:
    def __init__(self, client: BridgeClient, *, clock: Any = datetime) -> None:
        self.client = client
        self._clock = clock
        self.session: PublishSession | None = None

    # ---------------- 阶段推进 ----------------

    def begin(self, draft: Draft, *, gate_at: str) -> PublishSession:
        # 类型合法性由 Draft（存储边界）保证，此处无需重复校验
        if draft.kind == ContentKind.ANSWER and not draft.question_url.strip():
            raise PublishError("回答草稿必须登记问题 URL（question_url）")
        if draft.kind == ContentKind.ARTICLE and not draft.title.strip():
            raise PublishError("文章草稿必须有标题")
        if draft.kind == ContentKind.PIN and len(draft.body) < PIN_MIN_CHARS:
            raise PublishError(f"想法正文不足 {PIN_MIN_CHARS} 字，不能进入发布")
        if draft.status != "ready":
            raise PublishError(
                f"草稿当前为 {draft.status} 状态：通过固定门后请先推进为 ready 再进入填充"
            )
        session = PublishSession(
            kind=draft.kind,
            draft_slug=draft.slug,
            state=PublishState.GATE_PASSED,
            started_at=self._clock.now().isoformat(timespec="seconds"),
            gate_at=gate_at,
        )
        self.session = session
        return session

    def fill(self, draft: Draft) -> FillOutcome:
        session = self._require(PublishState.GATE_PASSED)
        try:
            if session.kind == ContentKind.ARTICLE:
                detail = self._fill_article(draft)
            elif session.kind == ContentKind.ANSWER:
                detail = self._fill_answer(draft)
            else:
                detail = self._fill_pin(draft)
        except BridgeError as exc:
            return self._degrade(draft, f"自动填充中断：{exc}")
        except PublishError as exc:
            return self._degrade(draft, str(exc))
        session.state = PublishState.FILLED
        session.detail = detail
        return FillOutcome(session.state, detail)

    def hand_to_human(self) -> str:
        session = self._require(PublishState.FILLED)
        session.state = PublishState.AWAITING_HUMAN
        return _HUMAN_INSTRUCTIONS[ContentKind(session.kind)]

    def confirm(
        self, ws: Workspace, *, day: date | None = None, now: datetime | None = None
    ) -> ConfirmResult:
        session = self._require(PublishState.AWAITING_HUMAN)
        day = day or date.today()
        now = now or self._clock.now()
        kind = ContentKind(session.kind)

        draft = load_draft(ws, session.draft_slug)
        href = str(self.client.evaluate("location.href").get("value", ""))
        match = _PUBLISHED_PATTERNS[kind].match(href)
        # 想法发布后停在首页：按正文前缀反查刚发布的 pin，再导航到其详情页读信号
        if not match and kind == ContentKind.PIN:
            resolved = self._resolve_pin_url(draft.body)
            if resolved is not None:
                self.client.navigate(resolved, group_title="知乎想法发布")
                time.sleep(1.0)
                href = str(self.client.evaluate("location.href").get("value", ""))
                match = _PUBLISHED_PATTERNS[kind].match(href)
        if not match:
            raise PublishError(
                f"当前页面 URL 不像已发布的{kind.value}：{href}。"
                "请在浏览器中由你本人完成发布后再点「我已发布」。"
            )
        published_url = href
        content_id = published_url.rstrip("/").split("/")[-1]
        stamp = now.strftime("%Y%m%d-%H%M%S")
        shot = ws.ensure_within_local(
            ws.screenshots_dir / f"{kind.value}-{stamp}-{content_id}.png"
        )
        self.client.screenshot(path=str(shot))

        draft.status = transition_status(draft.status, "published")
        draft.published_url = published_url
        save_draft(ws, draft)

        entry = load_entry(ws, day)
        entry.contents.append(
            ContentRecord(
                kind=kind,
                char_count=len(draft.body),
                url=published_url,
                question_url=draft.question_url,
                draft_slug=draft.slug,
                published_at=now.isoformat(timespec="seconds"),
            )
        )
        save_entry(ws, entry)

        session.state = PublishState.CONFIRMED
        session.detail["published_url"] = published_url
        return ConfirmResult(session.state, published_url, str(shot), content_id)

    def _find_pin_href(self, body_prefix: str) -> str | None:
        code = _PIN_FIND_JS.replace("__NEEDLE__", json.dumps(body_prefix, ensure_ascii=False))
        result = self._readback(code)
        href = result.get("href")
        return str(href) if href else None

    def _resolve_pin_url(self, body: str) -> str | None:
        """想法发布后反查详情 URL。

        真实冒烟（2026-09-28）：点发布后知乎原地刷新 feed，``location.href``
        仍是首页；发布成功弹窗数秒后自动消失。依次尝试：
        1) 当前页（弹窗/feed 中的 pin 链接，按正文前缀匹配，轮询数次）；
        2) 本人主页 ``/people/<token>/pins`` 想法列表（懒加载，最多等约 16s）。
        只接受卡片文本包含正文前 12 字的 pin，杜绝误认他人内容。
        """
        prefix = body[:12]
        for _ in range(4):
            href = self._find_pin_href(prefix)
            if href:
                return href
            time.sleep(0.6)
        profile = self._readback(_PROFILE_HREF_JS)
        me_url = str(profile.get("href") or "")
        match = re.search(r"/people/([^/?#]+)", me_url)
        if match is None:
            return None
        pins_url = f"https://www.zhihu.com/people/{match.group(1)}/pins"
        self.client.navigate(pins_url, group_title="知乎想法发布")
        # 列表靠 IntersectionObserver 懒渲染：后台标签页会被节流，需前台 + 逐步滚动
        for step in range(16):
            time.sleep(1.0)
            href = self._find_pin_href(prefix)
            if href:
                return href
            self.client.evaluate(f"window.scrollTo(0, {(step + 1) * 600})")
        return None

    # ---------------- 三种类型填充 ----------------

    def _fill_article(self, draft: Draft) -> dict[str, Any]:
        self.client.navigate(ARTICLE_WRITE_URL, group_title="知乎文章发布")
        # 真实 /write 编辑器懒挂载：先等标题框出现，否则 fill 会抢跑失败
        if self._wait_located(_TITLE_SELECTORS) is None:
            raise PublishError("找不到文章标题输入框（页面加载超时）")
        title_hit = self._fill_any(_TITLE_SELECTORS, draft.title)
        if title_hit is None:
            raise PublishError("找不到文章标题输入框")
        body_hit = self._fill_body(_BODY_SELECTORS, draft.body)
        if body_hit is None:
            raise PublishError("找不到文章正文编辑器")
        readback = self._readback(
            "(() => { const t=document.querySelector("
            "'textarea.Input, .WriteIndex-titleInput textarea');"
            " const e=document.querySelector("
            "'div.public-DraftEditor-content,div[contenteditable=true]');"
            " return JSON.stringify({title: t?t.value:'', bodyLen: e?e.textContent.length:0}); })()"
        )
        if readback.get("title", "").strip() != draft.title.strip():
            raise PublishError("标题回读不一致，已停止自动操作")
        if int(readback.get("bodyLen", 0)) < len(draft.body) - 2:
            raise PublishError("正文回读字数明显偏少，已停止自动操作")
        return {
            "title_selector": title_hit[0],
            "body_selector": body_hit[0],
            "body_mode": body_hit[1],
            "readback": readback,
        }

    def _fill_answer(self, draft: Draft) -> dict[str, Any]:
        self.client.navigate(draft.question_url, group_title="知乎回答发布")
        entry = self.client.evaluate(_ANSWER_ENTRY_JS)
        try:
            entry_signal = json.loads(entry.get("value", "{}"))
        except (ValueError, TypeError):
            entry_signal = {}
        body_hit = self._fill_body(_BODY_SELECTORS, draft.body)
        if body_hit is None:
            raise PublishError("找不到回答正文编辑器（可能未进入编辑态）")
        readback = self._readback(
            "(() => { const e=document.querySelector("
            "'div.public-DraftEditor-content,div.AnswerForm-editor [contenteditable=true],div[contenteditable=true]');"
            " return JSON.stringify({url: location.href, bodyLen: e?e.textContent.length:0}); })()"
        )
        readback_url = str(readback.get("url", ""))
        if "/question/" not in readback_url:
            raise PublishError("回读 URL 不在问题页，已停止自动操作")
        # 防误发：回读页问题 ID 必须与草稿登记的 question_url 一致
        registered = re.search(r"/question/(\d+)", draft.question_url)
        if registered is not None and f"/question/{registered.group(1)}" not in readback_url:
            raise PublishError(
                f"回读问题 ID 与草稿登记不一致（应为 {registered.group(1)}），已停止自动操作"
            )
        if int(readback.get("bodyLen", 0)) < len(draft.body) - 2:
            raise PublishError("回答正文回读字数明显偏少，已停止自动操作")
        return {
            "entry_signal": entry_signal,
            "body_selector": body_hit[0],
            "body_mode": body_hit[1],
            "readback": readback,
        }

    def _fill_pin(self, draft: Draft) -> dict[str, Any]:
        if len(draft.body) < PIN_MIN_CHARS:
            raise PublishError(f"想法正文不足 {PIN_MIN_CHARS} 字")
        self.client.navigate(ZHIHU_HOME_URL, group_title="知乎想法发布")
        opened = self._readback(_PIN_OPEN_JS)
        if not opened.get("opened"):
            raise PublishError("打不开想法输入框（首页未找到「分享此刻的想法...」入口）")
        body_hit = self._fill_body(_PIN_SELECTORS, draft.body)
        if body_hit is None:
            raise PublishError("找不到想法输入框")
        readback = self._readback(
            "(() => { const e=document.querySelector("
            "'.DraftEditor-root [contenteditable=true],div[contenteditable=true],textarea.Textarea');"
            " const len = e ? (e.value!==undefined ? e.value.length : e.textContent.length) : 0;"
            " return JSON.stringify({bodyLen: len}); })()"
        )
        if int(readback.get("bodyLen", 0)) < PIN_MIN_CHARS:
            raise PublishError("想法回读不足 20 字，已停止自动操作")
        return {"body_selector": body_hit[0], "body_mode": body_hit[1], "readback": readback}

    # ---------------- 辅助与降级 ----------------

    def _note_fill_error(self, message: str) -> None:
        # 单元直调 _fill_body 等场景可能尚未 begin（session 为 None）
        if self.session is not None:
            self.session.detail["last_fill_error"] = message

    def _fill_any(self, selectors: list[str], value: str) -> tuple[str, str] | None:
        last: str = ""
        for selector in selectors:
            try:
                resp = self.client.fill(selector, value)
                return selector, str(resp.get("mode", "unknown"))
            except BridgeError as exc:
                last = str(exc)
                continue
        self._note_fill_error(last)
        return None

    # ---- CDP 受信输入 ----

    def _wait_located(
        self, selectors: list[str], *, timeout: float = 10.0, interval: float = 0.3
    ) -> dict[str, Any] | None:
        """轮询等待选择器列表中任一元素可见（真实页面编辑器懒挂载，导航即返回）。"""
        code = _CDP_LOCATE_JS.replace("__SELECTORS__", json.dumps(selectors))
        deadline = time.monotonic() + timeout
        while True:
            located = self._readback(code)
            if located.get("ok"):
                return located
            if time.monotonic() >= deadline:
                return None
            time.sleep(interval)

    def _cdp_key(self, cdp: Callable[..., dict[str, Any]], key: str, code: str,
                 vk: int, *, ctrl: bool = False) -> None:
        mods = 2 if ctrl else 0
        if ctrl:
            cdp("Input.dispatchKeyEvent", {
                "type": "keyDown", "key": "Control", "code": "ControlLeft",
                "windowsVirtualKeyCode": 17, "nativeVirtualKeyCode": 17,
                "modifiers": 0,
            })
        cdp("Input.dispatchKeyEvent", {
            "type": "rawKeyDown", "key": key, "code": code,
            "windowsVirtualKeyCode": vk, "nativeVirtualKeyCode": vk,
            "modifiers": mods,
        })
        cdp("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": key, "code": code,
            "windowsVirtualKeyCode": vk, "nativeVirtualKeyCode": vk,
            "modifiers": mods,
        })
        if ctrl:
            cdp("Input.dispatchKeyEvent", {
                "type": "keyUp", "key": "Control", "code": "ControlLeft",
                "windowsVirtualKeyCode": 17, "nativeVirtualKeyCode": 17,
            })

    def _cdp_insert(self, selectors: list[str], value: str) -> tuple[str, str] | None:
        """CDP 受信路径填充 DraftJS 正文。

        * 成功 → ``(selector, "cdp-insert")``；
        * 页面没有可见编辑器或桥不支持 cdp → ``None``（交回旧兜底路径）；
        * 焦点未确认/回读字数不足 → 抛 :class:`PublishError`（直接降级，
          禁止再走只改 DOM 的合成兜底，否则「标题在、正文消失」发空文）。
        """
        cdp = getattr(self.client, "cdp", None)
        if not callable(cdp):
            return None
        located = self._wait_located(selectors)
        if located is None:
            return None
        try:
            x, y = int(located["x"]), int(located["y"])
            # 前台切换/弹层展开有动画：点击+焦点确认最多重试 3 次
            active: dict[str, Any] = {}
            for attempt in range(3):
                cdp("Page.bringToFront", {})
                time.sleep(0.2)
                for evt, buttons in (("mousePressed", 1), ("mouseReleased", 0)):
                    cdp("Input.dispatchMouseEvent", {
                        "type": evt, "x": x, "y": y, "button": "left",
                        "buttons": buttons, "clickCount": 1,
                    })
                time.sleep(0.5)
                active = self._readback(_CDP_ACTIVE_JS)
                if active.get("ce") == "true":
                    break
            if active.get("ce") != "true":
                raise PublishError(
                    "正文编辑器未获得真实焦点。请把浏览器窗口切到前台，"
                    "用鼠标点一下正文区后重试「填充」（草稿与正文已准备好，无需手动粘贴）。"
                )
            # 重试场景：先受信清空可能的半截内容（全新空草稿时无副作用）
            self._cdp_key(cdp, "a", "KeyA", 65, ctrl=True)
            time.sleep(0.15)
            self._cdp_key(cdp, "Delete", "Delete", 46)
            time.sleep(0.2)
            lines = value.split("\n")
            for line_index, line in enumerate(lines):
                for start in range(0, len(line), _CDP_CHUNK):
                    cdp("Input.insertText", {"text": line[start:start + _CDP_CHUNK]})
                    time.sleep(0.12)
                if line_index < len(lines) - 1:
                    self._cdp_key(cdp, "Enter", "Enter", 13)
                    time.sleep(0.08)
            time.sleep(1.0)
            result = self._readback(
                _CDP_LEN_JS.replace("__SELECTORS__", json.dumps(selectors))
            )
            expected = len(value.replace("\n", ""))
            if int(result.get("len", 0)) < expected - 2:
                raise PublishError(
                    "正文受信上屏后回读字数不足（模型可能未接收），已停止，请勿发布；"
                    "请把窗口切到前台后重试。"
                )
        except PublishError:
            raise
        except BridgeError:
            # 守护端/调试器不支持 cdp：交回旧兜底（不写 session.detail，
            # 单元直调场景可能尚未 begin）
            return None
        return str(located.get("selector") or selectors[0]), "cdp-insert"

    def _fill_body(self, selectors: list[str], value: str) -> tuple[str, str] | None:
        """正文填充。优先级：CDP 受信输入 > DraftJS execCommand 注入 > bridge fill。

        后两者只改 DOM，真实知乎 DraftJS 不接收（失焦被回滚、字数 0），
        仅在 cdp 不可用时作为旧守护端兜底保留。焦点未确认类失败直接抛出，
        由 ``fill()`` 降级，不会静默落到合成兜底。
        """
        cdp_hit = self._cdp_insert(selectors, value)
        if cdp_hit is not None:
            return cdp_hit
        try:
            self.client.evaluate(
                "window.__zch_fill__ = " + json.dumps(value, ensure_ascii=False) + ";"
            )
            code = _DRAFTJS_INJECT_JS.replace("__SELECTORS__", json.dumps(selectors))
            result = self._readback(code)
            # 段落分隔符不计入 textContent，故按去换行后的长度核对
            expected = len(value.replace("\n", ""))
            if result.get("ok") and int(result.get("len", 0)) >= expected - 2:
                return str(result.get("selector") or selectors[0]), "draftjs-inject"
            self._note_fill_error(
                f"draftjs 注入未确认：{result.get('why') or '回读字数不足'}"
            )
        except (BridgeError, PublishError) as exc:
            self._note_fill_error(f"draftjs 注入异常：{exc}")
        return self._fill_any(selectors, value)

    def _readback(self, code: str) -> dict[str, Any]:
        resp = self.client.evaluate(code)
        try:
            return json.loads(resp.get("value", "{}"))
        except (ValueError, TypeError):
            raise PublishError("回读结果无法解析")

    def _degrade(self, draft: Draft, reason: str) -> FillOutcome:
        session = self._require_any()
        session.state = PublishState.DEGRADED
        target = (
            draft.question_url
            if session.kind == ContentKind.ANSWER
            else ARTICLE_WRITE_URL
            if session.kind == ContentKind.ARTICLE
            else ZHIHU_HOME_URL
        )
        session.target_url = target
        clipboard_ok = False
        try:
            self.client.evaluate(
                f"navigator.clipboard.writeText({json.dumps(draft.body)})"
            )
            clipboard_ok = True
        except BridgeError:
            clipboard_ok = False
        session.detail = {
            "reason": reason,
            "target_url": target,
            "clipboard": clipboard_ok,
            "instruction": (
                "自动填充未成功。已为你打开目标页面，并尝试把正文放入剪贴板"
                f"（{'成功' if clipboard_ok else '失败，请手动复制草稿'}）。"
                "请手动粘贴、核对后由你本人完成发布，再回到应用点「我已发布」。"
            ),
        }
        return FillOutcome(session.state, session.detail)

    def _require(self, expected: PublishState) -> PublishSession:
        session = self._require_any()
        if session.state != expected:
            raise PublishError(
                f"发布会话状态应为 {expected}，当前为 {session.state}，拒绝该操作"
            )
        return session

    def _require_any(self) -> PublishSession:
        if self.session is None:
            raise PublishError("尚未开始发布会话（begin 未调用）")
        return self.session
