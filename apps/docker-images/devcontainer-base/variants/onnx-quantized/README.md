# onnx-quantized 变体 - 发布说明 v2.0.0

> **发布日期**: 2026-08-14 | **状态**: 🔄 架构迁移（base 从 onnx-pytorch → onnx-dev） | **Python**: 3.14.6 cp314t free-threading

ONNX 模型量化工具链变体，基于 onnxruntime.quantization 原生 API 构建，提供完整的模型量化、优化和部署能力。支持动态/静态 INT8 量化、FP16 半精度转换、QDQ 格式。

**v2.0.0 架构变更**：基础镜像从 `onnx-pytorch`（含 PyTorch，base 环境，GIL 启用）切换为 `onnx-dev`（纯 ONNX 生态，main 环境，**free-threading cp314t，GIL 禁用**）。量化测试模型全部改用 `onnx.helper` 纯 ONNX API 构建，**镜像不含 PyTorch**。Intel Neural Compressor 保持可选（需 torch，按需自装）。

---

## 📦 版本信息

| 组件 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.14.6 (cp314t) | **free-threading 构建**（main 环境，GIL 禁用） |
| **ONNX** | 1.22.0 | Open Neural Network Exchange |
| **ONNX Runtime** | 1.28.0 | 高性能推理引擎（含 quantization 模块） |
| **ONNX Script** | 0.7.1 | ONNX 脚本工具 |
| **ONNX Simplifier** | v0.7.3 | 模型简化（量化前必用） |
| **ONNX Converter Common** | 1.16.0 | float16 转换工具 |
| **LLVM/Clang** | 22.1.8 | 编译工具链（继承自 conda-llvm） |
| ~~PyTorch~~ | **已移除** | v2.0.0 起基于 onnx-dev（无 PyTorch，按需 `pip install torch`） |
| ~~onnxoptimizer~~ | **已移除** | free-threading 不兼容（CPython #111506），继承 onnx-dev 排除策略 |
| **Neural Compressor** | 可选安装 | Intel 神经压缩器（PyTorch weight-only量化，需 `pip install neural-compressor torch`） |

---

## ✅ 验证结果

本地 WSL2 Docker 环境部署验证结果（v2.0.0，构建后运行 `test-onnx-quantized.sh` 24 项测试）：

| 测试项 | 结果 | 详情 |
|--------|------|------|
| **free-threading 验证** | ✅ PASS | cp314t，GIL 禁用（`sys._is_gil_enabled() is False`） |
| **torch/onnxoptimizer 缺席** | ✅ PASS | 负向验证（by design，继承 onnx-dev） |
| **量化包导入** | ✅ PASS | onnxconverter-common/onnxsim/onnxruntime.quantization |
| **纯 ONNX 模型构建 + Checker** | ✅ PASS | onnx.helper 构建 Gemm/Relu 模型，opset=18 |
| **动态 INT8 量化** | ✅ PASS | QInt8 权重量化成功 |
| **静态 QDQ 量化** | ✅ PASS | CalibrationDataReader + MinMax 校准 |
| **FP16 半精度转换** | ✅ PASS | onnxconverter-common 正常 |
| **Neural Compressor 导入** | ⏭️ SKIP | 未预装（可选PyTorch扩展）；ONNX量化使用onnxruntime原生API |
| **基础服务继承** | ✅ PASS | SSH/Docker DinD/Jupyter/Supervisord |

**汇总**: 24 项测试（v2.0.0 结构：L1 free-threading/缺席守卫 + L2 工具链导入 + L3 纯 ONNX 量化冒烟 + L4 服务继承 + L5 PATH 优先级 + L6 build-info + L7 kit 集成）

---

## 🧪 onnx_quantize_kit 测试质量

### 测试覆盖概览

