#!/usr/bin/env python3
"""V 阶段：bundle 内相对链接、toctree 覆盖、frontmatter 必填字段机械检查。"""
import re
import sys
from pathlib import Path

BUNDLE = Path(
    r"d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\jishu\ai\products\vibeknow-cli"
)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TOCTREE = re.compile(r"```\{toctree\}\n(.*?)```", re.S)

problems = []


def read(p):
    return p.read_text(encoding="utf-8")


def check_links():
    n = 0
    for md in BUNDLE.rglob("*.md"):
        for link in LINK.findall(read(md)):
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if "://" in link:
                problems.append(f"[绝对URI] {md.relative_to(BUNDLE)} -> {link}")
                continue
            if link.startswith("/"):
                # bundle-relative 绝对路径
                target = BUNDLE / link.lstrip("/")
            else:
                target = (md.parent / link).resolve()
            n += 1
            if not target.exists():
                problems.append(f"[断链] {md.relative_to(BUNDLE)} -> {link}")
    return n


def check_toctrees():
    total = 0
    for md in BUNDLE.rglob("index.md"):
        text = read(md)
        m = TOCTREE.search(text)
        if not m:
            problems.append(f"[缺toctree] {md.relative_to(BUNDLE)}")
            continue
        total += 1
        entries = [ln.strip() for ln in m.group(1).splitlines()
                   if ln.strip() and not ln.strip().startswith(":")]
        for e in entries:
            stem = e if e.endswith(".md") else e + ".md"
            if e.startswith("/"):
                target = BUNDLE / stem.lstrip("/")
            else:
                target = (md.parent / stem).resolve()
            if not target.exists():
                problems.append(f"[toctree断链] {md.relative_to(BUNDLE)} -> {e}")
    # 内容文档必须可达
    for md in BUNDLE.rglob("*.md"):
        if md.name in ("index.md", "log.md"):
            continue
        if md.parent.name in ("concepts", "examples", "references"):
            idx = md.parent / "index.md"
            if md.stem not in read(idx):
                problems.append(f"[未登记] {md.relative_to(BUNDLE)} 未出现在 {idx.relative_to(BUNDLE)}")
    return total


def check_frontmatter():
    n = 0
    for md in BUNDLE.rglob("*.md"):
        text = read(md)
        reserved = md.name in ("index.md", "log.md")
        if not text.startswith("---"):
            if not reserved:
                problems.append(f"[无frontmatter] {md.relative_to(BUNDLE)}")
            continue
        end = text.find("\n---", 3)
        if end < 0:
            problems.append(f"[frontmatter未闭合] {md.relative_to(BUNDLE)}")
            continue
        fm = text[3:end]
        n += 1
        if "type:" not in fm:
            problems.append(f"[缺type] {md.relative_to(BUNDLE)}")
        # okf_version 只允许在根 index.md
        if "okf_version:" in fm and not (md.name == "index.md" and md.parent == BUNDLE):
            problems.append(f"[okf_version越位] {md.relative_to(BUNDLE)}")
        # sources[].resource 必填
        for blk in re.findall(r"sources:\n((?:\s+- .*\n|\s+.*\n)*)", fm):
            if "- id:" in blk and "resource:" not in blk and "url:" not in blk:
                problems.append(f"[sources缺resource] {md.relative_to(BUNDLE)}")
        # generated.by 必填
        if "generated:" in fm and "by:" not in fm.split("generated:")[1][:200]:
            problems.append(f"[generated缺by] {md.relative_to(BUNDLE)}")
    return n


def check_sensitive_paths():
    """只标记真实出现的本机绝对路径；正文中对 file:/// 约定的描述性提及不计。"""
    pats = (r"file:///[A-Za-z]", r"[A-Za-z]:\\Users\\", r"[A-Za-z]:\\spaces\\")
    for md in BUNDLE.rglob("*.md"):
        t = read(md)
        for pat in pats:
            for m in re.finditer(pat, t):
                problems.append(f"[敏感路径] {md.relative_to(BUNDLE)} 含 {m.group(0)!r}")


def check_f_refs():
    facts = read(BUNDLE / "references" / "source-facts.md")
    registered = set(re.findall(r"\bF-(\d{3})\b", facts))
    print(f"F 编号登记数: {len(registered)} (断言 104)")
    if len(registered) != 104:
        problems.append(f"[F编号数] 登记 {len(registered)} != 104")
    # 连续性
    nums = sorted(int(x) for x in registered)
    if nums != list(range(1, 105)):
        gaps = [i for i in range(1, 105) if i not in nums]
        problems.append(f"[F编号不连续] 缺 {gaps[:20]}")
    # 正文引用
    cited = set()
    for md in BUNDLE.rglob("*.md"):
        if md.name == "source-facts.md":
            continue
        cited |= set(re.findall(r"\bF-(\d{3})\b", read(md)))
    unknown = sorted(cited - registered)
    if unknown:
        problems.append(f"[未登记引用] 正文引用了未登记的 F 编号: {unknown}")
    print(f"正文引用 F 编号数: {len(cited)}")


links = check_links()
trees = check_toctrees()
fms = check_frontmatter()
check_sensitive_paths()
check_f_refs()

print(f"相对链接检查: {links} 条")
print(f"index.md 带 toctree: {trees} 个")
print(f"frontmatter 解析: {fms} 个")
print(f"\n问题数: {len(problems)}")
for p in problems:
    print("  " + p)
sys.exit(1 if problems else 0)
