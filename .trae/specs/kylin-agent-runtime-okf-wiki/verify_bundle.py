#!/usr/bin/env python3
"""V 阶段束内验证：frontmatter 必填键、束内链接可达性、禁链扫描（仅针对 kylin-agent-runtime 束）。"""
import re, sys, pathlib

B = pathlib.Path(r"d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\jishu\ai\frameworks\ai-agent\kylin-agent-runtime")
REQ = ["type:", "title:", "description:", "tags:", "generated:", "verified:", "status:", "stale_after:", "sources:"]
errors, warnings = [], []
checked_links = 0

def split_fm(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[4:end], text[end+4:]
    return None, text

for md in sorted(B.rglob("*.md")):
    rel = md.relative_to(B).as_posix()
    text = md.read_text(encoding="utf-8")
    fm, body = split_fm(text)
    is_index = md.name == "index.md"
    if rel in ("index.md",):
        for k in ["type:", "okf_version:"]:
            if k not in (fm or ""):
                errors.append(f"{rel}: 根 index 缺 {k}")
        continue
    if is_index:
        if fm is not None:
            warnings.append(f"{rel}: 子目录 index 含 frontmatter（规范要求无）")
        if "{toctree}" not in text:
            errors.append(f"{rel}: 子目录 index 缺 toctree")
        continue
    if md.parent.name == "spec" and fm is not None:
        for k in ["type:", "title:", "generated:", "status:", "sources:"]:
            if k not in fm:
                errors.append(f"{rel}: frontmatter 缺 {k}")
    elif rel == "log.md":
        if fm is None or "type:" not in fm:
            errors.append(f"{rel}: log frontmatter 异常")
    elif fm is None:
        errors.append(f"{rel}: 缺 frontmatter")
    else:
        for k in REQ:
            if k not in fm:
                errors.append(f"{rel}: frontmatter 缺 {k}")
    if "file:///" in text:
        errors.append(f"{rel}: 含 file:/// 链接")
    if re.search(r"(?<![A-Za-z0-9])[a-z]:[\\/]", body):
        errors.append(f"{rel}: 正文含本地盘符绝对路径")
    if "external/dao" in text or "external\\dao" in text:
        errors.append(f"{rel}: 含本地 external 路径")
    # 链接检查
    for m in re.finditer(r"\]\(([^)]+)\)", body):
        tgt = m.group(1).split("#", 1)[0].strip()
        if not tgt or tgt.startswith(("http://", "https://", "mailto:")):
            continue
        checked_links += 1
        if tgt.startswith("/"):
            p = B / tgt.lstrip("/")
        else:
            p = (md.parent / tgt).resolve()
        if not p.exists():
            errors.append(f"{rel}: 断链 -> {tgt}")
    if "## 相关概念" not in body and md.parent.name in ("concepts", "examples"):
        warnings.append(f"{rel}: 缺 ## 相关概念")

print(f"检查内容/信源文档链接数: {checked_links}")
print(f"ERRORS: {len(errors)}")
for e in errors:
    print("  [ERROR]", e)
print(f"WARNINGS: {len(warnings)}")
for w in warnings:
    print("  [WARN]", w)
sys.exit(1 if errors else 0)
