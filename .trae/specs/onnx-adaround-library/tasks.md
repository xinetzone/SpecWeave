# Tasks

## Task 1: 包骨架与依赖声明
- [ ] 在 `external/chaos/npuusertools/xmnn/onnx_adaround/` 创建包骨架（`__init__.py` 导出公共 API）
- [ ] 创建 `pyproject.toml`：依赖仅 onnx/onnxruntime/onnxscript/numpy/Pillow，注释与配置显式排除 torch/torchvision/onnx2pytorch
- [ ] 创建 `README.md`（简介、安装、使用示例）与 `docs/api.md`（API 文档）
- [ ] 配置 ruff/flake8（PEP 8）与 pytest+coverage 配置

## Task 2: ONNX 模型加载与图级 BN 折叠
- [ ] 实现 ONNX 图遍历：识别 Conv/MatMul/Gemm 后接 BatchNormalization 的节点对
- [ ] 实现 `fold_bn`：折叠参数进权重/偏置 initializer，移除 BN 节点
- [ ] 实现权重/偏置映射表构建（node.op_type + initializer 名 → 层索引）
- [ ] 编写 `tests/test_bn_fold.py`：对照公式验证折叠后数值（绝对误差 <1e-6）

## Task 3: 量化器复刻
- [ ] 实现 `UniformAffineQuantizer`（max/mse、channel_wise、symmetric、bitwidth_refactor、round_ste、delta/zero_point）
- [ ] 实现 `AdaRoundQuantizer`（learned_hard_sigmoid、soft_targets、init_alpha、gamma/zeta/beta）
- [ ] 编写 `tests/test_quantizers.py`：与 torch 原版数值对照（绝对误差 <1e-5）

## Task 4: 轻量 numpy 自动微分引擎
- [ ] 实现自动微分支架（Tensor + 计算图 + backward）
- [ ] 实现算子前向/反向：conv2d、matmul、add、relu、sigmoid、round-ste 直通、量化/反量化
- [ ] 实现 Adam 优化器与 LinearTempDecay 温度退火
- [ ] 实现 mse/fisher_diag/fisher_full 重建损失
- [ ] 编写 `tests/test_autodiff.py`：数值差分对照梯度（相对误差 <1e-4）

## Task 5: 量化模型与层/块重建
- [ ] 实现量化模块容器（等价 QuantModule/BaseQuantBlock/AutoQuantBlock 职责）
- [ ] 实现输入/输出缓存采集（等价 save_inp_oup_data / save_grad_data / GetLayerInpOut / GetLayerGrad）
- [ ] 实现 `layer_reconstruction`（mse 为主，Adam 优化 alpha）
- [ ] 实现 `block_reconstruction`
- [ ] 编写 `tests/test_reconstruction.py`：单层重建后 MSE 下降

## Task 6: 权重融合回 ONNX 与 CLI 入口
- [ ] 实现 4/8-bit 位宽选择（shape[0]/groups >16 → 4bit，否则 8bit）
- [ ] 实现 `fuse_quant_to_onnx`：烘焙量化权重写入 initializer，保留 AdaRound/NaiveQuant 标记
- [ ] 实现 `run_adaround` 6 步流程与 argparse CLI
- [ ] 实现校准数据加载管线（Pillow+numpy 替代 torchvision）
- [ ] 编写 `tests/test_export.py`：端到端生成 out.onnx 可被 onnxruntime 加载

## Task 7: 性能与精度对照验证
- [ ] 构建 torch 原版与新版对照脚本，同一模型+校准数据跑新旧实现
- [ ] 验证最终量化权重逐元素绝对误差 <1e-3、模型输出 cosine_sim ≥0.99
- [ ] 记录转换速度与内存占用，确认不劣于原实现

## Task 8: CI 流水线
- [ ] 配置 CI（GitHub Actions 或仓库既有 CI）：pytest+coverage、ruff lint、零 torch 依赖静态检查（grep 断言）

# Task Dependencies
- [Task 2] 依赖 [Task 1]
- [Task 3] 依赖 [Task 1]
- [Task 4] 依赖 [Task 1]
- [Task 5] 依赖 [Task 3][Task 4]
- [Task 6] 依赖 [Task 2][Task 5]
- [Task 7] 依赖 [Task 6]
- [Task 8] 依赖 [Task 1]（可在任意阶段并行配置）
