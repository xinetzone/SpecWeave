"""TR-8：发布编排器状态机、回读、降级、确认存证（FakeBridge 零真实浏览器）。"""

import json
import shutil
from datetime import date, datetime
from pathlib import Path

import pytest

from zhihu_checkin_hub.errors import BridgeError, PublishError
from zhihu_checkin_hub.publishing import publisher as publisher_mod
from zhihu_checkin_hub.publishing.publisher import (
    ARTICLE_WRITE_URL,
    PublishState,
    Publisher,
)
from zhihu_checkin_hub.storage.drafts import Draft, load_draft, save_draft
from zhihu_checkin_hub.storage.entries import ContentKind, load_entry
from zhihu_checkin_hub.storage.workspace import open_workspace

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"
CLOCK = datetime(2026, 10, 1, 21, 30, 0)


class FakeBridge:
    def __init__(self) -> None:
        self.navigated: list[str] = []
        self.fills: list[tuple[str, str]] = []
        self.fail_selectors: set[str] = set()
        self.eval_queue: list[dict] = []
        self.eval_calls: list[str] = []
        self.screenshots: list[dict] = []
        # 占位 None：默认模拟不支持 cdp 的旧守护端；CdpFakeBridge 覆盖为可调用对象
        self.cdp: object = None
        # 定位探测（_CDP_LOCATE_JS，含 getBoundingClientRect）自动应答，
        # 不消费 eval_queue；需要模拟「找不到编辑器」时置 False
        self.auto_located: bool = True

    def navigate(self, url: str, *, group_title: str | None = None, **_: object) -> dict:
        self.navigated.append(url)
        return {"success": True, "url": url}

    def _locate_reply(self) -> dict:
        payload = (
            {"ok": True, "selector": ".public-DraftEditor-content", "x": 300, "y": 200}
            if self.auto_located
            else {"ok": False}
        )
        return {"type": "string", "value": json.dumps(payload, ensure_ascii=False)}

    def evaluate(self, code: str) -> dict:
        self.eval_calls.append(code)
        if "getBoundingClientRect" in code:
            return self._locate_reply()
        if self.eval_queue:
            return {"type": "string", "value": json.dumps(self.eval_queue.pop(0), ensure_ascii=False)}
        return {"type": "string", "value": "{}"}

    def fill(self, selector: str, value: str) -> dict:
        if selector in self.fail_selectors:
            raise BridgeError(f"no such selector {selector}")
        self.fills.append((selector, value))
        return {"success": True, "mode": "contenteditable"}

    def screenshot(self, **args: object) -> dict:
        self.screenshots.append(args)
        return {"format": "png", "path": args.get("path"), "sizeBytes": 1}


@pytest.fixture()
def workspace(tmp_path: Path):
    d = tmp_path / "zhihu-monetization"
    d.mkdir()
    shutil.copy(FIXTURE, d / "tracker.md")
    return open_workspace(d)


def _save(ws, draft: Draft) -> Draft:
    save_draft(ws, draft)
    return draft


