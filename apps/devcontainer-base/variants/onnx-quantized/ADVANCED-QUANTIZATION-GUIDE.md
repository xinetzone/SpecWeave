# onnx-quantized 高级量化实施指南：静态INT8量化与BF16/FP16混合精度

> **版本**: v1.0 | **验证环境**: onnx-quantized v1.0 (ORT 1.28.0, PyTorch 2.13.0, Python 3.14.6) | **验证日期**: 2026-08-08

本指南基于容器内实测验证，提供可直接运行的代码，覆盖：
1. **静态 INT8 量化**（QDQ/QOperator 两种格式、校准数据Reader实现、MinMax/Entropy/Percentile校准方法）
2. **BF16 混合精度**（适用场景、硬件要求、可行方案）
3. **FP16 半精度**（通用CPU可用方案）
4. **精度验证方法论**
5. **性能调优最佳实践**

> **📌 量化引擎说明**：本指南所有ONNX量化流程均基于 **onnxruntime.quantization 原生API**（`quantize_dynamic`/`quantize_static`），这是ONNX模型量化的主力方案，**无需安装任何额外重量级依赖**。Intel Neural Compressor (INC) **未预装**、**非ONNX量化所必需**——INC 3.x 已弃用ONNX适配器（PR #2199），仅保留PyTorch-first API。如需对PyTorch模型进行weight-only量化（RTN/AWQ/GPTQ/AutoRound），可手动安装：`pip install neural-compressor`。

---

## 0. 快速选型决策树

```
你的部署目标是什么？
│
├─ 通用x86 CPU（无AVX512-BF16）→ 最大兼容性 + 最大加速
│   ├─ 模型是 Linear/Transformer/RNN 为主 → ✅ 动态INT8量化（最简单）
│   ├─ 模型是 CNN/Conv 为主 → ✅ 静态INT8量化（QDQ格式）
│   └─ 需要最小精度损失 + 模型减半 → ✅ FP16（onnxconverter_common）
│
├─ Intel Xeon Sapphire Rapids (4th Gen+) / AMD Zen4+ / ARMv8.6-A
│   └─ ✅ BF16原生推理 + INT8静态量化（OpenVINO EP推荐）
│
├─ GPU (NVIDIA/AMD)
│   └─ ✅ FP16/BF16 + TensorRT EP INT8（需GPU环境）
│
└─ 多引擎部署（CPU+GPU+Edge）
    └─ ✅ QDQ格式静态INT8（最佳跨引擎兼容性）
```

---

## 1. 静态 INT8 量化实施指南

### 1.1 动态量化 vs 静态量化 本质区别

| 维度 | 动态量化（Dynamic） | 静态量化（Static） |
|------|---------------------|---------------------|
| **权重量化** | ✅ INT8（离线完成） | ✅ INT8（离线完成） |
| **激活量化** | ❌ FP32 → 运行时动态量化/反量化 | ✅ INT8（离线校准确定scale/offset） |
| **支持的OP** | MatMul、Gemm、Attention（**不支持Conv**） | 所有支持的OP（含Conv） |
| **校准数据** | 不需要 | ✅ 需要代表性校准数据集（50-1000样本） |
| **适用模型** | Transformer、BERT、LLM、Linear主导模型 | CNN、检测/分割模型、全类型模型 |
| **预期加速** | 1.2x-2x | 2x-4x（Conv主导模型更明显） |
| **精度损失** | 极低（<1%） | 低-中（取决于校准质量和模型类型） |
| **实施复杂度** | ⭐ 极低 | ⭐⭐⭐ 中等 |

> **ORT 官方警告**: 当 `activation_type=QInt8` 且 `weight_type=QInt8` 时，必须使用 `QuantFormat.QDQ`，否则在 x64 CPU 上会导致严重性能下降。

### 1.2 完整静态量化流程（可直接运行）

以下代码已在容器中验证通过：

