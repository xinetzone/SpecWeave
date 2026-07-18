# 第一性原理后续研究方向规划 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 适用边界研究（16-boundary-conditions.md）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 建立第一性原理vs类比推理的场景判断维度框架（时间压力、问题新颖性、后果严重性、知识完备度等）
  - 收集并分析类比推理更高效的典型场景（至少5个）
  - 提出"何时使用哪种思维"的定性决策框架
  - 探讨两种思维混合使用的策略与模式
  - 编写3000-5000字的研究文档，包含案例与分析
- **Acceptance Criteria Addressed**: [AC-1, AC-5, AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件16-boundary-conditions.md存在，文件名符合kebab-case规范，YAML frontmatter格式正确
  - `programmatic` TR-1.2: 所有内部file:///链接有效，无断链
  - `human-judgement` TR-1.3: 至少包含4个判断维度、5个类比高效场景、决策框架、混合策略4部分内容
  - `human-judgement` TR-1.4: 保持平衡视角，不贬低类比推理价值，包含局限性说明与进一步研究方向
- **Notes**: 优先级最高，因为适用边界研究最具实践指导价值，能直接帮助读者判断何时使用何种思维方法

## [x] Task 2: 认知科学基础研究（13-cognitive-science-foundations.md）
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 文献调研：收集类比推理、认知负荷、双系统理论（System 1/2）相关的认知科学与神经科学文献
  - 分析类比推理作为大脑默认模式的认知神经机制（基于Kahneman、Stanovich等学者研究）
  - 研究第一性原理思考的认知负荷来源与可能的量化评估方法
  - 探索降低刻意练习门槛的认知策略与训练方法（与现有练习题体系衔接）
  - 引用至少10篇学术文献，包含DOI或可验证来源
  - 编写3000-5000字的研究文档
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件13-cognitive-science-foundations.md存在，文件名符合规范，YAML frontmatter格式正确
  - `programmatic` TR-2.2: 至少包含10个学术引用，其中一级来源（DOI/arXiv/高引论文）占比不低于70%
  - `programmatic` TR-2.3: 所有内部file:///链接有效，无断链
  - `human-judgement` TR-2.4: 覆盖默认模式机制、认知负荷、训练策略三个主题，避免过度技术化，保持非专业读者可读性
- **Notes**: 理论深度最高，为思维训练提供认知科学依据

## [x] Task 3: AI时代应用研究（14-first-principles-in-ai-era.md）
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 分析AIGC时代来源验证面临的新挑战（幻觉、虚构引用、内容生成规模化等）
  - 研究对抗性审查在AI辅助下的增强模式（AI辅助事实核查、交叉验证、偏差检测等）
  - 提出AI辅助来源验证的方法论框架与工作流程
  - 探讨第一性原理思维与AI推理能力的互补关系（人类负责第一性拆解，AI负责规模化验证等）
  - 明确标注AI能力边界与局限性，避免技术乐观主义偏差
  - 编写3000-5000字的研究文档
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件14-first-principles-in-ai-era.md存在，文件名符合规范，YAML frontmatter格式正确
  - `programmatic` TR-3.2: 所有内部file:///链接有效，无断链
  - `human-judgement` TR-3.3: 覆盖新挑战、AI辅助审查框架、人机互补关系三个主题
  - `human-judgement` TR-3.4: 明确标注AI局限性，不夸大AI能力，保持技术审慎态度
- **Notes**: 时代相关性最强，探索方法论在新技术环境下的演进

## [x] Task 4: 跨学科案例库扩展（15-cross-domain-cases/）
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 创建15-cross-domain-cases/子目录
  - 生物学领域（biology.md）：精选3-5个案例（如分子生物学中心法则、达尔文进化论、系统生物学等）
  - 数学领域（mathematics.md）：精选3-5个案例（如欧几里得公理化、非欧几何、哥德尔不完备定理等）
  - 计算机科学领域（computer-science.md）：精选3-5个案例（如UNIX哲学、关系型数据库、TCP/IP设计等）
  - 社会科学领域（social-sciences.md）：精选3-5个案例（如经济学理性人假设、韦伯方法论、博弈论基础等）
  - 每个案例沿用现有格式：背景、问题、第一性原理应用过程、结果、局限性标注
  - 创建子目录README.md作为导航索引
- **Acceptance Criteria Addressed**: [AC-1, AC-4, AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-4.1: 15-cross-domain-cases/目录存在，包含biology.md、mathematics.md、computer-science.md、social-sciences.md、README.md共5个文件
  - `programmatic` TR-4.2: 每个文件文件名符合kebab-case规范，YAML frontmatter格式正确
  - `programmatic` TR-4.3: 各领域案例数量：每个领域至少3个，总计至少12个案例
  - `programmatic` TR-4.4: 所有内部file:///链接有效，无断链
  - `human-judgement` TR-4.5: 每个案例包含背景、应用过程、结果、局限性标注4部分，诚实标注事后归因偏差
- **Notes**: 工作量最大但可并行开展，显著扩展知识库的学科覆盖范围

## [x] Task 5: 更新README导航与索引
- **Priority**: high
- **Depends On**: [Task 1, Task 2, Task 3, Task 4]
- **Description**: 
  - 在[README.md](../../../../.agents/docs/knowledge/learning/first-principles/README.md)文件导航表中新增序号13-16的条目
  - 为每个新增文档提供内容简介、难度等级、阅读顺序建议
  - 在README中新增"后续研究"或"扩展阅读"区块（如需要）
  - 确保所有链接使用正确的file:///格式
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: README.md文件导航表包含序号13、14、15、16的条目
  - `programmatic` TR-5.2: 所有链接可访问，无断链（运行链接检查脚本验证）
  - `human-judgement` TR-5.3: 每个条目有清晰的内容简介，阅读顺序建议合理
- **Notes**: 所有研究文档完成后统一更新导航

## [x] Task 6: 最终质量验证与收尾
- **Priority**: high
- **Depends On**: [Task 5]
- **Description**: 
  - 运行文件名规范检查脚本验证所有新增文件
  - 运行链接检查脚本验证所有链接有效性
  - 执行对抗性审查（自我审查）：检查偏差标注、来源质量、观点平衡
  - 检查所有文档的frontmatter完整性
  - 统计一级来源占比，确保不低于70%
  - 原子提交所有变更
- **Acceptance Criteria Addressed**: [AC-1, AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件名规范检查通过（运行python .agents/scripts/check-filename-convention.py）
  - `programmatic` TR-6.2: 链接检查通过，无断链
  - `human-judgement` TR-6.3: 对抗性审查完成，偏差标注到位，观点平衡
  - `programmatic` TR-6.4: 所有文档YAML frontmatter字段完整
- **Notes**: 最终质量门禁，确保研究成果符合知识库质量标准
