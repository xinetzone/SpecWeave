# Caffe-Slim Blob Shape 容器迁移至 tvm::ffi::Shape - PRD

## Overview
- **Summary**: 将 caffe-slim 中 Blob 类的形状存储从 `std::vector<int> shape_` 迁移到 tvm-ffi 提供的 `tvm::ffi::Shape`/`ShapeView` 容器，统一类型系统（int→int64_t），内置 Product/Stride 计算，简化 FFI 边界代码，消除跨语言类型转换开销。
- **Purpose**: 当前 `vector<int>` 存在三重问题：(1) FFI 边界需重复 int→int64_t 转换（`_caffe.cpp` 中3处冗余转换）；(2) 元素总数 count_ 手动计算易出错；(3) 与 tvm::ffi::Tensor/DLPack 生态类型不一致，阻碍零拷贝互操作。迁移后可提升代码可维护性、与 tvm-ffi 生态兼容性，并为未来 Stride 支持和动态形状扩展奠定基础。
- **Target Users**: caffe-slim 框架开发者、使用 pycaffe Python 绑定的推理部署工程师、基于 tvm-ffi 生态的系统集成开发者。

## Goals
- Blob 内部形状存储替换为 `tvm::ffi::Shape`（持有型引用计数容器）
- 对外暴露 `ShapeView shape_view()` const 方法，支持零拷贝只读访问
- 保留 `vector<int> shape()` 兼容接口（过渡期），内部从 Shape 转换生成
- 移除死代码 `shape_data_`（SyncedMemory 形状副本，只写不读）
- 利用 `Shape::Product()` 替代手动 count_ 计算（count_ 可缓存为 int64_t）
- 简化 `_caffe.cpp` FFI 绑定代码，消除 int→int64_t 重复转换
- Reshape 方法系列（4个重载）适配新容器
- 所有现有测试通过，无功能回归

## Non-Goals (Out of Scope)
- 不修改 Layer 实现中对 shape 的访问模式（通过兼容层保证）
- 不引入 Stride 支持到 Blob（Shape 有 StridesFromShape 能力，但本期仅做存储迁移）
- 不改变 BlobProto/BlobShape protobuf 定义（仍使用 repeated int64 dim）
- 不对 data_/diff_ SyncedMemory 进行 tvm::ffi::Tensor 替换（仅形状层迁移）
- 不修改 pycaffe Python 层 API（Python 侧 tuple/list 接口保持不变）
- 不处理 GPU 相关逻辑（slim 版本身 CPU-only）

## Background & Context
- caffe-slim 已使用 tvm-ffi 替代 Boost.Python 做 Python 绑定
- tvm-ffi 提供专业的 Shape/ShapeView 容器，设计用于张量形状表示：
  - ShapeView：非持有轻量视图（指针+大小），零拷贝传递
  - Shape：引用计数持有型容器，小对象内联分配（make_inplace_array_object）
  - 内置 Product() 计算元素总数、StridesFromShape() 步长推导
  - 类型为 int64_t，与 DLPack/tvm::ffi::Tensor 一致
- 当前 Blob 存在冗余设计：
  - `shape_data_`（shared_ptr<SyncedMemory>）在 Reshape 中写入但从未被读取
  - FFI 层每次获取 Blob 数据都要做 vector<int>→vector<int64_t>→ShapeView 双重转换
  - count_ 使用 int（32位），大张量存在 INT_MAX 溢出风险（当前有检查但防御性不足）

## Functional Requirements
- **FR-1**: Blob 类内部成员 `shape_` 类型从 `vector<int>` 变更为 `tvm::ffi::Shape`
- **FR-2**: 新增 `ShapeView shape_view() const` 方法返回形状的只读视图
- **FR-3**: 保留 `const vector<int>& shape() const` 方法，内部从 Shape 转换生成（过渡期兼容）
- **FR-4**: `shape(int index)` 方法支持负索引，语义不变，内部通过 CanonicalAxisIndex 转换
- **FR-5**: `num_axes()` 返回 `size_t`（或保留 int 返回但使用 static_cast）
- **FR-6**: `count()` 返回 `int64_t`（替代 int count_），利用 Shape::Product() 计算
- **FR-7**: 四个 Reshape 重载适配：
  - `Reshape(int num, int channels, int height, int width)` - 4维快捷方式
  - `Reshape(const vector<int>& shape)` - STL vector 输入
  - `Reshape(const BlobShape& shape)` - Proto 输入
  - `ReshapeLike(const Blob& other)` - 同源 Blob
- **FR-8**: 移除 `shape_data_` 成员变量及相关写入逻辑
- **FR-9**: `count_` 成员类型从 `int` 改为 `int64_t`（或直接用 shape_.Product() 缓存）
- **FR-10**: `offset()` 方法适配 int64_t 索引
- **FR-11**: `ShapeEquals`、`CopyFrom`、`FromProto`、`ToProto` 中 shape 比较/遍历逻辑适配
- **FR-12**: `_caffe.cpp` FFI 绑定简化：
  - `Blob_GetShape` 返回类型可选保留 vector<int>（Python 侧兼容）或新增 Shape 返回
  - `Blob_GetData`/`Blob_GetDiff` 直接使用 `blob->shape_view()` 构造 ShapeView，消除 vector 转换
  - `Blob_SetData` 中形状比较直接用 ShapeView 操作
  - `Param_GetShape`/`Param_GetData` 同样简化
