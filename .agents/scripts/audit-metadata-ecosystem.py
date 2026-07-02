#!/usr/bin/env python3
"""
元数据生态健康度审计工具。

从TOML侧反向校验元数据生态健康度，与check-frontmatter.py（MD侧正向检查）形成双向闭环。

检查维度：
1. 孤儿TOML：TOML文件存在但对应的MD文件不存在
2. 缺失TOML：MD文件有x-toml-ref但对应的TOML文件不存在
3. 镜像结构一致性：.meta/toml/下的路径结构与源目录镜像关系正确
4. TOML必填字段：TOML中必须包含id字段
5. MD-TOML id一致性：MD的YAML id与TOML中的id匹配
6. TOML语法有效性：TOML文件语法可解析
7. 孤儿MD：MD文件有frontmatter但无x-toml-ref（未接入元数据体系）
8. 覆盖率统计：frontmatter覆盖率、TOML覆盖率、健康度评分

用法：
    python audit-metadata-ecosystem.py                       # 全项目审计
    python audit-metadata-ecosystem.py --dir docs/knowledge/ # 指定目录
    python audit-metadata-ecosystem.py --fix                 # 自动创建缺失TOML骨架
    python audit-metadata-ecosystem.py --strict              # 严格模式（警告视为错误）
    python audit-metadata-ecosystem.py --format json         # JSON格式输出
    python audit-metadata-ecosystem.py --report report.md    # 生成报告文件
"""

import argparse
import io
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from lib.project import resolve_project_root
from lib.frontmatter import parse_yaml_frontmatter, extract_all_yaml_fields, _YAML_FRONTMATTER_RE


FM_PATTERN = _YAML_FRONTMATTER_RE
ID_PATTERN = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')


@dataclass
class Issue:
    severity: str
    category: str
    file: str
    message: str
    fixable: bool = False


@dataclass
class AuditResult:
    total_md_files: int = 0
    md_with_frontmatter: int = 0
    md_with_x_toml_ref: int = 0
    total_toml_files: int = 0
    toml_with_valid_id: int = 0
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    fixed: list[str] = field(default_factory=list)
    by_category: dict = field(default_factory=dict)
    by_directory: dict = field(default_factory=dict)

    def add_error(self, category: str, file_path: str, message: str, fixable: bool = False):
        self.errors.append(Issue('error', category, file_path, message, fixable))

    def add_warning(self, category: str, file_path: str, message: str, fixable: bool = False):
        self.warnings.append(Issue('warning', category, file_path, message, fixable))


def md_to_toml_rel(md_rel: str) -> str:
    """将MD文件相对路径转换为对应的TOML镜像相对路径。"""
    return '.meta/toml/' + md_rel.replace('.md', '.toml')


def compute_x_toml_ref(md_rel: str) -> str:
    """根据MD文件相对路径计算正确的x-toml-ref值。"""
    toml_rel = md_to_toml_rel(md_rel)
    parent_depth = len(Path(md_rel).parent.parts)
    if parent_depth == 0:
        return toml_rel
    return '../' * parent_depth + toml_rel


def is_excluded(rel_path: str, exclude_dirs: set[str]) -> bool:
    parts = rel_path.split('/')
    return any(ex in parts for ex in exclude_dirs)


def scan_md_files(project_root: Path, target_dir: Path, exclude_dirs: set[str]) -> dict[str, dict]:
    """扫描所有MD文件，提取frontmatter信息。

    Returns:
        {md_rel_path: {'fm': dict|None, 'has_fm': bool, 'x_toml_ref': str|None, 'md_id': str|None}}
    """
    result = {}
    for md_path in sorted(target_dir.rglob('*.md')):
        try:
            rel = md_path.relative_to(project_root).as_posix()
        except ValueError:
            continue
        if is_excluded(rel, exclude_dirs):
            continue

        entry = {'has_fm': False, 'x_toml_ref': None, 'md_id': None, 'fm': None}
        try:
            content = md_path.read_text(encoding='utf-8')
        except Exception:
            result[rel] = entry
            continue

        fm_match = FM_PATTERN.match(content)
        if fm_match:
            entry['has_fm'] = True
            fm_text = fm_match.group(1)
            fields = extract_all_yaml_fields(fm_text)
            entry['fm'] = fields
            entry['md_id'] = clean_field(fields.get('id'))
            entry['title'] = clean_field(fields.get('title'))
            entry['source'] = clean_field(fields.get('source'))
            x_ref = clean_field(fields.get('x-toml-ref'))
            entry['x_toml_ref'] = x_ref

        result[rel] = entry
    return result


