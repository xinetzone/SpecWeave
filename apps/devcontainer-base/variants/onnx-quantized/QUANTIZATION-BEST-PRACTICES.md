# ONNX 量化最佳实践：QDQ vs QOperator 选型、精度调优与自动化基准

> **版本**: v1.0 | **面向读者**: 算法/部署工程师 | **验证环境**: ORT 1.28.0 + x64 CPU | **日期**: 2026-08-08

本文档基于 4 类模型 × 5 种精度格式的实测基准数据，沉淀 QDQ/QOperator 选型决策、精度问题诊断方法论和自动化验证流程。所有结论均有 `scripts/run_full_benchmark.py` 和 `scripts/compare_qdq_vs_qoperator.py` 的可复现数据支撑。

---

## 1. 执行摘要：核心结论速查

| 模型类型 | 推荐格式 | 加速比 | 精度损失(max_diff) | 注意事项 |
|---------|---------|--------|-------------------|---------|
| **MLP/GEMM主导**（推荐系统、Tabular） | INT8 Dynamic 或 QOperator | 4.3x-6.4x | <0.015 | Dynamic最简单；静态QOperator在大MLP上最快 |
| **CNN/Conv主导**（CV分类、检测） | INT8 Static QDQ | 1.2x-1.6x | <0.004 | QDQ格式Conv算子融合更好；Dynamic反而更慢 |
| **Transformer/Attention** | INT8 Dynamic | 1.2x-1.3x | <0.010 | ⚠️ 静态QDQ会导致严重精度灾难(max_diff=0.24)和性能退化 |
| **极小模型**(<200KB) | FP32 或 FP16 | <1.0x（INT8更慢） | - | 量化反量化开销超过计算收益 |
| **追求最小精度损失** | FP16 | 0.5x-1.8x | <0.001 | CPU上不保证加速，但模型大小减半 |

> **⚠️ 最关键的反直觉发现**：QDQ并非在所有模型上都优于QOperator。在MLP/GEMM主导模型上，QOperator（QUInt8激活+QInt8权重）反而更快（6.39x vs 4.30x）；但在CNN上QDQ领先（1.22x vs 1.13x）。

---

## 2. 基准测试方法论与可复现脚本

### 2.1 测试环境与配置

所有基准测试在统一配置下运行，保证公平对比：

```python
# 统一SessionOptions（所有模型共用，避免线程/优化级别不一致）
so = ort.SessionOptions()
so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
so.intra_op_num_threads = 4       # 固定线程数
so.inter_op_num_threads = 1
so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
sess = ort.InferenceSession(path, sess_options=so, providers=['CPUExecutionProvider'])
```

**测试参数**：Warmup=50次（消除JIT/缓存影响），正式测量=300次，报告avg/p50/p95/p99延迟。

### 2.2 自动化基准脚本

| 脚本 | 用途 | 输出 |
|------|------|------|
| [run_full_benchmark.py](../scripts/run_full_benchmark.py) | 4类模型×5格式全量对比 | JSON结果 + 控制台表格 |
| [compare_qdq_vs_qoperator.py](../scripts/compare_qdq_vs_qoperator.py) | QDQ vs QOperator专项对比 | JSON结果 + 性能差异百分比 |

**运行方式**：
```bash
# 在onnx-quantized容器内运行
cd /workspace
python scripts/run_full_benchmark.py
# 结果输出到 apps/devcontainer-base/benchmark-results.json

# QDQ/QOperator专项对比
python scripts/compare_qdq_vs_qoperator.py --model conv --shape 1,3,32,32
```

### 2.3 精度验证指标

| 指标 | 计算公式 | 阈值建议 |
|------|---------|---------|
| **max_diff** | `max(|out_fp32 - out_quant|)` | <0.01优秀，<0.05可接受，>0.1危险 |
| **cosine_sim** | `cos(out_fp32, out_quant)` | >0.999优秀，>0.99可接受，<0.95危险 |
| **speedup** | `avg_fp32_ms / avg_quant_ms` | >1.5显著加速，<1.0反而更慢 |
| **size_ratio** | `quant_size / fp32_size` | INT8~25%，FP16~50% |

---

## 3. QDQ vs QOperator 深度对比

### 3.1 本质区别

