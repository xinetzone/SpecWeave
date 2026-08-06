# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import pytest
from mdi.parser import MDIParser
from mdi.validator import MDIValidator
from mdi.profiles import GraphQLProfile


@pytest.fixture
def parser():
    return MDIParser()


@pytest.fixture
def validator():
    return MDIValidator()


@pytest.fixture
def graphql_profile():
    return GraphQLProfile()

