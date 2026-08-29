# -*- coding: utf-8 -*-
"""补充分析：docDefaults / 页眉页脚 / 封面与标题段落 / 媒体 / 特殊颜色段落"""
import json
import sys

r = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "examples/output/xmnn-format-report.json", encoding="utf-8"))

print("=== docDefaults ===")
print(json.dumps(r.get("docDefaults", {}), ensure_ascii=False, indent=1))

print("\n=== 媒体文件 ===")
for m in r.get("media", []):
    print("  {}  {}  {} bytes".format(m["partname"], m["content_type"], m["size_bytes"]))

print("\n=== 页眉页脚 ===")
for h in r["headers_footers"]:
    print(json.dumps(h, ensure_ascii=False))

paras = r["paragraphs"]
print("\n=== 前 45 个记录段落（封面/修订记录区）===")
for p in paras[:45]:
    rpr = p.get("run_rPr_sample", {})
    print("[{:>3}] style={:<10} len={:<4} {!r} | pPr={} | rPr={}".format(
        p["idx"], p.get("style_name"), p["len"], p["text_preview"][:45],
        json.dumps(p.get("pPr", {}), ensure_ascii=False),
        json.dumps(rpr, ensure_ascii=False)))

print("\n=== 全部 Heading 段落（验证编号方式）===")
for p in paras:
    if p.get("style_name", "").startswith("Heading"):
        print("[{:>3}] {} | {!r} | pPr={} | rPr={}".format(
            p["idx"], p["style_name"], p["text_preview"][:60],
            json.dumps(p.get("pPr", {}), ensure_ascii=False),
            json.dumps(p.get("run_rPr_sample", {}), ensure_ascii=False)))

print("\n=== 含特殊颜色的正文段落（#4E95D9/#215F9A/#EE0000/#3B3B3B）===")
for p in paras:
    c = p.get("run_rPr_sample", {}).get("color", "")
    if c in ("4E95D9", "215F9A", "EE0000"):
        print("[{:>3}] style={:<12} color={} {!r} | rPr={}".format(
            p["idx"], p.get("style_name"), c, p["text_preview"][:60],
            json.dumps(p.get("run_rPr_sample", {}), ensure_ascii=False)))

print("\n=== code 样式段落样本（前 8 个）===")
n = 0
for p in paras:
    if p.get("style_name") == "code":
        print("[{:>3}] {!r} | pPr={} | rPr={}".format(
            p["idx"], p["text_preview"][:70],
            json.dumps(p.get("pPr", {}), ensure_ascii=False),
            json.dumps(p.get("run_rPr_sample", {}), ensure_ascii=False)))
        n += 1
        if n >= 8:
            break

print("\n=== List Paragraph 样式段落样本（前 10 个）===")
n = 0
for p in paras:
    if p.get("style_name") == "List Paragraph":
        print("[{:>3}] {!r} | pPr={} | rPr={}".format(
            p["idx"], p["text_preview"][:60],
            json.dumps(p.get("pPr", {}), ensure_ascii=False),
            json.dumps(p.get("run_rPr_sample", {}), ensure_ascii=False)))
        n += 1
        if n >= 10:
            break
