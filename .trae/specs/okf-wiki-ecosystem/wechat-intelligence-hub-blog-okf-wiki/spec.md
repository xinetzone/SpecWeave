---
okf_version: "0.2"
type: spec
title: "WeChat Intelligence Hub 博文 → OKF v0.2 wiki 教程"
source: "https://mp.weixin.qq.com/s/LNyKE5lex4qBOmIS4Z-7sg"
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-11-06T11:48:00+08:00" }
---

# Spec：微信博文 → OKF v0.2 知识包

## 0. 任务与场景识别

- **用户输入**：`/七概念 全面学习 https://mp.weixin.qq.com/s/LNyKE5lex4qBOmIS4Z-7sg，生成 okf wiki 教程到 D:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles 的恰当位置`
- **命令解析**：`/七概念` 是仓库斜杠别名 → `.agents/commands/seven-concepts.md`（L2 指令）+ `.agents/skills/seven-concepts-cmd/SKILL.md`（L1 门面）；非运行时 Skill 名。
- **场景**：场景 4「知识沉淀/方法论」，链路 **R→I→E→V→入库**；由 `.agents/skills/blog-article-to-okf-wiki/SKILL.md` 七阶段工作流承载，质量门 G1（事实）→ G2（骨架/归属）→ G3（信源先行）→ G4（对抗审查+机械门禁）。
- **产出边界**：用户显式指定 `projects/awesome-okf-xs/doc/bundles/`；该子项目 `AGENTS.md` 规定结构化知识包入 `doc/bundles/`，与根 `AGENTS.md` 的「根目录 docs/ 为唯一文档中心」不冲突——本产物是子项目内部资产，不是 SpecWeave 根级文档。

## 1. 内容敏感度预检

| 判据 | 结果 |
|------|------|
| URL 形态 | `mp.weixin.qq.com/s/<id>` 公开文章 |
| `share?code=` / `token=` / 邀请码 / 企业内部域名 | 均无 |
| 判定 | **Public** |
| 工作流 | 标准 Spec Mode：spec 在 `.trae/specs/okf-wiki-ecosystem/<name>/`，产出在子项目 `doc/bundles/` |
| 排除 | 不进 `playground/`，不触发私域就高不就低条款 |

> 注：Skill Gotcha 记载 `mp.weixin.qq.com` 反爬确定、应直接用 `browser_use` 取 `#js_content`；**本次 WebFetch 直接返回完整正文与元信息，未触发回退**。此为流程偏差但无内容损失，已在 `log.md` 登记。

## 2. 骨架判定（L3 操作可复现性两问）

| 问题 | 判定 | 依据 |
|------|------|------|
| Q1 是否有读者可照做的流程？ | **博文层：否**；官方 README 层：是 | 博文全文无一条安装/运行命令、无版本号、无步骤顺序；官方 README 另有 install.sh / run_demo.sh / profile-init / Codex 示例 |
| Q2 是否经作者实测且具备版本/输入/输出/步骤顺序？ | **否** | 博文明确「全虚构 Demo」「macOS 新机器的获取路径官方还没实测」；产出物为官方效果截图与图注，无真实数据的输入输出对照 |

**结论**：任一为否 → **概念骨架（无 `examples/`）**。官方命令作为「路径说明」写入 `concepts/04`，并显式标注「来自官方 README、本知识包未实机验证」，不得包装成实战示例。已创建目录仅 `concepts/` + `references/`，与此判定一致。

## 3. 归属决策树

1. **主线实体**：WeChat Intelligence Hub —— 一个具体的本地优先终端工具/产品（非方法论、非行业洞察）。
2. **查先例**：`jishu/ai/products/` 已有 `wigolo`、`open-code-review`、`agent-reach`、`inkos`、`skills-manager`、`vidbee`、`creatorhub` 等「微信博文 → 官方核验 → 产品束」先例。
3. **单篇博文禁止新建分组**：不新建 `wechat/` 之类分组。
4. **排除 `practice/`**：该组定位为工程实践/方法论/行业洞察；本束主体是产品。
5. **最终路径**：`doc/bundles/jishu/ai/products/wechat-intelligence-hub/`（目录名 kebab-case 纯英文，正文中文）。

## 4. 时效性与信源距离

- 博文发文 **2026-09-24 07:02**（北京），核验日 **2026-11-06**，间隔约 43 天；Star 等动态数字必须带时点。
- 信源距离分层：
  - 博文一手（标题/元信息/图注/作者观点）：F-001~F-004、F-007~F-008、F-037~F-040 等；
  - 官方截图经博文转述（UI 标签、视图风格）：F-011~F-013、F-016~F-018；
  - 第三方推介转述（能力与安全声明）：F-005~F-010、F-019~F-036；
  - **官方一手核验**（GitHub REST API + main 分支 README）：F-041~F-057。
- 判定：博文能力清单大体可在官方 README 找到语义对应，但**具体 UI 命名与「四种视图」仅有截图图注单源**；这些内容在 bundle 中一律标注「博文/图注单源，官方未逐字核验」。

