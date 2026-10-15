# WorkBuddy OPC 白皮书学习 → OKF Wiki 知识包 - 实施计划

> 方法论链路：seven-concepts 场景 4（知识沉淀）R→I→E，V 由独立 Review 承担；信源先行顺序：facts → references → concepts → bundle index → 上级索引 → 门禁 → 独立审查。
>
> 执行边界：产出写入 git submodule `projects/awesome-okf-xs/`；采集缓存留在 `.temp/workbuddy-opc/` 并在收尾清理；默认不执行 git commit/push。

## Task 1: R — 建立 spec 侧 F 编号事实台账（facts.md）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1 rule PASS：facts.md 含 source-manifest（W0/P0/P1/X1 四信源）段与 F 表；独立复核正则 `^\|\s*F-(\d{3})\s*\|` 实测 `count=357 min=1 max=357 dup=[] missing=[]`；页覆盖实测 `pages covered = 1…32` 全覆盖，页3–页32 每页 ≥1。
  - TR-1.2 rule PASS：357 行全部为 6 列（编号 + 声明/类型/source_id/locator/备注）；类型取值限定于 元信息(11)/厂商自述(87)/第三方研究口径(64)/官方或协会口径(59)/白皮书观点(113)/合作邀约语汇(23)；locator 统一为「页N·§x.y」形式；G1 门通过（声明栏无因果推断词，因果叙述归「白皮书观点」）。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `.trae/specs/okf-wiki-ecosystem/workbuddy-opc-whitepaper-okf-wiki/facts.md` 登记 source-manifest（W0/P0/P1/X1 四信源、访问日期、获取方式、体量、`publishVersion: 4`、公开性判定依据与 `noindex` 登记）与 F-001 起连续编号事实表。
  - 覆盖白皮书 32 页全部正文：六章导语、32 节、本章小结、数据说明、结语；分类仅用 元信息 / page_fact / 厂商自述 / 第三方研究口径 / 官方或协会口径 / 白皮书观点 / 合作邀约语汇；执行者解读不入 facts。
  - 预计 150~200 条（F-001~F-1XX，以实际连续编号为准），关键数字/金额/日期/政策名/机构名/专家团与 Skill 名零遗漏。
  - 采集基准为 P0 制品 `opc-whitepaper-mobile.html` 的提取文本（32 页 / 25 508 字符）；`janus.data.json` 仅作节点交叉参照。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 含 source-manifest 段与 F 表；正则 `^\|\s*F-(\d{3})\s*\|` 提取的编号从 F-001 连续无跳号无重复；章节覆盖集合与白皮书页码集合双向差集为空；证据=正则输出 + 逐页核对记录
  - `rule` TR-1.2: 每条含 claim/type/source_id/locator/status 五要素（列可合并但信息可辨识）；locator 采用「页N · §x.y」形式；证据=文件内容
- **Notes**: G1 门——事实栏无因果推断词，因果叙述归「白皮书观点」。实际采集 357 条（超出预估区间，按「以实际连续编号为准」口径接受）；`page_fact` 类型未单列——正文客观陈述并入其来源口径类别（官方或协会口径 / 第三方研究口径），已在 facts.md 的 G1 段显式说明。

