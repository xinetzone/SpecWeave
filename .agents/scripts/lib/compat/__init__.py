#!/usr/bin/env python3
"""
依赖裁剪适配层 (Dependency Shimming Layer)
=============================================
提供统一的第三方库导入接口，实现：
1. 可选依赖的优雅降级（缺失时给出友好提示而非崩溃）
2. 跨版本API兼容（如 tomllib/tomli、yaml 不同版本）
3. 标准库命名空间冲突防御
4. 延迟导入减少启动开销

设计原则（参考Caffe依赖裁剪实践）：
- ✅ 所有第三方库通过本层导入，禁止直接 import 第三方包
- ✅ 依赖缺失时抛出 DependencyMissingError 而非 ImportError，包含安装指引
- ✅ 跨Python版本兼容（3.9-3.12+）
- ✅ 避免与标准库重名（不使用 `types`、`io`、`parser` 等作为模块名）

使用方式：
```python
from lib.compat import yaml, toml, openpyxl, requests, np

# 或使用安全导入函数
from lib.compat import safe_import, DependencyMissingError

try:
    import pandas as pd
except DependencyMissingError as e:
    print(f"可选功能不可用: {e}")
```
"""
from __future__ import annotations

import sys
import importlib
from types import ModuleType
from typing import Any, Callable, Optional


class DependencyMissingError(ImportError):
    """依赖缺失异常，包含友好的安装指引"""

    def __init__(self, package_name: str, import_name: str | None = None,
                 install_hint: str | None = None, purpose: str | None = None):
        self.package_name = package_name
        self.import_name = import_name or package_name
        self.purpose = purpose
        install_cmd = install_hint or f"pip install {package_name}"
        msg_parts = [
            f"❌ 缺少可选依赖: {package_name}",
        ]
        if purpose:
            msg_parts.append(f"   用途: {purpose}")
        msg_parts.append(f"   安装: {install_cmd}")
        super().__init__("\n".join(msg_parts))


class _LazyModule(ModuleType):
    """延迟导入模块代理，首次访问属性时才真正导入"""

    def __init__(self, name: str, package_name: str, install_hint: str | None = None,
                 purpose: str | None = None, fallback: Any = None):
        super().__init__(name)
        self._package_name = package_name
        self._install_hint = install_hint
        self._purpose = purpose
        self._fallback = fallback
        self._module: ModuleType | None = None
        self._loaded = False

    def _load(self) -> ModuleType:
        if not self._loaded:
            try:
                self._module = importlib.import_module(self.__name__)
            except ImportError:
                if self._fallback is not None:
                    self._module = self._fallback
                else:
                    raise DependencyMissingError(
                        self._package_name,
                        install_hint=self._install_hint,
                        purpose=self._purpose,
                    ) from None
            self._loaded = True
        return self._module  # type: ignore[return-value]

    def __getattr__(self, name: str) -> Any:
        module = self._load()
        return getattr(module, name)

    def __dir__(self) -> list[str]:
        module = self._load()
        return dir(module)

    def __repr__(self) -> str:
        if self._loaded and self._module is not None:
            return repr(self._module)
        return f"<LazyModule {self.__name__!r} (not loaded)>"


def safe_import(
    module_name: str,
    package_name: str | None = None,
    install_hint: str | None = None,
    purpose: str | None = None,
    fallback: Any = None,
) -> Any:
    """
    安全导入第三方库，失败时返回 fallback 或抛出 DependencyMissingError

    Args:
        module_name: 要导入的模块名（如 'yaml', 'openpyxl'）
        package_name: pip包名（如 'PyYAML'，与module_name不同时需指定）
        install_hint: 自定义安装命令
        purpose: 依赖用途描述
        fallback: 导入失败时的回退对象（None则抛出异常）

    Returns:
        导入的模块或 fallback 对象

    Raises:
        DependencyMissingError: 依赖缺失且无fallback时
    """
    pkg = package_name or module_name
    try:
        return importlib.import_module(module_name)
    except ImportError:
        if fallback is not None:
            return fallback
        raise DependencyMissingError(pkg, module_name, install_hint, purpose) from None


# ----------------------------------------------------------------------------
# TOML 兼容层：Python 3.11+ 使用标准库 tomllib，旧版本使用 tomli
# ----------------------------------------------------------------------------

