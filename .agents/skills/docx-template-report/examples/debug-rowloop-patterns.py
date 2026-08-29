# -*- coding: utf-8 -*-
"""
debug-rowloop-patterns.py — 隔离实验：docxtpl 0.20.2 表格行循环标签写法对照。

背景：既有模板（tech-guide / xmnn 初版）在数据行首格放
``{% for r in rows %}{{ r.a }}``、末格放 ``{{ r.b }}{% endfor %}``（纯标签与变量同段），
渲染后行不复制、反而横向增生单元格（2xN 变成 2x(2N-1)）。
本脚本用 4 种标签写法各渲染一个 2 行 2 列表格（3 条数据），检查物理结构：

  A. {%tr for%}/{%tr endfor%} 与变量同段（docxtpl 官方文档写法）
  B. {%tr for%}/{%tr endfor%} 独占段落，变量在同格另一段
  C. 纯标签 {% for%}/{% endfor%} 独占段落，变量在同格另一段
  D. 纯标签 {% for%}/{% endfor%} 与变量同段（复现横向增生，对照基线）
  E. {%tr for%} 独占首格首段、{%tr endfor%} 独占末格末段
  F. {%tr for%}/{%tr endfor%} 同在首格（for 段 + 变量段 + endfor 段）
  G. 三行分离：for 标记行 / 数据行 / endfor 标记行（标记在首列，无表头）
  H. 同 G，标记放在末列
  I. 三行分离 + 表头行（表头 / for 标记行 / 数据行 / endfor 标记行）
  J. 同 G，标记行非标记单元格含静态文本，验证整行移除不泄漏

运行：
  py -3.14 examples/debug-rowloop-patterns.py
"""
import os
from docx import Document
from docx.oxml.ns import qn
from docxtpl import DocxTemplate

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT_DIR, exist_ok=True)

ROWS = [{"a": f"a{i}", "b": f"b{i}"} for i in range(3)]


VARIANTS = ["G", "H", "I", "J"]


# 各变体模板表格的物理行数与期望渲染维度（3 条数据）
NROWS = {"A": 2, "B": 2, "C": 2, "D": 2, "E": 2, "F": 2,
         "G": 3, "H": 3, "I": 4, "J": 3}
EXPECTED_DIM = {"G": (3, 2), "H": (3, 2), "I": (4, 2), "J": (3, 2)}


def fill_table(tbl, v):
    """按写法 v 填充表格。"""
    if v in ("G", "H", "J"):
        # 三行分离：r0=for 标记行（渲染移除）/ r1=数据行 / r2=endfor 标记行（渲染移除）
        r0, r1, r2 = tbl.rows
        mark_col = 1 if v == "H" else 0
        r0.cells[mark_col].text = '{%tr for r in rows %}'
        r2.cells[mark_col].text = '{%tr endfor %}'
        r1.cells[0].text = '{{ r.a }}'
        r1.cells[1].text = '{{ r.b }}'
        if v == "J":
            # 标记行另一格放静态文本：若整行正确移除则输出中不应出现 static
            r0.cells[1 - mark_col].text = 'static-for'
            r2.cells[1 - mark_col].text = 'static-end'
        return
    if v == "I":
        # 带表头：r0=表头 / r1=for 标记行 / r2=数据行 / r3=endfor 标记行
        r0, r1, r2, r3 = tbl.rows
        r0.cells[0].text = 'hdr-I-1'
        r0.cells[1].text = 'hdr-I-2'
        r1.cells[0].text = '{%tr for r in rows %}'
        r2.cells[0].text = '{{ r.a }}'
        r2.cells[1].text = '{{ r.b }}'
        r3.cells[0].text = '{%tr endfor %}'
        return
    hdr = tbl.rows[0].cells
    hdr[0].text = f"hdr-{v}-1"
    hdr[1].text = f"hdr-{v}-2"
    c0 = tbl.rows[1].cells[0]
    c1 = tbl.rows[1].cells[1]
    if v == "A":  # tr 标记，标签与变量同段
        c0.text = '{%tr for r in rows %}{{ r.a }}'
        c1.text = '{{ r.b }}{%tr endfor %}'
    elif v == "B":  # tr 标记，标签独占段，变量另起段
        c0.text = '{%tr for r in rows %}'
        c0.add_paragraph('{{ r.a }}')
        c1.text = '{{ r.b }}'
        c1.add_paragraph('{%tr endfor %}')
    elif v == "C":  # 纯标签独占段，变量另起段
        c0.text = '{% for r in rows %}'
        c0.add_paragraph('{{ r.a }}')
        c1.text = '{{ r.b }}'
        c1.add_paragraph('{% endfor %}')
    elif v == "D":  # 纯标签与变量同段（基线，预期横向增生）
        c0.text = '{% for r in rows %}{{ r.a }}'
        c1.text = '{{ r.b }}{% endfor %}'
    elif v == "E":  # tr 标记：for 在首格首段独占、endfor 在末格末段独占
        c0.text = '{%tr for r in rows %}'
        c0.add_paragraph('{{ r.a }}')
        c1.text = '{%tr endfor %}'
        c1.paragraphs[0].insert_paragraph_before('{{ r.b }}')
    else:  # F: tr 标记，for/endfor 同在首格（for 段 + endfor 段），变量在两格
        c0.text = '{%tr for r in rows %}'
        c0.add_paragraph('{{ r.a }}')
        c0.add_paragraph('{%tr endfor %}')
        c1.text = '{{ r.b }}'


def main():
    for v in VARIANTS:
        tpl_path = os.path.join(OUT_DIR, f"debug-rowloop-{v}-tpl.docx")
        out_path = os.path.join(OUT_DIR, f"debug-rowloop-{v}-out.docx")
        doc = Document()
        fill_table(doc.add_table(rows=NROWS[v], cols=2), v)
        doc.save(tpl_path)
        print(f"=== 写法 {v} ===")
        try:
            tpl = DocxTemplate(tpl_path)
            tpl.render({"rows": ROWS})
            tpl.save(out_path)
        except Exception as exc:
            print(f"    渲染失败: {type(exc).__name__}: {exc}\n")
            continue
        chk = Document(out_path)
        tbl = chk.tables[0]
        dim = (len(tbl.rows), len(tbl.columns))
        all_text = []
        for ri, tr in enumerate(tbl._tbl.findall(qn("w:tr"))):
            tcs = tr.findall(qn("w:tc"))
            texts = [
                "".join(t.text or "" for t in tc.iter(qn("w:t")))
                for tc in tcs
            ]
            all_text.extend(texts)
            print(f"    tr{ri}: {len(tcs)}tc -> {texts}")
        expected = EXPECTED_DIM.get(v, (4, 2))
        ok = dim == expected
        if v == "J":
            leak = [t for t in all_text if "static" in t]
            ok = ok and not leak
            print(f"    标记行静态文本泄漏检查: {'无泄漏 PASS' if not leak else f'泄漏 FAIL {leak}'}")
        print(f"    维度={dim} 期望={expected} => {'PASS 行复制正确' if ok else 'FAIL 结构异常'}\n")


if __name__ == "__main__":
    main()
