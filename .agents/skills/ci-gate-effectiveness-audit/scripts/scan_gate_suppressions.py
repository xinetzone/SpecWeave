#!/usr/bin/env python3
"""Enumerate CI gate suppressions that keep a workflow step from failing.

Scans workflow files for declarations and body fragments that downgrade a
failing gate to a log line, classifies each by scope, and can re-check one
literal pattern after a targeted removal. Read-only; executes nothing.

Line scanning is a heuristic: comment lines are skipped, but patterns buried
in block scalars are still reported. Confirm with a YAML re-parse before editing.

Exit codes:
  0 = no step-level blocker found (or --expect-zero with zero matching lines)
  1 = at least one step-level blocker found (or --expect-zero with matches)
  2 = usage error, no workflow file found, or an unreadable file
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "build",
    "_build",
    "dist",
    "__pycache__",
    ".mypy_cache",
    ".tox",
}

CLASS_BLOCKER = "step-level-blocker"
CLASS_DECLARED_FALSE = "step-level-declared-false"
CLASS_BODY = "body-level-tolerated"
CLASS_REVIEW = "needs-review"

CLASS_ORDER = (CLASS_BLOCKER, CLASS_DECLARED_FALSE, CLASS_BODY, CLASS_REVIEW)

DECLARATION_KEYS = ("continue-on-error", "allow_failure")

TRUE_VALUES = ("true", "'true'", '"true"', "yes", "on")
FALSE_VALUES = ("false", "'false'", '"false"', "no", "off")

BODY_PATTERNS = (
    ("or-true", re.compile(r"\|\|\s*true\b")),
    ("or-exit-0", re.compile(r"\|\|\s*exit\s+0\b")),
)

REVIEW_PATTERNS = (
    ("if-always", re.compile(r"""^\s*if\s*:\s*['"]?always\s*\(\s*\)['"]?\s*$""")),
)

STEP_NAME_RE = re.compile(r"^\s*-\s+name\s*:\s*(?P<name>.+?)\s*$")


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 2


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def display_path(path, root):
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def discover(root, explicit):
    if explicit:
        files = []
        for raw in explicit:
            path = Path(raw)
            if not path.is_file():
                raise FileNotFoundError(raw)
            files.append(path.resolve())
        return files

    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        current = Path(dirpath)
        if current.name != "workflows" or current.parent.name != ".github":
            continue
        for name in filenames:
            if name.endswith((".yml", ".yaml")):
                found.append((current / name).resolve())
    return sorted(found)


def strip_comment(value):
    return value.split("#", 1)[0].strip()


def classify_declaration(value):
    text = strip_comment(value)
    if not text or "${{" in text:
        return CLASS_REVIEW
    low = text.lower()
    if low in TRUE_VALUES:
        return CLASS_BLOCKER
    if low in FALSE_VALUES:
        return CLASS_DECLARED_FALSE
    return CLASS_REVIEW


def detect(raw):
    for key in DECLARATION_KEYS:
        match = re.match(rf"^\s*{re.escape(key)}\s*:(?P<value>.*)$", raw)
        if match:
            return key, classify_declaration(match.group("value"))
    for pattern_id, pattern in BODY_PATTERNS:
        if pattern.search(raw):
            return pattern_id, CLASS_BODY
    for pattern_id, pattern in REVIEW_PATTERNS:
        if pattern.search(raw):
            return pattern_id, CLASS_REVIEW
    return None


def make_item(pattern_id, klass, rel, line, text, step, step_line):
    return {
        "pattern": pattern_id,
        "class": klass,
        "file": rel,
        "line": line,
        "text": text.strip(),
        "step": step,
        "step_line": step_line,
    }


def scan_file(path, root):
    rel = display_path(path, root)
    items = []
    step = None
    step_line = None
    for number, raw in enumerate(read_text(path).splitlines(), start=1):
        name_match = STEP_NAME_RE.match(raw)
        if name_match:
            candidate = name_match.group("name").strip().strip("'\"")
            if candidate and not candidate.startswith("#"):
                step = candidate
                step_line = number
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        hit = detect(raw)
        if hit is not None:
            items.append(make_item(hit[0], hit[1], rel, number, raw, step, step_line))
    return items