| 指标 | 值 |
|------|------|
| **测试框架** | pytest 8.4.2 |
| **总测试用例** | **195** (100% 通过) |
| ├─ 核心单元测试 | 140 |
| ├─ 集成测试 | 23 |
| └─ 专项覆盖率测试 | 32 |
| **执行时间** | < 6s |
| **核心模块覆盖率** | **96%**（quantize.py 主逻辑 ✅ 达标） |
| **工具模块平均覆盖率** | **95%+** |

### 模块覆盖率详情

| 模块 | 覆盖率 | 说明 |
|------|--------|------|
| `__init__.py` | 100% | 公共 API 导出 |
| `calibration.py` | **100%** | 校准数据读取器 |
| `benchmark.py` | 96% | 性能基准测试 |
| `reporting.py` | 96% | 测试报告生成 |
| **`quantize.py`** | **96%** ✅ | **量化核心逻辑**（专项测试覆盖回退路径/异常/边界/所有策略分支） |
| `accuracy.py` | 91% | 精度验证 |
| `model_detect.py` | 81% | 模型类型检测 |
| `cli.py` | 0% | CLI 入口（E2E 测试范围，非单元测试） |
| **整体（不含CLI）** | **94%** | 核心库代码 |
| **整体（含CLI）** | 75% | - |

### P0 Bug 验证状态

所有前序修复的 P0 级 Bug 均有对应测试用例覆盖验证：

| Bug ID | 问题描述 | 验证状态 |
|--------|----------|----------|
| **Bug #1** | 便捷函数缺少 input_shape/input_name 参数 | ✅ 已验证（detect_input_info 全套测试） |
| **Bug #2** | 动态 dim_param 维度处理不完善 | ✅ 已验证（动态 batch 替换测试） |
| **Bug #3** | CLI 默认形状硬编码为图像尺寸 | ✅ 已验证（自动检测逻辑测试） |
| **T19** | build-info BASE_IMAGE 缺少仓库前缀 | ✅ 构建时自验证拦截 |

### 测试类型覆盖

- ✅ **正常路径**：所有公共 API 标准调用
- ✅ **边界值**：warmup=0、runs=1、动态维度、极小模型、dim_value=0、未知类型
- ✅ **异常场景**：不存在文件、损坏模型、类型不兼容、缺失字段、依赖导入失败、量化异常
- ✅ **空值/None**：可选参数 None 触发自动检测、perf/acc失败时字段处理
- ✅ **参数组合**：QInt8/QUInt8、QDQ/QOperator/QInt8/QInt8Quint8/QUInt8、per_channel、MinMax/Entropy 校准
- ✅ **回退路径**：onnxsim导入失败、quant_pre_process失败、主策略精度不达标自动fallback
- ✅ **日志路径**：verbose模式打印、回滚触发警告、全策略失败日志

### 运行测试

```bash
cd scripts/

# 运行全部测试（195个用例）
python -m pytest tests/ -v

# 生成覆盖率报告（Windows环境使用独立脚本避免C扩展冲突）
python run_coverage.py
# 目标：quantize.py ≥ 95%，当前：96% ✅

# 仅专项覆盖率测试（回退/异常/边界）
python -m pytest tests/test_quantize_coverage.py -v

# 仅集成测试（静态量化主路径）
python -m pytest tests/test_quantize_integration.py -v
```

详细测试用例清单见：[test-quantize-coverage-catalog.md](../../scripts/docs/test-quantize-coverage-catalog.md)（32个专项测试用例+未覆盖代码分析）
详细覆盖率报告见：[retrospective-onnx-quantize-kit-test-coverage-20260816.md](../../../../../.agents/docs/retrospective/reports/build-engineering/retrospective-onnx-quantize-kit-test-coverage-20260816.md)

---

## 📊 量化精度对比

### 动态 INT8 量化（Gemm 层，Xavier 初始化权重）

| 指标 | FP32 | INT8 | 变化 |
|------|------|------|------|
| **权重精度** | float32 | int8 | ↓ 75% 内存占用 |
| **激活精度** | float32 | float32（动态量化） | 运行时量化/反量化 |
| **最大输出误差** | - | < 0.01（冒烟阈值 5.0） | 计算密集层典型 <1% |
| **推理结果** | 基准 | 与 FP32 对齐 | 语义一致 |
| **模型大小** | FP32 基准 | ↓ 50-75% | 权重量化直接收益 |

