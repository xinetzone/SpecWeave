# TVM VM 调度器 Bug 反馈报告

> **Bug 标题**：`relay.backend.vm.compile` 处理「卷积 + 平方ReLU（relu(x)²）」融合图时，`LowerSchedule` 触发 `InternalError: Invalid Schedule, cannot find the producer compute(conv2d_NCHWc...)`
>
> **严重级别**：高（阻塞特定模型量化精度流程；编译与图执行路径不受影响）

---

## 1. 摘要

在 XMNN 工具链精度评估流程中，对 Caffe 前端模型 `fgvsirfeature_ssd`（输入 1×3×32×32，a8w8）执行浮点参考模型编译时，`tvm.relay.backend.vm.compile(mod, target="llvm")` 抛出 `InternalError`。根因是模型含「卷积 → 平方 ReLU（`T_multiply = relu(conv+p2)²`）」模式：卷积经 x86 布局重写为 `conv2d_NCHWc` 后，与消费它的平方 ReLU 被合入同一 fused group，自动调度尝试将卷积 `compute_at` 到消费者循环巢内失败，导致 `InferBound` 崩溃。

该问题与 XMNN 配置（4 种 `fuse_conv`/`fuse_branch_conv` 组合均复现）、运行镜像（`xmnn-whl-builder` / `xmnn-runtime` 行为一致）无关；`tvm.relay.build`（图执行器路径）可正常构建，说明问题集中在 **VM lowering 的调度 attach 逻辑**。

## 2. 环境

| 项 | 值 |
|---|---|
| TVM | **0.19.0**（`tvm.__version__`） |
| npu_tvm 源码 | 分支合并 commit `97865585`（2026-08-10），文件 `src/te/schedule/bound.cc:175` |
| Python | 3.14.6（`/opt/conda/bin/python`） |
| 平台 | x86_64 Linux（Docker 容器，Ubuntu 26.04 base） |
| XMNN | 1.2.1.dev0 |
| 模型 | `fgvsirfeature_ssd`（Caffe 前端，输入 1×3×32×32，a8w8） |
| 调用链 | `tvm.relay.backend.vm.compile(mod, target=tvm.target.Target("llvm"))` |

## 3. 现象与完整错误日志

`accuracy_xmnn` 在浮点参考模型构建阶段失败，`VM_COMPILE_FAIL: InternalError`，而 `GRAPH_BUILD_OK`。完整回溯：

```
tvm.error.InternalError: Traceback (most recent call last):
  [bt] (8) libtvm.so(+0x390148d)
  [bt] (7) libtvm.so(+0x38ff5d2)
  [bt] (6) libtvm.so(tvm::LowerSchedule(...)+0x1c2)
  [bt] (5) libtvm.so(tvm::LowerSchedule(...)+0x5b)
  [bt] (4) libtvm.so(tvm::ScheduleToModule(...)+0x194)
  [bt] (3) libtvm.so(tvm::te::InferBound(tvm::te::Schedule const&)+0xf3c)
  [bt] (2) libtvm.so(tvm::te::InferRootBound(...)+0x27ef)
  [bt] (1) libtvm.so(+0xc2a8ae)
  [bt] (0) libtvm.so(tvm::runtime::Backtrace()+0x29)
  File "npu_tvm/src/te/schedule/bound.cc", line 175
InternalError: Check failed: (found_attach || stage_attach.size() == 0) is false:
Invalid Schedule, cannot find the producer compute(conv2d_NCHWc,
  body=[conv2d_NCHWc.global[n, oc_chunk, oh, ow, oc_block]],
  axis=[T.iter_var(n, T.Range(0, 1), "DataPar", ""),
        T.iter_var(oc_chunk, T.Range(0, 16), "DataPar", ""),
        T.iter_var(oh, T.Range(0, 7), "DataPar", ""),
        T.iter_var(ow, T.Range(0, 7), "DataPar", ""),
        T.iter_var(oc_block, T.Range(0, 4), "DataPar", "")],
  reduce_axis=[], tag=conv2d_NCHWc,
  attrs={"workload": ["conv2d_NCHWc.x86", ... , "NCHW", "NCHW", "float32"]})
along the loop nest specified by compute_at of consumer compute(T_multiply,
  body=[T.max(conv2d_NCHWc[ax0, ax1 // 4, ax2, ax3, ax1 % 4] + p2[ax1, 0, 0], 0)
        * T.max(conv2d_NCHWc[ax0, ax1 // 4, ax2, ax3, ax1 % 4] + p2[ax1, 0, 0], 0)],
  axis=[T.iter_var(ax0, T.Range(0, 1), "DataPar", ""),
        T.iter_var(ax1, T.Range(0, 64), "DataPar", ""),
        T.iter_var(ax2, T.Range(0, 7), "DataPar", ""),
        T.iter_var(ax3, T.Range(0, 7), "DataPar", "")],
  reduce_axis=[], tag=broadcast, attrs={})
```

