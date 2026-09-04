# Caffe-Slim Blob Shape 迁移验证清单

## 代码结构验证
- [x] blob.hpp 已添加 `#include <tvm/ffi/container/shape.h>`
- [x] blob.hpp 中 `shape_` 成员类型为 `tvm::ffi::Shape`（非 vector<int>）
- [x] blob.hpp 中 `shape_data_` 成员已完全移除
- [x] blob.hpp 中 `count_` 成员类型为 `int64_t`
- [x] blob.hpp 新增 `shape_view()` 方法声明，返回 `tvm::ffi::ShapeView`
- [x] blob.hpp 保留 `shape()` 方法（返回 const vector<int>&，带shape_vec_缓存）
- [x] blob.hpp 新增 `shape_data()` 方法返回 `const int*`（兼容layers中直接访问shape数组的代码）
- [x] blob.hpp 中 `count()` 返回 int（Reshape时检查INT_MAX溢出）

## 实现逻辑验证
- [x] 4个Reshape重载均已适配tvm::ffi::Shape
- [x] Reshape中shape_data_相关SyncedMemory分配/写入代码已移除
- [x] Reshape中count_计算使用shape_.Product()，同时更新shape_vec_缓存
- [x] 溢出检查使用INT_MAX边界（count()返回int兼容现有math函数）
- [x] ShapeEquals方法正确处理legacy proto和新shape proto两种情况
- [x] FromProto正确从BlobProto解析构造Shape并同步shape_vec_
- [x] ToProto正确遍历shape_填充proto->add_dim()
- [x] CopyFrom使用shape_view()进行形状比较

## 索引与计算验证
- [x] CanonicalAxisIndex负索引逻辑保持不变
- [x] offset(n,c,h,w)使用int64_t中间计算，结果正确
- [x] offset(indices)使用int64_t中间计算，结果正确
- [x] count(start_axis, end_axis)范围计算返回int且正确（检查溢出）
- [x] LegacyShape访问器(num/channels/height/width)返回正确值
- [x] data_at/diff_at方法工作正常

## FFI绑定验证
- [x] _caffe.cpp不再有vector<int64_t> tensor_shape临时转换变量
- [x] Blob_GetData直接使用blob->shape_view()构造ShapeView
- [x] Blob_GetDiff直接使用blob->shape_view()构造ShapeView
- [x] Blob_SetData形状比较使用ShapeView直接迭代和Product()
- [x] Param_GetData直接使用blob->shape_view()
- [x] CpuBlobDataAllocator中net_keep_alive逻辑未破坏

## 编译与测试验证
- [x] C++代码零编译错误（仅有-Wsign-compare警告）
- [x] caffe-slim共享库构建成功
- [x] test_caffe_slim.cpp C++单元测试全部通过（45/45）
- [x] pycaffe wheel构建成功（caffe-1.0.0-py3-none-linux_x86_64.whl）
- [x] `import caffe` 无错误
- [x] test_import.py通过
- [x] test_python.py通过（ALL CHECKS PASSED）
- [x] batch_inference_demo.py端到端推理输出正确结果（LeNet MNIST准确率99.01%）

## 死代码与清理验证
- [x] grep -r "shape_data_" 无残留引用
- [x] 所有layers/ .cpp文件编译通过（无shape相关错误，零修改）
- [x] net.cpp/net.hpp编译通过（零修改）
- [x] ShareData/ShareDiff的count比较使用count()返回int兼容CHECK_EQ
- [x] 无遗留的关键int/int64_t隐式转换警告
- [x] BlobString()形状打印输出格式不变

## 兼容性验证
- [x] 现有Layer实现无需修改即可编译（通过shape()和shape_data()兼容接口）
- [x] Python端net.blob_shape(blob_name)返回tuple，与预期行为一致
- [x] Python端net.blob_data(blob_name)返回numpy数组，形状正确
- [x] net.set_input_data()赋值操作正常工作
- [x] forward()输出概率值正确（Softmax概率和为1.0，MNIST准确率99.01%）
