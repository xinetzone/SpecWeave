#!/usr/bin/env python3
"""扫描 Markdown 文件中的链接，校验外部 URL 可达性与本地文件引用有效性。
支持 --fix 自动修复可修复的断链，包括：
- file:/// 绝对路径转相对路径
- 相对路径层级自动校正（目录迁移后 ../ 层数不对的问题）
- 目录链接尾部斜杠补全
- 文件名重命名映射"""

import argparse
import re
import sys
import urllib.request
import urllib.error
import ssl
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from constants import (
    EXCLUDED_DIRS,
    LINK_CHECK_TIMEOUT,
    LINK_CHECK_WORKERS,
    LINK_CHECK_EXCLUDE_DIRS,
    LINK_CHECK_USER_AGENT,
)
from lib.link_fixer import is_code_fence_context

# 匹配 Markdown 内联链接: [text](url)
INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
# 匹配引用式链接定义: [ref]: url
REF_LINK_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(.+)$", re.MULTILINE)
# 匹配引用式链接使用: [text][ref]
REF_USAGE_RE = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")


CURLY_PLACEHOLDER_RE = re.compile(r"\{[^}]+\}")


def is_template_placeholder(url: str) -> bool:
    """判断 URL 是否为模板占位符（如 <!-- ... --> 或 {变量名} 格式）。"""
    if url.startswith("<!--") and url.endswith("-->"):
        return True
    if CURLY_PLACEHOLDER_RE.search(url):
        return True
    return False


def find_markdown_files(root_dir: Path, exclude_dirs: set[str]) -> list[Path]:
    """递归查找所有 Markdown 文件。"""
    md_files = []
    for md_path in root_dir.rglob("*.md"):
        parts = set(md_path.parts)
        # 排除系统目录
        if EXCLUDED_DIRS & parts:
            continue
        # 排除用户指定的目录（按目录名或相对路径匹配）
        try:
            rel_path = md_path.relative_to(root_dir)
        except ValueError:
            rel_path = md_path
        rel_str = rel_path.as_posix()
        if any(rel_str.startswith(excl.replace("\\", "/")) for excl in exclude_dirs):
            continue
        md_files.append(md_path)
    return md_files


def parse_links(file_path: Path) -> list[tuple[str, str, int]]:
    """解析 Markdown 文件中的链接，返回 (文本, URL, 行号) 列表。"""
    content = file_path.read_text(encoding="utf-8")
    links = []

    # 收集引用式链接定义
    ref_defs = {}
    for m in REF_LINK_RE.finditer(content):
        ref_id = m.group(1).lower()
        ref_url = m.group(2).strip()
        if not is_template_placeholder(ref_url):
            ref_defs[ref_id] = ref_url

    # 解析内联链接
    for m in INLINE_LINK_RE.finditer(content):
        if is_code_fence_context(content, m.start()):
            continue
        text = m.group(1)
        url = m.group(2).strip()
        if url and not url.startswith("#") and not is_template_placeholder(url):
            line_num = content[: m.start()].count("\n") + 1
            links.append((text, url, line_num))

    # 解析引用式链接使用 (不含定义行)
    for m in REF_USAGE_RE.finditer(content):
        if is_code_fence_context(content, m.start()):
            continue
        ref_id = m.group(2).strip().lower()
        if ref_id and ref_id in ref_defs:
            text = m.group(1)
            line_num = content[: m.start()].count("\n") + 1
            links.append((text, ref_defs[ref_id], line_num))

    return links


def is_external_url(url: str) -> bool:
    """判断 URL 是否为外部链接。"""
    return url.startswith("http://") or url.startswith("https://")


def is_local_ref(url: str) -> bool:
    """判断 URL 是否为本地文件引用。"""
    return not is_external_url(url) and not url.startswith("#") and not url.startswith("mailto:")


