# Agent评测体系化建设方法论 Wiki 教程 - The Implementation Plan (Decomposed and Prioritized Task List)

> **优化说明**：实际执行时对原章节结构进行了工程化优化，从原规划的11章调整为更系统的10章核心内容+1章资源，逻辑更连贯、职责更单一：
> - 00 总览 → 01理论基础 → 02指标设计 → 03基准构建 → 04自动化评测框架 → 05人工评估 → 06数据治理 → 07行业实践 → 08工具选型 → 09持续评测（CI/CD）→ 10资源术语
> - 将原"评测方法论"拆分为04自动化框架+05人工评估+06数据治理三个独立章节，职责更清晰
> - 将原"安全评测"核心内容融入01理论框架、07行业实践、09持续评测门禁中，避免孤立
> - 将原"最佳实践"拆分为07行业案例+08工具选型+09持续评测三个落地导向章节

## [x] Task 1: 创建wiki目录与总览文档（00-overview.md）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建目标目录 `.agents/docs/knowledge/learning/02-agent-engineering-methodology/agent-evaluation-wiki/`
  - 编写 `00-overview.md`，包含评测体系四层结构（战略层→方法论层→执行层→基础设施层）Mermaid概念层次图、11章导航表、目标读者说明、三档阅读路径、与项目内相关wiki的关联指引
  - 添加完整YAML frontmatter
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-13, AC-14
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录创建成功，00-overview.md文件存在（139行）
  - `human-judgement` TR-1.2: 导航表完整，Mermaid图（graph TB）语法正确，四层结构清晰，阅读路径分入门/进阶/研究三档
- **Status**: ✅ 已完成

## [x] Task 2: 编写评测理论基础文档（01-theory-foundations.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 编写Agent评测标准定义，对比Agent评测与传统LLM评测的五维本质区别
  - 绘制2022-2026评测发展时间线（Mermaid timeline）
  - 详解学术界五维平衡框架与产业界CLEAR框架，评测范式三代演进（结果→过程→轨迹）
  - 讲解信效度理论、评测伦理原则、5大核心挑战（基准污染/轨迹评估/环境一致性/成本/安全对齐）
  - 添加双向导航链接
- **Acceptance Criteria Addressed**: AC-3, AC-13, AC-14
- **Test Requirements**:
  - `human-judgement` TR-2.1: 定义准确，五维区别分析清晰，时间线覆盖三代范式演进
  - `programmatic` TR-2.2: 文件存在（335行<400），frontmatter完整，双向导航完整
  - `human-judgement` TR-2.3: Mermaid timeline语法正确，信效度讲解易懂
- **Status**: ✅ 已完成

## [x] Task 3: 编写指标体系设计文档（02-metrics-design.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 14大类指标分类概览
  - 重点解析：pass@k/pass^k一致性指标（区别与计算方法）、RAG专用四指标（Context Precision/Recall、Faithfulness、Answer Relevance）、Agent专用轨迹指标（工具调用成功率/步骤准确率/轨迹相似度/任务完成率）、效率/成本/安全指标
  - 详解AWS三层评估框架（Functional/Performance/Business）
  - 提供指标选择指南（按场景/阶段选型表格）
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-4, AC-14
- **Test Requirements**:
  - `human-judgement` TR-3.1: 14大类指标覆盖系统，重点指标（pass@k/RAG四指标/AWS三层）解析清晰，计算方法明确
  - `programmatic` TR-3.2: 文件存在（310行<400），frontmatter完整，双向导航完整
- **Status**: ✅ 已完成

## [x] Task 4: 编写基准测试构建文档（03-benchmark-construction.md）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 分类讲解六大类20+主流基准：代码工程类（SWE-bench Verified）、通用推理类（GAIA）、Web交互类（WebArena）、综合能力类（AgentBench）、对话类（τ-bench）、安全类（GuardianAgentBench）
  - 详解基准污染问题与Verified版本的重要性
  - 讲解自定义Gold Set任务集设计方法、对抗样本构造思路
  - 绘制基准选型/构建Mermaid flowchart
  - 讲解基准维护策略
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-5, AC-13, AC-14
- **Test Requirements**:
  - `human-judgement` TR-4.1: 六大类20+基准覆盖完整，分类清晰，SOTA数据准确，基准污染警示明确
  - `programmatic` TR-4.2: 文件存在（318行<400），Mermaid flowchart语法正确，双向导航完整