## Task 2: E(信源先行) — references 四文件
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1 rule PASS：独立复核 `facts.md` ↔ `references/article-source.md` 正则集合：各 357 条、`equal True`、双向差集为空、连续无跳号无重复。
  - TR-2.2 rule PASS：verification.md 含 22 项 P0 核验总表（✅14/⚠️8/❌0）、六类口径分层表、**11 项勘误清单**（存量数据时间口径、《法治日报》2026.5.14 未检索到、朝阳「生产工具平台 500 万」vs 官方 1000 万、所引《财经》报道未检索到 + 杭州 2 万㎡/江苏 OPC 城市未核到、认证 800 元 vs 官网 ¥330（原 ¥600）、联创存活率 45% vs 35%、十亿美元公司 80% 未核到、Polsia 领投存疑/8,700+ 家/周增 9% 未核到、§4.4.1「20 个专家团」vs §5.1「13 个」并附 §5.1 表内 13 行自洽清点、平台数字与官网「100+ 领域专家」不符、目录与正文标题微差）、V 四视角对抗审查表、status 裁决；全部 URL 取自实际检索结果，无编造。
  - TR-2.3 rule PASS：四文件 frontmatter/type/status/stale_after/sources 齐备（index.md 无 frontmatter）；链接受检 broken=0；敏感路径命中 0。
  - status 裁决：**`flagged`**（依据：平台能力数字内部自相矛盾且与厂商官网现口径不符、认证费用与官网冲突、政策资金与官方原文冲突、效率倍数与 Polsia 指标多为单源）。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 生成 `references/index.md`（toctree + 表格双轨）。
  - 生成 `references/source-manifest.md`：W0/P0/P1 采集台账 + X1「未取得」登记 + 逐页/逐章覆盖状态表 + 壳页与制品的路径区分 + `noindex`/公开性判定留痕。
  - 生成 `references/article-source.md`：frontmatter 完整；F 表与 facts.md 双份一致；末尾「引用边界」（无 PDF 母本、无原图入库、平台数字为厂商自述、案例数字为受访者自述）。
  - 生成 `references/verification.md`：P0 核验总表、六类口径分层表、勘误清单、V 四视角对抗审查表、`status` 裁决。
  - 核验手段：WebSearch 权威源交叉（政府公报／官媒报道／研究报告发布方／厂商官网），核验不到即标「仅白皮书单源」，**禁止编造 URL**。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: article-source.md 与 facts.md 的 F 编号正则集合相等、连续无跳号；证据=两文件提取结果比对
  - `rule` TR-2.2: verification.md 含六类口径分层表与勘误清单，且下列要点各有落点：235 专家／250 Skill／86 能力为厂商自述、§4.4.1 20 个专家团 vs §5.1 13 个核心专家团冲突、三案例受访者自述属性、5%/10%/70%/15% 与 80%/20% 为单一来源、第六章合作模式为框架性定位、政策与平台数字带 2026-06 时点；无编造 URL；证据=逐条定位
  - `rule` TR-2.3: 四文件 frontmatter/type/status/stale_after/sources 齐备；三个 index 含 toctree 块；证据=文件检查
- **Notes**: 核验在独立子任务上下文中完成（`external-verification.md` 为核验原始记录，位于 `.temp/workbuddy-opc/`）。status 由 spec 目标 `stable` 依规转 `flagged`（spec 待决事项④）。

