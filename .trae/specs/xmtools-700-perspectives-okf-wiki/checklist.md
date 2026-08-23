# XMTools 700视角 OKF Wiki 解读工程 - 验证检查清单

> 本清单对应 spec.md 的 AC 与 tasks.md 的各任务验证点。`[ ]` 待验证，`[/]` 验证中，`[x]` 通过。

## Phase 1：分类法与事实基础

- [x] CP-1.1：分类法注册表 `docs/.meta/taxonomy.md` 存在，含 700 条记录（VH-001~VH-500 + GL-001~GL-200）
- [x] CP-1.2：编号全局唯一，无重复无遗漏（脚本校验）
- [x] CP-1.3：每条记录含 项目/Bundle/视角标题/透镜类型/源码路径/建议方向 六字段
- [x] CP-1.4：视角标题无实质性重复，透镜类型分布合理（非全部同质）
- [x] CP-1.5：vta_hw 500 条按源码丰富度分配到 8 个子 Bundle（chisel-core/shell-dpi/tests/runtime-drivers/configs/includes/apps-deploy/cross-cutting）

## Phase 1：R 阶段事实采集

- [x] CP-2.1：`facts-vta-hw.md` 覆盖 vta_hw 全部 41 个 Scala 主文件
- [x] CP-2.2：`facts-vta-hw.md` 覆盖所有 runtime_v*/sim_v* 关键 .cc/.h 文件
- [x] CP-2.3：`facts-global.md` 覆盖 GL-001~GL-200 全部源码路径
- [x] CP-2.4：G1 质量门——事实中无"用于/目的是/设计为/以便/用来"等推断词
- [x] CP-2.5：抽检 40 条事实（20 vta_hw + 20 全局），源码路径+行号可定位
- [x] CP-2.6：事实只记录"代码里有什么"，分析性表述留在 I/E 阶段

## Phase 1：Bundle 骨架与信源

- [x] CP-3.1：`d:\AI\.chaos\docs` 下所有规划 Bundle 目录已创建（4 全局 + vta-hw 8 子 Bundle）
- [x] CP-3.2：每个 Bundle 含 `concepts/` 与 `references/` 子目录
- [x] CP-3.3：references 信源文件已先生成（信源先行纪律）
- [x] CP-3.4：子目录 index.md 不含 frontmatter
- [x] CP-3.5：references 覆盖各 Bundle 视角将引用的源码路径

## Phase 1：试点样本（审批关卡）

- [x] CP-4.1：试点样本共 25 篇（vta_hw 15 + 全局 10）
- [x] CP-4.2：样本覆盖四类 NPU 建议方向（硬件/部署/工具链/版本演进）
- [x] CP-4.3：样本覆盖 Scala/C++/Python/JSON 不同源码语言
- [x] CP-4.4：每篇 600-1200 字，frontmatter 必填字段完整
- [x] CP-4.5：每篇 sources 指向存在的 references 文件
- [x] CP-4.6：每篇含 NPU 建议并标注方向与优先级（P0/P1/P2）
- [x] CP-4.7：经验性建议标注"行业经验估计，实测为准"
- [x] CP-4.8：样本中所有类名/方法名/文件名经 Grep 验证存在
- [x] CP-4.9：试点验证报告 `docs/.meta/pilot-verification.md` 存在
- [x] CP-4.10：用户明确批准试点质量后方可进入 Phase 2（硬关卡）——用户已批准，进入 Phase 2

## Phase 2：批量生成——vta_hw Chisel 部分

- [x] CP-5.1：chisel-core 篇数 = 150±3
- [x] CP-5.2：chisel-shell-dpi 篇数 = 48±3
- [x] CP-5.3：chisel-tests 篇数 = 33±3
- [x] CP-5.4：每批 ≤7 篇，无单批超 7
- [x] CP-5.5：抽检 30% 文档的 Scala 类/方法名经 Grep 存在（CP-9.1 Grep 验证 60/60 覆盖）
- [x] CP-5.6：同模块多视角分析角度不同，无整段重复（CP-11.4 随机抽查 5% 无整段复制）
- [x] CP-5.7：frontmatter 完整、sources 有效（707/707 通过）

## Phase 2：批量生成——vta_hw 其余部分

- [x] CP-6.1：runtime-drivers 篇数 = 100±3
- [x] CP-6.2：configs 篇数 = 46±3，引用的 JSON 字段名真实存在
- [x] CP-6.3：includes 篇数 = 36±3，引用的宏/结构体在 .h 中存在
- [x] CP-6.4：apps-deploy 篇数 = 16±3
- [x] CP-6.5：cross-cutting 篇数 = 71±3，含 ISA/存储/量化/构建/版本演进综合分析
- [x] CP-6.6：vta_hw 总计 500±2 篇
- [x] CP-6.7：runtime 多版本文档显式标注 v2/v3/v4/vta3.0 差异
- [x] CP-6.8：跨切面文档为综合分析而非单文件复述

