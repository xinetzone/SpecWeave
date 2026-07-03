import re

from lib.frontmatter import extract_all_yaml_fields

from .constants import FORBIDDEN_EXTERNAL_FIELDS


def check_frontmatter(fm_text):
    issues = {
        'missing_id': 0,
        'missing_xref': 0,
        'has_forbidden_fields': 0,
        'has_nested': 0,
        'bloated_fm': 0,
    }

    fields = extract_all_yaml_fields(fm_text)
    has_source = 'source' in fields

    if 'id' not in fields:
        issues['missing_id'] += 1
    if 'x-toml-ref' not in fields:
        issues['missing_xref'] += 1

    forbidden = [f for f in FORBIDDEN_EXTERNAL_FIELDS if f in fields]
    if forbidden:
        issues['has_forbidden_fields'] += 1

    has_problematic_nesting = False
    in_forbidden_field = False
    for line in fm_text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if re.match(r'^\S', line):
            key = stripped.split(':')[0].strip()
            in_forbidden_field = key in FORBIDDEN_EXTERNAL_FIELDS
        elif re.match(r'^\s{2,}\S', line) and in_forbidden_field:
            has_problematic_nesting = True
            break
    if has_problematic_nesting:
        issues['has_nested'] += 1

    fm_line_count = len(fm_text.strip().split('\n'))
    if fm_line_count > 15:
        issues['bloated_fm'] += 1

    is_compliant = all(count == 0 for count in issues.values())
    return issues, is_compliant, has_source


def init_fm_issues():
    return {
        'missing_id': 0,
        'missing_xref': 0,
        'has_forbidden_fields': 0,
        'has_nested': 0,
        'bloated_fm': 0,
    }
