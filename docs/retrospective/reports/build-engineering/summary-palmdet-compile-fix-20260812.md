---
id: "summary-palmdet-compile-fix-20260812"
title: "palmDet 模型编译修复与完整编译过程总结"
date: "2026-08-12"
type: "summary"
source: "SpecWeave 会话 sc-20260812-palmdet-compile（修复闭环验证）"
author: "SpecWeave Orchestrator"
tags: ["palmDet", "model-compile", "config-layout", "NCHW", "NHWC", "adaround", "onnx2pytorch", "resize", "quantization"]
supersedes: "insight-palmdet-compile-failure-20260812（根因结论已修正）"
---

# palmDet 模型编译修复与完整编译过程总结

> **报告类型**：修复+编译过程总结报告（Summary Report）
> **生成日期**：2026-08-12
> **状态**：✅ 编译成功，问题已闭环
> **关联文件**：
> - 编译配置（已修复）：[config.toml](../../../../../external/chaos/models/debug/palmDet/config.toml)
> - Adaround 导出实现（含猴补丁）：[adaround_onnx_export.py](../../../../../external/chaos/npuusertools/xmnn/adaround/adaround_onnx_export.py)
> - 编译 CLI 入口：[compile.py](../../../../../external/chaos/npuusertools/tools/compile.py)
> - 编译配置解析：[compile_api.py](../../../../../external/chaos/npuusertools/xmnn/compile_api.py)
> - 输入数据处理：[data.py](../../../../../external/chaos/npuusertools/xmnn/data.py)

---

## 执行摘要

`palmDet` 模型（ONNX 前端）在 XMNN 工具链上启用 Adaround 量化（`a8w4`）编译失败。经多轮深入调查，**最终根因确认为 `config.toml` 输入布局配置与模型不匹配**：模型（Caffe 与 ONNX 一致）输入为 **NCHW** `[1,3,224,224]`，而 config 误写为 **NHWC** `[1,224,224,3]`。工具链按 NCHW 强制解包 shape，导致：
- 校准图片被 resize 成 `224×3`（`_get_model_input_hw` 取 `shape[3]=3` 作 input_w）
- onnx2pytorch 前向 W 维度逐层衰减为 1（第一层 Conv 输出 `(16,8,112,2)`）
- relay `from_onnx` 输入通道被覆盖为 224（应为 3），编译必然失败

**修复**：将 config 输入 `shape` 改为 `[1,3,224,224]`（NCHW），`layout` 按用户要求保留 `NV12`。**修复后前向验证通过**（转换模型输出与 onnxruntime 参考完全一致），**完整编译 6 阶段全部通过，退出码 0**。

> **⚠️ 根因纠偏**：本次调查推翻了早前洞察报告 `insight-palmdet-compile-failure-20260812.md` 的初步结论（当时聚焦 onnx2pytorch Resize 算子缺陷）。Resize/Reshape 猴补丁确为必要辅助修复，但 **W 维度恒为 1 的直接根因是 config 输入布局错误**，二者需区分。

---

## 一、问题背景

### 1.1 编译配置（修复前）

| 配置项 | 修复前值 | 修复后值 | 说明 |
|--------|---------|---------|------|
| frontend | onnx | onnx | 前端框架 |
| model_file_path | palm_det_agatha.onnx | 同左 | 源模型 |
| **input.shape** | **[1, 224, 224, 3]** | **[1, 3, 224, 224]** | **输入 shape（关键修复）** |
| input.layout | NV12 | NV12 | 输入布局（按用户要求保留） |
| input.format | RGB | RGB | 输入格式 |
| input.dtype | uint8 | uint8 | 输入数据类型 |
| compile.target | SIM_VTA2.0 | 同左 | 编译目标 |
| quantized_dtype | a8w4 | 同左 | 激活 8bit / 权重 4bit |
| adaround | enable=true, num_iteration=5000 | 同左 | Adaround 量化 |

### 1.2 模型实际输入布局（关键证据）

三个独立来源一致指向 **NCHW**：

