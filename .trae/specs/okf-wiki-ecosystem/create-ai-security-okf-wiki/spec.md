---
status: "draft"
spec: create-ai-security-okf-wiki
created: 2026-09-02
methodology: seven-concepts-cmd（场景4 知识沉淀，链路 R→I→E→V→C，depth=deep）
sensitivity: public（三仓库均为 GitHub 公开开源内容 → 标准工作流）
---

# AI 安全与红队研究 OKF Wiki（elder-plinius 三仓库）Spec

## Why

`external/dao/action/elder-plinius/` 下有三个公开开源仓库尚未沉淀为知识包：**CL4R1T4S**（20+ 主流 AI 厂商提取系统提示词档案）、**L1B3RT4S**（40+ 厂商越狱提示词研究库，本地工作树已删但 git HEAD 完整）、**OBLITERATUS**（最先进的开源 abliteration 拒绝行为消除研究工具包）。三者共同构成一条完整的"AI 安全对抗研究"知识线（系统提示词透明度 → 攻击面分类学 → 权重级对齐干预研究），但 `projects/awesome-okf-xs/doc/bundles` 中尚无对应知识包，需系统性调研整理后以 OKF v0.2 教程形式沉淀。

## What Changes

- 新增分组 `doc/bundles/jishu/ai/ai-security/`（🛡️ AI 安全与红队研究，3 束 1 组），含分组导航 `index.md`
- 新增束 `cl4r1t4s/`：系统提示词透明档案——仓库定位与透明性主张、厂商档案全景、系统提示词解剖学（角色/工具/护栏共性结构）、防御性提示工程教训、伦理框架
- 新增束 `l1b3rt4s/`：越狱提示词研究库——攻击面研究定位、攻击技术分类学（概念级学术转述）、防御视角反哺、负责任披露边界
- 新增束 `obliteratus/`：拒绝行为消除研究工具包——abliteration 原理、六阶段流水线、7 方法预设与双干预范式、15 分析模块与 informed 闭环、新技术谱系、扩展部署、研究生态
- 索引注册与计数对账（4 处）：`jishu/ai/index.md`、`jishu/index.md`、`bundles/index.md`（frontmatter/学科概览 mermaid/技术域节标题/分组表）计数由现状 +3 束 +1 组
- 全部新文档遵循 OKF v0.2 frontmatter 规范（`type` 必填、`sources` 溯源、中文正文、kebab-case 文件名）
- **内容边界（硬约束）**：研究性中性转述——不逐字复制可操作的越狱载荷与完整系统提示词正文；以结构特征、学术命名、脱敏示意片段说明；保留上游伦理声明与负责任使用章节

## Impact

- Affected specs: 无既有 spec 受影响（纯新增束）
- Affected code: 
  - `projects/awesome-okf-xs/doc/bundles/jishu/ai/ai-security/**`（新增 ~30 个 md）
  - `projects/awesome-okf-xs/doc/bundles/jishu/ai/index.md`（分组导航表 + toctree）
  - `projects/awesome-okf-xs/doc/bundles/jishu/index.md`（ai 行束数 121→124、关键词、正文"14 个分组"→15）
  - `projects/awesome-okf-xs/doc/bundles/index.md`（frontmatter total_bundles 398→401 / groups 46→47、mermaid jishu 节点计数、技术域节标题 301 束·14 组→304 束·15 组、ai 行）
- 质量门：新增束后必跑 `invoke gates.bundles` + `invoke gates.toctrees` + `invoke gates.utf8` + `invoke build`
- 子模块协作纪律：awesome-okf-xs 为共享子模块，`git add` 与 `git commit` 分离执行并核验暂存 blob（防并行会话竞态）

## 知识源清单（信源）

| 信源 | 本地路径 | 状态 | 读取方式 |
|---|---|---|---|
| CL4R1T4S | `external/dao/action/elder-plinius/CL4R1T4S/` | 工作树完整（20+ 厂商目录） | 直接 Read |
| L1B3RT4S | `external/dao/action/elder-plinius/L1B3RT4S/` | **工作树文件全部标记删除（D）**，git HEAD（64960b7）完整含 ~40 个 .mkd | 仅经 `git show HEAD:<file>` / `git cat-file` 读取；**禁止 restore 恢复工作树** |
| OBLITERATUS | `external/dao/action/elder-plinius/OBLITERATUS/` | 工作树完整（Python 项目 + README/AGENTS/CLAUDE） | 直接 Read |

