---
source: "seven-concepts-cmd 重构优化场景（I→F→V）"
status: draft
---

# caffe-ffi examples/ 与 tests/ 选择性收敛 Spec

## Why

`examples/` 目录职责本是"使用示例"（AGENTS.md 定义），但内部混居了 6 个**验证/基准脚本**（`test_memory_leak.py`、`test_memory_logging.py`、`test_tensor_api.py`、`test_blob_wrapper.py`、`benchmark_compute.py`、`benchmark_performance.py`）。这些脚本与真正的演示（lenet/mlp/rnn/zero-copy 等）语义不同类，造成"测试到底在哪"的认知混乱，且 `examples/` 不在 pytest 采集范围内，验证脚本无法被 CI 复用。

经七概念方法论评估（I→F→V），**整体合并 `examples/` 与 `tests/` 属负 ROI**（会破坏 57 处文档引用、pytest/CMake 接线、sdist 打包，且破坏"对外演示 vs 对内验证"的职责分离）。本 Spec 采取**选择性收敛**：仅将验证/基准脚本归位到正确目录，真正的演示保留在 `examples/`。

## What Changes

- **迁至 `tests/python/`**（验证包 API，转为 pytest 测试）：
  - `test_tensor_api.py` → `tests/python/test_tensor_api.py`
  - `test_blob_wrapper.py` → `tests/python/test_blob_wrapper.py`
  - `test_memory_logging.py` → `tests/python/test_memory_logging.py`
  - `test_memory_leak.py` → `tests/python/test_memory_leak.py`
- **迁至 `scripts/`**（开发基准/构建工具，与现有 `scripts/` 的 `run_*.py`/`p0_smoke_test.py` 约定一致）：
  - `benchmark_compute.py` → `scripts/benchmark_compute.py`
  - `benchmark_performance.py` → `scripts/benchmark_performance.py`
- **保留在 `examples/`**（真正的使用示例）：
  - `lenet_mnist_train.py`、`mlp_classifier_train.py`、`rnn_forward.py`、`zero_copy_vs_copy_demo.py`、`create_and_run_mlp.py`、`asan_demo.cpp`、`make_object_example.cpp`、`mock_sequence_data.py/.json`、`mnist_data/`
- **更新文档引用**：将 docs 中指向已迁移脚本的 `examples/xxx` 路径改为 `tests/python/xxx` 或 `scripts/xxx`。
- **更新脚本内部路径**：迁移后脚本的 `sys.path`/`os.chdir` 定位逻辑与 docstring 用法示例需随新目录调整。
- **配置**：`pyproject.toml` 的 `testpaths` 已覆盖 `tests/python/`，无需改动；`sdist.include` 已含 `/tests/**`、`/scripts/**`、`/examples/**`，无需改动。

**BREAKING**：无对外 API 变更（迁移的是脚本文件，非包内模块）。仅影响脚本路径与文档引用。

## Impact

- **Affected specs**：caffe-ffi 项目结构治理（examples/tests/scripts 职责收敛）
- **Affected code**：
  - 迁移文件：4 个验证脚本、2 个基准脚本
  - 文档：`docs/performance/`、`docs/setup/`、`docs/memory/`、`docs/summaries/`、`docs/retrospectives/` 中引用已迁移脚本的条目
  - 配置：无（仅当 pytest 采集需调整时）

## ADDED Requirements

### Requirement: 验证脚本归位 tests/
系统 SHALL 将 4 个验证脚本迁移至 `tests/python/` 并转为 pytest 兼容测试，使 `pytest tests/python/` 能采集并正确执行。

#### Scenario: Success case
- **WHEN** 开发者运行 `python -m pytest tests/python/ -k "tensor_api or blob_wrapper or memory_logging or memory_leak"`
- **THEN** 迁移后的测试被采集并全部通过，且不破坏既有测试套件（无回归）

#### Scenario: 内存相关测试避开泄漏自动检测
- **WHEN** `test_memory_leak.py`/`test_memory_logging.py` 中主动构造泄漏/析构场景
- **THEN** 相关用例标记 `@pytest.mark.leak_check(False)`，避免被 conftest 的 autouse 泄漏检测误判为失败

### Requirement: 基准工具归位 scripts/
系统 SHALL 将 2 个 benchmark 脚本迁移至 `scripts/`，并修正其内部路径定位与 docstring 用法示例。

#### Scenario: Success case
- **WHEN** 开发者运行 `python scripts/benchmark_compute.py --level P0`
- **THEN** 脚本能正确定位 `caffe_ffi` 扩展并正常执行基准

### Requirement: 文档引用一致性
系统 SHALL 更新所有指向已迁移脚本的文档引用，确保无 `examples/` 断链。

#### Scenario: 断链检测为零
- **WHEN** 执行链接检查（link-check）
- **THEN** 不再存在指向已迁移脚本的 `examples/xxx` 无效引用

## MODIFIED Requirements

### Requirement: examples/ 职责纯净
`examples/` 目录 SHALL 仅保留真正的使用示例（演示/训练/数据），不再包含验证与基准脚本。

**Reason**：消除"测试脚本与演示混居"的坏味道，恢复 AGENTS.md 定义的"使用示例"职责。
**Migration**：6 个脚本按上述分类迁移；`_rebuild.sh` 属构建工具，一并迁至 `scripts/`（若无外部引用）。

## REMOVED Requirements

### Requirement: examples/ 内联验证脚本
**Reason**：与演示职责不符，且不在 pytest 采集范围。
**Migration**：迁移至 `tests/python/`（验证）或 `scripts/`（基准工具）。