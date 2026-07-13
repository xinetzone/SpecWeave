# 七概念驱动的GPT-5.6时代Prompt Engineering Wiki教程 - The Implementation Plan

## [ ] Task 1: 创建Wiki目录结构与入口文件
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建目标目录 `docs/knowledge/learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/`
  - 创建README.md索引入页：包含文档索引表、主题概述、分层阅读路径（3条路径）、相关资源链接
  - 创建00-overview.md概述页：教程定位、学习目标、适用人群、可信度评级说明、文件导航表
  - 两个文件均需包含完整YAML frontmatter（id/title/category/date/version/status）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-9
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录创建成功，包含README.md和00-overview.md
  - `programmatic` TR-1.2: 两个文件frontmatter字段完整（6个必填字段）
  - `human-judgement` TR-1.3: README包含完整文档索引表（15个文件条目）
  - `human-judgement` TR-1.4: README包含至少3条分层阅读路径
  - `human-judgement` TR-1.5: 00-overview包含可信度评级说明
- **Notes**: 参考adversarial-review-wiki的README和00-overview结构

## [ ] Task 2: 创建范式变革与七概念映射章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建01-paradigm-shift.md：GPT-5.6带来的范式转变——从"规定过程"到"明确目标"，包含OpenAI测试数据（Eval+10-15%/Token-41-66%/成本-33-67%）、新旧范式对比
  - 创建02-seven-concepts-mapping.md：七概念（R-I-E-C-A-F-V）与Prompt Engineering的完整映射，包含五层模型对应关系、七概念驱动的Prompt编写工作流Mermaid图
  - 两个文件均需包含frontmatter，七概念映射不得歪曲原意
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: 两个文件创建成功，frontmatter完整
  - `human-judgement` TR-2.2: 范式转变章节包含完整测试数据与新旧对比
  - `human-judgement` TR-2.3: R/I/E/C/A/F/V每个概念都有明确的Prompt环节映射
  - `human-judgement` TR-2.4: 包含七概念驱动的Prompt工作流图（Mermaid）
  - `human-judgement` TR-2.5: 明确标注七概念整合为SpecWeave方法论，非OpenAI官方内容
- **Notes**: 对照seven-concepts-quick-reference.md确保映射准确

## [ ] Task 3: 创建GCOB四要素框架详解
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建03-gcob-framework.md：Goal-Context-Output-Boundaries四要素完整详解
  - 每个要素包含：定义、为什么重要、使用要点、正反示例、常见错误
  - 包含完整Prompt示例（项目状态通报案例）
  - 包含"把这些拼在一起"的完整示例（中英对照）
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件创建成功，frontmatter完整
  - `human-judgement` TR-3.2: 四个要素每个都有定义+要点+示例
  - `human-judgement` TR-3.3: 包含完整项目状态通报Prompt示例（中英对照）
  - `human-judgement` TR-3.4: 每个要素至少1个反面示例说明常见错误
- **Notes**: GCOB=Goal+Context+Output+Boundaries，这是OpenAI官方核心框架

## [ ] Task 4: 创建新写法核心规则与Before/After示例
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 创建04-new-paradigm-rules.md：新范式核心规则，包含应删除的5类内容详解、任务复杂度与Prompt长度指南（四级表格）、Steer与Queue机制说明
  - 创建05-before-after-examples.md：6组完整Before/After对照（内容分析、代码生成、翻译、研究分析完整结构、Agent工具调用、日常任务）
  - 每个Before/After包含：旧写法问题分析、新写法要点说明、可复制的完整Prompt
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 两个文件创建成功，frontmatter完整
  - `human-judgement` TR-4.2: 5类应删除内容每类都有说明和示例
  - `human-judgement` TR-4.3: 四级任务复杂度表格完整（结构+样例）
  - `human-judgement` TR-4.4: 6组Before/After完整，每组包含问题分析+新写法要点+可复制Prompt
  - `human-judgement` TR-4.5: 研究分析类和Agent工具调用类示例包含完整五段结构（Context/Request/Output/Constraints/Checkpoint）
  - `human-judgement` TR-4.6: Steer与Queue机制有清晰说明和使用场景
- **Notes**: 6组示例必须与微信文章中的内容一致，可补充说明但不得遗漏

## [ ] Task 5: 创建三大场景实战指南（上）：Chat与Work场景
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 创建06-chat-scenarios.md：Chat场景4大用法（理解话题、起草文字、比较选项、实用计划），每个场景包含适用场景说明、Prompt模板、完整示例
  - 创建07-work-scenarios.md：Work场景3大用法（源材料转成品、决策调研、协调发布），包含Work高效使用指南、示例
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 两个文件创建成功，frontmatter完整
  - `human-judgement` TR-5.2: Chat场景4个用法每个都有模板和示例
  - `human-judgement` TR-5.3: Work场景包含高效使用指南（6条要点）
  - `human-judgement` TR-5.4: Work场景3个用法每个都有完整示例
