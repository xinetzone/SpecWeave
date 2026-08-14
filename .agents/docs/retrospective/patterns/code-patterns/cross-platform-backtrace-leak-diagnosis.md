---
id: "cross-platform-backtrace-leak-diagnosis"
source: "caffe-ffi 内存调试日志体系实践 (2026-07-28)"
status: "validated"
maturity: "L2"
validation_count: 1
reuse_count: 0
tags: ["cpp", "debugging", "memory-leak", "backtrace", "cross-platform", "ffi", "diagnostics"]
---

# 跨平台堆栈回溯泄漏源定位模式

> 📦 **可执行示例包**：见 [examples/cross-platform-backtrace/](examples/cross-platform-backtrace/README.md)，包含独立CMake构建的演示程序、backtrace/log/tracked_object头文件和完整README，可直接编译运行验证模式效果。

## 模式概述

内存泄漏自动检测（计数器+autouse fixture）只能回答"**有没有泄漏、泄漏了多少**"，但无法回答"**泄漏的对象是在哪里创建的**"。本模式通过在**对象构造时捕获调用栈**、**析构时低级别日志输出**，形成"检测→定位"的完整可观测性闭环：自动fixture发现泄漏→开启TRACE日志重新运行→析构日志自动打印构造栈→直接定位源代码行号。支持 Windows（DbgHelp）和 Linux（execinfo.h）双平台，编译期开关控制，生产环境零开销。

## 触发场景

- C++ 原生扩展通过 FFI 暴露给 Python/其他语言，需要自动化检测并定位内存泄漏
- 自动泄漏检测（计数器/fixture）已就位，但缺少泄漏源定位能力
- 需要跨平台支持（Windows MSVC + Linux GCC/Clang）
- 生产环境需要零开销，仅在调试诊断时启用堆栈捕获
- 对象生命周期复杂，无法通过代码审查轻易定位泄漏点
- 需要在析构时自动输出创建上下文，无需手动在每个可能泄漏点加断点

## 核心步骤

### 1. 跨平台 backtrace.hpp 头文件（零依赖、包含即用）

