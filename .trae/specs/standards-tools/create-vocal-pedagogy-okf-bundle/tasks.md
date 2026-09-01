# 声乐教学（美通唱法+咽音体系）OKF 知识束 - 实施计划

> 方法论链路（七概念·知识沉淀场景）：R 事实采集（T1）→ I 洞察/E 萃取（T2）→ 内容撰写（T3-T5）→ 注册与验证（T6-T7）→ C 原子提交（T8）→ V 独立评审（T9）。

## Task 1: R 阶段——双路事实采集与 facts.md
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 双路子代理并行 Web 调研（信息边界隔离，输出不重叠）：
    - 轨 A「咽音体系轨」：意大利 Voce faringea 源流（阉人歌手时代、卡鲁索经验谈）；林俊卿生平（生卒年、福建/厦门籍、1940 协和医学博士、1941 后从意大利教师鲍那维塔等学声乐）；上海声乐研究所成立年（1954/1957 异说核验）与周恩来拨款；十年 97 学员；文革"骗术"批判；著作三书（《歌唱发音的机能状态》《歌唱发音不正确的原因及纠正方法》1960s、《咽音练声的八个步骤》出版年/出版社）；六步骤→八步骤演进；八步骤逐项动作要领与达标标准；师承（潘乃宪 1956 所长助理、钟振发/王福增/廖一明/罗荣钜等后学核验）；嗓音治疗案例（王昆、那英等说法核验）。
    - 轨 B「美通与教学法轨」：三种唱法制度史（1986 第二届青歌赛分设、2006 原生态、2013 第十五届取消分法核验）；金铁霖生平（1940-2022、中国音乐学院、七字标准、四性、三个阶段、混声/U 通道/支点/启发式感觉教学、学生名单、2011"中国声乐"概念）；潘乃宪生平（昆剧出身、1956 上海声乐研究所所长助理、著作年表 1994/1997/1999/2002/2010、辨证施治体系、学生毛阿敏等、2022-12-28 去世）；"美通"术语语境（金铁霖论文集"民通/通民/美通/美民"列举、乐天"创始人"自称的辨析）；沈湘体系（《歌唱学——沈湘歌唱学体系研究》邹本初）；现代嗓音科学（歌手共振峰 2800–3200 Hz、vocal fry/气泡音、声带小结）；海外体系（SLS Seth Riggs、Estill Voice Training）。
  - 汇总为 `think/vocal/meitong-yanyin-pedagogy/facts.md`：F 编号 ≥ 70 条，八组分类，纯客观陈述（G1 门：无因果推断词），信源 URL 逐条内嵌；P0 事实双源核验表附后。
  - 同步创建 `think/vocal/index.md`（group 级）与束根 `index.md` 骨架（frontmatter + toctree）。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 存在且 F 编号连续 ≥ 70 条；P0 事实（生卒年/机构年/出版年/八步骤/1986 青歌赛）每条 ≥ 2 独立信源 URL，单源项显式标注"单源/存疑"
  - `rule` TR-1.2: facts.md 全文无"因为/导致/所以"因果推断（G1 事实门），引文转述与事实陈述分开
  - `rubric` TR-1.3: 信源质量；scale 1-5；anchors: 1=仅自媒体/营销号; 3=百科+媒体混合; 5=出版社/学术期刊/央视党媒/权威机构为主、百科仅作线索; threshold >= 4；evidence: references 信源分级表

## Task 2: I/E 阶段——insights.md 与三层 index 骨架
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T1
- **Description**:
  - 撰写 `insights.md`：声乐教学知识地图核心洞察（"美通为用、咽音为体"主线；机能训练与风格表达分层；咽音八步骤的脚手架本质；自学边界与安全红线；术语门派辨析），每条洞察含现象/根因/影响/建议四元组（G2 门）。
  - 创建 `concepts/index.md`、`examples/index.md`、`references/index.md` 导航骨架（含 toctree 占位，随 T3-T5 填充）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-2.1: insights.md 含 ≥ 5 条洞察，每条具备现象/根因/影响/建议四要素
  - `rule` TR-2.2: 三个子目录 index.md 存在且 toctree 条目与实际文件一一对应（T7 门控复验）

## Task 3: E 阶段——10 篇概念文档
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - 按 FR-2 撰写 concepts/00-09；每篇 frontmatter（type: Concept、sources 指向 /facts.md 与外部信源）、正文结构统一（是什么→原理/机理→怎么教/怎么练→常见错误→相关概念链接）。
  - 05/06 八步骤两篇为教学核心：逐步骤给"动作要领+达标标准+常见错误+剂量"四要素。
  - 08 篇显式安全提示（嗓音病变就医、自学红线）。
