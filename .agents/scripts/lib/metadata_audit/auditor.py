from pathlib import Path
from typing import Optional

from .models import AuditResult
from .scanner import scan_md_files, scan_toml_files
from .utils import (
    build_md_to_toml_mapping, compute_x_toml_ref,
    create_toml_skeleton, md_to_toml_rel, patch_toml_missing_fields, toml_to_md_rel
)


def audit(project_root: Path, target_dir: Optional[Path] = None,
          exclude_dirs: Optional[set[str]] = None, fix: bool = False,
          single_file: Optional[Path] = None) -> AuditResult:
    if exclude_dirs is None:
        exclude_dirs = {'vendor', '.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv'}
    if target_dir is None:
        target_dir = project_root

    result = AuditResult()

    md_files = scan_md_files(project_root, target_dir, exclude_dirs)

    if target_dir == project_root:
        toml_subdir = ''
    else:
        try:
            toml_subdir = target_dir.relative_to(project_root).as_posix()
        except ValueError:
            toml_subdir = ''

    toml_files = scan_toml_files(project_root, exclude_dirs, toml_subdir)
    md_to_expected_toml = build_md_to_toml_mapping(md_files)

    referenced_tomls = set()
    toml_to_md_info = {}

    for md_rel, info in md_files.items():
        result.total_md_files += 1
        dir_key = str(Path(md_rel).parent)

        if info['has_fm']:
            result.md_with_frontmatter += 1
        else:
            continue

        x_ref = info['x_toml_ref']
        if x_ref:
            result.md_with_x_toml_ref += 1
            md_path = project_root / md_rel
            toml_abs_from_ref = (md_path.parent / x_ref).resolve()
            try:
                toml_rel_from_ref = toml_abs_from_ref.relative_to(project_root).as_posix()
            except ValueError:
                result.add_error('toml-ref-outside-project', md_rel,
                               f'x-toml-ref指向项目外: {x_ref}')
                continue

            referenced_tomls.add(toml_rel_from_ref)
            toml_to_md_info[toml_rel_from_ref] = info
            expected_toml = md_to_expected_toml[md_rel]

            if toml_rel_from_ref != expected_toml:
                result.add_error('mirror-path-mismatch', md_rel,
                               f'x-toml-ref路径不符合镜像规则: 当前="{x_ref}", 期望="{compute_x_toml_ref(md_rel)}"',
                               fixable=True)

            if toml_rel_from_ref not in toml_files:
                if fix:
                    toml_abs = project_root / expected_toml
                    md_id = info['md_id'] or Path(md_rel).stem
                    title = info.get('title')
                    create_toml_skeleton(md_rel, md_id, title, toml_abs)
                    result.fixed.append(f'{md_rel}: 创建TOML骨架 {expected_toml}')
                    toml_files[expected_toml] = {
                        'data': {'id': md_id}, 'parse_error': None,
                        'toml_id': md_id, 'title': title, 'status': None
                    }
                    toml_to_md_info[expected_toml] = info
                else:
                    result.add_error('missing-toml', md_rel,
                                   f'x-toml-ref指向的TOML不存在: {toml_rel_from_ref}',
                                   fixable=True)
            else:
                toml_info = toml_files[toml_rel_from_ref]
                if toml_info['parse_error']:
                    result.add_error('toml-syntax', toml_rel_from_ref,
                                   f'TOML语法错误: {toml_info["parse_error"]}')
                else:
                    result.toml_with_valid_id += 1
                    toml_id = toml_info['toml_id']
                    md_id = info['md_id']
                    if md_id and toml_id and md_id != toml_id:
                        result.add_error('id-mismatch', md_rel,
                                       f'MD的id("{md_id}")与TOML的id("{toml_id}")不一致')
                    if not toml_id:
                        if fix:
                            toml_abs = project_root / toml_rel_from_ref
                            if patch_toml_missing_fields(toml_abs, md_id, info.get('title')):
                                result.fixed.append(f'{toml_rel_from_ref}: 补全缺失的id字段(从MD同步)')
                                toml_files[toml_rel_from_ref]['toml_id'] = md_id
                                toml_files[toml_rel_from_ref]['data'] = {'id': md_id}
                            else:
                                result.add_error('toml-missing-id', toml_rel_from_ref,
                                               'TOML文件缺少必填字段id', fixable=True)
                        else:
                            result.add_error('toml-missing-id', toml_rel_from_ref,
                                           'TOML文件缺少必填字段id', fixable=True)
        else:
            is_index = md_rel.endswith('/README.md') or md_rel == 'README.md'
            is_dotfile = any(p.startswith('.') for p in Path(md_rel).parts if p != '..')
            if not is_index and not is_dotfile and '/templates/' not in md_rel and '.agents/' not in md_rel.split('/')[0]:
                pass

    for toml_rel, toml_info in toml_files.items():
        result.total_toml_files += 1
        if toml_rel not in referenced_tomls:
            expected_md = toml_to_md_rel(toml_rel)
            md_path = project_root / expected_md
            if not md_path.exists():
                result.add_warning('orphan-toml', toml_rel,
                                 f'孤儿TOML（无对应MD文件）: 期望MD="{expected_md}"')
            else:
                if fix and toml_info.get('data') is not None and not toml_info.get('toml_id'):
                    md_rel = expected_md
                    if md_rel in md_files and md_files[md_rel].get('md_id'):
                        md_info = md_files[md_rel]
                        toml_abs = project_root / toml_rel
                        if patch_toml_missing_fields(toml_abs, md_info['md_id'], md_info.get('title')):
                            result.fixed.append(f'{toml_rel}: 补全缺失的id字段(从MD同步)')
                            toml_info['toml_id'] = md_info['md_id']
                            continue

        if toml_info['parse_error'] and toml_rel not in {e.file for e in result.errors if e.category == 'toml-syntax'}:
            result.add_error('toml-syntax', toml_rel,
                           f'TOML语法错误: {toml_info["parse_error"]}')
        elif toml_info['data'] and not toml_info['toml_id']:
            if not any(e.file == toml_rel and e.category == 'toml-missing-id' for e in result.errors):
                result.add_error('toml-missing-id', toml_rel, 'TOML文件缺少必填字段id', fixable=True)

    if single_file:
        try:
            single_rel = single_file.relative_to(project_root).as_posix()
        except ValueError:
            single_rel = str(single_file)
        result.errors = [e for e in result.errors if e.file == single_rel or
                        (e.file.startswith('.meta/toml/') and e.file == md_to_toml_rel(single_rel))]
        result.warnings = [w for w in result.warnings if w.file == single_rel or
                          (w.file.startswith('.meta/toml/') and w.file == md_to_toml_rel(single_rel))]

    return result
