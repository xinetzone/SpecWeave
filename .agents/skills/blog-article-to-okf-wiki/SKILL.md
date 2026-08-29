---
name: blog-article-to-okf-wiki
version: 1.0.0
description: "当用户提供博文/资讯类文章 URL（微信公众号文章、技术博客、新闻稿、产品发布资讯、行业分析文章）并要求转化为 OKF 知识包/知识 bundle/Wiki 教程时，必须使用此技能。触发词：'博文转化'、'公众号文章'、'微信文章'、'这篇文章转成'、'转知识包'、'OKF bundle'、'OKF wiki'、'文章转文档'、'资讯转知识库'、'按同样模式转化'。提供七阶段工作流：敏感度预检→骨架判定（操作可复现性两问）→归属决策树→F编号事实采集+P0权威核验（勘误四张清单）→三层知识拆分→信源先行生成bundle→对抗审查与索引收尾。经13篇异质博文（7类内容形态）实战验证：492条事实登记、90项P0核验、拦截4项源文硬错误。杜绝无信源转述、源文错误静默照搬、营销数据污染、假核验四大问题。不要直接让AI读文章写知识包——本Skill封装了信源距离预判、厂商自宣成效数字必核验、status:flagged失败管理、双份F编号一致性核对等防护机制。信源是本地源码目录时改用 source-code-to-okf-wiki 技能。"
argument-hint: "<文章URL> [输出bundle分组]"
user-invocable: true
paths:
  - ".agents/skills/blog-article-to-okf-wiki/**"
  - ".agents/docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md"
title: "博文/资讯文章→OKF 知识包转化工作流 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/blog-article-to-okf-wiki/SKILL.toml"
---
# 博文/资讯文章→OKF 知识包转化工作流 Skill

> ⚠️ **本Skill是知识沉淀工作流门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+七阶段流程+质量门+安全清单+反模式）
> - L2：[博文类文章→OKF知识包转化模式（L3完整方法论）](../../docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md)（判据细节、demo 逐步对照、案例迁移记录）
>
> **术语速查**：OKF（Open Knowledge Format，开放知识格式，v0.2）；bundle（知识包，OKF 最小交付单元）；toctree（Sphinx 导航指令块，CI 门禁沿它做 BFS 导航）；P0（必核验级声明：数字/日期/官方表态/成效数字）；flagged（核心声明核验失败的 bundle 状态标记）；F 编号（事实登记编号，F-001 起）。

## 1. Skill ID
`blog-article-to-okf-wiki`

## 2. 功能描述

将单篇博文/资讯类文章（外部 URL）转化为结构化、可溯源、带时效管理的 OKF v0.2 知识包，采用七阶段工作流：

| 阶段 | 核心动作 | 关键产出 | 质量门 |
|------|---------|---------|--------|
| **0. 预检** | 内容敏感度判定（公开/私域） | 工作流分流结论 | 私域内容禁入公共 specs 区 |
| **R** | 信源获取 + F 编号事实采集 + P0 权威核验 | spec `facts.md` + 核验记录 | G1：事实无推断词；P0 逐项过勘误四张清单 |
| **I** | 骨架判定 + 三层知识拆分 | 知识地图（concepts/examples 篇目） | 操作可复现性两问决定 examples/ 取舍 |
| **E** | 信源先行生成 bundle | references/ → concepts/ → examples/ → index | G3：信源先行、F 编号引用、index 最后写 |
| **V** | 四视角对抗审查 + 机械门禁 + 索引收尾 | verification.md + log.md + 三级索引接入 | G4：双份 F 编号一致、计数同步、链接可达 |
| **C** | 原子提交（子模块→主仓库） | 两仓库提交记录 | 显式文件列表、不 push |

核心防护机制：信源距离五分类预判、厂商自宣成效数字默认 P0、勘误四张清单、源文错误不静默照搬、`status: flagged` 失败管理、双份 F 编号一致性核对。

