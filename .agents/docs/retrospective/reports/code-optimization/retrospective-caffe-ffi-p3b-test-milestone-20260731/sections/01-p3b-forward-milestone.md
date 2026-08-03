---
title: P3-B Forward测试里程碑（7层全覆盖）
date: 2026-07-31
category: code-optimization
task_type: testing
tags: [caffe-ffi, forward, p3b, eltwise, scale, bias, concat, dropout, softmaxwithloss, accuracy]
status: completed
verification: passed
source: "retrospective-caffe-ffi-p3b-test-milestone-20260731/README.md#s1"
---

# P3-B Forward测试里程碑

## 任务概览

| 项目 | 内容 |
|------|------|
| 里程碑 | P3-B：7个基础层Forward全覆盖 |
| 原始目标 | 覆盖RNN/LSTM层的真实forward逻辑（后调整） |
| 调整后目标 | 测试已实现但覆盖不足的7个层 |
| 方法论 | numpy参考实现对比 + prototxt网络构建 + perf_trace性能采集 |
| 结果 | ✅ 50个测试全部通过，118个已有测试无回归 |

## 产出物统计

| 指标 | 数值 |
|------|------|
| 新增测试文件 | test_p3b_eltwise_scale.py（1224行） |
| 测试用例总数 | 50个 |
| 测试类数 | 8个 |
| numpy参考函数 | 7个（scale/bias/eltwise/concat/softmax/softmax_loss/accuracy） |
| 覆盖层数 | 7个（Scale/Bias/Eltwise/Concat/Dropout/SoftmaxWithLoss/Accuracy） |
| P3-B通过率 | 50/50 (100%) |
| 回归通过率 | 118/118 (100%) |

## 各层测试覆盖

| 层 | 测试类 | 用例数 | 覆盖场景 |
|---|---|---|---|
| Scale | TestScaleLayers | 6 | identity/per-channel/bias/axis0/repeated/weights不变性 |
| Bias | TestBiasLayers | 6 | zero/per-channel/known/axis0/repeated/weights不变性 |
| Eltwise | TestEltwiseLayers | 9 | SUM/PROD/MAX/coeffs/三输入/已知值/repeated |
| Concat | TestConcatLayers | 6 | axis=0/1/2/三输入/已知值/repeated |
| Dropout | TestDropoutLayers | 6 | 推理identity(ratio=0/0.5/0.9)/1D/特殊值/repeated |
| SoftmaxWithLoss | TestSoftmaxWithLossLayers | 6 | perfect/uniform/numpy/probs/repeated |
| Accuracy | TestAccuracyLayers | 7 | perfect/zero/partial/top-k/spatial/numpy/repeated |
| 组合 | TestScaleBiasEltwiseCombination | 4 | Scale→Bias/Eltwise→Scale/分类全链路/20轮稳定性 |

## Bug修复记录

### Bug #1：Blob单消费模型导致"Unknown bottom blob"

- **现象**：同一net中多个Eltwise层共享bottom blob时，第一个消费后blob被移除，后续报Unknown bottom blob
- **根因**：net.cpp中`available_blobs->erase(blob_name)`在AppendBottom时立即删除，caffe-ffi采用严格single-consumer模型
- **修复**：三个Eltwise操作拆分为三个独立net
- **教训**：caffe-ffi与标准Caffe行为差异——必须显式Split处理多消费者

### Bug #2：Accuracy spatial期望值误算

- **现象**：断言准确率0.5，实际输出0.625
- **根因**：手动标记"4个正确"计数错误（实际5个）
- **修复**：逐位置核对，期望值改为5/8=0.625
- **教训**：部分正确测试数据必须逐元素标注

### Bug #3：分类全链路双消费者Split缺失

- **现象**：SoftmaxWithLoss消费score和label后，Accuracy报Unknown bottom blob
- **根因**：score需同时喂给Loss和Accuracy，同Bug #1
- **修复**：添加split_score和split_label两个Split层
- **教训**：任何被多layer消费的blob必须显式Split

### 性能优化（ACT-04）

P3-B测试从134s优化至8.27s（16.2x加速），详见[性能优化专题](#)（已沉淀为独立最佳实践）。

## 可复用模式沉淀

5个模式已萃取入库：numpy-reference-first、three-layer-test-validation、explicit-split-multi-consumer、perf-trace-instrumentation、separate-nets-independent-ops。

详见 [09-insights-patterns.md](09-insights-patterns.md)。

## 提交记录

| 提交 | 内容 |
|------|------|
| d1acc7b | test(p3b): 新增Scale/Bias/Eltwise/Concat/Dropout/SoftmaxWithLoss/Accuracy层P3-B测试（50用例） |
