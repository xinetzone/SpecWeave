# [项目名称] C++ 依赖瘦身优化 - 实现计划

> **模板版本**: v1.0 | 基于 Caffe→tvm-ffi 瘦身实践萃取
> **核心原则**: 兼容层先测 → 增量构建验证 → 每层验证后再进入下一层 → 禁止"大爆炸式"一次性添加所有文件

---

## ⚠️ 增量构建强制规则（MANDATORY BUILD RULES）

> 违反以下规则将导致"大爆炸式"配置/编译错误叠加，调试成本指数级增长。

1. **禁止 `file(GLOB_RECURSE ...)` 收集源文件**：必须显式列出每个源文件路径，每添加一个文件就添加到列表中
2. **增量添加 + 每步编译验证**：
   - 第一步：先让最小核心（5-10个文件）编译通过
   - 第二步：逐层添加源文件（如先 core → 再 util → 再 layers）
   - 第三步：每添加一批文件后立即编译，确认无新错误
   - 第四步：最后才配置链接第三方依赖库
3. **兼容层必须先写且先测**：compat/ 头文件必须在业务代码迁移之前完成，且有独立测试验证语义等价
4. **每步ctest**：每完成一个Task，运行相应的测试验证该Task成果正确，不带着错误进入下一步

---

## [ ] Task 0: 环境验证与准备

- **Priority**: critical（必须最先完成）
- **Depends On**: None
- **Description**:
  - 在目标平台（推荐WSL/Linux for Linux-origin C++ projects）安装构建依赖
    - [编译器：如 build-essential/gcc/g++]
    - [构建工具：cmake, ninja-build/make]
    - [依赖库：如 libprotobuf-dev, protobuf-compiler, libopenblas-dev]
    - [新库依赖：确认 tvm-ffi 等新库在目标平台可编译]
  - 验证编译器版本：`g++ --version`（确认满足 C++[XX] 要求）
  - 验证 cmake 版本：`cmake --version`（>= 3.18）
  - 创建目标目录结构：
    - `[目标目录]/include/[项目名]/`
    - `[目标目录]/include/[项目名]/compat/`
    - `[目标目录]/include/[项目名]/layers/`（如适用）
    - `[目标目录]/include/[项目名]/util/`
    - `[目标目录]/include/[项目名]/proto/`
    - `[目标目录]/src/[项目名]/`
    - `[目标目录]/src/[项目名]/layers/`
    - `[目标目录]/src/[项目名]/util/`
    - `[目标目录]/src/[项目名]/proto/`
    - `[目标目录]/tests/cpp/`
  - 创建初始 CMakeLists.txt（最小版本，仅编译一个 hello world 验证工具链可用）
- **Acceptance Criteria Addressed**: NFR-1, AC-3
- **Test Requirements**:
  - `programmatic` TR-0.1: `cmake -B build -G Ninja` 配置成功
  - `programmatic` TR-0.2: `cmake --build build` 编译 hello world 成功
  - `programmatic` TR-0.3: 运行 hello world 程序输出正确
- **Notes**: 环境验证不通过不要进入后续任务。Windows 环境下编译 Linux 原生 C++ 项目遇到问题时，优先切换 WSL 而非强行适配 Windows。

## [ ] Task 1: 创建最小 CMake 基础框架（仅核心，5-10文件）

- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 创建根 `[目标目录]/CMakeLists.txt`：
    - `cmake_minimum_required(VERSION 3.18)`
    - `project([项目名]_slim CXX)`
    - `set(CMAKE_CXX_STANDARD [XX])`
    - `set(CMAKE_CXX_STANDARD_REQUIRED ON)`
    - 添加 `add_subdirectory` 引入新依赖库（如 tvm-ffi 路径）
    - 查找必要依赖：[如 Protobuf, BLAS, Threads]
    - 定义编译选项：[如 CPU_ONLY, 版本宏]
    - **显式列出**初始核心源文件（5-10个，不是 GLOB）
    - 定义核心静态库目标（如 `[项目名]_core`）
    - 定义 FFI/绑定共享库目标（如 `_[项目名]`）
    - **不添加**所有源文件——只添加最小可编译集合
  - 复制 proto 文件（如适用）到 `src/[项目名]/proto/`，配置 protobuf 生成
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: CMake configure 成功，未报错，找到了所有依赖
  - `programmatic` TR-1.2: 初始核心静态库编译成功（0 errors）
  - `human-judgment` TR-1.3: CMakeLists.txt 中无 `find_package([旧库])`
  - `human-judgment` TR-1.4: 未使用 `file(GLOB_RECURSE)` 收集源文件