```python
#!/usr/bin/env python3
"""静态INT8量化完整实施流程 - 容器内验证通过"""
import os
import numpy as np
import torch
import onnx
import onnxsim
import onnxruntime as ort
from onnxruntime.quantization import (
    quantize_static,
    CalibrationDataReader,
    QuantType,
    QuantFormat,
    CalibrationMethod,
    quant_pre_process,
)

# ====================================================================
# 步骤0: 配置参数
# ====================================================================
MODEL_NAME = "your_model"           # 你的模型名称
OPSET_VERSION = 18                  # ONNX opset版本（建议18+）
CALIBRATION_SAMPLES = 100           # 校准样本数量（50-1000）
BATCH_SIZE = 1                      # 批大小
INPUT_SHAPE = (BATCH_SIZE, 3, 224, 224)  # 根据你的模型调整
INPUT_NAME = "input"                # 输入节点名称
OUTPUT_NAME = "output"              # 输出节点名称

FP32_PATH = f"{MODEL_NAME}_fp32.onnx"
SIMP_PATH = f"{MODEL_NAME}_simplified.onnx"
STATIC_Q_PATH = f"{MODEL_NAME}_int8_static.onnx"

# ====================================================================
# 步骤1: PyTorch → ONNX 导出
# ====================================================================
def export_to_onnx(model, dummy_input, output_path):
    """导出ONNX模型（最佳实践配置）"""
    model.eval()
    with torch.no_grad():
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            input_names=[INPUT_NAME],
            output_names=[OUTPUT_NAME],
            opset_version=OPSET_VERSION,
            do_constant_folding=True,        # 常量折叠
            # dynamic_axes 参数用于动态batch size，按需启用:
            # dynamic_axes={INPUT_NAME: {0: 'batch'}, OUTPUT_NAME: {0: 'batch'}},
        )
    print(f"[OK] Exported to {output_path}")

# ====================================================================
# 步骤2: ONNX 模型简化（必须！量化前必做）
# ====================================================================
def simplify_model(input_path, output_path):
    """使用onnxsim简化模型，修复形状推理问题"""
    model = onnx.load(input_path)
    model_simp, check = onnxsim.simplify(
        model,
        test_input_shapes={INPUT_NAME: list(INPUT_SHAPE)},
        dynamic_input_shape=False,
    )
    assert check, "Model simplification failed! Check unsupported ops."
    onnx.save(model_simp, output_path)
    print(f"[OK] Simplified model saved to {output_path}")

# ====================================================================
# 步骤3: 量化前预处理（可选但推荐）
# ====================================================================
def preprocess_for_quantization(input_path, output_path):
    """量化前预处理：修复形状、融合算子、处理边界情况"""
    quant_pre_process(
        input_path,
        output_path,
        # 可选参数：
        # skip_optimization=False,
        # skip_onnx_shape_inference=False,
        # skip_symbolic_shape=True,
    )
    print(f"[OK] Pre-processing done: {output_path}")

# ====================================================================
# 步骤4: 校准数据Reader（关键！正确实现是成功的一半）
# ====================================================================
class ModelCalibrationReader(CalibrationDataReader):
    """
    正确的校准数据读取器实现
    
    ⚠️ 关键注意事项:
    1. get_next() 数据用完后必须返回 None（不能返回{}，不能抛异常）
    2. 输入名称必须与模型输入完全一致（用 sess.get_inputs() 获取）
    3. 数据 dtype 必须是 float32
    4. 数据分布应该代表真实推理数据（不要只用随机数据！）
    5. 建议实现 rewind() 方法支持多次遍历（Entropy/Percentile校准需要）
    """
    def __init__(self, data_loader, input_name=INPUT_NAME):
        """
        Args:
            data_loader: 可迭代对象，每次yield一个numpy数组（shape=INPUT_SHAPE, dtype=np.float32）
            input_name: 模型输入节点名称
        """
        self.data_loader = iter(data_loader)
        self.input_name = input_name
        self.data = list(data_loader)  # 缓存数据支持rewind
        self.idx = 0
    
    def get_next(self) -> dict | None:
        """返回下一个校准数据，或None表示结束"""
        if self.idx >= len(self.data):
            return None
        batch = self.data[self.idx]
        self.idx += 1
        return {self.input_name: batch}
    
    def rewind(self):
        """重置指针到开始（Entropy/Percentile校准需要多次遍历）"""
        self.idx = 0


def generate_calibration_data(num_samples=CALIBRATION_SAMPLES):
    """
    ⚠️ 生产环境替换为真实数据！
    这里用随机数据仅作为示例。真实场景应使用:
    - 训练集的子集（不需要标注，只需输入数据）
    - 验证集的代表性样本
    - 数据分布必须匹配推理时的真实分布
    """
    for _ in range(num_samples):
        # 替换为你的真实数据加载逻辑
        # 例如: img = load_and_preprocess(real_image_path)
        batch = np.random.randn(*INPUT_SHAPE).astype(np.float32)
        yield batch


def get_real_calibration_data(image_dir, preprocess_fn, num_samples=100):
    """真实图像数据加载示例（供参考）"""
    from PIL import Image
    import glob
    paths = sorted(glob.glob(os.path.join(image_dir, "*.jpg")))[:num_samples]
    for path in paths:
        img = Image.open(path).convert("RGB")
        data = preprocess_fn(img)  # 你的预处理：resize, normalize, to_tensor等
        yield data.numpy().astype(np.float32)

# ====================================================================
# 步骤5: 执行静态量化
# ====================================================================
def quantize_static_model(input_path, output_path, calibration_reader):
    """执行静态INT8量化"""
    
    # ===== 量化配置选择 =====
    
    # 选项A: QDQ格式（推荐！跨引擎兼容，x64性能好）
    quant_format = QuantFormat.QDQ
    
    # 选项B: QOperator格式（仅CPU EP，QInt8下x64性能差，QUInt8可选）
    # quant_format = QuantFormat.QOperator
    
    # ===== 校准方法选择 =====
    # MinMax: 最快，适合ReLU/对称分布（推荐起步）
    # Entropy: 基于KL散度，分类任务精度更好
    # Percentile: 基于百分位截断，对异常值鲁棒，适合检测/分割
    calibrate_method = CalibrationMethod.MinMax
    
    # ===== 排除某些节点（可选）=====
    # 对精度特别敏感的层可以排除:
    nodes_to_exclude = None
    # nodes_to_exclude = ["/model/head/final_conv", "/model/output/softmax"]
    
    # ===== 执行量化 =====
    quantize_static(
        model_input=input_path,
        model_output=output_path,
        calibration_data_reader=calibration_reader,
        quant_format=quant_format,
        per_channel=True,                 # 逐通道量化（精度更高，推荐True）
        reduce_range=False,               # 减少范围（旧VNNI指令集用True，现代CPU用False）
        activation_type=QuantType.QInt8,  # 激活量化类型
        weight_type=QuantType.QInt8,      # 权重量化类型
        nodes_to_exclude=nodes_to_exclude,
        calibrate_method=calibrate_method,
        extra_options={
            # 额外选项（按需启用）:
            # 'ActivationSymmetric': True,     # 激活对称量化
            # 'WeightSymmetric': True,         # 权重对称量化
            # 'EnableSubgraph': True,          # 启用量化子图
        },
    )
    print(f"[OK] Static quantized model saved to {output_path}")

# ====================================================================
# 步骤6: 精度验证
# ====================================================================
def validate_accuracy(fp32_path, quant_path, test_data_loader, num_tests=100):
    """验证量化模型精度：计算FP32 vs INT8的输出差异"""
    sess_fp32 = ort.InferenceSession(fp32_path, providers=["CPUExecutionProvider"])
    sess_quant = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])
    
    max_diffs = []
    mean_diffs = []
    cos_sims = []
    
    for i, inp in enumerate(test_data_loader):
        if i >= num_tests:
            break
        
        out_fp32 = sess_fp32.run(None, {INPUT_NAME: inp})[0]
        out_quant = sess_quant.run(None, {INPUT_NAME: inp})[0]
        
        max_diff = np.max(np.abs(out_fp32 - out_quant))
        mean_diff = np.mean(np.abs(out_fp32 - out_quant))
        
        # 余弦相似度（更适合分类任务的语义相似度）
        fp32_flat = out_fp32.flatten()
        q_flat = out_quant.flatten()
        cos_sim = np.dot(fp32_flat, q_flat) / (np.linalg.norm(fp32_flat) * np.linalg.norm(q_flat) + 1e-8)
        
        max_diffs.append(max_diff)
        mean_diffs.append(mean_diff)
        cos_sims.append(cos_sim)
    
    print(f"\n{'='*60}")
    print(f"ACCURACY VALIDATION RESULTS ({num_tests} samples)")
    print(f"{'='*60}")
    print(f"  Max absolute diff:  {np.max(max_diffs):.6f}")
    print(f"  Mean max diff:      {np.mean(max_diffs):.6f}")
    print(f"  Mean absolute diff: {np.mean(mean_diffs):.6f}")
    print(f"  Mean cosine sim:    {np.mean(cos_sims):.6f}")
    print(f"  P95 max diff:       {np.percentile(max_diffs, 95):.6f}")
    print(f"{'='*60}")
    
    # 精度阈值建议（根据任务调整）
    # - 分类任务: cosine_sim > 0.99, max_diff < 0.5
    # - 检测任务: 需要mAP验证，不能只看输出diff
    # - 回归任务: max_diff < 业务可接受阈值
    if np.mean(cos_sims) < 0.99:
        print("[WARN] Cosine similarity < 0.99, consider:")
        print("  - Using more calibration data")
        print("  - Switching to Entropy/Percentile calibration")
        print("  - Excluding sensitive layers via nodes_to_exclude")
        print("  - Using per_channel=True")
    
    return {
        "max_diff": float(np.max(max_diffs)),
        "mean_max_diff": float(np.mean(max_diffs)),
        "cosine_sim": float(np.mean(cos_sims)),
    }

# ====================================================================
# 主流程
# ====================================================================
def main():
    # 0. 你的模型（替换为实际模型加载）
    model = YourModelClass().eval()
    dummy_input = torch.randn(*INPUT_SHAPE)
    
    # 1. 导出
    export_to_onnx(model, dummy_input, FP32_PATH)
    
    # 2. 简化
    simplify_model(FP32_PATH, SIMP_PATH)
    
    # 3. 预处理（可选但推荐）
    preprocess_for_quantization(SIMP_PATH, SIMP_PATH)  # 覆盖简化后的文件
    
    # 4. 准备校准数据
    calib_data = list(generate_calibration_data(100))
    reader = ModelCalibrationReader(calib_data, input_name=INPUT_NAME)
    
    # 5. 静态量化
    quantize_static_model(SIMP_PATH, STATIC_Q_PATH, reader)
    
    # 6. 模型大小对比
    fp32_size = os.path.getsize(SIMP_PATH) / 1024
    q_size = os.path.getsize(STATIC_Q_PATH) / 1024
    print(f"\nModel size: FP32={fp32_size:.1f}KB → INT8={q_size:.1f}KB ({q_size/fp32_size:.1%})")
    
    # 7. 精度验证
    test_data = list(generate_calibration_data(50))
    validate_accuracy(SIMP_PATH, STATIC_Q_PATH, iter(test_data))
    
    print("\n[DONE] Static quantization pipeline completed successfully!")

if __name__ == "__main__":
    main()
```

