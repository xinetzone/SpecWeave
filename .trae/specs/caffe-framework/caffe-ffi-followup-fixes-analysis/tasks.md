# caffe-ffi 后续修复与分析 - 可验证任务清单

## [x] Task 1: 支持标准 norm_param 协议（RQ-1）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 核查 caffe-ffi `caffe.proto` 与 BVLC/caffex 标准的字段差异（已知：caffe-ffi 用 `l2_norm_param=158`，BVLC 用 `norm_param=149`；且下落编号不同，如 dropout_param）。
  - 设计兼容方案：优先复用/重命名已有 L2NormParameter 为 `norm_param`，或新增 `norm_param` 消息字段，确保标准 Normalize 模型可解析且不破坏既有 `l2_norm_param` 使用。
  - 更新 `proto/caffe/proto/caffe.proto` 并重新生成 `caffe_pb2.py`。
  - 编写/复用解析测试：解析含 `norm_param { ... }` 的 prototxt，断言不报错、参数可读。
- **Acceptance**: RQ-1 两场景通过（含 Normalize 模型可解析；`l2_norm_param` 向后兼容）。
- **验证**: `programmatic` — 解析测试通过；`human-judgement` — 兼容方案合理性。

## [x] Task 2: 修复 A-001 read_net 权重加载（RQ-2）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 定位 `io.py::read_net` → `_merge_weights` → `caffe_ffi.NewNetFromProtoString` 链路，确认 C++ 端是否读取 `layer.blobs[].data` 并写入层权重。
  - 制定修复方案（写入真实权重；校验权重形状与层参数匹配）。
  - 落地修复并重新编译 native 扩展（如涉及 C++）。
  - 用预训练 caffemodel（如 InceptionV1）验证：conv1 权重真实、输出无 NaN、与 caffex 结果对齐。
- **Acceptance**: RQ-2 场景通过（权重真实、无 NaN、与 caffex 对齐）。
- **验证**: `programmatic` — 网络级推理测试；`human-judgement` — 修复方案文档。

## [x] Task 3: 性能瓶颈分析（RQ-3）
- **Priority**: medium
- **Depends On**: None（基于已有 bench JSON）
- **Description**:
  - 读取 `test-assets/results/bench_caffe_ffi.json` 与 `bench_caffex.json`。
  - 计算每算子比值（ffi/cx mean_ms）、绝对延迟、FPS 差距、延迟 std/方差。
  - 按严重程度（比值 × 绝对延迟）排序，定位最严重瓶颈（预期 eltwise_sum / pooling / inner_product）与高方差算子。
  - 产能出瓶颈分析报告（含优化建议，如算子级并行、FFI 边界开销、长尾分配/GC）。
- **Acceptance**: RQ-3 场景通过（瓶颈清单按严重程度排序，含高方差标注与建议）。
- **验证**: `human-judgement` — 分析结论与数据一致；`programmatic` — 分析脚本/报告产出。

## [x] Task 4: Top-K 数据 CSV 导出（RQ-4）
- **Priority**: low
- **Depends On**: None（基于已有 topk JSON）
- **Description**:
  - 读取 `test-assets/results/topk_caffe_ffi.json` 与 `topk_caffex.json`。
  - 导出 `topk_comparison.csv`，字段：impl / model / output_blob / output_shape / top1 / top5 / probs_top5 / has_nan / has_inf / score_max / ok。
- **Acceptance**: RQ-4 场景通过（CSV 可被 pandas/Excel 打开，数据与 JSON 一致）。
- **验证**: `programmatic` — CSV 存在且字段完整、数值与 JSON 一致。

## [x] Task 5: 容器内 native 编译 + A-001 验证脚本（RQ-2b）
- **Priority**: high
- **Depends On**: Task 2（A-001 修复代码已落地 net.cpp）
- **Description**:
  - 生成在 `caffe-ffi-jupyter` 容器内自动执行 native 编译 + A-001 修复后验证的脚本。
  - 覆盖：装载 conda env（caffe-ffi / Python 3.14）→ 定位本地 tvm-ffi 源码 → `pip install -e . --no-build-isolation` 重编译 `_caffe_ffi.so` → 运行 `a001_verify_fix.py`（conv1 权重真实、无 NaN、与 caffex 对齐）。
  - 脚本需幂等、可重入，失败时输出明确错误与退出码。
- **Acceptance**: RQ-2b 场景通过（脚本在容器内可一键执行编译+验证闭环）。
- **验证**: `programmatic` — 脚本语法/路径正确、命令可执行；`human-judgement` — 覆盖完整编译+验证链路。

## [x] Task 6: eltwise_sum / pooling OpenMP 并行优化代码示例（RQ-3b）
- **Priority**: medium
- **Depends On**: None（基于 perf-bottleneck-analysis.md 结论）
- **Description**:
  - 针对 `eltwise_sum`（14.46x）与 `pooling`（11.14x）两大严重瓶颈，给出引入 OpenMP 并行优化的具体 C++ 代码示例。
  - 覆盖：`#pragma omp parallel for` 并行维度选取（eltwise 输出块切分 / pooling batch×通道 collapse）、预分配缓冲区复用、对齐 `CAFFE_FFI_ENABLE_OPENMP` 构建选项、线程数/环境变量控制。
  - 代码示例基于 caffe-ffi 现有层实现（EltwiseLayer / PoolingLayer），标注改动点与预期收益。
- **Acceptance**: RQ-3b 场景通过（代码示例可直接落地到对应层实现，具备并行维度与构建配置说明）。
- **验证**: `human-judgement` — 示例与现有实现匹配、并行维度正确无数据竞争；`programmatic` — 示例可编译性或语法校验。

## [x] Task 7: 解释 norm_param 字段编号 190 vs 149 及二进制兼容性（RQ-1b）
- **Priority**: low
- **Depends On**: Task 1（norm_param 协议支持已确认）
- **Description**:
  - 解释 caffe-ffi 的 `norm_param` 为何用字段编号 190 而 BVLC/caffex 标准用 149。
  - 分析字段编号差异对**文本 prototxt** 与**二进制 caffemodel** 解析的影响，给出二进制兼容性结论与规避方案。
- **Acceptance**: RQ-1b 场景通过（解释含字段编号设计逻辑 + 文本/二进制兼容性分析 + 规避建议）。
- **验证**: `human-judgement` — 解释与 proto 事实一致、结论明确。

## Task Dependencies
- Task 1 至 Task 4 相互独立，可并行执行。
- Task 2 若涉及 C++ 需重新编译，取决于环境可用性。
- Task 3 / Task 4 仅依赖既有测试结果 JSON，无代码依赖。
- **Task 5** 依赖 Task 2（A-001 修复代码）；**Task 6** 依赖 Task 3（瓶颈数据）；**Task 7** 依赖 Task 1（协议事实）。
- Task 5 / 6 / 7 三者相互独立，可并行执行。