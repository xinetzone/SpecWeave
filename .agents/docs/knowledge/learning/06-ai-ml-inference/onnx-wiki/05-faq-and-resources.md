---
id: onnx-wiki-faq-resources
title: ONNX Wiki - FAQ与资源
date: 2026-08-09
tags:
  - onnx
  - faq
  - resources
  - glossary
  - references
source:
  - https://onnx.ai
  - https://github.com/onnx/onnx
category: knowledge/learning/06-ai-ml-inference
maturity: L1-draft
---

# ONNX FAQ与资源

常见问题解答、学习资源链接、术语表。

---

## 常见问题（FAQ）

### Q1：ONNX和ONNX Runtime是什么关系？

**ONNX**是模型格式/IR规范本身；**ONNX Runtime（ORT）**是微软开发的、最流行的ONNX生产级推理引擎。

类比：ONNX相当于Python语言规范，onnx包相当于CPython解释器（但只用于参考），ONNX Runtime相当于PyPy（高性能生产实现）。你可以用onnx包构建和验证模型，但生产推理必须用onnxruntime或其他专用runtime。

---

### Q2：为什么导出的模型在Netron里看结构不对？

先按顺序排查：
1. 导出时是否在eval模式？（PyTorch必须`model.eval()`）
2. dummy_input的形状/类型是否正确？
3. 导出时是否报错？有些警告被忽略了
4. 用`onnx.checker.check_model()`检查一下有没有问题
5. 尝试用onnxruntime加载看能不能跑，能跑说明模型本身没问题
6. 可能是Netron版本问题，试试网页版最新版

---

### Q3：opset、IR版本、onnx包版本三者是什么关系？

- **onnx包版本**：Python库的版本（如1.23.0），决定了你能构建多高opset的模型
- **opset版本**：算子行为契约版本（如28），决定每个算子遵循哪个版本的语义
- **IR版本**：ONNX语言本身的版本（如v13），决定图结构、protobuf schema

关系：onnx次版本号更新时，opset版本通常+1；IR版本变化不频繁（跨大版本才变）。

---

### Q4：为什么同样的输入，PyTorch和ONNX输出有微小差异？

这是**正常现象**，原因包括：
- 浮点计算顺序不同导致精度累积差异（1e-6 ~ 1e-4级别）
- 某些算子在不同框架的实现细节不同（如Conv的padding算法）
- 训练时 BatchNorm 的 running_mean/var 是浮点近似

判断是否正常：
- 相对误差 < 1e-3 通常是正常的
- 误差很大（>1e-2）或者结果完全不对，那一定有bug

---

### Q5：ONNX支持动态batch size吗？怎么设置？

支持。把输入形状的第0维设为`None`（或字符串"batch_size"）即可：

```python
# PyTorch导出示例
torch.onnx.export(
    ...,
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    }
)

# 手写图示例
X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [None, 3, 224, 224])
# 第一个None表示batch_size动态
```

---

### Q6：onnx文件超过2GB怎么办？

Protobuf单模型大小限制是2GB。解决方案：
1. **量化**：INT8量化通常能把模型缩小到1/4大小
2. **外部数据格式**：把权重存成外部文件，onnx只存图结构
   ```python
   onnx.save_model(model, "model.onnx", save_as_external_data=True, all_tensors_to_one_file=True)
   ```
3. **模型拆分**：把大模型拆成多个onnx文件顺序执行
4. **检查冗余**：是不是把不必要的训练节点/信息导进去了

---

### Q7：怎么修改已有的ONNX模型？

几种方案：
1. **onnx2py.py**：把onnx转成Python脚本，修改后重新生成（推荐）
   - https://github.com/microsoft/onnxconverter-common/blob/master/onnxconverter_common/onnx2py.py
2. **直接操作protobuf**：用onnx Python API遍历graph.node修改
3. **onnx-graphsurgeon**：NVIDIA的图修改工具（更友好）
   - `pip install onnx-graphsurgeon`
