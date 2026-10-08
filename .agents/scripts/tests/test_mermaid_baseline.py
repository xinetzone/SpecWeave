"""Tests for deterministic Mermaid historical baselines."""

import importlib.util
import subprocess
from pathlib import Path

import pytest

_lib_parent = Path(__file__).resolve().parent.parent
import sys

sys.path.insert(0, str(_lib_parent / "lib"))

from lib.mermaid.baseline import (  # noqa: E402
    _aggregate_findings,
    build_baseline_from_revision,
    collect_diagnostics,
    collect_findings,
    compare_findings,
    prune_baseline,
    write_baseline,
)
from lib.checks import mermaid as mermaid_check
from lib.mermaid.common import MermaidIssue

_repo_check_path = Path(__file__).resolve().parents[1] / "repo-check.py"
_repo_check_spec = importlib.util.spec_from_file_location("repo_check", _repo_check_path)
repo_check = importlib.util.module_from_spec(_repo_check_spec)
_repo_check_spec.loader.exec_module(repo_check)


def test_compare_ignores_line_drift_and_reports_only_excess_occurrences():
    baseline = {
        "schema_version": 1,
        "revision": "abc123",
        "findings": [
            {
                "path": "docs/guide.md",
                "rule_id": "vscode.br_tag",
                "source": 'A["one<br/>two"] --> B',
                "count": 2,
            }
        ],
    }
    current = [
        {
            "path": "docs/guide.md",
            "rule_id": "vscode.br_tag",
            "source": 'A["one<br/>two"] --> B',
            "line": line,
        }
        for line in (40, 90, 120)
    ]

    result = compare_findings(current, baseline)

    assert result["known_count"] == 2
    assert result["new_count"] == 1
    assert result["new_findings"] == [
        {
            "path": "docs/guide.md",
            "rule_id": "vscode.br_tag",
            "source": 'A["one<br/>two"] --> B',
            "line": 120,
        }
    ]
    assert result["resolved_count"] == 0


def test_compare_reports_resolved_historical_occurrences():
    baseline = {
        "schema_version": 1,
        "revision": "abc123",
        "findings": [
            {
                "path": "docs/guide.md",
                "rule_id": "vscode.br_tag",
                "source": 'A["one<br/>two"] --> B',
                "count": 3,
            }
        ],
    }
    current = [
        {
            "path": "docs/guide.md",
            "rule_id": "vscode.br_tag",
            "source": 'A["one<br/>two"] --> B',
            "line": 8,
        }
    ]

    result = compare_findings(current, baseline)

    assert result["known_count"] == 1
    assert result["new_count"] == 0
    assert result["resolved_count"] == 2


def test_prune_baseline_only_removes_or_reduces_existing_findings():
    baseline = {
        "schema_version": 1,
        "revision": "abc123",
        "findings": [
            {
                "path": "docs/guide.md",
                "rule_id": "vscode.br_tag",
                "source": 'A["one<br/>two"] --> B',
                "count": 2,
            },
            {
                "path": "docs/old.md",
                "rule_id": "vscode.br_tag",
                "source": 'C["old<br/>item"] --> D',
                "count": 1,
            },
        ],
    }
    current = [
        {
            "path": "docs/guide.md",
            "rule_id": "vscode.br_tag",
            "source": 'A["one<br/>two"] --> B',
            "line": 8,
        },
        {
            "path": "docs/new.md",
            "rule_id": "vscode.br_tag",
            "source": 'E["new<br/>item"] --> F',
            "line": 3,
        },
    ]

    pruned = prune_baseline(baseline, current)

    assert pruned["findings"] == [
        {
            "path": "docs/guide.md",
            "rule_id": "vscode.br_tag",
            "source": 'A["one<br/>two"] --> B',
            "count": 1,
        }
    ]
    assert pruned["revision"] == "abc123"


def test_rule_id_is_stable_across_dynamic_circled_digits(tmp_path):
    document = tmp_path / "guide.md"
    rule_ids = []
    for circled_digit in ("①", "②"):
        document.write_text(
            "```mermaid\nflowchart TD\n"
            f'    A["step {circled_digit}"] --> B\n'
            "```\n",
            encoding="utf-8",
        )

        findings = collect_findings(tmp_path)
        assert len(findings) == 1
        rule_ids.append(findings[0]["rule_id"])

    assert rule_ids == ["mermaid.vscode.circled_digit"] * 2


def test_baseline_identity_is_stable_across_dynamic_circled_digits(tmp_path):
    document = tmp_path / "guide.md"
    document.write_text(
        '```mermaid\nflowchart TD\n    A["step ①"] --> B\n```\n',
        encoding="utf-8",
    )
    baseline = {
        "schema_version": 1,
        "revision": "abc123",
        "findings": _aggregate_findings(collect_findings(tmp_path)),
    }
    assert baseline["findings"][0]["source"] == 'A["step ①"] --> B'
    assert (
        baseline["findings"][0]["identity_source"]
        == 'A["step <circled-digit>"] --> B'
    )

    document.write_text(
        '```mermaid\nflowchart TD\n    A["step ②"] --> B\n```\n',
        encoding="utf-8",
    )
    current_findings = collect_findings(tmp_path)
    comparison = compare_findings(current_findings, baseline)

    assert current_findings[0]["source"] == 'A["step ②"] --> B'
    assert (
        current_findings[0]["identity_source"]
        == baseline["findings"][0]["identity_source"]
    )
    assert comparison["known_count"] == 1
    assert comparison["new_count"] == 0
    assert comparison["resolved_count"] == 0


