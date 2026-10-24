"""Markdown 锚点（`#fragment`）可达性校验。

**为什么需要它**：`check-links.py` 的校验方向是「链接 → 目标文件存在」，不校验
`#fragment` 是否真实存在于目标文件中。因此「改标题不改引用」可以在链接门禁全绿的
前提下留下锚点断链——V2.23 轮次即发生过：标题由「（当前版本）」改为「（**wiki 当前
结构版本**）」后 slug 变化，3 处旧 slug 引用未被任何门禁发现。

**它检查什么**：
1. 收集每个 `.md` 的全部标题，按 GitHub slug 规则生成锚点集合（同名标题按出现顺序
   追加 `-1` / `-2` 后缀，与 GitHub 行为一致）；
2. 扫描 `](path#fragment)` 形式的行内链接（跳过围栏代码块与外部 URL），逐条核对
   fragment 是否命中目标文件锚点集合；
3. 报告两类问题：**锚点断链**（目标存在但锚点不存在）与**目标文件缺失**。

**用法**：
    python .agents/scripts/check-anchors.py
    python .agents/scripts/check-anchors.py --path docs --exclude playground
    python .agents/scripts/check-anchors.py --path playground/life/workbuddy \
        --exempt wiki/themes/_template
    # 退出码 0 = 无锚点断链；1 = 有断链或目标缺失（逐条打印明细）
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))
_sys.path.insert(0, str(_Path(__file__).resolve().parent))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from constants import EXCLUDED_DIRS
from lib.cli import print_error, print_header, print_pass, print_warn

FENCE_RE = re.compile(r"^\s*(```|~~~)")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp://", "file://")
# 行号引用（`file.md#L12` / `#L12-L20`）是代码行定位约定，不是标题锚点，不参与校验
LINE_ANCHOR_RE = re.compile(r"^l\d+(-l\d+)?$")
# 占位符（`#<锚点>`、`#{{N锚点}}`、`#章节`）是模板/文档示例，不是真实锚点
PLACEHOLDER_RE = re.compile(r"[{}<>]")
# 站点/系统绝对路径（`/concepts/x.md`、`C:\repo\x.md`）无法按本地相对路径解析
ABSOLUTE_PATH_RE = re.compile(r"^(/|[A-Za-z]:[\\/]|~)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
MD_LINK_TEXT_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _strip_heading_markup(text: str) -> str:
    """剥离标题里的 HTML 标签与 Markdown 链接/图片标记，只保留渲染后可见文本。

    渲染后 `<kbd>Ctrl</kbd>` 只剩 `Ctrl`、`[标题](url)` 只剩 `标题`；若直接对原始
    Markdown 生成 slug，会把标签名与 URL 一并算进锚点，产生误报。
    """
    s = HTML_TAG_RE.sub("", text)
    s = MD_IMAGE_RE.sub(r"\1", s)
    s = MD_LINK_TEXT_RE.sub(r"\1", s)
    return s


def gh_slug(text: str, seen: dict) -> str:
    """按 GitHub 规则生成锚点 slug。

    流程：去 HTML/链接标记 → 小写 → 去 `*` 与反引号（渲染后不存在的强调标记）→
    去标点（保留字母数字、连字符、下划线、空格与 CJK）→ 空格转连字符 → 同名按出现
    次数追加序号后缀。

    注意 1：下划线在 GitHub 锚点中**保留**（`### fix_x.py` → `#fix_xpy`），因此不做删除；
    仅 `*`/反引号视为强调标记去除。
    注意 2：符号（emoji、方块图）被删除后**保留其后的空格**，渲染为前导连字符
    （`## ✅ 概览` → `#-概览`），因此去标点后不再 strip。
    """
    s = _strip_heading_markup(text).strip().lower()
    s = s.replace("*", "").replace("`", "")
    s = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", s, flags=re.UNICODE)
    s = s.replace(" ", "-")
    if s in seen:
        seen[s] += 1
        return "%s-%d" % (s, seen[s])
    seen[s] = 0
    return s


def docutils_slug(slug: str) -> str:
    """把 GitHub slug 归一到 docutils/Sphinx 风格：压缩连字符、去掉首尾连字符。

    为什么需要两种：本仓 Markdown 有两个渲染面——仓库托管（GitHub slugger，保留
    前导连字符与连续连字符）与 Sphinx/MyST 站点（docutils `make_id`，压缩并去首尾）。
    同一标题在两个渲染面会得到不同锚点。若只按 GitHub 规则校验，`## ⚠️ 警示`
    这类符号开头标题的 `#警示` 链接会被误报为断链。
    """
    s = re.sub(r"-{2,}", "-", slug)
    return s.strip("-")


def collect_anchors(path: Path) -> set:
    """返回该文件的锚点集合（跳过围栏代码块内的 `#` 注释行）。

    每个标题同时产出 GitHub 与 docutils 两种 slug，任一命中即视为可达——
    避免因渲染面不同而把有效锚点误报为断链。
    """
    anchors = set()
    seen = {}
    in_fence = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if m:
                gh = gh_slug(m.group(2), seen)
                anchors.add(gh)
                anchors.add(docutils_slug(gh))
    return anchors


def iter_md_files(root: Path, excluded: set) -> list:
    """遍历 root 下全部 .md，跳过 excluded 目录名。"""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in excluded)
        for name in sorted(filenames):
            if name.lower().endswith(".md"):
                files.append(Path(dirpath) / name)
    return sorted(files)


def is_exempt(path: Path, root: Path, exempt_prefixes: list) -> bool:
    """豁免路径（模板占位件的 `#锚点` 是占位符，不是真实引用）。"""
    if not exempt_prefixes:
        return False
    rel = path.relative_to(root).as_posix()
    return any(rel.startswith(p.rstrip("/") + "/") for p in exempt_prefixes)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Markdown 锚点（#fragment）可达性校验（check-links.py 不覆盖此维度）"
    )
    parser.add_argument("--path", default=".", help="待扫描目录（默认当前目录）")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="额外排除的目录名，可重复（默认已排除 .git/vendor/projects/.temp 等）",
    )
    parser.add_argument(
        "--exempt",
        action="append",
        default=[],
        help="豁免校验的路径前缀（相对 --path），可重复；用于模板占位件",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print_error(f"路径不存在或不是目录：{root}")
        return 1

    excluded = set(EXCLUDED_DIRS) | set(args.exclude)
    files = iter_md_files(root, excluded)
    if not files:
        print_warn(f"{root} 下未找到 .md 文件")
        return 0

    anchor_map = {}
    for p in files:
        anchor_map[os.path.normcase(str(p.resolve()))] = collect_anchors(p)

    broken, missing = [], []
    scanned = 0
    for p in files:
        if is_exempt(p, root, args.exempt):
            continue
        in_fence = False
        with open(p, encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                if FENCE_RE.match(line):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for target in LINK_RE.findall(line):
                    if target.startswith(EXTERNAL_SCHEMES):
                        continue
                    if "#" not in target:
                        continue
                    rel_path, frag = target.split("#", 1)
                    frag = unquote(frag.strip()).lower()
                    if not frag or LINE_ANCHOR_RE.match(frag) or PLACEHOLDER_RE.search(frag):
                        continue
                    rel_path = rel_path.split("?", 1)[0]
                    # 占位符路径与站点/系统绝对路径无法按本地相对路径解析，跳过以避免误报
                    if PLACEHOLDER_RE.search(rel_path) or ABSOLUTE_PATH_RE.match(rel_path):
                        continue
                    scanned += 1
                    if rel_path:
                        tgt = (p.parent / rel_path.replace("/", os.sep)).resolve()
                    else:
                        tgt = p.resolve()
                    key = os.path.normcase(str(tgt))
                    if key not in anchor_map:
                        # 目标在扫描根之外（如 .agents 引用 ../docs/）：不遍历其目录，
                        # 但文件存在时按需解析锚点，避免把跨根引用误报为「目标缺失」
                        if tgt.is_file():
                            anchor_map[key] = collect_anchors(tgt)
                        else:
                            missing.append((p, lineno, target))
                            continue
                    if frag not in anchor_map[key]:
                        broken.append((p, lineno, target))

    print(f"锚点核查：{len(files)} 个 md / {scanned} 条带锚点链接")

    if broken or missing:
        print_header("问题明细")
        for p, lineno, target in broken:
            print_error(f"锚点断链  {p.relative_to(root).as_posix()} L{lineno} -> {target}")
        for p, lineno, target in missing:
            print_error(f"目标缺失  {p.relative_to(root).as_posix()} L{lineno} -> {target}")
        print(f"\n未通过：锚点断链 {len(broken)} 条 / 目标文件缺失 {len(missing)} 条")
        return 1

    print_pass("全部通过：无锚点断链")
    return 0


if __name__ == "__main__":
    sys.exit(main())
