---
name: source-code-to-okf-wiki
version: 1.3.0
description: "当用户提到'源码学习'、'读源码'、'源码阅读'、'生成Wiki'、'OKF Wiki'、'源码转文档'、'学习开源项目'、'读源码写文档'、'源码分析生成教程'、'深度学一个库'时，必须使用此技能。提供系统化的源码→OKF Wiki生成工作流：阶段0信源稳定性预检 + R→I→E→V→C五阶段链路（事实采集→架构洞察→批量生成→独立验证→模式沉淀），杜绝AI虚构API、事实无溯源、结构混乱、格式不统一、信源临时路径断裂、数量陈述失真六大问题。不要直接让AI读源码写文档——本Skill封装了信源稳定性门预检、信源先行、分批生成、Grep级API验证、计数断言等经过实战验证的防护机制。"
argument-hint: "<源码路径> <输出bundle路径> [OKF规范文件路径]"
user-invocable: true
paths:
  - ".agents/skills/source-code-to-okf-wiki/**"
  - "docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-code-to-okf-wiki-workflow.md"
title: "源码阅读→OKF Wiki 生成工作流 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/source-code-to-okf-wiki/SKILL.toml"
---
# 源码阅读→OKF Wiki 生成工作流 Skill

> ⚠️ **本Skill是知识沉淀工作流门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+五阶段流程+质量门+安全清单+反模式）
> - L2：[源模式文档](../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-code-to-okf-wiki-workflow.md)（完整方法论）+ [references/prompt-templates.md](references/prompt-templates.md)（各阶段Prompt模板）

## 1. Skill ID
`source-code-to-okf-wiki`

## 2. 功能描述

系统化学习开源项目/库的源码并产出结构化 OKF v0.2 规范 Wiki 教程，采用**阶段0信源稳定性预检 + R→I→E→V→C 五阶段链路**：

| 阶段 | 全称 | 核心产出 | 质量门 |
|------|------|---------|--------|
| **0** | Pre-flight（信源稳定性预检） | 信源分类表、vendor 子模块（固定 tag）、GATE-SPS 扫描记录 | G0：信源全部 stable，临时克隆零引用放行 |
| **R** | Read/Retrospective（事实采集） | 编号事实清单 F-xxx，零推测 | G1：事实中无推断性表述 |
| **I** | Insight（架构洞察） | 3-5个核心洞察四元组+知识地图 | G2：洞察含陈述/证据/反常识/行动 |
| **E** | Extraction/Execution（批量生成） | OKF规范文档（concepts/examples/references/indexes） | G3：信源先行、分批生成、Index最后写 |
| **V** | Verification（独立验证） | 验证报告+修复后的文档集 | G4：无虚构API（Grep验证）、计数断言一致、链接无断裂、frontmatter完整 |
| **C** | Commit（模式沉淀） | 可复用模式文档+Prompt模板入库 | G5：模式含触发场景、反模式≥5、迁移验证 |

核心防护机制：**信源稳定性门预检**（阶段0，临时克隆必须升级为 vendor 子模块固定 tag）、信源先行（references/先于concepts/生成）、分批生成（每批≤7文件）、Index最后写、Grep级API真实性验证、**计数断言验证**（数量陈述经 Glob/Grep 独立复核）。

> **为什么不能直接让AI"读源码写Wiki"？** AI生成技术文档的四大顽疾——虚构API（凭训练数据"统计惯性"编造不存在的类/方法）、事实无溯源（无法验证真伪）、结构混乱（学习路径凭直觉排列）、经验不可复用（下次从零开始）——根源都是把"读源码写文档"当作一次性内容生成任务，跳过了"建立事实基础"和"独立验证"两个关键环节。本Skill的五阶段链路强制在生成前建立零推测事实基础、生成后做Grep级API验证，从流程上杜绝虚构内容。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "源码学习"、"读源码"、"源码阅读"、"深度学一个库"、"学习开源项目"
- "生成Wiki"、"OKF Wiki"、"源码转文档"、"读源码写文档"
- "源码分析生成教程"、"为XX库写中文文档"、"系统化学习XX框架"
- 需要深度学习某个Python/JS/Go库并产出可溯源的知识笔记
- 为内部/开源库生成统一格式的Wiki，要求事实可验证

