---
source: "spec.md（caffe-ops-tests-migrate-to-caffe-ffi）"
---

# Checklist

## 迁移
- [x] `tests/python/ops/` 存在，含 `__init__.py`/`conftest.py`/`pytest.ini`/`.coveragerc`/`utils.py` + 全部 31 个 `test_*.py`
- [x] 迁移文件数与源 `vendor/caffe/tests/ops/` 一致，结构保留

## 改写
- [x] `utils.py` 不再依赖 pycaffe（无 `import caffe`），改用 caffe_ffi API 完成前向
- [x] 31 个测试文件导入/调用适配 caffe_ffi 版 harness，参数组合与 numpy 参考断言保持
- [x] caffe_ffi 未实现的算子已标记 skip 并说明（test_permute.py）

## 配置
- [x] `pytest.ini`/`.coveragerc` 路径适配，`testpaths` 使 `tests/python/ops/` 可被递归采集
- [x] `conftest.py` fixture 与根 conftest（泄漏检测/回调清理）无冲突
- [x] `pyproject.toml` 注册 pytest markers，迁移测试可正常采集

## 引用
- [x] 无指向 `vendor/caffe/tests/ops` 的有效断链（vendored 只读引用按规则处理）

## 验证
- [x] `pytest tests/python/ --collect-only` 采集无误，不破坏主套件
- [x] 无 C++ 扩展环境：`pytest tests/python/ops/` skip 而非报错
- [ ] 有 C++ 扩展环境：关键算子前向（conv/pooling/relu/softmax 等）`assert_op_correct` 通过（阻塞：沙箱限制编译 C++ 扩展，需在 WSL Docker `caffe-ffi` 环境执行）

## 交付
- [x] caffe-ffi 原子提交完成（b1b3a1b）
- [x] vendor/caffe submodule 移除 `tests/ops` 并提交（f938d88b）
- [x] 两仓库工作区干净（superproject gitlink 指针 698ae87）