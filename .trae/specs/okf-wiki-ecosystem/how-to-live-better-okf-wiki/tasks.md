# 《高性价比人生指南》OKF Wiki 精读教程 - 实施计划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E + 强制 V；C 阶段按用户决策仅落盘不提交。
> 事实单一事实源：`.trae/specs/okf-wiki-ecosystem/how-to-live-better-okf-wiki/facts.md`（R 阶段建立）。

## Task 1: R-1 补充信源采集与 facts.md 事实登记

- **Status**: `completed`
- **Completion Evidence**：
  - facts.md 已建立，F-001~F-069 连续编号（五类：元信息 15 + 版本计数 9 + 机制规则 18 + 精选条目 27）。
  - 一手补采：raw book/01（36 条，含成本标签注释体例）、book/13、book/08、book/19、book/10 原文；GitHub API docs/book 目录清单；skills/life-decision-guide/README.md。
  - FR-2 九类 P0 声明均有 F 行承载；27 条精选候选六要素齐备。
  - G1 事实门通过：客观数字照录，作者判断标【作者观点】、镜像标【快照】。
- **Priority**: high
- **Depends On**: None
- **Description**：
  - 补采尚缺的一手材料：原仓 `book/01-不要早死.md`（raw.githubusercontent，取全章条目数与代表性条目原文）、`skills/life-decision-guide/README.md`（AI skill 安装方式与能力边界）、必要时 1–2 个其他章节 raw 文件用于精选条目与章计数核对；GitHub API 核对 book/ 文件数（33）与 docs/ 清单（已采）。
  - 建立 spec `facts.md`：F-001 起按五类连续登记——① 元信息（仓库/组织/许可/创建日/stars 两时点/博文元信息/三镜像属性）；② 版本计数（498/31/323·126·49/45/39/88·248·162 与 615/33/415·151·49/57/35/104·279·232 两套时点口径）；③ 机制规则（四资源/三成本/收益量级阈值/性价比档/受益者四档/排序/互引/争议/TODO/只引原始文献）；④ 精选条目事实（15–25 条候选：六要素+DOI/法规名）；⑤ 生态与工具（检索页/离线三件套 URL/AI skill/自托管/5 篇长文/引用对照/核实记录）。
  - 每条标注信源 ID 与（如适用）原文位置；作者价值判断（如"一般≠不该做""档位是作者判断=C 级"）标"作者观点"；镜像数字标快照时点。
- **Acceptance Criteria Addressed**: AC-2、AC-7
- **Test Requirements**：
  - `rule` TR-1.1：facts.md 存在且 F 编号从 F-001 连续（正则提取，无跳号；若有跳号须同文件显式注记）。
  - `rule` TR-1.2：五类事实齐备，P0 九类声明（FR-2）逐项有 F 行承载；检查方式为以 FR-2 清单逐项在 facts.md 检索定位。
  - `rule` TR-1.3：精选候选条目 15–25 条，每条六要素（成本/说人话/收益/证据级/来源/备注）字段不缺关键项；不足者标"待 P0 核验补齐"。
- **Notes**：G1 质量门——事实行禁因果推断词（数字与断言照录，解释性文字单列为"作者观点/转化者注"）。

## Task 2: R-2 P0 权威交叉核验

- **Status**: `completed`
- **Completion Evidence**：
  - 两个独立上下文子代理完成 19 项核验（医学/安全 10 + 法规/社科 9），全部访问一手页面（PubMed DOI、Cochrane、China CDC Weekly、AHA、WHO GSRRS、NHTSA PDF、npc/gov/mem/mohrss/mps/mca.gov.cn）。
  - 核心结果：10 项医学研究全部真实存在、效应值逐字吻合；发现并记录 5 处需采用核验口径的差异——F-072（溶栓为 9 项 RCT 非 16）、F-073（BASIC-OHCA 20.3%/1.2% 为全队列口径）、F-074（中国道路死亡出处为 WHO GSRRS 2023 模型估计）、F-076（燃气条例应为第 18 条第 6 项）、F-078（逃逸全责在实施条例第 92 条）；另有 F-075/F-077/F-079/F-080 口径精化。
  - 核验补充事实 F-070~F-086 已回写 facts.md（编号连续，共 86 条）。
  - rubric TR-2.3 自评分 5：版本演进（498→608→615 两时点）与真错误（条款号/试验数）分表处理，四清单逐项过筛；均非核心声明失败，status 取 stable。
