from pathlib import Path
from collections.abc import Callable, Iterable

from lib.cli import print_summary
from lib.cli import print_pass as cli_print_pass
from lib.cli import print_warn as cli_print_warn
from lib.cli import print_error as cli_print_error


class ResultGroupMixin:
    results: list

    @property
    def errors(self) -> list:
        return [r for r in self.results if r.severity == "error" and not r.passed]

    @property
    def warnings(self) -> list:
        return [r for r in self.results if r.severity == "warn" and not r.passed]

    @property
    def passes(self) -> list:
        return [r for r in self.results if r.passed]


def score_to_ansi(score: int) -> str:
    if score >= 80:
        return "\033[92m"
    if score >= 60:
        return "\033[93m"
    return "\033[91m"


def print_result_lines(
    results: Iterable,
    *,
    verbose: bool,
    print_pass: Callable[[str], None],
    print_warn: Callable[[str], None],
    print_error: Callable[[str], None],
) -> None:
    for r in results:
        if r.passed and not verbose:
            continue
        if r.severity == "error" and not r.passed:
            print_error(f"    [FAIL] {r.name}: {r.message}")
        elif r.severity == "warn" and not r.passed:
            print_warn(f"    [WARN] {r.name}: {r.message}")
        elif verbose and r.passed:
            print_pass(f"    [PASS] {r.name}: {r.message}")


def issue_list(items: Iterable) -> list[dict]:
    return [{"name": res.name, "message": res.message} for res in items]


def safe_relative_to(path: Path, root_dir: Path) -> Path:
    try:
        return path.relative_to(root_dir)
    except Exception:
        return path


def aggregate_stats(reports: list) -> dict:
    total_errors = sum(len(r.errors) for r in reports)
    total_warnings = sum(len(r.warnings) for r in reports)
    total_passes = sum(len(r.passes) for r in reports)
    avg_score = sum(r.score for r in reports) // len(reports) if reports else 0
    return {
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "total_passes": total_passes,
        "avg_score": avg_score,
    }


def build_json_output(
    reports: list,
    root_dir: Path,
    *,
    base_dir_key: str,
    base_dir_value: Path,
    count_key: str,
    items_key: str,
    item_builder: Callable[[object], dict],
) -> dict:
    stats = aggregate_stats(reports)
    return {
        base_dir_key: str(base_dir_value),
        count_key: len(reports),
        items_key: [item_builder(r) for r in reports],
        "average_score": stats["avg_score"],
        "total_errors": stats["total_errors"],
        "total_warnings": stats["total_warnings"],
    }


def common_report_fields(report) -> dict:
    return {
        "score": report.score,
        "errors": issue_list(report.errors),
        "warnings": issue_list(report.warnings),
        "pass_count": len(report.passes),
    }


def print_scored_report(
    *,
    score: int,
    header: str,
    extra_lines: list[str],
    results: Iterable,
    verbose: bool,
    print_pass: Callable[[str], None],
    print_warn: Callable[[str], None],
    print_error: Callable[[str], None],
) -> None:
    score_color = score_to_ansi(score)
    reset = "\033[0m"
    print(f"\n  {score_color}{header}{reset}")
    for line in extra_lines:
        print(line)
    print_result_lines(
        results,
        verbose=verbose,
        print_pass=print_pass,
        print_warn=print_warn,
        print_error=print_error,
    )


def print_scored_report_cli(
    *,
    score: int,
    header: str,
    extra_lines: list[str],
    results: Iterable,
    verbose: bool,
) -> None:
    print_scored_report(
        score=score,
        header=header,
        extra_lines=extra_lines,
        results=results,
        verbose=verbose,
        print_pass=cli_print_pass,
        print_warn=cli_print_warn,
        print_error=cli_print_error,
    )


def print_aggregate_summary(reports: list) -> dict:
    stats = aggregate_stats(reports)
    print()
    print(f"  平均质量分: {stats['avg_score']}/100")
    print_summary(
        pass_count=stats["total_passes"],
        warn_count=stats["total_warnings"],
        error_count=stats["total_errors"],
    )
    return stats
