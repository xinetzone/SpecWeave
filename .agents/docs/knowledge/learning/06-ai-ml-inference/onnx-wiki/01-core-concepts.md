---
id: onnx-wiki-core-concepts
title: ONNX Wiki - 核心概念详解
date: 2026-08-09
tags:
  - onnx
  - deep-learning
  - core-concepts
  - computation-graph
  - type-system
source:
  - https://onnx.ai/onnx/intro/concepts.html
category: knowledge/learning/06-ai-ml-inference
maturity: L1-draft
---

# ONNX 核心概念详解

本章系统讲解ONNX的11个核心概念，贯穿案例使用**线性回归**：`y = X @ W + b`。

---

## 1. ONNX计算图本质：DSL语言而非文件格式

> **洞察 I-001**：ONNX本质是一门专门用于张量数值计算的、强类型的、纯函数式的领域特定语言（DSL），protobuf只是这门语言的二进制序列化编码方式。构建ONNX模型本质上是在"用ONNX算子编程"，而非"保存权重"。

这是理解ONNX最关键的心智模型转换：

| 错误直觉（文件格式思维） | 正确认知（DSL编程思维） |
|--------------------------|--------------------------|
| ONNX是像pickle/PMML那样的模型保存格式 | ONNX是像SQL那样的专用编程语言 |
| "导出模型" = "把权重存起来" | "构建图" = "用ONNX算子写函数" |
| onnx文件 = 权重文件 | onnx文件 = 编译后的程序二进制 |
| 只需要关心权重对不对 | 需要关心类型、版本、算子语义、控制流 |

**线性回归类比**：你不是在"保存W和b两个数组"，而是在定义一个函数`f(X) = MatMul(X, W) + b`，这个函数由MatMul和Add两个算子组成。

使用ONNX实现的机器学习模型通常被称为**ONNX图（ONNX graph）**。

---

## 2. 五大核心组件

ONNX图由五个核心组件构成，我们用线性回归`y = X @ W + b`为例说明：

```
X (Input) ──┐
            ├─→ MatMul(Node) ──→ intermediate ──┐
W (Initializer) ──┘                              ├─→ Add(Node) ──→ y (Output)
                                                 │
b (Initializer) ─────────────────────────────────┘
```

| 组件 | 作用 | 线性回归中的对应 | 特点 |
|------|------|------------------|------|
| **Input（输入）** | 图的外部输入，运行时由用户提供 | `X`（特征矩阵） | 有名称、类型、形状，形状可以是动态（None） |
| **Output（输出）** | 图的最终输出，返回给调用者 | `y`（预测值） | 同Input，有名称/类型/形状 |
| **Node（节点）** | 算子调用，执行具体计算 | `MatMul`、`Add` | 有算子类型、输入名列表、输出名列表、属性 |
| **Initializer（初始化器）** | 图中存储的常量 | `W`（权重）、`b`（偏置） | 与Input同名时成为可选输入默认值（见I-007） |
| **Attribute（属性）** | 算子的固定参数，加载后冻结 | MatMul可能没有，Gemm有alpha/beta/transA/transB | 不是运行时输入，是算子的编译期参数 |

> **关键记忆点**：节点之间不是通过对象引用连接，而是通过**字符串名称匹配**——节点输出名 = 下游节点输入名。这是函数式组装API的核心（见I-005）。

---

## 3. Protobuf序列化机制

ONNX使用**Protobuf（Protocol Buffers）**将计算图序列化为单个二进制块：

- **序列化**：`model.SerializeToString()` → bytes，可写入`.onnx`文件
- **反序列化**：`onnx.load("model.onnx")` → 恢复ModelProto对象
- **大小限制**：单模型序列化大小 < 2GB（Protobuf硬限制）
- **优势**：存储空间优化、跨语言/跨平台加载、向前向后兼容
- **相关类**：ONNX模块包含25个以`Proto`结尾的类（AttributeProto、GraphProto、ModelProto、NodeProto、TensorProto等）

> Protobuf只是编码方式，不是ONNX本身——类比：class文件是JVM字节码的编码，但Java是编程语言，不是class文件格式。

---

## 4. 算子域（Operator Domains）

ONNX算子按域（domain）组织，每个域有独立的opset版本：

