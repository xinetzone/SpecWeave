import pytest
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from docgen import (
    cmd_stats, _stats_validate_with_snapshot, _stats_load_snapshot,
    _stats_save_snapshot, ProjectStats, GitCodeStats, STATS_ANOMALY_FIELDS,
)


def _make_stats(**overrides):
    defaults = dict(
        commit_count=1000, pattern_count=400, script_count=300,
        skill_count=18, rule_count=100, command_count=12,
        role_count=7, core_entry_count=22, last_updated="2026-07-19",
        gitcode=GitCodeStats(stars=0, forks=0, issues=0, prs=0, fetched=False),
    )
    defaults.update(overrides)
    return ProjectStats(**defaults)


def _setup_minimal_project(project_root):
    (project_root / ".agents" / "scripts").mkdir(parents=True)
    (project_root / ".agents" / "skills").mkdir(parents=True)
    (project_root / ".agents" / "rules").mkdir(parents=True)
    (project_root / ".agents" / "commands").mkdir(parents=True)
    (project_root / ".agents" / "roles").mkdir(parents=True)
    (project_root / ".agents" / "docs" / "retrospective" / "patterns").mkdir(parents=True)

    import subprocess
    subprocess.run(["git", "init"], cwd=project_root, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t***@test.com"], cwd=project_root, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, capture_output=True)
    readme = project_root / "README.md"
    readme.write_text("# Test", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=project_root, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project_root, capture_output=True)


class TestStatsValidateWithSnapshot:
    def test_no_snapshot_returns_empty_warnings(self, tmp_path):
        stats = _make_stats()
        snapshot_path = tmp_path / ".stats-cache.json"
        warnings = _stats_validate_with_snapshot(stats, snapshot_path)
        assert warnings == []

    def test_normal_growth_returns_empty_warnings(self, tmp_path):
        snapshot_path = tmp_path / ".stats-cache.json"
        old = _make_stats(commit_count=800, pattern_count=300)
        _stats_save_snapshot(old, snapshot_path)
        new = _make_stats(commit_count=1000, pattern_count=400)
        warnings = _stats_validate_with_snapshot(new, snapshot_path)
        assert warnings == []

    def test_detects_50pct_drop(self, tmp_path, capsys):
        snapshot_path = tmp_path / ".stats-cache.json"
        old = _make_stats(commit_count=1000, pattern_count=400, script_count=300)
        _stats_save_snapshot(old, snapshot_path)
        new = _make_stats(commit_count=1000, pattern_count=100, script_count=300)
        warnings = _stats_validate_with_snapshot(new, snapshot_path)
        assert len(warnings) >= 1
        assert any("pattern_count" in w for w in warnings)

    def test_returns_list_of_warning_strings(self, tmp_path):
        snapshot_path = tmp_path / ".stats-cache.json"
        old = _make_stats(pattern_count=400)
        _stats_save_snapshot(old, snapshot_path)
        new = _make_stats(pattern_count=100)
        warnings = _stats_validate_with_snapshot(new, snapshot_path)
        assert isinstance(warnings, list)
        for w in warnings:
            assert isinstance(w, str)


class TestCmdStatsStrictAnomaly:
    def test_strict_mode_with_anomaly_returns_2(self, tmp_path, capsys):
        project_root = tmp_path
        _setup_minimal_project(project_root)

        snapshot_path = project_root / ".agents" / ".stats-cache.json"
        old_stats = _make_stats(pattern_count=400)
        _stats_save_snapshot(old_stats, snapshot_path)

        args = argparse.Namespace(path=project_root, strict_anomaly=True)
        rc = cmd_stats(args)
        assert rc == 2

    def test_strict_mode_without_anomaly_returns_0(self, tmp_path, capsys):
        project_root = tmp_path
        _setup_minimal_project(project_root)

        args = argparse.Namespace(path=project_root, strict_anomaly=True)
        rc = cmd_stats(args)
        assert rc == 0

    def test_normal_mode_returns_0_even_with_anomaly(self, tmp_path, capsys):
        project_root = tmp_path
        _setup_minimal_project(project_root)

        snapshot_path = project_root / ".agents" / ".stats-cache.json"
        old_stats = _make_stats(pattern_count=400)
        _stats_save_snapshot(old_stats, snapshot_path)

        args = argparse.Namespace(path=project_root, strict_anomaly=False)
        rc = cmd_stats(args)
        assert rc == 0
