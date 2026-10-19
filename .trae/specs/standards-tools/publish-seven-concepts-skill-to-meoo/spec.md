# 个人变现方向发现方法论 · OKF Wiki 知识包 Spec

## Why

大量个体（自由职业者、副业探索者、被动转型者、内容创作者、应届生）在回答"我能靠什么变现"时缺乏系统方法，普遍陷入三类误区：① **跟风赛道**——追逐热门赛道而忽视自身禀赋与资源约束；② **爱好即能力**——把"我喜欢"等同于"市场愿付费"，跳过需求验证；③ **只学技巧不问匹配**——收藏大量变现技巧，却从未完成"我是谁 → 市场要什么 → 交集在哪"的匹配闭环。

现有邻近知识包均非此定位（`ai-monetization` 讲 AI 变现技法、`monetization-essence` 讲变现本质公理、`zhihu-monetization` 讲单一平台机制、`overseas-freelance-night-work` 讲单一副业族）。**缺少一个面向"方向发现"本身的可溯源、可操作知识包**——即帮助个体从自我评估走到候选方向、再到验证与决策的方法论。

## What Changes

* 新增 OKF v0.2 知识包 `sheke/industry/monetization-direction/`（暂定名，实施时按命名三查定稿），三层结构：事实层（权威框架事实登记）/ 方法层（自评→候选生成→需求验证→决策）/ 路径层（路径矩阵与决策清单）。

* 新增 spec 区 `.trae/specs/create-monetization-direction-okf-wiki/`（spec.md / tasks.md / checklist.md / facts.md / sources.md / knowledge-map.md）。

* 接入 `sheke/industry/index.md`：导航表 +1 行、toctree +1 条、束数 26→27；同步 `sheke/index.md` 域内分组表 industry 26→27 与描述、`bundles/index.md` total\_bundles 641→642 与 sheke 域计数 69→70（**所有计数以执行时读取现值为基准，不凭记忆写数字**）。

* 新增 bundle 与既有同主题 bundle（ai-monetization / monetization-essence / zhihu-monetization / overseas-freelance-night-work / ai-one-person-micro-product）的"主题关联互链"段。

* **BREAKING**：无（纯新增，既有 bundle 正文零改动）。

## Impact

* Affected specs：新增能力 `个人变现方向发现（monetization-direction discovery）`

* Affected code / 资产：

  * `projects/awesome-okf-xs/doc/bundles/sheke/industry/`（新增 bundle + 组索引同步）

  * `projects/awesome-okf-xs/doc/bundles/sheke/index.md`（域内分组计数与描述同步）

  * `projects/awesome-okf-xs/doc/bundles/index.md`（总索引计数同步）

  * `.trae/specs/create-monetization-direction-okf-wiki/`（新增 spec 区）

* 触及子模块边界：`projects/awesome-okf-xs` 为 git submodule，变更须在子模块内提交后于主仓库更新 gitlink（子模块先提交、主仓库后提交、指针最后；不 push）。

## 问题、用户与目标

### 用户

* 主要用户：想找到自己适合的变现方向但缺乏系统方法的个人（有稳定主业想发展副业者、自由职业者、被动转型者、技能型创作者）；

* 次要用户：想系统了解"个人变现方向如何科学发现"的 OKF 知识库读者。

### 目标

1. 以七概念方法论（R→I→E→V→C，其中 F→V 用于方法层设计）执行"全面调研"，覆盖**四类权威信源**：① 职业匹配与设计人生理论；② 优势/兴趣/天赋识别工具；③ 个人商业模式与变现模式理论；④ 需求验证与最小可行验证方法；
2. 产出可溯源、经 P0 核验的 OKF Wiki 教程 bundle，使读者能照做完成"自我盘点 → 候选方向生成 → 需求验证 → 决策与启动"完整链路；
3. 全程通过质量门（G1-G4 + OKF 机械门禁），以原子提交交付到既定仓库位置。

### 非目标

* 不推荐任何具体性格测评产品、课程或付费工具，不引导消费；

* 不做收益承诺——所有涉及收益/规模的表述须挂 F 编号或标注"待验证/单源"；

* 不覆盖"全部行业变现清单"（避免清单式堆砌），聚焦"如何发现"的方法而非"有哪些"的罗列；

* 不改动 `vendor/`、不改动子模块内既有 bundle 正文；

* 不 push 到远端（用户未要求时）。

## 信源与内容敏感度（预检结论）

**敏感度判定**：本任务信源为公开的学术理论、公开出版著作、工具官方文档、公开研究报告（无 code/token/邀请码、无登录墙）→ **公开内容**，走标准工作流：

