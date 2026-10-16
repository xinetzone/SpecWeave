import re, pathlib, sys

ROOT = pathlib.Path(sys.argv[1])          # kywc source repo
B = pathlib.Path(sys.argv[2])             # bundle dir

# ---------- AC-3 计数（python 独立口径） ----------
ch = [p for p in ROOT.rglob('*') if p.suffix in ('.c', '.h') and '.git' not in p.parts]
loc = 0
for p in ch:
    loc += sum(1 for _ in p.open('rb'))
src_subs = sorted([p.name for p in (ROOT / 'src').iterdir() if p.is_dir()])
src_sub_files = sum(1 for p in (ROOT / 'src').rglob('*') if p.suffix in ('.c', '.h'))
xmls = sorted(p.name for p in (ROOT / 'protocols').glob('*.xml'))
effect_c = list((ROOT / 'src' / 'effect').glob('*.c'))
effect_shaders = [p for p in (ROOT / 'src' / 'effect' / 'shaders').iterdir()
                  if p.suffix in ('.frag', '.vert')]
opts = re.findall(r"^option\(", (ROOT / 'meson_options.txt').read_text(encoding='utf-8'), re.M)
pos = [l for l in (ROOT / 'po' / 'LINGUAS').read_text(encoding='utf-8').splitlines() if l.strip()]
pofiles = list((ROOT / 'po').glob('*.po'))
libkywc = [p for p in (ROOT / 'libkywc').rglob('*') if p.suffix in ('.c', '.h')]
portal = [p for p in (ROOT / 'portal').rglob('*') if p.suffix in ('.c', '.h')]
examples = [p for p in (ROOT / 'examples').rglob('*') if p.suffix in ('.c', '.h', '.cpp')]
# kywc.syms 非 static kywc_*：以 libkywc.h 声明数为口径
kyh = (ROOT / 'libkywc' / 'libkywc.h').read_text(encoding='utf-8')
api = re.findall(r'^\w[\w \*]*\bkywc_\w+\s*\(', kyh, re.M)

print('== COUNTS (python) ==')
for k, v in [('C/H files', len(ch)), ('LOC(sum lines)', loc), ('src/ subs', len(src_subs)),
             ('src/ recursive C/H', src_sub_files), ('protocols XML', len(xmls)),
             ('effect/*.c', len(effect_c)), ('effect shaders', len(effect_shaders)),
             ('meson options', len(opts)), ('LINGUAS lines', len(pos)),
             ('po/*.po', len(pofiles)), ('libkywc C/H', len(libkywc)),
             ('portal C/H', len(portal)), ('examples C/CPP/H', len(examples)),
             ('libkywc.h kywc_ decls', len(api))]:
    print(f'{k}: {v}')

# XML interface 数
iface = 0
for x in (ROOT / 'protocols').glob('*.xml'):
    iface += len(re.findall(r'<interface\s+name=', x.read_text(encoding='utf-8')))
print('XML interfaces:', iface)

# ---------- AC-4 路径纪律 ----------
print('\n== PATH DISCIPLINE (bundle) ==')
bad = []
for f in B.rglob('*.md'):
    t = f.read_text(encoding='utf-8')
    for pat in [r'file:///', r'external[/\\]dao', r'[dD]:\\spaces', r'\.tmp[/\\]', r'\.chaos[/\\]']:
        if re.search(pat, t):
            bad.append((f.relative_to(B), pat))
print('violations:', bad if bad else 'NONE')

# ---------- AC-5 束内链接 ----------
print('\n== INTERNAL LINKS ==')
broken = []
link_re = re.compile(r'\]\((/[^)]+\.md)(#[^)]*)?\)')
for f in B.rglob('*.md'):
    for m in link_re.finditer(f.read_text(encoding='utf-8')):
        target = m.group(1)
        p = B / target.lstrip('/')
        if not p.exists():
            broken.append((f.relative_to(B).as_posix(), target))
print('broken /-links:', broken if broken else 'NONE')

# ---------- 外链域名 ----------
print('\n== EXTERNAL LINKS ==')
ext = set()
for f in B.rglob('*.md'):
    for m in re.finditer(r'\]\((https?://[^)]+)\)', f.read_text(encoding='utf-8')):
        ext.add(m.group(1).split('#')[0])
for e in sorted(ext):
    print(e)
