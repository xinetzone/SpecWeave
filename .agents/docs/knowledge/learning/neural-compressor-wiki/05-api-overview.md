---
id: "neural-compressor-wiki-api-overview"
title: "API 概览"
date: "2026-08-09"
category: "learning"
author: "SpecWeave"
status: "stable"
source: "https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html"
summary: "Intel Neural Compressor PyTorch 扩展 API 的核心类与函数介绍，包括 prepare、convert、量化配置等关键接口。"
tags: ["neural-compressor", "api", "pytorch", "reference"]
---

# API 概览

本章详细介绍 Intel Neural Compressor PyTorch 扩展（`neural_compressor.torch`）的核心 API。Neural Compressor 采用与 PyTorch 原生量化一致的 `prepare`/`convert` API 风格，降低学习成本，同时提供统一的配置类和自动调优功能。

所有 API 均从以下模块导入：

```python
from neural_compressor.torch.quantization import (
    prepare,
    convert,
    autotune,
    load,
    StaticQuantConfig,
    DynamicQuantConfig,
    RTNConfig,
    GPTQConfig,
    FP8Config,
)
```

---

## 1. prepare() - 模型准备

### 函数签名

```python
def prepare(
    model: torch.nn.Module,
    quant_config: BaseConfig,
    inplace: bool = True,
    example_inputs: Any = None,
) -> torch.nn.Module:
```

### 功能说明

`prepare()` 函数用于将浮点模型转换为准备校准的模型。它在模型的适当位置插入**观察者（Observer）**模块，用于在校准过程中监控输入和输出张量的数值范围（最小值/最大值/直方图等统计信息）。

这是量化流程的第一步，必须在校准和转换之前调用。

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | `torch.nn.Module` | 必填 | 原始浮点模型，建议先调用 `model.eval()` 设置为评估模式 |
| `quant_config` | `BaseConfig` | 必填 | 量化配置对象，如 `StaticQuantConfig`、`RTNConfig`、`FP8Config` 等 |
| `inplace` | `bool` | `True` | 是否原地修改模型。如果为 `True`，传入的模型对象会被直接修改；如果为 `False`，会复制一份模型进行修改 |
| `example_inputs` | `tensor/tuple/dict` | `None` | 用于追踪模型计算图的示例输入，某些后端（如 IPEX）需要此参数进行 JIT 编译 |

### 返回值

返回插入了观察者的准备模型（`torch.nn.Module`），可以在校准数据集上运行前向传播。

### 代码示例

```python
import torch
import torchvision.models as models
from neural_compressor.torch.quantization import StaticQuantConfig, prepare

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.eval()

quant_config = StaticQuantConfig(dtype="int8")
example_inputs = torch.randn(1, 3, 224, 224)

prepared_model = prepare(
    model=model,
    quant_config=quant_config,
    inplace=False,
    example_inputs=example_inputs,
)
```

### 注意事项

- 调用 `prepare()` 之前，务必将模型设置为 `eval()` 模式
- IPEX 后端和 SmoothQuant 必须提供 `example_inputs` 参数
- 如果不希望修改原始模型，设置 `inplace=False`
- `prepare()` 返回的模型尚未量化，需要进行校准和 `convert()` 才能得到量化模型

---

## 2. convert() - 模型转换

### 函数签名

```python
def convert(
    model: torch.nn.Module,
    quant_config: BaseConfig = None,
    inplace: bool = True,
) -> torch.nn.Module:
```

### 功能说明

`convert()` 函数将经过 `prepare()` 和校准的模型转换为最终的量化模型。它执行以下操作：

1. 读取每个观察者收集到的统计信息（min/max 或直方图）
2. 根据统计信息计算每个张量的量化参数（scale 和 zero_point）
3. 将观察者模块替换为实际的量化（Quantize）和反量化（Dequantize）算子
4. 对权重进行离线量化
5. 对于仅权重量化，将权重打包为低比特存储格式（WeightOnlyLinear）

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | `torch.nn.Module` | 必填 | 经过 `prepare()` 和校准的模型 |
| `quant_config` | `BaseConfig` | `None` | 量化配置，通常不需要传入（使用 `prepare()` 时的配置），特殊场景下可用于覆盖配置 |
| `inplace` | `bool` | `True` | 是否原地修改模型 |

### 返回值

返回最终的量化模型（`torch.nn.Module`），可以直接用于推理。

### 代码示例