```cpp
// backtrace.hpp
#pragma once
#include <cstring>
#include <sstream>
#include <string>
#include <vector>

#if defined(_WIN32) && defined(YOUR_PROJECT_ENABLE_BACKTRACE)
  #ifndef WIN32_LEAN_AND_MEAN
    #define WIN32_LEAN_AND_MEAN
  #endif
  #include <windows.h>
  #include <dbghelp.h>
#endif

#if defined(__linux__) && defined(YOUR_PROJECT_ENABLE_BACKTRACE)
  #include <execinfo.h>
#endif

namespace your_project {
namespace backtrace {

static constexpr int kMaxFrames = 32;
static constexpr int kSkipFrames = 2;  // 跳过 GetBacktrace 自身帧

inline std::string GetBacktrace(int skip_frames = kSkipFrames, int max_frames = kMaxFrames) {
  if (max_frames <= 0) max_frames = kMaxFrames;
  if (skip_frames < 0) skip_frames = 0;
  std::ostringstream oss;

#if defined(_WIN32) && defined(YOUR_PROJECT_ENABLE_BACKTRACE)
  // Windows: CaptureStackBackTrace + DbgHelp 符号解析
  void* frames[kMaxFrames];
  USHORT captured = CaptureStackBackTrace(
      static_cast<ULONG>(skip_frames), static_cast<ULONG>(max_frames), frames, nullptr);

  HANDLE process = GetCurrentProcess();
  static bool sym_initialized = false;
  if (!sym_initialized) {
    SymSetOptions(SYMOPT_LOAD_LINES | SYMOPT_UNDNAME | SYMOPT_DEFERRED_LOADS);
    SymInitialize(process, nullptr, TRUE);
    sym_initialized = true;
  }

  char symbol_buffer[sizeof(SYMBOL_INFO) + MAX_SYM_NAME * sizeof(TCHAR)];
  SYMBOL_INFO* symbol = reinterpret_cast<SYMBOL_INFO*>(symbol_buffer);
  symbol->SizeOfStruct = sizeof(SYMBOL_INFO);
  symbol->MaxNameLen = MAX_SYM_NAME;

  IMAGEHLP_LINE64 line_info;
  line_info.SizeOfStruct = sizeof(IMAGEHLP_LINE64);
  DWORD displacement = 0;

  for (USHORT i = 0; i < captured; ++i) {
    DWORD64 addr = reinterpret_cast<DWORD64>(frames[i]);
    oss << "  #" << i << " " << frames[i];
    if (SymFromAddr(process, addr, nullptr, symbol)) {
      oss << " in " << symbol->Name;
    }
    if (SymGetLineFromAddr64(process, addr, &displacement, &line_info)) {
      const char* basename = std::strrchr(line_info.FileName, '\\');
      if (!basename) basename = std::strrchr(line_info.FileName, '/');
      basename = basename ? basename + 1 : line_info.FileName;
      oss << " at " << basename << ":" << line_info.LineNumber;
    }
    oss << "\n";
  }
#elif defined(__linux__) && defined(YOUR_PROJECT_ENABLE_BACKTRACE)
  // Linux: backtrace + backtrace_symbols
  void* frames[kMaxFrames];
  int n = ::backtrace(frames, max_frames + skip_frames);
  char** symbols = ::backtrace_symbols(frames, n);
  if (symbols) {
    int idx = 0;
    for (int i = skip_frames; i < n; ++i) {
      oss << "  #" << idx++ << " " << symbols[i] << "\n";
    }
    ::free(symbols);
  }
#else
  // 降级：未启用 backtrace 时返回友好提示，不崩溃
  oss << "  (backtrace not available: rebuild with YOUR_PROJECT_ENABLE_BACKTRACE=ON)\n";
  (void)skip_frames;
#endif

  return oss.str();
}

inline void PrintBacktrace(int skip_frames = kSkipFrames, int max_frames = kMaxFrames) {
  std::string bt = GetBacktrace(skip_frames + 1, max_frames);
  std::cerr << "Backtrace:\n" << bt;
  std::cerr.flush();
}

}  // namespace backtrace
}  // namespace your_project

// 便捷宏：跳过宏自身帧，直接获取当前调用栈
#define YOUR_PROJECT_BACKTRACE_STR() ::your_project::backtrace::GetBacktrace(2)
#define YOUR_PROJECT_BACKTRACE_STR_SKIP(skip) ::your_project::backtrace::GetBacktrace(2 + (skip))
```

### 2. 在目标类中添加构造栈捕获成员

```cpp
// your_object.hpp
#include "your_project/backtrace.hpp"

class YourObject {
 public:
  YourObject();
  explicit YourObject(ShapeView shape);
  ~YourObject();

  // 暴露构造栈供 Python/调试器访问
  std::string construction_backtrace() const { return construct_bt_; }

 private:
  int64_t id_;                           // 对象唯一序列号（防止指针复用混淆）
  std::string construct_bt_;             // 构造时捕获的调用栈
  // ... 其他成员
};
```

### 3. 构造时捕获堆栈，析构时 TRACE 日志输出

```cpp
// your_object.cpp
YourObject::YourObject() : id_(g_next_id.fetch_add(1)) {
  g_live_count.fetch_add(1);
  construct_bt_ = backtrace::GetBacktrace(3);  // 跳过3帧：GetBacktrace+构造函数+调用点
  // ... 构造逻辑
}

YourObject::YourObject(ShapeView shape) : id_(g_next_id.fetch_add(1)) {
  g_live_count.fetch_add(1);
  construct_bt_ = backtrace::GetBacktrace(3);
  // ... 构造逻辑
}

YourObject::~YourObject() {
  // 1. 先输出析构日志（字节数、live_count等）
  int64_t freed_bytes = ComputeSize();
  CAFFE_FFI_MEM_LOG << "[MEM-FREE] Object#" << id_ << " freed=" << freed_bytes << "B"
                    << " live=" << g_live_count.load() - 1;

  // 2. 显式释放持有的资源（触发 FreeData 原语，更新计数器）
  data_tensor_ = Tensor();
  diff_tensor_ = Tensor();

  // 3. TRACE 级别输出构造栈——默认 WARN 下完全静默
  CAFFE_FFI_LOG_TRACE() << "[MEM-LIFECYCLE] Object#" << id_
                        << " construction backtrace:\n" << construct_bt_;
}
```

