---
id: "onnx-pre-quantize-simplification"
title: "ONNX 量化前简化模式"
type: "code-pattern"
date: "2026-08-10"
maturity: "L1-draft"
source: "apps/devcontainer-base/variants/onnx-quantized/Dockerfile + external/chaos/ai (2026-08-10)"
related_patterns:
  - "framework-parameter-semantics-verification"
  - "incremental-regression-verification"
tags: ["onnx", "quantization", "onnxsim", "shape-inference", "torch", "onnxruntime"]
validation_count: 1
reuse_count: 0
---

# ONNX 量化前简化模式

## 触发场景

- 用 `torch.onnx.export` 导出 ONNX 模型后，再进行 `quantize_dynamic` / `quantize_static` 动态或静态量化
- 量化时遇到 `ShapeInferenceError`：`Inferred shape and existing shape differ in dimension 0: (64) vs (128)`
- 构建 Docker 镜像或 CI 流水线中，量化冒烟测试偶发/必现的形状推断冲突

**不适用于**：
- 直接手写、已确保 shape 自洽的 ONNX 图（无需简化）
- 使用非 torch 导出、本身经过 checker 验证且量化不报错的模型（保持现状即可，无需引入 onnxsim 依赖）

## 核心做法

### 1. 量化前统一简化

任何从 torch 导出的 ONNX 模型，在量化前先执行 `onnxsim.simplify`，再 `onnx.checker.check_model` 确认形状自洽：

```python
import onnx
import onnxsim

m = onnx.load(fp32_path)
m2, ok = onnxsim.simplify(m)
if ok:
    onnx.save(m2, fp32_path)
onnx.checker.check_model(onnx.load(fp32_path))
```

### 2. torch 导出时开启常量折叠

`torch.onnx.export` 时显式传 `do_constant_folding=True`，从源头减少图中残留的、导致 shape inference 冲突的常量计算节点：

```python
torch.onnx.export(
    model, sample,
    fp32_path,
    do_constant_folding=True,
    input_names=["input"], output_names=["output"],
)
```

### 3. 内联回归防护

将「导出 → 简化 → 量化 → checker → 推理」完整链路内联到构建层冒烟测试（而非外部脚本），使 shape inference 问题复发时构建立即失败，保证镜像产物自带验证能力且修复可追踪。

## 反模式（不要这么做）

### ❌ 反模式1：跳过简化直接量化

```python
m = onnx.load(fp32_path)
quantize_dynamic(fp32_path, int8_path)   # 直接量化，未先 simplify
# 报 ShapeInferenceError: Inferred shape and existing shape differ
```
- 后果：量化 shape inference 阶段崩溃，构建中断，且错误信息晦涩。

### ❌ 反模式2：忽略 `onnxsim.simplify` 的返回值

```python
m2, ok = onnxsim.simplify(m)
onnx.save(m2, fp32_path)   # 未检查 ok，简化失败时静默保存未简化图
```
- 后果：`ok=False` 时仍继续，等于没简化，问题依旧；必须检查 `ok` 再保存。

### ❌ 反模式3：同一问题多处修复但不统一为通用规则

- 后果：QSMOKE/ORTUNIT/QCHECK 三处各自打补丁，根因一致却未沉淀成一条通用预处理规则，后续新场景重复踩坑。

### ❌ 反模式4：把冒烟测试放在外部脚本而非构建层

- 后果：验证能力脱离镜像产物，无法保证每次构建都自动校验，修复不可追踪。

## 检验标准

做完之后怎么知道做对了？

1. 量化前简化后 `onnx.checker.check_model` 通过，无 `ShapeInferenceError`
2. `quantize_dynamic` 动态 INT8 量化成功，INT8 模型可正常推理
3. FP32 与 INT8 推理输出 shape 一致
4. 冒烟测试内联到构建层，任一环节 shape 冲突复发时构建立即失败

## 迁移示例

| 来源 | 简化/前置校验工具 |
|------|------------------|
| torch → onnxruntime 量化 | `onnxsim.simplify` + `onnx.checker.check_model` |
| 其他框架导出 ONNX | 先 `onnx.checker.check_model`，再决定是否需要 onnxsim |
| 通用图优化 | onnxruntime 的 `GraphOptimizationLevel` 作为量化外的前置 |

### 跨领域迁移
- **编译器中间表示**：任何"先优化/规约再分析"的流水线，都应在前置优化阶段先做形状/类型自洽校验
- **数据管道**：ETL 中复杂转换后先做 schema 校验再入量化/落库，避免脏数据带病进入下游

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [framework-parameter-semantics-verification.md](framework-parameter-semantics-verification.md) | 互补 | 该模式强调查源码确认参数语义；本模式强调导出后图的自洽性预处理 |
| [incremental-regression-verification.md](../architecture-patterns/incremental-regression-verification.md) | 互补 | 冒烟测试内联到构建层即回归防护的落点 |

## 待验证场景

本模式目前为 L1-draft（单项目验证），建议在以下场景验证：
1. 静态量化（`quantize_static`）是否同样受 shape inference 冲突影响
2. onnxruntime ≥ 1.28 新版本是否已自动缓解该问题（若已缓解可降级为可选优化）
3. 大规模模型（>1GB）简化耗时与收益权衡