## Task 3: E — concepts 七篇 + 子索引
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1 rule PASS：独立复核全束 `F-\d{3}` 引用 **508 处**、越界/查无 **0**（00=107/73、01=78/68、02=48/48、03=69/64、04=68/56、05=66/62、06=72/61）；数字抽查 ≥20 项全部命中（1,600 万家、27.4%、286 万户/+47%、570 万家、34%/7%、7,290 万、23.7%→36.3%、80%/95%/96%/87%、20-40%/2-10 倍/92%、1:72、8-10 倍、Polsia 四项、5/10/70/15%、朝阳 500/1000 万、深圳 50 万㎡/1,000 万/3,000 万、2,500 工位/800 万、35%/45%、Cursor/Lovable/Base44、235/250/86、60 工作流、3.3 亿/60%、800 元、71 套设计系统）。
  - TR-3.2 rule PASS：原创改写，无长段逐字复制；束内既无原图也无 HTML 制品（束内非 .md 文件 0）。
  - TR-3.3 rule PASS：8 文件（index + 00~06）落盘；7 篇 frontmatter 字段齐备（`type: Concept`/`status: flagged`/`stale_after: 2026-12-31`/三 sources），`concepts/index.md` 无 frontmatter 且含 7 条 toctree；**2 张 Mermaid**（04 架构承接图、06 生态四维度图）经 FlowchartChecker 校验无 error/warning。
  - TR-3.4 rubric PASS（4/5，阈值 ≥4）：每篇回答一个明确问题、六类口径全文一致落地、11 项勘误逐项落正文、三案例按「受访者自述」读法呈现、含可迁移判读框架。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `concepts/index.md`（无 frontmatter，toctree 7 条 + 列表）。
  - `00-whitepaper-provenance-and-reading-guide.md`：白皮书是谁出的/何时发的/制品从哪来、六类口径分层速查、阅读路径与已知边界。
  - `01-opc-landscape-and-super-individual.md`：规模数据、超级个体四特征与知识工作演化链、效率革命量化、创业生命周期四阶段对照、Polsia 上限表、三个新陷阱。
  - `02-from-execution-orchestration-to-business-models.md`：硅基员工三阶段演进、80/20 分工、三层能力模型、六大商业模式表、六条 C 端赛道表、万能套利公式、能力洗牌分层模型。
  - `03-china-policy-and-local-ecosystem.md`：北京朝阳 7 维度 10 措施表、深圳行动计划十维度表、20+ 省市政策亮点表、政策配套缺口五层表、园区与本地化生态表。
  - `04-super-team-and-workbuddy-architecture.md`：四重结构需要表 + 联创数据、组织竞争力公式、三种超级团队形态表与 AI Native 团队案例、WorkBuddy 三层架构承接表、三阶段专节、混合架构论据（含 Mermaid）。
  - `05-opc-capability-map-and-user-cases.md`：七个经营环节的能力矩阵、三个用户案例结构化呈现（韦优／蔡琛律师／智觉·李殿鹏）+「受访者自述」标注、案例数据读法。
  - `06-ecosystem-certification-and-cooperation.md`：四个建设维度表、各维度核心需求、WorkBuddy 定位表、认证体系表与设计逻辑、四类合作方合作模式表、结语要点（含 Mermaid）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: 每个出现的具体数字/金额/日期/机构名/政策名/专家团与 Skill 名均带 F 编号引用；无 facts 之外的新数字；证据=成稿后逐数回查
  - `rule` TR-3.2: 无原文连续长段逐字复制（>40 字直引须严格逐字且必要）；无原图/HTML 制品入库；证据=对照提取文本检查
  - `rule` TR-3.3: 八文件（含 index）frontmatter 齐备、`type: Concept`、`sources` 三源；concepts/index.md 含 toctree；至少 2 张 Mermaid 图且语法可解析；证据=文件检查 + Mermaid 校验
  - `rubric` TR-3.4: 知识转化质量；scale 1-5；anchors 同 AC-6；threshold >= 4；证据=七篇成稿审查评分
- **Notes**: E 阶段距 R 阶段已隔多轮，生成时显式附相关 F 编号，不确定时回查 facts.md。

## Task 4: E — bundle 根 index.md + log.md
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1 rule PASS：index.md 顶部含厂商白皮书 flagged 性质提示块与「非操作教程」声明；隐藏 toctree 三条目（`concepts/index`/`references/index`/`log`）拼写正确；24 条相对链接按目录规范化后 Test-Path 全部 True（含 4 条兄弟束互链 `../ai-solo-company-truth/index.md`、`../ai-one-person-micro-product/index.md`、`../workbuddy-content-system/index.md`、`../papi-jiang-solo-ip/index.md`），broken=0；frontmatter 十键齐备（`okf_version` 仅在束根），description 含「行业白皮书解读，非操作教程」。
  - TR-4.2 rule PASS：log.md 无 frontmatter、日期标题 `## 2026-10-15`；含 R→I→E→V 链路、F-001~F-357 双份登记相等、两问判定与不设 `examples/` 理由、信源与制品口径、六类口径分层、11 项勘误摘要、`status: flagged` 裁决理由、并行在途观测、门禁方式与结论、未提交声明。
  - 口径更正：束内实际为 **14** 个 Markdown（根 index + log + concepts 索引 + 7 篇 + references 索引 + 3 篇），spec 原写的 13 为计数笔误，已同步更正 spec.md FR-1/分层设计段与本文「提交说明」。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - `index.md`：OKF v0.2 frontmatter（九字段，sources 含分享页 URL 与内置信源）；顶部「厂商白皮书」性质提示块；「非操作教程、无 examples/」声明；三层阅读地图；核心结论速查表；主题关联互链（4 个兄弟束，逐条说明分工）；已知边界；目录结构块 + 隐藏 toctree。
  - `log.md`：记录 R→I→E→V 过程、F 编号区间、两问判定与不设 examples 的理由、口径与勘误决策、并行在途观测、门禁方式与结论、未提交声明。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-4.1: index.md 顶部含厂商白皮书性质提示与「非操作教程」声明；隐藏 toctree 三条目拼写正确；四条主题关联链接相对路径深度正确（自束根引用兄弟束为 `../<bundle>/index.md`，Test-Path 全 True）；证据=文件检查 + 链接 Test-Path
  - `rule` TR-4.2: log.md 含 F 区间、两问判定与理由、口径/勘误决策、门禁实际方式与结论；证据=文件内容
