import re
import tomllib
from pathlib import Path
from typing import Optional

ID_PATTERN = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')


def escape_toml_string(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', '\\"')


def md_to_toml_rel(md_rel: str) -> str:
    return '.meta/toml/' + md_rel.replace('.md', '.toml')


def compute_x_toml_ref(md_rel: str) -> str:
    toml_rel = md_to_toml_rel(md_rel)
    parent_depth = len(Path(md_rel).parent.parts)
    if parent_depth == 0:
        return toml_rel
    return '../' * parent_depth + toml_rel


def is_excluded(rel_path: str, exclude_dirs: set[str]) -> bool:
    parts = rel_path.split('/')
    return any(ex in parts for ex in exclude_dirs)


def clean_field(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().strip('"').strip("'")
    return str(value)


def build_md_to_toml_mapping(md_files: dict) -> dict[str, str]:
    mapping = {}
    for md_rel, info in md_files.items():
        expected_toml = md_to_toml_rel(md_rel)
        mapping[md_rel] = expected_toml
    return mapping


def toml_to_md_rel(toml_rel: str) -> str:
    return toml_rel.replace('.meta/toml/', '').replace('.toml', '.md')


def create_toml_skeleton(md_rel: str, md_id: str, title: str | None, toml_abs: Path):
    lines = [f'id = "{escape_toml_string(md_id)}"']
    if title:
        lines.append(f'title = "{escape_toml_string(title)}"')

    rel_parts = Path(md_rel).parts
    if len(rel_parts) >= 2:
        category = rel_parts[0]
        lines.append(f'category = "{escape_toml_string(category)}"')

    lines.append('date = "2026-07-02"')
    lines.append('changelog = [')
    lines.append('  "2026-07-02 | initial | 由audit-metadata-ecosystem自动生成骨架"')
    lines.append(']')

    toml_abs.parent.mkdir(parents=True, exist_ok=True)
    toml_abs.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def patch_toml_missing_fields(toml_abs: Path, md_id: str | None, title: str | None) -> bool:
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

    id_line = f'id = "{escape_toml_string(md_id)}"' if needs_id else None
    title_line = f'title = "{escape_toml_string(title)}"' if needs_title else None

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
