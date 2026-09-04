# Ψhē 理论体系 OKF Wiki 教程 - 实施计划

## [x] Task 1: R 阶段 — 事实采集与信源登记
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 从三个网站和本地 AllTheory 资源中提取编号事实清单（F-001 起），写入 `<spec-dir>/facts.md`
  - 事实覆盖：godgpt.fun 全部 5 页面、dw.cash 17 部著作结构、math.dw.cash 9 大系列、universe 三大公理与操作层级
  - 事实必须零推测，不含"用于"/"目的是"等推断词
  - 为每个知识束创建 references/ 信源文件（信源先行）
- **Acceptance Criteria Addressed**: AC-4, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 包含 ≥30 条编号事实，每条可追溯到 URL 或本地文件路径
  - `programmatic` TR-1.2: references/ 目录下为每个知识束创建至少 1 个信源登记文件
  - `human-judgement` TR-1.3: 事实中无因果推断词，纯客观描述
- **Notes**: 网站内容已通过浏览器子代理采集，本地内容已通过 general_purpose_task 采集，需整合为编号事实

## [x] Task 2: I 阶段 — 架构洞察与知识结构设计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单提炼 3-5 个核心洞察（陈述/证据/反常识/行动四元组），写入 `<spec-dir>/insights.md`
  - 设计每个知识束的概念文档清单（文档标题、覆盖的 F-xxx 事实、学习路径顺序）
  - 确定跨知识束的概念关联关系
  - 设计 psi-core/psi-math/psi-universe/godgpt 四个知识束的目录结构
- **Acceptance Criteria Addressed**: AC-2, AC-8
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每条洞察包含完整四元组（陈述/证据/反常识/行动）
  - `human-judgement` TR-2.2: 概念文档清单覆盖 spec.md 中 FR-2 到 FR-5 的所有主题
  - `human-judgement` TR-2.3: 学习路径设计合理（入门→核心→高级）
- **Notes**: 关键洞察包括两大形式体系的同构关系、64 章母题、自指递归作为统一主题

## [x] Task 3: E 阶段 Batch 1 — 创建知识束骨架与根索引
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `bundles/psi/` 目录结构
  - 创建 `bundles/psi/index.md` 分组索引（含 okf_version frontmatter）
  - 为 4 个知识束创建目录和根 index.md、log.md
  - 为每个知识束创建 concepts/index.md、examples/index.md、references/index.md（子目录 index 无 frontmatter）
  - 注意：本批 ≤ 7 文件（实际为骨架文件，后续批次填充内容）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: `bundles/psi/index.md` 存在且含 `okf_version: "0.2"`
  - `programmatic` TR-3.2: 4 个知识束目录均含 index.md 和 log.md
  - `programmatic` TR-3.3: 每个知识束的 concepts/examples/references 子目录均含 index.md 且无 frontmatter
- **Notes**: 骨架文件创建后，后续批次填充概念内容

## [x] Task 4: E 阶段 Batch 2 — 生成 references 信源文件
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 为 psi-core 生成 references：dw.cash 信源、alltheory 本地源码信源
  - 为 psi-math 生成 references：math.dw.cash 信源、theory_psi 核心文档信源
  - 为 psi-universe 生成 references：universe 本地源码信源、三大公理信源
  - 为 godgpt 生成 references：godgpt.fun 网站信源、隐私政策/服务条款信源
  - 每个 references 文件含完整 frontmatter（type: Reference, title, description, sources）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 每个知识束的 references/ 目录下有 ≥2 个信源文件
  - `programmatic` TR-4.2: 每个信源文件含 type: Reference 和有效 URL/路径
  - `programmatic` TR-4.3: 信源文件 frontmatter 字段完整
- **Notes**: 信源先行，必须在概念文档之前完成

## [x] Task 5: E 阶段 Batch 3 — psi-core 概念文档（上）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 生成 psi-core/concepts/ 的前 4 个概念文档：
    1. `00-psi-equation.md` — ψ=ψ(ψ) 核心方程
    2. `01-collapse-dynamics.md` — 塌缩动力学
    3. `02-echo-and-recursion.md` — 回声与递归
    4. `03-observer-formation.md` — 观察者形成
  - 每个文档含完整 frontmatter，sources 指向已存在的 references 文件
  - 每个文档结尾有 `## 相关概念` 章节
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 4 个文件均存在且含 type: Concept frontmatter
  - `programmatic` TR-5.2: sources 字段指向的 references 文件存在
  - `human-judgement` TR-5.3: 内容准确反映 dw.cash/alltheory 中的理论
- **Notes**: 每批 ≤ 7 文件，本批 4 个概念文档

## [x] Task 6: E 阶段 Batch 4 — psi-core 概念文档（下）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 生成 psi-core/concepts/ 的后续概念文档：
    5. `04-language-emergence.md` — 语言涌现
    6. `05-reality-crystallization.md` — 现实结晶
    7. `06-meta-recursion.md` — 元递归
    8. `07-unity-return.md` — 统一回归
  - 生成 psi-core/examples/ 下 1-2 个示例文档（红楼梦 ψ 解读、易经 64 卦映射）
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 4 个概念文件 + 示例文件均含完整 frontmatter
  - `human-judgement` TR-6.2: 概念间交叉链接使用 `/` 开头路径
  - `human-judgement` TR-6.3: 示例文档展示理论的实际应用
- **Notes**: 覆盖 psi-core 8 个核心概念

