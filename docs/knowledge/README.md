# 项目知识库

## 统计摘要

- **总条目数**：154

| 分类 | 数量 |
|------|------|
| architecture | 1 |
| best-practices | 2 |
| decisions | 1 |
| docs | 8 |
| knowledge/learning | 1 |
| learning | 84 |
| operations | 8 |
| research | 1 |
| standards | 1 |
| troubleshooting | 3 |
| unknown | 44 |

## 按类别浏览

### architecture

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | SpecWeave项目治理方法论体系的架构总览文档，定义了治理基建四层递进核心模型，以及围绕该模型形成的5个可复用元洞察模式，包含模式间关系、落地状态和自反性验证案例。 | 2026-06-30 | governance、architecture、methodology、stage-guardrails、patterns、four-layer-model、governance-loop、retrospective、meta-insights |

### best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | SpecWeave 项目中 Mermaid 图表的一站式操作手册，涵盖起步模板、安全编码六规则、自动化检查工具详解、渲染问题排查流程和不同图表类型注意事项。 | 2026-06-29 | mermaid、图表、可视化、check-mermaid、安全编码、六规则、模板、ci |
| [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md) | 基于MDI项目parser.py（1465行）重构复盘的经验总结：处理半结构化数据（Markdown/自然语言/配置文件）的Parser应预留2-3倍于Generator的时间/代码量预算，遵循三层架构拆分，并先写20+边界case测试。 | 2026-07-03 | parser、复杂度预算、semi-structured-parsing、三层架构、边界case、TDD、checklist |

### decisions

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由 | 2026-06-23 | architecture、naming、directory、vendor、convention |

### docs

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [MDI研究报告 - 执行摘要](mdi-research/00-executive-summary.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 可行性分析](mdi-research/01-feasibility-analysis.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 生态对比分析](mdi-research/02-ecosystem-comparison.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 技术架构深度解析](mdi-research/03-technical-architecture.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 工具链使用指南](mdi-research/04-toolchain-guide.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 版本控制与变更管理最佳实践](mdi-research/05-versioning-best-practices.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 未来演进方向](mdi-research/06-future-evolution.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 结论](mdi-research/07-conclusion.md) |  | 2026-07-02 | - |

### knowledge/learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [MopMonk 安全 Agent Wiki 教程](learning/mopmonk-security-agent-wiki.md) |  | 2026-07-04 | - |

### learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md) | 系统讲解Agent通信四大协议：MCP（Anthropic 2024，工具层）、ACP（IBM/BeeAI 2025，本地Agent协作）、A2A（Google 2025，跨厂商Agent协作）、ANP（去中心化网络层）。包含协议分层架构、N×M集成问题分析、各协议技术规范对比、代码示例与快速参考。本文档已原子化，详细内容见 agent-communication-protocols/ 子目录。 | 2026-07-03 | agent-protocols、mcp、acp、a2a、anp、multi-agent、communication、open-standard、linux-foundation、interoperability |
| [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md) | 基于 agentskills.io 官方完整教程（快速入门/最佳实践/描述优化/质量评估/脚本使用/客户端实现）和 external/agentskills 源码深度核实的 Agent Skills 开放标准完整指南。覆盖目录结构、SKILL.md格式规范、渐进式披露机制、自包含脚本设计、触发准确率优化、评估驱动迭代、skills-ref验证工具使用、客户端5步集成指南，以及与本项目现有Skill体系的对比分析。本文档已原子化，详细内容见 agent-skills-wiki/ 子目录。 | 2026-07-02 | agent-skills、skills、open-standard、specification、ai-agent、skill-development、progressive-disclosure、skills-ref、client-implementation、skill-evals |
| [Claude Tag 文章知识捕获](learning/claude-tag-article.md) | 捕获量子位 2026-06-24 文章《刚刚，Claude Code大升级！卡帕西：LLM第三次变革》核心内容：Anthropic 发布企业协作工具 Claude Tag，定位为 Claude Code 进化，强调团队共享、主动介入（Ambient Mode）、异步执行，卡帕西称其为 LLM 用户界面第三次重大变革。本文档已原子化，详细内容见 claude-tag-article/ 子目录。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、ambient-mode、opus、karpathy、llm、协作、知识沉淀、复盘闭环、模式入库、已原子化 |
| [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md) | 系统对比 DeepSeek V4、Kimi K2.7 Code、MiniMax M3、GLM 5.2 四款国产 AI 模型，按不写代码-文案类、不写代码-多模态资料、写代码、高并发批量任务四类人群给出推荐方案，并深入剖析国产模型信任问题，提出'能力是入场券，信任才是留下来的理由'核心洞察。 | 2026-07-04 | llm、domestic-model、model-comparison、glm、kimi、deepseek、minimax、coding、multi-modal、trust、scenario-recommendation、ai-agent |
| [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md) | 基于 executablebooks.org 和 mystmd.org 官方文档系统整理的 MyST Markdown 学习资料库，涵盖生态概览、核心语法（Directives/Roles）、项目结构与myst.yml配置、Frontmatter元数据、TOC目录配置、使用示例、配置模板、最佳实践和参考资源。 | 2026-07-02 | myst、myst-markdown、markdown、executablebooks、jupyter-book、documentation、markup、scientific-writing、mystmd、commonmark、directives、roles |
| [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md) | 源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则（编码前先思考/简约至上/精确编辑/目标驱动），一个CLAUDE.md文件管住AI编程最常犯的毛病。GitHub 61.6k星项目完整教程，包含背景故事、核心原则详解、真实代码正反例、四种分发格式安装指南（CLAUDE.md/Cursor Rules/SKILL.md/插件）、Multica平台架构与multica-cli Skill使用指南、仓库文件结构说明，以及在SpecWeave项目中的整合情况。本文档已原子化，详细内容见 karpathy-llm-coding-guidelines/ 子目录。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude、ai-programming、agentic-engineering、claude-code、cursor、skills、plugin、mdc、multica、multica-cli、managed-agents |
| [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md) | TuyaOpen 是涂鸦开源的跨平台、跨芯片、跨操作系统的 AI-IoT SDK，核心目标是用一套灵活的 C/C++ SDK，结合涂鸦云的低延迟多模态 AI 能力，简化开放式 AI-IoT 生态的搭建。 | 2026-06-30 | tuya、tuyaopen、iot、sdk、ai、embedded、c、cpp、mcu、esp32、mcp、cloud、tkl、tal、tdd、tdl |
| [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md) | TuyaOpen-dev-skills 是面向 TuyaOpen 硬件开发流程的 AI Skills 仓库，以“最小 SKILL.md + references/ 按需加载 + scripts/ 可执行脚本”的三分结构，把环境搭建、编译、代码检查、烧录监控与调试闭环规范化。 | 2026-06-30 | tuya、tuyaopen、skills、agent-skills、cursor、claude、iot、embedded、workflow、ci |
| [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md) | 针对 external/TuyaOpen 工作区的可执行学习路线：先跑通 LINUX target 构建闭环，再进入硬件烧录与 AI 智能体硬件能力区。 | 2026-06-30 | tuyaopen、learning-path、iot、embedded、sdk、cli、tos |
| [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md) | 学习分析卡兹克《Vibe Coding 两大神级 Prompt》一文：第一性原理(管生成)与对抗式审查(管验证)构成完整闭环,是 Vibe Coding 的两大基石。 | 2026-07-04 | vibe-coding、prompt、第一性原理、对抗式审查、ai-agent、代码审查、multi-agent、aihot、可复用模式 |
| [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md) | 基于 external/WSL 源码（src/windows/wslc/ + doc/docs/）深度核实的 WSL CLI 命令树、参数定义、CLI 架构四层模型与官方架构 Mermaid 源图。修正先前学习计划中关于 CLI 命令短形态的误判——list/remove 才是主名，ls/ps/rm/delete 是别名。补充 interop binfmt 机制、systemd 启动流程、wslservice COM 接口、mini_init 多通道拓扑等技术细节。所有信息均有源码文件锚点可追溯。 | 2026-07-01 | wsl、wslc、cli、command-tree、argument-definitions、architecture、mermaid、interop、systemd、wslservice、com、binfmt、hvsocket、source-verification |
| [WSL 系统学习计划](learning/wsl-learning-plan.md) | 基于 external/WSL 源码 + wsl.dev 开发者文档 + learn.microsoft.com 官方文档制定的系统学习计划，涵盖 Windows/Linux 三层架构、Linux 侧核心进程（mini_init/init/plan9/gns/relay）、Plan9/DrvFs 文件系统互操作、WSLC Container API 三语言投影（C/C#/C++ WinRT）、CMake 跨编译构建、组策略与诊断调试，包含 5 个实操练习、官方端到端示例、完整错误码表与 4 周学习路径。 | 2026-07-01 | wsl、learning-path、linux、windows、container、wslc、plan9、drvfs、cmake、sdk、diagnostics、hvsocket、gns、systemd、winrt、nuget、com、error-codes |
| [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md) | 从AI Agent技术实现视角出发的Interface/API/ABI/Protocol四层抽象总览，聚焦MCP/ACP/A2A/ANP生态中的具体体现 | 2026-07-03 | agent、mcp、interface、api、abi、protocol、a2a |
| [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md) | Agent视角的Interface：能力契约，JSON Schema驱动的Tool/Skill/Agent声明模式 | 2026-07-03 | agent、interface、mcp、tool、json-schema、skill |
| [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md) | Agent视角的API：JSON-RPC 2.0作为Agent API标准，MCP/ACP/A2A的API设计与调用案例 | 2026-07-03 | agent、api、json-rpc、mcp、a2a、rest |
| [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md) | Agent视角的ABI：JSON+STDIO/HTTP如何绕过传统二进制兼容问题，实现跨语言Agent互操作 | 2026-07-03 | agent、abi、json、serialization、cross-language、stdio、http |
| [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md) | Agent视角的Protocol：MCP/ACP/A2A/ANP四层协议定位、消息流程、握手机制与协作模式 | 2026-07-03 | agent、protocol、mcp、a2a、acp、anp、json-rpc |
| [对比分析：Agent四层技术栈协同](learning/agent-interface-deep-dive/05-agent-comparison.md) | Agent语境下Interface/API/ABI/Protocol九维度系统对比、全链路调用图、FAQ与技术选型决策指南 | 2026-07-03 | agent、comparison、architecture、mcp、decision-guide |
| [参考资料与学习路径](learning/agent-interface-deep-dive/06-agent-resources.md) | Agent术语表、官方规范参考链接、三条进阶学习路径（Tool开发者/协议设计者/跨语言Runtime） | 2026-07-03 | agent、resources、reference、glossary、learning-path |
| [一、概述](learning/agent-skills-wiki/00-overview.md) |  | 2026-07-02 | agent-skills、overview、introduction |
| [二、核心机制：渐进式披露（Progressive Disclosure）](learning/agent-skills-wiki/01-progressive-disclosure.md) |  | 2026-07-02 | agent-skills、progressive-disclosure、architecture |
| [三、目录结构规范](learning/agent-skills-wiki/02-directory-structure.md) |  | 2026-07-02 | agent-skills、directory-structure、specification |
| [四、SKILL.md 格式规范](learning/agent-skills-wiki/03-skill-md-format.md) |  | 2026-07-02 | agent-skills、skill-md、frontmatter、specification |
| [快速入门：创建你的第一个 Skill](learning/agent-skills-wiki/04-quickstart.md) |  | 2026-07-01 | agent-skills、quickstart、roll-dice、tutorial |
| [[分析标题]](learning/agent-skills-wiki/05-best-practices.md) |  | 2026-07-01 | agent-skills、best-practices、context、instruction-patterns、gotchas |
| [/// script](learning/agent-skills-wiki/06-scripts-guide.md) |  | 2026-07-01 | agent-skills、scripts、pep723、self-contained、idempotency |
| [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/agent-skills-wiki/07-description-optimization.md) |  | 2026-07-01 | agent-skills、description、trigger、evals、optimization、train-validation-split |
| [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md) |  | 2026-07-01 | agent-skills、evals、testing、assertions、grading、benchmark、iteration |
| [验证一个技能目录](learning/agent-skills-wiki/09-skills-ref-tool.md) |  | 2026-07-01 | agent-skills、skills-ref、validation、tooling |
| [文件引用规范](learning/agent-skills-wiki/10-file-references.md) |  | 2026-07-01 | agent-skills、file-references、path、best-practices |
| [与本项目现有Skill体系的对比](learning/agent-skills-wiki/11-project-comparison.md) |  | 2026-07-01 | agent-skills、comparison、specweave、integration |
| [技术上无效的 YAML——冒号破坏了解析](learning/agent-skills-wiki/12-client-implementation.md) |  | 2026-07-01 | agent-skills、client-implementation、integration、developer-guide |
| [资源链接](learning/agent-skills-wiki/13-resources.md) |  | 2026-07-01 | agent-skills、resources、links、references |
| [My Skill](learning/agent-skills-wiki/14-quick-reference.md) |  | 2026-07-01 | agent-skills、quick-reference、cheatsheet、checklist |
| [AI变现完整指南：从技术到商业的全流程方法论](learning/ai-monetization-wiki/00-overview.md) | AI变现完整指南总览，涵盖8大核心模块、3类应用场景与13章阅读路径 | 2026-07-03 | ai-monetization、overview、commercialization、business、guide |
| [核心概念界定：AI变现术语体系](learning/ai-monetization-wiki/01-core-concepts.md) | AI变现核心术语界定，含标准定义、AI变现语境释义与示例 | 2026-07-03 | ai-monetization、concepts、terminology、pmf、ltv-cac、moat |
| [市场需求分析：识别与评估AI商业化机会](learning/ai-monetization-wiki/02-market-analysis.md) | AI商业化机会识别与评估方法，含市场调研、用户需求挖掘、竞争格局、规模估算与场景适配性评估 | 2026-07-03 | ai-monetization、market-analysis、tam-sam-som、porter-five-forces、user-research |
| [商业模式设计：AI产品的盈利模式选择](learning/ai-monetization-wiki/03-business-models.md) | AI产品9类盈利模式、价值主张设计、客户细分与商业模式选择决策树 | 2026-07-03 | ai-monetization、business-model、saas、pricing、canvas、freemium |
| [技术选型：AI技术栈决策框架](learning/ai-monetization-wiki/04-tech-selection.md) | AI技术栈决策框架，含算法选型、算力配置、数据策略、部署方式与成本估算 | 2026-07-03 | ai-monetization、tech-selection、algorithm、compute、data-strategy、deployment |
| [产品开发：AI产品的构建与迭代流程](learning/ai-monetization-wiki/05-product-development.md) | AI产品开发流程，含原型设计、敏捷迭代、测试验证、数据飞轮与效果度量 | 2026-07-03 | ai-monetization、product-development、mlops、poc、data-flywheel、evaluation |
| [市场推广：AI产品的GTM策略](learning/ai-monetization-wiki/06-marketing-strategy.md) | AI产品市场进入策略，含定位、渠道、传播、GTM节奏与冷启动 | 2026-07-03 | ai-monetization、gtm、marketing、positioning、cold-start、channel |
| [盈利策略：定价模型与规模化路径](learning/ai-monetization-wiki/07-profitability-strategy.md) | AI产品定价模型、收入结构设计与规模化盈利路径，含单位经济模型优化 | 2026-07-03 | ai-monetization、pricing、revenue-structure、scaling、unit-economics |
| [企业服务场景：ToB AI应用变现路径](learning/ai-monetization-wiki/08-scenario-enterprise.md) | ToB AI应用三类变现路径、成功案例剖析与行业挑战应对策略 | 2026-07-03 | ai-monetization、tob、enterprise、saas、customization、platform |
| [消费级产品场景：ToC AI应用变现路径](learning/ai-monetization-wiki/09-scenario-consumer.md) | ToC AI应用三类变现路径、成功案例剖析与留存获客挑战应对 | 2026-07-03 | ai-monetization、toc、consumer、freemium、subscription、retention |
| [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md) | 医疗/金融/制造/教育/零售五大垂直行业AI变现路径、案例与挑战应对 | 2026-07-03 | ai-monetization、industry、vertical、healthcare、finance、manufacturing、education、retail |
| [实施步骤与关键成功因素](learning/ai-monetization-wiki/11-implementation-steps.md) | AI变现六阶段实施路径与各阶段关键成功因素 | 2026-07-03 | ai-monetization、implementation、ksf、roadmap、stages |
| [风险提示与资源推荐](learning/ai-monetization-wiki/12-risks-resources.md) | AI变现五大风险类别规避策略与实用资源推荐、术语速查表 | 2026-07-03 | ai-monetization、risks、resources、compliance、glossary |
| [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md) | Claude Tag 文章元信息与概述：Anthropic 发布企业协作工具 Claude Tag，卡帕西称其为 LLM 用户界面第三次重大变革。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、karpathy、llm |
| [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md) | Claude Tag 五大核心观点：产品定位（Claude Code进化）、卡帕西LLM三次变革论断、与传统AI助手的根本差异、四大能力（共享上下文/持续记忆/主动介入/异步执行）、企业统一入口战略。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、ambient-mode、karpathy、llm、协作 |
| [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md) | Claude Tag 关键术语解释：Claude Tag、Ambient Mode（主动介入模式）、共享上下文、持续记忆、异步执行、Claude身份权限隔离、Opus 4.8、Fable 5。 | 2026-06-29 | claude、tag、anthropic、ambient-mode、opus、fable、术语 |
| [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md) | Claude Tag 重要数据汇总：Anthropic 65%产品代码参与、Opus 4.8唯一支持、率先登陆Slack、30天内取代现有应用、Beta开放对象、扩展计划、Token预算管理等。 | 2026-06-29 | claude、tag、anthropic、opus、slack、数据、统计 |
| [Claude Tag：原文结构框架](learning/claude-tag-article/04-article-structure.md) | 原文四节结构概括：升级概览、先进团队先用Claude、实际部署、社区反响。 | 2026-06-29 | claude、tag、anthropic、slack、fable、社区 |
| [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md) | Claude Tag 与 SpecWeave 的三点关联：多智能体协作参照（已萃取为team-shared-ai-colleague模式）、组织知识沉淀对照、Agent工作流呼应（已萃取为ambient-proactive-agent模式）。 | 2026-06-29 | claude、tag、specweave、多智能体、知识沉淀、阶段守卫、自我演进 |
| [Claude Tag：知识沉淀闭环](learning/claude-tag-article/06-knowledge-closure.md) | 本知识条目复盘闭环状态：复盘报告索引、已萃取可复用模式（2项L1）、方法论沉淀（2项操作指南）。 | 2026-07-03 | claude、tag、复盘、模式入库、方法论、闭环 |
| [Claude Tag：参考链接](learning/claude-tag-article/07-resources.md) | Claude Tag 相关参考链接汇总：原文、官方产品页、官方博客、媒体报道、复盘报告、已入库模式文件。 | 2026-06-29 | claude、tag、anthropic、参考资料、链接 |
| [ExecutableBooks 生态概览](learning/executablebooks-myst-guide/00-overview.md) |  | 2026-07-02 | myst、executablebooks、overview、jupyter-book、mystmd、ecosystem |
| [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md) |  | 2026-07-02 | myst、syntax、directives、roles、markdown、commonmark、admonitions |
| [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md) |  | 2026-07-02 | myst、mystmd、project、configuration、myst.yml、cli、build |
| [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md) |  | 2026-07-02 | myst、frontmatter、yaml、metadata、authors、bibliography、exports |
| [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md) |  | 2026-07-02 | myst、toc、table-of-contents、navigation、glob、slug、hidden-pages |
| [MyST Markdown 使用最佳实践](learning/executablebooks-myst-guide/05-best-practices.md) |  | 2026-07-02 | myst、best-practices、gotchas、pitfalls、commonmark、compatibility |
| [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md) |  | 2026-07-02 | myst、resources、references、links、documentation、glossary、community |
| [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md) |  | 2026-07-02 | myst、examples、admonitions、note、warning、tip、danger、callout |
| [MyST Markdown 基础语法示例](learning/executablebooks-myst-guide/examples/basic-syntax.md) |  | 2026-07-02 | myst、examples、syntax、admonitions、code-block、basic |
| [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md) |  | 2026-07-02 | myst、examples、cross-references、labels、ref、numref、links |
| [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/mcp-server-demo.md) |  | 2026-07-02 | myst、mcp、example、demo、github |
| [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md) |  | 2026-07-02 | myst、examples、roles、inline、abbr、subscript、superscript、math |
| [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/poc/github-tools.md) |  | 2026-07-02 | myst、mcp、example、poc、github |
| [Weather Service MCP Server](learning/executablebooks-myst-guide/examples/poc/weather-service.md) |  | 2026-07-02 | weather、mcp、example、myst、poc |
| [一、概念总览：软件接口的四层抽象](learning/interface-api-abi-protocol-wiki/00-overview.md) | Interface/API/ABI/Protocol四个核心技术概念的层次总览与阅读指引 | 2026-07-03 | interface、api、abi、protocol、architecture |
| [二、接口（Interface）：语言级行为抽象](learning/interface-api-abi-protocol-wiki/01-interface.md) | 接口（Interface）的标准定义、核心特征、多范式应用场景与代码案例 | 2026-07-03 | interface、oop、functional-programming、polymorphism、duck-typing |
| [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md) | API的精确定义、REST/GraphQL/SOAP/gRPC类型对比、核心特征、应用场景与主流案例 | 2026-07-03 | api、rest、graphql、soap、grpc、web-api、microservices |
| [四、ABI（应用二进制接口）：二进制兼容约定](learning/interface-api-abi-protocol-wiki/03-abi.md) | ABI的技术内涵、与API的本质区别、核心技术特征、底层系统应用场景与案例 | 2026-07-03 | abi、binary-compatibility、calling-convention、ffi、shared-library、syscall |
| [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md) | 协议的综合定义、网络/软件协议分类、核心特征、主流协议对比与应用场景 | 2026-07-03 | protocol、network、http、tcp、websocket、osi-model、tcp-ip |
| [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md) | Interface/API/ABI/Protocol四概念对比表格、关联关系分析、Mermaid架构层次图、常见混淆点澄清与决策指南 | 2026-07-03 | comparison、architecture、abstraction-layers、interface、api、abi、protocol |
| [七、参考资料与扩展阅读](learning/interface-api-abi-protocol-wiki/06-resources.md) | 术语表、权威参考资料、扩展阅读建议与进阶学习路径 | 2026-07-03 | resources、references、glossary、further-reading、books、rfc |
| [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md) | 源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则，用一个CLAUDE.md文件管住AI编程最常犯的毛病。本教程包含背景介绍、核心原则详解、真实代码正反例、安装使用指南，以及在SpecWeave项目中的整合情况。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude、ai-programming、agentic-engineering |
| [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md) | 四条核心原则的详细说明：编码前先思考、简约至上、精确编辑、目标驱动，包含每条原则的问题根源、具体要求和检验标准。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、principles、think-before-coding、simplicity、surgical-changes、goal-driven |
| [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md) | 真实世界代码示例演示四条原则，每个示例展示LLM常见错误做法和正确做法，涵盖隐藏假设、过度抽象、顺手重构、模糊目标等场景。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、examples、python、anti-patterns |
| [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md) | 快速上手安装和使用指南：三种分发格式对比（CLAUDE.md/SKILL.md/Cursor Rules）、Claude Code插件安装、Cursor编辑器集成详解、SKILL.md格式、项目定制方法、贡献者指南。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude-code、cursor、installation、quickstart、skills、plugin |
| [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md) | Karpathy LLM编程准则在SpecWeave项目中的整合情况：四条原则如何融入现有规范体系，对应的规范文件位置，以及团队使用方式。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、specweave、integration、rules |
| [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md) | 相关资源链接：三个官方仓库（karpathy-skills/multica/multica-cli）的文件结构、分发格式说明、Karpathy原帖、中文报道、Multica平台相关资源等参考资料。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、resources、references、repository-structure、multica、multica-cli |
| [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md) | Multica 是开源的 Managed Agents 平台，将编码 Agent 变成真正的队友——分配任务、跟踪进度、积累技能。本文档介绍 Multica 平台的核心概念、架构、功能模块，以及它与 Karpathy 准则的关系。 | 2026-07-02 | karpathy、llm、coding、agent、multica、platform、managed-agents、agentic-engineering、runtime、daemon、skill、autopilot、squad |
| [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md) | multica-cli 是一个可移植 Skill，教任意本地编码 Agent（Claude Code、Codex、Cursor 等）通过已认证的 multica CLI 安全操作 Multica 平台。本文档按「背景→核心安全原则→命令正反例→快速上手→工作流实战→生态设计理念」六层认知阶梯组织，帮助读者从理解为什么需要到掌握最佳实践。 | 2026-07-02 | karpathy、llm、coding、agent、multica、cli、skill、claude-code、cursor、codex、safety、external-agent |

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。 | 2026-06-30 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
| [HTML 正文提取操作指南](operations/html-body-extraction.md) | HTML 正文提取双方案：正则提取（首选）与边界标记索引截取法（兜底），含 HTML 清洗六步流程，适用于复杂嵌套 HTML 容器 | 2026-06-29 | html、正文提取、正则、索引截取、边界标记、html清洗、降级策略 |
| [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md) | 一条可落地执行、可观测验收的 Tuya IPC（网络摄像机）端-云-手机最小闭环跑通路径：先明确最小假设，再按步骤给出依赖/验收/排查，并附依赖关系图与闭环验收总表。 | 2026-06-30 | tuya、ipc、iot、闭环、配网、音视频、设备绑定、事件上报、联调、排查、验收 |
| [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md) | 当需要在 SpecWeave 中新增或使用 flexloop 相关功能时，基于三区域边界模型和四不原则的5种合规集成路径决策指南 | 2026-06-29 | vendor、flexloop、agentforge、submodule、集成方案、三区域模型、四不原则 |
| [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md) | 微信公众号文章内容提取双路径决策模型：defuddle CLI 与 PowerShell Invoke-WebRequest 互为兜底，含边界标记索引截取法作为正则失败时的兜底方案 | 2026-06-29 | 微信公众号、内容提取、defuddle、powershell、invoke-webrequest、html提取、反爬、降级策略 |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |
| [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md) | 记录 Windows PowerShell 下将 Python 中文 stdout 通过文本管道写入文件时可能发生的转码污染，以及推荐的安全写回方案 | 2026-06-30 | windows、powershell、encoding、utf-8、pipe、set-content、python、docs |
| [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md) | 系统性解决Windows终端中文乱码问题的完整指南，涵盖系统级/用户级/项目级三层配置方案 | 2026-07-01 | windows、powershell、cmd、utf-8、encoding、gbk、chcp、乱码 |

### research

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [MDI (Markdown Interface) 深度研究报告](mdi-research-report.md) |  | 2026-07-02 | - |

### standards

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [MDI Spec v1.0：Markdown即接口规范](mdi-spec-v1.0.md) |  | 2026-07-02 | - |

### troubleshooting

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md) | 记录 AI 智能体因未读取 AGENTS.md 启动协议而导致输出格式、文件路径、文档结构三项错误的完整故障链与修复方案 | 2026-06-24 | agents、protocol、startup、output-format、path、skill-conflict |
| [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md) | 记录 PowerShell Move-Item 重命名目录时 Access Denied 错误的排查与解决方案 | 2026-06-23 | windows、powershell、rename、directory、access-denied |
| [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md) | 记录在 submodule 目录内创建主项目文件导致 submodule 永久 dirty 的故障原因与解决方案，以及 submodule 元数据外置的最佳实践 | 2026-06-29 | git、submodule、vendor、dirty、modified-content |

