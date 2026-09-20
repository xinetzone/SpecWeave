---
okf_version: "0.2"
type: spec
title: "QBS 书籍驱动技能构建法博文→OKF 知识包转化规划"
description: "将微信公众号博文《分享一个帮我快速把陌生领域方法论做成skill的新技巧》转化为 OKF 知识包，覆盖 QBS 方法论三段式、提示词模板、Make Time 注意力管理框架与作者开源实践"
tags: [okf-bundle, blog-article, qbs, agent-skills, make-time, attention-management, methodology]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-09-20T19:10:00+08:00" }
---

# QBS 博文 → OKF 知识包 转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段工作流执行。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 微信公众号公开文章 | https://mp.weixin.qq.com/s/cyiP8goJJrB5-Fi_F96GKA |
| 公众号 / 作者 | 卡尔的AI沃茨 / 卡尔 | 2026-09-19 12:04 发布 |
| 访问控制 | 无（公开可访问） | `/s/<id>` 公开文章格式；查询串仅 `from=industrynews&color_scheme=light`（渠道追踪与主题参数），无 `share?code=`/`token=`/邀请码等访问控制参数 |
| 敏感度级别 | **公开内容** | 公开技术博客，无个人隐私与商业秘密 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **作者一手实践叙述 + 二手书籍转述** | 非厂商自宣（作者为方法实践者与工具开源者，非被推介厂商）；QBS 方法本身来自第三方（作者称"在 X 上刷到"）；Make Time 概念为作者对成书内容的转述，权威源为原书而非本文 |

**信源距离分层说明**（决定核验强度）：

1. **QBS 方法**：作者转述第三方，且作者是实践者——转述层级 = 二手，方法细节以文章描述为准，无独立官方源可查（文章即该说法的主要来源）。
2. **Make Time 概念**：作者转述成书内容——书籍是权威源，本文为二手转述，**术语与数字必须对原书/官方材料核验**。
3. **作者个人实践数据**（Codex 任务数、切换成本推算、读书状态）：一手自述，属个人经验，不可外推为普遍结论。

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **部分** | 文章给出可直接复制的 QBS 提示词模板（含 5 条要求）与 Q→B→S 三步顺序，属"可照做的自然语言流程"；但**无**安装/配置/代码/API 调用类技术操作 |
| Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **否** | 作者虽实测了时间管理场景，但无版本约束、无可验证的输入输出对（结果依赖 GPT-6 生成与找书情况，不可复现）、无验收标准；Make Time 方法为书中知识转述，非作者实测的工程流程 |

