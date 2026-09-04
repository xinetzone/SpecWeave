# -*- coding: utf-8 -*-
"""V 阶段对抗审查：原文抽查逐字比对脚本（examples vs raw-texts.md）"""
import io
import random
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r"d:\spaces\SpecWeave"
EX1 = BASE + r"\projects\awesome-okf-xs\doc\bundles\think\confucian\four-books\examples\01-analects-close-reading.md"
EX2 = BASE + r"\projects\awesome-okf-xs\doc\bundles\think\confucian\four-books\examples\02-four-books-selected-readings.md"
RAW = BASE + r"\.trae\specs/classics-knowledge/create-confucian-okf-wiki\raw-texts.md"


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def first_diff(a, b):
    """返回首个差异位置与上下文；完全一致返回 None"""
    if a == b:
        return None
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            lo = max(0, i - 12)
            return (i, a[lo:i + 12], b[lo:i + 12])
    i = n
    lo = max(0, i - 12)
    return (i, a[lo:lo + 12], b[lo:lo + 12])


def extract_blockquotes_after(text, start_idx, count=None):
    """从 start_idx 起提取连续的 blockquote 段落（段落间以空行分隔），返回段落列表"""
    paras = []
    cur = []
    lines = text[start_idx:].split('\n')
    for ln in lines:
        if ln.startswith('> '):
            cur.append(ln[2:])
        elif ln.strip() == '' and cur:
            paras.append(''.join(cur))
            cur = []
            if count is not None and len(paras) >= count:
                break
        elif cur and not ln.startswith('>'):
            # blockquote 结束（遇到非空非引用行）
            paras.append(''.join(cur))
            cur = []
            if count is not None and len(paras) >= count:
                break
    if cur:
        paras.append(''.join(cur))
    return paras


def report(tag, ex_text, raw_text):
    d = first_diff(ex_text, raw_text)
    if d is None:
        print(f"  [PASS] {tag}：逐字一致（{len(ex_text)} 字）")
        return True
    i, ctx_a, ctx_b = d
    print(f"  [FAIL] {tag}：不一致于第 {i} 字")
    print(f"    examples: ...{ctx_a}...")
    print(f"    raw-texts: ...{ctx_b}...")
    print(f"    examples 长度={len(ex_text)}, raw-texts 长度={len(raw_text)}")
    return False


ex1 = read(EX1)
ex2 = read(EX2)
raw = read(RAW)

# ============ 一、《论语》随机 5 章 ============
# 解析 examples/01：### X.Y 标题 → **原文** 后的 blockquote
chapters_ex = {}
for m in re.finditer(r'\n### (\d+\.\d+) [^\n]*\n', ex1):
    cid = m.group(1)
    seg = ex1[m.end():m.end() + 4000]
    mm = re.search(r'\*\*原文\*\*[^\n]*\n((?:[^\n]*\n)?(?:> [^\n]*\n)+)', seg)
    if mm:
        quote = ''.join(l[2:] for l in mm.group(1).split('\n') if l.startswith('> '))
        chapters_ex[cid] = quote

# 解析 raw-texts.md：**X.Y** 文本
chapters_raw = {}
for m in re.finditer(r'\*\*(\d+\.\d+)\*\* (.+)', raw):
    chapters_raw[m.group(1)] = m.group(2).strip()

print("=" * 70)
print("一、《论语》精读随机抽样比对（seed=20260831，从 40 章抽 5）")
print("=" * 70)
print(f"  解析：examples/01 共 {len(chapters_ex)} 章；raw-texts 共 {len(chapters_raw)} 章")

random.seed(20260831)
sample = sorted(random.sample(sorted(chapters_ex.keys()), 5))
print(f"  随机样本：{sample}\n")
pass_count = 0
for cid in sample:
    ok = report(f"论语 {cid}", chapters_ex[cid], chapters_raw.get(cid, ''))
    pass_count += ok
print(f"  结果：{pass_count}/5 一致\n")

# ============ 二、examples/02 指定 5 段 ============
print("=" * 70)
print("二、四书精读指定段落比对（大学经一章/传五章/中庸首章/中庸二十章/孟子浩然之气）")
print("=" * 70)
pass_count2 = 0

# --- 大学经一章 ---
m = re.search(r'\n### 经一章\n', ex2)
paras_ex = extract_blockquotes_after(ex2, m.end(), 2)
# raw: ### 经 之后的两个段落
m_raw = re.search(r'\n### 经\n\n(.+?)\n\n(.+?)\n\n### 传\n', raw, re.S)
paras_raw = [m_raw.group(1).strip(), m_raw.group(2).strip()]
print(f"  [大学·经一章] examples {len(paras_ex)} 段 vs raw {len(paras_raw)} 段")
for i in range(min(len(paras_ex), len(paras_raw))):
    pass_count2 += report(f"大学经一章 第{i+1}段", paras_ex[i], paras_raw[i])

# --- 大学传五章（朱熹补传）---
m = re.search(r'\n#### 传五章（释格物致知，朱熹补传）\n', ex2)
paras_ex = extract_blockquotes_after(ex2, m.end(), 1)
m_raw = re.search(r'\*\*传五章（释格物致知，朱熹补传）\*\*\n\n(.+?)\n\n', raw, re.S)
pass_count2 += report("大学传五章（补传）", paras_ex[0], m_raw.group(1).strip())

# --- 中庸首章 ---
m = re.search(r'\n### 第一章（总纲：性、道、教与中和）\n', ex2)
m2 = re.search(r'\n#### 原文\n', ex2[m.start():m.start() + 2000])
paras_ex = extract_blockquotes_after(ex2, m.start() + m2.end(), 1)
m_raw = re.search(r'\*\*第一章\*\*\n\n(.+?)\n\n\*\*第二章\*\*', raw, re.S)
pass_count2 += report("中庸第一章（首章）", paras_ex[0], m_raw.group(1).strip())

# --- 中庸第二十章（上/下）---
paras_ex = []
for tag in ['第二十章（上）', '第二十章（下）']:
    m = re.search(r'\*\*' + re.escape(tag) + r'\*\*\n', ex2)
    bq = extract_blockquotes_after(ex2, m.end(), 1)
    paras_ex.append(bq[0])
    m_raw = re.search(r'\*\*' + re.escape(tag) + r'\*\*\n\n(.+?)\n\n', raw, re.S)
    pass_count2 += report(f"中庸{tag}", bq[0], m_raw.group(1).strip())

# --- 孟子浩然之气章（公孙丑上第二章，节选）---
m = re.search(r'\n#### 第二章（节选，浩然之气）\n', ex2)
paras_ex = extract_blockquotes_after(ex2, m.end(), 1)
m_raw = re.search(r'\*\*第二章（节选，浩然之气）\*\* (.+?)\n', raw, re.S)
pass_count2 += report("孟子·公孙丑上第二章（浩然之气，节选）", paras_ex[0], m_raw.group(1).strip())

print(f"\n  结果：{pass_count2}/6 段一致（含中庸二十章上下两段）")
print(f"\n总计：论语 {pass_count}/5 + 指定段落 {pass_count2}/6 = {pass_count + pass_count2}/11")
