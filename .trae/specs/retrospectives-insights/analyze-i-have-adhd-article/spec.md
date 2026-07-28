---
version: 1.0
source: "https://mp.weixin.qq.com/s/d7TmHsMOaqodfD0re239TQ?from=industrynews&color_scheme=light#rd"
---

# i-have-adhd项目分析与Agent输出优化方法论沉淀 - Product Requirement Document

## Overview
- **Summary**: 对微信公众号文章介绍的开源项目i-have-adhd（GitHub 9.4k+ Star）进行系统性深度分析，提炼AI Agent输出格式优化的核心方法论（行动优先、步骤化、进度重述、压制离题），形成结构化分析报告；严格遵循七概念方法论（R→I→E→V）完成知识沉淀，将可复用模式入库到SpecWeave模式库。
- **Purpose**: 1) 萃取AI Agent输出优化的核心规则与心理学原理，为SpecWeave项目的智能体输出规范提供可借鉴经验；2) 通过实践强化七概念方法论编排流程，建立知识沉淀类任务的可复用范例；3) 分析"心理学原理逆向应用于AI"的创新思路，提炼跨领域迁移方法论。
- **Target Users**: SpecWeave项目维护者、AI Agent开发者、提示词工程师、交互设计师、认知科学应用实践者

## Goals
- 系统梳理文章核心内容：i-have-adhd项目解决的痛点、4条核心输出规则、安装使用方法、例外场景
- 深度分析4条规则背后的认知科学原理与交互设计逻辑
- 提炼"行动优先、答案前置"的Agent输出规范核心要素
- 分析"心理学方法论逆向适配AI"的跨领域创新模式
- 评估项目的设计取舍（只改输出格式不改推理能力、6种例外场景灵活性）
- 形成综合分析报告：核心优势、可改进点、SpecWeave可借鉴经验
- 在知识沉淀过程中严格执行七概念方法论（R→I→E→V），通过G1-G3质量门
- 将核心洞察沉淀为可复用的模式文档，更新SpecWeave知识库索引

## Non-Goals (Out of Scope)
- 不对i-have-adhd项目进行实际安装、安装测试或二次开发
- 不开发SpecWeave版本的i-have-adhd插件或Skill
- 不对Claude Code、Codex等工具的插件生态进行全面调研（仅基于本文分析）
- 不修改SpecWeave现有的智能体提示词或输出规范
- 不进行ADHD心理学的深度学术研究（仅基于文章提及内容）
- 不执行Git原子提交之外的代码变更（本任务为纯文档知识沉淀）

## Background & Context
- 当前AI编程助手（Claude Code、Codex等）普遍存在输出啰嗦、铺垫过长、容易跑题、关键信息隐藏的问题，影响用户效率与Token消耗
- i-have-adhd项目通过一套纯文本SKILL.md规则，改变AI输出格式，实现"直接给答案、行动优先、步骤清晰、不客套不离题"
- 项目核心创新点：将面向ADHD患者的生活管理工具（《The Adult ADHD Tool Kit》）中的心理学建议逆向应用于AI输出规范设计
- SpecWeave项目自身正在建设智能体输出规范与Skill体系（见.agents/skills/、.agents/prompts/），需要借鉴外部成熟的输出优化经验
- 七概念方法论是SpecWeave核心知识沉淀框架，本任务是知识沉淀场景的标准实践
- 文章来源于"开源日记"公众号，项目基于MIT协议开源，具有较高的实践参考价值

## Functional Requirements
- **FR-1**: 文章内容结构化梳理 - 提取核心痛点、项目介绍、4条核心规则、使用方法、例外场景、设计理念，形成结构化摘要
- **FR-2**: 4条核心规则深度分析 - 拆解每条规则（行动为先/步骤编号/进度重述/压制离题）的设计逻辑、心理学依据、适用边界
- **FR-3**: 交互设计哲学提炼 - 分析"行动优先"vs"解释优先"的设计权衡、认知负荷管理、工作记忆适配原理
- **FR-4**: 跨领域迁移模式分析 - 解读"心理学方法→AI提示词"的逆向创新路径，提炼可复用的跨领域迁移方法论
- **FR-5**: 项目设计取舍评估 - 分析"不改推理只改输出""规则有例外""纯文本SKILL"等设计决策的合理性与 trade-off
- **FR-6**: 内容结构与传播特点分析 - 分析文章的写作风格、案例呈现方式、痛点-方案-效果的论证结构
- **FR-7**: 七概念方法论执行 - 严格按知识沉淀链路（R→I→E→V）执行，通过G1-G3质量门验证
- **FR-8**: 综合分析报告生成 - 形成包含核心洞察、优势分析、改进建议、SpecWeave可借鉴经验的完整报告
- **FR-9**: 模式萃取与入库 - 将核心方法论沉淀为结构化可复用模式文档，存放到docs/retrospective/patterns/对应目录
- **FR-10**: 索引更新与交叉引用 - 更新知识库索引，确保新沉淀的模式可被发现，关联相关现有文档

