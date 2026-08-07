---
id: "layered-repair-record-debug-caffe-demo"
source:
  - "external/chaos/xmtools/build/xmnn-failure-models-analysis-report.md#3.1"
  - "external/chaos/npu_tvm/src/te/schedule/bound.cc#175"
template:
  - ".agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/layered-repair-verification.md"
model: "debug/caffe_demo"
frontend: "caffe"
status: "收敛闭环"
tags: ["分层修复记录", "debug/caffe_demo", "rmsnorm", "conv2d_NCHWc", "Invalid Schedule"]
---

# debug/caffe_demo 分层修复记录

> 本记录依据「分层修复验证法」（[layered-repair-verification.md](../../../.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/layered-repair-verification.md)）对 `debug/caffe_demo` 精度失败案例进行分层修复的记录。核心判定原则：**修复是否闭环以最终验收标准（精度 `result.csv` 生成且指标合格）为准，而非以"当前错误消失/解析成功"为准**。

## 1. 案例背景与故障模型

- **模型**：`debug/caffe_demo`（Caffe 前端，`fgvsirfeature_ssd.prototxt` + `fgvsirfeature_ssd.caffemodel`）
- **输入**：`data`，shape `[1,3,120,120]`，BGR/NHWC/uint8
- **编译目标**：`sim_vta2.0`，量化 `a8w8`，非对称激活
- **故障现象**：精度测试无法产出 `result.csv`，在精度解析阶段抛 `ValueError: 未知的算子类型: VTA_TOPI_rmsnorm`

## 2. 最终验收标准（步骤 1）

| 项 | 定义 |
|----|------|
| 最终验收标准 | `debug/caffe_demo` 精度流水线跑至 `temp/debug/caffe_demo/accuracy/result.csv` 生成且指标合格 |
| 已确定为**伪闭环**的验收标准（❌ 不可用） | 以「`parse_network` 成功」宣告完成；以「当前错误消失」宣告完成 |
| 可执行命令 | `python sdk/tools/accuracy.py -n debug.caffe_demo` 后检查 `result.csv` 存在 |

> ⚠️ 若以「解析成功」为闭环，会在 L1 修复后误报完成，掩盖 L2 的调度缺陷。必须以流水线**终点产物** `result.csv` 判定。

## 3. 分层修复链（步骤 2-6）

| 层级 | 暴露错误 | 根因 | 处置 | 状态 |
|------|---------|------|------|------|
| **L1 精度解析** | `ValueError: 未知的算子类型: VTA_TOPI_rmsnorm`（`op_registry.py:41 get_op_class` 未命中） | 精度前端 op_registry 未注册 `VTA_TOPI_rmsnorm` 算子（模型 `Normalize` 层编译后生成该算子） | 在 `op_registration.py` 的 `_SPECIAL_ALIASES` 注册 `VTA_TOPI_rmsnorm -> VTA_TOPI_layernorm`（RMSNorm 与 LayerNorm 参数布局一致），重建 wheel | ✅ 已闭环（解析层） |
| **L2 浮点参考编译** | `conv2d_NCHWc Invalid Schedule`（`npu_tvm/src/te/schedule/bound.cc:175`） | relay 图含 `relu(conv2d)+p2` 自乘结构（`T_multiply = max(conv+p2,0) * max(conv+p2,0)`），LLVM 降级时 `compute_at` 找不到 producer | 判定为**既有缺陷**（路径独立、模型特有、基线同错），文档化另立 P2 任务（见 [tasks.md](tasks.md)） | 🔶 已文档化，另立任务 |

### 3.1 逐层细节

#### L1 层：rmsnorm 算子未注册（已修复）

**现象**
- 精度测试主函数抛 `ValueError: 未知的算子类型: VTA_TOPI_rmsnorm`。
- 堆栈：`accuracy_api.py:205 __post_init__ → network.py:154 parse_network → op_registry.py:41 get_op_class`。

**证据链**
- 模型为 Caffe 前端，网络含 `Normalize` 层（`norm_param`，`fgvsirfeature_ssd.prototxt` 第 172-176 行）。
- 编译产物 `network.xmnn` 中该 `Normalize` 层被编译为 `VTA_TOPI_rmsnorm` 算子。
- 精度前端 `get_op_class("VTA_TOPI_rmsnorm")` 未命中。

