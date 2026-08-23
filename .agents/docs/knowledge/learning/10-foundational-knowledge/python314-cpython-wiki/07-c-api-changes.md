---
id: "python314-cpython-wiki-07"
title: "Python 3.14 C API 与扩展开发"
source: "https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html#new-c-api-features"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/10-foundational-knowledge/python314-cpython-wiki/07-c-api-changes.toml"
---

# Python 3.14 C API 与扩展开发

Python 3.14 对 C API 进行了多项重要变更——PEP 741 统一配置 API、PEP 757 C 级整数导出、PEP 768 远程调试接口，以及 Limited API 的进一步不透明化。本章面向 C 扩展开发者，讲解新增 API、变更影响和迁移方案。

---

## 1. PEP 741：统一配置 C API

### 问题背景

CPython 的初始化配置长期以来使用大量全局变量和分散的配置函数（`Py_SetProgramName()`、`Py_SetPythonHome()`、`PySys_AddWarnOption()` 等），配置顺序敏感，嵌入 Python 的应用经常出错。

PEP 741 引入了**统一的配置结构体** `PyInitConfig`，通过单一配置对象管理所有初始化参数。

### 新 API 概览

```c
// Include/pyinitconfig.h (Python 3.14)

// 初始化配置类型
typedef struct {
    const char *program_name;
    const char *python_home;
    const char *executable;
    int isolated;        // 隔离模式（-I）
    int use_environment; // 使用环境变量（-E）
    int dev_mode;        // 开发模式（-X dev）
    int faulthandler;    // faulthandler
    int tracemalloc;     // tracemalloc
    // ... 其他配置项
    wchar_t **argv;      // 命令行参数
    int argc;
    // 模块搜索路径
    const char *module_search_paths_env;
    // ...
} PyInitConfig;

// 核心 API
void PyInitConfig_Init(PyInitConfig *config);           // 初始化默认配置
int Py_InitFromConfig(const PyInitConfig *config);      // 从配置初始化
void PyInitConfig_Free(PyInitConfig *config);           // 释放配置
```

### 迁移示例：嵌入 Python

**旧方式（3.13 及之前）**：

```c
// ❌ 旧 API：分散调用，顺序敏感
int main(int argc, char **argv) {
    Py_SetProgramName(L"myapp");
    Py_SetPythonHome(L"/usr/local/python");
    PySys_AddWarnOption(L"default::RuntimeWarning");
    
    Py_Initialize();  // 必须在所有设置之后调用
    
    // ... 使用 Python ...
    
    Py_Finalize();
    return 0;
}
```

**新方式（PEP 741）**：

```c
// ✅ 新 API：统一配置结构体
#include <Python.h>
#include <pyinitconfig.h>

int main(int argc, char **argv) {
    PyInitConfig config;
    PyInitConfig_Init(&config);  // 设置默认值
    
    // 自定义配置
    config.program_name = "myapp";
    config.python_home = "/usr/local/python";
    config.dev_mode = 1;  // 开发模式
    
    // 初始化
    if (Py_InitFromConfig(&config) < 0) {
        PyInitConfig_Free(&config);
        return 1;
    }
    
    // ... 使用 Python ...
    
    Py_Finalize();
    PyInitConfig_Free(&config);
    return 0;
}
```

### 隔离模式

```c
PyInitConfig config;
PyInitConfig_Init(&config);
config.isolated = 1;  // 等价于 python -I
// 隔离模式下：忽略环境变量、不导入 site 模块、不将脚本目录加入 sys.path
```

---

## 2. PEP 757：C 级整数导出 API

### 问题：获取 Python 整数的底层表示

Python 的整数（`int`/`long`）是任意精度的，C 扩展经常需要高效获取其值。之前的 API（`PyLong_AsLong`、`PyLong_AsLongLong`）会创建临时对象或进行复制，对于大数组处理效率低。

PEP 757 引入了**零拷贝整数读取 API**：

```c
// Include/longobject.h

// 获取整数的本地内存布局
typedef struct {
    int ndigits;          // 位数组长度
    int negative;         // 是否负数
    void *digits;         // 指向内部数字数组
    int digits_size;      // 数字数组元素大小（1/2/4 字节）
} PyLongInfo;

// 获取整数布局信息（不复制）
PyLongInfo PyLong_GetNativeLayout(PyObject *op);

// 导出整数（可返回临时缓冲区或指针）
int PyLong_Export(PyObject *op, PyLongInfo *info);

// 释放导出的缓冲区
void PyLong_FreeExport(PyObject *op, PyLongInfo *info);

// 快速写入接口
typedef struct {
    int (*write_long)(void *data, long long value);
    int (*write_unsigned_long_long)(void *data, unsigned long long value);
} PyLongWriter;
```