* 规划区：`.trae/specs/create-monetization-direction-okf-wiki/`

* 产出物：`projects/awesome-okf-xs/doc/bundles/`（OKF v0.2）

* 私域零残留：产出物中禁止出现 `file:///` 绝对路径、本机绝对路径、个人敏感信息。

**信源类别与信源距离预判**（R 阶段按此分层核验）：

| 类别                | 预期信源形态                                                                               | 信源距离         | 默认核验级             |
| ----------------- | ------------------------------------------------------------------------------------ | ------------ | ----------------- |
| C1 职业匹配 / 设计人生    | 学术理论原始提出者（如 Schein 职业锚、Holland RIASEC）、权威著作（Designing Your Life）                     | 一手理论 / 权威出版物 | P0（年份/提出者/归属）     |
| C2 优势 / 兴趣 / 天赋识别 | 工具官方文档（CliftonStrengths 等）、学术综述                                                      | 工具官方 / 第三方综述 | P1（能力声明）+P0（官方归属） |
| C3 个人商业模式与变现模式    | 权威著作（Business Model You、Company of One、1000 True Fans、So Good They Can't Ignore You） | 权威出版物        | P0（作者/年份/核心主张归属）  |
| C4 需求验证与最小验证      | 精益创业 / JTBD / 实验方法论权威来源                                                              | 一手方法论        | P0（提出者/年份）        |

## 功能性需求

### FR1 信源调研与候选清单（R-a）

按"全面调研"要求检索并确定四类信源（每类 ≥2 个可核验信源），产出 `spec/sources.md`：信源名 / 类型 / 权威口径 / 可访问 URL / 采用理由 / 弃用理由。**信源不足或不可访问不得静默跳过**——须记录并说明替代来源。

### FR2 事实采集与 P0 核验（R-b / R-c）

* F-001 起连续编号登记全部关键声明（理论提出者、提出年份、核心主张、工具官方定位、研究结论与其限定条件），作者/机构观点显式标注"观点"或"主张"；二手转述标注转述层级；

* 信源距离分层核验：C1/C3/C4 类"提出者+年份+核心主张归属"默认 **P0 必核验**（WebSearch 权威源：原始论文、出版社官方、工具官网、权威百科）；C2 类工具"能力声明"为 P1 选核验；

* **科学争议与边界强制标注**：涉及性格测评类工具（如 MBTI）须登记其科学效度争议与"非决定论"边界，禁止作为方向判定依据；

* 勘误四张清单逐项过筛：① 日期/年份表 ② 成效数字溯源表 ③ 口径对照表（限定条件/适用人群）④ 引文逐字核对表（著作主张不得意译加引号）；

* 源文/二手错误不静默照搬：新增 F 编号记录正确值与差异，verification.md 单列"勘误"，正文呈现正确值并标注原口径。

### FR3 骨架判定与三层知识拆分（I）

* **骨架判定（操作可复现性两问）**：① 本包是否含读者可照做的**自评/验证操作流程**（盘点表、验证实验步骤）？② 这些流程是否可复现（有输入、有步骤、有判定标准）？**两问皆"是" → 设** **`examples/`（工具表、自评清单、验证实验模板）**；任一为"否" → 不设空目录，操作以 concepts 承载。判定结论与理由必须写入 `log.md`；

* **三层拆分**：事实层（框架与工具的 What/Who/When，即权威来源登记）→ 方法层（"怎么找到"的操作方法与判断标准：自我盘点、候选生成、需求验证、决策，含因果解释须标注"洞察/推断"）→ 路径层（面向不同起点/资源约束个体的方向选择矩阵与决策清单）；

* **信源先行**：references/（article-source.md + verification.md）→ concepts/ → 各级 index.md 最后写。

### FR4 bundle 生成（E）

* frontmatter 齐备（OKF v0.2：`okf_version`（仅 bundle 根）/`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources`），`sources` 同时含理论/著作来源与核验权威 URL；

* 所有具体声明引用 F 编号，数字/年份/提出者/工具名必须有 F 出处，禁止 `facts.md` 之外的编造；

* 目录结构：`index.md` + `concepts/` + `references/` + `log.md`（`examples/` 按 FR3 两问结论取舍）。

### FR5 对抗审查与索引收尾（V）

* 四视角审查内容文档：事实溯源（无 F 之外的数字/年份/工具名，勘误在正文落实）、结构规范、读者可用性（相对链接逐一可达）、时效边界（观点分层、工具争议标注）；

* **魔鬼代言人视角专项证伪**：逐条攻击"伪科学自评断言""画饼式路径""把相关当因果"，无 F 支撑的因果与收益断言必须降级为假设或删除；

