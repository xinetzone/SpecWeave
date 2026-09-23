"""镜像归档的 torch 形态打通单测（C20，daemon-free / 无子进程）。

背景：cpu 与 cu130 两份镜像 **tag 相同**（``localhost/native-dev:latest``），形态只
存在于镜像 LABEL。若归档名也不携带形态，两者同族同名、共用同一个 ``-latest``
软链，离线机 ``load`` 按 mtime 取「最新」会静默导入错形态。

覆盖三段互逆契约：
  ① ``save_image`` 命名 —— 形态由镜像 LABEL 读出，写成归档名中缀 ``-torch-<形态>-``；
  ② ``utils.archive_flavor`` —— 从归档名反向解析出同一形态（与 ① 严格互逆）；
  ③ ``find_latest_image_tar(flavor=...)`` —— 按形态过滤选档，杜绝静默串档。
"""

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import jpman_client.tasks.client_core as cc
from jpman_client.tasks import utils as u

_TS = "20260920-101112"
_SHORT = "abc123def456"


# ---------------------------------------------------------------------------
# ② archive_flavor：归档名 → 形态（反向解析）
# ---------------------------------------------------------------------------


def test_archive_flavor_parses_marked_segment():
    assert u.archive_flavor(f"localhost-native-dev-torch-cu130-{_SHORT}-{_TS}.tar.gz") == "cu130"
    assert u.archive_flavor(f"localhost-native-dev-torch-cpu-{_SHORT}-{_TS}.tar") == "cpu"
    assert u.archive_flavor(f"localhost-native-dev-torch-cu130-unknown-{_TS}.tar.gz") == "cu130"


def test_archive_flavor_ignores_tag_latest_segment():
    """无标记的 ``-<形态>-`` 会与镜像 tag 自带的 ``-latest`` 段互相冒充。"""
    assert u.archive_flavor(f"localhost-native-dev-latest-{_SHORT}-{_TS}.tar.gz") == ""


def test_archive_flavor_returns_empty_for_non_archives():
    assert u.archive_flavor("manifest.txt") == ""
    # `-latest` 软链名：形态段后必须紧跟 shortid+ts，软链名不参与解析
    assert u.archive_flavor("localhost-native-dev-torch-cu130-latest.tar") == ""


# ---------------------------------------------------------------------------
# ③ find_latest_image_tar：按形态过滤选档
# ---------------------------------------------------------------------------


def _mk(dir_: Path, name: str, mtime: float) -> Path:
    p = dir_ / name
    p.write_bytes(b"x")
    os.utime(p, (mtime, mtime))
    return p


def test_find_latest_image_tar_filters_by_flavor(tmp_path):
    newer_cpu = _mk(tmp_path, f"localhost-native-dev-torch-cpu-{_SHORT}-20260920-120000.tar.gz", 2_000_000_000)
    older_cu130 = _mk(tmp_path, f"localhost-native-dev-torch-cu130-{_SHORT}-20260920-110000.tar.gz", 1_000_000_000)
    _mk(tmp_path, f"localhost-native-dev-{_SHORT}-20260920-100000.tar.gz", 900_000_000)

    # 默认不过滤：保持历史「取最新」语义（零回归）
    assert u.find_latest_image_tar(tmp_path) == newer_cpu
    # 按形态过滤：即便 cpu 更新，期望 cu130 也只会拿到 cu130
    assert u.find_latest_image_tar(tmp_path, "cu130") == older_cu130
    # 空串只取未标注形态的归档
    assert u.find_latest_image_tar(tmp_path, "").name.endswith("20260920-100000.tar.gz")
    # 无匹配返回 None（调用方据此报错而非静默取错形态）
    assert u.find_latest_image_tar(tmp_path, "cu999") is None