> **精度说明**: 
> - 对于 Gemm/Conv 等计算密集层，动态 INT8 量化通常能保持 >99% 的精度
> - 误差主要来自权重的 int8 量化（对称量化，scale 由每层权重范围决定）
> - 静态量化（需校准数据集）通常能获得更好的精度-性能平衡
> - FP16 转换精度损失可忽略不计（< 0.01%），适合 GPU 推理或需要半精度的场景

---

## 🚀 部署步骤

### 方式一：本地一键构建（推荐用于开发）

```bash
cd apps/docker-images/devcontainer-base

# 使用本地一键构建脚本（自动处理WSL2路径映射）
bash scripts/local-build.sh --variant onnx-quantized

# 国内镜像加速
bash scripts/local-build.sh --variant onnx-quantized --cn
```

### 方式二：Docker 直接构建

```bash
cd apps/docker-images/devcontainer-base

# 按依赖链构建（需先构建 base→conda-llvm→onnx-dev）
bash variants/build.sh --variant onnx-quantized --tag latest

# 国内源
bash variants/build.sh --variant onnx-quantized --tag latest --cn
```

### 方式三：启动容器

```bash
# 开发模式（推荐）
docker run -d --privileged \
  --name onnx-quantized-dev \
  -p 2222:22 \
  -p 8888:8888 \
  -p 2375:2375 \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=devtoken \
  -e GRANT_SUDO=yes \
  -v $(pwd)/workspace:/workspace \
  -v docker-data:/var/lib/docker \
  devcontainer-base:onnx-quantized-latest

# 快速验证（一次性运行）
docker run --rm devcontainer-base:onnx-quantized-latest \
  /opt/conda/envs/main/bin/python -c "
from onnxruntime.quantization import quantize_dynamic, QuantType
print('量化工具链就绪!')
"
```

### 访问服务

| 服务 | 地址 | 凭证 |
|------|------|------|
| **Jupyter Notebook** | http://localhost:8888 | Token: `devtoken`（或通过环境变量设置）|
| **SSH** | `ssh devuser@localhost -p 2222` | 密码: `devpass` |
| **Docker API** | tcp://localhost:2375 | - |

### CI/CD 自动构建

推送代码到 `main` 分支或创建 PR 时，GitHub Actions 会自动触发完整依赖链构建：
```
Lint → base → conda-llvm → onnx-dev → onnx-quantized
```

手动触发：
```bash
gh workflow run devcontainer-variants.yml --ref main -f variant=onnx-quantized
```

---

## ⚡ 性能优化建议

基于验证结果和量化本质分析，以下是可落地的性能优化方向：

### 1. ONNX Runtime 运行时优化（开箱即用）

```python
import onnxruntime as ort

# 推荐的 Session 配置（性能优先）
sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL  # 最高优化级别
sess_options.intra_op_num_threads = 4  # 内部算子并行线程数（建议=物理核心数）
sess_options.inter_op_num_threads = 1  # 算子间并行（通常设为1）
sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

# CPU EP 推荐配置
provider_options = [{
    'CPUExecutionProvider': {
        'arena_extend_strategy': 'kNextPowerOfTwo',
        'cpu_arena_extend_strategy': 'kSameAsRequested',
        'enable_arena_shrinkage': True,
    }
}]

session = ort.InferenceSession(
    "model_int8.onnx",
    sess_options=sess_options,
    providers=["CPUExecutionProvider"],
    provider_options=provider_options
)
```

### 2. OpenMP 环境变量（容器启动时设置）

