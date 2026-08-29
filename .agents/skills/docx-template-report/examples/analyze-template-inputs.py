# -*- coding: utf-8 -*-
"""模板制作前补充分析：body 块顺序 / 目录标题 / 分页符 / 代码块结构 / shell&warn 行 / 正文表格表头格式。"""
import sys
import glob
from docx import Document
from docx.oxml.ns import qn

# 源文档在本地 .chaos 工作区（不入库）；以通配符定位，不固化源文件名
SRC = sys.argv[1] if len(sys.argv) > 1 else (
    glob.glob(r"d:\AI\.chaos\tests\old\work\doc\*SDK*指南*.docx") or [None])[0]
doc = Document(SRC)
body = doc.element.body

def el(parent, tag):
    return parent.find(qn(tag))

def p_text(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))

def p_style(p):
    ppr = el(p, "w:pPr")
    if ppr is None:
        return None
    ps = el(ppr, "w:pStyle")
    return ps.get(qn("w:val")) if ps is not None else None

print("=== 1. body 顶层子元素序列（前 40 个）===")
children = list(body)
for i, ch in enumerate(children[:40]):
    tag = ch.tag.split("}")[1]
    if tag == "p":
        txt = p_text(ch)[:40].replace("\n", " ")
        print(f"  [{i}] p  style={p_style(ch)} text={txt!r}")
    elif tag == "tbl":
        # first cell text
        first_t = next(ch.iter(qn("w:t")), None)
        print(f"  [{i}] tbl firstText={first_t.text if first_t is not None else ''!r}")
    elif tag == "sdt":
        print(f"  [{i}] sdt (TOC 域块)")
    elif tag == "sectPr":
        print(f"  [{i}] sectPr")
    else:
        print(f"  [{i}] {tag}")
print(f"  ... 共 {len(children)} 个顶层子元素")

print("\n=== 2. 目录标题段落（sdt 内/外查找'目录'）===")
for i, ch in enumerate(children):
    if ch.tag == qn("w:sdt"):
        # sdt 内第一个段落
        for p in ch.iter(qn("w:p")):
            txt = p_text(p)
            if txt.strip():
                ppr = el(p, "w:pPr")
                style = p_style(p)
                numpr = el(ppr, "w:numPr") if ppr is not None else None
                numid = None
                if numpr is not None:
                    n = el(numpr, "w:numId")
                    numid = n.get(qn("w:val")) if n is not None else None
                print(f"  sdt内首个段落: style={style} numId={numid} text={txt[:30]!r}")
                break
        # sdt 前一个段落
        prev = children[i - 1]
        if prev.tag == qn("w:p"):
            print(f"  sdt前一段落: style={p_style(prev)} text={p_text(prev)[:30]!r}")
        break

print("\n=== 3. 分页符统计 ===")
br_count = 0
br_locs = []
for idx, p in enumerate(doc.paragraphs):
    for br in p._p.iter(qn("w:br")):
        if br.get(qn("w:type")) == "page":
            br_count += 1
            if len(br_locs) < 10:
                br_locs.append((idx, p.style.style_id if p.style else None, p_text(p._p)[:30]))
print(f"  w:br type=page 共 {br_count} 处；样例: {br_locs}")
# 段落级 pageBreakBefore
pbb = []
for i, p in enumerate(doc.paragraphs):
    ppr = p._p.find(qn("w:pPr"))
    if ppr is not None and ppr.find(qn("w:pageBreakBefore")) is not None:
        pbb.append(i)
print(f"  pageBreakBefore 段落数: {len(pbb)}，位置(前10): {pbb[:10]}")

