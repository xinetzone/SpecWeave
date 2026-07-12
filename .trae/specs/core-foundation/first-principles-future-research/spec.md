# 第一性原理后续研究方向规划 - Product Requirement Document

## Overview
- **Summary**: 基于第一性原理全面资料搜集项目的经验总结，系统化开展4个后续研究方向，包括第一性原理思维的认知科学基础研究、AI时代的第一性原理应用研究、跨学科第一性原理案例库扩展、第一性原理与类比推理的适用边界研究。通过分阶段的研究与文档沉淀，进一步完善第一性原理知识体系的深度与广度。
- **Purpose**: 解决现有第一性原理知识库在认知机制、AI时代应用、跨领域覆盖、适用边界等方面的不足。通过系统性后续研究，为第一性原理思维方法提供更坚实的认知科学基础，探索AI辅助下的新实践模式，扩展案例覆盖范围，并明确方法论的适用条件。
- **Target Users**: 第一性原理研究者与实践者、方法论爱好者、AI时代的知识工作者、希望系统掌握思维方法的学习者。

## Goals
- 完成第一性原理思维的认知科学基础研究，揭示类比推理作为默认模式的神经机制与认知负荷
- 探索AI时代第一性原理的应用范式，特别是AI辅助对抗性审查的方法与工具
- 扩展跨学科第一性原理案例库，覆盖生物、数学、计算机科学、社会科学等领域
- 明确第一性原理与类比推理的适用边界，建立场景判断框架
- 所有研究成果以Markdown文档形式沉淀至现有第一性原理知识库目录
- 延续现有质量规范（可信度评级、偏差标注、来源验证、对抗性审查）

## Non-Goals (Out of Scope)
- 不开展认知神经科学实验或原创性心理学研究（仅基于已有学术文献进行综述整合）
- 不开发AI辅助审查的生产级工具或软件系统（仅形成方法论文档与概念验证方案）
- 不追求案例库的全面覆盖（每个新增领域精选3-5个高质量案例即可）
- 不创建第一性原理vs类比推理的量化决策模型（v1版本建立定性判断框架即可）
- 不翻译为英文（仅中文版本）
- 不修改现有知识库核心文档结构（新增独立研究文档）

