import re
from pathlib import Path

from lib.frontmatter import parse_frontmatter_unified
from lib.quality_rules import check_no_file_url

from .check_frontmatter import check_frontmatter
from .check_content import (
    check_sections,
    check_file_length,
    check_why_explanations,
    check_visualization,
    check_cross_references,
)
from .models import CheckResult, PatternReport
from .scoring import calculate_score


def check_pattern(pattern_md, root):
    content = pattern_md.read_text(encoding="utf-8")
    fields = parse_frontmatter_unified(pattern_md)

    pattern_id = str(fields.get("id", pattern_md.stem)) if fields else pattern_md.stem

    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    pattern_title = title_match.group(1).strip() if title_match else pattern_md.stem

    report = PatternReport(
        pattern_path=pattern_md,
        pattern_id=pattern_id,
        pattern_title=pattern_title
    )

    report.results.extend(check_frontmatter(pattern_md, content, fields))
    report.results.extend(check_sections(content))
    report.results.extend(check_file_length(pattern_md, content))
    report.results.extend(check_why_explanations(content))
    report.results.extend(check_visualization(content))
    report.results.extend(check_no_file_url(content, lambda **kw: CheckResult(**kw)))
    report.results.extend(check_cross_references(content))

    report.score = calculate_score(report)
    return report
