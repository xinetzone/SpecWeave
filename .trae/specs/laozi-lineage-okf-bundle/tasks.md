# 《老子》传本源流谱系 OKF 知识包 - 实现计划（拆解与优先级任务清单）

> 方法论链路：七概念场景 4（知识沉淀）**R → I → E → V → 入库**。
> 执行约定：每个任务委托单个子代理完成，一次只推进一个任务；任务完成后由独立验证子代理按 checklist.md 黑盒验证，通过后再标记 completed。

## [x] Task 1: Bundle 脚手架与信源登记簿
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `bundles/laozi-lineage/` 下创建目录结构：`manuscripts/`、`archaeology/`、`variants/`、`methodology/`、`references/`。
  - 创建根 `index.md`（带 `---\nokf_version: "0.2"\n---` frontmatter，按子目录分组列出占位条目）。
  - 创建根 `log.md`（含 `## 2026-08-20` 下的 `**Creation**` 条目）。
  - 在 `references/` 下创建 `index.md` 与至少 10 个信源概念文档，每个为 `type: Reference`，frontmatter 含 `title`/`resource`（ISBN 或 DOI 或机构 URL）/`author`/`tags`/`generated`/`status: stable`，正文简述该信源的学术价值与适用范围。
  - 信源清单（至少覆盖）：高明《帛书老子校注》、荆门市博物馆《郭店楚墓竹简》、国家文物局古文献研究室《马王堆汉墓帛书（壹）》、湖南省博物馆等《长沙马王堆汉墓简帛集成》、北京大学出土文献研究所《北京大学藏西汉竹书（贰）》、楼宇烈《王弼集校释》、饶宗颐《老子想尔注校证》、陈鼓应《帛书老子注译与研究》、彭浩《郭店楚简老子校读》、Henricks《Lao Tzu's Te-Tao Ching》。
  - 对每条信源通过网络检索核实 ISBN/出版年/出版社，无法核实的字段标注"待核"而非编造。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录树存在 5 个子目录且每个含 `index.md`；根 `index.md` frontmatter 含 `okf_version: "0.2"`。
  - `programmatic` TR-1.2: `references/` 下 ≥10 个 `.md` 概念文件（不含 index.md/log.md），每个 frontmatter 可被 YAML 解析且 `type: Reference`、`resource` 非空。
  - `human-judgement` TR-1.3: 审查者抽查 3 条信源，ISBN/URL 真实可核查，作者/出版社/年份与实际一致；发现编造则判失败。
- **Notes**: 信源登记簿是后续所有概念 `sources` 字段的引用基础，id 必须稳定（建议 kebab-case，如 `gao-ming-boshu-jiaozhu`）。

## [x] Task 2: R 阶段 — 考古语境概念（2 个）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `archaeology/mawangdui-tomb-3.md`（`type: Archaeological Site`）：马王堆三号汉墓，墓葬年代公元前 168 年（汉文帝前元十二年），墓主利豨（第二代轪侯），出土位置（长沙东郊），椁室头箱漆奁内帛书存放情况，共存文献（《周易》《战国纵横家书》等），纪年木牍证据。
  - 创建 `archaeology/guodian-tomb.md`：郭店一号楚墓，墓葬年代约公元前 300 年（战国中期偏晚，楚 culture），墓主身份争议（一般认为是楚太子老师或下大夫级贵族），出土位置（湖北荆门沙洋），竹简出土位置（头箱），共存文献（《五行》《缁衣》《太一生水》等 16 篇）。
  - 正文纯客观事实陈述（G1 质量门：无"因为/导致/所以"因果词），每条事实带 `[^source-id]` 脚注引用 Task 1 信源。
  - frontmatter 含 `type`/`title`/`description`/`tags`/`generated: { by: reference_agent/trae-glm, at: 2026-08-20T... }`/`verified: { by: process:seven-concepts-R, at: ... }`/`status: stable`/`sources` 列表。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: 两个文件 frontmatter 均可解析，`type` 分别为 `Archaeological Site`，`sources` 至少各 2 条。
  - `human-judgement` TR-2.2: G1 质量门——正文无因果推断词（"因为/导致/所以/因而/从而"），纯客观描述；墓主"利豨"标注为学界主流考订而非绝对事实；郭店墓主身份标注争议。
  - `human-judgement` TR-2.3: 每条事实性语句可在脚注信源中找到对应依据；年代数字（前 168、前 300）有明确文献支持。

