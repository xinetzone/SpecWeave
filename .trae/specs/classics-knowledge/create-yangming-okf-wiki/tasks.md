# 王阳明心学 OKF Wiki 知识包 - 实施计划（tasks.md）

> 方法论链路（seven-concepts-cmd 场景 4 知识沉淀）：R（信源采集/事实登记）→ I（洞察 G2）→ E（模式萃取 G3）→ A（原子化 73 文件）→ V（对抗审查+三门）→ C（原子提交）。
> 委托策略：T1–T5 每束端到端委托独立代理（信息边界=束目录，禁止写共享索引）；T6–T8 由主控串行执行。
> 模板基线（代理必读）：`projects/awesome-okf-xs/doc/bundles/think/daojia/daojiao/qingjingjing/` 全部 14 文件。

## Task 1: 束1《传习录》阅读教程（chuanxilu）端到端建设
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 委托独立代理在 `doc/bundles/think/yangming/chuanxilu/` 建成 14 文件束（facts.md、insights.md、log.md、index.md、concepts/00-overview.md、01-compilation-versions.md、02-volumes-structure.md、03-core-entries-map.md、04-selected-readings.md、concepts/index.md、examples/01-reading-plan.md、examples/index.md、references/sources.md、references/index.md）。
  - R 阶段：WebSearch/WebFetch 采集信源（维基文库《传习录》上/中/下卷、ctext.org、《王文成公全书》/《王阳明全集》版本资料、邓艾民《传习录注疏》、陈荣捷《传习录详注集评》等）；facts.md 登记 F 编号零推测事实（书名出《论语》"传不习乎"、薛侃初刻 1518、南大吉增刻、钱德洪续刻下卷、隆庆六年 1572《全书》定型、三卷结构与条目分野、条数异说并列）+ Rn 信源表。
  - **双源硬指标**：04-selected-readings.md 收录 ≥10 组关键原文（建议：徐爱录"亲民/新民"首条、"心即理也"、"知是行之始，行是知之成"、"知行合一"相关条、"致良知"自语、"无善无恶心之体"四句教（天泉证道，见下卷钱德洪录）、"岩中花树"、"人须在事上磨"、《训蒙大意》、《答顾东桥书》"拔本塞源"段节文），每组维基文库 × ctext（或中华文库/第二独立信源）逐字核对，异文登记不改字，核对记录入 facts.md 与 log.md。
  - I/E：insights.md ≥3 条 G2 四元组洞察 + ≥2 个 G3 模式（如"语录体三卷分层核读法"）。
  - examples/01-reading-plan.md：零基础/进阶/研读三轨分阶段阅读计划。
  - references/sources.md：权威性评级（传世文献系统、版本定型清晰，评 B 级口径说明）、底本与注本分级、在线信源分层。
  - 全部 frontmatter 按 qingjingjing 模板（type/title/description/tags/generated{by:"agent:general_purpose_task",at:"2026-09-01T..+08:00"}/status:stable/stale_after:2027-09-01/okf_version:"0.2"）；中文语境引号一律全角“”，禁双引号标量内嵌 ASCII 引号。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-1.1: 14 文件全部落盘且 frontmatter 可被 yaml.safe_load 解析、含非空 type；证据：文件枚举+yaml 扫描。
  - `rule` TR-1.2: facts.md 事实均为 F 编号陈述句+[Rn] 信源、无因果推断词；信源表 URL 真实；证据：facts.md 审查+WebFetch 抽查。
  - `rule` TR-1.3: ≥10 组原文双源核对记录完整（异文登记不改字）；证据：log.md 核对清单+facts 对应 F 条。
  - `rule` TR-1.4: 束根 index.md 的 toctree 收录 6 项、各子目录 index 收录全部内容页，无断链；证据：check-toctrees 过滤 chuanxilu 为空。
  - `rubric` TR-1.5: 阅读计划教学可用性；scale 1-5；anchors 1=无路径/3=有计划但粗疏/5=三轨清晰可执行；threshold >=4；证据：独立审查。
- **Notes**: 代理只允许写 `think/yangming/chuanxilu/` 目录；禁止修改任何 index.md（组/域/总索引）；禁止虚构条目编号与引文。