def test_find_latest_image_tar_skips_symlinks(tmp_path):
    real = _mk(tmp_path, f"localhost-native-dev-torch-cu130-{_SHORT}-{_TS}.tar.gz", 1_000_000_000)
    try:
        (tmp_path / "newer.tar.gz").symlink_to(real.name)
    except (OSError, NotImplementedError):
        pytest.skip("宿主不支持创建符号链接")
    os.utime(tmp_path / "newer.tar.gz", (2_000_000_000, 2_000_000_000))
    assert u.find_latest_image_tar(tmp_path) == real


def test_find_latest_image_tar_missing_dir_returns_none(tmp_path):
    assert u.find_latest_image_tar(tmp_path / "nope") is None


# ---------------------------------------------------------------------------
# ① save_image：镜像 LABEL → 归档名 + manifest
# ---------------------------------------------------------------------------


@pytest.fixture
def save_env(monkeypatch, tmp_path):
    """打桩 save_image 的全部宿主接触面（镜像存在性 / inspect / 导出 / 压缩工具）。"""
    monkeypatch.setattr(cc, "_image_exists_fast", lambda c, image: True)
    # 无 pigz/gzip → 未压缩 .tar 降级（避开 gzip -t 子进程）
    monkeypatch.setattr(cc, "shutil", SimpleNamespace(which=lambda name: None))

    def fake_save(c, image, outfile):
        outfile.write_bytes(b"tar-bytes")
        return True

    monkeypatch.setattr(cc, "_save_via_cli", fake_save)

    def set_flavor(flavor: str) -> None:
        labels = {cc.TORCH_FLAVOR_LABEL: flavor} if flavor else {}
        monkeypatch.setattr(
            cc,
            "image_inspect_info",
            lambda c, tag: {"digest": f"sha256:{_SHORT}" + "0" * 52, "labels": labels},
        )

    cache = tmp_path / "cache"
    return SimpleNamespace(cache=cache, set_flavor=set_flavor)


def test_save_image_archive_name_carries_flavor(save_env):
    save_env.set_flavor("cu130")
    assert cc.save_image(None, "localhost/native-dev:latest", save_env.cache) is True

    archives = [p for p in save_env.cache.iterdir() if not p.is_symlink() and p.suffix == ".tar"]
    assert len(archives) == 1
    name = archives[0].name
    assert name.startswith(f"localhost-native-dev-latest-torch-cu130-{_SHORT}-")
    # 命名与解析严格互逆（改其一必须同步另一处）
    assert u.archive_flavor(name) == "cu130"

    manifest = (save_env.cache / "manifest.txt").read_text(encoding="utf-8")
    assert f"IMAGE_FILE={name}" in manifest
    assert "TORCH_FLAVOR=cu130" in manifest


def test_save_image_without_flavor_keeps_legacy_naming(save_env):
    """非 torch 栈 / 未烘 LABEL 的镜像：命名与历史产物逐字一致（零回归）。"""
    save_env.set_flavor("")
    assert cc.save_image(None, "localhost/native-dev:latest", save_env.cache) is True

    archives = [p for p in save_env.cache.iterdir() if not p.is_symlink() and p.suffix == ".tar"]
    assert len(archives) == 1
    name = archives[0].name
    assert name.startswith(f"localhost-native-dev-latest-{_SHORT}-")
    assert "-torch-" not in name
    assert u.archive_flavor(name) == ""
    assert "TORCH_FLAVOR=\n" in (save_env.cache / "manifest.txt").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# _image_torch_flavor：LABEL 读取的降级面
# ---------------------------------------------------------------------------


def test_image_torch_flavor_reads_label():
    assert cc._image_torch_flavor({"labels": {cc.TORCH_FLAVOR_LABEL: "cu130"}}) == "cu130"
    assert cc._image_torch_flavor({"labels": {cc.TORCH_FLAVOR_LABEL: "  cpu  "}}) == "cpu"


@pytest.mark.parametrize(
    "info",
    [{}, {"labels": None}, {"labels": "broken"}, {"labels": {}}, {"labels": {"other": "x"}}],
)
def test_image_torch_flavor_degrades_to_empty(info):
    assert cc._image_torch_flavor(info) == ""