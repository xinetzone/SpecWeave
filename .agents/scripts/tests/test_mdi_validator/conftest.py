import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.validator import MDIValidator
from mdi.parser import MDIParser


@pytest.fixture
def validator():
    return MDIValidator()


@pytest.fixture
def parser():
    return MDIParser()