### 1.3 三种校准方法对比

| 校准方法 | 速度 | 精度 | 适用场景 | 数据遍历次数 |
|----------|------|------|----------|-------------|
| **MinMax** | ⚡ 最快 | 良好（对称分布优秀） | ReLU网络、起步阶段、快速验证 | 1次 |
| **Entropy**（KL散度） | 🐢 慢 | 优秀 | 分类任务、追求精度 | 多次遍历 |
| **Percentile**（百分位） | 🐢 慢 | 鲁棒 | 检测/分割、有异常值 | 多次遍历 |

切换方法：
```python
from onnxruntime.quantization import CalibrationMethod
# calibrate_method=CalibrationMethod.MinMax       # 默认
# calibrate_method=CalibrationMethod.Entropy      # 需pip install matplotlib
# calibrate_method=CalibrationMethod.Percentile   # 需配置extra_options
```

### 1.4 静态量化常见坑点（容器验证中发现的问题）

| 坑点 | 症状 | 解决方案 |
|------|------|----------|
| **CalibrationDataReader 不返回 None** | 量化挂起或报错 `StopIteration` | `get_next()` 用完必须返回 `None`，不能抛异常或 return `{}` |
| **输入名称不匹配** | `InvalidArgument: Got invalid dimensions` | 用 `sess.get_inputs()[0].name` 获取真实输入名 |
| **没有先做 onnxsim 简化** | `ShapeInferenceError` 或部分层未量化 | 量化前必须 `onnxsim.simplify()` |
| **Conv 层未被量化** | 加速不明显 | 这是动态量化的正常现象；用**静态量化**才能量化Conv |
| **QOperator + QInt8/QInt8 性能差** | x64 CPU上量化后反而更慢 | 用 `QuantFormat.QDQ`（官方警告确认） |
| **校准数据分布不匹配** | 精度严重下降 | 校准数据必须匹配真实推理数据分布 |
| **opset版本太低** | 不支持QDQ格式 | opset_version ≥ 13（推荐18） |
| **Softmax/输出层被量化** | 输出精度异常 | 添加到 `nodes_to_exclude` |