**关键信息**：
- 生产者：`conv2d_NCHWc`，输出形状 `[1, 16, 7, 7, 4]`（NCHWc 分块，`oc_chunk=16, oc_block=4`）。
- 消费者：`T_multiply`（平方 ReLU），形状 `[1, 64, 7, 7]`（`ax1 // 4` + `ax1 % 4` 访问 NCHWc 布局的展开索引）。
- 失败点：`bound.cc:175`，`InferRootBound` 中 `found_attach` 为 false 且 `stage_attach.size() != 0`。

## 4. 复现步骤

以下步骤在 `xmnn-whl-builder:latest` 或 `xmnn-runtime:latest` 任一镜像下均稳定复现（结果一致）。

```bash
# 1) 启动容器并挂载模型目录
docker run -it --rm \
  -v /mnt/d/spaces/SpecWeave/external/chaos/models:/workspace/models \
  xmnn-whl-builder:latest bash

# 2) 进入模型目录（模型含 config.toml + caffe prototxt/caffemodel + dataset）
cd /workspace/models/debug

# 3) 运行最小复现脚本（from_frontend -> split_model -> vm.compile）
/opt/conda/bin/python /workspace/.temp/diag_caffe_config.py false false
# 预期输出：
#   VM_COMPILE_FAIL: InternalError   <-- 本 Bug
#   GRAPH_BUILD_OK                   <-- 图执行器路径正常，佐证为 VM 调度问题
```

最小复现脚本核心逻辑：

```python
import tvm
from xmnn.compile_api import from_frontend, split_model
from xmnn.config import set_config

config = set_config("caffe_demo", src_model_group_dir="./",
                    temp_dir="caffe_demo/temp/whl", config_path="config.toml")
mod, params = from_frontend(config, "tvm")
run_mod, run_params, _, _, _ = split_model(mod, params, config)

# 触发崩溃（VM 路径）
exe = tvm.relay.backend.vm.compile(run_mod, target=tvm.target.Target("llvm"))

# 对照：图执行器路径（正常）
with tvm.transform.PassContext(opt_level=3):
    lib = tvm.relay.build(run_mod, target="llvm", params=run_params)
```

**复现结论**：
- 在 `fuse_conv`/`fuse_branch_conv` 的 4 种组合（false/false、true/false、false/true、true/true）下均复现 VM 编译失败，图构建均成功 → 与 XMNN 融合配置无关。
- 在 `xmnn-whl-builder` 与 `xmnn-runtime` 两镜像下行为一致 → 与构建工具链有无无关。

## 5. 根因分析（第一性原理）

