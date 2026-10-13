"""显式命令注册表 L0 断言：键集、可调用性、零副作用导入。"""

import subprocess
import sys
from pathlib import Path

from okw.commands import COMMAND_HANDLERS

EXPECTED_KEYS = sorted(
    [
        "list",
        "status",
        "import",
        "export",
        "unregister",
        "exec",
        "verify",
        "scaffold",
        "ref",
        "ai preflight",
        "ai install",
        "ai verify",
        "podman preflight",
        "podman install",
        "podman verify",
        "compose preflight",
        "compose install",
        "compose verify",
        "desktop preflight",
        "desktop install",
        "desktop verify",
        "desktop launch",
        "image build",
        "image verify",
    ]
)

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


def test_registry_has_exactly_twenty_four_leaves():
    assert sorted(COMMAND_HANDLERS) == EXPECTED_KEYS
    assert len(COMMAND_HANDLERS) == 24


def test_every_registry_value_is_callable():
    for key, handler in COMMAND_HANDLERS.items():
        assert callable(handler), key


def test_registry_is_plain_dict():
    assert type(COMMAND_HANDLERS) is dict


def test_import_commands_has_no_subprocess_side_effects():
    # 干净子进程：把 distro 的 WSL 执行入口替换为探针后导入 commands 包，
    # 任何导入期子进程调用都会令探针失败。
    script = (
        "import sys\n"
        f"sys.path.insert(0, r'{SRC_ROOT}')\n"
        "import okw.distro as d\n"
        "def _boom(*a, **k):\n"
        "    raise AssertionError('import 期发生子进程副作用')\n"
        "d.run_wsl = _boom\n"
        "import okw.commands\n"
        "from okw.commands import COMMAND_HANDLERS\n"
        "assert len(COMMAND_HANDLERS) == 24\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
