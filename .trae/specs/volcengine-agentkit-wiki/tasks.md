# 火山引擎 AgentKit Wiki 教程 - The Implementation Plan (Decomposed and Prioritized Task List)
> 场景：知识沉淀（R→I→E→V链路）
> 执行深度：standard（标准版，含对抗审查V）

## [x] Task 1: R阶段 - 复盘采集事实数据（Retrospective）
> **完成记录**：60条事实（F001-F060），6大类每类≥5，来源标注齐全。G1质量门✅：0次因果词违规。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 基于已获取的 5 个官方来源（产品主页、产品简介文档、应用场景文档、VeADK 官网、AgentKit SDK官网），结构化采集客观事实
  - 按事实类别分组：产品定位事实 / 8大功能模块事实 / VeADK技术栈事实 / SDK&CLI事实 / 应用场景事实 / 竞品与生态事实
  - 产出物：`facts.md`（≥35条纯客观事实，无因果推断词，通过G1质量门）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 包含 ≥35 条编号事实条目，每条不超过 100 字
  - `programmatic` TR-1.2: G1质量门通过 — 使用正则检查 facts.md 无"因为/所以/导致/由于/因此/使得"等因果推断词
  - `human-judgement` TR-1.3: 事实覆盖 6 大类别（产品定位/功能模块/VeADK/SDKCLI/场景/生态），每类≥5条
  - `human-judgement` TR-1.4: 每条事实可溯源至明确来源（标注来源编号：S1产品主页/S2简介/S3场景/S4VeADK/S5SDK）
- **Notes**: 这是知识沉淀的基础，事实不全会导致后续洞察有偏差。事实阶段禁止加入任何主观判断。

## [x] Task 2: I阶段 - 洞察本质发现（Insight）
> **完成记录**：5条洞察（1战略+2架构+2实践），四元组完整。G2质量门✅：反常识3条高冲击+2条中冲击，证据引用全部有效。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 Task 1 的客观事实清单，提炼核心洞察
  - 每条洞察遵循四元组结构：现象陈述 + 证据引用（事实编号）+ 反常识发现 + 落地建议
  - 重点洞察方向：企业智能体工程化的本质矛盾、AgentKit 与开源框架的差异化策略、VeADK+AgentKit 的组合优势、存量系统智能化改造的关键路径
  - 产出物：`insights.md`（≥5条核心洞察，通过G2质量门）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-7, AC-8, AC-9, AC-15
- **Test Requirements**:
  - `human-judgement` TR-2.1: ≥5 条洞察，每条完整包含四元组：现象/证据(Fxx)/反常识/建议（G2质量门）
  - `human-judgement` TR-2.2: 洞察有层次感：至少 1 条产品战略层洞察 + 2 条架构设计层洞察 + 2 条落地实践层洞察
  - `programmatic` TR-2.3: 证据引用均来自 facts.md 的有效事实编号（无悬垂引用）
  - `human-judgement` TR-2.4: 反常识发现部分确实挑战了常见认知（如"智能体平台的核心不是编排而是治理"类观点），不是常规总结
- **Notes**: 洞察阶段的价值在于"反常识发现"——不是总结大家都知道的，而是提炼从事实中才能看到的深层规律。

## [/] Task 3: E阶段 - 萃取可复用模式（Extraction）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于洞察结果，提炼可迁移的模式文档
  - 模式 1：「企业级 AI Agent 平台 8 维度选型评估框架」（可用于评估任何 Agent 平台，不限于 AgentKit）
  - 模式 2：「存量业务系统智能化改造 5 步 SOP」（从 API 梳理到 Tool 接入到权限治理的标准流程）
  - 模式 3：「智能体从 Demo 到生产的 12 项检查清单」（安全/可观测/权限/成本/性能/稳定性6维度）
  - 每个模式包含：触发场景 + 核心步骤 + 反模式 + 迁移验证说明
  - 产出物：`patterns.md`（≥3个结构化模式，通过G3质量门）
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `human-judgement` TR-3.1: 模式 1（选型框架）包含 ≥8 个评估维度，每个维度有量化评分标准与权重建议
  - `human-judgement` TR-3.2: 模式 2（改造 SOP）包含 5 步流程，每步有明确输入/输出/工具，≥3 个反模式
  - `human-judgement` TR-3.3: 模式 3（Demo→生产）包含 ≥12 项检查项，覆盖 6 大维度，每项有通过/失败判定标准
  - `human-judgement` TR-3.4: G3质量门通过 — 每个模式均能迁移到至少 1 个非 AgentKit 场景（模式 1 可用于评估 Dify/LangGraph，模式 2 可用于任何 API 系统改造）
  - `human-judgement` TR-3.5: 每个模式明确标注反模式（"不要做什么"），每个模式 ≥2 条反模式