1. **图模式**：`fgvsirfeature_ssd` 输出前存在「卷积 → 平方 ReLU」模式：`T_multiply = max(conv + bias, 0)²`。该模式在 Relay 中表现为卷积的消费者为「取 max（ReLU）后再自乘」的 `multiply`。
2. **布局重写**：`target="llvm"`（x86）下 `AlterOpLayout` 将 4D 卷积重写为 `conv2d_NCHWc`（`oc_chunk×oc_block` 分块布局），输出为 5D `[n, oc_chunk, oh, ow, oc_block]`。
3. **融合冲突**：`FuseOps` 将 `conv2d_NCHWc` 与消费它的平方 ReLU 合入同一 fused group。自动调度对卷积（生产者）执行 `compute_at`，意图将其嵌套进消费者 `T_multiply` 的循环巢。
4. **调度 attach 失败**：生产者的 NCHWc 分块迭代轴（`oc_chunk`、`oc_block`）无法在消费者的 4D 循环巢（`ax0..ax3`，索引为 `ax1//4`、`ax1%4`）中被定位，`InferRootBound` 中 `found_attach=false` 且 `stage_attach` 非空 → `bound.cc:175` 触发 `InternalError`。
5. **路径差异**：图执行器（`tvm.relay.build`）走图级调度，不经过同一 `InferRootBound` attach 校验，故正常。

## 6. 影响

- **阻塞模型**：`fgvsirfeature_ssd`（`caffe_demo`）无法完成 XMNN 量化精度评估（`accuracy_xmnn` 的浮点参考依赖 `vm.compile`），暂无法为其产出精度基线。
- **波及范围**：仅影响含「卷积后平方 ReLU」模式、且经 x86 `NCHWc` 布局重写的模型；常规卷积模型（如 `palmDet`/ONNX 前端）不受影响，精度流程正常。
- **不涉及**：编译/量化/推理产物生成、图执行器推理、板端部署（`network.xmnn` 已正常生成）。

## 7. 预期 vs 实际

| 场景 | 预期 | 实际 |
|---|---|---|
| `vm.compile` 编译含平方ReLU的卷积图 | 成功生成 VM 可执行模块 | `InternalError: Invalid Schedule...` |
| `tvm.relay.build` 同图 | 成功 | 成功（与预期一致） |

## 8. 建议修复方向（供工具链参考）

1. **`bound.cc` attach 校验**：在 `InferRootBound` 中对「生产者 NCHWc 分块轴无法映射到消费者循环巢」的场景，回退为不执行 `compute_at`（将卷积作为独立 stage 生成）而非直接崩溃，或在 `FuseOps` 阶段避免将 NCHWc 卷积与其元素级消费者合入同一组。
2. **复现定位建议**：最小化 Relay 脚本构造 `conv2d → relu → multiply(relu, relu)` 图，`target="llvm"` 下 `vm.compile` 即可触发；也可直接对 `fgvsirfeature_ssd` 模型复现。
3. **短期规避（若可接受）**：若能在精度路径将目标改为不触发 `AlterOpLayout` 的 target 配置，可规避该调度路径；但当前 `accuracy_xmnn` 硬编码 `target="llvm"`，需工具链侧配合。

## 9. 对抗审查记录（V 自检）

| 视角 | 攻击点 | 结论 |
|---|---|---|
| 魔鬼代言人 | 是否 XMNN 融合配置导致？ | 已排除：4 种 `fuse_conv`/`fuse_branch_conv` 组合均复现；图执行器均正常。 |
| 魔鬼代言人 | 是否镜像/工具链差异导致？ | 已排除：`xmnn-whl-builder` 与 `xmnn-runtime` 行为一致（同因同果）。 |
| 新人视角 | 是否模型本身非法？ | 已排除：图执行器可构建并运行，模型结构合法。 |
| 老板视角 | 影响范围是否夸大？ | 已收窄：仅影响平方ReLU×NCHWc 布局的特定模式，常规模型不受影响。 |
| 未来视角 | 修复方向是否可行？ | 回退 `compute_at` 或调整融合分组为最小改动点，方向合理；具体需工具链在 `npu_tvm` 验证。 |

---

## 附：相关产物路径

- 完整错误日志：`external/chaos/models/debug/caffe_demo/temp/runtime_run.log`、spec 目录 `scripts/diag_caffe.log`
- 复现脚本：`external/chaos/ai/.temp/diag_caffe_config.py`、`run_model.py`
- 触发模型：`external/chaos/models/debug/caffe_demo/`（`fgvsirfeature_ssd`）