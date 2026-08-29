# -*- coding: utf-8 -*-
"""
scan-brand-residue.py — V 阶段对抗审查：模板品牌残留与悬空引用扫描。

检查模板包内全部 .xml/.rels：
  1. 品牌/人员关键词残留（Xmsilicon/芯劢微/浙江/XMNN/XMNPU/作者真名/水印元素名）；
  2. r:embed 悬空引用（drawing 已删但关系引用残留会导致 Word 修复）；
  3. word/media/ 文件；
  4. w:pict 元素；
  5. rels 中指向 media 的关系。

运行：
  py -3.14 examples/scan-brand-residue.py
"""
import os
import re
import zipfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = [
    ("xs模板", os.path.join(SKILL_DIR, "templates", "xs-sdk-guide-template.docx")),
    ("tech-guide模板", os.path.join(SKILL_DIR, "templates", "tech-guide-template.docx")),
    ("xs渲染产物", os.path.join(SKILL_DIR, "examples", "output", "xs-template-example.docx")),
]

# 检测词表（敏感词本身必须原样保留——扫描器职责即检出这些词；中立化产物命名为 xs，
# 但待检测对象可能携带原品牌词，词表不得随产物更名而替换）
KEYWORDS = ["Xmsilicon", "芯劢微", "浙江", "XMNN", "XMNPU", "新伟", "水之心",
            "张振宇", "刘新伟", "PowerPlusWaterMark"]

def main():
    for label, path in TARGETS:
        print(f"=== {label}: {os.path.basename(path)}")
        if not os.path.exists(path):
            rel = os.path.relpath(path, SKILL_DIR)
            print(f"  [跳过] 产物不存在：{rel}")
            print(f"         （渲染产物不入库，先运行 py -3.14 examples/xs-render-example.py 生成）")
            print()
            continue
        with zipfile.ZipFile(path) as z:
            allxml = ""
            for n in z.namelist():
                if n.endswith(".xml") or n.endswith(".rels"):
                    allxml += z.read(n).decode("utf-8", "ignore")
            hit = False
            for kw in KEYWORDS:
                cnt = allxml.count(kw)
                if cnt:
                    print(f"  [残留] {kw!r}: {cnt} 处")
                    hit = True
            if not hit:
                print("  关键词残留: 无")
            embeds = re.findall(r'r:embed="(rId\d+)"', allxml)
            print(f"  r:embed 引用: {embeds if embeds else '无'}")
            media = [n for n in z.namelist() if n.startswith("word/media/")]
            print(f"  word/media/ 文件: {len(media)}")
            print(f"  w:pict 元素: {allxml.count('<w:pict')}")
            img_rels = re.findall(r'Target="([^"]*media[^"]*)"', allxml)
            print(f"  rels 指向 media: {img_rels if img_rels else '无'}")
            # OPC 关系完整性：部件内 r:id/r:embed/r:link 引用必须在对应 .rels 中存在
            names = set(z.namelist())
            dangling = []
            for n in names:
                if not n.endswith(".xml") or n.endswith(".rels"):
                    continue
                if n == "word/document.xml":
                    rels_n = "word/_rels/document.xml.rels"
                elif re.match(r"word/(header|footer)\d+\.xml$", n):
                    rels_n = "word/_rels/" + n.split("/")[-1] + ".rels"
                else:
                    continue
                if rels_n not in names:
                    continue
                rels_xml = z.read(rels_n).decode("utf-8", "ignore")
                known = set(re.findall(r'Id="(rId\d+)"', rels_xml))
                used = set(re.findall(r'r:(?:id|embed|link)="(rId\d+)"',
                                      z.read(n).decode("utf-8", "ignore")))
                missing = used - known
                if missing:
                    dangling.append((n, sorted(missing)))
            print(f"  悬空关系引用: {dangling if dangling else '无'}")
        print()


if __name__ == "__main__":
    main()
