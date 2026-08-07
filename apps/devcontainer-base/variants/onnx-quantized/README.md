# onnx-quantized 变体

ONNX 模型量化工具链变体，基于 onnx-pytorch 构建，提供完整的模型量化能力。

## 功能特性

- **动态量化（Dynamic Quantization）**：INT8 权重量化，适合 RNN/Transformer
- **静态量化（Static Quantization）**：INT8 权重+激活量化，需校准数据集
- **QDQ 格式**：QuantizeLinear-DequantizeLinear 节点格式，兼容更多推理引擎
- **FP16 半精度**：权重转换为 FP16，减少 50% 模型大小
- **Intel Neural Compressor**：支持 PTQ/QAT、自动精度调优、混合精度
- **onnxruntime-tools**：BERT 等模型专用优化器和量化器
- **onnxconverter-common**：ONNX 模型转换和 float16 转换工具

## 快速开始

```bash
# 构建（国内源）
bash variants/build.sh --variant onnx-quantized --cn

# 验证
docker run --rm devcontainer-base:onnx-quantized-latest \
  python -c "
from onnxruntime.quantization import quantize_dynamic, QuantType
import torch, onnx, numpy as np

# 创建并导出模型
class M(torch.nn.Module):
    def forward(self, x): return x * 2 + 1
torch.onnx.export(M().eval(), torch.randn(1,3), '/tmp/m.onnx', opset_version=13)

# 动态INT8量化
quantize_dynamic('/tmp/m.onnx', '/tmp/m_int8.onnx', weight_type=QuantType.QInt8)
print('量化成功!')
"
```

## 量化工具快速参考

```python
# 1. 动态量化（最简单，无需校准数据）
from onnxruntime.quantization import quantize_dynamic, QuantType
quantize_dynamic("model.onnx", "model_int8.onnx", weight_type=QuantType.QInt8)

# 2. FP16 转换
from onnxconverter_common import float16
import onnx
model = onnx.load("model.onnx")
model_fp16 = float16.convert_float_to_float16(model)
onnx.save(model_fp16, "model_fp16.onnx")

# 3. Intel Neural Compressor 静态量化
from neural_compressor import quantization
from neural_compressor.config import PostTrainingQuantConfig
config = PostTrainingQuantConfig(approach="static")
q_model = quantization.fit("model.onnx", config, calib_dataloader=dataloader)
q_model.save("model_int8_static.onnx")
```

## 依赖链

```
base → conda → conda-llvm → onnx-pytorch → onnx-quantized
```

## 验证命令

```bash
# 版本检查
python -c "import onnxruntime; from onnxruntime.quantization import quantize_dynamic; print('ORT:', onnxruntime.__version__)"
python -c "import neural_compressor; print('INC:', neural_compressor.__version__)"
python -c "import onnxconverter_common; print('OCC:', onnxconverter_common.__version__)"

# 量化冒烟测试
python -c "
import torch, onnx, onnxruntime as ort, numpy as np
from onnxruntime.quantization import quantize_dynamic, QuantType
class M(torch.nn.Module):
    def forward(self, x): return self.fc(x)
    def __init__(self): super().__init__(); self.fc=torch.nn.Linear(10,5)
torch.onnx.export(M().eval(), torch.randn(1,10), '/t.onnx', opset_version=13, input_names=['i'], output_names=['o'])
quantize_dynamic('/t.onnx', '/t_q.onnx', weight_type=QuantType.QInt8)
s=ort.InferenceSession('/t_q.onnx'); o=s.run(None,{'i':np.random.randn(1,10).astype(np.float32)})[0]
print('量化推理OK, output shape:', o.shape)
"
```
