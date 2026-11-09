# Spec：微信聊天记录转发 WorkBuddy 与两个 Skill → OKF 知识包

- **信源**：`https://mp.weixin.qq.com/s/BvTuiZelPTb1ZgLT3NoMHQ`《微信聊天记录终于能正经交给 AI 了，官方开的口子不怕封号》，林月半子聊AI / 林月半子的AI笔记，2026-10-10（F-001~F-004）
- **任务意图**：使用 `/七概念` 方法论对文章做「全面学习」，生成 OKF wiki 教程，落到 `doc/bundles/` 恰当位置
- **执行链路**：七概念「知识沉淀 / 方法论」场景 → **R → I → E → V → C**（`seven-concepts-cmd` 场景 4 / `blog-article-to-okf-wiki` 七阶段工作流）
- **执行日期**：2026-11-06
- **session**：`sc-20261106-wechat-workbuddy-forward-skills`

## 1. 内容敏感度预检（步骤 0）

| 检查项 | 结果 |
|--------|------|
| URL 是否含 `code` / `token` / 邀请码 / `share?` 访问控制参数 | 否（F-004） |
| 是否企业内部域名 / 私域标注 | 否，`mp.weixin.qq.com` 公开文章页 |
| 判定 | **公开内容（Public）** |
| 工作流 | 标准 Spec Mode：spec 在主仓库 `.trae/specs/okf-wiki-ecosystem/`，产出物在子模块 `projects/awesome-okf-xs/doc/bundles/` |
| 依据 | 根 `AGENTS.md` 内容敏感度预检条款、`.agents/rules/content-sensitivity-precheck.md`、子项目 `AGENTS.md`「公开内容入 `doc/bundles/` 或 `doc/`」 |

## 2. Skill 路由判定

| 候选 | 判定 | 理由 |
|------|------|------|
| `blog-article-to-okf-wiki` | ✅ **采用** | 信源是单篇公开博文 URL，要求转化为可溯源 OKF 知识包；触发词「公众号文章 / OKF wiki」命中 |
| `source-code-to-okf-wiki` | ❌ | 无本地 vendor 源码目录，不适用 Grep 源码验证链路 |
| `seven-concepts-cmd` | ✅ 元编排 | 用户显式要求 `/七概念`，提供 R→I→E→V→C 链路与质量门追溯 |
| 直接摘要回答 | ❌ | 用户要求「全面学习 + 生成教程 + 落盘」，非快速摘要 |

## 3. 归属位置分析（步骤 3：主线实体优先 + 查先例 + 不新建分组）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `doc/bundles/jishu/ai/products/` | ✅ **选定** | ① 文章主线实体是「微信转发到其他应用 → WorkBuddy」这一**产品入口**与基于它的两个**工具型 skill**，不是官方文档也不是行业趋势；② 该组已有 39 个产品/工具型知识包，其中 `wechat-intelligence-hub`、`knocket`、`wigolo`、`pagekin`、`inurl-byok-token-hub`、`skills-manager` 等均为「微信博文经 OKF v0.2 七阶段转化」先例，证明分组可容纳非源码类产物；③ 单篇博文禁止新建分组 |
| `doc/bundles/jishu/ai/ecosystems/tencent/` | ❌ | 该组以腾讯官方文档、开放平台、白皮书、资料库实践等**官方生态资料**为主；本文是第三方作者的个人实践与自造工具，不是官方资料 |
| `doc/bundles/sheke/industry/` | ❌ | 已有 `workbuddy-content-system` 等商业分析包，但该组索引明确「AI 技术实现类教程归技术域」；本文核心是产品功能与工具用法，不是商业模式或行业趋势 |
| `doc/bundles/jishu/ai/practice/` | ❌ | 偏工程方法论与行业洞察；本文有明确产品实体，按「主线实体优先」应落 products |
| 新建顶级分组 | ❌ | 违反最小变更原则 |

**选定 bundle**：`workbuddy-wechat-chat-forward-skills`（kebab-case 纯英文，以产品名打头，与既有 `workbuddy-content-system` 命名一致）。

## 4. 骨架判定（步骤 2：操作可复现性两问）

| 问题 | 判定 | 依据 |
|------|------|------|
| ① 博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是** | 四步转发路径（F-016）、zip 导入说明（F-038）、四组提示词原文（F-075~F-078）、首次配置说明（F-078/F-079） |
| ② 这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **否** | zip 获取方式仅在评论区置顶、正文无外链（F-039/F-040/F-099/F-100）；无 WorkBuddy / 微信 / skill 版本号（F-096）；无源码、脚本、去重算法、检索策略或渲染实现（F-098）；输出为图片且图片文字未转录（F-095）；无运行日志、无导出数据文件（F-097）；「三条硬规矩」内容缺失（F-073/F-074）；全网检索无公开仓库与许可证（F-120） |

