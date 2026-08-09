# ORT-Only 量化方案重构 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 重构 Dockerfile — 移除 neural-compressor 必装依赖，NC 检查降级为可选
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 从 Stage 2 的 `pip install` 列表中移除 `neural-compressor`
  - 评估 `onnxruntime-tools` 是否仍需要（其 optimizer 已被 ORT 内置图优化覆盖），若无需则一并移除
  - 更新 LABEL `quantization` 字段，明确 onnxruntime 为核心
  - 更新文件头注释中的工具链描述
  - Stage 2 版本打印块中，NC 版本检查改为条件检查（python -c "import neural_compressor; ..." 2>/dev/null || echo "not installed (optional)"）
  - Stage 3 冒烟测试中的 NC 导入测试（NCIMPORT 块）改为可选：将 NC 导入从硬检查改为 try/except，失败时输出 INFO 而非 FAIL，不中断构建
  - build-info 中 `NEURAL_COMPRESSOR_VERSION` 改为条件字段（未安装时输出 "not installed"）
  - Stage 3 的 NCUNIT（test_neural_compressor.py 严格模式）改为条件运行（仅当 INC 已安装时执行，否则 SKIP）
  - `PACKAGES_INSTALLED` 标签中 neural-compressor 标记为 optional
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: Dockerfile 中 grep `neural-compressor` 不出现在 pip install 必装列表中（注释除外）
  - `programmatic` TR-1.2: Dockerfile 中 NC 版本打印包含 `|| echo` 或 `2>/dev/null` 容错逻辑
  - `programmatic` TR-1.3: NCIMPORT heredoc 中使用 try/except 处理 ImportError
  - `human-judgement` TR-1.4: Dockerfile 注释清晰说明 NC 为可选扩展及手动安装命令
- **Notes**: onnxruntime-tools 评估：查看其在代码库中的使用情况后决定是否保留。如果没有代码引用 `onnxruntime_tools`，一并移除。

## [ ] Task 2: 调整 verify-deployment.py — INC 从必选降级为可选
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `test_imports()` 中将 `("neural_compressor", "Neural Compressor")` 从必选包列表移到单独的"可选包"列表
  - 可选包导入失败时记录 status="SKIP"（而非 FAIL），message 说明 "optional, not installed"
  - `test_neural_compressor_imports()` 函数开头添加 INC 可用性检查：若 `import neural_compressor` 失败则打印 SKIP 信息并直接 return，不执行后续测试
  - 在文件头 docstring 中更新说明：Neural Compressor 标注为 optional
  - 确认最终结果汇总时，SKIP 状态不影响最终 PASS/FAIL 判定
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: verify-deployment.py 中 neural_compressor 不在必选 packages 列表中
  - `programmatic` TR-2.2: 在无 INC 环境中运行 verify-deployment.py，退出码为 0（成功），neural_compressor 状态为 SKIP
  - `programmatic` TR-2.3: 在有 INC 环境中运行 verify-deployment.py，test_neural_compressor_imports 正常执行并输出结果

## [ ] Task 3: 调整 Shell 脚本中的 INC 版本检查
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - `verify-services.sh`: 将 `import neural_compressor` 和版本打印改为容错模式（2>/dev/null 或 try/except），未安装时显示 "not installed"
  - `local-build.sh`: 同理调整 NC 版本打印逻辑
  - `variants/scripts/test-onnx-quantized.sh`: `test_neural_compressor()` 函数调整：当 NC 不可导入时返回 skip 而非 fail
  - `variants/build.sh`: 检查是否有 NC 硬依赖，如有调整为可选
- **Acceptance Criteria Addressed**: AC-3, NFR-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 所有 shell 脚本中 `import neural_compressor` 均有错误重定向或 fallback
  - `programmatic` TR-3.2: 在无 INC 环境中运行 verify-services.sh 和 local-build.sh 不因 NC 缺失报错退出

## [ ] Task 4: 更新 onnx_quantize_kit 包的 __init__.py docstring 和模块注释
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 确认 `__init__.py` 的 `__all__` 导出列表无 INC 相关符号（已确认无，只需验证）
  - 更新模块 docstring，明确说明量化引擎基于 `onnxruntime.quantization`
  - 在 `quantize.py` 顶部模块注释中添加说明：本模块仅使用 onnxruntime.quantization API，不依赖 Intel Neural Compressor；INC 适用于 PyTorch 模型直接量化场景
- **Acceptance Criteria Addressed**: AC-5, AC-10
- **Test Requirements**:
  - `programmatic` TR-4.1: grep onnx_quantize_kit/ 目录，仅注释中提及 neural_compressor，无 import 语句
  - `human-judgement` TR-4.2: docstring 清晰说明工具链定位

