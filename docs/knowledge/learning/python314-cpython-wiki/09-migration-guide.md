---
id: python314-cpython-wiki-09-migration-guide
title: "Python 3.14 迁移指南"
source: "https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html#porting-to-python-3-14"
date: "2026-08-19"
category: "learning"
tags: ["python314", "migration", "deprecation", "porting"]
---

# Python 3.14 迁移指南

本章提供从 Python 3.13（或更早版本）迁移到 Python 3.14 的实用指南，包括废弃 API 对照、行为变更注意事项、C 扩展迁移步骤和常见问题解决方案。

---

## 1. Python 3.13→3.14 迁移 Checklist

### 升级前准备

- [ ] 阅读本指南的行为变更部分（第 3 节）
- [ ] 在测试环境中使用 Python 3.14 运行测试套件
- [ ] 检查依赖库是否支持 Python 3.14（特别是 C 扩展）
- [ ] 如需使用自由线程，检查 C 扩展的 FT 兼容性
- [ ] 关注增量 GC 回退说明（3.14.5+）

### 代码变更

- [ ] 移除 `from __future__ import annotations`（可选，软弃用）
- [ ] 修复 `finally` 块中的 `return`/`break`/`continue`（SyntaxWarning）
- [ ] 检查 `NotImplemented` 的布尔上下文使用（TypeError）
- [ ] 废弃 API 替换（见下表）
- [ ] `map()` 使用 `strict=True` 防止静默截断
- [ ] 测试类型注解在 3.14 下的行为（延迟注解）

### 测试验证

- [ ] 运行完整测试套件，确保所有测试通过
- [ ] 测试自由线程模式（`python3.14t` 或 `PYTHON_GIL=0`）
- [ ] 测试 JIT 模式（`PYTHON_JIT=1`）
- [ ] 性能基准测试（单线程和多线程场景）

---

## 2. 废弃 API 对照表

| 3.13 API | 3.14 状态 | 替代方案/修复建议 |
|-----------|----------|-----------------|
| `from __future__ import annotations` | 软弃用 | 删除即可，PEP 649 延迟注解默认启用 |
| `asyncio` policy 系统（`set_event_loop_policy`） | 弃用 | 使用 asyncio 新 API |
| `codecs.open()` | 弃用 | 使用内置 `open()`（已支持编码参数） |
| `os.popen()` | 软弃用 | 使用 `subprocess.Popen()` |
| `os.spawn*()` | 软弃用 | 使用 `subprocess` 模块 |
| `argparse.FileType` | 弃用 | 使用 `pathlib.Path` + `open()` 或直接在代码中打开文件 |
| `asyncio.ChildWatcher` | 移除 | 不再需要，asyncio 重构了子进程管理 |
| `ast` 中已弃用的常量类（`ast.Num`、`ast.Str` 等） | 移除 | 使用 `ast.Constant` |
| `urllib.URLopener` / `urllib.FancyURLopener` | 移除 | 使用 `urllib.request.urlopen()` |
| `pathlib.PurePath` 的额外参数 | 移除 | 使用标准构造参数 |
| `Py_HUGE_VAL`（C API） | 移除 | 使用 C99 `HUGE_VAL`（`<math.h>`） |
| `Py_IS_NAN`/`Py_IS_INFINITY`/`Py_IS_FINITE`（C API） | 移除 | 使用 C99 `isnan()`/`isinf()`/`isfinite()` |
| `PySequence_Fast_GET_ITEM`/`_SIZE`（C API，Limited API） | 移除 | 使用 `PySequence_Fast()` + `PyList_GET_ITEM/SIZE` |

---

## 3. 重要行为变更

### multiprocessing 默认启动方法变更

**Unix（非 macOS）**：默认启动方法从 `fork` 改为 `forkserver`。

```python
import multiprocessing
print(multiprocessing.get_start_method())
# Linux 3.13: 'fork'
# Linux 3.14: 'forkserver'（更安全，避免 fork-after-multithreading 问题）
```

**影响**：如果依赖 fork 的特定行为（如继承所有内存状态），需要显式设置：

```python
multiprocessing.set_start_method('fork', force=True)
```

### functools.partial 变为方法描述符

`functools.partial` 对象现在正确支持方法绑定：

```python
from functools import partial

class MyClass:
    def method(self, x, y):
        return x + y

    add5 = partial(method, 5)

obj = MyClass()
obj.add5(3)  # 3.13: TypeError（partial 不绑定 self）
             # 3.14: 8（正确绑定 self，等价于 obj.method(5, 3)）
```

### types.UnionType 与 typing.Union 等价

`int | str` 返回的 `types.UnionType` 与 `typing.Union[int, str]` 在所有场景下完全等价：

```python
import typing
assert type(int | str) is typing.UnionType  # 3.14 保证
```