> **关于触发**：即使没有明确说"用OKF工作流"，只要涉及"系统化读源码+产出结构化文档"，就应该使用本Skill。如果只是快速查一个API用法或翻译已有文档，不需要本Skill（见§4不适用场景）。

## 4. 适用性决策树

```
用户需要源码相关输出？
├─ 只是快速查一个函数怎么调用？ → ❌ 不适用（直接看官方文档或AI问答）
├─ 只写一篇README/单文件说明？ → ❌ 不适用（直接撰写，五阶段过度工程）
├─ 纯翻译/改写已有官方文档？ → ❌ 不适用（直接翻译/改写prompt即可）
├─ 闭源项目/无源码访问（只有API文档）？ → ⚠️ 边界场景（改用外部文档分析模式）
├─ 超大规模源码（>50万行/核心模块>50个）？ → ⚠️ 调整策略（分层采样：架构文档→核心接口→按需深入）
└─ 系统化学习开源库+产出可溯源Wiki？ → ✅ 适用，执行R→I→E→V→C五阶段
```

> **为什么快速查API和单篇文档不适用？** 五阶段流程的核心价值是**建立事实基础+独立验证**，这需要R阶段通读源码、V阶段Grep验证，对于"查一个函数怎么用"这类轻量需求是过度工程——投入产出比不划算。

## 5. 核心步骤（阶段0预检 + 五阶段工作流）

```
步骤0：R阶段前置预检——信源稳定性门（G0，不可跳过）
   0a. 信源分类：列出全部信源（源码仓库/克隆/下载包），按路径特征段分类：
       - temporary：.chaos/、.tmp/、系统 Temp、缓存目录中的临时克隆
       - stable：vendor/ 子模块、site-packages、系统安装目录
       - env-bound：开发者机器任意绝对路径（Desktop、home 等）
   0b. 临时信源升级：temporary/env-bound 信源必须先固定为可追溯副本——
       首选 git submodule 固定到具体 release tag（记录 tag 名 + commit hash + 远程 URL），
       次选固定到具体 commit hash；
       ⚠️ 禁止固定 main/master/浮动分支（分支会前进、tag 可能被移动重打 = 信源漂移）；
       tag 选型判据：文档引用集合 ∩ 版本变更集合 = ∅（引用的 API 在所选版本中全部存在）
   0c. 路径引用生成：facts.md 与文档中的信源路径只指向 stable 位置（vendor/<lib>），
       禁止 file:/// 指向临时目录
   0d. 清理前扫描：临时克隆删除前必须运行 GATE-SPS——
       python .agents/scripts/check-source-path-stability.py --target <待删目录>
       rc=0（零引用）放行删除；rc=1（有引用）先迁移再删
   0e. 持久性验证：文档定稿后运行 audit 模式——
       python .agents/scripts/check-source-path-stability.py
       rc=0 通过；复盘报告事实表等历史时点快照中的临时路径属预期命中，
       按"历史记录 vs 活动引用"判据人工分流
步骤1：确认输入参数（源码路径、输出bundle路径、OKF规范文件路径）
步骤2：R阶段 - 源码深度阅读与事实采集
   2a. 列出源码目录结构，识别核心模块文件
   2b. 逐个阅读核心模块，提取可验证事实（类名、方法签名、参数、数据流、继承关系）
   2c. 所有事实编号F-xxx，写入 <spec-dir>/facts.md
   2d. G1质量门：事实中不出现"用于"/"目的是"/"设计为"等推断词
步骤3：I阶段 - 架构洞察与知识结构设计
   3a. 基于事实清单，提炼3-5个核心洞察（陈述+证据+反常识+行动四元组）
   3b. 设计知识地图：文档分组（入门/核心/高级）、依赖关系、学习路径
   3c. 确定每个概念文档覆盖哪些F-xxx事实
   3d. 洞察写入 <spec-dir>/insights.md
步骤4：E阶段 - 批量生成OKF文档（信源先行！）
   4a. 创建Bundle目录结构
   4b. ⚡ 先生成 references/ 信源登记（所有sources字段的指向目标）
   4c. 分批生成 concepts/ 概念文档（每批5-7个，按学习路径顺序）
   4d. 生成 examples/ 示例文档
   4e. ⚡ 最后生成各级 index.md 导航文件
   4f. 可通过 general_purpose_task 分批并行委派
步骤5：V阶段 - 独立审查与修复
   5a. 结构检查 + Frontmatter检查 + 链接检查
   5b. ⚡ Grep验证：对文档中引用的每个类名/方法名，在源码中验证存在性
   5c. 代码示例检查：API调用与源码一致
   5d. Index完整性检查
   5e. 输出检查报告，逐一修复问题
   5f. ⚡ 计数断言验证：对文档中所有"X个/Y份/Z处/N篇"类数量陈述，
       用 Glob/Grep 独立计数比对（如"15个核心模块"→实际数目录/Grep定义；
       "368个文件"→Glob 计数），数字不一致即修复——禁止凭印象写数量
步骤6：C阶段 - 模式萃取与沉淀
   6a. 回顾流程顺利点和问题点
   6b. 补充反模式和迁移验证
   6c. 模式存入 docs/retrospective/patterns/ 对应目录
```

