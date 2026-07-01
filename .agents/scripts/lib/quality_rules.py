import re


FILE_URL_PATTERN = re.compile(r"(?:\[[^\]]*\]\(|<)file:///[^)\s>]+(?:\)|>)", re.MULTILINE)


def count_file_urls(content: str) -> int:
    return len(FILE_URL_PATTERN.findall(content))


def check_no_file_url(content: str, make_result) -> list:
    file_url_count = count_file_urls(content)
    has_file_url = file_url_count > 0
    return [
        make_result(
            name="paths.no_file_url",
            passed=not has_file_url,
            severity="error",
            message="无file:///绝对路径"
            if not has_file_url
            else f"发现{file_url_count}处file:///绝对路径（应使用相对路径）",
        )
    ]