def check_external_link(url: str, timeout: int) -> tuple[str, int, str]:
    """检查外部链接是否可达。返回 (url, http_status, error_message)。"""
    ctx = ssl.create_default_context()
    # 对于证书问题，不验证（类似浏览器行为）
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", LINK_CHECK_USER_AGENT)

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return (url, resp.status, "")
    except urllib.error.HTTPError as e:
        # 405: 部分服务器不支持 HEAD，可视为链接存在
        # 403: 服务器拒绝非浏览器请求（反爬虫），链接本身通常有效
        if e.code in (405, 403):
            return (url, e.code, "")
        return (url, e.code, str(e))
    except urllib.error.URLError as e:
        return (url, 0, str(e.reason))
    except Exception as e:
        return (url, 0, str(e))


def check_local_link(file_path: Path, url: str) -> tuple[str, bool, str]:
    """检查本地文件引用是否存在。返回 (url, exists, error_message)。"""
    # 处理相对路径
    base_dir = file_path.parent
    # 移除 URL 中的锚点部分
    clean_url = url.split("#")[0]
    if not clean_url:
        return (url, True, "")

    target = (base_dir / clean_url).resolve()
    if target.exists():
        return (url, True, "")
    return (url, False, f"文件不存在: {target}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="扫描 Markdown 文件中的链接，校验外部 URL 可达性与本地文件引用有效性。"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="指定扫描的目录路径（默认为项目根目录）",
    )
    parser.add_argument(
        "--check-external",
        action="store_true",
        default=False,
        help="同时检查外部 HTTP/HTTPS 链接（默认仅检查本地文件引用）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=LINK_CHECK_TIMEOUT,
        help="外部链接检查超时秒数（默认 10 秒）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以 JSON 格式输出结果",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=LINK_CHECK_WORKERS,
        help="并发检查外部链接的线程数（默认 5）",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        nargs="*",
        default=LINK_CHECK_EXCLUDE_DIRS,
        help="额外排除的目录名称（默认排除 docs/templates）",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="自动修复可修复的断链（绝对路径转相对路径、相对路径层级校正、目录斜杠补全等）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="与 --fix 配合使用，仅预览修复内容不写入文件",
    )
    parser.add_argument(
        "--rename",
        type=str,
        nargs="*",
        default=[],
        metavar="OLD=NEW",
        help="文件名重命名映射（用于文件迁移后修复引用），如 --rename 旧名.html=新名.html",
    )
    args = parser.parse_args()

    root = args.path or Path(__file__).parent.parent.parent
    if not root.exists():
        print(f"错误: 路径不存在: {root}", file=sys.stderr)
        return 1

    exclude_dirs = set(args.exclude)
    print("=" * 60)
    print("Markdown 链接校验")
    print("=" * 60)

    # 查找 Markdown 文件
    print(f"\n扫描目录: {root}")
    if exclude_dirs:
        print(f"排除目录: {', '.join(sorted(exclude_dirs))}")
    md_files = find_markdown_files(root, exclude_dirs)
    print(f"找到 {len(md_files)} 个 Markdown 文件")

    # 自动修复（--fix）
    rename_map = {}
    for mapping in args.rename:
        if "=" in mapping:
            old, new = mapping.split("=", 1)
            rename_map[old] = new

    if args.fix:
        from lib.link_fixer import fix_directory_links, print_fix_report, _infer_project_root
        dry_run = args.dry_run
        mode_str = "预览修复（dry-run）" if dry_run else "自动修复"
        print(f"\n0. {mode_str}...")
        project_root = _infer_project_root(root)
        fixes = fix_directory_links(
            root, project_root,
            rename_map=rename_map or None,
            dry_run=dry_run,
            exclude_dirs=exclude_dirs,
        )
        if fixes:
            print_fix_report(fixes, dry_run=dry_run)
        else:
            print("  未发现需要修复的断链。")

    # 解析所有链接
    all_links: list[tuple[Path, str, str, int]] = []  # (文件, 文本, URL, 行号)
    for md_file in md_files:
        links = parse_links(md_file)
        for text, url, line_num in links:
            all_links.append((md_file, text, url, line_num))

    # 分类链接
    external_links = [(f, t, u, ln) for f, t, u, ln in all_links if is_external_url(u)]
    local_links = [(f, t, u, ln) for f, t, u, ln in all_links if is_local_ref(u)]
    other_links = [(f, t, u, ln) for f, t, u, ln in all_links if not is_external_url(u) and not is_local_ref(u)]

    print(f"  内联链接: {len(all_links)}")
    print(f"  外部链接: {len(external_links)}")
    print(f"  本地引用: {len(local_links)}")
    print(f"  其他链接: {len(other_links)}（锚点/mailto 等）")

    # 检查本地文件引用
    broken_local = []
    print(f"\n1. 检查本地文件引用（共 {len(local_links)} 个）...")
    for file_path, text, url, line_num in local_links:
        url_str, exists, error = check_local_link(file_path, url)
        if not exists:
            rel_path = file_path.relative_to(root) if root in file_path.parents else file_path
            broken_local.append((rel_path, line_num, text, url_str, error))

    if broken_local:
        print(f"   失败: {len(broken_local)} 个断链")
        for rel_path, line_num, text, url, error in broken_local:
            print(f"     [{rel_path}:{line_num}] {text} -> {url} ({error})")
    else:
        print(f"   通过: 所有本地引用均有效")

    # 检查外部链接（可选）
    broken_external = []
    if args.check_external and external_links:
        print(f"\n2. 检查外部链接（共 {len(external_links)} 个，超时 {args.timeout}s）...")
        unique_urls = set(u for _, _, u, _ in external_links)

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(check_external_link, url, args.timeout): url for url in unique_urls}
            url_results = {}
            for future in as_completed(futures):
                url, status, error = future.result()
                url_results[url] = (status, error)

        for file_path, text, url, line_num in external_links:
            status, error = url_results.get(url, (0, "未检查"))
            # 403/405 视为可接受（反爬虫 / 不支持 HEAD）
            if status == 0 or (status >= 400 and status not in (403, 405)):
                rel_path = file_path.relative_to(root) if root in file_path.parents else file_path
                broken_external.append((rel_path, line_num, text, url, status, error))

        if broken_external:
            print(f"   失败: {len(broken_external)} 个不可达链接")
            for rel_path, line_num, text, url, status, error in broken_external:
                print(f"     [{rel_path}:{line_num}] {text} -> {url} (HTTP {status}: {error})")
        else:
            print(f"   通过: 所有外部链接均可达")
    elif not args.check_external:
        print(f"\n2. 跳过外部链接检查（使用 --check-external 启用）")
        print(f"   共 {len(external_links)} 个外部链接待检查")

    # JSON 输出
    if args.json:
        import json
        result = {
            "summary": {
                "total_files": len(md_files),
                "total_links": len(all_links),
                "external_links": len(external_links),
                "local_links": len(local_links),
                "other_links": len(other_links),
                "broken_local": len(broken_local),
                "broken_external": len(broken_external),
            },
            "broken_local": [
                {
                    "file": str(f),
                    "line": ln,
                    "text": t,
                    "url": u,
                    "error": e,
                }
                for f, ln, t, u, e in broken_local
            ],
            "broken_external": [
                {
                    "file": str(f),
                    "line": ln,
                    "text": t,
                    "url": u,
                    "status": s,
                    "error": e,
                }
                for f, ln, t, u, s, e in broken_external
            ],
        }
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))

    # 汇总
    print("\n" + "=" * 60)
    total_broken = len(broken_local) + len(broken_external)
    if total_broken == 0:
        print("校验通过: 所有链接均有效")
        print("=" * 60)
        return 0
    else:
        print(f"校验失败: 发现 {total_broken} 个断链（本地 {len(broken_local)}，外部 {len(broken_external)}）")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())