> **完整各阶段Prompt模板见** [references/prompt-templates.md](references/prompt-templates.md)。

> **为什么references/必须先生成？** OKF文档的frontmatter中`sources`字段指向references/下的信源文件。如果先写concepts/再补references/，sources字段会指向不存在的文件，导致交叉引用断裂。信源先行是避免后期大面积修复的关键纪律。

> **为什么Index必须最后写？** Index文件列出目录中所有文档的清单。如果一开始就写好index，后续新增/删除/重命名文档时容易忘记更新index，导致遗漏或列出不存在的文件。所有内容文档定稿后再统一写index，确保100%完整。

## 6. OKF文档规范速查

### 6.1 Bundle目录结构

```
<bundle-name>/
├── index.md              # 根索引（含 okf_version frontmatter + toctree）
├── log.md                # 变更日志
├── concepts/             # 概念文档
│   ├── index.md          # 概念索引（无frontmatter，必须含 toctree 块）
│   └── 00-xxx.md ~ NN-xxx.md
├── examples/             # 示例文档
│   ├── index.md          # 必须含 toctree 块
│   └── ...
└── references/           # 信源登记
    ├── index.md          # 必须含 toctree 块
    └── <source>.md
```

### 6.2 Frontmatter必填字段

```yaml
---
type: <Concept|Example|Reference|Pattern>
title: <文档标题>
description: <一句话描述，30-80字>
tags: [<标签1>, <标签2>, ...]
generated: { by: <生成者标识>, at: <ISO8601时间> }
verified: { by: "process:seven-concepts-v", at: <ISO8601时间> }
status: <draft|stable|deprecated>
stale_after: <YYYY-MM-DD过期日期>
sources:
  - id: <信源ID>
    resource: /references/<source-file>.md
    title: <信源标题>
---
```

### 6.3 内容规范

- 开头1-2段概述概念/示例是什么
- 使用 `##` 二级标题分节，不使用 `#`（留给文件标题）
- 代码块标注语言，API调用必须与facts.md中事实一致
- 每个文档结尾有 `## 相关概念` 章节
- 交叉链接使用 `/` 开头的bundle-relative路径（如 `/concepts/02-task-basics.md`）
- 中文撰写，英文技术术语首次出现时括号注释

> **为什么交叉链接用`/`开头而非`../`相对路径？** 相对路径（`../concepts/xxx.md`）在文件移动后链接断裂，且不同目录深度需要不同层级的`../`，维护成本高。`/`开头的bundle-relative绝对路径从bundle根目录解析，不随文件位置变化，路径风格统一。

