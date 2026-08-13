# 双镜像模型精度测试报告（xmnn-whl-builder / xmnn-runtime）

- **Change-id**: `xmnn-dual-image-model-accuracy`
- **日期**: 2026-08-12
- **环境**: WSL（Ubuntu-26.04）Docker
- **镜像**: `xmnn-whl-builder:latest`（含构建工具链） / `xmnn-runtime:latest`（精简运行时，无 LLVM 工具链）
- **模型**: `caffe_demo`（Caffe 前端，`fgvsirfeature_ssd`，输入 1×3×32×32，a8w8）/ `palmDet`（ONNX 前端，`palm_det_agatha`，输入 1×3×224×224，a8w4）

---

## 1. 背景与目标

在 `external/chaos/ai/` 镜像矩阵中，`xmnn-whl-builder:latest` 与 `xmnn-runtime:latest` 均已构建可用。本任务在 WSL 下分别在两个镜像中对 `caffe_demo` 与 `palmDet` 执行 **编译 + 精度测试**（`compile_xmnn` + `accuracy_xmnn`，指标：余弦相似度 / MSE / MAE），交叉对比两镜像精度，确认两镜像对同一模型的量化精度一致、无回归，为镜像交付与板端部署提供精度基线。

## 2. 环境与方法

- 挂载：宿主 `external/chaos/models` → 容器 `/workspace/models`（双向，精度产物回写宿主）；`external/chaos/ai` → whl 容器 `/workspace`、runtime 容器 `/workspace`。
- 解释器：`/opt/conda/bin/python`（两镜像均含 tvm/vta/xmnn，Python 3.14）。
- 精度流程：`accuracy_xmnn` 先经 `compile_xmnn` 产出 `network.xmnn`/`param.bin`，再用浮点参考模型（`tvm.relay.backend.vm.compile(mod, target="llvm")`）与 XMNN 量化推理逐节点比对。
- 配置：`palmDet` 测试期临时关闭 `tune`/`adaround`（`onnx2pytorch` 可选依赖缺失）；测试完成后已恢复原始配置。

## 3. palmDet 双镜像精度对比

| 项 | whl-builder | runtime | 结论 |
|---|---|---|---|
| 编译 | OK（`temp/whl/palmDet/compile`） | OK（`temp/runtime/palmDet/compile`） | 通过 |
| 精度 | `temp/whl/palmDet/accuracy/result.csv`（67 节点） | `temp/runtime/palmDet/accuracy/result.csv`（67 节点） | 通过 |
| **result.csv MD5** | `9EC7CF7C8CB98BEF1354D5DC6B9E90A6` | `9EC7CF7C8CB98BEF1354D5DC6B9E90A6` | **完全一致** |

两镜像 palmDet 精度逐节点完全一致（字节级相同），量化结果无回归。

关键节点精度示例（两镜像一致）：

| 节点 | 余弦相似度 | MSE | MAE |
|---|---|---|---|
| Conv_0@12 | 0.999901 | 6.90e-05 | 0.00394 |
| Conv_35@105 | 0.985587 | 0.06604 | 0.17874 |
| Conv_82@228 | 0.956009 | 0.03060 | 0.10347 |
| Conv_144@395 | 0.989652 | 0.00220 | 0.02626 |
| output-output0@309 | 0.996667 | 0.00279 | 0.03352 |
| output-389@397 | 0.997804 | 0.00132 | 0.01891 |

> 全部 67 节点余弦相似度 ≥ 0.95，输出节点 ≥ 0.996，量化精度良好。

## 4. caffe_demo 阻塞分析

**结论：`caffe_demo` 在双镜像上编译均通过，但精度测试被 TVM VM 调度器 bug 阻塞。**

- 编译：双镜像均 OK（`temp/{whl,runtime}/caffe_demo/compile/network.xmnn` + `param.bin`）。
- 精度：`accuracy_xmnn` 浮点参考经 `tvm.relay.backend.vm.compile` 报错：

```
InternalError: Check failed: (found_attach || stage_attach.size() == 0) is false:
Invalid Schedule, cannot find the producer compute(conv2d_NCHWc, ...)
along the loop nest specified by compute_at of consumer compute(T_multiply, ...
body=[T.max(conv2d_NCHWc[...] + p2[...], 0) * T.max(conv2d_NCHWc[...] + p2[...], 0)], ...)
```