def matching_lines(path, needle, root):
    rel = display_path(path, root)
    hits = []
    for number, raw in enumerate(read_text(path).splitlines(), start=1):
        if needle in raw:
            hits.append({"file": rel, "line": number, "text": raw.strip()})
    return hits


def report_expect_zero(args, files, root):
    hits = []
    for path in files:
        hits.extend(matching_lines(path, args.expect_zero, root))

    if args.json:
        print(
            json.dumps(
                {
                    "root": root.as_posix(),
                    "expect_zero": args.expect_zero,
                    "files_scanned": [display_path(path, root) for path in files],
                    "matching_lines": len(hits),
                    "hits": hits,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"root: {root.as_posix()}")
        print(f"workflow files scanned: {len(files)}")
        print(f"expect-zero pattern: {args.expect_zero}")
        print(f"matching lines: {len(hits)}")
        for hit in hits:
            print(f"  {hit['file']}:{hit['line']}: {hit['text']}")

    return 0 if not hits else 1


def report_scan(args, files, items, root):
    counts = {klass: 0 for klass in CLASS_ORDER}
    for item in items:
        counts[item["class"]] += 1

    if args.json:
        print(
            json.dumps(
                {
                    "root": root.as_posix(),
                    "files_scanned": [display_path(path, root) for path in files],
                    "counts": counts,
                    "items": items,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"root: {root.as_posix()}")
        print(f"workflow files scanned: {len(files)}")
        for path in files:
            print(f"  {display_path(path, root)}")
        print()
        print(f"{CLASS_BLOCKER}: {counts[CLASS_BLOCKER]}")
        print(f"{CLASS_BODY} (not blockers): {counts[CLASS_BODY]}")
        print(f"{CLASS_REVIEW}: {counts[CLASS_REVIEW]}")
        print(f"{CLASS_DECLARED_FALSE} (informational): {counts[CLASS_DECLARED_FALSE]}")
        print()
        for item in items:
            where = f"{item['file']}:{item['line']}"
            context = f' step="{item["step"]}"' if item["step"] else ""
            print(f"[{item['class']}] {where}{context} {item['pattern']} :: {item['text']}")
        print()
        if counts[CLASS_BLOCKER]:
            print("verdict: step-level blocker present; this gate cannot fail the job")
        else:
            print("verdict: no step-level blocker found")
        if counts[CLASS_BODY]:
            print(
                "note: body-level suppressions are reported for review only; best-effort "
                "steps keep them legitimately, so do not remove them as part of a "
                "single-point gate fix"
            )
        if counts[CLASS_REVIEW]:
            print(
                "note: needs-review entries are not suppressors by themselves; "
                "if: always() only reorders execution and does not block failure spread"
            )

    return 1 if counts[CLASS_BLOCKER] else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Enumerate CI gate suppressions that keep a step from failing."
    )
    parser.add_argument("root", nargs="?", default=".", help="scan root (default: cwd)")
    parser.add_argument(
        "--paths",
        nargs="+",
        metavar="FILE",
        help="explicit workflow files, overriding auto-discovery",
    )
    parser.add_argument(
        "--expect-zero",
        metavar="PATTERN",
        help="literal substring to count, case-sensitive (grep -F semantics); "
        "exits 0 only when zero lines match",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        return fail(f"root is not a directory: {root}")

    try:
        files = discover(root, args.paths)
    except FileNotFoundError as exc:
        return fail(f"workflow file not found: {exc}")

    if not files:
        return fail(f"no workflow file found under {root}; pass --paths to name them")

    try:
        if args.expect_zero is not None:
            return report_expect_zero(args, files, root)
        items = []
        for path in files:
            items.extend(scan_file(path, root))
    except OSError as exc:
        return fail(f"cannot read file: {exc}")

    items.sort(key=lambda item: (item["file"], item["line"]))
    return report_scan(args, files, items, root)


if __name__ == "__main__":
    sys.exit(main())