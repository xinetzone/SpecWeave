# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

from lib.process import cmdline_matches


def test_cmdline_matches_all_required() -> None:
    assert cmdline_matches("python tos.py monitor -p COM3", ["tos.py", "monitor"]) is True


def test_cmdline_matches_missing_keyword() -> None:
    assert cmdline_matches("python tos.py build", ["monitor"]) is False


