import importlib.util
from typing import Any


def has_module(mod: str) -> bool:
    """探测模块是否可导入，不触发模块副作用。

    等价于原 conf.py 的 ``_has()``，但作为公共 API 导出供外部调用。
    基于 :func:`importlib.util.find_spec`，比 ``try-import`` 更轻量，
    不会触发被探测模块的顶层代码执行。
    """
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ModuleNotFoundError):
        return False


def deep_merge(base: dict[str, Any], override: dict[str, Any] | None = None,
               *, remove_marker: Any = None) -> dict[str, Any]:
    """分层合并配置字典（公理 A1 实现）。

    规则：
    * ``override`` 中存在的键覆盖 ``base`` 同键；
    * 值为 ``remove_marker``（默认 ``None``）的键**显式表示「从 base 中删除该键」——
      注意这与 Sphinx 原生「某键 = None 表示使用 Sphinx 默认」语义不同。
      若想表达「将某键显式置为 None 交给 Sphinx 默认处理」，请传
      ``sentinel`` 对象或其他非 ``remove_marker`` 的值；
    * 嵌套字典递归合并，其他类型直接替换。
    """
    override = override or {}
    result: dict[str, Any] = {}
    for k, v in base.items():
        if k in override and override[k] is remove_marker:
            continue
        if isinstance(v, dict) and k in override and isinstance(override[k], dict):
            result[k] = deep_merge(v, override[k], remove_marker=remove_marker)
        elif k in override:
            result[k] = override[k]
        else:
            result[k] = v
    for k, v in override.items():
        if k not in result and v is not remove_marker:
            result[k] = v
    return result