### unknown

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [stage-guardrails-guide](stage-guardrails-guide.md) |  |  | - |
| [three-layer-routing](three-layer-routing.md) |  |  | - |
| [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md) |  |  | - |
| [dspark-paper-wiki](learning/dspark-paper-wiki.md) |  |  | - |
| [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md) |  |  | - |
| [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md) |  | 2026-07-04 | text-to-cad、cad、ai-agent、build123d、step、urdf、3d-printing、robotics |
| [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md) |  | 2026-07-04 | the-agency、ai-agent、agent-framework、multi-agent、claude-code、cursor |
| [00、概述与背景](learning/agent-communication-protocols/00-overview.md) |  |  | - |
| [01、MCP协议详解：Model Context Protocol](learning/agent-communication-protocols/01-mcp.md) |  |  | - |
| [02、ACP协议详解：Agent Communication Protocol](learning/agent-communication-protocols/02-acp.md) |  |  | - |
| [03、A2A协议详解：Agent-to-Agent Protocol](learning/agent-communication-protocols/03-a2a.md) |  |  | - |
| [04、ANP协议概述：Agent Network Protocol](learning/agent-communication-protocols/04-anp.md) |  |  | - |
| [05、协议对比与分层架构](learning/agent-communication-protocols/05-comparison.md) |  |  | - |
| [06、交互流程与协作模式](learning/agent-communication-protocols/06-flows.md) |  |  | - |
| [07、技术实现要点与代码示例](learning/agent-communication-protocols/07-implementation.md) |  |  | - |
| [08、典型应用场景](learning/agent-communication-protocols/08-scenarios.md) |  |  | - |
| [09、术语表](learning/agent-communication-protocols/09-glossary.md) |  |  | - |
| [10、资源与参考链接](learning/agent-communication-protocols/10-resources.md) |  |  | - |
| [11、快速参考速查表](learning/agent-communication-protocols/11-quick-reference.md) |  |  | - |
| [第0章：快速上手（Quick Start）](learning/myst-markdown-tutorial/00-quick-start.md) |  |  | - |
| [第1章：MyST 简介与 CommonMark 对比](learning/myst-markdown-tutorial/01-introduction.md) |  |  | - |
| [第2章：基础语法（上）- 文本与格式](learning/myst-markdown-tutorial/02-basic-syntax-part1.md) |  |  | - |
| [第3章：基础语法（下）- 列表、链接与图片](learning/myst-markdown-tutorial/03-basic-syntax-part2.md) |  |  | - |
| [第4章：高级功能 - Directives 和 Roles](learning/myst-markdown-tutorial/04-advanced-directives-roles.md) |  |  | - |
| [第5章：高级功能 - 交叉引用](learning/myst-markdown-tutorial/05-advanced-cross-references.md) |  |  | - |
| [第6章：高级功能 - 数学公式与代码块](learning/myst-markdown-tutorial/06-advanced-math-code.md) |  |  | - |
| [第7章：高级功能 - 注释、脚注与参考文献](learning/myst-markdown-tutorial/07-advanced-notes-citations.md) |  |  | - |
| [第8章：扩展组件 - 提示框（Admonitions）](learning/myst-markdown-tutorial/08-components-admonitions.md) |  |  | - |
| [第9章：扩展组件 - 卡片、下拉与标签页](learning/myst-markdown-tutorial/09-components-ui.md) |  |  | - |
| [第10章：扩展组件 - 图片与表格](learning/myst-markdown-tutorial/10-components-figures.md) |  |  | - |
| [第11章：工具链集成 - Sphinx + myst-parser](learning/myst-markdown-tutorial/11-tooling-sphinx.md) |  |  | - |
| [第12章：工具链集成 - Jupyter Book v1](learning/myst-markdown-tutorial/12-tooling-jupyter-book.md) |  |  | - |
| [第13章：工具链集成 - mystmd（新一代）](learning/myst-markdown-tutorial/13-tooling-mystmd.md) |  |  | - |
| [第14章：实战案例 - 技术文档写作](learning/myst-markdown-tutorial/14-case-study-tech-docs.md) |  |  | - |
| [第15章：实战案例 - 学术论文与书籍](learning/myst-markdown-tutorial/15-case-study-academic.md) |  |  | - |
| [第16章：常见问题解答（FAQ）](learning/myst-markdown-tutorial/16-faq.md) |  |  | - |
| [附录A：MyST Markdown 速查表](learning/myst-markdown-tutorial/appendix/cheat-sheet.md) |  |  | - |
| [附录B：资源推荐](learning/myst-markdown-tutorial/appendix/resources.md) |  |  | - |
| [示例：Admonitions 提示框样式大全](learning/myst-markdown-tutorial/examples/admonitions-demo.md) |  |  | - |
| [示例：图片与表格](learning/myst-markdown-tutorial/examples/figures-tables-demo.md) |  |  | - |
| [模板：学术论文模板](learning/myst-markdown-tutorial/examples/paper-template.md) |  |  | - |
| [模板：技术文档模板](learning/myst-markdown-tutorial/examples/tech-doc-template.md) |  |  | - |
| [示例：卡片、下拉与标签页](learning/myst-markdown-tutorial/examples/ui-components-demo.md) |  |  | - |
| [discourse-api-research](operations/discourse-api-research.md) |  |  | - |

