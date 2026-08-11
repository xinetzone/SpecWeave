---
id: onnx-wiki-python-api
title: ONNX Wiki - Python API实战
date: 2026-08-09
tags:
  - onnx
  - python
  - api
  - tutorial
  - linear-regression
source:
  - https://onnx.ai/onnx/intro/python.html
category: knowledge/learning/06-ai-ml-inference
maturity: L1-draft
---

# ONNX Python API实战

本章通过从零构建**线性回归**模型，系统讲解ONNX Python API。代码基于onnx 1.23.0，可直接复制运行。

> **洞察 I-005**：Python API是"函数式组装+字符串接线"模式——你不是在操作可变的图对象，而是在用纯函数一步一步拼装protobuf消息，中间结果全靠字符串"接线"。

---

## 四大Helper函数详解

ONNX Python API的核心是四个Helper函数（共26个make_*函数，这四个最常用）：

| 函数 | 作用 | 对应组件 |
|------|------|----------|
| `make_tensor_value_info(name, elem_type, shape)` | 声明输入/输出变量 | Input/Output |
| `make_node(op_type, inputs, outputs, **kwargs)` | 创建算子节点 | Node |
| `make_graph(nodes, name, inputs, outputs, initializer=None)` | 组装计算图 | Graph |
| `make_model(graph, **kwargs)` | 生成最终模型（含元数据） | Model |

---

## 字符串接线模式解释

> 这是最容易让OO思维用户困惑的地方：

节点之间的连接**不是通过对象引用**，而是通过**字符串名称匹配**：

- 节点的输出名是一个字符串
- 下游节点的输入名是同一个字符串
- ONNX通过字符串相等性来判断数据流连接

```python
# 示例：MatMul输出名为"matmul_out"，Add的第一个输入也是"matmul_out"
node1 = make_node("MatMul", ["X", "W"], ["matmul_out"])
node2 = make_node("Add", ["matmul_out", "b"], ["y"])
# "matmul_out"这个字符串把两个节点连起来了
```

> **注意**：写错字符串名称不会在Python层报错，只会在`check_model()`时失败！建议使用常量定义名称，避免拼写错误。

---

## 完整可运行线性回归示例

我们实现：`y = X @ W + b`，其中W和b是训练好的权重（常量），X是输入。

```python
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper


# ============================================================
# 步骤1：定义输入输出（声明变量）
# ============================================================
# make_tensor_value_info(name, elem_type, shape)
# - name: 字符串名称（用于接线）
# - elem_type: TensorProto.FLOAT等类型枚举
# - shape: 形状列表，None表示动态维度

# 输入X：批量大小动态(None)，特征数2
X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [None, 2])

# 输出y：批量大小动态(None)，输出维度1
y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [None, 1])


# ============================================================
# 步骤2：创建Initializer（常量权重）
# ============================================================
# numpy_helper.from_array把numpy数组转为TensorProto
# 注意：name参数必须与接线用的字符串一致！

# 权重W：shape [2, 1]，假设已训练好的值
W_init = numpy_helper.from_array(
    np.array([[0.5], [0.8]], dtype=np.float32),
    name="W"
)

# 偏置b：shape [1]
b_init = numpy_helper.from_array(
    np.array([0.1], dtype=np.float32),
    name="b"
)


# ============================================================
# 步骤3：创建节点（算子调用）
# ============================================================
# make_node(op_type, inputs, outputs, **attributes)
# - op_type: 算子类型字符串（如"MatMul", "Add"）
# - inputs: 输入名称列表（字符串）
# - outputs: 输出名称列表（字符串）
# - **kwargs: 算子属性（如Transpose的perm=[1,0]）

# 节点1：矩阵乘法 MatMul(X, W) -> matmul_out
node_matmul = helper.make_node(
    "MatMul",
    inputs=["X", "W"],
    outputs=["matmul_out"]
)

# 节点2：加法 Add(matmul_out, b) -> y
node_add = helper.make_node(
    "Add",
    inputs=["matmul_out", "b"],
    outputs=["y"]
)

# 节点列表按执行顺序排列（虽然ONNX会自动拓扑排序，但建议按顺序写）
nodes = [node_matmul, node_add]


# ============================================================
# 步骤4：组装计算图
# ============================================================
# make_graph(nodes, graph_name, inputs, outputs, initializer=None)
graph = helper.make_graph(
    nodes=nodes,
    name="LinearRegression",
    inputs=[X],
    outputs=[y],
    initializer=[W_init, b_init]
)


# ============================================================
# 步骤5：生成模型（添加元数据和opset信息）
# ============================================================
# make_model会自动设置默认opset导入，建议显式指定
model = helper.make_model(
    graph,
    producer_name="onnx-wiki-tutorial",
    opset_imports=[helper.make_opsetid("", 17)]  # 使用opset 17兼容性好
)


# ============================================================
# 步骤6：校验模型（强烈建议每次都做！）
# ============================================================
onnx.checker.check_model(model)
print("✅ 模型校验通过！")


# ============================================================
# 步骤7：形状推断（可选但推荐）
# ============================================================
model = onnx.shape_inference.infer_shapes(model)
print("✅ 形状推断完成！")


# ============================================================
# 步骤8：序列化保存到文件
# ============================================================
onnx.save(model, "linear_regression.onnx")
print("✅ 模型已保存到 linear_regression.onnx")
```