**关键顺序要求**：
1. 先输出常规析构日志（释放字节数等）
2. 再显式重置资源（智能指针/Tensor 重置），确保 FreeData 原语执行
3. 最后输出构造栈——此时资源已释放，计数器已更新，日志上下文完整

### 4. CMake 编译控制（默认 ON，可关闭裁剪）

```cmake
# CMakeLists.txt
option(YOUR_PROJECT_ENABLE_BACKTRACE "Enable stack backtrace for memory leak diagnosis" ON)

if(YOUR_PROJECT_ENABLE_BACKTRACE)
  target_compile_definitions(your_lib PUBLIC YOUR_PROJECT_ENABLE_BACKTRACE)
endif()

if(MSVC)
  # Windows 需要链接 DbgHelp.lib（系统库，无需额外安装）
  target_link_libraries(your_lib PUBLIC DbgHelp.lib)
endif()
```

### 5. FFI 双端暴露（C++ 全局函数 + 对象属性 + Python API）

**C++ FFI 注册**：
```cpp
// _ffi_bindings.cc
std::string GetBacktraceString(int skip_frames, int max_frames) {
  return backtrace::GetBacktrace(skip_frames + 1, max_frames);  // +1 跳过本函数帧
}

TVM_FFI_STATIC_INIT_BLOCK() {
  tvm::ffi::refl::GlobalDef()
      .def("your_project.GetBacktrace", GetBacktraceString);

  tvm::ffi::refl::ObjectDef<YourObject>()
      // ... 其他方法
      .def("construction_backtrace", &YourObject::construction_backtrace);
}
```

**Python 层 API + 降级处理**：
```python
# your_project/__init__.py
def get_backtrace(skip_frames: int = 0, max_frames: int = 32) -> str:
    """Get a C++ stack backtrace string for debugging."""
    if _ffi_api.is_available():
        fn = _ffi_api.get_global_func("your_project.GetBacktrace")
        if fn is not None:
            return str(fn(skip_frames, max_frames))
    return "(backtrace not available: C++ extension missing or build without backtrace)"

class YourObject:
    @property
    def construction_backtrace(self) -> str:
        """Backtrace captured at object construction time (leak source location)."""
        if self._is_native and self._native_construction_backtrace is not None:
            return self._native_construction_backtrace(self)
        return "(backtrace not available: Python-only mode)"
```

## 反模式

### ❌ 反模式1：在析构函数中实时捕获堆栈（而非构造时）

```cpp
// 错误：析构时才捕获堆栈，此时调用栈是析构路径而非分配路径
~YourObject() {
    std::string bt = backtrace::GetBacktrace();  // 得到的是析构栈，不是构造栈！
    LOG << "destroyed, allocated at:\n" << bt;    // 输出的是析构位置，没用
}
```

**结果**：得到的是析构时的调用栈（谁触发了delete），而不是对象创建时的调用栈（谁分配了对象）。必须在**构造时**捕获并存储。

### ❌ 反模式2：使用 DEBUG 而非 TRACE 级别输出构造栈

```cpp
// 错误：使用 DEBUG 级别，日常调试时会输出大量无关的构造栈
CAFFE_FFI_LOG_DEBUG() << "construction backtrace:\n" << construct_bt_;
```

**结果**：开启 DEBUG 日志时，每个对象析构都会输出几十行堆栈信息，日志被淹没。构造栈是**诊断专用**信息，仅在精确定位泄漏时才需要，必须使用最低的 TRACE 级别。

### ❌ 反模式3：跳过帧数量硬编码错误

```cpp
// 错误：GetBacktrace(0) 不跳过自身帧，输出包含 backtrace::GetBacktrace 内部帧
construct_bt_ = backtrace::GetBacktrace(0);
```

