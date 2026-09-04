# -*- coding: utf-8 -*-
"""V 阶段对抗审查：格式抽查脚本（frontmatter / kebab-case / 交叉引用断链）"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r"d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\think\confucian\four-books"

issues = []
ok_count = 0

# 相对路径 markdown 链接（排除 http/https/mailto/锚点）
LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
URL_RE = re.compile(r'^(https?://|mailto:|#)')

for root, dirs, files in os.walk(BASE):
    for fn in sorted(files):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, BASE).replace('\\', '/')
        with open(p, encoding='utf-8') as f:
            text = f.read()

        # ---- 1. kebab-case 文件名检查 ----
        stem = fn[:-3]
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', stem):
            issues.append(f"[命名] {rel} 文件名非 kebab-case")

        # ---- 2. frontmatter type: OKF 检查（index/log 豁免） ----
        if stem not in ('index', 'log'):
            m = re.match(r'\A---\s*\n(.*?)\n---\s*\n', text, re.S)
            if not m:
                issues.append(f"[frontmatter] {rel} 缺少 frontmatter")
            elif not re.search(r'^type:\s*OKF\s*$', m.group(1), re.M):
                issues.append(f"[frontmatter] {rel} frontmatter 缺 type: OKF")

        # ---- 3. 交叉引用断链检查 ----
        # 排除代码块与行内代码，避免误提取
        stripped = re.sub(r'```.*?```', '', text, flags=re.S)
        stripped = re.sub(r'`[^`\n]*`', '', stripped)
        for m in LINK_RE.finditer(stripped):
            target = m.group(2).strip()
            if URL_RE.match(target):
                continue
            path_part = target.split('#')[0]
            if not path_part:
                continue  # 纯锚点
            # 处理 <> 包裹或空格
            path_part = path_part.strip('<>').replace('%20', ' ')
            abs_t = os.path.normpath(os.path.join(root, path_part))
            if not os.path.exists(abs_t):
                issues.append(f"[断链] {rel} -> {target}")
            else:
                ok_count += 1

print("== 格式抽查结果 ==")
if issues:
    for i in issues:
        print("FAIL:", i)
else:
    print("全部通过")
print(f"\n检查链接总数（有效）: {ok_count}")
print(f"问题总数: {len(issues)}")

# ---- 附加：根目录 index.md 存在性 ----
print("\n== 结构检查 ==")
print("根 index.md 存在:", os.path.exists(os.path.join(BASE, 'index.md')))
print("concepts/index.md 存在:", os.path.exists(os.path.join(BASE, 'concepts', 'index.md')))
print("examples/index.md 存在:", os.path.exists(os.path.join(BASE, 'examples', 'index.md')))
print("references/index.md 存在:", os.path.exists(os.path.join(BASE, 'references', 'index.md')))