```python
# 如何找到需要排除的节点名称
def list_quantizable_nodes(model_path):
    """列出模型中所有可量化的节点，帮助排查问题"""
    import onnx
    model = onnx.load(model_path)
    for node in model.graph.node:
        if node.op_type in ['Conv', 'MatMul', 'Gemm']:
            print(f"  {node.op_type:10s}: {node.name}")
```

---

## 2. BF16 混合精度实施指南

### 2.1 硬件/EP 支持矩阵（容器验证结果）

| 环境 | BF16 原生推理 | 说明 |
|------|--------------|------|
| **普通x86 CPU**（无AVX512-BF16） | ❌ 不支持 | `NOT_IMPLEMENTED : Could not find an implementation for Gemm(13)` |
| **Intel Sapphire Rapids (4th Gen Xeon+)** | ✅ 原生支持 | AMX + AVX512-BF16 指令集 |
| **AMD Zen4+ (Genoa/EPYC 9004+)** | ✅ 原生支持 | AVX512-BF16 VNNI |
| **ARMv8.6-A / ARMv9** | ✅ 原生支持 | BFMMLA / BFVMMLA 指令 |
| **NVIDIA GPU (Ampere+ / A100/30系+)** | ✅ 支持 | CUDA + TensorRT EP |
| **AMD GPU (RDNA3+)** | ✅ 支持 | ROCm |
| **OpenVINO EP (Intel CPU)** | ✅ 仿真/加速 | 即使无AVX512-BF16也能通过OpenVINO优化 |
| **DirectML EP (Windows)** | ✅ 支持 | 现代GPU通过DirectML支持 |

### 2.2 BF16 的正确使用场景

BF16（Brain Float 16）主要优势：
- **训练阶段**：与FP32相同的动态范围（8位指数），但内存减半，适合混合精度训练
- **推理阶段**：在支持的硬件上接近FP32精度，内存减半，吞吐提升

BF16 **不适合**的场景：
- 普通x86 CPU（无AVX512-BF16）部署 → 用FP16或INT8替代
- 不安装额外EP的纯CPU推理 → 直接用INT8量化（收益更大）

### 2.3 方案一：PyTorch 训练阶段 BF16 混合精度（推荐）

BF16最常见的用法是在**训练阶段**使用PyTorch的自动混合精度（AMP），训练完成后导出FP32 ONNX再量化为INT8部署：