**结果**：堆栈顶部几帧是 backtrace 库自身的内部函数，干扰阅读。需要根据调用层次正确设置 skip_frames：
- 从对象构造函数直接调用：skip=3（GetBacktrace→构造函数→make_object→调用点）
- 从便捷宏 `YOUR_PROJECT_BACKTRACE_STR()` 调用：自动 skip=2（宏展开+GetBacktrace）
- 从 FFI 绑定函数调用：skip+1（额外跳过 FFI 包装函数帧）

### ❌ 反模式4：未提供降级实现，stub/Python-only 模式崩溃

```cpp
// 错误：未启用backtrace时没有#else分支，调用GetBacktrace()链接错误
// 或者Python层直接调用None()崩溃
```

**结果**：关闭backtrace编译选项后链接失败，或Python-only模式下调用`get_backtrace()`抛AttributeError。必须在预处理器#else分支和Python层都提供友好降级。

### ❌ 反模式5：每次访问 construction_backtrace 时重新捕获

```cpp
// 错误：property每次访问都重新walk stack，而不是返回存储的构造栈
std::string construction_backtrace() const {
    return backtrace::GetBacktrace(2);  // 返回的是当前访问栈，不是构造栈！
}
```

**结果**：每次访问属性都得到当前调用栈，完全失去"泄漏源定位"的意义。必须在构造时一次性捕获并存储为成员变量。

## 与其他模式的协同工作流

```mermaid
flowchart TD
    A[运行pytest] --> B{autouse fixture<br/>检测泄漏?}
    B -->|否| C[测试通过]
    B -->|是: 泄漏N字节/M个对象| D[开启TRACE日志]
    D --> E[enable_debug_logging(LOG_LEVEL_TRACE)]
    E --> F[重新运行失败的测试]
    F --> G[析构时自动输出<br/>每个已释放对象的构造栈]
    G --> H{live_count==0?}
    H -->|是| I[检查未析构对象的<br/>上一个构造栈输出]
    H -->|否| J[TRACE日志最后一个<br/>未匹配析构的构造栈]
    I --> K[定位源代码文件名:行号]
    J --> K
    K --> L[修复泄漏点: 添加<br/>缺失的delete/RAII封装]
    L --> A

    classDef detect fill:#ffebee,stroke:#c62828,color:#b71c1c
    classDef diagnose fill:#fff3e0,stroke:#ef6c00,color:#e65100
    classDef fix fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    class B,D,G detect
    class E,F,H,I,J diagnose
    class K,L fix
```

**配套模式**：
- 上游：[FFI内存测试自动泄漏检测模式](ffi-memory-leak-autouse-fixture.md)（计数器+autouse fixture）负责检测
- 本模式：负责定位
- 下游：[资源计数器原语绑定模式](resource-counter-primitive-binding.md)（RAII资源追踪）确保计数器本身正确
- 日志基础：[C++ NullStream 零开销日志模式](cpp-nullstream-logging.md) 提供分级日志框架
- 零拷贝验证：[零拷贝张量访问验证模式](zero-copy-tensor-verification.md) 验证张量视图的内存共享语义

## 迁移验证

- ✅ **caffe-ffi Blob类**：
  - 3个构造函数统一捕获构造栈（skip=3帧）
  - 析构时TRACE级别输出，默认WARN下完全静默
  - `Blob.construction_backtrace` Python属性可随时访问
  - `caffe_ffi.get_backtrace()` 全局函数可任意点捕获
  - Python-only stub模式降级为友好提示
  - CMake `CAFFE_FFI_ENABLE_BACKTRACE=ON`（默认）编译通过
  - Windows MSVC 自动链接 DbgHelp.lib
  - 36个pytest全部通过，零回归
  - 自动泄漏fixture + 构造栈输出形成完整诊断闭环

## 适配指南：裸指针 FFI API（npu-ffi Buffer类）

> **架构差异**：caffe-ffi Blob 通过 TVM FFI Object 系统管理，C++ 对象生命周期与 FFI 绑定；而 npu-ffi Buffer 通过**裸指针(int64_t handle)** 在 FFI 层传递，C++ `Buffer` 类与 FFI `buffer_alloc`/`buffer_free` 函数是独立路径——Python 层直接持有整数指针，调用 `buffer_free` 释放。这种 C 风格 FFI 不能直接用「C++成员变量存储构造栈」的方式，需要**全局句柄表映射**适配。

