# -*- coding: utf-8 -*-
"""
build-xmnn-template.py — 从 XMNN SDK 使用指南源 DOCX 构建高保真 docxtpl 模板。

策略（副本基底法）：
  1. 以源 DOCX 为基底打开 → styles.xml / numbering.xml / settings.xml / theme /
     header*.xml 骨架原样保留（样式定义、标题自动编号 100% 继承）；
  2. 删除 body 全部内容子元素（保留 sectPr 节属性）；
  3. 重建正文结构并注入 Jinja2/docxtpl 标签：
     - 封面 sdt 块（标题/版本信息，deepcopy 源块后文本标签化）
     - 封面隐形表格（公司名/版权句，deepcopy）
     - 分页符 → “更新记录”H1（numId=0 抑制编号）→ 修订记录深色表（deepcopy + 三行分离行循环）
     - 分页符 → “目录”标题（样式80）+ TOC 域（Word 打开时更新）
     - 分页符 → 正文块循环 {% for blk in blocks %}（h1-h4/p/list/code/shell/warn/2-5列表格/分页）

  表格行循环（经 debug-rowloop-patterns.py A-J 十变体实证）：
  块级段落循环/条件 → 纯标签独占段落；表格行循环 → 必须三行分离：
  ``{%tr for x in items %}`` 独占一个标记行（渲染时整行移除）→ 数据行
  （单元格内只放 ``{{ x.field }}``）→ ``{%tr endfor %}`` 独占另一标记行。
  反模式：数据行格内放纯标签 {% for %}（单元格横向增生）；同一行放两个
  {%tr %} 标记（patch_xml 正则吞掉 for 标记 → unknown tag 'endfor'）。
  4. settings.xml 注入 updateFields=true（Word 打开时提示更新目录域）；
  5. 页眉公司名替换为 {{ company }}（默认页眉 + 首页页眉两个部件）；
  6. 品牌资产脱敏（通用模板必须品牌中立）：
     - 删除三个页眉部件的 VML 水印（PowerPlusWaterMarkObject，源文字 "Xmsilicon"）
       与 mc:AlternateContent 装饰图形，清理水印独立空段落；
     - logo 图片（页眉/封面 sdt）替换为占位标签 {{ header_logo }} / {{ cover_logo }}
       （渲染时可传 docxtpl.InlineImage 动态注入，不传则为空）；
     - 删除全部 image 部件关系（孤儿媒体随序列化自动排除，模板零媒体）；
     - docProps 元数据清空（作者真名/修改者/标题等）。

运行：
  py -3.14 examples/build-xmnn-template.py [源docx] [输出模板docx]
"""
import sys
from copy import deepcopy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = sys.argv[1] if len(sys.argv) > 1 else r"d:\AI\.chaos\tests\old\work\doc\XMNN_SDK_使用指南v1.1.0.docx"
OUT = sys.argv[2] if len(sys.argv) > 2 else r"templates\xmnn-sdk-guide-template.docx"

# ---------------------------------------------------------------- 基础工具

def el(parent, tag):
    return parent.find(qn(tag))

def p_text(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))

def text_runs(p):
    """仅含 w:t 的 run（跳过 drawing/br/fldChar 等非文本 run）。"""
    return [r for r in p.findall(qn("w:r")) if r.find(qn("w:t")) is not None]

def set_run_text(r, text):
    ts = r.findall(qn("w:t"))
    ts[0].text = text
    ts[0].set(qn("xml:space"), "preserve")
    for extra in ts[1:]:
        r.remove(extra)

def tag_paragraph(p, tag):
    """把段落整体替换为单个 Jinja 标签文本（保留首个文本 run 的 rPr，保留图片/域 run）。"""
    runs = text_runs(p)
    if not runs:
        r = OxmlElement("w:r")
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        r.append(t)
        p.append(r)
        runs = [r]
    set_run_text(runs[0], tag)
    for r in runs[1:]:
        p.remove(r)

def delete_paragraph(p):
    parent = p.getparent()
    if parent is not None:
        parent.remove(p)