| 域标识 | 包含内容 | 典型算子 |
|--------|----------|----------|
| **`ai.onnx`** | 标准算子域（默认） | 矩阵算子：Add、Sub、MatMul、Transpose、Reshape<br>归约算子：ReduceSum、ReduceMin<br>图像算子：Conv、MaxPool<br>神经网络层：RNN、DropOut<br>激活函数：Relu、Softmax |
| **`ai.onnx.ml`** | 传统机器学习域 | 树模型：TreeEnsembleRegressor<br>预处理：OneHotEncoder、LabelEncoder<br>SVM模型：SVMRegressor<br>数据处理：Imputer |
| **自定义域** | 用户/第三方扩展 | 如`com.yourcompany.ops` |

> **重要**：多域模型必须为每个域单独指定opset版本，互不影响。

---

## 5. 张量类型系统

ONNX是**强类型规范，定义中不支持任何隐式类型转换**（I-003）。

### 张量三要素

1. **元素类型**：所有元素类型必须相同，共26种
2. **形状**：维度数组，可以为空；维度值可以是null（动态维度）
3. **连续值数组**：密集张量，无strides，不支持视图

### 完整26种元素类型表

| 枚举值 | 类型名 | numpy对应类型 | 说明 |
|--------|--------|---------------|------|
| 1 | FLOAT | float32 | 32位浮点数（最常用） |
| 2 | UINT8 | uint8 | 8位无符号整数 |
| 3 | INT8 | int8 | 8位有符号整数 |
| 4 | UINT16 | uint16 | 16位无符号整数 |
| 5 | INT16 | int16 | 16位有符号整数 |
| 6 | INT32 | int32 | 32位有符号整数 |
| 7 | INT64 | int64 | 64位有符号整数（索引常用） |
| 8 | STRING | str | 字符串类型 |
| 9 | BOOL | bool | 布尔类型 |
| 10 | FLOAT16 | float16 | 16位浮点数 |
| 11 | DOUBLE | float64 | 64位浮点数 |
| 12 | UINT32 | uint32 | 32位无符号整数 |
| 13 | UINT64 | uint64 | 64位无符号整数 |
| 14 | COMPLEX64 | complex64 | 64位复数 |
| 15 | COMPLEX128 | complex128 | 128位复数 |
| 16 | BFLOAT16 | bfloat16 | Brain浮点数 |
| 17 | FLOAT8E4M3FN | - | 8位浮点数（训练常用） |
| 18 | FLOAT8E4M3FNUZ | - | 8位浮点数 |
| 19 | FLOAT8E5M2 | - | 8位浮点数（推理常用） |
| 20 | FLOAT8E5M2FNUZ | - | 8位浮点数 |
| 21 | UINT4 | - | 4位无符号整数 |
| 22 | INT4 | - | 4位有符号整数 |
| 23 | FLOAT4E2M1 | - | 4位浮点数 |
| 24 | FLOAT8E8M0 | - | 8位浮点数 |
| 25 | UINT2 | - | 2位无符号整数 |
| 26 | INT2 | - | 2位有符号整数 |

> **反常识警告**：NumPy的int+float自动提升、Python鸭子类型、PyTorch自动类型提升在ONNX里**完全不存在**。float32 + int64直接报错，必须显式插入`Cast`算子！

### 其他类型

除了密集张量，ONNX还支持：
- **SparseTensorProto**：2D稀疏张量（dims、indices、values）
- **SequenceProto**：张量序列
- **MapProto**：张量映射（字典）

---

## 6. opset版本机制：算子行为契约

> **洞察 I-004**：opset版本不是越高越好的功能开关，而是图中所有算子遵循的行为契约版本。

### 核心规则

- 每个ONNX图附加一个全局opset版本（多域则每个域一个）
- 图中的算子遵循**低于或等于**全局opset版本的**最新定义**
- 示例：Add算子在v6、v7、v13、v14更新
  - 图opset=15 → Add遵循v14规范
  - 图opset=12 → Add遵循v7规范
- opset版本映射到onnx包版本：onnx 1.23.0对应opset 28
- IR版本（当前v13）定义ONNX语言本身的版本，与opset独立

### 版本选错的后果

- opset设太高 → 部署目标runtime不支持
- 算子行为变化 → 精度问题、计算结果不一致

> **原则**：opset版本与部署目标runtime支持的最高版本对齐，而不是盲目追新。

---

## 7. 控制流（If/Scan/Loop）

ONNX提供三个控制流算子，**输出签名一致性是隐形炸弹**（I-006）。

### If算子

