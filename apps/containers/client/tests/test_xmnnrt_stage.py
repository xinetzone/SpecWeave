"""xmnnrt wheel 暂存选择顺序的 daemon-free 单测（V 审查 P0 回归锁）。

不触 daemon/podman：monkeypatch ``xmnnrt.overlay_dir`` 把暂存区与 dist
重定向到 tmp_path（目录形态对齐真实布局 client/overlays/xmnn-runtime 与
client/workspace/dist）。
"""

import os
from pathlib import Path

import pytest
from invoke.exceptions import Exit

from jpman_client.tasks import xmnnrt

_WHL = "xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl"


@pytest.fixture
def stage_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """构造 (wheels_dir, dist_dir)，并把模块的 overlay_dir 锚到 tmp 布局。"""
    overlay = tmp_path / "client" / "overlays" / "xmnn-runtime"
    wheels = overlay / "wheels"
    dist = tmp_path / "client" / "workspace" / "dist"
    wheels.mkdir(parents=True)
    dist.mkdir(parents=True)
    monkeypatch.setattr(xmnnrt, "overlay_dir", lambda spec: overlay)
    return wheels, dist


def _write(path: Path, data: bytes, mtime: float) -> Path:
    path.write_bytes(data)
    os.utime(path, (mtime, mtime))
    return path


def test_dist_newer_same_name_replaces_stale_stage(stage_dirs: tuple[Path, Path]) -> None:
    """V-P0：dev0 同名 whl 重打包（mtime 更新）必须替换暂存，不得复用旧文件。"""
    wheels, dist = stage_dirs
    _write(wheels / _WHL, b"OLD-BUILD", 1000.0)
    _write(dist / _WHL, b"NEW-BUILD", 2000.0)

    staged = xmnnrt._ensure_wheel_staged(None)

    assert staged.name == _WHL
    assert staged.read_bytes() == b"NEW-BUILD"
    assert staged.stat().st_mtime_ns == (dist / _WHL).stat().st_mtime_ns


def test_identical_name_size_mtime_skips_copy(stage_dirs: tuple[Path, Path]) -> None:
    """copy2 保留 mtime：二次运行 name+size+mtime 一致即复用（暂存区单文件）。"""
    wheels, dist = stage_dirs
    src = _write(dist / _WHL, b"SAME-BYTES", 3000.0)
    import shutil
    shutil.copy2(src, wheels / _WHL)

    staged = xmnnrt._ensure_wheel_staged(None)

    assert staged.read_bytes() == b"SAME-BYTES"
    assert xmnnrt._staged_wheels() == [wheels / _WHL]


def test_same_name_same_mtime_different_size_still_replaces(stage_dirs: tuple[Path, Path]) -> None:
    """秒级 mtime 相同但大小不同（极快重打包）也要识别为新产物。"""
    wheels, dist = stage_dirs
    _write(wheels / _WHL, b"short", 4000.0)
    _write(dist / _WHL, b"a-much-longer-wheel-content", 4000.0)

    assert xmnnrt._ensure_wheel_staged(None).read_bytes() == b"a-much-longer-wheel-content"


def test_fallback_to_staged_when_dist_empty(stage_dirs: tuple[Path, Path]) -> None:
    wheels, _ = stage_dirs
    _write(wheels / _WHL, b"STAGED-ONLY", 5000.0)

    assert xmnnrt._ensure_wheel_staged(None).read_bytes() == b"STAGED-ONLY"


def test_missing_everywhere_exits_with_hint(stage_dirs: tuple[Path, Path]) -> None:
    with pytest.raises(Exit):
        xmnnrt._ensure_wheel_staged(None)


def test_explicit_wheel_forces_replace(stage_dirs: tuple[Path, Path], tmp_path: Path) -> None:
    wheels, dist = stage_dirs
    _write(wheels / _WHL, b"STAGED", 6000.0)
    _write(dist / _WHL, b"DIST-LATEST", 7000.0)  # 即使 dist 更新也以显式为准
    pick = _write(tmp_path / _WHL, b"EXPLICIT-PICK", 8000.0)

    staged = xmnnrt._ensure_wheel_staged(str(pick))

    assert staged.read_bytes() == b"EXPLICIT-PICK"
    assert xmnnrt._staged_wheels() == [wheels / _WHL]  # 旧暂存被清空替换


def test_explicit_invalid_path_exits(stage_dirs: tuple[Path, Path], tmp_path: Path) -> None:
    with pytest.raises(Exit):
        xmnnrt._ensure_wheel_staged(str(tmp_path / "nope.whl"))
    with pytest.raises(Exit):
        xmnnrt._ensure_wheel_staged(str(__file__))  # 存在但不是 xmnn whl
