"""应用配置：CLI > 环境变量 > config.yaml > 自动推算。"""

import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .errors import WorkspaceError
from .storage.workspace import Workspace, open_workspace

APP_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_CONFIG_FILE = APP_ROOT / "config.yaml"
ENV_WORKSPACE = "ZHIHU_CHECKIN_WORKSPACE"
DEFAULT_WORKBENCH_REL = Path("projects/monetize/zhihu-monetization")


@dataclass(frozen=True)
class Config:
    workspace: Workspace
    webbridge_endpoint: str = "http://127.0.0.1:10086/command"
    session: str = "zhihu-checkin-hub"
    host: str = "127.0.0.1"
    port: int = 17253
    daily_reminder_hour: int = 21
    week_start: date = field(default_factory=lambda: date(2026, 9, 25))


def _read_yaml_config(config_file: Path) -> dict[str, Any]:
    if not config_file.is_file():
        return {}
    data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise WorkspaceError(f"配置文件格式非映射：{config_file}")
    return data


def _candidate_workspaces() -> list[Path]:
    """生成工作区候选路径（存在性由打开步骤判定）。"""
    candidates: list[Path] = []
    cwd = Path.cwd().resolve()
    for base in (cwd, *cwd.parents):
        candidates.append(base / DEFAULT_WORKBENCH_REL)
    candidates.append(REPO_ROOT / DEFAULT_WORKBENCH_REL)
    return candidates


def _resolve_workspace(
    cli_workspace: str | os.PathLike[str] | None,
    file_data: dict[str, Any],
) -> Path:
    if cli_workspace is not None and str(cli_workspace).strip():
        return Path(cli_workspace)
    env_value = os.environ.get(ENV_WORKSPACE)
    if env_value and env_value.strip():
        return Path(env_value)
    file_value = file_data.get("workspace")
    if isinstance(file_value, str) and file_value.strip():
        return Path(file_value)
    for cand in _candidate_workspaces():
        if cand.is_dir():
            return cand
    raise WorkspaceError(
        "无法自动定位知乎变现执行工作台。请用 --workspace 或环境变量 "
        f"{ENV_WORKSPACE} 指向包含 tracker.md 的目录（默认期望："
        f"{REPO_ROOT / DEFAULT_WORKBENCH_REL}）。"
    )


def load_config(
    cli_workspace: str | os.PathLike[str] | None = None,
    *,
    config_file: str | os.PathLike[str] | None = None,
    port: int | None = None,
    host: str | None = None,
) -> Config:
    """加载配置并打开/校验工作区。"""
    cfg_path = Path(config_file) if config_file else DEFAULT_CONFIG_FILE
    data = _read_yaml_config(cfg_path)
    ws_path = _resolve_workspace(cli_workspace, data)
    workspace = open_workspace(ws_path)

    def _as(key: str, default: Any) -> Any:
        return data.get(key, default)

    resolved_host = host or str(_as("host", "127.0.0.1"))
    if resolved_host not in ("127.0.0.1", "localhost", "::1"):
        raise WorkspaceError(
            f"出于安全考虑，服务只允许绑定本地地址，拒绝绑定：{resolved_host}"
        )

    return Config(
        workspace=workspace,
        webbridge_endpoint=str(
            _as("webbridge_endpoint", "http://127.0.0.1:10086/command")
        ),
        session=str(_as("session", "zhihu-checkin-hub")),
        host=resolved_host,
        port=int(port) if port is not None else int(_as("port", 17253)),
        daily_reminder_hour=int(_as("daily_reminder_hour", 21)),
        week_start=_parse_date(_as("week_start", "2026-09-25")),
    )


def _parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