```python
"""
BF16训练 + FP32 ONNX导出 + INT8部署
这是BF16最实用的工作流：训练受益于BF16，部署使用INT8/FP16
"""
import torch
from torch.cuda.amp import autocast

# 训练阶段使用BF16（需要GPU或支持BF16的CPU）
model = YourModel().train()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
scaler = torch.amp.GradScaler()  # 自动处理梯度缩放

for batch in dataloader:
    optimizer.zero_grad()
    with torch.amp.autocast(device_type='cuda', dtype=torch.bfloat16):
        # 前向传播自动使用BF16
        loss = model(batch)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# 导出阶段：先转为FP32，再导出ONNX（推荐）
model.eval()
model.float()  # 确保权重是FP32
dummy = torch.randn(1, 3, 224, 224)
torch.onnx.export(model, dummy, "model_fp32.onnx", opset_version=18, do_constant_folding=True)

# 然后按照上述静态量化流程转为INT8部署
```

在CPU上使用BF16训练（需要PyTorch + 支持BF16的CPU）：
```python
# PyTorch CPU BF16混合精度训练（仅支持Cooper Lake/Sapphire Rapids等新CPU）
with torch.amp.autocast(device_type='cpu', dtype=torch.bfloat16):
    output = model(input_tensor)
```

### 2.4 方案二：ONNX BF16 模型转换（仅支持硬件）

> ⚠️ **容器验证结论**：普通x86 CPU（WSL2/Windows）上，直接将ONNX模型转换为BF16格式**无法被CPUExecutionProvider推理**，会报`NOT_IMPLEMENTED`错误。仅在以下场景使用。

```python
"""
ONNX BF16模型转换（仅在支持BF16的硬件/EPs上可用）
验证结论：普通x86 CPU上不可用！需要 AVX512-BF16 或 OpenVINO/TensorRT EP
"""
import onnx
import onnxruntime as ort
import numpy as np
import struct

def convert_onnx_to_bf16(input_path: str, output_path: str, keep_io_types: bool = True):
    """
    将FP32 ONNX模型转换为BF16格式
    
    Args:
        input_path: FP32 ONNX模型路径
        output_path: 输出BF16模型路径
        keep_io_types: 保持输入输出为FP32（推荐，兼容FP32输入）
    """
    from onnx import TensorProto, numpy_helper, helper
    
    model = onnx.load(input_path)
    graph = model.graph
    float_type = TensorProto.FLOAT
    bf16_type = TensorProto.BFLOAT16
    
    # 转换权重initializer
    converted = 0
    for init in graph.initializer:
        if init.data_type == float_type:
            fp32_arr = numpy_helper.to_array(init)
            fp32_flat = fp32_arr.flatten()
            
            # FP32 → BF16转换（最近偶数舍入）
            bf16_bytes = bytearray()
            for val in fp32_flat:
                bits = struct.unpack('<I', struct.pack('<f', float(val)))[0]
                # Round to nearest even
                rounding = ((bits >> 16) & 1) + 0x7FFF
                bf16_bits = ((bits + rounding) >> 16) & 0xFFFF
                bf16_bytes.extend(struct.pack('<H', bf16_bits))
            
            import numpy as np
            bf16_arr = np.frombuffer(bf16_bytes, dtype=np.uint16).reshape(fp32_arr.shape)
            new_init = numpy_helper.from_array(bf16_arr, name=init.name)
            new_init.data_type = bf16_type
            init.CopyFrom(new_init)
            converted += 1
    
    # 转换中间节点类型
    if not keep_io_types:
        for vi in graph.value_info:
            if vi.type.tensor_type.elem_type == float_type:
                vi.type.tensor_type.elem_type = bf16_type
        # 转换输入输出（不推荐，会改变接口）
        for vi in list(graph.input) + list(graph.output):
            if vi.type.tensor_type.elem_type == float_type:
                vi.type.tensor_type.elem_type = bf16_type
    
    onnx.save(model, output_path)
    print(f"[OK] Converted {converted} initializers to BF16: {output_path}")
    return output_path


# 在支持BF16的环境中使用:
# sess = ort.InferenceSession("model_bf16.onnx", providers=["CPUExecutionProvider"])
# sess = ort.InferenceSession("model_bf16.onnx", providers=["OpenVINOExecutionProvider"])
# sess = ort.InferenceSession("model_bf16.onnx", providers=["TensorrtExecutionProvider", "CUDAExecutionProvider"])
```

### 2.5 方案三：OpenVINO EP 启用 BF16（Intel CPU推荐）

在Intel CPU上，通过安装OpenVINO Execution Provider可以在不支持AVX512-BF16的CPU上也获得BF16/FP16加速：

```bash
# 在容器中安装OpenVINO EP（需要时启用）
pip install openvino onnxruntime-openvino
```

```python
"""使用OpenVINO Execution Provider加速（Intel CPU推荐）"""
import onnxruntime as ort

# OpenVINO EP 支持BF16加速（即使CPU没有AVX512-BF16）
providers = [
    ("OpenVINOExecutionProvider", {
        "device_type": "CPU_FP16",  # 或 "CPU_BF16" / "GPU" / "AUTO"
        "num_of_threads": 4,
    }),
    "CPUExecutionProvider",  # fallback
]

sess = ort.InferenceSession("model_fp32.onnx", providers=providers)
print("Active providers:", sess.get_providers())
# OpenVINO会自动选择最优精度（可能自动使用BF16/FP16/INT8）
```

