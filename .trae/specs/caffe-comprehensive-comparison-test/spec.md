---
id: caffe-comprehensive-comparison-test
title: Caffe 三实现综合对比测试与标准化报告生成
source: 用户指令 /spec "/spec" 七概念编排
created: 2026-08-05
---

# Caffe 两实现（caffe-ffi / caffex）综合对比测试与标准化报告生成 - Product Requirement Document

## Why

需要对 Caffe 生态中的两套实现进行系统性验证与对比，为选型与质量基线提供可审计的数据支撑：

1. **caffe-ffi**（`projects/xuanspace/libs/caffe-ffi`，tvm-ffi 原生 FFI 绑定，Python 3.14+）—— 验证接口完整性、调用稳定性与功能正确性。
2. **caffex**（`projects/xuanspace/vendor/caffe/caffex`，优化实现）—— 在 **origin 提供的 Docker 镜像环境**（`projects/xuanspace/vendor/caffe/docker/origin`，`caffe-cpu:origin-runtime`）中运行，验证功能一致性与实现差异性。
3. 在多种常用算子（卷积/池化/激活等）与典型网络模型（ResNet/VGG/MobileNet 等）上对 **caffe-ffi 与 caffex 两套实现** 执行系统性测试，产出精度、性能、资源占用、差异分析与可视化图表的综合报告。

> **概念澄清**：`origin` 不是第三套独立实现，而是为 caffex 提供 Docker 镜像运行环境（含 Dockerfile/构建与运行脚本）。本任务的对比主体是 **caffe-ffi ⟷ caffex 两套实现**。

## What Changes

- 设计并执行一套**可复现**的**两实现综合对比测试方案**（caffe-ffi ⟷ caffex），覆盖算子正确性、网络级前向、精度指标、性能指标与资源占用。
- 产出**标准化综合测试报告**，包含：环境配置、精度对比（绝对误差/相对误差/Top-K 准确率）、性能对比（FPS/延迟/CPU/GPU 占用）、算子与网络差异分析、可视化图表、异常记录与问题定位建议。
- 复用之仓库既有测试资产：caffe-ffi 的 `tests/python/`（含 `networks/` 网络测试）、`apps/caffe-ffi-jupyter` 测试环境、caffex 的 `tests/ops/`、origin 的 `docker/origin` 运行脚本与 `run_ops_tests.sh`（caffex 的运行环境）。
- **不修改**任何实现源码（caffex/ 与 caffe-ffi/ 只读），测试代码与报告仅落在测试资产与报告目录。
- 报告归档遵循项目记忆约定：规划文件仅存 `.trae/specs/<theme>/<project>/`，最终分析产出归档至 `.agents/docs/retrospective/reports/insight-extraction/external-learning/`。

## Impact

- **Affected specs**: 复用并衔接 `caffex-ops-comprehensive-test`（已完成的算子测试）、`caffe-network-tests-integration`、`caffe-network-tests-migrate-to-caffe-ffi`（网络测试迁移）。
- **Affected code（只读引用，不修改实现）**:
  - `projects/xuanspace/libs/caffe-ffi`（实现库 + `tests/python/` + `scripts/`）
  - `projects/xuanspace/vendor/caffe/caffex`（实现库 + `tests/ops/`）
  - `projects/xuanspace/vendor/caffe/docker/origin`（caffex 的 Docker 镜像运行环境）
  - `apps/caffe-ffi-jupyter`（caffe-ffi 测试环境，image `jupyter-ssh-base:1.1`）
- **Affected specs（新增产出）**: 本 change-id 下的 `spec.md`/`tasks.md`/`checklist.md` + 综合测试报告。

## 环境约束（关键前提）

| 目标实现 | 运行环境 | Python | 说明 |
|---|---|---|---|
| caffe-ffi | `apps/caffe-ffi-jupyter` WSL Docker（`jupyter-ssh-base:1.1`）或本地 `py314` conda | 3.14+ | C++ 扩展 `_caffe_ffi.so`，需先 `pip install -e .`；**禁止在 py313 运行** |
| caffex | **origin 提供的 Docker 镜像**（`caffe-cpu:origin-runtime`，Ubuntu22.04） | 3.10 | 通过 `docker/origin/run_ops_tests.sh` / `tests/ops/` 运行 |