## 5. P0 权威核验清单（22 项：14✅ / 8⚠️ / 0❌）

见 `references/verification.md`。核心结论：

- ✅ 仓库真实存在且主线归属为 `Rion-Wu-tech/wechat-intelligence-hub`；Python、AGPL-3.0、只读边界、全虚构 Demo、Codex 自然语言调用、双格式报告、隐私条款均获官方印证。
- ⚠️ 8 项分三类：① 动态时点/成效数字（星标 1976/2000 → 2764、「5 天」无 star 时序数据）；② 口径范围（「不重签名」仅约束 Reader 核心）；③ UI 层单源（四入口名称、四视图、移动端、回复草稿、定向检索五维度）。
- ❌ 0 项：无核心声明被证伪 → `status: stable`，但标题 hook「5 天攒 2000 星」须在正文显著标注「未独立核验」。

**关键口径风险（必须在正文落实）**：

1. API `created_at=2026-09-04`，发文 `2026-09-24`，相隔约 20 天——**不得把「5 天」写成「仓库创建后 5 天」**；只能表述为「博文口径的星标增长窗口，未独立核验」。
2. 「不重签名」不可泛化到整个项目：官方 README 说明 macOS 候选接入工具可能重启微信、重签名副本，Windows 首次获取尚未合入。
3. README 精确写 `AGPL-3.0-only` 且闭源/OEM/白标需商业授权；API 仅给 `AGPL-3.0`。

## 6. 三层知识拆分

| 层 | 文件 | 职责 |
|----|------|------|
| references/ | `article-source.md`（F-001~F-057 博文事实清单）、`verification.md`（P0 核验报告 + 勘误四张清单） | 信源先行，先于 concepts 落盘 |
| concepts/ | `00` 项目身份与热度时点；`01` 本地优先只读架构与两个 Skill；`02` 旗舰日报与四种视图；`03` 定向检索/重点联系人/行动项；`04` 官方命令路径与全虚构 Demo 差距；`05` 洞察、可迁移模式与采用边界 | 概念化 + I 阶段洞察 + E 阶段模式萃取 |
| 根 | `index.md`（唯一含 `okf_version` 的 bundle 根）、`log.md` | 导航与变更/门禁记录 |

## 7. ADDED Requirements

- **R-1**：全部数字、命令、版本、许可证、日期携带 F 编号；不得出现 facts.md 之外的具体声明。
- **R-2**：`facts.md` 与 `references/article-source.md` 的 F 编号集合相等、连续无跳号（F-001~F-057）。
- **R-3**：勘误四张清单（日期/版本、成效数字溯源、口径对照、引文逐字）齐全，8 项 ⚠️ 逐项在正文有对应表述。
- **R-4**：四级索引接入——`products/index.md`（38→39，导航行 + toctree）、`ai/index.md`（287→288）、`jishu/index.md`（287→288 描述）、`bundles/index.md`（714→715、jishu 523→524、ai 287→288、mermaid、节标题、表行、计数行、frontmatter）；另同步子模块 `README.md` 与 `doc/index.md` 的规模数字。
- **R-5**：所有 `index.md` 含 `{toctree}`；toctree 指令行（以 `:` 开头）不计入条目；相对链接可达，禁止 `file:///` 绝对路径。
- **R-6**：`okf_version: "0.2"` 仅出现在 bundle 根 `index.md` 与总索引类文件；其余文档只用 `type` 等字段。
- **R-7**：机械门禁 `check-bundles-index.py`、`check-toctrees.py`、`check-utf8.py`、`check-asset-baseline.py` 全部 exit 0。
- **R-8**：C 阶段按用户「提交」指令执行**本地原子提交**（不 push）；提交范围严格限于本任务，登记于 `log.md`。

## 8. 提交顺序（C 阶段，已执行）

用户追加「提交」指令后，按原子提交「单一职责」原则收尾，实际顺序如下：

① 子模块 `projects/awesome-okf-xs`：**单独提交** `doc/bundles/jishu/ai/products/wechat-intelligence-hub/log.md`（V 阶段门禁结果与规模 10→12 的修正）——bundle 12 文件与四级索引早已由并行会话在 `12efe455` / `e9190519` 收录，不重复提交。
② 主仓库：提交本 spec 目录四件（`spec.md` / `facts.md` / `tasks.md` / `review.md`）。
③ 主仓库：单独一笔 `chore(submodule)` 把 `projects/awesome-okf-xs` 的 gitlink 更新为 ① 产生的新 HEAD（与仓库最近 `docs(spec)` + `chore(submodule)` 分离惯例一致）。共三笔本地提交。

**排除范围**（并行会话在途、非本任务，均未纳入）：主仓库的 `agent-autoloop-blog-okf-wiki/`、`wechatbridge-ios-relay-blog-okf-wiki/`、`wechatbridge-okf-wiki/` 三个 spec 目录；子模块的 `products/wechatbridge/`、`products/wechatbridge-ios-relay/`、`sheke/industry/ai-comic-drama-opc-transition/` 改动及 716→718 计数更新。

**未执行**：`git push`（推送由用户决定）。
