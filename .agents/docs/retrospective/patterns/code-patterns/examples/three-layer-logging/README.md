# 跨语言三层协调日志架构 — 可复用示例包

零依赖、开箱即用的跨语言日志系统参考实现，适用于 C/C++/Rust 原生扩展 + Python/Go/其他宿主语言绑定场景。

- **零外部依赖**：C++ 层仅依赖标准库（`<iostream>`/`<sstream>`/`<cstring>`）
- **编译期零开销**：Release 构建自动屏蔽 DEBUG/TRACE/INFO 日志，无字符串拼接运行时浪费
- **跨语言统一控制**：宿主语言一个函数调用同时控制原生层和宿主层日志粒度
- **组件标签分类**：`[MEM]`/`[TENSOR]`/`[NET]`/`[LAYER]` 等标签便于 grep 过滤

## 文件清单

| 文件 | 层级 | 用途 |
|------|------|------|
| [log.hpp](log.hpp) | C++ 核心层 | RAII Logger 类 + 5级日志 + 编译期闸门 + 组件标签宏 |
| [ffi_bridge.cc](ffi_bridge.cc) | FFI 桥接层 | 薄封装函数 + TVM FFI/pybind11/PyO3 注册示例 |
| [debug.py](debug.py) | Python 配置层 | setup_debug/setup_trace/setup_quiet 统一入口 + Handler 生命周期管理 |
| [demo_layer.cc](demo_layer.cc) | 集成示例 | 典型计算模块的「五日志点」埋点示范 |

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│ Layer 3: Python 配置层 (debug.py)                   │
│   setup_debug() / setup_trace() / setup_quiet()     │
│   ├─ 统一入口，一次调用同时控制 Python+C++ 两层      │
│   ├─ 管理 StreamHandler/FileHandler 生命周期        │
│   └─ 幂等安全：重复调用不会导致日志重复输出           │
├─────────────────────────────────────────────────────┤
│ Layer 2: FFI 桥接层 (ffi_bridge.cc)                 │
│   myproj_set_log_level(int) / myproj_get_log_level()│
│   ├─ 薄封装：仅做 int↔enum 类型转换，无业务逻辑      │
│   └─ 通过 FFI 反射系统注册为全局函数                 │
├─────────────────────────────────────────────────────┤
│ Layer 1: C++ 核心层 (log.hpp)                       │
│   enum Level {TRACE=0, DEBUG=1, INFO=2, WARN=3, ERROR=4}│
│   ├─ RAII Logger：构造记录位置，析构自动输出+flush   │
│   ├─ 编译期闸门 MYPROJ_ENABLE_DEBUG_LOG              │
│   └─ 组件标签宏 MYPROJ_MEM_LOG / MYPROJ_LAYER_LOG …  │
└─────────────────────────────────────────────────────┘
```

## 快速集成五步

### Step 1：复制核心头文件

将 [log.hpp](log.hpp) 复制到你的项目 include 目录，全局替换命名空间前缀：

- `myproj` → 你的项目命名空间（如 `mylib`）
- `MYPROJ_LOG` → 你的项目日志宏前缀（如 `MYLIB_LOG`）
- `MYPROJ_ENABLE_DEBUG_LOG` → 你的编译开关名（如 `MYLIB_ENABLE_DEBUG_LOG`）

### Step 2：CMake 构建开关

```cmake
option(MYPROJ_ENABLE_DEBUG_LOG "Enable DEBUG/TRACE/INFO logging" OFF)
if(MYPROJ_ENABLE_DEBUG_LOG)
  target_compile_definitions(your_lib PRIVATE MYPROJ_ENABLE_DEBUG_LOG)
endif()
```

Release 构建默认关闭（OFF），Debug 构建或排查问题时通过 `-DMYPROJ_ENABLE_DEBUG_LOG=ON` 开启。

### Step 3：在 C++ 代码中埋点

参考 [demo_layer.cc](demo_layer.cc) 的「五日志点」模式：

```cpp
#include "myproj/log.hpp"