---

## 模型序列化/反序列化

### 保存模型

```python
# 方式1：直接保存到文件
onnx.save(model, "model.onnx")

# 方式2：序列化为bytes（可用于网络传输、内存缓存）
model_bytes = model.SerializeToString()
with open("model.onnx", "wb") as f:
    f.write(model_bytes)
```

### 加载模型

```python
# 方式1：从文件加载
model = onnx.load("model.onnx")

# 方式2：从bytes加载
model = onnx.load_from_string(model_bytes)

# 加载后记得校验！
onnx.checker.check_model(model)
```

---

## Checker模型校验

`onnx.checker.check_model()`是你最好的朋友：

- 检查类型一致性
- 检查输入输出是否存在
- 检查算子是否在指定opset中定义
- 检查形状不匹配（静态可确定的部分）
- 检查属性是否合法

> **建议**：每次修改图结构后立即运行checker，不要等到最后才检查——错误越早发现越容易定位。

```python
try:
    onnx.checker.check_model(model)
except onnx.checker.ValidationError as e:
    print(f"❌ 模型校验失败: {e}")
    # 处理错误...
```

---

## 形状推断

形状推断帮你自动计算中间张量的形状：

```python
from onnx import shape_inference

# 推断形状，返回新的model对象（原对象不变）
model_with_shapes = shape_inference.infer_shapes(model)

# 查看每个value_info的形状
for vi in model_with_shapes.graph.value_info:
    shape = [d.dim_value if d.dim_value else "?" for d in vi.type.tensor_type.shape.dim]
    print(f"{vi.name}: {shape}")
```

---

## Reference Runtime求值（语义参考）

> ⚠️ **重要警告（洞察 I-002）**：`onnx.reference`是**语义参考实现**，目的是阐明ONNX算子语义，**禁止用于生产流量**！它没有性能优化、没有硬件加速、不保证API稳定性。但它非常适合：单元测试验证语义正确性、CI环境结果对比、教学演示、调试图结构。生产环境处理真实流量必须用onnxruntime等专用推理引擎。

```python
from onnx.reference import ReferenceEvaluator

# 创建参考运行时
sess = ReferenceEvaluator(model)

# 准备输入数据（必须是numpy数组，类型与模型定义一致！）
X_test = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

# 运行推理
results = sess.run(None, {"X": X_test})
y_pred = results[0]

print("输入X:")
print(X_test)
print("\n预测y:")
print(y_pred)
print("\n手动计算验证:")
print(X_test @ np.array([[0.5], [0.8]], dtype=np.float32) + 0.1)
```

### Reference Evaluator适用场景

✅ **可以用**：
- 验证算子语义是否符合预期
- 单元测试中与其他框架结果对比
- 调试图结构问题
- 教学演示

