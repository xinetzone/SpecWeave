---
id: onnx-wiki-quickstart
title: ONNX Wiki - 快速上手指南
date: 2026-08-09
tags:
  - onnx
  - quickstart
  - hello-world
  - netron
  - deployment
source:
  - https://onnx.ai/get-started.html
category: knowledge/learning/06-ai-ml-inference
maturity: L1-draft
---

# ONNX 快速上手指南

5分钟跑通你的第一个ONNX模型。

---

## 安装

### 前置条件
- Python 3.8 ~ 3.12（onnx 1.23.0支持版本）
- pip版本建议≥21.0

### 基础安装（构建+校验+参考运行时）

```bash
pip install onnx numpy
```

这会安装：
- `onnx`：核心库，包含Helper API、checker、shape inference、reference runtime
- `numpy`：数组处理

> **平台注意事项**：
> - **Windows**：如果安装失败，可能需要先安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
> - **Linux**：某些发行版可能需要先装`pip install --upgrade pip setuptools wheel`
> - **Mac (Apple Silicon)**：建议用conda安装或确保pip是arm64版本，避免装成x86版本
> - **国内用户**：可加`-i https://pypi.tuna.tsinghua.edu.cn/simple`加速下载

### 生产推理（推荐）

```bash
# CPU版本（通用，所有平台）
pip install onnxruntime

# GPU版本（需要NVIDIA CUDA环境）
# pip install onnxruntime-gpu
```

`onnxruntime`是微软开发的生产级推理引擎，支持CPU/GPU加速，性能是reference runtime的数百倍。

> **GPU版本注意**：onnxruntime-gpu版本需要与你的CUDA/cuDNN版本匹配，具体对照表见[官方文档](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements)

### 其他推理引擎选项（生态一览）
| 引擎 | 适用场景 | 特点 |
|------|----------|------|
| **onnxruntime** | 通用生产部署 | CPU/GPU支持好，跨平台，最流行 |
| **TensorRT** | NVIDIA GPU极致性能 | NVIDIA硬件上性能最好，需单独转换 |
| **OpenVINO** | Intel CPU/GPU/VPU | Intel硬件加速，边缘部署常用 |
| **onnx-mlir** | 嵌入式/自定义硬件 | 可编译到多种硬件架构 |
| **TVM** | 深度学习编译器 | 自动调优，支持多种硬件后端 |

### 验证安装

```python
import onnx
print(f"ONNX版本: {onnx.__version__}")
print(f"支持的opset版本: {onnx.defs.onnx_opset_version()}")
```

---

## 5分钟Hello World

我们直接用[02-python-api.md](./02-python-api.md)中的线性回归示例，快速跑通：

```python
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper

# 1. 声明输入输出
X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [None, 2])
y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [None, 1])

# 2. 创建Initializer（权重）
W = numpy_helper.from_array(np.array([[0.5], [0.8]], dtype=np.float32), name="W")
b = numpy_helper.from_array(np.array([0.1], dtype=np.float32), name="b")

# 3. 创建节点
node1 = helper.make_node("MatMul", ["X", "W"], ["matmul_out"])
node2 = helper.make_node("Add", ["matmul_out", "b"], ["y"])

# 4. 组装图
graph = helper.make_graph(
    [node1, node2], "LinearRegression",
    inputs=[X], outputs=[y], initializer=[W, b]
)

# 5. 生成模型并校验
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
onnx.checker.check_model(model)

# 6. 保存
onnx.save(model, "hello.onnx")
print("✅ 模型已保存到 hello.onnx")

# 7. 用onnxruntime推理（生产方式）
import onnxruntime as ort
sess = ort.InferenceSession("hello.onnx", providers=["CPUExecutionProvider"])
X_test = np.array([[1.0, 2.0]], dtype=np.float32)
result = sess.run(None, {"X": X_test})
print(f"输入: {X_test}")
print(f"预测: {result[0]}")
print(f"手动计算: {X_test @ np.array([[0.5],[0.8]]) + 0.1}")
```

运行后你应该看到预测结果与手动计算一致。

---

## 模型可视化（Netron）

**Netron是ONNX开发的必备工具**，遇到任何图相关问题，第一反应应该是用Netron打开看看。

### 使用方式

**方式1：网页版（推荐，零安装）**
1. 访问 https://netron.app
2. 直接拖放你的`.onnx`文件进去

**方式2：桌面应用**
```bash
pip install netron
```
```python
import netron
netron.start("hello.onnx")  # 自动打开浏览器
```