4. **重新导出**：如果能从原框架重新导出，这通常是最稳妥的

---

### Q8：自定义算子怎么处理？

三种主流方案：
1. **运行时自定义算子**：在目标runtime（如onnxruntime）里注册自定义算子实现
2. **Functions（函数组合）**：用现有ONNX算子组合成新算子，纯ONNX实现无需runtime扩展
3. **用子图替代**：如果逻辑不复杂，直接展开成标准算子组合

选择优先级：方案3 > 方案2 > 方案1（越靠前可移植性越好）。

---

### Q9：怎么调试ONNX模型中间结果？

1. **Netron可视化**：先看图结构对不对（必做第一步）
2. **zetane viewer**：执行时查看所有中间张量值
3. **onnxruntime加hook**：用InferenceSession的中间输出功能
4. **ReferenceEvaluator逐层计算**：手动把中间张量作为输出拿出来对比
5. **修改模型临时输出**：把想看的中间节点加到output列表里

---

### Q10：ONNX能用于训练吗？

ONNX主要定位是**推理格式**，但也支持训练相关功能：
- `ai.onnx.training`域有训练相关算子
- ONNX Runtime有训练模块（ORT Training）
- 但生态和成熟度远不如推理
- **绝大多数场景下，ONNX只用于部署推理**，训练在原框架（PyTorch/TF）做

---

### Q11：怎么列出模型的所有输入输出？

```python
import onnx

model = onnx.load("model.onnx")

print("=== 输入 ===")
for inp in model.graph.input:
    shape = [d.dim_value if d.dim_value else "?" for d in inp.type.tensor_type.shape.dim]
    print(f"  {inp.name}: {shape}, dtype={inp.type.tensor_type.elem_type}")

print("\n=== 输出 ===")
for out in model.graph.output:
    shape = [d.dim_value if d.dim_value else "?" for d in out.type.tensor_type.shape.dim]
    print(f"  {out.name}: {shape}, dtype={out.type.tensor_type.elem_type}")
```

---

### Q12：不同框架导出的ONNX模型通用吗？

理论上完全通用——这就是ONNX存在的意义。实际上：
- ✅ 标准算子（Conv/MatMul/Add/Relu等）完全通用
- ⚠️ 某些框架导出的模型可能用了自定义域算子，需要对应runtime支持
- ⚠️ 不同opset版本可能有兼容性问题
- ✅ 只要用的是ai.onnx标准域的算子，就能在所有支持ONNX的runtime上跑

---

## 资源链接

### 官方资源

| 资源 | 链接 | 说明 |
|------|------|------|
| ONNX官方主页 | https://onnx.ai | 官方入口 |
| 官方概念文档 | https://onnx.ai/onnx/intro/concepts.html | 本Wiki主要参考来源 |
| 官方Python API教程 | https://onnx.ai/onnx/intro/python.html | Python API入门 |
| ONNX Operators规范 | https://onnx.ai/onnx/operators/ | 所有算子的完整参考 |
| ONNX GitHub仓库 | https://github.com/onnx/onnx | 源码、Issue、Release |
| ONNX Runtime | https://onnxruntime.ai | 生产级推理引擎 |
| ONNX Runtime GitHub | https://github.com/microsoft/onnxruntime | ORT源码 |

### 工具

| 工具 | 链接 | 用途 |
|------|------|------|
| **Netron** | https://netron.app | 模型可视化（必备） |
| onnx2py.py | https://github.com/microsoft/onnxconverter-common | 图转Python代码便于修改 |
| onnx-graphsurgeon | https://github.com/NVIDIA/TensorRT/tree/main/tools/onnx-graphsurgeon | NVIDIA图修改工具 |
| zetane viewer | https://github.com/zetane/viewer | 执行时查看中间结果 |
| ir-py | https://github.com/onnx/ir-py | 下一代更现代的Python API |
| onnxconverter-common | https://github.com/microsoft/onnxconverter-common | 转换器公共库 |

### 框架导出器