## Task 2: 束2 心学义理体系（doctrine）端到端建设
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 委托独立代理在 `doc/bundles/think/yangming/doctrine/` 建成 15 文件束（facts.md、insights.md、log.md、index.md；concepts/00-overview.md、01-xin-ji-li.md（心即理：心外无理/心外无物/岩中花树，与朱熹"性即理"对峙）、02-zhi-xing-he-yi.md（1509 贵阳首讲、命题群、针对时弊）、03-zhi-liang-zhi.md（1521 南昌揭示、良知=是非之心、"满街都是圣人"、致=推致）、04-siju-jiao.md（四句教文本、天泉证道、四无/四有、利根/其次相资）、05-gewu-daxue.md（"格者正也"、"意之所在便是物"、《大学古本》亲民/新民、万物一体《大学问》）、concepts/index.md；examples/01-doctrine-map.md（义理地图：四纲领命题关系与工夫落位）+index；references/sources.md+index）。
  - R：信源以《传习录》《大学问》《明儒学案·姚江学案》、陈来《有无之境》、陈荣捷/冈田武彦研究为主；核心命题原文（"心外无理，心外无物"、"无善无恶心之体……"、"大人者，以天地万物为一体者也"等）双源核对并与束1 共享结论一致（跨束同引文不得互相矛盾）。
  - I/E：insights.md ≥3 洞察（如"心即理 vs 性即理的体系分叉点在格物"）+ ≥2 模式。
  - frontmatter 体例同 Task 1。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-2.1: 15 文件落盘、frontmatter 合规；证据：枚举+yaml 扫描。
  - `rule` TR-2.2: 四大纲领命题文本、提出年代（1509/1521/1527）与权威信源一致，引文可回溯；证据：facts F 条+双源记录。
  - `rule` TR-2.3: toctree 完整无断链；证据：门控过滤 doctrine 为空。
  - `rubric` TR-2.4: 义理讲解准确性与分层（本体/工夫/境界）；scale 1-5；anchors 1=混同曲解/3=准确但平铺/5=准确且显题旨脉络；threshold >=4；证据：独立审查。
- **Notes**: 写权限同 Task 1（仅 doctrine/ 目录）。

## Task 3: 束3 修养工夫与现代实践（gongfu）端到端建设
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 委托独立代理在 `doc/bundles/think/yangming/gongfu/` 建成 14 文件束（facts.md、insights.md、log.md、index.md；concepts/00-overview.md（工夫论总纲：头脑-工夫-效验）、01-lizhi.md（立志："志不立，天下无可成之事"）、02-jingzuo.md（静坐澄心、省察克治之别、阳明对枯坐之弊的警惕）、03-shishang-molian.md（事上磨练："人须在事上磨，方立得住"）、04-xingcha-kezhi.md（省察克治、存天理去人欲、慎独诚意、知行合一为工夫）、concepts/index.md；examples/01-modern-practice-30days.md（**现代人 30 天心学工夫实践手册**：立志句/每日省察日记格式/事上磨练任务库/知行合一微挑战/每周复盘，可直接执行）+index；references/sources.md+index）。
  - R：工夫论述原文均出《传习录》（静坐、事上磨、省察克治诸条）与《教条示龙场诸生》（立志/勤学/改过/责善），双源核对；现代转化部分显式标注为"现代实践设计"而非古文原意。
  - I/E：≥3 洞察（如"静坐-事磨的辩证：阳明晚年以事上磨为正鹄"）+ ≥2 模式（如"经典工夫论的现代实践转化模板"）。
  - frontmatter 体例同 Task 1。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: 14 文件落盘、frontmatter 合规；证据：枚举+yaml 扫描。
  - `rule` TR-3.2: 工夫类引文双源核对、现代实践与古典原意分层标注不混淆；证据：facts/log 审查。
  - `rule` TR-3.3: toctree 完整；证据：门控过滤 gongfu 为空。
  - `rubric` TR-3.4: 30 天实践手册可执行性（每日任务具体、可打卡、可复盘）；scale 1-5；anchors 1=空泛口号/3=有框架但不可执行/5=30 天逐日可操作；threshold >=4；证据：独立审查。
- **Notes**: 写权限仅 gongfu/ 目录；本束直接承载用户"进修提升能力"诉求，质量分权重最高。

