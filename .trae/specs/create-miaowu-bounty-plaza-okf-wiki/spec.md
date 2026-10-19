# 秒悟应用赏金广场（AI Builder Growth 共创计划）OKF 教程束 - Product Requirements Document

## Overview

- **Summary**：以七概念方法论 R→I→E→V→C 全链路，对公开网页「秒悟应用赏金广场」（`https://ahhap1kka804.events.meoo.com/?spm=meoo.chat.0.0.18557976nUGkdG#/skills`）做源页全量采集与核验，在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/miaowu/` 下新增 1 个 OKF v0.2 知识束 `miaowu-bounty-plaza/`：把页面的计划定位、七阶段技能分类法与 25 条共创技能条目沉淀为可溯源、可机械比对的中文教程，并完成三级索引注册与总索引计数对账。
- **Purpose**：源页是秒悟（Meoo，阿里云云端 AI 应用创作平台）面向 AI Builder 的「应用赏金广场」——按「从 Vibe Coding 作品到真实收益」的增长链路，把 25 位创作者提交的 25 个 Skill 编排进七个阶段（找到需求/定义产品/讲清价值/优化体验/获取用户/持续增长/做好内容）。当前 `miaowu` 分组仅收录「大使入驻指南」与「实训案例」两束，尚无对「共创计划 / 技能广场」这一平台侧机制的系统化记录；本束补上该空白，并为「平台级 Skill 目录 → 阶段化增长方法论」建立一套可复用的知识组织范式（阶段分布与创作者归属全部机械可数）。
- **Target Users**：使用秒悟/Meoo 或同类 AI 应用创作平台的独立开发者与 AI Builder；关注「作品如何变成有人用的产品」的产品与增长从业者；研究大厂 AI 平台技能生态与创作者激励机制的行业观察者；需要辨析「平台技能广场」与「模型能力/CLI 工具」边界的读者。

## Goals

- 覆盖 `jishu/ai/ecosystems/miaowu` 分组既有 2 束未触及的空白主题：应用赏金广场与 AI Builder Growth 共创计划。
- 事实采集以源页为唯一主源（单源忠实登记）、以 `meoo.com/skills` 技能市场页与 `docs.meoo.com`、阿里云产品页/公开报道为次源做平台归属与环境核验；源页 25 条技能条目全量登记，不抽样。
- 建立「三面机械可比对」的自检：①技能条目数 = 25；②七阶段分布 = {找到需求 4, 定义产品 3, 讲清价值 5, 优化体验 2, 获取用户 3, 持续增长 3, 做好内容 5}；③创作者去重数 = 22（「空格的键盘」3 条、「一起Vibe」2 条为已知重复项）。
- 对源页未支撑的信息（赏金金额、结算规则、投稿审核流程、技能详情页正文等）**显式声明为缺口**，不推断、不加料。
- 结构与 frontmatter 对齐同分组既有束；通过 awesome-okf-xs 两大门禁（`check-bundles-index.py`、`check-toctrees.py`）、Sphinx dummy 构建与 UTF-8 门禁。
- 完成三级索引注册（分组 index → 分类 index → 域 index → bundles 总索引），总索引 5 面对账一致。

## Non-Goals

- 不执行任何 git commit / push（`projects/awesome-okf-xs` 为 git submodule，提交待用户显式指令）；不改动子模块内 `.agents/` 规范、`tasks/`、`scripts/`、`doc/conf.py`。
- 不修改 `miaowu` 分组既有两束（`miaowu-ambassador-guide`、`miaowu-meoo-practice-cases`）的内容。
- 不逐条抓取 25 个 Skill 的详情页正文（首轮仅登记广场层条目）；不逆向源页 SPA 的私有接口，不绕过任何登录/鉴权。
- 不新增静态图片资产（`doc/_static/`）——本轮保持纯文本知识束，不外链图片。
- 不做方法论模式库入库（`docs/retrospective/patterns/`）与 `.agents/` 主权区资产落盘；如需另行发起。
- 不生成 DOCX/PDF/HTML 形态产出物；不做「如何投稿/如何变现」的收益承诺或操作保证。
- 不评测、不背书、不排序任何具体 Skill 或创作者；不作商业推荐。

## Background & Context

- 用户 `/spec` 指令（2026-10-17）：`Use Skill: seven-concepts-cmd` 全面学习 `https://ahhap1kka804.events.meoo.com/?spm=meoo.chat.0.0.18557976nUGkdG#/skills`，在 `projects/awesome-okf-xs/doc/bundles` 恰当位置生成 okf wiki 教程。
- 内容敏感度预检（步骤 2.3）：源页为公开可访问网页（无 `share?code=`/`token=` 等访问控制参数，`spm` 仅为来源追踪）→ **公开内容** → 标准工作流；规划区 `.trae/specs/create-miaowu-bounty-plaza-okf-wiki/`，产出物入 `projects/awesome-okf-xs/doc/bundles/`。核验方式：一次抓取即返回完整正文（25 条条目），证明无需登录。
- 定位决策：新增束 `jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/`。理由——①`miaowu` 分组已存在且为「秒悟（Miaowu/Meoo）AI 平台」专组；②本主题主体是平台侧的技能市场/共创计划，归 `ecosystems`（厂商与开源社区生态）而非 `learning`（学习路径）或 `practice`（工程方法论）。
- 目录树既有布局：域（`jishu/index.md`）→ 分类（`jishu/ai/index.md`）→ 生态目录（`ecosystems/index.md`）→ 组（`ecosystems/miaowu/index.md`）→ 束（`miaowu/<bundle>/`）；束内含 `index.md`/`log.md`/`concepts/`/`references/`。
- 门禁机制：`scripts/check-bundles-index.py` 以目录树为地面真值，对总索引 7 项边对账（frontmatter 计数 / 正文计数行 / 域节标题 / 分组表束数列 / 表内链接可达 / 组注册覆盖 / 末尾 toctree）；`scripts/check-toctrees.py` 校验零断链、零孤立内容、目录文件清单一致性、bundle 根 `index.md` 完整。本轮新增束含 `concepts/` marker → 按「锚点束」计 1 束。
- **计数基线（R 阶段实测，2026-10-17）**：`doc/bundles/index.md` 现为 `total_bundles: 644` / `groups: 62` / `domains: 9`；`jishu` 节标题「475 束 · 18 组」；`ecosystems` 分类「94 束 · 16 目录」；`miaowu` 组 2 束。本变更 +1 束 → 644→645、jishu 475→476、ecosystems 94→95、`jishu/ai` 246→247、miaowu 2→3。
- 子模块边界：`projects/awesome-okf-xs/` 为第一方 git submodule，本轮直接在其工作树内写入 bundle 文件（与既往 okf-wiki 任务一致），但**不 commit**。

