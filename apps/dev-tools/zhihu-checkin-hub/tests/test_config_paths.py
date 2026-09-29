"""TR-1.1：workspace 四分支守卫与配置优先级。"""

from pathlib import Path

import pytest

from zhihu_checkin_hub.config import load_config
from zhihu_checkin_hub.errors import WorkspaceError
from zhihu_checkin_hub.storage.workspace import (
    Workspace,
    _is_root_or_direct_child,
    open_workspace,
)


def test_open_valid_workspace_creates_local_dirs(workbench: Path) -> None:
    ws = open_workspace(workbench)
    assert isinstance(ws, Workspace)
    assert ws.tracker.is_file()
    for d in (
        ws.entries_dir,
        ws.posts_dir,
        ws.screenshots_dir,
        ws.backups_dir,
        ws.records_dir,
    ):
        assert d.is_dir()


def test_nonexistent_workspace_rejected(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError, match="不存在"):
        open_workspace(tmp_path / "no-such-dir")


def test_workspace_without_tracker_rejected(tmp_path: Path) -> None:
    plain = tmp_path / "plain-dir"
    plain.mkdir()
    with pytest.raises(WorkspaceError, match="tracker.md"):
        open_workspace(plain)


def test_path_is_file_rejected(tmp_path: Path) -> None:
    f = tmp_path / "a-file"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(WorkspaceError, match="不是目录"):
        open_workspace(f)


@pytest.mark.parametrize(
    "path,expected",
    [
        (Path("D:/"), True),
        (Path("C:/"), True),
        (Path("D:/.temp"), True),
        (Path("D:/spaces/SpecWeave"), False),
        (Path("/"), True),
        (Path("/tmp"), True),
    ],
)
def test_root_direct_child_guard(path: Path, expected: bool) -> None:
    assert _is_root_or_direct_child(path) is expected


def test_within_local_guard(workbench: Path, tmp_path: Path) -> None:
    ws = open_workspace(workbench)
    assert ws.ensure_within_local(ws.entries_dir / "x.yaml") == (
        ws.entries_dir / "x.yaml"
    ).resolve()
    with pytest.raises(WorkspaceError, match="越出 local"):
        ws.ensure_within_local(ws.root / "tracker.md")
    with pytest.raises(WorkspaceError, match="越出 local"):
        ws.ensure_within_local(ws.entries_dir / ".." / ".." / "evil.md")


def test_load_config_env_override(workbench: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZHIHU_CHECKIN_WORKSPACE", str(workbench))
    cfg = load_config(config_file=workbench / "nonexistent-config.yaml")
    assert cfg.workspace.root == workbench.resolve()
    assert cfg.host == "127.0.0.1"


def test_load_config_cli_beats_env(
    workbench: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    other = tmp_path / "other-ws"
    other.mkdir()
    (other / "tracker.md").write_text("# t\n", encoding="utf-8")
    monkeypatch.setenv("ZHIHU_CHECKIN_WORKSPACE", str(workbench))
    cfg = load_config(other, config_file=workbench / "nonexistent-config.yaml")
    assert cfg.workspace.root == other.resolve()


def test_load_config_rejects_nonlocal_host(workbench: Path) -> None:
    cfg_file = workbench / "cfg.yaml"
    cfg_file.write_text("host: 0.0.0.0\n", encoding="utf-8")
    with pytest.raises(WorkspaceError, match="本地地址"):
        load_config(workbench, config_file=cfg_file)
