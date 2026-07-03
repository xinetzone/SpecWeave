import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent

_spec = importlib.util.spec_from_file_location(
    "migrate_frontmatter", SCRIPTS_DIR / "migrate-frontmatter.py"
)
mf = importlib.util.module_from_spec(_spec)
sys.modules["migrate_frontmatter"] = mf
_spec.loader.exec_module(mf)


@pytest.fixture
def migrate_frontmatter():
    return mf


def create_toml_md(
    path: Path,
    fields: dict[str, str],
    body: str = "# Test\n\nBody content.\n",
) -> None:
    lines = ["+++"]
    for k, v in fields.items():
        lines.append(f'{k} = "{v}"')
    lines.append("+++")
    lines.append("")
    lines.append(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def create_yaml_md(
    path: Path,
    fields: dict[str, str],
    body: str = "# Test\n\nBody content.\n",
    has_toml_ref: bool = False,
) -> None:
    lines = ["---"]
    for k, v in fields.items():
        lines.append(f'{k}: "{v}"')
    lines.append("---")
    lines.append("")
    lines.append(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
