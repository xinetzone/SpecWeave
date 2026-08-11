---
id: onnx-wiki-best-practices
title: ONNX Wiki - 最佳实践与反模式
date: 2026-08-09
tags:
  - onnx
  - best-practices
  - anti-patterns
  - pitfalls
  - production
source:
  - https://onnx.ai/onnx/intro/concepts.html
  - https://onnx.ai/onnx/intro/python.html
category: knowledge/learning/06-ai-ml-inference
maturity: L1-draft
---

# ONNX 最佳实践与反模式

> **这是本Wiki最重要的一章**。90%的ONNX生产问题都来自本章列出的反模式。遵循"反模式对等原则"：正确做法和反模式成对出现。

---

## 反模式1：用onnx.reference处理生产流量（对应I-002）

### ❌ 反模式描述

看到`pip install onnx`后能跑推理，就直接把`onnx.reference.ReferenceEvaluator`部署到生产环境处理线上请求。

```python
# ❌ 错误：用reference runtime处理生产流量
from onnx.reference import ReferenceEvaluator
sess = ReferenceEvaluator(model)  # 这只是语义参考！
result = sess.run(None, feed_dict)  # 线上请求千万别这么做
```

### 💥 后果

- **性能极差**：reference runtime是纯Python解释执行，比onnxruntime慢100~1000倍
- **无硬件加速**：不支持GPU、TensorRT、CUDA、CPU指令集优化
- **无稳定性保证**：API可能随时变化，官方明确说"不用于生产"
- **资源消耗不可控**：内存占用高，无批量优化，无内存复用

### ✅ 正确做法

处理线上生产流量**必须**使用专用推理引擎：

```python
# ✅ 正确：用onnxruntime处理生产流量
import onnxruntime as ort

# CPU推理
sess = ort.InferenceSession("model.onnx", providers=["CPUExecutionProvider"])

# GPU推理（需要onnxruntime-gpu）
# sess = ort.InferenceSession("model.onnx", providers=["CUDAExecutionProvider"])

result = sess.run(None, feed_dict)
```

> **原则**：reference runtime是非常好的工具——它**适合**：单元测试验证语义正确性、CI环境结果对比、教学演示、调试图结构。但它**绝对不适合**：线上推理服务、性能基准测试、处理大批量真实数据——**永远不要用它处理生产流量**。

---

## 反模式2：期望隐式类型转换（对应I-003）

### ❌ 反模式描述

像NumPy/PyTorch那样，假设float32和int64做Add会自动提升类型：

```python
# ❌ 错误：期望自动类型提升
node_add = helper.make_node("Add", ["float_tensor", "int_tensor"], ["output"])
# check_model直接报错！
```

NumPy里`np.float32(1.0) + np.int64(2)`会自动得到float64(3.0)，但ONNX里这是图校验失败。

### 💥 后果

- `check_model()`直接失败，报错信息可能不直观
- 即使checker没发现，runtime执行时也会崩溃或产生未定义行为
- 新手可能花几小时调试图结构，根源只是少了一个Cast算子

### ✅ 正确做法

混合类型运算必须**显式插入Cast算子**：

```python
# ✅ 正确：显式类型转换
cast_node = helper.make_node(
    "Cast",
    ["int_tensor"],
    ["int_tensor_as_float"],
    to=TensorProto.FLOAT  # 目标类型
)
add_node = helper.make_node(
    "Add",
    ["float_tensor", "int_tensor_as_float"],
    ["output"]
)
```

**类型检查清单**：
- [ ] 运算前检查所有输入dtype是否一致
- [ ] 索引/形状相关张量通常是INT64，需要Cast到FLOAT再参与计算
- [ ] 模型输入输出类型明确声明，不要留到运行时才发现
- [ ] 可以写个辅助函数统一插入Cast节点

---

## 反模式3：盲目追最新opset（对应I-004）

### ❌ 反模式描述

opset_version直接设成最新值（如opset 28），以为"越新越好"。

```python
# ❌ 错误：盲目用最新opset
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 28)])
```

### 💥 后果

- **部署目标runtime不支持**：生产环境的onnxruntime可能是较旧版本，不支持新高opset
- **算子行为变化**：同一算子在不同opset版本语义可能不同，导致精度问题或计算错误
- **框架导出兼容性**：旧版本训练框架可能不支持导出到太高opset
- **回滚困难**：opset只升不降（没有downgrade工具），用了新高opset就很难回退

### ✅ 正确做法

**opset选择策略**：

| 场景 | 推荐opset | 理由 |
|------|-----------|------|
| 不知道部署目标是什么 | 17 或 18 | 兼容性最好，onnxruntime 1.10+都支持 |
| 明确用较新onnxruntime（1.15+） | 19 或 20 | 支持更多算子，稳定性好 |
| 部署环境完全可控（能升级runtime） | 按最新runtime支持的最高版本 | 充分利用新特性 |
| 需要与TensorRT/特定硬件对齐 | 查硬件/runtime文档 | 硬件vendor的opset支持往往滞后 |

