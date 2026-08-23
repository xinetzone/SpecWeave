# XMTools 700视角 OKF Wiki 解读工程 - 实施计划

> 方法论：`source-code-to-okf-wiki` 的 R→I→E→V→C 五阶段链路，由 `seven-concepts-cmd` 编排（知识沉淀场景 R→I→E，V 对抗审查加固）。分三阶段推进，Phase 1 试点为硬审批关卡。

## 输出目录结构（目标）

```
d:\AI\.chaos\docs\
├── README.md                              # 根索引（三级导航+学习路径）
├── npu-tvm-compiler/                      # Bundle: TVM编译器核心 (~70篇)
├── npu-tvm-vta-frontend/                  # Bundle: vta Python/topi/tutorials (~50篇)
├── npu-tvm-apps/                          # Bundle: npu_tvm apps部署 (~30篇)
├── npuusertools-sdk/                      # Bundle: XMNN工具链 (~50篇)
└── vta-hw/                                # Bundle组: vta_hw专项 (500篇)
    ├── index.md
    ├── chisel-core/                       # 25核心模块×6视角 (~150篇)
    ├── chisel-shell-dpi/                  # shell/dpi/axi/util (~48篇)
    ├── chisel-tests/                      # 测试文件 (~33篇)
    ├── runtime-drivers/                   # 多版本运行时+平台驱动 (~100篇)
    ├── configs/                           # 23个FPGA配置 (~46篇)
    ├── includes/                          # 多版本头文件 (~36篇)
    ├── apps-deploy/                       # 4个应用示例 (~16篇)
    └── cross-cutting/                     # ISA/存储/量化/构建/演进 (~71篇)
```

---

## Phase 1：分类法 + 事实基础 + 试点样本（审批关卡）

### [x] Task 1: 建立 700 视角分类法注册表
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 遍历两个项目源码树，识别所有可解读的源码单元（文件/模块/配置/跨切面主题）。
  - 设计视角透镜类型：①微架构与数据通路 ②指令/控制流 ③存储层次与带宽 ④时序与流水线 ⑤可配置性与版本差异 ⑥API/接口契约 ⑦构建与集成 ⑧测试与验证 ⑨量化与精度 ⑩部署与运维 ⑪错误处理与健壮性 ⑫NPU优化建议。
  - 为 vta_hw 分配 500 个、全局 200 个视角编号（VH-001~VH-500，GL-001~GL-200）。
  - 输出单一注册表 `d:\AI\.chaos\docs\.meta\taxonomy.md`（表格：编号/项目/Bundle/视角标题/透镜类型/源码路径/建议方向/状态）。
- **Acceptance Criteria Addressed**: AC-1, AC-10
- **Test Requirements**:
  - `programmatic` TR-1.1: 注册表记录数 = 700（VH 500 + GL 200），编号唯一无重复
  - `programmatic` TR-1.2: 每条记录的源码路径字段指向真实存在的文件或标注"跨切面"
  - `human-judgement` TR-1.3: 视角标题无实质性重复，透镜类型分布合理（非全部同质）
- **Notes**: 注册表是后续所有批次的派工单；跨切面主题允许不绑定单一文件

### [x] Task 2: vta_hw R 阶段事实采集
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 通读 vta_hw 全部 Chisel/Scala 主源码（41 文件）、C++ 运行时/驱动（~30 子目录关键文件）、include 头文件、config JSON、apps 源码。
  - 提取编号事实 F-VH-xxx：类名/方法签名/参数/字段/数据流/继承关系/配置项/版本差异，每条指向源码路径+行号。
  - 输出 `d:\AI\.chaos\docs\.meta\facts-vta-hw.md`。
  - G1 质量门：事实中无"用于/目的是/设计为/以便"等推断词。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 事实条目覆盖 vta_hw 全部 41 个 Scala 主文件与所有 runtime_v*/sim_v* 关键 .cc/.h
  - `programmatic` TR-2.2: 抽检 20 条事实，源码路径+行号可定位到对应代码
  - `programmatic` TR-2.3: G1 扫描——事实中无推断性动词（"用于/目的是/设计为/以便/用来"）