void MyModule::Init(const Config& cfg) {
  // 日志点 1：构造/初始化 — 记录关键参数
  MYPROJ_LAYER_LOG << "MyModule Init: batch_size=" << cfg.batch_size
                   << " channels=" << cfg.channels;

  // 日志点 2：资源分配 — 用 TENSOR/MEM 标签
  buffer_.resize(size);
  MYPROJ_TENSOR_LOG << "MyModule: allocated buffer size=" << size;
}

void MyModule::Reshape(Shape new_shape) {
  // 日志点 3：形状变化 — 记录前后差异
  MYPROJ_LAYER_LOG << "MyModule Reshape: old=" << old_shape
                   << " new=" << ShapeToString(new_shape);
}

float MyModule::Forward(const float* input, float* output, int n) {
  // 日志点 4：计算前 — 记录维度（禁止在循环内打日志！）
  MYPROJ_LAYER_LOG << "MyModule Forward: n=" << n << " dim=" << dim_;

  float result = compute(input, output, n);

  // 日志点 5：计算后 — 记录关键结果值
  MYPROJ_LAYER_LOG << "MyModule Forward: result=" << result;
  return result;
}
```

**关键规则**：
- **禁止在内层循环中打日志**——日志点 4 只在循环外打一次维度信息
- **多值拼装到一行**：用 `std::ostringstream` 先格式化，再单次 `<<` 输出，避免多行分裂
- **ERROR 走 stderr**：Logger 析构时自动对 ERROR 级别使用 `std::cerr`，WARN 及以下走 `std::cout`

### Step 4：FFI 桥接层

将 [ffi_bridge.cc](ffi_bridge.cc) 中的桥接函数适配到你的 FFI 系统：

**TVM FFI**（已在示例中）：
```cpp
TVM_FFI_STATIC_INIT_BLOCK() {
  tvm::ffi::FunctionRegistry::Global("myproj.SetLogLevel")
      .set_body([](TVMArgs args, TVMRetValue* rv) {
        myproj_set_log_level(args[0]);
      });
}
```

**pybind11**：
```cpp
#include <pybind11/pybind11.h>
PYBIND11_MODULE(_myproj, m) {
  m.def("set_log_level", &myproj_set_log_level);
  m.def("get_log_level", &myproj_get_log_level);
}
```

**PyO3 (Rust)**：
```rust
#[pyfunction]
fn set_log_level(level: i32) { unsafe { myproj_set_log_level(level); } }
```

**纯 C 导出**（供 Go/cgo/ctypes 使用）：
```c
// ffi_bridge.cc 中已用 extern "C" 导出符号
// Go 侧通过 //extern 直接调用
```

### Step 5：Python 配置层

将 [debug.py](debug.py) 复制到你的 Python 包中，替换模块名和 FFI 调用：

```python
# 你的包/__init__.py 中暴露便捷函数
LOG_LEVEL_TRACE = 0
LOG_LEVEL_DEBUG = 1
LOG_LEVEL_INFO  = 2
LOG_LEVEL_WARN  = 3
LOG_LEVEL_ERROR = 4

def set_log_level(level: int) -> None:
    fn = _ffi.get_global_func("myproj.SetLogLevel")  # 替换为你的FFI函数名
    if fn is not None:
        fn(level)
```

使用方式：
```python
from myproj.debug import setup_debug, setup_trace, setup_quiet