```python
# ✅ 正确：选兼容性好的opset
# opset 17是工业界目前最广泛使用的版本
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
```

> **原则**：opset是**行为契约版本**，不是功能级别开关。与部署目标支持的版本对齐，而不是盲目追新。

---

## 反模式4：If分支返回不同数量/类型/形状的输出（对应I-006）

### ❌ 反模式描述

像写Python那样，让If的then和else分支返回不同结构的输出：

```python
# ❌ 错误：两个分支输出数量不一致
then_branch = helper.make_graph(..., outputs=[out1])       # 返回1个
else_branch = helper.make_graph(..., outputs=[out1, out2]) # 返回2个
if_node = helper.make_node("If", ["cond"], ["out1", "out2"], then_branch=then_branch, else_branch=else_branch)
# check_model直接失败！
```

Python里`if cond: return a else: return a, b`完全合法，ONNX里这是硬性错误。

### 💥 后果

- `check_model()`直接失败
- 错误信息可能只说"output count mismatch"，新手可能不知从何改起
- 形状不匹配（如then返回[None, 10]，else返回[None, 20]）也会失败

### ✅ 正确做法

**控制流编写顺序：先定义输出签名，再写内部逻辑**

1. 先确定If节点最终要输出几个张量、什么类型、什么形状
2. 两个分支都必须输出**数量相同、类型相同、形状兼容**的张量
3. 如果确实需要条件性返回不同数量结果，多余的输出填dummy张量（如全0张量）

```python
# ✅ 正确：两个分支输出签名完全一致
# 先定义统一的输出
out_info = helper.make_tensor_value_info("result", TensorProto.FLOAT, [None, 10])

# then_branch和else_branch都必须输出1个FLOAT [None,10]张量
then_branch = helper.make_graph(..., outputs=[out_info])
else_branch = helper.make_graph(..., outputs=[out_info])

if_node = helper.make_node(
    "If",
    ["cond"],
    ["result"],  # 数量、类型、形状与两个分支一致
    then_branch=then_branch,
    else_branch=else_branch
)
```

**控制流检查清单**：
- [ ] 两个分支输出数量完全相等
- [ ] 对应位置输出类型完全相同
- [ ] 对应位置输出形状兼容（None可以匹配任意具体维度）
- [ ] Loop/Scan的输出聚合方式提前确定（拼接成张量 vs 收集成序列）

---

## 反模式5：混淆Initializer和Input的边界（对应I-007）

### ❌ 反模式描述

把Initializer和Input完全对立，认为：
- Initializer = 常量权重（永远不变）
- Input = 运行时喂入的数据（每次不同）

不知道两者可以同名重合实现可选参数。

另一种错误：应该作为Input的运行时数据错误地做成了Initializer（常量），导致推理时无法更改。

### 💥 后果

- **功能无法实现**：不知道可选输入参数机制，到处走"自定义算子"弯路
- **模型不灵活**：本该可配置的阈值/超参数被硬编码为Initializer，改参数要重新导出模型
- **概念混淆**：手写图时搞不清哪些该放input、哪些该放initializer

### ✅ 正确做法

明确Initializer的两种使用模式：

| 模式 | 名称是否与Input重名 | 语义 | 使用场景 |
|------|---------------------|------|----------|
| **纯常量模式** | ❌ 不重名 | 图内部常量，用户无法覆盖 | 训练好的权重W、偏置b、固定不变的超参数 |
| **可选默认值模式** | ✅ 重名 | Input的默认值，传了覆盖、不沿用默认 | 可选阈值、后处理参数、调试开关 |

```python
# ✅ 正确1：纯常量Initializer（权重）
W = numpy_helper.from_array(weight_array, name="W")
# W不与任何Input重名 → 纯常量，无法覆盖

# ✅ 正确2：可选参数默认值
threshold_input = helper.make_tensor_value_info("threshold", TensorProto.FLOAT, [])
threshold_default = numpy_helper.from_array(np.array(0.5), name="threshold")
# threshold_input和threshold_default同名 → 不传用0.5，传了覆盖
```

**边界判断指南**：
- 这个值推理时每次都变吗？→ 必须是Input，不能是Initializer
- 这个值训练完就固定了吗？→ 纯常量Initializer
- 这个值通常用默认值，但用户可能想改？→ Initializer（默认值）+ Input（同名）

---

## 反模式6：过度使用控制流算子

### ❌ 反模式描述

像写Python程序那样，在ONNX图里大量使用If/Loop/Scan算子，把ONNX当通用编程语言用。

```python
# ❌ 错误：过度控制流，性能极差
for i in range(100):
    # ... 每个循环体都有很多算子 ...
# ONNX的Loop不是Python for循环，性能天差地别
```

