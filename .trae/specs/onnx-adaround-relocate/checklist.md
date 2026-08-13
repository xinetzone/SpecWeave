# Checklist

- [x] `onnx_adaround` 包目录已完整迁移到 `apps/tests/onnx_adaround`，结构完整（autodiff/data/quant/recon/tests/bench、export.py、onnx_utils.py、pyproject.toml、README.md、docs/api.md）
- [x] 旧路径 `external/chaos/npuusertools/xmnn/onnx_adaround` 内容已移除（仅遗留一个空目录壳，因 OS 句柄被占用暂时无法删除，待占用进程退出后可手动移除）
- [x] 包在 `PYTHONPATH=apps/tests` 下可正常 `import onnx_adaround`（实测 import OK，指向 apps/tests/onnx_adaround/__init__.py）
- [x] 迁移后 `pytest tests/ --cov=.` 全部通过（59 项），覆盖率 88.80%（≥80%），关键模块 ≥90%（quant 100%、onnx_utils 96%、autodiff 90-94%）
- [x] 迁移后 `ruff check .` 干净（All checks passed，9 处 I001 已 --fix）
- [x] 迁移后零 torch 依赖静态检查通过（仅 docstring/print 提及，无实际 import 语句）
- [x] CI 工作流 `.github/workflows/onnx-adaround-ci.yml` 所有路径已指向 `apps/tests/onnx_adaround`，且零 torch grep 收窄为仅匹配真实 import 语句（注释/文档除外）
- [x] `onnx-adaround-library` 规范文档路径已同步更新
- [x] 库内业务逻辑与测试内容未改动（纯位置迁移 + 引用更新；仅 ruff --fix 重排了测试文件的 import 顺序）
