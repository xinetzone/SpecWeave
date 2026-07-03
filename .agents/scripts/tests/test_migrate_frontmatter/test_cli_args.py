import pytest

from .conftest import mf


class TestCliArgs:
    def test_help_exits_cleanly(self):
        with pytest.raises(SystemExit) as exc_info:
            parser = mf.build_arg_parser()
            parser.parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_dry_run_flag(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_backup_flag(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--backup"])
        assert args.backup is True

    def test_rollback_flag(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--rollback"])
        assert args.rollback is True

    def test_path_option(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--path", "docs/guide"])
        assert args.path == "docs/guide"

    def test_report_option(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args(["--report", "out.json"])
        assert args.report == "out.json"

    def test_defaults(self):
        parser = mf.build_arg_parser()
        args = parser.parse_args([])
        assert args.dry_run is False
        assert args.backup is False
        assert args.verify is False
        assert args.rollback is False
        assert args.path is None
        assert args.report is None
