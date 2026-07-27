# caffe-slim BVLC PyCaffe API 兼容层 - Verification Checklist

## C++ tvm-ffi 接口
- [ ] 新增的 9 个 tvm-ffi 函数编译通过（Net_NumLayers/Net_LayerNames/Net_LayerType/Net_LayerParamBlobCount/Net_ParamBlobNames/Net_ParamLayerIndices/Net_TopIds/Net_BottomIds/Param_GetData）
- [ ] 所有新增函数有正确的参数校验（空指针、非法索引、未知 blob/layer 名称）
- [ ] Param_GetData 使用 CpuBlobDataAllocator 零拷贝模式，与 Blob_GetData 一致
- [ ] 新增代码遵循现有代码风格（命名、错误处理、类型使用）

## BlobProxy 类
- [ ] BlobProxy.data 返回 numpy 数组，shape/dtype 正确
- [ ] BlobProxy.data[...] = arr 赋值正确写入底层 Caffe Blob 内存
- [ ] 返回的 numpy 数组是零拷贝视图（np.shares_memory 验证）
- [ ] BlobProxy.diff 返回 numpy 数组，shape 与 data 一致
- [ ] BlobProxy.shape 返回正确的 tuple
- [ ] 多次访问 .data 返回有效视图（不会因 tensor 销毁导致悬空指针）

## net.blobs
- [ ] net.blobs 是 OrderedDict，按网络拓扑顺序（输入到输出）
- [ ] net.blobs.keys() 与 net.blob_names 一致
- [ ] net.blobs['name'].data.shape 返回正确 shape
- [ ] 缓存生效：多次访问 net.blobs 返回同一 OrderedDict 对象
- [ ] net.blobs['data'].data[...] = x 赋值后 forward 结果正确

## net.forward() 兼容
- [ ] net.forward() 返回 dict 而非 None
- [ ] 返回 dict 包含所有 net.outputs 中的 blob
- [ ] net.forward(**kwargs) 支持通过关键字参数设置输入
- [ ] kwargs key 不匹配 inputs 时抛出异常
- [ ] net.forward(blobs=['layer_name']) 返回 outputs + 指定中间层
- [ ] 返回的 numpy 数组是零拷贝视图
- [ ] 原生 Net.forward 可通过 net._forward_slim() 访问
- [ ] batch size 不匹配时抛出异常

## net.layers 和 net.params
- [ ] net.layer_dict 是 OrderedDict，键是 layer_names
- [ ] net.layers['name'].type 返回正确的层类型字符串（如 'Convolution'、'ReLU'、'InnerProduct'）
- [ ] net.params 是 OrderedDict，只包含有参数的层
- [ ] net.params['conv'][0].data.shape 返回权重 shape（output_dim, input_dim, kH, kW）
- [ ] net.params['conv'][1].data.shape 返回 bias shape（output_dim,）
- [ ] 无参数层（如 ReLU、Pooling）不出现在 net.params 中或 params[name] 为空列表
- [ ] net.top_names['layer'] 返回该层 top blob 名称列表
- [ ] net.bottom_names['layer'] 返回该层 bottom blob 名称列表

## 加载机制与原生 API 保护
- [ ] import caffe 默认不启用 BVLC 兼容层（net.blobs 不存在）
- [ ] import caffe.compat 或 enable_bvlc_compat() 后兼容层可用
- [ ] 启用兼容层后 net.blob_data() 仍正常工作
- [ ] 启用兼容层后 net.set_input_data() 仍正常工作
- [ ] 启用兼容层后 net.blob_names、net.inputs、net.outputs 属性仍正常
- [ ] 启用兼容层后 net.reshape() 仍正常工作
- [ ] 兼容层加载后无性能下降（forward 时间增加 < 5%）

## 端到端验证
- [ ] fgvsirfeature 模型加载成功
- [ ] 设置输入→forward→获取输出结果与原生 slim API 一致
- [ ] 中间层特征提取（如 conv1、pool5）结果正确
- [ ] 模型参数访问（权重/bias）shape 正确
- [ ] 典型 BVLC 风格推理代码无需修改即可运行
- [ ] 明确不支持的功能（backward/solver/NetSpec/partial forward）给出清晰错误提示

## 代码质量
- [ ] 兼容层代码在独立文件（_compat.py）中，不污染原生 __init__.py
- [ ] 没有重复实现已有功能，复用 blob_data/set_input_data 等原生方法
- [ ] 所有猴子补丁在 enable_bvlc_compat() 中统一管理
- [ ] 错误信息清晰，提示哪些 BVLC 功能不支持
