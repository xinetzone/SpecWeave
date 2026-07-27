# caffe-slim BVLC PyCaffe API 兼容层 - Product Requirement Document

## Overview
- **Summary**: 在 caffe-slim 的 tvm-ffi 后端上实现 BVLC PyCaffe 风格 API 兼容层，支持 `net.blobs`、`net.layers`、`net.params`、`net.forward()` 返回 dict 等常用推理接口，使现有 BVLC 代码和 Notebook 可以最小改动迁移到 caffe-slim。
- **Purpose**: 解决现有 BVLC PyCaffe 代码/Notebook 在 caffe-slim 上无法直接运行的问题，降低用户迁移成本；保持 caffe-slim 轻量推理定位不变。
- **Target Users**: 使用 caffe-slim 进行模型推理、需要复用现有 BVLC 代码的算法工程师和研究员。

## Goals
- 在 Python 层实现 `net.blobs` OrderedDict，支持通过 `net.blobs['name'].data` 读写（零拷贝）
- 改造 `net.forward()` 使其返回 `{blob_name: ndarray}` dict，支持传入输入 kwargs 和 `blobs` 参数提取中间层
- 扩展 C++ tvm-ffi 接口，暴露层名称、层类型、参数信息、层连接拓扑
- 实现 `net.layers` 和 `net.params` OrderedDict，支持访问层类型和参数权重
- 保持 slim 原生 API（`blob_data`/`set_input_data`）为一等公民，兼容层为可选包装
- 零性能 overhead：兼容层使用零拷贝视图，不做不必要的数据复制

## Non-Goals (Out of Scope)
- **不支持** 训练相关功能：`backward()`、`backward_from/to()`、所有 Solver（SGD/Adam等）
- **不支持** 部分层前向/反向（`forward(start=, end=)`）
- **不支持** 训练模式下的 dropout/batch norm 训练行为（仅 TEST 模式推理）
- **不支持** `NetSpec` 网络定义 API（caffe-slim 仅支持从 prototxt 加载已有网络）
- **不支持** `net.save()`/`net.to_proto()` 模型保存功能
- **不支持** GPU 模式（caffe-slim 定位 CPU-only）
- **不支持** 多输入/多输出的复杂 batch 处理（`forward_all` 可延后或简化）

## Background & Context
- 当前 caffe-slim 的 tvm-ffi 后端仅暴露最小推理接口：`Net_Init`/`Net_Forward`/`Blob_GetData`/`Blob_SetData`/`Blob_Names`/`Input_Names`/`Output_Names`
- BVLC pycaffe.py 通过猴子补丁给 Net 类添加 `blobs`/`layers`/`params`/`forward` 等属性/方法，这些依赖底层 C++ 绑定暴露的 `_blobs`/`_layer_names`/`layers`/`_forward`/`_top_ids`/`_bottom_ids` 等内部属性
- C++ 核心 Net 类已经具备所有需要的公共方法（`layer_names()`/`layers()`/`params()`/`top_ids()`/`bottom_ids()`/`ForwardFromTo()`），只是 tvm-ffi 没有暴露
- 分析结论：`net.blobs` 和 `forward()` 返回 dict 可纯 Python 实现；`net.layers`/`net.params`/`top_names`/`bottom_names` 需要新增 C++ tvm-ffi 接口

## Functional Requirements
- **FR-1**: `net.blobs` 返回 OrderedDict[str, BlobProxy]，支持 `net.blobs['data'].data.shape`、`net.blobs['data'].data[...] = arr`、`net.blobs['data'].diff`
- **FR-2**: `net.forward(blobs=None, **kwargs)` 返回 `{blob_name: ndarray}` dict，kwargs 用于设置输入 blob 数据
- **FR-3**: `net.layers` 返回 OrderedDict[str, LayerProxy]，支持 `net.layers['conv1'].type`、`net.layers['conv1'].blobs`（参数列表）
- **FR-4**: `net.params` 返回 OrderedDict[str, List[BlobProxy]]，即 `net.params['conv1'][0].data` 为权重，`[1]` 为 bias
- **FR-5**: `net.layer_dict`、`net.top_names`、`net.bottom_names` 属性可用
- **FR-6**: C++ 端新增 tvm-ffi 函数：`Net_LayerNames`、`Net_LayerType`、`Net_NumLayers`、`Net_LayerParamBlobIndices`、`Net_TopIds`、`Net_BottomIds`、`Net_ParamBlobNames`
- **FR-7**: 原生 slim API（`blob_data`/`set_input_data`/`blob_names`/`inputs`/`outputs`）继续可用且行为不变
- **FR-8**: `BlobProxy` 对象保持零拷贝语义，`data` 属性返回 numpy 视图而非拷贝