- **Priority**: high
- **Depends On**: Task 1
- **Description**：
  - 按 FR-2 九类 P0 逐项核验，可委派独立上下文子代理分批执行（医学组：SSaSS NEJM/Cochrane 头盔/JAMA 烟雾报警/China CDC CO/OHCA 中国研究/蘑菇中毒；统计与元数据组：GitHub API stars 两时点、NHTSA/WHO 道路数据、版本计数）。
  - 每项产出：结论（✅/⚠️/❌）、权威 URL、原文关键数字、与博文/原仓口径差异；核验补充事实续编 F 编号回写 facts.md（区段"核验补充"）。
  - 版本计数差异（498/31 章 vs 615/33 章等）定性为"版本演进"，与"勘误"分表记录；stars 2,366（9/17）→19,238（9/28）记录为增长曲线两时点。
  - 无法找到独立权威源者标"仅原仓单源/仅博文单源"，禁止硬编 URL。
- **Acceptance Criteria Addressed**: AC-3、AC-U2
- **Test Requirements**：
  - `rule` TR-2.1：P0 清单每项在 verification 素材中有结论+信源 URL（或显式单源标注），✅/⚠️/❌ 三态无空项。
  - `rule` TR-2.2：至少 5 项核心医学/安全数字对到原始期刊/官方机构页面（NEJM DOI 10.1056/NEJMoa2105675、Cochrane CD004333.pub3、JAMA 1998、China CDC Weekly 2020、NHTSA DOT HS 813 573 类），URL 经 WebFetch 实际可达。
  - `rubric` TR-2.3：核验判断力——版本差与真错误不混同（差异处理合理性）；scale 1–5；anchors：1=把版本演进当硬错误或反之；3=主要区分正确；5=四清单（日期版本/数字溯源/口径对照/引文逐字）逐项过筛且论证清楚；threshold ≥ 4；证据：核验记录表。
- **Notes**：G2 前置；核验子代理任务书必须自带完整声明清单（不假设共享上下文）。

## Task 3: E-1 references/ 信源先行成文

- **Status**: `completed`
- **Completion Evidence**：
  - references/article-source.md（F-001~F-086 双份登记，五区结构）、verification.md（19 项 P0 总表、版本演进对照、勘误四清单、信源距离、方法边界）、references/index.md（含 toctree）均已创建。
  - 两篇 Reference frontmatter 齐字段、sources 完整；机械脚本实测双份集合相等（TR-3.1 见 Task 7 证据）。
- **Priority**: high
- **Depends On**: Task 2
- **Description**：
  - 创建 `references/article-source.md`：F 编号双份登记（与 facts.md 同编号体系），文首信源头（四用户 URL + 原仓 + API），五类分区 + 核验补充区；镜像快照属性与时点写清。
  - 创建 `references/verification.md`：P0 总表、勘误四张清单落点、版本演进对照表（498→608→615；31→33；两套分级/档位数；stars 两时点）、信源距离五分类评估、核验方法边界声明。
  - 创建 `references/index.md`：导语 + toctree（article-source、verification）。
  - frontmatter 齐字段（type: Reference；sources 列全）。
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-6
- **Test Requirements**：
  - `rule` TR-3.1：article-source.md 正则提取的 F 编号集合与 facts.md 完全相等（双份一致性）。
  - `rule` TR-3.2：references/index.md 含 toctree 且两个条目 Test-Path 为真；两篇 Reference frontmatter 必填字段齐备。
  - `rule` TR-3.3：verification.md 含 P0 总表、版本演进对照表、勘误四清单、方法边界四段，P0 每行有三态结论。

## Task 4: E-2 concepts/ 七篇概念文档

- **Status**: `completed`
- **Completion Evidence**：
  - concepts/ 下 7 篇（00~06）+ index.md 全部创建；03 篇 33 章全覆盖（章号 1–33 无缺漏）+ 5 篇 docs 长文导引 + 四大板块 Mermaid 图。
  - 04 篇精选 **21 条**（健康安全 14/法律 3/职场 2/人生大事 2，在 15–25 区间内），每条六要素 + F 编号 + "第 N 章第 M 条"定位 + 5 处核验注。
  - TR-4.5 教学链路自评 5（六段递进闭合）；TR-4.6 观点分层自评 5（事实/作者观点/快照三层、时点与禁忌齐）；TR-4.4 由独立评审抽查复核。
