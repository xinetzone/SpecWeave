# Checklist

- [ ] 新库 `onnx_adaround/` 已创建于 npuusertools/xmnn/ 下，与原 adaround 并列，未修改原目录任何文件
- [ ] `pyproject.toml` 依赖仅含 ONNX 生态包，显式排除 torch/torchvision/onnx2pytorch
- [ ] 源码零 torch 依赖：`grep -rE "import torch|from torch|onnx2pytorch" onnx_adaround/` 无匹配
- [ ] ONNX 图级 BN 折叠实现正确：折叠后数值与公式手算绝对误差 <1e-6，BN 节点被移除
- [ ] UniformAffineQuantizer 复刻：与 torch 原版输出绝对误差 <1e-5
- [ ] AdaRoundQuantizer 复刻：alpha 初始化、soft_targets、温度退火与 torch 原版一致
- [ ] 自动微分引擎梯度正确：解析梯度与数值差分相对误差 <1e-4
- [ ] layer/block reconstruction 实现：单层重建后重建损失下降
- [ ] 权重融合：4/8-bit 烘焙权重写入 ONNX initializer，模型可被 onnxruntime 加载
- [ ] run_adaround CLI 6 步流程：端到端生成 out.onnx 且可推理
- [ ] 校准数据管线基于 Pillow+numpy（无 torchvision）
- [ ] 精度对照：最终量化权重逐元素绝对误差 <1e-3，模型输出 cosine_sim ≥0.99
- [ ] 性能：转换速度与内存占用不劣于原实现
- [ ] pytest 全部通过，覆盖率 ≥80%，关键模块（quantizer/autodiff/bn_fold）≥90%
- [ ] lint（ruff）无 P0/P1 级错误，符合 PEP 8
- [ ] CI 流水线已配置（pytest+coverage、lint、零 torch 依赖静态检查）
- [ ] API 文档与使用示例已完成