def _init_toml() -> ModuleType:
    """初始化TOML模块，跨版本兼容"""
    if sys.version_info >= (3, 11):
        import tomllib as _toml
        _toml.loads = _toml.loads  # type: ignore[attr-defined]
        _toml.dumps = None  # type: ignore[attr-defined]
        return _toml
    else:
        try:
            import tomli as _toml
            try:
                import tomli_w as _toml_w
                _toml.dumps = _toml_w.dumps  # type: ignore[attr-defined]
                _toml.dump = _toml_w.dump  # type: ignore[attr-defined]
            except ImportError:
                _toml.dumps = None  # type: ignore[attr-defined]
                _toml.dump = None  # type: ignore[attr-defined]
            return _toml
        except ImportError:
            raise DependencyMissingError(
                "tomli",
                install_hint="pip install tomli tomli-w",
                purpose="TOML配置文件解析（Python 3.11以下版本需要）",
            ) from None


toml: ModuleType = _init_toml()


# ----------------------------------------------------------------------------
# YAML 适配层：统一 PyYAML 导入
# ----------------------------------------------------------------------------

yaml: ModuleType = _LazyModule(
    "yaml",
    package_name="PyYAML",
    install_hint="pip install pyyaml",
    purpose="YAML文件解析（frontmatter、配置文件）",
)


# ----------------------------------------------------------------------------
# openpyxl 适配层：Excel文件处理
# ----------------------------------------------------------------------------

openpyxl: ModuleType = _LazyModule(
    "openpyxl",
    package_name="openpyxl",
    install_hint="pip install openpyxl",
    purpose="Excel(.xlsx)文件读写（analyze-xlsx等功能）",
)


# ----------------------------------------------------------------------------
# requests 适配层：HTTP请求（链接检查、API调用）
# ----------------------------------------------------------------------------

requests: ModuleType = _LazyModule(
    "requests",
    package_name="requests",
    install_hint="pip install requests",
    purpose="HTTP网络请求（链接检查、外部API）",
)


# ----------------------------------------------------------------------------
# numpy 适配层：数值计算
# ----------------------------------------------------------------------------

np: ModuleType = _LazyModule(
    "numpy",
    package_name="numpy",
    install_hint="pip install numpy",
    purpose="数值计算（数据分析、测试辅助）",
)


# ----------------------------------------------------------------------------
# pytest 适配层：测试框架（仅在测试场景需要）
# ----------------------------------------------------------------------------

pytest: ModuleType = _LazyModule(
    "pytest",
    package_name="pytest",
    install_hint="pip install pytest",
    purpose="单元测试运行",
)


# ----------------------------------------------------------------------------
# 标准库冲突防御：避免导入与标准库重名的本地模块
# ----------------------------------------------------------------------------

STDLIB_CONFLICT_NAMES: frozenset[str] = frozenset({
    "types", "io", "os", "sys", "re", "json", "math", "time", "datetime",
    "pathlib", "argparse", "subprocess", "collections", "functools", "itertools",
    "typing", "dataclasses", "enum", "abc", "copy", "pprint", "logging",
    "threading", "multiprocessing", "socket", "http", "urllib", "email",
    "html", "xml", "csv", "configparser", "hashlib", "hmac", "secrets",
    "string", "textwrap", "unicodedata", "struct", "codecs",
})


def is_stdlib_name(name: str) -> bool:
    """检查模块名是否与标准库冲突"""
    base_name = name.split(".")[0]
    return base_name in STDLIB_CONFLICT_NAMES


def require_dependency(package_name: str, purpose: str | None = None) -> None:
    """
    断言依赖存在，不存在则抛出带提示的异常

    用于命令入口处提前检查依赖，避免执行到一半才崩溃。

    Example:
        def main():
            require_dependency("openpyxl", "Excel文件分析")
            # ... 后续逻辑
    """
    try:
        importlib.import_module(package_name)
    except ImportError:
        raise DependencyMissingError(package_name, purpose=purpose) from None


__all__ = [
    "DependencyMissingError",
    "_LazyModule",
    "safe_import",
    "require_dependency",
    "is_stdlib_name",
    "STDLIB_CONFLICT_NAMES",
    "toml",
    "yaml",
    "openpyxl",
    "requests",
    "np",
    "pytest",
]
