"""TR-9 / TR-10 / TR-11：安全门禁、页面渲染、打卡勾选、发布向导端到端。"""

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from zhihu_checkin_hub.config import Config
from zhihu_checkin_hub.errors import WorkspaceError
from zhihu_checkin_hub.storage.drafts import Draft, load_draft, save_draft
from zhihu_checkin_hub.storage.entries import ContentKind, load_entry
from zhihu_checkin_hub.storage.tracker import parse_tracker
from zhihu_checkin_hub.web.app import create_app
from zhihu_checkin_hub.web.security import SingleInstanceLock, is_local_origin, verify_post

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"
SRC = Path(__file__).resolve().parents[1] / "src"


class ScriptedBridge:
    """发布向导用：队列式 evaluate、可配置填充失败、可配置最终 href。"""

    def __init__(self) -> None:
        self.eval_queue: list[dict] = []
        self.fail_all_fills = False
        self.href = ""
        self.screenshots: list[dict] = []

    def navigate(self, url, **_):
        return {"success": True, "url": url}

    def evaluate(self, code):
        if code == "location.href":
            return {"type": "string", "value": self.href}
        # 标题/编辑器挂载等待探测：自动应答，不消费队列
        if "getBoundingClientRect" in code:
            return {"type": "string", "value": json.dumps(
                {"ok": True, "selector": ".public-DraftEditor-content", "x": 1, "y": 1})}
        if self.eval_queue:
            return {"type": "string", "value": json.dumps(self.eval_queue.pop(0), ensure_ascii=False)}
        return {"type": "string", "value": "{}"}

    def fill(self, selector, value):
        if self.fail_all_fills:
            from zhihu_checkin_hub.errors import BridgeError

            raise BridgeError("no selector")
        return {"success": True, "mode": "contenteditable"}

    def screenshot(self, **args):
        self.screenshots.append(args)
        return {"format": "png", "path": args.get("path"), "sizeBytes": 1}

    def health(self):
        from zhihu_checkin_hub.publishing.bridge import HealthReport, HealthState

        return HealthReport(HealthState.READY, "ok")


@pytest.fixture()
def workbench(tmp_path: Path) -> Path:
    d = tmp_path / "zhihu-monetization"
    d.mkdir()
    shutil.copy(FIXTURE, d / "tracker.md")
    return d


@pytest.fixture()
def cfg(workbench: Path) -> Config:
    from zhihu_checkin_hub.storage.workspace import open_workspace

    return Config(workspace=open_workspace(workbench), host="127.0.0.1", port=17299)


@pytest.fixture()
def bridge():
    return ScriptedBridge()


@pytest.fixture()
def client(cfg: Config, bridge: ScriptedBridge) -> TestClient:
    return TestClient(create_app(cfg, bridge=bridge))


def _csrf(client: TestClient) -> str:
    client.get("/")
    return client.cookies.get("zhihu_checkin_csrf")


# ---------------- TR-9 安全 ----------------


def test_post_without_csrf_cookie_rejected(cfg: Config, bridge: ScriptedBridge) -> None:
    fresh = TestClient(create_app(cfg, bridge=bridge))
    r = fresh.post("/checkin/checkoff", data={"item_id": "W1-1", "day": "2026-09-28"})
    assert r.status_code == 403


def test_post_wrong_csrf_rejected(client: TestClient) -> None:
    token = _csrf(client)
    r = client.post(
        "/checkin/checkoff",
        data={"_csrf": "wrong", "item_id": "W1-1", "day": "2026-09-28"},
    )
    assert r.status_code == 403
    assert token  # 已拿到 cookie


def test_post_foreign_origin_rejected(client: TestClient) -> None:
    token = _csrf(client)
    r = client.post(
        "/checkin/checkoff",
        data={"_csrf": token, "item_id": "W1-1", "day": "2026-09-28"},
        headers={"Origin": "https://evil.example.com"},
    )
    assert r.status_code == 403