- **Priority**: high
- **Depends On**: Task 3
- **Description**：
  - 按骨架生成 00–06 七篇（文件见 spec"内容骨架"）；写作时每篇 prompt 显式携带相关 F 编号，距 R 阶段防止事实衰减。
  - 03 章导览含一张 Mermaid 四大板块图（健康与生命/钱与法律/人生大事/信息与成长——按 33 章实际归类）+ 每章一行表（章号/章名/主题/口径/代表问题）+ 5 篇 docs 长文导引。
  - 04 精选 15–25 条：覆盖四板块、以"极高×A 级"交集为骨干（低钠盐/安全带/头盔/烟雾与 CO 报警/CPR 等），每条六要素+争议禁忌+"详见原书第 N 节第 M 条"指引；数字必须逐字同 F 集。
  - 01 含精选统计术语卡（HR/RR/OR/95%CI/RCT/荟萃/队列/观察性/混杂/反向因果），02 含收益量级阈值表与"档位=作者判断（C 级）"声明，06 含"用本书框架评估任意生活建议"的迁移步骤与免责声明。
  - 创建 concepts/index.md（学习路径表 + toctree 七篇）。
- **Acceptance Criteria Addressed**: AC-1、AC-6、AC-7、AC-U1、AC-U2
- **Test Requirements**：
  - `rule` TR-4.1：七篇文件存在且 concepts/index.md toctree 七条目逐一 Test-Path 为真。
  - `rule` TR-4.2：04 篇条目数在 15–25；抽查 5 条数字与 facts.md 逐字一致；每条有 F 编号引用与原书定位。
  - `rule` TR-4.3：03 篇覆盖全部 33 章（章号 1–33 无缺漏）与 docs/ 5 篇长文；Mermaid 图符合安全编码（节点文本无裸括号/特殊字符破坏解析）。
  - `rule` TR-4.4：全文无 facts 集外的新数字/新研究名（Grep 抽查百分比、DOI、机构名回溯 F 行）。
  - `rubric` TR-4.5：教学链路质量；scale 1–5；anchors 同 AC-U1；threshold ≥ 4；证据：通读笔记。
  - `rubric` TR-4.6：观点分层与时效标注质量；scale 1–5；anchors 同 AC-U2；threshold ≥ 4。

## Task 5: E-3 根 index.md 与 log.md

- **Status**: `completed`
- **Completion Evidence**：
  - index.md：frontmatter 十要素齐备、sources 14 条、status=stable、stale_after=2027-03-31；性质声明/版本时点/核验提示三块置顶；知识结构、分层导航、信任生命周期、已知边界 6 条、同组互链、toctree 齐。
  - log.md：R/I/E/V 各段记录 + 文件清单（13 新增、3 修改）+ 门禁记录段（Task 7 回填）。
- **Priority**: high
- **Depends On**: Task 4
- **Description**：
  - index.md：OKF v0.2 frontmatter（sources 含四用户 URL + 原仓 + API + 各权威核验源；status: stable（除非 Task 2 触发 flagged 条件）；stale_after: 2027-03-31）；性质声明块（开源项目导读、非原创医学法律建议、数字时点）、版本演进提示块（博文快照 vs 现行）、信源说明表、知识结构树、分层导航表（仿 sell-before-build 先例）、信任与生命周期段、已知边界 ≥5 条、同组互链、toctree（concepts/index、references/index、log）。
  - log.md：按 CMD-LOG 精神记录 R→I→E→V 各步时间与产出、F 编号计数、P0 计数（✅/⚠️/❌/单源）、门禁方式（invoke gates 或手动等效）、C 阶段决策（仅落盘，列全部新增/修改文件清单）。
- **Acceptance Criteria Addressed**: AC-1、AC-6
- **Test Requirements**：
  - `rule` TR-5.1：frontmatter 十要素齐备（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources），sources ≥8 条（4 用户 URL+原仓+API+权威源代表）。
  - `rule` TR-5.2：已知边界覆盖：非医学法律建议、数字时点、C 级/TODO、镜像滞后、Unlicense/CC BY 署名、精选非全量。
  - `rule` TR-5.3：根 toctree 三条目 Test-Path 为真。

## Task 6: V-1 三级索引接入与计数同步

- **Status**: `completed`
- **Completion Evidence**：
  - personal-growth/index.md：total_bundles=3、description/导航表（7+2 文档数）/阅读路径/链路说明/toctree 均接入；sheke/index.md：导语与分组表更新为 3 束；bundles/index.md：frontmatter 575、计数行、mermaid、域标题（46 束）、分组表行五面同步。
  - 官方 gates.bundles 与独立脚本双路确认对账一致（见 Task 7）。