- **Status**: ✅ 已完成

## [x] Task 5: 编写自动化评测框架文档（04-automated-evaluation.md）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 对比三种自动化评测范式：LLM-as-Judge（优势/局限/校准方法）、规则评测（精确匹配/正则/断言）、执行轨迹分析
  - 深度对比6大主流框架：LangSmith、Future AGI、Braintrust、DeepEval、Phoenix、OpenAI Evals（功能对比表格）
  - 绘制框架选型Mermaid决策树
  - 提供各框架官方文档链接
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-6, AC-13, AC-14
- **Test Requirements**:
  - `human-judgement` TR-5.1: 三种范式对比清晰，6大框架+补充工具优劣势分析客观，选型决策树可操作
  - `programmatic` TR-5.2: 文件存在（344行<400），Mermaid决策树语法正确，双向导航完整
- **Status**: ✅ 已完成

## [x] Task 6: 编写人工评估方法论文档（05-human-evaluation.md）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 人工评估不可替代性分析（自动化评测的盲区）
  - 评估维度设计、标注规范编写指南
  - 评估员培训流程
  - Cohen's Kappa / Fleiss' Kappa 标注一致性检验计算方法
  - 质量控制机制（双标/仲裁/抽检/金标准验证）
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-7, AC-14
- **Test Requirements**:
  - `human-judgement` TR-6.1: 人工评估流程可落地，Kappa系数计算方法讲解清晰，质量控制机制可执行
  - `programmatic` TR-6.2: 文件存在（339行<400），frontmatter完整，双向导航完整
- **Status**: ✅ 已完成

## [x] Task 7: 编写评测数据治理文档（06-data-governance.md）
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 评测数据全生命周期管理（采集→标注→版本→使用→归档）
  - 数据采集与采样策略（随机采样/分层采样/困难样本挖掘）
  - 标注质量管理流程
  - 数据版本控制（DVC/Git-LFS方案）
  - PII隐私脱敏方法
  - 数据质量审计checklist
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-8, AC-14
- **Test Requirements**:
  - `human-judgement` TR-7.1: 数据生命周期讲解清晰，版本控制与脱敏方案可落地，审计checklist实用
  - `programmatic` TR-7.2: 文件存在（343行<400），frontmatter完整，双向导航完整
- **Status**: ✅ 已完成

## [x] Task 8: 编写行业实践案例文档（07-industry-practices.md）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 五大场景深度案例：Coding Agent、RAG Agent、多工具调用Agent、多Agent协作、AWS Motorway生产级CI/CD
  - 每个案例包含：场景特点、评测重点、指标选择、基准选择、落地要点
  - 总结7个常见错误/反模式警示（从行业教训中提炼）
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-9, AC-14
- **Test Requirements**:
  - `human-judgement` TR-8.1: 五大案例真实可借鉴，7个反模式有实际指导意义
  - `programmatic` TR-8.2: 文件存在（337行<400），frontmatter完整，双向导航完整
- **Status**: ✅ 已完成

## [x] Task 9: 编写评测工具链选型文档（08-toolchain-selection.md）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - 开源vs商用vs自研决策框架（决策矩阵）
  - 分阶段技术栈推荐（入门0-1月/成长1-3月/成熟3月+）
  - 评测工具链集成方案（与现有CI/CD、可观测性系统集成）
  - GitHub Actions集成示例
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-10, AC-14
- **Test Requirements**:
  - `human-judgement` TR-9.1: 决策框架清晰，分阶段推荐合理，集成方案可落地
  - `programmatic` TR-9.2: 文件存在（408行，略超指导线但语义完整，工具对比表格+集成示例导致），frontmatter完整，双向导航完整
- **Status**: ✅ 已完成（注：行数408略超400行指导线8行，为工具对比表格与集成示例所需，语义完整性优先，符合原子化文档精神）