## [x] Task 3: R 阶段 — 出土抄本概念（4 个）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 创建 `manuscripts/guodian-chu-jian.md`（郭店楚简本《老子》）：约前 300 年，现存最早实物，三组（甲/乙/丙）节选本非全本，约 2000 字（现存全本约 5000 字），楚系文字，无篇序概念（节选），不避汉讳（早于汉），与传世本文字差异大。
  - 创建 `manuscripts/mawangdui-jia.md`（帛书甲本）：抄写年代约高祖至惠帝期（前 206-前 188），篆隶过渡字体，**不避高祖刘邦讳**（"邦"字多见），不避文帝刘恒讳（"恒"字多见），德经在前道经在后，残损较重但大部分可读，与乙本异文众多证明非同一底本。
  - 创建 `manuscripts/mawangdui-yi.md`（帛书乙本）：抄写年代约惠帝至吕后期（前 194-前 180），成熟汉隶，**避高祖讳**（"邦"改"国"），不避文帝讳，德前道后，残损较甲本轻，卷前另抄有《五行》等古佚书。
  - 创建 `manuscripts/beida-han-jian.md`（北大汉简本《老子》）：约汉武帝中后期（前 100 左右），2009 年北京大学接受捐赠入藏（非考古发掘，出土地点缺失），76 章（现存 76，缺约 4 章），近 5300 字，德前道后，分章规整有章节符号，是连接帛书本与传世本的关键中间环节。
  - 每个概念含统一小节：`# 基本信息`（年代/材质/字体/字数章数/篇序/完残/藏地）、`# 避讳特征`、`# 文本特征`、`# 整理与出版`、`# 谱系位置`。
  - G1：事实无因果词；每条事实带脚注；链接到对应考古语境概念（`../archaeology/xxx.md`）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-3.1: 4 个文件存在，`type: Manuscript`，每个 `sources` ≥3 条，正文中至少 1 个 bundle 内交叉链接。
  - `human-judgement` TR-3.2: G1 通过（无因果词）；甲本"不避邦讳"与乙本"避邦讳"的对比描述准确，有避讳字实例引用；北大简"非考古发掘、出土地点缺失"作为局限性明确写出。
  - `human-judgement` TR-3.3: 年代推断（甲本早于乙本）基于避讳证据而非臆测，逻辑链在"避讳特征"小节可见。

## [x] Task 4: R 阶段 — 传世注本概念（4 个）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `manuscripts/heshanggong-zhu.md`（河上公注本）：题名汉河上公撰，实际成书年代学界争议（有东汉说/魏晋说），81 章，道前德后，与帛书本系统相对较近，是道教系统重要传本，严遵《指归》或受其影响。**必须设"争议与不确定性"小节**。
  - 创建 `manuscripts/xiang-er-zhu.md`（《老子想尔注》）：题名张道陵（或张鲁）注，东汉末至三国（约 2 世纪），敦煌残卷（S.6825）保存道经部分，是早期天师道重要文献，避讳/用字反映东汉晚期特征，作者归属有争议。
  - 创建 `manuscripts/wangbi-zhu.md`（王弼注本）：王弼（226-249）魏玄学家注，81 章道前德后，是**通行本之祖**，后世绝大多数传本（含当代楼宇烈校释本）以此为底本，文字与帛书本差异较大，代表魏晋玄学化文本。
  - 创建 `manuscripts/fuyi-jiao.md`（傅奕校定本）：唐傅奕（555-639）校定，据北齐武平五年（574）彭城人开项羽妾冢得传本（"项羽妾本"），81 章，文字古奥，保留若干与帛书本/北大本相近的异文，是追溯汉唐古本面貌的重要参照。
  - 每个概念含：`# 基本信息`、`# 注者与成书`、`# 文本特征`、`# 版本源流`、`# 争议与不确定性`（如适用）。
  - 链接到相关异文概念（Task 5 将创建，先用相对路径链接，容忍断链）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-4.1: 4 个文件存在，`type: Manuscript`，每个 `sources` ≥2 条。
  - `human-judgement` TR-4.2: 河上公成书年代、想尔注作者两个争议点均有"争议与不确定性"小节并列 ≥2 种观点及代表学者，不做单一断言（AC-6）。
  - `human-judgement` TR-4.3: 王弼本"通行本之祖"定位准确；傅奕本"项羽妾冢"来源记载标注为文献传说而非考古实证。

