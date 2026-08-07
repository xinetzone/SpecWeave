---
id: caffe-hub-models-comparison-test
title: Caffe 两实现（caffe-ffi / caffex）在 hub 真实模型库上的网络级综合对比测试
source: 用户指令 /spec "caffe-comprehensive-comparison-test" 重启任务 七概念编排
created: 2026-08-06
related: caffe-comprehensive-comparison-test
---

# Caffe 两实现（caffe-ffi / caffex）在 hub 真实模型库上的网络级综合对比测试 - Product Requirement Document

## Why

上一轮综合对比（`caffe-comprehensive-comparison-test`，2026-08-05）在 **caffe-ffi 自带 `networks/` 合成/预训练网络**（ResNet50/InceptionV1/MobileNetV2/AlexNet）上完成了算子级与网络级对比，并发现高优先级缺陷 **A-001**（caffe-ffi `read_net(proto, caffemodel)` 未加载真实权重，导致网络级推理输出 NaN）。

本次**重启任务**将对比主体从合成网络切换到 **hub 真实模型库**（`external/chaos/xmtools/models/hub/caffe/`，约 30 个含真实 `.caffemodel` 权重的研发模型：人脸/人手/行人/车牌/宠物检测等）。这些模型：
1. **携带真实权重**，可在网络级别验证 caffe-ffi 的 A-001 权重加载缺陷在当前版本是否已修复；
2. **算子/拓扑覆盖更广**（Convolution、Deconvolution、Eltwise、Crop、Concat、group 卷积、InnerProduct、多种激活/Pooling 等），能暴露两实现在不常见层上的真实差异；
3. 是实际部署/编译（xmnn/VTA）的模型来源，对其在 CPU 上的两实现前向一致性进行验证具有工程价值。

## What Changes

- 枚举并归一化 hub/caffe/ 下全部约 30 个含 `.caffemodel` 的模型，为每个模型确定「标准 deploy prototxt + caffemodel + 输入形状」三元组（剔除 `*_xm530v200` 等 NPU 专用 variant，采用标准 caffe 语义 prototxt）。
- 构建一套**网络级对比 harness**，可在 caffe-ffi（py314）与 caffex（origin 镜像 py310）两套环境分别运行同一模型：加载真实权重 → 固定输入前向 → 输出逐层/末端 blob 采集。
- 对每个模型在两实现下执行：**前向正确性**（有限值检查、输出形状、与 numpy/参考对比）、**权重加载验证**（核实 A-001 是否仍存在）、**性能基准**（延迟 mean/std/min/max、FPS、CPU 占用）。
- 汇聚生成**综合对比报告**（网络级），含：模型清单与环境、逐模型通过/失败状态、精度对比、性能对比、算子/拓扑差异分析、A-001 状态判定、可视化图表、异常记录与复现命令。
- 复用上一轮 test-assets 中的对比/可视化工具（`compare_ops.py`、`gen_visualization.py`、`cpu_monitor.py` 等），必要时扩展为网络级。
- **不修改**任何实现源码（caffe-ffi / caffex / hub 模型只读），测试代码与报告仅落在本 change-id 的 test-assets 与报告目录。
- 报告归档遵循项目记忆约定：规划文件仅存 `.trae/specs/<change-id>/`，最终报告归档至 `.agents/docs/retrospective/reports/insight-extraction/external-learning/`。

## Impact

- **Affected specs**: 复用并衔接 `caffe-comprehensive-comparison-test`（已完成，本任务为其网络级真实模型扩展）。
- **Affected code（只读引用，不修改实现）**:
  - `external/chaos/xmtools/models/hub/caffe/`（约 30 个真实模型，测试主体）
  - `projects/xuanspace/libs/caffe-ffi`（实现库 + `python/caffe_ffi/io.py` 加载链路）
  - `projects/xuanspace/vendor/caffe/caffex`（实现库）
  - `projects/xuanspace/vendor/caffe/docker/origin`（caffex 运行环境）
  - `apps/caffe-ffi-jupyter`（caffe-ffi 运行环境）
- **Affected specs（新增产出）**: 本 change-id 下的 `spec.md`/`tasks.md`/`checklist.md` + test-assets/ + 网络级综合对比报告。

## 环境约束（关键前提）

| 目标实现 | 运行环境 | Python | 说明 |
|---|---|---|---|
| caffe-ffi | `apps/caffe-ffi-jupyter` WSL Docker（`jupyter-ssh-base:1.1`）或本地 `py314` conda | 3.14+ | C++ 扩展 `_caffe_ffi.so` 需先 `pip install -e .`；**禁止在 py313 运行**；`KMP_DUPLICATE_LIB_OK=TRUE` |
| caffex | origin 提供的 Docker 镜像（`caffe-cpu:origin-runtime`，Ubuntu22.04） | 3.10（pycaffe） | 通过 `docker/origin/run_ops_tests.sh` / `tests/ops/` 复用运行方式 |

> 两实现横跨两套独立运行环境，报告中必须分别记录环境配置，性能对比需标注环境差异。
> hub 模型面向 NPU（xmnn/VTA）编译，本任务仅使用其标准 caffe prototxt+caffemodel 在 **CPU** 上通过 caffe-ffi/caffex 前向，不涉及 NPU 编译。

## ADDED Requirements