## Task 4: 束4 生平与成学历程（biography）端到端建设
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 委托独立代理在 `doc/bundles/think/yangming/biography/` 建成 14 文件束（facts.md、insights.md、log.md、index.md；concepts/00-overview.md（"五溺三变"总览：黄宗羲《明儒学案》"学凡三变/教三变"框架）、01-life-chronology.md（1472 余姚出生—1506 忤刘瑾廷杖—1508 龙场—1517 巡抚南赣—1519 平宸濠—1521 致良知—1527 天泉证道—1529 南安卒，"此心光明，亦复何言"）、02-longchang-awakening.md（龙场悟道始末："圣人之道，吾性自足"）、03-shigong.md（事功：平漳南/横水/桶冈/浰头、《南赣乡约》、社学、43 天平宁王宸濠、平思田破八寨）、04-tianquan-and-final.md（天泉证道、严滩问答、临终遗言与从祀孔庙 1584）、concepts/index.md；examples/01-chronology-map.md（大事年表+地理研读地图+每阶段对应阅读篇目）+index；references/sources.md+index（《王阳明年谱》、《明史·王守仁传》、冈田武彦《王阳明大传》等））。
  - R：关键年代/事件双源核对（年谱 × 明史本传/权威传记）；"此心光明"等名言核对出处（年谱/《全书》）。
  - I/E：≥3 洞察（如"悟道-事功-立教三线互证：心学是逆境中逼出的实践哲学"）+ ≥2 模式。
  - frontmatter 体例同 Task 1。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-4.1: 14 文件落盘、frontmatter 合规；证据：枚举+yaml 扫描。
  - `rule` TR-4.2: 年代/事件零硬伤（1472/1506/1508/1517/1519/1521/1527/1529/1584），名言出处可回溯；证据：facts 双源记录。
  - `rule` TR-4.3: toctree 完整；证据：门控过滤 biography 为空。
  - `rubric` TR-4.4: 叙事可读性与"生平-思想"互证清晰度；scale 1-5；threshold >=4；证据：独立审查。
- **Notes**: 写权限仅 biography/ 目录。

## Task 5: 束5 源流·后学·东亚影响（lineage）端到端建设
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 委托独立代理在 `doc/bundles/think/yangming/lineage/` 建成 15 文件束（facts.md、insights.md、log.md、index.md；concepts/00-overview.md（谱系总图：孟子→陆九渊→王阳明→后学七派→东亚/近现代）、01-sources-mengzi-luxiang.md（思想来源：孟子良知良能/万物皆备、陆九渊心即理/鹅湖之会、陈献章湛若水汽门、出入佛老三十年）、02-zhu-wang-divergence.md（朱王异同：格竹事件、《朱子晚年定论》及其争议（陈建《学蔀通辨》）、心即理 vs 性即理、格物分歧）、03-disciples-schools.md（后学分化：浙中王畿/钱德洪、江右邹守益/罗洪先/聂豹、泰州王艮→李贽、止修李材，《明儒学案》分派）、04-critique-revival.md（明清反思：刘宗周慎独、黄宗羲《明儒学案》、顾炎武/王夫之批判；近代复兴：梁启超、孙中山"知难行易"、蒋介石/阳明山、毛泽东《实践论》知行观）、05-east-asia-modern.md（日本阳明学：中江藤树→吉田松阴/西乡隆盛与明治维新；韩国郑齐斗江华学派；现代：稻盛和夫敬天爱人、杜维明新儒家、"阳明学"学科命名东渡回流）、concepts/index.md；examples/01-study-path.md（读物分级：入门/进阶/研究三级书单 + 五阶段进学路径，与束1阅读计划衔接）+index；references/sources.md+index）。
  - R：学派人物/年代双源核对；争议性论断（《朱子晚年定论》取舍、日本阳明学与明治维新关系强度）并列 ≥2 说。
  - I/E：≥3 洞察（如"阳明学的两次下行：泰州学派民间化与日本志士行动化"）+ ≥2 模式。
  - frontmatter 体例同 Task 1。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 15 文件落盘、frontmatter 合规；证据：枚举+yaml 扫描。
  - `rule` TR-5.2: 人物/年代/学派归属与《明儒学案》等权威信源一致，争议并列；证据：facts 审查。
  - `rule` TR-5.3: toctree 完整；证据：门控过滤 lineage 为空。
  - `rubric` TR-5.4: 谱系图清晰度与书单分级实用性；scale 1-5；threshold >=4；证据：独立审查。
