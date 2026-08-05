# caffe-ffi P2 算子补齐实现 Spec

## Why
[gap_analysis_report.md](file:///d:/spaces/SpecWeave/.trae/specs/caffex-vs-caffe-ffi-gap-analysis/gap_analysis_report.md) 的 P2 清单包含 13 类训练专用/数据输入/冷门算子，此前标记为"推理引擎刻意不实现"。用户决定**全部补齐** P2 算子，以闭合算子覆盖差距（除 GPU 专属 CuDNN 包装层外）。补齐后算子覆盖率从 91.8% 进一步提升，且多标签损失（ContrastiveLoss/InfogainLoss/MultinomialLogisticLoss）与数据输入层（MemoryData/DummyData/Data 等）使 caffe-ffi 具备更完整的训练/数据加载能力。

## What Changes
- 在 [caffe.proto](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/proto/caffe/proto/caffe.proto) 新增 11 个 P2 参数 message，并在 `LayerParameter` 注册字段（179-189）
- 新增 13 个算子实现（头文件 + cpp），遵循现有 Layer/NeuronLayer/LossLayer 模式
  - **数据输入/工具类**：MemoryData、DummyData、Python、Recurrent（基类注册）、Upsample
  - **损失类**：ContrastiveLoss、InfogainLoss、MultinomialLogisticLoss
  - **数据 I/O 类（Python/numpy 桥接）**：Data、ImageData、HDF5Data、HDF5Output、WindowData
- **CuDNN\* 包装层（10 种）刻意不实现**（GPU 专属，caffe-ffi 为纯 CPU 引擎），在报告中记录理由
- 重新生成并提交 `caffe_pb2.py`（预生成 pb2，开箱即用约定）
- 补齐各算子单元测试（forward/backward/数值梯度），遵循项目 Backward 验证工作流
- 更新 [gap_analysis_report.md](file:///d:/spaces/SpecWeave/.trae/specs/caffex-vs-caffe-ffi-gap-analysis/gap_analysis_report.md) P2 状态

## Impact
- Affected specs: `caffex-vs-caffe-ffi-gap-analysis`（P2 状态刷新）
- Affected code: `projects/xuanspace/libs/caffe-ffi/`（proto / include / src / tests / python pb2）
- 构建：proto 变更需重新编译（protoc 自动生成），pb2 需手动同步提交
- 数据 I/O 层通过 Python/numpy 桥接，**不引入** leveldb/lmdb/OpenCV/HDF5 等 C++ 外部依赖

## ADDED Requirements

### Requirement: P2 算子参数模型扩展
系统 SHALL 在 `caffe.proto` 中新增下列参数 message，并在 `LayerParameter` 中注册对应字段（179-189）：
- `DataParameter`（source/batch_size/rand_skip/backend/scale/mean_file 等）、`ImageDataParameter`（source/batch_size/rand_skip/shuffle/new_height/new_width/scale 等）
- `HDF5DataParameter`（source/batch_size）、`HDF5OutputParameter`（file_name）、`MemoryDataParameter`（batch_size/channels/height/width/scale）、`WindowDataParameter`（source/batch_size/fg_threshold/bg_threshold 等）
- `DummyDataParameter`（shape/data_filler）、`PythonParameter`（module/layer/param_str）、`ContrastiveLossParameter`（margin）、`InfogainLossParameter`（source）、`UpsampleParameter`（scale）

#### Scenario: proto 编译通过
- **WHEN** 修改 `caffe.proto` 后执行 CMake 构建
- **THEN** protoc 成功生成 `caffe.pb.cc/.h/caffe_pb2.py`，无字段冲突

#### Scenario: pb2 同步提交
- **WHEN** 构建完成后
- **THEN** 新生成的 `caffe_pb2.py` 同步到 `python/caffe_ffi/caffe/proto/` 并提交

### Requirement: 数据输入/工具类 P2 算子（5 个）
系统 SHALL 实现并注册：
- **MemoryData**：内存数据输入（numpy/DLPack 张量 → Blob），支持 batch_size/channels/height/width/scale
- **DummyData**：占位数据层，按 `data_filler` 填充 shape 指定的数据
- **Python**：自定义 Python 层，通过 ffi 桥接调用 Python 模块的 `setup`/`reshape`/`forward`/`backward`
- **Recurrent**：注册通用 Recurrent 基类为独立层（`REGISTER_LAYER_CLASS(Recurrent)`，基础设施已存在，RNN/LSTM/LSTMUnit 已继承）
- **Upsample**：最近邻上采样，按 `scale` 因子放大空间维度

#### Scenario: 数据/工具算子前向正确
- **WHEN** 对典型输入执行 `Forward_cpu`
- **THEN** 输出与 numpy 参考实现一致（rtol=1e-5）

### Requirement: 损失类 P2 算子（3 个）
系统 SHALL 实现并注册（继承损失层模式，支持 `LossParameter` 的 ignore_label/normalization）：
- **ContrastiveLoss**：对比损失（margin 参数）
- **InfogainLoss**：信息增益损失（`source` 指定信息增益矩阵）
- **MultinomialLogisticLoss**：多项式逻辑损失（多分类，与 SoftmaxWithLoss 的 cross-entropy 对比）

#### Scenario: 损失层前向兼容
- **WHEN** 执行损失层前向
- **THEN** 损失输出与参考一致，且 Backward 梯度正确（支持常规训练循环）

### Requirement: 数据 I/O 类 P2 算子（5 个，Python/numpy 桥接）
系统 SHALL 实现并注册，通过 Python/numpy 桥接读取数据（**不引入** leveldb/lmdb/OpenCV/HDF5 C++ 依赖）：
- **Data**：数据源读取（batch 加载，经 Python 桥接提供）
- **ImageData**：图像列表读取（经 Python/numpy 桥接解码）
- **HDF5Data**：HDF5 数据读取（经 Python/h5py 桥接）
- **HDF5Output**：HDF5 数据写出（经 Python/h5py 桥接）
- **WindowData**：检测窗口数据读取（经 Python/numpy 桥接）

#### Scenario: 数据 I/O 算子经桥接加载
- **WHEN** Python 侧注册数据源回调并提供 numpy 数据
- **THEN** C++ 层 Forward 从桥接取数成功，输出 Blob 与提供的 numpy 一致

### Requirement: CuDNN 包装层决策记录
系统 SHALL **不实现** CuDNN\* 包装层（10 种），并在差距分析报告中记录理由：CuDNN 层为 GPU 加速包装层，caffe-ffi 为纯 CPU 引擎，实现无意义。

### Requirement: 单元测试全覆盖
系统 SHALL 为每个新增算子提供并行单元测试，覆盖：forward 数值正确性、backward 数值梯度、proto 序列化 round-trip、边界分支（如 Upsample 各 scale、ContrastiveLoss 的 margin、数据层各参数）。

#### Scenario: 数值梯度测试通过
- **WHEN** 运行各算子数值梯度测试
- **THEN** 使用 `avoid_c1_discontinuity` 处理拐点后梯度误差低于阈值

## MODIFIED Requirements

### Requirement: 算子覆盖率统计更新
[gap_analysis_report.md](file:///d:/spaces/SpecWeave/.trae/specs/caffex-vs-caffe-ffi-gap-analysis/gap_analysis_report.md) 的 P2 缺失清单、算子覆盖率、Proto 参数数量、路线图与行动项 SHALL 同步更新；CuDNN 包装层保持"不实现"并记录理由。

### Requirement: 数据层定位调整
原报告将数据输入层标记为"推理引擎通常不需要"，现因 P2 补齐而调整：数据层经 Python/numpy 桥接实现，定位从"刻意不实现"改为"已实现（Python 桥接）"。

## REMOVED Requirements
无。