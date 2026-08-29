# -*- coding: utf-8 -*-
"""第四轮：原始 XML 验证——标题编号真实性 / T0封面第三行 / TOC域 / 颜色run完整文本"""
import sys, zipfile, re

src = sys.argv[1] if len(sys.argv) > 1 else r"d:\AI\.chaos\tests\old\work\doc\XMNN_SDK_使用指南v1.1.0.docx"
z = zipfile.ZipFile(src)

doc_xml = z.read("word/document.xml").decode("utf-8")
styles_xml = z.read("word/styles.xml").decode("utf-8")
try:
    num_xml = z.read("word/numbering.xml").decode("utf-8")
except KeyError:
    num_xml = ""

print("=== 1. TOC 域检查 ===")
toc_hits = re.findall(r'instrText[^>]*>([^<]*(?:TOC|NOTEREF|REF)[^<]*)<', doc_xml)
print("document.xml 中 TOC/REF 域:", toc_hits[:5] if toc_hits else "无")

print("\n=== 2. H1 样式 numPr 原始 XML ===")
m = re.search(r'<w:style [^>]*w:styleId="2">.*?</w:style>', styles_xml, re.S)
if m:
    numpr = re.search(r'<w:numPr>.*?</w:numPr>', m.group(0), re.S)
    print("H1 style numPr:", numpr.group(0) if numpr else "无")

print("\n=== 3. 正文第2个 H1 段落（开发环境准备）原始 pPr ===")
# 找到包含“开发环境准备”的段落
m = re.search(r'<w:p [^>]*>(?:(?!</w:p>).)*?开发环境准备.*?</w:p>', doc_xml, re.S)
if m:
    ppr = re.search(r'<w:pPr>.*?</w:pPr>', m.group(0), re.S)
    print(ppr.group(0)[:800] if ppr else "无 pPr")

print("\n=== 4. numId=1 在 numbering.xml 的映射 ===")
m = re.search(r'<w:num w:numId="1"[^>]*>.*?</w:num>', num_xml, re.S)
print(m.group(0) if m else "未找到")
print("\n=== abstractNumId=2 的 L0 完整定义 ===")
m = re.search(r'<w:abstractNum w:abstractNumId="2"[^>]*>.*?</w:abstractNum>', num_xml, re.S)
if m:
    l0 = re.search(r'<w:lvl w:ilvl="0"[^>]*>.*?</w:lvl>', m.group(0), re.S)
    print(l0.group(0) if l0 else "未找到")

print("\n=== 5. T0 封面表格完整 XML（前 2500 字符）===")
m = re.search(r'<w:tbl>(?:(?!</w:tbl>).)*?浙江芯劢.*?</w:tbl>', doc_xml, re.S)
if m:
    seg = m.group(0)
    print("长度:", len(seg))
    # 提取所有文本
    texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', seg)
    print("表格内全部文本:", texts)
    drawings = seg.count("<w:drawing") + seg.count("<w:pict")
    print("图片/绘图数:", drawings)
    # 第三行内容
    rows = re.findall(r'<w:tr[ >].*?</w:tr>', seg, re.S)
    print("行数:", len(rows))
    for i, row in enumerate(rows):
        t = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', row)
        has_img = "<w:drawing" in row or "<w:pict" in row or "<w:object" in row
        print(f"  row{i}: text={t} image={has_img}")

print("\n=== 6. 红色 #EE0000 run 所在段落完整文本 ===")
for m in re.finditer(r'<w:p [^>]*>(?:(?!</w:p>).)*?EE0000.*?</w:p>', doc_xml, re.S):
    texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', m.group(0))
    print("  ", "".join(texts)[:120])

print("\n=== 7. 浅蓝 #4E95D9 run 上下文（hyperlink 检查）===")
for m in re.finditer(r'<w:hyperlink[^>]*>(?:(?!</w:hyperlink>).)*?</w:hyperlink>', doc_xml, re.S):
    seg = m.group(0)
    if "4E95D9" in seg:
        texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', seg)
        anchor = re.search(r'w:anchor="([^"]*)"', seg)
        rid = re.search(r'r:id="([^"]*)"', seg)
        print("  hyperlink text=", "".join(texts)[:80], " anchor=", anchor.group(1) if anchor else None, " rId=", rid.group(1) if rid else None)

print("\n=== 8. 部件清单（检查 settings/字体表等）===")
for n in z.namelist():
    print(" ", n)
