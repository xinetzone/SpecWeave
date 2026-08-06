#!/usr/bin/env python3
"""提交前质量门禁：拒绝 Markdown 文档中仍含盘符绑定 file:/// 绝对路径的链接。

正则特征：`file:///[A-Za-z]:/`（Windows 绝对盘符引用），命中表示该链接
在跨机器/跨环境迁移时必然断链，必须在提交前转为相对路径或按 B 桶模式内联化。

使用方式：
    # 默认扫描当前工作目录下所有 **/*.md
    python .agents/scripts/check-absolute-path-links.py

    # 只扫描指定路径（文件或目录）
    python .agents/scripts/check-absolute-path-links.py --path .agents/docs/knowledge

    # 扫描多个目录
    python .agents/scripts/check-absolute-path-links.py --paths .agents/docs .trae/specs

退出码：
    0  无命中（通过门禁）
    1  命中 ≥ 1 条绝对盘符链接（门禁拦截）
    2  参数错误
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310
enforce_python310()

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List, Tuple

# ---- 共享常量 ----
# 与 check-links.py 保持一致的默认排除目录
DEFAULT_EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv",
    "__pycache__", ".idea", ".vscode", ".tox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", "target",
    ".trae/cache", ".agents/cache",
}

# 命中目标：盘符绑定的 file:/// 绝对路径
ABS_DRIVE_RE = re.compile(r'file:///[A-Za-z]:/')

# 匹配 Markdown 链接语法（含显式 [text](url) 与自动链接 <url>）
# 注意：为了零第三方依赖，手写两层识别，不引入 mistune。
MD_INLINE_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
MD_AUTOLINK_RE = re.compile(r'<(file:///[^>\s]+)>')  # 自动链接只抓 file 开头


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() == ".md":
            yield root
        return
    for p in sorted(root.rglob("*.md")):
        # 排除已知的黑名单目录
        if any(part in DEFAULT_EXCLUDED_DIRS for part in p.parts):
            continue
        try:
            if p.is_file():
                yield p
        except OSError:
            continue


def _collect_hits_in_file(path: Path) -> List[Tuple[int, str, int, str]]:
    """返回 list[(line_no, line_content_truncated, col_offset, matched_url)]。
    自动跳过三引号/三波浪 fenced code block 内部内容，避免 C++ lambda/call 语法误报。"""
    hits: List[Tuple[int, str, int, str]] = []
    fence_stack = 0
    fence_marker: str | None = None

    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return hits

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.lstrip()
        # Fenced code block 判定：``` 或 ~~~ 独占行首（允许前置缩进）
        fence_match = re.match(r'^(\s*)(```+|~~~+)', raw_line)
        if fence_match:
            marker = fence_match.group(2)
            marker_char = marker[0]
            marker_len = len(marker)
            if fence_stack == 0:
                # 进入代码块
                fence_stack = 1
                fence_marker = marker_char * marker_len
            else:
                # 闭合：相同字符且长度 ≥ 开围栏
                if fence_marker and marker_char == fence_marker[0] and marker_len >= len(fence_marker):
                    fence_stack = 0
                    fence_marker = None
            # 围栏行本身也不参与链接解析（避免三引号里写的链接样例被扫）
            continue

        if fence_stack > 0:
            continue

        # 类型 1：[text](url) 形式
        for m in MD_INLINE_LINK_RE.finditer(raw_line):
            url = m.group(2)
            # 去掉可能的 "title" 部分（url "..."）
            url_clean = url.split(" ", 1)[0].split("\t", 1)[0]
            if ABS_DRIVE_RE.search(url_clean):
                col = m.start(2)
                trunc = raw_line.rstrip()
                if len(trunc) > 160:
                    trunc = trunc[:160] + "…"
                hits.append((lineno, trunc, col, url_clean))

        # 类型 2：<file:///...> 自动链接形式
        for m in MD_AUTOLINK_RE.finditer(raw_line):
            url = m.group(1)
            col = m.start(1)
            trunc = raw_line.rstrip()
            if len(trunc) > 160:
                trunc = trunc[:160] + "…"
            hits.append((lineno, trunc, col, url))

    return hits


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Markdown 绝对盘符链接门禁：检出 file:///[A-Z]:/ 形式的绝对路径链接",
    )
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--path",
        help="扫描单个文件或目录（默认：当前工作目录）",
        default=None,
    )
    group.add_argument(
        "--paths",
        nargs="+",
        help="扫描多个文件或目录（与 --path 互斥）",
        default=None,
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="额外打印每条命中的上下文（列号 + 匹配 URL）",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # 解析扫描目标
    targets: list[Path]
    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
        missing = [str(t) for t in targets if not t.exists()]
        if missing:
            print(f"[GATE-AA1] 参数错误：以下路径不存在 -> {', '.join(missing)}", file=sys.stderr)
            return 2
    elif args.path:
        t = Path(args.path).resolve()
        if not t.exists():
            print(f"[GATE-AA1] 参数错误：路径不存在 -> {t}", file=sys.stderr)
            return 2
        targets = [t]
    else:
        targets = [Path.cwd()]

    # 扫描所有目标，收集命中
    file_hits: dict[str, List[Tuple[int, str, int, str]]] = defaultdict(list)
    file_count = 0
    for root in targets:
        for md_file in _iter_markdown_files(root):
            file_count += 1
            h = _collect_hits_in_file(md_file)
            if h:
                rel = md_file.resolve()
                try:
                    rel_display = rel.relative_to(Path.cwd())
                except ValueError:
                    rel_display = rel
                file_hits[str(rel_display)].extend(h)

    total_hits = sum(len(v) for v in file_hits.values())

    print(f"[GATE-AA1] 扫描完成：共扫描 {file_count} 个 Markdown 文件，命中 {total_hits} 条绝对盘符链接。")

    if total_hits == 0:
        print("[GATE-AA1] 结果：通过 ✅（零 file:///<盘符>:/ 绝对路径链接）")
        return 0

    # 门禁拦截，结构化打印
    print("[GATE-AA1] 结果：拦截 ❌ — 请把以下绝对盘符链接改为相对路径，或按 B 桶模式内联化后再提交：")
    print("=" * 88)
    for fname, items in sorted(file_hits.items()):
        print(f"\n📄 {fname}  （{len(items)} 条）")
        for (lineno, line, col, url) in items:
            if args.verbose:
                print(f"  L{lineno}:C{col}  URL={url}")
                print(f"       | {line}")
            else:
                print(f"  L{lineno}: {line}")
    print("=" * 88)
    print(f"[GATE-AA1] 统计：{len(file_hits)} 个文件 × 共 {total_hits} 条。修复方式：")
    print("  - 若目标文件在本仓库内：改为相对路径引用；若跨盘符：转义为内联代码或本地路径说明。")
    print("  - 若目标属外部 vendor/历史归档：按 ExtBucket B 桶模式，转反引号内联 + 失效注记。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
