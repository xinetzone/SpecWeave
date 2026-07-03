from __future__ import annotations

import sys
from pathlib import Path

import openpyxl

from .constants import STATUS_VALUE_MAP


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_metric_key(value: object) -> str:
    return normalize_text(value).upper()


def load_workbook(input_path: Path):
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    try:
        return openpyxl.load_workbook(input_path, data_only=True)
    except Exception as exc:
        raise RuntimeError(f"无法读取工作簿: {input_path}") from exc
