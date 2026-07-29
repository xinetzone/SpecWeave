# Caffe-Slim Blob Shape 容器迁移 - 实现计划

## [x] Task 1: 修改 blob.hpp 头文件 - 类型与接口定义
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 添加 `#include <tvm/ffi/container/shape.h>`
  - 将 `vector<int> shape_` 成员替换为 `tvm::ffi::Shape shape_`
  - 移除 `shared_ptr<SyncedMemory> shape_data_` 成员（死代码）
  - 将 `int count_` 改为 `int64_t count_`
  - 新增 `tvm::ffi::ShapeView shape_view() const` 方法声明
  - 添加 `vector<int> shape_vec_` 缓存，`shape()` 返回 `const vector<int>&`（性能优化，避免按值返回）
  - 添加 `shape_data()` 方法返回 `const int*`（供layers中直接访问shape数组使用）
  - 修改 `shape(int index)` 返回类型适配 int64_t→int 安全转换
  - `num_axes()` 返回 int（static_cast<int>(shape_.size())）
  - `count()` 返回 int（static_cast<int>(count_)，Reshape时检查INT_MAX溢出）
  - `count(start_axis, end_axis)` 返回 int，内部使用 int64_t 乘法并检查溢出
  - `CanonicalAxisIndex` 逻辑不变
  - `offset()` 方法使用 int64_t 计算，返回 int（验证不溢出）
  - Legacy 访问器（num/channels/height/width）保持 int 返回
  - 保持 `DISABLE_COPY_AND_ASSIGN(Blob)`
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: blob.hpp 可独立编译（无语法错误）✅
  - `programmatic` TR-1.2: shape_data_ 不再出现在头文件中✅
  - `human-judgement` TR-1.3: 接口方法声明与PRD一致，无遗漏✅
- **Notes**: 编译优化：shape()返回const-ref而非按值返回，添加shape_vec_缓存和shape_data()指针方法，兼容layers中直接访问shape数据的代码

## [x] Task 2: 修改 blob.cpp - Reshape 与核心逻辑适配
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 4个Reshape重载均适配tvm::ffi::Shape，并同步更新shape_vec_缓存
  - 移除 shape_data_ 相关的 SyncedMemory 分配和写入逻辑
  - 保留 data_/diff_ 的 capacity 管理逻辑不变
  - 溢出检查：`CHECK_LE(shape[i], INT_MAX / count_)` （INT_MAX边界，因count()返回int）
  - `ShapeEquals`: 使用shape_直接比较（支持 proto BlobShape 比较）
  - `CopyFrom`: 使用shape_view()进行形状比较
  - `FromProto`: 从 BlobProto 解析形状，构造Shape并同步shape_vec_
  - `ToProto`: 遍历 shape_ 填充 proto->mutable_shape()->add_dim()
  - 模板特化（Update/asum/sumsq/scale 等）中 count() 返回int兼容math函数
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-2.1: 4个Reshape重载编译通过✅
  - `programmatic` TR-2.2: shape_data_ 引用完全移除（grep验证）✅
  - `programmatic` TR-2.3: ToProto/FromProto 序列化反序列化形状正确✅
  - `programmatic` TR-2.4: ShapeEquals 比较逻辑正确（旧4维proto和新shape proto都支持）✅
- **Notes**: Reshape每次赋值 shape_ = Shape(begin, end)，同时更新shape_vec_缓存

## [x] Task 3: 适配 offset() 与索引计算方法
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - `offset(n, c, h, w)`: 内部乘法使用 int64_t，最后 CHECK_LE(offset, INT_MAX) 后返回 int（兼容现有接口）
  - `offset(const vector<int>& indices)`: 同样使用 int64_t 中间计算
  - `count(start_axis, end_axis)`: 使用 int64_t 累乘并检查INT_MAX溢出
  - `CanonicalAxisIndex`: 逻辑不变，仍使用 int 索引
  - `LegacyShape`: 保持返回 int（Shape元素是int64_t但维度值小，安全static_cast）
  - `data_at`/`diff_at` 方法保持 Dtype 返回类型不变
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: offset计算结果与原实现一致（单元测试对比）✅
  - `programmatic` TR-3.2: count(start,end) 范围计算正确✅
  - `human-judgement` TR-3.3: 边界情况（空Blob、1维Blob）索引行为正常✅