- **Priority**: high
- **Depends On**: Task 5
- **Description**：
  - 改 `sheke/personal-growth/index.md`：frontmatter total_bundles 2→3；导航表加行（文档数 7+2，一句话简介）；阅读路径加一行；导语补本束"博文/开源项目核验转化（R→I→E→V）"定位；toctree 追加 how-to-live-better/index；加同组互链说明。
  - 改 `sheke/index.md`：束数 45→46（frontmatter 如有 + 正文计数 + 分组表 personal-growth 行 2→3）。
  - 改 `bundles/index.md`：frontmatter total_bundles 574→575；"当前共"句、mermaid sheke 节点 45 束→46 束、sheke 域节标题、personal-growth 表行束数 2→3（如该表在总索引出现——经查总索引 sheke 表为分组级，束数在域标题与 mermaid；以实际五面对账为准）。
  - 改前先读现值，禁止凭记忆写数。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**：
  - `rule` TR-6.1：实际 bundle 目录数 = personal-growth toctree 条目数 = 其 total_bundles = 3。
  - `rule` TR-6.2：sheke 域束数（组行求和 8+7+3+2+2+2+21+3=46）= sheke/index 与 bundles/index 标注值；bundles total=575 与九域求和一致。
  - `rule` TR-6.3：新增 toctree 行 `how-to-live-better/index` 对应路径 Test-Path 为真。

## Task 7: V-2 机械门禁与四视角对抗自审

- **Status**: `completed`
- **Completion Evidence**：
  - **官方 gates 实际运行通过**（非手动替代）：`python -m invoke gates.all`（py314，子模块根目录）——gates.utf8 10,668 文件全过；gates.toctrees 无断链/孤立；gates.bundles 9 域/59 组/575 束五面一致。
  - 手动八项脚本独立复跑：UTF-8 strict、F 双份 86=86 连续、12 toctree 目标全在、断链 0/file:/// 0、家目录与 .temp 0 命中、frontmatter 14 sources、计数目录=3=toctree=frontmatter、九域双路求和=575。
  - 勘误落实抽查：5 处核验口径 + 1 处措辞精化在 concepts/index 全部命中；四视角自审记录写入 bundle log.md。
  - TR-7.3 rubric 自评 5：四视角各有结论（事实溯源/结构/可用性/时效），无需修复项亦给出论证。
- **Priority**: high
- **Depends On**: Task 6
- **Description**：
  - 手动等效验证清单逐项执行并留痕：① UTF-8 strict roundtrip（PowerShell strict 解码新增文件）；② 双份 F 编号集合比对；③ 三级 toctree 全条目 Test-Path；④ 全部相对链接 Grep+Test-Path、零 file:///；⑤ 三级计数同步；⑥ 敏感路径零残留（Windows/Unix/macOS 用户目录绝对路径，以描述性措辞执行扫描避免字面枚举）；⑦ frontmatter 完整；⑧ 版本差/勘误在正文落实。
  - 尝试 `invoke gates.all`（子模块环境，py314）：可用则以其输出为准并记录；不可用执行手动清单并在 log.md 注明，禁止谎报。
  - 四视角自审：事实溯源视角（无 F 外数字）、结构规范视角、读者可用性视角（链接/导航/阅读路径）、时效边界视角（时点/单源/观点分层）；发现项就地修复并记录。
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-5、AC-U2
- **Test Requirements**：
  - `rule` TR-7.1：八项清单全部有打勾证据（命令/脚本输出或人工核对记录）写入 log.md。
  - `rule` TR-7.2：若 gates 可运行，结果全绿；若不可运行，log.md 含"invoke gates 不可用，已执行手动等效验证"原样注明。
  - `rubric` TR-7.3：四视角审查覆盖度；scale 1–5；anchors：1=仅做格式检查；3=四视角走过场；5=每视角有发现或显式"无发现"论证且修复闭环；threshold ≥ 4。

## Task 8: Review 独立只读评审（fresh context）

- **Status**: `completed`
- **Completion Evidence**：
  - review.md 已创建：CP-R1~R5 + CP-U1/U2 全覆盖 AC；Review History 含 R1（fail，1 actionable+5 advisory）与 R2（pass）两轮。
  - R1 独立子代理自行运行结构/F 集合/P0 URL 抽查（3 个权威源数字逐字一致）/机械脚本/官方 gates，产出 actionable F1；经 Issue I-1 修复后，R2 全新子代理独立验证 F1~F6 全部 pass、防回归全绿、无新 actionable，CP-U2 由 4 复评为 5。
  - 最终结论：所有规则 CP pass、两个 rubric CP 均 ≥4（U1=5、U2=5），达到唯一成功出口。
