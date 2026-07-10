---
id: adversarial-review-knowledge-base-spec
title: 对抗性审查知识库 PRD
version: "1.0"
created_at: "2026-07-10"
status: draft
---

# 对抗性审查知识库 - Product Requirement Document

## Overview
- **Summary**: 在 `docs/knowledge/learning/02-agent-engineering-methodology/` 下构建独立的「对抗性审查系统化资料档案」，形成与第一性原理知识库并列的质量方法论知识库。采用与第一性原理相同的对抗性审查质量标准（自举验证），系统整合项目内已沉淀的实践模式、外部行业标准（OWASP/NIST/MITRE）、学术研究（认知偏差/代码审查心理学/红队测试）、开源工具链、实战案例五大板块。
- **Purpose**: 解决当前对抗性审查知识分散在模式文件、复盘报告、洞察文档中的碎片化问题；为AI协作代码审查、知识档案质量控制、安全测试等场景提供一站式、经过可信度验证的方法论资源；通过"用对抗性审查方法构建对抗性审查知识库"的自举方式验证方法论的可操作性。
- **Target Users**:
  - AI Agent开发者（需要多Agent对抗审查Prompt模式）
  - 知识工程师（需要对抗性审查协议进行资料质量控制）
  - 安全工程师（需要红队测试方法论与工具）
  - 代码审查者（需要认知偏差防御与检查清单）
  - 方法论研究者（需要系统化的审查方法论体系）

## Goals
- 构建结构化、原子化的对抗性审查知识体系，覆盖理论→方法论→工具→案例→练习完整闭环
- 所有核心资料经对抗性审查协议验证，一级来源占比≥70%，🟢A级资料占比≥60%，🔴D级资料为0
- 整合项目内已有实践成果（2个L2模式、1个完整协议、实战案例）与外部权威资源
- 提供可直接复用的工具：检查清单、Prompt模板、工具选型矩阵、练习题库
- 明确与第一性原理、质量内建、认知偏差防御等关联模式的关系定位

## Non-Goals (Out of Scope)
- 不构建自动化红队测试平台或工具开发（仅提供工具选型和使用指南）
- 不重复第一性原理知识库中已有的认知偏差内容（做交叉引用而非复制）
- 不做特定领域（如金融/医疗）的合规性审查指南
- 不包含纯网络安全渗透测试的专业技术细节（聚焦方法论层面）
- 不实时跟进最新arXiv论文（建立更新机制而非一次性穷尽）

## Background & Context
- 项目已在第一性原理知识库中沉淀了「对抗性审查协议v1.1」（7模块框架）
- 方法论模式库中已有2个L2级对抗性审查模式（research-knowledge场景 + ai-collaboration场景）
- 已完成卡兹克Vibe Coding两大神级Prompt的学习分析，验证了多Agent对抗审查的实战价值
- AIHOT等项目已有实战案例：40个Agent并发审查发现OOM死循环、未来时间污染等关键BUG
- 外部资源已初步收集：OWASP/NIST/MITRE标准、NVIDIA/Microsoft/OpenAI实践、Garak/PyRIT/Promptfoo开源工具、PLOS One认知偏差研究等
- 现有知识库采用标准化wiki结构：00-overview → 核心章节 → glossary → resources → quick-reference，已在10+个主题验证可行
- 学习目录下现有6个分类目录（01-06），对抗性审查属于02-agent-engineering-methodology（与第一性原理并列的方法论类知识）