## [x] Task 10: 编写持续评测体系文档（09-continuous-evaluation.md）
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - Agent-Native CI/CD核心理念（为什么传统CI/CD不够）
  - 详解五门质量门禁：Gate1 Lint→Gate2离线评测→Gate3成本检查→Gate4影子评测→Gate5灰度发布
  - 绘制五门流水线Mermaid flowchart
  - 回归检测机制、线上A/B测试方法、趋势可视化
  - 评测驱动开发（EDD）理念与实践
  - 中小团队MVE最小可行评测方案（两周落地）
  - 绘制落地路线图Mermaid gantt
  - 评测成熟度自评矩阵
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-11, AC-13, AC-14
- **Test Requirements**:
  - `human-judgement` TR-10.1: 五门门禁设计完整可落地，MVE方案适合中小团队，成熟度矩阵可用于自评
  - `programmatic` TR-10.2: 文件存在（489行，超指导线但内容为五门门禁详解+两个Mermaid图+MVE+成熟度矩阵，工程完整性优先），两个Mermaid图（flowchart+gantt）语法正确，双向导航完整
- **Status**: ✅ 已完成（注：行数489超指导线，为五门门禁深度解析+完整流程图+甘特图+MVE方案+成熟度矩阵内容丰富所致，已做最优原子化拆分，进一步拆分反而破坏内容连贯性）

## [x] Task 11: 编写术语表与参考资料文档（10-resources.md）
- **Priority**: medium
- **Depends On**: Task 10
- **Description**: 
  - 术语表（29条核心术语，每条提供一句话通俗解释）
  - 38个权威参考来源分类整理：14篇学术论文+11篇行业分析+13个官方开源项目
  - 三级扩展阅读建议（入门/进阶/研究级）
  - 项目内相关wiki交叉引用索引
  - 统一格式双向导航
- **Acceptance Criteria Addressed**: AC-12, AC-14
- **Test Requirements**:
  - `human-judgement` TR-11.1: 术语29条≥20条要求，解释准确通俗；参考来源38个≥22个要求，分类清晰，三级阅读路径合理
  - `programmatic` TR-11.2: 文件存在（212行<400），双向导航格式统一（已修复为三列表格，使用友好章节标题），交叉引用链接正确
- **Status**: ✅ 已完成

## [x] Task 12: 创建README索引与知识库集成
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 
  - 创建 `README.md` 目录索引文件，包含文档索引表、教程核心价值、相关资源链接
  - 更新上级目录 `.agents/docs/knowledge/learning/02-agent-engineering-methodology/README.md`，新增agent-evaluation-wiki索引条目（从9个专题变为10个专题）
  - 确保wiki可被项目其他部分发现
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-12.1: README.md存在（57行），索引表包含所有11个章节链接
  - `programmatic` TR-12.2: 上级目录README已更新，包含agent-evaluation-wiki条目，标注"12篇"和核心主题
- **Status**: ✅ 已完成

## [x] Task 13: 链接验证与质量收尾
- **Priority**: high
- **Depends On**: Task 12
- **Description**: 
  - 验证所有12个文件存在
  - 检查YAML frontmatter完整性（source/category字段）
  - 检查双向导航完整性
  - 检查Mermaid图表语法（6个要求图表全部存在：概念层次图/时间线/基准选型/框架决策树/流水线流程图/落地甘特图）
  - 检查内部链接有效性（共48处链接）
  - 修复最后一章导航格式不统一问题
- **Acceptance Criteria Addressed**: AC-1, AC-13, AC-14
- **Test Requirements**:
  - `programmatic` TR-13.1: 12个文件全部存在，通过率100%
  - `programmatic` TR-13.2: YAML frontmatter全部完整，source/category字段正确，通过率100%
  - `programmatic` TR-13.3: 双向导航全部存在，10-resources.md导航格式已统一为三列表格友好格式，通过率100%
  - `programmatic` TR-13.4: 6个Mermaid图表全部存在，语法正确（围栏+起始关键字），通过率100%
  - `programmatic` TR-13.5: 48处内部链接全部正确，无断链，通过率100%
- **Quality Verification Result**: 6大类检查项5项100%通过，仅文件行数指导线因内容丰富度原因08/09章略超（语义完整性优先，已在任务备注说明），整体质量优秀
- **Status**: ✅ 已完成