### 架构对比

| 维度 | caffe-ffi Blob（Object 风格） | npu-ffi Buffer（裸指针风格） |
|------|-------------------------------|-------------------------------|
| FFI传递方式 | ObjectPtr\<Blob\>（智能指针） | int64_t（裸指针整数） |
| 构造路径 | `make_object<Blob>()` → 构造函数 | `npu_ffi_vta_buffer_alloc(size)` → malloc |
| 析构路径 | Object 引用计数归零时析构函数 | `npu_ffi_vta_buffer_free(ptr)` → free |
| 构造栈存储 | Blob::construct_bt_ 成员变量 | 全局 unordered_map\<ptr, {bt, size}\> |
| Python层对象 | 持有NativeBlob，FFI自动管理生命周期 | 持有int指针，手动__del__调用buffer_free |

### 步骤 1：复制 backtrace.hpp（同标准模式）

将 [caffe-ffi/include/caffe_ffi/backtrace.hpp](../../../../../../projects/xuanspace/vendor/caffe/caffe-ffi/include/caffe_ffi/backtrace.hpp) 复制到 `npu-ffi/include/npu_ffi/backtrace.hpp`，将命名空间改为 `npu_ffi::backtrace`，宏前缀改为 `NPU_FFI_ENABLE_BACKTRACE`，skip 常量设为 2。

### 步骤 2：在 runtime_common.cc 添加全局句柄表 + 原子计数器

```cpp
// src/vta/runtime_common.cc
#include <npu_ffi/backtrace.hpp>
#include <npu_ffi/logging.h>
#include <atomic>
#include <mutex>
#include <unordered_map>

namespace {

std::atomic<int> live_buffer_count{0};

#ifdef NPU_FFI_ENABLE_BACKTRACE
struct BufferDebugInfo {
  std::string construct_bt;
  size_t size;
};
std::mutex g_buffer_map_mutex;
std::unordered_map<void*, BufferDebugInfo> g_buffer_debug_map;
#endif

}  // namespace
```

### 步骤 3：修改 buffer_alloc / buffer_free C 函数

```cpp
extern "C" void* npu_ffi_vta_buffer_alloc(size_t size) {
  void* data = VTABufferAlloc(size);  // 原有分配逻辑
  if (data) {
    live_buffer_count.fetch_add(1, std::memory_order_relaxed);
    VTA_DLOG(INFO) << "Buffer allocated: ptr=" << data << " size=" << size
                  << " live_count=" << live_buffer_count.load();
#ifdef NPU_FFI_ENABLE_BACKTRACE
    std::lock_guard<std::mutex> lock(g_buffer_map_mutex);
    g_buffer_debug_map[data] = {
      npu_ffi::backtrace::GetBacktrace(2),  // skip: GetBacktrace→本函数→调用点
      size
    };
#endif
  }
  return data;
}

extern "C" void npu_ffi_vta_buffer_free(void* buffer) {
  if (buffer) {
    int remaining = live_buffer_count.fetch_sub(1, std::memory_order_relaxed) - 1;
    VTA_DLOG(INFO) << "Buffer freed: ptr=" << buffer
                  << " remaining_live=" << remaining;
#ifdef NPU_FFI_ENABLE_BACKTRACE
    std::string bt;
    size_t size = 0;
    {
      std::lock_guard<std::mutex> lock(g_buffer_map_mutex);
      auto it = g_buffer_debug_map.find(buffer);
      if (it != g_buffer_debug_map.end()) {
        bt = std::move(it->second.construct_bt);
        size = it->second.size;
        g_buffer_debug_map.erase(it);
      }
    }
    // TRACE级别输出：开启TRACE日志后每个析构自动打印构造栈
    VTA_DLOG(TRACE) << "Buffer freed, was allocated here (size=" << size << "):\n" << bt;
#endif
  }
  VTABufferFree(buffer);  // 原有释放逻辑
}
```

