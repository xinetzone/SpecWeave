#!/usr/bin/env python3
"""V阶段对抗审查：tkinter 三束 + gui 组索引。
检查项：frontmatter YAML 可解析 / 残留外链 / file协议 / 脚注配平 / 图片与本地链接存在性。
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(r"d:\spaces\SpecWeave\projects\awesome-okf-xs")
BUNDLES = ROOT / "doc" / "bundles" / "jishu" / "gui"
STATIC = ROOT / "doc" / "_static"

TARGETS = [
    BUNDLES / "tkinter-gui-design",
    BUNDLES / "tkinter-handbook",
    BUNDLES / "tkinterx-handbook",
]
EXTRA_FILES = [BUNDLES / "index.md"]

fm_re = re.compile(r"\A---\n(.*?)\n---\n", re.S)
img_re = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
link_re = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
fn_ref_re = re.compile(r"\[\^([^\]]+)\](?!:)")
fn_def_re = re.compile(r"^\[\^([^\]]+)\]:", re.M)
url_re = re.compile(r"https?://[^\s)\"']+")

errors = []
warns = []
files = []
for t in TARGETS:
    files += sorted(t.rglob("*.md"))
files += EXTRA_FILES

for f in files:
    rel = f.relative_to(ROOT)
    text = f.read_text(encoding="utf-8")
    body = text
    # frontmatter 要求（遵循存量束 pyqt5-gui 惯例）：
    # 束根/分组根 index.md 与 NN-*.md 内容文档必须携带；
    # 子目录 index.md（concepts/examples/references）与 log.md 不带 frontmatter
    needs_fm = not (
        f.name == "log.md"
        or (f.name == "index.md" and f.parent.name in ("concepts", "examples", "references"))
    )
    m = fm_re.match(text)
    if m:
        fm_text = m.group(1)
        body = text[m.end():]
        if yaml:
            try:
                data = yaml.safe_load(fm_text)
                if not isinstance(data, dict):
                    errors.append(f"[YAML] {rel}: frontmatter 非 dict")
            except Exception as e:
                errors.append(f"[YAML] {rel}: {e}")
    elif needs_fm:
        errors.append(f"[FM] {rel}: 缺少 frontmatter")

    is_sources = f.name == "sources.md" or "references" in f.parts
    # 残留外链
    for i, ln in enumerate(body.splitlines(), 1):
        for um in url_re.finditer(ln):
            url = um.group(0).rstrip('.,')
            if is_sources:
                continue
            errors.append(f"[URL] {rel}:{i}: {url}")
        if "file:///" in ln:
            errors.append(f"[FILE] {rel}:{i}: file 协议链接")
    # 脚注配平
    refs = set(fn_ref_re.findall(body))
    defs = set(fn_def_re.findall(body))
    miss = refs - defs
    extra = defs - refs
    if miss:
        errors.append(f"[FN] {rel}: 引用未定义脚注 {sorted(miss)}")
    if extra:
        warns.append(f"[FN] {rel}: 定义未引用脚注 {sorted(extra)}")
    # 图片存在性
    for im in img_re.finditer(body):
        p = im.group(1).split()[0].strip('"')
        if p.startswith("http"):
            errors.append(f"[IMG-URL] {rel}: 远程图片未本地化: {p}")
            continue
        target = (f.parent / p).resolve()
        if not target.exists():
            errors.append(f"[IMG-MISS] {rel}: 图片不存在: {p}")
    # 本地 markdown 链接存在性（跳过 toctree 由门禁管、跳过锚点）
    for lm in link_re.finditer(body):
        p = lm.group(1).split()[0].strip('"')
        if p.startswith(("http", "#", "mailto:")):
            continue
        p = p.split("#")[0]
        if not p:
            continue
        target = (f.parent / p).resolve()
        if not target.exists():
            errors.append(f"[LINK-MISS] {rel}: 本地链接不存在: {p}")

print(f"扫描 {len(files)} 个 md 文件")
print(f"ERRORS: {len(errors)}")
for e in errors:
    print("  ✗", e)
print(f"WARNS: {len(warns)}")
for w in warns:
    print("  ⚠", w)
sys.exit(1 if errors else 0)
