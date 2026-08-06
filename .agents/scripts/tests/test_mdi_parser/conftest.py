# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

from pathlib import Path

import pytest

from mdi.parser import MDIParser

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent


@pytest.fixture
def parser():
    return MDIParser()

