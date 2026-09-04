# Caffe 两实现（caffe-ffi / caffex）综合对比测试 - The Implementation Plan (可验证任务清单)

## [x] Task 1: 环境预检与测试矩阵设计
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 验证两套运行环境可用性：①caffe-ffi 的 `apps/caffe-ffi-jupyter`（`jupyter-ssh-base:1.1`）或本地 `py314` conda；②caffex 的 origin Docker 镜像（`caffe-cpu:origin-runtime`）。
  - 确认 caffe-ffi C++ 扩展已编译可加载（`import caffe_ffi` 通过），否则执行 `pip install -e . --no-build-isolation`。
  - 确认 caffex `tests/ops/` 与 `docker/origin/run_ops_tests.sh` 可用。
  - 设计测试矩阵：算子清单（≥10：conv/pooling/relu/sigmoid/tanh/prelu/elu/inner_product/softmax/batchnorm/scale/eltwise）、网络清单（≥3：ResNet-50/VGG16/MobileNet，复用 caffe-ffi `tests/python/networks/`）、输入形状、固定随机种子。
- **Acceptance**: TR-1 环境验证通过；测试矩阵文档化。
- **验证**: `programmatic` — 环境验证命令输出；`human-judgement` — 矩阵覆盖度。

## [x] Task 2: caffe-ffi 功能测试（py314）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 py314 环境运行 caffe-ffi 综合测试套件：`python -m pytest tests/python/ -v`（含 `ops/`、`networks/`、backward 测试）。
  - 记录通过/失败/跳过/错误用例数，捕获 JUnit XML 与日志。
  - 验证核心接口：`import caffe_ffi`、`read_net`、`net.forward()`（小写返回 ndarray）、`net.Forward()`（大写返回 Blob）等。
  - 记录 `_caffe_ffi.so` 加载状态与版本。
- **Acceptance**: FR-1 满足；接口可用、C++ 扩展正常加载。
- **验证**: `programmatic` — pytest 退出码、JUnit XML、用例统计。

## [x] Task 3: caffex 功能测试（origin 镜像环境）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 origin 提供的 Docker 镜像环境运行 caffex `tests/ops/` 测试（复用 `run_ops_tests.sh` 或等价容器内脚本）。
  - 以 numpy 参考验证算子输出正确性，记录规范化数值偏差。
  - 记录算子级通过率、失败用例，标注实现特性（COW 恒等、dtype、形状语义、Backward 行为），作为 vs caffe-ffi 差异分析的依据。
- **Acceptance**: FR-2 满足；功能正确性与实现特性清单产出。
- **验证**: `programmatic` — 测试结果文件；`human-judgement` — 实现特性章节。

## [x] Task 4: 跨实现算子精度对比（caffe-ffi vs caffex）
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 编写/复用对比脚本：对每个算子用相同随机输入与固定权重，分别经 caffe-ffi 与 caffex 前向。
  - 计算 max_abs_error、mean_abs_error、max_rel_error、Top-1/Top-5 一致率。
  - 保存逐算子精度结果 CSV/JSON。
  - 注意：两实现横跨不同运行环境，对比脚本需在各自环境产出输出后统一汇聚，或采用 numpy 参考作为公共基准。
- **Acceptance**: FR-3 满足；逐算子精度指标产出。
- **验证**: `programmatic` — 精度数据文件存在且数值合理。

## [x] Task 5: 性能与资源占用基准
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 对每个算子/网络标准输入形状，预热后运行多次，记录 mean/std/min/max 延迟（ms）、推算 FPS。
  - 采集 CPU 时间/内存占用（psutil 或容器内 tool）；GPU 如可用则记录，注明环境差异。
  - 保存性能数据 CSV。
- **Acceptance**: FR-4 满足；性能指标与资源占用产出。
- **验证**: `programmatic` — 性能数据文件；`human-judgement` — 环境差异标注合理。

## [x] Task 6: 可视化与结构化数据生成
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 生成可视化图表：性能对比柱状图（各实现/算子维度）、精度误差曲线图（误差 vs 输入规模或算子）。
  - 优先使用 ECharts 单文件 HTML（离线可渲染）或 matplotlib PNG。
- **Acceptance**: 图表可本地离线渲染，反映精度/性能数据。
- **验证**: `human-judgement` — 图表正确性；`programmatic` — 图表文件存在。

## [x] Task 7: 综合测试报告生成与归档
- **Priority**: high
- **Depends On**: Task 2-6
- **Description**:
  - 生成综合测试报告，包含 8 个章节：①标题/环境信息 ②执行摘要（通过/失败/跳过统计）③精度对比表 ④性能对比表 ⑤算子/网络差异分析 ⑥可视化图表 ⑦异常记录与问题定位建议 ⑧复现命令附录。
  - 采用七概念 V 对抗审查视角自检数据可信性（G1 事实无因果词、G2 洞察四元组、报告数据与原始结果一致）。
  - 归档最终报告至 `.agents/docs/retrospective/reports/insight-extraction/external-learning/`（如目录不存在则先创建）。
- **Acceptance**: FR-5 满足；报告 8 章节完整、数据可追溯、可复现。
- **验证**: `human-judgement` — 报告结构完整、数据一致；`programmatic` — 报告与原始数据文件存在。

## Task Dependencies
- Task 2 ⟵ Task 1
- Task 3 ⟵ Task 1
- Task 4 ⟵ Task 2, Task 3
- Task 5 ⟵ Task 2, Task 3
- Task 6 ⟵ Task 4, Task 5
- Task 7 ⟵ Task 2-6
- Task 2 与 Task 3 可并行（不同环境）。