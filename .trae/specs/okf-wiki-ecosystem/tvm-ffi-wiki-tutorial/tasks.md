---
version: "1.0"
---
# TVM FFI Wiki 教程 - The Implementation Plan

## [x] Task 1: 深入阅读tvm-ffi源码和官方文档，收集素材
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 系统阅读 `include/tvm/ffi/` 下核心头文件（any.h, object.h, function.h, c_api.h, container/*.h, reflection/*.h, extra/*.h）
  - 阅读 `python/tvm_ffi/` 下Python包源码（__init__.py, _ffi_api.py, container.py, registry.py, dataclasses/等）
  - 阅读 `docs/` 下官方文档（concepts/, guides/, get_started/）
  - 阅读 `examples/` 下所有示例代码（quickstart/, python_packaging/, kernel_library/, cubin_launcher/等）
  - 阅读CMakeLists.txt和pyproject.toml理解构建系统
  - 整理核心API列表、关键宏定义、类型系统、调用约定等素材
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 素材覆盖所有核心模块（头文件、Python包、文档、示例、构建系统）
  - `human-judgement` TR-1.2: 整理出核心概念清单和API索引
- **Notes**: 这是基础任务，为后续文档编写提供准确素材

## [x] Task 2: 创建教程目录和总览文档（00-overview.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建目标目录 `d:\spaces\SpecWeave\.agents\docs\knowledge\tech\tvm-ffi-wiki\`
  - 编写 `00-overview.md`，包含：教程简介、目标读者、阅读路径、12章导航表、TVM FFI在ML系统中的定位Mermaid图
  - 设置正确的YAML frontmatter
- **Acceptance Criteria Addressed**: [AC-1, AC-9]
- **Test Requirements**:
  - `programmatic` TR-2.1: 目录创建成功，00-overview.md文件存在
  - `human-judgement` TR-2.2: 总览包含完整导航表和Mermaid架构图
  - `programmatic` TR-2.3: frontmatter字段完整（id、title、tags等）
- **Notes**: 遵循项目已有wiki的frontmatter格式

## [x] Task 3: 编写项目结构说明（01-project-structure.md）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 详细说明目录树结构（include/, src/, python/, rust/, tests/, docs/, examples/, cmake/, 3rdparty/, addons/）
  - 每个目录的功能说明
  - 核心文件索引（关键头文件、关键Python模块、关键CMake配置）
  - 编译产物和安装路径说明
  - 包含目录树Mermaid图
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 目录结构说明与实际代码一致
  - `human-judgement` TR-3.2: 所有核心文件都有说明
  - `programmatic` TR-3.3: 文件引用使用正确的file:///绝对路径格式
- **Notes**: 对照实际LS输出验证目录结构

## [x] Task 4: 编写Any/AnyView类型系统章节（02-any-type.md）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 讲解类型擦除（type erasure）设计理念
  - 详解Any（拥有所有权）和AnyView（非持有视图）的区别
  - 支持的数据类型（基本类型、string、Object、函数等）
  - 类型转换和类型检查机制
  - 代码示例：创建Any值、类型检查、值提取
  - 包含内存布局Mermaid图
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-4.1: Any/AnyView概念讲解清晰，区别明确
  - `human-judgement` TR-4.2: 代码示例基于实际API，可验证
  - `programmatic` TR-4.3: 文件行数<500
- **Notes**: 参考any.h源码和docs/concepts/any.rst

## [x] Task 5: 编写Object对象系统章节（03-object-system.md）
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 4
- **Description**: 
  - 讲解引用计数（reference counting）内存管理机制
  - FooObj（数据类）+ Foo（引用包装器）设计模式
  - 对象继承体系和类型信息（TVM_FFI_DECLARE_OBJECT_INFO宏）
  - 对象创建（make_object）和引用计数操作
  - 类型转换（Downcast/Upcast）和运行时类型检查
  - 代码示例：定义自定义对象、创建对象、访问成员
  - 包含对象生命周期Mermaid图
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-5.1: Object系统设计模式讲解清晰
  - `human-judgement` TR-5.2: FooObj/Foo双类模式示例正确
  - `programmatic` TR-5.3: 文件行数<500
- **Notes**: 参考object.h源码和docs/concepts/object_and_class.rst

## [x] Task 6: 编写Function函数和注册表章节（04-function-registry.md）
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 4, Task 5
- **Description**: 
  - 讲解packed function调用约定（(const AnyView* args, int32_t num_args, Any* rv)）
  - Function对象的创建和调用
  - 全局函数注册表（register_global_func/get_global_func）
  - 跨语言函数调用机制
  - 函数参数和返回值的Any转换
  - 代码示例：注册函数、获取函数、调用函数、传递回调
  - 包含函数调用流程Mermaid时序图
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-6.1: packed calling convention讲解清晰
  - `human-judgement` TR-6.2: 注册表机制和跨语言调用说明准确
  - `programmatic` TR-6.3: 文件行数<500
- **Notes**: 参考function.h和c_api.h源码

## [x] Task 7: 编写Container容器类型章节（05-containers.md）
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 4, Task 5
- **Description**: 
  - 容器类型总览：不可变vs可变容器设计理念
  - Array<T>（不可变数组）和List<T>（可变列表）
  - Map<K,V>（不可变映射）和Dict（可变字典）
  - String、Shape、Tuple、Variant<T...>
  - Tensor容器和DLPack互操作
  - 容器的迭代、访问、修改操作
  - 代码示例：各种容器的创建和使用
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 不可变/可变容器设计区别讲解清晰
  - `human-judgement` TR-7.2: 所有主要容器类型都有覆盖和示例
  - `human-judgement` TR-7.3: Tensor/DLPack零拷贝互操作说明准确
  - `programmatic` TR-7.4: 文件行数<500
- **Notes**: 参考include/tvm/ffi/container/目录下头文件

## [x] Task 8: 编写Reflection反射系统章节（06-reflection.md）
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 5
- **Description**: 
  - 反射系统设计理念（C++/Python双向互操作）
  - ObjectDef<T>构建器（def_field/def_method）
  - C++端反射注册
  - Python端dataclass集成（c_class/py_class）
  - 自动stub生成（tvm-ffi-stubgen）
  - 代码示例：C++定义反射对象，Python端以dataclass形式使用
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 反射机制和stubgen工具说明清晰
  - `human-judgement` TR-8.2: C++/Python双向反射示例正确
  - `programmatic` TR-8.3: 文件行数<500
- **Notes**: 参考reflection/目录和python/tvm_ffi/dataclasses/源码

## [x] Task 9: 编写C++使用指南（08-cpp-guide.md）
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7, Task 8
- **Description**: 
  - C++开发环境配置（CMake、编译器、include路径）
  - 定义和导出函数（TVM_FFI_REGISTER_GLOBAL_FUNC宏）
  - 定义自定义Object类型
  - 使用容器类型
  - 错误处理（TVM_FFI_THROW异常机制）
  - 模块导出（__tvm_ffi_符号前缀）
  - 完整的C++扩展示例（基于examples/python_packaging/）
  - 编译和链接说明
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-9.1: C++开发全流程覆盖（环境配置→编码→编译→导出）
  - `programmatic` TR-9.2: 示例代码可参考examples/验证正确性
  - `human-judgement` TR-9.3: 关键宏和API使用说明准确
  - `programmatic` TR-9.4: 文件行数<500
- **Notes**: 基于examples/python_packaging/src/extension.cc和docs/guides/cpp_lang_guide.md

## [x] Task 10: 编写Python使用指南（09-python-guide.md）
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7, Task 8
- **Description**: 
  - Python包安装（pip install apache-tvm-ffi）
  - 调用全局函数（get_global_func）
  - 使用Object和Container
  - dataclass反射使用（c_class装饰器）
  - 加载动态模块（load_module）
  - Tensor与PyTorch/JAX/NumPy/CuPy零拷贝互操作
  - 完整Python示例（基于examples/quickstart/）
  - 类型注解和stub使用
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-10.1: Python开发全流程覆盖（安装→调用→互操作）
  - `programmatic` TR-10.2: 示例代码可参考examples/验证正确性
  - `human-judgement` TR-10.3: 多框架Tensor互操作说明完整
  - `programmatic` TR-10.4: 文件行数<500
- **Notes**: 参考docs/guides/python_lang_guide.md和examples/quickstart/load_*.py

## [x] Task 11: 编写Module模块系统和加载机制章节（07-module-system.md）
- **Priority**: medium
- **Depends On**: Task 1, Task 6
- **Description**: 
  - Module系统设计（动态库加载）
  - __tvm_ffi_<name>符号导出约定
  - load_module函数使用
  - 模块初始化和清理
  - 静态链接vs动态链接
  - 代码示例：编译和加载模块
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-11.1: 模块加载机制和符号约定讲解清晰
  - `human-judgement` TR-11.2: 示例代码基于examples/验证
  - `programmatic` TR-11.3: 文件行数<500
- **Notes**: 参考extra/module.h和python/tvm_ffi/module.py

## [x] Task 12: 编写构建与打包指南（10-build-packaging.md）
- **Priority**: high
- **Depends On**: Task 9, Task 10
- **Description**: 
  - C++库构建（CMake配置、编译选项、Ninja使用）
  - Python包构建（scikit-build-core、pyproject.toml配置）
  - Cython编译配置
  - stubgen类型桩生成
  - wheel打包流程
  - editable install开发模式
  - 跨平台编译注意事项（Linux/macOS/Windows）
  - 基于examples/python_packaging/的完整打包示例
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-12.1: CMake + scikit-build-core构建流程完整
  - `human-judgement` TR-12.2: pyproject.toml配置说明准确
  - `human-judgement` TR-12.3: stubgen使用说明正确
  - `programmatic` TR-12.4: 文件行数<500
- **Notes**: 参考根目录CMakeLists.txt、pyproject.toml和docs/packaging/

## [x] Task 13: 编写实战案例章节（11-examples.md）
- **Priority**: high
- **Depends On**: Task 9, Task 10, Task 12
- **Description**: 
  - 案例1：C++扩展导出简单函数到Python（基于examples/quickstart/）
  - 案例2：定义自定义Object并在Python中使用（基于examples/python_packaging/）
  - 案例3：与PyTorch Tensor零拷贝互操作（基于examples/quickstart/load_pytorch.py）
  - 每个案例包含：完整源码、CMakeLists.txt/pyproject.toml、构建命令、运行命令、预期输出
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-13.1: 至少2个完整案例（优先选择已验证可运行的）
  - `human-judgement` TR-13.2: 每个案例包含从源码到运行的完整步骤
  - `human-judgement` TR-13.3: 代码与examples/目录下实际代码一致
  - `programmatic` TR-13.4: 文件行数<500
- **Notes**: 优先使用examples/下已有的可运行示例，确保准确性

## [x] Task 14: 编写常见问题解答（12-faq.md）
- **Priority**: medium
- **Depends On**: Task 1（完成后即可开始，后续持续补充）
- **Description**: 
  - 编译错误类：CMake找不到tvm-ffi、C++标准不对、符号未导出、链接错误
  - 运行时错误类：类型转换失败、函数未找到、模块加载失败、引用计数问题
  - ABI兼容性：编译器版本、C++标准、平台差异
  - Python相关：import错误、Cython编译问题、版本兼容
  - 内存问题：内存泄漏、悬垂引用、跨语言所有权
  - 最佳实践：错误处理、类型安全、性能优化
  - 至少10个常见问题，每个包含：问题描述、原因分析、解决方案
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-14.1: ≥10个FAQ条目，覆盖编译/运行时/ABI/Python/内存等类别
  - `human-judgement` TR-14.2: 每个FAQ有明确的问题、原因、解决方案
  - `programmatic` TR-14.3: 文件行数<500
- **Notes**: 可从项目记忆中的经验教训（如tvm-ffi前缀一致性问题、DLL冲突等）提取素材

## [x] Task 15: 编写关键源码解析章节（13-source-analysis.md）
- **Priority**: medium
- **Depends On**: Task 4, Task 5, Task 6
- **Description**: 
  - Any类型擦除实现机制（Tagged Union或void* + type index）
  - Object引用计数原子操作实现
  - Function调用约定的C ABI层（c_api.h）
  - 全局注册表的线程安全实现
  - 关键宏展开分析（TVM_FFI_DECLARE_OBJECT_INFO等）
  - 包含关键代码片段和解释
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-15.1: 核心机制源码解析准确
  - `human-judgement` TR-15.2: 代码片段来自实际头文件
  - `programmatic` TR-15.3: 文件行数<500
- **Notes**: 深入阅读base_details.h、function_details.h、object.h等实现细节

## [x] Task 16: 添加导航链接和文档一致性检查
- **Priority**: high
- **Depends On**: Task 3-Task 15所有文档完成
- **Description**: 
  - 为每个章节文档添加双向导航（上一章、返回目录、下一章）
  - 检查所有内部链接有效性
  - 检查所有file:///路径格式正确
  - 检查YAML frontmatter一致性
  - 统一术语和格式
  - 检查每个文件行数<500
- **Acceptance Criteria Addressed**: [AC-9, AC-10]
- **Test Requirements**:
  - `programmatic` TR-16.1: 所有文档都有正确的双向导航链接
  - `programmatic` TR-16.2: 所有内部链接可访问（无断链）
  - `programmatic` TR-16.3: 所有file:///路径格式正确（使用/分隔符）
  - `programmatic` TR-16.4: 每个文件frontmatter字段完整一致
  - `programmatic` TR-16.5: 每个文件行数<500
- **Notes**: 使用项目链接检查工具验证
