# caffe-ffi P1 算子补齐实现 Spec

## Why
[caffe-ffi 技术差距分析报告](file:///d:/spaces/SpecWeave/.trae/specs/caffex-vs-caffe-ffi-gap-analysis/gap_analysis_report.md) 显示 P0 算子已全部补齐（算子覆盖率 59.0%），但 P1 仍有 18 组共 **20 个**常见推理算子缺失。补齐这些算子可覆盖 Clip（MobileNet V2/V3）、Swish（EfficientNet）、ArgMax/Reduction（分类后处理）、MVN/Exp/Log（概率计算）等高频推理场景，将算子覆盖率从 59.0% 提升至 ~90%。

## What Changes
- 在 [caffe.proto](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/proto/caffe/proto/caffe.proto) 新增 16 个 P1 参数 message，并在 `LayerParameter` 注册字段
- 新增 20 个算子实现（头文件 + cpp），遵循现有 NeuronLayer/Layer 模式
- 重新生成并提交 `caffe_pb2.py`（预生成 pb2，开箱即用约定）
- 补齐各算子单元测试（forward/backward/数值梯度），遵循项目 Backward 验证工作流
- 更新 [gap_analysis_report.md](file:///d:/spaces/SpecWeave/.trae/specs/caffex-vs-caffe-ffi-gap-analysis/gap_analysis_report.md) P1 状态

## Impact
- Affected specs: `caffex-vs-caffe-ffi-gap-analysis`（P1 状态刷新）
- Affected code: `projects/xuanspace/libs/caffe-ffi/`（proto / include / src / tests / python pb2）
- 构建：proto 变更需重新编译（protoc 自动生成），pb2 需手动同步提交

## ADDED Requirements

### Requirement: P1 算子参数模型扩展
系统 SHALL 在 `caffe.proto` 中新增下列参数 message，并在 `LayerParameter` 中注册对应字段：
- `ThresholdParameter`（threshold=0）、`PowerParameter`（power=1/scale=1/shift=0）、`ClipParameter`（min/max）、`ExpParameter`（base=-1/scale=1/shift=0）、`LogParameter`（base=-1/scale=1/shift=0）、`SwishParameter`（beta=1）
- `MVNParameter`（normalize_variance=true/across_channels=false/eps=1e-9）、`ReductionParameter`（operation/axis=0/coeff=1）、`TileParameter`（axis=1/tiles=1）、`Im2colParameter`（kernel/pad/stride/dilation）
- `ArgMaxParameter`（out_max_val=true/top_k=1/axis=1）、`SPPParameter`（pyramid_height/pool）、`EmbedParameter`（num_output/input_dim/bias_term/weight_filler/bias_filler）、`BatchReindexParameter`（空）、`FilterParameter`（空）、`SigmoidCrossEntropyLossParameter`（空）

#### Scenario: proto 编译通过
- **WHEN** 修改 `caffe.proto` 后执行 CMake 构建
- **THEN** protoc 成功生成 `caffe.pb.cc/.h/caffe_pb2.py`，无字段冲突

#### Scenario: pb2 同步提交
- **WHEN** 构建完成后
- **THEN** 新生成的 `caffe_pb2.py` 同步到 `python/caffe_ffi/caffe/proto/` 并提交

### Requirement: 激活类 P1 算子（7 个）
系统 SHALL 实现并注册以下激活类算子（继承 `NeuronLayer`）：
- Threshold、Power、BNLL、Clip、Exp、Log、Swish

各算子 SHALL 实现 `Forward_cpu` 与 `Backward_cpu`，遵循数值稳定实现（如 Exp/Log 的 scale/shift 处理、Swish 的 beta），并对 C¹ 拐点（如 Threshold x=0、Clip 边界）在数值梯度测试中推离拐点。

#### Scenario: 激活算子前向数值正确
- **WHEN** 对典型输入执行 `Forward_cpu`
- **THEN** 输出与 numpy 参考实现一致（rtol=1e-5）

#### Scenario: 激活算子反向梯度正确
- **WHEN** 执行 `Backward_cpu` 并通过数值梯度测试
- **THEN** 梯度误差低于阈值（C¹ 拐点处用 `avoid_c1_discontinuity` 推离）

### Requirement: 归一化/规约/复制类 P1 算子（4 个）
系统 SHALL 实现并注册：MVN、Reduction、Tile、Im2col。
- Im2col 可作为独立层实现（复用卷积 im2col 逻辑），设计为可复用模块
- Reduction 支持 SUM/ASUM/SUMSQ/MEAN 四种操作及 axis/coeff

#### Scenario: MVN 前向正确
- **WHEN** 对输入执行 MVN 前向
- **THEN** 均值/方差归一化结果与 numpy 一致（含 normalize_variance/across_channels 分支）

### Requirement: 后处理/工具类 P1 算子（7 个）
系统 SHALL 实现并注册：ArgMax、BatchReindex、Filter、Parameter、Silence、SPP、Embed。

#### Scenario: ArgMax 输出正确
- **WHEN** 对分数张量执行 ArgMax
- **THEN** 返回 top_k 最大值的索引（含 out_max_val 分支）

### Requirement: 损失类 P1 算子（2 个）
系统 SHALL 实现并注册：SigmoidCrossEntropyLoss、EuclideanLoss（均继承损失层模式，支持 `LossParameter` 的 ignore_label/normalization）。

#### Scenario: 损失层损失与前向兼容
- **WHEN** 执行损失层前向
- **THEN** 损失输出与参考一致，且支持常规训练循环（Backward 梯度正确）

### Requirement: 单元测试全覆盖
系统 SHALL 为每个新增算子提供并行单元测试，覆盖：forward 数值正确性、backward 数值梯度、proto 序列化 round-trip、边界分支（如 Clip 裁剪、Reduction 各操作、MVN 各分支）。

#### Scenario: 数值梯度测试通过
- **WHEN** 运行各算子数值梯度测试
- **THEN** 使用 `avoid_c1_discontinuity` 处理拐点后梯度误差低于阈值

## MODIFIED Requirements

### Requirement: 算子覆盖率统计更新
[gap_analysis_report.md](file:///d:/spaces/SpecWeave/.trae/specs/caffex-vs-caffe-ffi-gap-analysis/gap_analysis_report.md) 的 P1 缺失清单、算子覆盖率（59.0% → ~90%）、Proto 参数数量、路线图与行动项 SHALL 同步更新。

## REMOVED Requirements
无。