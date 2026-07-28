# Caffe FFI TVM FFI最佳实践优化 - Verification Checklist

## 构建系统验证
- [ ] CMakeLists.txt使用find_package(tvm_ffi CONFIG REQUIRED)
- [ ] CMakeLists.txt调用tvm_ffi_configure_target(_caffe_ffi)
- [ ] CMakeLists.txt中无add_subdirectory指向tvm-ffi源码
- [ ] CMake配置阶段成功，无错误或致命警告
- [ ] 项目编译成功，生成_caffe_ffi共享库（.dll/.so/.pyd）
- [ ] 编译无新增警告（-Wall -Wextra / W3下）

## Blob双类模式验证
- [ ] BlobObj类继承自Object，使用TVM_FFI_DECLARE_OBJECT_INFO_FINAL
- [ ] Blob类继承自ObjectRef，使用TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE
- [ ] BlobObj持有data_tensor_和diff_tensor_（Tensor类型）
- [ ] Blob构造函数通过make_object<BlobObj>创建实例
- [ ] Blob.data_tensor()和diff_tensor()直接返回Tensor
- [ ] Blob反射注册完整：init、shape、Reshape、count、num_axes、name等
- [ ] 引用计数正常工作，无内存泄漏

## Tensor零拷贝验证
- [ ] Blob从numpy数组设置数据时共享内存（零拷贝）
- [ ] Blob获取数据为numpy数组时共享内存（零拷贝）
- [ ] 修改numpy数组内容反映到Blob.data
- [ ] 修改Blob.data内容反映到numpy数组
- [ ] Reshape操作正确重新分配Tensor
- [ ] 无Array<float>→list→numpy的多次拷贝路径（或兼容层可选）

## Layer双类模式验证
- [ ] LayerObj类继承自Object，使用TVM_FFI_DECLARE_OBJECT_INFO（非final，可继承）
- [ ] Layer类继承自ObjectRef，使用TVM_FFI_DEFINE_OBJECT_REF_METHODS
- [ ] LayerObj设置_type_child_slots和_type_child_slots_can_overflow
- [ ] 虚函数接口（LayerSetUp、Reshape、Forward_cpu）签名保持不变
- [ ] blobs_使用Array<Blob>而非std::vector<ObjectPtr<Blob>>
- [ ] 所有20个Layer子类（Input/ReLU/Conv/InnerProduct/Softmax等）正确继承LayerObj
- [ ] LayerRegistry工厂类适配新的双类模式，能正确创建Layer实例
- [ ] Layer反射注册：type()、blobs()等方法

## Net双类模式验证
- [ ] NetObj类继承自Object，使用TVM_FFI_DECLARE_OBJECT_INFO_FINAL
- [ ] Net类继承自ObjectRef，使用TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE
- [ ] layers_使用Array<Layer>，blobs_使用Array<Blob>
- [ ] 名称索引使用Map<String, int64_t>
- [ ] Forward返回Map<String, Blob>而非Map<String, Array<float>>
- [ ] 拓扑排序和前向传播逻辑保持不变
- [ ] Net反射注册完整：Forward、name、layer_names、blob_names、blobs_array、layers_array、blob_by_name、layer_by_name、has_blob、has_layer、input_blobs、output_blobs、CopyTrainedLayersFrom等
- [ ] 从prototxt文件和字符串创建Net正常

## Python绑定验证
- [ ] Python Blob/Layer/Net使用@c_class装饰器
- [ ] _core.py代码量大幅减少（无复杂双轨逻辑）
- [ ] 无_add_python_wrappers monkey patch代码
- [ ] Blob.data属性返回numpy数组（零拷贝）
- [ ] Blob.diff属性返回numpy数组（零拷贝）
- [ ] Blob.from_numpy()实现零拷贝（或最小拷贝）
- [ ] Blob.to_numpy()实现零拷贝（或最小拷贝）
- [ ] Net.forward(input_dict)接受numpy数组输入，返回numpy数组输出
- [ ] Net.blobs_dict、Net.layers_dict属性正常
- [ ] Net['blob_name']、'blob_name' in net、for blob_name in net等协议正常
- [ ] Net.copy_from()加载caffemodel权重正常
- [ ] 所有Python公共API与优化前行为一致

## 全局函数与错误处理验证
- [ ] NewBlob、NewBlobFromShape、NewNetFromProtoString、NewNetFromFile工厂函数正常
- [ ] NewBlobFromShape直接接受ShapeView/Array，无冗余vector拷贝
- [ ] 关键函数使用TVM_FFI_DLL_EXPORT_TYPED_FUNC导出
- [ ] 无效shape（负维度）抛出异常
- [ ] 不存在的blob名称抛出KeyError/ValueError
- [ ] 文件打开失败抛出包含文件路径的IO错误
- [ ] prototxt解析失败抛出明确错误信息
- [ ] Python端能正确捕获C++抛出的异常

## 单元测试验证
- [ ] tests/python/test_blob.py全部通过
- [ ] tests/python/test_layers.py全部通过
- [ ] tests/python/test_net.py全部通过
- [ ] pytest运行无失败、无错误、无意外跳过
- [ ] 测试覆盖率不低于优化前水平

## 端到端冒烟测试验证
- [ ] examples/create_and_run_mlp.py运行无错误
- [ ] MLP创建Input→InnerProduct→ReLU→InnerProduct→Softmax网络正常
- [ ] 前向传播计算结果正确
- [ ] 数值精度误差<1e-5
- [ ] 典型用户工作流（创建Net→设置输入→Forward→获取输出）正常

## 性能验证
- [ ] 性能基准测试脚本可运行
- [ ] Blob<->numpy转换相比优化前有显著性能提升（>5倍）
- [ ] 1M float32元素零拷贝转换耗时<1ms（对比拷贝模式~10ms+）
- [ ] Forward前向传播耗时无退化
- [ ] 零拷贝内存共享验证通过（numpy数组与Blob共享内存地址）

## 文档与代码质量验证
- [ ] 关键公共API（Blob、Layer、Net类及主要方法）有Doxygen注释
- [ ] 头文件中无using namespace tvm::ffi（避免命名空间污染）
- [ ] include顺序统一：tvm/ffi头 → caffe_ffi头 → 标准库头
- [ ] 代码风格与现有代码库一致
- [ ] 无 commented-out 死代码
- [ ] OPTIMIZATION_REPORT.md优化报告完整，包含：
  - [ ] 优化点概述
  - [ ] 性能对比数据
  - [ ] 代码改进统计
  - [ ] API兼容性说明
  - [ ] 后续建议

## API兼容性验证
- [ ] Blob.shape、Blob.num_axes、Blob.count()、Blob.Reshape()存在且行为一致
- [ ] Blob.data、Blob.diff numpy属性存在且行为一致
- [ ] Blob.name getter/setter存在
- [ ] Net.name、Net.layer_names、Net.blob_names存在
- [ ] Net.blobs_array()、Net.layers_array()、Net.input_blobs_array()、Net.output_blobs_array()存在
- [ ] Net.blob_by_name()、Net.layer_by_name()、Net.has_blob()、Net.has_layer()存在
- [ ] Net.Forward()、Net.forward()存在且行为一致
- [ ] Net.CopyTrainedLayersFrom()存在
- [ ] Layer.type()、Layer.blobs_array()存在
- [ ] caffe_ffi.NewBlob()、caffe_ffi.NewNetFromFile()、caffe_ffi.NewNetFromProtoString()存在
- [ ] caffe_ffi.version()、caffe_ffi.set_log_level()等工具函数存在
