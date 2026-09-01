"""Three-layer logging Python configuration layer.

Provides unified setup functions that control both Python logging
and C++ native logging through a single entry point.

Usage:
    from myproj.debug import setup_debug, setup_quiet, setup_trace

    setup_debug()                        # DEBUG on both layers
    setup_debug(log_file="app.log")     # Also write to file
    setup_trace()                        # Finest TRACE level
    setup_quiet()                        # Restore WARN default
"""
from __future__ import annotations

import logging
import sys
from typing import Optional

# ── Level constants (must match C++ enum exactly) ────────
LOG_LEVEL_TRACE = 0
LOG_LEVEL_DEBUG = 1
LOG_LEVEL_INFO  = 2
LOG_LEVEL_WARN  = 3
LOG_LEVEL_ERROR = 4

_LOGGER_NAME = "myproj"
_logger = logging.getLogger(_LOGGER_NAME)
_configured_handlers: list[logging.Handler] = []


def _clear_handlers() -> None:
    """Remove all handlers added by this module (idempotent)."""
    for h in _configured_handlers:
        _logger.removeHandler(h)
        h.close()
    _configured_handlers.clear()


def _add_handler(handler: logging.Handler, level: int, fmt: str, datefmt: str) -> None:
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    _logger.addHandler(handler)
    _configured_handlers.append(handler)


def _set_native_level(level: int) -> None:
    """Set C++ native log level via FFI. Override for your FFI system."""
    try:
        from myproj import _ffi
        fn = _ffi.get_global_func("myproj.SetLogLevel")
        if fn is not None:
            fn(level)
    except (ImportError, AttributeError):
        pass  # FFI not available, pure Python mode


def setup_debug(
    level: int = LOG_LEVEL_DEBUG,
    log_file: Optional[str] = None,
    python_level: int = logging.DEBUG,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt: str = "%H:%M:%S",
) -> None:
    """Enable debug logging on both Python and C++ layers.

    Args:
        level: C++ native level (default LOG_LEVEL_DEBUG=1).
               Use LOG_LEVEL_TRACE=0 for finest-grained output.
        log_file: Optional file path; logs also written here.
        python_level: Python logging module level (default DEBUG).
        fmt: Log format string.
        datefmt: Time format string.
    """
    _clear_handlers()
    _logger.setLevel(python_level)

    # Console handler (avoid duplicates)
    has_console = any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in _logger.handlers
    )
    if not has_console:
        _add_handler(logging.StreamHandler(sys.stdout), python_level, fmt, datefmt)

    # Optional file handler
    if log_file:
        _add_handler(
            logging.FileHandler(log_file, encoding="utf-8"),
            python_level, fmt, datefmt,
        )

    _set_native_level(level)
    _logger.debug("Debug logging enabled (C++ level=%d, Python level=%d)", level, python_level)


def setup_trace(log_file: Optional[str] = None) -> None:
    """Enable TRACE-level logging for finest-grained diagnostics."""
    setup_debug(level=LOG_LEVEL_TRACE, log_file=log_file)
    _logger.debug("Trace mode enabled (level=0)")


def setup_quiet() -> None:
    """Disable debug logging; restore WARN default on both layers."""
    _clear_handlers()
    _logger.setLevel(logging.WARNING)
    _set_native_level(LOG_LEVEL_WARN)


def setup_file_logging(
    log_file: str,
    level: int = LOG_LEVEL_DEBUG,
    append: bool = False,
) -> None:
    """File-only logging (no console output) for long-running tasks."""
    _clear_handlers()
    _logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file, mode="a" if append else "w", encoding="utf-8")
    _add_handler(fh, logging.DEBUG,
                 "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%H:%M:%S")
    _set_native_level(level)
