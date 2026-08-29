# -*- coding: utf-8 -*-
"""检查既有 tech-guide-template 的标签 XML 放置方式（段落 vs 表格 vs 单元格）。"""
import zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
path = r"templates/tech-guide-template.docx"
with zipfile.ZipFile(path) as z:
    root = etree.fromstring(z.read("word/document.xml"))

body = root.find(f"{{{W}}}body")

def para_text(p):
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

for i, ch in enumerate(body):
    tag = etree.QName(ch).localname
    if tag == "p":
        txt = para_text(ch)
        if "{%" in txt:
            print(f"[{i}] PARA-TAG: {txt.strip()[:80]!r}")
    elif tag == "tbl":
        print(f"[{i}] TABLE start")
        for ri, tr in enumerate(ch.findall(f"{{{W}}}tr")):
            cells = tr.findall(f"{{{W}}}tc")
            for ci, tc in enumerate(cells):
                for p in tc.findall(f"{{{W}}}p"):
                    txt = para_text(p)
                    if "{%" in txt or "{{" in txt:
                        print(f"      r{ri}c{ci}: {txt.strip()[:70]!r}")
    else:
        print(f"[{i}] {tag}")
