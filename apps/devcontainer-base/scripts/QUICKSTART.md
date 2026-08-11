# ONNX Quantization Toolkit — 新成员快速上手指南

> **面向读者**：刚接触 ONNX 模型量化的团队成员
> **前置知识**：基础 Python、PyTorch/ONNX 概念
> **预计阅读时间**：15 分钟
> **环境**：devcontainer-base 的 onnx-quantized 变体（或本地安装 onnxruntime ≥ 1.20）

---

## 1. 5 分钟快速体验

### 1.1 环境检查

```bash
# 确认 onnx_quantize_kit 在 Python 路径中
cd apps/devcontainer-base/scripts
python -c "from onnx_quantize_kit import auto_quantize; print('OK')"
```

如果导入失败，设置 `PYTHONPATH`：
```bash
export PYTHONPATH=$(pwd):$PYTHONPATH   # Linux/Mac
set PYTHONPATH=%CD%;%PYTHONPATH%      # Windows
```

### 1.2 第一个量化（3 行代码）

```python
from onnx_quantize_kit import auto_quantize, QuantizationConfig

# 自动选择最优策略量化你的 ONNX 模型
result = auto_quantize("your_model.onnx", "your_model_quantized.onnx")

print(f"策略: {result.strategy_used}")    # static_qdq / dynamic / fp16
print(f"精度: max_diff={result.max_diff:.6f}")
print(f"加速: {result.speedup:.2f}x")
```

运行测试套件验证环境：
```bash
python test_quantize_kit.py
# 期望输出: Results: 37 passed, 0 failed
```

---

## 2. 工具包核心概念

### 2.1 量化策略选择链

工具包采用**自动回滚机制**——如果高精度策略不满足精度要求，自动降级到更安全的策略：

```
static_qdq (最高压缩比) 
    ↓ 精度不达标
static_qoperator 
    ↓ 精度不达标
dynamic (动态量化, 无需校准数据)
    ↓ 精度不达标
fp16 (最安全, 精度损失极小)
```

### 2.2 模型类型自动检测

| 模型类型 | 推荐策略 | 原因 |
|---------|---------|------|
| **MLP**（全连接网络） | `static_qoperator` | 计算密集，静态量化效果好 |
| **CNN**（卷积网络） | `static_qdq` | QDQ 格式对 Conv 算子优化最好 |
| **Transformer** | `dynamic` 或 `fp16` | Attention/LayerNorm 对静态量化敏感，容易精度崩溃 |

### 2.3 精度验证三重门禁

每个量化结果通过三个指标验证：
1. **max_diff**：量化前后输出最大绝对误差（默认阈值 0.05）
2. **cosine_sim_min**：余弦相似度最小值（默认阈值 0.99）
3. **speedup**：推理加速比（默认 ≥1.0x，低于此值拒绝量化）

---

## 3. 常见使用场景

### 3.1 场景一：CI 流水线自动量化门禁

在 GitHub Actions 中使用 `ci_quantization_gate.py`：

```bash
# 基本用法（自动策略 + 自动回滚，非零退出码阻断流水线）
python ci_quantization_gate.py \
  --model artifacts/model.onnx \
  --output artifacts/model_int8.onnx \
  --report artifacts/quant_report.json \
  --ci
```

常用参数：
```bash
--strict         # 严格模式（max_diff<0.02, cosine>0.999）
--relaxed        # 宽松模式（max_diff<0.1, cosine>0.95）
--calib-dir ./calib_data/  # 指定校准数据目录（.npy文件）
--calib-samples 200        # 校准样本数
--benchmark-samples 500    # 性能基准测试样本数
```

退出码：
- `0`：量化成功（含回退后成功）
- `1`：所有策略均失败
- `2`：参数错误
- `3`：模型文件不存在

### 3.2 场景二：Python API 精细控制

