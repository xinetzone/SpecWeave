# openTPU 源码 → OKF Wiki 教程知识包 - 需求规格（PRD）

## Overview

- **Summary**：以 `source-code-to-okf-wiki` 五阶段工作流（阶段0 信源固定 + R→I→E→V→C）系统学习 openTPU 源码（本地审计副本 `external/dao/openTPU`，固定提交 `ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`，2026-10-12）与既有概念页 [00-ai-designed-chip.md](../../../projects/awesome-okf-xs/doc/bundles/jishu/iot/embedded-weekly-03/concepts/00-ai-designed-chip.md)（固定旧基线 `8eaa4806`，2026-10-08，事实 F-001~F-072），在 `projects/awesome-okf-xs/doc/bundles/jishu/iot/opentpu/` 新建一个源码教程型 OKF bundle（17 篇 concepts + 3 篇 examples + 4 份 references + 各级 index/log）。
- **Purpose**：把「AI agent 设计的 AI 推理加速器」从一篇周报概念页，升级为可溯源到每一行源码契约（ISA 编码/位精确数值/MM 累加/VPU/量化/编译器/模拟器/RTL/板卡运行时）的系统中文教程；同时以独立束身份承担「契约对拍」可迁移方法论的源码级实证。
- **Target Users**：希望从一次矩阵乘法出发、沿 Python 内核→编译器→ISA→位精确模拟器→SystemVerilog RTL→FPGA 板卡端到端读懂 AI 加速器的中文技术读者；以及研究「AI agent 做硬件设计」工程方法的实践者。

## Goals

- G1：在 `jishu/iot/opentpu/` 产出符合 OKF v0.2 的完整 bundle（frontmatter、目录三层、toctree、log）。
- G2：全部技术陈述可溯源：事实编号 F-xxx 登记于 `references/facts.md`，每条给出 `ffe997e` blob 中的文件路径与行号区间；关键类名/函数名/指令名/文件名经 Grep 级存在性验证。
- G3：知识主线贯穿六层执行链（ol 内核 → 编译器 → ISA → ISA 模拟器 → RTL → 板卡运行时），以同一算子（MM/一次 matmul）跨层对拍为教学骨架。
- G4：与既有概念页显式对账：对 F-053~F-072 在新基线 `ffe997e` 下「仍成立 / 已扩展 / 已变更」逐条标注（旧基线距新基线 232 个提交，README 结果表已从 7 配置扩至 18 配置、模型从 6/7 个增至 10 个，并新增 STREAM/DSTEP、resident decode、otpu-serve、bcu1525、Nangate45 等内容）。
- G5：诚实的证据边界——本次为静态源码学习：不运行 pytest、不构建 Verilator/位流、不接触 FPGA；所有项目自报性能/板卡数字按「作者报告」口径引用。
- G6：完成三级索引计数面更新（iot 分组、jishu 域、bundles 总索引）并通过束相关门禁。

## Non-Goals

- N1：不逐行讲 `opentpu/llm/` 各模型移植文件（qwen3.py 2804 行、qwen35.py 2231 行、gemma4.py 1784 行等）、`opentpu/serve/`、`opentpu/host/` 全部主机工具与 `tools/litedram/` 校准固件——只在概念级讲结构、入口与契约，给出延伸阅读路径。
- N2：不改写、不重排 `embedded-weekly-03` 束的任何已验证文档；新束对其**单向引用**。
- N3：不把 `external/dao/openTPU` 升级为 vendor/ git submodule（沿用本库 tuya-iot 等源码束先例：references 登记 canonical 远程 + 固定全 hash 的 GitHub URL；本地路径仅出现在 spec 工作底稿中）。
- N4：不执行任何 git commit / push（子模块与主仓均不提交），完成后由用户决定。
- N5：不翻译 `docs/` 英文文档；教程为基于源码事实的原创中文组织。
- N6：不做 RTL 时序/资源数字的第三方复现（PPT、周期数、频率均引用项目文档口径）。

## Background & Context