**判定：Q2 为"否" → 方法论文骨架，不设 examples/**

判据依据（blog-article-to-okf-bundle L3）：examples/ 的取舍不看"是否技术"，看"操作可复现性"。同型先例：
- `jishu/ai/mattpocock-skills`（skills 主题微信博文）→ 无 examples/
- `jishu/ai/codex-agent-workflow-practices`（工作流实践博文）→ 无 examples/

**骨架**：
```
jishu/ai/qbs-book-to-skill/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-qbs-method.md          # 方法本体层：QBS 三段式 + 提示词模板
│   ├── 01-make-time-framework.md # 书中知识层：Highlight + 两大注意力陷阱 + Time Craters
│   └── 02-attention-tactics.md   # 战术层：书中具体战术与作者开源实践
└── references/
    ├── index.md
    ├── article-source.md         # 博文事实清单（F 编号双份登记之一）
    └── verification.md           # P0 核验报告（含勘误）
```

## 3. 归属位置分析

**主线实体**：QBS 方法（用 AI 读书把陌生领域方法论转成 Agent Skill 的方法论）。文章围绕该方法展开，《Make Time》是其一次应用产物而非主线。

**候选位置对照表**：

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/qbs-book-to-skill/`（选定） | ✅ | ① 主线是"AI 辅助构建 Agent Skill 的方法论"，属 ai 分组范畴；② 同层已有非源码类先例（`mattpocock-skills` 同为微信博文七阶段转化、`docx-report-skill` 为 Skill 设计方法论、`planning-with-files` 为 Agent 上下文工程方法论），证明该层可容纳博文转化产物；③ 与同层 `mattpocock-skills`（Skills 生态）形成"方法论→生态"互补，可交叉引用 |
| `jishu/ai/ai-agent/book-to-skill/`（子束旁挂） | ❌ | 该 bundle 是名为 book-to-skill 的**开源工具**教程（源码分析类），本文章是**方法论**而非该工具；且 bundle 不能再嵌套 bundle |
| `jishu/ai/ai-engineering-methodology/`（子束旁挂） | ❌ | 该 bundle 已为锚点组（组目录直挂 concepts/，按 1 束计），无法承载同级新束 |
| `jishu/ai/ai-agent/` 分组 | ❌ | 该分组定位为"Agent 运行时框架与架构模式"（工具调用循环/多代理编排/Coding Agent 源码），本文章为方法论而非运行框架 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**选定**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/qbs-book-to-skill/`

**幂等检查**：目标 bundle 目录不存在；`book-to-skill` 为同名近似的**不同实体**（开源工具，非本源文章），无覆盖风险。全库 Grep `qbs` 无既有知识包。

## 4. 知识结构三层拆分（I 阶段）

| 博文内容层 | 映射篇目 |
|-----------|---------|
| 方法本体层（What/How：QBS 三段式、提示词模板、方法来源） | `concepts/00-qbs-method.md` |
| 书中知识层（Why/机制：Highlight 选择法、Busy Bandwagon 与 Infinity Pools 成对机制、Time Craters 切换成本） | `concepts/01-make-time-framework.md` |
| 战术与实践层（书中具体战术 + 作者开源产物与个人实践） | `concepts/02-attention-tactics.md` |

无 examples/（见 §2）。

## 5. 核验计划（R 阶段 P0）

核验对象以**书籍事实**为主（本文的二手转述部分），辅以作者自述的产物可验证性：

| # | 待核验声明 | 类别 | 权威源方向 |
|---|-----------|------|-----------|
| P0-1 | 《Make Time》作者 Jake Knapp / John Zeratsky 及二人背景（Knapp 十年 Google、参与 Gmail 与 Google Meet；Zeratsky 十五年 YouTube 与 Google Ventures 设计） | ① 日期/版本表·④ 引文逐字 | 书籍官网 / 出版社 / 作者主页 |
| P0-2 | Make Time 核心术语：Highlight、Busy Bandwagon、Infinity Pools、Time Craters 均为书中概念 | ④ 引文逐字 | 书籍官网 maketimebook.com / 作者文章 |
| P0-3 | "书里给了 87 个具体方法"数字 | ③ 口径对照 | 书籍官网 / 出版社描述 |
| P0-4 | Caffeine Nap 战术与其"咖啡因约 20 分钟起效"依据 | ② 成效数字溯源·①  | 书籍内容 / 权威科普 |
| P0-5 | Time Craters "砸出比自身体积大 30 倍的坑"表述 | ② 成效数字溯源 | 书籍原文 |
| P0-6 | 作者开源仓库 `github.com/LearnPrompt/qbs` 是否存在及形态 | 事实存在性 | GitHub |
| P0-7 | 文中"GPT-6"模型称呼与发布状态 | ① 日期/版本表 | 官方发布信息 |
| P1 | 作者个人实践数据（切换成本 15-20 分钟、20 次×15 分钟=5 小时推算） | 作者自述 | 标注"作者自述推算"，不核验外推 |

**勘误处理约定**：发现源文错误不静默照搬——新增 F 编号记正确值，verification.md 单列勘误，正文呈现正确值并标注源文口径。

## 6. 索引接入计划（V 阶段）

| 项 | 当前值 | 目标值 |
|---|---|---|
| `bundles/index.md` total_bundles | 555 | 556 |
| jishu 域束数 | 422 | 423 |
| ai 分组束数（`jishu/ai/index.md` 表行 + toctree） | 203 | 204 |

接入动作：① `jishu/ai/index.md` 导航表新增行 + toctree 追加 `qbs-book-to-skill/index`；② `bundles/index.md` 三处计数同步；③ 与 `mattpocock-skills`、`ai-agent/book-to-skill` 建立互链。

## Open Questions

- 无。骨架与归属均已按判据确定，无待用户裁决项。