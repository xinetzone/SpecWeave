import tomllib
from pathlib import Path

from lib.frontmatter import extract_all_yaml_fields, _YAML_FRONTMATTER_RE

from .utils import is_excluded, clean_field

FM_PATTERN = _YAML_FRONTMATTER_RE


def scan_md_files(project_root: Path, target_dir: Path, exclude_dirs: set[str]) -> dict[str, dict]:
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