setup_debug()                        # 一键开启 DEBUG（两层同时）
setup_debug(log_file="app.log")     # 同时写入文件
setup_trace()                        # 最细 TRACE 级别（内存泄漏诊断）
setup_quiet()                        # 恢复 WARN 默认
```

## 日志级别约定

| 级别 | 值 | 用途 | Release 默认 |
|------|---|------|-------------|
| TRACE | 0 | 最细粒度：对象构造栈、缓冲区分配/释放、逐调用细节 | ❌ 关闭 |
| DEBUG | 1 | 调试信息：模块初始化参数、形状变化、资源分配 | ❌ 关闭 |
| INFO  | 2 | 关键事件：模型加载完成、流水线阶段切换 | ❌ 关闭 |
| WARN  | 3 | 警告：降级路径触发、性能次优、可恢复异常 | ✅ 开启 |
| ERROR | 4 | 错误：不可恢复失败、数据损坏、API误用 | ✅ 开启 |

级别数字必须在 C++ enum 和 Python 常量中严格对齐（0-4）。

## 组件标签约定

| 标签 | 用途 | grep 命令 |
|------|------|----------|
| `[MEM]` | 内存分配/释放/计数器 | `grep "\[MEM\]" app.log` |
| `[TENSOR]` | 张量/缓冲区创建、形状、dtype | `grep "\[TENSOR\]" app.log` |
| `[NET]` | 网络/流水线生命周期、阶段切换 | `grep "\[NET\]" app.log` |
| `[LAYER]` | 模块/层初始化、Reshape、计算维度 | `grep "\[LAYER\]" app.log` |

在你的项目中按需增删标签，在 `log.hpp` 中用宏统一定义：

```cpp
#define MYPROJ_DB_LOG    MYPROJ_LOG_DEBUG() << "[DB] "
#define MYPROJ_CACHE_LOG MYPROJ_LOG_DEBUG() << "[CACHE] "
```

## 编译期零开销验证

Release 构建（未定义 `MYPROJ_ENABLE_DEBUG_LOG`）时：

```cpp
MYPROJ_LOG_DEBUG() << "value=" << expensive_computation();
```

编译器看到的等价代码是：
```cpp
// enabled_ = false，operator<< 内 if(enabled_) 跳过所有操作
// expensive_computation() 不会被调用（短路求值保证）
```

可以通过以下方式验证零开销：
```bash
# 编译后检查汇编，确认没有字符串常量和函数调用
objdump -d -M intel release_binary | grep -A5 "expensive_computation"
# 预期：Release 版本中无相关调用
```

## 预期输出示例

```python
>>> from myproj.debug import setup_debug
>>> setup_debug()
14:32:01 [DEBUG] myproj: Debug logging enabled (C++ level=1, Python level=10)

# C++ 层输出（通过 std::cout/stderr 直接输出）
[DEBUG] demo_layer.cc:20 (DemoLayer) [LAYER] DemoLayer constructed: output_size=128 use_bias=1
[DEBUG] demo_layer.cc:30 (Init) [LAYER] DemoLayer Init: input_shape=[784] input_size=784 output_size=128
[DEBUG] demo_layer.cc:36 (Init) [TENSOR] DemoLayer: created weight buffer [784x128] = 100352 floats
[DEBUG] demo_layer.cc:42 (Init) [TENSOR] DemoLayer: created bias buffer [128] floats
[DEBUG] demo_layer.cc:68 (Forward) [LAYER] DemoLayer Forward: batch=32 M=32 N=128 K=784 use_bias=1
[DEBUG] demo_layer.cc:88 (Forward) [LAYER] DemoLayer Forward: total_loss=42.305 (avg=0.0103)

>>> setup_trace()
14:32:15 [DEBUG] myproj: Trace mode enabled (level=0)
[TRACE] blob.cpp:45 (Blob) [MEM] Buffer allocated: size=401408 ptr=0x2a3b1c0
[TRACE] blob.cpp:62 (~Blob) [MEM] Buffer freed: ptr=0x2a3b1c0 construction backtrace:
  #0 Blob::Blob at blob.cpp:45
  #1 DemoLayer::Init at demo_layer.cc:35
  #2 main at main.cc:28