- **Notes**: 萃取模式的价值不在 AgentKit 本身，而在于提炼出跨平台、跨场景的通用方法论。模式的可迁移性是关键。

## [ ] Task 4: V阶段 - 对抗性审查验证（Adversarial Review）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 四视角攻击已产出的 facts/insights/patterns 三份文档：
    - 视角 1：魔鬼代言人 — 挑事实漏洞、质疑洞察逻辑、攻击模式适用性
    - 视角 2：纯新手用户 — 质疑术语清晰度、步骤可操作性、入门门槛描述
    - 视角 3：CTO/技术决策者 — 质疑 TCO 成本分析、与自建对比的合理性、技术栈锁定风险
    - 视角 4：未来的资深用户 — 质疑可扩展性上限、与最新技术（如 MCP 2.0/本地模型）的兼容性、架构演进能力
  - 每个视角 ≥4 条具体攻击意见，总计 ≥16 条
  - 采纳率 ≥30%（≥5 条意见被采纳并修正文档）
  - 产出物：`adversarial-review.md`（攻击意见 + 采纳记录 + 修正说明）
- **Acceptance Criteria Addressed**: 全部 AC（V阶段横切验证所有内容）
- **Test Requirements**:
  - `human-judgement` TR-4.1: 四视角齐全，每视角 ≥4 条具体攻击意见，总计 ≥16 条
  - `human-judgement` TR-4.2: 攻击意见不是客套话（如"写得不错"），而是有具体质疑点和修正建议
  - `programmatic` TR-4.3: 采纳率 ≥30% — 统计 adversarial-review.md 中标注"已采纳"的条目比例
  - `human-judgement` TR-4.4: 至少修正 1 个 facts 中的事实性错误/遗漏、至少修正 1 个 insights 中的逻辑漏洞、至少修正 1 个 patterns 中的可迁移性问题
- **Notes**: V阶段是知识沉淀质量的最后保障。对抗审查越严格，最终教程的可信度越高。不要回避尖锐问题。

## [ ] Task 5: 生成 00-overview + README 索引导航
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建 `README.md`：教程入口文件，包含简介、11章快速导航、适用人群、阅读路径
  - 创建 `00-overview.md`：教程总览与知识地图
    - AgentKit 产品生态全景图（Mermaid：平台层/SDK层/工具链层/云服务层的四层关系图）
    - 10 章内容导航表（章号/标题/核心内容/适合人群/预计阅读时间）
    - 三条阅读路径：快速上手路径（01→03→05→09）/深度开发路径（01→02→03→04→05→07→09→10）/架构决策路径（01→02→06→08→09→10）
    - 与现有知识库 ≥6 个 wiki 的交叉引用矩阵（表格：关联 wiki/关联章节/互补关系）
- **Acceptance Criteria Addressed**: AC-1, AC-12, AC-14, AC-15
- **Test Requirements**:
  - `programmatic` TR-5.1: 目录下存在 README.md 和 00-overview.md，两个文件均 < 300 行
  - `human-judgement` TR-5.2: 00-overview.md 包含完整的 Mermaid 产品生态四层关系图（≥12 个节点）
  - `human-judgement` TR-5.3: 三条阅读路径明确，每路径列出章节顺序和预计总阅读时间
  - `programmatic` TR-5.4: YAML frontmatter 齐全，source 字段 = `seven-concepts: volcengine-agentkit-wiki`，category = `learning`
  - `human-judgement` TR-5.5: 交叉引用矩阵列出 ≥6 个已有 wiki，明确关联章节与互补关系