- **Notes**: 互链仅在新束内向既有束单向声明；不回补反向链接。

## Task 5: V — 三级索引接入与计数同步
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1 rule PASS：`sheke/industry/index.md` 导航表 25→26 行（新行文档数按同表既有「C+R」口径记为 `7+3`；抽样回验 5 个既有行口径一致）、toctree 25→26 条、frontmatter description「等 25 束行业分析」→26；`sheke/index.md` 正文「25 束」→26、域内分组导航 industry 行（25 束）→（26 束）并补入新束关键词；`doc/bundles/index.md` 五面同步——`total_bundles` 638→**639**、正文「638 个知识包」→639、mermaid sheke 节点 68→**69** 束、域节标题 68→69 束、industry 分组行 25→**26**（`groups: 61`/`domains: 9` 不动）。
  - TR-5.2 rule PASS：`git status --short` 证明本次仅改上述 3 个索引 + 新增 bundle 14 文件；并行会话在途改动（`jishu/index.md`、`jishu/ai/index.md`、`jishu/ai/ecosystems/index.md`、`.../tencent/index.md`、`.../workbuddy-official-docs/index.md` 与 2 个 untracked 新束）**零回退**；计数为「先读现值再 +1」（编辑前 working tree 已因并行会话为 638）。
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 组索引 `sheke/industry/index.md`：导航表 +1 行、toctree +1 条、frontmatter description 束数同步。
  - 域索引 `sheke/index.md`：正文束数与 industry 行同步。
  - 总索引 `doc/bundles/index.md`：五面同步（frontmatter / 正文计数 / mermaid 节点 / 域节标题 / industry 分组行）；不得回退并行 WIP。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 三级索引五面计数自洽、与脚本输出逐项相等；新增 toctree 条目指向的文件 Test-Path 为 True；证据=改动片段 + `check-bundles-index.py` 输出
  - `rule` TR-5.2: `git diff` 确认只在当前工作区版本上增量、并行 WIP 行完整保留；证据=git diff 输出
- **Notes**: 计数先读现值再 +1，禁止凭记忆写数字。

## Task 6: V — 机械门禁与收尾自检
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6.1 rule PASS（逐项实测）：`check-utf8.py` exit 0（11 651 文件均为有效 UTF-8）；`check-toctrees.py` exit 0（全部 index.md 引用有效、所有内容文档可达，输出中 `workbuddy-opc-whitepaper` **零命中**）；`check-bundles-index.py` exit 0（`9 域 / 61 组 / 639 束，frontmatter、计数行、节标题、分组表、toctree 五面一致`）；本束 14 文件 strict UTF-8 + 无 BOM **14/14** 通过；双份 F 集合 357=357 `SET_EQUAL: True`；全束相对链接 **checked 58 / broken 0**（含 `concepts/`、`references/` 下 `../../` 深度兄弟束引用）；敏感串（`file:///`、`C:\Users`、`/Users/`、`C:/Users`）命中 **0**；frontmatter 逐类符合（根 index 九字段、10 个内容文件不含 `okf_version`、3 个 index/log 无 frontmatter）；无 `examples/`、束内非 .md 文件 0；`sphinx-build -b dummy -E doc _build/dummy` exit 0 且**与本束路径相关的 error/warning = 0**。
  - `invoke gates.*` **不可用**（`invocations` 包缺失：`invoke --list` 抛 `PackageNotFoundError`），已按规范改用直接运行 `scripts/*.py` 并在 log.md 如实记录，**未谎报 invoke 通过**。
  - TR-6.2 rule PASS（部分，已如实注记）：束内无 `.html`/`.json`/图片制品，敏感路径零出现；**临时采集缓存 `.temp/workbuddy-opc/` 按计划延后至独立审查完成后清理**（审查需与源文提取文本逐字比对），已在 log.md 明示原因。
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 在子模块环境尝试 `invoke gates.*`；不可用时执行直接运行底层脚本——`scripts/check-toctrees.py`、`check-utf8.py`、`check-bundles-index.py` 并留存输出。
  - 手动等效清单：UTF-8 strict、双份 F 集合、三级 toctree 条目 Test-Path、全束相对链接可达、`file:///` 与家目录路径零出现、frontmatter 完整、计数三处一致。
  - 定向 Sphinx dummy 构建验证无本束引入的错误。
  - 清理 `.temp/workbuddy-opc/` 采集缓存与提取脚本（本项延后至 Review 完成后执行）。
  - 在 `log.md` 写入门禁实际方式与结论。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 手动等效清单逐项有证据；新增/修改 .md 全部 UTF-8 strict roundtrip 通过；`check-toctrees.py` 输出过滤本束名零命中；证据=命令输出
  - `rule` TR-6.2: 新束目录下无 `.html`/`.json`/`.png`/`.jpg` 制品；`file:///`、`C:\Users`、`/Users/` 在新文件零出现；`.temp/workbuddy-opc/` 已清理；证据=Glob + Grep + Test-Path
