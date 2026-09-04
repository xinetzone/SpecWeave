---
source: "spec.md（caffe-ops-tests-migrate-to-caffe-ffi）"
---

# Tasks

> 迁移 + 改写双结合。迁移保留结构；改写将 pycaffe API 替换为 caffe_ffi API。依赖无 C++ 扩展环境时的 skip 约定。

## Task 1: 迁移文件夹结构
将 `vendor/caffe/tests/ops/` 整体复制到 `libs/caffe-ffi/tests/python/ops/`，保留全部文件与结构。

- [x] SubTask 1.1: 复制 `__init__.py`/`conftest.py`/`pytest.ini`/`.coveragerc`/`utils.py` + 全部 `test_*.py`（31 个）到 `tests/python/ops/`
- [x] SubTask 1.2: 逐文件核对（文件数、结构、权限），确认无遗漏

## Task 2: 改写共用 harness `utils.py` 为 caffe_ffi
将 `utils.py` 中 pycaffe 依赖（`import caffe`、`caffe.NetSpec`、`caffe.layers as L`、`caffe.SGDSolver`、`caffe.Net`）改写为 caffe_ffi API。

- [x] SubTask 2.1: 调研 caffe_ffi 支持的层类型清单，建立 op_name → caffe_ffi layer type 映射
- [x] SubTask 2.2: 重写 `_siso_op`/`_miso_op`/`_simo_op`：改为生成 prototxt 字符串（沿用 caffe_ffi 的 `net_param_from_string`/`net_from_param` 路径）
- [x] SubTask 2.3: 重写 `_gen_model_files`/`_run_caffe`：改为 caffe_ffi 构建 Net + `Blob.from_numpy` 设权重/输入 + `net.forward()` 取输出
- [x] SubTask 2.4: 保留 `assert_op_correct`/`_gen_filename_str`/Timer/memory 工具（不依赖 pycaffe 的部分）
- [x] SubTask 2.5: 对 caffe_ffi 未实现的算子类型，提供 skip 标记（`pytest.mark.skipif`）或明确跳过

## Task 3: 改写 31 个测试文件
将各 `test_*.py` 中 `from utils import L, _test_op, assert_op_correct` 及 `L.<Op>` 调用适配为 caffe_ffi 版 harness。

- [x] SubTask 3.1: 批量替换 `L`/`_test_op` 调用与导入，保持参数组合与 numpy 参考断言不变
- [x] SubTask 3.2: 对 caffe_ffi 未实现的算子，标记 skip 并在 docstring 说明
- [x] SubTask 3.3: 语法/导入检查（`python -m py_compile` / ruff）

## Task 4: 适配 pytest 配置
调整 `tests/python/ops/` 的 pytest 配置，使其可被主套件递归采集且不干扰根 conftest。

- [x] SubTask 4.1: `pytest.ini` testpaths 改为 `..`（相对 ops 子目录），markers 保留
- [x] SubTask 4.2: `.coveragerc` source 路径适配
- [x] SubTask 4.3: `conftest.py` 的 `caffe_test_dir` fixture 保留；确认不与根 conftest 的 autouse（泄漏检测/回调清理）冲突
- [x] SubTask 4.4: 确认 `pyproject.toml` `testpaths=["tests/python"]` 递归包含 `ops/`，无需改动

## Task 5: 更新路径引用
更新所有指向 `vendor/caffe/tests/ops` 的引用。

- [x] SubTask 5.1: `grep -rl "vendor/caffe/tests/ops\|tests/ops"` 定位引用
- [x] SubTask 5.2: 更新 caffe-ffi 侧文档/脚本引用为 `tests/python/ops`
- [x] SubTask 5.3: vendor/caffe 内部只读引用（docker 脚本等）按第三方只读规则记录，不强行修改

## Task 6: 迁移后验证
验证完整性、采集、关键算子前向。

- [x] SubTask 6.1: 文件数/结构核对（源 vs 目标，排除预期改写差异）
- [x] SubTask 6.2: `pytest tests/python/ --collect-only` 采集无误，不破坏主套件
- [x] SubTask 6.3: 无 C++ 扩展环境运行 `pytest tests/python/ops/`，确认 skip 而非报错
- [ ] SubTask 6.4: 有 C++ 扩展环境运行关键算子前向（conv/pooling/relu/softmax 等），确认 `assert_op_correct` 通过
  - ⚠️ 阻塞：本地沙箱限制写入源码树 `build/`（`PermissionError: .skbuild-info.json`），Docker 主机不可达，本会话无法编译 C++ 扩展；需在 WSL Docker `caffe-ffi` 环境或放开沙箱后执行

## Task 7: 原子提交交付
- [x] SubTask 7.1: caffe-ffi 侧原子提交（迁移 + 改写 + 配置）— `feat(caffe-ffi)` b1b3a1b
- [x] SubTask 7.2: vendor/caffe submodule 内 `git rm tests/ops` 并提交删除 — `test(ops)` f938d88b
- [x] SubTask 7.3: 提交后 `git status` 确认两仓库干净（superproject 额外提交 gitlink 指针 `chore(caffe-ffi)` 698ae87）

# Task Dependencies
- [Task 2] 依赖 [Task 1]（需要源文件）
- [Task 3] 依赖 [Task 2]（harness 定义）
- [Task 4] 依赖 [Task 1]（配置随迁）
- [Task 5] 依赖 [Task 1]
- [Task 6] 依赖 [Task 2]~[Task 5]
- [Task 7] 依赖 [Task 6]