### pickle 错误类型变化

某些 pickle 错误现在抛出不同的异常类型（更具体的异常类型而非通用 `PicklingError`）。确保错误处理不会因为异常类型变化而失效。

### int() 不再委托 __trunc__

`int()` 不再调用 `__trunc__()` 方法。自定义数值类型应实现 `__int__()` 而非 `__trunc__()`：

```python
class MyNumber:
    # ❌ 旧方式
    def __trunc__(self):
        return 42
    
    # ✅ 新方式
    def __int__(self):
        return 42
```

### NotImplemented 布尔上下文 TypeError

在布尔上下文中使用 `NotImplemented` 现在抛出 `TypeError`：

```python
# ❌ 3.14 中会抛 TypeError
if NotImplemented:
    pass

# 富比较方法中也要注意
class MyClass:
    def __eq__(self, other):
        result = compare(self, other)
        if not result:  # ❌ result 可能是 NotImplemented
            return False
        return result
    
    # ✅ 正确写法
    def __eq__(self, other):
        result = compare(self, other)
        if result is NotImplemented:
            return NotImplemented
        return result
```

### ⚠️ 增量 GC 回退（3.14.5）

Python 3.14.0 引入了增量 GC（Incremental GC），旨在减少 GC 暂停时间。但在 3.14.1-3.14.4 中收到生产环境内存压力报告后，**3.14.5 回退到 3.13 式分代 GC**：

- 3.14.0-3.14.4：增量 GC（可能有内存使用增加）
- 3.14.5+：分代 GC（与 3.13 行为一致）

如果在 3.14.0-3.14.4 中遇到内存问题，升级到 3.14.5+ 即可。

---

## 4. C 扩展迁移指南

### 第一步：确保编译通过

```c
// 替换已移除的数学宏
// ❌ #include <Python.h> 中的 Py_IS_NAN
// ✅
#include <math.h>
#define Py_IS_NAN(x) isnan(x)  // 或直接使用 isnan()

// 替换 PySequence_Fast_GET_ITEM
// ❌ item = PySequence_Fast_GET_ITEM(seq, i);
// ✅
PyObject *fast = PySequence_Fast(seq, "");
if (!fast) goto error;
PyObject *item = PyList_GET_ITEM(fast, i);
// ... 使用 ...
Py_DECREF(fast);

// 不直接访问 ob_refcnt
// ❌ obj->ob_refcnt++;
// ✅ Py_INCREF(obj);
// ❌ obj->ob_type = &MyType;
// ✅ Py_SET_TYPE(obj, &MyType);
```

### 第二步：添加 GIL 依赖声明

```c
// 模块定义中添加 Py_mod_gil 槽位
static struct PyModuleDef_Slot mymodule_slots[] = {
    {Py_mod_gil, Py_MOD_GIL},  // 声明依赖 GIL（安全默认）
    {0, NULL}
};

static struct PyModuleDef mymodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "mymodule",
    .m_size = -1,
    .m_methods = mymethods,
    .m_slots = mymodule_slots,
};
```

这确保你的扩展在 `python3.14t`（自由线程构建）中仍然能正常工作（自动获取 GIL）。

### 第三步（可选）：适配自由线程

```c
// 对于对象的可变字段访问，使用关键区段
static PyObject*
myobj_get_data(MyObject *self, void *closure)
{
    Py_BEGIN_CRITICAL_SECTION(self);
    PyObject *data = Py_XNewRef(self->data);
    Py_END_CRITICAL_SECTION();
    return data;
}

static int
myobj_set_data(MyObject *self, PyObject *value, void *closure)
{
    Py_BEGIN_CRITICAL_SECTION(self);
    Py_XSETREF(self->data, Py_XNewRef(value));
    Py_END_CRITICAL_SECTION();
    return 0;
}
```

完成适配后，将 `Py_MOD_GIL` 改为 `Py_MOD_FREE_THREADED`。

### 第四步：验证

```bash
# 在标准构建下测试
python3.14 -m pytest tests/

# 在自由线程构建下测试
python3.14t -m pytest tests/

# 启用 JIT 测试
PYTHON_JIT=1 python3.14 -m pytest tests/
```

---

## 5. 字节码变更对工具的影响

Python 3.14 的字节码有以下变更：
- 新增 t-strings 相关指令
- 新增/调整特化指令
- 某些操作码编号变化

**影响范围**：
- ✅ 普通应用：无影响
- ⚠️ 字节码操作库（如 `dis`、`bytecode`、`xdis`）：需要更新
- ⚠️ 代码覆盖工具：可能需要适配新的行号映射
- ⚠️ AOT 编译器（Nuitka、Cython）：需要适配新字节码

---

- [上一章：构建系统与平台支持](08-build-platform.md) ←
- [下一章：实战示例](10-practical-examples.md) →
