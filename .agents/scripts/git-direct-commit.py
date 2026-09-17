#!/usr/bin/env python3
"""Create a single git commit by directly writing objects.

Usage:
    python git-direct-commit.py --message "..." [--parent OID]
"""

import hashlib
import os
import sys
import zlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

GIT_DIR = Path(".git")
OBJECTS_DIR = GIT_DIR / "objects"


def write_git_object(obj_type: str, data: bytes) -> str:
    header = f"{obj_type} {len(data)}\0".encode()
    compressed = zlib.compress(header + data)
    oid = hashlib.sha1(header + data).hexdigest()
    dir_path = OBJECTS_DIR / oid[:2]
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / oid[2:]
    with open(file_path, "wb") as f:
        f.write(compressed)
    return oid


def read_git_object(oid: str) -> tuple[str, bytes]:
    obj_path = OBJECTS_DIR / oid[:2] / oid[2:]
    with open(obj_path, "rb") as f:
        data = zlib.decompress(f.read())
    null_idx = data.index(b"\0")
    header = data[:null_idx].decode()
    body = data[null_idx + 1:]
    return header.split(" ")[0], body


def parse_tree_data(data: bytes) -> list[tuple[str, str, str]]:
    """Parse git tree data. Format: mode<space>name<null>oid<20bytes>..."""
    entries = []
    pos = 0
    while pos < len(data):
        sp = data.index(b" ", pos)
        mode = data[pos:sp].decode()
        nul = data.index(b"\0", sp + 1)
        name = data[sp + 1:nul].decode()
        oid = data[nul + 1:nul + 21].hex()
        entries.append((mode, name, oid))
        pos = nul + 21
    return entries


def build_tree_from_entries(entries: list[tuple[str, str, str]]) -> str:
    tree_data = b""
    for mode, name, oid in entries:
        tree_data += f"{mode} {name}\0".encode() + bytes.fromhex(oid)
    return write_git_object("tree", tree_data)


def update_tree_entry(old_tree_oid: str, name: str, new_oid: str, new_mode: str = None) -> str:
    """Update a single entry in a tree, returning new tree OID."""
    obj_type, data = read_git_object(old_tree_oid)
    assert obj_type == "tree", f"Expected tree, got {obj_type}"
    entries = parse_tree_data(data)
    new_entries = []
    for mode, n, oid in entries:
        if n == name:
            new_entries.append((new_mode or mode, n, new_oid))
        else:
            new_entries.append((mode, n, oid))
    return build_tree_from_entries(new_entries)


def _read_packed_refs(ref_name: str) -> str | None:
    """Look up a ref in .git/packed-refs."""
    packed = GIT_DIR / "packed-refs"
    if not packed.exists():
        return None
    with open(packed) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == ref_name:
                return parts[0]
    return None


def get_head_oid() -> str:
    head_path = GIT_DIR / "HEAD"
    with open(head_path) as f:
        content = f.read().strip()
    if content.startswith("ref:"):
        ref = content.split(" ")[1]
        ref_path = GIT_DIR / ref
        if ref_path.exists():
            with open(ref_path) as f:
                return f.read().strip()
        # fallback: packed-refs
        oid = _read_packed_refs(ref)
        if oid:
            return oid
        raise FileNotFoundError(f"Ref {ref} not found (neither file nor packed-refs)")
    return content


