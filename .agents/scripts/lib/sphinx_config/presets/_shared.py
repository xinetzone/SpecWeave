from collections.abc import Callable, Mapping
from typing import Any


_COMMON_KEY_DEFAULTS: dict[str, Any] = {
    "project": "Untitled Project",
    "author": "Unknown Author",
    "release": "0.1.0",
    "version": "0.1.0",
    "language": "en",
    "html_title": None,
    "html_theme": "alabaster",
    "html_theme_options": None,
    "extensions": (),
}


def build_project_meta(
    params: Mapping[str, Any],
    key_defaults: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """构建 preset 的标准 project_meta 字典（按 key_defaults 填默认 + params 白名单覆盖）。

    遵循 PRESET-SETUP 模式：白名单机制只覆盖已知键，防止 params 拼错字段时静默丢失——
    例如误写为 ``projecT`` 时不会出现在返回字典中，在类型检查或 Sphinx 配置层能暴露错误。
    """
    d = dict(_COMMON_KEY_DEFAULTS)
    if key_defaults:
        d.update(key_defaults)
    for key, value in params.items():
        if key in d:
            d[key] = value
    if d["html_title"] is None:
        d["html_title"] = d["project"]
    if d["html_theme_options"] is None:
        d["html_theme_options"] = {}
    return d


def build_setup_closure(
    register_fns: list[Callable[[Any], None]] | tuple[Callable[[Any], None], ...],
    user_setup: Callable[[Any], None] | None = None,
) -> Callable[[Any], None]:
    """生成标准执行顺序的 setup 闭包：``for fn in register_fns: fn(app) → user_setup(app)``。

    所有 preset 的 ``merged["setup"]`` 必须通过本函数生成，保证执行顺序是单一可信源
    （PRESET-SETUP 模式核心：避免 N 处 copy 导致顺序改漏）。
    """

    def _setup(app: Any) -> None:
        for fn in register_fns:
            fn(app)
        if callable(user_setup):
            user_setup(app)

    return _setup
