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
