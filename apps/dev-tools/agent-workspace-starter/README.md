---
id: "agent-workspace-starter-readme"
title: "智能体工作区起步套件（Agent Workspace Starter）——运营落地页"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 智能体工作区起步套件（Agent Workspace Starter）

> **9.9 元 · 60 分钟上手。** 把 AI 智能体的规范体系萃取成一份可拷贝、可自检、可复用的最小化起步套件。

## 一、价值主张

### 一句话定位

用一份最小化工作区（根契约 + 规范容器），让 AI 智能体在你自己的项目里**行为可预测**：开工流程固定、产出位置固定、验收标准固定——无需每次重复交代规则。

### 面向谁

- **AI 工具个人用户**：想给常用 AI 编码工具配一套「长期有效」的工作规则，而不是每次靠长提示词临时对齐。
- **小团队**：需要一份轻量、可拷贝到各项目的共识底座，统一「怎么开工、按什么标准、产出放哪」。

**典型场景**：

- 给个人项目配一套 AI 开工规则，避免每次重复交代偏好。
- 把团队共识写成可拷贝的规范底座，新项目直接整目录复用。
- 用一个 25 分钟的小任务，体验「先写规格、再实施、后验收」的完整闭环。

### 三个卖点

1. **60 分钟上手**：教程 + 演练合计 ≤1500 行，按 10/15/25/10 分钟四段时间盒推进，每段都有「完成检查点」。
2. **全貌导览 18 类目**：`.agents/` 的 18 个规范类目各保留代表文件并附一句话导览，一眼看清整套体系的骨架，不必通读。
3. **程序化可验证**：随附零依赖自检脚本，一键核对装载是否完整、「启动协议」锚点是否命中，exit code 说话。

### 与完整版的关系