**根因**
- 精度前端 op_registry 未注册 `VTA_TOPI_rmsnorm` 的解析逻辑，`parse_network` 无法构建算子节点。为工具链能力缺口，不影响编译与静态推理。

**处置（P1，已完成）**
- 注册别名 `VTA_TOPI_rmsnorm -> VTA_TOPI_layernorm`，重建 wheel（`xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`）。
- 验证：`get_op_class("VTA_TOPI_rmsnorm")` 返回 `VTA_TOPI_layernorm`；`parse_network(network.xmnn)` 成功，识别 7 个算子含 1 个 `VTA_TOPI_rmsnorm`（shape `[1,4,29,29,1,16]`）。

**L1 层结论**：该层错误已消除，但**未宣布闭环**——因为最终验收标准是精度 `result.csv`，解析成功只是进入下一层的门票。

#### L2 层：conv2d_NCHWc Invalid Schedule（已文档化，另立任务）

**现象**
- 精度测试推进至浮点参考模型 TVM 编译阶段（`infer_float` 的 `tvm.relay.backend.vm.compile(mod, target="llvm")`），报 `conv2d_NCHWc Invalid Schedule`。
- 触发点：`npu_tvm/src/te/schedule/bound.cc:175`：

```cpp
ICHECK(found_attach || stage_attach.size() == 0)
    << "Invalid Schedule, cannot find the producer " << stage->op
    << " along the loop nest specified by compute_at of consumer " << op;
```

**根因分析**
- relay 图含 `relu(conv2d)+p2` 自乘结构：`T_multiply = max(conv+p2,0) * max(conv+p2,0)`。
- LLVM 降级时，`T_multiply` 消费者张量的 loop nest 无法包含 `conv2d_NCHWc` producer 的 `oc_block`/`oc_chunk` 轴，`compute_at` 附着失败。

**「既有 or 新引入」对抗判定（步骤 4）**
| 判定依据 | 结论 |
|---------|------|
| 浮点参考构建路径与 rmsnorm 注册路径独立（rmsnorm 只影响 `network.xmnn` 解析，本错误在浮点参考重建） | 与 L1 修复无关 |
| 浮点参考由 `from_frontend` 重新加载 caffe 模型构建，与编译产物无关 | 与编译产物无关 |
| 54 个其他模型无此错，仅 caffe_demo 特有（`relu(conv)*relu(conv)` 自乘结构） | 模型特有 |
| 基线镜像 `xmnn:1.2.1-alpha` 同此 `Invalid Schedule` 失败 | **既有缺陷，非新回归** |

**L2 层处置（步骤 5）**
- L2 缺陷**超出本次 P1 修复范围** → 明确文档化为 P2 缺陷 + 另立修复任务（[tasks.md](tasks.md)），不混入本次修复，避免范围蔓延。
- 修复计划：根因诊断 → 对抗审查修复方案（调度 pass 修正 vs relay 图结构转换）→ 实施 → 重跑精度流水线至 `result.csv` → 更新本记录。

## 4. 检验标准结论（步骤 6 收尾）

| 层次判据 | 判定 |
|---------|------|
| 真闭环（最终验收标准达成，无未处置暴露缺陷） | ❌ 未达成——`result.csv` 尚未生成，L2 缺陷未修复 |
| **收敛闭环**（验收标准未达成，但暴露的下一层缺陷已明确文档化并另立任务，本次修复范围边界清晰） | ✅ **本次结论** |
| 伪闭环（以"解析成功/错误消失"宣告完成） | ❌ 已规避——L1 修复后未宣布闭环，主动推进暴露 L2 缺陷 |

**本次修复边界**：P1（注册 `VTA_TOPI_rmsnorm`）已完整落地并闭环；L2（`conv2d_NCHWc Invalid Schedule`）为既有缺陷，已文档化并另立 P2 修复任务，二者边界清晰，落于**收敛闭环**。

## 5. 遗留与后续

- 后续 P2 修复完成后，本记录需更新为「真闭环」，并将 L2 修复细节（根因、方案、验证）回填至分层链。
- 若 P2 修复达到多案例验证，可依据模板将 `layered-repair-verification.md` 从 L1 升级至 L2（见模板 Changelog）。