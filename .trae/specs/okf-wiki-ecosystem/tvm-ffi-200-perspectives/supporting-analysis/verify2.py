# -*- coding: utf-8 -*-
"""统计 d:\AI\projects\docs 下全部概念文档的字数（Checkpoint 76 / NFR-3）。

判定口径：
- 仅统计概念文档（concepts/ 下的 .md），排除 index.md/log.md/references。
- 排除 frontmatter（--- 包裹）后的正文。
- 主指标 CN=中文字符数（含 CJK 标点/全角字符），统计范围覆盖代码块与内联代码（代码中的注释汉字也计入）。
- 辅助指标 ALL=正文去除空白后的字符总数（中文+ASCII 字母数字）。
- 主指标 CN < 800 判定为字数不足。
"""
import os
import re

ROOT = r"d:\AI\projects\docs"

CN = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
# 中文字符 + ASCII 字母数字
ANY = re.compile(r"[^\s]")


def count_file(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"^---.*?---", "", text, count=1, flags=re.S)
    cn = len(CN.findall(text))
    allc = len(ANY.findall(text))
    return cn, allc


def main():
    below = []
    total_docs = 0
    for dirpath, _, files in os.walk(ROOT):
        for fn in sorted(files):
            if not fn.endswith(".md") or fn in ("index.md", "log.md") or "references" in dirpath:
                continue
            p = os.path.join(dirpath, fn)
            total_docs += 1
            cn, allc = count_file(p)
            if cn < 800:
                rel = os.path.relpath(p, ROOT)
                below.append((cn, allc, rel))
    below.sort()
    print(f"概念文档总数: {total_docs}")
    print(f"<800 中文字数文档数: {len(below)}")
    print("-" * 40)
    for cn, allc, rel in below:
        print(f"CN={cn:4d} (ALL={allc:5d})  {rel}")


if __name__ == "__main__":
    main()