- **Notes**: 事实只记录"代码里有什么"，分析留到 I/E 阶段

### [x] Task 3: npu_tvm 全局与 npuusertools R 阶段事实采集
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 通读 npu_tvm 的 vta/python（top/graphpack/autotvm/intrin 等）、关键 src/ 与 python/tvm 定制部分、apps/ 部署示例、已有 wiki/。
  - 通读 npuusertools 的 xmnn/（adaround/cli/tools/tools_cpp 接口）、tools/ 六大命令、tests/、doc/。
  - 提取编号事实 F-GL-xxx，输出 `d:\AI\.chaos\docs\.meta\facts-global.md`。
  - G1 质量门同上。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 事实覆盖 GL-001~GL-200 注册表中所有源码路径
  - `programmatic` TR-3.2: 抽检 20 条事实可定位源码
  - `programmatic` TR-3.3: G1 无推断词
- **Notes**: npuusertools 的 C++ 预编译库（.so/.a）不逆向，仅从头文件/API/Python 绑定提取事实

### [x] Task 4: 搭建 Bundle 骨架与 references 信源登记
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `d:\AI\.chaos\docs` 创建 Task 1 规划的全部 Bundle 目录（含 concepts/references 子目录）。
  - 为每个 Bundle 生成 references/ 信源文件，登记源码路径、关键符号、版本信息（信源先行）。
  - 生成 Bundle 级 `index.md`（仅根 index 保留 frontmatter，子目录 index 无 frontmatter）。
- **Acceptance Criteria Addressed**: AC-4, AC-11
- **Test Requirements**:
  - `programmatic` TR-4.1: 目录结构与 Task 1 注册表一致，所有 Bundle 含 concepts/ 与 references/
  - `programmatic` TR-4.2: references 信源文件覆盖该 Bundle 所有视角引用的源码路径
  - `human-judgement` TR-4.3: 子目录 index.md 不含 frontmatter
- **Notes**: 此时 index 仅占位骨架，内容文档定稿后在 Task 11 统一回填

### [x] Task 5: 生成试点样本（25 篇）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 从 700 视角中选取 25 篇代表性样本：vta_hw 15 篇（覆盖 Chisel 核心/运行时/配置/测试/apps）、全局 10 篇（覆盖 TVM 编译器/vta 前端/apps/npuusertools）。
  - 确保覆盖四类 NPU 建议方向与不同源码语言（Scala/C++/Python/JSON）。
  - 按 OKF 概念文档模板生成（600-1200 字，frontmatter 完整，sources 指向 references）。
  - 每篇含：视角概述、源码事实依据（引用 F-xxx）、分析、NPU 建议（标注方向与优先级）、相关概念。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: 25 篇文件均存在且 frontmatter 字段完整
  - `programmatic` TR-5.2: 每篇 sources 字段指向的 references 文件存在
  - `human-judgement` TR-5.3: 每篇有明确 NPU 建议且标注方向（硬件/部署/工具链/版本演进）与优先级
  - `human-judgement` TR-5.4: 分析基于事实，无虚构 API，篇幅 600-1200 字
- **Notes**: 试点样本是质量基准，经审批后作为后续批量生成的 few-shot 模板

### [x] Task 6: 试点自验证与提交审批（关卡）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 对 25 篇样本执行 V 阶段迷你验证：Grep 验证引用符号存在性、链接检查、frontmatter 检查。
  - 修复发现的问题。
  - 输出试点验证报告 `d:\AI\.chaos\docs\.meta\pilot-verification.md`。
  - **暂停，等待用户审批**。用户批准后方可进入 Phase 2。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 样本中所有类名/方法名/文件名经 Grep 在源码中存在
  - `programmatic` TR-6.2: 内部链接与 sources 无断裂
  - `human-judgement` TR-6.3: 用户明确批准试点质量与风格
- **Notes**: 这是硬关卡；若用户要求调整，回到 Task 1/5 修改后重新报审

---

## Phase 2：批量生成（Phase 1 审批通过后）

