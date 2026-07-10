---
id: "temporary-syspath-modification"
source: "../../reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/insight-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/temporary-syspath-modification.toml"
---
# 临时 sys.path 修改：条件导入可选依赖的安全模式

## 模式概述

导入不在默认 sys.path 中的可选模块（如 vendor 子模块、可选插件）时，临时修改 sys.path 完成导入，然后立即恢复原状。避免永久修改全局 sys.path 导致的模块名遮蔽、导入顺序依赖等问题。

## 问题现象

为了导入 vendor/flexloop 中的模块，常见的错误做法是永久修改 sys.path：

```python
# ❌ 反模式：永久污染 sys.path
import sys
sys.path.insert(0, "vendor/flexloop")
import apps.chaos.src.taolib.cli as flexloop_cli

# 问题：
# 1. 所有后续 import 都会搜索 vendor/flexloop，可能导致模块名冲突
# 2. 如果 flexloop 内有与标准库同名的模块（如 utils、common），会错误导入
# 3. 其他模块的导入行为依赖于这行代码是否被执行，产生隐式依赖
# 4. 异常时 sys.path 无法恢复
```

## 解决方案：临时插入 + 无条件恢复

使用 try/finally 确保 sys.path 总是被恢复，无论导入成功还是失败：

```python
"""vendor_sandbox.py - 可选依赖条件导入工具。"""
import sys
import importlib
from pathlib import Path
from typing import Optional, Any

# 从当前文件位置推算项目根目录（避免链式 parent 错误，参见 path-anchor-semantization）
_MODULE_DIR = Path(__file__).resolve().parent
_LIB_DIR = _MODULE_DIR.parent
_SCRIPTS_DIR = _LIB_DIR.parent
_AGENTS_DIR = _SCRIPTS_DIR.parent
PROJECT_ROOT = _AGENTS_DIR.parent

VENDOR_DIR = PROJECT_ROOT / "vendor"
FLEXLOOP_DIR = VENDOR_DIR / "flexloop"

# 检测子模块是否可用（注意：submodule 的 .git 是文件指针，不是目录！）
FLEXLOOP_AVAILABLE: bool = (
    FLEXLOOP_DIR.exists()
    and (FLEXLOOP_DIR / ".git").exists()
    and (FLEXLOOP_DIR / ".git").is_file()  # 关键：.is_file() 而非 .is_dir()
    and (FLEXLOOP_DIR / "AGENTS.md").exists()
)


def conditional_import(module_name: str, submodule_path: Path = FLEXLOOP_DIR) -> Optional[Any]:
    """
    条件导入模块，失败返回 None，不污染全局 sys.path。

    Args:
        module_name: 要导入的模块名（如 "apps.chaos.src.taolib.cli"）
        submodule_path: 子模块目录路径

    Returns:
        导入成功返回模块对象，失败返回 None
    """
    if not submodule_path.exists():
        return None

    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(submodule_path))
        return importlib.import_module(module_name)
    except (ImportError, ModuleNotFoundError):
        return None
    finally:
        # 无条件恢复 sys.path，即使导入时发生异常
        sys.path = original_path
```

## 关键要点

### 1. copy() 保存原始路径

```python
original_path = sys.path.copy()
```

列表是可变对象，直接赋值 `original_path = sys.path` 只是创建引用，不会保存快照。必须用 `copy()` 创建浅拷贝。

### 2. insert(0) 确保优先级

```python
sys.path.insert(0, str(submodule_path))
```

插入到位置 0 而非 append 到末尾，确保子模块路径优先级最高，不会被其他同名模块遮蔽。

### 3. 捕获两类导入异常

```python
except (ImportError, ModuleNotFoundError):
```

- `ImportError`：模块存在但导入失败（如语法错误、依赖缺失）
- `ModuleNotFoundError`：模块不存在（Python 3.6+）

两者都捕获，确保各种导入失败场景都返回 None 而非抛出异常。

### 4. finally 无条件恢复

```python
finally:
    sys.path = original_path
```

**必须在 finally 中恢复**，确保：
- 导入成功时恢复
- 导入失败时恢复
- 导入时发生其他异常（如模块代码执行出错）时也恢复

### 5. 返回 Optional 类型

函数返回 `Optional[Any]`，调用方**必须**检查 None：

```python
# 使用方式
from .vendor_sandbox import conditional_import, FLEXLOOP_AVAILABLE

flexloop_cli = conditional_import("apps.chaos.src.taolib.cli")
if flexloop_cli is not None:
    flexloop_cli.main()
else:
    print("flexloop 未安装，跳过相关功能（可选依赖）")
```

永远不要假设导入一定成功，必须提供降级路径。

## 进阶：带可用性检测的批量导入

如果需要从同一子模块导入多个对象，可以封装一个上下文管理器：

```python
from contextlib import contextmanager
from typing import Generator, List

@contextmanager
def temporary_path(*paths: Path) -> Generator[None, None, None]:
    """上下文管理器：临时添加路径到 sys.path，退出时自动恢复。"""
    original = sys.path.copy()
    try:
        for p in reversed(paths):  # reverse 保证第一个路径优先级最高
            sys.path.insert(0, str(p))
        yield
    finally:
        sys.path = original


# 使用方式
with temporary_path(FLEXLOOP_DIR):
    try:
        import apps.chaos.src.taolib.cli as cli
        import apps.chaos.src.core.engine as engine
        FLEXLOOP_READY = True
    except ImportError:
        FLEXLOOP_READY = False
```

## 全局状态修改通用原则

临时修改 sys.path 的模式是一个更通用原则的具体实例：**对任何全局状态的修改，谁修改谁恢复，使用 try/finally 确保异常安全**。

适用的全局状态包括：
- `sys.path`（Python 导入路径）
- `os.environ`（环境变量）
- 工作目录（`os.chdir`）
- 日志级别/处理器
- 警告过滤器（`warnings.filterwarnings`）
- 信号处理器（`signal.signal`）
- matplotlib/numpy 等库的全局配置

通用模板：

```python
original_state = get_global_state()
try:
    modify_global_state(new_value)
    do_work()
finally:
    restore_global_state(original_state)
```

## 不要做的事

1. **不要永久修改 sys.path**：导入完不恢复，污染后续所有 import
2. **不要在模块顶层裸 import 可选依赖**：如果依赖不存在，整个模块无法导入
3. **不要用 sys.path.append**：append 到末尾可能被其他同名模块遮蔽
4. **不要只捕获 Exception**：太宽泛会掩盖真正的错误；只捕获导入相关异常
5. **不要假设 FLEXLOOP_AVAILABLE 就一定能导入**：子模块存在但可能缺少传递依赖，仍需 try/except
6. **不要在 finally 中引用可能未定义的变量**：如果 `original_path` 在 try 块内才定义，异常时会触发 NameError

## 与其他模式的关系

- 被 [dual-mode-submodule-governance](../methodology-patterns/governance-strategy/dual-mode-submodule-governance.md) 使用：双模式治理中 owned_collab 子模块的标准导入方式
- 与 [context-aware-path-resolution](context-aware-path-resolution.md) 互补：上下文感知路径解析解决"路径从哪来"的问题，临时路径修改解决"路径怎么安全使用"的问题
- 是 RAII（Resource Acquisition Is Initialization）模式在 Python 导入系统中的应用
