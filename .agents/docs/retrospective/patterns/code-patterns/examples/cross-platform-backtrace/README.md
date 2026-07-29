# 跨平台堆栈回溯泄漏检测示例包

可独立编译运行的C++示例，演示完整的「检测→定位」内存泄漏诊断模式。

## 文件清单

| 文件 | 用途 |
|------|------|
| [backtrace.hpp](backtrace.hpp) | 跨平台堆栈捕获头文件（Windows DbgHelp / Linux execinfo） |
| [log.hpp](log.hpp) | 配套轻量分级日志（TRACE/DEBUG/INFO/WARN/ERROR + NullStream零开销） |
| [tracked_object.hpp](tracked_object.hpp) | RAII可追踪对象基类（原子计数器+构造栈捕获+析构TRACE输出） |
| [demo.cc](demo.cc) | 主演示程序（正常生命周期/故意泄漏/ad-hoc栈回溯） |
| [CMakeLists.txt](CMakeLists.txt) | CMake构建脚本（独立，无外部依赖） |

## 快速构建运行

```bash
mkdir build && cd build
cmake .. -DDEMO_ENABLE_BACKTRACE=ON -DDEMO_ENABLE_LOG=ON
cmake --build . --config Release

# 默认WARN级别：只输出检测结果，不打印构造栈
./leak_demo

# TRACE级别：析构时自动打印每个对象的构造栈
./leak_demo --trace
```

Windows MSVC（Developer Command Prompt）：
```cmd
mkdir build && cd build
cmake .. -G "Visual Studio 17 2022" -A x64 -DDEMO_ENABLE_BACKTRACE=ON -DDEMO_ENABLE_LOG=ON
cmake --build . --config Release
Release\leak_demo.exe --trace
```

## 工作流演示

1. **正常路径**：创建2个Resource对象→离开作用域→自动析构→`live_count=0`无泄漏
2. **泄漏路径**：通过`new`返回裸指针但不delete→`live_count=1`检测到泄漏
3. **定位**：加`--trace`重新运行→TRACE日志中最后一个未匹配析构的`construction backtrace`就是泄漏源
4. **ad-hoc API**：`backtrace::GetBacktrace(skip)`可任意点打印调用栈

## 集成到你自己项目的三步法

### Step 1：复制头文件
将 `backtrace.hpp` 和 `log.hpp` 复制到你的项目 include 目录。

### Step 2：CMake 配置
```cmake
option(MYPROJ_ENABLE_BACKTRACE "Enable stack backtrace for leak diagnosis" ON)
if(MYPROJ_ENABLE_BACKTRACE)
  target_compile_definitions(your_lib PUBLIC MYPROJ_ENABLE_BACKTRACE)
endif()
if(MSVC)
  target_link_libraries(your_lib PUBLIC DbgHelp.lib)
endif()
```

注意：把代码中的 `DEMO_ENABLE_BACKTRACE` 宏名替换为你项目的宏名。

### Step 3：在目标类中添加3样东西
```cpp
#include "your_project/backtrace.hpp"

class YourObject {
 public:
  YourObject() : id_(g_next_id++) {
    g_live_count.fetch_add(1);
    construct_bt_ = backtrace::GetBacktrace(3);  // 构造时捕获
    // ... 分配资源
  }
  ~YourObject() {
    // 1. 先输出常规析构日志
    // 2. 释放资源
    // 3. TRACE输出构造栈
    MY_LOG_TRACE() << "Object#" << id_
                   << " construction backtrace:\n" << construct_bt_;
    g_live_count.fetch_sub(1);
  }
  std::string construction_backtrace() const { return construct_bt_; }
 private:
  int64_t id_;
  std::string construct_bt_;  // 存储构造栈
};
```

### Step 4：FFI暴露（如需要）
参考caffe-ffi模式，通过静态注册块暴露全局`GetBacktrace`函数和对象`construction_backtrace`属性。

### Step 5：Python层（如需要）
```python
def get_backtrace(skip_frames=0, max_frames=32):
    fn = _ffi.get_global_func("your_project.GetBacktrace")
    return str(fn(skip_frames, max_frames)) if fn else "(backtrace unavailable)"
```

## 预期输出示例（--trace模式）

```
[INFO] --- Intentional leak test ---
[DEBUG][OBJ] [LIFECYCLE] TrackedObject#3 constructed this=0x... live=3
[DEBUG][MEM] [ALLOC] Resource#3 name='leaked-buffer' size=4096 ptr=0x...
[INFO] After leaking allocation: live TrackedObjects: 1  *** POTENTIAL LEAK DETECTED ***
[TRACE] [LIFECYCLE] TrackedObject#2 construction backtrace:
  #0 0x... in make_resource at demo.cc:52
  #1 0x... in do_work_normal at demo.cc:68
  #2 0x... in main at demo.cc:108
...
>>> The last construction backtrace that has NO matching destruction is the leak source. <<<
```

## 关键设计要点

- **构造时捕获**，不是析构时——析构时捕获得到的是析构路径而非分配路径
- **TRACE级别输出**，DEBUG及以下默认静默，生产零开销
- **编译期开关**，关闭时整个backtrace代码被预处理器排除
- **友好降级**，未启用backtrace时返回提示字符串而非崩溃
- **skip_frames正确**：从构造函数调用时传3（GetBacktrace→构造函数→make_unique/make_object→调用点）
