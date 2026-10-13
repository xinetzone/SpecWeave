# -*- coding: utf-8 -*-
"""Plane bundle V 阶段机械门禁等效验证（无第三方依赖）"""
import re, os, io, sys, glob

ROOT = r"D:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\jishu\dev\plane"
SPEC = r"D:\spaces\SpecWeave\.trae\specs\plane-okf-wiki"
ok = True

def check(label, cond, detail=""):
    global ok
    print(("  PASS  " if cond else "  FAIL  ") + label + (("  -> " + detail) if detail else ""))
    if not cond:
        ok = False

print("== 1. 双份 F 编号一致性 ==")
pat = re.compile(r"^\|\s*F-(\d{3})\s*\|", re.M)
def ids(path):
    with io.open(path, encoding="utf-8") as f:
        return [int(x) for x in pat.findall(f.read())]
a = ids(os.path.join(SPEC, "facts.md"))
b = ids(os.path.join(ROOT, "references", "article-source.md"))
check("facts.md 与 article-source.md 编号集合相等", sorted(set(a)) == sorted(set(b)),
      "spec=%d 条 / bundle=%d 条" % (len(set(a)), len(set(b))))
check("编号连续无跳号", sorted(set(a)) == list(range(1, max(a) + 1)),
      "区间 F-%03d ~ F-%03d" % (min(a), max(a)))

print("== 2. toctree 条目文件存在 ==")
for idx in glob.glob(os.path.join(ROOT, "**", "index.md"), recursive=True):
    base = os.path.dirname(idx)
    with io.open(idx, encoding="utf-8") as f:
        txt = f.read()
    for block in re.findall(r"```\{toctree\}(.*?)```", txt, re.S):
        entries = [l.strip() for l in block.splitlines()
                   if l.strip() and not l.strip().startswith(":")]
        for e in entries:
            p = os.path.join(base, e + ".md")
            check("%s -> %s" % (os.path.relpath(idx, ROOT), e), os.path.exists(p))

print("== 3. 相对链接可达 ==")
link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
files = glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)
bad = []
for f in files:
    with io.open(f, encoding="utf-8") as fh:
        txt = fh.read()
    for m in link.findall(txt):
        t = m.split("#")[0].strip()
        if not t or t.startswith(("http://", "https://", "mailto:", "file:///")):
            if t.startswith("file:///"):
                bad.append((f, m))
            continue
        p = os.path.normpath(os.path.join(os.path.dirname(f), t))
        if not os.path.exists(p):
            bad.append((f, m))
check("全部相对链接可达（且无 file:/// 绝对路径）", not bad,
      "; ".join("%s -> %s" % (os.path.relpath(x, ROOT), y) for x, y in bad[:5]))

print("== 4. UTF-8 严格 roundtrip ==")
badenc = []
for f in files:
    with open(f, "rb") as fh:
        raw = fh.read()
    try:
        raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as e:
        badenc.append((f, str(e)))
check("全部 .md 严格 UTF-8 解码通过", not badenc, str(badenc[:3]))

print("== 5. 敏感路径零残留 ==")
sens = re.compile(r"C:\\\\Users\\|C:/Users/|/Users/|D:\\\\spaces\\\\SpecWeave")
hits = []
for f in files:
    with io.open(f, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            if sens.search(line):
                hits.append((os.path.relpath(f, ROOT), i))
check("家目录/绝对路径零出现", not hits, str(hits[:5]))

print("== 6. frontmatter 必填字段 ==")
req = ["okf_version", "type", "title", "description", "generated", "verified", "status", "stale_after"]
with io.open(os.path.join(ROOT, "index.md"), encoding="utf-8") as f:
    fm = f.read().split("---")[1]
missing = [k for k in req if not re.search(r"^%s:" % k, fm, re.M)]
check("根 index frontmatter 齐备", not missing, str(missing))
check("sources 含博文 + 官方权威源",
      fm.count("url:") >= 5 and "mp.weixin.qq.com" in fm and "developers.plane.so" in fm)

print("\nRESULT:", "ALL PASS" if ok else "HAS FAILURES")
sys.exit(0 if ok else 1)
