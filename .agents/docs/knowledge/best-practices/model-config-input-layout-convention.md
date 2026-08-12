---
id: model-config-input-layout-convention
title: 模型编译 config 输入布局核验与修正规范（NCHW/NHWC）
category: best-practices
tags: ["model-compile", "config", "input-layout", "NCHW", "NHWC", "NV12", "onnx2pytorch", "tvm", "adaround", "checklist", "caffe", "onnx"]
date: "2026-08-12"
last_updated: "2026-08-12"
status: active
author: SpecWeave Orchestrator
summary: 从 palmDet 模型编译失败修复沉淀的规范：工具链强制按 NCHW 解包输入 shape，config 输入布局必须与模型（Caffe/ONNX）实际布局一致；提供布局判定、修正方案、新模型接入核验检查清单与配套算子转换修复。
security_level: "public"
knowledge_type: "procedural"
validation_status: "verified"
reuse_count: "1"
integrity: "unchecked"
source: "insight-palmdet-compile-failure-20260812 / summary-palmdet-compile-fix-20260812"
---

# 模型编译 config 输入布局核验与修正规范

> 一句话摘要：XMNN 工具链强制按 NCHW 解包输入 shape，若 config 输入布局与模型（Caffe/ONNX）实际布局不一致，将产生"校准图尺寸错误 + relay 输入通道不匹配"的隐蔽编译失败。本文提供布局判定、修正方案与接入核验检查清单。

---

## 1. 概述

在 XMNN 模型编译流程中，`config.toml` 的 `[input]` 段声明模型输入 `shape` 与 `layout`。**工具链强制按 NCHW 解包输入 shape**（见 [data.py](../../../../external/chaos/npuusertools/xmnn/data.py) 中 `N, C, H, W = model_shape`），并不会因 config 写成 NHWC 而自动转置。

因此：**config 的输入 `shape` 必须与模型（Caffe/ONNX/PyTorch）的实际输入布局（NCHW 或 NHWC）显式对齐**，否则会产生连锁失败。本次 palmDet 模型编译失败即源于此，本文沉淀为可复用规范。

> **核心原则**：输入 `shape` 遵循模型实际布局（工具链按 NCHW 解包）；`layout` 字段仅描述送入 VTA 的输入字节编码（如 NV12/NV21），校准数据始终按 NCHW 处理。二者职责不同，需分清。

---

## 2. 问题背景与故障机制

### 2.1 故障表象

palmDet 模型启用 Adaround 量化（`a8w4`）编译失败，报错：

```
RuntimeError: Sizes of tensors must match except in dimension 1.
Expected size 2 but got size 1 for tensor number 1 in the list
```

发生在 onnx2pytorch 转换模型的校准前向 `torch.cat(dim=1)`（FPN 特征金字塔多尺度拼接）。

### 2.2 根因链路（5-Why）

| 步骤 | 环节 | 结果 |
|------|------|------|
| 1 | config 输入 `shape=[1,224,224,3]`（NHWC） | 与模型 NCHW `[1,3,224,224]` 不一致 |
| 2 | 工具链按 NCHW 解包 `N,C,H,W` | 解析为 `C=224, H=224, W=3` |
| 3 | `_get_model_input_hw` 取 `shape[2], shape[3]` | `input_h=224, input_w=3` |
| 4 | 校准图片 resize 成 `224×3` | onnx2pytorch 前向 W 维度逐层衰减为 1 |
| 5 | relay `from_onnx` 输入通道被覆盖为 224 | 输入通道 ≠ 权重通道 3，编译必然失败 |

> **关键洞察**：表象（onnx2pytorch 前向 shape 错误）易被误判为第三方库缺陷。但先核验"输入数据本身是否合法（尺寸/布局）"更高效——多证据交叉定位（Caffe/ONNX/工具链三方一致指向 NCHW）可迅速锁定 config 为唯一错误源。

---

## 3. 修正方案

### 3.1 输入 `shape` 与模型布局对齐（核心）

将 config 输入 `shape` 改为与模型一致的布局：

```toml
# 修复前（错误）：NHWC，工具链按 NCHW 解包后 W=3
[input]
shape = [1, 224, 224, 3]

# 修复后（正确）：NCHW，与 Caffe/ONNX 模型一致
[input]
shape = [1, 3, 224, 224]
```

### 3.2 `layout` 字段按需保留

`layout` 仅影响送入 VTA 的输入字节编码：