**结论：任一为「否」→ 不设 `examples/`**。骨架为 `index.md + concepts/ + references/ + log.md`，共 10 个文件。`description` 显式标注「产品功能资讯与操作路径登记，非可复现实操教程／未在本机实跑」；根 index「已知边界」列出全部缺口。

> 提示词原文与四步路径作为 **F 编号事实**登记在 `references/article-source.md` 与 `concepts/03` 的「操作路径登记」段，但明确标为「原文照录，未经实机复现」，不伪装成演练示例。

## 5. 知识地图（I 阶段三层拆分）

按「技术综述 / 产品功能资讯」映射，四篇 concepts 递进：

| 层 | 篇目 | 承载内容 | 主要 F 编号 |
|----|------|---------|-----------|
| 事实时间线层（What/When/Who） | `concepts/00-official-entry-and-path.md` | 入口事实、四步路径、100 条上限与官方口径勘误、野路子对比、DMCA 下架事件、「不怕封号」证据边界 | F-013~F-033 / F-101~F-111 |
| 机制层 A（工作群日报） | `concepts/01-daily-report-skill.md` | 多次转发→时间线拼接与去重、脚本/模型/版式三层分工、选题雷达五信号、五种风格、实测数字证据等级 | F-042~F-059 / F-095~F-098 |
| 机制层 B（家族群辟谣） | `concepts/02-factcheck-card-skill.md` | 三条测试输入的权威核验对照、结论与依据分层、长图/单条卡输出分层、三条硬规矩缺口、关系洞察 | F-060~F-074 / F-112~F-118 |
| 模式与边界层（可迁移） | `concepts/03-transferable-patterns-and-boundaries.md` | 洞察四元组落地、五个可迁移模式（触发场景/核心步骤/反模式/迁移验证）、操作路径登记、可复现性与时效边界 | F-075~F-094 / F-099~F-120 |

`examples/`：无（理由见 §4）。`references/`：`article-source.md`（F 编号双份登记）、`verification.md`（P0 核验 + 勘误四清单）。

## 6. I 阶段洞察四元组（七概念质量门 G2）

| # | 陈述 | 证据 | 反常识 | 行动 |
|---|------|------|--------|------|
| 1 | 决定工作流能否长期运行的往往不是功能，而是**入口的合法性与稳定性** | F-024~F-030（旧方案心里不踏实、下架事件）、F-089/F-090（作者结论）、F-107~F-110（DMCA 直证） | 常见做法是先把功能做到最强；本文作者反而认为「门小、一次 100 条、要亲手推」是优点（F-033/F-088） | 设计自动化前先盘点数据入口的授权来源，把「入口断了怎么办」写进方案评审清单 |
| 2 | 把「一句话提示词」升级为 skill 的本质是**钉死流程**：确定性算数交给脚本、判断交给模型、呈现固定 | F-021/F-022、F-059（换风格只重出图不重分析）、F-080（配置沉淀） | 直觉认为模型越强越不需要固定流程；实际输出格式不稳定才是复用障碍 | 拆分「可计算 / 可判断 / 可呈现」三层，只对中间层用模型；风格切换做成只重渲染 |
| 3 | 辟谣类输出的说服力来自**可点名的权威依据**，而不是「AI 说这是谣言」 | F-068（三条依据）、F-069（「人民网说的」比「AI 说的」管用）、F-115（唯一逐字对应的一条）、F-117/F-118（另两条出处不符） | 通常把精力放在结论准确度；本文显示**引文出处写错**会直接削弱结论可用性 | 每条结论强制附可核验来源链接；并对引文做逐字核对，媒体名/栏目名不得凭印象写 |
| 4 | 面向不同受众要做**输出分层**，而非做一张「更全」的图 | F-070（长图给自己看、深红警示区、链接打码）、F-071（单条卡给群里）、F-072 | 常见倾向是把所有信息塞进一张长图；作者反而按「自己看 / 转发给长辈」拆成两种载体 | 先定受众与转发场景，再决定信息密度；高风险项固定置顶、原话链接自动打码 |
| 5 | 「官方入口」≠「官方免责」：标题的「不怕封号」是**因果跳跃** | F-030 vs F-108/F-111（腾讯回应对象是绕开加密的第三方项目；无免封号承诺） | 读者容易把「腾讯自己开的路」直接读成「腾讯保证不封号」 | 涉及账号安全的断言必须找到官方原文；找不到就标「作者推断」，`status: flagged` |
| 6 | 技术只能解决「知道」，关系仍要靠「说出口」 | F-091/F-092/F-093；作者建议把「建议这样回」「改两个字再发」 | 自动化目标是尽量少人工；本文主动保留一处人工改写 | 在自动化末环节显式留一个「人类语气」钩子，不要生成即发送 |

