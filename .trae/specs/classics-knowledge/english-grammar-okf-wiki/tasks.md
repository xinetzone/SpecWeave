# 旋元佑英语语法 OKF Wiki 教程 - The Implementation Plan (Decomposed and Prioritized Task List)

> 方法论链路：知识沉淀场景 R→I→E→V→C（事实采集→架构洞察→批量生成→独立验证→模式沉淀）

## [ ] Task 1: R阶段 - 事实采集与文档盘点
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 通读 english-grammar 目录下所有文件，建立完整的文件清单
  - 读取尚未探索的文件（guide.md、intro.md已读，其余23章+术语表待读）
  - 提取编号事实清单 F-xxx，包括：文档数量、章节主题、MyST语法使用情况、表格/例句/特殊格式分布
  - 确认 guide.md 的内容定位（使用指南/导读/术语说明？）
  - 确认 appendix/terminology.md 的内容和定位
  - 所有事实写入 `<spec-dir>/facts.md`，严格遵循零推测原则（G1质量门）
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 包含所有 30 个文件的完整清单，每个文件记录路径、字数估计、主题分类
  - `programmatic` TR-1.2: 事实中无"用于"/"目的是"/"设计为"等推断性表述
  - `human-judgment` TR-1.3: 文件分类（概念/示例/信源）合理，与内容匹配
- **Notes**: 这是R阶段核心任务，为后续I/E/V阶段提供事实基础。必须先读完全部文件再生成事实清单。

