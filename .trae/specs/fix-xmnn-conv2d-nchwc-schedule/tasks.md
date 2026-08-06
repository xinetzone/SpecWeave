# Tasks

> 本任务计划依据「分层修复验证法」（[layered-repair-verification.md](../../../.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/layered-repair-verification.md)）组织：
> **最终验收标准** = `debug/caffe_demo` 精度流水线跑至 `result.csv` 生成且指标合格（真闭环），或暴露的下一层缺陷已文档化并另立任务（收敛闭环）。**伪闭环**（解析成功即宣告完成）不合格。

- [ ] Task 0: 定义最终验收标准与回放基线
  - [ ] SubTask 0.1: 记录 `debug/caffe_demo` 当前失败现场（`conv2d_NCHWc Invalid Schedule` @ bound.cc:175）与已有证据（`xmnn-failure-models-analysis-report.md` §3.1）
  - [ ] SubTask 0.2: 确认基线镜像 `xmnn:1.2.1-alpha` 中 caffe_demo 的失败行为（用于后续「既有 or 新引入」对抗判定）
  - [ ] SubTask 0.3: 固化"最终验收标准"为可执行命令（重跑精度测试并检查 `result.csv` 生成）

- [ ] Task 1: 根因诊断 conv2d_NCHWc Invalid Schedule（I 洞察 + 第一性原理推导链）
  - [ ] SubTask 1.1: 复现场景确认——定位 `bound.cc:175` 的 `ICHECK(found_attach || stage_attach.size() == 0)` 触发条件，理解 `compute_at` 找不到 producer 的调度语义
  - [ ] SubTask 1.2: 提取 caffe_demo 最小 relay 片段（含 `relu(conv2d)+p2` 自乘结构）产出最小可复现用例，独立触发该错误
  - [ ] SubTask 1.3: 沿调度构造链定位是哪个 pass/步骤创建了无效 `compute_at`，收集 `bound.cc:175` 现场与调用栈证据
  - [ ] SubTask 1.4: 输出根因诊断结论（含"是调度器缺陷还是 relay 图结构触发既有缺陷"的判定）

- [ ] Task 2: 对抗审查修复方案（V 对抗审查，因涉及第一性原理推导必做）
  - [ ] SubTask 2.1: 生成候选方案 A（调度器/降级 pass 修正 bound.cc 相关逻辑）与候选方案 B（relay 图结构转换，拆分自乘结构）
  - [ ] SubTask 2.2: 用魔鬼代言人视角评估两方案：影响面、回归风险、与基线行为一致性、可迁移性
  - [ ] SubTask 2.3: 选定方案并记录论证依据（含被否方案及其否决理由）

- [ ] Task 3: 实施修复（C 原子化变更）
  - [ ] SubTask 3.1: 按选定方案实施代码变更（npu_tvm pass 或 relay 转换）
  - [ ] SubTask 3.2: 用最小复现用例验证：`bound.cc:175` 错误消除，且通过等价性检查（修正未改变正确语义）
  - [ ] SubTask 3.3: 重建 xmnn wheel（`external/chaos/xmtools/docker/dev-llvm22/` 构建流程）

- [ ] Task 4: 重跑完整精度流水线至最终验收标准（分层修复验证法步骤 3-5）
  - [ ] SubTask 4.1: 安装新 wheel，重跑 caffe_demo 完整精度测试
  - [ ] SubTask 4.2: 检查是否推进至 `result.csv` 生成（真闭环）还是暴露新层错误
  - [ ] SubTask 4.3: 若暴露新层错误，做「既有 or 新引入」对抗判定（对比基线、路径独立性）；若在本次范围则修复回 Task 3，若超范围则文档化另立任务
  - [ ] SubTask 4.4: 回归验证——确认修复未破坏其他既有通过模型（抽查已通过模型精度）

- [ ] Task 5: 生成分层修复记录（E 萃取 + 应用模板）
  - [x] SubTask 5.1: 基于 layered-repair-verification 模板，记录 `debug/caffe_demo` 完整分层链（L1 rmsnorm 注册、L2 conv2d_NCHWc 调度）→ 产出 `layered-repair-record.md`（落于收敛闭环）
  - [x] SubTask 5.2: 标注每层错误、根因、处置结论，最终落在「真闭环」或「收敛闭环」→ 已标注收敛闭环
  - [ ] SubTask 5.3: 回填模板的实战案例/成熟度信息（待 P2 修复完成后，若达多案例验证，可将 layered-repair-verification 升级至 L2）

# Task Dependencies
- [Task 1] depends on [Task 0]
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 0],[Task 3]
- [Task 5] depends on [Task 4]
- [Task 0] 与 [Task 1] 可并行启动（基线回放与根因诊断无先后约束）