## [x] Task 4: 简化 _caffe.cpp FFI 绑定
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `Blob_GetShape`: 直接返回 `blob->shape()`（返回vector<int>，tvm-ffi自动转tuple）
  - `Blob_GetData`: 删除 `vector<int64_t> tensor_shape` 临时变量，直接使用 `blob->shape_view()`
  - `Blob_GetDiff`: 同上简化
  - `Blob_SetData`: 形状比较直接用 ShapeView 迭代器比较
  - `Param_GetData`: 同 Blob_GetData 简化
  - numel 计算使用 `expected_shape.Product()`
  - 同步更新 src/caffe/_caffe.cpp 和 pycaffe/python/pycaffe/_caffe.cpp
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: _caffe.cpp 编译通过✅
  - `programmatic` TR-4.2: 不再有 `vector<int64_t> tensor_shape` 临时变量（grep验证）✅
  - `human-judgement` TR-4.3: FFI代码行数减少，可读性提升✅
- **Notes**: 关键简化点：消除 vector<int>→vector<int64_t>→ShapeView 的双重转换

## [x] Task 5: 编译修复 - 解决所有编译错误
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 全量编译 caffe-slim C++ 库（WSL环境）
  - 修复所有类型不匹配错误（int vs int64_t）
  - 添加shape_vec_缓存和shape_data()方法解决layers中const int* shape参数问题
  - 所有layers/目录下.cpp文件零修改通过编译
  - net.cpp、net.hpp无需修改
  - test_caffe_slim.cpp 编译通过
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: C++ 编译零错误（仅有-Wsign-compare警告）✅
  - `programmatic` TR-5.2: caffe-slim 共享库成功构建✅
  - `programmatic` TR-5.3: C++ 单元测试编译通过✅
- **Notes**: layers中存在使用`blob->shape(i)`和`const int* shape = blob->shape_data()`模式的代码，通过添加shape_data()方法完美兼容

## [x] Task 6: C++ 测试适配与验证
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 运行 tests/test_caffe_slim.cpp 单元测试
  - 38个层注册正常
  - 45项测试全部通过
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: test_caffe_slim 所有测试用例通过（45/45）✅
  - `programmatic` TR-6.2: 退出码0✅

## [x] Task 7: Python wheel 构建与 pycaffe 适配
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 更新 pycaffe/CMakeLists.txt：输出目录改为${CAFFE_ROOT}/python/caffe/，安装tvm_ffi Python包和libtvm_ffi.so
  - 更新 pycaffe/pyproject.toml：包名改为caffe，简化依赖为numpy>=1.24,<3.0，支持Python 3.10+
  - python/caffe/__init__.py 添加_setup_library_paths()预加载逻辑
  - 构建wheel成功（caffe-1.0.0-py3-none-linux_x86_64.whl）
  - import caffe基础测试通过
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-7.1: wheel构建成功✅
  - `programmatic` TR-7.2: `import caffe` 无错误✅
  - `programmatic` TR-7.3: Net.blob_shape()返回tuple✅

## [x] Task 8: Python 推理测试与回归验证
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 运行 test_import.py
  - 运行 test_python.py
  - 运行 batch_inference_demo.py 验证端到端推理（LeNet MNIST）
  - blob_shape返回tuple类型
  - blob_data返回正确形状的numpy数组
  - set_input_data赋值正常
  - forward()输出正确概率分布
  - LeNet MNIST准确率99.01%
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-8.1: test_import.py 通过✅
  - `programmatic` TR-8.2: test_python.py 通过（ALL CHECKS PASSED）✅
  - `programmatic` TR-8.3: batch_inference_demo.py 正常运行，准确率99.01%✅
  - `human-judgement` TR-8.4: Python端使用体验无变化✅

## [x] Task 9: 最终验证与清理
- **Priority**: medium
- **Depends On**: Task 6, Task 8
- **Description**:
  - grep 验证 shape_data_ 完全移除（无匹配）
  - 修复FromProto中count_被错误降级为int的问题
  - ShareData/ShareDiff使用count()返回int兼容CHECK_EQ
  - memory 布局（data_/diff_）无回归
- **Acceptance Criteria Addressed**: AC-1 through AC-9
- **Test Requirements**:
  - `programmatic` TR-9.1: `grep -r shape_data_` 返回空✅
  - `programmatic` TR-9.2: 重新编译零错误，test_python.py通过✅
  - `human-judgement` TR-9.3: 代码变更最小化，核心逻辑未被破坏✅