### 6.4 index.md 导航规范（toctree 必填）

**每个 index.md（根 + 全部子目录）必须包含 `{toctree}` 指令块**，收录本目录全部内容文档（跳过 index/readme/log 由根处理）：

````markdown
```{toctree}
:hidden:
:maxdepth: 2

00-first-doc
01-second-doc
```
````

- **根 index.md** 的 toctree 收录 `concepts/index`、`examples/index`、`references/index`、`log`；分组 index.md 收录各束的 `<bundle>/index`
- **子目录 index.md** 的 toctree 收录本目录全部内容文件（stem 形式，按文件名排序）
- toctree 与人类可读的表格/列表链接**并存**——表格给读者，toctree 给 Sphinx/CI 导航

> **为什么表格链接不能替代 toctree？** Markdown 表格链接只对人类读者有效；Sphinx 与 CI 质量门（`check-toctrees.py`）从 `doc/index.md` 沿 `{toctree}` 指令块做 BFS 导航，子目录 index 缺 toctree 块即导航断头，其下全部内容文档被判"未收录(不可达)"——即使表格链接完好无损。containers 域曾因此产生 52 个门禁失败项（6 束 18 个子目录 index 缺 toctree，2026-08-28 修复）。

## 7. 安全检查清单（质量门）

- [ ] **G0-预检（R阶段前）**：信源已分类（temporary/stable/env-bound）；临时信源已升级为 vendor 子模块并固定到具体 tag/commit（禁止 main/master）；facts.md 信源路径全部指向 stable；清理前扫描与持久性验证已用 GATE-SPS 脚本执行（rc=0）
- [ ] **G1-R阶段**：事实清单无推断性表述（"用于"/"目的是"等），每个事实指向源码路径，核心模块全覆盖
- [ ] **G2-I阶段**：洞察四元组完整（陈述/证据/反常识/行动），知识地图有学习路径设计
- [ ] **G3-E阶段**：references/信源文件先于其他文档生成，分批生成（每批≤7文件），index最后写
- [ ] **G4-V阶段**：链接无断裂、无虚构API（Grep源码验证每个类名/方法名存在性）、**计数断言全部比对一致**（"X个/Y份/Z处"类陈述经 Glob/Grep 独立复核）、frontmatter字段完整、index无遗漏
- [ ] **G5-C阶段**：模式文档含反模式（≥5个）、Prompt模板可复用、模式入库到正确目录
- [ ] 每批生成文档数≤7（防止上下文过载导致质量下降）
- [ ] 代码块标注语言，API调用与facts.md事实一致
- [ ] 子目录index.md不含frontmatter（仅根index.md保留okf_version）
- [ ] 每个index.md（根+子目录+分组）均含`{toctree}`块且收录本目录全部内容文档；生成后运行 `invoke gates.toctrees`（或 `python scripts/check-toctrees.py`）验证导航链完整

> **为什么V阶段Grep验证是"必须"而非"建议"？** AI在生成"看起来合理"的代码时非常危险——越是常见的编程模式（如HTTP响应对象`Response`），AI越容易凭训练数据的"统计惯性"编造不存在的API。PyInvoke实践中就出现了虚构的`Response`类，代码示例看起来完全合理但源码中根本不存在。V阶段的Grep验证是拦截虚构API的最后一道防线，不可省略。

## 8. 早期预警信号

执行过程中出现以下信号时，必须暂停并回退检查：