- 信源现状（2026-10-13 实测）：
  - 本地审计副本 `external/dao/openTPU`：remote `git@github.com:FeSens/openTPU.git`，HEAD = `ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`（2026-10-12 19:10 -0300，docs-only 提交），工作树干净。
  - 仓库有正式 release tag v0.1~v0.5，但 **v0.5 = 730ca28（2026-09-25）落后 HEAD 1499 个提交**，不含本教程引用集合（stream engine、当前 README 结果表、多目标 target 文件等），按「引用集合 ∩ 版本变更集合 = ∅」判据不可选；故固定精确 commit hash（G0 接受的次选），并同时记录 hash + 远程 URL + 日期。
  - 概念页基线 `8eaa4806`（2026-10-08）在本地对象库中，`8eaa4806..ffe997e` 相距 232 个提交，可做差异对账。
- 目标位置依据：openTPU 在本库分类中属 IoT 组（概念页即位于 `jishu/iot/embedded-weekly-03`）；同组已有源码教程型束先例 home-assistant、tuya-iot（concepts/examples/references 三层 + learning-reports 可选层）。
- 规范来源：子项目 `projects/awesome-okf-xs/AGENTS.md`、`.agents/rules/frontmatter.md`（OKF v0.2）；主仓技能 source-code-to-okf-wiki v1.5.0（信源先行、每批 ≤7、index 最后写、Grep 验证、计数断言、toctree 必填、多轮扩展纪律）。
- 概念页已建立的关键知识锚点：六层执行链、三种参照/两类正确性、位精确数值契约（RNE+FTZ、非完整 IEEE 754）、8eaa4806 数值修复反例测试、device/wall 性能口径、Python/RTL/FPGA 分级复现、Lens profiler、6 组板卡 0 ulp 对照。

## Functional Requirements

- **FR-1（束结构）**：创建 `jishu/iot/opentpu/`，含根 `index.md`（带 `okf_version: "0.2"` 与 `type: bundle`）、`log.md`、`concepts/`（00-16 共 17 篇 + index）、`examples/`（3 篇 + index）、`references/`（source-code-map / facts / insights / verification 共 4 份 + index）。
- **FR-2（信源先行）**：E 阶段第一个落盘文件为 `references/source-code-map.md`；所有 concept/example 的 frontmatter `sources` 指向 references 内已存在文件；正文信源链接使用固定到 `ffe997e` 的 GitHub URL，禁止 file:/// 与临时/本地绝对路径。
- **FR-3（内容覆盖）**：17 篇 concepts 覆盖：项目全景与学习路径(00)、机器模型(01)、ISA 编码与控制指令(02)、DMA/显式搬运/WAITW/HALT CHAIN(03)、MXU 与 MM(04)、权重格式 int8/int4/FP4/NVFP4/PAIR(05)、VPU 与 fp32 数值契约(06)、QACT/QST 量化(07)、ol 内核语言(08)、编译器(09)、ISA 模拟器(10)、RTL 架构(11)、分级验证与 validate.py(12)、板卡与主机运行时(13)、性能口径/模型矩阵/MoE offload/serve(14)、多 target 与 ASIC(15)、AI agent 设计硬件的方法与迁移(16)。
- **FR-4（examples）**：3 篇实战——模拟器快速上手源码级走读(00)、跟一次 matmul 穿越六层(01)、validate.py 四行对照输出解读(02)；命令均注明「本次未执行」与前置条件。
- **FR-5（facts 与对账）**：`references/facts.md` 承载 R 阶段全部 F-xxx 事实（按模块分组、含文件:行号）；设专章对概念页 F-053~F-072 做基线对账表（仍成立/扩展/变更/降级，附 ffe997e 证据）。
- **FR-6（洞察与模式）**：`references/insights.md` 给出 3-5 个四元组洞察（陈述/证据/反常识/行动）与知识地图；concept 16 沉淀「契约对拍」「限制隐式行为」「修复配反例」等可迁移方法及适用边界。
- **FR-7（导航与计数）**：束内每个 index.md 含隐藏 `{toctree}` 块且收录本目录全部内容文档；更新 `jishu/iot/index.md`（表格行 + toctree）、`jishu/index.md`（IoT 束计数）、`bundles/index.md`（total_bundles、jishu 束数与描述行）使官方计数门禁三角一致。
- **FR-8（验证产物）**：`references/verification.md` 记录 G4 全项：结构/frontmatter、Grep API 核验结果、计数断言（原始匹配数/去重名数分列与口径）、链接检查、门禁与 dummy 构建输出、遗留问题。

## Non-Functional Requirements

