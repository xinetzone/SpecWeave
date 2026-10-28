#!/usr/bin/env python3
"""Probe a file for read-to-write drift and diff it against a saved baseline.

Exit codes
  0  probed; no drift (or baseline written)
  1  drift detected, target absent, or link target unreadable
  2  usage or IO error (bad arguments, missing/invalid baseline, directory path)
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
COMPARE_FIELDS = ("kind", "realpath", "size", "mtime_ns", "sha256", "version")


def file_kind(path):
    if not os.path.lexists(path):
        return "absent"
    if os.path.isjunction(path):
        return "junction"
    if os.path.islink(path):
        return "symlink"
    mode = os.lstat(path).st_mode
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    return "other"


def extract_version(text):
    match = FRONTMATTER.match(text[:4000])
    if not match:
        return None
    front = match.group(1)
    found = re.search(r"^version:\s*(\S+)", front, re.M)
    if not found:
        found = re.search(r"^\s+version:\s*(\S+)", front, re.M)
    if not found:
        return None
    return found.group(1).strip().strip("\"'")


def extract_headings(text):
    headings = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if match:
            headings.append(match.group(1) + " " + match.group(2))
    return headings


def probe(path):
    info = {
        "path": path,
        "kind": file_kind(path),
        "lexists": os.path.lexists(path),
        "exists": os.path.exists(path),
    }
    if info["kind"] == "absent":
        return info

    real = os.path.realpath(path)
    info["realpath"] = real
    try:
        st = os.stat(path)
    except OSError as exc:
        info["error"] = f"unreadable target: {exc}"
        return info

    info["size"] = st.st_size
    info["mtime_ns"] = st.st_mtime_ns
    info["inode"] = st.st_ino
    if info["kind"] != "file":
        return info
    data = Path(real).read_bytes()
    info["sha256"] = hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8", errors="replace")
    info["version"] = extract_version(text)
    info["headings"] = extract_headings(text)
    return info


def compare(baseline, current):
    changes = {}
    for field in COMPARE_FIELDS:
        before, after = baseline.get(field), current.get(field)
        if before != after:
            changes[field] = {"baseline": before, "current": after}
    before_headings = baseline.get("headings") or []
    after_headings = current.get("headings") or []
    added = [h for h in after_headings if h not in before_headings]
    removed = [h for h in before_headings if h not in after_headings]
    if added or removed:
        changes["headings"] = {"added": added, "removed": removed}
    return changes


def load_baseline(path):
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"baseline not found: {path}") from exc
    except (OSError, ValueError) as exc:
        raise ValueError(f"baseline unreadable: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"baseline is not a JSON object: {path}")
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--path", required=True, help="file to probe")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--baseline", help="compare current state against this JSON snapshot")
    group.add_argument("--write-baseline", help="write current state to this JSON snapshot")
    args = parser.parse_args(argv)

    current = probe(args.path)
    if current["kind"] == "directory" or current["kind"] == "other":
        print(f"not a regular file: {args.path} ({current['kind']})", file=sys.stderr)
        return 2
    if "error" in current:
        print(current["error"], file=sys.stderr)
        return 1

    if args.write_baseline:
        if current["kind"] != "file":
            print(f"cannot baseline {current['kind']} target: {args.path}", file=sys.stderr)
            return 1
        current["saved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            Path(args.write_baseline).write_text(
                json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except OSError as exc:
            print(f"cannot write baseline: {exc}", file=sys.stderr)
            return 2
        print(json.dumps({"baseline_written": args.write_baseline, "state": current},
                         ensure_ascii=False, indent=2))
        return 0

    if args.baseline:
        try:
            baseline = load_baseline(args.baseline)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        changes = compare(baseline, current)
        payload = {"drift": bool(changes), "changes": changes, "state": current}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if changes else 0

    print(json.dumps({"drift": current["kind"] != "file", "state": current},
                     ensure_ascii=False, indent=2))
    return 0 if current["kind"] == "file" else 1


if __name__ == "__main__":
    sys.exit(main())