| 预警信号 | 可能问题 | 行动 |
|---------|---------|------|
| R阶段事实出现"用于"/"目的是" | 违反零推测原则 | 推断移至I阶段，事实只保留"代码里有什么" |
| AI说"根据常见模式"/"通常情况下" | AI凭印象编造 | 暂停，要求引用具体F-xxx编号 |
| 引用的类名/方法名在facts.md中找不到 | 可能虚构API | 立即Grep源码验证 |
| 单批生成>7个文件 | 上下文过载 | 拆分为更小批次 |
| references/未创建就开始写concepts/ | 违反信源先行 | 暂停，先生成references/ |
| index.md含frontmatter字段 | 不符合OKF规范 | 移除frontmatter |
| 子目录index.md只有表格链接、无`{toctree}`块 | CI门禁报"未收录(不可达)"，整束内容导航断头 | 按§6.4追加隐藏toctree块，收录本目录全部内容文件 |
| 交叉链接出现`../` | 路径风格不一致 | 替换为`/`开头路径 |
| V阶段发现>1个虚构API | E阶段事实遵循度不足 | 全面Grep验证所有文档 |
| 信源路径含 .chaos/.tmp/Temp 等临时段或 file:/// 绝对路径 | 临时信源，克隆清理后引用全部断裂 | 暂停R阶段，先执行步骤0信源升级（vendor 子模块 + 固定 tag） |
| 信源版本固定在 main/master/浮动分支 | 信源漂移：分支前进后文档与信源不一致 | 改为固定 release tag/commit hash，并记录 hash 与获取方式 |
| 文档出现"X个/Y份/Z处"数量陈述但未经独立计数 | 计数完整性盲区（验证了存在性、没验证数量） | V阶段用 Glob/Grep 独立计数比对（步骤5f） |

## 9. 反模式速查（10个致命错误）

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 跳过R阶段直接写文档 | 虚构API、过时方法、错误参数 | 强制R阶段，逐模块提取编号事实 |
| 2 | 信源后置（先写文档再补references） | sources指向不存在文件，交叉引用断裂 | E阶段第一步生成references/ |
| 3 | 一次生成所有文档（>7个） | 上下文过长→质量下降、格式不一致 | 分批生成，每批≤7文件 |
| 4 | Index先写/边写边更新 | Index遗漏新增文档或列出不存在文件 | 所有内容文档定稿后统一写index |
| 5 | 不验证API真实性就交付 | 虚构API混入文档，读者照抄报错 | V阶段Grep验证关键类名/方法名 |
| 6 | 产出物留在spec目录不入库 | 下次同类任务无法复用，经验浪费 | C阶段迁移模式到patterns/目录 |
| 7 | 交叉链接使用`../`相对路径 | 文件移动后链接断裂，维护成本高 | 统一使用`/`开头bundle-relative路径 |
| 8 | 子目录index.md用表格链接替代`{toctree}`块 | Sphinx/CI导航BFS断头，束内全部内容"未收录(不可达)"（containers域52项门禁失败实证） | 每个index.md必含隐藏toctree块（§6.4），与表格链接并存 |
| 9 | 临时克隆直接开读、不固定版本（.chaos/libs 里 git clone 完就生成文档） | 克隆清理后 file:/// 引用全部断裂（veadk 案例 800 处引用迁移实证）；版本不可追溯，重跑无法复现 | 步骤0预检：信源升级为 vendor 子模块固定 release tag（记录 tag+commit hash），引用只指 stable |
| 10 | 信源漂移：固定到 main/master/浮动分支，或只记 tag 名不记 commit hash | 分支前进/tag 被移动重打后，文档验证过的 API 与信源内容不一致，V 阶段结论失效 | 固定不可变 release tag/commit hash；tag 选型按"文档引用集合 ∩ 版本变更集合 = ∅"判定 |

## 10. Gotchas（陷阱与反直觉行为）