```python
import torch
import torchvision.models as models
from neural_compressor.torch.quantization import StaticQuantConfig, prepare, convert

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.eval()

quant_config = StaticQuantConfig(dtype="int8")
prepared_model = prepare(model, quant_config)

calibration_data = torch.randn(10, 3, 224, 224)
with torch.no_grad():
    for i in range(10):
        prepared_model(calibration_data[i:i+1])

quantized_model = convert(prepared_model)

with torch.no_grad():
    output = quantized_model(torch.randn(1, 3, 224, 224))
```

### 注意事项

- `convert()` 必须在 `prepare()` 和校准之后调用
- 对于 RTN 等不需要校准的仅权重量化，`prepare()` 后可直接调用 `convert()`
- 转换后的模型可以直接推理，但通常需要在目标硬件上运行才能获得加速效果
- `convert()` 后的模型会获得 `save()` 方法用于保存

---

## 3. 常用量化配置类

所有量化配置类都继承自 `BaseConfig`，提供统一的构造和配置接口。

### 3.1 StaticQuantConfig - 静态量化配置

#### 构造函数

```python
StaticQuantConfig(
    w_dtype: str = "int8",
    act_dtype: str = "int8",
    w_sym: bool = True,
    act_sym: bool = False,
    w_algo: str = "minmax",
    act_algo: str = "minmax",
    inputs=None,
    outputs=None,
)
```

#### 主要参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `w_dtype` | `str` | `"int8"` | 权重量化数据类型 |
| `act_dtype` | `str` | `"int8"` | 激活值量化数据类型 |
| `w_sym` | `bool` | `True` | 权重是否使用对称量化 |
| `act_sym` | `bool` | `False` | 激活值是否使用对称量化 |
| `w_algo` | `str` | `"minmax"` | 权重量化算法（minmax/kl 等） |
| `act_algo` | `str` | `"minmax"` | 激活值量化算法 |
| `inputs` | `list` | `None` | 需要量化的输入算子列表 |
| `outputs` | `list` | `None` | 需要量化的输出算子列表 |

#### 代码示例

```python
from neural_compressor.torch.quantization import StaticQuantConfig

qconfig = StaticQuantConfig(
    w_dtype="int8",
    act_dtype="int8",
    act_sym=True,
    act_algo="minmax",
)
```

---

### 3.2 DynamicQuantConfig - 动态量化配置

#### 构造函数

```python
DynamicQuantConfig(
    w_dtype: str = "int8",
    act_dtype: str = "int8",
    w_sym: bool = True,
    act_sym: bool = False,
)
```

#### 代码示例

```python
from neural_compressor.torch.quantization import DynamicQuantConfig

qconfig = DynamicQuantConfig()
```

> **注意**：动态量化目前仅支持 PT2E 后端，需要 `export` 和 `torch.compile` 配合使用。

---

### 3.3 RTNConfig - Round to Nearest 仅权重量化配置

#### 构造函数

```python
RTNConfig(
    dtype: str = "int",
    bits: int = 4,
    group_size: int = -1,
    use_sym: bool = True,
    quant_lm_head: bool = False,
    use_double_quant: bool = False,
    double_quant_dtype: str = "int",
    double_quant_bits: int = 8,
    double_quant_use_sym: bool = True,
    double_quant_group_size: int = 256,
    group_dim: int = 1,
    use_full_range: bool = False,
    use_mse_search: bool = False,
    use_layer_wise: bool = False,
    model_path: str = None,
)
```

#### 主要参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dtype` | `str` | `"int"` | 权重量化类型：`"int"`, `"nf4"`, `"fp4"` |
| `bits` | `int` | `4` | 量化位宽（1~8） |
| `group_size` | `int` | `-1` | 分组大小，-1 表示逐输出通道 |
| `use_sym` | `bool` | `True` | 是否对称量化 |
| `quant_lm_head` | `bool` | `False` | 是否量化 LM Head 层 |
| `use_double_quant` | `bool` | `False` | 是否启用双量化 |
| `use_mse_search` | `bool` | `False` | 是否使用 MSE 搜索最优量化参数 |
| `use_layer_wise` | `bool` | `False` | 是否启用分层量化（低内存模式） |

#### 代码示例

```python
from neural_compressor.torch.quantization import RTNConfig

qconfig = RTNConfig(
    bits=4,
    group_size=128,
    use_sym=True,
    use_mse_search=False,
)
```

---

### 3.4 GPTQConfig - GPTQ 仅权重量化配置

#### 构造函数

