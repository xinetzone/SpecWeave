# caffe-framework — Caffe/CaffEx 框架

Caffe/CaffEx 框架：Caffe FFI、pycaffe、算子实现、Docker 镜像与性能优化 spec。

**Spec 数量**：44
**上级看板**：[返回全局执行看板](../README.md)

---

## &#128451; 主题说明

- **归属判定**：Caffe/CaffEx 框架：Caffe FFI、pycaffe、算子实现、Docker 镜像与性能优化 spec
- **新增 Spec 流程**：先查重 → 创建三件套 → 全局看板由 docgen（C-6）自动刷新

*本看板由 Python 脚本于 2026-09-04 生成（C-2b），后续应由 docgen 自动化维护（C-6）。*

<!-- THEME_DASHBOARD_START -->

| # | Spec 名称 | 状态 | 三件套 |
|---|---|---|---|
| 1 | [asan-memory-verification](asan-memory-verification/spec.md) | ✓ 完成 | ✓/✗ |
| 2 | [blob-shape-tvm-ffi-refactor](blob-shape-tvm-ffi-refactor/spec.md) | ✓ 完成 | ✓/✗ |
| 3 | [caffe-comprehensive-comparison-test](caffe-comprehensive-comparison-test/spec.md) | ✓ 完成 | ✓/✗ |
| 4 | [caffe-conda-python314-docker](caffe-conda-python314-docker/spec.md) | ! 进行中 | ✓/✗ |
| 5 | [caffe-customer-docker](caffe-customer-docker/spec.md) | ? 待启动 | ✓/✗ |
| 6 | [caffe-demo-compile-fix](caffe-demo-compile-fix/spec.md) | ✓ 完成 | ✓/✗ |
| 7 | [caffe-ffi-conv-v4-milestone](caffe-ffi-conv-v4-milestone/spec.md) | ? 待启动 | ✓/✗ |
| 8 | [caffe-ffi-examples-tests-consolidation](caffe-ffi-examples-tests-consolidation/spec.md) | ! 进行中 | ✓/✗ |
| 9 | [caffe-ffi-extraction-migration](caffe-ffi-extraction-migration/spec.md) | ✓ 完成 | ✓/✗ |
| 10 | [caffe-ffi-followup-fixes-analysis](caffe-ffi-followup-fixes-analysis/spec.md) | ✓ 完成 | ✓/✗ |
| 11 | [caffe-ffi-optimization](caffe-ffi-optimization/spec.md) | ✓ 完成 | ✓✗✗ |
| 12 | [caffe-ffi-p1-ops-implementation](caffe-ffi-p1-ops-implementation/spec.md) | ✓ 完成 | ✓/✗ |
| 13 | [caffe-ffi-p2-ops-implementation](caffe-ffi-p2-ops-implementation/spec.md) | ✓ 完成 | ✓/✗ |
| 14 | [caffe-ffi-p2b-split-perf-csv](caffe-ffi-p2b-split-perf-csv/spec.md) | ✓ 完成 | ✓/✗ |
| 15 | [caffe-ffi-rnn-lstm-phase1](caffe-ffi-rnn-lstm-phase1/spec.md) | ✓ 完成 | ✓✗✗ |
| 16 | [caffe-ffi-rnn-lstm-phase2](caffe-ffi-rnn-lstm-phase2/spec.md) | ✓ 完成 | ✓✗✗ |
| 17 | [caffe-ffi-tvm-integration](caffe-ffi-tvm-integration/spec.md) | ✓ 完成 | ✓/✗ |
| 18 | [caffe-framework-learning](caffe-framework-learning/spec.md) | ? 待启动 | ✓/✗ |
| 19 | [caffe-hub-models-comparison-test](caffe-hub-models-comparison-test/spec.md) | ✓ 完成 | ✓/✗ |
| 20 | [caffe-jupyter-docker-build](caffe-jupyter-docker-build/spec.md) | ? 待启动 | ✓/✗ |
| 21 | [caffe-jupyter-ssh-dockerfile](caffe-jupyter-ssh-dockerfile/spec.md) | ✓ 完成 | ✓/✗ |
| 22 | [caffe-network-tests-integration](caffe-network-tests-integration/spec.md) | ✓ 完成 | ✓/✗ |
| 23 | [caffe-network-tests-migrate-to-caffe-ffi](caffe-network-tests-migrate-to-caffe-ffi/spec.md) | ✓ 完成 | ✓/✗ |
| 24 | [caffe-ops-library-extraction](caffe-ops-library-extraction/spec.md) | ✓ 完成 | ✓/✗ |
| 25 | [caffe-ops-tests-migrate-to-caffe-ffi](caffe-ops-tests-migrate-to-caffe-ffi/spec.md) | ! 进行中 | ✓/✗ |
| 26 | [caffe-origin-cpu-docker](caffe-origin-cpu-docker/spec.md) | ✓ 完成 | ✓/✗ |
| 27 | [caffe-origin-standalone-docker-export](caffe-origin-standalone-docker-export/spec.md) | ! 进行中 | ✓/✗ |
| 28 | [caffe-pycaffe-jupyter-ssh-docker](caffe-pycaffe-jupyter-ssh-docker/spec.md) | ✓ 完成 | ✓/✗ |
| 29 | [caffe-pycaffe-migration](caffe-pycaffe-migration/spec.md) | ✓ 完成 | ✓/✗ |
| 30 | [caffe-rmsnorm-optimization](caffe-rmsnorm-optimization/spec.md) | ✓ 完成 | ✓/✗ |
| 31 | [caffe-slim-bvlc-compat](caffe-slim-bvlc-compat/spec.md) | ! 进行中 | ✓/✗ |
| 32 | [caffe-standalone-pycaffe-docker](caffe-standalone-pycaffe-docker/spec.md) | ✓ 完成 | ✓/✗ |
| 33 | [caffe-tvm-ffi-dependency-migration](caffe-tvm-ffi-dependency-migration/spec.md) | ? 待启动 | ✓✗✗ |
| 34 | [caffeproto-l2-normalize](caffeproto-l2-normalize/spec.md) | ✓ 完成 | ✓/✗ |
| 35 | [caffeproto-upgrade-from-reference](caffeproto-upgrade-from-reference/spec.md) | ✓ 完成 | ✓/✗ |
| 36 | [caffex-ops-comprehensive-test](caffex-ops-comprehensive-test/spec.md) | ✓ 完成 | ✓/✗ |
| 37 | [caffex-ops-test-execution-report](caffex-ops-test-execution-report/spec.md) | ✓ 完成 | ✓/✗ |
| 38 | [caffex-vs-caffe-ffi-gap-analysis](caffex-vs-caffe-ffi-gap-analysis/spec.md) | ✓ 完成 | ✓/✗ |
| 39 | [cmake-atomization-caffe-ffi](cmake-atomization-caffe-ffi/spec.md) | ✓ 完成 | ✓✗✗ |
| 40 | [conda-pip-editable-tvm-ffi](conda-pip-editable-tvm-ffi/spec.md) | ✓ 完成 | ✓/✗ |
| 41 | [conv-gemm-optimization](conv-gemm-optimization/spec.md) | ✓ 完成 | ✓/✗ |
| 42 | [cow-blob-fix](cow-blob-fix/spec.md) | ✓ 完成 | ✓/✗ |
| 43 | [openblas-fix-and-report-update](openblas-fix-and-report-update/spec.md) | ! 进行中 | ✓/✗ |
| 44 | [pycaffe-python314-compat](pycaffe-python314-compat/spec.md) | ✓ 完成 | ✓/✗ |

<!-- THEME_DASHBOARD_END -->