- **Notes**: 写权限仅 lineage/ 目录。

## Task 6: 组索引与共享索引注册（主控串行）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 新建 `doc/bundles/think/yangming/index.md`（type: group；组总纲；mermaid 谱系图：文本 chuanxilu→义理 doctrine→工夫 gongfu，生平 biography 与源流 lineage 为两翼；5 束导航表；cross-ref 指向 ../confucian/four-books/index.md（《大学》《孟子》为经典依据）、../buddhism/index.md（禅宗影响）、../daojia/index.md（出入佛老）；toctree 收录 5 束 index）。
  - 更新 `doc/bundles/think/index.md`：域导航表增加 yangming 行（📜 王阳明心学）、toctree 增 `yangming/index`、description 补"王阳明心学/传习录"。
  - 更新 `doc/bundles/index.md`：think 域节表增 yangming 行（束数 5）；frontmatter 计数与节标题按**目录树地面真值**更新（新增后：total_bundles 353、groups 72、domains 16；think 节标题 48 束·25 组；think 表束数列和含 vocal 地面真值差由门控确认残余项仅 vocal/workplace）。
  - 编辑前重读共享索引当前工作区版本（并行会话可能已改动），只做增量编辑、不重写他人内容。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-6.1: yangming/index.md 存在且 toctree 收录 5 束；证据：文件+门控。
  - `rule` TR-6.2: check-toctrees 输出中 yangming 相关失败为 0；证据：门控过滤。
  - `rule` TR-6.3: check-bundles-index 输出中 yangming 相关失败为 0，计数=地面真值；残余失败仅 vocal/workplace；证据：门控全文。
- **Notes**: 不注册 vocal/workplace（用户决策）；不改动 confucian/index.md。

## Task 7: V 阶段——对抗审查、门控全量验证与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 运行 `python scripts/check-utf8.py`、check-toctrees.py、check-bundles-index.py 并完整存档输出。
  - 运行 yaml.safe_load 全束 frontmatter 扫描（73 文件），rc=0。
  - 断链检查：束内/跨束/组索引全部相对链接有效。
  - 引文抽查 ≥15 段逐条回溯双源记录；关键年代/人名/事件核对；发现问题回 T1–T5 修复（materialize 为 issue 后返工）。
  - 可选：`python -m sphinx -b dummy doc _build/dummy` 构建验证（环境可用时）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 三门输出中 yangming 相关失败为 0；utf8 零违规；证据：门控存档。
  - `rule` TR-7.2: yaml 扫描 rc=0；断链零命中；证据：扫描输出。
  - `rule` TR-7.3: 引文抽查 ≥15 段零虚构；证据：审查记录。
  - `rubric` TR-7.4: 全库一致性（跨束同引文不矛盾、F/R 编号自洽）；scale 1-5；threshold >=4；证据：主控核查。
- **Notes**: 修复后重跑至稳定；残余 vocal/workplace 红灯如实记录、不修复。

## Task 8: C 阶段——子模块本地原子提交
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 在 `projects/awesome-okf-xs` 子模块内：先 `git status`/查 MERGE_HEAD；**显式 add** 仅 73 个新文件 + doc/bundles/index.md + doc/bundles/think/index.md（用正斜杠路径）；add 与 commit 分两次工具调用，中间 `git diff --cached --name-only` 核对暂存集无 vocal/workplace/其他混入；混入则不提交并报告。
  - 提交信息：`docs(bundles): 新增王阳明心学知识包（传习录/义理/工夫/生平/源流五束）`（Conventional Commits 中文主体）。
  - 不 push；不操作主仓 gitlink（推送闸门统一调度）。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-8.1: `git show --stat HEAD` 文件清单 = 73 新文件 + 2 共享索引，无其他文件；证据：git show 输出。
  - `rule` TR-8.2: 无 push 行为（无远端交互）；证据：命令记录。
- **Notes**: 遵循记忆库共享索引竞态纪律；若暂存集异常立即停止。