- **Notes**: Chat适合快问快答，Work适合多步骤复杂任务，明确区分两者适用边界

## [ ] Task 6: 创建三大场景实战指南（下）：Codex开发场景
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 创建08-codex-scenarios.md：Codex场景8大开发工作流（解释代码库、修Bug、写测试、截图转原型、UI迭代、云端重构、本地Code Review、GitHub PR审查、更新文档）
  - 每个工作流包含：适用场景、载体选择（IDE/CLI/Cloud）、步骤说明、示例Prompt、上下文说明、验证方式
  - 包含Codex prompt核心四要素（行为+代码/复现步骤+约束+验证）
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件创建成功，frontmatter完整
  - `human-judgement` TR-6.2: 至少8个Codex工作流，每个都有完整要素
  - `human-judgement` TR-6.3: 每个工作流包含示例Prompt，可直接复制修改
  - `human-judgement` TR-6.4: 明确说明IDE/CLI/Cloud三种载体的差异
- **Notes**: Codex场景是开发者最常用的部分，示例要贴近真实开发场景

## [ ] Task 7: 创建检查清单、反模式与模板库
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 创建09-checklists-templates.md：Prompt五问自检清单（目标/完成/不能猜/不能越界/何时停）、可直接复用的Prompt模板库（研究分析、Agent编码、Bug修复、邮件写作等）、终检要求
  - 创建10-anti-patterns.md：5类以上反模式（如形容词堆砌、规定思考过程、无效角色设定、冗余规则、边界不清），每个反模式包含：特征识别、为什么有害、修正方案、Before/After
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 两个文件创建成功，frontmatter完整
  - `human-judgement` TR-7.2: 五问自检清单每个问题都有判定标准
  - `human-judgement` TR-7.3: 模板库至少包含5个可直接复用的模板，带占位符说明
  - `human-judgement` TR-7.4: 至少5类反模式，每类有特征+危害+修正方案+Before/After
  - `human-judgement` TR-7.5: 检查清单采用yes/no判定格式，可打印使用
- **Notes**: 这部分是可操作性最强的章节，模板必须可以直接复制使用

## [ ] Task 8: 创建术语表、FAQ与资源索引
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 创建11-glossary.md：核心术语表（中英文对照），至少15个术语，包含：Prompt、GCOB、Steer、Queue、Context Window、Checkpoint、Codex、Eval、Token等关键术语
  - 创建12-faq-resources.md：常见问题FAQ（至少10个问题）、延伸阅读资源索引、相关Wiki交叉引用
- **Acceptance Criteria Addressed**: AC-2, AC-10
- **Test Requirements**:
  - `programmatic` TR-8.1: 两个文件创建成功，frontmatter完整
  - `programmatic` TR-8.2: 术语表至少15个术语（计数检查）
  - `programmatic` TR-8.3: FAQ至少10个问题（计数检查）
  - `human-judgement` TR-8.4: FAQ覆盖高频疑问（旧写法还能用吗？小模型适用吗？中文Prompt注意事项？等）
  - `human-judgement` TR-8.5: 资源索引包含相关Wiki链接（Karpathy准则、对抗性审查等）
- **Notes**: 术语解释要通俗易懂，避免学术化；FAQ要回答读者真正会问的问题

## [ ] Task 9: 创建快速参考速查表
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - 创建13-quick-reference.md：一页纸速查表
  - 包含：GCOB四要素速查卡、6组Before/After速览、五问自检清单、反模式速查、不同任务复杂度Prompt长度速查、核心模板骨架
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件创建成功，frontmatter完整
  - `human-judgement` TR-9.2: 内容紧凑，适合快速查阅，每个速查项不超过半页
  - `human-judgement` TR-9.3: 包含所有核心框架要点，无需翻其他章节即可快速上手
- **Notes**: 速查表要做到打印出来贴在显示器边就能用的程度

## [ ] Task 10: 更新上级目录索引并验证链接
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 更新 `docs/knowledge/learning/02-agent-engineering-methodology/README.md`
  - 在子Wiki索引表中添加本教程条目（文件数、核心主题）
  - 在快速导航表中添加Prompt Engineering场景分组
  - 在推荐学习路径中整合本教程
  - 运行链接检查脚本验证所有内部链接有效
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `human-judgement` TR-10.1: 子Wiki索引表有本教程条目，描述准确
  - `human-judgement` TR-10.2: 快速导航表有Prompt Engineering分组
  - `human-judgement` TR-10.3: 至少1条学习路径包含本教程
  - `programmatic` TR-10.4: 运行check-links.py无断链、无file:///绝对路径
- **Notes**: 更新时遵循现有README的表格格式，不要破坏其他条目