### Requirement: hub 模型清单与归一化（FR-0）
系统 SHALL 从 `hub/caffe/` 枚举全部含 `.caffemodel` 的模型，并为每个模型归一化出「标准 deploy prototxt + caffemodel + 输入形状」三元组，形成机器可读清单（JSON/CSV）。

#### Scenario: 模型清单生成
- **WHEN** 扫描 `hub/caffe/` 全部子目录
- **THEN** 输出模型清单：每个模型含 name、prototxt 路径、caffemodel 路径、输入 name/shape、来源 `config.toml` 字段；对 `*_xm530v200` 等 NPU variant 明确标注并选用标准 prototxt

### Requirement: 网络级对比 harness（FR-1）
系统 SHALL 提供一套可在 caffe-ffi 与 caffex 两套环境复用的网络级前向对比脚本，支持输入模型清单、固定随机种子输入、逐层/末端 blob 输出采集。

#### Scenario: 同模型跨实现采集
- **WHEN** 分别用 caffe-ffi 与 caffex 加载同一模型的同一 prototxt+caffemodel 并前向
- **THEN** 输出该模型在两实现下的输出 blob（形状 + 数值），保存为 JSON/npy，供后续对比分析

### Requirement: caffe-ffi 全模型网络级测试（FR-2）
系统 SHALL 在 py314 环境对 hub/caffe/ 全部约 30 个模型执行 caffe-ffi 网络级前向，验证权重加载、前向有限性与输出可用性。

#### Scenario: 权重加载与有限值验证
- **WHEN** 对每个模型 `read_net(prototxt, caffemodel)` 并 `net.forward()`
- **THEN** 记录：权重加载状态（conv1 权重是否真实 vs 占位）、输出是否含 NaN/Inf、输出形状是否符合输入配置

### Requirement: caffex 全模型网络级测试（FR-3）
系统 SHALL 在 origin 镜像环境对全部约 30 个模型执行 caffex 网络级前向，验证功能正确性并识别实现特性。

#### Scenario: 前向正确性记录
- **WHEN** 对每个模型 `caffe.Net(prototxt, caffemodel)` 并 `net.forward()`
- **THEN** 记录通过/失败状态、输出形状、有限值状态、加载失败原因（不支持的层/输入配置等）

### Requirement: 跨实现网络级精度对比（FR-4）
系统 SHALL 对两实现前向输出进行逐模型数值对比，计算 max_abs_error、mean_abs_error、max_rel_error、Top-K 一致率（分类类模型）与形状一致性。

#### Scenario: 精度指标计算
- **WHEN** 对每个成功加载的模型比对两实现输出 blob
- **THEN** 输出逐模型精度指标并判定一致/不一致（容差内一致 / 数值差异 / 形状不一致 / 一方失败）

### Requirement: A-001 权重加载缺陷验证（FR-5）
系统 SHALL 在真实 hub 模型上验证 A-001（caffe-ffi 未加载 caffemodel 真实权重）在当前 caffe-ffi 版本是否已修复，并产出明确结论。

#### Scenario: A-001 现网判定
- **WHEN** 对至少 1 个带真实权重的模型（如 resnet50_caffe 或 head）比对 caffe-ffi 与 caffex 的 conv1 权重统计
- **THEN** 输出 A-001 状态：已修复 / 仍存在（附证据：权重 std、逐层 max-abs 放大链、输出 NaN 与否）

### Requirement: 性能与资源占用基准（FR-6）
系统 SHALL 对成功加载的模型在两实现下测量推理延迟（mean/std/min/max ms）与 FPS，并采集 CPU 占用；GPU 如可用则记录。

#### Scenario: 网络级性能采集
- **WHEN** 对每个模型预热后运行多次
- **THEN** 输出延迟统计、推算 FPS、CPU 占用（平均/峰值），并标注环境差异

### Requirement: 可视化与报告生成（FR-7）
系统 SHALL 生成网络级综合对比报告，含：模型清单与环境、逐模型通过/失败状态、精度对比、性能对比、算子/拓扑差异分析、A-001 判定、可视化图表、异常记录与复现命令。

#### Scenario: 报告结构与图表
- **WHEN** 报告生成完成
- **THEN** 包含：①标题/环境 ②执行摘要（全模型通过/失败/跳过统计）③逐模型精度对比表 ④逐模型性能对比表 ⑤算子/拓扑差异分析 ⑥可视化图表（性能柱状图、精度误差图、通过率）⑦异常记录与问题定位建议 ⑧复现命令附录

## MODIFIED Requirements

（无既有需求被修改；本 change-id 为 hub 真实模型库的网络级扩展任务）

## REMOVED Requirements

（无）

## Open Questions
- [ ] hub 部分模型输入为 GRAY/uint8 且针对 NPU 预处理（mean/std），网络级对比采用固定随机 float32 输入是否合适，还是应加载 demo 图并做相应预处理；需在 FR-1 harness 中统一约定。
- [ ] 部分模型存在多个 prototxt variant（如 `*_xm530v200`、`org`、`sigmoid`、`deploy`），选用标准 prototxt 的判定规则需在 FR-0 中明确并人工复核。
- [ ] caffex 对含 Deconvolution/Crop 等层的模型是否全部支持，需在 FR-3 中记录加载失败清单。