> **注意**：VTA_DLOG 需要先添加 TRACE 级别支持（见步骤4）。如果不想修改现有日志系统，也可以直接用 `fprintf(stderr, ...)` 在 `#ifdef NPU_FFI_ENABLE_BACKTRACE` 块内输出。

### 步骤 4：日志系统适配（npu-ffi logging.h）

当前 `npu-ffi/include/npu_ffi/logging.h` 只有 INFO/ERROR/WARNING/FATAL 四级，需要添加 TRACE 级别，参考 caffe-ffi 的零开销 NullStream 模式：

```cpp
// 在 logging.h 中添加
enum LogLevel { TRACE = 0, DEBUG = 1, INFO = 2, WARNING = 3, ERROR = 4, FATAL = 5 };

#ifdef NPU_FFI_ENABLE_LOG
// 现有 LogStream 实现扩展支持 TRACE 级别
// 运行时可通过环境变量 NPU_FFI_LOG_LEVEL=0 开启TRACE
class VtaLogStream {
 public:
  VtaLogStream(LogLevel level, const char* file, int line);
  ~VtaLogStream();
  template <typename T>
  VtaLogStream& operator<<(const T& msg) {
    if (level_ >= current_level_) { /* 输出 */ }
    return *this;
  }
 private:
  LogLevel level_;
};
#else
// NullStream 零开销模式：所有operator<<都是空操作
class NullStream {
 public:
  template <typename T>
  NullStream& operator<<(const T&) { return *this; }
};
#define VTA_DLOG(level) ::npu_ffi::NullStream()
#endif
```

**快速降级方案**：如果不想扩展日志系统，可以在 `#ifdef NPU_FFI_ENABLE_BACKTRACE` 块内直接使用 `fprintf(stderr, ...)` 输出，通过环境变量 `NPU_FFI_BACKTRACE_VERBOSE=1` 控制是否打印每个free的构造栈：

```cpp
// 无需修改日志系统的快速方案
#ifdef NPU_FFI_ENABLE_BACKTRACE
    {
      std::lock_guard<std::mutex> lock(g_buffer_map_mutex);
      auto it = g_buffer_debug_map.find(buffer);
      if (it != g_buffer_debug_map.end()) {
        bt = std::move(it->second.construct_bt);
        size = it->second.size;
        g_buffer_debug_map.erase(it);
      }
    }
    static bool verbose = []() {
      const char* e = getenv("NPU_FFI_BACKTRACE_VERBOSE");
      return e && (e[0] == '1' || tolower(e[0]) == 't');
    }();
    if (verbose && !bt.empty()) {
      fprintf(stderr, "[NPU_FFI TRACE] Buffer free, ptr=%p size=%zu, constructed at:\n%s\n",
              buffer, size, bt.c_str());
    }
#endif
```

### 步骤 5：CMakeLists.txt 添加编译开关和 DbgHelp 链接

在 [src/vta/CMakeLists.txt](../../../../../projects/xuanspace/libs/npu-ffi/src/vta/CMakeLists.txt) 中添加：

```cmake
option(NPU_FFI_ENABLE_BACKTRACE "Enable stack backtrace for buffer leak diagnosis" ON)

if(NPU_FFI_ENABLE_BACKTRACE)
  message(STATUS "npu-ffi: buffer backtrace leak diagnosis ENABLED")
  target_compile_definitions(npu_ffi_vta PRIVATE NPU_FFI_ENABLE_BACKTRACE)
  if(MSVC)
    target_link_libraries(npu_ffi_vta PRIVATE DbgHelp.lib)
  endif()
else()
  message(STATUS "npu-ffi: buffer backtrace disabled (set NPU_FFI_ENABLE_BACKTRACE=ON to enable)")
endif()
```

在顶层 [CMakeLists.txt](../../../../../projects/xuanspace/libs/npu-ffi/CMakeLists.txt) 的 `option()` 区域添加一行：

```cmake
option(NPU_FFI_ENABLE_BACKTRACE "Enable stack backtrace for buffer leak diagnosis" ON)
```

### 步骤 6：FFI 层暴露 buffer_get_construction_backtrace 函数

在 [src/vta/ffi_registry.cc](../../../../../projects/xuanspace/libs/npu-ffi/src/vta/ffi_registry.cc) 中添加查询函数：