```
QDQ格式（QuantizeLinear-DequantizeLinear）:
  FP32 Input → QuantizeLinear → INT8计算 → DequantizeLinear → FP32 Output
  （量化/反量化节点显式保留在图中，便于跨引擎识别和优化）

QOperator格式（Quantized Operators）:
  FP32 Input → QLinearConv/QLinearMatMul（直接INT8算子）→ FP32 Output
  （量化算子直接替换原算子，图更简洁但跨引擎兼容性差）
```

### 3.2 x64 CPU实测性能对比

| 模型 | FP32(ms) | QDQ(ms) | QDQ加速 | QOp(ms) | QOp加速 | QDQ vs QOp |
|------|----------|---------|---------|---------|---------|------------|
| SmallMLP | 0.0069 | 0.0100 | 0.69x | 0.0088 | 0.78x | QOp快13% |
| LargeMLP | 0.2149 | 0.0500 | 4.30x | 0.0336 | **6.39x** | **QOp快49%** |
| ConvNet | 0.0699 | **0.0574** | **1.22x** | 0.0619 | 1.13x | QDQ快8% |
| Transformer | 0.3237 | 0.6819 | 0.47x | 0.3349 | 0.97x | QOp快104% |

### 3.3 QDQ精度优势但性能陷阱

**精度对比**（max_diff，越小越好）：

| 模型 | QDQ max_diff | QOp max_diff | 结论 |
|------|-------------|-------------|------|
| SmallMLP | 0.0159 | 0.0323 | QDQ精度更好 |
| LargeMLP | 0.0069 | 0.0147 | QDQ精度更好 |
| ConvNet | 0.0034 | 0.0034 | 相当 |
| Transformer | **0.2401** ⚠️ | 0.0250 | **QDQ精度崩溃，QOp正常** |

> **⚠️ 严重问题**：Transformer模型使用QDQ+per_channel=True+QInt8/QInt8时，LayerNorm的rank-1权重遇到axis=1越界（`Axis 1 is out-of-range for weight 'norm1.weight' with rank 1`），导致量化参数错误，输出误差高达0.24。QOperator使用QUInt8激活+QInt8权重配置，未触发此问题。

### 3.4 选型决策矩阵

```
你的模型主要算子类型是什么？
│
├─ Conv（卷积）为主（CNN、检测、分割）
│   └─ ✅ 选择 QDQ 格式
│      - QDQ的Conv+ReLU+MaxPool模式在x64上融合更好
│      - QDQ对Conv的per_channel量化精度更优
│      - 配置: per_channel=True, activation_type=QInt8, weight_type=QInt8
│
├─ MatMul/Gemm（全连接）为主（MLP、推荐系统）
│   └─ ✅ 选择 QOperator 格式
│      - QLinearMatMul在CPU EP上有更直接的INT8 kernel实现
│      - 大MLP上QOperator比QDQ快约50%（6.39x vs 4.30x）
│      - 配置: per_channel=True, activation_type=QUInt8, weight_type=QInt8
│
├─ Attention/LayerNorm（Transformer、BERT）
│   ├─ 优先方案：动态量化（Dynamic Quantization）
│   │  - 不量化LayerNorm和Softmax，避免精度灾难
│   │  - 自动处理MatMul/Gemm的INT8量化
│   │  - 实施最简单，无需校准数据
│   └─ 若必须静态量化：
│      - 排除LayerNorm/Softmax节点（nodes_to_exclude）
│      - 使用QOperator格式（QUInt8激活）
│      - 必须运行精度验证（QDQ在Transformer上不可用）
│
└─ 跨引擎部署（CPU+GPU+Edge+Mobile）
    └─ ✅ 选择 QDQ 格式
       - TensorRT/NNAPI/CoreML都支持QDQ格式
       - QOperator仅在ORT CPU EP上高效
       - 跨引擎兼容性优先于单引擎性能
```

### 3.5 QDQ/QOperator 配置代码模板

