# caffe-ffi P1 算子补齐 - 验证检查清单

## Proto 参数模型
- [x] 16 个参数 message 已新增（Threshold/Power/Clip/Exp/Log/Swish/MVN/Reduction/Tile/Im2col/ArgMax/SPP/Embed/BatchReindex/Filter/SigmoidCrossEntropyLoss）
- [x] LayerParameter 已注册全部新字段（field number 无冲突）
- [x] protoc 编译通过，重新生成 caffe.pb.cc/.h/caffe_pb2.py
- [x] caffe_pb2.py 已同步到 `python/caffe_ffi/caffe/proto/` 并提交
- [x] 新 pb2 可通过 LayerParameter 访问所有新参数字段
- [x] proto 序列化 round-trip 通过

## Task 2: 激活类算子（7 个）
- [x] Threshold：forward/backward 实现，×0 拐点数值梯度处理
- [x] Power：power/scale/shift 前向正确
- [x] BNLL：forward/backward 实现
- [x] Clip：min/max 裁剪边界处理
- [x] Exp：base/scale/shift 支持
- [x] Log：base/scale/shift 支持
- [x] Swish：beta 支持
- [x] 7 个算子均 `REGISTER_LAYER_CLASS` 注册成功
- [x] 各算子 forward 与 numpy 参考一致（rtol=1e-5）
- [x] 各算子 backward 数值梯度通过（拐点推离）

## Task 3: 归一化/规约/复制算子（4 个）
- [x] MVN：normalize_variance/across_channels 分支正确
- [x] Reduction：SUM/ASUM/SUMSQ/MEAN 四种操作正确
- [x] Tile：沿 axis 复制 tiles 份正确
- [x] Im2col：kernel/pad/stride/dilation 正确
- [x] 4 个算子均注册成功

## Task 4: 后处理/工具算子（7 个）
- [x] ArgMax：top_k/out_max_val 分支正确
- [x] BatchReindex：按 index 重索引正确
- [x] Filter：按 top_names 过滤正确
- [x] Parameter：可学习参数 blob 正确
- [x] Silence：屏蔽输出正确
- [x] SPP：金字塔输出形状正确
- [x] Embed：含 weight/bias 参数 blob
- [x] 7 个算子均注册成功

## Task 5: 损失算子（2 个）
- [x] SigmoidCrossEntropyLoss：数值稳定 sigmoid，forward/backward 正确
- [x] EuclideanLoss：L2 回归损失 forward/backward 正确
- [x] 支持 LossParameter ignore_label/normalization
- [x] 2 个算子均注册成功

## Task 6: 构建验证
- [x] CMake 构建零错误（含 proto 重新生成）
- [x] `import caffe_ffi` 在 py314 环境正常
- [x] LayerTypeList 含全部 20 个新算子
- [x] 新算子可实例化（layer_factory 创建）

## Task 7: 单元测试
- [x] 20 个算子均有 forward/backward 测试
- [x] 数值梯度测试通过无回归
- [x] 单元测试覆盖率 ≥ 80%
- [x] C¹ 拐点算子使用 avoid_c1_discontinuity

## Task 8: 报告更新
- [x] gap_analysis_report.md P1 缺失清单移除已实现算子
- [x] 算子覆盖率更新至 ~91.8%
- [x] Proto 参数数量更新至 46
- [x] 路线图 Phase B 标记完成，行动项更新

## 质量门
- [x] G1 事实：实现对象与报告 P1 清单一一对应
- [x] G2 洞察：算子语义与 caffex 参考实现一致
- [x] G3 迁移：每个算子可独立验证（测试覆盖）