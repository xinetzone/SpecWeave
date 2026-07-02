#!/usr/bin/env python3
"""
.agents/ 目录 Frontmatter 批量补全工具。

功能：
1. 为缺少frontmatter的文件添加标准四字段YAML frontmatter
2. 为已有frontmatter但字段不全的文件补全缺失字段（source/x-toml-ref等）
3. 自动跳过使用专用schema的文件（skills/、元数据文件等）

标准四字段：
  id: kebab-case文件名/路径推导
  title: 从H1标题提取
  source: 推导来源（AGENTS.md索引）
  x-toml-ref: 自动计算相对路径到.meta/toml/

用法：
    python add-agents-frontmatter.py --dry-run                     # 预览模式
    python add-agents-frontmatter.py                               # 执行补全（新增+补字段）
    python add-agents-frontmatter.py --fix-fields                  # 仅补全已有frontmatter的缺失字段
    python add-agents-frontmatter.py --file .agents/rules/xxx.md   # 只处理单个文件
    python add-agents-frontmatter.py --exclude prompts systems    # 排除指定目录
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.project import resolve_project_root

H1_RE = re.compile(r'^#\s+(.+?)\s*$', re.MULTILINE)
YAML_FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
TOML_FM_RE = re.compile(r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n', re.DOTALL)

FIELD_ID_RE = re.compile(r'^id\s*[=:]\s*"?(.+?)"?\s*$', re.MULTILINE)
FIELD_TITLE_RE = re.compile(r'^title\s*[=:]\s*"?(.+?)"?\s*$', re.MULTILINE)
FIELD_SOURCE_RE = re.compile(r'^source\s*[=:]\s*"?(.+?)"?\s*$', re.MULTILINE)
FIELD_XREF_RE = re.compile(r'^x-toml-ref\s*[=:]\s*"?(.+?)"?\s*$', re.MULTILINE)
FIELD_NAME_RE = re.compile(r'^name\s*:', re.MULTILINE)
FIELD_SCHEMA_RE = re.compile(r'^schema\s*:', re.MULTILINE)

SKIP_DIRS = {'__pycache__', 'node_modules', '.venv', '.git', '.pytest_cache', 'mdi', 'tests', 'config'}

SCHEMA_FILES = {
    'ONBOARDING.md',
    'capability-registry.md',
}

SCHEMA_FILE_PREFIXES = ()

SOURCE_MAP = {
    'rules': 'AGENTS.md#规则体系',
    'protocols': 'AGENTS.md#协作协议',
    'roles': 'AGENTS.md#角色定义',
    'teams': 'AGENTS.md#团队管理',
    'templates': 'AGENTS.md#模板',
    'tools': 'AGENTS.md#工具规范',
    'workflows': 'AGENTS.md#标准工作流',
    'modules': 'AGENTS.md#自我演进模块',
    'commands': 'AGENTS.md#指令集',
    'prompts': 'AGENTS.md#提示词',
    'capabilities': 'AGENTS.md#能力注册中心',
    'worlds': 'AGENTS.md#团队管理',
    'systems': 'AGENTS.md#核心规范入口',
    'cases': 'AGENTS.md#知识库与复盘',
}


def compute_id(rel_path: str) -> str:
    stem = Path(rel_path).stem
    parent = Path(rel_path).parent.name
    if stem == 'README':
        if parent == '.agents':
            return 'agents-readme'
        return parent
    parts = rel_path.replace('.agents/', '').replace('.md', '').split('/')
    return '-'.join(p for p in parts if p and p != 'README')


def compute_source(rel_path: str) -> str:
    parts = rel_path.split('/')
    if len(parts) >= 2:
        subdir = parts[1]
        if subdir in SOURCE_MAP:
            return SOURCE_MAP[subdir]
    return 'AGENTS.md'


def compute_x_toml_ref(md_path: Path, project_root: Path) -> str:
    rel_path = md_path.relative_to(project_root).as_posix()
    toml_rel = '.meta/toml/' + rel_path.replace('.md', '.toml')
    parent_depth = len(Path(rel_path).parent.parts)
    if parent_depth == 0:
        return toml_rel
    return '../' * parent_depth + toml_rel


def extract_h1_title(content: str, fallback: str) -> str:
    m = H1_RE.search(content)
    if m:
        return m.group(1).strip()
    return fallback


def is_skill_format(fm_content: str) -> bool:
    return bool(FIELD_NAME_RE.search(fm_content)) and 'description' in fm_content


def has_custom_schema(fm_content: str, filename: str, rel_path: str) -> bool:
    if filename in SCHEMA_FILES:
        return True
    if 'ONBOARDING-TEMPLATE' in filename:
        return True
    if 'REGISTRY-TEMPLATE' in filename:
        return False
    parts = rel_path.split('/')
    if len(parts) >= 2 and parts[1] == 'skills':
        return True
    return False


def extract_yaml_frontmatter(content: str):
    m = YAML_FM_RE.match(content)
    if m:
        return m.group(0), m.group(1), m.end(), 'yaml'
    m = TOML_FM_RE.match(content)
    if m:
        return m.group(0), m.group(1), m.end(), 'toml'
    return None, None, 0, None


def parse_field(fm_text: str, pattern) -> str | None:
    m = pattern.search(fm_text)
    if m:
        return m.group(1).strip().strip('"')
    return None


def build_frontmatter_yaml(fid: str, title: str, source: str, xref: str) -> str:
    return (
        '---\n'
        f'id: "{fid}"\n'
        f'title: "{title}"\n'
        f'source: "{source}"\n'
        f'x-toml-ref: "{xref}"\n'
        '---\n'
    )


def merge_fields_into_fm(fm_block: str, fm_text: str, fid: str, title: str, source: str, xref: str, fmt: str) -> str:
    """在已有frontmatter块中补全缺失字段，保持其他字段不变。"""
    sep = ':' if fmt == 'yaml' else ' ='
    quote = '"' if fmt == 'yaml' else '"'

    has_id = FIELD_ID_RE.search(fm_text)
    has_title = FIELD_TITLE_RE.search(fm_text)
    has_source = FIELD_SOURCE_RE.search(fm_text)
    has_xref = FIELD_XREF_RE.search(fm_text)

    additions = []
    if not has_id:
        additions.append(f'id{sep} {quote}{fid}{quote}')
    if not has_title and title:
        safe_title = title.replace('"', "'")
        additions.append(f'title{sep} {quote}{safe_title}{quote}')
    if not has_source:
        additions.append(f'source{sep} {quote}{source}{quote}')
    if not has_xref:
        additions.append(f'x-toml-ref{sep} {quote}{xref}{quote}')

    if not additions:
        return fm_block

    if fmt == 'yaml':
        new_fm = fm_block.rstrip()
        if not new_fm.endswith('\n'):
            new_fm += '\n'
        for add in additions:
            new_fm = new_fm.replace('\n---\n', f'\n{add}\n---\n')
        return new_fm
    else:
        lines = fm_block.rstrip('\n').split('\n')
        insert_pos = len(lines) - 1
        for i, line in enumerate(lines):
            if line.strip() == '+++':
                insert_pos = i
                break
        for add in additions:
            lines.insert(insert_pos, add)
            insert_pos += 1
        return '\n'.join(lines) + '\n'


def process_file(md_path: Path, project_root: Path, dry_run: bool, fix_fields: bool) -> dict:
    result = {
        'file': str(md_path),
        'rel': '',
        'action': 'skip',
        'reason': '',
        'id': '',
        'fields_added': [],
    }

    try:
        rel = md_path.relative_to(project_root).as_posix()
        result['rel'] = rel
    except ValueError:
        rel = str(md_path)

    try:
        content = md_path.read_text(encoding='utf-8')
    except Exception as e:
        result['action'] = 'error'
        result['reason'] = f'read failed: {e}'
        return result

    fid = compute_id(rel)
    fallback_title = fid.replace('-', ' ').title()
    title = extract_h1_title(content, fallback_title)
    source = compute_source(rel)
    xref = compute_x_toml_ref(md_path, project_root)
    result['id'] = fid

    fm_block, fm_text, fm_end, fmt = extract_yaml_frontmatter(content)

    if fm_block is None:
        new_fm = build_frontmatter_yaml(fid, title.replace('"', "'"), source, xref)
        new_content = new_fm + content
        result['action'] = 'would_add' if dry_run else 'added'
        result['fields_added'] = ['id', 'title', 'source', 'x-toml-ref']
        if not dry_run:
            md_path.write_text(new_content, encoding='utf-8')
        return result

    if is_skill_format(fm_text) or has_custom_schema(fm_text, md_path.name, rel):
        result['action'] = 'skip'
        result['reason'] = '专用schema文件（Skill/模板/元数据），不修改'
        return result

    existing_id = parse_field(fm_text, FIELD_ID_RE)
    existing_title = parse_field(fm_text, FIELD_TITLE_RE)
    existing_source = parse_field(fm_text, FIELD_SOURCE_RE)
    existing_xref = parse_field(fm_text, FIELD_XREF_RE)

    missing = []
    if not existing_id: missing.append('id')
    if not existing_title: missing.append('title')
    if not existing_source: missing.append('source')
    if not existing_xref: missing.append('x-toml-ref')

    if not missing:
        result['action'] = 'skip'
        result['reason'] = '四字段齐全'
        return result

    if not fix_fields and not missing:
        result['action'] = 'skip'
        result['reason'] = '已有frontmatter（使用--fix-fields补全缺失字段）'
        return result

    resolved_title = existing_title or title
    new_fm_block = merge_fields_into_fm(fm_block, fm_text, fid, resolved_title, source, xref, fmt)
    body = content[fm_end:]
    new_content = new_fm_block + body
    result['action'] = 'would_patch' if dry_run else 'patched'
    result['fields_added'] = missing
    result['reason'] = f'补全字段: {", ".join(missing)}'

    if not dry_run:
        md_path.write_text(new_content, encoding='utf-8')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='.agents/ Frontmatter批量补全工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不修改文件')
    parser.add_argument('--file', help='只处理单个文件')
    parser.add_argument('--exclude', action='append', default=[], help='排除子目录名')
    parser.add_argument('--fix-fields', action='store_true', default=True, help='补全已有frontmatter的缺失字段（默认开启）')
    parser.add_argument('--no-fix-fields', action='store_true', help='仅为无frontmatter的文件新增，不补字段')
    args = parser.parse_args(argv)

    fix_fields = args.fix_fields and not args.no_fix_fields
    project_root = resolve_project_root(__file__)
    agents_dir = project_root / '.agents'
    skip_dirs = SKIP_DIRS | set(args.exclude)

    if args.file:
        target = Path(args.file).resolve()
        if not target.exists():
            print(f'file not found: {target}')
            sys.exit(1)
        md_files = [target]
    else:
        md_files = sorted(
            f for f in agents_dir.rglob('*.md')
            if not any(d in skip_dirs for d in f.relative_to(agents_dir).parts)
        )

    mode = 'DRY RUN' if args.dry_run else 'EXECUTE'
    print(f'.agents/ Frontmatter Batch Tool [{mode}]')
    print(f'Project root: {project_root}')
    print(f'Scan dir: .agents/')
    print(f'Files found: {len(md_files)}')
    print(f'Fix missing fields: {fix_fields}')
    print()

    results = []
    for f in md_files:
        r = process_file(f, project_root, dry_run=args.dry_run, fix_fields=fix_fields)
        results.append(r)

    added = [r for r in results if r['action'] in ('added', 'would_add')]
    patched = [r for r in results if r['action'] in ('patched', 'would_patch')]
    skipped = [r for r in results if r['action'] == 'skip']
    errors = [r for r in results if r['action'] == 'error']

    if added:
        print(f'New frontmatter ({len(added)} files):')
        for r in added:
            print(f'  + {r["rel"]}')
    if patched:
        print(f'Patched fields ({len(patched)} files):')
        for r in patched:
            print(f'  ~ {r["rel"]}: {r["reason"]}')
    if skipped:
        print(f'Skipped ({len(skipped)} files):')
        schema_skips = [r for r in skipped if '专用schema' in r.get('reason', '')]
        ok_skips = [r for r in skipped if '专用schema' not in r.get('reason', '')]
        if ok_skips:
            print(f'  Already complete: {len(ok_skips)}')
        if schema_skips:
            print(f'  Schema files (skipped by design): {len(schema_skips)}')
    if errors:
        print(f'Errors ({len(errors)} files):')
        for r in errors:
            print(f'  ! {r["rel"]}: {r["reason"]}')

    print()
    total_changed = len(added) + len(patched)
    print(f'Summary: {total_changed} files to update, {len(skipped)} skipped, {len(errors)} errors')
    if args.dry_run:
        print('Remove --dry-run to execute')

    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