## 7. 质量门与验收

| 门 | 判据 | 落实位置 |
|----|------|---------|
| G1 事实 | 事实无因果推断词、纯客观描述、事实数 ≥20 | `facts.md` 120 条，V/S/K/H 分层 |
| G2 洞察 | 每条含 陈述/证据/反常识/行动 四元组 | 本 §6，6 条 |
| G3 模式 | 每个模式含 触发场景/核心步骤/反模式/迁移验证 | `concepts/03` §2，5 个模式 |
| G4 行动 | 行动项原子化、可勾选 | `concepts/03` §5 自查清单 |
| V 门 | 四视角全覆盖、意见 ≥5 条、至少采纳 2 条修正 | `log.md` V 阶段记录 |
| 机械门 | 双份 F 编号一致、toctree 完整、相对链接可达、计数三面一致、UTF-8 | `log.md` 门禁记录 |

## 8. 交付清单

**子模块 `projects/awesome-okf-xs`（10 个新文件）**

```
doc/bundles/jishu/ai/products/workbuddy-wechat-chat-forward-skills/
├── index.md
├── log.md
├── concepts/{index.md, 00-official-entry-and-path.md, 01-daily-report-skill.md,
│             02-factcheck-card-skill.md, 03-transferable-patterns-and-boundaries.md}
└── references/{index.md, article-source.md, verification.md}
```

**索引联动（写盘前重读现值，不凭记忆）**：`jishu/ai/products/index.md`（组束数 + 导航表 + toctree）、`jishu/ai/index.md`、`jishu/index.md`（递归引用，通常无需改数字）、`doc/bundles/index.md`（frontmatter + 正文 + 域节 + 分组表）、`README.md`、`doc/index.md`。

**主仓库**：本 `spec.md`、`facts.md`。

## 9. 并行会话协调

- 开工前 `git status` 显示工作树已有并行会话 WIP：`agent-autoloop`（frameworks/ai-agent）、`wechat-intelligence-hub`（products）、`ai-comic-drama-opc-transition`（sheke/industry）等，以及多个已修改的索引文件；基线计数已从 712 → 714 → **715**。
- 处置：**不修改、不回滚、不提交他人在途文件**；本束计数一律以写盘时重读的现值为准 `+1`。
- 基线门禁失败项：**开工时**为 `wechat-intelligence-hub` 缺 `index.md`（并行会话在途束）；C 阶段复跑时该束已由并行会话补齐 `index.md`，失败项转移为新在途束 `wechatbridge/`（9 篇文档不可达 + 缺 `index.md`）。两轮均按仓库惯例不修他方 WIP，仅在 `log.md` 区分「本束零失败」与「全仓既有失败」。

## 10. C 阶段执行记录（2026-11-06）

- **计数联动**：写盘前重读目录树地面真值 = `716 / jishu 525 / ai 289 / products 40`；同步 `doc/bundles/index.md`（frontmatter + 计数行 + mermaid + 域节 + 分组表 5 面）、`doc/index.md`、`README.md`、`jishu/index.md`、`jishu/ai/index.md`、`jishu/ai/products/index.md`（+ 导航表行 + toctree 条目）。另修正 README 一处历史遗留陈旧计数「171 束」→「289 束」。
- **门禁**：`check-bundles-index.py` ✅ 五面一致通过；`check-utf8.py` ✅ 12940 文件；`check-toctrees.py` 本束 0 命中（全仓 10 处均为并行 WIP `wechatbridge/`）；`check-asset-baseline.py` 规模数字零矛盾，仅 1 项提交前工作区字节残差告警；`check-section-anchors.py` 本束 0 命中。`invoke` 未安装，按 Skill §7 手动等效清单脚本直跑，未谎报 `gates.all`。
- **复核**：F-001~F-120 双份登记集合相等且连续；本束相对链接 0 断链；三级 toctree 9 条可达。
- **提交**：子模块 → 主仓库 spec → 子模块指针，显式文件清单 + UTF-8 中文提交通道，不 push，不触碰他会话文件。
- **交付状态**：R / I / E / V / C 全部完成；`status: flagged` 保留（E-1 无官方依据、E-2 不可验证），`stale_after: 2026-12-31`；建议约 2026-12-06 先做一轮轻量复核。
