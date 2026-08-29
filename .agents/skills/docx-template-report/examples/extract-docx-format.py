# -*- coding: utf-8 -*-
"""
DOCX 格式全面提取工具（R 阶段事实采集）
用法: py -3.14 examples/extract-docx-format.py <source.docx> [report.json]
输出: 控制台摘要 + JSON 全量格式事实报告
"""
import json
import sys
from collections import Counter
from docx import Document
from docx.shared import Pt, Mm, Emu
from docx.oxml.ns import qn

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def el(parent, tag):
    return parent.find(qn(tag))


def els(parent, tag):
    return parent.findall(qn(tag))


def val(elem, attr="w:val"):
    if elem is None:
        return None
    return elem.get(qn(attr))


def rpr_info(rpr):
    """提取 rPr（文字属性）关键信息"""
    if rpr is None:
        return {}
    info = {}
    rf = el(rpr, "w:rFonts")
    if rf is not None:
        info["fonts"] = {k.split("}")[-1]: v for k, v in rf.attrib.items() if v}
    sz = el(rpr, "w:sz")
    if sz is not None:
        info["sz_half_pt"] = int(sz.get(qn("w:val")))
        info["sz_pt"] = int(sz.get(qn("w:val"))) / 2
    szcs = el(rpr, "w:szCs")
    if szcs is not None:
        info["szCs_pt"] = int(szcs.get(qn("w:val"))) / 2
    b = el(rpr, "w:b")
    if b is not None:
        info["bold"] = b.get(qn("w:val")) not in ("0", "false")
    i = el(rpr, "w:i")
    if i is not None:
        info["italic"] = i.get(qn("w:val")) not in ("0", "false")
    u = el(rpr, "w:u")
    if u is not None:
        info["underline"] = u.get(qn("w:val"))
    color = el(rpr, "w:color")
    if color is not None:
        info["color"] = color.get(qn("w:val"))
    hl = el(rpr, "w:highlight")
    if hl is not None:
        info["highlight"] = hl.get(qn("w:val"))
    shd = el(rpr, "w:shd")
    if shd is not None:
        info["shd_fill"] = shd.get(qn("w:fill"))
    vert = el(rpr, "w:vertAlign")
    if vert is not None:
        info["vertAlign"] = vert.get(qn("w:val"))
    spc = el(rpr, "w:spacing")
    if spc is not None:
        info["char_spacing_twips"] = spc.get(qn("w:val"))
    return info


def ppr_info(ppr):
    """提取 pPr（段落属性）关键信息"""
    if ppr is None:
        return {}
    info = {}
    jc = el(ppr, "w:jc")
    if jc is not None:
        info["align"] = jc.get(qn("w:val"))
    sp = el(ppr, "w:spacing")
    if sp is not None:
        info["spacing"] = {k.split("}")[-1]: v for k, v in sp.attrib.items() if v}
    ind = el(ppr, "w:ind")
    if ind is not None:
        info["indent"] = {k.split("}")[-1]: v for k, v in ind.attrib.items() if v}
    numpr = el(ppr, "w:numPr")
    if numpr is not None:
        ilvl = el(numpr, "w:ilvl")
        numid = el(numpr, "w:numId")
        info["numbering"] = {
            "ilvl": ilvl.get(qn("w:val")) if ilvl is not None else None,
            "numId": numid.get(qn("w:val")) if numid is not None else None,
        }
    ol = el(ppr, "w:outlineLvl")
    if ol is not None:
        info["outlineLvl"] = ol.get(qn("w:val"))
    pbdr = el(ppr, "w:pBdr")
    if pbdr is not None:
        info["borders"] = [b.tag.split("}")[-1] for b in pbdr]
    shd = el(ppr, "w:shd")
    if shd is not None:
        info["shd_fill"] = shd.get(qn("w:fill"))
    return info


def emu_to_mm(v):
    return round(Emu(v).mm, 2) if v is not None else None


