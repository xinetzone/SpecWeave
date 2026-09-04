# caffe-ffi P1 算子补齐 - 实施计划

## [x] Task 1: Proto 参数模型扩展（16 个 message + LayerParameter 字段）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `proto/caffe/proto/caffe.proto` 新增 16 个参数 message：ThresholdParameter、PowerParameter、ClipParameter、ExpParameter、LogParameter、SwishParameter、MVNParameter、ReductionParameter、TileParameter、Im2colParameter、ArgMaxParameter、SPPParameter、EmbedParameter、BatchReindexParameter、FilterParameter、SigmoidCrossEntropyLossParameter
  - 在 `LayerParameter` 注册对应字段（使用未占用的 field number）
  - 重新生成 `caffe_pb2.py` 并同步到 `python/caffe_ffi/caffe/proto/`
- **Acceptance Criteria Addressed**: AC-1（参数模型扩展）
- **Test Requirements**:
  - `programmatic` TR-1.1: `protoc` 编译通过，无字段冲突
  - `programmatic` TR-1.2: 新 pb2 可通过 `LayerParameter` 访问所有新参数字段
  - `programmatic` TR-1.3: proto 序列化 round-trip 通过

## [x] Task 2: 激活类 P1 算子（Threshold/Power/BNLL/Clip/Exp/Log/Swish，7 个）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 每个算子实现 `include/caffe_ffi/layers/<op>_layer.hpp` + `src/caffe_ffi/layers/<op>_layer.cpp`
  - 继承 `NeuronLayer`（逐元素激活），实现 `Forward_cpu`/`Backward_cpu` + `REGISTER_LAYER_CLASS`
  - 数值稳定实现：Exp/Log 支持 base/scale/shift；Swish 支持 beta；Clip 处理 min/max 边界
  - 复刻 caffex 实现语义（阈值/幂次/BNLL 公式）
- **Acceptance Criteria Addressed**: AC-2（激活算子）
- **Test Requirements**:
  - `programmatic` TR-2.1: 各算子 forward 与 numpy 参考一致（rtol=1e-5）
  - `programmatic` TR-2.2: backward 数值梯度通过（拐点用 `avoid_c1_discontinuity`）
  - `programmatic` TR-2.3: 7 个算子均注册成功（`REGISTER_LAYER_CLASS`）

## [x] Task 3: 归一化/规约/复制类 P1 算子（MVN/Reduction/Tile/Im2col，4 个）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - MVN：均值/方差归一化，支持 normalize_variance/across_channels/eps
  - Reduction：SUM/ASUM/SUMSQ/MEAN 四种操作 + axis/coeff
  - Tile：沿 axis 复制 tiles 份
  - Im2col：独立层实现，复用卷积 im2col 逻辑（kernel/pad/stride/dilation）
- **Acceptance Criteria Addressed**: AC-3（归一化/规约/复制算子）
- **Test Requirements**:
  - `programmatic` TR-3.1: MVN 各分支（normalize_variance/across_channels）forward 正确
  - `programmatic` TR-3.2: Reduction 四种操作 forward 正确
  - `programmatic` TR-3.3: Tile/Im2col forward 正确
  - `programmatic` TR-3.4: 4 个算子均注册成功

## [x] Task 4: 后处理/工具类 P1 算子（ArgMax/BatchReindex/Filter/Parameter/Silence/SPP/Embed，7 个）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - ArgMax：top_k 索引（含 out_max_val 分支）
  - BatchReindex：按 index blob 重索引 batch
  - Filter：按 top_names 过滤 bottom
  - Parameter：可学习参数层（无 bottom，仅 top）
  - Silence：屏蔽无用 top（输出零）
  - SPP：空间金字塔池化（pyramid_height + average/max）
  - Embed：嵌入层（num_output/input_dim/bias_term + filler）
- **Acceptance Criteria Addressed**: AC-4（后处理/工具算子）
- **Test Requirements**:
  - `programmatic` TR-4.1: ArgMax top_k/out_max_val 正确
  - `programmatic` TR-4.2: Parameter/Embed 含可学习参数 blob
  - `programmatic` TR-4.3: SPP 输出形状与金字塔期望一致
  - `programmatic` TR-4.4: 7 个算子均注册成功

## [x] Task 5: 损失类 P1 算子（SigmoidCrossEntropyLoss/EuclideanLoss，2 个）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 继承损失层模式，支持 `LossParameter` 的 ignore_label/normalization
  - SigmoidCrossEntropyLoss：多标签二分类损失（数值稳定 sigmoid）
  - EuclideanLoss：回归 L2 损失
- **Acceptance Criteria Addressed**: AC-5（损失算子）
- **Test Requirements**:
  - `programmatic` TR-5.1: 损失 forward 与参考一致
  - `programmatic` TR-5.2: backward 梯度正确（支持训练循环）
  - `programmatic` TR-5.3: 2 个算子均注册成功

## [x] Task 6: 注册与构建验证（layer_factory + CMake + 编译）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 确认 20 个算子全部注册（`REGISTER_LAYER_CLASS`）
  - CMake 构建通过（含 proto 重新生成）
  - 冒烟测试：`import tvm`/`import caffe_ffi` 正常，`LayerTypeList` 含全部新算子
  - 在 py314 环境 / Docker 内执行构建与冒烟测试
- **Acceptance Criteria Addressed**: AC-6（构建验证）
- **Test Requirements**:
  - `programmatic` TR-6.1: CMake 构建零错误
  - `programmatic` TR-6.2: `caffe_ffi` 可导入，新算子可实例化
  - `programmatic` TR-6.3: 新 pb2 字段可访问

## [x] Task 7: 单元测试全覆盖（20 个算子）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 为每个算子编写 pytest 测试：forward 数值正确性、backward 数值梯度、proto round-trip、边界分支
  - 遵循项目 Backward 验证工作流（L0 烟雾→L1 手算→L2 numpy→L3 数值梯度）
  - C¹ 拐点算子用 `avoid_c1_discontinuity` 推离
- **Acceptance Criteria Addressed**: AC-7（测试覆盖）
- **Test Requirements**:
  - `programmatic` TR-7.1: 每算子核心分支 ≥ 1 个测试用例
  - `programmatic` TR-7.2: 数值梯度测试通过无回归
  - `programmatic` TR-7.3: 单元测试覆盖率 ≥ 80%

## [x] Task 8: 差距分析报告更新（P1 状态刷新）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 更新 `gap_analysis_report.md`：P1 缺失清单移除已实现算子、算子覆盖率（59.0%→91.8%）、Proto 参数数量（32→46）、路线图 Phase B 标记完成、行动项更新
- **Acceptance Criteria Addressed**: AC-8（报告同步）
- **Test Requirements**:
  - `human-judgement` TR-8.1: 报告统计与实际代码一致
  - `human-judgement` TR-8.2: 覆盖率/缺失清单/行动项同步更新

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 1]
- [Task 5] depends on [Task 1]
- [Task 6] depends on [Task 2, Task 3, Task 4, Task 5]
- [Task 7] depends on [Task 6]
- [Task 8] depends on [Task 7]
- Task 2/3/4/5 相互独立，可并行