## Background & Context
- 第一性原理全面资料搜集项目已完成，沉淀了12个核心文档，覆盖哲学起源、物理应用、商业案例、方法论框架、对抗性审查等内容
- 现有知识库主要覆盖物理和商业领域，存在学科偏向（ACT-007已部分补充传统行业案例，但跨学科覆盖仍不足）
- 项目执行过程中识别出4个重要的后续研究方向，记录于[export-suggestions.md](../../../../docs/retrospective/reports/insight-extraction/external-learning/retrospective-ai-code-assistant-project-analysis-20260625/export-suggestions.md#L137-L145)第5章
- 现有文档已建立完整的质量保障体系：可信度双轨制评分、对抗性审查协议、偏差标注机制、来源分级标准
- 相关可参考模式：[adversarial-review-protocol.md](../../../../docs/retrospective/patterns/methodology-patterns/research-knowledge/adversarial-review-protocol.md)、[credibility-dual-track.md](../../../../docs/retrospective/patterns/methodology-patterns/research-knowledge/credibility-dual-track.md)

## Functional Requirements
- **FR-1**: 认知科学基础研究文档（13-cognitive-science-foundations.md）
  - 研究类比推理作为大脑默认模式的认知神经科学机制
  - 分析第一性原理思考的认知负荷来源与量化评估
  - 探索降低刻意练习门槛的认知策略与训练方法
  - 引用认知心理学、神经科学领域的一级学术来源（DOI/arXiv/高引论文）
- **FR-2**: AI时代应用研究文档（14-first-principles-in-ai-era.md）
  - 分析AI生成内容（AIGC）时代来源验证面临的新挑战
  - 研究对抗性审查在AI辅助下的增强模式
  - 提出AI辅助来源验证的方法论框架与工作流程
  - 探讨第一性原理思维与AI推理能力的互补关系
- **FR-3**: 跨学科案例库扩展（15-cross-domain-cases/目录）
  - 生物学领域：精选3-5个第一性原理应用案例（如分子生物学、进化论、系统生物学）
  - 数学领域：精选3-5个案例（如公理化方法、数学基础重构、重大定理证明）
  - 计算机科学领域：精选3-5个案例（如UNIX哲学、算法设计、系统架构创新）
  - 社会科学领域：精选3-5个案例（如经济学基础假设、社会学理论构建）
  - 每个案例沿用现有案例格式：背景、问题、第一性原理应用过程、结果、局限性标注
- **FR-4**: 适用边界研究文档（16-boundary-conditions.md）
  - 建立第一性原理vs类比推理的场景判断维度（时间压力、问题新颖性、后果严重性、知识完备度等）
  - 分析类比推理更高效的典型场景与案例
  - 提出"何时使用哪种思维"的决策框架
  - 讨论两种思维混合使用的策略与模式
- **FR-5**: 所有文档遵循现有frontmatter规范（YAML格式，包含id/title/date/type/source等字段）
- **FR-6**: 在[README.md](../../../../docs/knowledge/learning/first-principles/)中新增这4个研究方向的导航入口
- **FR-7**: 所有引用来源遵循可信度双轨制评分，一级来源占比不低于70%
- **FR-8**: 所有案例诚实标注事后归因偏差，沿用现有偏差提示传统

## Non-Functional Requirements
- **NFR-1**: 每个研究文档保持适度篇幅（认知科学/AI时代/适用边界：3000-5000字；案例库每个案例800-1500字）
- **NFR-2**: 认知科学研究避免过度技术化，保持对非专业读者的可读性
- **NFR-3**: AI应用研究保持技术审慎，不夸大AI能力，明确标注AI辅助的局限性
- **NFR-4**: 跨学科案例优先选择已有学术共识或被广泛认可的案例，避免争议过大的边缘案例
- **NFR-5**: 适用边界研究保持平衡视角，不贬低类比推理价值，明确两种思维各有适用场景
- **NFR-6**: 文件命名遵循kebab-case规范，纯英文文件名
- **NFR-7**: 所有研究文档包含进一步研究方向章节，为后续迭代预留空间

## Constraints
- **Technical**: 仅使用Markdown格式；遵循现有知识库的文档结构与格式规范
- **Business**: 低优先级长期研究任务（原export-suggestions.md中标注为低优先级），可分阶段迭代完成
- **Dependencies**: 依赖现有第一性原理知识库的核心文档（特别是08-methodology-framework.md、00-adversarial-review-protocol.md）

## Assumptions
- 现有知识库目录结构保持稳定，新增文档按序号递增（13、14、15、16）
- 学术文献获取渠道畅通（Google Scholar、arXiv、DOI解析等）
- 研究过程中可应用已沉淀的对抗性审查协议进行自我审查
- 读者已具备第一性原理基础知识（阅读过现有核心文档）

## Acceptance Criteria

### AC-1: 文档结构与格式合规
- **Given**: 所有研究任务完成
- **When**: 检查docs/knowledge/learning/first-principles/目录
- **Then**: 存在13-cognitive-science-foundations.md、14-first-principles-in-ai-era.md、15-cross-domain-cases/目录（含4个子领域文档）、16-boundary-conditions.md，所有文件使用正确YAML frontmatter，文件名为纯英文kebab-case
- **Verification**: `programmatic`
- **Notes**: 运行文件名规范检查脚本验证

### AC-2: 认知科学基础研究质量
- **Given**: 13-cognitive-science-foundations.md已创建
- **When**: 审查文档内容
- **Then**: 覆盖类比推理默认模式机制、第一性原理认知负荷、降低练习门槛策略三个主题，引用至少10篇认知科学/神经科学领域学术文献，包含DOI或可验证来源，保持非专业读者可读性
- **Verification**: `human-judgment`

### AC-3: AI时代应用研究质量
- **Given**: 14-first-principles-in-ai-era.md已创建
- **When**: 审查文档内容
- **Then**: 覆盖AIGC时代来源验证挑战、AI辅助对抗性审查框架、第一性原理与AI互补关系三个主题，提出具体的工作流程建议，明确标注AI能力边界与局限性，不夸大AI作用
- **Verification**: `human-judgment`

### AC-4: 跨学科案例库覆盖
- **Given**: 15-cross-domain-cases/目录已创建
- **When**: 统计各领域案例数量
- **Then**: 生物、数学、计算机科学、社会科学4个领域各至少3个案例，总计至少12个案例，每个案例包含背景、应用过程、结果、局限性标注，诚实标注事后归因偏差
- **Verification**: `programmatic` + `human-judgment`

### AC-5: 适用边界研究质量
- **Given**: 16-boundary-conditions.md已创建
- **When**: 审查文档内容
- **Then**: 建立至少4个维度的场景判断框架，提供类比推理更高效的典型场景（至少5个），提出决策框架与混合使用策略，保持平衡视角不贬低任一思维方式
- **Verification**: `human-judgment`

### AC-6: README导航更新
- **Given**: 所有研究文档完成
- **When**: 查看README.md文件导航表
- **Then**: 文件导航表中包含序号13-16的新增文档条目，链接正确，有内容简介和阅读顺序建议
- **Verification**: `programmatic`

### AC-7: 来源质量与可信度
- **Given**: 所有文档完成
- **When**: 运行链接检查并统计来源分级
- **Then**: 所有内部file:///链接有效无断链，一级学术来源占比不低于70%，所有事实性声明有来源支撑，沿用可信度双轨制评分
- **Verification**: `programmatic` + `human-judgment`

### AC-8: 质量规范延续性
- **Given**: 所有文档完成
- **When**: 审查内容风格与质量机制
- **Then**: 延续现有批判性视角，案例包含偏差提示，不做"第一性原理万能"的宣称，对抗性审查协议应用于研究过程，文档包含进一步研究方向章节
- **Verification**: `human-judgment`

## Open Questions
- [ ] 跨学科案例是否需要按统一模板结构化（如表格化），还是保持自由叙述格式？（建议：沿用现有案例叙述格式，保持可读性）
- [ ] AI辅助对抗性审查是否需要提供简单的Prompt示例？（建议：v1版本提供概念性方法论即可，具体Prompt可作为后续迭代）
- [ ] 4个研究方向的优先级如何排序？（建议：适用边界研究最具实践指导价值可优先，认知科学基础最具理论深度可次之）
- [ ] 是否需要为新增研究文档建立独立的子目录结构？（建议：13/14/16作为单文件放根目录，15跨领域案例因包含多个子领域建独立子目录）
