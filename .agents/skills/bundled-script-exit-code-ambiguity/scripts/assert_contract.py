#!/usr/bin/env python3
"""Assert the three-part contract of a bundled script for one contract path.

Checks, in order: exit code equals the expected value, stdout parses as JSON
(when --json is given), stderr carries no traceback, and stderr is empty
(unless the contract declares diagnostics on this path via --allow-stderr).
A case that reports the expected exit code while emitting a traceback is a
script defect, not a pass.

Exit codes
  0  every assertion for this case held
  1  at least one assertion failed (details on stderr)
  2  usage error, or the command could not be started
"""

import argparse
import json
import subprocess
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Assert exit code, stdout shape, and stderr silence of one contract path."
    )
    parser.add_argument("--expect", type=int, required=True, help="expected exit code")
    parser.add_argument("--json", action="store_true", help="require stdout to parse as JSON")
    parser.add_argument(
        "--allow-stderr",
        action="store_true",
        help="the contract declares diagnostics on this path (a traceback is still a failure)",
    )
    parser.add_argument("--name", default="case", help="label printed in the report")
    parser.add_argument("cmd", nargs=argparse.REMAINDER, help="command to run, after --")
    args = parser.parse_args(argv)
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        parser.error("no command given; put it after --")
    return args, cmd


def check_stdout(stdout, require_json):
    if not require_json:
        return None
    if not stdout.strip():
        return "stdout: empty, expected JSON (did the process die before printing?)"
    try:
        json.loads(stdout)
    except ValueError as exc:
        return f"stdout: not JSON ({exc})"
    return None


def main(argv=None):
    args, cmd = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        print(f"cannot execute {cmd[0]}: {exc}", file=sys.stderr)
        return 2

    failures = []
    if proc.returncode != args.expect:
        failures.append(f"exit code: expected {args.expect}, got {proc.returncode}")
    stdout_problem = check_stdout(proc.stdout, args.json)
    if stdout_problem:
        failures.append(stdout_problem)
    if "Traceback (most recent call last)" in proc.stderr:
        failures.append("stderr: traceback present (untrapped exception)")
    elif not args.allow_stderr and proc.stderr.strip():
        failures.append("stderr: not empty (undeclared diagnostic)")

    if not failures:
        shape = "json" if args.json else "unchecked"
        diag = "declared" if args.allow_stderr else "empty"
        print(f"PASS {args.name}: exit={proc.returncode} stdout={shape} stderr={diag}")
        return 0

    print(f"FAIL {args.name}: exit={proc.returncode}", file=sys.stderr)
    for item in failures:
        print(f"  - {item}", file=sys.stderr)
    if proc.stderr.strip():
        print("--- captured stderr ---", file=sys.stderr)
        print(proc.stderr.rstrip(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