## 标签索引

### 3d-printing

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)

### a2a

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)
- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md)
- [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md)
- [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md)

### abbr

- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)

### abi

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md)
- [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md)
- [一、概念总览：软件接口的四层抽象](learning/interface-api-abi-protocol-wiki/00-overview.md)
- [四、ABI（应用二进制接口）：二进制兼容约定](learning/interface-api-abi-protocol-wiki/03-abi.md)
- [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md)

### abstraction-layers

- [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md)

### access-denied

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### acp

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)
- [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md)

### admonitions

- [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md)
- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)
- [MyST Markdown 基础语法示例](learning/executablebooks-myst-guide/examples/basic-syntax.md)

### agent

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md)
- [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md)
- [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md)
- [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md)
- [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md)
- [对比分析：Agent四层技术栈协同](learning/agent-interface-deep-dive/05-agent-comparison.md)
- [参考资料与学习路径](learning/agent-interface-deep-dive/06-agent-resources.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### agent-framework

- [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md)

### agent-protocols

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)

### agent-skills

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [一、概述](learning/agent-skills-wiki/00-overview.md)
- [二、核心机制：渐进式披露（Progressive Disclosure）](learning/agent-skills-wiki/01-progressive-disclosure.md)
- [三、目录结构规范](learning/agent-skills-wiki/02-directory-structure.md)
- [四、SKILL.md 格式规范](learning/agent-skills-wiki/03-skill-md-format.md)
- [快速入门：创建你的第一个 Skill](learning/agent-skills-wiki/04-quickstart.md)
- [[分析标题]](learning/agent-skills-wiki/05-best-practices.md)
- [/// script](learning/agent-skills-wiki/06-scripts-guide.md)
- [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/agent-skills-wiki/07-description-optimization.md)
- [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md)
- [验证一个技能目录](learning/agent-skills-wiki/09-skills-ref-tool.md)
- [文件引用规范](learning/agent-skills-wiki/10-file-references.md)
- [与本项目现有Skill体系的对比](learning/agent-skills-wiki/11-project-comparison.md)
- [技术上无效的 YAML——冒号破坏了解析](learning/agent-skills-wiki/12-client-implementation.md)
- [资源链接](learning/agent-skills-wiki/13-resources.md)
- [My Skill](learning/agent-skills-wiki/14-quick-reference.md)

### agentforge

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### agentic-engineering

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)

### agents

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### ai

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### ai-agent

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)
- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)
- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)
- [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md)
- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### ai-monetization

