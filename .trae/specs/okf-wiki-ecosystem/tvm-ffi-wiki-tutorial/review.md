---
version: "1.0"
---
# TVM FFI Wiki 教程 - Verification Checklist

## 素材收集验证
- [x] 已系统阅读include/tvm/ffi/下所有核心头文件（any.h, object.h, function.h, c_api.h, container/*.h, reflection/*.h, extra/*.h）
- [x] 已阅读python/tvm_ffi/下Python包主要模块源码
- [x] 已阅读docs/下官方核心概念文档和指南
- [x] 已阅读examples/下主要示例代码（quickstart, python_packaging, kernel_library, inline_module, stable_c_abi）
- [x] 已理解CMakeLists.txt和pyproject.toml构建配置
- [x] 已整理出核心API清单和关键宏定义

## 文档结构验证
- [x] 目标目录 `d:\spaces\SpecWeave\.agents\docs\knowledge\tech\tvm-ffi-wiki\` 已创建
- [x] 00-overview.md（总览）存在且内容完整
- [x] 01-project-structure.md（项目结构）存在且内容完整
- [x] 02-any-type.md（Any类型系统）存在且内容完整
- [x] 03-object-system.md（Object对象系统）存在且内容完整
- [x] 04-function-registry.md（Function和注册表）存在且内容完整
- [x] 05-containers.md（容器类型）存在且内容完整
- [x] 06-reflection.md（反射系统）存在且内容完整
- [x] 07-module-system.md（Module模块系统）存在且内容完整
- [x] 08-cpp-guide.md（C++使用指南）存在且内容完整
- [x] 09-python-guide.md（Python使用指南）存在且内容完整
- [x] 10-build-packaging.md（构建与打包）存在且内容完整
- [x] 11-examples.md（实战案例）存在且内容完整
- [x] 12-faq.md（常见问题）存在且内容完整
- [x] 13-source-analysis.md（源码解析）存在且内容完整
- [x] 共14个章节文档，每个文档<500行（最大416行）

## 内容准确性验证
- [x] 目录结构说明与实际LS输出一致
- [x] Any/AnyView概念讲解准确，所有权区别清晰（拥有/借用）
- [x] Object系统FooObj/Foo双类模式说明正确（Obj数据类+Ref引用包装器）
- [x] Packed Function调用约定`(const AnyView* args, int32_t num_args, Any* rv)`描述准确
- [x] 全局注册表机制（GetGlobal/SetGlobal/get_global_func/register_global_func）说明正确
- [x] 不可变容器（Array/Map）vs可变容器（List/Dict）区别讲解清晰（COW vs 共享引用）
- [x] Tensor/DLPack零拷贝互操作说明准确
- [x] 反射系统（ObjectDef/dataclass: c_class/py_class）和stubgen工具说明正确
- [x] Module符号前缀`__tvm_ffi_`约定说明正确
- [x] C++宏（TVM_FFI_DECLARE_OBJECT_INFO, TVM_FFI_STATIC_INIT_BLOCK等）使用示例基于实际API
- [x] Python API调用示例与实际Python包接口一致
- [x] CMake + scikit-build-core构建配置说明准确
- [x] 代码示例均基于examples/目录下实际代码
- [x] FAQ包含27个条目，覆盖编译/运行时/ABI/Python/内存/设计等类别
- [x] 源码解析章节的代码片段来自实际头文件（标注了行号引用）

## 代码示例验证
- [x] C++扩展示例代码参考examples/quickstart和examples/python_packaging验证
- [x] Python调用示例代码参考examples/quickstart验证
- [x] 实战案例包含7个完整案例（Quickstart、CUDA Kernel、inline_module、C ABI、Tensor互操作、自定义Object、Python回调）
- [x] 每个案例包含场景说明、代码、运行方式
- [x] Tensor互操作示例（PyTorch/NumPy）与examples/目录一致

## 格式规范验证
- [x] 每个文档包含完整YAML frontmatter（id、title、tags、date、source、category）
- [x] 所有项目源码引用使用file:///绝对路径，使用/作为分隔符
- [x] file:///路径格式正确，指向真实存在的文件
- [x] Mermaid图表语法正确，使用```mermaid标记
- [x] 技术术语首次出现时给出中文解释
- [x] 文档语言为中文
- [x] 代码块标注正确的语言类型（cpp/python/cmake/bash/c/mermaid/toml）

## 导航链接验证
- [x] 每个章节文档顶部包含统一导航栏（全部14章链接）
- [x] 每个章节文档底部包含上一页/下一页顺序导航
- [x] 导航链接使用相对路径，可正确跳转
- [x] 00-overview.md中包含所有章节的导航表格
- [x] file:///绝对路径仅用于引用项目源码文件，不用于文档间导航

## 质量门验证
- [x] G1（事实无因果词）：概念描述章节使用客观描述
- [x] G2（洞察完整）：FAQ包含现象+原因+建议的完整分析
- [x] G3（模式可迁移）：构建和使用指南的步骤可复现
- [x] G4（原子化）：每个文档单一职责，<500行
- [x] 文档内容准确反映tvm-ffi当前版本实际实现（与vendor中代码一致）