- **Priority**: high
- **Depends On**: Task 7
- **Description**：
  - 队列清空后进入 Review：创建 review.md（检查点映射 AC-1～AC-7 规则项合并为 CP-R1～CP-R6、AC-U1/U2 为 CP-U1/CP-U2）。
  - 委派一个全新 general_purpose_task 只读子代理执行独立评审：给足仓库根、三绝对路径、运行说明、产物清单与各任务 Completion Evidence；要求独立重跑机械检查（不采信执行者自述）、抽查 5 条精选数字、核对 33 章覆盖与计数五面。
  - 按结果路由：pass→收尾；fail→把每条 actionable 发现物化为 Issue（本 tasks.md 追加 I-N），回 Implement 修复后重新发起新一轮新上下文评审；blocked→记录阻塞。
- **Acceptance Criteria Addressed**: 全部 AC
- **Test Requirements**：
  - `rule` TR-8.1：review.md 存在且每个 AC 至少被一个 CP 覆盖；含 Review History 与 R1 结论。
  - `rule` TR-8.2：独立评审证据中包含由评审者自行执行的检查输出（非引用执行者 log）。
  - `rubric` TR-8.3：评审独立性与深度；scale 1–5；anchors：1=自我复述；3=独立但只核格式；5=独立重跑机械项+内容抽查+给出可执行发现；threshold ≥ 4。
- **Notes**：评审通过是唯一成功出口；C 阶段不提交（用户决策），交付物为落盘文件清单（在 log.md 与最终回复中给出）。

## Issue I-1: Review R1 发现修复（1 actionable + 5 advisory）

- **Status**: `completed`
- **Completion Evidence**：
  - F1（actionable）：F-087 双份补登（88 条集合连续），02 篇 97.2% 挂编号并加"原书举例/未独立核验/非建议"三重限定；R2 独立验证 pass。
  - F2~F6（advisory）：F-088 双份补登并挂接 03 两处；三时点精确写法覆盖根 index/00/04/06；relationships 6→7；log 描述性措辞；F-049/F-067/F-046 双份校准。
  - 防回归：gates.all 三关复跑全绿、断链 0、双份 88=88；另处理 R2 advisory 3 项（frontmatter/节标题旧计数、review.md 回填、log 措辞）。
- **Priority**: high
- **Depends On**: Task 8（Review R1）
- **Discovered By**: Review R1（2026-09-28 fresh-context 独立评审，结论 fail）
- **Description**：
  - **F1（actionable/medium）**：concepts/02 篇"带状疱疹疫苗 97.2% 效力"为 facts 集外精确数字（FR-3/TR-4.4/NFR-1）。修法：双份补登 F-087（原书 README 举例，标注"原书自述、未在本次 19 项 P0 核验范围"），正文挂编号。
  - F2（advisory/low）：03 篇热线 12308/12356/12355 补登 F-088（出处为 README 目录章细目）。
  - F3（advisory/low）：根 index、04、06 三处"三周内 498→615"时间线压缩改为精确时点表述（9-07 上线/9-17 快照 498/9-28 现行 615）。
  - F4（advisory/low）：sheke/index.md relationships 行历史残留"（6 束）"→7 束（本次修改文件内顺手修正，使域索引自洽）。
  - F5（advisory/low）：log.md 门禁表第 6 项字面路径改为描述性措辞，消除朴素扫描噪音。
  - F6（advisory/low）：facts.md F-049 补论文精确样本 1,738,886（与 article-source 对齐）；F-067 定位"19 章 5、6 条"→"第 4–6 条"；F-046 补"软管几十元"成本。
  - 新增 F-087/F-088 后同步：facts.md、article-source.md 双份编号（86→88），及所有"86/F-086"计数表述（根 index、组索引、references/index、log）。
- **Acceptance Criteria Addressed**: AC-2、AC-5、AC-U2
- **Test Requirements**：
  - `rule` TR-I-1.1：双份 F 编号集合仍相等且连续（F-001~F-088，88 条）；02 篇 97.2% 挂 F-087 且 F-087 双份存在。
  - `rule` TR-I-1.2：grep 全 bundle 无"三周内 498"式压缩表述；sheke/index 计数自洽；门禁脚本（含家目录扫描）零真实命中。
  - `rule` TR-I-1.3：修复后 gates 仍全绿、相对链接仍 0 断链（防回归）。