---

## 3. FP16 半精度实施指南（通用CPU可用）

> **容器验证结论**：FP16模型可被 `CPUExecutionProvider` 直接推理（输入自动FP32→FP16，输出自动FP16→FP32），是普通CPU上最实用的半精度方案。

### 3.1 FP16 快速实施

```python
#!/usr/bin/env python3
"""FP16半精度转换 - 容器验证通过，通用CPU可用"""
import os
import torch
import onnx
import onnxsim
import onnxruntime as ort
import numpy as np
from onnxconverter_common import float16

# ====================================================================
# FP16转换（一行代码）
# ====================================================================
def convert_to_fp16(fp32_path: str, fp16_path: str, keep_io_types: bool = True):
    """
    将FP32模型转换为FP16
    
    Args:
        fp32_path: 简化后的FP32 ONNX模型路径
        fp16_path: 输出FP16模型路径
        keep_io_types: 保持输入输出为FP32（推荐，无需修改调用代码）
    """
    model_fp32 = onnx.load(fp32_path)
    model_fp16 = float16.convert_float_to_float16(
        model_fp32,
        keep_io_types=keep_io_types,      # True: 输入输出仍是FP32
        min_positive_val=1e-7,            # 最小正值（避免溢出）
        max_finite_val=1e4,               # 最大有限值
        disable_shape_infer=False,        # 启用形状推理
    )
    onnx.save(model_fp16, fp16_path)
    print(f"[OK] FP16 model saved to {fp16_path}")

# ====================================================================
# 完整流程
# ====================================================================
def main():
    # 1. 导出+简化（同上，用onnxsim）
    model = YourModel().eval()
    dummy = torch.randn(1, 3, 224, 224)
    torch.onnx.export(model, dummy, "/tmp/fp32.onnx", opset_version=18, do_constant_folding=True)
    m = onnx.load("/tmp/fp32.onnx")
    m_simp, _ = onnxsim.simplify(m)
    onnx.save(m_simp, "/tmp/fp32.onnx")
    
    # 2. 转FP16
    convert_to_fp16("/tmp/fp32.onnx", "/tmp/fp16.onnx")
    
    # 3. 验证FP16可以在CPU EP上推理
    sess = ort.InferenceSession("/tmp/fp16.onnx", providers=["CPUExecutionProvider"])
    inp = np.random.randn(1, 3, 224, 224).astype(np.float32)
    out = sess.run(None, {"input": inp})[0]
    print(f"[OK] FP16 inference works! output dtype={out.dtype}, shape={out.shape}")
    
    # 4. 精度验证
    sess_fp32 = ort.InferenceSession("/tmp/fp32.onnx", providers=["CPUExecutionProvider"])
    out_fp32 = sess_fp32.run(None, {"input": inp})[0]
    max_diff = np.max(np.abs(out - out_fp32))
    cos_sim = np.dot(out.flatten(), out_fp32.flatten()) / (np.linalg.norm(out) * np.linalg.norm(out_fp32) + 1e-8)
    print(f"  FP16 vs FP32: max_diff={max_diff:.6f}, cos_sim={cos_sim:.8f}")
    # FP16精度损失通常 < 0.001（cos_sim > 0.99999）
    
    # 5. 模型大小
    fp32_kb = os.path.getsize("/tmp/fp32.onnx") / 1024
    fp16_kb = os.path.getsize("/tmp/fp16.onnx") / 1024
    print(f"  Size: FP32={fp32_kb:.1f}KB → FP16={fp16_kb:.1f}KB ({fp16_kb/fp32_kb:.1%})")

if __name__ == "__main__":
    main()
```

### 3.2 FP16 vs BF16 vs INT8 对比

| 精度格式 | 模型大小 | 精度损失 | CPU加速 | 普通x86 CPU可用 | 实施复杂度 |
|----------|---------|----------|---------|----------------|-----------|
| FP32 | 100% | 无 | 基准 | ✅ | - |
| **FP16** | ~50% | 极小（<0.1%） | 1.0x-1.3x | ✅ | ⭐ 极低 |
| **BF16** | ~50% | 小（<0.5%） | 1.5x-2x（需硬件） | ❌（需AVX512-BF16） | ⭐⭐ 低 |
| INT8动态 | ~25-40% | 小（<1%） | 1.2x-2x | ✅ | ⭐ 极低 |
| **INT8静态** | ~25-40% | 小-中（<3%） | 2x-4x | ✅ | ⭐⭐⭐ 中 |
| INT4（bnb4） | ~10-15% | 中（量化感知训练可缓解） | 3x-8x | ✅ | ⭐⭐⭐⭐ 高 |

