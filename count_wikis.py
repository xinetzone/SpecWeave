import os

base = r"d:\AI\.agents\docs\knowledge\learning"

categories = sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and (d.startswith('0') or d.startswith('10-'))])

NON_WIKI_WIKIS = {
    'first-principles', 'deep-learning-atomic-design', 'ai-engineering-notes',
    'causal-ai', 'atomic-emergence', 'quantdinger', 'ai-switch-governance',
    'rqndd', 'miaowu',
    # 无 -wiki 后缀但有 README.md 的 wiki 目录
    'pyinvoke-wiki', 'executablebooks-myst-guide', 'mdx-graphql-guide',
    'myst-markdown-tutorial',
    'baidu', 'deepseek', 'google-cloud', 'openai', 'oray',
    'conda-dev-github-wiki', 'conda-dev-source-wiki', 'git-baidu-sync',
    'ai-powershell5-hell-wiki',
}

result = {}
for cat in categories:
    cat_path = os.path.join(base, cat)
    wiki_dirs_all = []
    single_md_all = []
    for root, dirs, files in os.walk(cat_path):
        rel = os.path.relpath(root, base)
        parts = rel.split(os.sep)
        # Count all wiki dirs at any depth >= 2 (cat/subdir or deeper)
        if len(parts) >= 2:
            name = parts[-1]
            if "README.md" in files and not name.startswith('.') and not name.startswith('_'):
                if name.endswith("-wiki") or name in NON_WIKI_WIKIS:
                    wiki_dirs_all.append(name)
        # Count single -wiki.md files at ANY depth (>= 1, includes root of cat)
        if len(parts) >= 1:
            for f in files:
                if f.endswith("-wiki.md"):
                    single_md_all.append(f)
    result[cat] = {"wiki_dirs": sorted(set(wiki_dirs_all)), "single_md": sorted(set(single_md_all))}

total_all = 0
print("=" * 80)
print("FINAL COUNT (wiki dirs + single -wiki.md files at all depths)")
print("=" * 80)
for cat, counts in result.items():
    w = counts['wiki_dirs']
    s = counts['single_md']
    t = len(w) + len(s)
    total_all += t
    print(f"{cat}: wiki_dirs({len(w)})  single_md({len(s)})  total={t}")
    if len(w) <= 20:
        print(f"  dirs: {w}")
    else:
        print(f"  dirs: {w[:10]}... ({len(w)} total)")
    if s:
        print(f"  md:   {s}")

print(f"\nGrand total: {total_all}")