```python
GPTQConfig(
    dtype: str = "int",
    bits: int = 4,
    group_size: int = -1,
    use_sym: bool = True,
    quant_lm_head: bool = False,
    use_double_quant: bool = False,
    use_mse_search: bool = False,
    use_layer_wise: bool = False,
    model_path: str = None,
    act_order: bool = False,
    hybrid_act_order: bool = False,
    percdamp: float = 0.01,
    block_size: int = 128,
    static_groups: bool = False,
    true_sequential: bool = False,
)
```

#### 主要参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `act_order` | `bool` | `False` | 是否按 Hessian 对角线值排序通道（提升精度但增加计算） |
| `hybrid_act_order` | `bool` | `False` | 是否启用组感知激活重排（GAR） |
| `percdamp` | `float` | `0.01` | Hessian 对角线阻尼百分比，增加数值稳定性 |
| `block_size` | `int` | `128` | GPTQ 量化的块大小，块形状为 [C_out, block_size] |
| `static_groups` | `bool` | `False` | 是否预先计算组量化参数，缓解 act_order 额外开销 |
| `true_sequential` | `bool` | `False` | 是否按 Transformer 块原始顺序量化层（精度更高但更慢） |

#### 代码示例

```python
from neural_compressor.torch.quantization import GPTQConfig

qconfig = GPTQConfig(
    bits=4,
    group_size=128,
    act_order=True,
    percdamp=0.01,
    block_size=128,
)
```

> **注意**：GPTQ 需要校准步骤，`prepare()` 后需要运行 `run_fn(model)` 进行校准。

---

### 3.5 FP8Config - FP8 量化配置

#### 构造函数

```python
FP8Config(
    fp8_config: str = "E4M3",
    hp_dtype: str = "bf16",
    observer: str = "maxabs",
    allowlist: dict = None,
    blocklist: dict = None,
    mode: str = "AUTO",
    dump_stats_path: str = "./hqt_output/measure",
    scale_method: str = "maxabs_hw",
    measure_exclude: str = "OUTPUT",
)
```

#### 主要参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `fp8_config` | `str` | `"E4M3"` | FP8 格式：`"E4M3"`（4 指数 3 尾数）或 `"E5M2"`（5 指数 2 尾数） |
| `hp_dtype` | `str` | `"bf16"` | 非 FP8 算子的高精度类型：`"bf16"`, `"fp16"`, `"fp32"` |
| `observer` | `str` | `"maxabs"` | 统计观测器算法 |
| `mode` | `str` | `"AUTO"` | 运行模式：`"AUTO"`, `"MEASURE"`, `"QUANTIZE"` |
| `scale_method` | `str` | `"maxabs_hw"` | 缩放因子计算方法 |
| `measure_exclude` | `str` | `"OUTPUT"` | 排除测量的张量：`"NONE"`, `"OUTPUT"` |

#### 代码示例

```python
from neural_compressor.torch.quantization import FP8Config

qconfig = FP8Config(
    fp8_config="E4M3",
    hp_dtype="bf16",
    scale_method="maxabs_hw",
)
```

---

## 4. autotune() - 自动调优

### 函数签名

```python
def autotune(
    model: torch.nn.Module,
    tune_config: TuningConfig,
    eval_fn: Callable,
    eval_args: tuple = None,
    run_fn: Callable = None,
    run_args: tuple = None,
    example_inputs: Any = None,
) -> torch.nn.Module:
```

### 功能说明

当不确定哪种量化配置能获得最佳精度-性能权衡时，可以使用 `autotune()` 自动搜索最优量化配置。Autotune 会自动尝试不同的量化配置组合（位宽、算法、算子配置等），根据评估函数的结果选择满足精度要求的最快模型。

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | `torch.nn.Module` | 必填 | 原始浮点模型 |
| `tune_config` | `TuningConfig` | 必填 | 调优配置，定义搜索空间和精度目标 |
| `eval_fn` | `Callable` | 必填 | 评估函数，输入模型，输出精度指标（如准确率） |
| `eval_args` | `tuple` | `None` | 传递给 `eval_fn` 的参数 |
| `run_fn` | `Callable` | `None` | 校准函数，用于运行前向传播收集统计信息 |
| `run_args` | `tuple` | `None` | 传递给 `run_fn` 的参数 |
| `example_inputs` | `Any` | `None` | 示例输入，用于 JIT 追踪 |

### 返回值

返回自动调优找到的最优量化模型。

### 代码示例

```python
import torch
import torchvision.models as models
from neural_compressor.torch.quantization import autotune
from neural_compressor.torch.quantization import TuningConfig, get_default_tuning_config

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.eval()

def eval_fn(model):
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in eval_dataloader:
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    return correct / total

def run_fn(model):
    with torch.no_grad():
        for inputs, _ in calib_dataloader:
            model(inputs)

tune_config = TuningConfig(
    max_trials=100,
    accuracy_criterion={"relative": 0.01},
    quant_levels=["auto", "int8", "int4"],
)

best_model = autotune(
    model=model,
    tune_config=tune_config,
    eval_fn=eval_fn,
    run_fn=run_fn,
)
```