### 你会看到什么

对于我们的线性回归模型，Netron会显示：
- 输入节点`X`（FLOAT [None, 2]）
- MatMul节点
- Add节点
- Initializer节点`W`和`b`
- 输出节点`y`（FLOAT [None, 1]）

点击任意节点可以查看详细信息：类型、属性、输入输出形状等。

---

## 从PyTorch/TensorFlow导出概览

大多数时候你不需要手写ONNX图，而是从训练框架导出。以下是快速参考（不展开细节，给出官方教程链接）：

### PyTorch导出

```python
import torch
import torchvision

model = torchvision.models.resnet18(pretrained=True)
model.eval()

dummy_input = torch.randn(1, 3, 224, 224)

torch.onnx.export(
    model,
    dummy_input,
    "resnet18.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)
```

**PyTorch导出注意事项**：
- 一定要设置`model.eval()`！否则BatchNorm/Dropout行为不对
- 用`dynamic_axes`指定动态维度（如batch size）
- opset_version选部署目标支持的版本，不是越高越好
- 导出后务必用onnx.checker校验，用Netron可视化检查结构
- 复杂模型可能需要自定义算子符号函数

**官方教程**：https://pytorch.org/docs/stable/onnx.html

### TensorFlow/Keras导出

```python
import tensorflow as tf
import tf2onnx

model = tf.keras.applications.ResNet50()

input_signature = [tf.TensorSpec([None, 224, 224, 3], tf.float32, name="input")]
model_proto, _ = tf2onnx.convert.from_keras(model, input_signature, opset=17)

with open("resnet50.onnx", "wb") as f:
    f.write(model_proto.SerializeToString())
```

需要安装：`pip install tf2onnx`

**官方教程**：https://github.com/onnx/tensorflow-onnx

### 其他框架

- **scikit-learn**：使用`skl2onnx`（https://github.com/onnx/sklearn-onnx）
- **XGBoost/LightGBM**：使用`onnxmltools`（https://github.com/onnx/onnxmltools）
- **PaddlePaddle**：使用`paddle2onnx`（https://github.com/PaddlePaddle/Paddle2ONNX）

---

## 常见入门问题

### Q1：导出的模型在onnxruntime里跑结果不对？

先按顺序检查：
1. 模型是否在eval模式下导出？（PyTorch）
2. 输入预处理是否与训练时一致？（归一化、BGR/RGB、通道顺序HWC/CHW）
3. 是否正确处理了动态batch？
4. 用reference runtime对比一下结果，确认是模型问题还是runtime问题
5. 用Netron看一下图结构是否符合预期

### Q2：opset_version选多少？

- 如果你不知道部署目标支持什么版本，**选17或18**——兼容性最好
- 如果你明确知道部署用最新版onnxruntime，可以选更高版本
- 参考：[04-best-practices.md](./04-best-practices.md) 中的opset选择策略

### Q3：导出时报错"Could not export an operator"？

这说明该算子没有对应的ONNX符号函数：
1. 先尝试升级PyTorch/tf2onnx到最新版
2. 查找是否有社区实现的自定义符号
3. 考虑用算子组合替代该算子
4. 最后才考虑自定义算子

### Q4：模型文件很大怎么办？

- 检查是否把训练节点（如Dropout的训练状态）导进去了
- 考虑常量折叠（constant folding）
- 考虑量化（INT8/FP8）——这是另一个大主题
- onnx本身支持infer_shapes后strip未使用的信息

### Q5：怎么验证两个模型等价？

1. 用相同输入对比输出，看误差是否在可接受范围内
2. 使用`onnx.checker`检查结构
3. 使用`onnx.metric`或手动逐层对比中间输出
4. 注意：浮点计算顺序不同可能导致微小误差（1e-6级别），这是正常的

---

## 下一步

- ✅ 你已经能跑通ONNX模型了
- 📖 想深入理解核心概念 → 读 [01-core-concepts.md](./01-core-concepts.md)
- 🛠️ 想手写/修改ONNX图 → 读 [02-python-api.md](./02-python-api.md)
- ⚠️ 想避开生产踩坑 → 直接读 **[04-best-practices.md](./04-best-practices.md)**（最重要！）
- ❓ 遇到问题 → 查 [05-faq-and-resources.md](./05-faq-and-resources.md)

---

**上一章**：[02-python-api.md - Python API实战](./02-python-api.md) | **下一章**：[04-best-practices.md - 最佳实践与反模式](./04-best-practices.md)
