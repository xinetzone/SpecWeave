"""user_config.py 用户配置文件加载测试（T19）。

覆盖路径解析（``XDG_CONFIG_HOME`` 优先、回退 ``~/.config/<name>``）、
三态来源优先级（默认路径 < ``MD_CONFIG_FILE`` < 显式 path）、
扩展名分派（``.yaml``/``.yml``/``.json``/其余走 TOML）以及
解析失败/顶层非映射的 :class:`UserConfigError` 语义。
"""

import re
from pathlib import Path

import pytest
import yaml

from doocs_md_py.user_config import (
    CONFIG_DIR_NAME,
    CONFIG_FILE_NAME,
    ENV_CONFIG_FILE,
    UserConfigError,
    config_dir,
    config_path,
    load_user_config,
)


# ---- 路径解析 ----


def test_config_dir_prefers_xdg_config_home(tmp_path):
    xdg = tmp_path / "xdg"
    assert config_dir({"XDG_CONFIG_HOME": str(xdg)}) == xdg / CONFIG_DIR_NAME


def test_config_dir_expands_user_in_xdg_value():
    assert config_dir({"XDG_CONFIG_HOME": "~/xdg"}) == (
        Path.home() / "xdg" / CONFIG_DIR_NAME
    )


def test_config_dir_falls_back_to_home_config():
    # 无 XDG_CONFIG_HOME（含空映射）→ ~/.config/<CONFIG_DIR_NAME>
    expected = Path.home() / ".config" / CONFIG_DIR_NAME
    assert config_dir({}) == expected
    assert config_path({}) == expected / CONFIG_FILE_NAME


def test_config_dir_reads_process_environ(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "env-xdg"))
    assert config_dir() == tmp_path / "env-xdg" / CONFIG_DIR_NAME
    assert config_path() == tmp_path / "env-xdg" / CONFIG_DIR_NAME / CONFIG_FILE_NAME


# ---- 来源优先级 ----


def test_explicit_path_wins_over_env_var(tmp_path):
    file = tmp_path / "explicit.json"
    file.write_text('{"legend": "explicit"}', encoding="utf-8")
    assert load_user_config(file, {ENV_CONFIG_FILE: str(tmp_path / "other.toml")}) == {
        "legend": "explicit"
    }


def test_env_var_path_used_when_path_absent(tmp_path, monkeypatch):
    file = tmp_path / "env.toml"
    file.write_text('provider = "github"\n', encoding="utf-8")
    monkeypatch.setenv(ENV_CONFIG_FILE, str(file))
    assert load_user_config() == {"provider": "github"}
    assert load_user_config(environ={"MD_CONFIG_FILE": str(file)}) == {
        "provider": "github"
    }


def test_default_config_path_when_env_var_absent(tmp_path, monkeypatch):
    # 无扩展名的默认 ``config`` 文件走 TOML 解析
    target = tmp_path / "xdg" / CONFIG_DIR_NAME / CONFIG_FILE_NAME
    target.parent.mkdir(parents=True)
    target.write_text('legend = "default"\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    monkeypatch.delenv(ENV_CONFIG_FILE, raising=False)
    assert load_user_config() == {"legend": "default"}


def test_missing_file_is_treated_as_unconfigured(tmp_path):
    assert load_user_config(tmp_path / "nope.toml") == {}
    assert load_user_config(tmp_path / "nope", {"XDG_CONFIG_HOME": str(tmp_path)}) == {}


# ---- 扩展名分派 ----


@pytest.mark.parametrize("suffix", [".yaml", ".yml", ".YAML"])
def test_yaml_suffixes_use_yaml_loader(tmp_path, suffix):
    file = tmp_path / f"config{suffix}"
    file.write_text("provider: github\nlegend: x\n", encoding="utf-8")
    assert load_user_config(file) == {"provider": "github", "legend": "x"}


@pytest.mark.parametrize("suffix", [".json", ".JSON"])
def test_json_suffix_uses_json_loader(tmp_path, suffix):
    file = tmp_path / f"config{suffix}"
    file.write_text('{"provider": "s3", "chunkSize": 8}', encoding="utf-8")
    assert load_user_config(file) == {"provider": "s3", "chunkSize": 8}


@pytest.mark.parametrize("suffix", [".toml", ".toml.bak", ""])
def test_other_suffixes_fall_back_to_toml(tmp_path, suffix):
    file = tmp_path / f"config{suffix}"
    file.write_text('provider = "qiniu"\n', encoding="utf-8")
    assert load_user_config(file) == {"provider": "qiniu"}


# ---- 失败语义 ----


@pytest.mark.parametrize(
    "name,text",
    [
        ("bad.json", "{not json"),
        ("bad.yaml", "a: [1, 2"),
        ("bad.toml", "k = \n"),
        ("bad", "k = \n"),
    ],
)
def test_parse_failure_wraps_original_error_and_path(tmp_path, name, text):
    file = tmp_path / name
    file.write_text(text, encoding="utf-8")

    with pytest.raises(UserConfigError, match=re.escape(str(file))) as excinfo:
        load_user_config(file)

    assert "配置文件解析失败" in str(excinfo.value)
    # 异常链保留原始错误：JSON/TOML 为 ValueError，YAML 为 YAMLError
    assert isinstance(excinfo.value.__cause__, (ValueError, yaml.YAMLError))


@pytest.mark.parametrize(
    "name,text",
    [
        ("list.json", "[1, 2]"),
        ("list.yaml", "- a\n- b\n"),
        ("scalar.yaml", "just-a-string\n"),
    ],
)
def test_non_mapping_top_level_rejected(tmp_path, name, text):
    file = tmp_path / name
    file.write_text(text, encoding="utf-8")

    with pytest.raises(UserConfigError, match="顶层必须是键值映射"):
        load_user_config(file)


def test_user_config_error_is_value_error():
    assert issubclass(UserConfigError, ValueError)
