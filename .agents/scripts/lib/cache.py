"""缓存读写工具。

提供跨脚本复用的 JSON 缓存加载/保存能力，支持原子写入和过期元数据。
"""


# 版本校验：相对导入共享库（depth=0）
from .python310_version_check import enforce_python310

enforce_python310()

from datetime import datetime
from pathlib import Path

from lib.atomic_write import atomic_write_json

DEFAULT_CACHE_DIR = ".agents/cache"


def get_cache_path(
    project_root: Path,
    cache_file_name: str,
    cache_dir_name: str = DEFAULT_CACHE_DIR,
) -> Path:
    """获取缓存文件路径，必要时创建目录。

    Args:
        project_root: 项目根目录。
        cache_file_name: 缓存文件名（如 "external-links-cache.json"）。
        cache_dir_name: 缓存目录名（默认 ".agents/cache"）。

    Returns:
        缓存文件的绝对路径。
    """
    cache_dir = project_root / cache_dir_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / cache_file_name


def load_cache(cache_path: Path) -> dict:
    """从 JSON 文件加载缓存。

    Args:
        cache_path: 缓存文件路径。

    Returns:
        缓存字典，文件不存在或解析失败时返回空字典。
    """
    if not cache_path.exists():
        return {}
    try:
        import json
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache_path: Path, cache: dict, ttl_days: int = 7) -> None:
    """以原子写入方式保存缓存，附带元数据。

    Args:
        cache_path: 缓存文件路径。
        cache: 要保存的缓存字典（会被原地修改，添加 _metadata 字段）。
        ttl_days: 缓存有效期天数。
    """
    cache["_metadata"] = {
        "updated_at": datetime.now().isoformat(),
        "ttl_days": ttl_days,
    }
    atomic_write_json(cache_path, cache, ensure_ascii=False, indent=2)
