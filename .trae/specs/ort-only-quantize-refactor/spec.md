# ORT-Only 量化方案重构 - Product Requirement Document

## Overview
- **Summary**: 将 `onnx-quantized` DevContainer 变体中的量化工具链从"双方案（ORT + INC）"重构为"onnxruntime.quantization 为唯一核心量化方案，INC 降级为可选扩展（仅限PyTorch场景）"。核心变更包括：从 Dockerfile 移除 `neural-compressor` 必装依赖、调整部署验证脚本将 INC 标记为可选、更新文档定位、补充 ORT 量化方案的全面回归测试。
- **Purpose**: 根据 INC 3.x vs onnxruntime 生产部署对比分析结论（ORT 在 ONNX 模型生产部署场景全面胜出：零额外依赖、推理引擎 100% 兼容、API 稳定、供应链风险最低），消除不必要的重量级依赖（neural-compressor 拉入 PyTorch ~2GB），精简镜像体积，明确工具链定位，降低维护成本。
- **Target Users**: 使用 devcontainer-base onnx-quantized 变体进行 ONNX 模型量化部署的开发者、CI/CD 流水线维护者。

## Goals
- 从 Dockerfile 移除 `neural-compressor` 作为必装依赖，大幅减小镜像体积
- 将所有部署验证/构建脚本中的 INC 检查从"必选/FAIL"改为"可选/SKIP"
- 更新文档（README、ADVANCED-QUANTIZATION-GUIDE），明确 ORT 为主力量化方案，INC 降级为可选扩展
- 生成一份全面的 ORT 量化方案回归测试脚本，覆盖动态/静态/QDQ/QOperator/FP16 全策略，含精度门禁
- 确保 onnx_quantize_kit 包的公共 API 入口函数零 INC 依赖
- 保留 `test_neural_compressor.py` 作为可选 PyTorch 场景测试（自动跳过当 INC 未安装）
- 原子提交，遵循 Conventional Commits 规范

## Non-Goals (Out of Scope)
- 不删除 onnx_quantize_kit 中已有的 ORT 量化逻辑（已经是 ORT-only，无需修改核心逻辑）
- 不删除 `test_neural_compressor.py`（保留作为 PyTorch 高级量化场景的可选测试）
- 不修改 onnx-pytorch 基础变体（该变体已经包含 PyTorch，INC 可在其上追加）
- 不引入新的量化算法库（如 onnxruntime-tools 的量化器被 ORT 内置 API 替代）
- 不重构 onnx_quantize_kit 内部模块架构（已正确分层）

## Background & Context
- **前期分析结论**（七概念方法论 I→F→V 链路产出）：
  - onnxruntime.quantization 在 ONNX 生产部署 10 维度加权得分 **8.1/10**，INC 3.x 在 ONNX 场景仅 **5.9/10**
  - INC 3.x 已战略性放弃 ONNX adaptor（PR #2199 标记 deprecated），ONNX 支持被剥离到独立 fork（仅 30 次 commit，成熟度低）
  - INC 3.x 重构为 PyTorch-first 的框架专属 API，`PostTrainingQuantConfig` 已不存在
  - INC 强制依赖 PyTorch（~2GB），大幅增加镜像体积和供应链攻击面
- **现状事实**：
  - `onnx_quantize_kit/` 核心包（quantize.py/calibration.py/accuracy.py/benchmark.py/model_detect.py/reporting.py/cli.py）已 100% 使用 ORT API，无 INC 导入
  - `ci-requirements.txt` 不包含 neural-compressor
  - Dockerfile Stage 2 将 neural-compressor 作为 pip 必装包
  - verify-deployment.py 将 neural_compressor 列为必导包（导入失败标记 FAIL）
  - 现有 test_onnxruntime_quantization.py 已有 58 项测试，但缺少以 onnx_quantize_kit 公共 API 为入口的端到端回归测试

## Functional Requirements
- **FR-1**: Dockerfile 不再将 `neural-compressor` 作为必装包；从 pip install 列表移除，保留注释说明其作为可选扩展的安装方式
- **FR-2**: Dockerfile Stage 3 冒烟测试中，NC 版本检查和 API 导入测试调整为可选（SKIP 而非 FAIL）
- **FR-3**: `verify-deployment.py` 中 `test_imports()` 将 neural_compressor 从必选包列表移至可选包列表（导入失败标记 SKIP 而非 FAIL）
- **FR-4**: `verify-deployment.py` 中 `test_neural_compressor_imports()` 保留但标注为 optional；当 INC 未安装时优雅跳过
- **FR-5**: `verify-services.sh` 和 `local-build.sh` 中的 INC 版本打印调整为可选（未安装时显示 "not installed" 而非报错）
- **FR-6**: Dockerfile 的 LABEL 和注释中更新工具链描述，明确 ORT 为核心量化引擎
- **FR-7**: 更新 Dockerfile build-info 输出，将 NC_VERSION 从必填字段改为条件字段
- **FR-8**: 生成 `test_ort_quantization_regression.py` 回归测试脚本，通过 onnx_quantize_kit 公共 API 测试全策略链
- **FR-9**: README.md 中更新工具链说明，明确 ORT 为唯一主力量化方案，INC 定位为 PyTorch 可选扩展
- **FR-10**: onnx_quantize_kit 的 `__init__.py` 导出列表确认无 INC 相关符号，docstring 更新工具链描述