- **Notes**: 这一步的目标是"最小可编译核心"跑通，不是把所有文件加进去。通常包含：common、SyncedMemory、Blob、Layer、Net 的头文件和最小实现。

## [ ] Task 2: 创建 compat 兼容层头文件（先验证语义等价）

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 根据 Step 0.5 的API映射表，在 `include/[项目名]/compat/` 下创建兼容层头文件：
    - `logging.hpp`：分级日志宏（[INFO]/[WARNING]/[ERROR] → stderr 带前缀；FATAL → 异常抛出）
    - `check_macros.hpp`：CHECK/DCHECK 系列宏映射到新库检查宏
    - `smart_ptr.hpp`：智能指针 using 别名（std::shared_ptr 等）
    - `thread.hpp`：线程/互斥锁/条件变量包装 + 必要的同步原语（如 Barrier）
    - `filesystem.hpp`：文件系统命名空间别名
    - `function.hpp`：函数对象/bind 别名
    - `chrono.hpp`：时间/时钟类型别名 + Timer 封装
    - `random.hpp`：随机数类型别名
    - `string_utils.hpp`：字符串工具函数（split/trim/lexical_cast 等，内联实现）
    - `thread_local.hpp`：thread_local 封装（替代 thread_specific_ptr）
    - `math.hpp`：数学函数替代（如 nextafter）
    - [其他需要的兼容头文件]
  - 所有 compat 头文件必须是 header-only
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 编写 `tests/cpp/test_compat.cpp`，include 所有 compat 头文件
  - `programmatic` TR-2.2: test_compat.cpp 编译通过并运行，使用每个兼容宏/类验证行为正确
  - `programmatic` TR-2.3: CHECK 失败测试——触发条件检查失败时抛出预期异常，消息包含文件/行号/条件
  - `human-judgment` TR-2.4: compat 头文件不 include 任何旧库头文件（grep 验证）
- **Notes**: **这是最关键的一步**。兼容层是基石，所有业务代码迁移都依赖它。兼容层bug会扩散到所有调用点，导致大面积返工。必须在这一步花足够时间验证每个宏/函数的语义等价性。

## [ ] Task 3: 迁移核心抽象层（增量添加，每批编译验证）

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - **第一批（5个文件）**：迁移最基础的核心文件
    - common.hpp/common.cpp（全局初始化/单例）
    - syncedmem.hpp/syncedmem.cpp（内存管理）
    - blob.hpp/blob.cpp（数据块）
    - 替换旧库引用为 compat 头文件
    - **编译验证通过后再继续**
  - **第二批**：迁移 layer.hpp/layer.cpp（层基类）
  - **第三批**：迁移 net.hpp/net.cpp（网络DAG）
  - **第四批**：迁移 solver.hpp/solver.cpp（求解器，如需要）
  - **第五批**：迁移 layer_factory、filler、data_transformer 等
  - 每批迁移后立即编译验证
  - 移除旧的全局初始化中对旧库的调用（如 gflags::ParseCommandLineFlags、InitGoogleLogging）
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 每批文件迁移后 caffe_core 编译通过，无旧库符号
  - `programmatic` TR-3.2: 核心类功能测试通过（Blob 创建/Reshape/数据访问）
  - `human-judgment` TR-3.3: grep 确认已迁移文件中无旧库引用
  - `human-judgment` TR-3.4: 核心业务逻辑算法代码未被修改（仅头文件替换和必要的语法适配）
- **Notes**: 采用"少量多次"策略，每次迁移3-5个文件，编译通过后再继续。不要一次性迁移几十个文件。

