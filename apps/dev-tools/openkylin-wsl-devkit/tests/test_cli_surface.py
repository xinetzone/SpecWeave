"""CLI 表面快照锁定：parser 树与入库快照必须逐字节等价。"""

import json
from pathlib import Path

from okw.cli import build_parser

from cli_surface_lib import collect_leaf_commands, serialize_parser

SNAPSHOT_PATH = Path(__file__).resolve().parent / "snapshots" / "cli_surface.json"

EXPECTED_LEAVES = sorted(
    [
        "list",
        "status",
        "import",
        "export",
        "unregister",
        "exec",
        "verify",
        "scaffold",
        "ref",
        "ai preflight",
        "ai install",
        "ai verify",
        "podman preflight",
        "podman install",
        "podman verify",
        "compose preflight",
        "compose install",
        "compose verify",
        "image build",
        "image verify",
    ]
)


def load_snapshot() -> dict:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_snapshot_covers_all_twenty_leaves():
    leaves = sorted(collect_leaf_commands(build_parser()))
    assert leaves == EXPECTED_LEAVES


def test_snapshot_file_is_current():
    current = serialize_parser(build_parser())
    stored = load_snapshot()
    assert current == stored


def test_snapshot_byte_stable_on_rebuild():
    # 重新序列化两次必须完全相同（确定性口径）。
    first = serialize_parser(build_parser())
    second = serialize_parser(build_parser())
    assert json.dumps(first, ensure_ascii=False, indent=2) == json.dumps(
        second, ensure_ascii=False, indent=2
    )