## [ ] Task 6: 生成产品层文档（01-product-intro + 02-core-architecture）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `01-product-intro.md`（产品介绍与核心概念）：
    - Wikipedia 风格定义 + 工程化 4 大痛点分析
    - 8 大功能模块详解（每模块：定位/核心能力/解决问题/关联组件）
    - 4 大产品优势（敏捷开发/生产就绪/开放兼容/成本优化），每优势配 2-3 条具体证据
    - 产品发展时间线（Mermaid timeline：2024 H2 内测 → 2025 GA → 2025 H2 VeADK 开源 → 2026 A2A/MCP 增强）
    - 底部双向导航
  - `02-core-architecture.md`（架构与核心能力）：
    - Agent Ready 基础设施分层架构图（Mermaid：接入层/编排层/运行层/数据层/治理层/观测层）
    - 动态 Harness 编排：配置即部署/热切换/复杂任务调度的实现机制
    - Serverless 运行底座：秒级扩缩容/多租户隔离/内置工具集
    - 安全防护三层模型：身份管控/云身份管控/内容护栏，每层 2-3 个具体能力
    - 评测与可观测闭环：离线评估→在线监控→满意度分析→持续优化（Mermaid 流程图）
    - 底部双向导航
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-12, AC-14
- **Test Requirements**:
  - `programmatic` TR-6.1: 两个文件均存在，每个 < 300 行
  - `human-judgement` TR-6.2: 01 的 8 大功能模块清晰对应 Runtime/Identity/Gateway/A2A/Session/Memory/Knowledge/Observability/Evaluation（注意 Session&Memory 算两个）
  - `human-judgement` TR-6.3: 02 的 Mermaid 分层架构图 ≥6 层，每层 ≥2 个组件节点
  - `human-judgement` TR-6.4: 02 的安全三层模型每层描述 ≥2 个具体能力点，不是空泛概念
  - `programmatic` TR-6.5: 两个文件 frontmatter 规范，底部均有双向导航链接

## [ ] Task 7: 生成开发工具链文档（03-veadk-framework + 04-agentkit-sdk-cli + 05-quickstart）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `03-veadk-framework.md`（VeADK 开发框架）：
    - VeADK 定位与 Google ADK 兼容性说明（什么是 ADK、为什么兼容）
    - 三语言安装命令：Python（pip+git+镜像）/ Go（go get）/ Java（Maven pom.xml），每语言≥2个安装方式
    - VeADK Family 产品融合矩阵（表格：组件/火山引擎产品/说明，≥20行，含大模型/提示词/工具/记忆/知识库/可观测/评测/云部署 8 大类）
    - DeepResearch 6 大构建特性详解（每特性：能力描述/产品支撑/使用场景）
    - GitHub 开源仓库 3 个链接 + 镜像仓库地址 3 个
    - 底部双向导航
  - `04-agentkit-sdk-cli.md`（SDK & CLI 工具链）：
    - 装饰器式 API 设计：`@app.entrypoint` 代码示例（≥20行完整示例，含 import/定义/入口/调用）
    - CLI 全命令清单：init/config/build/deploy/launch，每命令：功能/参数/示例输出
    - 三种部署模式对比表（Local/Hybrid/Cloud）：适用场景/资源需求/开发效率/运维成本/典型用户，5维度
    - Platform 服务集成：Memory/Knowledge/MCP Gateway 每服务的接入说明 + 代码片段
    - 底部双向导航
  - `05-quickstart.md`（快速入门指南）：
    - 前置条件清单（4项：火山引擎账号/实名认证/AgentKit权限开通/Python≥3.10）
    - 5 步标准上手流程：Step1环境安装 → Step2项目初始化 → Step3配置参数 → Step4构建部署 → Step5调用测试，每步：命令+预期输出截图（文字描述）+ 注意事项
    - ≥5 个常见问题排查（权限错误/网络超时/镜像拉取失败/配置缺失/版本不兼容），每条含：错误信息/原因/解决方案
    - 底部双向导航
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6, AC-12, AC-14
- **Test Requirements**:
  - `programmatic` TR-7.1: 三个文件均存在，每个 < 300 行
  - `human-judgement` TR-7.2: 03 的产品融合矩阵表格 ≥20 行且分类清晰（8大类），不是零散罗列
  - `human-judgement` TR-7.3: 04 的装饰器代码示例可运行（语法正确、import 齐全、有入口点调用）
  - `human-judgement` TR-7.4: 04 的三种部署模式对比表 5 维度齐全，有明确差异
  - `human-judgement` TR-7.5: 05 的 5 步流程每步命令可复制执行，预期输出明确；FAQ ≥5 条且每条有具体错误信息
  - `programmatic` TR-7.6: 三个文件 frontmatter 规范，底部均有双向导航