## ADDED Requirements

### Requirement: 方法论编排（R→I→E→V→C 深度链路）
任务 SHALL 按 seven-concepts-cmd 场景 4（知识沉淀）的链路执行：R 事实采集（三仓库独立采集、F 编号登记、L1B3RT4S 经 git 对象读取）→ I 跨仓库洞察（含四元组）→ E 生成 OKF 束（信源先行、逐文档溯源）→ V 对抗审查（事实核对 + YAML 解析扫描 + 伦理边界检查，depth=deep 多视角）→ C 质量门与原子提交。每阶段产出物必须通过对应质量门（G1 事实无因果词 / G2 洞察四元组 / G3 可迁移 / V 实质审查）方可推进。

#### Scenario: R 阶段事实采集
- **WHEN** 子代理按仓库采集事实
- **THEN** 产出 `facts-cl4r1t4s.md`、`facts-l1b3rt4s.md`、`facts-obliteratus.md` 于本 spec 目录，每条事实带 F 编号与可追溯来源（文件路径 / git 对象 / 行号），无因果推断词，L1B3RT4S 事实全部注明经 `git show HEAD:` 读取

#### Scenario: I 阶段跨仓库洞察
- **WHEN** 基于事实清单提炼洞察
- **THEN** 产出 `insights.md`，≥3 条洞察且每条含"陈述+证据（引用 F 编号）+反常识+行动"四元组，覆盖三仓库共性（如：透明度档案与攻击库一体两面、权重级干预是提示级对齐的降维验证）

### Requirement: 新增 ai-security 分组与三束
bundles 库 SHALL 在 `doc/bundles/jishu/ai/` 下新增 `ai-security` 分组（type: group，含 toctree 引用三束），并按下列结构生成三束（每束根 `index.md` 携带 `okf_version: "0.2"`、concepts/examples/references 三层、toctree 全量引用）：

| 束 | 目录 | 内容范围（详实目标） |
|---|---|---|
| CL4R1T4S | `jishu/ai/ai-security/cl4r1t4s/` | 5 concepts + 1 example + 1 references + index |
| L1B3RT4S | `jishu/ai/ai-security/l1b3rt4s/` | 4 concepts + 1 example + 1 references + index |
| OBLITERATUS | `jishu/ai/ai-security/obliteratus/` | 7 concepts + 2 examples + 1 references + index |

每篇 concepts 文档 SHALL 内容详实（目标 4000+ 字符/篇，含对比表、流程图（Mermaid）、代码示例）、真实可靠（关键论断可溯源至 facts 文件 F 编号或源文件路径；API/命令/参数经源码 Grep 核验）。

#### Scenario: 生成 OBLITERATUS 束
- **WHEN** 生成 `obliteratus/` 束
- **THEN** 覆盖 abliteration 原理（refusal direction/diff-in-means/SVD/白化）、六阶段流水线（SUMMON→PROBE→DISTILL→EXCISE→VERIFY→REBIRTH）、7 方法预设表、双干预范式（权重投影 vs steering vectors）、15 分析模块与 informed 闭环、2025-2026 新技术（EGA/CoT-aware/COSMIC/RDO/KL 共优化等）、多 GPU/量化/远程部署、社区遥测研究生态；CLI 命令与 Python API 均经源码核对

#### Scenario: 生成 CL4R1T4S 束
- **WHEN** 生成 `cl4r1t4s/` 束
- **THEN** 覆盖仓库定位（"shadow-puppet"透明性主张与贡献规范）、20+ 厂商档案全景（目录结构/版本标注/日期）、系统提示词解剖学（persona/工具 schema/安全护栏/输出格式/防注入指令共性结构）、防御性提示工程教训、伦理框架；示例文档做跨厂商护栏结构对比（结构层面，不复制全文）

