"""SpecWeave Bridge Plugin for Hermes Agent.

Integrates Hermes with a SpecWeave workspace:

1. ``pre_llm_call`` hook — when the current working directory is inside a
   SpecWeave workspace, injects a compact **启动协议** (startup protocol)
   brief into the user message.  Injecting into the user message (never the
   system prompt) preserves Hermes' three-tier prompt cache prefix.

2. ``specweave_route`` tool — maps a task type to the required SpecWeave
   specification path(s), honouring apps/projects/vendor sub-region routing.

3. ``specweave_check`` tool — runs a SpecWeave validation script.  Gated by
   ``check_fn`` so it only dispatches inside a SpecWeave workspace.

4. ``/specweave`` slash command and ``hermes specweave`` CLI subcommand —
   workspace status, routing lookup, and help.

5. ``specweave:protocol`` read-only skill — progressive-disclosure
   reference for the startup protocol and routing semantics.

Design follows Hermes' Footprint Ladder: everything is a plugin/skill on top
of the core, nothing modifies Hermes internals.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import detector
from ._constants import (
    AGENTS_DIR_NAME,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    ROUTES,
    SCRIPTS_DIR_NAME,
    SUBREGIONS,
)

logger = logging.getLogger(__name__)

_STARTUP_BRIEF = (
    "[SpecWeave 启动协议] 当前处于 SpecWeave 工作区。执行任何任务前请先阅读根目录 "
    "AGENTS.md 的启动协议，并按上下文路由表定位需读取的规范文件；若任务命中 "
    "apps/projects/vendor 子区域，需先读取对应子区域 AGENTS.md。可用 "
    "specweave_route 工具查询任务对应的规范路径。"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_specweave_root(cwd: Optional[str] = None) -> Optional[str]:
    """Resolve the nearest SpecWeave workspace root for *cwd* (default: cwd)."""
    try:
        return detector.find_specweave_root(cwd)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("resolve_specweave_root failed: %s", exc)
        return None


def _get_cwd() -> str:
    try:
        return os.getcwd()
    except Exception:
        return "."


def _abs_script_path(root: str, script_name: str) -> Optional[Path]:
    """Return the absolute path to a SpecWeave validation script."""
    base = Path(root) / AGENTS_DIR_NAME / SCRIPTS_DIR_NAME
    candidate = base / script_name
    if candidate.is_file():
        return candidate
    # Accept the script name with or without a .py suffix.
    if not script_name.endswith(".py"):
        candidate = base / f"{script_name}.py"
        if candidate.is_file():
            return candidate
    return None


# ---------------------------------------------------------------------------
# pre_llm_call hook — 启动协议注入
# ---------------------------------------------------------------------------

def _on_pre_llm_call(**_: Any) -> Optional[Dict[str, str]]:
    """Inject a compact SpecWeave startup protocol brief when in a workspace.

    Returns ``None`` when not in a SpecWeave workspace (no injection), and a
    ``{"context": ...}`` dict otherwise.  Context lands in the user message,
    keeping the system prompt byte-identical so the prompt cache is reused.
    """
    root = _resolve_specweave_root(_get_cwd())
    if not root:
        return None
    return {"context": _STARTUP_BRIEF}


# ---------------------------------------------------------------------------
# specweave_route tool — 任务→规范路径路由
# ---------------------------------------------------------------------------

def _check_in_specweave() -> bool:
    """Service gate: only dispatch inside a SpecWeave workspace."""
    return _resolve_specweave_root(_get_cwd()) is not None


def _handle_specweave_route(args: dict, **_: Any) -> str:
    task = str(args.get("task") or "").strip()
    cwd = str(args.get("cwd") or _get_cwd())
    if not task:
        return json.dumps(
            {"ok": False, "error": "task 参数必填"}, ensure_ascii=False
        )

    root = _resolve_specweave_root(cwd)
    if not root:
        return json.dumps(
            {"ok": False, "error": f"未检测到 SpecWeave 工作区（{cwd}）"},
            ensure_ascii=False,
        )

    subregion = detector.detect_subregion(cwd, root)
    matched = [
        {"task": key, "spec": rel}
        for key, rel in ROUTES.items()
        if task.lower() in key.lower()
    ]
    if not matched:
        # No keyword match — fall back to the context-routing entrypoint.
        matched = [{"task": task, "spec": ".agents/context-routing.md"}]

    return json.dumps(
        {
            "ok": True,
            "specweave_root": root,
            "cwd": cwd,
            "subregion": subregion,
            "subregion_agents_md": (
                f"{subregion}/AGENTS.md" if subregion in SUBREGIONS else None
            ),
            "routes": matched,
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# specweave_check tool — 验证脚本工具（服务门控）
# ---------------------------------------------------------------------------

def _handle_specweave_check(args: dict, **_: Any) -> str:
    script = str(args.get("script") or "").strip()
    cwd = str(args.get("cwd") or _get_cwd())
    extra = args.get("args") or []
    if not script:
        return json.dumps(
            {"ok": False, "error": "script 参数必填"}, ensure_ascii=False
        )

    root = _resolve_specweave_root(cwd)
    if not root:
        return json.dumps(
            {"ok": False, "error": f"未检测到 SpecWeave 工作区（{cwd}）"},
            ensure_ascii=False,
        )

    script_path = _abs_script_path(root, script)
    if script_path is None:
        return json.dumps(
            {
                "ok": False,
                "error": f"未找到验证脚本: {script}（应在 {AGENTS_DIR_NAME}/{SCRIPTS_DIR_NAME}/ 下）",
            },
            ensure_ascii=False,
        )

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), *([str(a) for a in extra] if isinstance(extra, list) else [])],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=float(args.get("timeout", 120) or 120),
        )
        return json.dumps(
            {
                "ok": result.returncode == 0,
                "exit_code": result.returncode,
                "script": str(script_path),
                "stdout": result.stdout[-8000:],
                "stderr": result.stderr[-4000:],
            },
            ensure_ascii=False,
            indent=2,
        )
    except subprocess.TimeoutExpired:
        return json.dumps(
            {"ok": False, "error": f"脚本执行超时: {script}"},
            ensure_ascii=False,
        )
    except Exception as exc:
        return json.dumps(
            {"ok": False, "error": f"执行失败: {exc}"}, ensure_ascii=False
        )


_ROUTE_SCHEMA = {
    "type": "object",
    "properties": {
        "task": {
            "type": "string",
            "description": "任务类型关键词（如：复盘、CI检查、Mermaid、skill创建）",
        },
        "cwd": {
            "type": "string",
            "description": "当前工作目录（可选，默认取进程 cwd）",
        },
    },
    "required": ["task"],
}

_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "script": {
            "type": "string",
            "description": "SpecWeave 验证脚本文件名（.agents/scripts/ 下）",
        },
        "cwd": {
            "type": "string",
            "description": "SpecWeave 工作区根目录（可选，默认探测）",
        },
        "args": {
            "type": "array",
            "items": {"type": "string"},
            "description": "传给脚本的额外参数（可选）",
        },
        "timeout": {
            "type": "number",
            "description": "执行超时秒数（默认 120）",
        },
    },
    "required": ["script"],
}


# ---------------------------------------------------------------------------
# /specweave slash command
# ---------------------------------------------------------------------------

_HELP_TEXT = f"""\
/specweave — SpecWeave 工作区规范集成（v{PLUGIN_VERSION}）

