"""Deterministic historical baselines for Mermaid findings."""

import json
import subprocess
import tarfile
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


BASELINE_SCHEMA_VERSION = 1


def collect_findings(root: Path, exclude_dirs: set[str] | None = None) -> list[dict[str, Any]]:
    """Collect blocking Mermaid findings with stable source-based identities."""
    return [
        {key: value for key, value in diagnostic.items() if key != "level"}
        for diagnostic in collect_diagnostics(root, exclude_dirs)
        if diagnostic["level"] == "error"
    ]


def collect_diagnostics(
    root: Path,
    exclude_dirs: set[str] | None = None,
    files: Iterable[Path] | None = None,
    identity_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Collect errors and warnings with stable source-based identities."""
    from lib.checks.mermaid import (
        CIRCLED_NUMBERS_RE,
        _find_md_files,
        _process_file,
    )
    from lib.mermaid.common import strip_inline_comment

    root = Path(root).resolve()
    identity_root = Path(identity_root).resolve() if identity_root else root
    diagnostics = []
    md_files = _find_md_files(root, exclude_dirs or set()) if files is None else files
    for md_file in sorted(md_files):
        issues, _, _ = _process_file(md_file, root, fix=False, dry_run=False)
        lines = md_file.read_text(encoding="utf-8").splitlines()
        relative_path = md_file.relative_to(identity_root).as_posix()
        for issue in issues:
            line_number, level, message = issue
            rule_id = getattr(issue, "rule_id", None)
            if level == "error" and not rule_id:
                raise ValueError(
                    f"{relative_path}:L{line_number} error diagnostic is missing "
                    "a stable rule_id"
                )
            if not rule_id:
                rule_id = "mermaid.warning"
            source_line = lines[line_number - 1] if line_number <= len(lines) else ""
            source = " ".join(strip_inline_comment(source_line).split())
            if not source:
                source = source_line.strip()
            diagnostic = {
                "path": relative_path,
                "rule_id": rule_id,
                "source": source,
                "line": line_number,
                "level": level,
                "message": message,
            }
            if rule_id == "mermaid.vscode.circled_digit":
                identity_source = CIRCLED_NUMBERS_RE.sub(
                    "<circled-digit>", source
                )
                if identity_source != source:
                    diagnostic["identity_source"] = identity_source
            diagnostics.append(diagnostic)
    return sorted(diagnostics, key=_finding_sort_key)


def build_baseline_from_revision(
    project_root: Path,
    revision: str,
    exclude_dirs: set[str] | None = None,
) -> dict[str, Any]:
    """Build a baseline from Markdown files committed at a Git revision."""
    project_root = Path(project_root).resolve()
    resolved_revision = _resolve_commit(project_root, revision)

    with tempfile.TemporaryDirectory(prefix="mermaid-baseline-") as temporary:
        temporary_root = Path(temporary)
        archive_path = temporary_root / "revision.tar"
        result = subprocess.run(
            [
                "git",
                "archive",
                "--format=tar",
                f"--output={archive_path}",
                resolved_revision,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            raise ValueError(
                f"无法归档 Git 提交 {resolved_revision}: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )

        with tarfile.open(archive_path, mode="r:") as archive:
            for member in archive:
                relative = PurePosixPath(member.name)
                if (
                    not member.isfile()
                    or relative.is_absolute()
                    or ".." in relative.parts
                    or relative.suffix.lower() != ".md"
                ):
                    continue
                source = archive.extractfile(member)
                if source is None:
                    continue
                destination = temporary_root.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read())

        findings = collect_findings(temporary_root, exclude_dirs)

    return {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "revision": resolved_revision,
        "findings": _aggregate_findings(findings),
    }


def compare_findings(
    current_findings: Iterable[dict[str, Any]],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Compare current findings to a baseline without relying on line numbers."""
    current = sorted(current_findings, key=_finding_sort_key)
    baseline_counts = Counter()
    for item in baseline.get("findings", []):
        baseline_counts[_identity(item)] += int(item["count"])

    current_counts = Counter(_identity(item) for item in current)
    seen = Counter()
    new_findings = []
    for finding in current:
        identity = _identity(finding)
        seen[identity] += 1
        if seen[identity] > baseline_counts[identity]:
            new_findings.append(finding)

    known_count = sum(
        min(count, baseline_counts[identity])
        for identity, count in current_counts.items()
    )
    resolved_count = sum(
        max(0, count - current_counts[identity])
        for identity, count in baseline_counts.items()
    )
    return {
        "known_count": known_count,
        "new_count": len(new_findings),
        "new_findings": new_findings,
        "resolved_count": resolved_count,
    }


def prune_baseline(
    baseline: dict[str, Any],
    current_findings: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Remove resolved baseline entries and reduce counts; never add exemptions."""
    current_counts = Counter(_identity(item) for item in current_findings)
    pruned = dict(baseline)
    pruned["findings"] = []
    for item in baseline.get("findings", []):
        count = min(int(item["count"]), current_counts[_identity(item)])
        if count:
            entry = {key: value for key, value in item.items() if key != "count"}
            entry["count"] = count
            pruned["findings"].append(entry)
    pruned["findings"].sort(key=_finding_sort_key)
    return pruned


def load_baseline(path: Path) -> dict[str, Any]:
    """Load and validate a versioned Mermaid baseline."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 Mermaid 基线 {path}: {exc}") from exc
    if data.get("schema_version") != BASELINE_SCHEMA_VERSION:
        raise ValueError(
            f"不支持的 Mermaid 基线 schema_version: {data.get('schema_version')!r}"
        )
    if not isinstance(data.get("findings"), list):
        raise ValueError("Mermaid 基线缺少 findings 数组")
    for item in data["findings"]:
        if (
            not isinstance(item, dict)
            or not all(key in item for key in ("path", "rule_id", "source", "count"))
            or not isinstance(item["count"], int)
            or item["count"] < 1
        ):
            raise ValueError("Mermaid 基线包含无效 finding")
    return data


def write_baseline(path: Path, baseline: dict[str, Any]) -> None:
    """Write a deterministic UTF-8 baseline file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _resolve_commit(project_root: Path, revision: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(f"无效的 Git 提交引用 {revision!r}: {result.stderr.strip()}")
    return result.stdout.strip()


def _identity(finding: dict[str, Any]) -> tuple[str, str, str]:
    return (
        finding["path"],
        finding["rule_id"],
        finding.get("identity_source", finding["source"]),
    )


def _finding_sort_key(
    finding: dict[str, Any]
) -> tuple[str, str, str, str, int]:
    return (
        finding["path"],
        finding["rule_id"],
        finding.get("identity_source", finding["source"]),
        finding["source"],
        int(finding.get("line", 0)),
    )


def _aggregate_findings(findings: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter()
    representatives = {}
    for item in sorted(findings, key=_finding_sort_key):
        identity = _identity(item)
        counts[identity] += 1
        representatives.setdefault(identity, item)

    aggregated = []
    for identity, count in counts.items():
        representative = representatives[identity]
        finding = {
            "path": identity[0],
            "rule_id": identity[1],
            "source": representative["source"],
            "count": count,
        }
        if "identity_source" in representative:
            finding["identity_source"] = representative["identity_source"]
        aggregated.append(finding)
    return sorted(aggregated, key=_finding_sort_key)