## Functional Requirements

- **FR-1**：新增束目录 `doc/bundles/jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/`，含 9 个 Markdown 文件：`index.md`、`log.md`、`concepts/index.md`、`concepts/00-intro.md`、`concepts/01-growth-stages.md`、`concepts/02-skills-catalog.md`、`references/index.md`、`references/source-ledger.md`、`references/verification.md`。
- **FR-2**：束根 `index.md` 含 `okf_version: "0.2"`、`type: bundle`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`（主源 = 源页 URL）；正文含本文概要、数据来源与单源声明、文档结构表、与 `miaowu` 分组既有两束及 `learning` 分类既有 Skills 束的主题关联、已知边界，并以 `{toctree}` 引 `concepts/index`、`references/index`、`log`。
- **FR-3**：`concepts/00-intro.md` 记录平台与计划定位——秒悟（Meoo）= 阿里云云端 AI 应用创作平台（次源核验）；源页标题「应用赏金广场」与副题「AI Builder Growth 共创计划：从 Vibe Coding 作品到真实收益」；页面对外表达「Meoo + Skill 帮你把想法变成有人用的『产品』」；三个对外入口（`meoo.com`、提交 Skill 参与共创计划、`meoo.com/skills` 查看更多技能）；页面形态特征（LIVE 计时、三位编号、阶段标签 + 标题@创作者 + 一句话说明）。
- **FR-4**：`concepts/01-growth-stages.md` 记录七阶段分类法——阶段名、页面顺序、每阶段目标一句话、该阶段收录条目数与占比、以及「从想法到有人用」的链路解读；明确标注阶段名与阶段顺序为源页原始口径。
- **FR-5**：`concepts/02-skills-catalog.md` 为 25 条技能全量清单（按页面编号 `01`–`025` 顺序，表格列：编号 / 阶段 / 技能名 / 创作者 / 源页一句话说明），附阶段分布统计表与创作者去重统计（22 位；重复项显式标注）。
- **FR-6**：`references/source-ledger.md` 登记 `F-001` 起编号事实（≥35 条：平台层 ≥6 条、页面层 ≥4 条、技能条目 25 条），每条标注来源类型（主源/次源）与 S 编号；文末含 `S1–Sn` 信源登记表（≥4 项：主源事件页 + `meoo.com/skills` + `docs.meoo.com` + 阿里云产品页/权威报道）与「放弃核验清单」。单源事实统一标注「单源（源页）」。
- **FR-7**：`references/verification.md` 为 P0 权威核验报告——至少核验：①平台归属（阿里云）②计划/广场命名 ③技能条目数与阶段分布 ④创作者去重数 ⑤页面公开可访问性；逐项给出 ✅/⚠️/❌ 与证据来源。
- **FR-8**：三级索引注册——`ecosystems/miaowu/index.md`（束列表 + `{toctree}`）、`ecosystems/index.md`（miaowu 行束数列 + 描述）、`jishu/ai/index.md`（分类计数 + ecosystems 行 + 描述）、`jishu/index.md`（ai 行计数）、`doc/bundles/index.md`（frontmatter / 计数行 / jishu 节标题 / ai 表行 / 生态概览 mermaid 中的 jishu 束数）；五处 toctree 链完整可解析。
- **FR-9**：`log.md` 与 `miaowu/log.md` 以 `YYYY-MM-DD` 倒序记录本次 R→V 全程。

## Non-Functional Requirements

- **NFR-1**：全束中文（平台名、Skill 名、创作者昵称、专有名词保留原文）；正文标题只用 `##` 起层级（H1 仅 frontmatter 后一处）；束内交叉引用优先使用 `/`-根路径（相对 bundle 根）；同目录清单/台账类文件（`concepts/index.md`、`references/index.md`）允许同级相对路径；无 `file:///`、无 `.temp/`/`.spec/` 引用。
- **NFR-2**：文件名与目录名 kebab-case 纯英文；无中文文件名。
- **NFR-3**：frontmatter 遵循 OKF v0.2——每个非保留 `.md` 含非空 `type`；`okf_version` 仅出现在束根 `index.md`；日期照常写裸格式（`doc/conf.py` 钩子自动加引号）。
- **NFR-4**：时效声明——事件页具临时性、技能清单与创作者归属易变，`stale_after` 设为 `2027-04-17`（约 6 个月），并在束内显式提示「平台收录与共创计划状态以 meoo.com 官方页面最新为准」。
- **NFR-5**：忠实度分层——凡源页未明示者（赏金金额、结算与分成规则、投稿审核流程、技能内部实现）一律标注为「源页未明示」或列入放弃核验清单，不得以推测补全。
- **NFR-6**：`.agents/` 未修改；除目标束目录与 6 处索引/日志文件外，不触碰其他文件。