> **为什么不能直接让AI"读文章写知识包"？** 博文类信源有四大固有风险——作者观点与事实交织（观点被固化为"官方结论"）、营销叙事数据（提效倍数无独立出处）、时效性信息快速过期（价格/版本/GA 日期）、源文本身含硬错误（13 篇实战拦截 4 项：年份错配、GA 日期误植、无证据的产品声明、归因失实的效率数据）。直接改写等于把这些风险原样固化进知识库。本 Skill 的 R 阶段强制"先核验后入库"、V 阶段强制机械门禁，从流程上拦截。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- 提供博文/文章 URL（微信公众号 `mp.weixin.qq.com`、技术博客、新闻稿、官方公告）并要求"转化/整理/沉淀/做成知识包/写进 wiki"
- "博文转化"、"公众号文章"、"这篇文章转成"、"转知识包"、"OKF bundle"、"OKF wiki"、"文章转文档"、"资讯转知识库"
- 上下文中已有博文转化先例时的"按同样模式（处理这篇）"

> **关于触发**：即使没有明确说"用 OKF 工作流"，只要意图是"把一篇外部文章系统性沉淀为可溯源知识库条目"，就应使用本 Skill。

## 4. 适用性决策树

```
用户提供了文章/内容并希望沉淀为知识库文档？
├─ 信源是本地源码目录/要读源码？ → ❌ 改用 source-code-to-okf-wiki 技能（Grep 源码验证，非 WebSearch）
├─ 只是快速总结/翻译/摘要一篇文章？ → ❌ 不适用（直接回答，七阶段过度工程）
├─ 写一篇原创文章/单文件笔记，无溯源要求？ → ❌ 不适用
├─ URL 含 share?code=/token=/邀请码，或企业内部域名？ → ⚠️ 私域工作流（跳过 .trae/specs/，产出放 playground/ 或用户指定目录）
├─ 非 URL 的本地文档（PDF/Word/Markdown 批量）？ → ⚠️ 边界场景（参考批量文档转换模式，见§11）
└─ 公开博文/资讯 URL → 可溯源 OKF 知识包？ → ✅ 适用，执行七阶段工作流
```

> **为什么首问"信源是 URL 还是本地源码"？** 本 Skill 与 [source-code-to-okf-wiki](../source-code-to-okf-wiki/SKILL.md) 共享 R→I→E→V→C 链路与 OKF 规范，但核验手段根本不同：博文类事实靠 WebSearch 权威交叉核验（源码不在本地），源码类靠 Grep 验证 API 存在性（WebSearch 查不到本地代码）。误触发会在第一步就失败。

## 5. 核心步骤（七阶段工作流）

> 以下为步骤骨架与判据；**完整规则、demo 逐步对照、13 案例迁移记录以 [L2 模式文档](../../docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md) 为准**。

### 步骤1：内容敏感度预检
- 公开内容（无访问控制的公开博文/博客/新闻页）→ 标准工作流：spec 在 `.trae/specs/<theme>-okf-wiki/`，产出在 `projects/awesome-okf-xs/doc/bundles/`
- 私域内容（含 code/token/邀请码、内部域名）→ 私域工作流：跳过公共 specs 区，产出放 `playground/` 对应用户目录
- 不确定时默认按私域处理或向用户确认

### 步骤2：骨架判定（操作可复现性两问）
1. 博文中是否有读者可照做的安装/配置/代码/调用/实测流程？
2. 这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？

**两问皆"是" → 设 `examples/`；任一为"否" → 无论主题多技术都不设**（空 examples/ 制造伪结构比没有更糟；正例：threeui 开源组件盘点、a2a-mcp 协议综述均为硬核技术但正确地无 examples/）。