```bash
# 在 ~/.bashrc 或容器启动环境中设置
export OMP_NUM_THREADS=4          # 与 intra_op_num_threads 保持一致
export OMP_WAIT_POLICY=PASSIVE     # 减少CPU空闲时的占用
export OPENBLAS_NUM_THREADS=1      # 避免OpenBLAS多线程与ORT线程冲突
export KMP_AFFINITY=granularity=fine,compact,1,0  # 线程亲和性
export KMP_BLOCKTIME=1             # 减少线程等待时间
```

### 3. 量化流程最佳实践（纯 ONNX，无 torch）

```python
# ✅ 推荐量化流程（精度最优）
import numpy as np
import onnx
import onnxsim
from onnx import TensorProto, helper
from onnxruntime.quantization import quantize_dynamic, QuantType

# 步骤1: 用 onnx.helper 构建模型（或从训练框架导出后导入）
# 等价 nn.Linear(IN, OUT) 的纯 ONNX 构建：
rng = np.random.default_rng(42)
w = (rng.standard_normal((IN, OUT)) / np.sqrt(IN)).astype(np.float32)
b = np.zeros(OUT, dtype=np.float32)
nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
graph = helper.make_graph(
    nodes, "linear",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT])],
    [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
     helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
onnx.save(model, "model.onnx")

# 步骤2: onnxsim 简化（必须！修复形状推理问题）
model_onnx = onnx.load("model.onnx")
model_simp, check = onnxsim.simplify(model_onnx)
assert check, "Model simplification failed"
onnx.save(model_simp, "model_simplified.onnx")

# 步骤3: 动态量化（适合大多数场景）
quantize_dynamic(
    model_input="model_simplified.onnx",
    model_output="model_int8.onnx",
    weight_type=QuantType.QInt8,  # QInt8 比 QUInt8 在对称分布上精度更好
    per_channel=True,             # 逐通道量化（精度更高）
    optimize_model=True,          # 自动启用 ORT_ENABLE_ALL
)

# 步骤4: 精度验证
import onnxruntime as ort
import numpy as np
sess_fp32 = ort.InferenceSession("model_simplified.onnx", providers=["CPUExecutionProvider"])
sess_int8 = ort.InferenceSession("model_int8.onnx", providers=["CPUExecutionProvider"])

# 使用真实数据验证
for _ in range(100):
    inp = rng.standard_normal((1, IN)).astype(np.float32)  # 用真实输入分布
    out_fp32 = sess_fp32.run(None, {"input": inp})[0]
    out_int8 = sess_int8.run(None, {"input": inp})[0]
    max_diff = np.max(np.abs(out_fp32 - out_int8))
    assert max_diff < 0.1, f"精度损失过大: {max_diff}"
```

> **从 PyTorch 导出模型？** 本镜像不含 torch。在外部环境导出 `.onnx` 后拷入容器，或按需 `pip install torch`（会破坏 torch 缺席负向验证，仅建议临时使用）。

### 4. 高级优化方向（进阶）

| 优化项 | 难度 | 预期收益 | 适用场景 |
|--------|------|----------|----------|
| **静态量化 + 校准** | 中等 | 20-40% 加速，更好精度 | 有代表性校准数据集 |
| **QDQ 格式量化** | 中等 | 兼容性更好，支持 TensorRT/OpenVINO | 多引擎部署 |
| **INT8 算子融合** | 高 | 额外 10-20% 加速 | Conv+ReLU+BN 等常见模式 |
| **Neural Compressor 自动调优**（可选） | 中等 | 精度-性能 Pareto 最优 | PyTorch模型追求极致精度（需手动 `pip install neural-compressor torch`） |
| **BF16 混合精度（新CPU）** | 低 | 接近 FP32 精度，支持 AVX512-BF16 | Intel Xeon Sapphire Rapids+ |
| **ONNX Runtime Extensions** | 低 | 自定义算子支持 | 特殊业务算子 |
| **IO 绑定 + 预分配内存** | 低 | 减少内存拷贝开销 | 高吞吐服务化部署 |

### 5. 预热策略