子命令:
  status               显示当前工作区状态与子区域
  route <task>         查询任务对应的规范路径
  help                 显示本帮助

示例:
  /specweave status
  /specweave route 复盘
"""


def _handle_slash(raw_args: str) -> Optional[str]:
    argv = raw_args.strip().split()
    if not argv or argv[0] in {"help", "-h", "--help"}:
        return _HELP_TEXT

    cwd = _get_cwd()
    root = _resolve_specweave_root(cwd)
    sub = argv[0]

    if sub == "status":
        if not root:
            return f"[specweave] 未检测到 SpecWeave 工作区（cwd={cwd}）"
        subregion = detector.detect_subregion(cwd, root)
        lines = [
            f"[specweave] 工作区: {root}",
            f"  当前 cwd : {cwd}",
            f"  子区域   : {subregion or '（根区域）'}",
            f"  技能/脚本: {AGENTS_DIR_NAME}/{SCRIPTS_DIR_NAME}/",
        ]
        return "\n".join(lines)

    if sub == "route":
        task = " ".join(argv[1:]).strip()
        if not task:
            return "用法: /specweave route <task>"
        return _handle_specweave_route({"task": task, "cwd": cwd})

    return f"未知子命令: {sub}\n\n{_HELP_TEXT}"


# ---------------------------------------------------------------------------
# CLI subcommand — hermes specweave ...
# ---------------------------------------------------------------------------

def _setup_cli(subparser) -> None:
    sub = subparser.add_subparsers(dest="specweave_cmd")
    p_status = sub.add_parser("status", help="显示 SpecWeave 工作区状态")
    p_status.set_defaults(func=_cli_status)
    p_route = sub.add_parser("route", help="查询任务对应的规范路径")
    p_route.add_argument("task", help="任务类型关键词")
    p_route.set_defaults(func=_cli_route)


def _cli_status(args) -> None:
    cwd = _get_cwd()
    root = _resolve_specweave_root(cwd)
    if not root:
        print(f"[specweave] 未检测到 SpecWeave 工作区（cwd={cwd}）")
        return
    subregion = detector.detect_subregion(cwd, root)
    print(f"[specweave] 工作区: {root}")
    print(f"  当前 cwd : {cwd}")
    print(f"  子区域   : {subregion or '（根区域）'}")


def _cli_route(args) -> None:
    cwd = _get_cwd()
    print(_handle_specweave_route({"task": args.task, "cwd": cwd}))


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------

def register(ctx) -> None:
    """Register all SpecWeave bridge components with Hermes."""
    logger.info("Loading SpecWeave bridge plugin v%s", PLUGIN_VERSION)

    # 1. 启动协议注入 hook（用户消息层，保留 prompt cache）
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)

    # 2. 路由工具
    ctx.register_tool(
        name="specweave_route",
        toolset="specweave",
        schema=_ROUTE_SCHEMA,
        handler=_handle_specweave_route,
        check_fn=_check_in_specweave,
        description="根据任务类型查询 SpecWeave 规范路径，支持子区域路由。",
        emoji="🧭",
    )

    # 3. 验证脚本工具（服务门控）
    ctx.register_tool(
        name="specweave_check",
        toolset="specweave",
        schema=_CHECK_SCHEMA,
        handler=_handle_specweave_check,
        check_fn=_check_in_specweave,
        description="在 SpecWeave 工作区内运行验证脚本（.agents/scripts/ 下）。",
        emoji="✅",
    )

    # 4. 斜杠命令
    ctx.register_command(
        "specweave",
        handler=_handle_slash,
        description="SpecWeave 工作区规范集成：状态、路由、帮助。",
    )

    # 5. CLI 子命令
    ctx.register_cli_command(
        "specweave",
        help="SpecWeave 工作区规范集成（status / route）",
        setup_fn=_setup_cli,
        handler_fn=None,
    )

    # 6. 只读技能（渐进式披露参考）
    skill_dir = Path(__file__).resolve().parent / "skills" / "protocol"
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        ctx.register_skill(
            "protocol",
            skill_md,
            description="SpecWeave 启动协议、上下文路由与子区域路由参考。",
        )
    else:
        logger.debug("SKILL.md 未找到，跳过技能注册: %s", skill_md)

    logger.info(
        "SpecWeave bridge plugin registered: hook=pre_llm_call, "
        "tools=specweave_route/specweave_check, slash=/specweave, cli=specweave"
    )