```python
from onnx_quantize_kit import (
    auto_quantize, QuantizationConfig, 
    quantize_model, validate_accuracy, benchmark_model,
    detect_model_type, get_recommended_config,
    RandomCalibrationReader
)

# 检测模型类型
model_type = detect_model_type("model.onnx")
print(f"模型类型: {model_type}")  # mlp / cnn / transformer

# 获取推荐配置
config = get_recommended_config(model_type)
print(f"推荐策略: {config.strategy}")

# 自定义配置
custom_config = QuantizationConfig(
    strategy="dynamic",              # 强制使用动态量化
    accuracy_threshold=0.05,         # 精度阈值
    optimize_model=True,             # 量化前先优化模型
    verify_accuracy=True,            # 验证精度
    benchmark=True,                  # 运行性能基准
    num_calibration_samples=100,     # 校准样本数
    num_threads=4,                   # 推理线程数
)

result = auto_quantize("model.onnx", "model_q.onnx", config=custom_config)

if result.success:
    print(f"量化成功: {result.strategy_used}")
    print(f"加速比: {result.speedup:.2f}x")
    print(f"精度: max_diff={result.max_diff:.6f}, cosine={result.cosine_sim_min:.6f}")
    for attempt in result.all_attempts:
        print(f"  尝试: {attempt['strategy']} → {'✓' if attempt['success'] else '✗ ' + attempt.get('reason','')}")
else:
    print(f"量化失败: {result.error}")
```

### 3.3 场景三：提供校准数据

静态量化需要代表性校准数据。两种方式：

**方式一：准备 .npy 文件目录**
```python
import numpy as np
import os

calib_dir = "./calib_data"
os.makedirs(calib_dir, exist_ok=True)

# 保存 100 个真实输入样本
for i in range(100):
    sample = load_real_input(i)  # 你的真实数据
    np.save(os.path.join(calib_dir, f"calib_{i:04d}.npy"), sample)

# 运行量化（ci_gate 会自动读取目录）
# python ci_quantization_gate.py -m model.onnx -o out.onnx -d ./calib_data/
```

**方式二：自定义 CalibrationDataReader**
```python
from onnx_quantize_kit import CalibrationDataReader
import numpy as np

class MyCalibrationReader(CalibrationDataReader):
    def __init__(self, input_name, input_shape, num_samples=100):
        self.input_name = input_name
        self.input_shape = input_shape
        self.data = self._generate(num_samples)
        self.index = 0
    
    def _generate(self, n):
        # 从你的数据加载器生成校准数据
        return [
            {self.input_name: get_real_sample(i).astype(np.float32)}
            for i in range(n)
        ]
    
    def get_next(self):
        if self.index >= len(self.data):
            return None
        item = self.data[self.index]
        self.index += 1
        return item
    
    def rewind(self):
        self.index = 0
```

---

## 4. 关键文件清单

| 文件 | 用途 |
|------|------|
| `onnx_quantize_kit/__init__.py` | 包入口，导出所有公共 API |
| `onnx_quantize_kit/quantize.py` | 核心量化逻辑（auto_quantize、策略链、回滚） |
| `onnx_quantize_kit/calibration.py` | 校准数据读取器（含 RandomCalibrationReader） |
| `onnx_quantize_kit/accuracy.py` | 精度验证（max_diff、cosine_sim） |
| `onnx_quantize_kit/benchmark.py` | 性能基准测试（延迟、吞吐、百分位） |
| `onnx_quantize_kit/model_detect.py` | 模型类型自动检测（MLP/CNN/Transformer/RNN） |
| `test_quantize_kit.py` | 完整测试套件（37 个测试用例） |
| `ci_quantization_gate.py` | CI 门禁命令行工具 |
| `ci-requirements.txt` | CI 环境依赖清单 |
| `../../variants/scripts/test-onnx-quantized.sh` | Docker 镜像集成测试脚本 |
| `../../../.github/workflows/onnx-quantize-ci.yml` | GitHub Actions CI 配置 |

---

## 5. Transformer 模型量化特别指南

### 5.1 为什么 Transformer 量化容易"精度灾难"