- **NFR-1（零虚构）**：文中出现的每个文件名、类名、函数名、指令助记符、opcode、寄存器/参数名、命令行工具名，必须能在 `ffe997e` blob 中 Grep 命中；V 阶段全量复核并留证据。
- **NFR-2（数量断言）**：凡「X 个/Y 份/Z 处/N 篇」陈述，R 阶段对固定 blob 脚本计数（禁止人工枚举当事实），V 阶段换独立手段复核；每个数字附统计口径，勘误在 facts.md 留痕并三处同步（facts/insights/正文）。
- **NFR-3（风格一致）**：中文正文、kebab-case 英文文件名；二级标题分节；代码块标注语言；每篇结尾含「相关概念」；束内交叉链接一律 `/` 开头 bundle-relative；子目录 index 无 frontmatter；frontmatter 字段风格对齐 embedded-weekly-03（generated/verified/status/stale_after/sources 齐备）。
- **NFR-4（证据边界显式）**：性能/板卡/流片数字标注信源层级（项目报告 / 规格文档 / 本次静态读码），教程不宣称独立复现；`status: draft`、`stale_after: 2027-04-30`（与概念页一致的复核节奏）。
- **NFR-5（教学连贯）**：概念按学习路径编号，跨篇引用同一符号约定；matmul 六层贯穿示例在 00 给出路线图、在 04/08/09/10/11/01-example 中逐层兑现。
- **NFR-6（门禁）**：束相关 toctree 检查零失败；计数门禁对本束三角一致；变更文件 dummy Sphinx 构建 0 error（全量门禁中若非本束归属的红项，过滤说明、不代为修复）。

## Constraints

- **Technical**：产出在 git submodule `projects/awesome-okf-xs` 工作树内（子模块流程：本次只写不提交）；Windows + PowerShell 7 环境；门禁脚本位于子项目 `scripts/`（check-toctrees.py / check-bundles-index.py / check-utf8.py），可经 `invoke gates.*` 或直接 `python scripts/...` 执行；Sphinx dummy 构建需子项目 doc 工程依赖（若环境缺依赖，记录为 blocked 证据而非放行）。
- **Business**：用户指定的两个信源（概念页 + 本地 openTPU 源码）与指定产出根目录；公开内容（Apache-2.0 开源代码 + 公开博文/文档）。
- **Dependencies**：`external/dao/openTPU` 工作树保持 `ffe997e` 检出且不得切换/修改；concept 页与 embedded-weekly-03 references 作为二级事实源。

## Assumptions

- A1：本地克隆在任务期间保持 ffe997e、干净工作树（开工前与落盘前各核一次 hash）。
- A2：`ffe997e` 即为用户意图对应的「当前源码」（用户指定路径时的实际 HEAD）；固定 hash 而非回退到 8eaa4806。
- A3：子项目 Python 环境至少可直接运行 `scripts/check-toctrees.py` 与 `check-bundles-index.py`（纯 stdlib 概率高；invoke/dummy 构建若缺依赖按 blocked 处理）。
- A4：IoT 组主表（源码教程区）是新束的登记位置，不必新建分组。

## Acceptance Criteria

### AC-1：束结构与 OKF frontmatter 合规（rule）

- **Given**：`jishu/iot/opentpu/` 落盘完成
- **When**：运行 toctree 门禁（`python scripts/check-toctrees.py`，cwd=子项目根）并人工核对 frontmatter
- **Then**：rc=0 且本束零命中失败项；每个非保留 .md 有可解析 YAML 与非空 type；仅根 index.md 含 okf_version；子目录 index 无 frontmatter；log.md 存在
- **Pass Condition**：门禁输出中本束相关项 0 失败 + 逐文件检查清单全部勾选
- **Evidence**：门禁 stdout（粘贴进 verification.md）、文件清单（Glob 输出）

### AC-2：零虚构 API/符号（rule）

- **Given**：全部 concept/example 正文
- **When**：V 阶段把每篇出现的文件名、类/函数名、指令助记符与 opcode、CLI 名整理为符号清单，并在 `ffe997e` blob 中逐一 Grep
- **Then**：每个符号有命中路径:行号；任何无命中项必须删除或改写为有证据表述
- **Pass Condition**：符号核验表零「未命中」（或全部未命中项已修复并复验）
- **Evidence**：verification.md 符号核验表（抽样全量 + Grep 命令/命中数）

