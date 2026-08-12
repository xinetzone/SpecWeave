# onnx-adaround 库（纯 ONNX 生态复刻 adaround）Spec

## Why
`d:\spaces\SpecWeave\external\chaos\npuusertools\xmnn\adaround` 依赖 `onnx2pytorch` 完成 ONNX→PyTorch 模型转换，进而依赖 torch 实现量化/BN折叠/AdaRound优化/权重融合。onnx2pytorch 存在多个功能性缺陷（Resize 的 scales 解析、固定 reshape 的 batch 坍缩、含 scales 参数的 Resize 转换不可靠等），且 torch 是重量级依赖（~2GB，非 Linux 平台不可用）。需要开发一个**完全禁用 torch、仅使用 ONNX 生态包**的新库，在模型转换、层结构映射、权重处理、推理验证等核心功能上与现有 adaround 行为一致。

## 关键决策（已与用户确认）
- **完全禁用 Torch**：新库任何模块不得 `import torch` / `import torchvision` / `import onnx2pytorch`。
- **梯度引擎**：允许依赖 ONNX 生态的梯度/自动微分扩展库；为控制供应链风险，优先内置一个轻量 numpy 自动微分子模块（覆盖量化所需算子），可选用 ONNX 梯度扩展库做前向参照。
- **存放位置**：独立新包目录，与原 `adaround` 并列，不修改原实现。

## 技术栈约束
- **允许**：`onnx`、`onnxruntime`、`onnxscript`、`numpy`、Pillow（图像加载）；ONNX 生态社区维护的梯度扩展库。
- **禁止**：`torch`、`torchvision`、`onnx2pytorch` 及任何 onnx2pytorch 衍生分支。
- 项目配置文件（`pyproject.toml`）须通过依赖声明与注释**显式声明排除 onnx2pytorch**。

## What Changes
- 新增独立 Python 包 `onnx_adaround/`（位于 `external/chaos/npuusertools/xmnn/` 下，与原 `adaround/` 并列）。
- 实现六大核心模块：模型加载与图改写（ONNX 图级 BN 折叠）、量化算子（numpy/onnxscript 实现 Conv/MatMul/Gemm/ReLU/PReLU/Resize/Reshape）、量化器（UniformAffineQuantizer / AdaRoundQuantizer）、层/块重建（layer/block reconstruction + 温度退火）、可学习 alpha 的自动微分优化引擎、权重融合回 ONNX initializer。
- 数据管线：校准数据加载（基于 Pillow + numpy，替代 torchvision）。
- CLI 入口 `run_adaround` 与原 `adaround_onnx_export.py` 的 `run_adaround` 签名/流程一致（`onnx_path`→`final_onnx_path`，6 步流程）。
- 单元测试体系：覆盖率 ≥80%，关键模块 ≥90%；PEP 8；API 文档；CI 流水线。
- **不修改**原 `adaround/` 目录任何文件。

## Impact
- Affected specs：`onnx-wiki-tutorial`（ONNX 生态知识背景）、`ort-only-quantize-refactor`（同为去重量级依赖方向）
- Affected code：
  - `external/chaos/npuusertools/xmnn/onnx_adaround/`（新增包）
  - `external/chaos/npuusertools/xmnn/onnx_adaround/pyproject.toml`（新增，声明排除 onnx2pytorch）
  - `external/chaos/npuusertools/xmnn/onnx_adaround/tests/`（新增测试）
  - `.github/workflows/`（CI，若仓库已配置）

## ADDED Requirements

### Requirement: 零 torch 依赖
系统 SHALL 使新库所有源码模块不含任何 `import torch` / `import torchvision` / `import onnx2pytorch` 语句，且 `pyproject.toml` 依赖声明仅含 ONNX 生态包。

#### Scenario: 静态检查零 torch 依赖
- **WHEN** 对 `onnx_adaround/` 执行 `grep -rE "import torch|import torchvision|from torch|from torchvision|onnx2pytorch" onnx_adaround/`
- **THEN** 无匹配（注释与文档除外），退出码非零表示无违禁导入

#### Scenario: 依赖声明排除
- **WHEN** 读取 `onnx_adaround/pyproject.toml`
- **THEN** `[project] dependencies` 不包含 torch/torchvision/onnx2pytorch，并有注释或 `exclude` 声明说明禁止原因

### Requirement: 模型加载与图级 BN 折叠
系统 SHALL 提供 ONNX 图级 BatchNorm 折叠：识别 Conv/MatMul/Gemm 后紧跟 BatchNormalization 的节点对，将 BN 参数折叠进前算子权重与偏置，并从图中移除 BN 节点。

#### Scenario: 图级 BN 折叠
- **WHEN** 加载含 `Conv→BatchNormalization` 结构的 ONNX 模型并执行折叠
- **THEN** 图中 BN 节点被移除，Conv initializer 权重已按 `w * (gamma/sqrt(var+eps))` 更新、偏置已按公式吸收