### 注意事项

- `eval_fn` 必须返回一个数值型的精度指标，Autotune 会根据该指标判断模型是否可接受
- `accuracy_criterion` 设置精度容忍度，`{"relative": 0.01}` 表示精度下降不超过 1%
- Autotune 可能需要较长时间，因为它需要多次量化和评估
- 如果对量化配置比较了解，直接使用 `prepare`/`convert` 更高效

---

## 5. save() - 保存模型

### 方法签名

量化模型通过 `convert()` 后会自动获得 `save()` 方法：

```python
def save(self, output_dir: str = "./saved_results"):
```

### 功能说明

将量化模型保存到指定目录。保存的内容通常包括：

- `quantized_model.pt` 或 `weight_only_qmodel.pt`：量化模型权重
- `qconfig.json`：量化配置元数据

对于仅权重量化，模型使用 `WeightOnlyLinear` 模块，将低比特数据打包存储以节省空间。

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_dir` | `str` | `"./saved_results"` | 保存模型的目录路径 |

### 代码示例

```python
from neural_compressor.torch.quantization import RTNConfig, prepare, convert

model = YourModel()
qconfig = RTNConfig(bits=4)
model = prepare(model, qconfig)
model = convert(model)

model.save("./my_quantized_model")
```

---

## 6. load() - 加载模型

### 函数签名

```python
def load(
    output_dir: str = "./saved_results",
    model: torch.nn.Module = None,
    format: str = "default",
    device: str = "cpu",
    torch_dtype: torch.dtype = None,
    **kwargs,
) -> torch.nn.Module:
```

### 功能说明

`load()` 函数是加载量化模型的统一入口，支持多种格式：

1. 加载 Neural Compressor 自身 `save()` 保存的模型
2. 加载 HuggingFace Hub 上的预量化模型（如 GPTQ、AWQ 格式）
3. 首次加载 HuggingFace 格式模型时，会自动转换为 Neural Compressor 后端格式并缓存

> **重要**：如果模型之前的 `original_model` 在保存时没有被保存，加载时需要传入 `model`（原始 FP32 模型或空模型）。

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_dir` | `str` | `"./saved_results"` | 模型路径或 HuggingFace 模型名称 |
| `model` | `torch.nn.Module` | `None` | 原始浮点模型，加载分层量化模型时需要 |
| `format` | `str` | `"default"` | 模型格式：`"default"`（INC 格式）或 `"huggingface"` |
| `device` | `str` | `"cpu"` | 目标设备：`"cpu"`, `"cuda"`, `"hpu"` |
| `torch_dtype` | `torch.dtype` | `None` | 激活值计算精度，如 `torch.bfloat16` |

### 返回值

返回加载好的量化模型。

### 代码示例

#### 加载 INC 格式模型

```python
from neural_compressor.torch.quantization import load

loaded_model = load("./my_quantized_model")
```

#### 加载 HuggingFace 预量化模型

```python
import torch
from neural_compressor.torch.quantization import load

model = load(
    model_name_or_path="TheBloke/Llama-2-7B-GPTQ",
    format="huggingface",
    device="cpu",
    torch_dtype=torch.bfloat16,
)
```

#### 加载分层量化模型

```python
from neural_compressor.torch.quantization import load
from neural_compressor.torch import load_empty_model

orig_model = load_empty_model("/path/to/model")
loaded_model = load(
    "./layerwise_quantized_model",
    model=orig_model,
)
```

### 注意事项

- 首次加载 HuggingFace GPTQ/AWQ 模型时会进行格式转换，可能需要 5-30 分钟
- 转换后的模型会缓存到 HuggingFace 缓存目录，后续加载速度会很快
- 使用 `use_layer_wise=True` 量化的模型，加载时必须传入 `original_model`

---

## 7. set_local() - 算子级配置

### 方法签名

所有配置类都提供 `set_local()` 方法用于为特定算子或层设置不同的量化配置：

```python
def set_local(
    self,
    operator_name_or_list: Union[str, list, Callable],
    config: BaseConfig,
) -> BaseConfig:
```

### 功能说明

`set_local()` 允许在全局默认配置的基础上，为特定的算子名称、算子类型或名称模式设置不同的量化配置。这在以下场景非常有用：