def test_article_happy_path_to_confirmation(workspace) -> None:
    body = "这是一篇专栏正文。" * 10
    _save(
        workspace,
        Draft(slug="art-1", title="第一篇文章", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    bridge = FakeBridge()
    bridge.eval_queue = [
        {"ignored": True},  # setvar evaluate（结果不用）
        {"ok": True, "len": len(body)},  # DraftJS 提交式注入确认
        {"title": "第一篇文章", "bodyLen": len(body)},  # 回读
    ]
    pub = Publisher(bridge)
    # confirm 阶段需要裸字符串 value，单独插队
    draft = load_draft(workspace, "art-1")
    pub.begin(draft, gate_at="2026-10-01T21:00:00")

    outcome = pub.fill(draft)
    assert outcome.state == PublishState.FILLED
    assert bridge.navigated[-1] == ARTICLE_WRITE_URL
    assert bridge.fills[0][1] == "第一篇文章"  # 标题仍走 fill
    # 正文走 DraftJS 提交式注入，不再调用 bridge.fill（防止 React 回滚）
    assert outcome.detail["body_selector"] == ".public-DraftEditor-content"
    assert len(bridge.fills) == 1  # 只有标题用 fill

    instruction = pub.hand_to_human()
    assert "你本人" in instruction
    assert pub.session.state == PublishState.AWAITING_HUMAN

    # 让 confirm 的 evaluate 返回已发布 URL（裸字符串）
    bridge.eval_queue = []
    bridge.evaluate = lambda code: {"type": "string", "value": "https://zhuanlan.zhihu.com/p/123456"}  # type: ignore[method-assign]
    result = pub.confirm(workspace, day=date(2026, 10, 1), now=CLOCK)
    assert result.state == PublishState.CONFIRMED
    assert result.published_url.endswith("/p/123456")
    assert "screenshots" in result.screenshot_path and result.screenshot_path.endswith(".png")
    assert bridge.screenshots[0]["path"] == result.screenshot_path

    published = load_draft(workspace, "art-1")
    assert published.status == "published"
    assert published.published_url == result.published_url
    entry = load_entry(workspace, date(2026, 10, 1))
    rec = entry.contents[-1]
    assert rec.kind == "article" and rec.url.endswith("/p/123456") and rec.draft_slug == "art-1"


def test_answer_flow_preserves_question(workspace) -> None:
    body = "回答正文内容，长度足够。" * 8
    _save(
        workspace,
        Draft(
            slug="ans-1",
            title="某问题",
            kind=ContentKind.ANSWER,
            body=body,
            question_url="https://www.zhihu.com/question/999",
            status="ready",
        ),
    )
    bridge = FakeBridge()
    bridge.eval_queue = [
        {"clicked": True, "text": "写回答"},
        {"ignored": True},  # setvar
        {"ok": True, "len": len(body)},  # DraftJS 注入确认
        {"url": "https://www.zhihu.com/question/999", "bodyLen": len(body)},
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "ans-1")
    pub.begin(draft, gate_at="2026-10-01T21:00:00")
    assert pub.fill(draft).state == PublishState.FILLED
    assert bridge.navigated[-1] == "https://www.zhihu.com/question/999"
    pub.hand_to_human()
    bridge.eval_queue = []
    bridge.evaluate = lambda code: {  # type: ignore[method-assign]
        "type": "string",
        "value": "https://www.zhihu.com/question/999/answer/888",
    }
    result = pub.confirm(workspace, day=date(2026, 10, 1), now=CLOCK)
    assert result.published_url.endswith("/answer/888")
    entry = load_entry(workspace, date(2026, 10, 1))
    assert entry.contents[-1].question_url == "https://www.zhihu.com/question/999"


def test_pin_requires_twenty_chars(workspace) -> None:
    short = Draft(slug="pin-1", title="", kind=ContentKind.PIN, body="太短")
    pub = Publisher(FakeBridge())
    with pytest.raises(PublishError, match="20"):
        pub.begin(short, gate_at="2026-10-01T21:00:00")


def test_pin_flow(workspace) -> None:
    body = "今天的想法足足超过二十个字，用于打卡与发布测试。"
    _save(
        workspace,
        Draft(slug="pin-1", title="", kind=ContentKind.PIN, body=body, status="ready"),
    )
    bridge = FakeBridge()
    bridge.eval_queue = [
        {"opened": True},
        {"ignored": True},  # setvar
        {"ok": True, "len": len(body)},  # DraftJS 注入确认
        {"bodyLen": len(body)},
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "pin-1")
    pub.begin(draft, gate_at="2026-10-01T21:00:00")
    assert pub.fill(draft).state == PublishState.FILLED
    pub.hand_to_human()
    bridge.evaluate = lambda code: {"type": "string", "value": "https://www.zhihu.com/pin/777"}  # type: ignore[method-assign]
    result = pub.confirm(workspace, day=date(2026, 10, 1), now=CLOCK)
    assert "/pin/777" in result.published_url


def test_confirm_wrong_url_blocks(workspace) -> None:
    body = "专栏正文内容。" * 10
    _save(
        workspace,
        Draft(slug="art-2", title="第二篇", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    bridge = FakeBridge()
    bridge.eval_queue = [
        {"ignored": True},  # setvar
        {"ok": True, "len": len(body)},
        {"title": "第二篇", "bodyLen": len(body)},
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "art-2")
    pub.begin(draft, gate_at="2026-10-01T21:00:00")
    pub.fill(draft)
    pub.hand_to_human()
    bridge.evaluate = lambda code: {"type": "string", "value": "https://zhuanlan.zhihu.com/write"}  # type: ignore[method-assign]
    with pytest.raises(PublishError, match="不像已发布"):
        pub.confirm(workspace, day=date(2026, 10, 1), now=CLOCK)
    assert pub.session.state == PublishState.AWAITING_HUMAN
    assert bridge.screenshots == []
    assert load_draft(workspace, "art-2").status == "ready"


def test_degrade_on_missing_title_selector(workspace) -> None:
    body = "正文内容。" * 10
    _save(
        workspace,
        Draft(slug="art-3", title="第三篇", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    bridge = FakeBridge()
    bridge.fail_selectors.update(publisher_mod._TITLE_SELECTORS)
    bridge.eval_queue = [{"ok": 1}]  # 剪贴板 evaluate
    pub = Publisher(bridge)
    draft = load_draft(workspace, "art-3")
    pub.begin(draft, gate_at="2026-10-01T21:00:00")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED
    assert outcome.detail["clipboard"] is True
    assert "手动" in outcome.detail["instruction"]
    with pytest.raises(PublishError):
        pub.confirm(workspace, day=date(2026, 10, 1))


def test_state_guard() -> None:
    pub = Publisher(FakeBridge())
    with pytest.raises(PublishError):
        pub.hand_to_human()


# ---------------- begin 入参校验 ----------------


def _begin_draft(**over: object) -> Draft:
    base: dict[str, object] = dict(
        slug="d1",
        title="标题",
        kind=ContentKind.ARTICLE,
        body="正文内容。" * 20,
        status="ready",
    )
    base.update(over)
    return Draft(**base)  # type: ignore[arg-type]


def test_begin_answer_requires_question_url() -> None:
    with pytest.raises(PublishError, match="问题 URL"):
        Publisher(FakeBridge()).begin(
            _begin_draft(kind=ContentKind.ANSWER, question_url="  "), gate_at="g"
        )


def test_begin_article_requires_title() -> None:
    with pytest.raises(PublishError, match="必须有标题"):
        Publisher(FakeBridge()).begin(_begin_draft(title="  "), gate_at="g")


def test_begin_rejects_non_ready() -> None:
    with pytest.raises(PublishError, match="draft 状态"):
        Publisher(FakeBridge()).begin(_begin_draft(status="draft"), gate_at="g")


# ---------------- 填充失败路径与降级 ----------------


class _RawBridge(FakeBridge):
    """evaluate 依次返回裸 value（不经 JSON 包装），便于构造坏回读。"""

    def __init__(self, values: list[str]) -> None:
        super().__init__()
        self._values = list(values)

    def evaluate(self, code: str) -> dict:
        self.eval_calls.append(code)
        if "getBoundingClientRect" in code:  # 定位探测不消耗裸值队列
            return self._locate_reply()
        return {"type": "string", "value": self._values.pop(0)}


class _NavFailBridge(FakeBridge):
    def navigate(self, *a: object, **k: object) -> dict:
        raise BridgeError("nav down")


def test_degrade_when_navigate_raises(workspace) -> None:
    _save(workspace, _begin_draft(slug="nav"))
    bridge = _NavFailBridge()
    pub = Publisher(bridge)
    draft = load_draft(workspace, "nav")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED
    assert outcome.detail["target_url"] == ARTICLE_WRITE_URL


def test_article_missing_body_editor_degrades(workspace) -> None:
    _save(workspace, _begin_draft(slug="nobody"))
    bridge = FakeBridge()
    bridge.fail_selectors.update(publisher_mod._BODY_SELECTORS)
    bridge.eval_queue = [
        {"ignored": True},  # setvar
        {"ok": False, "why": "no-visible-editor"},  # 注入失败
        {"ok": 1},  # 剪贴板
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "nobody")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.DEGRADED


def test_article_title_readback_mismatch_degrades(workspace) -> None:
    _save(workspace, _begin_draft(slug="tm", title="正确标题"))
    bridge = _RawBridge(
        [
            "1",
            json.dumps({"ok": True, "len": 999}),
            json.dumps({"title": "别的标题", "bodyLen": 999}),
            "{}",
        ]
    )
    pub = Publisher(bridge)
    draft = load_draft(workspace, "tm")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "标题回读" in outcome.detail["reason"]


def test_article_body_readback_short_degrades(workspace) -> None:
    _save(workspace, _begin_draft(slug="bs"))
    bridge = _RawBridge(
        [
            "1",
            json.dumps({"ok": True, "len": 999}),
            json.dumps({"title": "标题", "bodyLen": 3}),
            "{}",
        ]
    )
    pub = Publisher(bridge)
    draft = load_draft(workspace, "bs")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "正文回读" in outcome.detail["reason"]


def test_readback_unparseable_degrades(workspace) -> None:
    _save(workspace, _begin_draft(slug="rb"))
    bridge = _RawBridge(["1", json.dumps({"ok": True, "len": 999}), "这不是JSON", "{}"])
    pub = Publisher(bridge)
    draft = load_draft(workspace, "rb")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.DEGRADED


def _answer_draft(slug: str = "a1") -> Draft:
    return _begin_draft(
        slug=slug,
        title="某问题",
        kind=ContentKind.ANSWER,
        question_url="https://www.zhihu.com/question/999",
    )


def test_answer_bad_entry_json_treated_as_no_entry(workspace) -> None:
    _save(workspace, _answer_draft("a-bad"))
    body_len = len(load_draft(workspace, "a-bad").body)
    bridge = _RawBridge(
        [
            "garbage-not-json",
            "1",
            json.dumps({"ok": True, "len": body_len}),
            json.dumps({"url": "https://www.zhihu.com/question/999", "bodyLen": body_len}),
        ]
    )
    pub = Publisher(bridge)
    draft = load_draft(workspace, "a-bad")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.FILLED


def test_answer_missing_editor_degrades(workspace) -> None:
    _save(workspace, _answer_draft("a-noedit"))
    bridge = FakeBridge()
    bridge.fail_selectors.update(publisher_mod._BODY_SELECTORS)
    bridge.eval_queue = [
        {"clicked": True},
        {"ignored": True},  # setvar
        {"ok": False, "why": "no-visible-editor"},  # 注入失败
        {"ok": 1},  # 剪贴板
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "a-noedit")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.DEGRADED


def test_answer_readback_wrong_url_degrades(workspace) -> None:
    _save(workspace, _answer_draft("a-url"))
    bridge = _RawBridge(
        [
            json.dumps({"clicked": True}),
            "1",
            json.dumps({"ok": True, "len": 999}),
            json.dumps({"url": "https://zhihu.com/", "bodyLen": 999}),
            "{}",
        ]
    )
    pub = Publisher(bridge)
    draft = load_draft(workspace, "a-url")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "不在问题页" in outcome.detail["reason"]


def test_answer_readback_mismatched_question_id_degrades(workspace) -> None:
    _save(workspace, _answer_draft("a-qid"))
    bridge = _RawBridge(
        [
            json.dumps({"clicked": True}),
            "1",
            json.dumps({"ok": True, "len": 999}),
            json.dumps({"url": "https://www.zhihu.com/question/123", "bodyLen": 999}),
            "{}",
        ]
    )
    pub = Publisher(bridge)
    draft = load_draft(workspace, "a-qid")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "问题 ID" in outcome.detail["reason"]


def test_answer_readback_short_degrades(workspace) -> None:
    _save(workspace, _answer_draft("a-short"))
    bridge = _RawBridge(
        [
            json.dumps({"clicked": True}),
            "1",
            json.dumps({"ok": True, "len": 999}),
            json.dumps({"url": "https://www.zhihu.com/question/999", "bodyLen": 2}),
            "{}",
        ]
    )
    pub = Publisher(bridge)
    draft = load_draft(workspace, "a-short")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "回读字数" in outcome.detail["reason"]


def test_pin_fill_short_body_guarded() -> None:
    # begin 之后草稿被异常截短的防御路径
    pub = Publisher(FakeBridge())
    with pytest.raises(PublishError, match="20"):
        pub._fill_pin(Draft(slug="p", title="", kind=ContentKind.PIN, body="短"))


def test_pin_missing_editor_degrades(workspace) -> None:
    body = "今天的想法足足超过二十个字，用于打卡与发布测试。"
    _save(
        workspace,
        Draft(slug="pin-noedit", title="", kind=ContentKind.PIN, body=body, status="ready"),
    )
    bridge = FakeBridge()
    bridge.fail_selectors.update(publisher_mod._PIN_SELECTORS)
    bridge.eval_queue = [
        {"opened": True},
        {"ignored": True},  # setvar
        {"ok": False, "why": "no-visible-editor"},  # 注入失败
        {"ok": 1},
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "pin-noedit")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.DEGRADED


def test_pin_entry_not_found_degrades(workspace) -> None:
    body = "今天的想法足足超过二十个字，用于打卡与发布测试。"
    _save(
        workspace,
        Draft(slug="pin-noentry", title="", kind=ContentKind.PIN, body=body, status="ready"),
    )
    bridge = FakeBridge()
    bridge.eval_queue = [{"opened": False}]  # 首页未出现想法入口
    pub = Publisher(bridge)
    draft = load_draft(workspace, "pin-noentry")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "想法输入框" in outcome.detail["reason"]
    # 入口都没打开时不应尝试任何填充
    assert bridge.fills == []


def test_pin_readback_short_degrades(workspace) -> None:
    body = "今天的想法足足超过二十个字，用于打卡与发布测试。"
    _save(
        workspace,
        Draft(slug="pin-rs", title="", kind=ContentKind.PIN, body=body, status="ready"),
    )
    bridge = _RawBridge(
        [
            json.dumps({"opened": True}),
            "1",
            json.dumps({"ok": True, "len": 999}),
            json.dumps({"bodyLen": 5}),
            "{}",
        ]
    )
    pub = Publisher(bridge)
    draft = load_draft(workspace, "pin-rs")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "不足 20" in outcome.detail["reason"]


class _ClipboardFailBridge(FakeBridge):
    """第一次 evaluate（回读）返回偏少字数触发降级，第二次（剪贴板）抛错。"""

    def __init__(self) -> None:
        super().__init__()
        self._n = 0

    def evaluate(self, code: str) -> dict:
        self.eval_calls.append(code)
        if "getBoundingClientRect" in code:  # 先发生的标题等待探测
            return self._locate_reply()
        self._n += 1
        if self._n == 1:
            return {"type": "string", "value": json.dumps({"title": "标题", "bodyLen": 1})}
        raise BridgeError("clipboard blocked")


def test_degrade_clipboard_failure_recorded(workspace) -> None:
    _save(workspace, _begin_draft(slug="cf"))
    pub = Publisher(_ClipboardFailBridge())
    draft = load_draft(workspace, "cf")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED
    assert outcome.detail["clipboard"] is False and "手动复制" in outcome.detail["instruction"]


def test_fill_body_prefers_committed_draftjs_injection(workspace) -> None:
    # 真实冒烟教训：bridge.fill 只改 DOM 会被 DraftJS 回滚，
    # 注入成功时绝不应再调用 fill。
    body = "提交式注入的正文内容，长度足够通过回读。"
    bridge = FakeBridge()
    bridge.eval_queue = [
        {"ignored": True},  # setvar evaluate（结果不用）
        {"ok": True, "selector": ".public-DraftEditor-content", "len": len(body)},
    ]
    pub = Publisher(bridge)
    hit = pub._fill_body(publisher_mod._BODY_SELECTORS, body)
    assert hit is not None and hit[1] == "draftjs-inject"
    assert bridge.fills == []


def test_fill_body_falls_back_to_bridge_fill(workspace) -> None:
    body = "注入失败时退回 bridge.fill 的正文内容，长度足够。"
    _save(
        workspace,
        Draft(slug="fb", title="回退", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    bridge = FakeBridge()
    bridge.eval_queue = [
        {"ignored": True},
        {"ok": False, "why": "no-visible-editor"},
    ]
    pub = Publisher(bridge)
    pub.begin(load_draft(workspace, "fb"), gate_at="g")
    hit = pub._fill_body(publisher_mod._BODY_SELECTORS, body)
    assert hit is not None and hit[1] == "contenteditable"
    assert bridge.fills[0][1] == body


def test_real_daemon_fill_selectors_avoid_quoted_attributes() -> None:
    # webbridge v1.11.6 真实冒烟：fill 对 [attr='x'] 类选择器抛 SyntaxError，
    # 首选选择器必须是纯 class，保证真实守护端首轮即可命中。
    assert publisher_mod._BODY_SELECTORS[0] == ".public-DraftEditor-content"
    assert publisher_mod._PIN_SELECTORS[0] == ".DraftEditor-root .public-DraftEditor-content"
    for selectors in (publisher_mod._BODY_SELECTORS, publisher_mod._PIN_SELECTORS):
        assert "[" not in selectors[0]
    assert publisher_mod.ARTICLE_WRITE_URL == "https://zhuanlan.zhihu.com/write"


def test_no_final_publish_button_click_in_source() -> None:
    src = Path(publisher_mod.__file__).read_text(encoding="utf-8")
    # 编排器只允许 fill / evaluate；不得出现 client.click（最终按钮一律用户点）
    assert "client.click(" not in src
    # 编辑入口白名单只包含回答类入口
    assert "写回答" in src
    forbidden = ["发布文章'", "发布回答'", "发布想法'", "发表回答", "立即发布"]
    for token in forbidden:
        assert token not in src


# ---------------- CDP 受信输入（真实冒烟定稿）----------------


class CdpFakeBridge(FakeBridge):
    """模拟支持 chrome.debugger cdp 通道的真实守护端。"""

    def __init__(self, *, raises: bool = False) -> None:
        super().__init__()
        self.cdp_calls: list[tuple[str, dict]] = []
        self._raises = raises
        self.cdp = self._do_cdp  # 覆盖 None 占位

    def _do_cdp(self, method: str, params: dict | None = None) -> dict:
        self.cdp_calls.append((method, params or {}))
        if self._raises:
            raise BridgeError("debugger unavailable")
        return {"ok": True}


_FOCUSED = {"tag": "div", "ce": "true", "cls": "notranslate public-DraftEditor-content"}


def _cdp_methods(bridge: CdpFakeBridge) -> list[str]:
    return [m for m, _ in bridge.cdp_calls]


def test_cdp_article_happy_path_chunked_trusted_input(workspace) -> None:
    body = "（知乎打卡工作台自动填充冒烟测试，本人确认发布后立即删除。）" * 2
    _save(
        workspace,
        Draft(slug="cdp-art", title="冒烟", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    bridge = CdpFakeBridge()
    bridge.eval_queue = [
        _FOCUSED,  # 点击后 activeElement 必须是 contenteditable
        {"len": len(body)},  # 受信上屏后回读
        {"title": "冒烟", "bodyLen": len(body)},  # 总回读
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "cdp-art")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.FILLED
    assert outcome.detail["body_mode"] == "cdp-insert"
    methods = _cdp_methods(bridge)
    assert "Page.bringToFront" in methods
    assert "Input.dispatchMouseEvent" in methods
    # 分块上屏：每块 ≤20 字（真实守护端整块长文本会截断）；60 字 → 3 块
    chunks = [p["text"] for m, p in bridge.cdp_calls if m == "Input.insertText"]
    assert len(chunks) == 3 and all(len(ch) <= publisher_mod._CDP_CHUNK for ch in chunks)
    assert "".join(chunks) == body
    # 先受信清空（Ctrl+A / Delete），防重试场景的半截残留
    key_methods = [p for m, p in bridge.cdp_calls if m == "Input.dispatchKeyEvent"]
    assert any(p.get("code") == "KeyA" and p.get("modifiers") == 2 for p in key_methods)
    assert any(p.get("code") == "Delete" for p in key_methods)
    # 正文绝不再走只改 DOM 的 fill；只有标题 textarea 用 fill
    assert len(bridge.fills) == 1 and bridge.fills[0][0] in publisher_mod._TITLE_SELECTORS


def test_cdp_pin_flow(workspace) -> None:
    body = "（知乎打卡工作台自动填充冒烟测试，本人确认发布后立即删除。）"
    _save(
        workspace,
        Draft(slug="cdp-pin", title="", kind=ContentKind.PIN, body=body, status="ready"),
    )
    bridge = CdpFakeBridge()
    bridge.eval_queue = [
        {"opened": True},
        _FOCUSED,
        {"len": len(body)},
        {"bodyLen": len(body)},
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "cdp-pin")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.FILLED
    assert outcome.detail["body_mode"] == "cdp-insert"
    chunks = [p["text"] for m, p in bridge.cdp_calls if m == "Input.insertText"]
    assert "".join(chunks) == body


def test_cdp_focus_not_confirmed_degrades_without_synthetic_fill(workspace) -> None:
    # 窗口在 OS 后台时 CDP 点击不产生真实焦点：必须直接降级，
    # 绝不做 execCommand/bridge.fill 合成兜底（否则发空文）。
    body = "焦点不在正文时用于验证降级路径的正文内容，长度足够。"
    _save(
        workspace,
        Draft(slug="cdp-focus", title="焦点", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    bridge = CdpFakeBridge()
    unfocused = {"tag": "body", "ce": "null", "cls": ""}
    bridge.eval_queue = [
        unfocused, unfocused, unfocused,  # 焦点确认重试 3 次均失败
        {"ok": 1},  # 降级剪贴板
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "cdp-focus")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED
    assert "焦点" in outcome.detail["reason"]
    # 正文没有任何上屏与合成填充（标题 textarea 在正文前已填，属正常）
    assert "Input.insertText" not in _cdp_methods(bridge)
    assert all(s in publisher_mod._TITLE_SELECTORS for s, _ in bridge.fills)
    # 点击重试 3 次
    assert _cdp_methods(bridge).count("Input.dispatchMouseEvent") == 6


def test_cdp_readback_short_degrades(workspace) -> None:
    body = "受信上屏后回读字数不足时必须降级的正文内容，长度足够。"
    _save(
        workspace,
        Draft(slug="cdp-short", title="短回读", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    bridge = CdpFakeBridge()
    bridge.eval_queue = [
        _FOCUSED,
        {"len": 3},  # 模型未接收
        {"ok": 1},  # 降级剪贴板
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "cdp-short")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED
    assert "回读字数" in outcome.detail["reason"]
    assert "Input.insertText" in _cdp_methods(bridge)  # 尝试过上屏


def test_cdp_unavailable_falls_back_to_legacy_injection(workspace) -> None:
    # 旧守护端/调试器拒绝（cdp 抛 BridgeError）：退回 execCommand 注入旧兜底
    body = "cdp 不可用时退回旧注入路径的正文内容，长度足够。"
    bridge = CdpFakeBridge(raises=True)
    bridge.eval_queue = [
        {"ignored": True},  # setvar
        {"ok": True, "selector": ".public-DraftEditor-content", "len": len(body)},
    ]
    pub = Publisher(bridge)
    hit = pub._fill_body(publisher_mod._BODY_SELECTORS, body)
    assert hit is not None and hit[1] == "draftjs-inject"


class _PinConfirmBridge(FakeBridge):
    """confirm 阶段脚本化：location.href 序列、pin 反查序列、个人主页链接。"""

    def __init__(self, *, href_seq, find_seq, profile="notset"):
        super().__init__()
        self._hrefs = iter(href_seq)
        self._finds = iter(find_seq)
        self._profile = profile

    def evaluate(self, code):  # type: ignore[override]
        self.eval_calls.append(code)
        if code == "location.href":
            return {"type": "string", "value": next(self._hrefs)}
        if 'a[href*="/pin/"]' in code and "needle" in code:
            return {"type": "string", "value": json.dumps({"href": next(self._finds)}, ensure_ascii=False)}
        if 'a[href*="/people/"]' in code:
            return {"type": "string", "value": json.dumps({"href": self._profile})}
        return super().evaluate(code)


_PIN_BODY = "（知乎打卡工作台自动填充冒烟测试，本人确认发布后立即删除。）"
_PIN_URL = "https://www.zhihu.com/pin/777"


def _pin_to_awaiting(workspace, bridge: FakeBridge) -> "Publisher":
    _save(workspace, Draft(slug="pin-cf", title="", kind=ContentKind.PIN,
                           body=_PIN_BODY, status="ready"))
    bridge.eval_queue = [
        {"opened": True},
        {"ignored": True},
        {"ok": True, "len": len(_PIN_BODY)},
        {"bodyLen": len(_PIN_BODY)},
    ]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "pin-cf")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.FILLED
    pub.hand_to_human()
    return pub


def test_confirm_pin_resolves_from_home_feed(workspace, monkeypatch) -> None:
    # 真实冒烟：想法发布后停在首页，弹窗/feed 里按正文前缀反查到 pin
    monkeypatch.setattr(publisher_mod.time, "sleep", lambda _s: None)
    bridge = _PinConfirmBridge(href_seq=["https://www.zhihu.com/", _PIN_URL],
                               find_seq=[_PIN_URL])
    pub = _pin_to_awaiting(workspace, bridge)
    result = pub.confirm(workspace, day=date(2026, 9, 28), now=CLOCK)
    assert result.state == PublishState.CONFIRMED
    assert result.published_url == _PIN_URL
    assert any("/pin/777" in u for u in bridge.navigated)
    assert load_draft(workspace, "pin-cf").status == "published"
    assert load_entry(workspace, date(2026, 9, 28)).contents[-1].url == _PIN_URL


def test_confirm_pin_resolves_via_profile_pins(workspace, monkeypatch) -> None:
    # 首页反查 4 次未命中 → 个人主页想法列表第 3 次轮询命中
    monkeypatch.setattr(publisher_mod.time, "sleep", lambda _s: None)
    bridge = _PinConfirmBridge(
        href_seq=["https://www.zhihu.com/", _PIN_URL],
        find_seq=[None] * 4 + [None, None, _PIN_URL],
        profile="https://www.zhihu.com/people/xinetzone",
    )
    pub = _pin_to_awaiting(workspace, bridge)
    result = pub.confirm(workspace, day=date(2026, 9, 28), now=CLOCK)
    assert result.published_url == _PIN_URL
    assert "https://www.zhihu.com/people/xinetzone/pins" in bridge.navigated


def test_confirm_pin_unresolved_still_blocks(workspace, monkeypatch) -> None:
    # 首页与个人主页都找不到（如发布失败/误点）：维持阻断，不得误确认
    monkeypatch.setattr(publisher_mod.time, "sleep", lambda _s: None)
    bridge = _PinConfirmBridge(
        href_seq=["https://www.zhihu.com/"],
        find_seq=[None] * 24,
        profile=None,
    )
    pub = _pin_to_awaiting(workspace, bridge)
    with pytest.raises(PublishError, match="不像已发布"):
        pub.confirm(workspace, day=date(2026, 9, 28), now=CLOCK)
    assert bridge.screenshots == []
    assert load_draft(workspace, "pin-cf").status == "ready"


def test_cdp_editor_not_found_falls_back_to_legacy(workspace) -> None:
    body = "页面没有可见编辑器时退回旧路径的正文内容，长度足够。"
    bridge = CdpFakeBridge()
    bridge.auto_located = False  # 定位轮询超时：cdp 一次都不应被调用
    bridge.eval_queue = [
        {"ignored": True},
        {"ok": False, "why": "no-visible-editor"},
    ]
    pub = Publisher(bridge)
    hit = pub._fill_body(publisher_mod._BODY_SELECTORS, body)
    assert hit is not None and hit[1] == "contenteditable"
    assert bridge.fills[0][1] == body
    assert "Page.bringToFront" not in _cdp_methods(bridge)
