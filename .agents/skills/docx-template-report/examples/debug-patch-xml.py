# -*- coding: utf-8 -*-
"""debug-patch-xml.py — 导出 docxtpl patch_xml 处理后的表格 XML，揭示 tr 标签解包机制。"""
import os, re, zipfile, tempfile
from docxtpl import DocxTemplate

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

for v in ["A", "B", "E"]:
    path = os.path.join(OUT, f"debug-rowloop-{v}-tpl.docx")
    if not os.path.exists(path):
        print(f"[{v}] template missing, skip"); continue
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    tpl = DocxTemplate(path)
    patched = tpl.patch_xml(xml)
    # 截取 tbl 段落
    m = re.search(r"<w:tbl>.*?</w:tbl>", patched, re.S)
    print(f"===== 写法 {v} patched tbl =====")
    print(m.group(0) if m else "no tbl found")
    print()