- [AI变现完整指南：从技术到商业的全流程方法论](learning/ai-monetization-wiki/00-overview.md)
- [核心概念界定：AI变现术语体系](learning/ai-monetization-wiki/01-core-concepts.md)
- [市场需求分析：识别与评估AI商业化机会](learning/ai-monetization-wiki/02-market-analysis.md)
- [商业模式设计：AI产品的盈利模式选择](learning/ai-monetization-wiki/03-business-models.md)
- [技术选型：AI技术栈决策框架](learning/ai-monetization-wiki/04-tech-selection.md)
- [产品开发：AI产品的构建与迭代流程](learning/ai-monetization-wiki/05-product-development.md)
- [市场推广：AI产品的GTM策略](learning/ai-monetization-wiki/06-marketing-strategy.md)
- [盈利策略：定价模型与规模化路径](learning/ai-monetization-wiki/07-profitability-strategy.md)
- [企业服务场景：ToB AI应用变现路径](learning/ai-monetization-wiki/08-scenario-enterprise.md)
- [消费级产品场景：ToC AI应用变现路径](learning/ai-monetization-wiki/09-scenario-consumer.md)
- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)
- [实施步骤与关键成功因素](learning/ai-monetization-wiki/11-implementation-steps.md)
- [风险提示与资源推荐](learning/ai-monetization-wiki/12-risks-resources.md)

### ai-programming

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)

### aihot

- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### algorithm

- [技术选型：AI技术栈决策框架](learning/ai-monetization-wiki/04-tech-selection.md)

### ambient-mode

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md)

### anp

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)
- [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md)

### anthropic

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/claude-tag-article/04-article-structure.md)
- [Claude Tag：参考链接](learning/claude-tag-article/07-resources.md)

### anti-patterns

- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)

### api

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md)
- [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md)
- [一、概念总览：软件接口的四层抽象](learning/interface-api-abi-protocol-wiki/00-overview.md)
- [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md)
- [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md)

### architecture

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)
- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [对比分析：Agent四层技术栈协同](learning/agent-interface-deep-dive/05-agent-comparison.md)
- [二、核心机制：渐进式披露（Progressive Disclosure）](learning/agent-skills-wiki/01-progressive-disclosure.md)
- [一、概念总览：软件接口的四层抽象](learning/interface-api-abi-protocol-wiki/00-overview.md)
- [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md)

### argument-definitions

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### assertions

- [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md)

### authors

- [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md)

### autopilot

- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)

### basic

- [MyST Markdown 基础语法示例](learning/executablebooks-myst-guide/examples/basic-syntax.md)

### benchmark

- [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md)

### best-practices

- [[分析标题]](learning/agent-skills-wiki/05-best-practices.md)
- [文件引用规范](learning/agent-skills-wiki/10-file-references.md)
- [MyST Markdown 使用最佳实践](learning/executablebooks-myst-guide/05-best-practices.md)

### bibliography

- [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md)

### binary-compatibility

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/interface-api-abi-protocol-wiki/03-abi.md)

### binfmt

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### books

- [七、参考资料与扩展阅读](learning/interface-api-abi-protocol-wiki/06-resources.md)

### browser

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### build

- [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md)

### build123d

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)

### business

- [AI变现完整指南：从技术到商业的全流程方法论](learning/ai-monetization-wiki/00-overview.md)

### business-model

- [商业模式设计：AI产品的盈利模式选择](learning/ai-monetization-wiki/03-business-models.md)

### c

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### cad

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)

### calling-convention

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/interface-api-abi-protocol-wiki/03-abi.md)

### callout

- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)

### canvas

- [商业模式设计：AI产品的盈利模式选择](learning/ai-monetization-wiki/03-business-models.md)

### channel

- [市场推广：AI产品的GTM策略](learning/ai-monetization-wiki/06-marketing-strategy.md)

### chcp

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### cheatsheet

- [My Skill](learning/agent-skills-wiki/14-quick-reference.md)

### check-mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### checklist

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)
- [My Skill](learning/agent-skills-wiki/14-quick-reference.md)

### ci

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### claude

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/claude-tag-article/04-article-structure.md)
- [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md)
- [Claude Tag：知识沉淀闭环](learning/claude-tag-article/06-knowledge-closure.md)
- [Claude Tag：参考链接](learning/claude-tag-article/07-resources.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)

### claude-code

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### cli

- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### client-implementation

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)
- [技术上无效的 YAML——冒号破坏了解析](learning/agent-skills-wiki/12-client-implementation.md)

### cloud

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### cmake

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### cmd

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### code-block

- [MyST Markdown 基础语法示例](learning/executablebooks-myst-guide/examples/basic-syntax.md)

### codex

- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### coding

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)
- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### cold-start

- [市场推广：AI产品的GTM策略](learning/ai-monetization-wiki/06-marketing-strategy.md)

### com

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### command-tree

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### commercialization

- [AI变现完整指南：从技术到商业的全流程方法论](learning/ai-monetization-wiki/00-overview.md)

### commonmark

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md)
- [MyST Markdown 使用最佳实践](learning/executablebooks-myst-guide/05-best-practices.md)

### communication

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)

### community

- [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md)

### comparison

- [对比分析：Agent四层技术栈协同](learning/agent-interface-deep-dive/05-agent-comparison.md)
- [与本项目现有Skill体系的对比](learning/agent-skills-wiki/11-project-comparison.md)
- [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md)

### compatibility

- [MyST Markdown 使用最佳实践](learning/executablebooks-myst-guide/05-best-practices.md)

### compliance

- [风险提示与资源推荐](learning/ai-monetization-wiki/12-risks-resources.md)

### compute

- [技术选型：AI技术栈决策框架](learning/ai-monetization-wiki/04-tech-selection.md)

### concepts

- [核心概念界定：AI变现术语体系](learning/ai-monetization-wiki/01-core-concepts.md)

### configuration

- [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md)

### consumer

- [消费级产品场景：ToC AI应用变现路径](learning/ai-monetization-wiki/09-scenario-consumer.md)

### container

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### context

- [[分析标题]](learning/agent-skills-wiki/05-best-practices.md)

### convention

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### cpp

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### cross-language

- [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md)

### cross-references

- [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md)

### cursor

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### customization

- [企业服务场景：ToB AI应用变现路径](learning/ai-monetization-wiki/08-scenario-enterprise.md)

### daemon

- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)

### danger

- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)

### data-flywheel

- [产品开发：AI产品的构建与迭代流程](learning/ai-monetization-wiki/05-product-development.md)

### data-strategy

- [技术选型：AI技术栈决策框架](learning/ai-monetization-wiki/04-tech-selection.md)

### decision-guide

- [对比分析：Agent四层技术栈协同](learning/agent-interface-deep-dive/05-agent-comparison.md)

### deepseek

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### defuddle

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### demo

- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/mcp-server-demo.md)

### deployment

- [技术选型：AI技术栈决策框架](learning/ai-monetization-wiki/04-tech-selection.md)

### description

- [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/agent-skills-wiki/07-description-optimization.md)

### developer-guide

- [技术上无效的 YAML——冒号破坏了解析](learning/agent-skills-wiki/12-client-implementation.md)

### diagnostics

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### directives

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md)

### directory

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### directory-structure

- [三、目录结构规范](learning/agent-skills-wiki/02-directory-structure.md)

### dirty

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### discourse

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### docs

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### documentation

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md)

### domestic-model

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### drvfs

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### duck-typing

- [二、接口（Interface）：语言级行为抽象](learning/interface-api-abi-protocol-wiki/01-interface.md)

### ecosystem

- [ExecutableBooks 生态概览](learning/executablebooks-myst-guide/00-overview.md)

### education

- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)

### embedded

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)

### encoding

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### enterprise

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [企业服务场景：ToB AI应用变现路径](learning/ai-monetization-wiki/08-scenario-enterprise.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)

### error-codes

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### esp32

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### evals

- [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/agent-skills-wiki/07-description-optimization.md)
- [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md)

### evaluation

- [产品开发：AI产品的构建与迭代流程](learning/ai-monetization-wiki/05-product-development.md)

### example

- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/mcp-server-demo.md)
- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/poc/github-tools.md)
- [Weather Service MCP Server](learning/executablebooks-myst-guide/examples/poc/weather-service.md)

### examples

- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)
- [MyST Markdown 基础语法示例](learning/executablebooks-myst-guide/examples/basic-syntax.md)
- [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md)
- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)
- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)

### executablebooks

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [ExecutableBooks 生态概览](learning/executablebooks-myst-guide/00-overview.md)

### exports

- [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md)

### external-agent

- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### fable

- [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md)
- [Claude Tag：原文结构框架](learning/claude-tag-article/04-article-structure.md)

### ffi

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/interface-api-abi-protocol-wiki/03-abi.md)

### file-references

- [文件引用规范](learning/agent-skills-wiki/10-file-references.md)

### finance

- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)

### flexloop

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### four-layer-model

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### freemium

- [商业模式设计：AI产品的盈利模式选择](learning/ai-monetization-wiki/03-business-models.md)
- [消费级产品场景：ToC AI应用变现路径](learning/ai-monetization-wiki/09-scenario-consumer.md)

### frontmatter

- [四、SKILL.md 格式规范](learning/agent-skills-wiki/03-skill-md-format.md)
- [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md)

### functional-programming