print("\n=== 4. 代码块结构（style=64 连续段，取第一段看 run/br 结构）===")
code_paras = [(i, p) for i, p in enumerate(doc.paragraphs) if p.style and p.style.style_id == "64"]
print(f"  code 样式段落总数: {len(code_paras)}")
if code_paras:
    i0, p0 = code_paras[0]
    runs = p0._p.findall(qn("w:r"))
    brs = list(p0._p.iter(qn("w:br")))
    print(f"  首个 code 段 idx={i0} run数={len(runs)} br数={len(brs)} text={p_text(p0._p)[:60]!r}")
    # 连续段长度分布
    runs_len = []
    cur = 1
    for k in range(1, len(code_paras)):
        if code_paras[k][0] == code_paras[k - 1][0] + 1:
            cur += 1
        else:
            runs_len.append(cur)
            cur = 1
    runs_len.append(cur)
    print(f"  连续 code 段块数量={len(runs_len)}，长度分布(前15): {sorted(runs_len, reverse=True)[:15]}")

print("\n=== 5. shell(215F9A)/warn(EE0000) 行段落样式 ===")
for color, name in [("215F9A", "shell"), ("EE0000", "warn")]:
    found = []
    for i, p in enumerate(doc.paragraphs):
        for r in p._p.findall(qn("w:r")):
            rpr = el(r, "w:rPr")
            if rpr is not None:
                c = el(rpr, "w:color")
                if c is not None and c.get(qn("w:val")) == color:
                    found.append((i, p.style.style_id if p.style else None, p_text(p._p)[:50]))
                    break
    print(f"  {name}({color}): {len(found)} 段")
    for f in found[:6]:
        print(f"    idx={f[0]} style={f[1]} text={f[2]!r}")

print("\n=== 6. 正文表格（非封面/修订表）表头行格式采样 ===")
for ti, tbl in enumerate(doc.tables[:8]):
    style_id = tbl.style.style_id if tbl.style else None
    nrows = len(tbl.rows)
    ncols = len(tbl.columns)
    hdr_cell = tbl.rows[0].cells[0]
    hdr_p = hdr_cell.paragraphs[0]
    runs = hdr_p._p.findall(qn("w:r"))
    bold = any(el(r, "w:rPr") is not None and el(el(r, "w:rPr"), "w:b") is not None for r in runs)
    shd = None
    tcpr = hdr_cell._tc.find(qn("w:tcPr"))
    if tcpr is not None:
        s = el(tcpr, "w:shd")
        if s is not None:
            shd = s.get(qn("w:fill"))
    print(f"  T{ti}: style={style_id} {nrows}x{ncols} 表头首格={hdr_p.text[:20]!r} bold={bold} shd={shd}")

print("\n=== 7. H1 段落 run 直接格式采样 ===")
h1_count = 0
for p in doc.paragraphs:
    if p.style and p.style.style_id == "2":
        h1_count += 1
        if h1_count <= 3:
            runs = p._p.findall(qn("w:r"))
            rpr_info = []
            for r in runs[:2]:
                rpr = el(r, "w:rPr")
                if rpr is not None:
                    sz = el(rpr, "w:sz")
                    rf = el(rpr, "w:rFonts")
                    rpr_info.append(f"sz={sz.get(qn('w:val')) if sz is not None else '-'},fonts={rf.get(qn('w:eastAsia')) if rf is not None else '-'}")
            print(f"  H1 {p_text(p._p)[:30]!r} runs={len(runs)} rpr={rpr_info}")
print(f"  H1 总数: {h1_count}")

print("\n=== 8. 正文普通段落（无样式/样式1）直接格式采样 ===")
shown = 0
for i, p in enumerate(doc.paragraphs):
    sid = p.style.style_id if p.style else None
    if sid in ("1", None) and p_text(p._p).strip() and shown < 5:
        ppr = el(p._p, "w:pPr")
        spacing = el(ppr, "w:spacing") if ppr is not None else None
        ind = el(ppr, "w:ind") if ppr is not None else None
        jc = el(ppr, "w:jc") if ppr is not None else None
        sp = {k.split('}')[1]: v for k, v in dict(spacing.attrib).items()} if spacing is not None else {}
        ind_d = {k.split('}')[1]: v for k, v in dict(ind.attrib).items()} if ind is not None else {}
        jcv = jc.get(qn('w:val')) if jc is not None else '-'
        print(f"  idx={i} style={sid} jc={jcv} spacing={sp} ind={ind_d} text={p_text(p._p)[:30]!r}")
        shown += 1