### AC-3：数量断言经脚本双重计数（rule）

- **Given**：facts.md 与正文中全部数量陈述（如指令数、VOP 功能码数、测试文件数、RTL 文件数、模型数、性能表行数、target 数等）
- **When**：R 阶段脚本计数结果与 V 阶段独立复核结果比对
- **Then**：两口径一致或差异已解释（原始匹配数 vs 去重名数分列）；每个数字带口径注记
- **Pass Condition**：计数对账表无数值冲突；人工枚举零采信
- **Evidence**：facts.md 计数记录（含命令）、verification.md 对账表

### AC-4：信源固定与路径纪律（rule）

- **Given**：references/source-code-map.md 与全部发布文档
- **When**：检查信源登记内容与文档中的链接
- **Then**：source-code-map 记录 remote URL、`ffe997e9a8b8607b07b3d1bb3c1132db0faf044e` 全 hash、提交日期、与 v0.5(730ca28)/8eaa4806 的关系；发布文档无 file:///、无 `external/dao`、无 .tmp/.chaos 路径；外部源码链接为固定 hash 的 GitHub URL
- **Pass Condition**：`grep -R "file:///"` 与本地路径扫描在束内 0 命中；信源字段四要素齐全
- **Evidence**：verification.md 路径扫描结果 + source-code-map 内容

### AC-5：链接完整可达（rule）

- **Given**：束内全部 Markdown 链接
- **When**：检查束内 `/`-开头链接与相对链接、跨束链接（指 embedded-weekly-03）
- **Then**：全部目标存在；toctree 条目 stem 与文件一一对应
- **Pass Condition**：断链检查 0 失败（本束范围）
- **Evidence**：链接检查输出（check-links 或等价脚本/手工清单）

### AC-6：与概念页基线对账完整（rule）

- **Given**：概念页 F-053~F-072（20 条）与 ffe997e 现状
- **When**：逐条核对新源码下事实状态
- **Then**：facts.md 对账表给出每条「仍成立/扩展/变更/无法静态确认」裁决与新证据定位；已变更项（如性能表扩为 18 配置、模型增至 10 个、新增 STREAM 指令/otpu-serve/bcu1525 等）在正文以 ffe997e 为准并显式说明演进
- **Pass Condition**：20 条全部有裁决，无遗漏条
- **Evidence**：facts.md 对账章节（20 行齐）

### AC-7：教程质量与六层贯穿（rubric）

- **Type**：`rubric`
- **Dimension**：教学有效性
- **Scale**：1-5
- **Anchors**：1 = 概念堆砌、跨层无关联、读者无法形成端到端路径；3 = 分层清楚但同一算子跨层对拍只覆盖部分层、证据边界偶有模糊；5 = 学习路径平滑、matmul 六层贯穿完整兑现、每章证据/边界/延伸阅读清晰、读者可按图完成静态走读
- **Pass Threshold**：>= 4
- **Evidence**：独立 Review 按维度评分并引用具体篇章证据

### AC-8：洞察与可迁移方法质量（rubric）

- **Type**：`rubric`
- **Dimension**：知识沉淀深度
- **Scale**：1-5
- **Anchors**：1 = 只有事实复述；3 = 有洞察但四元组不完整或迁移建议空泛；5 = 3-5 个四元组洞察证据扎实，「契约对拍/限制隐式行为/修复配反例/agent 产物与归属分离」方法含触发条件、步骤、反模式与不适用边界
- **Pass Threshold**：>= 4
- **Evidence**：insights.md + concept 16，独立 Review 评分

## Open Questions

- [ ] Q1：R/I 阶段的工作底稿（facts.md 的工作版、洞察草稿）放在 `.trae/specs/opentpu-okf-wiki/` 下随 spec 留存，定稿后再「发布」入束 references/——默认按此执行（spec 底稿可引用本地审计路径，发布版只保留固定 hash URL）。
- [ ] Q2：若子项目环境无法运行 dummy Sphinx 构建（缺 sphinx/myst），AC-1 的构建证据是否接受「门禁脚本 + 人工 frontmatter 核对」降级？默认：记 blocked 并尝试 `python -m sphinx` 一次取证，不静默降级。