### [x] Task 7: 批量生成 vta_hw Chisel 核心与 Shell/DPI/Tests（~231篇）
- **Priority**: high
- **Depends On**: Task 6（审批通过）
- **Description**:
  - 按注册表生成 chisel-core（~150）、chisel-shell-dpi（~48）、chisel-tests（~33）共 ~231 篇。
  - 拆分为每批 ≤7 篇，通过 general_purpose_task 子代理并行委派。
  - 每批 prompt 必须附相关 F-VH 事实编号与试点样本作为格式模板，要求 AI 不确定时回查 facts。
  - 每批完成后立即做迷你 Grep 验证，防止事实遵循度衰减。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-7, AC-8, AC-10
- **Test Requirements**:
  - `programmatic` TR-7.1: chisel-core+shell-dpi+tests 文件数 = 231±3
  - `programmatic` TR-7.2: 每篇 frontmatter 完整、sources 指向存在文件
  - `programmatic` TR-7.3: 抽检 30% 文档的 Scala 类/方法名经 Grep 存在
  - `human-judgement` TR-7.4: 同模块的 6 个视角分析角度不同，无整段重复
- **Notes**: 并行委派时每个子任务独立获得完整格式规范与事实清单，不假设共享上下文

### [x] Task 8: 批量生成 vta_hw 运行时/配置/头文件/apps/跨切面（~269篇）
- **Priority**: high
- **Depends On**: Task 6（审批通过）
- **Description**:
  - 生成 runtime-drivers（~100）、configs（~46）、includes（~36）、apps-deploy（~16）、cross-cutting（~71）共 ~269 篇。
  - 同样每批 ≤7 篇并行委派，附 F-VH 事实与模板。
  - 跨切面主题（ISA/存储/量化/构建/版本演进）需跨文件综合，单独成批。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-7, AC-8, AC-10
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件数 = 269±3，vta_hw 总计 500±2
  - `programmatic` TR-8.2: 配置文档引用的 JSON 字段名在对应 config 文件中存在
  - `programmatic` TR-8.3: 头文件文档引用的宏/结构体在 .h 中存在
  - `human-judgement` TR-8.4: 跨切面文档有综合分析而非单文件复述
- **Notes**: runtime 多版本（v2/v3/v4/vta3.0）文档须显式标注版本差异

### [x] Task 9: 批量生成 npu_tvm 全局（~150篇）
- **Priority**: high
- **Depends On**: Task 6（审批通过）
- **Description**:
  - 生成 npu-tvm-compiler（~70）、npu-tvm-vta-frontend（~50）、npu-tvm-apps（~30）共 ~150 篇。
  - 每批 ≤7 篇并行委派，附 F-GL 事实。
  - 与 npu_tvm/wiki/ 已有 9 篇建立交叉链接但不重复内容。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-7, AC-8, AC-10
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件数 = 150±3
  - `programmatic` TR-9.2: Python API 文档引用的函数/类在对应 .py 中存在
  - `human-judgement` TR-9.3: TVM 上游通用部分与芯劢定制部分区分清晰
- **Notes**: 聚焦定制部分，上游通用机制点到为止