def test_host_must_be_loopback(workbench: Path) -> None:
    from zhihu_checkin_hub.config import load_config
    from zhihu_checkin_hub.errors import WorkspaceError as WE

    with pytest.raises(WE):
        load_config(cli_workspace=workbench, host="0.0.0.0")


def test_single_instance_lock_blocks_second_process(workbench: Path) -> None:
    lock_path = workbench / "local" / ".serve.lock"
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    code = (
        "import time,sys;"
        "from pathlib import Path;"
        "from zhihu_checkin_hub.web.security import SingleInstanceLock;"
        f"l=SingleInstanceLock(Path({str(lock_path)!r}));l.acquire_nonblocking();time.sleep(6)"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        import time

        # 等子进程拿到锁（文件出现且写入占位字节、进程存活）
        for _ in range(60):
            if lock_path.exists() and lock_path.stat().st_size >= 1 and proc.poll() is None:
                break
            time.sleep(0.1)
        assert proc.poll() is None, f"持锁子进程意外退出：{proc.stderr.read().decode('utf-8', 'replace')}"
        time.sleep(0.3)
        with pytest.raises(WorkspaceError, match="另一个"):
            SingleInstanceLock(lock_path).acquire_nonblocking()
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_lock_release_allows_reacquire(workbench: Path) -> None:
    lock = SingleInstanceLock(workbench / "local" / ".serve.lock")
    lock.acquire_nonblocking()
    lock.release()
    lock.release()  # 幂等：未持锁时直接返回
    lock.acquire_nonblocking()  # 释放后同进程可重新获取
    lock.release()


class _Req:
    def __init__(self, headers: dict[str, str]) -> None:
        self.headers = dict(headers)


def test_local_origin_predicate() -> None:
    assert is_local_origin("http://127.0.0.1:8765/")
    assert is_local_origin("http://localhost:8765/publish/fill")
    assert is_local_origin("http://[::1]:8765/")
    assert not is_local_origin("https://evil.example.com/")
    assert not is_local_origin("http://127.0.0.1.evil.com/")


def test_verify_post_rejects_foreign_origin_and_referer() -> None:
    ok, reason = verify_post(_Req({"origin": "http://127.0.0.1:8765/"}), "tok")
    assert ok and not reason
    ok, reason = verify_post(_Req({"origin": "https://evil.example.com"}), "tok")
    assert not ok and "Origin" in reason
    ok, reason = verify_post(_Req({"referer": "https://evil.example.com/x"}), "tok")
    assert not ok and "Referer" in reason
    ok, _ = verify_post(_Req({"referer": "http://localhost:8765/checkin"}), "tok")
    assert ok
    ok, reason = verify_post(_Req({}), "tok")
    assert ok
    ok, reason = verify_post(_Req({}), None)
    assert not ok and "CSRF Cookie" in reason


# ---------------- TR-10 页面与核心操作 ----------------


def test_pages_render(client: TestClient) -> None:
    today = date.today().isoformat()
    home = client.get("/")
    assert home.status_code == 200 and today in home.text
    checkin = client.get("/checkin")
    assert checkin.status_code == 200
    assert "W1-1" in checkin.text and "科学季报名" in checkin.text
    assert client.get("/records").status_code == 200
    assert client.get("/drafts").status_code == 200
    assert client.get("/publish").status_code == 200


def test_checkin_entry_and_checkoff_e2e(
    client: TestClient, workbench: Path
) -> None:
    token = _csrf(client)
    r = client.post(
        "/checkin/entry",
        data={
            "_csrf": token,
            "day": "2026-09-28",
            "kind": ["answer"],
            "char_count": ["320"],
            "url": [""],
            "question_url": [""],
            "draft_slug": [""],
            "interaction": ["upvote", "comment", "follow"],
            "interaction_target": ["", "", "", "", ""],
            "note": "底盘完成",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    entry = load_entry_path(workbench)
    text = (workbench / "local" / "entries" / "2026-09-28.yaml").read_text(encoding="utf-8")
    assert "320" in text and "底盘完成" in text

    r2 = client.post(
        "/checkin/checkoff",
        data={"_csrf": token, "item_id": "W1-1", "day": "2026-09-28"},
        follow_redirects=False,
    )
    assert r2.status_code == 303
    doc = parse_tracker(workbench / "tracker.md")
    assert doc.get("W1-1").checked
    assert list((workbench / "local" / "backups").glob("tracker-*.md"))


def load_entry_path(workbench: Path):
    from zhihu_checkin_hub.storage.workspace import open_workspace

    return load_entry(open_workspace(workbench), date(2026, 9, 28))


def test_draft_create_and_edit_page(client: TestClient, workbench: Path) -> None:
    token = _csrf(client)
    r = client.post(
        "/drafts/save",
        data={
            "_csrf": token,
            "slug": "",
            "title": "第一篇回答",
            "kind": "answer",
            "body": "本人撰写的回答正文内容，长度超过一百字。" * 5,
            "question_url": "https://www.zhihu.com/question/999",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    page = client.get("/drafts/第一篇回答")
    assert page.status_code == 200 and "本人撰写" in page.text


def test_records_posts(client: TestClient) -> None:
    token = _csrf(client)
    r = client.post(
        "/records/earning",
        data={"_csrf": token, "day": "2026-09-30", "action": "answer", "salt_raw": "120", "note": ""},
        follow_redirects=False,
    )
    assert r.status_code == 303
    page = client.get("/records")
    assert "120" in page.text


# ---------------- TR-11 发布向导 ----------------


def _ready_article(workbench: Path) -> str:
    from zhihu_checkin_hub.storage.workspace import open_workspace

    ws = open_workspace(workbench)
    body = "专栏正文内容，长度足够通过回读门槛。" * 6
    save_draft(
        ws,
        Draft(slug="art-web", title="向导文章", kind=ContentKind.ARTICLE, body=body, status="ready"),
    )
    return body


def test_gate_reject_returns_422(client: TestClient, workbench: Path) -> None:
    _ready_article(workbench)
    token = _csrf(client)
    r = client.post(
        "/publish/gate",
        data={
            "_csrf": token,
            "slug": "art-web",
            "deletion_note": "x",
            "ratio_note": "y",
            # 复选全缺
        },
    )
    assert r.status_code == 422


def test_fill_before_gate_is_409(client: TestClient, workbench: Path) -> None:
    _ready_article(workbench)
    token = _csrf(client)
    r = client.post("/publish/fill", data={"_csrf": token, "slug": "art-web"})
    assert r.status_code == 409


def test_full_wizard_flow(client: TestClient, bridge: ScriptedBridge, workbench: Path) -> None:
    body = _ready_article(workbench)
    token = _csrf(client)
    # ② 门全绿
    gate = client.post(
        "/publish/gate",
        data={
            "_csrf": token,
            "slug": "art-web",
            "deletion_tested": "1",
            "deletion_note": "已做删稿测试",
            "ratio_selfcheck": "1",
            "ratio_note": "常规创作",
            "clauses": ["none"],
            "edge_confirmed": "1",
            "edge_note": "",
        },
        follow_redirects=False,
    )
    assert gate.status_code == 303

    # ④ 填充（回读队列）
    bridge.eval_queue = [
        {"ignored": True},
        {"ok": True, "len": len(body)},
        {"title": "向导文章", "bodyLen": len(body)},
    ]
    fill = client.post("/publish/fill", data={"_csrf": token, "slug": "art-web"})
    assert fill.status_code == 200
    assert fill.json()["state"] == "awaiting_human"

    # 本人发布后确认
    bridge.href = "https://zhuanlan.zhihu.com/p/4242"
    confirm = client.post("/publish/confirm", data={"_csrf": token, "slug": "art-web"})
    assert confirm.status_code == 200
    data = confirm.json()
    assert data["state"] == "confirmed" and data["published_url"].endswith("/p/4242")
    assert bridge.screenshots and "screenshots" in bridge.screenshots[0]["path"]

    draft = load_draft_path(workbench, "art-web")
    assert draft.status == "published"
    entry = load_entry(
        __import__("zhihu_checkin_hub.storage.workspace", fromlist=["open_workspace"]).open_workspace(
            workbench
        ),
        date.today(),
    )
    assert any(c.url.endswith("/p/4242") for c in entry.contents)


def load_draft_path(workbench: Path, slug: str):
    from zhihu_checkin_hub.storage.workspace import open_workspace

    return load_draft(open_workspace(workbench), slug)


def test_degraded_flow_writes_nothing(
    client: TestClient, bridge: ScriptedBridge, workbench: Path
) -> None:
    _ready_article(workbench)
    token = _csrf(client)
    client.post(
        "/publish/gate",
        data={
            "_csrf": token,
            "slug": "art-web",
            "deletion_tested": "1",
            "deletion_note": "已做",
            "ratio_selfcheck": "1",
            "ratio_note": "常规",
            "clauses": ["none"],
            "edge_confirmed": "1",
        },
        follow_redirects=False,
    )
    bridge.fail_all_fills = True
    r = client.post("/publish/fill", data={"_csrf": token, "slug": "art-web"})
    assert r.status_code == 200
    assert r.json()["state"] == "degraded"
    assert "手动" in r.json()["detail"]["instruction"]
    # 草稿未 published、当日无内容回填
    from zhihu_checkin_hub.storage.workspace import open_workspace

    ws = open_workspace(workbench)
    assert load_draft(ws, "art-web").status == "ready"
    assert load_entry(ws, date.today()).contents == []


_GATE_OK = {
    "deletion_tested": "1",
    "deletion_note": "已做",
    "ratio_selfcheck": "1",
    "ratio_note": "常规",
    "clauses": ["none"],
    "edge_confirmed": "1",
}


def test_fill_slug_must_match_gated_draft(
    client: TestClient, workbench: Path
) -> None:
    from zhihu_checkin_hub.storage.workspace import open_workspace

    _ready_article(workbench)
    ws = open_workspace(workbench)
    save_draft(
        ws,
        Draft(
            slug="art-other",
            title="另一篇",
            kind=ContentKind.ARTICLE,
            body="另一篇正文，长度足够通过回读门槛。" * 6,
            status="ready",
        ),
    )
    token = _csrf(client)
    gated = client.post(
        "/publish/gate",
        data={"_csrf": token, "slug": "art-web", **_GATE_OK},
        follow_redirects=False,
    )
    assert gated.status_code == 303
    # 过门的是 art-web，拿 art-other 调填充必须拒绝（门留痕与发布草稿绑定）
    r = client.post("/publish/fill", data={"_csrf": token, "slug": "art-other"})
    assert r.status_code == 409


def test_pin_confirm_requires_explicit_image_choice(
    client: TestClient, bridge: ScriptedBridge, workbench: Path
) -> None:
    from zhihu_checkin_hub.storage.workspace import open_workspace

    ws = open_workspace(workbench)
    save_draft(
        ws,
        Draft(
            slug="pin-web",
            title="",
            kind=ContentKind.PIN,
            body="这是一条足够长的想法正文，用于验证图片确认门。",
            status="ready",
        ),
    )
    token = _csrf(client)
    gated = client.post(
        "/publish/gate",
        data={"_csrf": token, "slug": "pin-web", **_GATE_OK},
        follow_redirects=False,
    )
    assert gated.status_code == 303
    bridge.eval_queue = [
        {"opened": True},
        {"ignored": True},
        {"ok": True, "len": 28},
        {"bodyLen": 28},
    ]
    fill = client.post("/publish/fill", data={"_csrf": token, "slug": "pin-web"})
    assert fill.status_code == 200
    assert fill.json()["state"] == "awaiting_human"

    bridge.href = "https://www.zhihu.com/pin/777"
    missing = client.post(
        "/publish/confirm", data={"_csrf": token, "slug": "pin-web"}
    )
    assert missing.status_code == 422
    ok = client.post(
        "/publish/confirm",
        data={"_csrf": token, "slug": "pin-web", "pin_image": "none"},
    )
    assert ok.status_code == 200
    assert ok.json()["published_url"].endswith("/pin/777")
