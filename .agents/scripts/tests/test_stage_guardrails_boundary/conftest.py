import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest

from lib.stage_guardrails.boundary import (
    BoundaryChecker,
    BoundaryResult,
    OperationType,
    STAGE_EXIT_CRITERIA,
    OPERATION_CATEGORIES,
    _STAGE_PERMISSIONS,
)
from lib.stage_guardrails.state import STAGE_ORDER, STAGE_NAMES, VALID_ROLES, STAGE_ROLES


@pytest.fixture
def checker():
    return BoundaryChecker()