## [ ] Task 4: 迁移 util 工具组件

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批迁移 util 目录下的文件：
    - **第一批**：math_functions（数学函数）
    - **第二批**：blocking_queue（阻塞队列，线程同步）
    - **第三批**：benchmark、format、insert_splits
    - **第四批**：io（文件IO，替换文件系统库）
    - **第五批**：rng、signal_handler、upgrade_proto
    - **第六批**：db stub（如不迁移具体后端，提供空实现）
    - **第七批**：internal_thread（内部线程，替换 thread 库）
  - 每批迁移后编译验证
  - GPU相关代码在 CPU_ONLY 模式下 stub 或移除
  - 不迁移的文件明确列出并确认无依赖
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 每批文件编译通过
  - `programmatic` TR-4.2: 核心静态库完整链接成功
  - `programmatic` TR-4.3: 线程相关组件测试通过（BlockingQueue push/pop, InternalThread start/stop）
- **Notes**: util 组件通常被核心层和层实现依赖，必须在迁移 Layer 之前完成。

## [ ] Task 5: 迁移核心功能模块（Layers/其他业务模块）

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 首先迁移基类头文件
  - 然后按功能组迁移实现文件：
    - **组1（基础激活层）**：NeuronLayer 基类 + ReLU/Sigmoid/TanH/ELU 等
    - **组2（核心计算层）**：Convolution/InnerProduct/Pooling + im2col
    - **组3（归一化/正则）**：BatchNorm/Scale/Dropout
    - **组4（损失层）**：Softmax/SoftmaxWithLoss
    - **组5（组织层）**：Concat/Split/Eltwise/Slice/Reshape/Flatten
    - **组6（数据层）**：Input/MemoryData + BaseDataLayer
    - **组7（评估层）**：Accuracy/ArgMax
    - **组8（可选层）**：[根据需要迁移的其他层]
  - 在工厂注册中为每个迁移的模块添加注册宏
  - 每组迁移后编译验证
  - 不迁移的文件明确列出并确认无依赖（如 GPU 特定层、PythonLayer、特殊训练层）
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 每组 Layer 编译通过
  - `programmatic` TR-5.2: 工厂注册测试——可通过工厂创建所有迁移的模块类型
  - `human-judgment` TR-5.3: 核心功能路径所需模块均已覆盖
- **Notes**: 按功能依赖顺序迁移，基础层先于使用它的层。每迁移一组就编译，不要攒到最后。

## [ ] Task 6: 重写绑定/FFI 模块

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 完全移除旧绑定机制代码（如 boost::python、Python.h、numpy C API 等）
  - 使用新绑定机制（如 tvm-ffi TVM_FFI_DLL_EXPORT_TYPED_FUNC）
  - 采用 opaque handle 模式管理 C++ 对象：
    - 定义 Handle 类型别名（如 `using NetHandle = uintptr_t;`）
    - 导出创建/销毁/成员函数调用的 C ABI 函数
    - 所有导出函数使用安全调用宏包裹（如 TVM_FFI_SAFE_CALL_BEGIN/END）
  - 数据传递使用跨语言零拷贝机制（如 DLPack/Tensor）
  - 移除不需要的功能（如 NCCL、多GPU、PythonLayer 等，提供 stub）
  - 导出函数清单设计：
    - 版本/模式设置
    - 核心对象创建/销毁/操作
    - 数据输入/输出
    - 计时工具
    - [其他必要接口]
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-10
- **Test Requirements**:
  - `programmatic` TR-6.1: 绑定模块编译成功，无旧绑定依赖
  - `programmatic` TR-6.2: 检查导出符号（nm/dumpbin）包含正确前缀
  - `programmatic` TR-6.3: C++ 测试程序能通过 FFI 创建核心对象、执行核心操作、获取输出
  - `programmatic` TR-6.4: 异常安全——触发错误时异常正确传递到调用端
  - `human-judgment` TR-6.5: 绑定文件中无旧绑定机制引用
- **Notes**: handle 模式的关键是：C++ 对象通过 new 创建，指针转为 uintptr_t 返回；调用时从 handle 转回指针；销毁时 delete。每个 new 必须对应一个 delete，避免内存泄漏。

