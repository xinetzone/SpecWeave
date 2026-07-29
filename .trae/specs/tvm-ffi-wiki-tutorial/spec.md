---
version: "1.0"
---
# TVM FFI Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 深入学习 `d:\spaces\SpecWeave\projects\xuanspace\vendor\tvm-ffi`（Apache TVM FFI）项目，创建一份全面、系统的中文wiki教程，帮助其他开发者快速掌握TVM FFI的使用和开发方法。TVM FFI是一个为机器学习系统设计的开放ABI和FFI（外部函数接口）库，提供稳定的C ABI、C++17 API、Python绑定（通过Cython）和Rust绑定。
- **Purpose**: TVM FFI是xuanspace项目中caffe-ffi等子项目的核心依赖，开发者需要系统性的中文教程来理解其架构、核心概念和使用方法，降低学习曲线，提高开发效率。
- **Target Users**: 使用xuanspace进行机器学习系统开发的工程师、需要跨语言集成C++/Python/Rust代码的开发者、对ML系统FFI技术感兴趣的技术人员。

## Goals
- 系统性梳理TVM FFI的目录结构和核心组件
- 深入解析核心概念（Any/AnyView、Object系统、Function、Container、Reflection等）
- 提供完整的C++和Python使用指南，含可运行代码示例
- 涵盖构建系统、打包发布、常见问题等实用内容
- 形成可作为项目内部参考的权威中文教程

## Non-Goals (Out of Scope)
- 不修改tvm-ffi源代码本身（tvm-ffi是vendor子模块，只读）
- 不创建Rust语言的详细教程（Rust绑定非当前项目核心需求）
- 不翻译官方英文文档全部内容（聚焦核心概念和实践指南）
- 不涉及CUDA ORCJit addon的深入讲解（作为进阶内容简述）
- 不创建视频或交互式教程（仅静态Markdown文档）

