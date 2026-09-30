"""配置与数据目录守卫测试（TR-1.1 / TR-1.3）。"""

import os
from pathlib import Path

import pytest
import yaml

from travel_planner.config import (
    APP_ENV_API_KEY,
    APP_ENV_DATA,
    ensure_data_dir,
    is_root_direct_child,
    load_llm_config,
    resolve_data_dir,
)
from travel_planner.errors import ConfigError
from travel_planner.lock import InstanceLock


def test_resolve_explicit_path(tmp_path):
    target = tmp_path / "somewhere" / "data"
    assert resolve_data_dir(str(target)) == target.resolve()


def test_resolve_env_override(tmp_path, monkeypatch):
    env_dir = tmp_path / "env-data"
    monkeypatch.setenv(APP_ENV_DATA, str(env_dir))
    assert resolve_data_dir(None) == env_dir.resolve()
    # CLI 显式优先于环境变量
    explicit = tmp_path / "cli-data"
    assert resolve_data_dir(str(explicit)) == explicit.resolve()


def test_resolve_default_from_repo_root():
    """默认路径推算：从 .temp/travel-planner 向上找到 SpecWeave 仓库根。"""
    resolved = resolve_data_dir(None)
    assert resolved.match("playground/travel-planner/data")


def test_is_root_direct_child():
    assert is_root_direct_child(Path("D:/x"))
    assert not is_root_direct_child(Path("D:/a/b"))
    assert not is_root_direct_child(Path("D:/a/b/c"))


def test_ensure_data_dir_guard_and_layout(tmp_path):
    with pytest.raises(ConfigError, match="磁盘根"):
        ensure_data_dir(Path("D:/tp-root-child"))
    data = ensure_data_dir(tmp_path / "data")
    assert (data / "trips").is_dir()
    assert (data / "backups").is_dir()
    cfg = data / "config.yaml"
    assert cfg.is_file()
    assert "base_url" in cfg.read_text(encoding="utf-8")


def test_ensure_data_dir_idempotent_keeps_user_config(data_dir):
    cfg = data_dir / "config.yaml"
    cfg.write_text("llm:\n  base_url: http://x\n", encoding="utf-8")
    ensure_data_dir(data_dir)
    assert "http://x" in cfg.read_text(encoding="utf-8")


def test_load_llm_config_from_file(data_dir):
    (data_dir / "config.yaml").write_text(
        yaml.safe_dump(
            {"llm": {"base_url": "http://x/v1", "api_key": "sk-file", "model": "m", "timeout": 30}}
        ),
        encoding="utf-8",
    )
    cfg = load_llm_config(data_dir)
    assert cfg.base_url == "http://x/v1"
    assert cfg.api_key == "sk-file"
    assert cfg.model == "m"
    assert cfg.timeout == 30.0
    assert cfg.configured


def test_load_llm_config_env_key_priority(data_dir, monkeypatch):
    (data_dir / "config.yaml").write_text(
        yaml.safe_dump({"llm": {"base_url": "http://x/v1", "api_key": "sk-file", "model": "m"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv(APP_ENV_API_KEY, "sk-env")
    cfg = load_llm_config(data_dir)
    assert cfg.api_key == "sk-env"


def test_load_llm_config_invalid(data_dir):
    (data_dir / "config.yaml").write_text("llm:\n  timeout: abc\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="timeout"):
        load_llm_config(data_dir)
    (data_dir / "config.yaml").write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="顶层"):
        load_llm_config(data_dir)


def test_lock_release_and_reacquire(data_dir):
    lock = InstanceLock(data_dir)
    lock.acquire_nowait()
    assert lock.held
    lock.release()
    assert not lock.held
    lock.acquire_nowait()  # 可重复获取
    lock.release()


def test_lock_conflict_within_process(data_dir):
    """同进程另一句柄也应被锁拒绝（Windows 字节范围锁语义）。"""
    first = InstanceLock(data_dir)
    first.acquire_nowait()
    second = InstanceLock(data_dir)
    with pytest.raises(Exception):
        second.acquire_nowait()
    first.release()