```

## 反模式清单

| ❌ 反模式 | ✅ 正确做法 |
|-----------|-----------|
| C++ 层直接 `std::cout << "debug"` | 用 `MYPROJ_LOG_DEBUG()` 宏，受级别控制 |
| FFI 层传字符串 `"DEBUG"` 作级别 | 传 int（0-4），字符串转换在两端各自处理 |
| Python 层只配 logging 不调 set_log_level | 必须通过 FFI 同步 C++ 级别，否则两层独立 |
| 每次 setup_debug 都 add Handler 不清理 | 先 `_clear_handlers()` 再添加，保证幂等 |
| Release 构建仍定义 ENABLE_DEBUG_LOG | Release 默认 OFF，仅 Debug/排障时开启 |
| 内层循环中打日志 | 只在循环外打一次维度信息 |
| ERROR 日志用 std::cout | Logger 自动路由 ERROR→stderr，WARN→cout |
| 同一消息拆成多个 `<<` Logger 实例 | 用 std::ostringstream 先格式化再单次输出 |
| 组件标签硬编码字符串 `"[MEM]"` | 定义宏 `MYPROJ_MEM_LOG` 统一前缀格式 |

## 不同 FFI 框架适配指南

| 框架 | 桥接方式 | Python 调用 |
|------|---------|------------|
| pybind11 | `m.def("set_log_level", &fn)` | `from . import _myproj; _myproj.set_log_level(1)` |
| ctypes | `extern "C"` 导出 + CDLL | `lib = ctypes.CDLL("libmyproj.so"); lib.myproj_set_log_level(1)` |
| cffi (CFFI) | `extern "C"` 导出 + ffi.cdef | `lib = ffi.dlopen("libmyproj.so"); lib.myproj_set_log_level(1)` |
| PyO3 (Rust) | `#[pyfunction]` 包装 | 同 pybind11 |
| TVM FFI | `FunctionRegistry::Global()` | `tvm.ffi.get_global_func("myproj.SetLogLevel")(1)` |
| Go cgo | `//extern` 注释 + `import "C"` | `C.myproj_set_log_level(1)` |

## 与其他模式的关系

- **[cpp-nullstream-logging](../cpp-nullstream-logging.md)**：纯 C++ 场景下用 NullStream 模板实现零开销日志（本模式 C++ 层是其简化版，用 `if(enabled_)` 替代模板吸收）
- **[dual-channel-tiered-logging](../dual-channel-tiered-logging.md)**：纯 Python 场景控制台+文件双轨输出（本模式 Python 层的 Handler 管理借鉴了其思路）
- **[cross-platform-backtrace-leak-diagnosis](../cross-platform-backtrace-leak-diagnosis.md)**：本日志模式 TRACE 级别输出构造栈的典型应用
- **[resource-counter-primitive-binding](../resource-counter-primitive-binding.md)**：资源计数器在 `[MEM]` 标签日志中读取
- **[ffi-memory-leak-autouse-fixture](../ffi-memory-leak-autouse-fixture.md)**：测试 fixture 利用本模式的 `setup_trace()` 开启泄漏诊断

## 检验清单

集成完成后，验证以下 6 项：

1. **零开销**：Release 构建下 DEBUG 日志不产生任何字符串拼接（objdump 验证）
2. **单入口控制**：`setup_debug()` 后 C++ DEBUG 立即输出；`setup_quiet()` 后立即停止
3. **级别对齐**：`set_log_level(0)` 看到 TRACE；`set_log_level(4)` 只看到 ERROR
4. **幂等安全**：连续 `setup_debug()` 三次，同一行日志只输出一次
5. **无残留**：`setup_debug()` → `setup_quiet()` 后无残留 Handler
6. **grep 友好**：`[MEM]`/`[LAYER]` 标签能精确过滤对应模块日志

## 来源

本模式从 caffe-ffi 项目（深度学习推理框架 FFI 绑定）的生产实践中萃取，已在 20+ 计算模块（卷积、全连接、Softmax、池化、归一化、损失函数等）中验证通过。

- 原始实现：[caffe-ffi/log.hpp](../../../../../../projects/xuanspace/vendor/caffe/caffe-ffi/include/caffe_ffi/log.hpp)
- 模式文档：[cross-language-three-layer-logging.md](../../cross-language-three-layer-logging.md)
