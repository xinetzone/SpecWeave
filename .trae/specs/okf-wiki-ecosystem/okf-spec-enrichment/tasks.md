# OKF Spec Bundle 内容补充 - 实施计划

## Task 1: 获取并整理信源材料
- **Status**: `in_progress`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 获取 GitHub 上 OKF v0.2 SPEC.md 完整英文原文（约408行）
  - 整理 okf.md/spec v0.1 Annotated Guide 的完整内容
  - 整理 okf.md/quickstart、/validator、/skill 页面内容
  - 将所有原始信源材料准备就绪，为后续文档生成提供事实基础
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: v0.2 SPEC.md 完整原文可获取（§1-§13全部章节无截断）
  - `rule` TR-1.2: v0.1 Annotated Guide、Quickstart、Validator、Skill四个页面内容已获取
  - `rubric` TR-1.3: 信源材料完整性；scale 1-5；anchors 1=缺少2个以上信源/3=主要信源获取但有截断/5=所有信源完整无截断；threshold >= 4；evidence: 文件行数和章节检查
- **Notes**: 信源先行原则——此任务是后续所有任务的前置条件

## Task 2: 更新 references/okf-spec.md 为完整英文v0.2规范
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 references/okf-spec.md 从现有19行中文摘要替换/扩展为包含完整英文v0.2规范原文
  - 保留现有frontmatter（更新description以反映包含完整原文）
  - 在英文原文前保留简短中文说明，标注本文件为vendored第三方规范
  - 确保文件以 `---` frontmatter开头，正文包含完整SPEC.md内容
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-2.1: 文件frontmatter包含type: Reference且字段完整
  - `rule` TR-2.2: 文件正文包含§1 Motivation到§13 Changes from v0.1的全部章节
  - `rule` TR-2.3: 英文原文与GitHub SPEC.md内容一致（无遗漏章节）
  - `evidence`: 读取文件验证章节标题序列和关键内容

## Task 3: 创建 references/okf-annotated-v01.md 信源登记
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 references/okf-annotated-v01.md 作为v0.1 Annotated Guide的信源登记
  - frontmatter标注type: Reference，resource指向okf.md/spec
  - 中文说明该文档为v0.1带注释开发者指南，包含实践建议和作者注释
  - 收录v0.1注释版中v0.2规范未包含的增量内容要点（设计原则、实践建议等摘要）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-3.1: 文件frontmatter合规（type: Reference, sources指向okf.md/spec）
  - `rule` TR-3.2: 文件明确说明v0.1与v0.2的关系（v0.1注释版包含实践注释，v0.2是正式规范）
  - `evidence`: 读取文件验证frontmatter和内容

## Task 4: 创建 concepts/design-principles.md（设计原则）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 新增概念文档，阐述OKF三大设计原则：最小意见化(Minimally opinionated)、生产者/消费者独立(Producer/consumer independence)、格式而非平台(Format not platform)
  - 解释每个原则如何影响规范中的具体设计决策
  - 中文撰写，frontmatter标注type: Rationale（或Concept）
  - sources指向okf-annotated-v01和okf-spec两个信源
  - 末尾添加"相关概念"章节，链接到motivation.md和concept-documents.md
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-4.1: 文件frontmatter合规，含type/title/description/tags/generated/sources字段
  - `rule` TR-4.2: 三大设计原则均有独立小节阐述
  - `rule` TR-4.3: 交叉链接使用`/`开头路径
  - `evidence`: 读取文件验证内容和格式

## Task 5: 创建 concepts/practical-guidance.md（实践指南）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 新增概念文档，收录v0.1注释版和网站中的实践建议：
    - type字段的治理建议（"自由但危险"——团队应约定命名规范）
    - 扩展字段实用示例（owner、freshness_sla）
    - 自动化生成index.md的bash脚本示例
    - "断链即特性"设计意图（允许先引用后补全）
    - Body结构化markdown对LLM+RAG的重要性
    - log.md vs git log的区别（受众不同，log.md是人工CHANGELOG）
    - Obsidian用户对比说明（Bundle≈vault, Concept≈note, Link≈wikilink）
    - v0.1 Citations到v0.2 footnote attribution的演进说明
    - 实践中的目录放置建议（knowledge/或docs/catalog/）
  - sources指向okf-annotated-v01
  - 交叉链接到相关概念文档
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-5.1: 文件frontmatter合规
  - `rule` TR-5.2: 至少覆盖8条实践建议（TR-5.2验证条目数量≥8）
  - `rule` TR-5.3: 包含bash脚本示例代码块（标注语言）
  - `rubric` TR-5.4: 实践建议可操作性；scale 1-5；anchors 1=建议空泛无具体指导/3=有建议但缺少示例/5=每条建议有解释和代码/示例支撑；threshold >= 4；evidence: 评审各建议的深度
  - `evidence`: 读取文件验证

## Task 6: 创建 concepts/tooling-validator.md（验证工具）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 新增概念文档，介绍OKF Validator在线验证工具
  - 内容：工具定位（零后端、浏览器端验证）、功能（粘贴验证/ZIP上传验证/SVG徽章生成）、三个合规规则检查、当前状态（Coming Soon）、手动验证替代方案
  - sources指向okf.md/validator
  - 相关概念链接到conformance.md
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-6.1: 文件frontmatter合规
  - `rule` TR-6.2: 覆盖Validator的三个核心功能（paste/upload/badge）
  - `rule` TR-6.3: 列出三个合规验证规则
  - `evidence`: 读取文件验证

