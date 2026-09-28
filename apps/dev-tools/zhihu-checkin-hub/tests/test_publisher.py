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

    def navigate(self, url: str, *, group_title: str | None = None, **_: object) -> dict:
        self.navigated.append(url)
        return {"success": True, "url": url}

    def evaluate(self, code: str) -> dict:
        self.eval_calls.append(code)
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
    bridge.eval_queue = [{"title": "第一篇文章", "bodyLen": len(body)}]  # 回读
    pub = Publisher(bridge)
    # confirm 阶段需要裸字符串 value，单独插队
    draft = load_draft(workspace, "art-1")
    pub.begin(draft, gate_at="2026-10-01T21:00:00")

    outcome = pub.fill(draft)
    assert outcome.state == PublishState.FILLED
    assert bridge.navigated[-1] == ARTICLE_WRITE_URL
    assert bridge.fills[0][1] == "第一篇文章"
    assert bridge.fills[1][1] == body

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
    bridge.eval_queue = [{"bodyLen": len(body)}]
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
    bridge.eval_queue = [{"title": "第二篇", "bodyLen": len(body)}]
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
    bridge.eval_queue = [{"ok": 1}]  # 剪贴板
    pub = Publisher(bridge)
    draft = load_draft(workspace, "nobody")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.DEGRADED


def test_article_title_readback_mismatch_degrades(workspace) -> None:
    _save(workspace, _begin_draft(slug="tm", title="正确标题"))
    bridge = _RawBridge([json.dumps({"title": "别的标题", "bodyLen": 999}), "{}"])
    pub = Publisher(bridge)
    draft = load_draft(workspace, "tm")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "标题回读" in outcome.detail["reason"]


def test_article_body_readback_short_degrades(workspace) -> None:
    _save(workspace, _begin_draft(slug="bs"))
    bridge = _RawBridge([json.dumps({"title": "标题", "bodyLen": 3}), "{}"])
    pub = Publisher(bridge)
    draft = load_draft(workspace, "bs")
    pub.begin(draft, gate_at="g")
    outcome = pub.fill(draft)
    assert outcome.state == PublishState.DEGRADED and "正文回读" in outcome.detail["reason"]


def test_readback_unparseable_degrades(workspace) -> None:
    _save(workspace, _begin_draft(slug="rb"))
    bridge = _RawBridge(["这不是JSON", "{}"])
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
    bridge.eval_queue = [{"clicked": True}, {"ok": 1}]  # 入口点击 + 剪贴板
    pub = Publisher(bridge)
    draft = load_draft(workspace, "a-noedit")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.DEGRADED


def test_answer_readback_wrong_url_degrades(workspace) -> None:
    _save(workspace, _answer_draft("a-url"))
    bridge = _RawBridge(
        [json.dumps({"clicked": True}), json.dumps({"url": "https://zhihu.com/", "bodyLen": 999}), "{}"]
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
    bridge.eval_queue = [{"ok": 1}]
    pub = Publisher(bridge)
    draft = load_draft(workspace, "pin-noedit")
    pub.begin(draft, gate_at="g")
    assert pub.fill(draft).state == PublishState.DEGRADED


def test_pin_readback_short_degrades(workspace) -> None:
    body = "今天的想法足足超过二十个字，用于打卡与发布测试。"
    _save(
        workspace,
        Draft(slug="pin-rs", title="", kind=ContentKind.PIN, body=body, status="ready"),
    )
    bridge = _RawBridge([json.dumps({"bodyLen": 5}), "{}"])
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


def test_no_final_publish_button_click_in_source() -> None:
    src = Path(publisher_mod.__file__).read_text(encoding="utf-8")
    # 编排器只允许 fill / evaluate；不得出现 client.click（最终按钮一律用户点）
    assert "client.click(" not in src
    # 编辑入口白名单只包含回答类入口
    assert "写回答" in src
    forbidden = ["发布文章'", "发布回答'", "发布想法'", "发表回答", "立即发布"]
    for token in forbidden:
        assert token not in src