❌ **绝对不要用**：
- 生产环境推理
- 性能基准测试
- 处理大批量数据
- 任何需要速度的场景

> **生产环境请用onnxruntime**：
> ```python
> import onnxruntime as ort
> sess = ort.InferenceSession("linear_regression.onnx", providers=["CPUExecutionProvider"])
> y_pred = sess.run(None, {"X": X_test})[0]
> ```

---

## Initializer可选参数模式（洞察 I-007）

Initializer有两种使用模式：

### 模式1：纯常量Initializer（默认，不与Input重名）

Initializer名称不与任何Input重名 → 它是图内部的常量，用户无法覆盖。这就是我们线性回归例子中的用法——W和b是训练好的权重，永远不变。

### 模式2：可选输入默认值（与Input重名）

Initializer名称与某个Input**同名** → 它成为该Input的默认值！推理时不传该输入则使用默认值，显式传入则覆盖默认值。这是ONNX实现可选参数的官方机制。

```python
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper

# 示例：一个带可选阈值threshold的后处理算子
# threshold不传入时默认0.5，传入时用用户提供的值

# 同时声明Input和同名Initializer！
threshold_input = helper.make_tensor_value_info("threshold", TensorProto.FLOAT, [])
threshold_default = numpy_helper.from_array(np.array(0.5, dtype=np.float32), name="threshold")

# 其他输入输出...
X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [None])
y = helper.make_tensor_value_info("y", TensorProto.BOOL, [None])

# Greater(X, threshold) -> y
node = helper.make_node("Greater", ["X", "threshold"], ["y"])

graph = helper.make_graph(
    [node],
    "OptionalThresholdExample",
    inputs=[X, threshold_input],  # threshold是Input
    outputs=[y],
    initializer=[threshold_default]  # 同时有同名Initializer作为默认值
)

model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
onnx.checker.check_model(model)

# 测试
sess = onnx.reference.ReferenceEvaluator(model)

# 不传threshold，使用默认值0.5
result1 = sess.run(None, {"X": np.array([0.3, 0.7], dtype=np.float32)})
print("默认阈值0.5:", result1[0])  # [False, True]

# 显式传threshold=0.6，覆盖默认值
result2 = sess.run(None, {"X": np.array([0.3, 0.7], dtype=np.float32),
                         "threshold": np.array(0.6, dtype=np.float32)})
print("阈值0.6:", result2[0])  # [False, True]
```

> **这是一个极其有用但鲜为人知的特性**！很多人不知道ONNX原生支持可选输入参数，到处用常量折叠或者自定义算子，其实用Initializer默认值模式就可以优雅实现。

---

## numpy_helper工具函数

在numpy数组和ONNX TensorProto之间转换：

```python
from onnx import numpy_helper

# numpy → TensorProto
arr = np.array([[1, 2], [3, 4]], dtype=np.float32)
tensor = numpy_helper.from_array(arr, name="my_tensor")

# TensorProto → numpy
arr_back = numpy_helper.to_array(tensor)

# 类型转换工具
from onnx.helper import tensor_dtype_to_np_dtype, tensor_dtype_to_string
np_dtype = tensor_dtype_to_np_dtype(TensorProto.FLOAT)  # np.float32
type_str = tensor_dtype_to_string(TensorProto.FLOAT)     # "FLOAT"
```

---

## 代码验证清单

运行完上述代码后，你应该看到：
1. ✅ 模型校验通过
2. ✅ 形状推断完成
3. ✅ 生成linear_regression.onnx文件
4. ✅ ReferenceEvaluator预测结果与手动计算一致
5. ✅ 可选参数示例中，不传threshold用默认值，传了则覆盖

> **下一章**：[03-quickstart.md - 快速上手指南](./03-quickstart.md) 将带你5分钟跑通第一个ONNX模型。

---

**上一章**：[01-core-concepts.md - 核心概念详解](./01-core-concepts.md) | **下一章**：[03-quickstart.md - 快速上手](./03-quickstart.md)