## Task 7: 创建 concepts/tooling-agent-skill.md（Agent技能）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 新增概念文档，介绍OKF Agent Skill
  - 内容：安装方式（Claude Code/Kiro CLI npx skills add、Cursor/Windsurf规则引用、直接URL引用）、六项能力（Create/Validate/Enrich/Generate/Convert/Serve）、使用示例、内置资源（spec-v01.md/examples.md/conversion.md/validate.sh）、validate.sh脚本使用方法、Knowledge Catalog推送能力
  - sources指向okf.md/skill
  - 相关概念链接到conformance.md和tooling-knowledge-catalog.md
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-7.1: 文件frontmatter合规
  - `rule` TR-7.2: 覆盖三种安装方式
  - `rule` TR-7.3: 列出6项能力
  - `rule` TR-7.4: 包含validate.sh使用示例
  - `evidence`: 读取文件验证

## Task 8: 创建 concepts/tooling-knowledge-catalog.md（Knowledge Catalog集成）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 2, Task 7
- **Description**:
  - 新增概念文档，介绍Google Cloud Knowledge Catalog集成
  - 内容：Knowledge Catalog对OKF的原生支持（2026年6月起）、kcmd CLI工具（init/push）、MCP服务器工具（pull/push/list-entries/lookup-entry/modify-entry）、Agent配置方法
  - sources指向okf.md/skill
  - 相关概念链接到tooling-agent-skill.md
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-8.1: 文件frontmatter合规
  - `rule` TR-8.2: 介绍kcmd基本用法
  - `rule` TR-8.3: 列出MCP工具列表
  - `evidence`: 读取文件验证

## Task 9: 创建 examples/saas-metrics-quickstart.md（SaaS指标快速入门示例）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 新增示例文档，收录Quickstart教程的完整SaaS Metrics bundle
  - 内容：5分钟快速入门说明、最终目录结构、Step-by-step创建过程、三个Metric概念完整示例（MRR/Churn/NPS，含frontmatter、公式、基准数据、交叉链接）、index.md示例、log.md示例、三规则验证说明
  - 注意：Quickstart示例基于v0.1（使用timestamp字段和# Citations），需要在文档中说明v0.1→v0.2的映射关系（timestamp→generated.at, # Citations→footnotes+sources）
  - sources指向okf.md/quickstart
  - 相关概念链接到concept-documents.md、index-files.md、log-files.md、conformance.md
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-9.1: 文件frontmatter合规（type: Example）
  - `rule` TR-9.2: 包含MRR/Churn/NPS三个Metric的完整frontmatter+正文示例
  - `rule` TR-9.3: 包含index.md和log.md的代码示例
  - `rule` TR-9.4: 说明v0.1示例到v0.2的字段映射关系
  - `evidence`: 读取文件验证内容完整性

## Task 10: 更新 references/index.md 信源索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 在references/index.md中添加新增信源（okf-annotated-v01.md、以及okf.md各页面的信源说明）
  - 遵循"Index最后写"原则，但references/index可以在references文件完成后立即更新
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-10.1: index.md列出okf-spec.md和okf-annotated-v01.md
  - `rule` TR-10.2: index.md无frontmatter（子目录index约定）
  - `evidence`: 读取文件验证

## Task 11: 更新 concepts/index.md 概念索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7, Task 8
- **Description**:
  - 在concepts/index.md中添加所有新增概念文档条目（design-principles、practical-guidance、tooling-validator、tooling-agent-skill、tooling-knowledge-catalog）
  - 每个条目包含中文标题和简短描述
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-11.1: 5个新增概念文档全部在index中列出
  - `rule` TR-11.2: 每个条目有简短中文描述
  - `evidence`: 读取文件验证

## Task 12: 更新 examples/index.md 示例索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 在examples/index.md中添加saas-metrics-quickstart.md条目
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-12.1: saas-metrics-quickstart.md在index中列出
  - `evidence`: 读取文件验证

## Task 13: 更新根 index.md
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10, Task 11, Task 12
- **Description**:
  - 更新根index.md，反映新增的概念、示例、信源文档
  - 更新文档计数（原20个内容文档，新增后约27个）
  - 更新信任与生命周期说明，解释新增文档的status（draft/stable判定）
  - 保留okf_version: "0.2" frontmatter
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-13.1: 根index.md的concepts/列表包含所有新增概念
  - `rule` TR-13.2: examples/列表包含saas-metrics-quickstart
  - `rule` TR-13.3: references/列表包含新增信源
  - `rule` TR-13.4: 文档计数准确
  - `rule` TR-13.5: okf_version frontmatter保留
  - `evidence`: 读取文件验证

## Task 14: 更新 log.md
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 13
- **Description**:
  - 在log.md顶部添加2026-08-21日期分组
  - 记录本次补充的所有变更：v0.2英文原文补全、v0.1注释指南信源、新增5个概念文档、新增1个示例文档、索引更新
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-14.1: log.md顶部有## 2026-08-21日期标题
  - `rule` TR-14.2: 记录所有新增文件
  - `evidence`: 读取文件验证

## Task 15: 自检与链接验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 14
- **Description**:
  - 验证所有新增文档frontmatter合规性（type字段必填、其他字段正确）
  - 验证所有交叉链接路径正确（`/`开头、目标文件存在）
  - 验证现有文档未被破坏（抽查motivation、provenance-sources、attested-computations、conformance）
  - 检查kebab-case文件名
  - 检查中文正文
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-15.1: 所有新增.md文件有合法YAML frontmatter且type字段非空
  - `rule` TR-15.2: 所有交叉链接目标文件存在（无断链）
  - `rule` TR-15.3: 现有文档v0.2核心字段族内容未丢失
  - `rubric` TR-15.4: 文档规范合规性；scale 1-5；anchors 1=多文档frontmatter缺失或路径错误/3=基本合规但有小瑕疵/5=全部合规；threshold >= 4；evidence: 逐文件检查结果
  - `evidence`: 自检报告
