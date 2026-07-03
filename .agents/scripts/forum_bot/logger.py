"""forum-bot 日志系统与彩色输出工具。

提供分级日志配置、彩色控制台输出、步骤/门禁/重试等语义化日志函数。
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from .constants import (
    ACTION_DELAY, ANSI_BOLD, ANSI_CYAN, ANSI_GREEN, ANSI_GREY, ANSI_RED,
    ANSI_RESET, ANSI_YELLOW, STATE_FILE,
)

logger = logging.getLogger("forum-bot")


def setup_logging(debug: bool = False) -> None:
    """初始化日志系统：控制台按级别过滤，文件始终记录DEBUG级。"""
    console_level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(message)s",
        datefmt="%H:%M:%S",
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    log_dir = Path(__file__).resolve().parent.parent / "logs"
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
