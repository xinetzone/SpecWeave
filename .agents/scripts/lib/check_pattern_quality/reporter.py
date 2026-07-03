from pathlib import Path

from lib.quality_report import (
    safe_relative_to,
    print_scored_report_cli,
)


def print_pattern_report(report, root_dir, verbose=False):
    rel_path = safe_relative_to(report.pattern_path, root_dir)
    print_scored_report_cli(
        score=report.score,
        header=f"【{report.pattern_id}】{report.score}分 {report.pattern_title[:40]}",
        extra_lines=[f"     ({rel_path})"],
        results=report.results,
        verbose=verbose,
    )
