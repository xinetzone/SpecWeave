"""XMNN bootstrap: sets up TVM environment before any tvm imports.
Installed to site-packages and activated via xmnn_bootstrap.pth.
"""
import os
import ctypes
import sys
from pathlib import Path

_pkg_dir = Path(__file__).parent.resolve()
_libs_dir = _pkg_dir / "_libs"

if _libs_dir.is_dir():
    os.environ["TVM_LIBRARY_PATH"] = str(_libs_dir)
    _ld = os.environ.get("LD_LIBRARY_PATH", "")
    _libs_path = str(_libs_dir)
    if _ld:
        os.environ["LD_LIBRARY_PATH"] = _libs_path + os.pathsep + _ld
    else:
        os.environ["LD_LIBRARY_PATH"] = _libs_path
    _tvm_lib = _libs_dir / "libtvm.so"
else:
    os.environ["TVM_LIBRARY_PATH"] = str(_pkg_dir)
    _ld = os.environ.get("LD_LIBRARY_PATH", "")
    if _ld:
        os.environ["LD_LIBRARY_PATH"] = str(_pkg_dir) + os.pathsep + _ld
    else:
        os.environ["LD_LIBRARY_PATH"] = str(_pkg_dir)
    _tvm_lib = _pkg_dir / "libtvm.so"

if sys.platform.startswith("linux"):
    def _load_libs_in_dir(lib_dir: Path):
        """Load all .so libraries in directory with RTLD_GLOBAL, retrying to resolve dependencies."""
        if not lib_dir.is_dir():
            return
        libs = sorted(lib_dir.glob("*.so*"))
        # Filter out directories and non-files
        libs = [lib for lib in libs if lib.is_file() and not lib.is_symlink() or lib.is_file()]
        loaded = set()
        # Retry up to len(libs) rounds to resolve cross-dependencies
        for _round in range(len(libs) + 1):
            remaining = [lib for lib in libs if lib.name not in loaded]
            if not remaining:
                break
            progress = False
            for lib in remaining:
                try:
                    ctypes.CDLL(str(lib), mode=ctypes.RTLD_GLOBAL)
                    loaded.add(lib.name)
                    progress = True
                except OSError:
                    pass
            if not progress:
                break
        return loaded

    try:
        if _libs_dir.is_dir():
            _load_libs_in_dir(_libs_dir)
        # Load libtvm.so last (after all dependencies)
        if _tvm_lib.exists():
            ctypes.CDLL(str(_tvm_lib), mode=ctypes.RTLD_GLOBAL)
    except OSError as e:
        import warnings
        warnings.warn(f"Failed to preload libs: {e}")

import ast

# 与 npuusertools/_xmnn_bootstrap.py 的同名哨兵共用 ast 模块属性：任一副本先
# 安装，另一副本的 install() 即为 no-op，杜绝双重包装/语义漂移。
_AST_ALIAS_FLAG = "_xmnn_ast_compat_applied"


def install():
    """幂等补回 CPython 3.12+ 移除的 ast 遗留节点别名。

    与语义真源 npuusertools/_xmnn_bootstrap.py 的 ``install()`` 同名同契约
    （``xmnn.vta_compat.apply_ast_compat`` 直接 ``from _xmnn_bootstrap
    import install`` 复用）；本简版补丁集覆盖 tvm py_converter 的
    ``from ast import`` 需求并额外恢复 Index/ExtSlice。

    Returns:
        bool: 本次调用是否实际执行安装（已安装返回 False）。
    """
    if getattr(ast, _AST_ALIAS_FLAG, False):
        return False
    if not hasattr(ast, "NameConstant"):
        class _NameConstant(ast.Constant):
            def __new__(cls, value=None, **kwargs):
                return super().__new__(cls, value=value, **kwargs)
        ast.NameConstant = _NameConstant
    if not hasattr(ast, "Num"):
        class _Num(ast.Constant):
            def __new__(cls, n=None, **kwargs):
                return super().__new__(cls, value=n, **kwargs)
        ast.Num = _Num
    if not hasattr(ast, "Str"):
        class _Str(ast.Constant):
            def __new__(cls, s='', **kwargs):
                return super().__new__(cls, value=s, **kwargs)
        ast.Str = _Str
    if not hasattr(ast, "Bytes"):
        class _Bytes(ast.Constant):
            def __new__(cls, s=b'', **kwargs):
                return super().__new__(cls, value=s, **kwargs)
        ast.Bytes = _Bytes
    if not hasattr(ast, "Index"):
        class _Index(ast.expr):
            _fields = ("value",)
            def __init__(self, value, **kwargs):
                self.value = value
                super().__init__(**kwargs)
        ast.Index = _Index
    if not hasattr(ast, "ExtSlice"):
        class _ExtSlice(ast.expr):
            _fields = ("dims",)
            def __init__(self, dims=None, **kwargs):
                self.dims = dims if dims is not None else []
                super().__init__(**kwargs)
        ast.ExtSlice = _ExtSlice
    setattr(ast, _AST_ALIAS_FLAG, True)
    return True


