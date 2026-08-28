#!/usr/bin/env python3
"""CI gate：扫描 docs/ 下所有 Markdown 文件的 UTF-8 有效性。

用法:
    python scripts/check-utf8.py            # 扫描 docs/（默认，递归）
    python scripts/check-utf8.py [PATH...]  # 扫描指定目录/文件
    python scripts/check-utf8.py --self-test  # 运行破坏性探针自检

退出码:
    0  全部文件为有效 UTF-8（CI 通过）；或自检通过
    1  存在非法 UTF-8 文件，并已列出（CI gate 拦截）；或自检发现 gate 失效
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCAN = (ROOT,)
EXCLUDE_DIRS = {"_build", "_static", "_templates", ".git", "__pycache__"}
EXTENSIONS = {".md", ".rst", ".txt"}


def iter_targets(paths) -> list[Path]:
    """展开输入路径为待检查文件列表。"""
    files: list[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            print(f"错误: 路径不存在: {p}", file=sys.stderr)
            continue
        if p.is_file():
            files.append(p)
        else:
            for f in p.rglob("*"):
                if f.is_file() and any(part in EXCLUDE_DIRS for part in f.parts):
                    continue
                if f.suffix in EXTENSIONS:
                    files.append(f)
    return files


def check_file(path: Path) -> bool:
    """返回该文件是否为有效 UTF-8。"""
    try:
        path.read_bytes().decode("utf-8")
        return True
    except UnicodeDecodeError as exc:
        display = _display_path(path)
        print(f"非法 UTF-8: {display}  (偏移 {exc.start})")
        return False
    except OSError as exc:
        print(f"读取失败: {_display_path(path)}: {exc}", file=sys.stderr)
        return False


def _display_path(path: Path) -> str:
    """返回相对 ROOT 的路径；ROOT 外（如临时探针）回退绝对路径。"""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def self_test() -> bool:
    """破坏性探针双向自检。"""
    bad_text = "中文字符被截断: \xe7\x9f\xad".encode("utf-8", "replace")[:-1]
    probe = Path(tempfile.gettempdir()) / "probe-bad-utf8-docs.md"
    good_probe = Path(tempfile.gettempdir()) / "probe-good-utf8-docs.md"
    try:
        probe.write_bytes(bad_text)
        if check_file(probe):
            print("自检失败: 破坏性探针文件未被拦截（gate 失效）", file=sys.stderr)
            return False
        good_probe.write_text("# 有效 UTF-8 中文测试\n", encoding="utf-8")
        if not check_file(good_probe):
            print("自检失败: 正常文件被误判为非法（gate 过严）", file=sys.stderr)
            return False
        print("自检通过: check-utf8.py 既能拦截非法 UTF-8，也能放行有效 UTF-8。")
        return True
    finally:
        probe.unlink(missing_ok=True)
        good_probe.unlink(missing_ok=True)


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return 0 if self_test() else 1

    targets = DEFAULT_SCAN if not args else [Path(a) for a in args]
    files = iter_targets(targets)
    if not files:
        print("未找到任何可扫描文件", file=sys.stderr)
        return 1

    bad = [f for f in files if not check_file(f)]
    if bad:
        print(f"\n检测到 {len(bad)} 个非法 UTF-8 文件，CI gate 拦截。")
        return 1

    print(f"UTF-8 检查通过: {len(files)} 个文件均为有效 UTF-8。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
