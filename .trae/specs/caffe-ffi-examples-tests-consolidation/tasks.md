---
source: "spec.md（caffe-ffi-examples-tests-consolidation）"
---

# Tasks

> 迁移的是脚本文件（非包内模块），无对外 API 变更。每项任务完成后需运行对应验证命令。

## Task 1: 迁移验证脚本至 tests/python（转 pytest）
将 4 个验证脚本从 `examples/` 迁至 `tests/python/`，并转为 pytest 兼容测试。

- [x] SubTask 1.1: 迁移 `test_tensor_api.py` → `tests/python/test_tensor_api.py`
  - 将 `check()` runner 改造为 pytest `assert` + `test_*` 函数；保留 `__main__` 独立运行入口
  - 修正 `sys.path.insert(0, 'python')` 的定位逻辑（`tests/python/` 下由 conftest 注入，可移除冗余路径插入）
- [x] SubTask 1.2: 迁移 `test_blob_wrapper.py` → `tests/python/test_blob_wrapper.py`
  - 同上 pytest 化；依赖的 `caffe_ffi.tools` 已是包内模块，无需路径 hack
- [x] SubTask 1.3: 迁移 `test_memory_logging.py` → `tests/python/test_memory_logging.py`
  - pytest 化；对构造泄漏/析构日志的用例标记 `@pytest.mark.leak_check(False)`
- [x] SubTask 1.4: 迁移 `test_memory_leak.py` → `tests/python/test_memory_leak.py`
  - pytest 化；主动泄漏/进程退出场景用例标记 `@pytest.mark.leak_check(False)`；进程退出场景改写为 skip 用例并说明（由 conftest `pytest_sessionfinish` 钩子覆盖）
- [x] SubTask 1.5: pytest 采集验证通过（28 tests collected，无导入/syntax 错误，marker 被识别）；完整运算回归需 P0 环境

## Task 2: 迁移基准脚本至 scripts/
将 2 个 benchmark 脚本迁至 `scripts/`，并修正路径定位。

- [x] SubTask 2.1: 迁移 `benchmark_compute.py` → `scripts/benchmark_compute.py`
  - 修正 `os.chdir(dirname(__file__))` 与 `sys.path.insert(0, "python")` → `../python`；docstring 用法示例改为 `python scripts/benchmark_compute.py`
- [x] SubTask 2.2: 迁移 `benchmark_performance.py` → `scripts/benchmark_performance.py`
  - 同上路径修正；docstring 用法示例改为 `python scripts/benchmark_performance.py`
- [ ] SubTask 2.3: 运行验证 `python scripts/benchmark_compute.py --level P0` 与 `python scripts/benchmark_performance.py`，确认能正确定位 `caffe_ffi` 扩展（需 P0 环境）

## Task 3: 迁移重建脚本至 scripts/
将 `examples/_rebuild.sh` 迁至 `scripts/_rebuild.sh`（属构建工具）。若 `git grep "_rebuild"` 无外部引用则直接迁移。

- [x] SubTask 3.1: `git grep -n "_rebuild"` 确认无外部引用后迁移
- [x] SubTask 3.2: 更新脚本内 `SRC=` 路径注释（如有硬编码 examples 路径）

## Task 4: 更新文档引用
将 docs 中指向已迁移脚本的 `examples/xxx` 引用更新为新路径。

- [x] SubTask 4.1: 更新 `docs/performance/OPTIMIZATION_REPORT.md`（`examples/benchmark_performance.py` → `scripts/benchmark_performance.py`）
- [x] SubTask 4.2: 更新 `docs/performance/P0_OPTIMIZATION_ADDENDUM_20260729.md`（`examples/test_tensor_api.py` → `tests/python/test_tensor_api.py`）
- [x] SubTask 4.3: 更新 `docs/summaries/TEAM_SHARING_SUMMARY.md`（`examples/benchmark_performance.py` → `scripts/benchmark_performance.py`）
- [x] SubTask 4.4: 更新 `docs/setup/ASAN_VERIFICATION_REPORT_20260804.md`（`examples/test_memory_leak.py` → `tests/python/test_memory_leak.py`）
- [x] SubTask 4.5: 更新 `docs/memory/memory-logging-report.md`（`examples/test_memory_logging.py`、`examples/test_memory_leak.py` 对应迁移路径）
- [x] SubTask 4.6: 更新 `docs/retrospectives/memory-logging-retrospective.md`（同 4.5）
- [x] SubTask 4.7: Grep 校验无本仓库 `examples/xxx` 断链（vendored 只读引用按 spec 保留）

## Task 5: 配置与结构校验
- [x] SubTask 5.1: 确认 `pyproject.toml` `testpaths=["tests/python"]` 已覆盖迁移测试，无需改动
- [x] SubTask 5.2: 确认 `sdist.include` 已含 `/tests/**`、`/scripts/**`、`/examples/**`，无需改动
- [x] SubTask 5.3: 确认 `examples/` 仅剩演示/数据/示例，无 `test_*`/`benchmark_*` 残留
- [ ] SubTask 5.4: 全量回归 `python -m pytest tests/python/ -v` 确认无回归（需 P0 环境）

## Task 6: 原子提交交付
- [x] SubTask 6.1: 按原子提交规范提交（迁移脚本 + 文档引用 + 配置），提交信息中文描述"为什么"
- [x] SubTask 6.2: 提交后运行 `git show --stat` 确认文件列表与预期一致（xuanspace e51268f / parent 855886d1 + f1351f11，两仓库均干净）

# Task Dependencies
- [Task 4] 依赖 [Task 1] 与 [Task 2]（文档引用指向迁移后的目标路径）
- [Task 5] 依赖 [Task 1] ~ [Task 4]
- [Task 6] 依赖 [Task 5]