Transformer 中的 **LayerNorm** 和 **Attention Softmax** 层对量化极其敏感：
- 静态量化使用的校准数据分布稍有偏差 → 权重/激活量化范围严重偏移
- 结果：输出变成随机噪声（max_diff 可达 1.0+，cosine_sim 甚至为负）
- 典型表现：模型输出全是 NaN 或与预期完全无关

### 5.2 工具包如何自动处理

工具包在 `detect_model_type()` 中检测到 Transformer 结构后：
1. 优先推荐 `dynamic` 或 `fp16` 策略
2. 如果强制静态量化，自动触发回滚链
3. 回滚日志中会清晰标注失败原因

```
Test 4b: Transformer static quantization disaster → auto rollback
  ❌ static_qdq     max_diff=1.84  (灾难级精度损失)
  ❌ static_qop     max_diff=1.13  (仍然不行)
  ❌ dynamic        max_diff=0.91  (接近崩溃边缘)
  ✅ fp16           max_diff=0.0007 (完美保留精度)
```

### 5.3 Transformer 量化最佳实践

1. **优先使用 FP16**：对精度要求高时，直接 `strategy="fp16"`，精度损失可忽略
2. **动态量化作为备选**：`strategy="dynamic"` 在大多数 Transformer 上效果可接受
3. **必须静态量化时**：
   - 使用**大量**真实校准数据（≥1000 样本）
   - 使用 `--exclude-nodes` 跳过 LayerNorm/Softmax 节点
   - 务必检查 `cosine_sim`（>0.99 才安全）

```python
# Transformer 推荐配置
config = QuantizationConfig(
    strategy="auto",
    accuracy_threshold=0.05,
    # 如果已知敏感节点，排除它们
    # exclude_nodes=["layernorm.weight", "softmax"]
)
```

---

## 6. 本地开发工作流

### 6.1 运行测试

```bash
# 完整测试套件
python test_quantize_kit.py

# 单个模块快速测试
python -c "
from onnx_quantize_kit import auto_quantize
# ... 你的测试代码
"
```

### 6.2 Docker 环境验证

```bash
# 构建 onnx-quantized 变体镜像
cd apps/devcontainer-base
bash variants/build.sh -v conda-llvm -t local
bash variants/build.sh -v onnx-pytorch -t local
bash variants/build.sh -v onnx-quantized -t local

# 运行镜像集成测试（含 onnx_quantize_kit L7 测试）
bash variants/scripts/test-onnx-quantized.sh --tag local
```

### 6.3 CI 模拟运行

```bash
# 模拟 CI gate
python ci_quantization_gate.py \
  -m your_model.onnx \
  -o your_model_q.onnx \
  --report report.json \
  --ci \
  --relaxed

# 检查报告
cat report.json
```

---

## 7. 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Calibration data is required for static quantization` | 静态量化需要校准数据 | 提供 `--calib-dir` 或使用 `--strategy dynamic` |
| `max_diff=X.XX` 特别大（>1.0） | 精度灾难，通常是 Transformer+静态量化 | 工具包会自动回滚，或手动指定 `--strategy fp16` |
| 所有策略都失败（exit code=1） | 模型结构特殊或数据问题 | 检查模型是否可正常推理，提供更好的校准数据 |
| `No module named 'onnx_quantize_kit'` | PYTHONPATH 未设置 | 将 scripts/ 加入 PYTHONPATH |
| 量化后速度变慢（speedup < 1.0x） | 模型太小或量化开销大于收益 | 工具包会自动拒绝，保持 FP32 模型 |

---

## 8. 进一步学习

- **ONNX Runtime 量化官方文档**：https://onnxruntime.ai/docs/performance/quantization.html
- **Intel Neural Compressor**：https://github.com/intel/neural-compressor
- **测试用例**：阅读 `test_quantize_kit.py` 中的 Test 1-6 了解所有 API 使用模式
- **CI 配置**：参考 `.github/workflows/onnx-quantize-ci.yml` 了解流水线集成方式
