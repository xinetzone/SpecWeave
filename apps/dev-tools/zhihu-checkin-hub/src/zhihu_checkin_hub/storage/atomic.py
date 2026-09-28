"""原子写与 YAML 序列化公共工具。"""

import os
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml


def _represent_str_enum(dumper: yaml.SafeDumper, data: StrEnum) -> yaml.ScalarNode:
    return dumper.represent_str(str(data))


yaml.SafeDumper.add_multi_representer(StrEnum, _represent_str_enum)


def atomic_write_text(path: Path, text: str) -> None:
    """同目录临时文件 + os.replace，保证落盘原子性；统一 LF。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def dump_yaml(data: Any) -> str:
    return yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False, default_flow_style=False, width=1000
    )
