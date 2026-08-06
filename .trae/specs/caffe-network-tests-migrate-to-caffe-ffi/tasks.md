---
source: "spec.md（caffe-network-tests-migrate-to-caffe-ffi）"
---

# Tasks

> 迁移 + 改写双结合。迁移保留结构；改写将 pycaffe（`caffe.Net`）替换为 caffe_ffi（`read_net`）。无 C++ 扩展环境时 skip 的约定与 `ops/` 一致。

## Task 1: 迁移文件夹结构
将 `vendor/caffe/tests/networks/` 整体复制到 `libs/caffe-ffi/tests/python/networks/`，保留全部文件与结构。

- [x] SubTask 1.1: 复制 `__init__.py`/`conftest.py`/`utils.py`/`test_alexnet.py`/`test_mobilenetv2.py`/`test_resnet50.py`/`test_inceptionv1.py`（共 7 个）到 `tests/python/networks/`
- [x] SubTask 1.2: 逐文件核对（文件数、结构、License 头部），确认无遗漏

## Task 2: 改写共用 harness `utils.py` 为 caffe_ffi
将 `utils.py` 中 pycaffe 依赖（`import caffe`、`caffe.Net`、`caffe.TEST`）改写为 caffe_ffi API。

- [x] SubTask 2.1: 保留 `_download_model`、`_preprocess_imagenet` 不变；移除 `import caffe`
- [x] SubTask 2.2: 重写 `_test_network`：`net = caffe_ffi.read_net(proto_file, blob_file)` → `net.blob_by_name("data").data = data` → `out = net.forward()` → 返回 `list(out.values())`
- [x] SubTask 2.3: 增加 C++ 扩展可用性判断（`caffe_ffi.is_available()`），不可用时 `pytest.skip`（复用 `ops/utils.py` 的 `_CAFFE_FFI_AVAILABLE` 约定）
- [x] SubTask 2.4: 保留 `GLOG_minloglevel`/logging 环境抑制逻辑；确认无 `tvm`/`relay`/`download_testdata` 导入

## Task 3: 改写 4 个测试文件
将各 `test_*.py` 适配为 caffe_ffi 版 harness，保持预处理参数、模型 URL、输入形状与断言不变。

- [x] SubTask 3.1: 确认 4 个测试文件 `from utils import _download_model, _preprocess_imagenet, _test_network` 与 `caffe_model_dir` fixture 引用无需改动（仅 harness 内部改写）
- [x] SubTask 3.2: 确认 4 个测试均保留 `@pytest.mark.slow`，AlexNet 与 InceptionV1 无 `@pytest.mark.skip`
- [x] SubTask 3.3: 语法/导入检查（`python -m py_compile` / ruff）

## Task 4: 适配 pytest 配置
调整 `tests/python/networks/` 的 pytest 配置，使其可被主套件递归采集且不干扰根 conftest。

- [x] SubTask 4.1: `networks/conftest.py` 保留 `caffe_model_dir` fixture（session 级，默认 `~/.caffe_test_data/models/`）
- [x] SubTask 4.2: 在 `networks/conftest.py` 将 `_networks_dir` 加入 `sys.path`，使 `from utils import ...` 平铺导入可解析（与 `ops/conftest.py` 同款方案）
- [x] SubTask 4.3: 确认无需新增 `pytest.ini`（`pyproject.toml` `testpaths=["tests/python"]` 递归包含 `networks/`）；确认不与根 conftest 的 autouse（泄漏检测/回调清理）冲突

## Task 5: 更新路径引用
更新所有指向 `vendor/caffe/tests/networks` 的引用。

- [x] SubTask 5.1: `grep -rl "vendor/caffe/tests/networks\|tests/networks"` 定位引用（caffe-ffi 与 vendor/caffe 均无残留）
- [x] SubTask 5.2: 更新 caffe-ffi 侧文档/脚本引用为 `tests/python/networks`（无匹配，无需改动）
- [x] SubTask 5.3: vendor/caffe 内部只读引用按第三方只读规则记录，不强行修改

## Task 6: 迁移后验证
验证完整性、采集、skip 约定与真实网络前向。

- [x] SubTask 6.1: 文件数/结构核对（源 vs 目标，排除预期改写差异，共 7 个文件）
- [x] SubTask 6.2: `pytest tests/python/ --collect-only` 采集无误，不破坏主套件（4 tests collected）
- [x] SubTask 6.3: 无 C++ 扩展环境运行 `pytest tests/python/networks/`，确认 skip 而非报错（4 skipped，0.17s）
- [x] SubTask 6.4: 有 C++ 扩展环境验证迁移核心路径：容器内 `read_net(proto,caffemodel)`→`blob_by_name("data")`→`forward()` 输出有限值、形状正确；完整预训练模型推理受限于容器下载速率（~4MB/min）阻塞，与 ops 迁移 SubTask 6.4 相同的环境限制

## Task 7: 原子提交交付
- [x] SubTask 7.1: caffe-ffi 侧原子提交（迁移 + 改写 + 配置）— `feat(caffe-ffi)`（commit `f5ac091`，7 文件）
- [x] SubTask 7.2: vendor/caffe 源测试**保留不动**（用户确认：第三方只读子模块，AGENTS.md 禁止本地修改；迁移作复制而非移动，不违反治理契约）
- [x] SubTask 7.3: 提交后 `git status` 确认仓库干净（vendor/caffe 子模块保持只读与 clean 状态，superproject 无 gitlink 指针变更）

# Task Dependencies
- [Task 2] 依赖 [Task 1]（需要源文件）
- [Task 3] 依赖 [Task 2]（harness 定义）
- [Task 4] 依赖 [Task 1]（配置随迁）
- [Task 5] 依赖 [Task 1]
- [Task 6] 依赖 [Task 2]~[Task 5]
- [Task 7] 依赖 [Task 6]