# -*- coding: utf-8 -*-
"""第五轮：封面表 r2 内容 / header XML / settings / 真实H1段落编号覆盖检查"""
import sys, zipfile, re

src = sys.argv[1] if len(sys.argv) > 1 else r"d:\AI\.chaos\tests\old\work\doc\XMNN_SDK_使用指南v1.1.0.docx"
z = zipfile.ZipFile(src)
doc_xml = z.read("word/document.xml").decode("utf-8")

print("=== 1. 封面表 row2 原始 XML ===")
m = re.search(r'<w:tbl>(?:(?!</w:tbl>).)*?浙江芯劢.*?</w:tbl>', doc_xml, re.S)
seg = m.group(0)
rows = re.findall(r'<w:tr[ >].*?</w:tr>', seg, re.S)
print(rows[2][:1500])

print("\n=== 2. 封面表之后的结构（前 1200 字符）===")
after = doc_xml[doc_xml.index(seg) + len(seg):doc_xml.index(seg) + len(seg) + 1200]
print(after)

print("\n=== 3. header1.xml 内容（logo + 公司名 + 页码）===")
h1 = z.read("word/header1.xml").decode("utf-8")
texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', h1)
print("文本:", texts)
print("含图片:", "<w:drawing" in h1 or "<w:pict" in h1)
print("PAGE 域:", "PAGE" in h1)
print("表格:", h1.count("<w:tbl>"))

print("\n=== 4. 真实 H1 段落（body 直属，排除 sdt）编号检查 ===")
# 找 body 直属 w:p 中 pStyle=2 的段落
body_m = re.search(r'<w:body>(.*)</w:body>', doc_xml, re.S)
body = body_m.group(1)
# 移除 sdt 块
body_nosdt = re.sub(r'<w:sdt>.*?</w:sdt>', '', body, flags=re.S)
for m in re.finditer(r'<w:p [^>]*>(?:(?!</w:p>).)*?</w:p>', body_nosdt, re.S):
    p = m.group(0)
    if '<w:pStyle w:val="2"/>' in p:
        txt = "".join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))
        numpr = re.search(r'<w:numPr>.*?</w:numPr>', p, re.S)
        pbr = "<w:br w:type=\"page\"" in p or 'w:type="page"' in p
        sect = "<w:sectPr" in p
        print(f"  H1: {txt[:30]!r} numPr={numpr.group(0) if numpr else '继承样式(有编号)'} pageBreak={pbr} sectPr={sect}")

print("\n=== 5. H2/H3 样式编号链接（abstract 2 的 pStyle 绑定）===")
num_xml = z.read("word/numbering.xml").decode("utf-8")
m = re.search(r'<w:abstractNum w:abstractNumId="2"[^>]*>(.*?)</w:abstractNum>', num_xml, re.S)
for lvl in re.finditer(r'<w:lvl w:ilvl="(\d)"[^>]*>(.*?)</w:lvl>', m.group(1), re.S):
    il, body_l = lvl.groups()
    ps = re.search(r'<w:pStyle w:val="(\d+)"/>', body_l)
    fmt = re.search(r'<w:numFmt w:val="([^"]+)"/>', body_l)
    txt = re.search(r'<w:lvlText w:val="([^"]*)"/>', body_l)
    ind = re.search(r'<w:ind ([^/]+)/>', body_l)
    print(f"  L{il}: pStyle={ps.group(1) if ps else '-'} fmt={fmt.group(1) if fmt else '-'} text={txt.group(1) if txt else '-'} ind={ind.group(1) if ind else '-'}")

print("\n=== 6. settings.xml 关键项 ===")
st = z.read("word/settings.xml").decode("utf-8")
for pat, name in [(r'<w:defaultTabStop w:val="(\d+)"/>', "defaultTabStop"),
                  (r'<w:docVars>.*?</w:docVars>', "docVars"),
                  (r'<w:proofState[^/]*/>', "proofState"),
                  (r'<w:characterSpacingControl[^/]*/>', "characterSpacingControl")]:
    mm = re.search(pat, st, re.S)
    if mm:
        print(f"  {name}: {mm.group(0)[:120]}")
