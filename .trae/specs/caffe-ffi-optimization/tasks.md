# Caffe FFI TVM FFI最佳实践优化 - The Implementation Plan

## [ ] Task 1: CMake构建系统迁移到find_package(tvm_ffi)
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将CMakeLists.txt从add_subdirectory(tvm-ffi)迁移到find_package(tvm_ffi CONFIG REQUIRED)
  - 添加Python解释器查找，使用`python -m tvm_ffi.config --cmakedir`获取tvm_ffi路径
  - 对_caffe_ffi目标调用tvm_ffi_configure_target()
  - 保留原有编译选项、DLL复制逻辑、protobuf集成等
  - 验证CMake配置和编译成功
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: CMake配置无错误，成功找到tvm_ffi包
  - `programmatic` TR-1.2: 项目编译成功，无链接错误
  - `programmatic` TR-1.3: 生成的_caffe_ffi.dll/.so依赖正确，无DLL冲突
- **Notes**: 这是基础任务，必须首先完成以符合项目硬约束

## [ ] Task 2: Blob双类模式重构与Tensor零拷贝
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将Blob重构为BlobObj（继承Object）+ Blob（继承ObjectRef）双类模式
  - 使用TVM_FFI_DECLARE_OBJECT_INFO_FINAL声明BlobObj类型信息
  - 使用TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE定义Blob引用方法
  - 直接暴露data_tensor()和diff_tensor()返回Tensor对象
  - 移除get_data()/set_data()/get_diff()/set_diff()等Array拷贝方法（或保留为兼容层）
  - 实现零拷贝numpy互操作：data属性通过DLPack与numpy共享内存
  - 完善反射注册：注册构造函数、shape方法、Reshape、data_tensor、diff_tensor、name等
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 编译通过
  - `programmatic` TR-2.2: Blob创建、Reshape、shape/count/num_axes等基础API正常
  - `programmatic` TR-2.3: Blob.data返回numpy数组，与C++ Tensor共享内存（修改numpy反映到Blob）
  - `programmatic` TR-2.4: test_blob.py所有测试通过
  - `human-judgement` TR-2.5: 代码审查确认双类模式正确使用宏
- **Notes**: 核心优化任务，零拷贝是性能提升关键

## [ ] Task 3: Layer基类双类模式兼容重构
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 将Layer重构为LayerObj（继承Object）+ Layer（继承ObjectRef）双类模式
  - 使用TVM_FFI_DECLARE_OBJECT_INFO声明LayerObj（可被继承），设置_type_child_slots
  - 使用TVM_FFI_DEFINE_OBJECT_REF_METHODS定义Layer引用方法
  - 保持现有虚函数接口（LayerSetUp、Reshape、Forward_cpu等）签名不变
  - 将std::vector<ObjectPtr<Blob>> blobs_改为Array<Blob>容器
  - 完善反射注册：注册type()、blobs()、blobs_array等
  - 更新所有20个Layer子类（input/relu/conv/fc等）继承自LayerObj，最小化修改
  - 更新layer_factory.hpp适配新的双类模式
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: 编译通过
  - `programmatic` TR-3.2: 所有20个Layer子类正确注册
  - `programmatic` TR-3.3: test_layers.py核心Layer测试通过
- **Notes**: 渐进式重构，保持子类计算逻辑不变

## [ ] Task 4: Net双类模式重构与容器统一
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 将Net重构为NetObj（继承Object）+ Net（继承ObjectRef）双类模式
  - 使用TVM_FFI_DECLARE_OBJECT_INFO_FINAL声明NetObj
  - 使用TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE定义Net引用方法
  - 将内部std::vector<ObjectPtr<Layer>> layers_改为Array<Layer>
  - 将std::vector<ObjectPtr<Blob>> blobs_改为Array<Blob>
  - 将std::vector<std::vector<Blob*>> bottom_vecs_/top_vecs_改为适配容器（使用Array<Array<Blob>>或保持指针但正确管理生命周期）
  - 将std::map<std::string, int>索引改为Map<String, int64_t>
  - Forward返回Map<String, Blob>而非Map<String, Array<float>>
  - 完善反射注册：Forward、name、layer_names、blob_names、blobs_array、layers_array、blob_by_name、layer_by_name等
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 编译通过
  - `programmatic` TR-4.2: Net从prototxt创建、Forward前向传播正常
  - `programmatic` TR-4.3: test_net.py所有测试通过
- **Notes**: Net是最复杂的重构，确保拓扑排序和前向传播逻辑不变

## [ ] Task 5: 全局函数注册与导出优化
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 更新NewBlob、NewBlobFromShape、NewNetFromProtoString、NewNetFromFile等工厂函数返回ObjectRef子类
  - 优化NewBlobFromShape，直接使用ShapeView避免vector拷贝
  - 为关键入口函数添加TVM_FFI_DLL_EXPORT_TYPED_FUNC导出（除了Version外）
  - 函数参数使用TVM FFI类型（String而非std::string，Array/ShapeView而非vector）
  - 完善LayerTypeList返回Array<String>
  - 添加必要的参数校验（如文件存在性、prototxt解析错误提示）
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有工厂函数正常工作
  - `programmatic` TR-5.2: Net从文件和字符串创建正常
  - `programmatic` TR-5.3: LayerTypeList返回正确列表