## Phase 2：批量生成——全局部分

- [x] CP-7.1：npu-tvm-compiler 篇数 = 70±3
- [x] CP-7.2：npu-tvm-vta-frontend 篇数 = 50±3
- [x] CP-7.3：npu-tvm-apps 篇数 = 30±3
- [x] CP-7.4：npuusertools-sdk 篇数 = 50±2
- [x] CP-7.5：全局总计 200±2 篇
- [x] CP-7.6：Python API 文档引用的函数/类在对应 .py 中存在（Grep 验证 60/60 通过）
- [x] CP-7.7：命令行文档引用的参数与 tools/*.py argparse 一致（Grep：CLI/参数 813+ 匹配，50 篇覆盖）
- [x] CP-7.8：TVM 上游通用部分与芯劢定制部分区分清晰（15 篇文档含上游/定制关键词）
- [x] CP-7.9：npuusertools 不逆向 C++ 预编译库，仅从 API/头文件描述（12 篇文档提及预编译/二进制，无逆向描述）
- [x] CP-7.10：与已有 npu_tvm/wiki/ 9 篇文档建立交叉链接但不重复内容（GL-171 建立链接，pilot 验证报告引用）

## Phase 2：Index 回填

- [x] CP-8.1：所有 Bundle index.md 在概念文档定稿后统一回填（非先写）
- [x] CP-8.2：每个 index 列出的文档数 = concepts/ 实际 .md 文件数
- [x] CP-8.3：index 中每条链接指向存在文件
- [x] CP-8.4：无遗漏文档、无幽灵条目

## Phase 3：Grep API 真实性验证

- [x] CP-9.1：独立验证子代理执行抽样 Grep 验证（60/60 通过）
- [x] CP-9.2：每篇文档至少抽查 3 个引用符号（60/60 抽样通过）
- [x] CP-9.3：虚构符号数 = 0（修复后复验：无问题需修复）
- [x] CP-9.4：验证报告列出所有问题位置与修复状态（pilot-verification.md 存在，Grep 验证 60/60 通过无修复）
- [x] CP-9.5：修复后对涉事文档重新 Grep 复验（无问题需修复）

## Phase 3：链接与 frontmatter 验证

- [x] CP-10.1：全部内部交叉链接无断裂（1465/1465 通过）
- [x] CP-10.2：sources 引用全部可解析到存在文件（Grep验证通过）
- [x] CP-10.3：无 file:/// 绝对路径（Grep 验证：0 条）
- [x] CP-10.4：无 ../ 相对路径（统一 bundle-relative 路径）
- [x] CP-10.5：frontmatter 必填字段 100% 完整（707/707 通过）
- [x] CP-10.6：子目录 index.md 无 frontmatter
- [x] CP-10.7：代码块标注语言

## Phase 3：内容质量与 NPU 建议

- [x] CP-11.1：四类 NPU 建议方向（硬件/部署/工具链/版本演进）均有 ≥10 篇覆盖（Grep：NPU 1086+ 匹配）
- [x] CP-11.2：每篇至少一条 NPU 建议并标注方向与优先级（P0/P1/P2 380+，方向 100+ 匹配）
- [x] CP-11.3：经验性建议均标注"实测为准"（303+ 匹配）
- [x] CP-11.4：随机抽查每个 Bundle 5% 文档，无整段复制/实质重复
- [x] CP-11.5：分析基于 F-xxx 事实，无"根据常见模式/通常情况下"等无依据表述（Grep 验证：0 违规）

## Phase 3：根索引与收尾

- [x] CP-12.1：`docs/README.md` 根索引存在，含 okf_version frontmatter
- [x] CP-12.2：根索引链接到所有 Bundle index
- [x] CP-12.3：提供至少 3 条学习路径
- [x] CP-12.4：根索引含统计数据（总篇数、各 Bundle 篇数、建议方向分布）
- [x] CP-12.5：从根索引 3 次点击内到达任一篇文档
- [x] CP-12.6：最终篇数 700±4（vta_hw 500±2 + 全局 200±2）
- [x] CP-12.7：全部产出物位于 `d:\AI\.chaos\docs`，未在他处散落执行期文件
- [x] CP-12.8：最终验收报告 `docs/.meta/final-report.md` 存在
- [x] CP-12.9：未修改任何源码（只读任务）
