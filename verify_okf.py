import os
import re

BASE = r'd:\AI\docs\knowledge\learning'

BUNDLES = [
    'analyze-wechat-article-ai-switch-governance',
    'analyze-wechat-article-causal-ai',
    'analyze-wechat-article-quantdinger',
    'analyze-wechat-article-rqndd'
]

def parse_frontmatter(content):
    if not content.startswith('---'):
        return None, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    return parts[1].strip(), parts[2]

def verify_bundle(bundle_name):
    path = os.path.join(BASE, bundle_name)
    print(f'{"="*60}')
    print(f'Bundle: {bundle_name}')
    print(f'{"="*60}')
    
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = '  ' * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = '  ' * (level + 1)
        for f in sorted(files):
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, path)
            print(f'{subindent}{f}')
            
            if f.endswith('.md'):
                with open(fpath, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                fm, body = parse_frontmatter(content)
                
                if f == 'index.md' and root == path:
                    print(f'{subindent}  -> ROOT INDEX (okf_version check)')
                    if fm and 'okf_version' in fm:
                        print(f'{subindent}     [OK] okf_version present')
                    else:
                        print(f'{subindent}     [FAIL] okf_version missing')
                elif f == 'index.md':
                    print(f'{subindent}  -> SUBDIR INDEX (no frontmatter expected)')
                    if fm is None:
                        print(f'{subindent}     [OK] no frontmatter')
                    else:
                        print(f'{subindent}     [WARN] has frontmatter (should be none)')
                elif f == 'log.md':
                    print(f'{subindent}  -> LOG FILE')
                else:
                    print(f'{subindent}  -> CONTENT FILE')
                    required_fields = ['type', 'description', 'generated', 'verified', 'status', 'stale_after']
                    for field in required_fields:
                        if fm and field in fm:
                            print(f'{subindent}     [OK] {field}')
                        else:
                            print(f'{subindent}     [FAIL] {field} missing')
                    
                    if fm and 'source:' in fm and 'sources:' not in fm:
                        print(f'{subindent}     [FAIL] source not converted to sources')
                    elif fm and 'sources:' in fm:
                        print(f'{subindent}     [OK] source -> sources converted')
                    
                    links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', body)
                    bare_md_links = []
                    for text, url in links:
                        if url.endswith('.md') and not url.startswith('/') and not url.startswith('http'):
                            bare_md_links.append(url)
                    if bare_md_links:
                        print(f'{subindent}     [WARN] bare .md links: {bare_md_links}')
                    else:
                        print(f'{subindent}     [OK] no bare .md links')
    print()

for bundle in BUNDLES:
    verify_bundle(bundle)

print('Verification complete!')
