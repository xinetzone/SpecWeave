from pathlib import Path

import pytest

from mdi.parser import MDIParser

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent


@pytest.fixture
def parser():
    return MDIParser()