```python
from onnxruntime.quantization import quantize_static, QuantType, QuantFormat, CalibrationMethod

def quantize_for_conv_models(fp32_path, qdq_path, calib_reader):
    """CNN/Conv主导模型 - QDQ格式"""
    quantize_static(
        model_input=fp32_path,
        model_output=qdq_path,
        calibration_data_reader=calib_reader,
        quant_format=QuantFormat.QDQ,               # QDQ格式
        per_channel=True,
        activation_type=QuantType.QInt8,            # QInt8激活
        weight_type=QuantType.QInt8,                # QInt8权重
        calibrate_method=CalibrationMethod.MinMax,
    )

def quantize_for_mlp_models(fp32_path, qop_path, calib_reader):
    """MLP/Gemm主导模型 - QOperator格式"""
    quantize_static(
        model_input=fp32_path,
        model_output=qop_path,
        calibration_data_reader=calib_reader,
        quant_format=QuantFormat.QOperator,         # QOperator格式
        per_channel=True,
        activation_type=QuantType.QUInt8,           # QUInt8激活（关键！）
        weight_type=QuantType.QInt8,                # QInt8权重
        calibrate_method=CalibrationMethod.MinMax,
    )

def quantize_transformer_dynamic(fp32_path, dyn_path):
    """Transformer模型 - 动态量化（最安全）"""
    from onnxruntime.quantization import quantize_dynamic
    quantize_dynamic(
        model_input=fp32_path,
        model_output=dyn_path,
        weight_type=QuantType.QInt8,
        # 动态量化自动处理MatMul/Gemm，跳过LayerNorm/Softmax
    )
```

---

## 4. 精度下降诊断与调整建议

### 4.1 精度退化分级标准

基于4类模型实测数据，定义三级精度退化：

| 级别 | max_diff范围 | cos_sim范围 | 业务影响 | 典型场景 |
|------|-------------|-------------|---------|---------|
| 🟢 **可接受** | <0.01 | >0.999 | 无感知，不影响指标 | FP16、INT8 Dynamic(MLP/Trans) |
| 🟡 **需关注** | 0.01-0.05 | 0.99-0.999 | 可能影响精度敏感任务 | INT8 Static(MLP/SmallMLP QOp) |
| 🔴 **不可接受** | >0.05 | <0.99 | 输出严重错误，不可部署 | Transformer QDQ(0.24) |

### 4.2 问题诊断与修复方案

#### 问题1：Transformer/Attention模型QDQ静态量化后精度崩溃

**现象**：max_diff > 0.1，输出完全不可用，同时推理速度反而更慢。

**根因**：
1. LayerNorm的weight是rank-1向量（shape=[hidden_size]），per_channel=True + axis=1导致越界警告，量化参数计算错误
2. Softmax输出范围是[0,1]，INT8量化（scale/offset）引入极大误差
3. QDQ格式在注意力MatMul上的反量化节点插入导致额外开销

**修复方案**（按优先级排列）：

```python
# 方案A：改用动态量化（推荐，最简单）
from onnxruntime.quantization import quantize_dynamic
quantize_dynamic(fp32_path, output_path, weight_type=QuantType.QInt8)

# 方案B：静态量化 + 排除敏感节点
sensitive_nodes = [
    "/model/encoder/layer.0/norm1/ReduceMean",  # LayerNorm
    "/model/encoder/layer.0/norm2/ReduceMean",
    "/model/encoder/softmax",                     # Softmax
    "/model/head/output",                         # 输出层
]
quantize_static(
    fp32_path, output_path, calib_reader,
    quant_format=QuantFormat.QOperator,          # 用QOperator
    activation_type=QuantType.QUInt8,            # QUInt8激活
    weight_type=QuantType.QInt8,
    nodes_to_exclude=sensitive_nodes,            # 排除敏感节点
)

# 方案C：量化后检查LayerNorm警告日志
# 如果看到 "Axis X is out-of-range for weight ... with rank 1"
# 需要设置 per_channel=False 或手动修复opset版本
```

#### 问题2：小模型（<1MB）INT8量化后反而更慢

**现象**：speedup < 1.0，量化模型延迟高于FP32。

**根因**：量化/反量化（Q/DQ）操作的开销超过了INT8计算节省的时间。小模型的计算量太小，内存访问和kernel launch开销占主导。

**修复方案**：
```python
import os
fp32_size_kb = os.path.getsize(fp32_path) / 1024
if fp32_size_kb < 200:  # 小于200KB的模型
    print(f"模型仅{fp32_size_kb:.0f}KB，跳过INT8量化，使用FP32或FP16")
    # FP16虽然也不保证加速，但模型大小减半，精度损失极小
    convert_to_fp16(fp32_path, fp16_path)
```

#### 问题3：ConvNet动态量化后性能严重下降

**现象**：ConvNet INT8 Dynamic speedup = 0.46x（比FP32慢一倍以上）。

