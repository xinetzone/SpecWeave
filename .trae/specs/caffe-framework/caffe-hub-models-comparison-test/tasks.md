# Caffe 两实现（caffe-ffi / caffex）在 hub 真实模型库上的网络级综合对比测试 - The Implementation Plan (可验证任务清单)

## [x] Task 1: hub 模型清单枚举与归一化（FR-0）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 扫描 `external/chaos/xmtools/models/hub/caffe/` 全部子目录，枚举所有含 `.caffemodel` 的模型（目标 ~30 个）。
  - 为每个模型读取 `config.toml`，归一化「标准 deploy prototxt + caffemodel + 输入 name/shape」三元组；对 `*_xm530v200`/`org`/`sigmoid`/`deploy` 等多 variant 明确判定规则并选用标准 caffe 语义 prototxt（人工复核）。
  - 生成机器可读模型清单 `models_manifest.json`（name、prototxt、caffemodel、input name/shape、来源 toml 字段、variant 标注）。
- **Acceptance**: FR-0 满足；清单覆盖全部含 caffemodel 的模型，字段完整、可被 harness 消费。
- **验证**: `programmatic` — 清单 JSON 存在且条目数 ≥ 25；`human-judgement` — prototxt 选择规则正确。

## [x] Task 2: 环境预检（caffe-ffi py314 / caffex origin）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 验证 caffe-ffi 环境（`apps/caffe-ffi-jupyter` 或本地 `py314`）：`import caffe_ffi` 通过、`_caffe_ffi.so` 可加载、`read_net` 可用；否则 `pip install -e . --no-build-isolation`。
  - 验证 caffex origin 镜像（`caffe-cpu:origin-runtime`）可用，`caffe.Net` 可加载模型。
  - 记录两环境版本（Python/numpy/caffe_ffi/caffex）。
- **Acceptance**: 两套环境可运行网络级加载；环境版本记录产出。
- **验证**: `programmatic` — 环境验证命令输出。

## [x] Task 3: 网络级对比 harness 构建（FR-1）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 编写可在两环境复用的网络级前向脚本（`run_net_forward_ffi.py` / `run_net_forward_caffex.py`）：读取 `models_manifest.json`，对每个模型加载真实权重 → 固定随机/固定输入（seed 统一）→ 前向 → 采集末端 blob（形状 + 数值）与逐层权重统计 → 保存 JSON/npy。
  - 定义统一的输入生成约定（FR-0 Open Question 1：固定随机 float32 或 demo 图预处理，统一实现）。
  - 复用上一轮 test-assets 工具（`compare_ops.py`、`gen_visualization.py`、`cpu_monitor.py`）或扩展为网络级。
- **Acceptance**: FR-1 满足；harness 可在两环境对同一模型分别产出输出文件。
- **验证**: `programmatic` — 对至少 1 个模型（如 resnet50_caffe）成功产出两实现输出文件。

## [x] Task 4: caffe-ffi 全模型网络级测试（FR-2）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在 py314 环境对清单内全部模型执行 `read_net(prototxt, caffemodel)` + `net.forward()`。
  - 记录每个模型：权重加载状态（conv1 权重 std/是否占位）、输出是否含 NaN/Inf、输出形状、加载失败原因。
  - 保存 `caffe_ffi_net_results.json`。
- **Acceptance**: FR-2 满足；全部模型网络级状态记录产出。
- **验证**: `programmatic` — 结果 JSON 条目覆盖全部清单模型。

## [x] Task 5: caffex 全模型网络级测试（FR-3）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在 origin 镜像环境对清单内全部模型执行 `caffe.Net(prototxt, caffemodel)` + `net.forward()`。
  - 记录每个模型：通过/失败状态、输出形状、有限值状态、加载失败原因（不支持的层/输入配置）。
  - 保存 `caffex_net_results.json`。
- **Acceptance**: FR-3 满足；全部模型网络级状态记录产出。
- **验证**: `programmatic` — 结果 JSON 条目覆盖全部清单模型。

## [x] Task 6: 跨实现网络级精度对比与 A-001 验证（FR-4 + FR-5）
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 对每个两实现均成功加载的模型，比对输出 blob：max_abs_error、mean_abs_error、max_rel_error、形状一致性、Top-K 一致率（分类类模型）。
  - 判定逐模型一致/不一致/形状不符/一方失败；保存 `net_comparison.json`。
  - 对至少 1 个带真实权重模型（如 resnet50_caffe / head）比对 conv1 权重统计与逐层 max-abs 放大链，输出 **A-001 状态判定**（已修复/仍存在，附证据）。
- **Acceptance**: FR-4/FR-5 满足；逐模型精度指标 + A-001 明确结论产出。
- **验证**: `programmatic` — 对比结果 JSON 存在且数值合理；`human-judgement` — A-001 判定有证据。

## [x] Task 7: 性能与资源占用基准（FR-6）
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 对成功加载的模型在两实现下预热后运行多次，记录延迟 mean/std/min/max（ms）与 FPS。
  - 采集 CPU 占用（平均/峰值，复用 `cpu_monitor.py`）；GPU 如可用则记录，标注环境差异。
  - 保存 `net_bench_ffi.json` / `net_bench_caffex.json`。
- **Acceptance**: FR-6 满足；逐模型性能指标与资源占用产出。
- **验证**: `programmatic` — 性能数据文件存在；`human-judgement` — 环境差异标注合理。

## [x] Task 8: 可视化与综合报告生成（FR-7）
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**:
  - 生成可视化图表（复用/扩展 `gen_visualization.py`）：逐模型性能柱状图、精度误差图、通过率、A-001 证据图（ECharts HTML 或 matplotlib PNG，离线可渲染）。
  - 生成网络级综合报告（8 章节：①环境 ②执行摘要 ③逐模型精度对比 ④逐模型性能对比 ⑤算子/拓扑差异分析 ⑥可视化 ⑦异常记录与问题定位建议 ⑧复现命令）。
  - 七概念 V 对抗审查视角自检数据可信性（G1 事实无因果词、G2 洞察四元组、数据与原始结果一致）。
  - 归档报告至 `.agents/docs/retrospective/reports/insight-extraction/external-learning/`（如目录不存在先创建）。
- **Acceptance**: FR-7 满足；报告 8 章节完整、数据可追溯、图表可离线渲染、已归档。
- **验证**: `human-judgement` — 报告结构完整、数据一致；`programmatic` — 报告与原始数据文件存在。

## Task Dependencies
- Task 2 ⟵ 独立（可与 Task 1 并行）
- Task 3 ⟵ Task 1, Task 2
- Task 4 ⟵ Task 3；Task 5 ⟵ Task 3（Task 4 与 Task 5 可并行，不同环境）
- Task 6 ⟵ Task 4, Task 5
- Task 7 ⟵ Task 4, Task 5
- Task 8 ⟵ Task 6, Task 7