# Caffe 网络级测试迁移到 caffe-ffi Spec

## Why
`vendor/caffe/tests/networks/` 下的 4 个预训练网络端到端测试（AlexNet、MobileNetV2、ResNet50、InceptionV1）目前依赖 pycaffe（`import caffe` + `caffe.Net`），无法在 caffe-ffi 测试环境中运行。为与已迁移的 `tests/python/ops/` 单算子测试并列，需将网络级测试整体迁移至 `libs/caffe-ffi/tests/python/networks/`，改写为纯 `caffe_ffi` 实现，验证完整模型加载、权重载入与推理流程。

## What Changes
- 将 `vendor/caffe/tests/networks/` 全部 7 个文件迁移至 `libs/caffe-ffi/tests/python/networks/`（保留目录结构与 Apache License 头部）。
- 改写 `utils.py` 的 `_test_network`：由 `caffe.Net(proto, blob, caffe.TEST)` 改为 `caffe_ffi.read_net(proto, blob)`，输入注入用 `net.blob_by_name("data").data = data`，输出用 `net.forward()`。
- 无 C++ 扩展环境时对网络测试做 skip（复用 `ops/` 的 `_CAFFE_FFI_AVAILABLE` 约定），避免 Python-only 回退给出空/错误结果。
- 保持 `_download_model`、`_preprocess_imagenet` 与 4 个测试文件的参数/URL/断言不变（仅 `from utils import ...` 解析路径适配）。
- vendor/caffe 侧删除 `tests/networks/`（第三方只读子模块，按子模块流程 `git rm` 提交）。

## Impact
- Affected specs: `caffe-network-tests-integration`（源 networks 创建规格）、`caffe-ops-tests-migrate-to-caffe-ffi`（参考的迁移模式）
- Affected code:
  - `projects/xuanspace/libs/caffe-ffi/tests/python/networks/`（新增：__init__.py、conftest.py、utils.py、test_alexnet.py、test_mobilenetv2.py、test_resnet50.py、test_inceptionv1.py）
  - `projects/xuanspace/vendor/caffe/tests/networks/`（删除）

## ADDED Requirements

### Requirement: 网络测试迁移到 caffe-ffi
系统 SHALL 将 `vendor/caffe/tests/networks/` 迁移至 `libs/caffe-ffi/tests/python/networks/`，并改写为纯 `caffe_ffi` 实现。

#### Scenario: 完整迁移
- **WHEN** 迁移完成
- **THEN** 目标目录包含 `__init__.py`、`conftest.py`、`utils.py` 及 4 个 `test_*.py`，共 7 个文件，全部保留 Apache License 头部

#### Scenario: 改写 util 为 caffe_ffi
- **WHEN** 执行网络推理
- **THEN** `_test_network` 使用 `caffe_ffi.read_net(proto_file, blob_file)` 加载模型与权重，`net.blob_by_name("data").data = data` 注入输入，`net.forward()` 返回输出，且源码中无任何 `import caffe` / `caffe.Net`

#### Scenario: 无 C++ 扩展时安全跳过
- **WHEN** `caffe_ffi.is_available()` 为假
- **THEN** 网络测试通过 `pytest.skip` 跳过，而非失败

### Requirement: 迁移后的 pytest 采集与验证
系统 SHALL 使迁移后的 `networks/` 可被主套件递归采集，且不干扰根 conftest。

#### Scenario: 采集通过
- **WHEN** 运行 `pytest tests/python/ --collect-only`
- **THEN** `networks/` 下 4 个测试被采集，无导入错误，不破坏主套件

#### Scenario: 有扩展环境真实推理
- **WHEN** 在 WSL Docker `caffe-ffi` 环境运行网络前向
- **THEN** 模型加载成功、推理执行成功、输出非空、无 NaN/Inf（对 caffe-ffi 暂不支持的网络层，测试应明确 skip 并记录，而非静默失败）

## MODIFIED Requirements

### Requirement: 网络测试文件保留原有参数语义（源自 caffe-network-tests-integration）
迁移后的 4 个测试 SHALL 保留源文件的预处理参数、模型 URL 与输入形状：
- MobileNetV2: mean 默认、scale=58.8、输入 (1,3,224,224)
- AlexNet: mean 默认、scale=1.0、输入 (1,3,227,227)、无 `@pytest.mark.skip`
- ResNet50: mean 默认、scale=1.0、输入 (1,3,224,224)
- InceptionV1: mean 默认、scale=58.8、输入 (1,3,224,224)、无 `@pytest.mark.skip`
- 4 个测试均保留 `@pytest.mark.slow`

## REMOVED Requirements

### Requirement: vendor/caffe 侧 networks 测试（pycaffe 版）
**Reason**: 网络测试已迁移至 caffe-ffi 测试库，vendor/caffe 为第三方只读子模块，不应长期保留与 caffe-ffi 测试库重复且依赖 pycaffe 的测试副本。
**Migration**: 从 `vendor/caffe` 子模块内 `git rm tests/networks` 并提交删除；superproject 额外提交 gitlink 指针更新。