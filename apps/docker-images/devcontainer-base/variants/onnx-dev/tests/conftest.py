"""
pytest conftest for onnx-dev variant tests.
Sets up sys.path so that tools/ and examples/ can be imported directly.
"""
import sys
from pathlib import Path

VARIANT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = VARIANT_ROOT / "tools"
EXAMPLES_DIR = VARIANT_ROOT / "examples"
SCRIPTS_DIR = VARIANT_ROOT / "scripts"

for d in (str(TOOLS_DIR), str(EXAMPLES_DIR), str(SCRIPTS_DIR)):
    if d not in sys.path:
        sys.path.insert(0, d)
