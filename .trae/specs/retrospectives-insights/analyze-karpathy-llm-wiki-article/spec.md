# Karpathy LLM Wiki 知识库方案文章深度洞察分析 Spec

## Why

用户希望对微信公众号文章《Karpathy发了一条推文2000万人看了，我照着他的方法搭了个知识库》（作者 wuhiufan）进行系统性学习与深度洞察分析。该文章介绍了 Andrej Karpathy 于 2026 年 4 月提出的个人知识库构建方案——用 LLM 将知识"编译"成结构化 Wiki，以替代传统 RAG（检索增强生成）方案。该方案提出 RAG 的四个结构性缺陷、LLM Wiki 的编译器类比、三层架构（Raw/Wiki/Schema）、四个核心操作（摄入/查询/索引/健康检查）、工具链选型，并梳理了从 Memex（1945）到 Luhmann 卡片盒（1950-1998）再到 Karpathy LLM Wiki（2026）的八十年思想谱系。

这一方案与 SpecWeave 项目的 `.agents/` 规范体系、AGENTS.md 路由机制、知识库管理、复盘体系、原子化文档操作高度相关——Schema 层（CLAUDE.md/AGENTS.md）对应 SpecWeave 的 AGENTS.md 入口路由，Wiki 编译思路对应 SpecWeave 的文档原子化与看板自动生成，健康检查对应 SpecWeave 的链接检查与一致性校验脚本。深入分析可为本项目的智能体协作、知识沉淀机制、文档治理体系提供直接的借鉴视角与方法论支撑。

## What Changes

- 提取并整理微信文章全文内容，识别文章主体结构（推文背景引入、RAG 问题剖析、编译器类比、三层架构、四个核心操作、实践体验、工具链、思想谱系、方案成立原因、上手指南）
- 提炼文章核心观点：LLM Wiki 用"编译式知识管理"替代 RAG 的"检索式知识管理"，让知识库从无状态查询升级为持续积累的编译产物
- 分析论证逻辑：从 RAG 缺陷→编译器类比→架构设计→操作流程→实践验证→工具支撑→思想溯源→成立原因→上手指南的递进论证链条
- 评估信息结构：按"问题—方案—实现—验证—溯源—行动"六层递进的组织方式
- 萃取关键知识点：RAG 四大结构性问题、编译器六概念映射、三层架构定义、四操作流程、工具链四件套、Memex/Luhmann/Karpathy 思想谱系
- 评估信息来源可靠性（作者 wuhiufan 实践转述、Karpathy 推文与 GitHub Gist 源头）、内容时效性（2026年4月推文、作者跑了一个多月的实践）、专业性
- 形成系统性理解与批判性思考，结合知识管理工具演进背景进行拓展分析
- 与 SpecWeave 的 `.agents/` 体系进行对照分析，提炼可借鉴的架构设计与操作机制
- 输出结构化洞察分析报告
- **BREAKING**：无（纯分析任务，不涉及代码或现有文档修改）

## Impact

- Affected specs：无直接修改；产出可作为 retrospectives-insights 主题的知识管理方法论参考材料
- Affected code：无代码改动；产出为 Markdown 分析报告
- 关联资产：可与 SpecWeave 的 `.agents/` 规范体系（AGENTS.md 路由、Schema 层设计）、原子化文档操作（docgen-cmd/atomization-cmd）、知识库与复盘体系（docs/knowledge、docs/retrospective）、健康检查脚本（link-check-cmd/check-duplication-cmd）形成深度对照分析

## ADDED Requirements

### Requirement: 文章全文内容提取与结构识别

系统 SHALL 完整提取微信文章正文内容，并识别其结构组成与章节层次。

#### Scenario: 内容提取完整

- **WHEN** 分析任务启动
- **THEN** 系统已通过 defuddle 提取文章全文 Markdown
- **AND** 识别出文章的主要章节（推文背景、RAG 四问题、编译器类比、三层架构、四核心操作、实践体验、工具链、思想谱系、成立原因、上手指南）
- **AND** 清理微信公众号尾部噪声（点赞/在看/分享按钮文字、小程序提示等）
- **AND** 保留关键表格（编译器概念与 LLM Wiki 对应表）、代码块（目录结构示例）、列表（四操作流程、健康检查项）

