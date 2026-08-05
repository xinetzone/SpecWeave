# caffe-ffi 后续修复与分析 Spec

## Why

在完成 caffe-ffi / caffex 综合对比测试后，暴露了 4 项需跟进的问题：
1. caffe-ffi 的 protobuf 协议与 BVLC 标准字段命名/编号偏离，导致含标准 `Normalize` 层（`norm_param`）的 Caffe 模型无法解析。
2. 对比测试发现高优先级缺陷 A-001：`read_net` 未加载 caffemodel 真实权重，导致网络级推理输出垃圾值/NaN，需制定并实施修复方案。
3. 性能基准数据显示 caffe-ffi 在部分算子（eltwise_sum / pooling / inner_product）上落后 caffex 4~14 倍，需系统分析瓶颈。
4. Top-K 分类一致性数据已产出，需导出为 CSV 便于后续详细分析。

## What Changes

- **修复 caffe-ffi protobuf 对标准 `norm_param` 的兼容**：在 `LayerParameter` 中支持 BVLC 标准 `NormalizeParameter`（`norm_param`），使含 Normalize 层的模型可解析。
- **修复 A-001（`read_net` 权重加载）**：定位并修复 `read_net` 未写入 caffemodel 真实权重的问题，网络级推理输出与 caffex 对齐。
- **产出性能瓶颈分析**：基于 `bench_caffe_ffi.json` / `bench_caffex.json` 数据，量化 caffe-ffi 各算子延迟/FPS 差距，定位最严重瓶颈并给出优化建议。
- **导出 Top-K 数据为 CSV**：将 `topk_caffe_ffi.json` / `topk_caffex.json` 汇总为结构化 CSV。

## Impact

- Affected specs：
  - `caffe-comprehensive-comparison-test`（A-001 缺陷来源、性能/精度数据来源）
  - `caffeproto-l2-normalize`（Normalize 协议参考背景）
- Affected code：
  - `projects/xuanspace/libs/caffe-ffi/proto/caffe/proto/caffe.proto`（norm_param 兼容）
  - `projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/`（`read_net` 权重加载）
  - `projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/caffe_pb2.py`（重新生成）
- 交付物：性能瓶颈分析报告、`topk_comparison.csv`

> 注意：`projects/xuanspace/libs/caffe-ffi` 为 git submodule，直接修改需遵循子项目流程（本 spec 以修复方案 + 变更落地为主，提交由子项目流程负责）。

## ADDED Requirements

### Requirement: 支持标准 norm_param 协议（RQ-1）
caffe-ffi 的 `LayerParameter` SHALL 支持解析 BVLC 标准 `norm_param`（`NormalizeParameter`）字段，使含 Normalize 层的模型能被 `caffe_ffi` 正确解析，同时保持已有 `l2_norm_param`（158）向后兼容。

#### Scenario: 解析含 Normalize 层的模型
- **WHEN** 用户用 `caffe_ffi` 解析一个含 `norm_param { ... }` 的 Caffe prototxt/caffemodel
- **THEN** 解析成功，不抛出 `Wire format`/未知字段错误，Normalize 层参数可被读取

#### Scenario: 向后兼容
- **WHEN** 已有使用 `l2_norm_param`（158）的模型仍被解析
- **THEN** 行为不变，不破坏现有字段编号的既有使用

### Requirement: 修复 A-001 read_net 权重加载（RQ-2）
`read_net(proto, caffemodel)` SHALL 将 caffemodel 中的真实权重写入网络各层，使网络级前向输出与 caffex 使用同一 caffemodel 的结果对齐（不再为占位权重/NaN）。

#### Scenario: 网络级推理正确性
- **WHEN** 用 `read_net` 加载预训练 caffemodel 并对固定输入推理
- **THEN** conv1 权重为真实值（非全 1.0/std=0），输出无 Inf/NaN，与 caffex 结果一致（精度容差内）

### Requirement: 性能瓶颈分析（RQ-3）
基于已有基准数据，分析 caffe-ffi 各算子的延迟（mean_ms）、FPS、与 caffex 的比值及延迟方差，产能出按严重程度排序的瓶颈清单与优化建议。

#### Scenario: 瓶颈排序
- **WHEN** 分析 `bench_caffe_ffi.json` / `bench_caffex.json`
- **THEN** 产出按比值/绝对延迟排序的算子清单，标注最严重瓶颈（预期 eltwise_sum / pooling / inner_product）及高方差算子

### Requirement: Top-K 数据 CSV 导出（RQ-4）
将两实现的 Top-K 分类一致性结果汇总导出为结构化 CSV，字段清晰、可被常见表格工具打开。

#### Scenario: CSV 可用性
- **WHEN** 用 pandas/Excel 打开 `topk_comparison.csv`
- **THEN** 每行一条实现记录，含 impl / model / output_shape / top1 / top5 / probs_top5 / has_nan / has_inf / score_max / ok 字段，数据与 JSON 结果一致

### Requirement: 容器内 A-001 编译+验证脚本（RQ-2b）
提供在 `caffe-ffi-jupyter` 容器内一键执行 native 编译与 A-001 修复后验证的脚本，形成「重编译 → 验证」闭环。

#### Scenario: 一键执行编译+验证
- **WHEN** 用户在容器内运行该脚本
- **THEN** 依次装载 env、重编译 `_caffe_ffi.so`（含本地 tvm-ffi）、运行 `a001_verify_fix.py`，输出 conv1 权重真实、无 NaN、与 caffex 对齐的验证结果

### Requirement: eltwise_sum / pooling OpenMP 并行优化示例（RQ-3b）
针对 `eltwise_sum`（14.46x）与 `pooling`（11.14x）两大瓶颈，提供可直接落地的 OpenMP 并行优化 C++ 代码示例。

#### Scenario: 优化示例可落地
- **WHEN** 开发者按示例修改 EltwiseLayer / PoolingLayer 并启用 `CAFFE_FFI_ENABLE_OPENMP`
- **THEN** 示例具备正确并行维度（无数据竞争）、预分配缓冲复用、构建配置与线程数控制说明

### Requirement: norm_param 字段编号差异解释（RQ-1b）
解释 caffe-ffi 的 `norm_param` 字段编号 190 与 BVLC/caffex 标准 149 的差异，及其对文本/二进制模型解析的兼容性影响。

#### Scenario: 解释完整
- **WHEN** 用户询问字段编号差异与二进制兼容性
- **THEN** 产出含编号设计逻辑、文本 prototxt 与二进制 caffemodel 兼容性分析、规避建议的说明

## MODIFIED Requirements

（无既有需求被修改；本 spec 为新增跟进需求。）

## REMOVED Requirements

（无。）