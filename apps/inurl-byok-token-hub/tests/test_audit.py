"""静态审计测试（TR-1.4）：构建后端、依赖白名单、Secret 字面量与路径规范。

故意写入 setuptools 后端、``from __future__`` 导入或令牌字面量时，本文件应转红。
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"

#: 允许出现在白名单中的第三方依赖
ALLOWED_DEPS = {
    "fastapi",
    "uvicorn",
    "httpx",
    "typer",
    "pyyaml",
    "pydantic",
    "cryptography",
    "jinja2",
    "pytest",
    "pytest-cov",
    "ruff",
}

#: 令牌/密钥字面量：前缀后跟 12 位以上主体（常量定义本身不算）
TOKEN_LITERAL = re.compile(r"byok_(?:live|rec)_[A-Za-z0-9_\-]{12,}")
KEY_LITERAL = re.compile(r"\bsk-(?:live|proj|ant|or)-[A-Za-z0-9]{12,}")


def _py_files(*roots: Path):
    for root in roots:
        yield from sorted(root.rglob("*.py"))


def test_build_backend_is_scikit_build_core():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "scikit_build_core.build" in text
    assert "setuptools.build_meta" not in text


FUTURE_IMPORT = re.compile(r"^\s*from __future__\s+import", re.MULTILINE)


def test_no_future_annotations():
    offenders = [
        str(p)
        for p in _py_files(SRC, TESTS)
        if p.name != "test_audit.py" and FUTURE_IMPORT.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, f"Python 3.14 默认 PEP 649，禁止 __future__ 导入：{offenders}"


def test_no_secret_literals_in_source():
    offenders = []
    for path in _py_files(SRC, TESTS):
        text = path.read_text(encoding="utf-8")
        if TOKEN_LITERAL.search(text) or KEY_LITERAL.search(text):
            offenders.append(str(path))
    assert not offenders, f"源码/测试中不得出现令牌或密钥字面量：{offenders}"


def test_no_file_url_in_docs_and_source():
    offenders = []
    for path in list(_py_files(SRC)) + [ROOT / "README.md"]:
        if not path.exists():
            continue
        if "file:///" in path.read_text(encoding="utf-8"):
            offenders.append(str(path))
    assert not offenders, f"禁止使用 file:/// 绝对路径：{offenders}"


def test_gitignore_covers_runtime_data():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/runtime/" in text or "runtime/" in text
    assert "*.egg-info/" in text


def test_no_cmake_lists():
    assert not list(ROOT.rglob("CMakeLists.txt")), "纯 Python 包不得引入 CMakeLists.txt"


def test_dependencies_within_whitelist():
    import tomllib

    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = set(data["project"]["dependencies"]) | set(
        data["project"].get("optional-dependencies", {}).get("dev", [])
    )
    names = {re.split(r"[<>=!\[ ;]", d)[0].strip().lower() for d in declared}
    unexpected = names - ALLOWED_DEPS
    assert not unexpected, f"出现白名单外依赖：{sorted(unexpected)}"


def test_layer_boundaries():
    """分层约束：services 不得反向依赖 api/web；models 不得依赖 services。"""
    offenders = []
    for path in (SRC / "inurl_byok_token_hub" / "services").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "from ..api" in text or "from ..web" in text or "from ..cli" in text:
            offenders.append(str(path))
    for path in (SRC / "inurl_byok_token_hub" / "models").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "from ..services" in text or "from ..api" in text:
            offenders.append(str(path))
    assert not offenders, f"违反分层约束：{offenders}"
