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
