#!/usr/bin/env python3
"""Assert that a temp-fixture teardown path stays inside %TEMP%.

Exit codes: 0 allowed / self-test passed, 1 self-test failed, 2 bad arguments,
3 refused by guard.
"""

import argparse
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

DEFAULT_PREFIX = "sw-fixture-"
# Depth counts components below the temp root. A mkdtemp fixture is depth 1,
# so the minimum is 1: strictly inside the root, never the root itself.
MIN_DEPTH = 1


class GuardError(RuntimeError):
    def __init__(self, reason, path=None, depth=None):
        super().__init__(reason)
        self.reason = reason
        self.path = str(path) if path is not None else "n/a"
        self.depth = "n/a" if depth is None else str(depth)


def temp_root() -> Path:
    return Path(tempfile.gettempdir()).resolve()


def is_link_like(path: Path) -> bool:
    checker = getattr(os.path, "isjunction", None)
    if checker is not None and checker(path):
        return True
    return os.path.islink(path)


def normalize(raw: Path) -> Path:
    # Resolve the parent only: resolving the entry itself would follow a
    # junction/symlink and turn "delete the link" into "delete the target".
    parent = raw.parent.resolve()
    return parent / raw.name


def guard_path(raw, prefix=DEFAULT_PREFIX, min_depth=MIN_DEPTH, root=None):
    text = "" if raw is None else str(raw).strip()
    if not text:
        raise GuardError("empty path")
    root = (root or temp_root()).resolve()
    path = normalize(Path(text).expanduser())
    if path == root:
        raise GuardError("path is the temp root itself", path, 0)
    try:
        rel = path.relative_to(root)
    except ValueError:
        raise GuardError(f"outside temp root {root}", path) from None
    if len(rel.parts) < min_depth:
        raise GuardError(f"depth {len(rel.parts)} below {min_depth}", path, len(rel.parts))
    if prefix and not rel.parts[0].startswith(prefix):
        raise GuardError(f"top-level name lacks prefix {prefix}", path, len(rel.parts))
    return path, rel


def create_fixture(prefix=DEFAULT_PREFIX) -> Path:
    path = Path(tempfile.mkdtemp(prefix=prefix)).resolve()
    guard_path(path, prefix=prefix)
    return path


def teardown(raw, prefix=DEFAULT_PREFIX) -> Path:
    path, _ = guard_path(raw, prefix=prefix)
    if is_link_like(path):
        if path.is_dir():
            os.rmdir(path)
        else:
            path.unlink()
        return path
    shutil.rmtree(path)
    return path


@contextmanager
def fixture(prefix=DEFAULT_PREFIX):
    root = create_fixture(prefix)
    try:
        yield root
    finally:
        if os.path.lexists(root):
            teardown(root, prefix=prefix)


def run_selftest() -> int:
    root = temp_root()
    failures = []

    def expect(name, ok, detail=""):
        print(f"{'PASS' if ok else 'FAIL'} {name} {detail}".rstrip())
        if not ok:
            failures.append(name)

    fixture_dir = create_fixture()
    expect("accept mkdtemp fixture", True, f"path={fixture_dir}")
    (fixture_dir / "realdir").mkdir()
    (fixture_dir / "realfile").write_text("x", encoding="utf-8")
    expect("fixture content created", (fixture_dir / "realfile").is_file())

    refused_cases = [
        ("refuse empty", ""),
        ("refuse drive root", "C:/"),
        ("refuse git-bash root", "/c"),
        ("refuse users dir", "C:/Users"),
        ("refuse temp root itself", str(root)),
    ]
    for name, candidate in refused_cases:
        try:
            guard_path(candidate)
        except GuardError as exc:
            expect(name, True, f"reason={exc.reason}")
        else:
            expect(name, False, "guard allowed the path")

    no_prefix = root / "plain-dir"
    try:
        guard_path(no_prefix)
    except GuardError as exc:
        expect("refuse unprefixed direct child", True, f"reason={exc.reason}")
    else:
        expect("refuse unprefixed direct child", False, "guard allowed the path")

    prefixed_shallow = root / f"{DEFAULT_PREFIX}selftest-shallow"
    try:
        guard_path(prefixed_shallow, min_depth=2)
    except GuardError as exc:
        expect("refuse depth below min_depth", True, f"reason={exc.reason}")
    else:
        expect("refuse depth below min_depth", False, "guard allowed the path")

    wrong_prefix = root / "other-dir" / "leaf"
    try:
        guard_path(wrong_prefix)
    except GuardError as exc:
        expect("refuse wrong prefix", True, f"reason={exc.reason}")
    else:
        expect("refuse wrong prefix", False, "guard allowed the path")

    teardown(fixture_dir)
    expect("fixture removed", not os.path.lexists(fixture_dir), f"path={fixture_dir}")

    with fixture() as scoped:
        (scoped / "nested").mkdir()
        expect("context fixture usable", (scoped / "nested").is_dir())
    expect("context fixture removed", not os.path.lexists(scoped))

    if failures:
        print(f"SELFTEST FAIL count={len(failures)}")
        return 1
    print("SELFTEST OK")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Assert a teardown path is an expendable temp fixture before deleting it."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", metavar="PATH", help="assert PATH may be deleted")
    group.add_argument("--selftest", action="store_true", help="run built-in positive and negative cases")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help=f"required fixture prefix (default {DEFAULT_PREFIX})")
    parser.add_argument("--min-depth", type=int, default=MIN_DEPTH, help=f"minimum depth below temp root (default {MIN_DEPTH})")
    args = parser.parse_args(argv)

    if args.selftest:
        return run_selftest()

    try:
        path, rel = guard_path(args.check, prefix=args.prefix, min_depth=args.min_depth)
    except GuardError as exc:
        print(f"REFUSE reason={exc.reason} path={exc.path} depth={exc.depth} root={temp_root()}")
        return 3
    print(f"ALLOW path={path} depth={len(rel.parts)} root={temp_root()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
