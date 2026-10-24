#!/usr/bin/env python3
"""Read-only pre-merge gate for shared worktrees.

Checks divergence, authorization drift, upstream path collisions,
merge conflicts, and lock/intermediate git state. It never fetches,
merges, pushes, or writes to the index/worktree.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_CLEAR = 0
EXIT_DRIFT = 2
EXIT_CONFLICT = 3
EXIT_COLLISION = 4
EXIT_STATE = 5
EXIT_ENV = 6

INTERMEDIATE_PATHS = (
    "MERGE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
    "BISECT_LOG",
    "rebase-merge",
    "rebase-apply",
)


def _decode(data):
    return data.decode("utf-8", "replace")


def _git(repo, *args):
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "git executable not found"
    return proc.returncode, _decode(proc.stdout), _decode(proc.stderr)


def _git_text(repo, *args):
    code, out, err = _git(repo, *args)
    if code != 0:
        detail = (err or out).strip() or "exit %d" % code
        raise RuntimeError("git %s: %s" % (" ".join(args), detail))
    return out.strip()


def _split_z(text):
    return [item for item in text.split("\0") if item]


def parse_status(raw):
    """Parse `git status --porcelain=v1 -z` without losing leading spaces."""
    fields = _split_z(raw)
    entries = []
    index = 0
    while index < len(fields):
        field = fields[index]
        if len(field) < 4:
            index += 1
            continue
        xy = field[:2]
        path = field[3:]
        entries.append({"xy": xy, "path": path})
        if ("R" in xy or "C" in xy) and index + 1 < len(fields):
            entries.append({"xy": xy, "path": fields[index + 1]})
            index += 1
        index += 1
    return entries


def collides(left, right):
    left = left.rstrip("/")
    right = right.rstrip("/")
    if not left or not right:
        return False
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def path_state(path):
    if path is None or not path.exists():
        return {"exists": False}
    stat = path.stat()
    return {
        "exists": True,
        "size": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
    }


def git_path(root, name):
    code, out, _ = _git(root, "rev-parse", "--git-path", name)
    if code != 0 or not out.strip():
        return None
    path = Path(out.strip())
    if not path.is_absolute():
        path = (root / path).resolve()
    return path


def collect(repo, upstream, expect_ahead, expect_behind, expect_head):
    root = Path(_git_text(repo, "rev-parse", "--show-toplevel")).resolve()
    code, branch_out, _ = _git(root, "symbolic-ref", "--short", "-q", "HEAD")
    branch = branch_out.strip() if code == 0 and branch_out.strip() else "(detached)"

    head_full = _git_text(root, "rev-parse", "HEAD")
    head_short = _git_text(root, "rev-parse", "--short", "HEAD")

    code, upstream_out, upstream_err = _git(
        root, "rev-parse", "--verify", upstream + "^{commit}"
    )
    if code != 0:
        raise RuntimeError(
            "upstream ref %s not found; run git fetch first (%s)"
            % (upstream, (upstream_err or upstream_out).strip())
        )
    upstream_sha = upstream_out.strip()
    upstream_time = _git_text(root, "log", "-1", "--format=%cI", upstream)

    divergence = _git_text(
        root, "rev-list", "--left-right", "--count", "HEAD..." + upstream
    )
    parts = divergence.split()
    ahead, behind = int(parts[0]), int(parts[1])

    merge_base = _git_text(root, "merge-base", "HEAD", upstream)
    code, diff_raw, diff_err = _git(
        root,
        "diff",
        "--name-only",
        "--no-renames",
        "-z",
        merge_base,
        upstream,
    )
    if code != 0:
        raise RuntimeError("git diff failed: " + (diff_err or diff_raw).strip())
    upstream_paths = _split_z(diff_raw)

    code, status_raw, status_err = _git(root, "status", "--porcelain=v1", "-z")
    if code != 0:
        raise RuntimeError("git status failed: " + (status_err or status_raw).strip())
    local_entries = parse_status(status_raw)
    local_paths = sorted({entry["path"] for entry in local_entries})

    collision_pairs = []
    for upstream_path in upstream_paths:
        for local_path in local_paths:
            if collides(upstream_path, local_path):
                collision_pairs.append(
                    {"upstream": upstream_path, "local": local_path}
                )

    code, merge_tree_out, merge_tree_err = _git(
        root, "merge-tree", "--write-tree", "HEAD", upstream
    )
    if code == 0:
        merge_tree = "clean"
        merge_tree_detail = merge_tree_out.strip()
    elif code == 1:
        merge_tree = "conflict"
        merge_tree_detail = (merge_tree_out or merge_tree_err).strip()
    else:
        merge_tree = "unavailable"
        merge_tree_detail = (merge_tree_err or merge_tree_out).strip()

    index_lock = git_path(root, "index.lock")
    lock_state = path_state(index_lock)
    intermediate = {}
    for name in INTERMEDIATE_PATHS:
        state = path_state(git_path(root, name))
        if state["exists"]:
            intermediate[name] = state

    drift = {}
    if expect_ahead is not None and ahead != expect_ahead:
        drift["ahead"] = {"expected": expect_ahead, "actual": ahead}
    if expect_behind is not None and behind != expect_behind:
        drift["behind"] = {"expected": expect_behind, "actual": behind}
    if expect_head:
        if not head_full.startswith(expect_head.strip()):
            drift["head"] = {"expected": expect_head.strip(), "actual": head_short}

    return {
        "repo": str(root),
        "branch": branch,
        "head": head_full,
        "head_short": head_short,
        "upstream": upstream,
        "upstream_sha": upstream_sha,
        "upstream_committed_at": upstream_time,
        "ahead": ahead,
        "behind": behind,
        "upstream_path_count": len(upstream_paths),
        "local_path_count": len(local_paths),
        "local_paths": local_paths,
        "collisions": collision_pairs,
        "merge_tree": merge_tree,
        "merge_tree_detail": merge_tree_detail[:1000],
        "index_lock": lock_state,
        "intermediate": intermediate,
        "authorization_drift": drift,
        "baseline_provided": expect_ahead is not None
        or expect_behind is not None
        or bool(expect_head),
    }


def verdict(result):
    reasons = []
    state_blocked = result["index_lock"]["exists"] or bool(result["intermediate"])
    if state_blocked:
        reasons.append("index.lock or an in-progress git operation is present")
    if result["merge_tree"] == "conflict":
        reasons.append("merge-tree reports conflicts")
    elif result["merge_tree"] == "unavailable":
        reasons.append("merge-tree could not prove a conflict-free merge")
    if result["collisions"]:
        reasons.append(
            "%d upstream/local path collision(s)" % len(result["collisions"])
        )
    if result["authorization_drift"]:
        reasons.append("authorization baseline drifted")

    if state_blocked:
        code = EXIT_STATE
    elif result["merge_tree"] in ("conflict", "unavailable"):
        code = EXIT_CONFLICT
    elif result["collisions"]:
        code = EXIT_COLLISION
    elif result["authorization_drift"]:
        code = EXIT_DRIFT
    else:
        code = EXIT_CLEAR
    return code, reasons


def print_human(result, code, reasons):
    print("shared-branch merge gate (read-only)")
    print("repo:      %s" % result["repo"])
    print("branch:    %s" % result["branch"])
    print("HEAD:      %s (%s)" % (result["head_short"], result["head"]))
    print(
        "upstream:  %s @ %s (%s)"
        % (
            result["upstream"],
            result["upstream_sha"][:12],
            result["upstream_committed_at"],
        )
    )
    print("divergence: ahead %d / behind %d" % (result["ahead"], result["behind"]))
    print(
        "paths:     upstream %d / local dirty+untracked %d"
        % (result["upstream_path_count"], result["local_path_count"])
    )
    print("merge-tree: %s" % result["merge_tree"])
    if result["merge_tree_detail"]:
        first_line = result["merge_tree_detail"].splitlines()[0]
        print("           %s" % first_line[:300])
    print("index.lock: %s" % ("present" if result["index_lock"]["exists"] else "absent"))
    if result["index_lock"]["exists"]:
        print(
            "           size=%s mtime=%s"
            % (result["index_lock"].get("size"), result["index_lock"].get("mtime"))
        )
    if result["intermediate"]:
        print("intermediate: %s" % ", ".join(sorted(result["intermediate"])))
    else:
        print("intermediate: none")

    if result["collisions"]:
        print("collisions:")
        for pair in result["collisions"][:20]:
            print("  - %s  <->  %s" % (pair["upstream"], pair["local"]))
        if len(result["collisions"]) > 20:
            print("  ... %d more" % (len(result["collisions"]) - 20))
    else:
        print("collisions: none")

    if result["authorization_drift"]:
        print("authorization drift:")
        for key, delta in result["authorization_drift"].items():
            print(
                "  - %s: expected %s, actual %s"
                % (key, delta["expected"], delta["actual"])
            )
    elif result["baseline_provided"]:
        print("authorization drift: none")
    else:
        print("authorization drift: not checked (no --expect-* baseline)")

    print("")
    if code == EXIT_CLEAR:
        if result["behind"] == 0:
            print("verdict: CLEAR - nothing to merge; push directly if authorized")
        else:
            print("verdict: CLEAR")
        print("next: git -C %s merge --no-edit %s" % (result["repo"], result["upstream"]))
    else:
        print("verdict: BLOCKED (exit %d)" % code)
        for reason in reasons:
            print("  - %s" % reason)
        print("next: report these facts before changing any state")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Read-only pre-merge gate for shared worktrees.",
        epilog=(
            "Exit codes: 0 clear, 2 authorization drift, 3 conflict/unknown, "
            "4 path collision, 5 lock/intermediate state, 6 environment error. "
            "When multiple conditions hold, the highest-priority code wins in "
            "the order 6, 5, 3, 4, 2."
        ),
    )
    parser.add_argument("--repo", default=".", help="repository path (default: .)")
    parser.add_argument(
        "--upstream",
        default="origin/main",
        help="upstream ref to merge from (default: origin/main)",
    )
    parser.add_argument("--expect-ahead", type=int, help="authorized ahead count")
    parser.add_argument("--expect-behind", type=int, help="authorized behind count")
    parser.add_argument(
        "--expect-head", help="authorized HEAD SHA (full or sufficient prefix)"
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    if (args.expect_ahead is None) != (args.expect_behind is None):
        parser.error("--expect-ahead and --expect-behind must be provided together")

    try:
        result = collect(
            args.repo,
            args.upstream,
            args.expect_ahead,
            args.expect_behind,
            args.expect_head,
        )
    except RuntimeError as error:
        payload = {"error": str(error), "exit_code": EXIT_ENV}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("shared-branch merge gate (read-only)")
            print("verdict: ENVIRONMENT ERROR (exit %d)" % EXIT_ENV)
            print("  - %s" % error)
        return EXIT_ENV

    code, reasons = verdict(result)
    result["verdict"] = "clear" if code == EXIT_CLEAR else "blocked"
    result["exit_code"] = code
    result["reasons"] = reasons

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human(result, code, reasons)
    return code


if __name__ == "__main__":
    sys.exit(main())
