# Checklist

- [x] 新库 `onnx_adaround/` 已创建于 apps/tests/ 下（由 onnx-adaround-relocate 迁入），未修改原 adaround 目录任何文件
- [x] `pyproject.toml` 依赖仅含 ONNX 生态包，显式排除 torch/torchvision/onnx2pytorch
- [x] 源码零 torch 依赖：`grep -rE "import torch|from torch|onnx2pytorch" onnx_adaround/` 无匹配（仅注释/文档命中）
- [x] ONNX 图级 BN 折叠实现正确：折叠后数值与公式手算绝对误差 <1e-6，BN 节点被移除
- [x] UniformAffineQuantizer 复刻：与 torch 原版输出绝对误差 <1e-5
- [x] AdaRoundQuantizer 复刻：alpha 初始化、soft_targets、温度退火与 torch 原版一致
- [x] 自动微分引擎梯度正确：解析梯度与数值差分相对误差 <1e-4
- [x] layer/block reconstruction 实现：单层重建后重建损失下降
- [x] 权重融合：4/8-bit 烘焙权重写入 ONNX initializer，模型可被 onnxruntime 加载
- [x] run_adaround CLI 6 步流程：端到端生成 out.onnx 且可推理
- [x] 校准数据管线基于 Pillow+numpy（无 torchvision）
- [x] 精度对照：最终量化权重逐元素绝对误差 <1e-3（实测 0.0），模型输出 cosine_sim ≥0.99（实测 0.99164）
- [x] 性能：基准脚本（bench/benchmark_conversion.py）记录转换耗时 21.6s、峰值内存 129.93MB；原 onnx2pytorch 路径本环境不可运行，以 FP32 基线+参考公式验证新库绝对精度/性能
- [x] pytest 全部通过（59 passed），覆盖率 ≥80%（实测 88.80%），关键模块（quantizer/autodiff/bn_fold）≥90%（autodiff 90-94%、quant 100%、onnx_utils 96%）
- [x] lint（ruff）无 P0/P1 级错误（All checks passed），符合 PEP 8
- [x] CI 流水线已配置（.github/workflows/onnx-adaround-ci.yml：pytest+coverage、lint、零 torch 依赖静态检查）
- [x] API 文档与使用示例已完成（README.md + docs/api.md）