```cpp
#ifdef NPU_FFI_ENABLE_BACKTRACE
#include <npu_ffi/backtrace.hpp>
#include <mutex>
#include <unordered_map>
extern std::mutex g_buffer_map_mutex;
extern std::unordered_map<void*, /* BufferDebugInfo */ void*> g_buffer_debug_map;
// （实际需要将g_buffer_map_mutex和g_buffer_debug_map的声明放到头文件中暴露，
//  或者在runtime_common.cc中提供查询函数）
#endif

std::string buffer_get_construction_backtrace(int64_t ptr) {
#ifdef NPU_FFI_ENABLE_BACKTRACE
  void* data = reinterpret_cast<void*>(static_cast<intptr_t>(ptr));
  std::lock_guard<std::mutex> lock(g_buffer_map_mutex);
  auto it = g_buffer_debug_map.find(data);
  if (it != g_buffer_debug_map.end()) {
    return it->second.construct_bt;
  }
  return "(buffer not found in debug map: already freed or not allocated via buffer_alloc)";
#else
  return "(backtrace not available: build with -DNPU_FFI_ENABLE_BACKTRACE=ON)";
#endif
}

// 在 TVM_FFI_STATIC_INIT_BLOCK 中注册：
//   .def("vta.buffer_get_construction_backtrace", buffer_get_construction_backtrace)
```

### 步骤 7：Python Buffer 层暴露属性（可选）

在 [python/npu_ffi/vta/buffer.py](../../../../../projects/xuanspace/libs/npu-ffi/python/npu_ffi/vta/buffer.py) 添加：

```python
@property
def construction_backtrace(self) -> str:
    """Get the stack backtrace captured when this buffer was allocated (for leak diagnosis)."""
    if self._data != 0 and self._owns:
        try:
            fn = _ffi_api.get_global_func("vta.buffer_get_construction_backtrace")
            if fn is not None:
                return str(fn(self._data))
        except Exception:
            pass
    return "(backtrace not available: buffer is non-owning, already freed, or backtrace disabled)"
```

### 步骤 8：添加 pytest autouse fixture 检测泄漏

```python
# tests/conftest.py
import os
import pytest

@pytest.fixture(autouse=True)
def check_buffer_leaks():
    # npu-ffi需要暴露GetLiveBufferCount() C++函数
    # 参考caffe-ffi get_live_blob_count()的实现
    from npu_ffi._ffi_api import get_global_func
    get_count_fn = get_global_func("vta.get_live_buffer_count")
    before = int(get_count_fn()) if get_count_fn else 0
    yield
    if get_count_fn:
        after = int(get_count_fn())
        leaked = after - before
        if leaked > 0:
            pytest.fail(f"Buffer leak detected: {leaked} buffer(s) not freed! "
                        f"Set NPU_FFI_BACKTRACE_VERBOSE=1 and re-run to see allocation stacks.")
```

### 裸指针风格适配要点

1. **全局 map + mutex**：裸指针 FFI 没有C++对象来携带构造栈，必须用线程安全的全局映射表维护 `ptr→debug_info` 关系
2. **alloc 插入 / free 移除**：在C函数入口处插入，出口处移除和打印，不改变原有内存管理逻辑
3. **skip_frames = 2**：从 `npu_ffi_vta_buffer_alloc` C函数调用时，比Object构造函数少一层间接，跳过2帧即可
4. **map 查找失败容错**：如果传入的ptr不是通过buffer_alloc分配的（如from_foreign_pointer包装的外部指针），map查找会失败，需要优雅降级而非崩溃
5. **非owning Buffer处理**：Python层`from_foreign_pointer()`创建的Buffer owns=False，不会调用buffer_free，因此不会触发map查找，构造栈也不会被捕获（这是正确行为——外部管理的内存不由npu-ffi负责泄漏检测）

## 设计决策与权衡