install()

# ── PEP 649 × Nuitka 类体注解闭包缺陷兜底（2026-10-08 实证）──────────────────
# 本块与 npuusertools/_xmnn_bootstrap.py 同名函数保持逐字一致（双副本契约）。
# Nuitka 4.2.1/4.2.2 编译「类体内定义类型别名、又被同类方法注解引用」的模块时，
# 为函数生成的 PEP 649 __annotate__ 闭包不捕获类命名空间中的该别名，
# 模块导入期 tvm 的 @type_checked → inspect.signature → annotationlib 按
# Format.VALUE 求值注解即抛 NameError，import tvm 整体失败。
# 全 tvm 源码树仅 3 处该模式（tir/schedule/schedule.py 的 AnnotationValueT、
# script/printer/doc.py 的 _IndexType、meta_schedule/.../space_generator.py 的
# ScheduleFnType）；CPython 纯源码执行语义正确，故严格只在 Nuitka 编译帧内兜底：
# 把该闭包的 NameError 降级为空注解——等价于对应参数未标注，@type_checked 跳过
# 其运行时类型分发，不影响 FFI 与功能（tvm 运行期分派基于真实实参类型）。
# 帧判定：co_name == "__annotate__" 且 Nuitka 伪文件名含 "$$$function"，
# 且属于本仓自有编译单元前缀 tvm$/vta$/xmnn$。真实源码 NameError 原样传播。
import sys as _sys

_NUITKA_ANNOTATE_MARK = "$$$function"
_NUITKA_OWN_PREFIXES = ("tvm$", "vta$", "xmnn$")
_ANNOTATE_FIX_FLAG = "_xmnn_nuitka_annotate_fix_applied"


def _nameerror_from_nuitka_annotate(exc):
    """判断 NameError 是否源自自有 Nuitka 单元的 __annotate__ 闭包缺名。"""
    tb = exc.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        filename = code.co_filename
        if (
            code.co_name == "__annotate__"
            and _NUITKA_ANNOTATE_MARK in filename
            and filename.startswith(_NUITKA_OWN_PREFIXES)
        ):
            return True
        tb = tb.tb_next
    return False


def install_nuitka_annotate_fix():
    """幂等地为 annotationlib 装上 Nuitka 注解闭包 NameError 兜底。

    仅包装标准库 annotationlib._get_dunder_annotations（inspect.signature
    经 Format.VALUE 路径求值函数注解的入口）；3.13 及更早没有该符号时 no-op。

    Returns:
        bool: 本次调用是否实际执行了安装（已安装或不适用均返回 False）。
    """
    if getattr(_sys, _ANNOTATE_FIX_FLAG, False):
        return False
    try:
        import annotationlib as _annotationlib

        _original = _annotationlib._get_dunder_annotations
    except (ImportError, AttributeError):
        return False
    if getattr(_original, "_xmnn_nuitka_wrapper", False):
        setattr(_sys, _ANNOTATE_FIX_FLAG, True)
        return False

    def _safe_get_dunder_annotations(obj):
        try:
            return _original(obj)
        except NameError as exc:
            if _nameerror_from_nuitka_annotate(exc):
                return {}
            raise

    _safe_get_dunder_annotations._xmnn_nuitka_wrapper = True
    _annotationlib._get_dunder_annotations = _safe_get_dunder_annotations
    setattr(_sys, _ANNOTATE_FIX_FLAG, True)
    return True


install_nuitka_annotate_fix()
