# -*- coding: utf-8 -*-
"""分析 format-report.json，输出样式体系/编号/页眉页脚/表格细节摘要"""
import json
import sys

r = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "examples/output/xs-format-report.json", encoding="utf-8"))

print("=== 1. 样式定义全览（id | type | name | basedOn）===")
id2name = {}
for s in r["styles"]:
    if "error" in s:
        continue
    id2name[s["style_id"]] = s["name"]
    line = "{:>6} | {:<22} | {}".format(s["style_id"], s["type"], s["name"])
    if s.get("basedOn"):
        line += "  <- " + s["basedOn"]
    print(line)

print("\n=== 2. 正文使用的样式ID -> 名称 ===")
for sid, n in r["stats"]["style_usage"].items():
    print("  {:>4} 段  id={:<6} name={}".format(n, sid, id2name.get(sid, "?")))

print("\n=== 3. 段落样式完整定义（非内置默认样式全量打印）===")
SKIP_IDS = set()
for s in r["styles"]:
    if "error" in s:
        continue
    if not s["type"].startswith("PARAGRAPH"):
        continue
    # 打印全部段落样式（含 toc/heading 等内置，便于完整审计）
    print("\n--- {} (id={}) basedOn={} next={} ---".format(
        s["name"], s["style_id"], s.get("basedOn"), s.get("next")))
    if s.get("rPr"):
        print("    rPr:", json.dumps(s["rPr"], ensure_ascii=False))
    if s.get("pPr"):
        print("    pPr:", json.dumps(s["pPr"], ensure_ascii=False))
    if s.get("tbl_borders"):
        print("    tblBorders:", json.dumps(s["tbl_borders"], ensure_ascii=False))

print("\n=== 4. 字符样式（CHARACTER，仅打印有 rPr 定义的）===")
for s in r["styles"]:
    if "error" in s:
        continue
    if s["type"].startswith("CHARACTER") and s.get("rPr"):
        print("--- {} (id={}) ---".format(s["name"], s["style_id"]))
        print("    rPr:", json.dumps(s["rPr"], ensure_ascii=False))

print("\n=== 5. 表格样式（TABLE）===")
for s in r["styles"]:
    if "error" in s:
        continue
    if s["type"].startswith("TABLE"):
        print("--- {} (id={}) ---".format(s["name"], s["style_id"]))
        if s.get("tbl_borders"):
            print("    borders:", json.dumps(s["tbl_borders"], ensure_ascii=False))

print("\n=== 6. 编号定义（numbering）===")
num = r.get("numbering", {})
print("num_map:", json.dumps(num.get("num_map", {}), ensure_ascii=False))
for aid, lvls in num.get("abstract", {}).items():
    print("\nabstractNumId={}:".format(aid))
    for il, lvl in lvls.items():
        print("  L{}: fmt={} text={!r} jc={} pPr={} rPr={}".format(
            il, lvl["numFmt"], lvl["lvlText"], lvl["lvlJc"],
            json.dumps(lvl.get("pPr", {}), ensure_ascii=False),
            json.dumps(lvl.get("rPr", {}), ensure_ascii=False)))

print("\n=== 7. 页眉页脚 ===")
for h in r["headers_footers"]:
    print(json.dumps(h, ensure_ascii=False))

print("\n=== 8. 表格首行（表头）格式采样 ===")
for t in r["tables"]:
    print("\nT{}: {}行x{}列 style={} align={}".format(t["index"], t["rows"], t["cols"], t["style"], t.get("align")))
    if t.get("first_row_cells"):
        c0 = t["first_row_cells"][0]
        print("   表头单元格[0]:", json.dumps(c0, ensure_ascii=False))
    if t.get("data_row_sample"):
        print("   数据单元格[0]:", json.dumps(t["data_row_sample"][0], ensure_ascii=False))
    if t.get("borders"):
        print("   表边框:", json.dumps(t["borders"], ensure_ascii=False))
    if t.get("cell_margins_twips"):
        print("   单元格边距(twips):", t["cell_margins_twips"])
