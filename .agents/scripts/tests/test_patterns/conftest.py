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

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent


def _write_pattern(base: Path, domain_dir: str, filename: str, fm_lines: list[str], body: str = "# Pattern\n") -> Path:
    d = base / domain_dir
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    fm = "\n".join(fm_lines)
    p.write_text(f"+++\n{fm}\n+++\n\n{body}", encoding="utf-8")
    return p


def _complete_fm(**overrides) -> list[str]:
    defaults = {
        "id": "test-pattern",
        "domain": "test",
        "layer": "cognition",
        "maturity": "L1",
        "validation_count": "1",
        "reuse_count": "0",
        "documentation_level": "complete",
        "source": "test.md",
    }
    defaults.update(overrides)
    return [f'{k} = "{v}"' if k not in ("validation_count", "reuse_count") else f"{k} = {v}" for k, v in defaults.items()]

