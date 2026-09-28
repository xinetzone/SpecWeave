"""TR-12：安全/合规静态审计、依赖白名单、离线冒烟、入库卫生。

红线（AC-8/AC-10）：
- 不出现任何 LLM 生成 SDK/端点（openai、anthropic、chat/completions 等）；
- 不读写知乎账号凭证（document.cookie / z_c0 / 密码 / Access Secret）；
- 不调用知乎 CLI 的发布命令，也不出现 ``client.click(``（最终发布按钮只能人点）；
- 运行时写入全部落在工作区 ``local/``，真实工作区 ``local/`` 不产生 git 条目。
"""

import re
import shutil
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

import pytest

from zhihu_checkin_hub.config import Config
from zhihu_checkin_hub.publishing.bridge import BridgeClient, HealthState
from zhihu_checkin_hub.storage.checkoff import check_off
from zhihu_checkin_hub.storage.drafts import Draft, load_draft, save_draft, transition_status
from zhihu_checkin_hub.storage.entries import (
    ContentKind,
    ContentRecord,
    DayEntry,
    Interaction,
    save_entry,
)
from zhihu_checkin_hub.storage.records import add_earning
from zhihu_checkin_hub.storage.workspace import open_workspace
from zhihu_checkin_hub.web.app import create_app
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"
REPO_ROOT = ROOT.parents[2]  # apps/dev-tools/zhihu-checkin-hub -> 仓库根 SpecWeave

PY_TOKENS = [
    (r"import\s+openai|from\s+openai", "禁止接入 OpenAI SDK"),
    (r"import\s+anthropic|from\s+anthropic", "禁止接入 Anthropic SDK"),
    (r"chat/completions", "禁止调用 LLM 补全端点"),
    (r"api\.openai\.com|api\.anthropic\.com", "禁止访问 LLM 服务域名"),
    (r"document\.cookie", "禁止读取浏览器 cookie"),
    (r"z_c0", "禁止接触知乎登录凭证 z_c0"),
    (r"(?i)access[_-]?secret", "禁止接触 Access Secret"),
    (r"getpass|\bpassword\b", "禁止读取/存储密码"),
    (r"client\.click\(", "禁止 client.click（最终发布只能由用户本人点击）"),
    (r"""["']zhihu[a-z\-]*["']\s*,?\s*["'](answer|article|pin)["']""", "禁止 subprocess 调用知乎发布 CLI"),
]
TEMPLATE_TOKENS = [
    (r"document\.cookie", "模板禁止读取 cookie"),
    (r"querySelector[^;]*发布[^;]*\.click\(\)", "模板禁止自动点击任何「发布」按钮"),
    (r"openai|anthropic|chat/completions", "模板禁止出现 LLM 服务"),
]


def _scan(files: list[Path], tokens: list[tuple[str, str]]) -> None:
    offenders: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for pattern, why in tokens:
            if re.search(pattern, text):
                offenders.append(f"{path.relative_to(ROOT)}: {why}（/{pattern}/）")
    assert not offenders, "审计红线被触发：\n" + "\n".join(offenders)


def test_audit_python_sources_clean() -> None:
    _scan(sorted(SRC.rglob("*.py")), PY_TOKENS)


def test_audit_templates_clean() -> None:
    _scan(sorted((SRC / "zhihu_checkin_hub" / "web" / "templates").rglob("*.html")), TEMPLATE_TOKENS)


def test_dependencies_on_whitelist() -> None:
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = meta["project"]["dependencies"]
    allowed = {"fastapi", "uvicorn", "jinja2", "typer", "pyyaml", "httpx", "python-multipart"}
    names = {
        re.split(r"[<>=!~\[\s]", dep, maxsplit=1)[0].lower() for dep in declared
    }
    extra = names - allowed
    assert not extra, f"依赖白名单外的包：{extra}"
    # 构建后端按主仓库主权区统一约定
    assert meta["build-system"]["build-backend"] == "scikit_build_core.build"


@pytest.fixture()
def workbench(tmp_path: Path) -> Path:
    root = tmp_path / "zhihu-monetization"
    root.mkdir()
    shutil.copy(FIXTURE, root / "tracker.md")
    return root


def test_offline_smoke_full_write_flow(workbench: Path) -> None:
    """daemon 不存在：打卡/记录/草稿/勾选全流程仍可离线完成。"""
    ws = open_workspace(workbench)
    entry = DayEntry(
        day="2026-09-28",
        contents=[
            ContentRecord(kind=ContentKind.ANSWER, char_count=320, url="", question_url="q")
        ],
        interactions=[Interaction(kind=k, target="") for k in ("upvote", "comment", "follow")],
        note="离线冒烟",
    )
    save_entry(ws, entry)
    add_earning(ws, day="2026-09-28", action="answer", salt_raw="10")
    save_draft(
        ws,
        Draft(slug="smoke", title="冒烟", kind=ContentKind.ARTICLE, body="正文。" * 30),
    )
    assert transition_status(load_draft(ws, "smoke").status, "ready") == "ready"
    check_off(ws, "W1-1", when=date(2026, 9, 28))
    assert "- [x] 2026-09-28" in ws.tracker.read_text(encoding="utf-8")

    # Web 层在离线（无 bridge 注入）下也能起服务并渲染
    app = create_app(Config(workspace=ws, host="127.0.0.1", port=1), bridge=None)
    pages = TestClient(app)
    assert pages.get("/").status_code == 200
    assert pages.get("/publish").status_code == 200


def test_bridge_health_reports_daemon_down_offline() -> None:
    """指向关闭端口：健康检查必须稳定返回 daemon_down，而不是抛出原始异常。"""
    client = BridgeClient(endpoint="http://127.0.0.1:1", session="zhihu-checkin-hub", timeout=1.0)
    report = client.health()
    assert report.state == HealthState.DAEMON_DOWN


def test_real_workspace_local_remains_clean_in_git() -> None:
    """TR-12.3：真实工作区 local/ 不允许因测试产生任何 git 条目。"""
    target = REPO_ROOT / "projects" / "monetize" / "zhihu-monetization" / "local"
    if not (REPO_ROOT / ".git").exists():
        pytest.skip("不在 git 工作树内，跳过入库卫生检查")
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    rel = target.relative_to(REPO_ROOT).as_posix()
    hits = [line for line in proc.stdout.splitlines() if rel in line.replace("\\", "/")]
    assert not hits, f"真实工作区 local/ 出现 git 变更条目：{hits}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