**根因**：动态量化**不支持Conv算子**，Conv权重未被量化，仍然以FP32计算；而动态量化的运行时量化/反量化开销反而增加了延迟。

**修复方案**：Conv模型必须使用**静态量化**（QDQ格式），不能使用动态量化。

```python
# ❌ 错误：ConvNet用动态量化
quantize_dynamic(conv_model_path, output_path)  # Conv不量化，速度更慢

# ✅ 正确：ConvNet用静态量化（QDQ格式）
quantize_static(conv_model_path, output_path, calib_reader,
                quant_format=QuantFormat.QDQ)   # Conv量化加速1.2-1.6x
```

#### 问题4：QOperator + QInt8/QInt8在x64 CPU上性能差

**现象**：按照某些教程配置 `activation_type=QInt8, weight_type=QInt8, quant_format=QOperator` 后，模型速度明显慢于预期。

**根因**：ORT官方警告确认——当激活和权重都是QInt8时，QOperator格式在x64 CPU上缺少优化kernel。QDQ格式对此配置有专门的QDQ→QOperator图优化pass，性能更好。

**修复方案**：
| quant_format | activation_type | weight_type | x64 CPU性能 | 推荐 |
|-------------|----------------|-------------|------------|------|
| QDQ | QInt8 | QInt8 | ✅ 良好 | ✅ 推荐组合 |
| QOperator | QUInt8 | QInt8 | ✅ 良好 | ✅ MLP/Transformer可用 |
| QOperator | QInt8 | QInt8 | ❌ 差 | ❌ 避免 |

#### 问题5：校准数据分布不匹配导致精度差

**现象**：用随机数据校准后模型精度差，但业务指标下降明显。

**根因**：校准数据分布必须与推理时真实数据一致。随机正态分布数据的scale/offset与真实图像/文本数据差异大。

**修复方案**：
```python
class RealCalibrationReader(CalibrationDataReader):
    """使用真实数据校准"""
    def __init__(self, data_dir, preprocess_fn, num_samples=200):
        self.data = []
        for path in sorted(glob.glob(f"{data_dir}/*.jpg"))[:num_samples]:
            img = Image.open(path).convert("RGB")
            tensor = preprocess_fn(img)  # 与推理时完全一致的预处理
            self.data.append({"input": tensor.numpy().astype(np.float32)})
        self.idx = 0

    def get_next(self):
        if self.idx >= len(self.data): return None
        d = self.data[self.idx]; self.idx += 1; return d

    def rewind(self): self.idx = 0
```

### 4.3 精度调优Checklist（按优先级排序）

量化精度不达标时，按此顺序排查：

1. [ ] **检查量化警告日志**：搜索 "out-of-range"、"not quantized"、"WARNING"
2. [ ] **验证校准数据**：是否使用真实数据？预处理是否与推理一致？样本≥50？
3. [ ] **检查模型类型匹配**：Conv→静态QDQ，MLP→QOperator/Dynamic，Transformer→Dynamic
4. [ ] **运行onnxsim**：量化前必须简化模型，`onnxsim.simplify(model, test_input_shapes=...)`
5. [ ] **运行quant_pre_process**：`from onnxruntime.quantization import quant_pre_process`
6. [ ] **切换校准方法**：MinMax→Entropy（分类任务）或Percentile（检测任务）
7. [ ] **排除敏感节点**：LayerNorm、Softmax、输出层用nodes_to_exclude
8. [ ] **调整量化类型**：QInt8↔QUInt8，per_channel↔per_tensor
9. [ ] **混合精度**：只量化部分层，敏感层保持FP32/FP16
10. [ ] **考虑量化感知训练（QAT）**：如果以上都无效，需要在训练时模拟量化

---

## 5. FP16在x64 CPU上的真实表现

### 5.1 实测数据

| 模型 | FP32(ms) | FP16(ms) | FP16加速 | max_diff | size_ratio |
|------|----------|----------|---------|----------|-----------|
| SmallMLP | 0.0069 | 0.0079 | 0.87x | 0.0004 | 50.2% |
| LargeMLP | 0.2149 | 0.1223 | **1.76x** | 0.0002 | 50.0% |
| ConvNet | 0.0699 | 0.1134 | 0.62x | 0.0001 | 50.0% |
| Transformer | 0.3237 | 0.6743 | 0.48x | 0.0005 | 50.1% |