## [x] Task 7: E 阶段 Batch 5 — psi-math 概念文档
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 生成 psi-math/concepts/ 的概念文档：
    1. `00-theory-psi-core.md` — theory_psi 核心文档（ψ 作为自指塌缩的最小核心）
    2. `01-collapse-set-theory.md` — 坍缩集合论（CST）
    3. `02-riemann-hypothesis.md` — RH 证明结构与方法论
    4. `03-collapse-mathematics.md` — 坍缩数学十大系统
    5. `04-physics-constants.md` — 物理常数的坍缩起源
    6. `05-zfc-collapse.md` — ZFC 坍缩与元数学批判
  - 生成 1 个示例文档（RH 证明的多路径论证概览）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 6 个概念文件含完整 frontmatter
  - `human-judgement` TR-7.2: 数学公式使用 LaTeX 格式
  - `human-judgement` TR-7.3: RH 证明内容准确反映 math.dw.cash 的论证结构
- **Notes**: 数学内容侧重结构和方法论，不复制完整证明

## [x] Task 8: E 阶段 Batch 6 — psi-universe 概念文档
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 生成 psi-universe/concepts/ 的概念文档：
    1. `00-three-axioms.md` — 三大公理（绝对递归/二元一体/信息本体）
    2. `01-flip-xor-shift.md` — FLIP/XOR/SHIFT 基础操作
    3. `02-recursion-meta-operator.md` — REC 递归与元操作符
    4. `03-dimension-spectrum.md` — 维度谱系 D0-D∞
    5. `04-cosmic-ontology.md` — 宇宙本体论（D10 中心理论）
    6. `05-information-field.md` — 信息场与意识理论
  - 生成 1 个示例文档（XOR-SHIFT 推导量子-经典统一）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 6 个概念文件含完整 frontmatter
  - `human-judgement` TR-8.2: 操作层级关系准确（FLIP⊂XOR⊂SHIFT⊂REC⊂M）
  - `human-judgement` TR-8.3: 维度谱系与 universe 源文件一致
- **Notes**: 基于 universe/formal_theory/ 的 778 个文件做分类概览

## [x] Task 9: E 阶段 Batch 7 — godgpt 概念文档
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 生成 godgpt/concepts/ 的概念文档：
    1. `00-divine-intelligence.md` — 神圣智能产品定位
    2. `01-core-features.md` — 核心功能（深度共情/模式识别/灵性智慧）
    3. `02-business-model.md` — 商业模式（订阅制/推广联盟）
    4. `03-privacy-legal.md` — 隐私与法律框架
  - 生成 1 个示例文档（GodGPT 与 ψ 理论的理念关联）
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-9.1: 4 个概念文件含完整 frontmatter
  - `human-judgement` TR-9.2: 产品信息与 godgpt.fun 网站内容一致
- **Notes**: GodGPT 是商业产品，客观记录其功能和定位

## [x] Task 10: E 阶段 Batch 8 — 生成各级 Index 与 Log
- **Priority**: high
- **Depends On**: Task 6, Task 7, Task 8, Task 9
- **Description**:
  - 更新每个知识束的 concepts/index.md（列出所有概念文档）
  - 更新每个知识束的 examples/index.md
  - 更新每个知识束的 references/index.md
  - 更新每个知识束的根 index.md（含知识束概述、文档统计、阅读路径）
  - 创建/更新每个知识束的 log.md（初始版本记录）
  - **最后**更新 `bundles/psi/index.md` 分组索引
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-10.1: 每个 index.md 列出的文档链接均指向存在的文件
  - `programmatic` TR-10.2: 子目录 index.md 不含 frontmatter
  - `human-judgement` TR-10.3: 根 index.md 包含阅读路径建议
- **Notes**: Index 必须最后生成，确保 100% 完整

## [x] Task 11: 更新 bundles 总索引
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 更新 `bundles/index.md`：
    - 在分组导航表中添加 psi 分组行
    - 在生态关系概览图中添加 psi 节点
    - 在分组详情中添加 psi 分组的 4 个知识束条目
    - 更新 total_bundles 和 groups 计数
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-11.1: bundles/index.md 中 psi 分组链接指向 psi/index.md
  - `human-judgement` TR-11.2: 知识束简介准确
- **Notes**: 使用 Edit 工具增量更新，不覆盖已有内容

## [x] Task 12: V 阶段 — 独立验证与修复
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 结构检查：所有 .md 文件含可解析 frontmatter
  - Frontmatter 检查：type 非空，字段完整
  - 链接检查：所有 `/` 开头交叉链接和相对链接有效
  - 源文件验证：关键概念、公式、术语在 sources 指向的原始材料中可找到
  - Index 完整性：index 列出的文件均存在，无遗漏
  - 输出检查报告，逐一修复问题
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-12.1: 无断裂链接（通过脚本或人工遍历验证）
  - `programmatic` TR-12.2: 所有非 index.md 文件含 type 字段
  - `human-judgement` TR-12.3: 抽样 5 个概念文档，关键事实可溯源到 references
  - `human-judgement` TR-12.4: 无虚构的 API、术语或公式
- **Notes**: 委派给独立子代理做黑盒验证

## [x] Task 13: C 阶段 — 模式沉淀与提交
- **Priority**: low
- **Depends On**: Task 12
- **Description**:
  - 回顾本次 OKF Wiki 生成流程的顺利点和问题点
  - 如发现可复用模式，补充到 source-code-to-okf-wiki 的反模式库
  - 记录"多源网站+本地内容"场景的适配经验
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-13.1: 如有新模式，含触发场景、核心步骤、反模式
- **Notes**: C 阶段为知识沉淀，非必须产出新模式
