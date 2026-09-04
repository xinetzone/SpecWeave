# caffe-slim BVLC PyCaffe API 兼容层 - Verification Checklist

## C++ tvm-ffi 接口
- [x] 新增的 8 个 tvm-ffi 函数编译通过（Net_NumLayers/Net_LayerNames/Net_LayerType/Net_ParamLayerIndices/Net_TopIds/Net_BottomIds/Param_GetShape/Param_GetData）
- [x] 所有新增函数有正确的参数校验（非法索引抛出 ValueError）
- [x] Param_GetData 使用 CpuBlobDataAllocator 零拷贝模式，与 Blob_GetData 一致
- [x] 新增代码遵循现有代码风格（命名、错误处理、类型使用、TVM_FFI_REGISTER_EXPORT 宏）
- [ ] 编译无 warning（需在 Docker 中实际编译验证）
- [ ] fgvsirfeature 模型加载后 layer_names 数量与 prototxt 一致（需端到端验证）

## BlobProxy 类
- [x] BlobProxy.data 返回 numpy 数组，shape/dtype 正确（Mock 测试 TR-2.1 通过）
- [x] BlobProxy.data[...] = arr 赋值正确写入底层 Caffe Blob 内存（Mock 测试 TR-2.2 通过）
- [x] 返回的 numpy 数组是零拷贝视图（直接复用 blob_data() 返回值）
- [x] BlobProxy.diff 返回 numpy 数组，shape 与 data 一致
- [x] BlobProxy.shape 返回正确的 tuple
- [x] BlobProxy.count 属性返回元素总数
- [x] 参数 BlobProxy（param_idx 模式）data/shape/count 正确
- [ ] 多次访问 .data 返回有效视图（不会因 tensor 销毁导致悬空指针，需端到端验证）

## net.blobs
- [x] net.blobs 是 OrderedDict，按 net.blob_names 顺序（Mock 测试 TR-3.1, TR-3.3 通过）
- [x] net.blobs.keys() 与 net.blob_names 一致
- [x] net.blobs['name'].data.shape 返回正确 shape
- [x] 缓存生效：多次访问 net.blobs 返回同一 OrderedDict 对象
- [x] net.blobs['data'].data[...] = x 赋值后 forward 结果正确（Mock 测试 TR-3.4 通过）

## net.forward() 兼容
- [x] net.forward() 返回 dict 而非 None（Mock 测试 TR-4.1 通过）
- [x] 返回 dict 包含所有 net.outputs 中的 blob
- [x] net.forward(**kwargs) 支持通过关键字参数设置输入（Mock 测试 TR-4.2 通过）
- [x] kwargs key 不匹配 inputs 时抛出 ValueError
- [x] net.forward(blobs=['layer_name']) 返回 outputs + 指定中间层（Mock 测试 TR-4.3 通过）
- [x] 返回的 numpy 数组是零拷贝视图
- [x] 原生 Net.forward 可通过 net._forward_slim() 访问
- [x] batch size 不匹配时由 numpy 赋值自动抛出 ValueError

## net.layers 和 net.params
- [x] net.layers 是 list，按网络顺序排列
- [x] net.layer_dict 是 OrderedDict，键是 layer_names
- [x] net.layers[i].type / net.layer_dict['name'].type 返回层类型字符串（Mock 测试 TR-5.2 通过）
- [x] net.params 是 OrderedDict，只包含有参数的层（Mock 测试 TR-5.3 通过）
- [x] net.params['conv'][0].data.shape 返回权重 shape（Mock 测试 TR-5.3 通过）
- [x] net.params['conv'][1].data.shape 返回 bias shape（Mock 测试 TR-5.4 通过）
- [x] 无参数层（如 ReLU、Pooling）不出现在 net.params 中
- [x] net.top_names['layer'] 返回该层 top blob 名称列表（Mock 测试 TR-5.5 通过）
- [x] net.bottom_names['layer'] 返回该层 bottom blob 名称列表（Mock 测试 TR-5.6 通过）
- [x] net._layer_names 缓存 layer 名称列表
- [x] LayerProxy.blobs 属性返回该层参数 BlobProxy 列表，带缓存

## 加载机制与原生 API 保护
- [x] import caffe 默认不启用 BVLC 兼容层（compat.py 不自动加载，需显式 import caffe.compat）
- [x] import caffe.compat 自动启用兼容层
- [x] enable_bvlc_compat() 可显式调用，幂等安全
- [x] 启用兼容层后 net.blob_data() 仍正常工作（原生方法未被覆盖）
- [x] 启用兼容层后 net.set_input_data() 仍正常工作
- [x] 启用兼容层后 net.blob_names、net.inputs、net.outputs 属性仍正常
- [x] 启用兼容层后 net._forward_slim() 可调用原生 forward
- [ ] 启用兼容层后 net.reshape() 仍正常工作（需端到端验证）
- [ ] 兼容层加载后无性能下降（forward 时间增加 < 5%，需端到端验证）

## 端到端验证（需在 Docker 中重建镜像后运行）
- [ ] 端到端测试脚本 test_bvlc_compat.py 全部通过
- [ ] fgvsirfeature 模型加载成功
- [ ] 设置输入→forward→获取输出结果与原生 slim API 一致
- [ ] 中间层特征提取（如 conv 层）结果正确
- [ ] 模型参数访问（权重/bias）shape 和数据正确
- [ ] 典型 BVLC 风格推理代码仅需 `import caffe.compat` 即可运行
- [ ] 不支持的功能（backward/start/end/NetSpec）抛出清晰的 NotImplementedError

## 代码质量
- [x] 兼容层代码在独立文件（_compat.py）中，不污染原生 __init__.py
- [x] compat.py 作为独立入口文件，文档完整
- [x] 没有重复实现已有功能，复用 blob_data/set_input_data 等原生方法
- [x] 所有猴子补丁在 enable_bvlc_compat() 中统一管理
- [x] _bvlc_compat_enabled 标记确保幂等
- [x] 基础单元测试 test_compat_basic.py 覆盖 BlobProxy/LayerProxy/Net 兼容属性
- [x] 端到端测试脚本 test_bvlc_compat.py 覆盖真实模型场景