### 5.2 关键发现

- **FP16精度极佳**：所有模型max_diff < 0.0005，几乎无精度损失
- **FP16在CPU上加速不稳定**：大MLP加速1.76x，但ConvNet/Transformer反而慢40-50%
- **根本原因**：x64 CPU没有原生FP16计算指令（需要AVX512-FP16或ARM SVE），当前FP16模型在CPU EP上可能是FP32仿真计算+输入输出转换
- **FP16的核心价值**：**模型大小减半**（~50%），适合内存/带宽受限场景

### 5.3 使用建议

- ✅ 当**模型大小**是主要瓶颈（边缘设备部署、模型传输）时使用FP16
- ✅ 作为INT8量化前的baseline对比
- ❌ 不要期望FP16在通用x64 CPU上带来推理加速
- ❌ BF16在普通x64 CPU上完全不可用（NOT_IMPLEMENTED错误），除非使用OpenVINO EP

---

## 6. 标准工作流：从模型到部署

### 6.1 自动化验证流水线

```python
#!/usr/bin/env python3
"""量化模型自动化验证流水线 - 团队标准流程"""
import json
import numpy as np
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, quantize_static, QuantType, QuantFormat

def quantization_pipeline(fp32_path, output_dir, model_type, calib_reader=None):
    """
    一键量化+验证+基准流水线

    Args:
        fp32_path: 简化后的FP32 ONNX模型路径
        output_dir: 输出目录
        model_type: "mlp" | "conv" | "transformer" | "tiny"
        calib_reader: 校准数据Reader（静态量化需要）
    """
    results = {}

    # 1. 根据模型类型选择量化策略
    if model_type == "tiny":
        print("[INFO] 小模型，直接使用FP16")
        # ... FP16转换
        return results

    if model_type == "transformer":
        print("[INFO] Transformer，使用动态量化")
        dyn_path = f"{output_dir}/model_int8_dynamic.onnx"
        quantize_dynamic(fp32_path, dyn_path, weight_type=QuantType.QInt8)
        results["INT8_Dynamic"] = validate_and_bench(fp32_path, dyn_path)

    elif model_type == "conv":
        print("[INFO] Conv模型，使用静态QDQ量化")
        qdq_path = f"{output_dir}/model_int8_qdq.onnx"
        quantize_static(fp32_path, qdq_path, calib_reader,
                       quant_format=QuantFormat.QDQ, per_channel=True,
                       activation_type=QuantType.QInt8, weight_type=QuantType.QInt8)
        results["INT8_QDQ"] = validate_and_bench(fp32_path, qdq_path)

    elif model_type == "mlp":
        print("[INFO] MLP模型，对比Dynamic和QOperator")
        # 动态量化
        dyn_path = f"{output_dir}/model_int8_dynamic.onnx"
        quantize_dynamic(fp32_path, dyn_path, weight_type=QuantType.QInt8)
        results["INT8_Dynamic"] = validate_and_bench(fp32_path, dyn_path)
        # 静态QOperator
        qop_path = f"{output_dir}/model_int8_qop.onnx"
        quantize_static(fp32_path, qop_path, calib_reader,
                       quant_format=QuantFormat.QOperator, per_channel=True,
                       activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)
        results["INT8_QOperator"] = validate_and_bench(fp32_path, qop_path)

    # 2. 输出验证报告
    print("\n" + "="*70)
    print(f"QUANTIZATION PIPELINE RESULTS ({model_type})")
    print("="*70)
    for name, r in results.items():
        status = "✅" if r["speedup"] > 1.0 and r["max_diff"] < 0.05 else "⚠️"
        print(f"  {status} {name:20s}: speedup={r['speedup']:.2f}x  "
              f"max_diff={r['max_diff']:.4f}  size={r['size_ratio']:.1%}")

    # 3. 自动选择最优格式
    valid = {k: v for k, v in results.items()
             if v["speedup"] > 1.0 and v["max_diff"] < 0.05}
    if valid:
        best = max(valid, key=lambda k: valid[k]["speedup"])
        print(f"\n[BEST] 推荐格式: {best} (speedup={valid[best]['speedup']:.2f}x)")
    else:
        print("\n[WARN] 无满足speedup>1.0且max_diff<0.05的量化方案，建议使用FP32/FP16")

    return results
```

### 6.2 CI集成建议

在CI流水线中加入量化验证步骤：

