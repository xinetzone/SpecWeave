"""flexloop 子模块运行时沙箱工具。

提供自有协作子模块(flexloop)的安全运行环境，包括：
- FLEXLOOP_AVAILABLE: 检测子模块是否已初始化
- conditional_import(): 条件导入 flexloop 模块
- run_flexloop_script(): 在沙箱环境中运行 flexloop 脚本

## 使用方式

在 `.agents/scripts/` 下的脚本中导入：

```python
from lib.vendor_sandbox import FLEXLOOP_AVAILABLE, conditional_import, run_flexloop_script

if FLEXLOOP_AVAILABLE:
    # 条件导入 flexloop 模块
    some_module = conditional_import("some_module")
    if some_module:
        some_module.do_something()

    # 运行 flexloop 脚本
    result = run_flexloop_script(".agents/scripts/check_gitignore.py")
    print(result.stdout)
```

**注意**：
- FLEXLOOP_AVAILABLE 为 False 时，所有功能不可用
- conditional_import() 不会永久修改 sys.path
- run_flexloop_script() 在子进程中运行，提供逻辑隔离
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

_MODULE_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _MODULE_DIR.parent
_AGENTS_DIR = _SCRIPTS_DIR.parent
PROJECT_ROOT = _AGENTS_DIR.parent

VENDOR_DIR = PROJECT_ROOT / "vendor"
FLEXLOOP_DIR = VENDOR_DIR / "flexloop"
TEMP_DIR = PROJECT_ROOT / ".temp"

FLEXLOOP_AVAILABLE: bool = (
    (FLEXLOOP_DIR / ".git").is_file()
    and (FLEXLOOP_DIR / "AGENTS.md").exists()
)


def conditional_import(
    module_name: str,
    submodule: str = "vendor/flexloop",
) -> ModuleType | None:
    """尝试导入指定模块，如果失败返回 None。

    临时将 submodule 目录加入 sys.path，导入完成后恢复，
    不会永久修改 sys.path。

    Args:
        module_name: 要导入的模块名称。
        submodule: 子模块相对路径（相对于项目根目录）。

    Returns:
        导入成功返回模块对象，失败返回 None。
    """
    if not FLEXLOOP_AVAILABLE:
        return None

    submodule_path = str(PROJECT_ROOT / submodule)
    path_inserted = False

    try:
        if submodule_path not in sys.path:
            sys.path.insert(0, submodule_path)
            path_inserted = True

        return importlib.import_module(module_name)
    except (ImportError, ModuleNotFoundError):
        return None
    finally:
        if path_inserted and submodule_path in sys.path:
            sys.path.remove(submodule_path)


def run_flexloop_script(
    script_path: str,
    args: list[str] | None = None,
    cwd: Path | str | None = None,
    *,
    python_executable: str | None = None,
    allowed_write_dirs: list[Path] | None = None,
    timeout: int = 60,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """在子进程中运行 flexloop 目录下的脚本。

    提供逻辑隔离的沙箱环境：
    - 自动设置工作目录为 vendor/flexloop/
    - 不继承 PYTHONPATH 环境变量
    - 设置 PATH 为当前 Python 环境 + 系统 PATH
    - 子进程超时控制

    Args:
        script_path: flexloop 内的脚本相对路径（如 ".agents/scripts/check_gitignore.py"）。
        args: 传递给脚本的命令行参数列表。
        cwd: 工作目录，默认为 vendor/flexloop/。
        python_executable: Python 解释器路径，默认为 sys.executable。
        allowed_write_dirs: 允许写入的目录列表（当前为逻辑标记，预留扩展）。
        timeout: 超时秒数，默认 60 秒。
        env: 额外环境变量（合并到当前环境）。

    Returns:
        subprocess.CompletedProcess（stdout/stderr 为 text 模式）。

    Raises:
        RuntimeError: flexloop 子模块未初始化时抛出。
        FileNotFoundError: 脚本文件不存在时抛出。
        subprocess.TimeoutExpired: 脚本执行超时时抛出。
    """
    if not FLEXLOOP_AVAILABLE:
        raise RuntimeError("flexloop 子模块未初始化")

    script_full_path = FLEXLOOP_DIR / script_path
    if not script_full_path.is_file():
        raise FileNotFoundError(f"脚本不存在: {script_full_path}")

    if cwd is None:
        work_dir = FLEXLOOP_DIR
    else:
        work_dir = Path(cwd)
        if not work_dir.is_absolute():
            work_dir = FLEXLOOP_DIR / work_dir

    if python_executable is None:
        py_exe = sys.executable
    else:
        py_exe = python_executable

    if allowed_write_dirs is None:
        allowed_write_dirs = [FLEXLOOP_DIR, TEMP_DIR]

    cmd = [py_exe, str(script_full_path)]
    if args:
        cmd.extend(args)

    run_env = os.environ.copy()

    run_env.pop("PYTHONPATH", None)
    run_env.pop("PYTHONHOME", None)

    python_dir = Path(py_exe).parent
    scripts_dir = python_dir / "Scripts"
    if scripts_dir.exists():
        path_sep = os.pathsep
        existing_path = run_env.get("PATH", "")
        run_env["PATH"] = f"{scripts_dir}{path_sep}{python_dir}{path_sep}{existing_path}"

    if env:
        run_env.update(env)

    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW

    return subprocess.run(
        cmd,
        cwd=str(work_dir),
        env=run_env,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=creationflags,
    )