| 决策 | 选择 | 理由 | 权衡 |
|------|------|------|------|
| 符号解析时机 | **捕获时即解析**（构造时格式化为字符串） | 避免延迟解析的线程安全问题（DbgHelp SymFromAddr 非线程安全）；Blob构造不是热路径，一次性开销可接受 | 构造时有少量CPU开销（符号解析），但析构时零开销 |
| 存储方式 | **std::string 成员** | 一次性格式化，析构时直接输出，无需运行时解析 | 每个Blob多占一个string的内存（通常几百字节，可接受） |
| 堆栈帧深度 | **默认32帧，跳过2-3帧** | 足够覆盖 Python→FFI→C++→业务代码 的完整调用链 | 更深的调用链可能需要调大max_frames |
| 日志级别 | **TRACE(0)** | 默认WARN下完全静默，不产生任何输出；诊断时主动开启 | 需要用户知道TRACE级别存在并主动开启 |
| 平台抽象 | **头文件内inline实现** | 零依赖，无需额外源文件，`#include "backtrace.hpp"` 即用 | 代码全部在头文件中，编译时间略有增加 |
| 编译期开关 | **CMake option 默认ON** | 开发/CI环境默认启用便于调试；发布构建可`-DCAFFE_FFI_ENABLE_BACKTRACE=OFF`完全裁剪 | 需要发布构建时显式关闭，否则DbgHelp链接会增加二进制体积 |
| 降级策略 | **友好提示字符串** | 未启用backtrace或stub模式下返回`"(backtrace not available: ...)"`而非nullptr/崩溃 | 调用方需要检查返回值是否包含"not available"判断是否真的拿到了堆栈 |

## 适用条件

- **语言**：C++11 及以上（template、lambda 需要 C++11）
- **平台**：Windows（MSVC，DbgHelp.lib 系统库）、Linux（glibc execinfo.h）
- **构建系统**：CMake（或支持 compile definitions + 平台条件链接的构建系统）
- **场景**：
  - C++ 原生扩展通过 FFI 暴露给高级语言（Python/JS/Rust等）
  - 已有内存泄漏自动检测机制（原子计数器/autouse fixture）
  - 需要精确定位泄漏源的调试场景
  - 不希望引入第三方堆栈回溯库（如 libunwind、boost::stacktrace）的轻量项目
- **不适用**：
  -  macOS（需额外添加 `<execinfo.h>` 或 Darwin 特定API支持）
  -  已使用 spdlog/glog 等自带堆栈功能的成熟日志库的项目
  -  嵌入式/实时系统（DbgHelp/backtrace 不可用，需自定义实现）
  -  构造路径极热（每秒构造百万级对象）的场景——堆栈捕获有不可忽略的开销

## 可复用代码片段

| 组件 | 位置 | 复用方式 |
|------|------|---------|
| backtrace.hpp 完整头文件 | caffe-ffi/include/caffe_ffi/backtrace.hpp | 复制后替换命名空间和宏前缀即可使用 |
| CMake 链接配置 | caffe-ffi/CMakeLists.txt L11,L127-129,L156 | 复制 option + target_compile_definitions + MSVC DbgHelp 链接三行 |
| Python get_backtrace() | caffe-ffi/python/caffe_ffi/__init__.py L107-125 | 复制函数体，修改全局函数名 |
| Python construction_backtrace property | caffe-ffi/python/caffe_ffi/_core.py L172,L245-250 | 复制native方法缓存+property定义+降级返回 |

## 升级标准（L2 → L3 正式）

当满足以下条件时升级为正式 L3 模式：
1. 在第二个独立 C++ 项目（如 npu-ffi Buffer类、xmnn C++ Tensor类）中实际部署验证
2. 补充 macOS（Darwin）平台的 backtrace 实现
3. 验证线程安全性：多线程并发构造对象时 DbgHelp SymFromAddr 的行为
4. 考虑添加延迟符号解析选项（仅保存返回地址，输出时才解析）以支持热路径场景

## Changelog

<!-- changelog -->
- 2026-07-28 | update | 从candidate升级为validated，补充与[ffi-memory-leak-autouse-fixture](ffi-memory-leak-autouse-fixture.md)、[resource-counter-primitive-binding](resource-counter-primitive-binding.md)、[zero-copy-tensor-verification](zero-copy-tensor-verification.md)的交叉引用
