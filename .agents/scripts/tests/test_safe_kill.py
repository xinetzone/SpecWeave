from lib.process import cmdline_matches


def test_cmdline_matches_all_required() -> None:
    assert cmdline_matches("python tos.py monitor -p COM3", ["tos.py", "monitor"]) is True


def test_cmdline_matches_missing_keyword() -> None:
    assert cmdline_matches("python tos.py build", ["monitor"]) is False

