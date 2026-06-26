#!/usr/bin/env python3
"""构建文件引用反向索引：{目标文件: [引用文件列表]}。

扫描项目中所有 Markdown 文件，提取本地相对链接，建立反向引用索引。
在文件移动、删除、重构前，可快速查询受影响的引用方，避免断链遗漏。

用法：
  python build-ref-index.py                     # 构建索引并输出统计摘要
  python build-ref-index.py --query <文件>      # 查询引用了指定文件的所有文件
  python build-ref-index.py --query <文件1> <文件2>  # 批量查询
  python build-ref-index.py --query-dir <目录>  # 查询引用了指定目录下任意文件的文件
  python build-ref-index.py --json              # JSON 格式输出（便于工具集成）
  python build-ref-index.py --top N             # 显示被引用次数最多的 N 个文件
  python build-ref-index.py --orphans           # 列出未被任何文件引用的文件（孤立文件）
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_header, print_pass, print_warn
from lib.link_fixer import INLINE_LINK_RE

from constants import EXCLUDED_DIRS

CODE_BLOCK_RE = re.compile(r"```(?:.*?)\n(.*?)```", re.DOTALL)


@dataclass
class RefEntry:
    """单个引用关系记录。"""
    source: str
    target: str
    line_num: int
    link_text: str


@dataclass
class RefIndex:
    """反向引用索引。"""
    forward: dict[str, list[RefEntry]] = field(default_factory=lambda: defaultdict(list))
    backward: dict[str, list[RefEntry]] = field(default_factory=lambda: defaultdict(list))
    project_root: Path = field(default_factory=Path)

    def add_ref(self, source: Path, target: Path, line_num: int, link_text: str):
        """添加一条引用关系（使用相对路径作为键）。"""
        try:
            src_rel = source.resolve().relative_to(self.project_root.resolve()).as_posix()
            tgt_rel = target.resolve().relative_to(self.project_root.resolve()).as_posix()
        except ValueError:
            return

        entry = RefEntry(
            source=src_rel,
            target=tgt_rel,
            line_num=line_num,
            link_text=link_text,
        )
        self.forward[src_rel].append(entry)
        self.backward[tgt_rel].append(entry)

    def get_referrers(self, target: str) -> list[RefEntry]:
        """查询引用了指定目标文件的所有引用。"""
        return self.backward.get(target, [])

    def get_outgoing(self, source: str) -> list[RefEntry]:
        """查询指定文件的所有出链。"""
        return self.forward.get(source, [])

    def get_all_targets(self) -> list[str]:
        """获取所有被引用的目标文件列表（按引用次数降序）。"""
        return sorted(self.backward.keys(), key=lambda t: -len(self.backward[t]))

    def get_all_sources(self) -> list[str]:
        """获取所有有出链的源文件列表。"""
        return sorted(self.forward.keys())

    def get_orphans(self) -> list[str]:
        """获取未被任何其他文件引用的 Markdown 文件（孤立文件）。"""
        all_md = set()
        for md_file in self.project_root.rglob("*.md"):
            if _is_excluded(md_file, self.project_root):
                continue
            try:
                rel = md_file.resolve().relative_to(self.project_root.resolve()).as_posix()
                all_md.add(rel)
            except ValueError:
                continue

        referenced = set(self.backward.keys())
        return sorted(all_md - referenced)

    def to_json(self) -> dict:
        """序列化为 JSON 可序列化的字典。"""
        return {
            "project_root": str(self.project_root),
            "stats": {
                "total_sources": len(self.forward),
                "total_targets": len(self.backward),
                "total_refs": sum(len(refs) for refs in self.forward.values()),
            },
            "backward": {
                target: [
                    {"source": e.source, "line": e.line_num, "text": e.link_text}
                    for e in refs
                ]
                for target, refs in sorted(self.backward.items())
            },
        }


def _is_excluded(path: Path, project_root: Path) -> bool:
    """判断文件/目录是否应排除。"""
    try:
        rel = path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRS for part in rel.parts)


def _strip_code_blocks(content: str) -> str:
    """移除代码块内容，避免提取到示例中的链接。"""
    return CODE_BLOCK_RE.sub("", content)


def _resolve_link(source_file: Path, url: str, project_root: Path) -> Optional[Path]:
    """解析相对链接为绝对路径，仅返回本地存在的 Markdown/文件目标。

    返回 None 表示外部链接、锚点链接或目标不存在。
    """
    clean_url = url.split("#")[0].strip()

    if not clean_url:
        return None

    if clean_url.startswith(("http://", "https://", "mailto:", "file://")):
        return None

    target = (source_file.parent / clean_url).resolve()

    if target.is_dir():
        target = target / "README.md"

    if target.exists() and target.is_file():
        return target

    if not target.exists() and target.suffix == "":
        target_md = target.with_suffix(".md")
        if target_md.exists():
            return target_md

    return None


def build_index(project_root: Path, verbose: bool = True) -> RefIndex:
    """扫描整个项目构建反向引用索引。"""
    index = RefIndex(project_root=project_root)
    md_files = []

    for md_file in project_root.rglob("*.md"):
        if _is_excluded(md_file, project_root):
            continue
        md_files.append(md_file)

    if verbose:
        print(f"  扫描 {len(md_files)} 个 Markdown 文件...")

    total_links = 0
    for md_file in sorted(md_files):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            if verbose:
                print_warn(f"  无法读取 {md_file.name}: {e}")
            continue

        clean_content = _strip_code_blocks(content)
        lines = clean_content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for match in INLINE_LINK_RE.finditer(line):
                link_text = match.group(1)
                url = match.group(2).strip()

                target = _resolve_link(md_file, url, project_root)
                if target is not None:
                    index.add_ref(md_file, target, line_num, link_text)
                    total_links += 1

    if verbose:
        print(f"  索引构建完成: {len(index.forward)} 个源文件, "
              f"{len(index.backward)} 个目标文件, {total_links} 条引用关系")

    return index


def cmd_query(index: RefIndex, targets: list[str], as_json: bool = False):
    """执行查询：列出引用了指定目标文件的所有文件。"""
    results = {}
    for target in targets:
        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = (index.project_root / target_path).resolve()

        try:
            target_rel = target_path.resolve().relative_to(index.project_root.resolve()).as_posix()
        except ValueError:
            print_warn(f"  目标不在项目内: {target}")
            continue

        referrers = index.get_referrers(target_rel)
        results[target_rel] = referrers

    if as_json:
        output = {}
        for tgt, refs in results.items():
            output[tgt] = [
                {"source": r.source, "line": r.line_num, "text": r.link_text}
                for r in refs
            ]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    for tgt, refs in results.items():
        if not refs:
            print(f"\n  📄 {tgt}")
            print(f"     未被任何文件引用")
        else:
            print(f"\n  📄 {tgt}")
            print(f"     被 {len(refs)} 个文件引用:")
            current_source = None
            for r in sorted(refs, key=lambda x: (x.source, x.line_num)):
                if r.source != current_source:
                    print(f"       • {r.source}")
                    current_source = r.source
                print(f"           L{r.line_num}: [{r.link_text}]")


def cmd_query_dir(index: RefIndex, dir_path: str, as_json: bool = False):
    """查询引用了指定目录下任意文件的所有引用。"""
    dir_abs = Path(dir_path)
    if not dir_abs.is_absolute():
        dir_abs = (index.project_root / dir_abs).resolve()

    try:
        dir_rel = dir_abs.resolve().relative_to(index.project_root.resolve()).as_posix()
    except ValueError:
        print_warn(f"  目录不在项目内: {dir_path}")
        return

    all_refs = []
    for target, refs in index.backward.items():
        if target.startswith(dir_rel + "/") or target == dir_rel:
            all_refs.extend(refs)

    if as_json:
        output = {
            "directory": dir_rel,
            "referrers": [
                {"source": r.source, "target": r.target, "line": r.line_num, "text": r.link_text}
                for r in sorted(all_refs, key=lambda x: (x.source, x.target, x.line_num))
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"\n  📁 {dir_rel}/")
    if not all_refs:
        print(f"     目录下文件未被任何文件引用")
        return

    by_source = defaultdict(list)
    for r in all_refs:
        by_source[r.source].append(r)

    print(f"     被 {len(by_source)} 个文件引用（共 {len(all_refs)} 条引用）:")
    for src, refs in sorted(by_source.items()):
        targets = sorted(set(r.target.split("/")[-1] for r in refs))
        print(f"       • {src}")
        for t in targets[:5]:
            print(f"           → {t}")
        if len(targets) > 5:
            print(f"           ... 及其他 {len(targets) - 5} 个文件")


def cmd_top(index: RefIndex, n: int, as_json: bool = False):
    """显示被引用次数最多的文件。"""
    targets = index.get_all_targets()
    top = [(t, len(index.backward[t])) for t in targets[:n]]

    if as_json:
        print(json.dumps([{"target": t, "ref_count": c} for t, c in top], ensure_ascii=False, indent=2))
        return

    print(f"\n  🏆 被引用次数 Top {n}:")
    for i, (tgt, count) in enumerate(top, 1):
        sources = sorted(set(r.source for r in index.backward[tgt]))
        print(f"    {i:2d}. [{count:3d} refs] {tgt}")
        if len(sources) <= 5:
            for s in sources:
                print(f"         ← {s}")
        else:
            for s in sources[:3]:
                print(f"         ← {s}")
            print(f"         ... 及其他 {len(sources) - 3} 个文件")


def cmd_orphans(index: RefIndex, as_json: bool = False):
    """列出未被任何文件引用的孤立文件。"""
    orphans = index.get_orphans()

    if as_json:
        print(json.dumps({"orphans": orphans}, ensure_ascii=False, indent=2))
        return

    print(f"\n  🔍 孤立文件（未被任何其他 Markdown 文件引用）:")
    if not orphans:
        print_pass("    无孤立文件")
        return

    for f in orphans:
        print(f"    • {f}")
    print_warn(f"    共 {len(orphans)} 个孤立文件")


def cmd_stats(index: RefIndex, as_json: bool = False):
    """输出索引统计摘要。"""
    stats = {
        "total_sources": len(index.forward),
        "total_targets": len(index.backward),
        "total_refs": sum(len(refs) for refs in index.forward.values()),
        "top_referenced": [
            (t, len(index.backward[t]))
            for t in index.get_all_targets()[:10]
        ],
    }

    if as_json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    print(f"\n  📊 索引统计:")
    print(f"     有源文件（含出链）: {stats['total_sources']}")
    print(f"     被引用目标:         {stats['total_targets']}")
    print(f"     总引用关系:         {stats['total_refs']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="构建文件引用反向索引，查询文件引用关系"
    )
    parser.add_argument(
        "--query", "-q",
        nargs="+",
        metavar="FILE",
        help="查询引用了指定文件的所有文件（可指定多个）"
    )
    parser.add_argument(
        "--query-dir", "-Q",
        metavar="DIR",
        help="查询引用了指定目录下任意文件的所有文件"
    )
    parser.add_argument(
        "--top", "-t",
        type=int,
        default=10,
        metavar="N",
        help="显示被引用次数最多的 N 个文件（默认 10）"
    )
    parser.add_argument(
        "--orphans", "-o",
        action="store_true",
        help="列出未被任何文件引用的孤立文件"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="仅显示统计摘要"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="以 JSON 格式输出（便于工具集成）"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式，减少输出"
    )
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)

    if not args.quiet and not args.json:
        print_header("文件引用反向索引")
        print(f"  项目根: {project_root}")

    index = build_index(project_root, verbose=not args.quiet and not args.json)

    did_something = False

    if args.query:
        cmd_query(index, args.query, as_json=args.json)
        did_something = True

    if args.query_dir:
        cmd_query_dir(index, args.query_dir, as_json=args.json)
        did_something = True

    if args.top and not args.stats and not args.query and not args.query_dir and not args.orphans:
        cmd_top(index, args.top, as_json=args.json)
        did_something = True
    elif args.top and (args.query or args.query_dir or args.orphans):
        pass

    if args.orphans:
        cmd_orphans(index, as_json=args.json)
        did_something = True

    if args.stats or not did_something:
        cmd_stats(index, as_json=args.json)
        if not args.json and not args.quiet:
            cmd_top(index, min(args.top, 10), as_json=False)
        did_something = True

    return 0


if __name__ == "__main__":
    sys.exit(main())