- [二、接口（Interface）：语言级行为抽象](learning/interface-api-abi-protocol-wiki/01-interface.md)

### further-reading

- [七、参考资料与扩展阅读](learning/interface-api-abi-protocol-wiki/06-resources.md)

### gbk

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### git

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### github

- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/mcp-server-demo.md)
- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/poc/github-tools.md)

### glm

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### glob

- [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md)

### glossary

- [参考资料与学习路径](learning/agent-interface-deep-dive/06-agent-resources.md)
- [风险提示与资源推荐](learning/ai-monetization-wiki/12-risks-resources.md)
- [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md)
- [七、参考资料与扩展阅读](learning/interface-api-abi-protocol-wiki/06-resources.md)

### gns

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### goal-driven

- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)

### gotchas

- [[分析标题]](learning/agent-skills-wiki/05-best-practices.md)
- [MyST Markdown 使用最佳实践](learning/executablebooks-myst-guide/05-best-practices.md)

### governance

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### governance-loop

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### grading

- [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md)

### graphql

- [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md)

### grpc

- [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md)

### gtm

- [市场推广：AI产品的GTM策略](learning/ai-monetization-wiki/06-marketing-strategy.md)

### guide

- [AI变现完整指南：从技术到商业的全流程方法论](learning/ai-monetization-wiki/00-overview.md)

### guidelines

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)

### healthcare

- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)

### heredoc

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### hidden-pages

- [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md)

### html

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### html提取

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### html清洗

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### http

- [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md)
- [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md)

### hvsocket

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### idempotency

- [/// script](learning/agent-skills-wiki/06-scripts-guide.md)

### implementation

- [实施步骤与关键成功因素](learning/ai-monetization-wiki/11-implementation-steps.md)

### industry

- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)

### inline

- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)

### installation

- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)

### instruction-patterns

- [[分析标题]](learning/agent-skills-wiki/05-best-practices.md)

### integration

- [与本项目现有Skill体系的对比](learning/agent-skills-wiki/11-project-comparison.md)
- [技术上无效的 YAML——冒号破坏了解析](learning/agent-skills-wiki/12-client-implementation.md)
- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)

### interface

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md)
- [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md)
- [一、概念总览：软件接口的四层抽象](learning/interface-api-abi-protocol-wiki/00-overview.md)
- [二、接口（Interface）：语言级行为抽象](learning/interface-api-abi-protocol-wiki/01-interface.md)
- [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md)

### interop

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### interoperability

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)

### introduction

- [一、概述](learning/agent-skills-wiki/00-overview.md)

### invoke-webrequest

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### iot

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### ipc

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### iteration

- [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md)

### json

- [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md)

### json-rpc

- [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md)
- [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md)

### json-schema

- [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md)

### jupyter-book

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [ExecutableBooks 生态概览](learning/executablebooks-myst-guide/00-overview.md)

### karpathy

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### kimi

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### ksf

- [实施步骤与关键成功因素](learning/ai-monetization-wiki/11-implementation-steps.md)

### labels

- [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md)

### learning-path

- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)
- [参考资料与学习路径](learning/agent-interface-deep-dive/06-agent-resources.md)

### links

- [资源链接](learning/agent-skills-wiki/13-resources.md)
- [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md)
- [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md)

### linux

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### linux-foundation

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)

### llm

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)
- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)
- [Karpathy LLM 编程准则：概述与背景](learning/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### ltv-cac

- [核心概念界定：AI变现术语体系](learning/ai-monetization-wiki/01-core-concepts.md)

### managed-agents

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)

### manufacturing

- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)

### markdown

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md)

### market-analysis

- [市场需求分析：识别与评估AI商业化机会](learning/ai-monetization-wiki/02-market-analysis.md)

### marketing

- [市场推广：AI产品的GTM策略](learning/ai-monetization-wiki/06-marketing-strategy.md)

### markup

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)

### math

- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)

### mcp

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)
- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md)
- [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md)
- [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md)
- [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md)
- [对比分析：Agent四层技术栈协同](learning/agent-interface-deep-dive/05-agent-comparison.md)
- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/mcp-server-demo.md)
- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/poc/github-tools.md)
- [Weather Service MCP Server](learning/executablebooks-myst-guide/examples/poc/weather-service.md)
- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### mcu

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### mdc

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)

### mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### meta-insights

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### metadata

- [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md)

### methodology

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### microservices

- [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md)

### minimax

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### mlops

- [产品开发：AI产品的构建与迭代流程](learning/ai-monetization-wiki/05-product-development.md)

### moat

- [核心概念界定：AI变现术语体系](learning/ai-monetization-wiki/01-core-concepts.md)

### model-comparison

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### modified-content

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### multi-agent

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)
- [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md)
- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### multi-modal

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### multica

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### multica-cli

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)

### myst

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [ExecutableBooks 生态概览](learning/executablebooks-myst-guide/00-overview.md)
- [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md)
- [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md)
- [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md)
- [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md)
- [MyST Markdown 使用最佳实践](learning/executablebooks-myst-guide/05-best-practices.md)
- [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md)
- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)
- [MyST Markdown 基础语法示例](learning/executablebooks-myst-guide/examples/basic-syntax.md)
- [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md)
- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/mcp-server-demo.md)
- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)
- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/poc/github-tools.md)
- [Weather Service MCP Server](learning/executablebooks-myst-guide/examples/poc/weather-service.md)

### myst-markdown

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)

### myst.yml

- [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md)

### mystmd

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [ExecutableBooks 生态概览](learning/executablebooks-myst-guide/00-overview.md)
- [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md)

### naming

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### navigation

- [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md)

### network

- [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md)

### note

- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)

### nuget

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### numref

- [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md)

### oop

- [二、接口（Interface）：语言级行为抽象](learning/interface-api-abi-protocol-wiki/01-interface.md)

### open-standard

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md)
- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)

### optimization

- [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/agent-skills-wiki/07-description-optimization.md)

### opus

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md)

### osi-model

- [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md)

### output-format

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### overview

- [一、概述](learning/agent-skills-wiki/00-overview.md)
- [AI变现完整指南：从技术到商业的全流程方法论](learning/ai-monetization-wiki/00-overview.md)
- [ExecutableBooks 生态概览](learning/executablebooks-myst-guide/00-overview.md)

### parser

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### path

- [文件引用规范](learning/agent-skills-wiki/10-file-references.md)
- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### patterns

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### pep723

- [/// script](learning/agent-skills-wiki/06-scripts-guide.md)

### pipe

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### pitfalls

- [MyST Markdown 使用最佳实践](learning/executablebooks-myst-guide/05-best-practices.md)

### plan9

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### platform

- [企业服务场景：ToB AI应用变现路径](learning/ai-monetization-wiki/08-scenario-enterprise.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)

### playwright

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### plugin

- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)

### pmf

- [核心概念界定：AI变现术语体系](learning/ai-monetization-wiki/01-core-concepts.md)

### poc

- [产品开发：AI产品的构建与迭代流程](learning/ai-monetization-wiki/05-product-development.md)
- [GitHub Tools MCP Server](learning/executablebooks-myst-guide/examples/poc/github-tools.md)
- [Weather Service MCP Server](learning/executablebooks-myst-guide/examples/poc/weather-service.md)

### polymorphism

- [二、接口（Interface）：语言级行为抽象](learning/interface-api-abi-protocol-wiki/01-interface.md)

### porter-five-forces

- [市场需求分析：识别与评估AI商业化机会](learning/ai-monetization-wiki/02-market-analysis.md)

### positioning

- [市场推广：AI产品的GTM策略](learning/ai-monetization-wiki/06-marketing-strategy.md)

### powershell

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)
- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### pricing

- [商业模式设计：AI产品的盈利模式选择](learning/ai-monetization-wiki/03-business-models.md)
- [盈利策略：定价模型与规模化路径](learning/ai-monetization-wiki/07-profitability-strategy.md)

### principles

- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)

### product-development

- [产品开发：AI产品的构建与迭代流程](learning/ai-monetization-wiki/05-product-development.md)

### progressive-disclosure

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)
- [二、核心机制：渐进式披露（Progressive Disclosure）](learning/agent-skills-wiki/01-progressive-disclosure.md)

### project

- [MyST 项目结构与 myst.yml 配置](learning/executablebooks-myst-guide/02-project-structure.md)

### prompt

- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### protocol

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md)
- [Agent Protocol：通信规则层](learning/agent-interface-deep-dive/04-agent-protocol.md)
- [一、概念总览：软件接口的四层抽象](learning/interface-api-abi-protocol-wiki/00-overview.md)
- [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md)
- [六、对比分析：四概念系统辨析](learning/interface-api-abi-protocol-wiki/05-comparison.md)
- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### python

