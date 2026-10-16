"""用户配置文件加载（T19）。

upstream ``md-cli`` 仅从 argv/env 取配置（``util.js`` 的 ``parseArgv``，``server.js:16-23``）；
本仓新增用户级配置文件，路径约定 ``~/.config/doocs-md-py/config``（尊重 ``XDG_CONFIG_HOME``）。

读取优先级：默认路径 < ``--config`` / ``MD_CONFIG_FILE`` 指定的文件 < ``MD_*`` 环境变量。
配置文件只存在于用户本机，**凭证不入版本库**（应用内不含任何内置凭证）。
"""

import json
import os
import tomllib
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR_NAME = "doocs-md-py"
CONFIG_FILE_NAME = "config"
ENV_CONFIG_FILE = "MD_CONFIG_FILE"

# upload 子命令的环境变量回退（缺省时替代 --provider/--file/--config）
ENV_UPLOAD_PROVIDER = "MD_UPLOAD_PROVIDER"
ENV_UPLOAD_FILE = "MD_UPLOAD_FILE"


class UserConfigError(ValueError):
    """配置文件读取或解析失败（CLI 转成使用性错误，退出码 2）。"""


def config_dir(environ: dict[str, str] | None = None) -> Path:
    env = environ if environ is not None else os.environ
    base = env.get("XDG_CONFIG_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".config"
    return root / CONFIG_DIR_NAME


def config_path(environ: dict[str, str] | None = None) -> Path:
    return config_dir(environ) / CONFIG_FILE_NAME


def load_user_config(
    path: str | os.PathLike[str] | None = None,
    environ: dict[str, str] | None = None,
) -> dict[str, Any]:
    """读取用户配置；文件不存在视为合法的「未配置」并返回空映射。"""
    env = environ if environ is not None else os.environ
    if path is None:
        path = env.get(ENV_CONFIG_FILE) or config_path(env)
    file = Path(path).expanduser()
    if not file.is_file():
        return {}
    text = file.read_text(encoding="utf-8")
    try:
        data = _parse(text, file.suffix.lower())
    except (ValueError, yaml.YAMLError) as exc:
        raise UserConfigError(f"配置文件解析失败：{file}（{exc}）") from exc
    if not isinstance(data, dict):
        raise UserConfigError(f"配置文件顶层必须是键值映射：{file}")
    return data


def _parse(text: str, suffix: str) -> Any:
    # 无扩展名的默认 ``config`` 与 ``.toml`` 走标准库 TOML，其余按扩展名分派
    if suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    if suffix == ".json":
        return json.loads(text)
    return tomllib.loads(text)