def make_p(style_id=None):
    p = OxmlElement("w:p")
    if style_id:
        ppr = OxmlElement("w:pPr")
        ps = OxmlElement("w:pStyle")
        ps.set(qn("w:val"), style_id)
        ppr.append(ps)
        p.append(ppr)
    return p

def add_run(p, text, bold=False, color=None, italic=False):
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    if bold:
        rpr.append(OxmlElement("w:b"))
    if italic:
        rpr.append(OxmlElement("w:i"))
    if color:
        c = OxmlElement("w:color")
        c.set(qn("w:val"), color)
        rpr.append(c)
    if len(rpr):
        r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    p.append(r)
    return r

def add_tag_p(anchor, tag, style_id="1"):
    """独立标签段：仅含 Jinja 标签的正文段落（块级循环/条件用）。

    段落级 for/if 用纯标签独占段落即可正确工作（docxtpl patch_xml 的
    y="p" 规则会把含标签的段落元素解包，标签留在原位，段落渲染时移除）。
    注意：表格行循环不能用此法——纯标签放在数据行单元格内会导致单元格
    横向增生；行循环必须用三行分离的 ``{%tr %}`` 标记行（见文件头说明）。
    """
    p = make_p(style_id)
    add_run(p, tag)
    anchor.addprevious(p)
    return p

def page_break_p():
    p = OxmlElement("w:p")
    r = OxmlElement("w:r")
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r.append(br)
    p.append(r)
    return p

def set_spacing_ind(p, line="300", first_line="420"):
    """正文段落直接格式：行距 1.25 倍 + 首行缩进 2 字符（与源文档一致）。"""
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    sp = OxmlElement("w:spacing")
    sp.set(qn("w:line"), line)
    sp.set(qn("w:lineRule"), "auto")
    ppr.append(sp)
    if first_line:
        ind = OxmlElement("w:ind")
        ind.set(qn("w:firstLine"), first_line)
        ppr.append(ind)

