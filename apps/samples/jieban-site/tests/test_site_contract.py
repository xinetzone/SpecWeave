"""结伴站点契约测试。

校验两件事：
1. 站点骨架的页面与六条公约内容齐备；
2. `conf.py` 里的「版本身份证」构建期守卫真的会拦截未标注版本的引文
   （防止守卫写成永不触发的装饰品）。

运行（需含 Sphinx 依赖的 Python 环境，本项目为 py314）：

    pytest apps/samples/jieban-site/tests
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
CHANNEL_SLUGS = ("zhizu", "hengyu", "zhihe", "yuduo")


def _load_conf():
    """直接加载 conf.py，以便对构建期守卫做真实调用。"""
    spec = importlib.util.spec_from_file_location("jieban_conf", SRC_DIR / "conf.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["jieban_conf"] = module
    spec.loader.exec_module(module)
    return module


def test_pages_exist():
    assert (SRC_DIR / "index.md").is_file()
    assert (SRC_DIR / "origin.md").is_file()
    assert (SRC_DIR / "covenant.md").is_file()


def test_four_channels_present():
    text = (SRC_DIR / "index.md").read_text(encoding="utf-8")
    for channel in ("知足", "恒与", "知和", "愈多"):
        assert channel in text


def test_four_channel_colors_defined():
    css = (SRC_DIR / "_static" / "jieban.css").read_text(encoding="utf-8")
    for token in ("--zhizu", "--hengyu", "--zhihe", "--yuduo"):
        assert token in css


def test_six_covenant_items_present():
    text = (SRC_DIR / "covenant.md").read_text(encoding="utf-8")
    for item in (
        "真实",
        "善意",
        "不评判",
        "频道隔离 · 零收费导流",
        "隐私默认保护",
        "好好生活",
    ):
        assert item in text


def test_channel_pages_exist():
    for slug in CHANNEL_SLUGS:
        assert (SRC_DIR / "channels" / f"{slug}.md").is_file()


def test_channel_pages_in_toctree():
    toc = (SRC_DIR / "channels" / "index.md").read_text(encoding="utf-8")
    for slug in CHANNEL_SLUGS:
        assert f"\n{slug}\n" in toc


def test_channels_reachable_from_home():
    assert "channels/index" in (SRC_DIR / "index.md").read_text(encoding="utf-8")


def test_no_pending_placeholder_left():
    """所有页面占位都应已填实，首页导航不应残留「待补」。"""
    for name in ("index.md", "origin.md", "covenant.md", "channels/index.md"):
        text = (SRC_DIR / name).read_text(encoding="utf-8")
        assert "（待补）" not in text, f"{name} 仍有未填内容"
        assert "TODO" not in text, f"{name} 仍有未填内容"


def test_top_pages_in_home_toctree():
    text = (SRC_DIR / "index.md").read_text(encoding="utf-8")
    for page in ("origin", "covenant", "channels/index"):
        assert f"\n{page}\n" in text


def test_internal_group_nicknames_not_on_site():
    """内部群昵称不上站点（含禁用词「变现」，以及官方机构误认风险）。"""
    forbidden = ("感恩小队", "民政局小分队", "玩转 AI 变现", "玩转AI变现")
    for md in SRC_DIR.glob("**/*.md"):
        text = md.read_text(encoding="utf-8")
        for name in forbidden:
            assert name not in text, f"{md.name} 出现内部群昵称：{name}"


def test_version_guard_accepts_current_pages():
    _load_conf()._check_version_labels(None, None)


def test_version_guard_rejects_unlabelled_quote(tmp_path, monkeypatch):
    conf = _load_conf()
    monkeypatch.setattr(conf, "SRC_DIR", tmp_path)
    (tmp_path / "bad.md").write_text("既以予人矣，己愈多。", encoding="utf-8")
    with pytest.raises(RuntimeError, match="帛书乙本"):
        conf._check_version_labels(None, None)


def test_version_guard_tolerates_emphasis_markers(tmp_path, monkeypatch):
    """版本名被加粗排版包裹（帛书**乙本**）不应被误判为缺标注。"""
    conf = _load_conf()
    monkeypatch.setattr(conf, "SRC_DIR", tmp_path)
    (tmp_path / "ok.md").write_text(
        "帛书**乙本**《老子》：「既以予人矣，己愈多。」", encoding="utf-8"
    )
    conf._check_version_labels(None, None)


def test_version_guard_rejects_unlabelled_jia_ben_quote(tmp_path, monkeypatch):
    conf = _load_conf()
    monkeypatch.setattr(conf, "SRC_DIR", tmp_path)
    (tmp_path / "bad.md").write_text("和曰常，知和曰明。", encoding="utf-8")
    with pytest.raises(RuntimeError, match="帛书甲本"):
        conf._check_version_labels(None, None)