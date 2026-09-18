"""ast_inject.sh 的 daemon-free 单测（问题解决场景：rootless ACL EINVAL 回归）。

覆盖契约（见 overlays/xmnn-dev/builder/scripts/lib/ast_inject.sh 头注）：
  - 字节级备份（禁止 cp -p/-a/--preserve：含未映射 UID 的 POSIX ACL 会让
    内核 setxattr 返回 EINVAL）；
  - ast_restore 内容回写原 inode（属主/模式不变，外部源码树零修改）；
  - 四态自愈矩阵 + 幂等；
  - cp 失败不留 tmp 残文件；入口清扫同 tag 陈旧 tmp。

仅 POSIX（需 bash）；Windows 原生自动 skip。真机 ACL/uidmap 场景由
``inv xmnn.wheel`` 端到端回归覆盖，本套件不构造用户命名空间。
"""
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="ast_inject.sh 需 bash（POSIX 平台）"
)

CLIENT_ROOT = Path(__file__).resolve().parents[1]
AST_LIB = (
    CLIENT_ROOT
    / "overlays/xmnn-dev/builder/scripts/lib/ast_inject.sh"
)
MARKER = "# === XMNN BOOTSTRAP ==="
ORIGINAL = "print('hello xmnn')\n"


def _bash(snippet: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """source ast_inject.sh 后执行 snippet，返回完成进程。"""
    prelude = (
        f"export AST_PYTHON={shlex.quote(sys.executable)}\n"
        f"source {shlex.quote(str(AST_LIB))}\n"
    )
    return subprocess.run(
        ["bash", "-c", prelude + snippet],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def _call(func: str, *args: str) -> subprocess.CompletedProcess:
    quoted = " ".join(shlex.quote(a) for a in args)
    # ast_inject 的 backup 路径无尾换行，RC 前补换行防粘连
    return _bash(f"{func} {quoted}\nprintf '\\nRC=%s\\n' $?\n")


def _rc(proc: subprocess.CompletedProcess) -> int:
    matches = re.findall(r"RC=(\d+)", proc.stdout)
    assert matches, f"未取到 RC：stdout={proc.stdout!r} stderr={proc.stderr!r}"
    return int(matches[-1])


def _stdout(proc: subprocess.CompletedProcess) -> str:
    """取 RC 行之前的函数 stdout（ast_inject 的 backup 路径契约）。"""
    return proc.stdout.rsplit("\nRC=", 1)[0].strip()


def _make_pkg(tmp_path: Path, name: str = "__init__.py") -> Path:
    init = tmp_path / name
    init.write_text(ORIGINAL, encoding="utf-8")
    os.chmod(init, 0o640)
    return init


def test_inject_then_restore_roundtrip(tmp_path):
    init = _make_pkg(tmp_path)
    inode0 = init.stat().st_ino
    mode0 = init.stat().st_mode

    r = _call("ast_inject", str(init), "tvm")
    assert _rc(r) == 0, r.stderr
    backup = Path(_stdout(r))
    assert backup.read_text(encoding="utf-8") == ORIGINAL  # 字节一致
    injected = init.read_text(encoding="utf-8")
    assert MARKER in injected and injected.endswith(ORIGINAL)
    assert init.stat().st_ino == inode0  # 注入是 in-place 截断写

    r = _call("ast_restore", str(init), str(backup))
    assert _rc(r) == 0, r.stderr
    assert init.read_text(encoding="utf-8") == ORIGINAL
    assert not backup.exists()  # 还原后备份被消费
    assert init.stat().st_ino == inode0  # 内容回写不换 inode
    assert init.stat().st_mode == mode0  # 模式不变


def test_restore_noop_without_backup(tmp_path):
    init = _make_pkg(tmp_path)
    r = _call("ast_restore", str(init), str(tmp_path / "no.bak"))
    assert _rc(r) == 1
    assert init.read_text(encoding="utf-8") == ORIGINAL


def test_self_heal_marker_with_backup(tmp_path):
    init = _make_pkg(tmp_path)
    backup = tmp_path / "__init__.py.bak_tvm"
    backup.write_text(ORIGINAL, encoding="utf-8")
    init.write_text(MARKER + "\nresidue\n" + ORIGINAL, encoding="utf-8")

    r = _call("ast_inject", str(init), "tvm")  # 应先自愈再重新注入
    assert _rc(r) == 0, r.stderr
    assert MARKER in init.read_text(encoding="utf-8")

    r = _call("ast_restore", str(init), str(backup))
    assert _rc(r) == 0, r.stderr
    assert init.read_text(encoding="utf-8") == ORIGINAL


def test_fatal_marker_without_backup(tmp_path):
    init = _make_pkg(tmp_path)
    polluted = MARKER + "\npolluted\n"
    init.write_text(polluted, encoding="utf-8")

    r = _call("ast_inject", str(init), "tvm")
    assert _rc(r) == 2  # 不可自愈：要求人工 git checkout
    assert init.read_text(encoding="utf-8") == polluted  # 绝不覆盖


def test_truncated_residue_self_heals(tmp_path):
    init = _make_pkg(tmp_path)
    backup = tmp_path / "__init__.py.bak_vta"
    backup.write_text(ORIGINAL, encoding="utf-8")
    init.write_text("", encoding="utf-8")  # 注入器截断窗口残留

    r = _call("ast_inject", str(init), "vta")
    assert _rc(r) == 0, r.stderr
    r = _call("ast_restore", str(init), str(backup))
    assert _rc(r) == 0, r.stderr
    assert init.read_text(encoding="utf-8") == ORIGINAL


def test_stale_tmp_swept_on_entry(tmp_path):
    init = _make_pkg(tmp_path)
    stale = tmp_path / "__init__.py.bak_xmnn.tmp.99999"
    stale.write_text("junk", encoding="utf-8")

    r = _call("ast_inject", str(init), "xmnn")
    assert _rc(r) == 0, r.stderr
    assert not stale.exists()  # 陈旧 tmp 被入口清扫
    assert not list(tmp_path.glob("*.tmp.*"))


def test_backup_failure_leaves_no_tmp(tmp_path):
    if os.geteuid() == 0:
        pytest.skip("root 绕过目录 DAC，无法制造 cp EACCES")
    init = _make_pkg(tmp_path)
    os.chmod(tmp_path, 0o555)  # 目录不可写 → cp 必失败
    try:
        r = _call("ast_inject", str(init), "tvm")
        assert _rc(r) == 2
    finally:
        os.chmod(tmp_path, 0o755)
    assert not list(tmp_path.glob("*.tmp.*"))  # 失败路径无残留
    assert init.read_text(encoding="utf-8") == ORIGINAL  # 源文件未动


def test_concurrent_tags_isolation(tmp_path):
    init_a = _make_pkg(tmp_path, "a_init.py")
    init_b = _make_pkg(tmp_path, "b_init.py")
    r = _call(
        "ast_inject", str(init_a), "tvm"
    )
    assert _rc(r) == 0, r.stderr
    r = _call("ast_inject", str(init_b), "vta")
    assert _rc(r) == 0, r.stderr

    for init, tag in ((init_a, "tvm"), (init_b, "vta")):
        backup = tmp_path / f"{init.name}.bak_{tag}"
        assert backup.exists()
        assert _rc(_call("ast_restore", str(init), str(backup))) == 0
        assert init.read_text(encoding="utf-8") == ORIGINAL
    assert not list(tmp_path.glob("*.bak_*"))


def test_double_cycle_idempotent(tmp_path):
    init = _make_pkg(tmp_path)
    for _ in range(2):
        r = _call("ast_inject", str(init), "tvm")
        assert _rc(r) == 0, r.stderr
        backup = Path(_stdout(r))
        assert _rc(_call("ast_restore", str(init), str(backup))) == 0
    assert init.read_text(encoding="utf-8") == ORIGINAL
    assert not list(tmp_path.glob("*.bak*"))
    assert not list(tmp_path.glob("*.tmp.*"))


def test_no_metadata_preserving_cp_in_lib():
    """静态回归守卫：备份 cp 永远不得带 -p/-a/--preserve（ACL EINVAL 根因）。

    只扫代码行（禁令本身写在注释里，不能让注释触发守卫）。
    """
    text = AST_LIB.read_text(encoding="utf-8")
    code = "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
    )
    for line in code.splitlines():
        if not re.search(r"\bcp\b", line):
            continue
        for token in re.findall(r"(--?[A-Za-z-]+)", line):
            flags = token.lstrip("-")
            assert "p" not in flags and "a" not in flags, (
                f"ast_inject.sh 禁止 cp 携带 -p/-a/--preserve/--archive："
                f"rootless 下复制含未映射 UID 的 ACL 会 EINVAL：{line.strip()}"
            )
    # 还原必须是原 inode 内容回写，不得 mv 替换源码文件
    assert 'cat -- "$backup" > "$init_file"' in code
    assert 'mv -f "$backup" "$init_file"' not in code