- **Acceptance Criteria Addressed**: AC-2, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 10 篇文件齐备，每篇含非空 type frontmatter 与 sources 字段
  - `rubric` TR-3.2: 教学可操作性；scale 1-5；anchors 同 AC-6；threshold >= 4；evidence: 05/06/07 四要素齐备检查
  - `rubric` TR-3.3: 事实与 facts.md 一致（无 F 编号之外的新数字断言）；scale 1-5；threshold >= 4

## Task 4: 实操文档 2 篇
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T3
- **Description**:
  - `examples/01` 每日 20–30 分钟练声清单：八步骤剂量表（晨起/睡前时段、次数时长）、自检标准、红线。
  - `examples/02` 八周自学路线图：周目标、重点练习、美通曲目选择建议、阶段自检。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 2 篇齐备，练习项均可回溯到 concepts/05/06 的步骤定义
  - `rubric` TR-4.2: 可照做程度；scale 1-5；anchors 同 AC-6；threshold >= 4

## Task 5: 信源文档 3 篇
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: T3
- **Description**:
  - references/01 著作教材、02 嗓音科学与海外体系、03 机构人物赛事史料；每条信源含标题/作者/出版者/年/URL/可信度分级/用途。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-5.1: 3 篇齐备；facts.md 引用的全部外部信源在 references 中可查
  - `rule` TR-5.2: 信源分级标注完整（权威/学术/媒体/网络）

## Task 6: 索引注册
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T4, T5
- **Description**:
  - `think/index.md`：导航表追加声乐教学行（置于 daojia 行后）、toctree 追加 `vocal/index`、description 补入声乐教学。
  - `doc/bundles/index.md`：frontmatter 改 total_bundles 348/groups 70/domains 15；正文计数行同步；think 节标题改「43 束 · 24 组」；think 分组表追加声乐教学行（束数 1）；两处 mermaid think 节点标签补 vocal。
  - 编辑前重读工作树最新版（并行会话可能再改动），只做追加/计数更新。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-6.1: think/index.md 导航行 + toctree 含 vocal；bundles/index.md 五面计数一致（由 T7 门控机械判定）
  - `rule` TR-6.2: 不触碰 think/daojia 下任何文件（git diff 核对）

## Task 7: 门控与构建验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T6
- **Description**:
  - 运行 check-utf8 / check-toctrees / check-bundles-index 三门；全束 frontmatter 做 yaml.safe_load 扫描（双引号嵌套兜底）；运行 sphinx dummy 构建对比基线 warning。
  - 失败即修复重跑直至全绿。
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: 三脚本退出码 0，bundles 对账输出 15 域/70 组/348 束
  - `rule` TR-7.2: yaml.safe_load 解析全束 frontmatter 无异常；sphinx dummy 构建无新增 myst.topmatter/断链 warning

## Task 8: C 阶段——原子提交（仅本束文件）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: T7
- **Description**:
  - 先 `git add` 仅本束路径（doc/bundles/think/vocal/、doc/bundles/think/index.md、doc/bundles/index.md）；**单独**跑 `git diff --cached --name-only` 核对暂存集；若混入 daojia 或他方文件则不 commit、停止报告。
  - 暂存集干净后提交：`docs(bundles): 新增声乐教学知识束（美通唱法与咽音体系教学教程）`，正文中文说明结构与信源。不推送。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-8.1: 暂存集仅含 think/vocal/** + think/index.md + bundles/index.md；commit 成功且不含他方文件
  - `rule` TR-8.2: 提交后三门复跑仍全绿

## Task 9: V 阶段——独立只读评审
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: T8
- **Description**:
  - 新上下文只读评审代理：依据 spec.md AC 逐项核验（三门证据、文件结构、P0 双源抽查 10 条事实对照信源、教学四要素抽查、frontmatter/链接规范、提交隔离）。
  - 结果 fail 则物化为 Issue 回 T3-T7 修复后重新评审；pass 则收尾。
- **Acceptance Criteria Addressed**: AC-1..AC-9（独立复核）
- **Test Requirements**:
  - `rule` TR-9.1: review.md 记录全部 checkpoint 与证据，最终 Result = pass
  - `rubric` TR-9.2: 事实抽查准确率；scale 1-5；threshold >= 4（10 条 P0 抽查 ≤ 1 条轻微措辞问题）