## [ ] Task 2: I阶段 - 架构洞察与知识地图设计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单，提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组）
  - 设计知识地图：文档分组（入门篇/基础篇/进阶篇/高级篇/附录）
  - 确定学习路径顺序：建议按原书章节顺序（01→25）
  - 确定每个概念文档覆盖的 F-xxx 事实
  - 设计文件名编号规则：NN-topic-name.md（如 00-preface.md, 01-simple-sentences.md）
  - 确定交叉链接策略（章末相关概念章节）
  - 洞察写入 `<spec-dir>/insights.md`
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgment` TR-2.1: 洞察四元组完整（陈述+证据+反常识+行动）
  - `human-judgment` TR-2.2: 知识地图分组逻辑合理，学习路径清晰
  - `programmatic` TR-2.3: 所有 30 个文档都被分配到某个分组并有对应编号
- **Notes**: 这是I阶段核心任务。分组建议：入门篇（序/引言/指南/术语表）、基础篇（01-08）、进阶篇（09-16）、高级篇（17-25）

## [ ] Task 3: E阶段-1 - 创建Bundle目录结构与references信源
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 `bundles/chaos/english-grammar/` 下创建标准 OKF 目录结构
  - ⚡ 信源先行：先生成 references/ 目录下的所有信源登记文件
    - references/index.md
    - references/insights.md（架构洞察）
    - references/facts.md（事实清单）
    - 为每个原始文件创建信源登记文件（如 references/source-preface.md 等），记录原始路径、作者、来源
  - 创建 log.md 变更日志
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-3.1: 目录结构完整（concepts/examples/references + index.md/log.md）
  - `programmatic` TR-3.2: references/ 下所有文件创建完成，sources字段格式正确
  - `programmatic` TR-3.3: 子目录 index.md 不含 frontmatter（仅根index.md保留okf_version）
  - `human-judgment` TR-3.4: 信源文件元数据准确（路径/作者/来源信息）
- **Notes**: ⚠️ references/ 必须先于 concepts/ 生成，这是信源先行原则

## [ ] Task 4: E阶段-2 - 生成第一批概念文档（入门篇+基础篇01-07）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成，每批≤7文件，本批包含：
    - 00-preface.md（序）
    - 01-reading-approach.md（引：广读学英语）
    - 02-grammar-guide.md（guide，待Task1确认内容）
    - 03-terminology.md（术语表）
    - 04-simple-sentences.md（第一章：基本句型）
    - 05-noun-phrases.md（第二章：名词短语）
    - 06-pronouns.md（第三章：代词）
  - 每个文档：添加完整frontmatter、转换MyST语法为标准Markdown、添加sources字段、添加「相关概念」章末导航
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 7个文件全部创建，frontmatter字段完整
  - `programmatic` TR-4.2: 无残留MyST语法（{toctree}/{note}/```{ 等）
  - `programmatic` TR-4.3: 交叉链接使用/开头路径，目标文件存在（已生成的文件）
  - `human-judgment` TR-4.4: 内容与原文一致，无遗漏或篡改
- **Notes**: 严格控制每批≤7文件，防止上下文过载

## [ ] Task 5: E阶段-3 - 生成第二批概念文档（基础篇08-14）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 第二批（7个文件）：
    - 07-adjectives.md（第四章：形容词）
    - 08-adverbs.md（第五章：副词）
    - 09-comparative-patterns.md（第六章：比较句型）
    - 10-prepositions.md（第七章：介词）
    - 11-participles.md（第八章：分词）
    - 12-verb-tenses.md（第九章：动词时态）
    - 13-voice.md（第十章：被动语态）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 7个文件全部创建，frontmatter字段完整
  - `programmatic` TR-5.2: 无残留MyST语法
  - `programmatic` TR-5.3: 交叉链接格式正确
  - `human-judgment` TR-5.4: 内容完整保留

## [ ] Task 6: E阶段-4 - 生成第三批概念文档（进阶篇15-21）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 第三批（7个文件）：
    - 14-auxiliaries.md（第十一章：助动词）
    - 15-moods.md（第十二章：语气）
    - 16-gerunds.md（第十三章：动名词）
    - 17-infinitives.md（第十四章：不定词）
    - 18-conjunctions.md（第十五章：连接词）
    - 19-compound-sentences.md（第十六章：合句）
    - 20-noun-clauses.md（第十七章：名词从句）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 7个文件全部创建，frontmatter字段完整
  - `programmatic` TR-6.2: 无残留MyST语法
  - `programmatic` TR-6.3: 交叉链接格式正确
  - `human-judgment` TR-6.4: 内容完整保留

## [ ] Task 7: E阶段-5 - 生成第四批概念文档（高级篇22-25）+ examples
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 第四批（4个概念文件+examples目录）：
    - 21-adverb-clauses.md（第十八章：副词从句）
    - 22-relative-clauses.md（第十九章：关系从句）
    - 23-subject-verb-agreement.md（第二十章：主谓一致）
    - 24-inversion.md（第二十一章：倒装句）
    - examples/index.md
    - examples/extensive-reading-materials.md（广读材料推荐作为示例，来自intro.md）
  - 注：第22-25章（reduced clauses系列）确认下章号
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有文件创建完成，frontmatter完整
  - `programmatic` TR-7.2: examples/ 目录结构正确
  - `human-judgment` TR-7.3: 示例文档内容合理

## [ ] Task 8: E阶段-6 - 生成第五批概念文档（简化从句系列22-25）+ 根index.md
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 第五批（剩余4个简化从句章节+根index）：
    - 25-reduced-clauses.md（第二十二章：简化从句）
    - 26-reduced-relative-clauses.md（第二十三章：关系从句简化）
    - 27-reduced-noun-clauses.md（第二十四章：名词从句简化）
    - 28-reduced-adverb-clauses.md（第二十五章：副词从句简化）
    - concepts/index.md（概念导航，无frontmatter，列出所有概念文档）
  - ⚡ 最后生成根 index.md（含 okf_version frontmatter），按学习路径分组导航
  - 更新 log.md 记录完成
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有28个概念文档+根index+concepts/index全部生成
  - `programmatic` TR-8.2: 根index.md包含okf_version: "0.2" frontmatter
  - `human-judgment` TR-8.3: 根index按学习路径分组，导航清晰合理
  - `human-judgment` TR-8.4: concepts/index.md列出所有概念文件无遗漏
- **Notes**: ⚠️ Index必须最后写！这是source-code-to-okf-wiki的核心纪律

## [ ] Task 9: V阶段 - 独立验证与修复
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 结构检查：目录结构完整、所有文件存在
  - Frontmatter检查：所有必填字段完整、格式正确
  - MyST残留检查：Grep搜索 {toctree}/{note}/```{ 等MyST指令
  - 交叉链接检查：所有/开头路径的目标文件存在
  - 内容完整性抽样：随机抽取3-5个文件对比原文确认内容无遗漏
  - 输出检查报告，逐一修复发现的问题
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: Grep搜索无MyST残留指令
  - `programmatic` TR-9.2: 所有交叉链接目标文件存在
  - `programmatic` TR-9.3: frontmatter字段完整（type/title/description/tags/sources等必填项）
  - `human-judgment` TR-9.4: 抽样文件内容与原文一致
  - `programmatic` TR-9.5: 无../相对路径链接
- **Notes**: 这是G4质量门，必须严格执行。如发现虚构内容或格式问题立即修复

## [ ] Task 10: C阶段 - 收尾与验证
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 运行link-check验证所有内部链接
  - 更新log.md最终状态
  - 最终完整性检查：文件数量核对、格式一致性
  - 如发现可复用的批量文档转换模式，简要记录（可选）
- **Acceptance Criteria Addressed**: All ACs
- **Test Requirements**:
  - `programmatic` TR-10.1: link-check无断链
  - `programmatic` TR-10.2: 总文件数与预期一致（约30+个内容文件+索引+日志）
  - `human-judgment` TR-10.3: 整体质量符合OKF规范，可作为学习资源使用
