---
id: spec-ai-agent-book-blog-okf-wiki
title: 微信博文《2.8万Star！AI Agent 教材来了》→ OKF 知识包转化方案
source: https://mp.weixin.qq.com/s/XL9UWNcrC9BwQw8BbShHOA
created: 2026-09-16
status: done
workflow: blog-article-to-okf-wiki（R→I→E→V→C，seven-concepts 场景4 知识沉淀）
---

# Spec：ai-agent-book 开源书推荐博文 → OKF bundle

## 0. 内容敏感度预检

- URL 为微信公众号公开文章（`mp.weixin.qq.com/s/<id>`，无 `share?code=`/`token=`/邀请码参数）→ **公开内容（Public）**
- 工作流：标准工作流——spec 位于 `.trae/specs/okf-wiki-ecosystem/ai-agent-book-blog-okf-wiki/`，bundle 产出位于 `projects/awesome-okf-xs/doc/bundles/`（git submodule）
- 信源获取：微信域名对 WebFetch 反爬确定（Skill 13/13 记录），直接用 browser_use 子代理提取 `#js_content`，得全文 2811 字 + 2 代码块 + 2 表 + 6 配图 alt

## 1. 信源距离预判

**第三方推荐文 → 但核验对象（开源书仓库）一手可得**。公众号"杰克王聊AI"非作者本人、非厂商赞助文（无成效数字/提效倍数类营销叙事），属第三方资源盘点；书籍事实可直接对 GitHub 仓库（bojieli/ai-agent-book）、GitHub API、作者官方个人页（ring0.me / 01.me）做权威核验，核验强度高于一般博文。无厂商自宣成效数字（Pine AI 的 93%/$37M 出自作者 CV，仅作作者背景旁证，不入正文主张）。

## 2. 骨架判定（操作可复现性两问）

| 两问 | 判定 | 证据 |
|------|------|------|
| Q1 有读者可照做的安装/配置/代码/调用/实测流程？ | 边界性"是" | 有 git clone、uv sync/uv run、PDF 下载三条命令 |
| Q2 经博文作者实测、有版本/输入输出/步骤顺序？ | **否** | 公众号作者未声称实测；全文无任何运行输出；命令逐字引自官方 README；无实验结果展示 |