| 来源 | 输入定义 |
|------|---------|
| Caffe prototxt | `dim: 1, 3, 224, 224`（NCHW） |
| ONNX 模型 | `images [1, 3, 224, 224]`（NCHW, float32） |
| 工具链强制解包 | [data.py#L126](../../../../../external/chaos/npuusertools/xmnn/data.py#L126) `N, C, H, W = model_shape` |

---

## 二、故障现象链

### 2.1 表象：onnx2pytorch 前向 shape 错误

- 报错：`RuntimeError: Sizes of tensors must match except in dimension 1. Expected size 2 but got size 1`
- 位置：量化模型前向 `torch.cat(dim=1)`（FPN 特征金字塔多尺度拼接）
- 特征尺寸：第一层 Conv 输出 `(16,8,112,2)`，后续 W 维度逐层衰减为 1

### 2.2 深层根因：config 输入布局与模型不匹配

| 环节 | 错误表现 | 直接原因 |
|------|---------|---------|
| `_get_model_input_hw` | 返回 `(224, 3)` | 从 NHWC `[1,224,224,3]` 取 `shape[3]=3` 作 input_w |
| 校准数据加载 | 图片被 resize 成 `224×3` | input_h/input_w 错误 |
| onnx2pytorch 前向 | W 维度恒为 1 | 输入 `(16,3,224,3)`，第一层 Conv（stride=2, pad=1, k=3）W 3→2→1 |
| relay `from_onnx` | 输入通道 224 ≠ 权重 3 | `shape_dict={images:[1,224,224,3]}` 覆盖 ONNX 输入 |

---

## 三、修复方案

### 3.1 核心修复：config 输入布局纠正

将 [config.toml](../../../../../external/chaos/models/debug/palmDet/config.toml) 输入 shape 由 NHWC `[1,224,224,3]` 改为 NCHW `[1,3,224,224]`，与 Caffe/ONNX 模型一致；layout 保留 `NV12`（仅影响 VTA 输入字节编码，校准数据始终为 NCHW）。

### 3.2 辅助修复：onnx2pytorch 算子猴补丁

在 [adaround_onnx_export.py](../../../../../external/chaos/npuusertools/xmnn/adaround/adaround_onnx_export.py) 中已落地两个猴补丁（`run_adaround` 内调用）：

- **`_patch_onnx2pytorch_resize`**：按 ONNX 语义正确解析 `scales`/`sizes`，剥离批/通道维前缀，确保 `scales=[1,1,2,2]` 正确映射为 `scale_factor=(2.0, 2.0)`。
- **`_patch_onnx2pytorch_reshape`**：修复固定 `[1,-1]` reshape 在 batch>1 时的第一维坍缩问题。

> **说明**：config 布局修复是根治 W 维度问题的关键；猴补丁解决 onnx2pytorch 对 ONNX 算子语义的独立转换缺陷。二者共同保障 Adaround 前向在正确输入尺寸下可正常执行。

### 3.3 环境/脚本修复（排查过程附带）

- Python 3.14+ `forkserver` 多进程要求主模块 `if __name__ == "__main__":` 保护，避免子进程递归导入导致 `ConnectionResetError`。
- `onnx2pytorch` 为可选依赖，需 `pip install onnx2pytorch`（阿里源+超时重试）。

---

## 四、验证结果

### 4.1 前向一致性验证（修复 config 后）

| 输出 | ORT 参考 | onnx2pytorch 转换 | 结果 |
|------|---------|------------------|------|
| out[0] | (28, 28) | (28, 28) | ✅ OK |
| out[1] | (14, 14) | (14, 14) | ✅ OK |
| out[2] | (7, 7) | (7, 7) | ✅ OK |

特征尺寸链路 224→112→56→28→14→7 全部正确，W 维度恒为 1 问题消失。

### 4.2 完整编译验证

```
[1/6] 加载模型 → [2/6] 模型量化 → [3/6] 构建XMNN模型
[4/6] 导出模型文件 → [5/6] 自动调优 → [6/6] 生成静态运行时
[6/6] Fusing quantized weights into ONNX
COMPILE_EXIT=0
```

**编译产物**（`temp/palmDet/compile/`）：
- `palmDet.bin`（VTA 模型二进制）
- `network.xmnn`、`param.bin`（XMNN 网络与参数）
- `vta_config.insn`、`vta_data.bin`、`vta_data_rtos.bin`（VTA 指令/数据）
- `cpp_deploy_static`、`xm_autotools_static`（静态运行时）
- `inputs/images.bin`（输入数据）
- Adaround 量化产物：`palm_det_agatha_adaround.onnx`（38 个 AdaRound 层，62 个融合权重）

---

## 五、经验教训与预防模式

### 5.1 教训：config 与模型布局不一致是隐蔽的编译失败源

工具链强制按 NCHW 解包输入 shape，不因 config 写 NHWC 而自动转置。模型前端（Caffe/ONNX）的输入布局必须与 config 显式对齐，否则产生"校准图片尺寸错误 + relay 输入通道不匹配"的连锁失败。

### 5.2 模式 1：跨框架模型输入布局核验（新模型接入前置检查）

**触发场景**：接入新模型（ONNX/Caffe/PyTorch）编译前，config 输入布局与模型定义不一致。

**核心步骤**：
1. 读取模型输入定义（ONNX `graph.input` / Caffe `input_param`）确认 NCHW 或 NHWC
2. 核对 config `shape` 与模型布局一致（工具链按 NCHW 解包）
3. 核验 `_get_model_input_hw` 提取的 H/W 与模型实际输入尺寸一致
4. 不一致则 fail-fast，避免进入耗时的 Adaround/编译阶段

### 5.3 模式 2：算子转换形状自校验（衔接洞察报告）

跨框架转换（onnx2pytorch）后用 onnxruntime 参考输出做逐层/关键节点 shape 断言，shape 不一致立即暴露，而非传播到下游产生难懂报错。

### 5.4 排查方法论启示

- **根因可能在配置层而非第三方库**：表象（onnx2pytorch 前向 shape 错误）易引导到库缺陷，但先核验"输入数据本身是否合法"（尺寸/布局）更高效。
- **多证据交叉定位**：Caffe/ONNX/工具链三方输入定义一致指向 NCHW，迅速锁定 config 为唯一错误源。

---

## 六、与已有洞察报告的关系与建议

| 报告 | 生成时机 | 根因结论 | 状态 |
|------|---------|---------|------|
| `insight-palmdet-compile-failure-20260812.md` | 修复前 | 聚焦 onnx2pytorch Resize 算子缺陷 + Heisenbug 特性 | ⚠️ 根因结论不完整 |
| `summary-palmdet-compile-fix-20260812.md`（本文） | 修复后 | **config 输入布局错误为根因**，Resize/Reshape 猴补丁为必要辅助 | ✅ 最终结论 |

**建议**：更新 `insight-palmdet-compile-failure-20260812.md`，将根因从"onnx2pytorch Resize 缺陷"补正为"config 输入布局错误为主因、算子转换缺陷为辅因"，以保持归档知识的一致性。

---

## 七、归档信息

- **报告分类**：`build-engineering`（构建工程/模型编译）
- **命名规范**：英文小写、连字符分隔、含日期
- **溯源**：`source` 指向 SpecWeave 会话 `sc-20260812-palmdet-compile`
- **关联洞察**：`insight-palmdet-compile-failure-20260812.md`