## Non-Functional Requirements
- **NFR-1 (镜像体积)**: onnx-quantized 变体镜像体积应比当前版本显著减小（移除 neural-compressor + PyTorch 依赖后预计减少 1.5-2GB）
- **NFR-2 (构建速度)**: 移除 neural-compressor 后 pip install 阶段应更快（减少大包下载）
- **NFR-3 (精度门禁)**: 回归测试中，MLP 模型动态量化 cosine_sim ≥ 0.999，FP16 cosine_sim ≥ 0.9999
- **NFR-4 (向后兼容)**: onnx_quantize_kit 公共 API 签名不变，已有调用方（onnx-quantize.py、batch_quantize.py、ci_quantization_gate.py）无需修改
- **NFR-5 (零 INC 硬依赖)**: 除 test_neural_compressor.py（可选）外，所有核心脚本 `import neural_compressor` 必须在 try/except 内，导入失败不得导致脚本退出码非零

## Constraints
- **Technical**:
  - Python 3.10+，onnxruntime ≥ 1.20.0，onnx ≥ 1.16.0
  - 不得破坏现有 onnx_quantize_kit 公共 API 签名
  - FP16 转换依赖 onnxconverter-common（保留）
  - onnxsim 保留（量化预处理简化模型用）
  - onnxruntime-tools 评估：如其 optimizer 仍有用则保留，否则一并移除
- **Business**: 原子提交，message 遵循 Conventional Commits（`refactor(quantize): ...`）
- **Dependencies**: onnxruntime.quantization（内置，随 onnxruntime 包提供）

## Assumptions
- onnxruntime ≥ 1.20.0 的内置量化 API 已完全覆盖 INC 2.x adaptor 层在 ONNX 场景提供的能力（动态/静态/QDQ/QOperator/FP16）
- 现有用户若需要 INC PyTorch 高级量化（RTN/AWQ/GPTQ/AutoRound），可在 onnx-pytorch 基础变体之上自行 pip install neural-compressor
- onnxruntime-tools 包的 optimizer 功能已被 ORT 内置图优化（ORT_ENABLE_ALL）覆盖，非必需
- `test_neural_compressor.py` 已有完善的 SKIP 逻辑，当 INC 未安装时自动跳过全部测试

## Acceptance Criteria

### AC-1: Dockerfile 移除 neural-compressor 必装依赖
- **Given**: 当前 Dockerfile Stage 2 中 pip install 包含 neural-compressor
- **When**: 重构后重新构建镜像
- **Then**: neural-compressor 不再出现在必装列表中；pip install 命令移除该包；镜像中 `python -c "import neural_compressor"` 应失败（ImportError）
- **Verification**: `programmatic`
- **Notes**: 保留注释说明如需 PyTorch 高级量化可手动安装

### AC-2: Dockerfile 冒烟测试 INC 部分降级为可选
- **Given**: Dockerfile Stage 3 冒烟测试包含 NC 导入检查
- **When**: INC 未安装时运行构建
- **Then**: NC 相关测试标记为 SKIP/INFO 而非 FAIL；整体构建不因 NC 缺失而失败
- **Verification**: `programmatic`

### AC-3: verify-deployment.py 中 INC 检查为可选
- **Given**: 当前 test_imports() 将 neural_compressor 列为必选包
- **When**: 在未安装 INC 的环境中运行 verify-deployment.py
- **Then**: neural_compressor 导入标记为 SKIP（非 FAIL）；脚本整体不因 NC 缺失返回非零退出码
- **Verification**: `programmatic`

### AC-4: ORT 量化回归测试脚本覆盖全策略
- **Given**: 生成 test_ort_quantization_regression.py
- **When**: 在容器内运行该脚本
- **Then**: 覆盖 dynamic/static_qdq/static_qoperator/fp16 四种策略；每种策略至少测试一个模型；精度指标达标（cosine_sim ≥ 0.99 for INT8, ≥ 0.9999 for FP16）；全部测试 PASS
- **Verification**: `programmatic`

### AC-5: onnx_quantize_kit 公共 API 零 INC 依赖
- **Given**: onnx_quantize_kit 包的所有模块
- **When**: 执行 `grep -r "neural_compressor" onnx_quantize_kit/`
- **Then**: 除注释外无任何 `import neural_compressor` 或 `from neural_compressor` 语句
- **Verification**: `programmatic`

### AC-6: 核心入口脚本无 INC 硬依赖
- **Given**: onnx-quantize.py、batch_quantize.py、ci_quantization_gate.py、benchmark_quantization.py
- **When**: 在未安装 INC 的环境中运行这些脚本的 --help 或基本功能
- **Then**: 不因 ImportError 崩溃
- **Verification**: `programmatic`

### AC-7: 文档更新正确反映工具链定位
- **Given**: README.md 和 ADVANCED-QUANTIZATION-GUIDE.md
- **When**: 人工审查文档
- **Then**: 明确说明 ORT 为 ONNX 量化主力方案；INC 标注为 PyTorch 场景可选扩展；安装命令示例不包含 neural-compressor（除非标注可选）
- **Verification**: `human-judgment`

### AC-8: 原子提交符合规范
- **Given**: 所有变更完成
- **When**: 执行 git commit
- **Then**: Commit message 遵循 Conventional Commits（`refactor(quantize): make onnxruntime.quantization the sole ONNX quantization engine, demote INC to optional PyTorch extension`）；单次提交包含所有相关变更
- **Verification**: `human-judgment`

## Open Questions
- [ ] onnxruntime-tools 是否也一并移除？其 optimizer 功能是否仍有价值？（建议移除，ORT 内置图优化已覆盖）
- [ ] 是否需要在 Dockerfile 中保留一个注释块说明如何手动安装 INC（供需要 PyTorch 量化的用户）？
