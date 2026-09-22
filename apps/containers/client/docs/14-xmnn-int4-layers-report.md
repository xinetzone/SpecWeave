---
id: "jupyter-podman-client-xmnn-int4-layers-report"
title: "分析报告：network.xmnn int4 层清单（debug.iranti_caffe-a8w4）"
source: "workspace/temp/debug.iranti_caffe-a8w4"
---
# 分析报告：network.xmnn int4 层清单

- 报告日期：2026-09-21
- 分析对象：`../workspace/temp/debug.iranti_caffe-a8w4/compile/network.xmnn`（变体命名含义：激活 8bit / 权重 4bit）
- 模型来源：caffe 前端，编译目标 `SIM_VTA2.0`，量化校准模式 `percentile`
- 证据文件（均位于 `../workspace/temp/debug.iranti_caffe-a8w4/`）：
  - `compile/network_decoded.txt` — 解码后的可读网络文本
  - `compile/network.xmnn` — 原始加密网络
  - `compile/param.bin` — 权重数据
  - `compile/0-compile.log` — 编译日志
  - `compile/autotvm_bandwidth_first.log` — 自动调优日志

> 目录定位：本报告分析的是工作负载栈 `native-dev`（见 [11-native-overlay.md](11-native-overlay.md)）运行时产生的模型调试产物。
> 该产物位于客户端工作区的 `workspace/temp/` 临时区，可被清理；**2026-09-21 核验：该目录已被清理**，
> 原始证据文件已不可复现，如需复算请先重新编译模型并归档产物（步骤见 §六）。

## 一、解码结果概要

| 项目 | 值 |
|------|----|
| 加密版本 | v1（内置兼容算法解密） |
| 输入节点 | 1 个（`data`，shape `[1, 224, 224, 1]`，dtype `uint8`） |
| 参数节点 | 98 个 |
| 算子节点 | 34 个（其中输出节点 1 个，`fc`，shape `[1, 2]`） |
| 带权算子 | 22 个（21 个 `VTA_TOPI_conv2d` + 1 个 `VTA_TOPI_dense`） |
| 无算权子 | 8 个 `VTA_TOPI_eltwise`、1 个 `VTA_TOPI_maxpool2d`、1 个 `VTA_TOPI_adaptive_avgpool2d`、1 个 `VTA_TOPI_preprocess`、1 个 `Output` |

## 二、位宽判定依据

1. `is_int4` 是 conv2d / dense 节点结构的**最后一个字段**，定义见 `xmnn/vta_nodes.py`（conv2d 第 414 行、dense 第 672 行），注释明确 `0 表示 int8 / 1 表示 int4`，语义为**权重位宽**（见 `xmnn/sim_bandwidth.py`：`nbit_weight = 8 if node.is_int4 == 0 else 4`）。
2. 解码文本中算子的 `args` 与结构字段**按序一一对应**：conv2d 共 27 项（末项 `is_int4`），dense 共 12 项（末项 `is_int4`）。本次解析对全部 22 个带权算子做了字段数断言校验，全部精确吻合。
3. 交叉验证：对同源 `../workspace/temp/debug.iranti_caffe-a16w8` 变体（全 int8 权重）做同一解析，22 个算子 `is_int4` 全为 0；且 int8 变体中 conv7–conv21 的权重 shape 首维为 a8w4 的 **2 倍**（如 conv7：`[2,1,3,3,16,16]` vs `[1,1,3,3,16,16]`），与"int4 将两个 4bit 值打包进一个 int8"的物理形态一致；而 conv1–conv6 在两个变体中 shape 完全相同，佐证其本就未启用 int4。

## 三、int4 层清单（共 15 个）

| 序号 | 节点 id | 算子 | 通道 in→out | kernel/stride | 输出分辨率 | 权重位宽 |
|:----:|:-------:|------|:-----------:|:-------------:|:----------:|:--------:|
| 7 | 47 | VTA_TOPI_conv2d | 16→32 | 3×3/s2 | 28×28 | **int4** |
| 8 | 51 | VTA_TOPI_conv2d | 32→32 | 3×3/s1 | 28×28 | **int4** |
| 9 | 55 | VTA_TOPI_conv2d | 16→32 | 1×1/s2 | 28×28 | **int4** |
| 10 | 63 | VTA_TOPI_conv2d | 32→32 | 3×3/s1 | 28×28 | **int4** |
| 11 | 67 | VTA_TOPI_conv2d | 32→32 | 3×3/s1 | 28×28 | **int4** |
| 12 | 75 | VTA_TOPI_conv2d | 32→64 | 3×3/s2 | 14×14 | **int4** |
| 13 | 79 | VTA_TOPI_conv2d | 64→64 | 3×3/s1 | 14×14 | **int4** |
| 14 | 83 | VTA_TOPI_conv2d | 32→64 | 1×1/s2 | 14×14 | **int4** |
| 15 | 91 | VTA_TOPI_conv2d | 64→64 | 3×3/s1 | 14×14 | **int4** |
| 16 | 95 | VTA_TOPI_conv2d | 64→64 | 3×3/s1 | 14×14 | **int4** |
| 17 | 103 | VTA_TOPI_conv2d | 64→128 | 3×3/s2 | 7×7 | **int4** |
| 18 | 107 | VTA_TOPI_conv2d | 128→128 | 3×3/s1 | 7×7 | **int4** |
| 19 | 111 | VTA_TOPI_conv2d | 64→128 | 1×1/s2 | 7×7 | **int4** |
| 20 | 119 | VTA_TOPI_conv2d | 128→128 | 3×3/s1 | 7×7 | **int4** |
| 21 | 123 | VTA_TOPI_conv2d | 128→128 | 3×3/s1 | 7×7 | **int4** |