| 内容性质 | 目录骨架 | 备注 |
|---------|---------|------|
| 技术教程/选型 | index + concepts/ + **examples/** + references/ + log | 含可复现操作 |
| 技术综述/资讯盘点 | index + concepts/ + references/ + log | description 标注"非操作教程" |
| 商业分析/战略资讯 | index + concepts/ + references/ + log | description 标注"非源码教程" |
| 资讯速报 | index + references/ + log（concepts 可仅 1 篇） | `stale_after` 缩短至 1-2 月 |

### 步骤3：归属判定决策树
1. **主线实体优先**：文章围绕哪个实体展开就落哪个分组；"A+B 协作"类以承担核心角色的实体为锚点
2. **查先例**：目标分组已有非源码类 bundle（资源列表/应用模型/资讯）证明可容纳
3. **单篇博文禁止新建分组**（过度工程，违反最小变更）
4. 主线不明时在 spec 中列"候选位置 | 判定 | 理由"对照表论证

### 步骤4：事实采集与核验（R 阶段）
- **信源获取**：微信公众号文章 WebFetch 被反爬拦截 → 直接用 browser_use 子代理提取全文（JS 取 `#js_content` innerText）；其他站点优先 WebFetch/Defuddle，失败回退 browser_use；全部失败时请用户提供正文/截图
- **F-001 起编号**登记到 spec `facts.md`；作者观点显式标注"作者观点"；外媒转述标注转述层级
- **信源距离预判**（核验前必做）：官方发布 / 作者一手实测 / 开源项目文档 / 第三方综述 / **厂商自宣**。厂商自宣类的**所有成效数字（提效倍数/节省工时/成本下降）默认 P0 必核验**，bundle index 顶部加"厂商自述数据"提示块
- **P0 必核验**（WebSearch 权威来源）：数字/金额/日期、官方表态、产品发布与功能时间线、成效数字；P1 选核验：能力声明/市场份额；P2 可单源：背景叙述/个人观点
- **勘误四张清单**（P0 逐项过筛；13 篇 25+ 项问题全部收敛于此四类）：
  ① **日期/版本表**：GA/发布日期、模型版本号、年份归属对官方源
  ② **成效数字溯源表**：提效倍数/工时节省须找到原始出处，无出处即 ❌
  ③ **口径对照表**：规模数字核对地域/时间/统计口径限定词，警惕拔高与省略
  ④ **引文逐字核对表**：官方定位/高管引语核对原文（意译不得加引号）；报告须查发布方身份（厂商赞助须披露）
- **源文错误不静默照搬**：新增 F 编号记录正确值与差异，verification.md 单列"勘误"，正文呈现正确值并标注源文口径；无法核验标注"仅博文单源"

### 步骤5：三层知识拆分（I 阶段）
- 技术教程/选型类：发布事实层 → concepts 首篇；选型矩阵/方法论层 → 中部；架构模式层 → 尾篇；可演练内容 → examples/
- 商业分析/技术综述类：事件时间线层（What/When/Who）→ 首篇；驱动逻辑/机制原理层（Why，因果分析属作者洞察须与事实分层）→ 中部；竞争格局/生态趋势层 → 尾篇；Mermaid 图可入 concepts

### 步骤6：bundle 生成（E 阶段）
1. **信源先行**：先写 references/（article-source.md 博文事实清单 + verification.md 核验报告），再写 concepts/、examples/，**各级 index.md 最后写**
2. **所有具体声明引用 F 编号**：数字/模型名/API/组织变动必须有 F 出处，禁止 facts.md 之外的编造；伪代码/推导显著标注"非官方"
3. frontmatter 遵循 OKF v0.2，`sources` 同时列出博文 URL 与核验权威 URL；`stale_after` 按性质设定（资讯速报 1-2 月，其余至年末）
4. **flagged 状态管理**：P0 出现 ❌ 且失败项为博文**核心声明**（主结论/主推事实）→ frontmatter `status: flagged` + verification.md 顶部明示 + index 已知边界提示 + stale_after 前安排复核；非核心声明失败可 stable 但勘误必须完整
5. **同主题多 bundle 互链**：各 bundle index.md 增加"主题关联"段，两两互链并说明分工（正例：豆包工作主题簇 3 bundle）

### 步骤7：对抗审查与索引收尾（V 阶段）
1. 四视角审查内容文档：事实溯源（无 F 之外的数字/模型名，勘误在正文落实）、结构规范、读者可用性（相对链接逐一可达）、时效边界（单源/价格时点/观点分层）
2. **双份 F 编号一致性核对**：正则提取 spec `facts.md` 与 bundle `references/article-source.md` 两边编号集合比对——须连续无跳号（跳号须显式注记）；V 阶段补充事实不回转 article-source 时须在 log.md 注记原因
3. **父级分组 index 接入**：导航表加行 + toctree 追加 + 束数计数；非源码教程类若板块语义不符则新增分类（如"📰 战略资讯"）
4. **全库计数同步**：`bundles/index.md` 的 total_bundles/域束数/组束数与正文计数三处一致
5. **门禁**：依赖可用时 `invoke gates.toctrees` / `invoke gates.utf8`（需先 `pip install -e ".[doc]"`）；**依赖不可用时禁止声称"gates 通过"**，必须执行§7 手动等效验证清单并在 log.md 注明

## 6. OKF Bundle 规范速查

### 6.1 目录结构
```
<bundle-name>/
├── index.md              # 根索引（okf_version frontmatter + toctree）
├── log.md                # 变更日志
├── concepts/             # 概念文档
│   ├── index.md          # 无 frontmatter，必须含 toctree 块
│   └── 00-xxx.md ~ NN-xxx.md
├── examples/             # 示例文档（仅步骤2两问皆"是"时设立）
│   ├── index.md          # 必须含 toctree 块
│   └── ...
└── references/           # 信源登记（信源先行，最先生成）
    ├── index.md          # 必须含 toctree 块
    ├── article-source.md # 博文事实清单（F 编号双份登记之一）
    └── verification.md   # P0 核验报告（含勘误）
```

### 6.2 Frontmatter 必填字段
```yaml
---
okf_version: "0.2"
type: bundle            # 子文档为 Concept/Example/Reference
title: <标题>
description: <30-80字>
tags: [<标签>]
generated: { by: <生成者标识>, at: <ISO8601> }
verified: { by: "process:seven-concepts-v", at: <ISO8601> }
status: <draft|stable|flagged|deprecated>
stale_after: <YYYY-MM-DD>
sources:
  - id: <信源ID>
    resource: /references/<source-file>.md   # 内部信源
  - id: blog
    url: <博文 URL>                          # 外部博文
  - id: official-<n>
    url: <核验权威 URL>                      # 外部权威信源
---
```

### 6.3 toctree 规范（每个 index.md 必含）
````markdown
```{toctree}
:hidden:
:maxdepth: 2

00-first-doc
01-second-doc
```
````
- 根 index.md toctree 收录 `concepts/index`、`examples/index`（如有）、`references/index`、`log`
- 子目录 index.md 收录本目录全部内容文件（stem 形式，按文件名排序）
- 分组 index.md 收录各束 `<bundle>/index`
- **计数时排除 `:` 开头的指令行**（`:hidden:`/`:maxdepth:`），只数条目行
- toctree 与人类可读表格链接**并存**——表格给读者，toctree 给 Sphinx/CI

> **为什么表格链接不能替代 toctree？** CI 质量门从 `doc/index.md` 沿 toctree 指令块做 BFS 导航，子目录 index 缺 toctree 块即导航断头，其下全部内容被判"未收录(不可达)"——即使表格链接完好。

## 7. 安全检查清单（V 阶段逐项打勾）

**机械门禁（依赖不可用时的手动等效验证，逐项执行）：**

- [ ] **UTF-8 严格 roundtrip**：用 `[System.Text.UTF8Encoding]::new($false,$false)`（strict）解码全部新增/修改 .md 文件，无乱码
- [ ] **双份 F 编号一致**：正则 `^\|\s*F-(\d{3})\s*\|` 分别提取 facts.md 与 article-source.md 表行编号，两集合相等且连续（跳号有注记）
- [ ] **三级 toctree 完整**：每个 index.md 含 toctree 块；条目（排除 `:` 指令行）逐一 Test-Path 对应文件存在；组索引 frontmatter `total_bundles` = toctree 条目数 = 实际 bundle 目录数
- [ ] **相对链接全可达**：Grep 全部 .md 的 Markdown 链接，相对路径逐一 Test-Path；`file:///` 绝对路径零出现
- [ ] **三级计数同步**：bundles/index.md 的 total_bundles、域束数、组束数与正文数字一致
- [ ] **敏感信息零残留**：`/Users/`、`C:\Users\`、家目录绝对路径等零出现（用 `~/` 替代）
- [ ] **frontmatter 完整**：okf_version/type/title/description/tags/generated/verified/status/stale_after/sources 齐备；sources 含博文 + 核验权威双信源
- [ ] **勘误落实**：verification.md 中 ❌/⚠️ 项在 bundle 正文呈现的是正确值（非源文错误数字），flagged bundle 有顶部明示

**幂等与提交规范（C 阶段）：**

- [ ] **重跑幂等**：开工前先查目标 bundle 目录与 spec 目录是否已存在——已存在时先读其 log.md/index.md，判定为"更新/补核验"还是"重建"，禁止静默覆盖既有文件；索引计数先读现值再 +1，不凭记忆写数字
- [ ] **提交顺序**：① 子模块 `projects/awesome-okf-xs` 内先提交（bundle 文件 + 组 index + bundles/index.md）→ ② 主仓库提交 spec（`.trae/specs/`）→ ③ 主仓库更新子模块指针
- [ ] 使用 [git-commit-utf8.py](../../scripts/git-commit-utf8.py) 提交（UTF-8 中文通道）：`python .agents\scripts\git-commit-utf8.py -m "type(scope): 中文描述" <显式文件1> <显式文件2>...`——**必须显式列全文件，传目录参数会失败**
- [ ] 遵循 Conventional Commits（`docs(ai-agent): ...`）；用户未要求时不 push

> **为什么 V 阶段机械检查是"必须"而非"建议"？** 13 篇实战的全部已记录瑕疵（F 编号跳号、双份登记 460 vs 458 漂移、toctree 计数误报、跨 bundle 相对路径少一层、文件计数重复计入 index.md）都发生在收尾环节，且每一项都能被上述正则/脚本拦截——agent 知道规则不等于执行中不漏项，清单打勾是把"记得检查"变成"强制检查"。

## 8. 早期预警信号

| 预警信号 | 可能问题 | 行动 |
|---------|---------|------|
| 想给技术综述/资讯盘点建 examples/ | 违反两问判据 | 回到步骤2，两问皆"是"才设 |
| 成效数字找不到独立出处 | 厂商自宣营销数据 | 标"厂商/客户自述"，P0 核验；核心声明无证据 → flagged |
| WebSearch 不到官方来源想硬编 URL | 假核验 | 禁止；标注"仅博文单源" |
| 核验发现源文错误但正文已照抄 | 错误固化进知识库 | 新增 F 编号记正确值，verification 单列勘误，正文改正确值 |
| 想为单篇博文新建顶级分组 | 过度工程 | 落既有分组，主线不明列候选对照表 |
| facts.md 与 article-source.md 编号数不等 | 双份登记漂移 | 正则比对集合，回转或 log 注记 |
| 微信文章 WebFetch 返回空/拦截页 | 反爬 | 改用 browser_use 取 `#js_content` |
| 子目录 index.md 只有表格无 toctree | CI 导航断头 | 按§6.3 追加隐藏 toctree 块 |
| 准备声称"gates 通过"但没跑 invoke | 环境缺依赖 | 执行§7 手动等效清单并在 log 注明，禁止谎报 |

## 9. 反模式速查（13 个致命错误）

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 无信源转述（博文观点当事实写） | 个人判断固化为"官方结论" | 全部声明登记 F 编号，观点标"作者观点" |
| 2 | 忽视时效性（不设 stale_after） | 过期价格/版本误导决策 | 设 stale_after + 已知边界声明价格时点 |
| 3 | 单篇博文新建分组 | 目录体系碎片化 | 落既有分组，bundle 承载单篇内容 |
| 4 | 核验不过硬编官方 URL | 假核验，可信度虚假升级 | WebSearch 确认后才补信源，否则标单源 |
| 5 | 伪代码不标注非官方 | 读者误当官方 API | 文内显著标注"非官方" |
| 6 | 不跑 gates 也不做等效验证就声称通过 | 孤立文档/断链静默存在 | 跑 invoke gates 或执行§7 手动清单并 log 注明 |
| 7 | 私域内容进公共 specs 区 | 访问控制内容泄露 | 私域链接走 playground 工作流 |
| 8 | 商业分析类硬塞 examples/ | 空目录制造伪结构 | 按两问判据，无 examples 并在分组 index 新增匹配分类 |
| 9 | 核验发现源文错误却静默照搬 | 知识库可信度低于源文 | 新 F 编号记正确值 + verification 勘误 + 正文标注源文口径 |
| 10 | 微信文章直接 WebFetch | 反爬返回空/拦截页 | 直接用 browser_use 子代理 |
| 11 | 厂商自宣成效数字不标"自述"即入库 | 营销数据污染知识库 | 信源距离预判 + P0 溯源 + 正文标"厂商/客户自述" + index 提示块 |
| 12 | 技术主题想当然设 examples/ | 伪示例制造结构噪声 | 操作可复现性两问为唯一判据 |
| 13 | 核心声明核验失败仍发 stable | 下游无法识别可信度 | `status: flagged` + verification 顶部明示 + 到期前复核 |

## 10. Gotchas（陷阱与反直觉行为）

- **微信反爬是确定的，不是偶发**：`mp.weixin.qq.com` 对 WebFetch 13/13 拦截，不要先试 WebFetch 浪费轮次，直接 browser_use；提取后核对正文长度（千字文 <500 字说明取错节点）。
- **invoke gates 依赖不默认安装**：`invocations` 在 `pyproject.toml` 的 optional-dependencies.doc 中，环境缺该包时 `invoke gates.*` 报 ModuleNotFoundError——此时手动等效验证（§7）是**规定的替代路径**，但必须在 log.md 注明，禁止谎报"gates 通过"。
- **toctree 计数别把指令行算进去**：`:hidden:`/`:maxdepth: 2` 以 `:` 开头，正则计数时必须排除，否则组索引束数虚高（实战中曾误报 31 vs 实际 29）。
- **产出在 git submodule 里**：bundle 位于 `projects/awesome-okf-xs/`（git submodule），spec 位于主仓库 `.trae/specs/`。提交顺序：子模块内先提交 → 主仓库提交 spec → 主仓库更新子模块指针；子模块内 `doc/bundles/` 的组 index 与总 index 改动也属于子模块提交。
- **git-commit-utf8.py 不接受目录参数**：工具按显式文件列表校验暂存区，传目录会报"git add后暂存区文件与指定列表不一致"；必须逐个列出全部 .md 文件。
- **跨 bundle 相对链接注意深度**：从 `<bundle>/concepts/` 引用兄弟 bundle 是 `../../<sibling-bundle>/index.md`（两级上跳），引用本 bundle 内文档用 `/concepts/xx.md`（bundle-relative，`/` 开头）。
- **R→E 事实遵循度衰减**：E 阶段距 R 阶段已隔多轮对话，生成 concepts 时须在 prompt 中显式附相关 F 编号，不确定时回查 facts.md，禁止凭印象写数字。
- **核验子代理要独立上下文**：P0 核验委派 general_purpose_task 时，每个子任务需独立给出完整待核验声明清单（声明内容 + 博文口径 + 要求官方源），不能假设共享主会话上下文。

## 11. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| **博文转化模式（完整方法论 L3）** | **L2** | [blog-article-to-okf-bundle.md](../../docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md) | **首次使用必读**——7 步骤完整判据、2 个 demo 逐步对照、13 案例迁移记录、勘误四清单详解 |
| 12 篇批量转化里程碑复盘 | L2 | [blog-to-okf-bundle-12posts-milestone-retrospective-20260829.md](../../docs/retrospective/reports/concepts/milestone/blog-to-okf-bundle-12posts-milestone-retrospective-20260829.md) | 勘误四模式萃取过程、30 条事实、4 条洞察 |
| 源码→OKF Wiki（姊妹 Skill） | L1 | [source-code-to-okf-wiki/SKILL.md](../source-code-to-okf-wiki/SKILL.md) | 信源为本地源码目录时改用；OKF 结构规范两 Skill 一致 |
| 方法论编排 | L1 | [seven-concepts-cmd/SKILL.md](../seven-concepts-cmd/SKILL.md) | 需要 R→I→E→V→C 元编排/质量门追溯时 |
| 原子提交 | L1 | [atomic-commit-cmd/SKILL.md](../atomic-commit-cmd/SKILL.md) | C 阶段提交规范 |
| 链接检查 | L1 | [link-check-cmd/SKILL.md](../link-check-cmd/SKILL.md) | V 阶段链接验证 |

**可迁移性**：勘误四模式（日期版本/成效溯源/口径对照/引文逐字）不依赖 OKF 场景，可迁移至一切"二手内容→可信知识库"任务（网页学习笔记、竞品分析、行业报告解读）。

## 12. Changelog

- **v1.0.0** (2026-08-29): 初始版本。从 13 篇博文→OKF 知识包转化实践萃取（13 篇异质博文、7 类内容形态、492 条事实登记、90 项 P0 核验：64✅/22⚠️/4❌、133 个 md 文件），封装七阶段工作流、操作可复现性两问、信源距离五分类、勘误四张清单、flagged 状态管理、双份 F 编号核对、8 项机械门禁清单、13 条反模式。对应 L2 模式文档 maturity_level=L3（validation_count=12，第 13 篇资讯速报骨架案例已由 agora-gemini-transcribe 补齐）。