- **Notes**: 实际门禁方式已在 log.md「门禁与验证（V 阶段实测结论）」小节逐条留痕。

## Task 7: V — 独立对抗审查（Spec Mode Review 阶段）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7.1 rule PASS：fresh-context 只读审查者独立产出 `review.md`（审查元信息含只读声明、对照基准与方法），逐 AC 给出独立证据；rubric 逐条给出分数与锚点理由；含 P0/P1/P2 发现清单与「机械检查原始输出摘要」（全部为审查者亲自执行）。
  - 独立复跑结果：双份 F 集合 facts=357 / article=357 `SET_EQUAL=True`（连续 1–357、无重号缺号）；全束相对链接 checked=58 / broken=0；`check-utf8.py`/`check-toctrees.py`（本束名 0 命中）/`check-bundles-index.py` 退出码均 0；计数实测 industry 导航=toctree=磁盘=26、sheke 域=69、total_bundles=639，与脚本输出逐项相等；敏感路径真实命中 0；无 `examples/`、无非 .md 制品；Sphinx dummy exit 0 且本束相关 ERROR/WARNING=0。
  - TR-7.2 rubric PASS（4/5，阈值 ≥4）：审查独立重跑全部关键机械检查并做实质性质证（引号逐字核对、≥20 个数字回指 F 抽查、11 项勘误在正文的落实情况抽查、口径标签一致性抽查、verification.md 对 external-verification.md 的忠实度抽查、log.md 与磁盘一致性抽查）。
  - **最终结论：`pass`** —— AC-1~AC-5（rule）全部 PASS，AC-6=4、AC-7=4（均 ≥4 阈值）；P0=0、P1=0，仅 6 项 P2 advisory（不阻断），其中 3 项（log.md 类型清单含未用 `page_fact`、log.md 两处并行观测措辞不一、临时目录清理状态）已在收尾阶段闭环，其余属后续打磨建议。
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 实施队列清空后进入 Review：向 fresh context 只读审查者交付独立审查契约（目标、仓库根、spec.md/tasks.md/review.md 绝对路径、spec 侧 facts.md、门禁输出），逐条核验 AC-1~AC-7 并独立重跑关键机械检查（正则、官方三脚本、Test-Path、Grep、git diff），产出 `review.md`；结果为 `fail` 时把每条可行动发现固化为 `tasks.md` 中的 pending 修复 issue 并回 Implement。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: review.md 覆盖每个 AC、每条 rule 有独立证据、每条 rubric 有评分与锚点理由；证据=review.md
  - `rubric` TR-7.2: 审查独立性与深度；scale 1-5；3=仅复述自验结论，5=独立重跑关键机械检查并提出实质性质证；threshold >= 4；证据=审查过程记录

## 提交说明（非任务项）

按 `.trae/specs/README.md` 与同组先例，本轮**默认不执行 git commit/push**。若用户后续授权，提交顺序为：① 子模块 `projects/awesome-okf-xs` 内先提交（bundle 14 文件 + `sheke/industry/index.md` + `sheke/index.md` + `doc/bundles/index.md`）→ ② 主仓库提交 spec（`.trae/specs/okf-wiki-ecosystem/workbuddy-opc-whitepaper-okf-wiki/`）→ ③ 主仓库更新子模块指针；提交须显式列全文件并使用 `python .agents\scripts\git-commit-utf8.py`。
