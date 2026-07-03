import re
from pathlib import Path

from .constants import LARGE_FILE_THRESHOLD, PATTERN_LINK_RE, NAV_PATTERNS


def check_file_size(content):
    line_count = len(content.split('\n'))
    return line_count > LARGE_FILE_THRESHOLD


def check_nav_and_atomization(content, rel_path):
    chapter_match = re.search(r'/\d{2}-[a-z]', rel_path)
    has_nav = any(p in content for p in NAV_PATTERNS)

    is_atomized = False
    has_nav_links = False
    if chapter_match and has_nav:
        has_nav_links = True
        is_atomized = True

    return has_nav_links, is_atomized


def check_pattern_references(content):
    matches = PATTERN_LINK_RE.findall(content)
    count = len(matches)
    has_refs = count > 0
    return count, has_refs