- **Notes**: 优化函数签名，充分利用FromTyped自动类型转换

## [ ] Task 6: 增强错误处理与参数校验
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 在关键入口添加TVM_FFI_ICHECK或TVM_FFI_THROW参数校验
  - Blob Reshape时校验shape维度合法性（非负维度等）
  - Net Forward前校验输入blob名称存在、shape匹配
  - Layer CheckBlobCounts提供更友好的错误信息
  - 文件IO错误（打开失败、解析失败）抛出明确异常包含文件路径
  - 使用TVM_FFI_THROW(ValueError)、TVM_FFI_THROW(TypeError)等typed异常
  - 移除或完善log.hpp，考虑使用TVM FFI内置错误机制（可选保留自定义日志）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 无效参数（如负维度、不存在的blob名）抛出异常
  - `programmatic` TR-6.2: 错误信息包含上下文（文件名、参数名等）
  - `programmatic` TR-6.3: Python端能捕获到对应异常类型
- **Notes**: 参考TVM FFI error.h中的异常类型

## [ ] Task 7: Python绑定层重构（@c_class+消除monkey patch）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 重构_core.py：使用tvm_ffi.dataclasses.c_class装饰器定义Blob/Layer/Net
  - 移除复杂的_is_native双轨逻辑和_py_*纯Python fallback（或大幅简化）
  - 移除_add_python_wrappers中的monkey patch代码
  - 利用C++反射自动获得字段和方法访问
  - Blob.data属性：基于DLPack实现零拷贝numpy访问（使用from_dlpack/to_dlpack）
  - Blob.from_numpy()/to_numpy()：零拷贝实现
  - Net.forward()：输入numpy数组→零拷贝到Blob→Forward→输出Blob→零拷贝到numpy
  - 保留原有API兼容性（blob.data、net.forward()、net.blobs_dict等）
  - 添加类型注解（TYPE_CHECKING块）支持IDE提示
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: Python导入caffe_ffi无错误
  - `programmatic` TR-7.2: Blob/Layer/Net通过@c_class正常实例化
  - `programmatic` TR-7.3: Blob.data零拷贝验证（共享内存）
  - `programmatic` TR-7.4: 原有API（data、diff、forward、copy_from等）正常工作
  - `human-judgement` TR-7.5: 代码审查确认无monkey patch，代码量显著减少
- **Notes**: Python层重构是消除技术债务的关键

## [ ] Task 8: 完善文档注释与代码风格统一
- **Priority**: medium
- **Depends On**: Task 2-7
- **Description**:
  - 为Blob、Layer、Net类和关键公共方法添加Doxygen风格注释
  - 统一命名空间使用（namespace caffe_ffi，避免using namespace tvm::ffi在头文件）
  - 统一include顺序（tvm/ffi头文件在前，caffe_ffi头文件在后，标准库最后）
  - 代码格式化（保持现有风格，统一缩进和换行）
  - 检查并修复编译器警告（-Wall -Wextra下的warning）
  - 更新common.hpp：确保类型别名正确，CPUMemAlloc注释完善
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-8.1: 代码审查确认注释完整、风格统一
  - `programmatic` TR-8.2: 编译无警告（或警告数量不增加）
- **Notes**: 注释重点在公共API，私有实现可以简洁

## [ ] Task 9: 全量测试与兼容性验证
- **Priority**: high
- **Depends On**: Task 2-8
- **Description**:
  - 运行tests/python/下所有单元测试（test_blob.py、test_layers.py、test_net.py）
  - 运行examples/create_and_run_mlp.py端到端冒烟测试
  - 修复所有测试失败问题（确保功能不退化）
  - 验证API向后兼容性：检查原有公共方法都存在且行为一致
  - 验证典型工作流：创建Net→加载权重→Forward→获取结果
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: pytest运行所有测试100%通过
  - `programmatic` TR-9.2: examples/create_and_run_mlp.py运行成功，输出正确
  - `programmatic` TR-9.3: MLP数值精度误差<1e-5
- **Notes**: 这是质量门禁任务，所有测试必须通过才能进入下一阶段

## [ ] Task 10: 性能测试与优化报告生成
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 编写性能基准测试脚本：对比优化前后Blob<->numpy转换耗时
  - 测试不同张量大小（1K、100K、1M、10M float32元素）
  - 测试Forward整体耗时对比
  - 验证零拷贝特性（内存共享验证）
  - 生成OPTIMIZATION_REPORT.md，包含：
    - 优化点概述
    - 性能对比数据（表格+图表）
    - 代码改进统计（代码行数变化、移除的冗余代码）
    - API兼容性说明
    - 后续优化建议
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: 性能基准测试脚本可运行
  - `human-judgement` TR-10.2: 优化报告完整，数据可信
  - `programmatic` TR-10.3: 零拷贝验证通过（Blob<->numpy共享内存）
- **Notes**: 性能数据要真实可信，对比优化前后的相同环境