- 某些层对量化敏感，需要保持 FP32 精度
- 某些层可以使用更低比特获得更大压缩比
- 需要排除特定层不量化

匹配规则支持：
- **精确名称匹配**：如 `"fc1"`
- **正则表达式匹配**：如 `".*mlp.*"` 匹配所有名称含 "mlp" 的层
- **算子类型匹配**：如 `"Linear"`, `"Conv2d"`

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `operator_name_or_list` | `str/list/Callable` | 算子名称、算子类型、正则模式，或它们的列表 |
| `config` | `BaseConfig` | 该算子要使用的量化配置 |

### 返回值

返回配置对象自身，支持链式调用。

### 代码示例

```python
from neural_compressor.torch.quantization import RTNConfig

quant_config = RTNConfig(bits=4)

quant_config.set_local("lm_head", RTNConfig(dtype="fp32"))

quant_config.set_local(".*mlp.*", RTNConfig(bits=8))

quant_config.set_local("Conv1d", RTNConfig(dtype="fp32"))
```

#### 静态量化的算子回退示例

```python
from neural_compressor.torch.quantization import StaticQuantConfig

quant_config = StaticQuantConfig(dtype="int8")

quant_config.set_local(
    "fc1",
    StaticQuantConfig(w_dtype="fp32", act_dtype="fp32"),
)

quant_config.set_local(
    "Linear",
    StaticQuantConfig(w_dtype="fp32", act_dtype="fp32"),
)
```

### 注意事项

- 配置优先级：`set_local` 设置的配置 > 全局默认配置
- 可以多次调用 `set_local` 为不同模式设置不同配置
- PT2E 后端的 `set_local` 支持需要 PyTorch 2.4 及以上版本
- AutoRound 算法推荐使用其专用的 `layer_config` 参数而不是 `set_local`

---

## 8. 其他常用 API

### 8.1 export() - 导出 FX 图模型

PT2E 后端需要先将 eager 模式模型导出为 FX 图：

```python
from neural_compressor.torch.export import export

exported_model = export(
    model=model,
    example_inputs=example_inputs,
)
```

### 8.2 load_empty_model() - 加载空模型（分层量化用）

对于超大模型，可以先加载一个没有实际权重的空模型结构，配合分层量化使用：

```python
from neural_compressor.torch import load_empty_model

empty_model = load_empty_model("/path/to/model/state/dict")
```

### 8.3 finalize_calibration() - 完成校准（FP8 两阶段流程）

FP8 混合量化流程中，完成 MEASURE 阶段后调用：

```python
from neural_compressor.torch.algorithms.fp8_quant import finalize_calibration

finalize_calibration(model)
```

---

## 9. 完整 API 使用流程示例

以下是一个综合示例，展示从配置到量化、保存、加载的完整流程：

```python
import torch
import torch.nn as nn
from neural_compressor.torch.quantization import (
    RTNConfig,
    prepare,
    convert,
    load,
)

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(768, 768)
        self.fc2 = nn.Linear(768, 768)
        self.lm_head = nn.Linear(768, 1000)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.lm_head(x)

def main():
    model = SimpleModel()
    model.eval()

    quant_config = RTNConfig(bits=4, group_size=128)
    quant_config.set_local("lm_head", RTNConfig(dtype="fp32"))

    prepared_model = prepare(model, quant_config)
    quantized_model = convert(prepared_model)

    with torch.no_grad():
        test_input = torch.randn(1, 768)
        output = quantized_model(test_input)
        print(f"输出形状: {output.shape}")

    save_dir = "./simple_model_quantized"
    quantized_model.save(save_dir)
    print(f"模型已保存到: {save_dir}")

    loaded_model = load(save_dir)
    with torch.no_grad():
        loaded_output = loaded_model(test_input)
        diff = torch.max(torch.abs(output - loaded_output))
        print(f"加载后输出差异: {diff:.6f}")

if __name__ == "__main__":
    main()
```

---

## 10. 后端自动检测

Neural Compressor 会自动检测可用的量化后端，优先级如下：

| 环境 | 自动选择后端 |
|------|-------------|
| 已安装 `intel-extension-for-pytorch` | IPEX 后端 |
| 已导入 `torch` 且有 `torch.dynamo` | PT2E (TorchDynamo) 后端 |

如果需要强制指定目标设备，可以设置环境变量：

```bash
export INC_TARGET_DEVICE=cpu
```

可选值：`cpu`, `cuda`, `xpu`, `hpu`。

---

[← 上一章：量化技术详解](04-quantization-techniques.md) | [下一章：最佳实践 →](06-best-practices.md)
