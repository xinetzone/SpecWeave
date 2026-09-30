"""应用配置：数据目录定位、LLM 配置读取与首启初始化。

数据目录优先级：CLI ``--data-dir`` > 环境变量 ``TRAVEL_PLANNER_DATA``
> 仓库根推算（``playground/travel-planner/data/``）。

密钥优先级：环境变量 ``TRAVEL_PLANNER_API_KEY`` > ``config.yaml`` 的
``llm.api_key``。密钥只在本模块读取，任何日志与错误信息不得包含其原文。
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import ConfigError

APP_ENV_DATA = "TRAVEL_PLANNER_DATA"
APP_ENV_API_KEY = "TRAVEL_PLANNER_API_KEY"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
BACKUP_KEEP = 5

CONFIG_TEMPLATE = """\
# travel-planner 配置（YAML）。
# LLM 为可选在线层：不配置时除「AI 行程生成」外全部功能离线可用。
llm:
  # 任意 OpenAI 兼容端点，例如 https://api.deepseek.com/v1
  # 也可指向本机代理（如 inurl-byok-token-hub 的 OpenAI 兼容端口）。
  base_url: ""
  # 建议改用环境变量 TRAVEL_PLANNER_API_KEY 提供密钥（优先级更高）。
  api_key: ""
  model: ""
  # 请求超时（秒），生成行程通常需要 30~120 秒。
  timeout: 60
"""


@dataclass(frozen=True)
class LLMConfig:
    """LLM 连接配置；三项齐备才视为「已配置」。"""

    base_url: str = ""
    api_key: str = ""
    model: str = ""
    timeout: float = 60.0

    @property
    def configured(self) -> bool:
        return bool(self.base_url.strip() and self.api_key.strip() and self.model.strip())


@dataclass(frozen=True)
class AppConfig:
    """应用运行配置。"""

    data_dir: Path
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    backup_keep: int = BACKUP_KEEP


def resolve_data_dir(explicit: str | None = None) -> Path:
    """解析数据目录绝对路径（优先级见模块说明）。"""
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get(APP_ENV_DATA)
    if env:
        return Path(env).expanduser().resolve()
    root = _find_repo_root()
    base = root if root is not None else Path.cwd()
    return (base / "playground" / "travel-planner" / "data").resolve()


def _find_repo_root() -> Path | None:
    """从当前目录向上（最多 4 层）寻找 SpecWeave 仓库根。

    判据：目录同时含 ``apps/`` 与 ``AGENTS.md``（首部含「启动协议」锚点）。
    """
    cur = Path.cwd().resolve()
    for _ in range(4):
        if (cur / "apps").is_dir() and (cur / "AGENTS.md").is_file():
            try:
                head = (cur / "AGENTS.md").read_text(encoding="utf-8", errors="ignore")[:800]
            except OSError:
                head = ""
            if "启动协议" in head:
                return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def is_root_direct_child(path: Path) -> bool:
    """判断路径是否为文件系统根的直接子级（如 ``D:\\x``）。"""
    resolved = path.resolve() if path.exists() else path.absolute()
    parent = resolved.parent
    return parent.parent == parent


def ensure_data_dir(data_dir: Path) -> Path:
    """初始化数据目录结构；守卫根直接子级；幂等。"""
    if is_root_direct_child(data_dir):
        raise ConfigError(
            f"数据目录不允许直接位于磁盘根下（{data_dir}），"
            "请用 --data-dir 指定更深层的目录"
        )
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "trips").mkdir(exist_ok=True)
    (data_dir / "backups").mkdir(exist_ok=True)
    cfg_file = data_dir / "config.yaml"
    if not cfg_file.exists():
        cfg_file.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    return data_dir


def load_llm_config(data_dir: Path) -> LLMConfig:
    """读取 LLM 配置；环境变量密钥优先；结构错误给中文提示。"""
    cfg_file = data_dir / "config.yaml"
    data: dict = {}
    if cfg_file.exists():
        try:
            loaded = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"config.yaml 解析失败：{exc}") from exc
        if not isinstance(loaded, dict):
            raise ConfigError("config.yaml 顶层必须是键值映射结构")
        data = loaded.get("llm") or {}
        if not isinstance(data, dict):
            raise ConfigError("config.yaml 的 llm 段必须是键值映射结构")
    api_key = os.environ.get(APP_ENV_API_KEY) or str(data.get("api_key") or "")
    timeout_raw = data.get("timeout", 60)
    try:
        timeout_val = float(timeout_raw)
    except (TypeError, ValueError):
        raise ConfigError("config.yaml 的 llm.timeout 必须是数字（秒）") from None
    return LLMConfig(
        base_url=str(data.get("base_url") or "").strip(),
        api_key=api_key.strip(),
        model=str(data.get("model") or "").strip(),
        timeout=timeout_val,
    )
