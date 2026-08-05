---
source: "seven-concepts-cmd 重构优化场景（I→F→A→C）"
status: draft
change-id: caffe-ops-tests-migrate-to-caffe-ffi
---

# Caffe 算子测试套件迁入 caffe-ffi 并改写为测试 caffe_ffi Spec

## Why

`vendor/caffe/tests/ops/` 是从 TVM Caffe 前端提取出的 31 个算子参考测试套件（`caffe-ops-library-extraction` 产物），当前作为**第三方 submodule（vendor/caffe）** 内的文件存在。但它实际是**第一方测试资产**，校验对象是原版 BVLC Caffe（pycaffe），与 vendor 的"只读第三方依赖"定位不符，也无法被 caffe-ffi 复用。

caffe-ffi 是 Caffe 的独立重实现（自己的 `caffe_ffi` 包），其 `tests/python/` 测试 `caffe_ffi` 自身实现。将 ops 套件迁入 caffe-ffi 并**改写为通过 caffe_ffi API 执行**，可：1) 消除第一方测试资产滞留第三方 submodule 的结构债；2) 让 31 个算子的大量参数组合（pad/kernel/stride/dilation/group 等前向覆盖）校验 caffe-ffi 实现；3) 复用 ops 的 numpy 参考断言体系。

## What Changes

- **迁移结构**：`vendor/caffe/tests/ops/` 整体迁入 `libs/caffe-ffi/tests/python/ops/`（嵌套子目录，保留 `__init__.py`/`conftest.py`/`pytest.ini`/`.coveragerc`/`utils.py` + 31 个 `test_*.py`）。
- **改写语义**：将 `utils.py` 及 31 个测试文件中依赖 pycaffe 的实现（`import caffe`/`caffe.Net`/`caffe.SGDSolver`/`caffe.layers as L`/`caffe.NetSpec`）改写为使用 **caffe_ffi**（`net_param_from_string`/`net_from_param`/`Blob.from_numpy`/`net.forward`）。
- **配置适配**：`pytest.ini` 的 testpaths 改为 `..`（相对 ops 目录）；`.coveragerc` 的 source 改为 `../..` 或保留；`conftest.py` 的 `caffe_test_dir` fixture 保留。
- **依赖声明**：`pyproject.toml` 的 `testpaths` 已覆盖 `tests/python/`（递归包含 `ops/`），无需改动；若改写后 ops 依赖 numpy 等，确认已在依赖中。
- **不修改 vendor 源码**：仅从 vendor 迁出测试文件到 caffe-ffi，`vendor/caffe` 内其余文件不动。

**BREAKING**：无对外 API 变更（迁移的是测试文件）。`vendor/caffe/tests/ops/` 从第三方 submodule 中移除，需在 vendor submodule 内提交删除。

## Impact

- **Affected specs**：caffe-ffi 测试套件治理；vendor/caffe 测试资产归位
- **Affected code**：
  - 迁移：`tests/python/ops/`（35 文件：`utils.py` + 31 测试 + `__init__.py`/`conftest.py`/`pytest.ini`/`.coveragerc`）
  - 改写：`utils.py` 的 `_siso_op`/`_miso_op`/`_simo_op`/`_run_caffe`/`_gen_model_files`/`_test_op` 及 31 个测试文件的 `L`/`_test_op` 调用
  - 配置：`pyproject.toml`（如需要）、`tests/python/ops/pytest.ini`/`.coveragerc`
  - 引用：任何指向 `vendor/caffe/tests/ops` 的脚本/文档（vendor 内部 docker 脚本按只读规则处理）

## ADDED Requirements

### Requirement: 算子测试套件完整迁入 caffe-ffi
系统 SHALL 将 `vendor/caffe/tests/ops/` 全部文件迁入 `libs/caffe-ffi/tests/python/ops/`，保留完整目录结构与文件。

#### Scenario: Success case
- **WHEN** 检查 `libs/caffe-ffi/tests/python/ops/`
- **THEN** 存在 `__init__.py`/`conftest.py`/`pytest.ini`/`.coveragerc`/`utils.py` 及全部 `test_*.py`，文件内容与源一致

### Requirement: 测试改写为使用 caffe_ffi
系统 SHALL 将 `utils.py` 与 31 个测试文件中的 pycaffe API 改写为 caffe_ffi API，使每个算子测试通过 caffe_ffi 执行前向推理并与 numpy 参考比对。

#### Scenario: caffe_ffi 前向执行
- **WHEN** 运行 `pytest tests/python/ops/ -k "test_forward"`（在有 C++ 扩展的环境）
- **THEN** 测试通过 caffe_ffi 完成前向，输出与 numpy 参考一致（`assert_op_correct` 通过）

#### Scenario: 无 C++ 扩展时不报错
- **WHEN** 在无 C++ 扩展环境运行 `pytest tests/python/ops/`
- **THEN** 相关用例按 caffe-ffi 既有约定 skip（不抛 ImportError/收集错误），不破坏主测试套件收集

### Requirement: pytest 配置适配
系统 SHALL 调整 `pytest.ini`/`.coveragerc`/`conftest.py`，使 `tests/python/ops/` 可被 `pytest tests/python/` 正常递归采集且不影响根 conftest 行为。

#### Scenario: 主套件采集无误
- **WHEN** 运行 `pytest tests/python/ --collect-only`
- **THEN** `tests/python/ops/` 用例被采集，且既有 `tests/python/` 用例、autouse fixture（泄漏检测/回调清理）不受干扰

### Requirement: 路径引用更新
系统 SHALL 更新所有指向 `vendor/caffe/tests/ops` 的引用为新路径 `libs/caffe-ffi/tests/python/ops`。

#### Scenario: 断链为零
- **WHEN** 执行链接/引用检查
- **THEN** 不再存在指向原 `vendor/caffe/tests/ops` 的有效引用（vendored 内部只读引用按规则处理）

### Requirement: 迁移后功能验证
系统 SHALL 在迁移改写完成后验证迁移文件的完整性（文件数、内容）与可用性（导入、采集、关键算子前向）。

#### Scenario: 完整性核对
- **WHEN** 对比源 `vendor/caffe/tests/ops` 与目标，统计文件数与每文件校验和
- **THEN** 文件数一致，内容一致（改写文件除外）

## MODIFIED Requirements

### Requirement: 原 vendor/caffe/tests/ops 移除
`vendor/caffe/tests/ops/` 从第三方 submodule 移除，迁入 caffe-ffi。

**Reason**：该套件是第一方测试资产，校验对象已改写为 caffe-ffi，不再归属原版 Caffe 测试目录。
**Migration**：在 vendor/caffe submodule 内 `git rm tests/ops` 并提交；caffe-ffi 侧新增 `tests/python/ops/`。

## REMOVED Requirements

### Requirement: ops 套件依赖 pycaffe 运行
**Reason**：改写为测试 caffe_ffi 后不再依赖 pycaffe。
**Migration**：`utils.py` 中 `import caffe` 等 pycaffe 调用替换为 caffe_ffi 对应的 API。