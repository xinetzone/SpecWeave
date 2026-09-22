"""setup-ssh-env.sh 的 daemon-free 单测（问题解决场景：SSH 会话缺调试环境变量）。

覆盖契约（见 overlays/native-dev/scripts/setup-ssh-env.sh 头注）：

- **防漂移**：同一组 5 个调试变量在仓库里有三份副本——compose.yaml 的
  ``environment``、register-kernel.sh 内嵌的 kernel env、setup-ssh-env.sh 的
  字面量。三者必须逐字一致：任何一处改漏都造成「Jupyter 内核可用、SSH 不可用」
  这类半失效（本次故障的形态）。
- **实跑**：在临时目录里用测试替身 sshd 执行**真实脚本**，断言
  ① 生成的 profile.d 文件含 5 条 ``${VAR:=默认}`` + ``export``；
  ② sshd_config 只写**一行** SetEnv 且 5 个键齐全——sshd 对多行 SetEnv 是
     first-wins（实测 ``sshd -T`` 只回显首条，其余静默丢弃）；
  ③ 幂等：连跑两次仍只有一行；
  ④ 历史多行形态（5 行 SetEnv）被清理干净；
  ⑤ ``sshd -t`` 失败时整段回滚、退出码非 0、不留备份文件。

仅 POSIX（需 bash/sed/grep）；Windows 原生自动 skip。
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

# 判据必须含 POSIX 平台：Windows 自带 System32\bash.exe（WSL 启动器）会让
# `which("bash")` 判真，但 WSL 无法翻译 SMB/UNC 检出路径（且本脚本需 sed/grep）。
pytestmark = pytest.mark.skipif(
    os.name != "posix" or shutil.which("bash") is None,
    reason="setup-ssh-env.sh 需 POSIX + bash（Windows 原生自动 skip）",
)

CLIENT_ROOT = Path(__file__).resolve().parents[1]
OVERLAY = CLIENT_ROOT / "overlays" / "native-dev"
SCRIPT = OVERLAY / "scripts" / "setup-ssh-env.sh"
KERNEL_SCRIPT = OVERLAY / "scripts" / "register-kernel.sh"
COMPOSE = OVERLAY / "compose.yaml"

DEBUG_VARS = (
    "PYTHONPATH",
    "TVM_LIBRARY_PATH",
    "LD_LIBRARY_PATH",
    "NPU_TOOLS_ROOT",
    "XMNN_TOOLS_ROOT",
)

# 测试替身：只复刻本测试需要的最小契约。
# `-T` 刻意复刻实测的 first-wins——只取**第一条** SetEnv 行、按空格拆成多对。
# 因此若脚本回退成「每变量一行」，脚本自身的生效性自检会读到 1 != 5 而失败。
STUB_SSHD = """#!/bin/sh
case "$1" in
  -t) exit "${NATIVE_TEST_SSHD_T_EXIT:-0}" ;;
  -T)
    line=$(grep -m1 '^SetEnv ' "$NATIVE_TEST_SSHD_CONFIG" 2>/dev/null || true)
    [ -n "$line" ] || exit 0
    for pair in ${line#SetEnv }; do printf 'setenv %s\\n' "$pair"; done
    ;;
esac
exit 0
"""


def _script_literals() -> dict[str, str]:
    """脚本里的 ``NAME_VALUE=...`` 字面量。"""
    text = SCRIPT.read_text(encoding="utf-8")
    found = dict(re.findall(r"^([A-Z_]+)_VALUE=(\S+)$", text, re.MULTILINE))
    return {k: v for k, v in found.items() if k in DEBUG_VARS}


def _compose_debug_env() -> dict[str, str]:
    data = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    env = data["services"]["native"]["environment"]
    return {k: v for k, v in env.items() if k in DEBUG_VARS}


def _kernel_env() -> dict[str, str]:
    """register-kernel.sh 内嵌 kernel env 里的同名键（正则取 ``"KEY": "值"``）。"""
    text = KERNEL_SCRIPT.read_text(encoding="utf-8")
    found = dict(re.findall(r'"([A-Z_]+)": "([^"]*)"', text))
    return {k: v for k, v in found.items() if k in DEBUG_VARS}


# ── 防漂移：三份副本逐字一致 ─────────────────────────────────────────────────

def test_script_literals_match_compose_environment() -> None:
    """脚本字面量 == compose environment（唯一运行时事实源）。"""
    assert _script_literals() == _compose_debug_env()


def test_kernel_env_matches_compose_environment() -> None:
    """Jupyter 内核 env == compose environment（同源，防内核/SSH 分叉）。"""
    assert _kernel_env() == _compose_debug_env()


def test_all_debug_vars_present_in_all_three_copies() -> None:
    """5 个键在三处副本里都不缺（少一个即为半失效）。"""
    for name, mapping in (
        ("compose.yaml", _compose_debug_env()),
        ("register-kernel.sh", _kernel_env()),
        ("setup-ssh-env.sh", _script_literals()),
    ):
        assert set(mapping) == set(DEBUG_VARS), f"{name} 缺少调试变量"


# ── 实跑：临时目录 + 替身 sshd ───────────────────────────────────────────────

class _Sandbox:
    def __init__(self, tmp_path: Path, config_text: str = "Port 22\n") -> None:
        self.profile = tmp_path / "profile.d" / "50-native-dev-env.sh"
        self.profile.parent.mkdir(parents=True, exist_ok=True)
        self.config = tmp_path / "sshd_config"
        self.config.write_text(config_text, encoding="utf-8")
        self.original = config_text
        self.stub = tmp_path / "sshd"
        self.stub.write_text(STUB_SSHD, encoding="utf-8")
        self.stub.chmod(0o755)

    def run(self, t_exit: int = 0) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.update(
            NATIVE_SSH_ENV_PROFILE_FILE=str(self.profile),
            NATIVE_SSH_ENV_SSHD_CONFIG=str(self.config),
            NATIVE_SSH_ENV_SSHD_BIN=str(self.stub),
            NATIVE_TEST_SSHD_CONFIG=str(self.config),
            NATIVE_TEST_SSHD_T_EXIT=str(t_exit),
        )
        return subprocess.run(
            ["bash", str(SCRIPT)], env=env, capture_output=True, text=True
        )

    def setenv_lines(self) -> list[str]:
        return [
            line
            for line in self.config.read_text(encoding="utf-8").splitlines()
            if line.startswith("SetEnv ")
        ]


def test_writes_profile_d_and_single_setenv_line(tmp_path: Path) -> None:
    box = _Sandbox(tmp_path)
    proc = box.run()

    assert proc.returncode == 0, proc.stderr
    profile = box.profile.read_text(encoding="utf-8")
    for name, value in _compose_debug_env().items():
        assert f': "${{{name}:={value}}}"' in profile
        assert f"export {name}" in profile

    lines = box.setenv_lines()
    assert len(lines) == 1, f"SetEnv 必须单行（first-wins）：{lines}"
    for name, value in _compose_debug_env().items():
        assert f"{name}={value}" in lines[0]
    assert not box.config.with_suffix(".native-dev.bak").exists()

def test_idempotent_across_repeated_runs(tmp_path: Path) -> None:
    box = _Sandbox(tmp_path)
    assert box.run().returncode == 0
    assert box.run().returncode == 0
    assert len(box.setenv_lines()) == 1
    # 标记行同样不得累积（V 审查实测：只删 SetEnv 不删标记时连跑 3 次留 3 行）
    text = box.config.read_text(encoding="utf-8")
    assert text.count("# native-dev ssh-env") == 1
    assert box.profile.read_text(encoding="utf-8").count("export PYTHONPATH") == 1


def test_stale_multi_line_setenv_is_cleaned(tmp_path: Path) -> None:
    """历史形态（每变量一行）必须先被清干净，否则 first-wins 只生效首条。"""
    stale = "".join(
        f"SetEnv {name}={value}\n"
        for name, value in _compose_debug_env().items()
    )
    box = _Sandbox(tmp_path, config_text="Port 22\n" + stale)
    assert box.run().returncode == 0

    lines = box.setenv_lines()
    assert len(lines) == 1, f"陈旧多行 SetEnv 未清理：{lines}"


def test_rolls_back_when_sshd_config_invalid(tmp_path: Path) -> None:
    box = _Sandbox(tmp_path)
    proc = box.run(t_exit=1)

    assert proc.returncode != 0
    assert box.config.read_text(encoding="utf-8") == box.original
    assert not box.config.with_suffix(".native-dev.bak").exists()