## [ ] Task 7: 统一 CMake 构建和编译验证

- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 完善 CMakeLists.txt：
    - 将所有迁移的 C++ 源文件**显式**加入核心静态库（不是 GLOB）
    - 添加编译选项：编译定义、C++标准、警告级别
    - 正确配置 include 路径（include/、build/ 生成代码目录）
    - target_link_libraries：新依赖库、Protobuf、BLAS、Threads
    - 绑定共享库链接核心静态库和新依赖库
    - 添加 install 目标（安装绑定模块到正确位置）
  - 完整编译验证（从零开始的干净构建）
  - 确保共享库输出名与上层 import 路径兼容
  - 生成 compile_commands.json 供 IDE 使用
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: 干净构建目录下 cmake configure 无错误无警告
  - `programmatic` TR-7.2: 完整编译成功（0 errors，允许第三方库警告）
  - `programmatic` TR-7.3: 链接成功，无未定义引用错误
  - `human-judgment` TR-7.4: CMakeLists.txt 不包含旧依赖查找/链接逻辑

## [ ] Task 8: 适配上层语言接口

- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 修改上层语言包（如 Python __init__.py）使用新的绑定加载方式
  - 编写上层包装类（Net/Blob/Timer 等），持有 handle 并管理生命周期
  - 封装核心操作（创建/执行/数据访问）
  - 保留上层 API 兼容性（如猴子补丁模式、属性访问方式）
  - 更新包配置（pyproject.toml 等）添加新依赖
  - 适配其他上层文件（如 classifier、detector 等）
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-8.1: `import [上层模块]` 成功
  - `programmatic` TR-8.2: 核心对象可以实例化
  - `programmatic` TR-8.3: 核心操作（如 forward）正常工作，返回正确类型
  - `human-judgment` TR-8.4: 上层 API 尽量保持向后兼容
- **Notes**: 上层包装类是纯上层语言代码，通过 handle 调用底层 FFI 函数。利用 RAII/上下文管理器确保资源正确释放。

## [ ] Task 9: 编写测试和端到端验证

- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - C++ 单元测试（tests/cpp/）：
    - test_blob：数据块创建/变形/读写
    - test_net：代码创建简单网络/执行核心操作
    - test_check：检查宏失败时异常行为
    - test_logging：日志宏正常使用不崩溃
    - test_thread：线程同步组件正确性
    - [其他核心功能测试]
  - 上层语言端到端测试：
    - 加载模型/执行核心操作/验证输出
  - 配置 CTest 集成
  - 内存泄漏检测（valgrind/ASan）
- **Acceptance Criteria Addressed**: AC-4, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-9.1: C++ 测试编译并通过（ctest 100% passed）
  - `programmatic` TR-9.2: 端到端测试通过
  - `programmatic` TR-9.3: 内存泄漏检测无明确泄漏报告
  - `human-judgment` TR-9.4: 测试覆盖核心功能路径

## [ ] Task 10: 旧依赖残留审计和清理

- **Priority**: high
- **Depends On**: Task 7（编译验证阶段即可开始）
- **Description**:
  - 对所有迁移源文件执行 grep 审计旧依赖残留
  - 检查 CMakeLists.txt 无旧依赖查找/链接
  - 检查生成的共享库动态依赖（ldd/dumpbin）
  - 移除旧构建配置
  - 如有残留逐一修复
  - 最终审计：
    ```bash
    # 旧头文件引用
    grep -rn "#include <[旧库]" [目标目录]/include [目标目录]/src
    # 旧命名空间
    grep -rn "[旧库命名空间]::" [目标目录]/include [目标目录]/src
    # CMake旧依赖
    grep -rn "find_package.*[旧库]" [目标目录]/
    ```
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-10.1: grep 旧头文件引用返回空（compat 层别名除外）
  - `programmatic` TR-10.2: grep 旧命名空间返回空（compat 层别名除外）
  - `programmatic` TR-10.3: grep CMake 旧依赖返回空
  - `programmatic` TR-10.4: ldd/dumpbin 检查共享库无旧依赖动态链接