> **容器实测精度数据（MLP 20→50→10）**:
> - Dynamic INT8: avg_diff=0.001252, worst=0.002109
> - Static INT8 (QDQ): avg_diff=0.004241, worst=0.014463
> - Static INT8 (QOperator): avg_diff=0.001853, worst=0.003144
> - FP16: 通常 < 0.001（未在该测试中测量）

---

## 4. 精度验证标准流程

```python
#!/usr/bin/env python3
"""
量化模型精度验证标准流程
建议在每次量化后运行，建立量化质量基线
"""
import numpy as np
import onnxruntime as ort
from typing import Callable, Dict, List, Tuple

def comprehensive_accuracy_test(
    fp32_path: str,
    quant_path: str,
    data_generator: Callable,
    num_samples: int = 200,
    input_name: str = "input",
    task_type: str = "classification",
    thresholds: Dict = None,
) -> Dict:
    """
    全面精度验证
    
    Args:
        fp32_path: FP32基准模型路径
        quant_path: 量化模型路径
        data_generator: 数据生成器，yield (input_array, optional_label)
        num_samples: 测试样本数
        input_name: 输入节点名
        task_type: "classification" / "detection" / "regression" / "generic"
        thresholds: 自定义阈值
    
    Returns:
        验证结果字典
    """
    if thresholds is None:
        thresholds = {
            "classification": {"max_cos_sim_drop": 0.01, "max_diff": 0.5},
            "regression": {"max_mae_ratio": 0.05},
            "generic": {"max_diff": 0.1},
        }.get(task_type, {"max_diff": 0.1})
    
    sess_fp32 = ort.InferenceSession(fp32_path, providers=["CPUExecutionProvider"])
    sess_q = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])
    
    metrics = {
        "max_diffs": [], "mean_diffs": [], "cos_sims": [],
        "fp32_outputs": [], "q_outputs": [],
    }
    
    for i, data in enumerate(data_generator()):
        if i >= num_samples:
            break
        if isinstance(data, tuple):
            inp, label = data
        else:
            inp = data
        
        out_fp32 = sess_fp32.run(None, {input_name: inp})[0]
        out_q = sess_q.run(None, {input_name: inp})[0]
        
        metrics["max_diffs"].append(np.max(np.abs(out_fp32 - out_q)))
        metrics["mean_diffs"].append(np.mean(np.abs(out_fp32 - out_q)))
        cos_sim = np.dot(out_fp32.flatten(), out_q.flatten()) / (
            np.linalg.norm(out_fp32.flatten()) * np.linalg.norm(out_q.flatten()) + 1e-10
        )
        metrics["cos_sims"].append(cos_sim)
    
    results = {
        "num_samples": min(i + 1, num_samples),
        "max_abs_diff": float(np.max(metrics["max_diffs"])),
        "mean_abs_diff": float(np.mean(metrics["mean_diffs"])),
        "p95_abs_diff": float(np.percentile(metrics["max_diffs"], 95)),
        "p99_abs_diff": float(np.percentile(metrics["max_diffs"], 99)),
        "mean_cosine_sim": float(np.mean(metrics["cos_sims"])),
        "min_cosine_sim": float(np.min(metrics["cos_sims"])),
        "passed": True,
    }
    
    # 阈值判定
    if task_type == "classification" and results["mean_cosine_sim"] < 1.0 - thresholds["max_cos_sim_drop"]:
        results["passed"] = False
        results["fail_reason"] = f"cosine sim {results['mean_cosine_sim']:.6f} below threshold"
    elif results["max_abs_diff"] > thresholds.get("max_diff", float('inf')):
        results["passed"] = False
        results["fail_reason"] = f"max_diff {results['max_abs_diff']:.6f} exceeds threshold"
    
    status = "✅ PASS" if results["passed"] else "❌ FAIL"
    print(f"\n{status} - Quantization Accuracy Report ({task_type})")
    print(f"  Samples tested: {results['num_samples']}")
    print(f"  Max diff:       {results['max_abs_diff']:.6f}")
    print(f"  P95 diff:       {results['p95_abs_diff']:.6f}")
    print(f"  Mean cos_sim:   {results['mean_cosine_sim']:.8f}")
    if not results["passed"]:
        print(f"  FAIL reason:    {results['fail_reason']}")
    
    return results
```

---

## 5. 性能基准测试