## Functional Requirements
- **FR-1**: 创建标准化wiki目录结构 `adversarial-review-wiki/`，包含12-15个原子化文档
- **FR-2**: 00-overview.md 提供知识库概览、可信度评级说明、阅读路径导航、文件索引表
- **FR-3**: 01-core-concepts.md 定义对抗性审查的核心概念、与相关概念辨析（代码审查/红队测试/质量保证/审计/penetration testing）、两大应用分支（知识研究场景 vs AI协作/代码场景）
- **FR-4**: 02-philosophy-origins.md 追溯对抗性审查的思想源头：科学革命的怀疑主义传统、波普尔证伪主义、双盲同行评审、安全领域红队演练起源、认知心理学偏差研究
- **FR-5**: 03-methodology-framework.md 系统阐述两大场景方法论：①知识研究七模块协议（含阶段0跨领域扫描→三级来源分类→四级可信度评分→五维验证→偏差防御→异常标记→验证日志）；②AI协作/代码多Agent对抗模式（四大攻击者角色、Prompt标准形式、执行流程）
- **FR-6**: 04-cognitive-biases-defense.md 系统整理审查场景高频认知偏差（确认偏差/权威偏差/锚定效应/群体思维/幸存者偏差/事后归因等），含识别特征、在审查中的具体表现、防御措施、检查清单（与第一性原理做交叉引用，补充审查场景特有偏差）
- **FR-7**: 05-checklists-templates.md 提供可直接复用的工具：知识研究五维验证检查清单、代码对抗审查四大攻击者检查清单、来源可信度评分表、异常标记模板、验证日志模板、多Agent对抗Prompt标准模板
- **FR-8**: 06-industry-standards.md 整合外部权威标准：OWASP代码审查指南与LLM Top 10、NIST AI RMF红队要求、MITRE ATLAS矩阵、EU AI Act合规要求，标注核心要点与适用场景
- **FR-9**: 07-open-source-tools.md 开源工具链指南：Garak/PyRIT/Promptfoo/Inspect AI/DeepTeam/Purple Llama对比矩阵、选型指南、快速上手教程、CI/CD集成建议
- **FR-10**: 08-practice-cases.md 实战案例集：本项目AIHOT案例（OOM/未来时间污染/HTML清洗炸弹）、金融公司LLM泄露案例、卡兹克对抗式全局审查方法、OpenAI强化学习红队Agent实践，每案例含问题→对抗方法→发现→经验教训
- **FR-11**: 09-academic-resources.md 经筛选的学术资源与权威书籍：Tversky & Kahneman认知偏差奠基论文、Nickerson确认偏差综述、NVIDIA PLOS One LLM红队扎根理论研究、代码审查心理学论文等，按可信度分级标注
- **FR-12**: 10-source-validation-log.md 完整的来源验证档案：五维验证执行记录、来源类型统计、可信度分布、关键事实交叉验证、异常标记汇总、排除资料记录（自举验证——用对抗性审查方法验证本知识库自身）
- **FR-13**: 11-glossary.md 核心术语表，精确定义所有专业术语，含中英文对照、交叉引用
- **FR-14**: 12-resources.md 延伸阅读与外部资源链接，按主题分类
- **FR-15**: 13-quick-reference.md 快速参考速查表，包含核心流程、检查清单、工具命令、Prompt模板的极简版
- **FR-16**: README.md 作为目录索引文件，遵循现有自动生成格式规范
- **FR-17**: 更新02-agent-engineering-methodology/README.md，将新知识库加入索引

## Non-Functional Requirements
- **NFR-1（可信度质量）**: 核心论据一级来源占比≥70%，🟢A级资料占比≥60%，🔴D级资料为0%，所有关键事实完成≥2个独立来源交叉验证
- **NFR-2（原子化要求）**: 单个文件≤500行，单一职责，每个文件有清晰的边界，避免大而全的单文件
- **NFR-3（格式一致性）**: 遵循现有知识库格式规范：YAML frontmatter（id/title/category/date）、数字前缀文件名、kebab-case纯英文文件名、可信度标记（🟢/🔵/🟡/🔴）、异常标记（⚠️/❓/⚖️/🔍）、相对路径链接
- **NFR-4（可审计性）**: 所有外部引用必须可追溯，验证日志完整记录每个关键事实的验证过程
- **NFR-5（自举验证）**: 知识库自身的构建过程必须完整应用对抗性审查协议，作为方法论可操作性的验证案例
- **NFR-6（交叉引用）**: 与第一性原理知识库、相关模式文档建立双向交叉引用，避免内容重复
- **NFR-7（可读性）**: 提供分层次阅读路径（入门/进阶/专家），不同背景读者可快速找到适合的入口