- **本产品 = 起步套件**：帮你「快速上手 + 拿到全貌导览」，是一次成功体验的入口。
- **完整版 = SpecWeave 开源仓库**：[https://github.com/xinetzone/SpecWeave](https://github.com/xinetzone/SpecWeave)（外链文字）。完整 `.agents/` 实测 6850 文件 / 134.5 MB，本套件从中萃取 40 文件 / 1436 行的最小子集，把 93%+ 的执行体（技能与脚本，按文件数计 6388/6850≈93.3%）挡在门外。

### 本套件不包含什么（防止预期错配）

- 不含完整 `.agents/`（6850 文件 / 134.5 MB）——那是完整版的范围。
- 不含技能与脚本全家桶（按体积计占完整体系约 97.6%），仅保留一份 Skill 门面示例。
- 不含支付 / 购买系统——9.9 元交易在站外完成。
- 不含 Hub CLI、应用市场等生态功能——本套件聚焦「首个成功体验」。

## 二、内容清单

```
agent-workspace-starter/
├── README.md                 ← 本文件（运营落地页）
├── starter/                  ← 最小化工作区套件（40 文件 / 1436 行，可整体拷入自有项目）
├── guide/                    ← 60 分钟时间盒教程（5 文件 / 362 行）
├── walkthrough/              ← 「规格驱动小任务」演练剧本（4 文件 / 338 行）
├── bootstrap-prompt.md       ← 一句话装载提示词（安全规则 + 幂等条款）
├── skill/SKILL.md            ← Trae Skill 装载门面
└── scripts/verify_starter.py ← 零依赖自检脚本（纯 Python 标准库）
```

| 部分 | 一句话说明 |
|---|---|
| [starter/](starter/) | 可直接拷贝的最小化工作区：根契约 [AGENTS.md](starter/AGENTS.md)（含「启动协议」锚点）+ [.agents/](starter/.agents/) 全貌导览 + [许可说明](starter/LICENSE-NOTICE.md) |
| [guide/](guide/) | 学习路径总览与四段教程：[README](guide/README.md) / [00 概览](guide/00-overview.md) / [01 装载](guide/01-bootstrap.md) / [02 首个任务](guide/02-first-task.md) / [03 进阶](guide/03-next-steps.md) |
| [walkthrough/](walkthrough/) | 「目录树查看器」规格驱动演练：先写 spec → 再实施 → 后验收，全程可照抄 |
| [bootstrap-prompt.md](bootstrap-prompt.md) | 装载门面：把套件装进自有项目的一句话提示词 |
| [skill/SKILL.md](skill/SKILL.md) | Trae Skill 门面，供 IDE 内一键装载 |
| [scripts/verify_starter.py](scripts/verify_starter.py) | 自检脚本：核对文件齐备性 / 启动协议锚点 / 相对链接可达 |

**全貌导览覆盖的 18 个类目**（每个类目保留代表文件 + 一句话导览）：

- 根契约与入口层（2）：根契约 `AGENTS.md`；入口层 `ONBOARDING`（入门）/ `context-routing`（路由）/ `global-core-rules`（全局规则）/ `capability-registry`（索引）
- 核心类目（5）：`roles`（角色）/ `rules`（规则）/ `protocols`（协议）/ `workflows`（工作流）/ `templates`（模板）
- 配套类目（3）：`commands`（指令）/ `checklists`（检查清单）/ `skills`（技能门面）
- 扩展导览（8）：`modules` / `teams` / `prompts` / `tools` / `worlds` / `capabilities` / `cases` / `systems`

**规模事实**（2026-10-07 实测）：

| 交付物 | 文件数 | 行数 |
|---|---|---|
| starter/（最小化套件） | 40 | 1436 |
| guide/（教程） | 5 | 362 |
| walkthrough/（演练） | 4 | 338 |

## 三、1 小时上手路径

按四段时间盒推进，完整总览与逐段步骤见 [guide/README.md](guide/README.md)。

| 段位 | 时长 | 做什么 | 本段产出（可观察） |
|---|---|---|---|
| 00 概览 | 10 min | 认识「根契约 + 规范容器」结构与类目地图 | 能说出 ≥5 个类目的作用 |
| 01 装载 | 15 min | 用一句话提示词把 starter 拷进自有项目并自检 | 自检脚本 exit 0；根 `AGENTS.md` 命中「启动协议」 |
| 02 首个任务 | 25 min | 按「规格驱动」完成一个小工具 | `spec/` + `tree_view.py` + 运行输出 + 验收记录 |
| 03 进阶 | 10 min | 选定 rules/protocols 深潜条目与后续路径 | 1 个深潜条目 + 一句话后续动作 |
| **合计** | **60 min** | — | — |

> 走完之后你会得到：一个已装载最小化工作区的自有项目、一份可复用的装载提示词、一个跑通过一次的规格驱动小工具产出物、一张清晰的后续深潜地图。

**为什么 1 小时能上手（内容基线）**：

- **入口层天然轻量**：`.agents/` 根级 9 份 Markdown 合计 503 行，最长一份 120 行——概览与装载两段要读的入口总量落在数百行量级。
- **体量主体被挡在门外**：完整 `.agents/` 有 6850 文件 / 134.5 MB，其中技能与脚本两类按体积占约 97.6%（按文件数占约 93.3%）；本套件只取各类目代表文件，把执行体挡在门外。
- **预算硬约束**：教程 ≤900 行、演练 ≤600 行、合计 ≤1500 行，正是「60 分钟可消化」的刻度——不是让你读完整个体系，而是读入口层、装好工作区、跑通一个任务。

## 四、快速开始（3 步）

**前置条件**：一个可装载智能体的工具（Trae 或兼容的 AI 编码工具）；套件文件已下载到本地；一个想让它变「规范」的自有项目目录（空目录亦可）；Python 3.10+（自检脚本仅用标准库）。

1. **拷贝**：把 [starter/](starter/) 下的 `AGENTS.md`、`.agents/`、`LICENSE-NOTICE.md` 并入你的项目根目录（照抄命令见 [guide/01-bootstrap.md](guide/01-bootstrap.md)）。
2. **装载**：把 [bootstrap-prompt.md](bootstrap-prompt.md) 里的提示词发给你的智能体，让它按根 `AGENTS.md` 的「启动协议」读取 `.agents/` 并报告装载清单。
3. **自检与走教程**：在套件根目录运行 `python scripts/verify_starter.py`（输出通过报告且退出码为 0），随后从 [guide/README.md](guide/README.md) 开始走 60 分钟路径。

## 五、许可与使用边界

- **授予**：购买者可**个人使用与修改**本套件——将 [starter/](starter/) 整体拷贝进自有项目，并按需增删、改写其中的规范文件。
- **允许**：在自有项目、团队内部及交付给客户的成果中使用本套件内容。
- **禁止**：将本套件整体或实质性部分**转售、重新分发为同类付费产品**（包括打包进其他付费入门包、模板市场商品或培训课程售卖）。
- 引用、转述本套件中的方法或规范用于公开文章时，请注明来源。
- 本套件中的规范内容萃取自 SpecWeave 开源仓库（Apache License 2.0）；源自该仓库的内容依 Apache-2.0 授权，上述禁止转售限制仅针对本套件的原创部分（教程 / 演练 / 提示词 / 脚本 / 编排）。详见 [starter/LICENSE-NOTICE.md](starter/LICENSE-NOTICE.md#内容来源与许可)。
- 本套件为**最小化入门子集**，并非完整规范体系；完整版规范见 [SpecWeave 开源仓库](https://github.com/xinetzone/SpecWeave)。本套件按「现状」提供，不附带任何明示或默示担保。

> 完整条款见 [starter/LICENSE-NOTICE.md](starter/LICENSE-NOTICE.md)。

## 六、获取方式

- **定价**：9.9 元。
- **获取方式**：<待运营者填写>（收款与交付渠道在站外完成）。
- **交付形态**：你将下载到本目录的完整内容——`starter/`（40 文件最小化套件）、`guide/`（四段教程）、`walkthrough/`（演练剧本）、装载门面与自检脚本，均为纯 Markdown 与单份 Python 标准库脚本，无需构建即可使用。

## 七、常见问题

- **能商用吗？** 可以在自有项目、团队内部及交付给客户的成果中使用；但禁止把本套件整体或实质性部分转售、重新分发为同类付费产品。详见 [五、许可与使用边界](#五许可与使用边界)。
- **和 SpecWeave 开源仓库什么关系？** 本套件是从 SpecWeave 的 `.agents/`（6850 文件 / 134.5 MB）萃取出的 40 文件最小入门子集，聚焦「60 分钟首个成功体验」；完整体系见 [SpecWeave 开源仓库](https://github.com/xinetzone/SpecWeave)。
- **需要什么环境？** 一个可装载智能体的工具（Trae 或兼容工具）；Python 3.10+（自检脚本仅用标准库，无第三方依赖）。无需构建步骤、无需联网。