### 使用示例

```c
// 高效读取整数数组
PyObject *list_of_ints = ...;  // Python list of ints
Py_ssize_t n = PyList_GET_SIZE(list_of_ints);

for (Py_ssize_t i = 0; i < n; i++) {
    PyObject *item = PyList_GET_ITEM(list_of_ints, i);
    
    PyLongInfo info;
    if (PyLong_Export(item, &info) < 0) {
        // 错误处理
        goto error;
    }
    
    // 直接访问内部数字数组（零拷贝）
    if (info.ndigits == 0) {
        c_array[i] = 0;
    } else if (info.ndigits == 1 && !info.negative) {
        // 适合 small int 快速路径
        if (info.digits_size == 4) {
            c_array[i] = (int64_t)((int32_t*)info.digits)[0];
        }
        // ... 其他 digit 大小
    } else {
        // 大整数处理
    }
    
    PyLong_FreeExport(item, &info);
}
```

---

## 3. PEP 768：安全外部调试接口

PEP 768 为外部调试器（如 gdb、lldb 或 IDE 调试器）提供了**安全的 C API**，允许在不需要注入代码的情况下附加到运行中的 Python 进程：

```c
// Include/cpython/pydebug.h

// 调试器附加回调类型
typedef int (*PyDebuggerCallback)(PyThreadState *tstate, void *data);

// 注册/注销调试器回调
int PyDebugger_Attach(PyDebuggerCallback callback, void *data);
int PyDebugger_Detach(PyDebuggerCallback callback);

// 检查是否有调试器附加
int PyDebugger_IsAttached(void);
```