## Constraints
- **Technical**:
  - 文件必须放在 `d:\AI\docs\knowledge\learning\02-agent-engineering-methodology\adversarial-review-wiki\` 目录下
  - 遵循项目现有Markdown格式规范（YAML frontmatter、相对路径链接、无中文文件名）
  - 文件名必须通过 `python .agents/scripts/check-filename-convention.py` 检查
- **Business**:
  - 基于已收集的内外部资源进行系统化整理，不进行大规模新的外部研究
  - 复用项目已有对抗性审查协议作为质量标准（自举）
- **Dependencies**:
  - 已有：第一性原理知识库的对抗性审查协议v1.1
  - 已有：2个L2级对抗性审查模式文件
  - 已有：已收集的外部资源（OWASP/NIST/MITRE标准、开源工具、学术论文）
  - 依赖：现有知识库的格式规范和目录结构约定

## Assumptions
- 用户希望对抗性审查知识库作为独立主题存在于02-agent-engineering-methodology目录下，而非第一性原理知识库的子章节
- 现有收集的外部资源已覆盖核心领域，不需要大规模额外搜索
- 认知偏差的基础理论部分可以引用第一性原理知识库内容，不需要重复撰写
- 知识库构建过程本身可以作为对抗性审查协议的实战验证案例

## Acceptance Criteria

### AC-1: 目录结构与文件完整性
- **Given**: 知识库构建完成
- **When**: 检查 `adversarial-review-wiki/` 目录
- **Then**: 包含15-17个文件（00-overview至13-quick-reference + README + 可选子目录），每个文件有正确的YAML frontmatter，文件名符合kebab-case纯英文+数字前缀规范
- **Verification**: `programmatic`
- **Notes**: 通过文件名检查脚本验证

### AC-2: 可信度质量达标
- **Given**: 所有文档完成撰写
- **When**: 统计来源分级和可信度评分
- **Then**: 一级来源占比≥70%，🟢A级资料占比≥60%，🔴D级资料为0%，所有关键事实完成≥2个独立来源交叉验证
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 验证日志中需有明确统计数据

### AC-3: 原子化与单一职责
- **Given**: 所有文档完成
- **When**: 检查每个文件
- **Then**: 单个文件≤500行，每个文件有清晰的单一主题，没有内容重复，文件间通过交叉引用关联
- **Verification**: `human-judgment`
- **Notes**: 参照第一性原理知识库的原子化程度

### AC-4: 方法论完整性
- **Given**: 核心方法论章节完成
- **When**: 阅读03-methodology-framework.md和05-checklists-templates.md
- **Then**: 两大应用场景（知识研究+AI协作/代码）的方法论均完整覆盖，提供可直接复用的检查清单和Prompt模板，工具可立即使用
- **Verification**: `human-judgment`
- **Notes**: 检查清单需可打印使用，Prompt模板可直接复制给AI

### AC-5: 自举验证完成
- **Given**: 知识库构建完成
- **When**: 检查10-source-validation-log.md
- **Then**: 完整记录本知识库自身应用对抗性审查协议的过程，包含五维验证执行记录、来源统计、交叉验证记录、偏差识别记录
- **Verification**: `human-judgment`

### AC-6: 交叉引用正确
- **Given**: 知识库完成
- **When**: 检查所有内部链接和外部引用
- **Then**: 与第一性原理知识库、模式文件的交叉引用正确（使用相对路径），外部链接可访问，没有断链
- **Verification**: `programmatic`（运行链接检查脚本）

### AC-7: 分层次阅读路径
- **Given**: 00-overview.md完成
- **When**: 阅读概览文档的阅读指南部分
- **Then**: 提供至少3条不同背景读者的阅读路径（入门/代码审查者/方法论研究者/安全工程师），每条路径有明确的文件顺序和说明
- **Verification**: `human-judgment`

### AC-8: 索引更新
- **Given**: 知识库完成
- **When**: 检查上级目录README
- **Then**: adversarial-review-wiki被正确加入02-agent-engineering-methodology/README.md的索引
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要为对抗性审查创建独立的Skill/指令集（类似first-principles.md），还是仅作为知识库存在？（建议：先完成知识库，后续根据使用情况再考虑指令集）
- [ ] 是否需要配套练习题（类似第一性原理exercises/子目录）？（建议：第一期暂不包含，先完成核心知识体系，练习题作为v1.1扩展）
- [ ] 是否需要交互式知识图谱（类似第一性原理12-knowledge-graph.html）？（建议：第一期暂不包含，后续根据使用需求添加）
