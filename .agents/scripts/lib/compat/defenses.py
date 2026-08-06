#!/usr/bin/env python3
"""
反模式防御代码模板
=====================
提供8大反模式的防御工具函数与装饰器，可直接在项目中复用。

每个防御函数都包含：
- 反模式描述
- 问题代码示例
- 防御实现
- 使用示例
"""
from __future__ import annotations


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import sys
import functools
import inspect
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypeVar, ParamSpec, Concatenate

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


# ----------------------------------------------------------------------------
# 防御1：可变默认值陷阱 (Mutable Default Argument)
# ----------------------------------------------------------------------------

def mutable_default_fix(default_factory: Callable[[], T]) -> T:
    """
    防御可变默认值反模式，提供类型安全的替代方案。

    ❌ 反模式（不要这样写）:
        def bad(items=[]):
            items.append(1)
            return items

    ✅ 防御模式（正确写法）:
        def good(items=None):
            items = items if items is not None else []
            items.append(1)
            return items

        # 或使用 Sentinel 值 + 本装饰器（更优雅）
    """
    sentinel = object()

    def decorator(func: Callable[Concatenate[Any, P], R]) -> Callable[Concatenate[Any, P], R]:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> R:
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()
            for param_name, param in sig.parameters.items():
                if param.default is sentinel:
                    if param_name not in kwargs or kwargs[param_name] is sentinel:
                        bound.arguments[param_name] = default_factory()
            return func(*bound.args, **bound.kwargs)

        return wrapper

    return sentinel  # type: ignore[return-value]


class _Sentinel:
    """哨兵值，用于检测参数是否被显式传入"""
    def __repr__(self) -> str:
        return "<Sentinel>"


NOT_PROVIDED = _Sentinel()


def guard_mutable_default(value: T | _Sentinel, factory: Callable[[], T]) -> T:
    """
    运行时防御可变默认值。

    用法：
        def append_item(item, lst=NOT_PROVIDED):
            lst = guard_mutable_default(lst, list)
            lst.append(item)
            return lst
    """
    if isinstance(value, _Sentinel):
        return factory()
    return value


# ----------------------------------------------------------------------------
# 防御2：循环导入检测
# ----------------------------------------------------------------------------

_import_stack: list[str] = []
_circular_import_detected = False


def detect_circular_import(module_name: str) -> bool:
    """
    检测循环导入（调试用）。

    用法：在模块顶部添加
        from lib.compat.defenses import detect_circular_import
        detect_circular_import(__name__)

    循环导入发生时会打印警告但不阻止导入（生产环境可关闭）。
    """
    global _circular_import_detected
    if module_name in _import_stack:
        cycle = " → ".join(_import_stack[_import_stack.index(module_name):] + [module_name])
        warnings.warn(
            f"⚠️  检测到循环导入: {cycle}\n"
            f"   解决方案：\n"
            f"   1. 将共享类型提取到独立的 types.py 模块\n"
            f"   2. 在函数内部延迟导入（import inside function）\n"
            f"   3. 使用依赖注入模式",
            ImportWarning,
            stacklevel=2
        )
        _circular_import_detected = True
        return True
    _import_stack.append(module_name)
    return False


# ----------------------------------------------------------------------------
# 防御3：大对象 repr 爆炸防御（numpy数组、大列表等）
# ----------------------------------------------------------------------------

def safe_repr(obj: Any, max_length: int = 200) -> str:
    """
    安全repr，防止大对象（numpy数组、长列表、大字典）导致日志爆炸。

    ❌ 反模式:
        @dataclass
        class Bad:
            weights: np.ndarray  # repr会打印整个数组，可能几MB！

    ✅ 防御:
        @dataclass
        class Good:
            weights: np.ndarray = field(repr=False)  # 不打印
            # 或自定义__repr__调用 safe_repr
    """
    r = repr(obj)
    if len(r) > max_length:
        return f"{r[:max_length]}...(truncated, total {len(r)} chars)"
    return r


# ----------------------------------------------------------------------------
# 防御4：静态初始化顺序问题 (Static Initialization Order Fiasco)
# ----------------------------------------------------------------------------