```python
# 推理前预热（避免首次运行冷启动开销）
def warmup(session, input_shape, num_warmup=10):
    dummy = np.random.randn(*input_shape).astype(np.float32)
    for _ in range(num_warmup):
        session.run(None, {"input": dummy})
```

---

## 📝 使用示例

### 示例1: 快速 FP32→INT8 量化（纯 ONNX）

```python
import numpy as np
import onnx
import onnxsim
import onnxruntime as ort
from onnx import TensorProto, helper
from onnxruntime.quantization import quantize_dynamic, QuantType

# 1. 构建 Gemm 模型（等价 nn.Linear(10, 5)）
rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 10, 5
w = (rng.standard_normal((IN_DIM, OUT_DIM)) * 0.1).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
graph = helper.make_graph(
    nodes, "linear",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
     helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
onnx.save(model, "fp32.onnx")

# 2. 简化
m = onnx.load("fp32.onnx")
m_simp, _ = onnxsim.simplify(m)
onnx.save(m_simp, "fp32_simp.onnx")

# 3. 量化
quantize_dynamic("fp32_simp.onnx", "int8.onnx",
                 weight_type=QuantType.QInt8, per_channel=True)

# 4. 验证
sess = ort.InferenceSession("int8.onnx", providers=["CPUExecutionProvider"])
out = sess.run(None, {"input": rng.standard_normal((1, IN_DIM)).astype(np.float32)})[0]
print(f"量化完成! 输出形状: {out.shape}")
```

### 示例2: FP16 转换

```python
import onnx
from onnxconverter_common import float16

model = onnx.load("fp32_simp.onnx")
model_fp16 = float16.convert_float_to_float16(model, keep_io_types=True)
onnx.save(model_fp16, "fp16.onnx")
print("FP16 转换完成")
```

---

## ⚠️ 已知问题与注意事项

1. **v2.0.0 架构迁移注意事项（重要）**

   | 方面 | v1.0.0（旧） | v2.0.0（新） |
   |------|--------------|--------------|
   | **基础镜像** | onnx-pytorch（含 PyTorch） | onnx-dev（纯 ONNX） |
   | **Python 环境** | conda base（GIL 启用） | conda main（**free-threading cp314t**） |
   | **Python 路径** | `/opt/conda/bin/python` | `/opt/conda/envs/main/bin/python` |
   | **torch** | 2.13.0+cpu 预装 | **缺席**（负向验证，按需自装） |
   | **模型构建方式** | `torch.onnx.export` | `onnx.helper` 纯构建 |
   | **onnxoptimizer** | 0.4.2 预装 | **排除**（free-threading 不兼容） |

   **迁移指引**：
   - 所有 `/opt/conda/bin/python` 引用改为 `/opt/conda/envs/main/bin/python`
   - 依赖 torch 的工作流：在外部环境导出 ONNX 后拷入，或 `pip install torch`（临时）
   - 需要 onnxoptimizer 的场景：用 `onnxsim`（已内置）替代图优化