def set_cell_shd(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def set_cell_width(cell, width_dxa):
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = OxmlElement("w:tcW")
    tcW.set(qn("w:w"), str(width_dxa))
    tcW.set(qn("w:type"), "dxa")
    tcPr.append(tcW)

def style_cell_paragraph(cell, p, jc=None, line="300"):
    ppr = p._p.get_or_add_pPr()
    ps = OxmlElement("w:pStyle")
    ps.set(qn("w:val"), "63")  # 表格文本样式：宋体、无首行缩进
    ppr.insert(0, ps)
    if jc:
        j = OxmlElement("w:jc")
        j.set(qn("w:val"), jc)
        ppr.append(j)
    if line:
        sp = OxmlElement("w:spacing")
        sp.set(qn("w:line"), line)
        sp.set(qn("w:lineRule"), "auto")
        ppr.append(sp)

# ---------------------------------------------------------------- 1. 打开基底

doc = Document(SRC)
body = doc.element.body
children = list(body)

# 捕获需 deepcopy 的原始部件（清空 body 前）
cover_sdt_src = next(ch for ch in children if ch.tag == qn("w:sdt"))
tables_src = [ch for ch in children if ch.tag == qn("w:tbl")]
cover_tbl_src = tables_src[0]   # T0 封面隐形表
rev_tbl_src = tables_src[1]     # T1 修订记录深色表
sectPr = children[-1] if children[-1].tag == qn("w:sectPr") else el(body, "w:sectPr")

# 清空 body（保留 sectPr）
for ch in children:
    if ch is not sectPr:
        body.remove(ch)

# ---------------------------------------------------------------- 2. 封面 sdt 块

cover_sdt = deepcopy(cover_sdt_src)
for p in list(cover_sdt.iter(qn("w:p"))):
    txt = p_text(p).strip()
    if "XMNN" in txt and "指南" in txt:
        tag_paragraph(p, "{{ doc_title }}")
    elif "文件状态" in txt:
        tag_paragraph(p, "文件状态：{{ doc_status }}")
    elif "正在修改" in txt or txt == "正式发布":
        delete_paragraph(p)
    elif "当前版本" in txt:
        # 标签段保留：标签 run 用普通格式（不加粗、不着色）
        runs = text_runs(p)
        if runs:
            set_run_text(runs[0], "当前版本：")
            for r in runs[1:]:
                p.remove(r)
        add_run(p, "{{ doc_version }}")
    elif txt == "1.1.0":
        delete_paragraph(p)
    elif txt == "XMNPU":
        tag_paragraph(p, "{{ doc_author }}")
    elif txt == "2025-10-15":
        tag_paragraph(p, "{{ doc_date }}")
    elif txt == "张振宇":
        tag_paragraph(p, "{{ doc_reviewer }}")
sectPr.addprevious(cover_sdt)

# ---------------------------------------------------------------- 3. 封面隐形表

cover_tbl = deepcopy(cover_tbl_src)
cover_cells = [tc for tc in cover_tbl.iter(qn("w:tc"))]
for tc in cover_cells:
    for p in tc.findall(qn("w:p")):
        txt = p_text(p)
        if "浙江" in txt and "公司" in txt:
            tag_paragraph(p, "{{ company }}")
        elif "版本所有" in txt or "翻版" in txt:
            tag_paragraph(p, "{{ copyright_notice }}")
sectPr.addprevious(cover_tbl)

# ---------------------------------------------------------------- 4. 更新记录页

sectPr.addprevious(page_break_p())

# H1“更新记录”：pStyle=2 + numId=0 抑制自动编号
h1 = make_p("2")
numpr = OxmlElement("w:numPr")
ilvl = OxmlElement("w:ilvl"); ilvl.set(qn("w:val"), "0")
numid = OxmlElement("w:numId"); numid.set(qn("w:val"), "0")
numpr.append(ilvl); numpr.append(numid)
h1.find(qn("w:pPr")).append(numpr)
add_run(h1, "更新记录")
sectPr.addprevious(h1)

# 修订记录深色表（deepcopy + 三行分离行循环）
# 模板物理 4 行：表头 / for 标记行(渲染移除) / 数据行 / endfor 标记行(渲染移除)
rev_tbl = deepcopy(rev_tbl_src)
trs = rev_tbl.findall(qn("w:tr"))
header_tr, data_tr1 = trs[0], trs[1]
for extra_tr in trs[2:]:
    rev_tbl.remove(extra_tr)
rev_fields = ["version", "author", "date", "description", "reviewer"]

# 数据行：5 个单元格只放 {{ rev.xxx }} 变量
data_cells = data_tr1.findall(qn("w:tc"))
for i, tc in enumerate(data_cells):
    paras = tc.findall(qn("w:p"))
    tag_paragraph(paras[0], "{{ rev." + rev_fields[i] + " }}")
    for extra_p in paras[1:]:
        tag_paragraph(extra_p, "")

def make_marker_tr(src_tr, tag):
    """以数据行为底板造标记行：首格放 {%tr %} 标签，其余格清空（整行渲染时移除）。"""
    mtr = deepcopy(src_tr)
    cells = mtr.findall(qn("w:tc"))
    p0s = cells[0].findall(qn("w:p"))
    tag_paragraph(p0s[0], tag)
    for extra_p in p0s[1:]:
        tag_paragraph(extra_p, "")
    for tc in cells[1:]:
        for p in tc.findall(qn("w:p")):
            tag_paragraph(p, "")
    return mtr

for_tr = make_marker_tr(data_tr1, "{%tr for rev in revisions %}")
endfor_tr = make_marker_tr(data_tr1, "{%tr endfor %}")
header_tr.addnext(for_tr)       # 表头 → for 标记行 → 数据行
data_tr1.addnext(endfor_tr)     # 数据行 → endfor 标记行
sectPr.addprevious(rev_tbl)

# ---------------------------------------------------------------- 5. 目录页

sectPr.addprevious(page_break_p())

toc_title = make_p("80")  # TOC 标题2：居中、color=104862
add_run(toc_title, "目录")
sectPr.addprevious(toc_title)

# TOC 域（Word 打开时经 updateFields 提示更新，或 F9 手动更新）
toc_p = make_p()
r1 = OxmlElement("w:r"); fc1 = OxmlElement("w:fldChar"); fc1.set(qn("w:fldCharType"), "begin"); r1.append(fc1); toc_p.append(r1)
r2 = OxmlElement("w:r"); it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
it.text = ' TOC \\o "1-3" \\h \\z \\u '; r2.append(it); toc_p.append(r2)
r3 = OxmlElement("w:r"); fc2 = OxmlElement("w:fldChar"); fc2.set(qn("w:fldCharType"), "separate"); r3.append(fc2); toc_p.append(r3)
r4 = OxmlElement("w:r"); t4 = OxmlElement("w:t")
t4.text = "（请在 Word 中按 F9 或右键“更新域”生成目录）"; r4.append(t4); toc_p.append(r4)
r5 = OxmlElement("w:r"); fc3 = OxmlElement("w:fldChar"); fc3.set(qn("w:fldCharType"), "end"); r5.append(fc3); toc_p.append(r5)
sectPr.addprevious(toc_p)

# ---------------------------------------------------------------- 6. 正文块循环

sectPr.addprevious(page_break_p())

# 外层块循环开始
add_tag_p(sectPr, "{% for blk in blocks %}")

# --- 标题块 h1-h4
for level, sid in [(1, "2"), (2, "3"), (3, "4"), (4, "5")]:
    add_tag_p(sectPr, f'{{% if blk.type == "h{level}" %}}')
    p = make_p(sid)
    add_run(p, "{{ blk.text }}")
    sectPr.addprevious(p)
    add_tag_p(sectPr, "{% endif %}")

# --- 正文段落
add_tag_p(sectPr, '{% if blk.type == "p" %}')
p = make_p("1")
set_spacing_ind(p, line="300", first_line="420")
add_run(p, "{{ blk.text }}")
sectPr.addprevious(p)
add_tag_p(sectPr, "{% endif %}")

# --- 列表项（List Paragraph 样式46）
add_tag_p(sectPr, '{% if blk.type == "list" %}')
p = make_p("46")
add_run(p, "{{ blk.text }}")
sectPr.addprevious(p)
add_tag_p(sectPr, "{% endif %}")

# --- shell 命令行（code 样式 + 215F9A 蓝色斜体 run）
add_tag_p(sectPr, '{% if blk.type == "shell" %}')
p = make_p("64")
add_run(p, "{{ blk.text }}", color="215F9A", italic=True)
sectPr.addprevious(p)
add_tag_p(sectPr, "{% endif %}")

# --- 警告行（Normal 样式 + EE0000 红色加粗 run）
add_tag_p(sectPr, '{% if blk.type == "warn" %}')
p = make_p("1")
set_spacing_ind(p, line="300", first_line="420")
add_run(p, "{{ blk.text }}", bold=True, color="EE0000")
sectPr.addprevious(p)
add_tag_p(sectPr, "{% endif %}")

# --- 代码块（code 样式，逐行段落循环）
add_tag_p(sectPr, '{% if blk.type == "code" %}')
add_tag_p(sectPr, "{% for line in blk.lines %}")
p = make_p("64")
add_run(p, "{{ line }}")
sectPr.addprevious(p)
add_tag_p(sectPr, "{% endfor %}")
add_tag_p(sectPr, "{% endif %}")

# --- 表格块（2/3/4/5 列四种预置，Table Grid 样式26，黑底白字加粗表头）
TABLE_TOTAL_DXA = 8306  # A4 正文宽（210.01 - 31.75×2 mm ≈ 8306 twips）
for ncols in (2, 3, 4, 5):
    add_tag_p(sectPr, f'{{% if blk.type == "table" and blk.cols == {ncols} %}}')

    # 物理 4 行：表头 / for 标记行(渲染移除) / 数据行 / endfor 标记行(渲染移除)
    tbl = doc.add_table(rows=4, cols=ncols)
    tblPr = tbl._tbl.tblPr
    tstyle = OxmlElement("w:tblStyle"); tstyle.set(qn("w:val"), "26")
    tblPr.insert(0, tstyle)
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW"); tblPr.append(tblW)
    tblW.set(qn("w:w"), "5000"); tblW.set(qn("w:type"), "pct")
    # 等宽列
    col_w = TABLE_TOTAL_DXA // ncols
    for gc in tbl._tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol")):
        gc.set(qn("w:w"), str(col_w))
    # r0 表头行：黑底白字加粗居中
    for i, cell in enumerate(tbl.rows[0].cells):
        set_cell_shd(cell, "000000")
        set_cell_width(cell, col_w)
        p = cell.paragraphs[0]
        style_cell_paragraph(cell, p, jc="center")
        add_run(p._p, f"{{{{ blk.header[{i}] }}}}", bold=True, color="FFFFFF")
    # r1 for 标记行：首格 {%tr for %}（整行渲染时移除）
    for i, cell in enumerate(tbl.rows[1].cells):
        set_cell_width(cell, col_w)
        if i == 0:
            add_run(cell.paragraphs[0]._p, "{%tr for row in blk.rows %}")
    # r2 数据行：单元格只放 {{ row[i] }} 变量
    for i, cell in enumerate(tbl.rows[2].cells):
        set_cell_width(cell, col_w)
        p = cell.paragraphs[0]
        style_cell_paragraph(cell, p, jc=None)
        add_run(p._p, f"{{{{ row[{i}] }}}}")
    # r3 endfor 标记行：首格 {%tr endfor %}（整行渲染时移除）
    for i, cell in enumerate(tbl.rows[3].cells):
        set_cell_width(cell, col_w)
        if i == 0:
            add_run(cell.paragraphs[0]._p, "{%tr endfor %}")

    add_tag_p(sectPr, "{% endif %}")

# --- 显式分页块
add_tag_p(sectPr, '{% if blk.type == "pagebreak" %}')
sectPr.addprevious(page_break_p())
add_tag_p(sectPr, "{% endif %}")

# 外层块循环结束
add_tag_p(sectPr, "{% endfor %}")

# ---------------------------------------------------------------- 7. 页眉公司名标签化

def tag_header_container(container):
    for p in container.paragraphs:
        if "浙江" in p.text and "公司" in p.text:
            tag_paragraph(p._p, "{{ company }}")
    for tbl in container.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if "浙江" in p.text and "公司" in p.text:
                        tag_paragraph(p._p, "{{ company }}")

for section in doc.sections:
    tag_header_container(section.header)
    if section.different_first_page_header_footer:
        tag_header_container(section.first_page_header)

# ---------------------------------------------------------------- 8. 脱敏：水印/品牌图形/媒体关系/元数据

MC_ALT_CONTENT = "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent"

def desensitize_element(element, logo_tag, clean_empty_paras):
    """对单个 part 根元素执行图形脱敏，返回替换的 logo 数量。

    1. 删除 mc:AlternateContent（DrawingML/VML 双写装饰图形，如页眉椭圆）；
    2. 删除 w:pict（VML 水印 PowerPlusWaterMarkObject 等）；
    3. 剩余 w:drawing（logo 图片）所在 run 替换为 logo 占位标签；
    4. clean_empty_paras=True 时清理表格外因删除变空的直接子段落（水印独立段落）；
       表格内段落不清理（单元格必须保留至少一个段落），正文不清理
       （分页/间距空段落是有意结构）。
    """
    n_logo = 0
    for ac in list(element.iter(MC_ALT_CONTENT)):
        ac.getparent().remove(ac)
    for pict in list(element.iter(qn("w:pict"))):
        pict.getparent().remove(pict)
    for drawing in list(element.iter(qn("w:drawing"))):
        run = drawing.getparent()
        while run is not None and run.tag != qn("w:r"):
            run = run.getparent()
        if run is None:
            continue
        run.remove(drawing)
        if run.find(qn("w:t")) is None:
            t = OxmlElement("w:t")
            t.set(qn("xml:space"), "preserve")
            t.text = logo_tag
            run.append(t)
        n_logo += 1
    if clean_empty_paras:
        for p in list(element.findall(qn("w:p"))):
            has_content = (
                p.find(".//" + qn("w:t")) is not None or
                p.find(".//" + qn("w:drawing")) is not None or
                p.find(".//" + qn("w:br")) is not None or
                p.find(qn("w:fldSimple")) is not None or
                p.find(".//" + qn("w:instrText")) is not None
            )
            if not has_content:
                element.remove(p)
    return n_logo

# 敏感关系类型：
#   /image             — 媒体（logo/正文截图）
#   /customXml         — WPS 自定义 XML（校对缓存含源文术语、水印形状扩展信息）
#   /custom-properties — docProps/custom.xml（WPS 私有属性，base64 内含 WPS 用户 ID）
# 关系删除后，失去引用的 part 不会写入序列化包（OPC 按关系图可达性打包）。
SENSITIVE_RELTYPES = ("/image", "/customXml", "/custom-properties")

def drop_sensitive_rels(rels_owner):
    """删除 owner（part 或 package，均暴露 .rels）上的敏感关系，返回删除条数。"""
    n = 0
    for rel in list(rels_owner.rels.values()):
        if any(rel.reltype.endswith(suf) for suf in SENSITIVE_RELTYPES):
            rels_owner.rels.pop(rel.rId, None)
            n += 1
    return n

# 正文（封面 sdt logo → {{ cover_logo }}）；正文空段落保留（分页/间距结构）
n_logo_body = desensitize_element(doc.element.body, "{{ cover_logo }}", False)

# 全部 header/footer 部件（default/first/even 三个页眉均含水印，逐一脱敏）
n_logo_hdr = 0
for part in list(doc.part.package.iter_parts()):
    pn = str(part.partname)
    if pn.startswith("/word/header") or pn.startswith("/word/footer"):
        n_logo_hdr += desensitize_element(part.element, "{{ header_logo }}", True)

# 删除敏感部件关系（document part + package 根关系 + 页眉页脚 part）
n_rels = drop_sensitive_rels(doc.part)
n_rels += drop_sensitive_rels(doc.part.package)
for part in list(doc.part.package.iter_parts()):
    pn = str(part.partname)
    if pn.startswith("/word/header") or pn.startswith("/word/footer"):
        n_rels += drop_sensitive_rels(part)

# docProps 元数据脱敏（作者真名/修改者/标题等）
cp = doc.core_properties
cp.author = ""
cp.last_modified_by = ""
cp.title = ""
cp.subject = ""
cp.keywords = ""
cp.comments = ""
cp.category = ""
cp.content_status = ""
_lp = cp._element.find(qn("cp:lastPrinted"))
if _lp is not None:
    cp._element.remove(_lp)
print(f"[CHECK] 脱敏: logo 占位 正文 {n_logo_body} 处/页眉 {n_logo_hdr} 处, 删除 image 关系 {n_rels} 条")

# ---------------------------------------------------------------- 9. settings: 打开时更新域

settings_el = doc.settings.element
if settings_el.find(qn("w:updateFields")) is None:
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    settings_el.append(uf)

# ---------------------------------------------------------------- 10. 保存

doc.save(OUT)
print(f"[OK] 模板已生成: {OUT}")

# 简要自检
chk = Document(OUT)
n_p = len(chk.paragraphs)
n_tbl = len(chk.tables)
print(f"[CHECK] 正文段落数(含表格外): {n_p}, 顶层表格数: {n_tbl}")
styles_xml = chk.styles.element
has_code = any(s.get(qn("w:styleId")) == "64" for s in styles_xml.findall(qn("w:style")))
print(f"[CHECK] code 样式(64)保留: {has_code}")