### 💥 后果

- **性能极差**：ONNX运行时对控制流优化很弱，特别是嵌套循环
- **可移植性差**：不同runtime对复杂控制流的支持程度不一
- **调试困难**：控制流内的错误很难定位
- **失去了张量计算的优势**：ONNX的优势是批量张量并行计算，控制流让它退回到逐元素解释执行

### ✅ 正确做法

**优先用张量操作替代控制流**：

| Python写法（控制流） | ONNX写法（张量化） |
|----------------------|---------------------|
| `for x in data: sum += x` | `ReduceSum(data)` |
| `if x > 0: x else 0` | `x * Greater(x, 0)`（或Relu） |
| `for i in range(N): out[i] = f(in[i])` | 直接批量计算`f(in)`（算子天然支持batch） |
| 条件分支选择两个张量之一 | `Where(cond, a, b)` |

**控制流使用原则**：
- ✅ **可以用**：循环次数固定且较少、确实无法张量化的逻辑、动态长度序列处理（RNN类）
- ❌ **尽量避免**：逐元素循环、复杂嵌套条件、本可张量化的操作
- 如果控制流逻辑太复杂，考虑：
  1. 能不能拆成多个模型顺序执行？
  2. 能不能把逻辑移到模型外（前后处理用Python做）？
  3. 是不是应该用自定义算子？

---

## 通用最佳实践

### 1. Checker是你最好的朋友

- **每改几步就check一次**，不要等图写完了才check——错误越早发现越容易定位
- 不要忽略checker警告，警告往往预示着潜在问题

```python
onnx.checker.check_model(model)  # 每次图结构变更后必跑
```

### 2. 形状推断随时做

```python
model = onnx.shape_inference.infer_shapes(model)
```
- 帮助发现形状不匹配问题
- 可视化（Netron）时能看到完整形状信息
- 辅助runtime内存预分配

### 3. 输入输出类型明确声明

- 不要留模糊的类型定义
- 静态维度尽量写具体值，动态维度用None
- 输入名称要有意义，不要用"input1"/"input2"

### 4. 每次导出/修改后做三件事

1. **Check**：`onnx.checker.check_model(model)`
2. **Visualize**：用Netron打开看图结构是否符合预期
3. **Verify**：用一组样本对比原框架和ONNX输出，确认误差在可接受范围

### 5. 生产上线完整验证Checklist

模型上生产前必须逐项确认：

- [ ] **结构校验**：`onnx.checker.check_model()`无错误无警告
- [ ] **可视化确认**：Netron看图结构符合预期，输入输出名称/类型/形状正确
- [ ] **精度验证**：
  - [ ] 至少100+代表性样本对比原框架输出
  - [ ] 相对误差阈值：分类任务<1e-3，回归任务<1e-4（根据业务调整）
  - [ ] 边界case（极值、零值、异常输入）测试通过
- [ ] **性能基准**：
  - [ ] 目标硬件上单样本/批量延迟符合要求
  - [ ] 吞吐量QPS满足业务峰值
  - [ ] 内存占用在预期范围内
- [ ] **版本兼容**：
  - [ ] opset版本与生产runtime版本兼容
  - [ ] 测试环境与生产环境runtime版本一致
  - [ ] 模型元数据记录了版本信息（opset、onnx版本、导出框架版本）
- [ ] **降级预案**：准备好旧版本模型回滚方案

### 6. 版本固定记录

在模型元数据里记录清楚：
- onnx包版本
- opset版本
- 导出框架版本（PyTorch/TensorFlow版本）
- 导出日期

```python
helper.set_model_props(model, {
    "framework": "pytorch",
    "framework_version": torch.__version__,
    "onnx_version": onnx.__version__,
    "opset": "17",
})
```

---

## 反模式速查表

| 反模式 | 对应洞察 | 一句话总结 |
|--------|----------|------------|
| 用onnx.reference跑生产 | I-002 | reference是语义参考，onnxruntime才是生产 |
| 期望隐式类型转换 | I-003 | 混合类型必须显式Cast，没有自动提升 |
| 盲目追最新opset | I-004 | opset是契约，选部署目标支持的版本 |
| If分支输出签名不一致 | I-006 | 先定输出签名，再写分支逻辑 |
| 混淆Initializer和Input边界 | I-007 | 同名Initializer是Input默认值，不是二选一 |
| 过度使用控制流 | - | 优先张量化，控制流是最后手段 |

> **记住**：ONNX不是通用编程语言，它是张量计算DSL。用张量思维写ONNX，而不是用Python思维写ONNX。

---

**上一章**：[03-quickstart.md - 快速上手](./03-quickstart.md) | **下一章**：[05-faq-and-resources.md - FAQ与资源](./05-faq-and-resources.md)
