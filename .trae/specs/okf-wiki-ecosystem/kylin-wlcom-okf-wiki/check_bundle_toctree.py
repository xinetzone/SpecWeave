import re, pathlib, sys

b = pathlib.Path(sys.argv[1])

def stems(p):
    txt = p.read_text(encoding='utf-8')
    m = re.search(r'`{3}\{toctree\}.*?\n(.*?)\n`{3}', txt, re.S)
    if not m:
        return None
    return [l.strip() for l in m.group(1).splitlines()
            if l.strip() and not l.strip().startswith(':')]

ok = True
for idx, sub in [('concepts/index.md', 'concepts'),
                 ('examples/index.md', 'examples'),
                 ('references/index.md', 'references')]:
    listed = stems(b / idx)
    actual = sorted(f.stem for f in (b / sub).glob('*.md') if f.name != 'index.md')
    match = sorted(listed) == actual
    print(f'{sub}: toctree={len(listed)} files={len(actual)} {"MATCH" if match else "MISMATCH"}')
    if not match:
        ok = False
        print('  only_listed=', sorted(set(listed) - set(actual)))
        print('  only_files =', sorted(set(actual) - set(listed)))

root = stems(b / 'index.md')
print('root toctree:', root)
for s in root:
    if not (b / (s + '.md')).exists():
        print('MISSING root target', s)
        ok = False

# 全部内容文件 frontmatter type 检查
fm_ok = True
for f in list((b / 'concepts').glob('*.md')) + list((b / 'examples').glob('*.md')) + list((b / 'references').glob('*.md')) + [b / 'index.md']:
    if f.name == 'index.md' and f.parent != b:
        continue
    head = f.read_text(encoding='utf-8')[:400]
    if not head.startswith('---'):
        print('NO FRONTMATTER:', f.relative_to(b)); fm_ok = False
    elif not re.search(r'^type:\s*\S+', head, re.M):
        print('NO TYPE:', f.relative_to(b)); fm_ok = False
# 子目录 index 不得有 frontmatter
for sub in ['concepts', 'examples', 'references']:
    t = (b / sub / 'index.md').read_text(encoding='utf-8')
    if t.startswith('---'):
        print('SUBINDEX HAS FRONTMATTER:', sub); ok = False
# okf_version 仅根 index
for f in b.rglob('*.md'):
    if f == b / 'index.md':
        continue
    if 'okf_version' in f.read_text(encoding='utf-8')[:300]:
        print('ROGUE okf_version:', f.relative_to(b)); ok = False

print('frontmatter/type:', 'PASS' if fm_ok else 'FAIL')
print('BUNDLE TOCTREE', 'PASS' if ok and fm_ok else 'FAIL')
