# Free-Threading C Extension CMake Template

> 标准 CMake + Ninja 构建模板，用于开发 Python 3.13t+ free-threading（无 GIL）环境下的 C 扩展模块。

## 快速开始

```bash
# 1. 复制模板到你的项目
cp -r templates/cmake-cext/ my_extension/
cd my_extension/

# 2. 重命名模块（可选）
# 编辑 CMakeLists.txt 修改 MODULE_NAME，或通过 -D 传入：
# cmake -DMODULE_NAME=my_module ..

# 3. 构建 + 测试
bash build.sh

# 或手动构建：
mkdir build && cd build
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release ..
ninja -j$(nproc)
cd ..
python -c "import ft_extension; ft_extension.run_self_test()"
```

## 模板结构

```
cmake-cext/
├── CMakeLists.txt      # CMake 构建配置（参数化模板）
├── src/
│   └── ft_extension.c  # C 扩展源代码（含完整注释和最佳实践）
├── build.sh            # 一键构建+测试脚本
└── README.md           # 本文档
```

## 编译规范（必须遵守）

### 1. GIL 声明（🔴 强制）

每个支持 free-threading 的 C 扩展模块**必须**在 `PyModuleDef_Slot` 数组中声明：

```c
static PyModuleDef_Slot ModuleSlots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},  // ← 必须有这一行！
    {Py_mod_exec, (void*)module_exec},
    {0, NULL}
};
```

**如果忘记这一行**：Python 会在模块加载时自动重新启用 GIL，导致你的多线程代码退化为单线程串行执行，free-threading 完全失效。

### 2. ABI 兼容性

| 项 | 要求 |
|---|---|
| Python 版本 | 3.13t+（SOABI 包含 `t` 后缀，如 `cpython-314t-x86_64-linux-gnu`） |
| 编译宏 | 必须定义 `Py_GIL_DISABLED=1`（CMake 模板已自动添加） |
| 文件名 | `.so` 文件后缀必须匹配 sysconfig SOABI（模板自动处理） |

验证方法：
```python
import sysconfig
print(sysconfig.get_config_var('SOABI'))  # 应包含 cpython-31Xt
print(sysconfig.get_config_var('Py_GIL_DISABLED'))  # 应返回 1
```

### 3. 线程安全规则

| 场景 | 正确做法 | 错误做法 |
|---|---|---|
| 共享可变状态 | 使用 `<stdatomic.h>` 原子类型（`atomic_long`, `atomic_int` 等） | 使用普通全局变量（`long counter = 0;`）→ **数据竞争** |
| CPU 密集纯 C 计算 | `Py_BEGIN_ALLOW_THREADS` / `Py_END_ALLOW_THREADS` 释放 GIL | 持有 GIL 计算 → 无法并行 |
| Python API 调用 | 必须在持有 GIL 时调用 | GIL 释放后调用 `PyLong_From*`, `Py_DECREF` 等 → **崩溃** |
| 模块状态 | 使用 `m_size = sizeof(State)` + `PyModule_GetState()` | 使用全局变量存储模块状态 → 多解释器/子模块数据竞争 |
| 跨 GIL 边界变量 | 在 `Py_BEGIN_ALLOW_THREADS` 之前声明变量 | 在块内声明 → 块外不可访问（作用域错误） |

### 4. CMake 配置要点

```cmake
# 必须显式指定 Python 查找策略（优先使用 conda 环境）
set(Python3_FIND_STRATEGY LOCATION)
set(Python3_FIND_IMPLEMENTATIONS CPython)
if(DEFINED ENV{CONDA_PREFIX})
    set(Python3_ROOT_DIR "$ENV{CONDA_PREFIX}")
endif()
find_package(Python3 3.13 REQUIRED COMPONENTS Interpreter Development.Module)

# 使用 python3_add_library 而非普通 add_library
python3_add_library(my_module MODULE src/my_module.c)

# 输出文件名必须匹配 SOABI
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import sysconfig; print(sysconfig.get_config_var('SOABI'))"
    OUTPUT_VARIABLE PYTHON_SOABI
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
set_target_properties(my_module PROPERTIES
    PREFIX ""
    SUFFIX ".${PYTHON_SOABI}.so"
)
```

### 5. 编译器参数

```cmake
target_compile_options(my_module PRIVATE
    -O3                         # 优化级别
    -Wall -Wextra -Wpedantic    # 严格警告
    -fno-semantic-interposition # 符号解析优化（重要：避免符号插入导致的性能下降）
)
target_compile_definitions(my_module PRIVATE Py_GIL_DISABLED=1)
```

## 依赖要求

构建 C 扩展需要以下工具链（在 devcontainer-base v2.2+ 镜像中已预装）：

| 工具 | 最低版本 | conda 包名 |
|---|---|---|
| Python | 3.13t+ | `python=3.14.*=*_cp314t`（free-threading build） |
| CMake | 3.27+ | `cmake>=3.30` |
| Ninja | 1.11+ | `ninja>=1.12` |
| GCC/Clang | C11 支持 | `c-compiler`（conda-forge） |
| Python 开发头文件 | 与 Python 版本匹配 | `python` 包已包含 |

安装命令（在 conda 环境中）：
```bash
conda install -c conda-forge "python=3.14.*=*_cp314t" "cmake>=3.30" "ninja>=1.12" c-compiler
```

## 测试要求

每个 C 扩展**必须**包含：

1. **自检函数**（如 `run_self_test()`）：验证基础功能正确性
2. **多线程压力测试**（如 `thread_stress()`）：8 线程 × 100,000 次原子操作，验证无 race condition
3. **ABI 验证**：检查 SOABI 包含 `t` 后缀，`Py_GIL_DISABLED=1`

模板已内置这些测试，可直接作为参考。

## 常见坑点

详见 `docs/PY314T-C-EXTENSION-GUIDE.md` 团队技术分享文档。

## 参考

- [Python 3.13 Free-Threading 官方文档](https://docs.python.org/3.13/howto/free-threading-extensions.html)
- [PEP 703 – Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/)
- [devcontainer-base v2.2 构建流水线文档](../../docs/v2.2-build-pipeline-optimization.md)