```toml
# NV12/NV21：原始 YUV 字节流送入 VTA
# NCHW/NHWC：直接按张量布局送入
layout = "NV12"
```

> 校准数据（dataset）始终按 NCHW 处理，`layout` 不影响校准前向的正确性；二者可独立配置。

### 3.3 配套修复：onnx2pytorch 算子转换缺陷（独立层）

即使输入尺寸正确，onnx2pytorch 对 ONNX 算子语义的转换仍可能出错，需在 Adaround 导出流程中打猴补丁：

- **`_patch_onnx2pytorch_resize`**：按 ONNX 语义剥离 `scales`/`sizes` 的批/通道维前缀，确保 `scales=[1,1,2,2]` 正确映射为 `scale_factor=(2.0, 2.0)`。
- **`_patch_onnx2pytorch_reshape`**：修复固定 `[1,-1]` reshape 在 batch>1 时的第一维坍缩。

> **根因分层**：config 布局错误（主因）决定"输入非法"；算子转换缺陷（辅因）决定"即使输入正确，Resize/Reshape 仍转换错误"。二者独立，需分别修复。落地位置见 [adaround_onnx_export.py](../../../../external/chaos/npuusertools/xmnn/adaround/adaround_onnx_export.py)。

---

## 4. 新模型接入输入布局核验清单

接入新模型（ONNX/Caffe/PyTorch）编译前，按以下清单核验，**不一致则 fail-fast**，避免进入耗时的 Adaround/编译阶段：

- [ ] **读取模型输入定义**，确认 NCHW 或 NHWC：
  - ONNX：`graph.input` 的 `shape`（如 `images [1,3,224,224]`）
  - Caffe：`input_param` 的 `dim`（如 `dim: 1, 3, 224, 224`）
  - PyTorch：`torch.jit` 的输入 shape 或 forward 输入张量
- [ ] **核对 config `input.shape` 与模型布局一致**（工具链按 NCHW 解包）
- [ ] **核验 `_get_model_input_hw` 提取的 H/W** 与模型实际输入尺寸一致（应为 `shape[2], shape[3]` 且与模型匹配）
- [ ] **核验 `input.format`**（RGB/BGR/GRAY）与模型预处理一致
- [ ] **核验 `input.dtype`** 与模型输入类型一致
- [ ] 有疑问时用 onnxruntime 参考输出做**前向一致性验证**（见 §5）

> **反模式**：
> - ❌ 直接照搬模板 config，不核验输入布局
> - ❌ 把布局问题误判为下游算子/库缺陷
> - ❌ 修改工具链强制解包逻辑来"兼容"错误配置（应改 config，不改工具链）

---

## 5. 验证方法

### 5.1 前向一致性验证（快速门禁）

修复 config 后，用 onnxruntime 参考输出对比 onnx2pytorch 转换模型的空间维度：

| 校验项 | 方法 | 通过标准 |
|--------|------|---------|
| 关键节点 shape | 逐层/关键算子对比 | 与 ORT 参考一致 |
| 输出空间维度 | 对比各分支 H/W | 全部一致（MISMATCH 即 fail） |
| Resize/Reshape 专门断言 | 检查 scale_factor/size 映射 | 空间维放大正确 |

典型通过输出：`ORT=(28,28) PT=(28,28) OK`，特征链路 224→112→56→28→14→7。

### 5.2 完整编译验证

修正后应全流程通过，退出码 0：

```
[1/6] 加载模型 → [2/6] 模型量化 → [3/6] 构建XMNN模型
[4/6] 导出模型文件 → [5/6] 自动调优 → [6/6] 生成静态运行时
COMPILE_EXIT=0
```

---

## 6. 参考与溯源

- 复盘报告：`build-engineering/summary-palmdet-compile-fix-20260812.md`、`insight-palmdet-compile-failure-20260812.md`（`../../retrospective/reports/build-engineering/`）
- 示例配置（已修复）：[config.toml](../../../../external/chaos/models/debug/palmDet/config.toml)
- 工具链实现：[compile_api.py](../../../../external/chaos/npuusertools/xmnn/compile_api.py)、[data.py](../../../../external/chaos/npuusertools/xmnn/data.py)
- 相关最佳实践：[compiled-package-data-file-lifecycle.md](compiled-package-data-file-lifecycle.md)、[dataloader-pickle-diagnosis-sop.md](dataloader-pickle-diagnosis-sop.md)