### [x] Task 10: 批量生成 npuusertools（~50篇）
- **Priority**: high
- **Depends On**: Task 6（审批通过）
- **Description**:
  - 生成 npuusertools-sdk Bundle 全部 ~50 篇（xmnn 核心、量化、CLI、六大命令、测试、示例模型）。
  - 每批 ≤7 篇并行委派。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件数 = 50±2，全局总计 200±2
  - `programmatic` TR-10.2: 命令行文档引用的参数与 tools/*.py argparse 一致
  - `programmatic` TR-10.3: AdaRound 量化文档引用的类/函数在 xmnn/adaround/ 中存在
- **Notes**: C++ 预编译库不逆向，仅从 Python API 与头文件描述

### [x] Task 11: 回填各级 index 导航
- **Priority**: high
- **Depends On**: Task 7, Task 8, Task 9, Task 10
- **Description**:
  - 所有概念文档定稿后，统一回填每个 Bundle 的 index.md 文档清单。
  - 确保 index 列出该 Bundle 全部文档，无遗漏、无幽灵条目。
  - **Index 最后写**纪律。
- **Acceptance Criteria Addressed**: AC-4, AC-9
- **Test Requirements**:
  - `programmatic` TR-11.1: 每个 index.md 列出的文档数 = concepts/ 下实际 .md 文件数
  - `programmatic` TR-11.2: index 中每条链接指向存在的文件
- **Notes**: 用脚本生成 index 清单避免人工遗漏

---

## Phase 3：独立验证与收尾

### [x] Task 12: V 阶段——Grep API 真实性全量验证
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 委派独立验证子代理（黑盒，不参与生成），对全部 700 篇文档引用的类名/方法名/文件名/配置项/宏在源码树 Grep 验证。
  - 输出验证报告：虚构符号清单、位置、修复建议。
  - 修复所有虚构项后复验。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-12.1: 虚构符号数 = 0（修复后复验通过）
  - `programmatic` TR-12.2: 验证报告覆盖 100% 文档，每篇至少抽查 3 个符号
  - `human-judgement` TR-12.3: 修复未引入新的事实错误
- **Notes**: 验证子代理与生成子代理必须是不同的独立上下文（黑盒验证）

### [x] Task 13: V 阶段——链接与 frontmatter 全量检查
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 使用 link-check-cmd Skill 检查全部内部交叉链接与 sources 引用。
  - 检查 frontmatter 必填字段完整性与路径风格（`/` 开头，无 `../`）。
  - 检查子目录 index 无 frontmatter。
  - 修复后复验。
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-13.1: 断链数 = 0
  - `programmatic` TR-13.2: 无 file:/// 绝对路径、无 ../ 相对路径
  - `programmatic` TR-13.3: frontmatter 必填字段 100% 完整
- **Notes**: 可与 Task 12 并行（不同验证维度）

### [x] Task 14: 问题修复
- **Priority**: high
- **Depends On**: Task 12, Task 13
- **Description**:
  - 根据 Task 12/13 验证报告，逐篇修复虚构符号、断链、frontmatter 缺失、重复内容。
  - 修复后回归验证。
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-10
- **Test Requirements**:
  - `programmatic` TR-14.1: 所有 P0 问题（虚构/断链）100% 修复
  - `human-judgement` TR-14.2: 重复内容已改写为差异化分析
- **Notes**: 修复单篇文档后重新 Grep 验证该篇

### [x] Task 15: 生成根索引与学习路径
- **Priority**: medium
- **Depends On**: Task 14
- **Description**:
  - 生成 `d:\AI\.chaos\docs\README.md` 根索引：项目总览、Bundle 分类导航、四类 NPU 建议方向索引、学习路径（快速上手/深度理解/硬件设计/部署优化）。
  - 根索引含 okf_version frontmatter 与统计数据（总篇数、各 Bundle 篇数）。
- **Acceptance Criteria Addressed**: AC-9, AC-11
- **Test Requirements**:
  - `programmatic` TR-15.1: 根索引链接到所有 Bundle index，Bundle index 链接到全部概念文档
  - `human-judgement` TR-15.2: 提供至少 3 条学习路径，每条路径点击 ≤3 次到达目标文档
- **Notes**: 根索引是用户入口，须经人工可读性评审

### [x] Task 16: C 阶段——模式沉淀与最终验收
- **Priority**: medium
- **Depends On**: Task 15
- **Description**:
  - 回顾本次大规模 OKF 生成的顺利点与问题点，补充反模式（如批量生成事实遵循度衰减、Windows 路径转义等）。
  - 更新 `source-code-to-okf-wiki` 模式文档的迁移验证记录。
  - 输出最终验收报告 `d:\AI\.chaos\docs\.meta\final-report.md`（篇数统计、验证结果、NPU 建议方向分布）。
- **Acceptance Criteria Addressed**: AC-8, AC-11
- **Test Requirements**:
  - `programmatic` TR-16.1: 最终篇数 700±4（vta_hw 500±2 + 全局 200±2）
  - `programmatic` TR-16.2: 四类 NPU 建议方向均有 ≥10 篇覆盖
  - `human-judgement` TR-16.3: 最终验收报告完整记录质量门通过情况
- **Notes**: 不强制提交 git（私域内容），模式沉淀可追加到项目记忆