- 根据条件执行`then_branch`或`else_branch`两个子图之一
- **硬性约束**：两个子图必须产生**数量完全相同、类型完全一致、形状兼容**的输出
- ❌ Python里合法的写法：`if cond: return a else: return a, b`
- ✅ ONNX要求：两个分支返回值数量、类型、形状必须字面上一致

### Scan算子

- 实现固定次数迭代的循环
- 沿输入的某一维度循环
- 沿同一轴连接输出

### Loop算子

- 实现for和while循环（固定次数或条件终止）
- 输出有两种机制：
  1. 沿第一维连接成张量
  2. 连接成张量序列

> **编写顺序建议**：**先定义好输出签名（数量/类型/形状），再写两个分支的内部逻辑**，而不是反过来。

---

## 8. 扩展性：自定义算子

ONNX原生支持自定义算子扩展：

- 使用自定义域名（如`com.yourcompany.ops`）
- 为自定义域指定opset版本
- 自定义算子在目标runtime中需要有对应的实现
- 常用场景：特殊后处理逻辑、硬件特定优化算子、研究中的新算子

---

## 9. Functions（函数组合）

Functions是**使用现有ONNX算子定义的算子组合**：

- 定义后行为与其他算子完全相同：有输入、输出、属性
- 通过`make_function`创建：指定域名、函数名、输入/输出名列表、节点列表、opset导入、属性名列表
- 作用：
  - 封装重复子图
  - 提高图可读性
  - 作为自定义算子的纯ONNX实现（无需runtime扩展）

---

## 10. 形状推断（Shape Inference）

形状推断是ONNX的重要工具——**新手一定要跑，能帮你省很多调试时间**。

- 在已知输入形状的情况下计算大多数标准算子的输出形状
- 帮助运行时管理内存
- 通过`onnx.shape_inference.infer_shapes()`执行
- **为什么要做？不做会怎样？**
  - ✅ **提前发现形状不匹配错误**：比如MatMul的两个矩阵维度对不上，不用等到推理时才崩溃，checker+形状推断阶段就能发现
  - ✅ **Netron可视化时能看到完整形状**：不做形状推断的话，Netron里很多中间张量形状显示为"?"
  - ✅ **无需运行即可获得完整形状信息**：静态分析就能知道整个图的张量形状
  - ⚠️ **不做会怎样**：模型本身仍然可以运行，但你失去了静态检查的机会，形状错误要到推理时才能发现，调试更困难
  - ⚠️ **注意**：动态维度（None）无法推断出具体值，这是正常的

---

## 11. 工具链

| 工具 | 用途 | 地址 |
|------|------|------|
| **Netron** | 无需编程即可可视化ONNX图 | https://netron.app |
| **onnx2py.py** | 从ONNX图创建Python文件，可修改图结构 | https://github.com/microsoft/onnxconverter-common/blob/master/onnxconverter_common/onnx2py.py |
| **zetane** | 加载模型并在执行时显示中间结果 | https://github.com/zetane/viewer |
| **ir-py** | 更现代更符合人体工程学的Python API | https://github.com/onnx/ir-py |
| **onnxruntime** | 生产级推理引擎 | https://onnxruntime.ai |

> **Netron是必备工具**——遇到图相关问题，第一反应应该是用Netron打开看看结构对不对。

---

## 贯穿案例：线性回归的组件映射

我们用线性回归`y = X @ W + b`总结所有概念：

| 概念 | 线性回归中的体现 |
|------|------------------|
| DSL本质 | 我们在定义函数`f(X) = MatMul(X, W) + b`，不是存两个数组 |
| Input | X：形状[None, n_features]，类型FLOAT |
| Output | y：形状[None, 1]，类型FLOAT |
| Node | MatMul（矩阵乘）、Add（加偏置） |
| Initializer | W（权重，形状[n_features, 1]）、b（偏置，形状[1]） |
| Protobuf | 序列化为linear_regression.onnx文件 |
| 算子域 | ai.onnx（MatMul和Add都在标准域） |
| 类型 | 所有张量都是FLOAT，类型一致无需Cast |
| opset | 选择与部署runtime匹配的版本（如opset 17兼容性好） |
| 控制流 | 线性回归不需要控制流 |
| 形状推断 | X@W形状是[None, 1]，加b后还是[None, 1] |

下一章我们将用Python API实际构建这个线性回归模型。

---

**上一章**：[00-overview.md - 总览](./00-overview.md) | **下一章**：[02-python-api.md - Python API实战](./02-python-api.md)
