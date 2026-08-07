# 修复 xmnn conv2d_NCHWc Invalid Schedule 缺陷 Spec

## Why

`debug/caffe_demo` 的 P1 缺陷（`VTA_TOPI_rmsnorm` 未注册）已修复并通过解析层闭环验证，但精度验证推进至浮点参考模型 TVM 编译阶段时暴露**第二层既有缺陷**：`conv2d_NCHWc Invalid Schedule`（`npu_tvm/src/te/schedule/bound.cc:175`）。该缺陷阻止 caffe_demo 达到"精度 result.csv 生成"的最终验收标准，需要按「分层修复验证法」逐层推进直至真闭环。

## What Changes

- 诊断 `conv2d_NCHWc Invalid Schedule` 根因：`bound.cc:175` 的 `ICHECK(found_attach || stage_attach.size() == 0)` 由调度构造产生，定位是哪个 pass/调度器为 `T_multiply = max(conv+p2,0) * max(conv+p2,0)` 自乘结构创建了无法找到 producer 的 `compute_at`
- 产出最小可复现用例（最小化 caffe_demo relay 图，独立触发该调度错误）
- 确定并实施修复方案（调度器/降级 pass 修正 或 relay 图结构转换，二选一，需对抗审查论证）
- 重建 xmnn wheel，重跑 caffe_demo 完整精度流水线至 `result.csv` 生成（最终验收标准）
- 全程遵循「分层修复验证法」：以最终验收标准判定闭环，逐层推进，对每一层暴露错误做「既有 or 新引入」对抗判定
- 基于已入库的 [layered-repair-verification.md](../../../.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/layered-repair-verification.md) 模板，为 `debug/caffe_demo` 生成一份完整的分层修复记录（含 L1 rmsnorm 与 L2 conv2d_NCHWc 的分层链）

## Impact

- Affected specs: [xmnn-failure-models-analysis](../xmnn-failure-models-analysis/spec.md)（P2 处置的后续落地）
- Affected code:
  - `external/chaos/npu_tvm/src/te/schedule/bound.cc`（ICHECK 触发点，诊断起点）
  - npu_tvm 调度/降级相关 pass（`schedule` / `lower` / 相关绑定逻辑）
  - 可能的 relay 图转换 pass（若选择图结构修复方案）
  - xmnn 构建脚本（wheel 重建，`external/chaos/xmtools/docker/dev-llvm22/`）
- 产出物：
  - `external/chaos/xmtools/build/` 下：最小复现用例、诊断报告、修复验证脚本
  - `debug/caffe_demo` 精度 `result.csv`（最终验收标准）
  - 分层修复记录文档（应用 layered-repair-verification 模板）

## ADDED Requirements

### Requirement: 根因诊断 conv2d_NCHWc Invalid Schedule
系统 SHALL 定位 `conv2d_NCHWc Invalid Schedule` 的根因，明确是调度器/降级 pass 的缺陷，并产出最小可复现用例。

#### Scenario: 最小复现
- **WHEN** 提取 caffe_demo 中含 `relu(conv)*relu(conv)` 自乘结构的最小 relay 片段并编译
- **THEN** 独立复现 `bound.cc:175` 的 `Invalid Schedule, cannot find the producer` 错误，且复现用例与完整模型无关

#### Scenario: 根因定位
- **WHEN** 分析调度构造链（compute_at 的 consumer/producer 关系）
- **THEN** 明确是哪一个 pass/调度步骤创建了无效的 `compute_at` 附着，结论有 `bound.cc:175` 现场与调用栈证据

### Requirement: 实施修复并达最终验收标准
系统 SHALL 修复该缺陷，重跑 caffe_demo 完整精度流水线至 `result.csv` 生成，且不引入新回归。

#### Scenario: 精度闭环
- **WHEN** 修复后重建 wheel 并重跑 caffe_demo 精度测试
- **THEN** `result.csv` 生成、指标合格，落到「真闭环」或「收敛闭环」，而非「伪闭环」（解析成功即宣告完成）

#### Scenario: 回归判定
- **WHEN** 修复推进中暴露新的下一层错误
- **THEN** 对每层做「既有 or 新引入」对抗判定（对比基线镜像 `xmnn:1.2.1-alpha`、检查路径独立性），并记录分层链

### Requirement: 生成分层修复记录
系统 SHALL 基于 layered-repair-verification 模板，为 `debug/caffe_demo` 生成完整的分层修复记录文档。

#### Scenario: 记录完整分层链
- **WHEN** 修复达到闭环或收敛后
- **THEN** 记录每一层（L1 rmsnorm 注册、L2 conv2d_NCHWc 调度）暴露的错误、根因、处置结论，标注最终落在「真闭环」或「收敛闭环」

## MODIFIED Requirements

无。

## REMOVED Requirements

无。