## Background & Context
TVM FFI是Apache TVM项目的核心FFI组件，已独立为单独项目（[tvm.apache.org/ffi/](https://tvm.apache.org/ffi/)）。它具有以下核心特性：
- **稳定的最小化C ABI**：为kernel库、DSL和运行时扩展设计
- **零拷贝互操作**：通过DLPack协议在PyTorch、JAX、CuPy之间零拷贝共享tensor
- **紧凑的值和调用约定**：覆盖ML应用中常见数据类型，极低开销
- **多语言支持**：开箱即用支持Python、C++、Rust

核心抽象包括：
- `Any`/`AnyView`：类型擦除的值容器（Any拥有所有权，AnyView不持有）
- `Object`/`ObjectRef`：引用计数的堆对象系统（FooObj数据 + Foo引用包装器模式）
- `Function`：类型擦除的可调用对象，packed调用约定
- 全局注册表：通过字符串名称注册函数，跨语言访问
- 容器类型：Array（不可变）、List（可变）、Map（不可变）、Dict（可变）、String、Tensor、Shape、Tuple、Variant
- 反射系统：ObjectDef构建器，支持C++/Python双向反射
- 模块系统：通过`__tvm_ffi_<name>`符号前缀加载动态库

tvm-ffi在xuanspace项目中是caffe-ffi的核心依赖，理解tvm-ffi对于开发基于C++的Python扩展至关重要。

## Functional Requirements
- **FR-1**: 提供项目概览和目录结构说明，帮助快速定位各模块
- **FR-2**: 系统讲解核心概念（Any、Object、Function、Container、Reflection、Module等）
- **FR-3**: 提供C++ API使用指南，含对象定义、函数注册、容器使用、异常处理等完整示例
- **FR-4**: 提供Python API使用指南，含对象使用、函数调用、dataclass反射、模块加载等示例
- **FR-5**: 讲解构建系统（CMake + scikit-build-core）和Python打包方法
- **FR-6**: 提供从C++扩展到多框架（PyTorch/JAX/Paddle/NumPy）的完整实战案例
- **FR-7**: 编写常见问题解答（FAQ）和故障排查指南
- **FR-8**: 提供关键源码解析，帮助深入理解实现机制

## Non-Functional Requirements
- **NFR-1**: 教程使用中文编写，技术术语保留英文并在首次出现时给出中文解释
- **NFR-2**: 每个原子文档不超过500行，遵循单一职责原则
- **NFR-3**: 代码示例必须基于实际源码（examples/目录），确保可运行或可验证
- **NFR-4**: 所有对项目文件的引用使用clickable `file:///` 绝对路径格式（根据用户偏好）
- **NFR-5**: Mermaid图表用于可视化架构和流程，提升可读性
- **NFR-6**: 文档结构遵循项目wiki规范，包含YAML frontmatter、导航链接
- **NFR-7**: 内容准确性需通过阅读源码和官方文档双重验证

## Constraints
- **Technical**: 
  - tvm-ffi是vendor子模块（projects/xuanspace/vendor/tvm-ffi），禁止修改其源码
  - 文档使用Markdown + Mermaid格式
  - Python版本要求3.9+（tvm-ffi要求），xuanspace环境要求3.13+
  - C++标准为C++17
- **Business**: 
  - 教程聚焦于xuanspace项目实际使用的功能子集
  - 产出物放置于SpecWeave主权区docs目录，不写入projects/xuanspace子模块
- **Dependencies**:
  - tvm-ffi源码（含include/、python/、examples/、docs/）
  - 项目已有的wiki模板和格式规范

## Assumptions
- 读者具备C++和Python基础编程能力
- 读者对FFI/ABI概念有基本了解（可参考项目内ffi-wiki教程）
- 教程产出物放置于 `d:\spaces\SpecWeave\.agents\docs\knowledge\tech\tvm-ffi-wiki\` 目录
- 代码示例基于tvm-ffi当前版本（与项目中vendor版本一致）

## Acceptance Criteria

### AC-1: 目录结构说明完整
- **Given**: 教程创建完成
- **When**: 查看 `00-overview.md` 和 `01-project-structure.md`
- **Then**: 包含完整的目录树说明、各目录功能描述、核心文件索引
- **Verification**: `human-judgment`

### AC-2: 核心概念讲解清晰
- **Given**: 核心概念章节（02-06）
- **When**: 阅读Any/Object/Function/Container/Reflection概念文档
- **Then**: 每个概念包含：设计理念、核心API、代码示例、与其他概念的关系
- **Verification**: `human-judgment`

### AC-3: C++使用指南完整可运行
- **Given**: C++指南章节（07-cpp-guide.md）
- **When**: 按照指南编写C++扩展代码
- **Then**: 涵盖对象定义、函数注册、容器操作、异常处理、模块导出，示例代码可编译运行
- **Verification**: `programmatic`
- **Notes**: 基于examples/quickstart和examples/python_packaging验证

### AC-4: Python使用指南完整可运行
- **Given**: Python指南章节（08-python-guide.md）
- **When**: 按照指南编写Python调用代码
- **Then**: 涵盖函数调用、对象使用、dataclass反射、模块加载、Tensor互操作，示例代码可运行
- **Verification**: `programmatic`
- **Notes**: 基于examples/quickstart验证

### AC-5: 构建与打包指南实用
- **Given**: 构建打包章节（09-build-packaging.md）
- **When**: 按照指南构建C++扩展并打包为wheel
- **Then**: 包含CMake配置、scikit-build-core设置、stubgen生成、wheel打包步骤
- **Verification**: `human-judgment`

### AC-6: 实战案例完整
- **Given**: 实战案例章节（10-examples.md）
- **When**: 阅读并运行实战案例
- **Then**: 包含至少2个完整案例（如C++扩展导出到Python、与PyTorch Tensor零拷贝互操作），含完整源码和运行说明
- **Verification**: `programmatic`

### AC-7: FAQ和故障排查实用
- **Given**: FAQ章节（11-faq.md）
- **When**: 查阅常见问题
- **Then**: 包含≥10个常见问题，覆盖编译错误、运行时错误、ABI兼容性、内存问题等
- **Verification**: `human-judgment`

### AC-8: 关键源码解析深入
- **Given**: 源码解析章节（12-source-deep-dive.md）
- **When**: 阅读源码解析
- **Then**: 解析核心头文件实现机制（Any类型擦除、Object引用计数、Function调用约定），帮助深入理解
- **Verification**: `human-judgment`

### AC-9: 文档元数据规范
- **Given**: 所有文档
- **When**: 检查frontmatter
- **Then**: 每个文档包含YAML frontmatter（id、title、tags、date等），遵循项目文档规范
- **Verification**: `programmatic`

### AC-10: 导航链接有效
- **Given**: 教程完成
- **When**: 检查所有内部链接
- **Then**: 文档间导航链接有效，目录页可跳转至各章节，章节间有前后导航
- **Verification**: `programmatic`
- **Notes**: 使用链接检查工具验证

## Open Questions
- [ ] 教程产出物的最终存放位置：`.agents/docs/knowledge/tech/tvm-ffi-wiki/` 是否合适？还是放在其他位置？
- [ ] 是否需要包含与项目中已有caffe-ffi代码的对照讲解，帮助理解tvm-ffi在实际项目中的应用？
- [ ] 是否需要包含Docker环境下的构建和测试说明？