## Non-Functional Requirements
- **NFR-1**: 分析深度 - 不仅复述内容，需提炼"为什么有效""可迁移到什么场景""反模式是什么"等深度洞察
- **NFR-2**: 七概念合规 - R阶段事实无因果词，I阶段洞察包含四元组，E阶段模式包含触发场景/核心步骤/反模式/迁移验证，V阶段对抗审查有实质内容
- **NFR-3**: 结构化输出 - 报告使用清晰的章节结构、标题层级、要点列表，模式文档遵循SpecWeave现有模式模板
- **NFR-4**: 可操作性 - 对SpecWeave的借鉴建议需具体可执行，避免空泛论述
- **NFR-5**: 溯源规范 - 所有引用文章内容标注来源，文档携带source字段
- **NFR-6**: 中文输出 - 报告主体使用中文，技术术语保留英文原文

## Constraints
- **Technical**: 基于defuddle提取的文本内容进行分析，无法进行实际交互体验测试；遵循SpecWeave现有Markdown文档规范与模式模板
- **Business**: 知识沉淀需在一次Spec流程中完成，时间受控
- **Dependencies**: defuddle已提取文章内容；七概念方法论规范已定义（.agents/commands/seven-concepts.md）；项目已建立docs/retrospective/patterns/模式库结构；模式萃取遵循extraction-cmd规范

## Assumptions
- 提取的文章内容完整、准确，无关键信息缺失
- i-have-adhd项目的核心规则如文章所述，无需访问GitHub仓库验证源码细节
- "ADHD心理学方法逆向应用于AI"的思路具有跨领域迁移价值，可应用于其他AI交互场景
- SpecWeave现有模式库结构无需调整即可容纳本次沉淀的新模式

## Acceptance Criteria

### AC-1: 文章核心内容完整梳理
- **Given**: 已提取的文章markdown内容
- **When**: 完成内容梳理章节
- **Then**: 报告包含文章核心痛点概述、项目基本信息（名称/Star数/协议/仓库地址）、4条规则的要点总结、安装使用方法、例外场景说明
- **Verification**: `programmatic`
- **Notes**: 核心信息使用要点列表呈现，关键事实准确无误

### AC-2: 4条核心规则深度分析完成
- **Given**: 文章列出的4条输出规则
- **When**: 完成规则分析章节
- **Then**: 每条规则均包含"规则解读→设计逻辑→心理学/认知科学依据→适用边界→可迁移性"五要素分析
- **Verification**: `human-judgment`
- **Notes**: 需关联到认知负荷理论、工作记忆理论、行动导向设计等原理

### AC-3: 交互设计哲学提炼完成
- **Given**: 4条规则的分析结果
- **When**: 完成设计哲学章节
- **Then**: 提炼出"行动优先、答案前置"的Agent输出设计范式，对比"解释优先"范式的适用场景与优劣
- **Verification**: `human-judgment`

### AC-4: 跨领域迁移模式分析完成
- **Given**: 文章提到的"心理学→AI"逆向创新
- **When**: 完成跨领域迁移章节
- **Then**: 总结出跨领域方法论迁移的一般路径，识别"人因工程方法→AI交互设计"的可复用机会点
- **Verification**: `human-judgment`

### AC-5: 项目设计取舍评估完成
- **Given**: 文章提到的设计决策
- **When**: 完成设计评估章节
- **Then**: 分析3个以上关键设计决策的trade-off，指出优势与潜在局限
- **Verification**: `human-judgment`

### AC-6: 七概念方法论质量门通过
- **Given**: R/I/E各阶段产出物
- **When**: 各阶段完成时
- **Then**: G1（事实无因果词）通过、G2（洞察四元组完整）通过、G3（模式可迁移）通过、V门（对抗审查有实质内容）通过
- **Verification**: `programmatic`
- **Notes**: 每个质量门有检查记录，不通过需返工修正

### AC-7: 综合分析报告形成
- **Given**: 所有分析章节完成
- **When**: 完成报告整合
- **Then**: 报告包含执行摘要、3-5条核心优势、2-3条可改进点、5条以上SpecWeave可直接借鉴的实践经验
- **Verification**: `human-judgment`

### AC-8: 可复用模式萃取入库
- **Given**: 分析报告完成
- **When**: 完成模式萃取
- **Then**: 在docs/retrospective/patterns/下新增至少1个结构化模式文档，模式包含触发场景、核心步骤、反模式、迁移验证四要素
- **Verification**: `programmatic`
- **Notes**: 模式遵循extraction-cmd规范，可独立理解不依赖原报告

### AC-9: 知识库索引更新完成
- **Given**: 新模式文档入库
- **When**: 完成索引更新
- **Then**: 对应目录的README.md已更新，包含新模式条目；spec目录登记到retrospectives-insights主题README
- **Verification**: `programmatic`

### AC-10: 文档格式规范合规
- **Given**: 生成的所有Markdown文件
- **When**: 文档最终检查
- **Then**: 所有文件包含正确的YAML frontmatter（version/source/title等字段）、无file:///绝对路径、相对路径引用正确、Markdown语法规范、无错别字
- **Verification**: `programmatic`
- **Notes**: 通过link-check等验证脚本检查链接有效性

## Open Questions
- [ ] 沉淀的模式应存放在patterns下的哪个子目录？（methodology-patterns/interaction-patterns/prompt-patterns？）
- [ ] 是否需要访问i-have-adhd的GitHub仓库查看SKILL.md原文以获取完整规则？
- [ ] 是否需要为本次知识沉淀生成额外的对抗审查视角文档？