节点 id 汇总：`47, 51, 55, 63, 67, 75, 79, 83, 91, 95, 103, 107, 111, 119, 123`。

按网络结构划分：**stage2 / stage3 / stage4 的全部残差卷积**（含每级下采样卷积与 1×1 投影），共 5 + 5 + 5 = 15 个。

## 四、int8 层清单（共 7 个，对照）

| 序号 | 节点 id | 算子 | 通道 in→out | kernel/stride | 输出分辨率 | 权重位宽 |
|:----:|:-------:|------|:-----------:|:-------------:|:----------:|:--------:|
| 1 | 9 | VTA_TOPI_conv2d | 16→16 | 7×7/s2 | 112×112 | int8 |
| 2 | 15 | VTA_TOPI_conv2d | 16→16 | 3×3/s1 | 56×56 | int8 |
| 3 | 19 | VTA_TOPI_conv2d | 16→16 | 3×3/s1 | 56×56 | int8 |
| 4 | 23 | VTA_TOPI_conv2d | 16→16 | 1×1/s1 | 56×56 | int8 |
| 5 | 35 | VTA_TOPI_conv2d | 16→16 | 3×3/s1 | 56×56 | int8 |
| 6 | 39 | VTA_TOPI_conv2d | 16→16 | 3×3/s1 | 56×56 | int8 |
| 22 | 133 | VTA_TOPI_dense | 128→16 | 1×1 | 1×1（fc） | int8 |

按网络结构划分：**stem 卷积（conv1）+ 56×56 残差块（conv2–conv6）+ 收尾全连接**。

## 五、规律与结论

1. **int4 启用的分界点恰好是"输出通道 ≥ 32"**：conv1–conv6 的输入/输出通道均为 16，达不到 int4 的 32 通道打包粒度，被强制保持 int8；一旦通道数升到 32（conv7 起），后续卷积全部采用 int4。
2. 位宽划分与分辨率强相关：56×56 及以上分辨率全为 int8，28×28 及以下分辨率全为 int4。原因是该网络在 56×56 阶段通道数固定为 16，分辨率下降与通道扩张（16→32→64→128）同步发生。
3. 激活位宽不受影响：本变体全部算子的输入/输出张量 dtype 均为 `int8`，与目录命名"a8"一致；差异只体现在权重侧（w4 / w8）。

## 六、复现步骤

> 前置：`../workspace/temp/` 下的证据文件已于 2026-09-21 核验**不存在**（临时区被清理），
> 复现需先在 `xmnn-dev` 栈内重新编译该模型并产出 `compile/` 下同名产物。
> 路径均以本目录（`docs/`）为基准。

```bash
# 1) 解码（skill：xmnn-decode）
xmnn-decode ../workspace/temp/debug.iranti_caffe-a8w4/compile/network.xmnn

# 2) 解析各带权算子的 is_int4 字段（脚本见附录 A，先落盘为 list_int4.py）
python list_int4.py \
  ../workspace/temp/debug.iranti_caffe-a8w4/compile/network_decoded.txt
```

## 七、已知限制

- 解码文本中算子名统一为 `VTA_TOPI_conv2d`，**不含原始层名**，因此层间对应关系只能按拓扑序（convN）与节点 id 标定；本报告的 conv 序号按 topo 顺序从 1 编号，与精度分析表中的 `convN@<节点id>` 命名一致。
- 位宽判定依赖 `args` 的位置映射；脚本中的字段列表若与上游 `xmnn/vta_nodes.py` 不同步，断言会立即失败（快速失败，而非静默错读）。
- 证据文件位于客户端工作区 `workspace/temp/` 临时区，且已于 2026-09-21 被清理，本报告的原始数据**当前不可复现**，需按 §六 重新编译模型。

## 附录 A：is_int4 解析脚本

```python
import ast, sys

path = sys.argv[1]
lines = open(path, encoding="utf-8", errors="replace").read().splitlines()

# VTA_TOPI_conv2d 字段顺序（来自 xmnn/vta_nodes.py，共 27 项，末项为 is_int4）
conv_fields = ["src_c","src_h","src_w","kernel_co","kernel_ci","k_h","k_w","dst_c","dst_h","dst_w",
               "in_channels","out_channels","kernel_h","kernel_w","stride_h","stride_w",
               "pad_top","pad_left","pad_bottom","pad_right","pad_value","group","clip_min","clip_max",
               "ms_nums","zero_point","is_int4"]
# VTA_TOPI_dense 字段顺序（共 12 项，末项为 is_int4）
dense_fields = ["batch_size","src_c","k_co","k_ci","dst_c","in_channels","out_channels",
                "clip_min","clip_max","ms_nums","zero_point","is_int4"]

nodes, order = {}, []
for ln in lines:
    if not ln.startswith("id:"):
        continue
    d = dict((t[:t.find(":")], t[t.find(":")+1:]) for t in ln.split(";") if t)
    nodes[int(d["id"])] = d
    order.append(int(d["id"]))

idx = 0
for nid in order:
    d = nodes[nid]
    if not d.get("name", "").startswith(("VTA_TOPI_conv2d", "VTA_TOPI_dense", "VTA_TOPI_batch_matmul")):
        continue
    idx += 1
    args, inputs = ast.literal_eval(d["args"]), ast.literal_eval(d["inputs"])
    w = nodes[inputs[1]]
    fields = conv_fields if "conv2d" in d["name"] else dense_fields
    assert len(args) == len(fields), f"字段数不匹配: id={nid}, args={len(args)}, fields={len(fields)}"
    a = dict(zip(fields, args))
    print(idx, nid, w["name"], w["shape"], (a["in_channels"], a["out_channels"]), a["is_int4"])
```