### Requirement: 核心观点提炼

系统 SHALL 准确提炼文章的核心观点与主张，包括主论点和支撑论点。

#### Scenario: 核心观点识别

- **WHEN** 进行核心观点分析
- **THEN** 识别主论点："LLM Wiki 用编译式知识管理替代 RAG 的检索式知识管理，让 LLM 提前把知识编译成结构化 Wiki，查询时读产物而非重新检索"
- **AND** 识别问题论点：RAG 存在四个结构性缺陷（分块切割语义断裂、无状态查询、规模越大越不准、嵌入模型过时）
- **AND** 识别架构论点：三层架构（Raw 原始素材/Wiki 编译产物/Schema 规则配置）实现关注点分离
- **AND** 识别操作论点：四个核心操作（摄入/查询/索引/健康检查）形成闭环工作流
- **AND** 识别体验论点：跑了一个多月 80 篇素材 130 个页面，"知识在生长"的感受是 RAG 给不了的
- **AND** 识别思想论点：从 Memex（Bush 构想愿景）到 Luhmann（人力纪律实现）到 Karpathy（LLM 自动化维护）的八十年思想谱系
- **AND** 识别成立论点：维护成本接近于零是 LLM Wiki 能持续运转的根本原因

### Requirement: 论证逻辑分析

系统 SHALL 分析文章的论证结构，评估论据是否充分支撑论点。

#### Scenario: 论证链条梳理

- **WHEN** 进行论证逻辑分析
- **THEN** 梳理"RAG 缺陷→编译器类比→三层架构→四操作流程→实践体验→工具链→思想溯源→成立原因→上手指南"的论证结构
- **AND** 评估 RAG 缺陷分析是否有数据支撑（语义分块平均 43 token 的研究数据）
- **AND** 评估编译器类比是否成立（源代码/编译产物/编译器/构建配置/增量编译/依赖图/代码检查七概念映射）
- **AND** 评估实践体验是否有量化指标（80 篇素材、130 个页面、一个多月运行、一次主动矛盾标注案例）
- **AND** 评估思想谱系梳理是否准确（1945 Memex、1950-1998 Luhmann、2026 Karpathy 三个节点）
- **AND** 评估成立原因论证是否有逻辑支撑（维护成本增长 vs 使用价值增长的非对称性分析）

### Requirement: 关键知识点萃取

系统 SHALL 系统性萃取文章中的关键技术知识点与方法论要点。

#### Scenario: 知识点结构化输出

- **WHEN** 进行知识萃取
- **THEN** 输出 RAG 四大结构性问题的具体描述（分块切割/无状态/规模衰减/嵌入过时）
- **AND** 输出编译器七概念映射表（源代码→原始文档、编译产物→Wiki 页面、编译器→LLM、构建配置→Schema、增量编译→部分更新、依赖图→交叉引用、代码检查→健康检查）
- **AND** 输出三层架构定义（Raw 不可变只读/Wiki 由 LLM 拥有/Schema 规则配置）
- **AND** 输出目录结构示例（wiki-root/CLAUDE.md、raw/、wiki/、assets/ 的完整层级）
- **AND** 输出四操作的完整流程（摄入 9 步流程、查询的回填机制、索引的双文件设计 index.md+log.md、健康检查的 6 项检查项）
- **AND** 输出工具链四件套（Claude Code/Codex、Obsidian、qmd、Git 的各自职责）
- **AND** 输出思想谱系三节点（Memex 1945/Luhmann 1950-1998/Karpathy 2026 的传承关系）

### Requirement: 信息来源可靠性评估

系统 SHALL 评估文章信息来源的可靠性，包括发布媒体权威性、信息源头、数据可信度。

#### Scenario: 来源可靠性评估

- **WHEN** 进行可靠性评估
- **THEN** 评估作者 wuhiufan 的身份定位（实践者转述，非 Karpathy 本人）
- **AND** 评估信息源头（Karpathy 的 X 推文 + GitHub Gist）的权威性
- **AND** 评估传播数据可信度（1500 万浏览、9 万收藏、2000 万讨论度——标注为作者声称，无法独立验证）
- **AND** 评估研究数据可信度（语义分块平均 43 token——需追溯原始研究来源）
- **AND** 评估实践数据可信度（80 篇素材、130 个页面——作者个人实践，样本量有限）
- **AND** 评估工具推荐客观性（Claude Code 优于 Codex 的判断是否有充分依据）