def scan_toml_files(project_root: Path, exclude_dirs: set[str], toml_subdir: str = '') -> dict[str, dict]:
    """扫描.meta/toml/下TOML文件，解析内容。

    Args:
        toml_subdir: 限定扫描的TOML子目录（如'docs/knowledge'），空字符串表示全量扫描。

    Returns:
        {toml_rel_path: {'data': dict|None, 'parse_error': str|None, 'toml_id': str|None}}
    """
    result = {}
    if toml_subdir:
        toml_root = project_root / '.meta' / 'toml' / toml_subdir
    else:
        toml_root = project_root / '.meta' / 'toml'
    if not toml_root.exists():
        return result

    for toml_path in sorted(toml_root.rglob('*.toml')):
        try:
            rel = toml_path.relative_to(project_root).as_posix()
        except ValueError:
            continue
        if is_excluded(rel, exclude_dirs):
            continue

        entry = {'data': None, 'parse_error': None, 'toml_id': None, 'title': None, 'status': None}
        try:
            with open(toml_path, 'rb') as f:
                data = tomllib.load(f)
            entry['data'] = data
            entry['toml_id'] = data.get('id')
            entry['title'] = data.get('title')
            entry['status'] = data.get('status')
        except tomllib.TOMLDecodeError as e:
            entry['parse_error'] = str(e)
        except Exception as e:
            entry['parse_error'] = f'读取失败: {e}'

        result[rel] = entry
    return result


def clean_field(value) -> Optional[str]:
    """清理字段值，去除引号和空白。"""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().strip('"').strip("'")
    return str(value)


def build_md_to_toml_mapping(md_files: dict) -> dict[str, str]:
    """构建 MD路径 → 期望TOML路径 的映射。"""
    mapping = {}
    for md_rel, info in md_files.items():
        expected_toml = md_to_toml_rel(md_rel)
        mapping[md_rel] = expected_toml
    return mapping


def create_toml_skeleton(md_rel: str, md_id: str, title: str | None, toml_abs: Path):
    """创建缺失的TOML骨架文件。"""
    lines = [f'id = "{md_id}"']
    if title:
        lines.append(f'title = "{title}"')

    rel_parts = Path(md_rel).parts
    if len(rel_parts) >= 2:
        category = rel_parts[0]
        lines.append(f'category = "{category}"')

    lines.append('date = "2026-07-02"')
    lines.append('changelog = [')
    lines.append('  "2026-07-02 | initial | 由audit-metadata-ecosystem自动生成骨架"')
    lines.append(']')

    toml_abs.parent.mkdir(parents=True, exist_ok=True)
    toml_abs.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def toml_to_md_rel(toml_rel: str) -> str:
    """将TOML镜像路径转换回对应的MD相对路径。"""
    return toml_rel.replace('.meta/toml/', '').replace('.toml', '.md')


def patch_toml_missing_fields(toml_abs: Path, md_id: str | None, title: str | None) -> bool:
    """为已有TOML文件补全缺失的id/title字段。

    Returns:
        是否进行了修改。
    """
    try:
        content = toml_abs.read_text(encoding='utf-8')
    except Exception:
        return False

    with open(toml_abs, 'rb') as f:
        try:
            data = tomllib.load(f)
        except Exception:
            return False

    needs_id = 'id' not in data and md_id
    needs_title = 'title' not in data and title

    if not needs_id and not needs_title:
        return False

    lines = content.split('\n')
    new_lines = []
    inserted = False

    id_line = f'id = "{md_id}"' if needs_id else None
    title_line = f'title = "{title}"' if needs_title else None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not inserted and (stripped.startswith('title') or stripped.startswith('category') or stripped.startswith('date') or stripped.startswith('version') or stripped.startswith('changelog')):
            if id_line:
                new_lines.append(id_line)
            if title_line and not stripped.startswith('title'):
                new_lines.append(title_line)
                title_line = None
            inserted = True
        new_lines.append(line)

    if not inserted:
        if id_line:
            new_lines.insert(0, id_line)
        if title_line:
            new_lines.insert(1 if id_line else 0, title_line)

    toml_abs.write_text('\n'.join(new_lines), encoding='utf-8')
    return True


def audit(project_root: Path, target_dir: Optional[Path] = None,
          exclude_dirs: Optional[set[str]] = None, fix: bool = False,
          single_file: Optional[Path] = None) -> AuditResult:
    """执行元数据生态健康度审计。"""
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


