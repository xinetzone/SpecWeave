# xmnn 未完成模型失败原因分析报告 Spec

## Why
上一轮任务（`xmnn-repackage-docker-model-validation`）已完成了 54 个模型的精度测试与基线对比，但仍有 6 个模型未能产出有效精度结果（`debug/caffe_demo`、`debug/yolov5ns`、`debug/yolov5ns2`、`tests/whisper`、`tests/whisper2`、`tests/whisper2_sim`）。这些模型代表不同的失败模式（编译/推理/精度解析/超时），需要一份**具体的失败原因分析报告**，明确每个模型的失败根因、证据链、影响范围与后续处置建议，供研发团队针对性修复。

## What Changes
- 基于 `xmnn:1.2.1-new` 容器内的实际日志与产物，对 6 个失败模型逐一做根因分析
- 按失败模式分类（编译算子缺失 / 静态推理崩溃 / 精度 watch_ops 映射不匹配 / 推理超时挂起）
- 生成一份结构化失败原因分析报告，含每个模型的：失败现象、根因、证据（日志/退出码/堆栈）、影响与处置建议
- 报告与既有 `xmnn-repackage-docker-model-validation-report.md` 的 §7 相互印证但更深入

## Impact
- Affected specs: `xmnn-repackage-docker-model-validation`（既有报告 §7 的细化）
- Affected code: 无（纯分析报告，不改动 xmnn 代码）
- 产出物：`external/chaos/xmtools/build/xmnn-failure-models-analysis-report.md`

## ADDED Requirements

### Requirement: 生成失败原因分析报告
系统 SHALL 对 6 个未完成模型逐一生成失败原因分析，产出结构化 Markdown 报告。

#### Scenario: 成功分析全部 6 个模型
- **WHEN** 查阅 `xmnn:1.2.1-new` 容器内各模型的 accuracy_logs / temp 产物 / 退出码
- **THEN** 报告包含 6 个模型各自的失败现象、根因、证据链、影响与处置建议

#### Scenario: 证据不足
- **WHEN** 某模型的日志或产物缺失
- **THEN** 报告中明确标注"证据不足以判定根因"，并给出需补充的检查项

### Requirement: 报告符合方法论分析规范
系统 SHALL 采用七概念方法论（问题解决场景 I→F→V→C）组织分析，确保根因有证据支撑、结论可证伪。

#### Scenario: 根因验证
- **WHEN** 报告给出每个模型的根因结论
- **THEN** 结论引用具体日志行/退出码/堆栈作为证据，且对"是否新 wheel 回归"给出明确判定

## MODIFIED Requirements
无。

## REMOVED Requirements
无。

## 执行状态（2026-08-06 更新）

**P1 已完成**：在 `npuusertools/xmnn/op_registration.py` 的 `_SPECIAL_ALIASES` 注册 `VTA_TOPI_rmsnorm -> VTA_TOPI_layernorm`，重建 wheel 并闭环验证（`network.xmnn` 解析成功，`未知算子`错误消除）。

**新暴露缺陷（已文档化，待 P2 处置）**：P1 修复后，`debug/caffe_demo` 精度测试推进至浮点参考 TVM 编译阶段，报 `conv2d_NCHWc Invalid Schedule`（`npu_tvm/src/te/schedule/bound.cc:175`）。该缺陷为模型特有（relay 含 relu 自乘结构）+ 既有（与基线 `xmnn:1.2.1-alpha` 一致），非新回归。已写入 `xmtools/build/xmnn-failure-models-analysis-report.md` §3.1 / §4 / §5。