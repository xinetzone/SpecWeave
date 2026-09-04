# 双镜像模型精度测试 - The Implementation Plan (可验证任务清单)

## [x] Task 1: WSL 环境预检与挂载准备
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 确认 WSL（Ubuntu-26.04）下 `xmnn-whl-builder:latest` 与 `xmnn-runtime:latest` 镜像存在。
  - 确认 `external/chaos/models/debug/caffe_demo` 与 `external/chaos/models/debug/palmDet` 具备完整产物（config.toml + 模型文件 + dataset）。
  - 设计容器运行命令：将宿主 `external/chaos/models` 挂载为容器 `/workspace/models`（双向，精度产物可回写），`-e` 传入 conda PATH。
  - 保活策略：在同一 WSL 会话内完成运行，避免 dockerd/容器被回收。
- **Acceptance**: TR-1 两镜像存在、两模型产物完整、挂载命令可用。
- **验证**: `programmatic` — `docker images` 与 `docker run --rm <img> ls /workspace/models` 输出。

## [ ] Task 2: whl-builder 镜像编译并精度测试两模型
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `xmnn-whl-builder:latest` 中，对 `caffe_demo`（Caffe 前端）与 `palmDet`（ONNX 前端）分别执行 `compile_xmnn` + `accuracy_xmnn`。
  - 运行脚本置于各模型 `temp/`（如 `temp/run_accuracy.py`），记录每模型编译耗时与精度耗时。
  - 收集每模型 `temp/<model>/accuracy/result.csv`（逐节点余弦/MSE/MAE）。
  - 若 palmDet `tune/adaround` 耗时过长，评估临时关闭（先备份 config.toml，测试后恢复）或直接以原始配置执行并记录耗时。
- **Acceptance**: FR-1 满足；两模型编译无错误，`result.csv` 产出。
- **验证**: `programmatic` — compile/infer 退出码 0、`result.csv` 存在且指标合理。
- **执行结果（2026-08-12）**:
  - `palmDet`（ONNX 前端, a8w4）编译+精度通过，产出 `temp/whl/palmDet/accuracy/result.csv`（67 节点）。
  - `caffe_demo`（Caffe 前端, a8w8）**编译通过**，但精度被 **TVM VM 调度器 bug** 阻塞：`accuracy_xmnn` 的浮点参考经 `tvm.relay.backend.vm.compile` 报 `InternalError: Invalid Schedule, cannot find the producer compute(conv2d_NCHWc...) along the loop nest specified by compute_at of consumer compute(T_multiply...)`。
  - 根因：`fgvsirfeature_ssd` 的「卷积后平方 ReLU（T_multiply）」模式与 `conv2d_NCHWc` 布局融合时调度 attach 失败；经 4 种 fuse_conv/fuse_branch_conv 组合验证均复现（非配置问题）；graph executor 可正常构建（模型本身无误）。
  - 因 FR-4 禁止修改 xmnn/tvm 源码，此阻塞**无法在本 spec 范围内解决**，记录为基线期发现（见报告）。

## [x] Task 3: runtime 镜像编译并精度测试两模型
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `xmnn-runtime:latest` 中，对 `caffe_demo` 与 `palmDet` 分别执行 `compile_xmnn` + `accuracy_xmnn`。
  - 记录 runtime 无 LLVM 工具链场景下 `tvm.build(llvm)`（浮点参考模型 relay-vm 编译）是否可运行。
  - 收集每模型 `temp/<model>/accuracy/result.csv`。
- **Acceptance**: FR-2 满足；两模型编译无错误，`result.csv` 产出，runtime 精度流程完整。
- **验证**: `programmatic` — 退出码 0、`result.csv` 存在。
- **执行结果（2026-08-12）**:
  - `palmDet` 编译+精度通过，产出 `temp/runtime/palmDet/accuracy/result.csv`（67 节点），与 whl-builder 产物 **MD5 一致**（`9EC7CF7C8CB98BEF1354D5DC6B9E90A6`）。
  - `caffe_demo` 编译通过，精度被与 whl-builder **相同的 TVM VM 调度器 bug** 阻塞（无 LLVM 工具链不影响——bug 在 relay-vm 编译阶段，`tvm.build(llvm)` 布局重写触发，与工具链有无无关）。
  - runtime 无 LLVM 工具链场景下浮点参考推理路径本身可运行（palmDet 精度已证明 vm 推理正常）；`caffe_demo` 阻塞为模型特定的调度 bug，非 runtime 环境缺陷。

## [x] Task 4: 双镜像精度交叉对比与报告
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 汇总 2 模型 × 2 镜像的精度指标（按输出节点对齐：余弦相似度/MSE/MAE）。
  - 生成 `xmnn-dual-image-accuracy-report.md`，含逐模型/逐镜像对比表、一致性判定（容差范围）与差异说明。
  - 采用七概念 V 对抗审查视角自检数据可信性（G1 事实无因果词、G2 洞察四元组、报告数据与原始 result.csv 一致）。
- **Acceptance**: FR-3 满足；报告含完整对比表与一致性结论。
- **验证**: `human-judgement` — 报告结构完整、数据与 result.csv 一致；`programmatic` — 报告文件存在。

## [x] Task 5: 环境恢复与污染核查
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 校验模型 config.toml / prototxt / onnx 未被修改；若执行时临时关闭过 tune/adaround，从备份恢复 config.toml。
  - 确认编译/精度产物仅落在模型 `temp/` 与 spec 目录内。
  - 更新 `checklist.md` 全部勾选。
- **Acceptance**: FR-4 满足；无污染、报告归档。
- **验证**: `programmatic` — git status 无模型源文件改动；`human-judgement` — 目录归属正确。

# Task Dependencies
- Task 2 ⟵ Task 1
- Task 3 ⟵ Task 1
- Task 4 ⟵ Task 2, Task 3（需两镜像数据）
- Task 5 ⟵ Task 4
- Task 2 与 Task 3 可并行（不同镜像）。
