# onnx-adaround 库位置迁移（external/chaos → apps/tests）Spec

## Why
`onnx_adaround` 库此前开发时置于 `d:\spaces\SpecWeave\external\chaos\npuusertools\xmnn\onnx_adaround`（外部嵌套仓库，**不受主 SpecWeave 仓库版本控制**）。用户认为该位置不合适，希望将其迁移到主仓库内受版本控制的 `d:\spaces\SpecWeave\apps\tests` 目录，使其成为主仓库内置资产。

## What Changes
- 将整个 `onnx_adaround/` 包目录从 `external/chaos/npuusertools/xmnn/onnx_adaround` 物理移动到 `apps/tests/onnx_adaround`。
- 移动后包仍以顶层包名 `onnx_adaround` 导入（`apps/tests` 需在 `sys.path` / PYTHONPATH 上）。
- 更新 CI 工作流 `.github/workflows/onnx-adaround-ci.yml` 中所有旧路径引用（paths 过滤、PYTHONPATH、cache-dependency-path、working-directory、零 torch grep 路径）。
- 更新 `onnx-adaround-library` 规范文档中的包路径引用（spec/tasks/checklist 中的 `external/chaos/...` 路径 → `apps/tests/...`）。
- 迁移后完整验证：59 项测试通过、覆盖率 ≥80%、ruff 干净、零 torch 依赖静态检查通过。
- **不修改** 库内任何业务逻辑与测试内容，纯位置迁移 + 引用更新。

## Impact
- Affected specs：`onnx-adaround-library`（包路径引用更新）
- Affected code：
  - `apps/tests/onnx_adaround/**`（迁移后的包，含 autodiff/data/quant/recon/tests/bench + export.py/onnx_utils.py/pyproject.toml/README.md/docs）
  - `.github/workflows/onnx-adaround-ci.yml`（路径更新）
  - 源路径 `external/chaos/npuusertools/xmnn/onnx_adaround/**`（迁移后移除）

## ADDED Requirements

### Requirement: 包位置迁移
系统 SHALL 将 `onnx_adaround` 包目录完整迁移到 `apps/tests/onnx_adaround`，保持目录结构与文件内容不变。

#### Scenario: 目录迁移完整
- **WHEN** 检查 `apps/tests/onnx_adaround/`
- **THEN** 包含与源目录一致的完整结构与文件（autodiff/data/quant/recon/tests/bench、export.py、onnx_utils.py、pyproject.toml、README.md、docs/api.md），且旧路径 `external/chaos/npuusertools/xmnn/onnx_adaround` 不再存在

### Requirement: 迁移后可用性（不劣于迁移前）
迁移后包 SHALL 仍可正常导入并运行，所有测试在 `apps/tests` 作为 PYTHONPATH 根时通过，覆盖率与代码质量不下降。

#### Scenario: 迁移后测试全绿
- **WHEN** 在 `apps/tests/onnx_adaround` 下以 `PYTHONPATH=apps/tests` 执行 `pytest tests/ --cov=.`
- **THEN** 全部测试通过（59 项），总覆盖率 ≥80%，关键模块（quantizer/autodiff/bn_fold）≥90%，ruff `All checks passed`

#### Scenario: 零 torch 依赖保持
- **WHEN** 对迁移后的 `apps/tests/onnx_adaround` 执行零 torch grep 检查
- **THEN** 无实际 `import torch`/`from torch`/`onnx2pytorch`（仅注释/文档命中）

### Requirement: CI 路径更新
系统 SHALL 更新 `.github/workflows/onnx-adaround-ci.yml` 使所有路径指向新位置，保证 CI 在迁移后正常工作。

#### Scenario: CI 引用新路径
- **WHEN** 读取 `onnx-adaround-ci.yml`
- **THEN** `paths` 过滤、`PYTHONPATH`、`cache-dependency-path`、`working-directory`、零 torch grep 路径均指向 `apps/tests/onnx_adaround`，不再引用 `external/chaos/...`

### Requirement: 规范文档路径同步
系统 SHALL 更新 `onnx-adaround-library` 规范（spec.md/tasks.md/checklist.md）中的包路径引用，从 `external/chaos/npuusertools/xmnn/onnx_adaround` 更新为 `apps/tests/onnx_adaround`。

#### Scenario: 文档路径一致
- **WHEN** 检索 `onnx-adaround-library` 规范文档
- **THEN** 包路径引用均指向新位置 `apps/tests/onnx_adaround`

## MODIFIED Requirements
无（库内业务逻辑与测试内容不变，仅位置与引用变更）。

## REMOVED Requirements
无。
