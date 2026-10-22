#!/usr/bin/env python3
"""V 阶段计数复核 第二轮：修正 i18n 键正则、确认 internal 根级包、统计顶层命令全口径。"""
import re
from pathlib import Path

SRC = Path(r"d:\spaces\SpecWeave\external\dao\flows\vibeknow\cli")

# ---- i18n 词条（键含点号）----
txt = (SRC / "internal" / "i18n" / "strings.go").read_text(encoding="utf-8", errors="replace")
keys = re.findall(r'^\s*"([a-z0-9_.]+)"\s*:', txt, re.M)
print("=== i18n 词条 ===")
print(f"源码词条数: {len(keys)}  (断言 392)")
print(f"去重后: {len(set(keys))}  (断言 196)")
pref = {}
for k in keys:
    p = k.split(".")[0]
    pref[p] = pref.get(p, 0) + 1
top = sorted(pref.items(), key=lambda kv: -kv[1])
print(f"前缀分布: {top}")

# ---- internal 根级文件（包 "."）----
print("\n=== internal 根级 go 文件 ===")
rootfiles = sorted(p.name for p in (SRC / "internal").glob("*.go") if not p.name.endswith("_test.go"))
print(f"{len(rootfiles)}: {rootfiles}")

# ---- 顶层命令全口径 ----
print("\n=== 顶层命令全口径 ===")
root = (SRC / "cmd" / "root.go").read_text(encoding="utf-8", errors="replace")
n_root = len(re.findall(r"rootCmd\.AddCommand\(", root))
others = []
for name in ("doctor", "completion", "update", "version"):
    f = SRC / "cmd" / f"{name}.go"
    if f.exists() and "rootCmd.AddCommand(" in f.read_text(encoding="utf-8", errors="replace"):
        others.append(name)
print(f"root.go init() 内注册: {n_root}")
print(f"各自 init() 内注册: {others} ({len(others)} 个)")
print(f"顶层命令合计: {n_root + len(others)}  (断言 19)")

# ---- 分组子命令合计 ----
print("\n=== 分组子命令 ===")
per = {}
for d in sorted((SRC / "cmd").iterdir()):
    if not d.is_dir():
        continue
    cnt = 0
    for p in sorted(d.glob("*.go")):
        if p.name.endswith("_test.go"):
            continue
        cnt += len(re.findall(r"\.AddCommand\(", p.read_text(encoding="utf-8", errors="replace")))
    if cnt:
        per[d.name] = cnt
print(f"{per}")
print(f"合计: {sum(per.values())}  (断言 41)")
