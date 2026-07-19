import pytest
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).parent.parent))
from docgen import cmd_weekly, _weekly_collect, _weekly_count_test_commits, resolve_project_root


class TestWeeklyCollect:
    def test_weekly_collect_returns_dict_with_required_fields(self, tmp_path):
        """_weekly_collect 返回包含必要字段的 dict"""
        stats = _weekly_collect(tmp_path, days=7)
        assert isinstance(stats, dict)
        assert "commit_count_total" in stats
        assert "commit_count_week" in stats
        assert "commits_by_type" in stats
        assert "test_commit_count" in stats
        assert "test_commit_ratio" in stats
        assert "period_days" in stats
        assert "period_start" in stats
        assert "period_end" in stats

    def test_test_commit_count_zero_for_non_git_dir(self, tmp_path):
        """非 git 目录返回 0"""
        count = _weekly_count_test_commits(tmp_path, days=7)
        assert count == 0

    def test_commits_by_type_has_all_categories(self, tmp_path):
        """commits_by_type 包含所有类型键"""
        stats = _weekly_collect(tmp_path, days=7)
        for t in ["feat", "fix", "refactor", "docs", "test", "chore", "other"]:
            assert t in stats["commits_by_type"]

    def test_cmd_weekly_returns_zero_and_prints_summary(self, tmp_path, capsys):
        """cmd_weekly 返回退出码 0 并输出周统计"""
        import argparse
        args = argparse.Namespace(path=tmp_path, days=7)
        rc = cmd_weekly(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "周迭代数据摘要" in out or "Weekly" in out or "本周" in out