> 两实现横跨两套独立运行环境（caffe-ffi 在 py314，caffex 在 origin 镜像 py310），报告中必须分别记录环境配置，对比时需在结论中明确标注环境差异对性能数据的影响。

## ADDED Requirements

### Requirement: 测试方案设计（FR-0）
系统 SHALL 提供一份可复现的三实现综合对比测试方案，明确测试矩阵（算子清单、网络清单、输入形状、随机种子）、执行命令与预期输出路径。

#### Scenario: 测试矩阵确定
- **WHEN** 执行对比测试
- **THEN** 测试矩阵包含：≥10 个常用算子（卷积/池化/激活/全连接/Softmax/归一化等）与 ≥3 个典型网络（ResNet-50、VGG16、MobileNet 等，复用 caffe-ffi `networks/` 已有资源）

### Requirement: caffe-ffi 功能测试（FR-1）
系统 SHALL 在 py314 环境（`apps/caffe-ffi-jupyter` 或本地 py314）中对 caffe-ffi 执行功能测试，验证接口完整性、调用稳定性与功能正确性。

#### Scenario: 接口与稳定性验证
- **WHEN** 在 py314 环境运行 caffe-ffi 测试套件（`tests/python/`）
- **THEN** 记录通过/失败/跳过用例数，验证 `import caffe_ffi`、`read_net`、`net.forward()` 等核心接口可用，C++ 扩展 `_caffe_ffi.so` 正常加载

### Requirement: caffex 功能测试（FR-2）
系统 SHALL 在 origin 提供的 Docker 镜像环境中运行 caffex 算子测试，验证功能正确性，并识别其实现特性（与 caffe-ffi 的差异性来源）。

#### Scenario: 功能正确性与实现特性识别
- **WHEN** 在 origin 镜像环境运行 caffex `tests/ops/`
- **THEN** 记录算子级通过率、与 numpy 参考的数值偏差；标注实现特性（如 COW 恒等、dtype、形状语义、Backward 行为），作为 vs caffe-ffi 差异分析的依据

### Requirement: 跨实现算子精度对比（FR-3）
系统 SHALL 对 caffe-ffi 与 caffex 在相同输入/权重下输出数值进行对比，计算绝对误差、相对误差与 Top-K 准确率。

#### Scenario: 精度指标计算
- **WHEN** 对每个算子用相同随机输入与固定权重分别经 caffe-ffi 与 caffex 前向
- **THEN** 输出 max_abs_error、mean_abs_error、max_rel_error、Top-1/Top-5 一致率，并保存逐算子结果

### Requirement: 性能对比（FR-4）
系统 SHALL 测量各实现算子在标准输入形状下的推理性能，记录吞吐量（FPS）、单次延迟（ms）与 CPU/GPU 资源占用率。

#### Scenario: 性能基准采集
- **WHEN** 对每个算子/网络预热后运行多次
- **THEN** 输出 mean/std/min/max 延迟、推算 FPS、资源占用（CPU 时间/内存、GPU 如可用），并标注环境差异

### Requirement: 可视化与报告生成（FR-5）
系统 SHALL 生成综合测试报告，含各测试项配置、精度数据、性能数据、差异分析、可视化图表与异常记录。图表须为本地离线可渲染（优先 ECharts HTML 或 matplotlib PNG）。

#### Scenario: 报告结构与图表
- **WHEN** 报告生成完成
- **THEN** 包含：①②标题/环境信息、③精度对比表、④性能对比表、⑤算子/网络差异分析、⑥可视化图表（性能柱状图、精度误差图）、⑦异常记录与问题定位建议、⑧复现命令附录

## MODIFIED Requirements
（无既有需求被修改；本 change-id 为新增综合对比测试任务）

## REMOVED Requirements
（无）

## Open Questions
- [ ] 是否已有可用的 caffe 模型权重（.caffemodel）用于网络级精度对比？caffe-ffi `networks/` 测试使用在线下载，需确认网络可达性；caffex 侧是否具备等价网络测试入口。
- [ ] 性能资源占用（CPU/GPU）的采集在 Docker 容器内的可行性与工具（如 `psutil`/`nvidia-smi`）是否需要新增依赖。
- [ ] 报告最终归档路径：遵循项目记忆约定归档至 `.agents/docs/retrospective/reports/insight-extraction/external-learning/`，需确认目录是否存在。