| 框架 | 工具 | 链接 |
|------|------|------|
| PyTorch | torch.onnx（内置） | https://pytorch.org/docs/stable/onnx.html |
| TensorFlow/Keras | tf2onnx | https://github.com/onnx/tensorflow-onnx |
| scikit-learn | skl2onnx | https://github.com/onnx/sklearn-onnx |
| XGBoost/LightGBM | onnxmltools | https://github.com/onnx/onnxmltools |
| PaddlePaddle | paddle2onnx | https://github.com/PaddlePaddle/Paddle2ONNX |

### 模型库与示例

| 资源 | 链接 | 说明 |
|------|------|------|
| ONNX Model Zoo | https://github.com/onnx/models | 官方预训练ONNX模型集合 |
| ONNX Runtime示例 | https://github.com/microsoft/onnxruntime/tree/main/samples | 各种语言/场景的推理示例 |
| ONNX教程 | https://github.com/onnx/tutorials | 官方教程集合 |

---

## 术语表（Glossary）

| 英文术语 | 中文翻译 | 说明 |
|----------|----------|------|
| ONNX | 开放神经网络交换格式 | Open Neural Network Exchange的缩写 |
| Opset | 算子集版本 | Operator Set Version，算子行为契约版本 |
| IR | 中间表示 | Intermediate Representation，ONNX图本身 |
| Graph | 计算图 | 由节点、输入输出、初始化器组成的计算结构 |
| Node | 节点 | 计算图中的算子调用 |
| Input | 输入 | 图的外部输入，运行时提供 |
| Output | 输出 | 图的最终输出 |
| Initializer | 初始化器/常量 | 图中存储的常量张量，可作为权重或默认值 |
| Attribute | 属性 | 算子的固定参数（非运行时输入） |
| Domain | 算子域 | 算子的命名空间（ai.onnx、ai.onnx.ml、自定义域） |
| Tensor | 张量 | 多维数组，ONNX的基本数据类型 |
| Cast | 类型转换算子 | 用于显式张量类型转换 |
| Checker | 模型校验器 | onnx.checker，验证模型一致性 |
| Shape Inference | 形状推断 | 根据输入形状自动计算输出形状 |
| Reference Runtime | 参考运行时 | onnx.reference，仅用于语义验证 |
| ONNX Runtime (ORT) | ONNX运行时 | 微软开发的生产级推理引擎 |
| Provider | 执行提供者 | ORT中的硬件执行后端（CPU/CUDA/TensorRT等） |
| Dynamic Axes | 动态轴 | 形状中可变的维度（如batch size） |
| Constant Folding | 常量折叠 | 编译期计算常量表达式的优化 |
| Quantization | 量化 | 降低数值精度（如FP32→INT8）以减小模型加速推理 |
| Function | 函数 | 用现有算子组合定义的新算子 |
| Custom Operator | 自定义算子 | 用户扩展的非标准算子 |
| Proto | Protobuf消息类 | 以Proto结尾的类（ModelProto、GraphProto等） |
| Serialization | 序列化 | 将内存中的模型转为字节流/文件 |
| Deserialization | 反序列化 | 从字节流/文件恢复模型对象 |
| Dynamic Shape | 动态形状 | 包含None/动态维度的张量形状 |
| Static Shape | 静态形状 | 所有维度都是具体数值的形状 |

---

## 与本Wiki其他章节交叉引用

- [00-overview.md](./00-overview.md)：总览与TL;DR快速结论
- [01-core-concepts.md](./01-core-concepts.md)：核心概念详解（如果某个术语不理解来这里查）
- [02-python-api.md](./02-python-api.md)：Python API实战代码
- [03-quickstart.md](./03-quickstart.md)：5分钟快速上手
- [04-best-practices.md](./04-best-practices.md)：**6个反模式与最佳实践**（生产必读）
- [README.md](./README.md)：Wiki入口导航

---

**上一章**：[04-best-practices.md - 最佳实践与反模式](./04-best-practices.md) | **返回入口**：[README.md](./README.md)