- **AI对"常见模式"的虚构倾向最强**：HTTP响应对象、配置类、上下文管理器等通用编程模式是AI虚构的高发区——越"合理"的API越需要Grep验证，不要因为代码"看起来对"就跳过验证。
- **R→E时间距离导致事实遵循度衰减**：E阶段生成高级概念文档时，距离R阶段事实采集已过几轮对话，AI对facts.md的遵循度自然下降。解决方法是在每批生成prompt中显式附上相关F-xxx事实编号，并要求AI在不确定时回查facts.md。
- **初始V阶段不能只查链接和frontmatter**：链接有效+frontmatter完整≠内容准确。PyInvoke实践中初始V阶段只做了结构检查，遗漏了虚构的`Response`类。必须增加API真实性Grep验证。
- **Windows路径分隔符陷阱**：源码路径在Grep命令中使用`/`或正确转义的`\\`，避免路径解析失败导致误判"API不存在"。
- **分批并行委派时保持独立上下文**：通过general_purpose_task分批并行生成时，每个子任务必须独立获得完整的格式规范和相关事实清单，不能假设子任务共享主会话上下文。
- **tag 也可能漂移**：固定版本时优先选择正式 release tag 并同时记录 commit hash——轻量 tag/分支 tag 可能被维护者移动重打，浮动分支必然前进；只记 tag 名不记 hash，事后无法证明"文档验证的就是这份代码"，也无法复现。
- **临时克隆的引用断裂是"静默"的**：file:/// 指向 .chaos/libs 的链接在克隆存在时完全可用，问题只在清理后爆发——所以信源稳定性必须在 R 阶段开工前（步骤0）解决，而非 V 阶段修补。

## 11. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| **源模式文档（完整方法论）** | **L2** | [source-code-to-okf-wiki-workflow.md](../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-code-to-okf-wiki-workflow.md) | **首次使用必读**——含完整案例、失败复盘、检验标准、跨场景迁移 |
| **信源稳定性门模式** | **L2** | [source-stability-gate.md](../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-stability-gate.md) | 步骤0预检的完整方法论（5步法+反模式+双案例验证） |
| **Prompt模板集** | **L2** | [references/prompt-templates.md](references/prompt-templates.md) | 每阶段执行时复制对应Prompt |
| **GATE-SPS 扫描脚本** | **L1 工具** | `.agents/scripts/check-source-path-stability.py` | 步骤0d/0e：清理前扫描（--target）与持久性 audit |
| **批量文档转换模式** | **L2** | [batch-docs-to-okf-bundle-conversion.md](../../docs/retrospective/patterns/methodology-patterns/concepts/batch-docs-to-okf-bundle-conversion.md) | 非源码文档（Wiki/报告/笔记）批量转换为OKF Bundle时参考，含9个反模式 |
| 七概念方法论编排 | L1 | [seven-concepts-cmd](../seven-concepts-cmd/SKILL.md) | 本模式是七概念在知识沉淀场景的具体化 |
| 原子提交 | L1 | [atomic-commit-cmd](../atomic-commit-cmd/SKILL.md) | C阶段模式入库时使用 |
| 链接检查 | L1 | [link-check-cmd](../link-check-cmd/SKILL.md) | V阶段链接验证时使用 |

## 12. Changelog

- **v1.3.0** (2026-08-29): R阶段前新增「步骤0 信源稳定性门预检」（G0）：信源分类→临时信源升级 vendor 子模块并固定 release tag（禁 main/master）→引用只指 stable→GATE-SPS 清理前扫描（--target）→持久性 audit；V阶段新增 5f 计数断言验证（"X个/Y份/Z处"类陈述经 Glob/Grep 独立复核）；新增反模式9（临时克隆直接开读不固定版本）与反模式10（信源漂移），早期预警信号新增 3 行，Gotchas 增 tag 漂移与静默断裂；源于 jira-skill v3.29.0 与 veadk-python 1.0.10 两次 vendor 同步里程碑（800 处引用迁移实证）；同步 frontmatter version 字段（1.0.0→1.3.0）并补 SKILL.toml 元数据镜像。
- **v1.2.0** (2026-08-28): 新增§6.4「index.md 导航规范（toctree 必填）」与反模式8（表格链接替代toctree），源于 containers 域 52 项 toctrees 门禁失败修复实践；G4检查清单增加toctree门禁验证项。
- **v1.1.0** (2026-08-22): 扩展非源码文档转换场景，新增「批量Markdown文档→OKF Bundle转换模式」参考（31个Bundle、368文件实战验证）。
- **v1.0.0** (2026-08-21): 初始版本，从PyInvoke v3.0.3 OKF Wiki生成实践萃取，封装R→I→E→V→C五阶段工作流、OKF文档规范、7个反模式、Grep级API验证机制。
