# -*- coding: utf-8 -*-
"""
analyze-media-watermark.py — R 阶段事实盘点：模板/源文档的媒体引用与水印现状。

检查项：
  1. word/media/ 清单（文件名、大小）
  2. 每个媒体被哪些部件引用（document/header/footer 的 .rels）
  3. 水印：header/footer 内 v:shape/w:pict/PowerPlusWaterMarkObject、document w:background
  4. docProps 元数据（core.xml/app.xml 作者/公司/标题）
  5. 封面 sdt 与页眉表格内 drawing 定位

运行：
  py -3.14 examples/analyze-media-watermark.py
"""
import os
import zipfile
import re
import glob

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 源文档在本地 .chaos 工作区（不入库）；以通配符定位，不固化源文件名
_SRC = (glob.glob(r"d:\AI\.chaos\tests\old\work\doc\*SDK*指南*.docx") or [None])[0]
TARGETS = [
    ("源文档", _SRC),
    ("xs模板", os.path.join(SKILL_DIR, "templates", "xs-sdk-guide-template.docx")),
]

WATERMARK_MARKERS = [
    "PowerPlusWaterMarkObject", "watermark", "Watermark",
    "<v:shape", "<w:pict", "urn:schemas-microsoft-com:vml",
    "<w:background", "textpath",
]


def analyze(label, path):
    print(f"\n{'='*70}\n{label}: {path}\n{'='*70}")
    if not os.path.exists(path):
        print("  [缺失] 文件不存在")
        return
    print(f"  文件大小: {os.path.getsize(path):,} 字节")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()

        # 1. media 清单
        media = [n for n in names if n.startswith("word/media/")]
        print(f"\n[1] word/media/ 文件数: {len(media)}")
        total = 0
        for n in sorted(media):
            sz = z.getinfo(n).file_size
            total += sz
            print(f"    {n}  {sz:,} 字节")
        print(f"    媒体总大小: {total:,} 字节")

        # 2. rels 引用关系：rId -> media
        rels_files = [n for n in names if n.endswith(".rels")]
        rid_to_media = {}   # (part_dir, rId) -> target
        for rf in rels_files:
            xml = z.read(rf).decode("utf-8", "ignore")
            for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', xml):
                rid, target = m.group(1), m.group(2)
                if "media/" in target:
                    part_dir = os.path.dirname(rf.replace("_rels/", "").replace("word/_rels", "word"))
                    rid_to_media[(rf, rid)] = target

        # 3. 各部件内 embed 引用
        print(f"\n[2] 媒体引用位置:")
        embed_re = re.compile(r'(?:r:embed|r:link|r:id)="(rId\d+)"')
        parts = [n for n in names if n.endswith(".xml") and (
            n.startswith("word/") and not n.startswith("word/_rels"))]
        used_media = set()
        for p in sorted(parts):
            xml = z.read(p).decode("utf-8", "ignore")
            embeds = embed_re.findall(xml)
            if not embeds:
                continue
            # 找该部件对应的 rels
            rels_name = "word/_rels/" + os.path.basename(p) + ".rels" if "/" not in p[5:] \
                else os.path.dirname(p) + "/_rels/" + os.path.basename(p) + ".rels"
            rel_map = {}
            if rels_name in names:
                rxml = z.read(rels_name).decode("utf-8", "ignore")
                for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rxml):
                    rel_map[m.group(1)] = m.group(2)
            targets = [rel_map.get(r, f"?{r}") for r in embeds]
            for t in targets:
                used_media.add("word/" + t.lstrip("/").replace("../", ""))
            print(f"    {p}: {len(embeds)} 处 drawing 引用 -> {targets}")

        orphan = [n for n in media if n not in used_media and not any(
            n.endswith(os.path.basename(t)) for t in used_media)]
        print(f"\n[3] 孤儿媒体（包内存在但无部件引用）: {len(orphan)}")
        for n in orphan:
            print(f"    {n}")

        # 4. 水印检查
        print(f"\n[4] 水印检查:")
        wm_found = False
        for p in sorted(parts):
            xml = z.read(p).decode("utf-8", "ignore")
            hits = [mk for mk in WATERMARK_MARKERS if mk in xml]
            if hits:
                wm_found = True
                # 提取 v:shape 中的 style/文字
                shapes = re.findall(r'<v:shape[^>]*>.*?</v:shape>', xml, re.S)
                texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml)
                print(f"    {p}: 命中标记 {hits}")
                if shapes:
                    for s in shapes[:3]:
                        style = re.search(r'style="([^"]*)"', s)
                        tid = re.search(r'id="([^"]*)"', s)
                        print(f"      v:shape id={tid.group(1) if tid else '?'} "
                              f"style={style.group(1) if style else '?'}")
                if "textpath" in xml:
                    tp = re.findall(r'<v:textpath[^>]*string="([^"]*)"', xml)
                    print(f"      水印文字: {tp}")
        if not wm_found:
            print("    未发现水印元素")

        # 5. docProps 元数据
        print(f"\n[5] docProps 元数据:")
        for dp in ("docProps/core.xml", "docProps/app.xml"):
            if dp in names:
                xml = z.read(dp).decode("utf-8", "ignore")
                fields = re.findall(r"<(dc:[^>]+|cp:[^>]+|Company|Manager|Application|TitlesOfParts)>([^<]*)<", xml)
                print(f"    {dp}:")
                for tag, val in fields:
                    if val.strip():
                        print(f"      {tag} = {val.strip()}")


for label, path in TARGETS:
    analyze(label, path)