class LazyInit:
    """
    延迟初始化装饰器，解决跨模块全局变量初始化顺序问题。

    ❌ 反模式:
        # config.py
        SETTINGS = load_settings()  # 可能依赖其他模块的全局变量

        # main.py
        from config import SETTINGS  # 导入时机可能不对

    ✅ 防御:
        # config.py
        @LazyInit
        def SETTINGS():
            return load_settings()

        # 使用时: SETTINGS() 首次访问才初始化
    """

    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._value: T | None = None
        self._initialized = False
        functools.update_wrapper(self, factory)

    def __call__(self) -> T:
        if not self._initialized:
            self._value = self._factory()
            self._initialized = True
        return self._value  # type: ignore[return-value]

    def reset(self) -> None:
        """重置（仅用于测试）"""
        self._value = None
        self._initialized = False


# ----------------------------------------------------------------------------
# 防御5：异常吞噬防御 (Exception Swallowing)
# ----------------------------------------------------------------------------

@dataclass
class ErrorHandler:
    """
    结构化异常处理，禁止裸 except: 吞噬所有异常。

    ❌ 反模式:
        try:
            risky_op()
        except:  # 会吞掉 KeyboardInterrupt、SystemExit！
            pass

    ✅ 防御:
        with ErrorHandler(context="file load", allowed_exceptions=(IOError, ValueError)):
            risky_op()
    """
    context: str = ""
    allowed_exceptions: tuple[type[BaseException], ...] = (Exception,)
    log_warning: bool = True
    reraise: bool = False

    def __enter__(self) -> "ErrorHandler":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            return False
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit, MemoryError)):
            return False  # 永远不要吞噬这些致命异常
        if not issubclass(exc_type, self.allowed_exceptions):
            return False
        if self.log_warning:
            import logging
            logging.warning(
                f"[{self.context}] 捕获异常: {exc_type.__name__}: {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb) if self.reraise else False
            )
        return not self.reraise


# ----------------------------------------------------------------------------
# 防御6：资源泄漏防御 (RAII / Context Manager)
# ----------------------------------------------------------------------------

class ResourceGuard:
    """
    通用资源守卫，确保资源（文件句柄、锁、连接）在异常时也能正确释放。

    用法：
        with ResourceGuard(
            acquire=lambda: open("file.txt"),
            release=lambda f: f.close()
        ) as f:
            f.read()
    """

    def __init__(self, acquire: Callable[[], T], release: Callable[[T], None]):
        self._acquire = acquire
        self._release = release
        self._resource: T | None = None

    def __enter__(self) -> T:
        self._resource = self._acquire()
        return self._resource

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._resource is not None:
            try:
                self._release(self._resource)
            except Exception:
                pass  # 释放异常不掩盖原始异常
        return False


# ----------------------------------------------------------------------------
# 防御7：隐式类型转换陷阱防御
# ----------------------------------------------------------------------------

def _strict_zip_polyfill(*iterables, strict: bool = True):
    """strict_zip 的Python 3.9及以下版本polyfill实现"""
    iterators = [iter(it) for it in iterables]
    while True:
        values = []
        for i, it in enumerate(iterators):
            try:
                values.append(next(it))
            except StopIteration:
                if i == 0 and not values:
                    if strict and any(list(it) for it in iterators[i+1:]):
                        raise ValueError("zip() arguments have different lengths")
                    return
                if strict:
                    raise ValueError("zip() arguments have different lengths")
                return
        yield tuple(values)


def strict_zip(*iterables, strict: bool = True):
    """
    严格zip，长度不一致时抛出ValueError（Python 3.10+ 内置，此为兼容实现）。

    ❌ 反模式:
        for a, b in zip([1,2,3], [4,5]):  # 3被静默丢弃！
            print(a, b)

    ✅ 防御:
        for a, b in strict_zip([1,2,3], [4,5]):  # 抛出 ValueError
            ...
    """
    if sys.version_info >= (3, 10):
        return zip(*iterables, strict=strict)
    return _strict_zip_polyfill(*iterables, strict=strict)