def test_diagnostic_wording_change_keeps_baseline_finding_known(
    tmp_path, monkeypatch
):
    document = tmp_path / "guide.md"
    document.write_text(
        '```mermaid\nflowchart TD\n    A["one<br/>two"] --> B\n```\n',
        encoding="utf-8",
    )
    message = ["Original diagnostic wording"]
    monkeypatch.setattr(
        mermaid_check,
        "_process_file",
        lambda *_args, **_kwargs: (
            [
                MermaidIssue(
                    3,
                    "error",
                    message[0],
                    rule_id="mermaid.vscode.br_tag",
                )
            ],
            0,
            [],
        ),
    )

    baseline_findings = collect_findings(tmp_path)
    baseline_message = collect_diagnostics(tmp_path)[0]["message"]
    finding = baseline_findings[0]
    baseline = {
        "schema_version": 1,
        "revision": "abc123",
        "findings": [
            {
                "path": finding["path"],
                "rule_id": finding["rule_id"],
                "source": finding["source"],
                "count": 1,
            }
        ],
    }

    message[0] = "Reworded diagnostic message"
    current_findings = collect_findings(tmp_path)
    current_message = collect_diagnostics(tmp_path)[0]["message"]
    comparison = compare_findings(current_findings, baseline)

    assert baseline_message != current_message
    assert current_findings[0]["rule_id"] == "mermaid.vscode.br_tag"
    assert comparison["known_count"] == 1
    assert comparison["new_count"] == 0


def test_collect_findings_rejects_errors_without_explicit_rule_ids(
    tmp_path, monkeypatch
):
    (tmp_path / "guide.md").write_text("# Doc\n", encoding="utf-8")
    monkeypatch.setattr(
        mermaid_check,
        "_process_file",
        lambda *_args, **_kwargs: ([(1, "error", "unregistered error")], 0, []),
    )

    with pytest.raises(ValueError, match="stable rule_id"):
        collect_findings(tmp_path)


def test_build_baseline_reads_only_the_requested_commit(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Baseline Test")
    _git(tmp_path, "config", "user.email", "baseline@example.invalid")

    tracked = tmp_path / "docs" / "guide.md"
    tracked.parent.mkdir()
    tracked.write_text(
        '```mermaid\nflowchart TD\n    A["old<br/>line"] --> B\n```\n',
        encoding="utf-8",
    )
    _git(tmp_path, "add", "docs/guide.md")
    _git(tmp_path, "commit", "-q", "-m", "baseline")
    revision = _git(tmp_path, "rev-parse", "HEAD").stdout.strip()

    tracked.write_text(
        '```mermaid\nflowchart TD\n    A["worktree<br/>change"] --> B\n```\n',
        encoding="utf-8",
    )
    untracked = tmp_path / "docs" / "new.md"
    untracked.write_text(
        '```mermaid\nflowchart TD\n    C["untracked<br/>line"] --> D\n```\n',
        encoding="utf-8",
    )

    first = build_baseline_from_revision(tmp_path, revision)
    second = build_baseline_from_revision(tmp_path, revision)
    first_path = tmp_path / "first-baseline.json"
    second_path = tmp_path / "second-baseline.json"
    write_baseline(first_path, first)
    write_baseline(second_path, second)

    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first["revision"] == revision
    assert {finding["path"] for finding in first["findings"]} == {"docs/guide.md"}
    assert all("old" in finding["source"] for finding in first["findings"])


def test_create_baseline_cli_writes_the_requested_revision(tmp_path, capsys):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Baseline Test")
    _git(tmp_path, "config", "user.email", "baseline@example.invalid")
    document = tmp_path / "guide.md"
    document.write_text(
        '```mermaid\nflowchart TD\n    A["old<br/>line"] --> B\n```\n',
        encoding="utf-8",
    )
    _git(tmp_path, "add", "guide.md")
    _git(tmp_path, "commit", "-q", "-m", "baseline")
    revision = _git(tmp_path, "rev-parse", "HEAD").stdout.strip()

    output_path = tmp_path / "baseline.json"
    args = repo_check.build_parser().parse_args(
        ["mermaid", "--create-baseline", str(output_path), "--revision", revision]
    )

    result = repo_check.check_mermaid.run(tmp_path, args)

    assert result == 0
    assert load_json(output_path)["revision"] == revision
    assert "创建 Mermaid 基线" in capsys.readouterr().out


def test_repo_check_all_uses_repository_baseline_by_default(tmp_path):
    captured = {}

    class CaptureMermaidArgs:
        @staticmethod
        def run(project_root, args):
            captured["baseline"] = args.baseline
            return 0

    original_checks = repo_check.CHECKS_CI_ORDER
    repo_check.CHECKS_CI_ORDER = [("mermaid", "Mermaid", CaptureMermaidArgs)]
    try:
        repo_check.run_all(tmp_path, repo_check.build_parser().parse_args(["all"]))
    finally:
        repo_check.CHECKS_CI_ORDER = original_checks

    assert captured["baseline"] == str(
        tmp_path / ".agents" / "scripts" / "data" / "mermaid-baseline.json"
    )


def load_json(path: Path):
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
