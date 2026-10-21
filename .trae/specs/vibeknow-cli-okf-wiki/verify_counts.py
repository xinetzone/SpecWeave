#!/usr/bin/env python3
"""V 阶段计数断言独立复核：用与 R 阶段不同的手段重新统计关键数量。

复核项：
1. internal/ 非测试代码行数合计 6803 + 27 个包 + 前三名 861/812/558
2. 端点数 39（account 5 / figlens 26 / vectoria 6 / vibeknow 2）
3. i18n 词条 392 条 / 去重 196 条
4. 顶层命令 19 个（按 rootCmd.AddCommand 调用点）
5. internal 包名列表
"""
import re
from pathlib import Path

SRC = Path(r"d:\spaces\SpecWeave\external\dao\flows\vibeknow\cli")

# ---------- 1. internal/ 代码行数与包数 ----------
print("=== 1. internal/ 包与行数 ===")
pkgs = {}
for p in sorted((SRC / "internal").rglob("*.go")):
    if p.name.endswith("_test.go"):
        continue
    rel = p.parent.relative_to(SRC / "internal")
    key = rel.as_posix() if rel.parts else "."
    pkgs.setdefault(key, 0)
    pkgs[key] += len(p.read_text(encoding="utf-8", errors="replace").splitlines())
total = sum(pkgs.values())
print(f"包数: {len(pkgs)}  (断言 27)")
print(f"非测试行数合计: {total}  (断言 6803)")
top3 = sorted(pkgs.items(), key=lambda kv: -kv[1])[:3]
print(f"前三: {top3}  (断言 httpclient 861 / cmdutil 812 / keychain 558)")

# ---------- 2. 端点数 ----------
print("\n=== 2. 后端端点数 ===")
ENDPOINT = re.compile(r"[\"'`](/v[0-9][^\"'`\s]*)[\"'`]")
counts = {}
for svc in ("account", "figlens", "vectoria", "vibeknow"):
    s = set()
    for p in (SRC / "client" / svc).rglob("*.go"):
        if p.name.endswith("_test.go"):
            continue
        for m in ENDPOINT.finditer(p.read_text(encoding="utf-8", errors="replace")):
            s.add(m.group(1))
    counts[svc] = len(s)
print(f"分服务去重: {counts}  (断言 account 5 / figlens 26 / vectoria 6 / vibeknow 2)")
print(f"合计: {sum(counts.values())}  (断言 39)")

# ---------- 3. i18n 词条 ----------
print("\n=== 3. i18n 词条 ===")
txt = (SRC / "internal" / "i18n" / "strings.go").read_text(encoding="utf-8", errors="replace")
keys = re.findall(r'"([a-z0-9_]+)"\s*:\s*', txt)
raw = len(re.findall(r'^\s*"[a-z0-9_]+"\s*:', txt, re.M))
uniq = len(set(keys))
print(f"源码词条行数: {raw}  (断言 392)")
print(f"去重键数: {uniq}  (断言 196)")

# ---------- 4. 顶层命令 ----------
print("\n=== 4. 顶层命令 ===")
root = (SRC / "cmd" / "root.go").read_text(encoding="utf-8", errors="replace")
adds = re.findall(r"rootCmd\.AddCommand\(([^)]+)\)", root)
print(f"AddCommand 调用数: {len(adds)}  (断言 19)")
print(f"列表: {adds}")

# ---------- 5. internal 包名 ----------
print("\n=== 5. internal 顶层包 ===")
subs = sorted(x.name for x in (SRC / "internal").iterdir() if x.is_dir())
print(f"{len(subs)} 个: {subs}")