* **双份 F 编号一致性核对**：正则提取 spec `facts.md` 与 bundle `references/article-source.md` 编号集合比对——连续无跳号（跳号须显式注记）；V 阶段补充事实未回转时须在 `log.md` 注记原因；

* **父级分组索引接入**：`sheke/industry/index.md` 导航表加行 + toctree 追加 + 束数计数；`sheke/index.md` 组计数与描述同步；`bundles/index.md` total/域/组计数三处一致；

* **门禁**：依赖可用时 `invoke gates.all`（UTF-8 + toctree + 计数对账）；**依赖不可用时禁止声称"gates 通过"**，执行手动等效验证清单并在 `log.md` 注明。

### FR6 原子提交（C）

awesome-okf-xs 子模块内提交（bundle + 组索引 + 域索引 + 总索引）→ 主仓库提交 spec 区 → 主仓库提交子模块指针。Conventional Commits 中文描述；显式文件列表；不 push。

## 非功能性需求

| 编号   | 需求                                                                                       |
| ---- | ---------------------------------------------------------------------------------------- |
| NFR1 | **可溯源**：bundle 与 spec 中一切具体声明（年份/提出者/工具归属/研究结论）挂 F 编号或核验来源，禁止 `facts.md` 之外的编造           |
| NFR2 | **时效管理**：bundle `stale_after` ≤ 2027-06-30；工具能力与平台数据标注核验时点；涉及方法论类稳定内容可延长，工具类短时效内容缩短      |
| NFR3 | **治理合规**：遵循 Spec Mode 产物规范与 OKF frontmatter 规范；中文正文、kebab-case 英文文件名；相对路径引用，禁 `file:///` |
| NFR4 | **提交纪律**：Conventional Commits 中文描述；子模块先提交、主仓库后提交、指针更新最后；不 push                           |
| NFR5 | **门禁纪律**：依赖可用时跑 `invoke gates.all`；不可用时执行手动等效验证清单并在 log.md 注明；禁止谎报 gates 状态              |

## 验收标准

### AC-1: facts.md 存在且 F 编号连续

* **Type**: `rule`

* **Pass Condition**: spec 区 `facts.md` 存在；F 编号从 F-001 起连续无跳号（跳号须显式注记）；四类信源（C1-C4）的关键声明均有对应事实条目；观点/主张与事实分层标注；条数 ≥60。

* **Evidence**: `facts.md` 文件 + 编号连续性核对输出。

### AC-2: P0 声明 100% 有核验记录

* **Type**: `rule`

* **Pass Condition**: C1/C3/C4 类"提出者+年份+核心主张归属"与全部数字类声明 100% 有核验记录（权威 URL 或显式"单源/仅二手转述"标注）；勘误四张清单逐项过筛并记录于 `verification.md`；涉及性格测评工具者均有科学效度争议标注。

* **Evidence**: `references/verification.md` 核验结论表 + 勘误四清单 + 单源清单。

### AC-3: bundle 落于既有分组且计数三面同步

* **Type**: `rule`

* **Pass Condition**: bundle 落于既有分组（预期 `sheke/industry/`），未新建顶级分组，归属理由已留痕（`spec/knowledge-map.md` 或 `log.md`）；组 index 导航表行、toctree 条目、束数计数三面同步（以读取现值 +1 为准）。

* **Evidence**: 组 index / 域 index / 总 index 的 diff + `invoke gates.bundles`（或手动等效）输出。

### AC-4: bundle 结构符合 OKF v0.2

* **Type**: `rule`

* **Pass Condition**: 根 `index.md` 带 `okf_version: "0.2"` frontmatter 且含 `{toctree}`；存在 `concepts/`（含 toctree）、`references/`（article-source.md + verification.md）、`log.md`；`examples/` 取舍由操作可复现性两问判定且理由入 `log.md`；全部非保留 `.md` 含非空 `type`。

* **Evidence**: 目录清单 + frontmatter 抽查 + `log.md` 判定记录。

### AC-5: 链接与编码零缺陷

* **Type**: `rule`

* **Pass Condition**: 三级 toctree 完整（根/子目录/组 index 均含 toctree 块，条目排除 `:` 指令行逐一可达）；全部新增/修改 `.md` 相对链接可达、零 `file:///`；UTF-8 strict roundtrip 无乱码。

* **Evidence**: 链接检查输出 + `invoke gates.toctrees` / `invoke gates.utf8`（或手动等效）输出。

### AC-6: 双份 F 编号集合一致

* **Type**: `rule`

* **Pass Condition**: `facts.md` 与 `references/article-source.md` 的 F 编号集合正则比对一致；差异项（若有）已在 `log.md` 注记原因。

