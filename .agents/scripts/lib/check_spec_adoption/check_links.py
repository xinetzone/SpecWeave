from pathlib import Path

from lib.markdown import parse_inline_links

from .constants import FENCED_CODE_BLOCK_RE, INLINE_CODE_RE, PLACEHOLDER_RE


def check_links(content, fpath):
    content_no_code = FENCED_CODE_BLOCK_RE.sub('', content)
    content_no_code = INLINE_CODE_RE.sub('', content_no_code)

    links = parse_inline_links(content_no_code)
    local_links = []
    for text, url in links:
        if url.startswith(('http://', 'https://', 'file:///', '#')) or url.startswith('mailto:'):
            continue
        if PLACEHOLDER_RE.search(url):
            continue
        clean_url = url.split('#')[0].split('?')[0].strip()
        if not clean_url:
            continue
        local_links.append((text, clean_url))

    links_total = len(local_links)
    links_valid = 0
    links_broken = 0

    for text, clean_url in local_links:
        target = (fpath.parent / clean_url).resolve()
        if target.is_dir():
            has_content = any(p.is_file() for p in target.iterdir())
            if has_content:
                links_valid += 1
            else:
                links_broken += 1
        elif target.exists():
            links_valid += 1
        else:
            links_broken += 1

    return links_total, links_valid, links_broken