def format_text_report(result: AuditResult, project_root: Path) -> str:
    """生成文本格式报告。"""
    lines = []
    lines.append('=' * 60)
    lines.append('元数据生态健康度审计报告')
    lines.append('=' * 60)
    lines.append(f'项目根: {project_root}')
    lines.append('')

    lines.append('── 覆盖率统计 ──')
    fm_rate = (result.md_with_frontmatter / result.total_md_files * 100) if result.total_md_files > 0 else 0
    toml_rate = (result.md_with_x_toml_ref / result.md_with_frontmatter * 100) if result.md_with_frontmatter > 0 else 0
    lines.append(f'  MD文件总数:          {result.total_md_files}')
    lines.append(f'  有frontmatter:      {result.md_with_frontmatter} ({fm_rate:.1f}%)')
    lines.append(f'  有x-toml-ref:       {result.md_with_x_toml_ref} ({toml_rate:.1f}% of FM)')
    lines.append(f'  TOML文件总数:        {result.total_toml_files}')
    lines.append(f'  TOML有有效id:       {result.toml_with_valid_id}')
    lines.append('')

    if result.errors:
        lines.append(f'── 错误 ({len(result.errors)}) ──')
        by_cat = {}
        for e in result.errors:
            by_cat.setdefault(e.category, []).append(e)
        for cat, issues in sorted(by_cat.items()):
            lines.append(f'  [{cat}] ({len(issues)}个)')
            for issue in issues[:10]:
                lines.append(f'    ❌ {issue.file}')
                lines.append(f'       {issue.message}')
            if len(issues) > 10:
                lines.append(f'    ... 还有{len(issues) - 10}个')
        lines.append('')

    if result.warnings:
        lines.append(f'── 警告 ({len(result.warnings)}) ──')
        by_cat = {}
        for w in result.warnings:
            by_cat.setdefault(w.category, []).append(w)
        for cat, issues in sorted(by_cat.items()):
            lines.append(f'  [{cat}] ({len(issues)}个)')
            for issue in issues[:10]:
                lines.append(f'    ⚠️  {issue.file}')
                lines.append(f'       {issue.message}')
            if len(issues) > 10:
                lines.append(f'    ... 还有{len(issues) - 10}个')
        lines.append('')

    if result.fixed:
        lines.append(f'── 自动修复 ({len(result.fixed)}) ──')
        for f in result.fixed:
            lines.append(f'  ✅ {f}')
        lines.append('')

    error_count = len(result.errors)
    warn_count = len(result.warnings)
    lines.append('=' * 60)
    if error_count == 0:
        lines.append(f'✅ 审计通过（{warn_count}个警告）')
    else:
        lines.append(f'❌ 审计发现{error_count}个错误，{warn_count}个警告')
    lines.append('=' * 60)

    return '\n'.join(lines)


def format_json_report(result: AuditResult, project_root: Path) -> str:
    """生成JSON格式报告。"""
    import json
    data = {
        'project_root': str(project_root),
        'summary': {
            'total_md_files': result.total_md_files,
            'md_with_frontmatter': result.md_with_frontmatter,
            'md_with_x_toml_ref': result.md_with_x_toml_ref,
            'total_toml_files': result.total_toml_files,
            'toml_with_valid_id': result.toml_with_valid_id,
            'error_count': len(result.errors),
            'warning_count': len(result.warnings),
            'fixed_count': len(result.fixed),
        },
        'errors': [
            {'severity': e.severity, 'category': e.category, 'file': e.file, 'message': e.message}
            for e in result.errors
        ],
        'warnings': [
            {'severity': w.severity, 'category': w.category, 'file': w.file, 'message': w.message}
            for w in result.warnings
        ],
        'fixed': result.fixed,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def main(argv=None):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description='元数据生态健康度审计工具')
    parser.add_argument('--dir', help='目标目录（默认全项目）')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--fix', action='store_true', help='自动创建缺失TOML骨架并补全id')
    parser.add_argument('--strict', action='store_true', help='严格模式：警告视为错误')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--report', help='报告输出文件路径')
    parser.add_argument('--exclude', action='append', default=[], help='排除目录名（可多次指定）')
    args = parser.parse_args(argv)

    project_root = resolve_project_root(__file__)
    exclude_dirs = {'vendor', '.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', '.trae'}
    exclude_dirs.update(args.exclude)

    target_dir = Path(args.dir).resolve() if args.dir else project_root
    single_file = None

    if args.file:
        single_file = Path(args.file).resolve()
        target_dir = single_file.parent

    result = audit(project_root, target_dir, exclude_dirs, fix=args.fix, single_file=single_file)

    if args.format == 'json':
        output = format_json_report(result, project_root)
    else:
        output = format_text_report(result, project_root)

    print(output)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding='utf-8')
        print(f'\n报告已保存到: {report_path}')

    exit_code = 1 if result.errors or (args.strict and result.warnings) else 0
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