**结论：任一问为否 → 不设 examples/**（参照 threeui/a2a-mcp 技术盘点正例）。获取与运行方式以概念文档承载。内容性质：**技术综述/资源盘点（开源书籍推荐）**，index 顶部声明"非操作教程，无 examples"。

## 3. 归属判定（决策树）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/ai-agent/`（选定） | ✅ | ① 主线实体是通用 AI Agent 系统性教材，公式/工作流/评估/多 Agent 均为该组主题；② 分组"📰 产品资讯"板块已有 pi-agent-harness（博文综述）、matrix-zero-person-company（产品资讯）、a2a-mcp-convergence（技术分析）等非源码博文转化先例；③ 与同组 ai-agent-fundamentals（6 大架构模式）、book-to-skill（书籍→技能编译器）天然互链 |
| `jishu/ai/datawhale/` | ❌ | Datawhale 开源学习社区是组织锚点，本书作者与该社区无关 |
| `jishu/document/` | ❌ | 文档工程域（Sphinx/MyST），主题不符 |
| 新建分组 | ❌ | 单篇博文新建分组违反最小变更原则 |

- bundle 名：`ai-agent-book`
- 板块：分组 index "📰 产品资讯"表，类型"开源书推荐"

## 4. R 阶段核验结论摘要（勘误四张清单）

事实集：F-001~F-024 博文事实（24 条）+ F-025~F-041 核验补充（17 条），共 41 条，见 [facts.md](facts.md)。

P0 核验 18 项 + P2 单源 1 项：

- ✅ 通过 13 项：仓库存在与 Apache-2.0、上线 2025-09-09、Star 时点口径自洽、10 章主题（1.4 时点）、13 语言（时点）、Python 3.10+（时点）、uv 命令逐字一致、三渠道 URL 逐字一致、核心公式、三维对比表、作者身份（ring0.me/CV）、Pine AI 业务、Trending 徽章、免费开源
- ❌ 勘误 2 项：①博文"94 实验"——发布前 9 小时官方头条为 **95**，且博文逐章表自相加为 **98**（内部矛盾）；②第 6 章写 11，官方编号至 6-12 为 **12**
- ⚠️ 口径 3 项：③"四种工作流模式"——仓库现存 5 张 wf 图（含 routing/evaluator），2.0 正文已改"工作流 vs 自主 Agent"二分；④"一条命令就能跑"以偏概全（实验分 ✅/📖/🚧 三类，22 个外部仓库、API Key/GPU 等）；⑤时效漂移（13→15 语言、3.10+→3.11–3.13、94/95→109、1.4→2.0 章节重组）
- 单源 1 项：⑥"中科大 Linux 用户组成员"官方页未检出，不进入正文

**状态决策**：2 处 ❌ 均为非核心数字失准（书的核心声明"免费、开源、系统性、10 章教材"全部成立；且实验数当周处于 88→92→95→109 快速增补期），按 Skill 规则 **status: stable + 完整勘误**，不触发 flagged。

## 5. I 阶段：三层知识拆分（5 篇概念，无 examples）

| 知识层 | 篇目 | 承载 F |
|--------|------|--------|
| 事实层（What/Who/When） | `concepts/00-book-and-author.md` 书籍卡片、双时点指标、作者档案、获取渠道 | F-001~F-009, F-022, F-024, F-031, F-032, F-036, F-039~F-041 |
| 原理层（核心公式/框架） | `concepts/01-core-formula.md` 公式与 Environment 边界、大脑/眼睛/手脚、Harness、工具三/五类、三维对比表 | F-010~F-012, F-019, F-034, F-035, F-038 |
| 模式层（工作流） | `concepts/02-workflow-patterns.md` 链式/并行/Orchestrator、四种说法 vs 5 图核验、2.0 二分叙述 | F-013, F-018, F-033 |
| 结构层（章节/实验/版本） | `concepts/03-chapter-map-and-experiments.md` 三口径章节对照、实验数勘误、三类状态、运行方式、1.4→2.0 迁移 | F-014~F-017, F-025~F-030, F-037 |
| 生态层（社区/学习价值） | `concepts/04-community-and-learning.md` 13→15 语言、Star 双时点、观点分层、适合谁、时效导览 | F-020, F-021, F-023, F-029, F-037 |

references：`article-source.md`（F-001~F-041 双份登记）+ `verification.md`（18 项 P0 核验报告 + 6 条勘误）。

## 6. E 阶段产物清单（11 文件）

```
jishu/ai/ai-agent/ai-agent-book/
├── index.md                 # 根索引（性质声明/双时点提示/已知边界/toctree）
├── log.md                   # 生成与 V 阶段记录
├── concepts/
│   ├── index.md
│   ├── 00-book-and-author.md
│   ├── 01-core-formula.md
│   ├── 02-workflow-patterns.md
│   ├── 03-chapter-map-and-experiments.md
│   └── 04-community-and-learning.md
└── references/
    ├── index.md
    ├── article-source.md
    └── verification.md
```

索引接入（V 阶段）：分组 `ai-agent/index.md`（导航行 + toctree + total_bundles）、域 `jishu/ai/index.md`（如含束数则同步）、总索引 `bundles/index.md`（三面计数）。注意：子模块工作树有**他会话并行 WIP**（未跟踪 openviking/、loopx/，sheke 计数改动），按 gate 脚本"谁添加谁对账"原则只对账本束，残余漂移在 log 注明。

## 7. 质量门

- G1（R）：事实无推断词、P0 逐项过勘误四张清单 ✅
- G3（E）：信源先行、F 编号引用、index 最后写、所有具体数字可溯源
- G4（V）：双份 F 编号集合一致（41=41 连续）、三级 toctree 完整、相对链接可达、UTF-8 strict、计数同步（扣除他会话 WIP）
- frontmatter：okf_version 0.2 / status: stable / stale_after: 2026-11-30（书籍迭代极快：6 周内 95→109 实验、1.4→2.0，设 2.5 个月复核窗口）/ sources 含博文 + GitHub 仓库 + GitHub API + 作者官方页
