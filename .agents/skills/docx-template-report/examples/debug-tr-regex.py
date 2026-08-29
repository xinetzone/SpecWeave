# -*- coding: utf-8 -*-
"""debug-tr-regex.py — 直接对变体 A 的原始 XML 运行 docxtpl y="tr" 解包正则，打印匹配分组。"""
import os, re, zipfile

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
path = os.path.join(OUT, "debug-rowloop-A-tpl.docx")
with zipfile.ZipFile(path) as z:
    xml = z.read("word/document.xml").decode("utf-8")

tbl = re.search(r"<w:tbl>.*?</w:tbl>", xml, re.S).group(0)
print("===== 原始 tbl =====")
print(tbl)
print()

y = "tr"
pat = (
    r"<w:%(y)s[ >](?:(?!<w:%(y)s[ >]).)*({%%|{{)%(y)s ([^}%%]*(?:%%}|}})).*?</w:%(y)s>"
    % {"y": y}
)
for m in re.finditer(pat, tbl, flags=re.DOTALL):
    print(f"MATCH span={m.span()}")
    print(f"  group1={m.group(1)!r} group2={m.group(2)!r}")
    print(f"  matched text head: {m.group(0)[:120]!r}")
    print(f"  matched text tail: ...{m.group(0)[-120:]!r}")
    print()