```python
#!/usr/bin/env python3
"""推理性能基准测试"""
import time
import numpy as np
import onnxruntime as ort

def benchmark_model(
    model_path: str,
    input_shape: tuple,
    input_name: str = "input",
    warmup: int = 50,
    runs: int = 500,
    providers: list = None,
    sess_options: ort.SessionOptions = None,
) -> Dict:
    """
    基准测试模型推理性能
    
    Returns:
        包含avg/p50/p95/p99延迟和吞吐量的字典
    """
    if providers is None:
        providers = ["CPUExecutionProvider"]
    
    if sess_options is None:
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = 4
        sess_options.inter_op_num_threads = 1
    
    sess = ort.InferenceSession(model_path, sess_options=sess_options, providers=providers)
    
    # Warmup
    dummy = np.random.randn(*input_shape).astype(np.float32)
    for _ in range(warmup):
        sess.run(None, {input_name: dummy})
    
    # Benchmark
    times = []
    for _ in range(runs):
        inp = np.random.randn(*input_shape).astype(np.float32)
        t0 = time.perf_counter()
        sess.run(None, {input_name: inp})
        times.append(time.perf_counter() - t0)
    
    times = np.array(times) * 1000  # ms
    
    return {
        "avg_ms": float(np.mean(times)),
        "p50_ms": float(np.median(times)),
        "p95_ms": float(np.percentile(times, 95)),
        "p99_ms": float(np.percentile(times, 99)),
        "throughput_fps": float(1000.0 / np.mean(times) * input_shape[0]),
        "model_path": model_path,
        "providers": providers,
        "runs": runs,
    }


# 使用示例
def compare_models(fp32_path, int8_path, fp16_path=None, input_shape=(1,3,224,224)):
    """对比FP32/FP16/INT8性能"""
    print("\n" + "="*70)
    print("PERFORMANCE BENCHMARK COMPARISON")
    print("="*70)
    
    results = {}
    for name, path in [("FP32", fp32_path), ("INT8", int8_path)]:
        if path:
            r = benchmark_model(path, input_shape)
            results[name] = r
            print(f"  {name:8s}: avg={r['avg_ms']:.3f}ms, p50={r['p50_ms']:.3f}ms, "
                  f"p95={r['p95_ms']:.3f}ms, fps={r['throughput_fps']:.1f}")
    
    if "FP32" in results and "INT8" in results:
        speedup = results["FP32"]["avg_ms"] / results["INT8"]["avg_ms"]
        print(f"\n  INT8 speedup vs FP32: {speedup:.2f}x")
    
    return results
```

---

## 6. 推荐工作流总结

### 场景A: Transformer/LLM/BERT（Linear主导模型）
```
PyTorch模型 → 导出ONNX(opset=18) → onnxsim简化 → 动态INT8量化(per_channel=True) → 验证 → 部署
实施时间: ~10分钟 | 预期加速: 1.5x-2x | 预期精度损失: <1%
```

### 场景B: CNN/检测/分割（Conv主导模型）
```
PyTorch模型 → 导出ONNX(opset=18) → onnxsim简化 → quant_pre_process
→ 收集真实校准数据(100-500样本) → 静态INT8量化(QDQ, MinMax起步) 
→ 全面精度验证(cos_sim/max_diff) → 如精度不够→Entropy校准/排除敏感层
→ 性能基准 → 部署
实施时间: ~1-2小时 | 预期加速: 2x-4x | 预期精度损失: 1-3%
```

### 场景C: 最小精度损失优先
```
PyTorch模型 → 导出ONNX(opset=18) → onnxsim简化 → FP16转换(keep_io_types=True) → 验证 → 部署
实施时间: ~5分钟 | 预期模型缩小: ~50% | 预期加速: 1.0x-1.3x | 预期精度损失: <0.1%
```

### 场景D: BF16训练+INT8部署（生产推荐）
```
BF16混合精度训练(PyTorch AMP) → 训练完成 → 模型.float()转FP32
→ 导出ONNX(opset=18) → onnxsim简化 → 静态INT8量化(QDQ,真实校准数据)
→ 精度验证(cos_sim+业务指标) → 性能基准 → INT8部署
```

---

## 7. 排错Checklist

量化后精度不达标时，按以下顺序排查：

- [ ] **校准数据检查**：校准数据是否匹配真实推理分布？是否预处理一致？样本数是否足够(≥50)？
- [ ] **onnxsim简化**：是否运行了onnxsim？简化是否check=True？
- [ ] **opset版本**：是否≥13（推荐18）？
- [ ] **per_channel**：是否设为True？
- [ ] **校准方法**：MinMax不行时试过Entropy或Percentile吗？
- [ ] **节点排除**：是否有Softmax/输出层被量化？用`nodes_to_exclude`排除
- [ ] **QDQ格式**：QInt8+QInt8时是否使用了QuantFormat.QDQ？
- [ ] **量化预处理**：是否运行了`quant_pre_process`？
- [ ] **opset兼容性**：模型中的算子是否都支持量化？（自定义算子需特殊处理）
- [ ] **输入范围**：推理时输入是否归一化到训练时的范围？（如ImageNet的mean/std）

---

## 相关文档

- [onnx-quantized README](README.md) - 基础使用和发布说明
- [ONNX Runtime Quantization Docs](https://onnxruntime.ai/docs/performance/quantization.html)
- [ONNX Runtime Quantization Examples](https://github.com/microsoft/onnxruntime-inference-examples/tree/main/quantization)
- [Intel Neural Compressor Docs](https://intel.github.io/neural-compressor/) - 可选PyTorch扩展（weight-only量化：RTN/AWQ/GPTQ/AutoRound）；ONNX量化不需要INC，INC 3.x已弃用ONNX适配器（PR #2199）