## [x] Task 5: I+V 阶段 — 关键异文概念（4 个）
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 创建 `variants/taboo-bang-guo.md`：邦/国避讳——甲本用"邦"不避，乙本及以下避高祖刘邦讳改"国"；作为断代硬证据区分甲本（前 206 前或汉初不严格避讳期）与乙本（汉初避讳制度化后）；含各本对照表。**I 四元组**：现象（甲乙本邦/国差异）+ 根因（汉初避讳制度）+ 影响（断代依据）+ 建议（据避讳字推定相对年代需结合其他证据）。
  - 创建 `variants/taboo-heng-chang.md`：恒/常避讳——甲乙本均作"恒"不避文帝刘恒讳，证明两本抄写均早于文帝即位（前 180）或不受避讳约束；传世本作"常"；这是帛书本早出的铁证之一。
  - 创建 `variants/de-dao-chapter-order.md`：德经/道经篇序——甲乙本、北大本均德经在前（第 38-81 章在前，1-37 在后），与《韩非子·解老》《喻老》引述顺序一致；传世本道经在前；篇序翻转发生在两汉之际至魏晋；哲学意义（德论为入口 vs 道论为入口）。
  - 创建 `variants/daqi-mian-cheng.md`：大器免成（帛书乙本，第 41 章）vs 大器晚成（通行本）——"免"释为"免成"即"大器不成/无成"（与"大音希声、大象无形"并列的否定式哲学），"晚成"为后世误读或传抄之变；学界有不同释读意见（"免"通"晚"说 vs "免成"说），V 阶段需呈现争议。
  - 每个异文概念含：`# 异文对照`（各本文字表）、`# 断代/谱系意义`（I 四元组）、`# 争议与不确定性`（V 对抗审查结果）、`# 关联传本`（链接）。
  - G2：每个异文洞察含完整四元组（现象/根因/影响/建议）；V：对过度诠释做攻击，"大器免成"不得断言为唯一正解。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-5.1: 4 个文件存在，`type: Textual Variant`，每个含异文对照表（Markdown 表格）且 `sources` ≥2 条。
  - `human-judgement` TR-5.2: G2 质量门——每个异文的"断代/谱系意义"小节明确包含现象、根因、影响、建议四要素。
  - `human-judgement` TR-5.3: V 对抗审查——"大器免成"呈现"免成"与"免通晚"两说，不做单一断言；篇序翻转的具体时间标注为"两汉之际至魏晋逐渐定型"而非精确年份。
  - `human-judgement` TR-5.4: 避讳异文有具体字例（引用原文字形或隶定字），非泛泛而谈。