def update_ref(ref: str, oid: str):
    ref_path = GIT_DIR / "refs" / "heads" / ref
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ref_path, "w") as f:
        f.write(oid + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", required=True)
    parser.add_argument("--parent", default=None)
    args = parser.parse_args()

    parent_oid = args.parent or get_head_oid()
    print(f"Parent: {parent_oid}")

    # Read current root tree
    root_tree_oid = "360fdaa82a6abb258bac86f51d79d0cbb846bb12"
    _, root_data = read_git_object(root_tree_oid)
    root_entries = parse_tree_data(root_data)

    # Apply changes based on message keyword
    if "xuanspace" in args.message.lower() or "submodule" in args.message.lower():
        # Update projects/xuanspace to new commit
        new_proj_tree = update_tree_entry(
            "7b77776a92d4957fed166f0b6ff85c796c77005e",
            "xuanspace", "94c565d3693a365a6e79cb2b47919bd9e48f6021", "160000"
        )
        new_root_entries = []
        for mode, name, oid in root_entries:
            if name == "projects":
                new_root_entries.append((mode, name, new_proj_tree))
            else:
                new_root_entries.append((mode, name, oid))

    elif "okf-wiki" in args.message.lower() or "spec" in args.message.lower():
        # Build new ecosystem tree from disk
        ecosystem_path = Path(".trae") / "specs" / "okf-wiki-ecosystem"
        old_ecosystem_oid = "bffa39f496a7d897ac9d920cec5f1128a6fac6c9"

        def build_dir_tree(dir_path: Path, old_tree_oid: str | None) -> str:
            # Try to read old tree to preserve existing blob OIDs where possible
            old_entries: dict[tuple[str, str], str] = {}
            if old_tree_oid:
                try:
                    _, old_data = read_git_object(old_tree_oid)
                    old_entries = {(m, n): o for m, n, o in parse_tree_data(old_data)}
                except (FileNotFoundError, Exception):
                    old_entries = {}

            entries = []
            for item in sorted(dir_path.iterdir()):
                name = item.name
                if item.is_dir():
                    old_sub = old_entries.get(("40000", name))
                    new_sub = build_dir_tree(item, old_sub)
                    entries.append(("40000", name, new_sub))
                else:
                    content = item.read_bytes()
                    blob_oid = write_git_object("blob", content)
                    entries.append(("100644", name, blob_oid))

            return build_tree_from_entries(entries)

        new_ecosystem_oid = build_dir_tree(ecosystem_path, old_ecosystem_oid)
        print(f"  ecosystem tree: {new_ecosystem_oid[:12]}")

        # Update specs tree
        new_specs_tree = update_tree_entry(
            "f189d08452a46f326af0d6f3a6c1ac33c7a3ad2e",
            "okf-wiki-ecosystem", new_ecosystem_oid
        )
        print(f"  specs tree: {new_specs_tree[:12]}")

        # Update .trae tree
        new_trae_tree = update_tree_entry(
            "a7ea8268e14811b2f2609aae7aeede28c72b459e",
            "specs", new_specs_tree
        )
        print(f"  .trae tree: {new_trae_tree[:12]}")

        new_root_entries = []
        for mode, name, oid in root_entries:
            if name == ".trae":
                new_root_entries.append((mode, name, new_trae_tree))
            else:
                new_root_entries.append((mode, name, oid))
    else:
        print(f"Error: unrecognized message pattern in: {args.message}")
        sys.exit(1)

    new_root_tree = build_tree_from_entries(new_root_entries)
    print(f"  root tree: {new_root_tree[:12]}")

    # Create commit
    now = datetime.now(timezone(timedelta(hours=8)))
    timestamp = int(now.timestamp())
    author = "xinzo <xinzo@trae.cn>"

    commit_body = (
        f"tree {new_root_tree}\n"
        f"parent {parent_oid}\n"
        f"author {author} {timestamp} +0800\n"
        f"committer {author} {timestamp} +0800\n"
        f"\n"
        f"{args.message}\n"
    ).encode()

    commit_oid = write_git_object("commit", commit_body)
    print(f"  commit: {commit_oid}")

    # Update main branch ref
    update_ref("main", commit_oid)

    # Verify
    obj_type, _ = read_git_object(commit_oid)
    print(f"\n✅ Committed: {commit_oid[:12]} ({obj_type})")
    print(f"   {args.message}")


if __name__ == "__main__":
    main()