def twips_to_mm(v):
    return round(int(v) / 1440 * 25.4, 2) if v is not None else None


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "format-report.json"
    doc = Document(src)
    report = {"source": src}

    # ---------- 1. 包结构 ----------
    package = doc.part.package
    parts = []
    for p in package.iter_parts():
        parts.append({"partname": str(p.partname), "content_type": p.content_type})
    report["parts"] = parts

    # ---------- 2. 节属性（页面设置） ----------
    sections = []
    for s in doc.sections:
        sections.append({
            "page_w_mm": emu_to_mm(s.page_width),
            "page_h_mm": emu_to_mm(s.page_height),
            "orientation": str(s.orientation),
            "margin_top_mm": emu_to_mm(s.top_margin),
            "margin_bottom_mm": emu_to_mm(s.bottom_margin),
            "margin_left_mm": emu_to_mm(s.left_margin),
            "margin_right_mm": emu_to_mm(s.right_margin),
            "header_distance_mm": emu_to_mm(s.header_distance),
            "footer_distance_mm": emu_to_mm(s.footer_distance),
            "gutter_mm": emu_to_mm(s.gutter),
            "different_first_page": s.different_first_page_header_footer,
            "header_is_linked": s.header.is_linked_to_previous,
            "footer_is_linked": s.footer.is_linked_to_previous,
        })
    report["sections"] = sections

    # ---------- 2.5 docDefaults（文档默认字体/字号）+ 主题 + 媒体 ----------
    styles_el = doc.styles.element
    docdef = el(styles_el, "w:docDefaults")
    if docdef is not None:
        rpd = el(docdef, "w:rPrDefault")
        ppd = el(docdef, "w:pPrDefault")
        report["docDefaults"] = {
            "rPrDefault": rpr_info(el(rpd, "w:rPr")) if rpd is not None else {},
            "pPrDefault": ppr_info(el(ppd, "w:pPr")) if ppd is not None else {},
        }
    media = []
    for p in package.iter_parts():
        pn = str(p.partname)
        if "/media/" in pn or "image" in p.content_type:
            media.append({"partname": pn, "content_type": p.content_type,
                          "size_bytes": len(p.blob)})
    report["media"] = media

    # ---------- 3. 页眉页脚内容 ----------
    hf = []
    for idx, s in enumerate(doc.sections):
        for name, obj in (("header", s.header), ("footer", s.footer),
                          ("first_page_header", s.first_page_header),
                          ("first_page_footer", s.first_page_footer),
                          ("even_page_header", s.even_page_header),
                          ("even_page_footer", s.even_page_footer)):
            try:
                paras = []
                for p in obj.paragraphs:
                    if p.text.strip() or p._p.findall(qn("w:r")):
                        ppr = el(p._p, "w:pPr")
                        jc = el(ppr, "w:jc") if ppr is not None else None
                        paras.append({
                            "text": p.text,
                            "style": p.style.name if p.style else None,
                            "align": jc.get(qn("w:val")) if jc is not None else None,
                            "has_field": bool(p._p.findall(f".//{{{W}}}fldChar") or
                                              p._p.findall(f".//{{{W}}}instrText")),
                            "rPr_sample": rpr_info(el(p._p, f".//{{{W}}}rPr")) if p._p.find(f".//{{{W}}}rPr") is not None else {},
                        })
                tables_n = len(obj.tables)
                if paras or tables_n:
                    hf.append({"section": idx, "type": name,
                               "linked": obj.is_linked_to_previous,
                               "paragraphs": paras, "tables": tables_n})
            except Exception as e:
                hf.append({"section": idx, "type": name, "error": str(e)})
    report["headers_footers"] = hf

    # ---------- 4. 样式定义 ----------
    styles = []
    for st in doc.styles:
        try:
            s_el = st.element
            entry = {
                "style_id": st.style_id,
                "name": st.name,
                "type": str(st.type),
                "builtin": st.builtin,
            }
            based = el(s_el, "w:basedOn")
            if based is not None:
                entry["basedOn"] = based.get(qn("w:val"))
            nxt = el(s_el, "w:next")
            if nxt is not None:
                entry["next"] = nxt.get(qn("w:val"))
            link = el(s_el, "w:link")
            if link is not None:
                entry["link"] = link.get(qn("w:val"))
            qf = el(s_el, "w:qFormat")
            entry["qFormat"] = qf is not None
            ui = el(s_el, "w:uiPriority")
            if ui is not None:
                entry["uiPriority"] = ui.get(qn("w:val"))
            rpr = el(s_el, "w:rPr")
            if rpr is not None:
                entry["rPr"] = rpr_info(rpr)
            ppr = el(s_el, "w:ppr") or el(s_el, "w:pPr")
            if ppr is not None:
                entry["pPr"] = ppr_info(ppr)
            # 表格样式额外属性
            tblpr = el(s_el, "w:tblPr")
            if tblpr is not None:
                borders = el(tblpr, "w:tblBorders")
                if borders is not None:
                    entry["tbl_borders"] = {b.tag.split("}")[-1]:
                        {k.split("}")[-1]: v for k, v in b.attrib.items()}
                        for b in borders}
            styles.append(entry)
        except Exception as e:
            styles.append({"style_id": getattr(st, "style_id", "?"), "error": str(e)})
    report["styles"] = styles

    # ---------- 5. numbering.xml 编号定义 ----------
    numbering = {}
    try:
        np = doc.part.numbering_part
        n_el = np.element
        # abstractNum
        for an in els(n_el, "w:abstractNum"):
            aid = an.get(qn("w:abstractNumId"))
            lvls = {}
            for lvl in els(an, "w:lvl"):
                il = lvl.get(qn("w:ilvl"))
                fmt = el(lvl, "w:numFmt")
                txt = el(lvl, "w:lvlText")
                jc = el(lvl, "w:lvlJc")
                ppr = el(lvl, "w:pPr")
                rpr = el(lvl, "w:rPr")
                lvls[il] = {
                    "numFmt": fmt.get(qn("w:val")) if fmt is not None else None,
                    "lvlText": txt.get(qn("w:val")) if txt is not None else None,
                    "lvlJc": jc.get(qn("w:val")) if jc is not None else None,
                    "pPr": ppr_info(ppr) if ppr is not None else {},
                    "rPr": rpr_info(rpr) if rpr is not None else {},
                }
            numbering.setdefault("abstract", {})[aid] = lvls
        # num -> abstract 映射
        for num in els(n_el, "w:num"):
            nid = num.get(qn("w:numId"))
            an = el(num, "w:abstractNumId")
            numbering.setdefault("num_map", {})[nid] = an.get(qn("w:val")) if an is not None else None
    except Exception as e:
        numbering["error"] = str(e)
    report["numbering"] = numbering

    # ---------- 6. 正文段落与表格（按文档顺序） ----------
    body = doc.element.body
    para_records = []
    table_records = []
    p_idx = 0
    t_idx = 0
    font_hist = Counter()
    size_hist = Counter()
    color_hist = Counter()
    style_hist = Counter()

    def walk_tbl(tbl_el, depth=0):
        nonlocal t_idx
        from docx.table import Table
        tbl = Table(tbl_el, doc)
        rec = {"index": t_idx, "depth": depth,
               "style": tbl.style.name if tbl.style else None,
               "rows": len(tbl.rows), "cols": len(tbl.columns)}
        # tblPr
        tblpr = el(tbl_el, "w:tblPr")
        if tblpr is not None:
            w_el = el(tblpr, "w:tblW")
            if w_el is not None:
                rec["width"] = {k.split("}")[-1]: v for k, v in w_el.attrib.items()}
            jc = el(tblpr, "w:jc")
            if jc is not None:
                rec["align"] = jc.get(qn("w:val"))
            look = el(tblpr, "w:tblLook")
            if look is not None:
                rec["tblLook"] = {k.split("}")[-1]: v for k, v in look.attrib.items()}
            borders = el(tblpr, "w:tblBorders")
            if borders is not None:
                rec["borders"] = {b.tag.split("}")[-1]:
                    {k.split("}")[-1]: v for k, v in b.attrib.items()} for b in borders}
            cellmar = el(tblpr, "w:tblCellMar")
            if cellmar is not None:
                rec["cell_margins_twips"] = {m.tag.split("}")[-1]: m.get(qn("w:w"))
                                             for m in cellmar}
        # grid
        grid = el(tbl_el, "w:tblGrid")
        if grid is not None:
            rec["grid_cols_twips"] = [g.get(qn("w:w")) for g in els(grid, "w:gridCol")]
        # 首行单元格格式（表头样式采样）
        rows = els(tbl_el, "w:tr")
        if rows:
            first_row_cells = []
            for tc in els(rows[0], "w:tc"):
                tcpr = el(tc, "w:tcPr")
                cinfo = {}
                if tcpr is not None:
                    shd = el(tcpr, "w:shd")
                    if shd is not None:
                        cinfo["shd_fill"] = shd.get(qn("w:fill"))
                    tcw = el(tcpr, "w:tcW")
                    if tcw is not None:
                        cinfo["width"] = {k.split("}")[-1]: v for k, v in tcw.attrib.items()}
                    va = el(tcpr, "w:vAlign")
                    if va is not None:
                        cinfo["vAlign"] = va.get(qn("w:val"))
                    tcborders = el(tcpr, "w:tcBorders")
                    if tcborders is not None:
                        cinfo["borders"] = [b.tag.split("}")[-1] for b in tcborders]
                # 单元格首段文字格式
                p = el(tc, "w:p")
                if p is not None:
                    ppr = el(p, "w:pPr")
                    r = el(p, "w:r")
                    if r is not None:
                        cinfo["run_rPr"] = rpr_info(el(r, "w:rPr"))
                    if ppr is not None:
                        cinfo["pPr"] = ppr_info(ppr)
                first_row_cells.append(cinfo)
            rec["first_row_cells"] = first_row_cells
            # 第二行（数据行）采样
            if len(rows) > 1:
                sample = []
                for tc in els(rows[1], "w:tc")[:2]:
                    p = el(tc, "w:p")
                    cinfo = {}
                    if p is not None:
                        r = el(p, "w:r")
                        if r is not None:
                            cinfo["run_rPr"] = rpr_info(el(r, "w:rPr"))
                        ppr = el(p, "w:pPr")
                        if ppr is not None:
                            cinfo["pPr"] = ppr_info(ppr)
                    tcpr = el(tc, "w:tcPr")
                    if tcpr is not None:
                        shd = el(tcpr, "w:shd")
                        if shd is not None:
                            cinfo["shd_fill"] = shd.get(qn("w:fill"))
                    sample.append(cinfo)
                rec["data_row_sample"] = sample
        table_records.append(rec)
        t_idx += 1
        # 嵌套表
        for nt in tbl_el.findall(f".//{{{W}}}tbl"):
            if nt is not tbl_el and nt.getparent().tag == qn("w:tc"):
                pass  # 嵌套表在深度遍历时另计；python-docx 不直接暴露，跳过计数

    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            from docx.text.paragraph import Paragraph
            p = Paragraph(child, doc)
            text = p.text.strip()
            ppr = el(child, "w:pPr")
            pstyle = None
            if ppr is not None:
                ps = el(ppr, "w:pStyle")
                if ps is not None:
                    pstyle = ps.get(qn("w:val"))
            style_hist[pstyle or "(default)"] += 1
            runs_info = []
            for r in p.runs:
                ri = rpr_info(el(r._r, "w:rPr"))
                if ri:
                    runs_info.append(ri)
                    f = ri.get("fonts", {})
                    for k in ("ascii", "eastAsia", "hAnsi"):
                        if f.get(k):
                            font_hist[f"{k}:{f[k]}"] += 1
                    if ri.get("sz_pt"):
                        size_hist[f"{ri['sz_pt']}pt"] += 1
                    if ri.get("color"):
                        color_hist[ri["color"]] += 1
            # 仅记录有实质内容或有直接格式的段落
            if text or runs_info or (ppr is not None and pstyle):
                rec = {"idx": p_idx, "style_id": pstyle,
                       "style_name": p.style.name if p.style else None,
                       "text_preview": text[:60],
                       "len": len(text),
                       "pPr": ppr_info(ppr)}
                if runs_info:
                    rec["run_rPr_sample"] = runs_info[0]
                    if len(runs_info) > 1:
                        rec["run_rPr_variants"] = len(runs_info)
                para_records.append(rec)
            p_idx += 1
        elif tag == "tbl":
            walk_tbl(child)

    report["paragraphs"] = para_records
    report["tables"] = table_records
    report["stats"] = {
        "total_paragraphs": p_idx,
        "recorded_paragraphs": len(para_records),
        "total_tables": t_idx,
        "style_usage": dict(style_hist.most_common()),
        "font_usage": dict(font_hist.most_common(30)),
        "size_usage": dict(size_hist.most_common(20)),
        "color_usage": dict(color_hist.most_common(20)),
    }

    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    # ---------- 控制台摘要 ----------
    print(f"=== 格式提取摘要: {src} ===")
    print(f"部件数: {len(parts)}  节数: {len(sections)}  段落: {p_idx}  表格: {t_idx}  样式定义: {len(styles)}")
    print(f"\n[页面] {sections[0]['page_w_mm']}x{sections[0]['page_h_mm']}mm, "
          f"边距 上{sections[0]['margin_top_mm']} 下{sections[0]['margin_bottom_mm']} "
          f"左{sections[0]['margin_left_mm']} 右{sections[0]['margin_right_mm']}mm")
    print(f"\n[段落样式使用 Top15]")
    for k, v in list(report["stats"]["style_usage"].items())[:15]:
        print(f"  {v:4d}  {k}")
    print(f"\n[字体使用 Top15]")
    for k, v in list(report["stats"]["font_usage"].items())[:15]:
        print(f"  {v:4d}  {k}")
    print(f"\n[字号使用]")
    for k, v in report["stats"]["size_usage"].items():
        print(f"  {v:4d}  {k}")
    print(f"\n[颜色使用]")
    for k, v in list(report["stats"]["color_usage"].items())[:10]:
        print(f"  {v:4d}  #{k}")
    print(f"\n[表格规模分布]")
    sizes = Counter((t["rows"], t["cols"]) for t in table_records)
    for (r, c), n in sorted(sizes.items()):
        print(f"  {n:3d} 个  {r}行 x {c}列  样式: {[t['style'] for t in table_records if (t['rows'],t['cols'])==(r,c)][0]}")
    print(f"\n全量报告: {out}")


if __name__ == "__main__":
    main()