- [真实代码正反例](learning/karpathy-llm-coding-guidelines/02-code-examples.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### quick-reference

- [My Skill](learning/agent-skills-wiki/14-quick-reference.md)

### quickstart

- [快速入门：创建你的第一个 Skill](learning/agent-skills-wiki/04-quickstart.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)

### ref

- [交叉引用示例](learning/executablebooks-myst-guide/examples/cross-references.md)

### reference

- [参考资料与学习路径](learning/agent-interface-deep-dive/06-agent-resources.md)

### references

- [资源链接](learning/agent-skills-wiki/13-resources.md)
- [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md)
- [七、参考资料与扩展阅读](learning/interface-api-abi-protocol-wiki/06-resources.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)

### rename

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### repository-structure

- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)

### resources

- [参考资料与学习路径](learning/agent-interface-deep-dive/06-agent-resources.md)
- [资源链接](learning/agent-skills-wiki/13-resources.md)
- [风险提示与资源推荐](learning/ai-monetization-wiki/12-risks-resources.md)
- [参考资源与链接汇总](learning/executablebooks-myst-guide/06-resources.md)
- [七、参考资料与扩展阅读](learning/interface-api-abi-protocol-wiki/06-resources.md)
- [资源与参考链接](learning/karpathy-llm-coding-guidelines/05-resources.md)

### rest

- [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md)
- [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md)

### retail

- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)

### retention

- [消费级产品场景：ToC AI应用变现路径](learning/ai-monetization-wiki/09-scenario-consumer.md)

### retrospective

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### revenue-structure

- [盈利策略：定价模型与规模化路径](learning/ai-monetization-wiki/07-profitability-strategy.md)

### rfc

- [七、参考资料与扩展阅读](learning/interface-api-abi-protocol-wiki/06-resources.md)

### risks

- [风险提示与资源推荐](learning/ai-monetization-wiki/12-risks-resources.md)

### roadmap

- [实施步骤与关键成功因素](learning/ai-monetization-wiki/11-implementation-steps.md)

### robotics

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)

### roles

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)
- [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md)
- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)

### roll-dice

- [快速入门：创建你的第一个 Skill](learning/agent-skills-wiki/04-quickstart.md)

### rules

- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)

### runtime

- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)

### saas

- [商业模式设计：AI产品的盈利模式选择](learning/ai-monetization-wiki/03-business-models.md)
- [企业服务场景：ToB AI应用变现路径](learning/ai-monetization-wiki/08-scenario-enterprise.md)

### safety

- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### scaling

- [盈利策略：定价模型与规模化路径](learning/ai-monetization-wiki/07-profitability-strategy.md)

### scenario-recommendation

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### scientific-writing

- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/executablebooks-myst-guide-wiki.md)

### scripts

- [/// script](learning/agent-skills-wiki/06-scripts-guide.md)

### sdk

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### self-contained

- [/// script](learning/agent-skills-wiki/06-scripts-guide.md)

### semi-structured-parsing

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### serialization

- [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md)

### set-content

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### shared-library

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/interface-api-abi-protocol-wiki/03-abi.md)

### shell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### simplicity

- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)

### skill

- [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md)
- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### skill-conflict

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### skill-development

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)

### skill-evals

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)

### skill-md

- [四、SKILL.md 格式规范](learning/agent-skills-wiki/03-skill-md-format.md)

### skills

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)
- [Karpathy LLM 编程准则完整教程](learning/karpathy-llm-coding-guidelines-tutorial.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [快速上手指南](learning/karpathy-llm-coding-guidelines/03-quickstart.md)

### skills-ref

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)
- [验证一个技能目录](learning/agent-skills-wiki/09-skills-ref-tool.md)

### slack

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/claude-tag-article/04-article-structure.md)

### slug

- [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md)

### soap

- [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md)

### source-verification

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### specification

- [Agent Skills 开放标准完整指南](learning/agent-skills-open-standard-wiki.md)
- [三、目录结构规范](learning/agent-skills-wiki/02-directory-structure.md)
- [四、SKILL.md 格式规范](learning/agent-skills-wiki/03-skill-md-format.md)

### specweave

- [与本项目现有Skill体系的对比](learning/agent-skills-wiki/11-project-comparison.md)
- [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md)
- [SpecWeave 项目整合情况](learning/karpathy-llm-coding-guidelines/04-specweave-integration.md)

### squad

- [Multica 平台：AI Agent 协作管理平台](learning/karpathy-llm-coding-guidelines/06-multica-platform.md)

### stage-guardrails

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### stages

- [实施步骤与关键成功因素](learning/ai-monetization-wiki/11-implementation-steps.md)

### startup

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### stdio

- [Agent ABI：跨语言边界层](learning/agent-interface-deep-dive/03-agent-abi.md)

### step

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)

### submodule

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### subscript

- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)

### subscription

- [消费级产品场景：ToC AI应用变现路径](learning/ai-monetization-wiki/09-scenario-consumer.md)

### superscript

- [MyST Roles（行内扩展）示例](learning/executablebooks-myst-guide/examples/roles-demo.md)

### surgical-changes

- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)

### syntax

- [MyST Markdown 核心语法](learning/executablebooks-myst-guide/01-myst-syntax.md)
- [MyST Markdown 基础语法示例](learning/executablebooks-myst-guide/examples/basic-syntax.md)

### syscall

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/interface-api-abi-protocol-wiki/03-abi.md)

### systemd

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### table-of-contents

- [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md)

### tag

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：文章概述](learning/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/claude-tag-article/04-article-structure.md)
- [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md)
- [Claude Tag：知识沉淀闭环](learning/claude-tag-article/06-knowledge-closure.md)
- [Claude Tag：参考链接](learning/claude-tag-article/07-resources.md)

### tal

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tam-sam-som

- [市场需求分析：识别与评估AI商业化机会](learning/ai-monetization-wiki/02-market-analysis.md)

### tcp

- [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md)

### tcp-ip

- [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md)

### TDD

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### tdd

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tdl

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tech-selection

- [技术选型：AI技术栈决策框架](learning/ai-monetization-wiki/04-tech-selection.md)

### terminology

- [核心概念界定：AI变现术语体系](learning/ai-monetization-wiki/01-core-concepts.md)

### testing

- [质量评估（Evals）](learning/agent-skills-wiki/08-evals.md)

### text-to-cad

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)

### the-agency

- [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md)

### think-before-coding

- [四条核心原则详解](learning/karpathy-llm-coding-guidelines/01-four-principles.md)

### tip

- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)

### tkl

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tob

- [企业服务场景：ToB AI应用变现路径](learning/ai-monetization-wiki/08-scenario-enterprise.md)

### toc

- [消费级产品场景：ToC AI应用变现路径](learning/ai-monetization-wiki/09-scenario-consumer.md)
- [目录结构（TOC）配置指南](learning/executablebooks-myst-guide/04-table-of-contents.md)

### tool

- [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md)

### tooling

- [验证一个技能目录](learning/agent-skills-wiki/09-skills-ref-tool.md)

### tos

- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)

### train-validation-split

- [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/agent-skills-wiki/07-description-optimization.md)

### trigger

- [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/agent-skills-wiki/07-description-optimization.md)

### trust

- [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md)

### tutorial

- [快速入门：创建你的第一个 Skill](learning/agent-skills-wiki/04-quickstart.md)

### tuya

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### tuyaopen

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)

### unit-economics

- [盈利策略：定价模型与规模化路径](learning/ai-monetization-wiki/07-profitability-strategy.md)

### urdf

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md)

### user-research

- [市场需求分析：识别与评估AI商业化机会](learning/ai-monetization-wiki/02-market-analysis.md)

### utf-8

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### validation

- [验证一个技能目录](learning/agent-skills-wiki/09-skills-ref-tool.md)

### vendor

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### vertical

- [行业解决方案场景：垂直行业AI变现路径](learning/ai-monetization-wiki/10-scenario-industry.md)

### vibe-coding

- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### warning

- [Admonitions（提示框）样式大全](learning/executablebooks-myst-guide/examples/admonitions.md)

### weather

- [Weather Service MCP Server](learning/executablebooks-myst-guide/examples/poc/weather-service.md)

### web-api

- [三、API（应用编程接口）：源码与服务级契约](learning/interface-api-abi-protocol-wiki/02-api.md)

### websocket

- [五、协议（Protocol）：通信规则约定](learning/interface-api-abi-protocol-wiki/04-protocol.md)

### windows

- [WSL 系统学习计划](learning/wsl-learning-plan.md)
- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### winrt

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### workflow

- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### wsl

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### wslc

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### wslservice

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### yaml

- [Frontmatter 配置详解](learning/executablebooks-myst-guide/03-frontmatter-config.md)

### 三区域模型

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 三层架构

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### 乱码

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### 事件上报

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 代码审查

- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### 六规则

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 内容提取

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 协作

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：核心观点](learning/claude-tag-article/01-core-insights.md)

### 参考资料

- [Claude Tag：参考链接](learning/claude-tag-article/07-resources.md)

### 反爬

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 发布

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 可复用模式

- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### 可视化

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 四不原则

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 图表

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 复杂度预算

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### 复盘

- [Claude Tag：知识沉淀闭环](learning/claude-tag-article/06-knowledge-closure.md)

### 复盘闭环

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### 多智能体

- [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md)

### 安全编码

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 对抗式审查

- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### 已原子化

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### 微信公众号

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 排查

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 数据

