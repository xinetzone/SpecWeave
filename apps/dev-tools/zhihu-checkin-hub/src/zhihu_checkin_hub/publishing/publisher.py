"""发布编排器。

状态机：``idle → gate_passed → filled → awaiting_human → confirmed``；
任何填充/回读失败 → ``degraded``（打开目标页 + 草稿入剪贴板 + 中文指引）。

铁律：本模块 **永远不会** 点击知乎的最终发布按钮。自动操作仅限打开编辑入口、
填充标题/正文；发布动作由用户本人在浏览器中完成，应用只在用户点击
「我已发布」后读取 URL 信号并截图存证。
"""

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any

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

        draft = load_draft(ws, session.draft_slug)
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

    # ---------------- 三种类型填充 ----------------

    def _fill_article(self, draft: Draft) -> dict[str, Any]:
        self.client.navigate(ARTICLE_WRITE_URL, group_title="知乎文章发布")
        title_hit = self._fill_any(_TITLE_SELECTORS, draft.title)
        if title_hit is None:
            raise PublishError("找不到文章标题输入框")
        body_hit = self._fill_any(_BODY_SELECTORS, draft.body)
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
        return {"title_selector": title_hit[0], "body_selector": body_hit[0], "readback": readback}

    def _fill_answer(self, draft: Draft) -> dict[str, Any]:
        self.client.navigate(draft.question_url, group_title="知乎回答发布")
        entry = self.client.evaluate(_ANSWER_ENTRY_JS)
        try:
            entry_signal = json.loads(entry.get("value", "{}"))
        except (ValueError, TypeError):
            entry_signal = {}
        body_hit = self._fill_any(_BODY_SELECTORS, draft.body)
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
        return {"entry_signal": entry_signal, "body_selector": body_hit[0], "readback": readback}

    def _fill_pin(self, draft: Draft) -> dict[str, Any]:
        if len(draft.body) < PIN_MIN_CHARS:
            raise PublishError(f"想法正文不足 {PIN_MIN_CHARS} 字")
        self.client.navigate(ZHIHU_HOME_URL, group_title="知乎想法发布")
        opened = self._readback(_PIN_OPEN_JS)
        if not opened.get("opened"):
            raise PublishError("打不开想法输入框（首页未找到「分享此刻的想法...」入口）")
        body_hit = self._fill_any(_PIN_SELECTORS, draft.body)
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
        return {"body_selector": body_hit[0], "readback": readback}

    # ---------------- 辅助与降级 ----------------

    def _fill_any(self, selectors: list[str], value: str) -> tuple[str, str] | None:
        last: str = ""
        for selector in selectors:
            try:
                resp = self.client.fill(selector, value)
                return selector, str(resp.get("mode", "unknown"))
            except BridgeError as exc:
                last = str(exc)
                continue
        self.session.detail["last_fill_error"] = last
        return None

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