## [ ] Task 8: 生成应用与集成文档（06-application-scenarios + 07-core-features-detailed）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `06-application-scenarios.md`（应用场景与落地方案）：
    - 4 大典型企业场景：
      1. 企业内部员工助手：描述 + 参考架构（Mermaid：用户/门户/Agent/知识库/工具/鉴权/可观测） + 关键能力映射 + 5步实施
      2. 业务系统智能化改造（工单/订单/CRM）：描述 + 架构（存量API→Gateway Tool→Agent→交互） + 5步实施 + 引用模式2
      3. 多Agent编排与复杂工作流：描述 + 架构（主控Agent/专业Agent/A2A协议/任务状态） + 5步实施 + 交叉引用 agent-communication-protocols A2A 章节
      4. 生产级AI应用平台化交付：描述 + 架构（多租户/资源隔离/统一治理/统一观测） + 5步实施
    - 3 大行业落地框架：泛互联网科技/零售电商/制造业，每行业：2-3 个具体用例 + 核心能力组合
    - 标准化 vs 定制化选型决策树（Mermaid：业务复杂度/团队能力/预算/是否有存量系统 → 结论）
    - 底部双向导航
  - `07-core-features-detailed.md`（核心功能深度解析）：
    - Identity 统一鉴权：用户池管理/IdP 集成（SAML/OIDC）/智能体身份标签/第三方凭据托管/动态授权 5 子模块，每模块：原理+接入模式+配置示例
    - Gateway 工具接入：MCP Server 接入流程/REST/OpenAPI 转换流程/调用治理（限流/熔断/审计）3 子模块，每模块流程步骤 + 代码片段 + 交叉引用 MCP 协议章节
    - A2A 协议支持：任务分发机制/结果回传格式/状态同步协议 3 子模块，含消息交互图（Mermaid sequence）
    - Session & Memory 分层：短期记忆持久化（MySQL/PG）/长期记忆召回（Viking/OpenSearch/Redis）/跨会话记忆策略 3 子模块，含数据流转图
    - Knowledge 知识检索：LlamaIndex 入口配置/Viking 知识库后端接入/检索调优 3 子模块，含代码片段
    - 底部双向导航
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-12, AC-14, AC-15
- **Test Requirements**:
  - `programmatic` TR-8.1: 两个文件均存在，每个 < 300 行
  - `human-judgement` TR-8.2: 06 的 4 大场景每个含：文字描述 + Mermaid 架构图 + 关键能力映射 + 5 步实施（4要素齐全）
  - `human-judgement` TR-8.3: 06 的选型决策树可执行 — 回答 4 个 yes/no 问题即可得出明确结论
  - `human-judgement` TR-8.4: 07 的 5 大模块每模块包含 ≥3 个子模块详解，不是蜻蜓点水
  - `human-judgement` TR-8.5: 07 有明确的交叉引用：Gateway 引用 MCP 协议 wiki、A2A 引用 A2A 协议 wiki
  - `programmatic` TR-8.6: 两个文件 frontmatter 规范，底部均有双向导航

## [ ] Task 9: 生成选型与资源文档（08-comparison-ecosystem + 09-faq-best-practices + 10-resources-glossary）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `08-comparison-ecosystem.md`（竞品对比与生态定位）：
    - 10 维度对比表格：AgentKit vs LangGraph vs LangChain vs LlamaIndex vs Coze vs Dify（6平台 × 10维度：抽象层次/开发者体验/部署模式/安全治理/可观测性/成本/生态/开源协议/企业级能力/学习曲线），每格有明确评分或描述
    - AI Agent 平台 8 维度选型评估框架（引用 Task 3 模式 1）：评估维度/权重/1-5分标准/AgentKit 示例得分，附可复用打分模板
    - 火山引擎 AI 产品矩阵定位图（Mermaid：大模型层/开发框架层/平台层/应用层，AgentKit 在平台层的位置，与 Ark/Viking/VeFaaS/APM 的关系）
    - 自研 vs 采购决策树：团队规模/预算/定制化需求/安全合规要求/时间窗口 → 结论
    - 底部双向导航
  - `09-faq-best-practices.md`（FAQ 与最佳实践）：
    - FAQ ≥15 条，6 大分类：开通计费（3条）/权限配置（3条）/部署问题（3条）/调试排障（3条）/性能优化（2条）/安全合规（1条），每条：问题 + 原因 + 解决方案
    - 8 条最佳实践：
      1. 从 Demo 到生产的 12 项检查清单（引用 Task 3 模式 3）
      2. 存量系统智能化改造 SOP（引用 Task 3 模式 2）
      3. 多租户隔离策略（硬隔离 vs 软隔离选型）
      4. 成本优化 4 招（Serverless 弹性/冷启动策略/资源配额/路由优化）
      5. 知识库质量保障 3 原则（数据源治理/分块策略/检索效果评估）
      6. 智能体权限最小化原则（身份/工具/数据三层最小权限）
      7. 可观测性埋点标准（至少埋哪些关键事件）
      8. A/B 测试驱动的智能体迭代方法论
    - 常见陷阱 ≥5 条：陷阱描述 + 触发条件 + 规避方案
    - 底部双向导航
  - `10-resources-glossary.md`（术语表与参考资源）：
    - 术语表 ≥20 条：AgentKit/Harness/VeADK/A2A/MCP/Gateway/Session/Memory/Knowledge/RAG/Runtime/Identity/Evaluation/Observability/Tracing/Serverless/Multi-Tenant/IdP/IAM/VikingDB，每条：英文/中文/标准定义
    - 官方资源汇总：产品主页/控制台/产品文档中心/VeADK Python文档/VeADK Go文档/VeADK Java文档/SDK文档/GitHub仓库×3/开发者社区，每项含链接
    - 扩展阅读推荐：MCP协议 wiki/A2A协议 wiki/智能体七大组件 wiki/对抗审查评测 wiki/智能体接口 deep-dive wiki/Skill开发 wiki/LongCat Agent wiki 等 ≥10 个知识库交叉引用，每项：关联 wiki/推荐章节/为什么读
    - 版本兼容性说明（AgentKit SDK 版本 × VeADK 版本兼容矩阵，≥3行）
    - 底部双向导航