```yaml
# GitHub Actions示例
- name: Quantization Validation
  run: |
    python scripts/run_full_benchmark.py
    python scripts/compare_qdq_vs_qoperator.py
    # 验证基准结果的关键指标
    python -c "
import json
r = json.load(open('benchmark-results.json'))
# 断言ConvNet QDQ加速比>1.0
assert r['results']['ConvNet(CIFAR-10)']['INT8_Static_QDQ']['speedup'] > 1.0
# 断言Transformer Dynamic精度可接受
assert r['results']['Transformer(3L-256d)']['INT8_Dynamic']['max_diff'] < 0.05
print('[CI-PASS] Quantization benchmarks validated')
"
```

---

## 7. 常见误区与反模式

| 误区 | 为什么错 | 正确做法 |
|------|---------|---------|
| "QDQ总是比QOperator好" | 实测MLP上QOperator快50% | 根据算子类型选择 |
| "INT8一定比FP32快" | 小模型/Transformer QDQ反而更慢 | 先benchmark再部署 |
| "Conv模型用动态量化简单" | 动态量化不量化Conv，速度更慢 | Conv必须用静态量化 |
| "QOperator+QInt8/QInt8是标准配置" | x64 CPU上性能差 | QDQ+QInt8/QInt8 或 QOp+QUInt8/QInt8 |
| "随机数据足够校准" | 分布不匹配导致精度差 | 使用真实代表性数据 |
| "FP16在CPU上也有2x加速" | 普通x86 CPU无FP16指令，反而更慢 | FP16主要减小模型大小 |
| "BF16是FP16的升级" | 普通x86 CPU完全不支持BF16推理 | 普通CPU用FP16或INT8 |
| "静态量化总是比动态快" | Transformer静态QDQ精度崩溃且更慢 | Transformer首选动态量化 |
| 不做onnxsim直接量化 | 形状推理错误，部分层未量化 | 量化前必须onnxsim.simplify() |

---

## 8. 附录：完整基准数据表

### 8.1 延迟（ms，越小越好）

| 模型 | FP32 | FP16 | INT8_Dyn | INT8_QDQ | INT8_QOp |
|------|------|------|----------|----------|----------|
| SmallMLP | 0.0069 | 0.0079 | 0.0087 | 0.0100 | 0.0088 |
| LargeMLP | 0.2149 | 0.1223 | **0.0398** | 0.0500 | **0.0336** |
| ConvNet | 0.0699 | 0.1134 | 0.1529 | **0.0574** | 0.0619 |
| Transformer | 0.3237 | 0.6743 | **0.2625** | 0.6819 | 0.3349 |

### 8.2 加速比（vs FP32，越大越好）

| 模型 | FP16 | INT8_Dyn | INT8_QDQ | INT8_QOp |
|------|------|----------|----------|----------|
| SmallMLP | 0.87x | 0.79x | 0.69x | 0.78x |
| LargeMLP | 1.76x | 5.40x | 4.30x | **6.39x** |
| ConvNet | 0.62x | 0.46x | **1.22x** | 1.13x |
| Transformer | 0.48x | **1.23x** | 0.47x | 0.97x |

### 8.3 精度误差max_diff（vs FP32，越小越好）

| 模型 | FP16 | INT8_Dyn | INT8_QDQ | INT8_QOp |
|------|------|----------|----------|----------|
| SmallMLP | 0.0004 | 0.0091 | 0.0159 | 0.0323 |
| LargeMLP | 0.0002 | 0.0040 | 0.0069 | 0.0147 |
| ConvNet | 0.0001 | 0.0029 | 0.0034 | 0.0034 |
| Transformer | 0.0005 | 0.0094 | **0.2401** 🔴 | 0.0250 |

---

## 相关资源

- [ADVANCED-QUANTIZATION-GUIDE.md](ADVANCED-QUANTIZATION-GUIDE.md) - 高级量化实施指南（含完整代码）
- [run_full_benchmark.py](../scripts/run_full_benchmark.py) - 全量基准测试脚本
- [compare_qdq_vs_qoperator.py](../scripts/compare_qdq_vs_qoperator.py) - QDQ/QOperator对比脚本
- [benchmark-report.html](../benchmark-report.html) - 交互式性能对比图表
- [ONNX Runtime Quantization Docs](https://onnxruntime.ai/docs/performance/quantization.html)