- [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md)

### 方法论

- [Claude Tag：知识沉淀闭环](learning/claude-tag-article/06-knowledge-closure.md)

### 未分类

- [MDI (Markdown Interface) 深度研究报告](mdi-research-report.md)
- [MDI Spec v1.0：Markdown即接口规范](mdi-spec-v1.0.md)
- [stage-guardrails-guide](stage-guardrails-guide.md)
- [three-layer-routing](three-layer-routing.md)
- [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md)
- [dspark-paper-wiki](learning/dspark-paper-wiki.md)
- [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md)
- [MopMonk 安全 Agent Wiki 教程](learning/mopmonk-security-agent-wiki.md)
- [00、概述与背景](learning/agent-communication-protocols/00-overview.md)
- [01、MCP协议详解：Model Context Protocol](learning/agent-communication-protocols/01-mcp.md)
- [02、ACP协议详解：Agent Communication Protocol](learning/agent-communication-protocols/02-acp.md)
- [03、A2A协议详解：Agent-to-Agent Protocol](learning/agent-communication-protocols/03-a2a.md)
- [04、ANP协议概述：Agent Network Protocol](learning/agent-communication-protocols/04-anp.md)
- [05、协议对比与分层架构](learning/agent-communication-protocols/05-comparison.md)
- [06、交互流程与协作模式](learning/agent-communication-protocols/06-flows.md)
- [07、技术实现要点与代码示例](learning/agent-communication-protocols/07-implementation.md)
- [08、典型应用场景](learning/agent-communication-protocols/08-scenarios.md)
- [09、术语表](learning/agent-communication-protocols/09-glossary.md)
- [10、资源与参考链接](learning/agent-communication-protocols/10-resources.md)
- [11、快速参考速查表](learning/agent-communication-protocols/11-quick-reference.md)
- [第0章：快速上手（Quick Start）](learning/myst-markdown-tutorial/00-quick-start.md)
- [第1章：MyST 简介与 CommonMark 对比](learning/myst-markdown-tutorial/01-introduction.md)
- [第2章：基础语法（上）- 文本与格式](learning/myst-markdown-tutorial/02-basic-syntax-part1.md)
- [第3章：基础语法（下）- 列表、链接与图片](learning/myst-markdown-tutorial/03-basic-syntax-part2.md)
- [第4章：高级功能 - Directives 和 Roles](learning/myst-markdown-tutorial/04-advanced-directives-roles.md)
- [第5章：高级功能 - 交叉引用](learning/myst-markdown-tutorial/05-advanced-cross-references.md)
- [第6章：高级功能 - 数学公式与代码块](learning/myst-markdown-tutorial/06-advanced-math-code.md)
- [第7章：高级功能 - 注释、脚注与参考文献](learning/myst-markdown-tutorial/07-advanced-notes-citations.md)
- [第8章：扩展组件 - 提示框（Admonitions）](learning/myst-markdown-tutorial/08-components-admonitions.md)
- [第9章：扩展组件 - 卡片、下拉与标签页](learning/myst-markdown-tutorial/09-components-ui.md)
- [第10章：扩展组件 - 图片与表格](learning/myst-markdown-tutorial/10-components-figures.md)
- [第11章：工具链集成 - Sphinx + myst-parser](learning/myst-markdown-tutorial/11-tooling-sphinx.md)
- [第12章：工具链集成 - Jupyter Book v1](learning/myst-markdown-tutorial/12-tooling-jupyter-book.md)
- [第13章：工具链集成 - mystmd（新一代）](learning/myst-markdown-tutorial/13-tooling-mystmd.md)
- [第14章：实战案例 - 技术文档写作](learning/myst-markdown-tutorial/14-case-study-tech-docs.md)
- [第15章：实战案例 - 学术论文与书籍](learning/myst-markdown-tutorial/15-case-study-academic.md)
- [第16章：常见问题解答（FAQ）](learning/myst-markdown-tutorial/16-faq.md)
- [附录A：MyST Markdown 速查表](learning/myst-markdown-tutorial/appendix/cheat-sheet.md)
- [附录B：资源推荐](learning/myst-markdown-tutorial/appendix/resources.md)
- [示例：Admonitions 提示框样式大全](learning/myst-markdown-tutorial/examples/admonitions-demo.md)
- [示例：图片与表格](learning/myst-markdown-tutorial/examples/figures-tables-demo.md)
- [模板：学术论文模板](learning/myst-markdown-tutorial/examples/paper-template.md)
- [模板：技术文档模板](learning/myst-markdown-tutorial/examples/tech-doc-template.md)
- [示例：卡片、下拉与标签页](learning/myst-markdown-tutorial/examples/ui-components-demo.md)
- [MDI研究报告 - 执行摘要](mdi-research/00-executive-summary.md)
- [MDI研究报告 - 可行性分析](mdi-research/01-feasibility-analysis.md)
- [MDI研究报告 - 生态对比分析](mdi-research/02-ecosystem-comparison.md)
- [MDI研究报告 - 技术架构深度解析](mdi-research/03-technical-architecture.md)
- [MDI研究报告 - 工具链使用指南](mdi-research/04-toolchain-guide.md)
- [MDI研究报告 - 版本控制与变更管理最佳实践](mdi-research/05-versioning-best-practices.md)
- [MDI研究报告 - 未来演进方向](mdi-research/06-future-evolution.md)
- [MDI研究报告 - 结论](mdi-research/07-conclusion.md)
- [discourse-api-research](operations/discourse-api-research.md)

### 术语

- [Claude Tag：关键概念与术语](learning/claude-tag-article/02-key-concepts.md)

### 模式入库

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：知识沉淀闭环](learning/claude-tag-article/06-knowledge-closure.md)

### 模板

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 正则

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 正文提取

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 知识沉淀

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md)

### 社区

- [Claude Tag：原文结构框架](learning/claude-tag-article/04-article-structure.md)

### 第一性原理

- [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md)

### 索引截取

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 统计

- [Claude Tag：重要数据](learning/claude-tag-article/03-key-data.md)

### 联调

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 自动化

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 自我演进

- [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md)

### 论坛

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 设备绑定

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 边界case

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### 边界标记

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 配网

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 链接

- [Claude Tag：参考链接](learning/claude-tag-article/07-resources.md)

### 闭环

- [Claude Tag：知识沉淀闭环](learning/claude-tag-article/06-knowledge-closure.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 阶段守卫

- [Claude Tag：与 SpecWeave 的关联](learning/claude-tag-article/05-specweave-relevance.md)

### 降级策略

- [HTML 正文提取操作指南](operations/html-body-extraction.md)
- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 集成方案

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 音视频

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 验收

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [国产AI模型对比与使用场景推荐](learning/domestic-llm-comparison-notes.md) | 2026-07-04 | learning |
| [MopMonk 安全 Agent Wiki 教程](learning/mopmonk-security-agent-wiki.md) | 2026-07-04 | knowledge/learning |
| [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/text-to-cad-wiki.md) | 2026-07-04 | unknown |
| [The Agency 项目完整学习教程](learning/the-agency-project-wiki.md) | 2026-07-04 | unknown |
| [Vibe Coding 两大神级 Prompt](learning/vibe-coding-prompts-learning-analysis.md) | 2026-07-04 | learning |
| [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md) | 2026-07-03 | best-practices |
| [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/agent-communication-protocols-wiki.md) | 2026-07-03 | learning |
| [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/agent-interface-deep-dive/00-overview.md) | 2026-07-03 | learning |
| [Agent Interface：能力契约层](learning/agent-interface-deep-dive/01-agent-interface.md) | 2026-07-03 | learning |
| [Agent API：可调用方法层](learning/agent-interface-deep-dive/02-agent-api.md) | 2026-07-03 | learning |

## 相关资源

### 回溯报告

- [项目硬编码问题系统性复盘报告](../retrospective/hardcode-retrospective-report.md)
- [提示词工程 — 可迁移模式、模板与方法论萃取](../retrospective/prompt-extraction.md)
- [复盘文档体系](../retrospective/README.md)

### 任务总结

- [任务执行总结报告](../task-summaries/task-summary-git-local-clone-bug-20260701.md)
- [任务执行总结报告](../task-summaries/task-summary-readme-creation-20260623.md)

## 使用指南

### 如何添加知识条目

1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`platform/` 等）
2. 复制 `template.md` 作为模板，创建新的 `.md` 文件
3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）
4. 在正文中按照模板结构编写内容
5. 运行 `python scripts/generate_index.py` 重新生成索引

### 如何检索

- **按类别浏览**：使用上方的「按类别浏览」章节，按操作、平台、排错等分类查找
- **按标签检索**：使用上方的「标签索引」章节，按关键词标签快速定位
- **按时间排序**：查看「最近更新」章节，了解最新添加的知识条目
- **全文搜索**：在项目根目录使用 `grep -r "关键词" docs/knowledge/` 进行全文搜索

### 如何维护

- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息
- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）
- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目
- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成索引

---

*索引自动生成于 2026-07-04 09:54:15*