- **Acceptance Criteria Addressed**: AC-9, AC-10, AC-11, AC-12, AC-14, AC-15
- **Test Requirements**:
  - `programmatic` TR-9.1: 三个文件均存在，每个 < 300 行
  - `human-judgement` TR-9.2: 08 的对比表格 6平台×10维度齐全，每格不是"待补充"，有具体描述或评分
  - `human-judgement` TR-9.3: 08 的选型评估框架有量化打分标准，读者可直接套用
  - `human-judgement` TR-9.4: 09 的 FAQ ≥15 条，6大分类齐全，每条有原因+解决方案（不只是"联系客服"）
  - `human-judgement` TR-9.5: 09 的 8 条最佳实践每条有可操作步骤，不是空泛口号
  - `human-judgement` TR-9.6: 10 的术语表 ≥20 条，每条定义准确简洁
  - `human-judgement` TR-9.7: 10 的知识库交叉引用 ≥10 个，每项明确推荐章节与学习价值
  - `programmatic` TR-9.8: 三个文件 frontmatter 规范，底部均有双向导航

## [ ] Task 10: 整体验证 + 链接修复 + 入库提交
- **Priority**: high
- **Depends On**: Task 5, Task 6, Task 7, Task 8, Task 9
- **Description**:
  - 运行链接检查（`check-links.py --path .../volcengine-agentkit-wiki/`），修复所有断链和 `file:///` 绝对路径
  - 验证所有 11+1 个文件 frontmatter 一致性（source/category/tags 统一）
  - 验证 G1-G3 质量门完整：facts.md（G1）/insights.md（G2）/patterns.md（G3）三份中间产出的质量门通过记录
  - 验证 AC-1 到 AC-15 验收标准逐项通过，产出 `verification-report.md` 验收报告
  - （可选）运行 docgen-cmd 更新知识库索引（不在本任务必做范围，但需要确认目录位置正确）
- **Acceptance Criteria Addressed**: AC-1, AC-12, AC-13, AC-14, AC-15
- **Test Requirements**:
  - `programmatic` TR-10.1: 链接检查脚本 0 errors，0 warnings（内部链接）
  - `programmatic` TR-10.2: 12 个文件 frontmatter 字段齐全（id/title/source/category/tags/date/status/author/summary），source 字段值统一
  - `programmatic` TR-10.3: verification-report.md 包含 AC-1 到 AC-15 逐项验证结果（✓/✗ + 备注）
  - `human-judgement` TR-10.4: G1-G3 质量门通过记录齐全，每个质量门有具体验证方法和结果
  - `programmatic` TR-10.5: 所有文件 < 300 行（NFR-1 合规）

## 七概念编排执行总结
```
知识沉淀链路：R → I → E → V → 教程生成（Task5-9）→ 验证入库（Task10）
质量门位置：G1(R阶段) → G2(I阶段) → G3(E阶段) → V门(V阶段) → G4（可选，Task10整体验证可视为G4等价）
中间产出：facts.md / insights.md / patterns.md / adversarial-review.md / verification-report.md
最终产出：00-overview.md ~ 10-resources-glossary.md + README.md 共 12 文件
```