## Non-Functional Requirements
- **NFR-1**: 兼容层加载后，模型初始化和 forward 性能相比原生 slim API 下降不超过 5%
- **NFR-2**: 兼容层代码与原生代码解耦，可选择不加载兼容层保持最小依赖
- **NFR-3**: 错误信息与 BVLC 保持兼容语义，blob/layer 不存在时抛出 KeyError（或兼容的 ValueError）
- **NFR-4**: 所有 BlobProxy 数据访问保持零拷贝，`.data[...] = x` 赋值直接写入底层 Caffe Blob
- **NFR-5**: 兼容层与现有 pycaffe.py 猴子补丁风格保持一致，便于熟悉 BVLC 的用户理解

## Constraints
- **Technical**: tvm-ffi 后端只能通过 DLL 导出的 C 函数交互，不能直接访问 C++ 对象成员；Python 版本 3.14+；仅 CPU 推理
- **Business**: 保持 caffe-slim "slim" 定位——二进制体积和内存占用不应显著增长
- **Dependencies**: tvm-ffi（已有）、numpy（已有）、DLPack 零拷贝协议（已有）

## Assumptions
- 用户主要使用推理（TEST 模式），不需要训练
- Blob 的 diff 属性在推理场景下基本不用，但仍提供访问（返回零数组或真实 diff）
- 模型从 prototxt + caffemodel 加载，不需要 Python 端动态构建网络
- 不需要支持 `forward_all` 批处理的完整 BVLC 语义，可简化实现或延后

## Acceptance Criteria

### AC-1: net.blobs 可用
- **Given**: 已加载一个有 data 和 conv1 层的网络
- **When**: 用户访问 `net.blobs['data'].data.shape`
- **Then**: 返回正确的 shape tuple（如 (1,3,224,224)），是 numpy 数组
- **Verification**: `programmatic`

### AC-2: net.blobs 可写
- **Given**: 已加载网络
- **When**: 用户执行 `net.blobs['data'].data[...] = np.random.randn(1,3,224,224).astype(np.float32)` 然后 `net.forward()`
- **Then**: 输入数据被正确设置，前向传播使用新数据
- **Verification**: `programmatic`

### AC-3: forward() 返回 dict
- **Given**: 已加载网络且设置好输入
- **When**: 用户执行 `out = net.forward()`
- **Then**: `out` 是 dict，包含所有 output blob 名称，值是 numpy 数组
- **Verification**: `programmatic`

### AC-4: forward() 接受输入 kwargs
- **Given**: 已加载网络
- **When**: 用户执行 `out = net.forward(data=np.random.randn(1,3,224,224).astype(np.float32))`
- **Then**: 输入自动设置，完成前向传播，返回 outputs dict
- **Verification**: `programmatic`

### AC-5: forward(blobs=[...]) 提取中间层
- **Given**: 已加载网络
- **When**: 用户执行 `out = net.forward(blobs=['conv1'])`
- **Then**: 返回 dict 包含 output blobs 和 'conv1'，'conv1' 值是 conv1 输出 numpy 数组
- **Verification**: `programmatic`

### AC-6: net.layers 可用
- **Given**: 已加载网络
- **When**: 用户访问 `net.layers['conv1'].type`
- **Then**: 返回层类型字符串，如 'Convolution'
- **Verification**: `programmatic`

### AC-7: net.params 可用
- **Given**: 已加载带权重的网络
- **When**: 用户访问 `net.params['conv1'][0].data.shape`
- **Then**: 返回卷积权重 shape（如 (64,3,7,7)）
- **Verification**: `programmatic`

### AC-8: 原生 slim API 不受影响
- **Given**: 兼容层已加载
- **When**: 用户使用 `net.blob_data('conv1')`、`net.set_input_data('data', arr)`、`net.blob_names`
- **Then**: 行为与加载兼容层之前完全一致
- **Verification**: `programmatic`

### AC-9: Notebook 兼容性
- **Given**: 兼容层已加载
- **When**: 在 Jupyter 中运行现有 BVLC 推理代码（只做前向、不做训练）
- **Then**: 代码无需修改或仅需极小修改即可运行
- **Verification**: `human-judgment`

## Open Questions
- [ ] `blob_diff` 在推理场景下是否需要真实可写？还是返回只读零数组即可？
- [ ] `forward_all` 是否需要实现？还是只实现核心 `forward()` 即可？
- [ ] 兼容层是默认加载还是通过 `import caffe.compat` 显式加载？
- [ ] 层的 `blobs` 属性是只包含参数 blobs（weights/biases）还是包含 top/bottom blobs？BVLC 原语义是前者（参数）