## Acceptance Criteria

- **AC-1（rule）**：`doc/bundles/jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/` 下恰有 9 个 `.md` 文件（路径见 FR-1），每个非保留文件（非 `index.md`/`log.md`）均含非空 `type` frontmatter 字段。
- **AC-2（rule）**：`concepts/02-skills-catalog.md` 的技能条目表恰 25 行；阶段分布为 {找到需求 4, 定义产品 3, 讲清价值 5, 优化体验 2, 获取用户 3, 持续增长 3, 做好内容 5}；创作者去重计数为 22，且「空格的键盘」（3 条）与「一起Vibe」（2 条）的重复被显式标注。
- **AC-3（rule）**：`projects/awesome-okf-xs` 工作目录下运行 `python scripts/check-bundles-index.py` 退出码 0；六处计数同步到位：`miaowu` 组 2→3、`ecosystems` 94→95、`jishu/ai` 246→247、`jishu` 475→476、`doc/bundles/index.md` 的 `total_bundles` 644→645 且正文计数行 644→645。
- **AC-4（rule）**：`python scripts/check-toctrees.py` 退出码 0（零断链、零不可达内容、目录文件清单一致、bundle 根 `index.md` 完整）。
- **AC-5（rule）**：`python scripts/check-utf8.py` 通过；`sphinx-build -b dummy -E doc _build/dummy` 无 frontmatter 序列化报错。束根与各内容文档含 `sources`（主源为源页 URL）；`stale_after` ≤ `2027-04-30`。
- **AC-6（rubric）**：教程可读性与事实忠实度（1–5，阈值 ≥4）。维度：①阶段—技能映射无错配；②每条技能说明是对源页一句话的忠实中文改写（不虚构）；③缺口声明到位（源页未明示项未被补全）；④读者能沿「七阶段 → 25 技能」路径定位。

## Constraints

- **Technical**：Windows 环境；门禁脚本为 stdlib 单文件，须在 `projects/awesome-okf-xs` 工作目录下运行；Sphinx dummy 构建用于验证 frontmatter 兼容与 toctree 完整性；源页为 SPA（hash 路由 `#/skills`），抓取以渲染后正文为准，不以原始 HTML 空壳为准。
- **Business**：不 commit、不 push；不修改子模块内既有束；不背书具体 Skill/创作者；不承诺收益。
- **Dependencies**：`scripts/check-bundles-index.py`、`scripts/check-toctrees.py`、`scripts/check-utf8.py`、`doc/conf.py`；同分组既有束 `miaowu-ambassador-guide/`（结构参照）；`.agents/rules/frontmatter.md`（元数据规范）；子模块边界规范 `projects/AGENTS.md`。

## Assumptions

- 束名 `miaowu-bounty-plaza`、落位 `jishu/ai/ecosystems/miaowu/` 为本轮设计决策；如用户要求改名或改址，回到 Specify 重新对齐。
- 源页在实施期间内容稳定；若 R 阶段复抓发现条目增减，以实施时实测为准并更新 AC-2 的比对数字（不得静默沿用旧数）。
- 源页 25 条技能为「广场层条目」，其 Skill 详情正文不可从本页获得；首轮不抓详情页，列为知识缺口。
- 平台归属（阿里云）可由 `docs.meoo.com` 与公开报道双源核验；共创计划的官方规则/条款页面若不可达，则以「源页单源 + 缺口声明」处理并标 ⚠️。
