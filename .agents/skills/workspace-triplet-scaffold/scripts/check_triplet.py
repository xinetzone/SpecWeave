#!/usr/bin/env python3
"""Validate README.md + AGENTS.md + .agents/README.md triplets."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REQUIRED = ("README.md", "AGENTS.md", ".agents/README.md")
KEYWORD = "启动协议"
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".temp", ".build-temp", ".ccache", "build", "dist",
    "target", "site-packages", ".mypy_cache", ".pytest_cache",
}
LINK_RE = re.compile(
    r"\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
ABSOLUTE_WIN_RE = re.compile(r"^[A-Za-z]:[\\/]")


def strip_code(text):
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def check_links(path):
    text = strip_code(path.read_text(encoding="utf-8", errors="replace"))
    total = 0
    broken = []
    for match in LINK_RE.finditer(text):
        raw = match.group(1)
        if raw.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        if raw.startswith(("file://", "file:///")):
            broken.append((raw, "absolute file:// link"))
            continue
        target = raw.strip("<>").split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        if Path(target).is_absolute() or ABSOLUTE_WIN_RE.match(target):
            broken.append((raw, "absolute path"))
            continue
        total += 1
        resolved = (path.parent / target.replace("%20", " ")).resolve()
        if not resolved.exists():
            broken.append((raw, "missing target"))
    return total, broken


def nested_agents(root, max_depth):
    root = root.resolve()
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        depth = len(current.relative_to(root).parts)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in SKIP_DIRS and not name.startswith(".")
        )
        if 1 <= depth <= max_depth and "AGENTS.md" in filenames:
            found.append((current / "AGENTS.md").relative_to(root))
        if depth >= max_depth:
            dirnames[:] = []
    return sorted(found)


def run_git(args, cwd):
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return 127, "", "git not found"
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_state(target):
    code, out, _ = run_git(["rev-parse", "--show-toplevel"], target)
    if code != 0:
        return {"kind": "not-a-repo"}
    repo = Path(out).resolve()
    try:
        rel = target.resolve().relative_to(repo).as_posix()
    except ValueError:
        return {"kind": "not-a-repo"}
    rel = rel or "."

    code, out, _ = run_git(["check-ignore", "-v", "--", rel], repo)
    ignored = code == 0 and bool(out)
    _, tracked_out, _ = run_git(["ls-files", "--", rel], repo)
    tracked = len([line for line in tracked_out.splitlines() if line.strip()])

    if ignored:
        kind = "ignored"
    elif tracked:
        kind = "tracked"
    else:
        kind = "untracked"
    return {
        "kind": kind,
        "repo": str(repo),
        "rel": rel,
        "rule": out if ignored else "",
        "tracked_count": tracked,
    }


def validate(target, max_depth):
    target = target.resolve()
    errors, warnings, messages = [], [], []

    if not target.is_dir():
        return [f"target is not a directory: {target}"], [], []

    for rel in REQUIRED:
        path = target / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
        elif not path.is_file():
            errors.append(f"required path is not a file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty required file: {rel}")
        else:
            messages.append(("OK", f"{rel} ({path.stat().st_size} bytes)"))

    agents = target / "AGENTS.md"
    agents_text = ""
    if agents.is_file():
        agents_text = agents.read_text(encoding="utf-8", errors="replace")
        if KEYWORD in agents_text:
            messages.append(("OK", f"AGENTS.md contains {KEYWORD}"))
        else:
            errors.append(f"AGENTS.md missing required keyword: {KEYWORD}")

    for rel in REQUIRED:
        path = target / rel
        if not path.is_file():
            continue
        total, broken = check_links(path)
        messages.append(("OK", f"{rel}: {total} relative link(s) checked"))
        for raw, reason in broken:
            errors.append(f"{rel}: broken link {raw} ({reason})")

    nested = nested_agents(target, max_depth)
    if nested:
        messages.append(("INFO", f"nested AGENTS.md: {len(nested)}"))
        if "嵌套" not in agents_text or "优先" not in agents_text:
            warnings.append(
                f"{len(nested)} nested AGENTS.md found but root AGENTS.md "
                "does not declare nested priority (嵌套优先)"
            )

    if (target / ".agents" / "docs").exists():
        warnings.append(".agents/docs/ exists (deprecated SpecWeave output path)")

    state = git_state(target)
    kind = state["kind"]
    if kind == "ignored":
        messages.append(("INFO", f"git: ignored ({state['rule']}) - not committable"))
    elif kind == "tracked":
        messages.append(("INFO", f"git: tracked ({state['tracked_count']} file(s))"))
    elif kind == "untracked":
        warnings.append("git: untracked - will appear in repository status")
    else:
        messages.append(("INFO", "git: not a repository (skipped)"))

    return errors, warnings, messages


def main():
    parser = argparse.ArgumentParser(
        description="Validate README.md + AGENTS.md + .agents/README.md triplets."
    )
    parser.add_argument("targets", nargs="+", help="directories to validate")
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as failures"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="nested AGENTS.md scan depth (default: 4)",
    )
    args = parser.parse_args()

    total_errors = 0
    total_warnings = 0
    for raw_target in args.targets:
        target = Path(raw_target)
        print(f"== {target.resolve()} ==")
        errors, warnings, messages = validate(target, args.max_depth)
        for tag, text in messages:
            print(f"  [{tag}] {text}")
        for text in warnings:
            print(f"  [WARN] {text}")
        for text in errors:
            print(f"  [FAIL] {text}")
        total_errors += len(errors)
        total_warnings += len(warnings)
        print()

    print(
        f"summary: {len(args.targets)} target(s), "
        f"{total_errors} error(s), {total_warnings} warning(s)"
    )
    if total_errors or (args.strict and total_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