2. **Neural Compressor 2.x vs 3.x API 差异**

   INC 3.x 进行了重大API重构，这是**预期的版本演进**，不是错误：

   | 方面 | INC 2.x（旧统一API） | INC 3.x（新框架专属API） |
   |------|---------------------|-------------------------|
   | **API风格** | 框架无关统一API | 框架专属API（PyTorch-first） |
   | **PyTorch入口** | `from neural_compressor import quantization` | `from neural_compressor.torch.quantization import ...` |
   | **配置类** | 统一 `PostTrainingQuantConfig` | 细粒度：`RTNConfig`/`AWQConfig`/`GPTQConfig`/`TeqConfig`/`AutoRoundConfig` |
   | **ONNX支持** | 通过 `adaptor/onnxrt.py` 适配 | ⚠️ **已弃用**（PR #2199标记deprecated） |

   **本项目的策略**：
   - ✅ **ONNX模型量化**：直接使用 `onnxruntime.quantization` 原生API（主力方案，完全不受影响）
   - ✅ **PyTorch模型量化**：如需INC高级功能，先 `pip install neural-compressor torch` 再使用 INC 3.x PyTorch API
   - 📦 **包未预装**：INC 需 torch，本镜像按设计不含

   **INC 3.x PyTorch API 示例**：
   ```python
   # 先安装: pip install neural-compressor torch
   from neural_compressor.torch.quantization import RTNConfig, quantize, prepare, convert

   # Weight-only RTN量化（4bit）
   woq_config = RTNConfig(bits=4, group_size=128)
   q_model = quantize(model, quant_config=woq_config, example_inputs=example_inputs)

   # 或两步式 prepare + convert
   prepared_model = prepare(model, quant_config=woq_config, example_inputs=example_inputs)
   # 校准...
   q_model = convert(prepared_model)
   q_model.save("./saved_quantized_model")
   ```

   **ONNX量化（本项目推荐，主力方案）**：
   ```python
   # 我们的主力方案 - 直接使用ONNX Runtime原生API，不依赖INC
   from onnxruntime.quantization import quantize_dynamic, QuantType
   quantize_dynamic(
       model_input="model.onnx",
       model_output="model_int8.onnx",
       weight_type=QuantType.QInt8,
       per_channel=True,
       optimize_model=True,
   )
   ```

3. **量化前必须简化模型**
   - 原因：部分 ONNX 模型存在形状推理问题（如 InceptionV1 的 Split 层）
   - 解决：始终在量化前运行 `onnxsim.simplify()`，确保 opset_version ≥ 18

4. **动态量化 vs 静态量化选择**
   - 动态量化：无需校准数据，适合 RNN/Transformer/Linear 主导模型
   - 静态量化：需要代表性校准数据集（~100样本），CNN 模型精度更好
   - FP16：几乎无精度损失，适合 GPU、支持 FP16 的 CPU、边缘设备

5. **线程数配置**
   - 延迟敏感场景：`OMP_NUM_THREADS=2-4`，`intra_op_num_threads=2-4`
   - 吞吐场景：`OMP_NUM_THREADS=物理核心数`，`intra_op_num_threads=物理核心数`
   - 务必设置 `OPENBLAS_NUM_THREADS=1` 避免嵌套并行

6. **依赖链构建**
   - onnx-quantized 依赖 onnx-dev → conda-llvm → base
   - 本地构建建议使用 `local-build.sh` 自动处理依赖链
   - CI 构建按拓扑顺序自动执行

---

## 🔗 相关链接

- [发布清单 RELEASE.md](./RELEASE.md)（v2.0.0 镜像标识/版本矩阵/验证记录）
- [文档站点版发布说明](../../../../../docs/tech/release-onnx-quantized-v2.md)（Sphinx 站点）
- [基础变体 onnx-dev](../onnx-dev/README.md)
- [姊妹变体 onnx-pytorch](../onnx-pytorch/README.md)（含 PyTorch 架构）
- [本地构建脚本](../../scripts/local-build.sh)
- [部署验证脚本](../../scripts/verify-deployment.py)
- [ONNX Runtime 量化文档](https://onnxruntime.ai/docs/performance/quantization.html)
- [Intel Neural Compressor 文档](https://intel.github.io/neural-compressor/)

---

## 📋 依赖链

```
base (Ubuntu 26.04 + SSH + Docker DinD + Jupyter)
  ↓
conda-llvm (LLVM/Clang 22.1.8 + 编译工具链)
  ↓
onnx-dev (纯 ONNX 生态 + main 环境 free-threading cp314t，无 PyTorch)
  ↓
onnx-quantized (量化工具链 ← 当前变体)
  - onnxruntime.quantization (内置，主量化引擎)
  - onnxconverter-common (FP16)
  - onnxsim (模型简化，量化前必用)
  - neural-compressor (可选，PyTorch-only in 3.x，需手动 pip install neural-compressor torch)
  - 排除: torch/torchvision (by design), onnxoptimizer (free-threading 不兼容)
```