- **FR-13**: `LegacyShape`/`num()`/`channels()`/`height()`/`width()` 访问器保持原有语义

## Non-Functional Requirements
- **NFR-1（性能）**: Reshape 操作开销不增加（Shape 内联分配 vs vector 堆分配，实际可能更优）
- **NFR-2（兼容性）**: 现有 C++ 调用方通过 `shape()` 方法获取 vector<int> 的代码不修改即可编译（兼容层）
- **NFR-3（内存）**: 移除 shape_data_ 节省冗余内存分配
- **NFR-4（类型安全）**: 元素计数使用 int64_t，消除 32位溢出风险
- **NFR-5（FFI效率）**: Blob_GetData/Blob_SetData 热路径消除 vector 构造和拷贝

## Constraints
- **Technical**: C++17；必须使用已有 tvm-ffi 依赖（已在 CMake 中链接）；保持 CPU-only；不引入新依赖
- **Business**: caffe-slim 基于 BSD 2-Clause，修改可自由使用
- **Dependencies**: tvm-ffi（已存在）、Protobuf（已存在）、BLAS（已存在）

## Assumptions
- tvm-ffi 的 Shape 容器在 caffe-slim 的 CMake 构建环境中可用（已通过 `_caffe.cpp` 中 `#include <tvm/ffi/container/tensor.h>` 验证）
- Reshape 操作频率低（初始化时一次，动态输入时偶尔），Shape 不可变性导致的"每次Reshape创建新对象"开销可接受
- 现有 Layer 实现不直接操作 Blob::shape_ 成员（均通过公共方法访问），兼容层足够
- Python 侧 pycaffe 接收 list/tuple，`Blob_GetShape` 即使返回 Shape，tvm-ffi 也会自动转换为 Python tuple

## Acceptance Criteria

### AC-1: Blob 内部使用 tvm::ffi::Shape 存储
- **Given**: Blob 类定义
- **When**: 查看 blob.hpp 成员变量
- **Then**: `shape_` 类型为 `tvm::ffi::Shape`；`shape_data_` 成员已移除
- **Verification**: `programmatic` - 代码检查 + 编译通过

### AC-2: shape_view() 方法返回零拷贝视图
- **Given**: 已构造的 Blob 对象
- **When**: 调用 `blob.shape_view()`
- **Then**: 返回 `tvm::ffi::ShapeView`，其 data() 指针指向 Shape 内部数据，无拷贝；Product() 等于 count()
- **Verification**: `programmatic` - 单元测试验证指针相等 + 数值正确

### AC-3: shape() 兼容接口保留
- **Given**: 已构造的 Blob 对象
- **When**: 调用 `blob.shape()`
- **Then**: 返回 `const vector<int>&` 或等效可转换到 `vector<int>` 的类型；包含正确的维度值
- **Verification**: `programmatic` - 编译验证 + 现有测试通过

### AC-4: Reshape 全系列方法正常工作
- **Given**: 默认构造的 Blob
- **When**: 依次调用4种 Reshape 重载
- **Then**: 形状正确设置；count()/num_axes()/shape(i) 返回正确值；data_/diff_ 内存正确分配
- **Verification**: `programmatic` - 单元测试覆盖

### AC-5: count() 返回 int64_t 且无溢出
- **Given**: 大张量形状（如接近 INT_MAX 的维度）
- **When**: 调用 Reshape 设置大形状后调用 count()
- **Then**: 正确返回 int64_t 元素总数；原有的 INT_MAX 溢出检查升级为 int64_t 检查
- **Verification**: `programmatic` - 边界值测试

### AC-6: FFI 绑定简化且功能不变
- **Given**: 加载的网络
- **When**: Python 侧调用 net.blobs['data'].data 获取张量
- **Then**: 返回正确的 numpy 数组，形状匹配；无类型转换错误
- **Verification**: `programmatic` - tests/test_inference.py 通过

### AC-7: 所有现有测试通过
- **Given**: 修改后的代码库
- **When**: 运行 C++ 测试和 Python 测试
- **Then**: tests/test_caffe_slim.cpp、tests/test_inference.py、test_import.py、test_python.py 全部通过
- **Verification**: `programmatic` - CI 测试

### AC-8: shape_data_ 死代码完全移除
- **Given**: 修改后的代码库
- **When**: 搜索 shape_data_
- **Then**: 无残留引用
- **Verification**: `programmatic` - grep 验证

### AC-9: Python 端 API 兼容
- **Given**: 修改后的 pycaffe
- **When**: 运行 batch_inference_demo.py
- **Then**: 推理正常执行，输出概率正确
- **Verification**: `human-judgment` + `programmatic` - Demo 运行验证

## Open Questions
- [ ] `shape()` 返回类型是保留 `const vector<int>&`（需持久化vector成员）还是改为返回 `vector<int>` 按值返回（每次构造）？
- [ ] `Blob_GetShape` FFI函数是否直接改为返回 `tvm::ffi::Shape`（Python侧自动转tuple），还是保留 `vector<int>` 返回？
- [ ] count_ 是保留为缓存成员变量，还是每次调用 shape_.Product() 计算（形状维数小，Product开销极低）？