* **Evidence**: 编号集合比对结果。

### AC-7: gates 与提交纪律

* **Type**: `rule`

* **Pass Condition**: 在 awesome-okf-xs 子项目内 `invoke gates.all` 三 gate 全绿；依赖不可用时执行手动等效验证清单并在 `log.md` 注明（未谎报 gates 状态）；提交顺序为子模块 → 主仓库 spec → 主仓库 docs/指针；Conventional Commits 中文描述；`git log` 验证未 push。

* **Evidence**: gates 输出（或手动清单）+ `git log` 提交记录。

### AC-8: 方法链路可操作（读者可用性）

* **Type**: `rubric`

* **Dimension**: 从自我盘点到方向决策的完整可操作性

* **Scale**: 1-5

* **Anchors**: 1 = 仅罗列框架与名词，无可照做的步骤；3 = 有框架与步骤，但缺少判定标准或验证环节；5 = 完整链路（自我盘点表 + 候选方向生成法 + 需求验证实验 + 决策清单），每步有输入、步骤、判定标准与常见误区

* **Pass Threshold**: >= 4

* **Evidence**: concepts 路径层与方法层文档 + 魔鬼代言人审查记录。

### AC-9: 七概念质量门

* **Type**: `rubric`

* **Dimension**: 方法论质量门合规度

* **Scale**: 1-5

* **Anchors**: 1 = 事实含推断词、洞察无四元组、行动无判定标准；3 = 多数达标但部分洞察与事实混层；5 = G1 事实无因果词 / G2 洞察四元组完整（现象+根因+影响+建议）/ G3 模式含触发场景+核心步骤+反模式+迁移验证 / G4 行动项原子化；F 后有 V 对抗审查

* **Pass Threshold**: >= 4

* **Evidence**: 各阶段产出物 + 质量门通过记录。

### AC-10: 反伪科学与反画饼边界

* **Type**: `rule`

* **Pass Condition**: 涉及性格/天赋测评工具者均标注科学争议与"非决定论"边界；无 F 支撑的因果或收益断言为零（或已降级为显式假设）；无收益承诺；无具体产品/课程推荐。

* **Evidence**: 魔鬼代言人审查记录 + 正文边界声明段。

## 约束、依赖与假设

**约束**

* bundle 归属不新建顶级分组；预期落既有 `sheke/industry`（须先在 `knowledge-map.md` 列"候选位置 | 判定 | 理由"对照表论证）；

* 不修改子模块内既有 bundle 正文；仅追加新 bundle 与索引行/计数；

* 自评工具类内容须标注科学争议与边界，不得作为方向判定依据；

* 收益/规模类表述一律标"非承诺"，无 F 者不得出现。

**依赖**

* `projects/awesome-okf-xs` submodule 已初始化（已确认存在，含 641 束 / industry 组 26 束）；

* WebSearch / WebFetch（信源调研与 P0 核验）；

* awesome-okf-xs 内 `invoke gates.*` 可用（依赖 `invocations`，缺依赖时走手动等效清单）。

**假设**

* 四类信源存在可公开访问、可核验的权威来源；

* 用户不要求 push；

* 方法论类内容具有跨时间稳定性，工具类内容时效较短。

**待决问题（实施阶段按规则自行决策并留痕）**

1. bundle 精确命名（`monetization-direction` 暂定）→ 命名三查（查同类命名惯例、查是否重名、查语义准确性）；
2. `examples/` 是否设立 → 操作可复现性两问判定（**预期为"是"**，因自评表/验证实验可照做），理由入 `log.md`；
3. 组归属最终确认 → 决策树 + 候选对照表（industry vs personal-growth），理由入 `knowledge-map.md`；
4. `stale_after` 具体取值 → 按 NFR2 依内容性质设定。

## 关联资产

* 方法论：seven-concepts-cmd（本任务元编排，场景"知识沉淀" R→I→E→V→C，方法层设计叠加 F→V）

* 转化规范：blog-article-to-okf-wiki（OKF 结构 / F 编号 / 勘误四清单 / 骨架两问 / 索引收尾规则的落盘权威）

* 先例 bundle：`sheke/industry/ai-monetization`、`monetization-essence`、`zhihu-monetization`、`overseas-freelance-night-work`、`ai-one-person-micro-product`（同主题簇，互链参考）

* OKF 规范：`projects/awesome-okf-xs/.agents/rules/frontmatter.md`、`projects/awesome-okf-xs/AGENTS.md`（toctree 完整性 / 计数对账）

* 项目规范：`projects/awesome-okf-xs/.agents/context-routing.md`

