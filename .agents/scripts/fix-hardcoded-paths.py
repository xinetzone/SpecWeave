#!/usr/bin/env python3
r"""可复用的「硬编码路径批量修复」工具。

扫描指定目录下 .py 与 .ipynb 文件，将硬编码的旧路径根目录
（如 d:\flexloop / d:/flexloop / D:\flexloop / d:\\flexloop，不区分大小写）
批量替换为新的路径根目录（如 d:\spaces\chaos\flexloop）。

处理时保留原始分隔符风格（反斜杠数量、正斜杠）与盘符大小写，例如：
    d:\\flexloop  -> d:\\spaces\\chaos\\flexloop   （.py 源码中的双反斜杠）
    d:\flexloop   -> d:\spaces\chaos\flexloop    （单反斜杠）
    d:/flexloop   -> d:/spaces/chaos/flexloop    （正斜杠）
    D:\flexloop   -> D:\spaces\chaos\flexloop    （保持盘符大小写）

「旧路径根目录 / 新路径片段」可在下方常量中调整；默认扫描目录由命令行
--dir 指定（不内置真实个人路径作为默认值）。

用法：
    python fix-hardcoded-paths.py --dir <扫描目录>             # 仅预览（dry-run，默认）
    python fix-hardcoded-paths.py --dir <扫描目录> --apply     # 实际写入文件
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ============ 可按需调整的路径配置 ============
# 旧路径的根目录名（正则中用于匹配的结尾部分）
_OLD_ROOT = "flexloop"
# 新路径的片段（不含盘符与首个分隔符，由工具按原始分隔符风格拼接）
_NEW_ROOT = "spaces/chaos/flexloop"
# =============================================

# 匹配旧路径根目录。不区分大小写，可选单个或多个反斜杠或正斜杠作为分隔符，
# 并保留匹配到的盘符字母。
# 示例可匹配：d:\flexloop、d:/flexloop、D:\flexloop、d:\\flexloop、D:\\flexloop
_OLD_PATH_RE = re.compile(
    rf"(?i)(?P<drive>[a-z]):(?P<sep>\\+|/+){re.escape(_OLD_ROOT)}"
)


def _replacement(match: re.Match) -> str:
    """根据匹配到的分隔符风格与盘符大小写生成新路径。"""
    drive = match.group("drive")
    sep = match.group("sep")
    if sep.startswith("/"):
        # 正斜杠风格
        return f"{drive}:/{_NEW_ROOT}"
    # 反斜杠风格：保留原始反斜杠数量（单反斜杠或双反斜杠）
    bs = "\\" * len(sep)
    return f"{drive}:{bs}{_NEW_ROOT.replace('/', bs)}"


def _fix_text(text: str) -> tuple[str, int]:
    """对文本执行替换，返回 (新文本, 替换次数)。"""
    new_text, count = _OLD_PATH_RE.subn(_replacement, text)
    return new_text, count


def fix_py_file(path: Path, apply: bool) -> tuple[int, int]:
    """处理 .py 文件，返回 (替换次数, 失败计数)。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  [跳过] 无法读取 {path}: {exc}")
        return 0, 1

    new_text, count = _fix_text(text)
    if count == 0:
        return 0, 0

    print(f"  待修复: {path}  ({count} 处)")
    for old_line, new_line in zip(text.splitlines(), new_text.splitlines()):
        if old_line != new_line:
            print(f"    旧: {old_line.strip()}")
            print(f"    新: {new_line.strip()}")

    if apply:
        try:
            path.write_text(new_text, encoding="utf-8")
        except OSError as exc:
            print(f"  [跳过] 写入失败 {path}: {exc}")
            return count, 1
    return count, 0


def fix_ipynb_file(path: Path, apply: bool) -> tuple[int, int]:
    """处理 .ipynb 文件，返回 (替换次数, 失败计数)。

    通过 json.load 解析，遍历 cells[].source 中的字符串列表进行替换，
    写回时用 json.dump 保证 JSON 合法。
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  [跳过] 无法读取/解析 {path}: {exc}")
        return 0, 1

    total = 0
    changed_cells = []
    for cell_idx, cell in enumerate(data.get("cells", [])):
        source = cell.get("source")
        if isinstance(source, str):
            # 兼容单字符串形式
            source = [source]
            cell["source"] = source
        if not isinstance(source, list):
            continue

        cell_count = 0
        for i, chunk in enumerate(source):
            if not isinstance(chunk, str):
                continue
            new_chunk, sub_count = _fix_text(chunk)
            if sub_count:
                source[i] = new_chunk
                cell_count += sub_count
        if cell_count:
            total += cell_count
            changed_cells.append((cell_idx, cell_count))

    if total == 0:
        return 0, 0

    print(f"  待修复: {path}  ({total} 处)")
    for cell_idx, cell_count in changed_cells:
        print(f"    Cell #{cell_idx}: {cell_count} 处")

    if apply:
        try:
            # 保持与原文件一致：ensure_ascii=False 保留中文可读，缩进为 2 空格
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"  [跳过] 写入失败 {path}: {exc}")
            return total, 1
    return total, 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            f"批量修复硬编码旧路径根目录 "
            f"{_OLD_ROOT} -> {_NEW_ROOT}（支持 .py / .ipynb，dry-run 与 apply 双模式）"
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="确认写入，实际修改文件内容（默认仅预览，不写文件）",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path.cwd(),
        help="要扫描的目录（默认：当前工作目录，建议显式指定目标目录）",
    )
    args = parser.parse_args()

    target_dir = args.dir
    if not target_dir.is_dir():
        print(f"错误：目录不存在 {target_dir}", file=sys.stderr)
        return 1

    mode = "APPLY（写入）" if args.apply else "DRY-RUN（仅预览，不写文件）"
    print(f"扫描目录: {target_dir}")
    print(f"模式: {mode}")
    print("-" * 60)

    py_files = sorted(target_dir.glob("*.py"))
    ipynb_files = sorted(target_dir.glob("*.ipynb"))
    scanned = len(py_files) + len(ipynb_files)
    fixes = 0
    skipped = 0

    for path in py_files:
        fixes += fix_py_file(path, args.apply)[0]
    for path in ipynb_files:
        result = fix_ipynb_file(path, args.apply)
        fixes += result[0]
        skipped += result[1]

    print("-" * 60)
    print(f"扫描文件数: {scanned}")
    print(f"修复位置数: {fixes}")
    print(f"跳过项: {skipped}")
    if not args.apply:
        print("提示: 使用 --apply 参数应用修复并写入文件。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