## [ ] Task 5: 生成 ORT 量化回归测试脚本 test_ort_quantization_regression.py
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 在 `scripts/` 目录创建 `test_ort_quantization_regression.py`
  - 测试通过 onnx_quantize_kit 公共 API（auto_quantize, quantize_dynamic_simple, quantize_static_qdq, quantize_static_qoperator, quantize_fp16）进行端到端量化
  - 使用项目中已有的测试模型（models/mlp.onnx, models/cnn.onnx, models/transformer.onnx）
  - 每组测试包含：量化执行 → 精度验证（cosine_sim, max_diff）→ 性能基准 → 文件大小比较
  - 精度门禁阈值：
    - INT8 动态量化 (MLP): cosine_sim ≥ 0.999, max_diff < 0.05
    - INT8 静态 QDQ (CNN): cosine_sim ≥ 0.99, max_diff < 0.1
    - INT8 静态 QOperator (MLP): cosine_sim ≥ 0.99, max_diff < 0.1
    - FP16 (MLP/CNN): cosine_sim ≥ 0.9999, max_diff < 0.001
    - Transformer 动态量化: cosine_sim ≥ 0.99, max_diff < 0.1
  - auto_quantize 端到端测试：使用自动策略链，验证自动检测模型类型并选择策略，失败时回滚
  - 输出格式：与现有 test_onnxruntime_quantization.py 一致的 check()/pass/fail 统计格式
  - 确保脚本可独立运行（python test_ort_quantization_regression.py），不依赖 INC
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 脚本中无 `import neural_compressor` 或 `from neural_compressor`
  - `programmatic` TR-5.2: 脚本可在仅安装 onnxruntime + onnx + numpy 的环境中运行通过
  - `programmatic` TR-5.3: 覆盖 5 种量化策略（dynamic, static_qdq, static_qoperator_quint8, fp16, auto）
  - `programmatic` TR-5.4: 至少测试 2 种模型类型（MLP + Transformer 或 CNN）
  - `programmatic` TR-5.5: 所有精度断言通过（cosine_sim 和 max_diff 阈值）
  - `programmatic` TR-5.6: 脚本语法检查通过（python -m py_compile）

## [ ] Task 6: 更新文档（README.md 和 ADVANCED-QUANTIZATION-GUIDE.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 更新 `variants/onnx-quantized/README.md`：
    - 工具链概述段明确说明 onnxruntime.quantization 为唯一核心量化引擎
    - 预装包列表中 neural-compressor 标注为 "not pre-installed (optional for PyTorch)"
    - INC 导入示例代码标注为 "仅当你需要 PyTorch 高级量化时手动安装后使用"
    - 添加"为什么不默认安装 INC"的简短说明（基于七概念分析结论）
  - 更新 `variants/onnx-quantized/ADVANCED-QUANTIZATION-GUIDE.md`：
    - 检查是否有将 INC 作为主要 ONNX 量化方案的描述，调整为 ORT 主力、INC PyTorch-only
  - 更新 `.agents/rules/dockerfile.md`（如存在硬编码 INC 为必需包的描述则调整）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-6.1: 文档一致表述 ORT 为主力量化方案
  - `human-judgement` TR-6.2: INC 明确定位为 PyTorch 场景可选扩展
  - `programmatic` TR-6.3: README.md 中安装命令示例不包含 neural-compressor（除非在可选安装段落）

## [ ] Task 7: 集成回归测试到 Dockerfile 构建流程
- **Priority**: medium
- **Depends On**: Task 5, Task 1
- **Description**:
  - 在 Dockerfile Stage 3 中添加 ORTREGRESSION heredoc 块，运行 `test_ort_quantization_regression.py`
  - 该测试为必过测试（构建失败时中断构建）
  - 保留现有的 ONTUNIT 块（底层 ORT API 单元测试）
  - 保留 NCUNIT 块但标记为 optional（仅当 INC 可用时运行）
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `programmatic` TR-7.1: Dockerfile 包含运行 test_ort_quantization_regression.py 的构建步骤
  - `programmatic` TR-7.2: ORTREGRESSION 块为非容错（失败则构建失败）
  - `programmatic` TR-7.3: NCUNIT 块为条件执行（INC 不可用时 SKIP）

## [ ] Task 8: 全局验证 — 零 INC 硬依赖审计
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 在 scripts/ 目录下执行 grep 审计：所有 `import neural_compressor` 必须在以下位置之一：
    1. test_neural_compressor.py（允许，已有 SKIP 逻辑）
    2. try/except 块内（容错导入）
    3. 注释/文档字符串中
  - 验证 onnx_quantize_kit/ 目录下无任何 neural_compressor import（注释除外）
  - 验证 ci-requirements.txt 不包含 neural-compressor
  - 验证所有核心入口脚本（onnx-quantize.py, batch_quantize.py, ci_quantization_gate.py）可在无 INC 环境下正常 import
- **Acceptance Criteria Addressed**: AC-5, AC-6, NFR-5
- **Test Requirements**:
  - `programmatic` TR-8.1: grep 审计结果无违规导入
  - `programmatic` TR-8.2: python -c "from onnx_quantize_kit import auto_quantize; print('OK')" 在无 INC 环境下成功
  - `programmatic` TR-8.3: python -m py_compile 所有修改过的 .py 文件通过

## [ ] Task 9: 原子提交
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 使用 atomic-commit-cmd 技能执行原子提交
  - 遵循 Conventional Commits 规范
  - Commit message: `refactor(quantize): make onnxruntime.quantization the sole ONNX quantization engine, demote INC to optional PyTorch extension`
  - 提交前运行所有检查：py_compile、grep 审计、确认无遗留 INC 硬依赖
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-9.1: Commit message 符合 Conventional Commits 格式
  - `programmatic` TR-9.2: git status 显示所有相关变更已 staged
  - `programmatic` TR-9.3: git diff --cached 检查无意外变更
