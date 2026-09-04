---
source: "spec.md（caffe-ffi-examples-tests-consolidation）"
---

# Checklist

## 脚本迁移
- [x] `test_tensor_api.py` 已迁移至 `tests/python/` 并转为 pytest 测试
- [x] `test_blob_wrapper.py` 已迁移至 `tests/python/` 并转为 pytest 测试
- [x] `test_memory_logging.py` 已迁移至 `tests/python/` 并转为 pytest 测试，泄漏/析构用例标记 `@pytest.mark.leak_check(False)`
- [x] `test_memory_leak.py` 已迁移至 `tests/python/` 并转为 pytest 测试，泄漏/进程退出用例标记 `@pytest.mark.leak_check(False)`
- [x] `benchmark_compute.py` 已迁移至 `scripts/`，路径定位与 docstring 用法已修正
- [x] `benchmark_performance.py` 已迁移至 `scripts/`，路径定位与 docstring 用法已修正
- [x] `_rebuild.sh` 已迁移至 `scripts/`（无外部引用时）
- [x] `examples/` 仅保留演示/数据/示例，无 `test_*`/`benchmark_*` 残留

## 测试验证
- [x] pytest 采集：28 个测试被正确采集，无导入/语法错误，`leak_check` marker 被识别（集合验证通过）
- [ ] 完整运算回归：`python -m pytest tests/python/ -k "tensor_api or blob_wrapper or memory_logging or memory_leak" -v`（**需 P0 环境**：当前 py314 本地 C++ 扩展未编译，`is_available=False`；需在 WSL Docker caffe-ffi-jupyter 或编译扩展后验证）
- [ ] `python scripts/benchmark_compute.py --level P0` 正常执行（需 P0 环境）
- [ ] `python scripts/benchmark_performance.py` 正常执行（需 P0 环境）

## 文档与配置
- [x] docs 中指向已迁移脚本的 `examples/xxx` 引用已更新为 `tests/python/xxx` 或 `scripts/xxx`
- [x] 链接检查无本仓库 `examples/xxx` 断链（4 处 vendored 只读引用按 spec 保留）
- [x] `pyproject.toml` 无需改动即可采集迁移测试（`testpaths` 已覆盖 `tests/python/`）
- [x] `sdist.include` 已覆盖 `/tests/**`、`/scripts/**`、`/examples/**`

## 交付
- [ ] 原子提交完成，`git show --stat` 文件列表与预期一致
- [x] 无对外 API 变更（BREAKING=无）