#### Scenario: 生成 L1B3RT4S 束
- **WHEN** 生成 `l1b3rt4s/` 束
- **THEN** 覆盖攻击面研究定位、攻击技术分类学（概念级学术命名：编码混淆/token 走私/角色框架/多轮递进等，参照 JailbreakBench/HarmBench 学术谱系）、防御视角反哺（分类学如何用于护栏设计与红队评估基准）、负责任披露与法律边界；**不包含任何可操作的完整攻击载荷正文**

### Requirement: 内容伦理边界（硬约束）
所有产出 SHALL 采用研究性中性转述框架：
- 不逐字复制可操作的越狱载荷或完整系统提示词正文；结构示意最多使用少量脱敏片段并明确标注为研究说明
- 保留上游仓库的伦理声明、负责任使用、免责章节要点
- 术语采用学术界既有命名（refusal direction、abliteration、red-teaming 等）并给出 arXiv 引用
- 每束 `index.md` 或伦理文档 SHALL 载明"仅用于安全研究与防御评估"的用途限定

#### Scenario: 伦理边界检查
- **WHEN** V 阶段对抗审查
- **THEN** 专设"伦理边界"检查项：全文无逐字可操作攻击载荷、无绕过安全机制的 step-by-step 操作指南（OBLITERATUS 的合法研究工具用法除外，其本身即公开研究工具且保留上游用途限定）

### Requirement: 索引注册与计数对账
索引更新 SHALL 覆盖以下五面并保持三角一致（束/组/域计数）：
1. `jishu/ai/index.md`：域内分组导航表新增 ai-security 行 + toctree 新增 `ai-security/index`
2. `jishu/index.md`：ai 行束数 121→124、关键词串追加 `ai-security`、正文"14 个分组"改 15、toctree 不变（ai-security 在 ai 内部）
3. `bundles/index.md`：frontmatter `total_bundles: 398→401`、`groups: 46→47`；导语文字同步；mermaid 概览 jishu 节点束数 +3；技术域节标题"301 束 · 14 组"→"304 束 · 15 组"；ai 分组行束数 121→124 且关键词追加
4. 严禁手填计数——一律以 `invoke gates.bundles` 重算为准（教训：远端索引数字曾自相矛盾）
5. toctree 写法统一：目录条目 `/index` 形式（如 `ai-security/index`），束根 `index.md` 内子条目 `concepts/xxx.md` 显式后缀

#### Scenario: 计数对账通过
- **WHEN** 索引更新完成并运行 `invoke gates.bundles`
- **THEN** 束/组/域三角校验通过（401 束 / 47 组 / 9 域），`invoke gates.toctrees` 无断链无孤立文档，`invoke build` Sphinx 构建零 error（含 frontmatter YAML 解析）

### Requirement: 原子提交与协作纪律
最终交付 SHALL 遵循原子提交与共享子模块协作纪律：
- `git add` 与 `git commit` 分两次工具调用，中间以 `git diff --cached --name-only` 核对暂存集仅含本次产物；发现非己方文件立即停下报告，不 commit、不 reset
- `git add` 后以 `git show :<path>` 核验暂存 blob 含关键改动（计数行、新分组节、toctree 条目），再导出暂存态快照跑双门
- 提交信息遵循 Conventional Commits，主体中文描述"为什么"（如 `docs(bundles): 新增 AI 安全与红队研究分组沉淀 elder-plinius 三仓库`）
- 派生产物 frontmatter 携带 `sources` 字段标注三仓库信源

#### Scenario: 提交暂存核验
- **WHEN** 执行原子提交
- **THEN** 暂存集仅含 ai-security 相关新增文件与 4 个索引文件，暂存 blob 核验通过，双门（gates.bundles + gates.toctrees）在暂存快照上通过

## REMOVED Requirements

无。

## 非目标（Out of Scope）

- 不修改 elder-plinius 三仓库任何文件（含 L1B3RT4S 被删除的工作树——禁止 restore）
- 不为 L1B3RT4S 建立逐厂商逐条载荷的全文翻译教程（只做分类学与防御视角）
- 不改动 bundles 库其他既有分组/束的内容
- 不处理 `jishu/index.md` 与 `bundles/index.md` 中 data 分组既有的 7/9 计数矛盾（独立历史问题，除非 gates 阻塞本次交付）