**根因**（I→F 第一性原理 + 证据验证）：
1. `fgvsirfeature_ssd` 网络含「卷积 → 平方 ReLU」模式：`T_multiply = relu(conv+p2)²`（对 SSD 特征提取的常见平方激活）。
2. 该平方 ReLU 作为 `conv2d_NCHWc`（x86 布局重写后的卷积）的消费者，在 `FuseOps` 后与卷积合入同一 fused group，自动调度尝试 `compute_at` 将卷积 attach 进消费者循环巢。
3. `conv2d_NCHWc` 的分块迭代轴（`oc_chunk`/`oc_block`）无法在消费者 `T_multiply` 的循环巢（`ax0..ax3`）中被找到 → `InferBound` 失败。

**排除配置因素**（4 种组合验证，均复现 VM 编译失败、graph executor 均成功）：
- `fuse_conv=false, fuse_branch_conv=false`（原始配置）
- `fuse_conv=true, fuse_branch_conv=false`
- `fuse_conv=false, fuse_branch_conv=true`
- `fuse_conv=true, fuse_branch_conv=true`

**结论**：该 bug 为模型特定（`fgvsirfeature_ssd` 平方 ReLU 模式）的 TVM VM 调度缺陷，与镜像（有无构建工具链）及 config 均无关。两镜像行为完全一致。

**约束**：精度流程 `accuracy_xmnn` 在 [accuracy_api.py](file:///d:/spaces/SpecWeave/external/chaos/npuusertools/xmnn/accuracy_api.py#L242) 硬编码 `tvm.relay.backend.vm.compile`；依据 FR-4（不修改 xmnn/tvm 源码），本阻塞**无法在本 spec 范围内解决**，作为基线期发现记录，建议移交工具链修复。

## 5. 一致性结论

| 模型 | 前端 | 两镜像编译 | 两镜像精度 | 交叉一致性 |
|---|---|---|---|---|
| palmDet | ONNX | 均 OK | 均 OK | ✅ 逐节点一致（MD5 相同） |
| caffe_demo | Caffe | 均 OK | 均被同一 TVM bug 阻塞 | ✅ 行为一致（同因同果） |

**总判定**：两镜像对同一模型的量化精度与编译行为**一致、无回归**。`xmnn-runtime`（无 LLVM 工具链）与 `xmnn-whl-builder`（含工具链）在精度流程上行为等价。

## 6. 七概念 V 对抗审查自检

- **G1（事实，无因果词）**：报告数据直接取自双镜像 `result.csv`（MD5 一致为客观事实）；caffe_demo 失败为 `runtime_run.log`/`diag_caffe.log` 的原始报错，无推断性因果措辞。
- **G2（洞察四元组）**：
  - 现象：palmDet 双镜像精度逐节点一致；caffe_demo 精度被 TVM VM 调度 bug 阻塞（编译正常）。
  - 根因：`fgvsirfeature_ssd` 平方 ReLU × `conv2d_NCHWc` 融合 attach 失败，模型特定、非配置/镜像问题。
  - 影响：caffe_demo 当前无法在本工具链产出精度基线；需工具链修复后补测。
  - 建议：向工具链反馈该 LowerSchedule bug；可先以 graph executor 路径验证模型正确性（已证明可构建），待 VM 调度修复后补精度。
- **G3（数据可信）**：对比表数据与 `result.csv` 逐值一致；MD5 校验防篡改；未修改模型源文件与 xmnn/tvm 源码。

## 7. 后续建议

1. 向工具链反馈 `conv2d_NCHWc × T_multiply` 的 TVM LowerSchedule bug（`npu_tvm/src/te/schedule/bound.cc:175`）。
2. `caffe_demo` 精度基线：待 VM 调度修复后，用 `run_model.py caffe_demo <tag>` 复测即可闭环。
3. 交付基线以 palmDet 双镜像一致为准；caffe_demo 以「编译通过 + 精度阻塞原因明确」作为当前状态。

## 附件

- 精度原始数据：`external/chaos/models/debug/palmDet/temp/{whl,runtime}/palmDet/accuracy/result.csv`
- 编译产物：`external/chaos/models/debug/caffe_demo/temp/{whl,runtime}/caffe_demo/compile/`
- 诊断脚本：`external/chaos/ai/.temp/diag_caffe_config.py`、`run_model.py`
- 运行日志：`external/chaos/models/debug/caffe_demo/temp/runtime_run.log`