## [x] Task 6: E+V 阶段 — 方法论模式概念（2 个）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 创建 `methodology/taboo-character-dating.md`（`type: Methodology Pattern`）：避讳断代法——
    - 触发场景：出土/传抄文献需推定抄写年代；
    - 核心步骤：① 识别讳字（邦/国、恒/常、启/开、彻/通、弗/不等）② 对照避讳帝系（高帝邦、文帝恒、景帝启、武帝彻、元帝奭等）③ 确定时代上下限 ④ 结合字体/材质/共存物交叉验证；
    - 反模式：单靠避讳断代而忽略"不避讳可能是抄手随意而非早出"、"后世仿古本不避旧讳"、"避讳改字回改"；
    - 迁移验证：本方法在《老子》甲乙本的成功应用（邦/恒讳），可迁移至其他出土简帛（如《黄帝四经》《周易》帛书本）。
  - 创建 `methodology/manuscript-transmission-lineage.md`（`type: Methodology Pattern`）：传本源流重建法——
    - 触发场景：多部异本需重建亲缘关系；
    - 核心步骤：① 建立异文对照表 ② 识别共享异文簇（shared errors/readings）③ 据避讳/字形定相对年代 ④ 绘制谱系树（stemma）⑤ 用外部证据（引文、目录著录）校验；
    - 反模式：把"文字较古"直接等同于"本子较古"、忽略平行演化、把节选本（郭店）当作全本谱系节点；
    - 迁移验证：《老子》谱系（郭店→帛书→北大→传世）是标准案例，方法可迁移至《墨子》《管子》等多传本文献。
  - 每个含：`# 触发场景`、`# 核心步骤`、`# 反模式`、`# 迁移验证`、`# 在《老子》谱系中的应用`。
  - G3：模式可迁移（有触发条件+核心步骤+反模式+迁移验证四要素）。
  - V：用魔鬼代言人视角攻击——避讳断代法的局限（仿古不讳、回改）、谱系重建的主观性（异文选择偏差）必须在反模式中体现。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: 2 个文件存在，`type: Methodology Pattern`，每个含 5 个规定小节标题。
  - `human-judgement` TR-6.2: G3 质量门——每个模式四要素齐全（触发/步骤/反模式/迁移），且迁移验证引用《老子》之外的至少 1 个可迁移目标。
  - `human-judgement` TR-6.3: V 审查——反模式不是泛泛而谈，至少各含 2 条具体陷阱（如"避讳回改""仿古不讳"）。

## [ ] Task 7: 交叉链接、索引、日志与最终一致性验证
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 回填所有概念的交叉链接：传本→考古语境、传本→相关异文、异文→关联传本、方法论→具体传本案例；确保关键链接不断（OKF 容忍断链但本 bundle 追求关键路径连通）。
  - 重新生成各子目录 `index.md`（无 frontmatter，按概念分组，每条含标题+description）。
  - 更新根 `index.md`：反映最终概念清单，含 bundle 简介、OKF 版本、概念数量统计。
  - 更新 `log.md`：追加各任务完成的 Update 条目（按日期倒序）。
  - 运行 OKF §11 一致性自查：① 每个非保留 `.md` 含可解析 frontmatter ② 每个 frontmatter 含非空 `type` ③ `index.md`/`log.md` 结构合规。
  - 运行溯源自查：扫描所有正文脚注 `[^id]`，确认每个 id 在同文件 `sources` 中存在；扫描 `sources[].resource`，确认无空值、无"待核"遗留（"待核"项必须显式标注而非伪造）。
  - 运行链接自查：确认 bundle 内交叉链接目标文件存在。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-7.1: 脚本扫描所有 `.md`，frontmatter 解析成功率 100%，`type` 非空率 100%，无文件违反保留文件名。
  - `programmatic` TR-7.2: 所有正文 `[^id]` 脚注在同文件 `sources[].id` 中可匹配（孤立脚注为 0）；所有 bundle 内相对链接目标存在（断链数 = 0，对关键链接）。
  - `human-judgement` TR-7.3: 审查者通读根 `index.md` 与各子目录 `index.md`，确认描述准确、分组合理、无遗漏概念；`log.md` 日期倒序且条目完整。
  - `human-judgement` TR-7.4: 最终 bundle 概念总数 ≥ 22（8 传本 + 2 考古 + 4 异文 + 2 方法论 + ≥10 信源 + 6 个 index/log ≈ 32 文件，其中概念 ≥26）。
- **Notes**: 本任务是 G4 原子化交付的收尾——bundle 作为一个整体可被消费。完成后由独立验证子代理执行 checklist.md 全量黑盒验证。