def checked_int(value: Any, field_name: str = "value") -> int:
    """
    安全整数转换，禁止浮点数隐式截断。

    ❌ 反模式:
        n = int(3.9)  # 得到 3，静默丢失0.9

    ✅ 防御:
        n = checked_int(3.9, "count")  # 抛出 TypeError
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise TypeError(
            f"{field_name}={value!r} 是浮点数，禁止隐式截断为整数。"
            f"请显式使用 int(round({value})) 或 math.trunc({value})"
        )
    return int(value)


# ----------------------------------------------------------------------------
# 防御8：命名空间污染/全局状态防御
# ----------------------------------------------------------------------------

def frozen_config(cls: type[T]) -> type[T]:
    """
    不可变配置类装饰器，推荐直接使用 @dataclass(frozen=True) 代替。
    本装饰器用于非dataclass场景。

    ❌ 反模式:
        CONFIG = {"debug": False}
        CONFIG["debug"] = True  # 任何地方都能改，难以追踪

    ✅ 防御:
        @frozen_config
        class Config:
            debug: bool = False
            port: int = 8080

        CONFIG = Config()
        CONFIG.debug = True  # 抛出 AttributeError
    """
    original_setattr = cls.__setattr__

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False) and name != "_frozen":
            raise AttributeError(
                f"不可变配置对象不允许修改 {name!r}。"
            )
        original_setattr(self, name, value)

    original_init = cls.__init__

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        object.__setattr__(self, "_frozen", True)

    def replace(self, **kwargs):
        new_kwargs = {k: getattr(self, k) for k in vars(self) if not k.startswith("_")}
        new_kwargs.update(kwargs)
        return type(self)(**new_kwargs)

    cls.__setattr__ = __setattr__
    cls.__init__ = __init__
    cls.replace = replace
    return cls


ImmutableConfig = frozen_config  # 别名，方便理解


class ThreadLocalState:
    """
    线程局部状态容器，避免全局变量在多线程下的竞争问题。
    """

    def __init__(self):
        import threading
        self._local = threading.local()

    def get(self, key: str, default: T = None) -> T:
        return getattr(self._local, key, default)

    def set(self, key: str, value: Any) -> None:
        setattr(self._local, key, value)

    def clear(self) -> None:
        self._local.__dict__.clear()


# ----------------------------------------------------------------------------
# 防御代码快速索引表
# ----------------------------------------------------------------------------

DEFENSE_CHEAT_SHEET: dict[str, dict[str, str]] = {
    "mutable_defaults": {
        "bad": "def f(x=[]): ...",
        "good": "def f(x=None):\n    x = x or []\n    ...",
        "helper": "guard_mutable_default(x, list)",
    },
    "circular_imports": {
        "bad": "# a.py imports b.py; b.py imports a.py at top level",
        "good": "# move import inside function, or extract types to types.py",
        "helper": "detect_circular_import(__name__)",
    },
    "repr_explosion": {
        "bad": "@dataclass\nclass C:\n    big_array: np.ndarray",
        "good": "field(repr=False) on large fields",
        "helper": "safe_repr(obj, max_length=200)",
    },
    "init_order": {
        "bad": "MODULE_CONST = compute_at_import_time()",
        "good": "@LazyInit\ndef MODULE_CONST(): ...",
        "helper": "LazyInit decorator",
    },
    "bare_except": {
        "bad": "try: ...\nexcept: pass",
        "good": "except SpecificError: ...",
        "helper": "with ErrorHandler(allowed_exceptions=(IOError,)):",
    },
    "resource_leak": {
        "bad": "f = open('file')\nf.read()  # no close if exception",
        "good": "with open('file') as f: ...",
        "helper": "ResourceGuard(acquire, release)",
    },
    "implicit_conversion": {
        "bad": "n = int(3.9)  # silent truncation to 3",
        "good": "n = int(round(3.9))",
        "helper": "checked_int(value, field_name)",
    },
    "global_mutable_state": {
        "bad": "CONFIG = {}; CONFIG['x'] = 1",
        "good": "ImmutableConfig dataclass, ThreadLocalState for thread-local",
        "helper": "ImmutableConfig / ThreadLocalState",
    },
}


__all__ = [
    "NOT_PROVIDED",
    "guard_mutable_default",
    "detect_circular_import",
    "safe_repr",
    "LazyInit",
    "ErrorHandler",
    "ResourceGuard",
    "strict_zip",
    "checked_int",
    "ImmutableConfig",
    "ThreadLocalState",
    "DEFENSE_CHEAT_SHEET",
]

