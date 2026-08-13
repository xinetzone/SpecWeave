# Tasks

## Task 1: 物理迁移包目录
- [x] 将 `external/chaos/npuusertools/xmnn/onnx_adaround` 完整移动到 `apps/tests/onnx_adaround`（含 autodiff/data/quant/recon/tests/bench、export.py、onnx_utils.py、pyproject.toml、README.md、docs/）
- [x] 确认旧路径已移除、新路径结构完整
- [x] 验证包在 `PYTHONPATH=apps/tests` 下可 `import onnx_adaround`

## Task 2: 更新 CI 工作流路径
- [x] 更新 `.github/workflows/onnx-adaround-ci.yml`：paths 过滤、PYTHONPATH、cache-dependency-path、working-directory、零 torch grep 路径全部指向 `apps/tests/onnx_adaround`

## Task 3: 更新规范文档路径
- [x] 更新 `onnx-adaround-library` 规范（spec.md/tasks.md/checklist.md）中的包路径引用为 `apps/tests/onnx_adaround`

## Task 4: 迁移后验证
- [x] 在 `apps/tests/onnx_adaround` 下运行 `pytest tests/ --cov=.`：59 项通过、覆盖率 ≥80%、关键模块 ≥90%
- [x] 运行 `ruff check .`：All checks passed
- [x] 零 torch 依赖 grep 检查通过（仅注释/文档命中）

# Task Dependencies
- [Task 2] 依赖 [Task 1]
- [Task 3] 依赖 [Task 1]
- [Task 4] 依赖 [Task 1]（可在迁移后独立执行）