此 API 支持 `pdb -p PID` 远程附加功能（见 [05-stdlib-improvements.md §5](05-stdlib-improvements.md#5-pdb远程调试与增强)）。

---

## 4. 新增 C API 汇总

以下是 Python 3.14 中新增的主要 C API 函数/宏：

### 类型与对象

| API | 功能 |
|-----|------|
| `PyType_GetName()` | 获取类型的限定名 |
| `PyType_GetQualName()` | 获取类型的完全限定名 |
| `PyObject_GetOptionalAttr()` | 获取属性，属性不存在时返回 NULL 但不抛异常 |
| `PyObject_GetOptionalItem()` | 获取字典项，key 不存在时返回 NULL 但不抛异常 |
| `Py_Is(const PyObject*, const PyObject*)` | 同一性判断（等价于 `is`） |

### 内存与引用计数

| API | 功能 |
|-----|------|
| `Py_NewRef(PyObject*)` | 返回对象的新引用（等价于 `Py_INCREF; return obj`） |
| `Py_XNewRef(PyObject*)` | Py_NewRef 的 NULL 安全版本 |
| `PyUnstable_Object_IsUniqueReferencedTemporary()` | 自由线程：检查对象是否只有一个临时引用 |

### 导入与模块

| API | 功能 |
|-----|------|
| `PyImport_AddModuleRef()` | 返回模块的新引用（替代 `PyImport_AddModule` 的借用引用） |
| `PyModule_AddObjectRef()` | 添加对象到模块，返回新引用 |

### 监控与 profiling

| API | 功能 |
|-----|------|
| `PyMonitor_EnterCallback()` | 监控回调进入 |
| `PyMonitor_ExitCallback()` | 监控回调退出 |
| PEP 669 监控 API 的稳定版本 | 低开销事件监控 |

### Unicode

| API | 功能 |
|-----|------|
| `PyUnicode_EqualToUTF8()` | 与 UTF-8 字符串比较 |
| `PyUnicode_EqualToUTF8AndSize()` | 指定长度版本 |

---

## 5. Limited API 变更

### Py_TYPE/Py_REFCNT 不透明化

Python 3.14 中，Limited API 下的 `Py_TYPE()`、`Py_REFCNT()`、`Py_SIZE()` 宏**变为函数调用**，不再直接访问结构体字段：

```c
// Limited API 3.13 及之前：直接访问结构体（不透明化前）
#define Py_REFCNT(ob) (((PyObject*)(ob))->ob_refcnt)
#define Py_TYPE(ob)   (((PyObject*)(ob))->ob_type)
#define Py_SIZE(ob)   (((PyVarObject*)(ob))->ob_size)

// Limited API 3.14+：函数调用（字段不再直接暴露）
static inline Py_ssize_t Py_REFCNT(PyObject *ob) { return ob->ob_refcnt; }
// 未来版本将改为：Py_ssize_t Py_REFCNT(PyObject *ob);  // 真正的函数
```

**迁移建议**：
- 如果你的扩展使用 `Py_REFCNT(obj) = new_value` 直接设置引用计数，必须改为 `Py_SET_REFCNT(obj, new_value)`
- 如果直接访问 `ob->ob_type`，必须改用 `Py_TYPE(obj)`（读取）或 `Py_SET_TYPE(obj, type)`（写入）

```c
// ❌ 旧代码（在 future Limited API 中会编译失败）
obj->ob_refcnt = 1;
obj->ob_type = &MyType;

// ✅ 新代码（推荐）
Py_SET_REFCNT(obj, 1);
Py_SET_TYPE(obj, &MyType);
Py_INCREF(obj);  // 正常的引用计数操作不变
```

### 移除 PySequence_Fast_* 宏

`PySequence_Fast_GET_ITEM` 和 `PySequence_Fast_GET_SIZE` 宏从 Limited API 中移除。使用 `PySequence_GetItem()` 和 `PySequence_Size()` 替代，或先将序列转换为 list/tuple。

```c
// ❌ 旧代码
PyObject *item = PySequence_Fast_GET_ITEM(seq, i);
Py_ssize_t size = PySequence_Fast_GET_SIZE(seq);

// ✅ 新代码
PyObject *fast = PySequence_Fast(seq, "expected a sequence");
if (!fast) goto error;
PyObject *item = PyList_GET_ITEM(fast, i);  // PySequence_Fast 返回 list
Py_ssize_t size = PyList_GET_SIZE(fast);
// ... 使用 ...
Py_DECREF(fast);
```

---

## 6. 自由线程 C API 适配

### 模块级 GIL 声明

扩展必须声明是否支持自由线程：

```c
// 方式1：声明依赖 GIL（最简单，3.14 推荐先这样做）
static struct PyModuleDef_Slot mymodule_slots[] = {
    {Py_mod_gil, Py_MOD_GIL},  // 自由线程模式下自动获取 GIL
    {0, NULL}
};

static struct PyModuleDef mymodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "mymodule",
    .m_size = -1,
    .m_methods = MyMethods,
    .m_slots = mymodule_slots,
};

// 方式2：声明自由线程兼容（需要确保线程安全）
static struct PyModuleDef_Slot mymodule_slots[] = {
    {Py_mod_gil, Py_MOD_FREE_THREADED},  // 支持无 GIL 并行
    {0, NULL}
};
```

### 关键区段 API

```c
// 保护对象状态的关键区段
static PyObject*
myobj_set_value(MyObject *self, PyObject *value)
{
    Py_BEGIN_CRITICAL_SECTION(self);
    Py_XSETREF(self->value, Py_NewRef(value));
    Py_END_CRITICAL_SECTION();
    Py_RETURN_NONE;
}

static PyObject*
myobj_get_value(MyObject *self, PyObject *Py_UNUSED(ignored))
{
    Py_BEGIN_CRITICAL_SECTION(self);
    PyObject *value = Py_NewRef(self->value);
    Py_END_CRITICAL_SECTION();
    return value;
}
```

### 永生对象

永生对象（immortal objects）不需要引用计数操作：

```c
// 创建永生类型
// 类型对象通过 Py_TPFLAGS_IMMORTAL 标记或 Py_SET_IMMORTAL 宏
#define Py_SET_IMMORTAL(op) do { \
    (op)->ob_refcnt = _Py_IMMORTAL_REFCNT; \
} while(0)
```

### 引用计数变更

自由线程模式下引用计数行为变化：
- 永生对象跳过 INCREF/DECREF
- 非永生对象使用 BRC（批量引用计数），原子操作在静默点合并
- 对象析构通过 QSBR 延迟执行

```c
// C 扩展中，正常使用 Py_INCREF/Py_DECREF 即可
// 不需要直接使用 BRC 或 QSBR API
// 但需要确保在关键区段内访问对象的可变字段
```

---

## 7. 移除和弃用的 C API

### 移除的 API

| 移除的 API | 替代方案 |
|-----------|---------|
| `Py_HUGE_VAL` | C99 `HUGE_VAL`（`<math.h>`） |
| `Py_IS_NAN(x)` | C99 `isnan(x)`（`<math.h>`） |
| `Py_IS_INFINITY(x)` | C99 `isinf(x)`（`<math.h>`） |
| `Py_IS_FINITE(x)` | C99 `isfinite(x)`（`<math.h>`） |
| `PySequence_Fast_GET_ITEM` | `PySequence_Fast()` + `PyList_GET_ITEM()` |
| `PySequence_Fast_GET_SIZE` | `PySequence_Fast()` + `PyList_GET_SIZE()` |
| `PyObject_GET_ITEM` 宏 | `PyObject_GetItem()` 函数 |

### 弃用的 API

| 弃用的 API | 替代方案 | 移除版本 |
|-----------|---------|---------|
| `PyEval_CallObject` | `PyObject_CallNoArgs()` / `PyObject_CallOneArg()` | 3.16 |
| `PyEval_CallMethod` | `PyObject_CallMethod()` | 3.16 |
| `PyImport_ImportModuleNoBlock` | `PyImport_ImportModule()` | 3.16 |
| `PySys_SetArgv` | `PyInitConfig` API | 3.16 |

---

## 8. 稳定 ABI（stable_abi.toml）

稳定 ABI 的定义从硬编码迁移到 [Misc/stable_abi.toml](https://github.com/python/cpython/blob/v3.14.0/Misc/stable_abi.toml) TOML 文件：

```toml
# stable_abi.toml 示例
[structs.PyObject]
    [structs.PyObject.fields.ob_refcnt]
    type = "Py_ssize_t"
    # 3.14 起，ob_refcnt 和 ob_type 仅为 ABI 兼容保留，不应在 Limited API 中直接访问

[functions.PyLong_AsLong]
    added = "3.2"
    abi_only = false
```

---

## 9. C 扩展迁移检查清单

将 C 扩展从 Python 3.13 迁移到 3.14 的步骤：

### 第一阶段：兼容性（必做）

- [ ] 检查是否使用了已移除的 C API（`Py_HUGE_VAL`、`Py_IS_NAN` 等），替换为 C99 标准函数
- [ ] 检查是否直接访问 `ob_refcnt`/`ob_type`，替换为 `Py_REFCNT()`/`Py_TYPE()`/`Py_SET_REFCNT()`/`Py_SET_TYPE()`
- [ ] 检查是否使用 `PySequence_Fast_GET_ITEM`/`_SIZE`，迁移到 `PySequence_Fast()` 模式
- [ ] 测试编译，确保没有弃用警告

### 第二阶段：新特性（可选）

- [ ] 评估 PEP 741 配置 API（如嵌入 Python 或需要精细控制初始化）
- [ ] 评估 PEP 757 整数导出 API（如处理大整数数组）
- [ ] 使用 `Py_NewRef`/`Py_XNewRef` 简化引用计数代码
- [ ] 使用 `PyObject_GetOptionalAttr`/`GetOptionalItem` 简化属性/项访问

### 第三阶段：自由线程适配（推荐）

- [ ] 添加 `Py_MOD_GIL` 标记（确保在自由线程模式下可运行）
- [ ] 审查全局变量和静态变量，确保线程安全
- [ ] 对对象可变字段访问添加 `Py_BEGIN_CRITICAL_SECTION`/`Py_END_CRITICAL_SECTION`
- [ ] 在 `python3.14t` 下运行测试
- [ ] 确认无误后改为 `Py_MOD_FREE_THREADED`

---

## 10. 本章小结

| C API 变更 | PEP | 影响 |
|-----------|-----|------|
| 统一配置 API | 741 | 嵌入 Python 的初始化方式更清晰可靠 |
| C 整数导出 API | 757 | 大数组/数值计算扩展性能提升 |
| 远程调试 API | 768 | 调试器可以安全附加到运行进程 |
| Py_TYPE/Py_REFCNT 不透明化 | — | Limited API 更加隔离，未来版本兼容性更好 |
| 数学宏标准化 | — | `Py_IS_NAN` 等改用 C99 标准函数 |
| 自由线程声明 | 779 | 扩展必须声明 GIL 依赖或自由线程兼容性 |
| 关键区段 API | 703 | 保护对象状态在自由线程下安全访问 |

下一章介绍 Python 3.14 的**构建系统变化和平台支持**。

---

- [上一章：CPython 源码架构总览](06-cpython-architecture.md) ←
- [下一章：构建系统与平台支持](08-build-platform.md) →