### Requirement: 内容时效性与专业性评估

系统 SHALL 评估文章内容的时效性与技术专业性。

#### Scenario: 时效性与专业性评估

- **WHEN** 进行时效性评估
- **THEN** 评估文章发布时间与 Karpathy 推文时间差（推文 2026 年 4 月 2 日，文章为后续实践总结）
- **AND** 评估方案成熟度（Karpathy 自称"idea file"未开源代码，社区有实现但无官方版本）
- **AND** 评估技术深度（架构设计清晰但无性能基准、无与 RAG 的定量对比、无失败案例分析）
- **AND** 评估实践可行性（最小可用版本三步可上手，但规模化需 qmd 等额外工具）
- **AND** 评估方案适用边界（个人知识库场景，企业级/多用户协作场景未涉及）

### Requirement: 批判性思考与拓展分析

系统 SHALL 形成对文章内容的批判性思考，并结合知识管理工具演进背景进行拓展分析。

#### Scenario: 批判性分析

- **WHEN** 进行批判性思考
- **THEN** 识别文章优点（编译器类比精妙、架构分层清晰、操作流程可执行、思想谱系有深度、上手指南实用）
- **AND** 识别文章局限性（实践样本量小、无定量对比 RAG、无失败/限制案例、无企业级场景、思想谱系简化、工具推荐主观）
- **AND** 识别潜在风险（LLM 编译成本、Schema 设计门槛、Wiki 膨胀后的索引瓶颈、LLM 幻觉导致的内容错误、Git 回退能力有限）
- **AND** 结合知识管理工具演进背景拓展分析（从 RAG 到 LLM Wiki 到未来 Agentic Knowledge Graph 的趋势）
- **AND** 与 SpecWeave 的 `.agents/` 体系进行对照，提炼可借鉴之处（Schema 层设计、原子化操作、健康检查机制、思想谱系梳理方法）

### Requirement: 与 SpecWeave 体系对照分析

系统 SHALL 将 LLM Wiki 方案与 SpecWeave 项目的现有体系进行深度对照，提炼可借鉴的架构设计与操作机制。

#### Scenario: SpecWeave 对照分析

- **WHEN** 进行对照分析
- **THEN** 对照 Schema 层：LLM Wiki 的 CLAUDE.md/AGENTS.md 与 SpecWeave 的 AGENTS.md 路由体系（上下文路由表、角色定义、协作协议）的异同
- **AND** 对照三层架构：LLM Wiki 的 Raw/Wiki/Schema 与 SpecWeave 的 raw 素材/docs 文档/.agents 规范的对应关系
- **AND** 对照操作机制：LLM Wiki 的摄入/查询/索引/健康检查与 SpecWeave 的 atomization-cmd/docgen-cmd/link-check-cmd/check-duplication-cmd 的对应关系
- **AND** 对照思想谱系：LLM Wiki 的 Memex→Luhmann→Karpathy 谱系与 SpecWeave 的复盘体系/可复用模式库的传承关系
- **AND** 提炼可借鉴之处：增量编译思路、交叉引用维护、矛盾检测机制、Graph View 可视化、frontmatter 动态查询
- **AND** 识别差异点：SpecWeave 面向多智能体协作（LLM Wiki 面向个人）、SpecWeave 有阶段守卫（LLM Wiki 无）、SpecWeave 有 vendor 嵌套路由（LLM Wiki 无）

### Requirement: 结构化分析报告输出

系统 SHALL 输出一份结构化的 Markdown 分析报告，涵盖上述所有分析维度。

#### Scenario: 报告结构完整

- **WHEN** 输出分析报告
- **THEN** 报告包含文章基本信息、核心观点、论证逻辑、信息结构、关键知识点、可靠性评估、时效性评估、专业性评估、批判性思考、拓展分析、SpecWeave 对照分析、总结与展望等章节
- **AND** 报告语言为中文（Markdown 格式）
- **AND** 报告保存到指定路径

## REMOVED Requirements

无（新任务，无移除项）
