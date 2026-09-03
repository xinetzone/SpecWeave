"""公共工具函数。

- `has_module`：直接来自 :mod:`mystx.utils`（F-001 事实，字节级一致）
- `deep_merge`：包装 mystx 的两参数版本为 `deep_merge(*dicts)` 多参数形式，
  保持 sphinx_config 原有签名兼容性
- `ensure_mystx_on_syspath`：D1 维度 sphinx_config 独有的路径自举——
  逐级向上搜索 git submodule ``projects/xuanspace/libs/mystx/src`` 注入 sys.path
"""

import sys
from pathlib import Path


def ensure_mystx_on_syspath(anchor: str | None = None) -> Path | None:
    """从 anchor 逐级向上查 ``projects/xuanspace/libs/mystx/src``，找到则注入 sys.path。

    Returns
    -------
    Path | None
        成功注入时返回已加入 sys.path 的 mystx src 根目录；未找到则 ``None``。
    """
    anchor_path = Path(anchor or __file__).resolve()
    mystx_src: Path | None = None
    for parent in anchor_path.parents:
        candidate = parent / "projects" / "xuanspace" / "libs" / "mystx" / "src"
        if (candidate / "mystx" / "__init__.py").exists():
            mystx_src = candidate
            break
        candidate2 = parent.parent / "xuanspace" / "libs" / "mystx" / "src"
        if (candidate2 / "mystx" / "__init__.py").exists():
            mystx_src = candidate2
            break
    if mystx_src is not None:
        mystx_str = str(mystx_src)
        if mystx_str not in sys.path:
            sys.path.insert(0, mystx_str)
        return mystx_src
    return None


ensure_mystx_on_syspath(__file__)

from mystx.utils import deep_merge as _mystx_deep_merge, has_module  # noqa: E402


def deep_merge(*dicts: dict) -> dict:
    """多参数递归字典合并（保持 sphinx_config 原有签名）。

    底层实现来自 mystx.utils.deep_merge：依次将每个 dict 从左向右合并，
    遇到值为 ``None`` 的键表示「删除」语义（remove_marker）。
    嵌套字典递归合并，其他类型直接替换。

    Examples
    --------
    >>> deep_merge({'a': 1, 'nested': {'x': 1}}, {'nested': {'y': 2}}, {'b': 3})
    {'a': 1, 'b': 3, 'nested': {'x': 1, 'y': 2}}
    """
    if not dicts:
        return {}
    result = dict(dicts[0])
    for d in dicts[1:]:
        result = _mystx_deep_merge(result, d)
    return result


__all__ = ["has_module", "deep_merge", "ensure_mystx_on_syspath"]
