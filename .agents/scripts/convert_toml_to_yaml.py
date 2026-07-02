#!/usr/bin/env python3
"""Convert TOML frontmatter (+++) to YAML frontmatter (---) in Markdown files."""

import re
import sys
from pathlib import Path


def parse_toml_value(lines, start_idx):
    """Parse a TOML value starting at lines[start_idx], may span multiple lines.
    Returns (key, yaml_value_str, next_line_idx, is_multiline)."""
    line = lines[start_idx].strip()

    if '=' not in line:
        return None, line, start_idx + 1, False

    key_part, _, value_part = line.partition('=')
    value = value_part.strip()
    key = key_part.strip()

    if value.startswith('[') and not value.endswith(']'):
        array_lines = [value]
        idx = start_idx + 1
        bracket_depth = value.count('[') - value.count(']')
        while idx < len(lines) and bracket_depth > 0:
            curr = lines[idx].strip()
            array_lines.append(curr)
            bracket_depth += curr.count('[') - curr.count(']')
            idx += 1
        value = ' '.join(array_lines)
        return key, _toml_array_to_yaml(value, multiline=True), idx, True

    if value.startswith('[') and value.endswith(']'):
        return key, _toml_array_to_yaml(value, multiline=False), start_idx + 1, False

    return key, _toml_scalar_to_yaml(value), start_idx + 1, False


def _toml_scalar_to_yaml(value: str) -> str:
    """Convert a TOML scalar value to YAML."""
    value = value.strip()
    if not value:
        return '""'

    if value.startswith('"') and value.endswith('"'):
        return value
    if value.startswith("'") and value.endswith("'"):
        return '"' + value[1:-1] + '"'

    if value.lower() in ('true', 'false'):
        return value.lower()
    try:
        int(value)
        return value
    except ValueError:
        pass
    try:
        float(value)
        return value
    except ValueError:
        pass

    return f'"{value}"'


def _split_toml_array_items(s: str) -> list[str]:
    """Split TOML array items respecting quotes and nested brackets."""
    s = s.strip()
    if s.startswith('['):
        s = s[1:]
    if s.endswith(']'):
        s = s[:-1]
    s = s.strip()

    if not s:
        return []

    items = []
    current = []
    in_string = False
    string_char = None
    depth = 0

    for c in s:
        if c in ('"', "'") and not in_string:
            in_string = True
            string_char = c
            current.append(c)
        elif c == string_char and in_string:
            in_string = False
            string_char = None
            current.append(c)
        elif c == '[' and not in_string:
            depth += 1
            current.append(c)
        elif c == ']' and not in_string:
            depth -= 1
            current.append(c)
        elif c == ',' and not in_string and depth == 0:
            items.append(''.join(current).strip())
            current = []
        else:
            current.append(c)

    if current:
        items.append(''.join(current).strip())
    return [i for i in items if i]


def _toml_array_to_yaml(value: str, multiline: bool = False) -> str:
    """Convert a TOML array string to YAML."""
    items = _split_toml_array_items(value)
    if not items:
        return "[]"

    yaml_lines = []
    for item in items:
        item = item.strip()
        if item.startswith('"') and item.endswith('"'):
            yaml_lines.append(f"  - {item}")
        elif item.startswith("'") and item.endswith("'"):
            yaml_lines.append(f'  - "{item[1:-1]}"')
        else:
            yaml_lines.append(f"  - {item}")

    return "\n" + "\n".join(yaml_lines)


def convert_frontmatter(content: str) -> str:
    """Convert TOML frontmatter to YAML frontmatter."""
    lines = content.split('\n')

    if not lines or lines[0].strip() != '+++':
        return content

    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '+++':
            end_idx = i
            break

    if end_idx is None:
        return content

    toml_body_lines = lines[1:end_idx]
    yaml_lines = []

    idx = 0
    while idx < len(toml_body_lines):
        line = toml_body_lines[idx].strip()
        if not line or line.startswith('#'):
            idx += 1
            continue

        if '=' not in line:
            idx += 1
            continue

        key, yaml_value, idx, is_multiline = parse_toml_value(toml_body_lines, idx)
        if key is None:
            idx += 1
            continue

        if yaml_value.startswith('\n'):
            yaml_lines.append(f"{key}:{yaml_value}")
        else:
            yaml_lines.append(f"{key}: {yaml_value}")

    new_lines = ['---'] + yaml_lines + ['---'] + lines[end_idx + 1:]
    return '\n'.join(new_lines)


def process_file(filepath: Path, dry_run: bool = False) -> bool:
    """Process a single file. Returns True if converted."""
    content = filepath.read_text(encoding='utf-8')
    new_content = convert_frontmatter(content)

    if new_content == content:
        return False

    if not dry_run:
        filepath.write_text(new_content, encoding='utf-8')
    print(f"{'Would convert' if dry_run else 'Converted'}: {filepath}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_toml_to_yaml.py <file1> [file2 ...]")
        sys.exit(1)

    files = [Path(p) for p in sys.argv[1:]]
    converted = 0

    for f in files:
        if not f.exists():
            print(f"File not found: {f}")
            continue
        if process_file(f, dry_run=False):
            converted += 1

    print(f"\nConverted {converted} files.")


if __name__ == '__main__':
    main()