#### Scenario: 权重偏置更新正确
- **WHEN** 用 numpy 对照公式验证折叠后的 initializer
- **THEN** 与手算结果逐元素一致（绝对误差 < 1e-6）

### Requirement: 量化器（UniformAffine / AdaRound）
系统 SHALL 复刻 `UniformAffineQuantizer`（max/mse 刻度方法、channel_wise、symmetric、bitwidth_refactor、round_ste）与 `AdaRoundQuantizer`（learned_hard_sigmoid、soft_targets、init_alpha、温度退火），输出与 torch 原版一致的量化结果。

#### Scenario: 量化数值一致
- **WHEN** 用相同输入/参数分别跑新库与 torch 原版 `UniformAffineQuantizer`
- **THEN** 输出张量数值一致（绝对误差 < 1e-5），alpha 初始化一致

### Requirement: 层/块重建（AdaRound 优化）
系统 SHALL 复刻 `layer_reconstruction` 与 `block_reconstruction`：采集每层输入/输出缓存、Adam 优化可学习 alpha、relaxation round loss + 温度退火（LinearTempDecay）、mse/fisher 重建损失，迭代优化取整策略。

#### Scenario: 层重建收敛
- **WHEN** 对某 Conv 层执行 layer_reconstruction（iters>0）
- **THEN** 优化后重建损失下降、最终量化输出与浮点参照的 MSE 小于未优化前

### Requirement: 可学习 alpha 的自动微分优化引擎
系统 SHALL 提供轻量 numpy 自动微分引擎（或选用 ONNX 梯度扩展库），覆盖量化优化所需的算子前向+反向：conv2d、matmul、add、relu、sigmoid、round-ste 直通、量化/反量化。支持 Adam 优化器与 L2/relaxation 损失。

#### Scenario: 梯度正确性
- **WHEN** 用数值差分（finite difference）对照引擎对 alpha 的梯度
- **THEN** 解析梯度与数值梯度相对误差 < 1e-4

### Requirement: 权重融合回 ONNX
系统 SHALL 复刻 `fuse_quant_to_onnx`：对每个 QuantModule 按其 4/8-bit 位宽烘焙量化权重，写入对应 ONNX initializer，保留 AdaRound/NaiveQuant 标记逻辑。

#### Scenario: 融合权重写入
- **WHEN** 完成 AdaRound 后执行融合
- **THEN** 目标 initializer 的值等于量化后的权重 numpy 数组，模型可被 onnxruntime 加载推理

### Requirement: CLI 入口与 6 步流程
系统 SHALL 提供 `run_adaround(onnx_path, final_onnx_path, data_path, ...)` 与原 `adaround_onnx_export.py` 相同签名与 6 步流程（加载→构建量化模型→加载校准数据→层重建→保存ckpt→融合权重）。

#### Scenario: CLI 端到端
- **WHEN** 用校准数据目录执行 `python -m onnx_adaround --onnx_path model.onnx --final_onnx_path out.onnx --data_path cali/`
- **THEN** 生成 `out.onnx`，可被 onnxruntime 加载，且流程日志含 6 个阶段标记

### Requirement: 单元测试与 CI
系统 SHALL 建立 pytest 单元测试体系，代码覆盖率 ≥80%（关键模块：quantizer、autodiff、bn_fold 覆盖 ≥90%），遵循 PEP 8（ruff/flake8），提供 API 文档与使用示例，配置 CI 流水线执行测试与静态检查。

#### Scenario: 测试与覆盖率
- **WHEN** 执行 `pytest --cov=onnx_adaround`
- **THEN** 全部测试通过，覆盖率 ≥80%，关键模块 ≥90%

#### Scenario: 静态检查
- **WHEN** 执行 lint（ruff check onnx_adaround）
- **THEN** 无 P0/P1 级错误

### Requirement: 性能与精度指标
新库在模型转换速度与内存占用上不劣于原实现；推理精度与原实现一致，误差在可接受范围（量化输出 cosine_sim ≥0.99，重量化权重逐元素一致）。

#### Scenario: 精度对照
- **WHEN** 用同一模型、同一校准数据，分别跑新旧实现
- **THEN** 最终量化权重逐元素绝对误差 < 1e-3，模型输出 cosine_sim ≥0.99

## MODIFIED Requirements
无（原 `adaround/` 目录保持不变）。

## REMOVED Requirements
无。

## Open Questions
- [ ] ONNX 梯度扩展库选型：优先内置 numpy 自动微分引擎，是否同时集成社区 ONNX autodiff 扩展作参照（待实现阶段评估）？
- [ ] 是否需要在原 `adaround/` 提供一层兼容转发（薄适配）让旧调用方无缝迁移，还是保持完全独立？（当前按完全独立处理）
