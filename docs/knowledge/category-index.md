# 分类总索引

- [返回知识库首页](README.md)
- [按标签检索](tags/README.md)

## 统计摘要

- **总条目数**：679

| 分类 | 数量 |
|------|------|
| architecture | 1 |
| best-practices | 12 |
| decisions | 1 |
| docs | 8 |
| knowledge | 40 |
| knowledge/best-practices | 1 |
| knowledge/learning | 5 |
| knowledge/learning/01-agent-protocols-interfaces | 2 |
| knowledge/learning/01-agent-protocols-interfaces/agent-communication-protocols | 12 |
| knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki | 15 |
| knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki | 16 |
| knowledge/learning/02-agent-engineering-methodology | 2 |
| knowledge/learning/02-agent-engineering-methodology/headroom-context-compression-wiki | 11 |
| knowledge/learning/02-agent-engineering-methodology/longcat-agent-learning-wiki | 9 |
| knowledge/learning/03-agent-platforms-tools | 11 |
| knowledge/learning/03-agent-platforms-tools/fable5-cost-optimization-wiki | 9 |
| knowledge/learning/03-agent-platforms-tools/mopmonk-security-agent-wiki | 7 |
| knowledge/learning/03-agent-platforms-tools/open-code-review-wiki | 11 |
| knowledge/learning/03-agent-platforms-tools/rainman-translate-book-wiki | 8 |
| knowledge/learning/04-docs-markup-tooling | 2 |
| knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide | 7 |
| knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/examples | 5 |
| knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc | 2 |
| knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial | 17 |
| knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix | 2 |
| knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/examples | 5 |
| knowledge/learning/05-ai-multimodal-content | 4 |
| knowledge/learning/06-business-trends-analysis | 10 |
| knowledge/learning/07-vendor-product-learning | 2 |
| knowledge/learning/07-vendor-product-learning/comparison | 2 |
| knowledge/learning/07-vendor-product-learning/openai/chatgpt-codex-wiki | 16 |
| knowledge/learning/07-vendor-product-learning/oray | 1 |
| knowledge/learning/07-vendor-product-learning/oray/retrospective-oray-comprehensive-analysis-20260706 | 3 |
| knowledge/learning/07-vendor-product-learning/sunlogin | 13 |
| knowledge/learning/07-vendor-product-learning/sunlogin/retrospective-sunlogin-wiki-mobile-control-update-20260706 | 3 |
| knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis | 10 |
| knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki | 11 |
| knowledge/learning/07-vendor-product-learning/volcengine | 11 |
| knowledge/learning/first-principles | 16 |
| knowledge/learning/first-principles/15-cross-domain-cases | 4 |
| knowledge/learning/first-principles/exercises | 10 |
| knowledge/learning/okr-wiki | 1 |
| knowledge/learning/okr-wiki/appendix | 1 |
| knowledge/learning/okr-wiki/concepts | 6 |
| knowledge/learning/okr-wiki/implementation | 6 |
| knowledge/learning/okr-wiki/methods | 4 |
| knowledge/learning/okr-wiki/scoring | 4 |
| knowledge/learning/okr-wiki/templates | 7 |
| knowledge/learning/okr-wiki/tools | 2 |
| learning | 211 |
| operations | 11 |
| reference | 3 |
| research | 1 |
| standards | 1 |
| troubleshooting | 4 |
| unknown | 80 |

## 按类别浏览

### architecture

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | SpecWeave项目治理方法论体系的架构总览文档，定义了治理基建四层递进核心模型，以及围绕该模型形成的5个可复用元洞察模式，包含模式间关系、落地状态和自反性验证案例。 | 2026-06-30 | governance、architecture、methodology、stage-guardrails、patterns、four-layer-model、governance-loop、retrospective、meta-insights |

### best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [AI拟人化互动服务极端情绪干预机制技术实施方案](best-practices/ai-anthropomorphic-crisis-intervention-implementation.md) | 针对《人工智能拟人化互动服务管理暂行办法》第13条要求，设计极端情绪/自残自杀干预机制的完整技术实施方案，包含系统架构、识别引擎、分级干预、运营后台、测试验收和7天上线排期 | 2026-07-08 | AI合规、极端情绪干预、安全机制、拟人化互动、技术方案 |
| [Python AST静态分析实践：五类消歧法降低误报](best-practices/ast-static-analysis-disambiguation.md) | 基于并发安全检查器（六维检查法）开发实战，总结Python AST静态分析中降低误报的五类消歧策略，帮助开发者编写准确的代码检查工具。核心原则：宁可漏报，不可误报。 | 2026-07-08 | AST、static-analysis、python、false-positive、code-quality、automation |
| [IDE Agent 环境下 CLI 工具配置操作手册](best-practices/cli-setup-in-agent-environment.md) | 针对团队新人的 IDE Agent（Trae/Claude Code 等）环境下 CLI 工具配置操作手册：基于 arkcli 安装配置实战，提炼通用方法论——安装验证→沙箱权限预判→非交互式认证→配置验证四步法，涵盖常见坑点、排错 Checklist 和决策矩阵。 | 2026-07-07 | cli、setup、agent-environment、sandbox、sso、non-interactive、arkcli、newbie-guide、npm |
| [并发代码安全审查与Bug修复闭环指南](best-practices/concurrent-code-safety-review.md) | 基于多智能体冲突解决机制实现与死锁修复实战复盘，提炼并发模块安全审查六维检查法、调度类模块N-scaling测试矩阵、Bug修复1+N+1闭环公式等5个可复用洞察，提供原子提交前的完整Checklist模板。 | 2026-07-08 | concurrency、deadlock-prevention、code-review、defensive-programming、bug-fix、checklist、tdd |
| [并发安全八维检查法技术规格](best-practices/eight-dimensions-concurrent-safety-spec.md) |  | 2026-07-08 | concurrent-safety、AST、static-analysis、eight-dimensions、check-rules、pre-commit |
| [文件 I/O 并发安全规范：原子写入、日志模板与重试策略](best-practices/file-io-concurrency-safety.md) | 基于原子写入重构实战（11个模块统一改造、46个测试覆盖、并发成功率82%→100%），提炼文件I/O并发安全三原则：写共享文件必须原子化、日志必须分阶段计时、重试必须有限次+退避。提供决策树、日志模板、重试参数规范和完整代码示例，作为所有涉及文件写入的脚本必须遵守的开发规范。 | 2026-07-12 | concurrency、file-io、atomic-write、logging、retry-pattern、windows、defensive-programming |
| [链式pre-commit钩子架构实践指南](best-practices/git-hook-chain-architecture.md) | 基于敏感信息检测和并发安全检查两个pre-commit钩子的实战经验，总结链式pre-commit钩子架构模式——单Shell入口+Python链式主入口+独立检查模块，解决跨平台维护、检查顺序控制和扩展成本问题。 | 2026-07-08 | git-hooks、pre-commit、architecture、cross-platform、automation |
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | SpecWeave 项目中 Mermaid 图表的一站式操作手册，涵盖起步模板、安全编码六规则、自动化检查工具详解、渲染问题排查流程和不同图表类型注意事项。 | 2026-06-29 | mermaid、图表、可视化、check-mermaid、安全编码、六规则、模板、ci |
| [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md) | 基于IDL Wiki章节拆分实战复盘的多文件编辑操作可靠性指南：涵盖章节拆分级联编号成本、Edit工具精确匹配陷阱、串行vs并行Edit策略、Windows管道稳定性四条核心经验，提供决策矩阵和操作Checklist。 | 2026-07-05 | edit、multi-file、reliability、serial-vs-parallel、windows-pipe、cascading-renumber、wiki-split、tool-pitfalls |
| [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md) | 基于MDI项目parser.py（1465行）重构复盘的经验总结：处理半结构化数据（Markdown/自然语言/配置文件）的Parser应预留2-3倍于Generator的时间/代码量预算，遵循三层架构拆分，并先写20+边界case测试。 | 2026-07-03 | parser、复杂度预算、semi-structured-parsing、三层架构、边界case、TDD、checklist |
| [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md) | 分类处置决策树(Classification-Disposition Decision Tree)与三阶段渐进推广验证(Phased Rollout Validation)两个L2治理模式的第3次验证报告。验证场景为复盘模板v1.2批量标准化升级（61个项目），验证了模式在轻量级模板升级场景下的有效性，记录了P1批量执行后集中格式校验的新增实践。 | 2026-07-06 | pattern-validation、L2-pattern、phased-rollout、classification-disposition、batch-upgrade、governance、methodology-evolution |
| [从实战到工具：三段式PDF导出、Mermaid全量扫描与三个工程洞察](best-practices/pdf-export-mermaid-automation-insights.md) | 从一次Mermaid漏斗图重绘与PDF导出任务中萃取的工程经验：三段式中文Markdown+Mermaid PDF导出法、Mermaid全量扫描自动化、以及三个核心工程洞察（工具选择熟悉度偏差、无头浏览器DOM检测原则、自动化检查的免费质量提升）。 | 2026-07-11 | pdf导出、mermaid、playwright、pandoc、自动化、工程洞察、工具封装、质量保证 |

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

### knowledge

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [反爬策略预设清单](anti-crawler-strategy-playbook.md) |  | 2026-07-02 | anti-crawler、web-scraping、fallback-strategy |
| [00、概述与背景](learning/02-agent-engineering-methodology/adversarial-review-wiki/00-overview.md) |  | 2026-07-10 | - |
| [01、核心概念定义](learning/02-agent-engineering-methodology/adversarial-review-wiki/01-core-concepts.md) |  | 2026-07-10 | - |
| [02、思想源头追溯](learning/02-agent-engineering-methodology/adversarial-review-wiki/02-philosophy-origins.md) |  | 2026-07-10 | - |
| [03、方法论框架](learning/02-agent-engineering-methodology/adversarial-review-wiki/03-methodology-framework.md) |  | 2026-07-10 | - |
| [04、认知偏差防御](learning/02-agent-engineering-methodology/adversarial-review-wiki/04-cognitive-biases-defense.md) |  | 2026-07-10 | - |
| [05、检查清单与工具模板](learning/02-agent-engineering-methodology/adversarial-review-wiki/05-checklists-templates.md) |  | 2026-07-10 | - |
| [06、行业标准与合规要求](learning/02-agent-engineering-methodology/adversarial-review-wiki/06-industry-standards.md) |  | 2026-07-10 | - |
| [07、开源工具链指南](learning/02-agent-engineering-methodology/adversarial-review-wiki/07-open-source-tools.md) |  | 2026-07-10 | - |
| [08、实战案例集](learning/02-agent-engineering-methodology/adversarial-review-wiki/08-practice-cases.md) |  | 2026-07-10 | - |
| [09、学术资源与推荐阅读](learning/02-agent-engineering-methodology/adversarial-review-wiki/09-academic-resources.md) |  | 2026-07-10 | - |
| [10、来源验证档案（自举验证）](learning/02-agent-engineering-methodology/adversarial-review-wiki/10-source-validation-log.md) |  | 2026-07-10 | - |
| [11、核心术语表](learning/02-agent-engineering-methodology/adversarial-review-wiki/11-glossary.md) |  | 2026-07-10 | - |
| [12、延伸阅读与资源索引](learning/02-agent-engineering-methodology/adversarial-review-wiki/12-resources.md) |  | 2026-07-10 | - |
| [13、快速参考速查表](learning/02-agent-engineering-methodology/adversarial-review-wiki/13-quick-reference.md) |  | 2026-07-10 | - |
| [00、概述与背景](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/00-overview.md) |  | 2026-07-13 | - |
| [01、GPT-5.6范式变革：从规定过程到明确目标](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/01-paradigm-shift.md) |  | 2026-07-13 | - |
| [02、七概念方法论与Prompt Engineering映射](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/02-seven-concepts-mapping.md) |  | 2026-07-13 | - |
| [03、GCOB四要素框架：Goal-Context-Output-Boundaries](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/03-gcob-framework.md) |  | 2026-07-13 | - |
| [04、新范式核心规则：做减法而非做加法](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/04-new-paradigm-rules.md) |  | 2026-07-13 | - |
| [05、6组Before/After实战对照](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/05-before-after-examples.md) |  | 2026-07-13 | - |
| [06、Chat场景实战指南](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/06-chat-scenarios.md) |  | 2026-07-13 | - |
| [07、Work场景实战指南](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/07-work-scenarios.md) |  | 2026-07-13 | - |
| [08、Codex/Agent开发基础：安全原则与标准结构](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/08-codex-scenarios.md) |  | 2026-07-14 | - |
| [08b、Codex/Agent开发实战：8个场景模板](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/08b-codex-examples.md) |  | 2026-07-14 | - |
| [09、检查清单与可复用模板库](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/09-checklists-templates.md) |  | 2026-07-13 | - |
| [10、反模式：20+个Prompt写法陷阱](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/10-anti-patterns.md) |  | 2026-07-13 | - |
| [00、总览：MyST Markdown 统一化接口生态体系](myst-unified-ecosystem/00-overview.md) |  | 2026-07-02 | - |
| [01、IDL：接口描述语言](myst-unified-ecosystem/01-idl.md) |  | 2026-07-02 | - |
| [02、Interface：行为契约](myst-unified-ecosystem/02-interface.md) |  | 2026-07-02 | - |
| [03、API：应用程序编程接口](myst-unified-ecosystem/03-api.md) |  | 2026-07-02 | - |
| [04、ABI：应用程序二进制接口](myst-unified-ecosystem/04-abi.md) |  | 2026-07-02 | - |
| [05、Protocol：通信协议](myst-unified-ecosystem/05-protocol.md) |  | 2026-07-02 | - |
| [06、Implementation：具体实现](myst-unified-ecosystem/06-implementation.md) |  | 2026-07-02 | - |
| [07、MCP：Model Context Protocol](myst-unified-ecosystem/07-mcp.md) |  | 2026-07-02 | - |
| [08、ACP：Agent Communication Protocol](myst-unified-ecosystem/08-acp.md) |  | 2026-07-02 | - |
| [09、A2A：Agent-to-Agent](myst-unified-ecosystem/09-a2a.md) |  | 2026-07-02 | - |
| [10、ANP：Agent Network Protocol](myst-unified-ecosystem/10-anp.md) |  | 2026-07-02 | - |
| [11、MDI：Markdown Document Interface](myst-unified-ecosystem/11-mdi.md) |  | 2026-07-02 | - |
| [12、关系全景：11个概念的形式化关系与交互](myst-unified-ecosystem/12-relationships.md) |  | 2026-07-02 | - |

### knowledge/best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [B2B/旗舰产品信息源分层采集规范](best-practices/b2b-product-info-collection-sop.md) |  | 2026-07-04 | 信息采集、B2B产品、SOP、多源验证、Defuddle |

### knowledge/learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [AtomGit AI 平台最佳实践](learning/atomgit-ai-best-practices.md) |  | 2026-07-02 | AtomGit、AI开发平台、MLOps、模型管理、数据集管理、Space应用、Notebook开发、协作开发、安全最佳实践、性能监控 |
| [抖音人气赛道创作指南深度分析——基于第一性原理的vibecoding内容传播方法论](learning/douyin-vibecoding-guide-analysis.md) |  | 2026-07-02 | vibecoding、抖音、内容创作、第一性原理、TRAE大赛、短视频传播 |
| [华秋智联与星宸科技战略合作深度分析：打通芯片量产最后一公里](learning/huaqiu-sigmastar-partnership-analysis-20260709.md) |  | 2026-07-09 | 端边侧AI、芯片生态、硬件量产、开发者生态、华秋、星宸科技 |
| [OKR制定指南Wiki手册](learning/okr-guide.md) |  | 2026-07-08 | - |
| [向日葵三个服务页面系统性学习与深度洞察分析报告](learning/sunlogin-service-pages-analysis.md) |  | 2026-07-06 | 向日葵、Sunlogin、屏幕墙、CLI、MCP、AweSun、远程控制、AI Agent、命令行、产品分析、服务页面分析 |

### knowledge/learning/01-agent-protocols-interfaces

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md) |  | 2026-07-04 | agent-runtime、agent-protocol、langgraph、openai-assistants、autogen、claude-sdk、mcp、thread、run、checkpoint、artifact、event、human-in-the-loop、error-recovery、multi-agent、observability |
| [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md) |  | 2026-07-04 | skill、mcp、cli、ai-agent、ecosystem、domestic、wechat、feishu、dingtalk、payment |

### knowledge/learning/01-agent-protocols-interfaces/agent-communication-protocols

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [00、概述与背景](learning/01-agent-protocols-interfaces/agent-communication-protocols/00-overview.md) |  | 2026-07-02 | - |
| [01、MCP协议详解：Model Context Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/01-mcp.md) |  | 2026-07-02 | - |
| [02、ACP协议详解：Agent Communication Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/02-acp.md) |  | 2026-07-02 | - |
| [03、A2A协议详解：Agent-to-Agent Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/03-a2a.md) |  | 2026-07-02 | - |
| [04、ANP协议概述：Agent Network Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/04-anp.md) |  | 2026-07-02 | - |
| [05、协议对比与分层架构](learning/01-agent-protocols-interfaces/agent-communication-protocols/05-comparison.md) |  | 2026-07-02 | - |
| [06、交互流程与协作模式](learning/01-agent-protocols-interfaces/agent-communication-protocols/06-flows.md) |  | 2026-07-02 | - |
| [07、技术实现要点与代码示例](learning/01-agent-protocols-interfaces/agent-communication-protocols/07-implementation.md) |  | 2026-07-02 | - |
| [08、典型应用场景](learning/01-agent-protocols-interfaces/agent-communication-protocols/08-scenarios.md) |  | 2026-07-02 | - |
| [09、术语表](learning/01-agent-protocols-interfaces/agent-communication-protocols/09-glossary.md) |  | 2026-07-02 | - |
| [10、资源与参考链接](learning/01-agent-protocols-interfaces/agent-communication-protocols/10-resources.md) |  | 2026-07-02 | - |
| [11、快速参考速查表](learning/01-agent-protocols-interfaces/agent-communication-protocols/11-quick-reference.md) |  | 2026-07-02 | - |

### knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [一、概述](learning/01-agent-protocols-interfaces/agent-skills-wiki/00-overview.md) |  | 2026-07-02 | - |
| [二、核心机制：渐进式披露（Progressive Disclosure）](learning/01-agent-protocols-interfaces/agent-skills-wiki/01-progressive-disclosure.md) |  | 2026-07-02 | - |
| [三、目录结构规范](learning/01-agent-protocols-interfaces/agent-skills-wiki/02-directory-structure.md) |  | 2026-07-02 | - |
| [四、SKILL.md 格式规范](learning/01-agent-protocols-interfaces/agent-skills-wiki/03-skill-md-format.md) |  | 2026-07-02 | - |
| [04-quickstart](learning/01-agent-protocols-interfaces/agent-skills-wiki/04-quickstart.md) |  | 2026-07-02 | - |
| [[分析标题]](learning/01-agent-protocols-interfaces/agent-skills-wiki/05-best-practices.md) |  | 2026-07-02 | - |
| [/// script](learning/01-agent-protocols-interfaces/agent-skills-wiki/06-scripts-guide.md) |  | 2026-07-02 | - |
| [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/01-agent-protocols-interfaces/agent-skills-wiki/07-description-optimization.md) |  | 2026-07-02 | - |
| [08-evals](learning/01-agent-protocols-interfaces/agent-skills-wiki/08-evals.md) |  | 2026-07-02 | - |
| [验证一个技能目录](learning/01-agent-protocols-interfaces/agent-skills-wiki/09-skills-ref-tool.md) |  | 2026-07-02 | - |
| [10-file-references](learning/01-agent-protocols-interfaces/agent-skills-wiki/10-file-references.md) |  | 2026-07-02 | - |
| [11-project-comparison](learning/01-agent-protocols-interfaces/agent-skills-wiki/11-project-comparison.md) |  | 2026-07-02 | - |
| [技术上无效的 YAML——冒号破坏了解析](learning/01-agent-protocols-interfaces/agent-skills-wiki/12-client-implementation.md) |  | 2026-07-02 | - |
| [13-resources](learning/01-agent-protocols-interfaces/agent-skills-wiki/13-resources.md) |  | 2026-07-02 | - |
| [My Skill](learning/01-agent-protocols-interfaces/agent-skills-wiki/14-quick-reference.md) |  | 2026-07-02 | - |

### knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md) |  | 2026-07-05 | tvm-ffi、ffi、cross-language、cpp、python、rust |
| [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md) |  | 2026-07-05 | tvm-ffi、ffi、cross-language、cpp、python、rust |
| [02 - C++ 核心 API：Any、Object、Function、Tensor](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/02-cpp-core-api.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [03 - 类型系统：DType、Enum、Optional、String](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/03-type-system.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [05 - 反射与注册机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [06 - 序列化：JSON、Base64、结构相等与哈希](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/06-serialization.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |

### knowledge/learning/02-agent-engineering-methodology

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md) |  | 2026-07-04 | prompt-engineering、context-engineering、harness-engineering、loop-engineering、ai-agent、bottleneck-shift、methodology |
| [别再逼Agent一次做对了](learning/02-agent-engineering-methodology/harness-loop-engineering-article-analysis.md) |  | 2026-07-09 | - |

### knowledge/learning/02-agent-engineering-methodology/headroom-context-compression-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Headroom：概述与学习目标](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/00-overview.md) |  | 2026-07-02 | - |
| [核心架构与设计理念](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/01-core-architecture.md) |  | 2026-07-02 | - |
| [六种压缩算法详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/02-compression-algorithms.md) |  | 2026-07-02 | - |
| [CCR可逆机制深度解析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/03-ccr-mechanism.md) |  | 2026-07-02 | - |
| [四种接入方式详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/04-integration-methods.md) |  | 2026-07-02 | - |
| [效果验证与数据分析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/05-performance-data.md) |  | 2026-07-02 | - |
| [跨Agent记忆与自动学习](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/06-advanced-features.md) |  | 2026-07-02 | - |
| [快速上手指南](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/07-quick-start.md) |  | 2026-07-02 | - |
| [深度洞察与模式萃取](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/08-insights-patterns.md) |  | 2026-07-02 | - |
| [常见问题与资源链接](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/09-faq-resources.md) |  | 2026-07-02 | - |
| [总结与Takeaways](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/10-summary.md) |  | 2026-07-02 | - |

### knowledge/learning/02-agent-engineering-methodology/longcat-agent-learning-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [LongCat-2.0 Agent能力实测：概述与学习目标](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/00-overview.md) |  | 2026-07-02 | - |
| [LongCat-2.0核心概念解析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/01-core-concepts.md) |  | 2026-07-02 | - |
| [Claude Code接入LongCat-2.0配置指南](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/02-claude-code-integration.md) |  | 2026-07-02 | - |
| [BI数据看板项目实战全流程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/03-bi-dashboard-demo.md) |  | 2026-07-02 | - |
| [Token效率对比分析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/04-token-efficiency.md) |  | 2026-07-02 | - |
| [Loop Engineering方法论解析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/05-loop-engineering.md) |  | 2026-07-02 | - |
| [总结与回顾](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/06-summary.md) |  | 2026-07-02 | - |
| [常见问题（FAQ）](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/07-faq.md) |  | 2026-07-02 | - |
| [资源与参考链接](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/08-resources.md) |  | 2026-07-02 | - |

### knowledge/learning/03-agent-platforms-tools

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md) |  | 2026-07-04 | anthropic、financial-services、ai-agent、claude、mcp、fintech、vertical-industry、investment-banking |
| [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md) |  | 2026-07-04 | areal、agentic-rl、online-rl、self-evolving-agent、reinforcement-learning、ant-group、agent-infrastructure、agent-trajectory |
| [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md) |  | 2026-07-04 | browseract、ai-agent、browser-automation、playwright、skill-forge、web-automation |
| [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md) |  | 2026-07-04 | echobird、ai-agent、tauri、rust、model-nexus、claude-code、codex、openclaw、local-llm、desktop-tool |
| [MopMonk 安全 Agent Wiki 教程](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki.md) |  | 2026-07-02 | - |
| [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md) |  | 2026-07-04 | octo、mininglamp、private-ai、agent-collaboration、a2a、matter、taste、orchestration、multi-agent、trustworthy-ai |
| [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md) |  | 2026-07-04 | open-code-review、ai-code-review、alibaba、cli、agent、aacr-bench、code-quality、devops |
| [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md) |  | 2026-07-04 | quantdinger、ai-trading、mcp、quantitative-finance、self-hosted、docker、agent-gateway、trading-bot |
| [Rainman Translate Book Wiki 教程](learning/03-agent-platforms-tools/rainman-translate-book-wiki.md) |  | 2026-07-02 | - |
| [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md) |  | 2026-07-04 | the-agency、ai-agent、agent-framework、multi-agent、claude-code、cursor |
| [TRAE v3.3.74 版本发布笔记](learning/03-agent-platforms-tools/trae-v3-3-74-release-notes.md) |  | 2026-07-08 | trae、release-notes、browser-configuration、windows-sdk、mssdk、ide |

### knowledge/learning/03-agent-platforms-tools/fable5-cost-optimization-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Fable 5成本优化技巧Wiki - 概述](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/00-overview.md) |  | 2026-07-02 | - |
| [定价背景与按量计费转型](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/01-pricing-background.md) |  | 2026-07-02 | - |
| [社区开源成本优化方案](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/02-community-solutions.md) |  | 2026-07-02 | - |
| [官方成本优化机制](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/03-official-optimizations.md) |  | 2026-07-02 | - |
| [场景化选型决策指南](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/04-selection-guide.md) |  | 2026-07-02 | - |
| [核心工程洞察](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/05-core-insights.md) |  | 2026-07-02 | - |
| [常见问题解答](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/06-faq.md) |  | 2026-07-02 | - |
| [资源与参考链接](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/07-resources.md) |  | 2026-07-02 | - |
| [天才程序员体验卡+5！](learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/article-content.md) |  | 2026-07-02 | - |

### knowledge/learning/03-agent-platforms-tools/mopmonk-security-agent-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [教程概述与学习目标](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/00-overview.md) |  | 2026-07-02 | - |
| [核心概念解析（一）：CyberGym、Harness与PoC](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/01-core-concepts.md) |  | 2026-07-02 | - |
| [MiniMax M3基座：国产开源的六边形战士](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/02-minimax-m3.md) |  | 2026-07-02 | - |
| [三大核心技术：记忆驱动的安全Agent范式](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/03-core-technologies.md) |  | 2026-07-02 | - |
| [步骤式学习导读：入门/进阶/深入三层](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/04-learning-guide.md) |  | 2026-07-02 | - |
| [常见问题解答（FAQ）](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/05-faq.md) |  | 2026-07-02 | - |
| [相关资源链接](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/06-resources.md) |  | 2026-07-02 | - |

### knowledge/learning/03-agent-platforms-tools/open-code-review-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [概述与学习目标](learning/03-agent-platforms-tools/open-code-review-wiki/00-overview.md) |  | 2026-07-02 | - |
| [核心概念与设计理念](learning/03-agent-platforms-tools/open-code-review-wiki/01-core-concepts.md) |  | 2026-07-02 | - |
| [安装与配置指南](learning/03-agent-platforms-tools/open-code-review-wiki/02-installation.md) |  | 2026-07-02 | - |
| [使用流程与命令详解](learning/03-agent-platforms-tools/open-code-review-wiki/03-usage.md) |  | 2026-07-02 | - |
| [关键技术优化](learning/03-agent-platforms-tools/open-code-review-wiki/04-optimizations.md) |  | 2026-07-02 | - |
| [集成与高级用法](learning/03-agent-platforms-tools/open-code-review-wiki/05-integrations.md) |  | 2026-07-02 | - |
| [效果验证与质量评估](learning/03-agent-platforms-tools/open-code-review-wiki/06-effectiveness.md) |  | 2026-07-02 | - |
| [局限性与对比](learning/03-agent-platforms-tools/open-code-review-wiki/07-limitations.md) |  | 2026-07-02 | - |
| [总结与展望](learning/03-agent-platforms-tools/open-code-review-wiki/08-summary.md) |  | 2026-07-02 | - |
| [常见问题（FAQ）](learning/03-agent-platforms-tools/open-code-review-wiki/09-faq.md) |  | 2026-07-02 | - |
| [资源与参考链接](learning/03-agent-platforms-tools/open-code-review-wiki/10-resources.md) |  | 2026-07-02 | - |

### knowledge/learning/03-agent-platforms-tools/rainman-translate-book-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [教程概述与学习目标](learning/03-agent-platforms-tools/rainman-translate-book-wiki/00-overview.md) |  | 2026-07-02 | - |
| [核心功能详解](learning/03-agent-platforms-tools/rainman-translate-book-wiki/01-core-concepts.md) |  | 2026-07-02 | - |
| [安装部署指南](learning/03-agent-platforms-tools/rainman-translate-book-wiki/02-installation.md) |  | 2026-07-02 | - |
| [使用流程](learning/03-agent-platforms-tools/rainman-translate-book-wiki/03-usage.md) |  | 2026-07-02 | - |
| [局限性与注意事项](learning/03-agent-platforms-tools/rainman-translate-book-wiki/04-limitations.md) |  | 2026-07-02 | - |
| [总结与回顾](learning/03-agent-platforms-tools/rainman-translate-book-wiki/05-summary.md) |  | 2026-07-02 | - |
| [常见问题](learning/03-agent-platforms-tools/rainman-translate-book-wiki/06-faq.md) |  | 2026-07-02 | - |
| [资源链接](learning/03-agent-platforms-tools/rainman-translate-book-wiki/07-resources.md) |  | 2026-07-02 | - |

### knowledge/learning/04-docs-markup-tooling

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md) |  | 2026-07-04 | html、declarative-partial-updates、streaming、partial-rendering、web-standards、chrome、declarative-shadow-dom、ssr |
| [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/04-docs-markup-tooling/executablebooks-myst-guide-wiki.md) |  | 2026-07-02 | - |

### knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ExecutableBooks 生态概览](learning/04-docs-markup-tooling/executablebooks-myst-guide/00-overview.md) |  | 2026-07-02 | - |
| [MyST Markdown 核心语法](learning/04-docs-markup-tooling/executablebooks-myst-guide/01-myst-syntax.md) |  | 2026-07-02 | - |
| [MyST 项目结构与 myst.yml 配置](learning/04-docs-markup-tooling/executablebooks-myst-guide/02-project-structure.md) |  | 2026-07-02 | - |
| [Frontmatter 配置详解](learning/04-docs-markup-tooling/executablebooks-myst-guide/03-frontmatter-config.md) |  | 2026-07-02 | - |
| [目录结构（TOC）配置指南](learning/04-docs-markup-tooling/executablebooks-myst-guide/04-table-of-contents.md) |  | 2026-07-02 | - |
| [MyST Markdown 使用最佳实践](learning/04-docs-markup-tooling/executablebooks-myst-guide/05-best-practices.md) |  | 2026-07-02 | - |
| [参考资源与链接汇总](learning/04-docs-markup-tooling/executablebooks-myst-guide/06-resources.md) |  | 2026-07-02 | - |

### knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/examples

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Admonitions（提示框）样式大全](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/admonitions.md) |  | 2026-07-02 | - |
| [MyST Markdown 基础语法示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/basic-syntax.md) |  | 2026-07-02 | - |
| [交叉引用示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/cross-references.md) |  | 2026-07-02 | - |
| [GitHub Tools MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/mcp-server-demo.md) |  | 2026-07-02 | - |
| [MyST Roles（行内扩展）示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/roles-demo.md) |  | 2026-07-02 | - |

### knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [GitHub Tools MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc/github-tools.md) |  | 2026-07-02 | - |
| [Weather Service MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc/weather-service.md) |  | 2026-07-02 | - |

### knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [第0章：快速上手（Quick Start）](learning/04-docs-markup-tooling/myst-markdown-tutorial/00-quick-start.md) |  | 2026-07-02 | - |
| [第1章：MyST 简介与 CommonMark 对比](learning/04-docs-markup-tooling/myst-markdown-tutorial/01-introduction.md) |  | 2026-07-02 | - |
| [第2章：基础语法（上）- 文本与格式](learning/04-docs-markup-tooling/myst-markdown-tutorial/02-basic-syntax-part1.md) |  | 2026-07-02 | - |
| [第3章：基础语法（下）- 列表、链接与图片](learning/04-docs-markup-tooling/myst-markdown-tutorial/03-basic-syntax-part2.md) |  | 2026-07-02 | - |
| [第4章：高级功能 - Directives 和 Roles](learning/04-docs-markup-tooling/myst-markdown-tutorial/04-advanced-directives-roles.md) |  | 2026-07-02 | - |
| [第5章：高级功能 - 交叉引用](learning/04-docs-markup-tooling/myst-markdown-tutorial/05-advanced-cross-references.md) |  | 2026-07-02 | - |
| [第6章：高级功能 - 数学公式与代码块](learning/04-docs-markup-tooling/myst-markdown-tutorial/06-advanced-math-code.md) |  | 2026-07-02 | - |
| [第7章：高级功能 - 注释、脚注与参考文献](learning/04-docs-markup-tooling/myst-markdown-tutorial/07-advanced-notes-citations.md) |  | 2026-07-02 | - |
| [第8章：扩展组件 - 提示框（Admonitions）](learning/04-docs-markup-tooling/myst-markdown-tutorial/08-components-admonitions.md) |  | 2026-07-02 | - |
| [第9章：扩展组件 - 卡片、下拉与标签页](learning/04-docs-markup-tooling/myst-markdown-tutorial/09-components-ui.md) |  | 2026-07-02 | - |
| [第10章：扩展组件 - 图片与表格](learning/04-docs-markup-tooling/myst-markdown-tutorial/10-components-figures.md) |  | 2026-07-02 | - |
| [第11章：工具链集成 - Sphinx + myst-parser](learning/04-docs-markup-tooling/myst-markdown-tutorial/11-tooling-sphinx.md) |  | 2026-07-02 | - |
| [第12章：工具链集成 - Jupyter Book v1](learning/04-docs-markup-tooling/myst-markdown-tutorial/12-tooling-jupyter-book.md) |  | 2026-07-02 | - |
| [第13章：工具链集成 - mystmd（新一代）](learning/04-docs-markup-tooling/myst-markdown-tutorial/13-tooling-mystmd.md) |  | 2026-07-02 | - |
| [第14章：实战案例 - 技术文档写作](learning/04-docs-markup-tooling/myst-markdown-tutorial/14-case-study-tech-docs.md) |  | 2026-07-02 | - |
| [第15章：实战案例 - 学术论文与书籍](learning/04-docs-markup-tooling/myst-markdown-tutorial/15-case-study-academic.md) |  | 2026-07-02 | - |
| [第16章：常见问题解答（FAQ）](learning/04-docs-markup-tooling/myst-markdown-tutorial/16-faq.md) |  | 2026-07-02 | - |

### knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [附录A：MyST Markdown 速查表](learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/cheat-sheet.md) |  | 2026-07-02 | - |
| [附录B：资源推荐](learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/resources.md) |  | 2026-07-02 | - |

### knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/examples

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [示例：Admonitions 提示框样式大全](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/admonitions-demo.md) |  | 2026-07-02 | - |
| [示例：图片与表格](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/figures-tables-demo.md) |  | 2026-07-02 | - |
| [模板：学术论文模板](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/paper-template.md) |  | 2026-07-02 | - |
| [模板：技术文档模板](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/tech-doc-template.md) |  | 2026-07-02 | - |
| [示例：卡片、下拉与标签页](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/ui-components-demo.md) |  | 2026-07-02 | - |

### knowledge/learning/05-ai-multimodal-content

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md) |  | 2026-07-04 | agnes-ai、pavo、ai-video、ai-shortdrama、agent、harness、aigc、creative-platform、free-api、multimodal |
| [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md) |  | 2026-07-04 | AudioX-Turbo、音频生成、音乐生成、视频配音、扩散模型、模型蒸馏、AI开源、多模态、Anything-to-Audio、Distribution-Matching-Distillation、师生蒸馏 |
| [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md) |  | 2026-07-04 | libtv、ai-shortdrama、ai-video、ai-manhua、character-quality、emotion-control、3d-director、workflow |
| [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md) |  | 2026-07-04 | text-to-cad、cad、ai-agent、build123d、step、urdf、3d-printing、robotics |

### knowledge/learning/06-business-trends-analysis

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [《人工智能拟人化互动服务管理暂行办法》深度分析报告](learning/06-business-trends-analysis/2026-07-08-ai-anthropomorphic-interim-measures-analysis.md) | 系统解读五部门联合发布的《人工智能拟人化互动服务管理暂行办法》（2026年7月15日施行），对比涂鸦平台公告覆盖度，识别6项高风险遗漏义务，提供7天倒计时行动方案和37项合规自查清单。 | 2026-07-08 | AI regulation、compliance、CAC、Tuya、智能体、AI agent |
| [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md) |  | 2026-07-04 | ai-tools、intelligent-terminal、claudian、book-to-skill、ai-agent、terminal、obsidian、claude-code、agent-skills |
| [火山引擎AgentKit企业级AI Agent平台深度学习笔记：生产级四大能力+四大价值支柱+打通PoC到生产最后一公里](learning/06-business-trends-analysis/volcengine-agentkit-platform-analysis.md) |  | 2026-07-06 | AgentKit、火山引擎、企业级AI、智能体平台、Harness编排、Serverless、MCP协议、安全沙箱、存量焕新、生产就绪、全链路可观测、AI云原生 |
| [火山引擎AI云原生沙箱解决方案深度分析：Agent时代的生产级执行底座——极致性能、海量弹性、实战验证、普惠成本](learning/06-business-trends-analysis/volcengine-ai-cloud-native-sandbox-analysis.md) |  | 2026-07-06 | 火山引擎、云原生、沙箱、AI安全、MicroVM、Serverless、大模型应用、代码执行、Agent基础设施、安全隔离、弹性计算、E2B |
| [火山引擎方舟大模型平台入门文档深度分析报告](learning/06-business-trends-analysis/volcengine-ark-introduction-analysis.md) |  | 2026-07-02 | - |
| [火山引擎方舟 Ark CLI 深度分析：AI原生命令行工具的双层Agent架构与CLI即Skill模式](learning/06-business-trends-analysis/volcengine-arkcli-analysis.md) |  | 2026-07-07 | 火山引擎、方舟、ARK、Ark CLI、arkcli、Ark Docs MCP、命令行工具、AI Agent、MCP、大模型工具、AI开发工具、Claude Code、Cursor、Trae、双层架构 |
| [火山引擎HiAgent一站式数字员工派遣站完整学习笔记：八大优势+十大场景+企业级Agent全生命周期平台](learning/06-business-trends-analysis/volcengine-hiagent-platform-analysis.md) |  | 2026-07-06 | HiAgent、火山引擎、智能体平台、Agent开发、数字员工、企业AI、MCP、低代码、大模型运维、私有化部署、AI安全 |
| [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md) |  | 2026-07-04 | KickArt、火山引擎、AI视频生成、电商营销、创作Agent、爆款裂变、投前预审、内容分发、Seedance、VLM、AIGC营销、短视频创作、AI特效模板 |
| [火山引擎机器学习平台完整学习笔记：企业级云原生MLOps平台六大功能+千亿大模型训练+性能提升79%](learning/06-business-trends-analysis/volcengine-ml-platform-analysis.md) |  | 2026-07-07 | 火山引擎、机器学习平台、MLOps、分布式训练、大模型训练、云原生、GPU、模型推理、深度学习、字节跳动、AI基础设施、火山方舟 |
| [火山方舟协作奖励计划深度分析：数据换免费Tokens的飞轮模式与撤回授权机制设计](learning/06-business-trends-analysis/volcengine-reward-plan-analysis.md) |  | 2026-07-07 | 火山引擎、方舟、协作奖励计划、数据飞轮、增长策略、数据授权、撤回授权、用户激励、数据合规 |

### knowledge/learning/07-vendor-product-learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [火山引擎云手机（ACEP）完整学习笔记：一站式云手机解决方案+四大能力+四大优势+五大场景](learning/07-vendor-product-learning/volcengine-acep-cloudphone-analysis.md) |  | 2026-07-06 | ACEP、火山引擎、云手机、ARM服务器、音视频技术、云游戏、边缘计算、云原生、虚拟手机、仿真测试、云办公、B端产品设计、信息架构 |
| [火山引擎Mobile Use Agent完整学习笔记：云手机+视觉大模型的企业级移动端AI智能体+六大优势+三层架构+四大场景](learning/07-vendor-product-learning/volcengine-mobile-use-agent-analysis.md) |  | 2026-07-07 | Mobile Use Agent、火山引擎、云手机、豆包视觉大模型、MCP、GUI Agent、移动端自动化、Jeddak AICC、AI Agent、云原生 |

### knowledge/learning/07-vendor-product-learning/comparison

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [神卓互联 vs cpolar vs 花生壳：三款主流内网穿透工具六维度全面对比分析（2026版）](learning/07-vendor-product-learning/comparison/nat-penetration-tools-comparison-wiki.md) |  | 2026-07-06 | 内网穿透、NAT穿透、神卓互联、cpolar、花生壳、贝锐、Oray、远程访问、端口映射、SD-WAN、NAS外网访问、对比分析、选型指南、SaaS |
| [向日葵远程控制 vs 涂鸦智能：远程控制SaaS与AIoT平台的七维度全面对比分析](learning/07-vendor-product-learning/comparison/sunlogin-tuya-comparison-wiki.md) |  | 2026-07-06 | 向日葵、Sunlogin、Oray、贝锐科技、涂鸦智能、Tuya、TuyaSmart、远程控制、AIoT、IoT平台、对比分析、商业模式、产品矩阵、技术架构、定价策略 |

### knowledge/learning/07-vendor-product-learning/openai/chatgpt-codex-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [概述与学习路径](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/00-overview.md) |  | 2026-07-08 | 概述、产品简介、学习路径、章节导航、ChatGPT Codex、AI工作助手 |
| [产品定位与价值主张](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/01-product-positioning.md) |  | 2026-07-08 | 产品定位、价值主张、用户画像、差异化分析、痛点分析、ChatGPT Codex、AI工作助手 |
| [核心功能详解](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/02-core-features.md) |  | 2026-07-08 | 核心功能、功能模块、研究助手、成果交付、流程自动化、连接器、ChatGPT Codex、AI工作助手 |
| [界面设计与视觉分析](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/03-interface-design.md) |  | 2026-07-08 | 界面设计、视觉设计、布局结构、色彩体系、组件设计、排版系统、ChatGPT Codex |
| [信息架构与导航设计](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/04-information-architecture.md) |  | 2026-07-08 | 信息架构、导航设计、内容组织、用户路径、站点地图、下拉菜单、渐进式披露、ChatGPT Codex |
| [用户体验策略分析](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/05-user-experience.md) |  | 2026-07-08 | 用户体验、UX策略、文案写作、信任建立、CTA设计、社会认同、转化优化、ChatGPT Codex |
| [用户交互流程分析](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/06-user-flow.md) |  | 2026-07-08 | 用户旅程、交互设计、转化漏斗、访客路径、导航设计、移动端适配、多平台入口、决策点设计、ChatGPT Codex |
| [双轨产品策略解析](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/07-dual-track-strategy.md) |  | 2026-07-08 | 产品策略、双轨定位、市场细分、用户分层、for-work、for-developers、价值叙事、客户证言、ChatGPT Codex |
| [多端协同策略分析](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/08-multi-platform.md) |  | 2026-07-08 | 多端协同、跨平台、IDE集成、CLI、桌面应用、移动端、统一账号、上下文同步、审批模式、ChatGPT Codex |
| [工具集成与生态系统](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/09-tool-integration.md) |  | 2026-07-08 | 工具集成、连接器、Connectors、MCP、生态系统、工作流自动化、Gmail、Slack、GitHub、Notion、Figma、Stripe、ChatGPT Codex |
| [定价策略与商业模式](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/10-pricing-model.md) |  | 2026-07-08 | 定价策略、商业模式、Freemium、订阅制、价格锚定、配额管理、套餐设计、SaaS定价、ChatGPT Codex |
| [技术实现推测](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/11-technology-speculation.md) |  | 2026-07-08 | 技术架构、Agent架构、沙箱环境、上下文工程、模型路由、MCP协议、代码审查、多端同步、ChatGPT Codex |
| [可借鉴的设计理念](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/12-design-insights.md) |  | 2026-07-08 | 设计理念、产品设计、UX设计、增长策略、转化设计、信任建立、价值叙事、ChatGPT Codex |
| [AI产品功能启发](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/13-feature-inspiration.md) |  | 2026-07-08 | 功能设计、产品功能、连接器模式、自动化、成果交付、任务管理、入门引导、配额管理、AI产品设计、ChatGPT Codex |
| [设计启示与经验总结](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/14-lessons-learned.md) |  | 2026-07-08 | 经验总结、产品思维、设计哲学、商业化、信息架构、UX写作、AI产品、ChatGPT Codex |
| [相关资源链接](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/15-resources.md) |  | 2026-07-08 | 资源链接、官方文档、开发者资源、下载链接、学习路径、ChatGPT Codex |

### knowledge/learning/07-vendor-product-learning/oray

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [贝锐（Oray）五大产品线综合分析Wiki：20年连接专家的软硬服铁三角与AI战略跃迁](learning/07-vendor-product-learning/oray/oray-comprehensive-analysis-wiki.md) |  | 2026-07-06 | 贝锐、Oray、向日葵、蒲公英、花生壳、洋葱头、OrayOS、远程控制、SD-WAN、内网穿透、4A管理、AI战略、软硬结合、SaaS、产品矩阵 |

### knowledge/learning/07-vendor-product-learning/oray/retrospective-oray-comprehensive-analysis-20260706

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [贝锐五大产品线综合分析执行过程复盘](learning/07-vendor-product-learning/oray/retrospective-oray-comprehensive-analysis-20260706/execution-retrospective.md) |  | 2026-07-06 | - |
| [贝锐五大产品线综合分析导出建议与后续方向](learning/07-vendor-product-learning/oray/retrospective-oray-comprehensive-analysis-20260706/export-suggestions.md) |  | 2026-07-06 | - |
| [贝锐五大产品线综合分析洞察萃取](learning/07-vendor-product-learning/oray/retrospective-oray-comprehensive-analysis-20260706/insight-extraction.md) |  | 2026-07-06 | - |

### knowledge/learning/07-vendor-product-learning/sunlogin

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [HSK CLI（@aweray/hsk-cli）完整学习教程：AI时代零配置公网预览工具](learning/07-vendor-product-learning/sunlogin/hsk-cli-wiki.md) |  | 2026-07-06 | 向日葵、HSK、hsk-cli、CLI、内网穿透、文件托管、公网预览、零配置、AI Agent、匿名分享 |
| [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md) |  | 2026-07-04 | 贝锐、Oray、OrayClaw、龙虾、AI Agent、MCP、向日葵、蒲公英、花生壳、洋葱头、远程连接、AI执行基础设施、远程运维、SD-WAN、内网穿透、RPA、软硬结合 |
| [向日葵AI开发者生态（MCP+Skill+CLI+UI Locator）深度解析：四层架构与实战指南](learning/07-vendor-product-learning/sunlogin/sunlogin-ai-developer-ecosystem-wiki.md) |  | 2026-07-06 | 向日葵、Sunlogin、MCP、Model Context Protocol、Skill、CLI、UI Locator、AI Agent、远程控制、自动化、RPA |
| [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md) |  | 2026-07-04 | 向日葵、开机盒子、远程开机、WOL、硬件产品、Oray、贝锐科技、远程办公、IoT、智能硬件 |
| [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md) |  | 2026-07-04 | 向日葵、USB摄像头、SU1、远程视频、远程监控、远程医疗、视频会议、400万像素、双全向麦克风、免驱、智能硬件、Oray、贝锐科技、远程办公 |
| [向日葵企业CLI（awesun-cli）完整学习教程：AI时代的命令行远控工具](learning/07-vendor-product-learning/sunlogin/sunlogin-cli-wiki.md) |  | 2026-07-06 | 向日葵、Sunlogin、awesun-cli、CLI、命令行、MCP、AI Agent、自动化运维、远程控制 |
| [向日葵远程控制产品全面深度解析：国民远控的生态战略、商业模式与AI跃迁](learning/07-vendor-product-learning/sunlogin/sunlogin-comprehensive-analysis-wiki.md) |  | 2026-07-06 | 向日葵、Sunlogin、Oray、贝锐科技、远程控制、产品矩阵、商业模式、软硬结合、AI Agent、MCP、竞品分析 |
| [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md) |  | 2026-07-04 | 向日葵、智能远控鼠标、MM110、BM110、蓝牙鼠标、远程控制、移动办公、智能硬件、Oray、贝锐科技、硬件对比 |
| [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md) |  | 2026-07-04 | sunlogin、远程控制、硬件、IPKVM、无网远控、蓝牙、HDMI采集、运维 |
| [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md) |  | 2026-07-06 | 向日葵、智能插线板、P4、P1Pro、4G智能插座、WiFi智能插座、远程控制、智能硬件、独立分控、电量监控、温柔关机、Oray、贝锐科技、远程办公 |
| [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md) |  | 2026-07-04 | 向日葵、PDU、智能排插、远程电源管理、IPDU、数据中心、机房运维、远程控制、智能硬件、Oray、贝锐科技 |
| [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md) |  | 2026-07-04 | 向日葵、远程控制、网络安全、等保2.0、国密算法、企业安全、零信任、远控安全 |
| [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md) |  | 2026-07-04 | 向日葵、智能插座、远程开机、C1Pro、C2、C4、蓝牙配网、4G联网、电量统计、智能硬件、Oray、贝锐科技、远程办公 |

### knowledge/learning/07-vendor-product-learning/sunlogin/retrospective-sunlogin-wiki-mobile-control-update-20260706

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [向日葵Wiki移动端远程控制功能更新执行过程复盘](learning/07-vendor-product-learning/sunlogin/retrospective-sunlogin-wiki-mobile-control-update-20260706/execution-retrospective.md) |  | 2026-07-06 | - |
| [向日葵Wiki移动端远程控制更新导出建议与后续方向](learning/07-vendor-product-learning/sunlogin/retrospective-sunlogin-wiki-mobile-control-update-20260706/export-suggestions.md) |  | 2026-07-06 | - |
| [向日葵Wiki移动端远程控制更新洞察萃取](learning/07-vendor-product-learning/sunlogin/retrospective-sunlogin-wiki-mobile-control-update-20260706/insight-extraction.md) |  | 2026-07-06 | - |

### knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md) |  | 2026-07-04 | 概述、产品定位、远程办公、目标用户、应用场景、研究背景 |
| [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md) |  | 2026-07-04 | 核心功能、远程开机、定时开机、双网络接入、批量开机、MAC地址开机、网络拓扑 |
| [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md) |  | 2026-07-04 | 技术实现、WOL原理、魔术包、网络协议栈、硬件规格、软硬协同架构、四层架构 |
| [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md) |  | 2026-07-04 | 版本差异、K3、K4、产品策略、市场分层、功能对比、定价策略 |
| [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md) |  | 2026-07-04 | 网页设计、用户体验、UX分析、信息架构、视觉设计、文案策略、交互设计 |
| [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md) |  | 2026-07-04 | 竞争优势、市场定位、竞品分析、差异化、远程开机、WOL局限、软硬件协同 |
| [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md) |  | 2026-07-04 | 深度洞察、行业启示、产品设计、智能硬件、痛点解决、生态协同、商业模式 |
| [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md) |  | 2026-07-04 | 改进建议、优化方向、功能增强、用户体验、安全性、产品迭代、增值服务 |
| [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md) |  | 2026-07-04 | WOL技术、网络唤醒、魔术包、Wake-on-LAN、技术历史、BIOS设置、故障排查 |
| [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md) |  | 2026-07-04 | 相关资源、官方链接、技术文档、参考资料、产品页面、帮助中心、社区支持 |

### knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md) |  | 2026-07-04 | 概述、学习目标、产品线全景、无网远控价值、阅读导航、产品定位 |
| [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md) |  | 2026-07-04 | 核心技术、IPKVM、HDMI采集、USB仿真、加密、架构模式、蓝牙配网、4G/5G、BIOS控制 |
| [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md) |  | 2026-07-04 | 控控2、旗舰IPKVM、KVM切换器、BIOS控制、看门狗、多上网方式、企业级、机房运维 |
| [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md) |  | 2026-07-04 | Q1、消费级入门、蓝牙5.0、双唤醒、高性价比、百兆网口、中小企业、远程办公 |
| [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md) |  | 2026-07-04 | Q2Pro、工业级4G、4K@60Hz、宽温设计、DIN导轨、双电源、医疗工控、防浪涌、文件传输 |
| [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md) |  | 2026-07-04 | Q0.5、口袋级近场、物理隔离、完全无网、防跳板、涉密运维、便携、USB取电、应急排障 |
| [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md) |  | 2026-07-04 | Q5Pro、专业级5G、双卡5G、协同远控、双向语音、USB映射、远程医疗、手术示教、2.5G网口、葵码登录 |
| [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md) |  | 2026-07-04 | 产品对比、25维度对比、产品线梯度、技术演进、技术路线对比、选型参考 |
| [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md) |  | 2026-07-04 | 应用场景、选型指南、决策树、八大场景、产品组合、机房运维、医疗工控、涉密场景、选型速查表 |
| [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md) |  | 2026-07-04 | FAQ、常见问题、BIOS控制、兼容性、安全加密、分辨率帧率、KVM切换器、流量卡、工业级 |
| [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md) |  | 2026-07-04 | 参考资料、官方链接、技术名词、市场报告、相关Wiki、版本信息、术语解释 |

### knowledge/learning/07-vendor-product-learning/volcengine

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [火山引擎Viking AI搜索推荐产品核心笔记](learning/07-vendor-product-learning/volcengine/viking-ai-search-rec-core-notes.md) |  | 2026-07-02 | 火山引擎、AI搜索、个性化推荐、大模型问答、字节跳动、企业服务、SaaS |
| [火山引擎方舟大模型平台入门文档深度分析报告](learning/07-vendor-product-learning/volcengine/volcengine-ark-introduction-analysis-report.md) |  | 2026-07-02 | 火山引擎、火山方舟、大模型平台、深度分析、Doubao、OpenAI兼容、SDK、MCP、多模态、Agent、产品分析 |
| [火山引擎方舟大模型平台核心笔记](learning/07-vendor-product-learning/volcengine/volcengine-ark-introduction-core-notes.md) |  | 2026-07-02 | 火山引擎、火山方舟、大模型平台、Doubao、OpenAI兼容、SDK、MCP、多模态、Agent、函数调用、豆包、云部署MCP、GUI自动化、上下文缓存、批量推理 |
| [火山引擎方舟入门文档原始内容提取](learning/07-vendor-product-learning/volcengine/volcengine-ark-introduction-extracted-content.md) |  | 2026-07-02 | 火山引擎、火山方舟、大模型平台、原始内容、SDK示例、Doubao |
| [火山引擎方舟 Ark CLI 核心笔记](learning/07-vendor-product-learning/volcengine/volcengine-arkcli-core-notes.md) |  | 2026-07-02 | 火山引擎、方舟、Ark CLI、arkcli、命令行工具、AI Agent、MCP、AI开发工具、Claude Code、Cursor、Trae |
| [火山引擎Computer Use Agent (CUA)深度分析：多模态大模型驱动的企业级桌面AI智能体——视觉感知·自主规划·桌面执行·任务闭环](learning/07-vendor-product-learning/volcengine/volcengine-computer-use-agent-analysis.md) |  | 2026-07-07 | Computer Use Agent、CUA、火山引擎、云手机、桌面自动化、多模态大模型、GUI Agent、AI智能体、RPA、noVNC、TOS、云端沙箱、视觉感知、Anthropic Computer Use |
| [火山引擎公网IP（EIP）完整学习笔记：云网络公网出入口基础组件](learning/07-vendor-product-learning/volcengine/volcengine-eip-analysis.md) |  | 2026-07-06 | 公网IP、EIP、火山引擎、云网络、BGP多线、DDoS防护、NAT网关、负载均衡、共享带宽包、弹性IP、字节跳动 |
| [火山引擎机器学习平台核心笔记](learning/07-vendor-product-learning/volcengine/volcengine-ml-platform-core-notes.md) |  | 2026-07-02 | 火山引擎、机器学习平台、MLOps、分布式训练、大模型训练、云原生、GPU、模型推理、深度学习、火山方舟 |
| [火山引擎Mobile Use Agent Skill与API技术实现指南](learning/07-vendor-product-learning/volcengine/volcengine-mobileuse-agent-skill-api-guide.md) |  | 2026-07-07 | 火山引擎、云手机、Mobile Use Agent、MUA、ClawHub、OpenClaw、Skill、OpenAPI、JSONL、自动化、GUI Agent、飞书机器人、Doubao视觉模型、移动端自动化 |
| [火山方舟协作奖励计划核心笔记](learning/07-vendor-product-learning/volcengine/volcengine-reward-plan-core-notes.md) |  | 2026-07-02 | 火山引擎、方舟、协作奖励计划、数据飞轮、增长策略、数据授权、撤回授权、用户激励 |
| [豆包搜索（SearchInfinity）完整学习笔记：专为AI Agent打造的信息获取引擎](learning/07-vendor-product-learning/volcengine/volcengine-searchinfinity-analysis.md) |  | 2026-07-06 | 豆包搜索、SearchInfinity、火山引擎、AI搜索、AI Agent、大模型联网、API服务、多模态检索、信息获取引擎、字节跳动、产品设计模式、ToB产品UX |

### knowledge/learning/first-principles

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [对抗性审查标准与验证流程](learning/first-principles/00-adversarial-review-protocol.md) |  | 2026-07-02 | - |
| [第一性原理的哲学起源与发展历程](learning/first-principles/01-philosophy-origins.md) |  | 2026-07-02 | - |
| [物理学中的第一性原理](learning/first-principles/02-physics-applications.md) |  | 2026-07-02 | - |
| [第一性原理商业创新实践案例](learning/first-principles/03-business-innovation-cases.md) |  | 2026-07-02 | - |
| [第一性原理核心学者与实践者论述汇编](learning/first-principles/04-key-thinkers-quotes.md) |  | 2026-07-02 | - |
| [第一性原理学术资源与推荐阅读](learning/first-principles/05-academic-resources.md) |  | 2026-07-02 | - |
| [第一性原理核心概念术语表与思维方式对比](learning/first-principles/06-concepts-glossary.md) |  | 2026-07-02 | - |
| [第一性原理发展时间线](learning/first-principles/07-timeline.md) |  | 2026-07-02 | - |
| [第一性原理方法论框架与实践指南](learning/first-principles/08-methodology-framework.md) |  | 2026-07-02 | - |
| [延伸阅读与资源索引](learning/first-principles/09-further-reading.md) |  | 2026-07-02 | - |
| [来源验证档案与对抗性审查记录](learning/first-principles/10-source-validation-log.md) |  | 2026-07-02 | - |
| [第三方外部评审记录](learning/first-principles/11-external-review.md) |  | 2026-07-02 | - |
| [第一性原理思维训练题库](learning/first-principles/12-exercises.md) |  | 2026-07-02 | - |
| [第一性原理思维的认知科学基础](learning/first-principles/13-cognitive-science-foundations.md) |  | 2026-07-02 | - |
| [AI时代的第一性原理：人机协同的思维增强](learning/first-principles/14-first-principles-in-ai-era.md) |  | 2026-07-02 | - |
| [第一性原理与类比推理的适用边界研究](learning/first-principles/16-boundary-conditions.md) |  | 2026-07-02 | - |

### knowledge/learning/first-principles/15-cross-domain-cases

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [生物学中的第一性原理思维案例](learning/first-principles/15-cross-domain-cases/biology.md) |  | 2026-07-02 | - |
| [计算机科学中的第一性原理思维案例](learning/first-principles/15-cross-domain-cases/computer-science.md) |  | 2026-07-02 | - |
| [数学中的第一性原理思维案例](learning/first-principles/15-cross-domain-cases/mathematics.md) |  | 2026-07-02 | - |
| [社会科学中的第一性原理思维案例](learning/first-principles/15-cross-domain-cases/social-sciences.md) |  | 2026-07-02 | - |

### knowledge/learning/first-principles/exercises

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [第一性原理思维训练题库 — 使用指南](learning/first-principles/exercises/00-intro.md) |  | 2026-07-02 | - |
| [Step 1 专项练习——问题定义与边界澄清](learning/first-principles/exercises/01-step1-problem-definition.md) |  | 2026-07-02 | - |
| [Step 2 专项练习——现有方案与假设列举](learning/first-principles/exercises/02-step2-assumptions.md) |  | 2026-07-02 | - |
| [Step 3 专项练习——拆解至基本要素](learning/first-principles/exercises/03-step3-decomposition.md) |  | 2026-07-02 | - |
| [Step 4 专项练习——质疑与验证](learning/first-principles/exercises/04-step4-questioning.md) |  | 2026-07-02 | - |
| [Step 5 专项练习——从基本原理重新构建](learning/first-principles/exercises/05-step5-reconstruction.md) |  | 2026-07-02 | - |
| [Step 6 专项练习——验证与迭代](learning/first-principles/exercises/06-step6-validation.md) |  | 2026-07-02 | - |
| [误区识别专项练习](learning/first-principles/exercises/07-pitfalls.md) |  | 2026-07-02 | - |
| [综合案例分析](learning/first-principles/exercises/08-cases.md) |  | 2026-07-02 | - |
| [练习实践指南](learning/first-principles/exercises/09-practice-guide.md) |  | 2026-07-02 | - |

### knowledge/learning/okr-wiki

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [叮当OKR帮助手册Wiki](learning/okr-wiki/00-overview.md) |  | 2026-07-08 | - |

### knowledge/learning/okr-wiki/appendix

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [术语表与参考资源](learning/okr-wiki/appendix/glossary.md) |  | 2026-07-08 | - |

### knowledge/learning/okr-wiki/concepts

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Key Results（关键结果）的特征](learning/okr-wiki/concepts/key-results-features.md) |  | 2026-07-08 | - |
| [Objective（目标）的特征](learning/okr-wiki/concepts/objective-features.md) |  | 2026-07-08 | - |
| [OKR的历史背景](learning/okr-wiki/concepts/okr-history.md) |  | 2026-07-08 | - |
| [OKR的核心原则](learning/okr-wiki/concepts/okr-principles.md) |  | 2026-07-08 | - |
| [OKR与KPI的区别](learning/okr-wiki/concepts/okr-vs-kpi.md) |  | 2026-07-08 | - |
| [什么是OKR](learning/okr-wiki/concepts/what-is-okr.md) |  | 2026-07-08 | - |

### knowledge/learning/okr-wiki/implementation

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [OKR对齐机制](learning/okr-wiki/implementation/aligning-okr.md) |  | 2026-07-08 | - |
| [OKR常见误区与避坑建议](learning/okr-wiki/implementation/common-mistakes.md) |  | 2026-07-08 | - |
| [OKR制定流程](learning/okr-wiki/implementation/creating-okr.md) |  | 2026-07-08 | - |
| [OKR启动阶段](learning/okr-wiki/implementation/getting-started.md) |  | 2026-07-08 | - |
| [OKR周期设置](learning/okr-wiki/implementation/setting-cycle.md) |  | 2026-07-08 | - |
| [OKR跟进与复盘](learning/okr-wiki/implementation/tracking-progress.md) |  | 2026-07-08 | - |

### knowledge/learning/okr-wiki/methods

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [自下而上的共创方法](learning/okr-wiki/methods/bottom-up-approach.md) |  | 2026-07-08 | - |
| [KR共创七步操作法](learning/okr-wiki/methods/kr-co-creation.md) |  | 2026-07-08 | - |
| [KR量化的七类方法](learning/okr-wiki/methods/kr-quantification-methods.md) |  | 2026-07-08 | - |
| [自上而下的共创方法](learning/okr-wiki/methods/top-down-approach.md) |  | 2026-07-08 | - |

### knowledge/learning/okr-wiki/scoring

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [OKR评分方法](learning/okr-wiki/scoring/how-to-score.md) |  | 2026-07-08 | - |
| [OKR与绩效的关系](learning/okr-wiki/scoring/okr-vs-performance.md) |  | 2026-07-08 | - |
| [OKR复盘流程](learning/okr-wiki/scoring/review-process.md) |  | 2026-07-08 | - |
| [OKR打分模板](learning/okr-wiki/scoring/scoring-templates.md) |  | 2026-07-08 | - |

### knowledge/learning/okr-wiki/templates

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [公司级OKR示例](learning/okr-wiki/templates/company-okr-examples.md) |  | 2026-07-08 | - |
| [部门级OKR示例](learning/okr-wiki/templates/department-okr-examples.md) |  | 2026-07-08 | - |
| [个人级OKR示例](learning/okr-wiki/templates/individual-okr-examples.md) |  | 2026-07-08 | - |
| [不同行业OKR示例](learning/okr-wiki/templates/industry-examples.md) |  | 2026-07-08 | - |
| [OKR检查清单](learning/okr-wiki/templates/okr-checklist.md) |  | 2026-07-08 | - |
| [OKR制定模板](learning/okr-wiki/templates/okr-templates.md) |  | 2026-07-08 | - |
| [OKR评分与复盘模板](learning/okr-wiki/templates/review-templates.md) |  | 2026-07-08 | - |

### knowledge/learning/okr-wiki/tools

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [隐藏关键词设置教程](learning/okr-wiki/tools/hidden-keyword-setting.md) |  | 2026-07-08 | - |
| [权限管理与安全设置](learning/okr-wiki/tools/permission-management.md) |  | 2026-07-08 | - |

### learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Learning Wiki 主题分类体系](learning/CATEGORIES.md) | Learning Wiki 知识库的8主题分类体系设计，包含分类原则、主题关系图、学习路径与各主题完整Wiki清单 | 2026-07-05 | categories、learning-wiki、knowledge-architecture、topic-classification、learning-path |
| [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md) | Learning Wiki知识库59个Wiki的系统化学习路径推荐，包含8主题内部学习顺序、前置依赖、关联知识点、角色定制路径 | 2026-07-05 | learning-path、study-guide、prerequisites、knowledge-graph、curriculum |
| [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) | 系统讲解Agent通信四大协议：MCP（Anthropic 2024，工具层）、ACP（IBM/BeeAI 2025，本地Agent协作）、A2A（Google 2025，跨厂商Agent协作）、ANP（去中心化网络层）。包含协议分层架构、N×M集成问题分析、各协议技术规范对比、代码示例与快速参考。本文档已原子化，详细内容见 agent-communication-protocols/ 子目录。 | 2026-07-03 | agent-protocols、mcp、acp、a2a、anp、multi-agent、communication、open-standard、linux-foundation、interoperability |
| [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md) | 基于 agentskills.io 官方完整教程（快速入门/最佳实践/描述优化/质量评估/脚本使用/客户端实现）和 external/agentskills 源码深度核实的 Agent Skills 开放标准完整指南。覆盖目录结构、SKILL.md格式规范、渐进式披露机制、自包含脚本设计、触发准确率优化、评估驱动迭代、skills-ref验证工具使用、客户端5步集成指南，以及与本项目现有Skill体系的对比分析。本文档已原子化，详细内容见 agent-skills-wiki/ 子目录。 | 2026-07-02 | agent-skills、skills、open-standard、specification、ai-agent、skill-development、progressive-disclosure、skills-ref、client-implementation、skill-evals |
| [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md) | 从AI Agent技术实现视角出发的Interface/API/ABI/Protocol四层抽象总览，聚焦MCP/ACP/A2A/ANP生态中的具体体现 | 2026-07-03 | agent、mcp、interface、api、abi、protocol、a2a |
| [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md) | Agent视角的Interface：能力契约，JSON Schema驱动的Tool/Skill/Agent声明模式 | 2026-07-03 | agent、interface、mcp、tool、json-schema、skill |
| [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md) | Agent视角的API：JSON-RPC 2.0作为Agent API标准，MCP/ACP/A2A的API设计与调用案例 | 2026-07-03 | agent、api、json-rpc、mcp、a2a、rest |
| [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md) | Agent视角的ABI：JSON+STDIO/HTTP如何绕过传统二进制兼容问题，实现跨语言Agent互操作 | 2026-07-03 | agent、abi、json、serialization、cross-language、stdio、http |
| [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md) | Agent视角的Protocol：MCP/ACP/A2A/ANP四层协议定位、消息流程、握手机制与协作模式 | 2026-07-03 | agent、protocol、mcp、a2a、acp、anp、json-rpc |
| [对比分析：Agent四层技术栈协同](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/05-agent-comparison.md) | Agent语境下Interface/API/ABI/Protocol九维度系统对比、全链路调用图、FAQ与技术选型决策指南 | 2026-07-03 | agent、comparison、architecture、mcp、decision-guide |
| [参考资料与学习路径](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.md) | Agent术语表、官方规范参考链接、三条进阶学习路径（Tool开发者/协议设计者/跨语言Runtime） | 2026-07-03 | agent、resources、reference、glossary、learning-path |
| [FFI（外部函数接口）教程总览](learning/01-agent-protocols-interfaces/ffi-wiki/00-overview.md) | FFI（Foreign Function Interface，外部函数接口）系统性技术教程总览，涵盖定义、工作原理、语言实现、应用案例、优劣分析、概念对比与参考资料。 | 2026-07-04 | ffi、foreign-function-interface、overview、tutorial |
| [FFI 定义与核心概念](learning/01-agent-protocols-interfaces/ffi-wiki/01-what-is-ffi.md) | FFI（Foreign Function Interface）的定义、核心概念、发展历史、与 ABI/API 的关系辨析，以及 FFI 解决的核心问题。 | 2026-07-04 | ffi、foreign-function-interface、definition、core-concepts |
| [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md) | FFI 的底层工作原理：调用约定、名称修饰、数据封送、内存管理、绑定生成机制的详细讲解。 | 2026-07-04 | ffi、calling-convention、name-mangling、marshalling、memory-management、binding |
| [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md) | Python、Java、Go、Rust、Node.js、C# 六种主流编程语言中的 FFI 实现方式、核心 API 与代码示例。 | 2026-07-04 | ffi、python、java、go、rust、nodejs、csharp、language-implementations |
| [实际应用案例与代码示例](learning/01-agent-protocols-interfaces/ffi-wiki/04-use-cases.md) | FFI 实际应用案例：Python 调用 C 实现矩阵运算加速、Rust 集成 C 图形库、Go 通过 cgo 调用 C 压缩库，以及 FFI 最佳实践清单。 | 2026-07-04 | ffi、use-cases、code-examples、best-practices |
| [FFI 的优势与局限性](learning/01-agent-protocols-interfaces/ffi-wiki/05-advantages-limitations.md) | FFI 的优势、局限性、性能开销分析与安全性考量，帮助读者全面评估 FFI 的适用性。 | 2026-07-04 | ffi、advantages、limitations、performance、security |
| [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md) | FFI 与 ABI、API、RPC、IPC、IDL 的多维度对比分析，含选型决策树与常见混淆点澄清。 | 2026-07-04 | ffi、comparison、abi、api、rpc、ipc、idl |
| [术语表与参考资料](learning/01-agent-protocols-interfaces/ffi-wiki/07-resources.md) | FFI 相关术语表（≥15条）、权威参考资料、分难度扩展阅读建议与项目内相关 wiki 交叉引用。 | 2026-07-04 | ffi、glossary、references、further-reading |
| [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md) | IDL（接口定义语言）Wiki 教程总览，介绍 IDL 在接口技术栈中的定位、9 章导航与阅读路径 | 2026-07-04 | idl、interface-definition-language、overview、tutorial、protobuf、thrift、corba |
| [一、IDL 定义与作用：接口契约的语言中立描述](learning/01-agent-protocols-interfaces/idl-wiki/01-what-is-idl.md) | IDL（接口定义语言）的标准定义、核心特征、发展三阶段时间线与价值定位 | 2026-07-04 | idl、definition、history、concept、interface-contract |
| [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md) | IDL 基本数据类型体系（标量/复合/枚举/容器）与注解注释机制，含 Protobuf/CORBA/Thrift 三语法对照 | 2026-07-04 | idl、syntax、type-system、protobuf、corba-idl、thrift、annotations |
| [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md) | IDL 接口声明语法与方法描述规范，含参数方向、异常声明、Protobuf/CORBA/Thrift 三语法对照 | 2026-07-04 | idl、syntax、interface、service、rpc、protobuf、corba-idl、thrift |
| [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md) | Protocol Buffers、Apache Thrift、CORBA IDL、COM/DCOM IDL、Apache Avro IDL 五大主流规范详解 | 2026-07-04 | idl、protobuf、thrift、corba、com-idl、avro、specifications |
| [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md) | Protocol Buffers、Thrift、CORBA IDL、COM IDL、Avro IDL 五大规范的多维度对比与按场景的选型决策指南 | 2026-07-04 | idl、comparison、decision-tree、selection、protobuf、thrift、corba、avro |
| [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md) | IDL 编译流程图、主流编译器介绍、构建系统集成（Maven/Gradle/Bazel）与 Schema 演进兼容性管理 | 2026-07-04 | idl、toolchain、compiler、codegen、protoc、thrift、maven、gradle、bazel、schema-evolution |
| [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md) | 三个完整应用案例（gRPC 服务定义、Thrift 微服务接口、CORBA 遗留系统集成）与 IDL 设计最佳实践 | 2026-07-04 | idl、use-cases、grpc、thrift、corba、best-practices、examples |
| [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md) | 传统 IDL 与现代接口描述格式（OpenAPI/GraphQL Schema/JSON Schema/AsyncAPI）的边界划分、对比与演进，含 MDI 关联 | 2026-07-04 | idl、openapi、graphql、json-schema、asyncapi、mdi、comparison、modern-formats |
| [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md) | IDL 相关术语表、权威参考资料、按难度分级的扩展阅读建议与项目内相关 wiki 交叉引用 | 2026-07-04 | idl、resources、glossary、references、further-reading、specifications |
| [一、概念总览：软件接口的四层抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md) | Interface/API/ABI/Protocol四个核心技术概念的层次总览与阅读指引 | 2026-07-03 | interface、api、abi、protocol、architecture |
| [二、接口（Interface）：语言级行为抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/01-interface.md) | 接口（Interface）的标准定义、核心特征、多范式应用场景与代码案例 | 2026-07-03 | interface、oop、functional-programming、polymorphism、duck-typing |
| [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md) | API的精确定义、REST/GraphQL/SOAP/gRPC类型对比、核心特征、应用场景与主流案例 | 2026-07-03 | api、rest、graphql、soap、grpc、web-api、microservices |
| [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md) | ABI的技术内涵、与API的本质区别、核心技术特征、底层系统应用场景与案例 | 2026-07-03 | abi、binary-compatibility、calling-convention、ffi、shared-library、syscall |
| [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md) | 协议的综合定义、网络/软件协议分类、核心特征、主流协议对比与应用场景 | 2026-07-03 | protocol、network、http、tcp、websocket、osi-model、tcp-ip |
| [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md) | Interface/API/ABI/Protocol四概念对比表格、关联关系分析、Mermaid架构层次图、常见混淆点澄清与决策指南 | 2026-07-03 | comparison、architecture、abstraction-layers、interface、api、abi、protocol |
| [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md) | 术语表、权威参考资料、扩展阅读建议与进阶学习路径 | 2026-07-03 | resources、references、glossary、further-reading、books、rfc |
| [Agent Skills（Addy Osmani）完整学习教程：谷歌Gemini团队的AI编程代理人工程技能库](learning/02-agent-engineering-methodology/agent-skills-wiki.md) | 谷歌Gemini团队主管Addy Osmani开源的AI编程代理人生产级工程技能库完整教程，GitHub星标1.9万+，围绕6阶段生命周期定义20个核心技能，配套7个斜杠命令，深度融入Google工程文化（Hyrum定律/测试金字塔/Chesterton栅栏/左移等）。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices、addy-osmani、gemini |
| [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md) | 阿里技术发布的Harness Engineering深度文章学习笔记，系统讲解从Prompt Engineering到Context Engineering再到Harness Engineering的范式演进，包含四条反直觉铁律、六大工程模式、悟空AI招聘实战案例、行业标杆地图、未来趋势与六条心法。 | 2026-07-04 | Harness Engineering、Agent Engineering、AI Agent、多Agent系统、Prompt Engineering、Context Engineering |
| [Harness七大组件Wiki教程](learning/02-agent-engineering-methodology/harness-seven-components-wiki.md) |  | 2026-07-13 | harness、七大组件、agent、业务底座 |
| [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md) | 系统学习Headroom AI Agent上下文压缩中间件，掌握给Agent装'压缩层'的完整技术方案，实现1万Token压到1千且质量不降反升，涵盖六种压缩算法、CCR可逆机制、四种接入方式、跨Agent记忆与自动学习等核心特性。 | 2026-07-04 | headroom、context-compression、agent、middleware、token-optimization、ccr、ai-agent |
| [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md) | 源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则（编码前先思考/简约至上/精确编辑/目标驱动），一个CLAUDE.md文件管住AI编程最常犯的毛病。GitHub 61.6k星项目完整教程，包含背景故事、核心原则详解、真实代码正反例、四种分发格式安装指南（CLAUDE.md/Cursor Rules/SKILL.md/插件）、Multica平台架构与multica-cli Skill使用指南、仓库文件结构说明，以及在SpecWeave项目中的整合情况。本文档已原子化，详细内容见 karpathy-llm-coding-guidelines/ 子目录。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude、ai-programming、agentic-engineering、claude-code、cursor、skills、plugin、mdc、multica、multica-cli、managed-agents |
| [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md) | 基于郭震AI实测经验，系统学习美团LongCat-2.0（1.6T参数MoE模型）接入Claude Code的完整流程，涵盖架构解析、配置指南、BI数据看板项目实战、Token效率对比和Loop Engineering方法论。 | 2026-07-04 | longcat、agent、claude-code、moe、loop-engineering、ai-coding、meituan |
| [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md) | 学习分析卡兹克《Vibe Coding 两大神级 Prompt》一文：第一性原理(管生成)与对抗式审查(管验证)构成完整闭环,是 Vibe Coding 的两大基石。含本项目亲身践行验证案例（含反面教材）及元方法论自举验证。 | 2026-07-04 | vibe-coding、prompt、第一性原理、对抗式审查、ai-agent、代码审查、multi-agent、aihot、可复用模式、践行鸿沟、类比推理 |
| [Agent Skills 项目概述与背景](learning/02-agent-engineering-methodology/agent-skills-wiki/00-overview.md) | 谷歌Gemini团队主管Addy Osmani开源的AI编程代理人生产级工程技能库，GitHub星标1.9万+，围绕6阶段生命周期定义20个核心技能，配套7个斜杠命令，深度融入Google工程文化。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [六阶段生命周期模型详解](learning/02-agent-engineering-methodology/agent-skills-wiki/01-lifecycle-model.md) | Agent Skills将软件开发生命周期划分为Define→Plan→Build→Verify→Review→Ship六个顺序阶段，用结构化工作流对抗AI的最短路径谬误。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [20个核心技能索引](learning/02-agent-engineering-methodology/agent-skills-wiki/02-skills-index.md) | 按Define/Plan/Build/Verify/Review/Ship六个阶段分组的20个核心技能详解，每个技能对应解决AI的一个天然缺陷。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [7个触发命令机制](learning/02-agent-engineering-methodology/agent-skills-wiki/03-slash-commands.md) | 斜杠命令是用户与Agent Skills交互的入口，每个命令对应一个或多个技能，通过简洁口诀传递核心理念，作为阶段转换的显式信号。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [Google工程文化术语解释](learning/02-agent-engineering-methodology/agent-skills-wiki/04-google-engineering-culture.md) | 详解Hyrum定律、Beyonce规则、Chesterton栅栏、测试金字塔、左移、基于主干开发、DAMP胜过DRY、代码即负债等8个Google工程文化核心术语。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [与SpecWeave对比分析与借鉴建议](learning/02-agent-engineering-methodology/agent-skills-wiki/05-specweave-comparison.md) | 对比Agent Skills与SpecWeave .agents/体系的架构范式、治理机制、体系完备度三个核心维度，提出可直接借鉴的设计模式，并分析Agent Skills的潜在不足。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [潜在应用场景](learning/02-agent-engineering-methodology/agent-skills-wiki/06-application-scenarios.md) | 覆盖遗留系统重构、新功能从零开发、紧急Bug修复、代码库健康度提升、团队AI编程规范落地等5个实战应用场景。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [延伸学习资源](learning/02-agent-engineering-methodology/agent-skills-wiki/07-resources.md) | Google工程实践文档、Addy Osmani著作、《Software Engineering at Google》书籍、Andrej Karpathy相关项目等延伸学习资源。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices |
| [Harness Engineering（驾驭工程）：概述与学习目标](learning/02-agent-engineering-methodology/harness-engineering-wiki/00-overview.md) |  | 2026-07-04 | - |
| [范式演进：三代AI工程](learning/02-agent-engineering-methodology/harness-engineering-wiki/01-paradigm-evolution.md) |  | 2026-07-04 | - |
| [四条反直觉铁律](learning/02-agent-engineering-methodology/harness-engineering-wiki/02-four-iron-laws.md) |  | 2026-07-04 | - |
| [六大工程模式](learning/02-agent-engineering-methodology/harness-engineering-wiki/03-six-patterns.md) |  | 2026-07-04 | - |
| [实战案例：悟空AI招聘](learning/02-agent-engineering-methodology/harness-engineering-wiki/04-wukong-case-study.md) |  | 2026-07-04 | - |
| [行业标杆地图](learning/02-agent-engineering-methodology/harness-engineering-wiki/05-industry-benchmarks.md) |  | 2026-07-04 | - |
| [未来趋势与六条心法](learning/02-agent-engineering-methodology/harness-engineering-wiki/06-future-trends.md) |  | 2026-07-04 | - |
| [批判性思考与评估](learning/02-agent-engineering-methodology/harness-engineering-wiki/07-critical-thinking.md) |  | 2026-07-04 | - |
| [常见问题（FAQ）](learning/02-agent-engineering-methodology/harness-engineering-wiki/08-faq.md) |  | 2026-07-04 | - |
| [资源链接](learning/02-agent-engineering-methodology/harness-engineering-wiki/09-resources.md) |  | 2026-07-04 | - |
| [Harness业务运行底座七组件：概述与学习目标](learning/02-agent-engineering-methodology/harness-seven-components-wiki/00-overview.md) |  | 2026-07-13 | harness、agent、业务运行底座、七组件 |
| [核心概念：从智能到交付——为什么需要Harness](learning/02-agent-engineering-methodology/harness-seven-components-wiki/01-core-concepts.md) |  | 2026-07-13 | harness、核心概念、智能vs交付 |
| [模型网关（Model Gateway）：大脑调度中心](learning/02-agent-engineering-methodology/harness-seven-components-wiki/02-model-gateway.md) |  | 2026-07-13 | harness、模型网关、model-gateway、模型路由 |
| [工具注册表（Tool Registry）：Agent的手脚管理](learning/02-agent-engineering-methodology/harness-seven-components-wiki/03-tool-registry.md) |  | 2026-07-13 | harness、工具注册表、tool-registry、工具调用 |
| [知识库引擎（Knowledge Base Engine）：业务参考书与判断力缓存](learning/02-agent-engineering-methodology/harness-seven-components-wiki/04-knowledge-base.md) |  | 2026-07-13 | harness、知识库、knowledge-base、RAG、业务知识 |
| [记忆系统（Memory System）：便签本与档案柜](learning/02-agent-engineering-methodology/harness-seven-components-wiki/05-memory-system.md) |  | 2026-07-13 | harness、记忆系统、memory、上下文、偏好 |
| [策略引擎（Policy Engine）：规则红线与强制约束](learning/02-agent-engineering-methodology/harness-seven-components-wiki/06-policy-engine.md) |  | 2026-07-13 | harness、策略引擎、policy-engine、安全、红线 |
| [可观测性（Observability）：数据追踪与Badcase闭环](learning/02-agent-engineering-methodology/harness-seven-components-wiki/07-observability.md) |  | 2026-07-13 | harness、可观测性、observability、监控、badcase |
| [配置管理（Configuration Management）：持续调教面板](learning/02-agent-engineering-methodology/harness-seven-components-wiki/08-configuration.md) |  | 2026-07-13 | harness、配置管理、configuration、调教、参数 |
| [实践指南：从零搭建你的文章Agent](learning/02-agent-engineering-methodology/harness-seven-components-wiki/09-practice-guide.md) |  | 2026-07-13 | harness、实践指南、实操、步骤、文章Agent |
| [案例分析：文章写作Agent的Harness拆解](learning/02-agent-engineering-methodology/harness-seven-components-wiki/10-case-study.md) |  | 2026-07-13 | harness、案例分析、文章Agent、实战拆解 |
| [常见问题解答（FAQ）](learning/02-agent-engineering-methodology/harness-seven-components-wiki/11-faq.md) |  | 2026-07-13 | harness、faq、常见问题、疑问解答 |
| [延伸资源与推荐阅读](learning/02-agent-engineering-methodology/harness-seven-components-wiki/12-resources.md) |  | 2026-07-13 | harness、资源、推荐阅读、进阶 |
| [速查手册：七大组件一页纸](learning/02-agent-engineering-methodology/harness-seven-components-wiki/13-cheatsheet.md) |  | 2026-07-13 | harness、速查、cheatsheet、手册 |
| [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md) | 源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则，用一个CLAUDE.md文件管住AI编程最常犯的毛病。本教程包含背景介绍、核心原则详解、真实代码正反例、安装使用指南，以及在SpecWeave项目中的整合情况。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude、ai-programming、agentic-engineering |
| [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md) | 四条核心原则的详细说明：编码前先思考、简约至上、精确编辑、目标驱动，包含每条原则的问题根源、具体要求和检验标准。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、principles、think-before-coding、simplicity、surgical-changes、goal-driven |
| [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md) | 真实世界代码示例演示四条原则，每个示例展示LLM常见错误做法和正确做法，涵盖隐藏假设、过度抽象、顺手重构、模糊目标等场景。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、examples、python、anti-patterns |
| [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md) | 快速上手安装和使用指南：三种分发格式对比（CLAUDE.md/SKILL.md/Cursor Rules）、Claude Code插件安装、Cursor编辑器集成详解、SKILL.md格式、项目定制方法、贡献者指南。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude-code、cursor、installation、quickstart、skills、plugin |
| [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md) | Karpathy LLM编程准则在SpecWeave项目中的整合情况：四条原则如何融入现有规范体系，对应的规范文件位置，以及团队使用方式。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、specweave、integration、rules |
| [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md) | 相关资源链接：三个官方仓库（karpathy-skills/multica/multica-cli）的文件结构、分发格式说明、Karpathy原帖、中文报道、Multica平台相关资源等参考资料。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、resources、references、repository-structure、multica、multica-cli |
| [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md) | Multica 是开源的 Managed Agents 平台，将编码 Agent 变成真正的队友——分配任务、跟踪进度、积累技能。本文档介绍 Multica 平台的核心概念、架构、功能模块，以及它与 Karpathy 准则的关系。 | 2026-07-02 | karpathy、llm、coding、agent、multica、platform、managed-agents、agentic-engineering、runtime、daemon、skill、autopilot、squad |
| [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md) | multica-cli 是一个可移植 Skill，教任意本地编码 Agent（Claude Code、Codex、Cursor 等）通过已认证的 multica CLI 安全操作 Multica 平台。本文档按「背景→核心安全原则→命令正反例→快速上手→工作流实战→生态设计理念」六层认知阶梯组织，帮助读者从理解为什么需要到掌握最佳实践。 | 2026-07-02 | karpathy、llm、coding、agent、multica、cli、skill、claude-code、cursor、codex、safety、external-agent |
| [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md) | 深度解析Anthropic即将推出的六条Agent产品线：Conway永久在线智能体、文件级记忆系统、Orbit主动助手、Operon生命科研平台、BugCrawl代码Bug自动修复，以及生态升级细节和GPT-5.6竞争动态分析。 | 2026-07-04 | anthropic、claude、conway、agent、orbit、operon、bugcrawl、file-memory、gpt-5.6、ai-agent、always-on-agent、proactive-ai |
| [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md) | 捕获量子位 2026-06-24 文章《刚刚，Claude Code大升级！卡帕西：LLM第三次变革》核心内容：Anthropic 发布企业协作工具 Claude Tag，定位为 Claude Code 进化，强调团队共享、主动介入（Ambient Mode）、异步执行，卡帕西称其为 LLM 用户界面第三次重大变革。本文档已原子化，详细内容见 claude-tag-article/ 子目录。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、ambient-mode、opus、karpathy、llm、协作、知识沉淀、复盘闭环、模式入库、已原子化 |
| [Minitap.ai 官方Wiki完整学习教程：零脚本AI QA工程师minitest深度解析、AndroidWorld 100%基准测试、开源mobile-use SDK与移动端测试革命](learning/03-agent-platforms-tools/minitap-official-wiki.md) | 深度解析Minitap.ai AI驱动的移动端测试平台，核心产品minitest作为完全自主的AI QA工程师，在AndroidWorld基准测试中达到100%任务成功率（全球第一），实现零脚本、零维护、零flake的移动端测试范式革命。涵盖技术架构、集成生态、客户案例、成本效益分析及开源mobile-use SDK。 | 2026-07-07 | minitap、minitest、mobile-use、ai-qa、mobile-testing、androidworld、e2e-testing、agent-testing、zero-script、ai-agent、mobile-automation |
| [Minitest & Mobile Use SDK 官方文档完整教程：AI QA工程师与开源移动自动化SDK系统化学习指南](learning/03-agent-platforms-tools/minitest-mobile-use-official-docs-wiki.md) | Minitest与Mobile Use SDK官方文档系统化学习教程，涵盖minitest AI QA工程师完整使用指南（入门、套件管理、运行测试、分类集成、参考手册）和mobile-use开源SDK深度教程（介绍安装、快速开始、核心概念、示例、SDK参考、故障排除），包含FAQ、最佳实践、术语表和资源链接。 | 2026-07-07 | minitest、mobile-use、minitap、ai-qa、mobile-testing、mobile-automation、sdk、official-docs、tutorial、e2e-testing、agent-testing |
| [mobile-use 深度分析：首个 AndroidWorld 100% 准确率的多智能体移动自动化框架架构解析](learning/03-agent-platforms-tools/mobile-use-deep-learning-analysis.md) | 深度解析 mobile-use 框架的技术架构：基于 LangGraph 的 6 智能体协作系统、统一设备控制器抽象层、工具包装器模式、SDK 双模式执行设计、LLM 分级配置策略，以及实现 AndroidWorld 基准测试 100% 准确率的关键架构决策。 | 2026-07-07 | mobile-use、langgraph、multi-agent、android-automation、ios-automation、mobile-agent、ai-agent、androidworld、uiautomator、wda、idb、minitap |
| [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md) | Claude Tag 文章元信息与概述：Anthropic 发布企业协作工具 Claude Tag，卡帕西称其为 LLM 用户界面第三次重大变革。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、karpathy、llm |
| [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md) | Claude Tag 五大核心观点：产品定位（Claude Code进化）、卡帕西LLM三次变革论断、与传统AI助手的根本差异、四大能力（共享上下文/持续记忆/主动介入/异步执行）、企业统一入口战略。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、ambient-mode、karpathy、llm、协作 |
| [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md) | Claude Tag 关键术语解释：Claude Tag、Ambient Mode（主动介入模式）、共享上下文、持续记忆、异步执行、Claude身份权限隔离、Opus 4.8、Fable 5。 | 2026-06-29 | claude、tag、anthropic、ambient-mode、opus、fable、术语 |
| [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md) | Claude Tag 重要数据汇总：Anthropic 65%产品代码参与、Opus 4.8唯一支持、率先登陆Slack、30天内取代现有应用、Beta开放对象、扩展计划、Token预算管理等。 | 2026-06-29 | claude、tag、anthropic、opus、slack、数据、统计 |
| [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md) | 原文四节结构概括：升级概览、先进团队先用Claude、实际部署、社区反响。 | 2026-06-29 | claude、tag、anthropic、slack、fable、社区 |
| [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md) | Claude Tag 与 SpecWeave 的三点关联：多智能体协作参照（已萃取为team-shared-ai-colleague模式）、组织知识沉淀对照、Agent工作流呼应（已萃取为ambient-proactive-agent模式）。 | 2026-06-29 | claude、tag、specweave、多智能体、知识沉淀、阶段守卫、自我演进 |
| [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md) | 本知识条目复盘闭环状态：复盘报告索引、已萃取可复用模式（2项L1）、方法论沉淀（2项操作指南）。 | 2026-07-03 | claude、tag、复盘、模式入库、方法论、闭环 |
| [Claude Tag：参考链接](learning/03-agent-platforms-tools/claude-tag-article/07-resources.md) | Claude Tag 相关参考链接汇总：原文、官方产品页、官方博客、媒体报道、复盘报告、已入库模式文件。 | 2026-06-29 | claude、tag、anthropic、参考资料、链接 |
| [最佳实践](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/best-practices.md) | 从官方文档中提取的minitest产品使用和mobile-use SDK开发最佳实践，帮助用户高效使用工具并避免常见陷阱。 | 2026-07-07 | best-practices、minitest、mobile-use、最佳实践、guidelines |
| [常见问题解答（FAQ）](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/faq.md) | 汇总minitest和mobile-use SDK的常见问题与解答，分为产品使用和SDK开发两大部分。 | 2026-07-07 | faq、minitest、mobile-use、troubleshooting、常见问题 |
| [综合术语表](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/glossary.md) | 整合minitest和mobile-use SDK的术语定义，确保术语翻译统一，方便查阅。 | 2026-07-07 | glossary、minitest、mobile-use、术语表、terminology |
| [资源链接](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/resources.md) | 汇总minitest和mobile-use SDK的官方资源链接，包括文档、GitHub、社区、博客、学术论文等，以及项目内相关Wiki交叉引用。 | 2026-07-07 | resources、links、minitest、mobile-use、资源、链接 |
| [入门指南总览](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/01-getting-started/00-overview.md) | miniTest入门指南章节导航，包含产品介绍、Mini代理介绍和快速开始教程。 | 2026-07-07 | minitest、ai-qa、入门、getting-started |
| [什么是miniTest](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/01-getting-started/01-what-is-minitest.md) | miniTest是一款AI驱动的移动端QA测试平台，无需组建QA团队即可为iOS和Android应用提供自动化测试覆盖。 | 2026-07-07 | minitest、ai-qa、产品介绍、overview |
| [认识Mini代理](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/01-getting-started/02-meet-mini.md) | Mini是miniTest背后的AI QA工程师代理，负责运行测试套件、维护用户故事、在虚拟设备上执行测试并提供可操作的反馈。 | 2026-07-07 | minitest、mini、ai-agent、ai-qa、代理介绍 |
| [快速开始](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/01-getting-started/03-quickstart.md) | 从注册到运行第一个用户故事的完整快速开始教程，全程约15分钟。 | 2026-07-07 | minitest、quickstart、快速开始、入门教程 |
| [测试套件管理总览](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/02-suite-management/00-overview.md) | 测试套件管理章节导航，包含用户故事结构、手动编写方法和Mini自动维护机制。 | 2026-07-07 | minitest、test-suite、用户故事、套件管理 |
| [用户故事解析](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/02-suite-management/01-anatomy-of-user-story.md) | 详细解析用户故事的组成结构，包括名称、类型、描述、验收标准、配置文件、附件和依赖关系。 | 2026-07-07 | minitest、user-story、acceptance-criteria、用户故事、验收标准 |
| [手动编写用户故事](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/02-suite-management/02-authoring-stories.md) | 介绍在仪表板、Slack、IDE（Cursor/Claude）三种界面中手动编写和编辑用户故事的方法。 | 2026-07-07 | minitest、user-story、authoring、编写用户故事、仪表板、Slack、IDE |
| [Mini自动维护套件](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/02-suite-management/03-mini-maintains-suite.md) | 介绍Mini如何自动读取代码库、生成初始测试套件、添加新功能测试、停用旧功能测试，保持套件与应用同步。 | 2026-07-07 | minitest、self-maintenance、自动维护、套件管理、ai-maintenance |
| [测试运行总览](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/03-running-tests/00-overview.md) | 测试运行章节导航，包含如何提供应用构建、触发测试运行和阅读运行报告。 | 2026-07-07 | minitest、test-runs、builds、运行测试、构建版本 |
| [提供应用构建](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/03-running-tests/01-providing-builds.md) | 介绍提供应用构建的两种方式：GitHub自动构建和CLI手动上传，以及Web预览URL和环境变量配置。 | 2026-07-07 | minitest、builds、构建版本、github、cli、web-preview |
| [触发运行](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/03-running-tests/02-triggering-runs.md) | 介绍从仪表板、Slack、GitHub Actions、CLI四种方式触发测试运行的方法。 | 2026-07-07 | minitest、trigger-run、触发运行、dashboard、slack、github-actions、cli |
| [阅读运行报告](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/03-running-tests/03-reading-run-report.md) | 详细介绍运行报告的结构，包括判定结果、验收标准列表、视频时间线、修复提示，以及无法处理状态的排查方法。 | 2026-07-07 | minitest、run-report、运行报告、verdict、fix-prompt |
| [问题分类与集成总览](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/00-overview.md) | 问题分类与集成章节导航，包含问题分类流程、Mini改进建议、Cursor/Claude集成、GitHub集成和Slack集成。 | 2026-07-07 | minitest、triage、integration、问题分类、集成 |
| [问题分类](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/01-triaging-issues.md) | 详细介绍问题分类流程，包括问题结构、三种分类操作、严重性覆盖以及在仪表板和Slack中的分类方式。 | 2026-07-07 | minitest、issues、triage、问题分类、bug、criticality |
| [Mini改进建议](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/02-mini-suggestions.md) | 介绍Mini在测试过程中主动发现的UX问题和边缘情况，建议与问题的区别，以及建议的生命周期。 | 2026-07-07 | minitest、suggestions、改进建议、ux、edge-cases |
| [Cursor和Claude集成](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/03-cursor-claude-integration.md) | 介绍如何通过CLI和MCP服务器将miniTest与Cursor、Claude Code等AI编码助手集成，从IDE编写测试故事和触发运行。 | 2026-07-07 | minitest、cursor、claude、ide、mcp、cli、集成 |
| [GitHub集成](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/04-github-integration.md) | 详细介绍GitHub集成配置，包括GitHub App安装、PR检查、自动构建、触发运行和分支保护设置。 | 2026-07-07 | minitest、github、integration、github-app、pr-check、ci |
| [Slack集成](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/05-slack-integration.md) | 详细介绍Slack集成配置，包括安装、频道路由、运行心跳消息、线程内分类操作和账户链接。 | 2026-07-07 | minitest、slack、integration、chatops、通知、运行心跳 |
| [参考文档总览](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/00-overview.md) | 参考文档章节导航，包含能力范围、CLI命令、术语表、MCP工具、Mini命令和GitHub Action参考。 | 2026-07-07 | minitest、reference、参考文档、cli、mcp、github-action |
| [能力范围](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/01-capabilities.md) | 诚实回答\"这对我的应用有效吗？\" — 详细说明Mini能做什么、即将推出什么、目前不能做什么以及不在路线图上的功能。 | 2026-07-07 | minitest、capabilities、能力范围、limitations、限制 |
| [CLI命令参考](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/02-cli-commands.md) | miniTest CLI命令的完整参考文档，包括全局标志、认证、应用管理、用户故事、配置文件、测试文件、构建和运行命令。 | 2026-07-07 | minitest、cli、command-line、命令行、参考 |
| [术语表](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/03-glossary.md) | miniTest在仪表板、CLI、MCP服务器和文档中使用的术语定义和规范命名。 | 2026-07-07 | minitest、glossary、术语表、terminology |
| [MCP工具参考](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/04-mcp-tools.md) | miniTest MCP服务器暴露的所有工具的API级参考文档，包括发现、用户故事、运行、构建、配置和文档工具。 | 2026-07-07 | minitest、mcp、mcp-tools、model-context-protocol、参考 |
| [Mini命令参考](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/05-mini-commands.md) | Slack中@Mini支持的所有命令，包括运行命令、编写命令、应用命令及其替代措辞。 | 2026-07-07 | minitest、slack、commands、mini-commands、聊天命令、参考 |
| [GitHub Action参考](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/06-github-action.md) | minitest-trigger GitHub Action的完整参考文档，包括输入输出、配置示例、构建路径要求、Web运行配置和取消先前运行机制。 | 2026-07-07 | minitest、github-action、ci、github-actions、参考 |
| [介绍与安装](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/01-introduction-installation/00-overview.md) | Mobile Use SDK介绍与安装指南章节，涵盖SDK基本介绍和环境准备步骤。 | 2026-07-07 | mobile-use、mobile-automation、installation、introduction |
| [SDK介绍](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/01-introduction-installation/01-introduction.md) | Mobile Use SDK基本介绍，了解SDK的核心功能和用途。 | 2026-07-07 | mobile-use、mobile-automation、introduction、sdk |
| [安装指南](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/01-introduction-installation/02-installation.md) | Mobile Use SDK安装指南，包含系统要求、SDK安装和设备连接配置。 | 2026-07-07 | mobile-use、mobile-automation、installation、setup |
| [快速开始](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/00-overview.md) | Mobile Use SDK快速开始章节总览，包含本地开发、平台模式、云设备、BrowserStack和iOS真机等多种使用方式的入门指南。 | 2026-07-07 | mobile-use、mobile-automation、quickstart、getting-started |
| [本地快速开始](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/01-local-quickstart.md) | 本地开发快速开始指南，通过配置文件管理LLM设置，完全控制执行环境。 | 2026-07-07 | mobile-use、mobile-automation、quickstart、local-development |
| [平台快速开始](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/02-platform-quickstart.md) | Minitap平台快速开始指南，使用集中式配置和内置可观测性，无需LLM配置文件。 | 2026-07-07 | mobile-use、mobile-automation、quickstart、platform |
| [云设备快速开始](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/03-cloud-quickstart.md) | Minitap云设备快速开始指南，使用托管的虚拟Android设备，零本地设置，所有智能体逻辑在云端运行。 | 2026-07-07 | mobile-use、mobile-automation、quickstart、cloud-devices |
| [BrowserStack快速开始](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/04-browserstack-quickstart.md) | BrowserStack快速开始指南，使用云端真实物理iOS设备运行移动自动化，无需本地硬件。 | 2026-07-07 | mobile-use、mobile-automation、quickstart、browserstack、ios |
| [iOS真机设置](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/05-physical-ios-setup.md) | USB连接物理iOS设备的一次性设置指南，使用WebDriverAgent (WDA)进行自动化。 | 2026-07-07 | mobile-use、mobile-automation、ios、physical-device、webdriveragent |
| [核心概念](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/00-overview.md) | Mobile Use SDK核心概念章节总览，介绍分层架构、Agent、任务、配置文件和Builder模式等核心组件。 | 2026-07-07 | mobile-use、mobile-automation、core-concepts、architecture |
| [架构概览](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/01-architecture-overview.md) | Mobile Use SDK分层架构详解，包括Agent层、任务层、LangGraph集成和设备交互层的设计。 | 2026-07-07 | mobile-use、mobile-automation、architecture、langgraph |
| [Agent核心类](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/02-agent.md) | Agent类详解，作为SDK的主要入口点，负责设备管理、服务器生命周期、任务执行和资源清理。 | 2026-07-07 | mobile-use、mobile-automation、agent、sdk |
| [Builder模式](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/03-builder-pattern.md) | Mobile Use SDK Builder模式详解，提供流式、类型安全的API来配置Agent和任务。 | 2026-07-07 | mobile-use、mobile-automation、builder-pattern、fluent-api |
| [可观测性与追踪](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/04-observability.md) | Mobile Use SDK可观测性功能详解，包括本地追踪记录、Platform GIF上传、调试工具和执行可视化。 | 2026-07-07 | mobile-use、mobile-automation、observability、tracing、debugging |
| [Agent配置](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/05-agent-profiles.md) | Agent配置文件详解，自定义LLM模型配置，为不同Agent组件配置不同模型，支持多配置文件切换。 | 2026-07-07 | mobile-use、mobile-automation、profiles、llm-configuration |
| [任务与任务请求](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/06-tasks.md) | 任务与任务请求详解，包括目标定义、结构化输出、任务配置选项、Builder模式和多步工作流。 | 2026-07-07 | mobile-use、mobile-automation、tasks、structured-output、workflows |
| [使用示例](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/00-overview.md) | Mobile Use SDK 使用示例总览，包含从简单到进阶的多个完整示例。 | 2026-07-07 | mobile-use、mobile-automation、examples、tutorial |
| [简单照片整理器](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/01-simple-photo-organizer.md) | 最基础的入门示例，展示如何使用默认配置创建 Agent、执行任务并获取结构化输出。 | 2026-07-07 | mobile-use、mobile-automation、examples、beginner、pydantic |
| [智能通知助手](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/02-smart-notification-assistant.md) | 高级示例，展示多 Profile 配置、TaskRequestBuilder、追踪录制和健壮的异常处理。 | 2026-07-07 | mobile-use、mobile-automation、examples、advanced、profiles、builder-pattern、tracing |
| [应用锁消息示例](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/03-app-lock-messaging.md) | 演示如何使用 App Lock 功能，确保自动化任务始终在特定应用（如 WhatsApp）内执行。 | 2026-07-07 | mobile-use、mobile-automation、examples、app-lock、messaging |
| [平台任务示例](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/04-platform-task-example.md) | 演示如何使用 Minitap 平台进行集中式任务编排、统一 API Key 管理和云端可观测性。 | 2026-07-07 | mobile-use、mobile-automation、examples、platform、cloud |
| [视频录制分析](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/05-video-recording-analysis.md) | 演示如何使用视频录制工具捕获和分析移动设备屏幕上播放的视频内容。 | 2026-07-07 | mobile-use、mobile-automation、examples、video、gemini、ffmpeg |
| [SDK 参考](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/00-overview.md) | Mobile Use SDK 完整 API 参考文档，包含核心类、Builder、类型定义和异常处理。 | 2026-07-07 | mobile-use、mobile-automation、sdk、reference、api |
| [Agent 类](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/01-agent-class.md) | Agent 类是 mobile-use SDK 的主入口点，负责管理设备交互和执行任务。 | 2026-07-07 | mobile-use、mobile-automation、sdk、agent、api |
| [AgentConfigBuilder](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/02-agent-config-builder.md) | AgentConfigBuilder 提供流式接口用于配置 Agent 行为、设备连接和服务器设置。 | 2026-07-07 | mobile-use、mobile-automation、sdk、builder、configuration、api |
| [TaskRequestBuilder](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/03-task-request-builder.md) | TaskRequestBuilder 类提供流式接口用于配置带详细选项的任务请求。 | 2026-07-07 | mobile-use、mobile-automation、sdk、builder、tasks、api |
| [类型定义](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/04-types.md) | mobile-use SDK 中使用的核心类型和数据结构参考。 | 2026-07-07 | mobile-use、mobile-automation、sdk、types、pydantic、data-structures |
| [异常处理](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/05-exceptions.md) | mobile-use SDK 中的异常类参考，包括异常层次结构、常见原因、解决方案和最佳实践。 | 2026-07-07 | mobile-use、mobile-automation、sdk、exceptions、error-handling、debugging |
| [故障排除与反馈](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/06-troubleshooting/00-overview.md) | 故障排除与反馈章节包含常见问题诊断、解决方案和反馈指南。 | 2026-07-07 | mobile-use、mobile-automation、troubleshooting、debugging、feedback、support |
| [常见问题排查](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/06-troubleshooting/01-troubleshooting.md) | 诊断和解决使用 Mobile Use SDK 时的常见问题，包括设备连接、服务器启动、任务执行、LLM API 和系统环境问题。 | 2026-07-07 | mobile-use、mobile-automation、troubleshooting、debugging、device-connection、server-issues |
| [反馈指南](learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/06-troubleshooting/02-providing-feedback.md) | 如何向 Minitap 团队提供反馈，包括 Bug 报告、功能建议，以及通过社区获取支持。 | 2026-07-07 | mobile-use、feedback、support、bug-report、feature-request、community |
| [scikit-build-core 全面教程：概述与导航](learning/04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md) | scikit-build-core Wiki 教程入口与导航枢纽：3 分钟理解项目定位、核心价值与 7 章阅读路径，含源码版本与学习建议 | 2026-07-04 | scikit-build-core、overview、pep517、cmake、python-packaging |
| [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md) | 系统讲解 scikit-build-core 的 PEP 517/660 后端机制、CMake 三层抽象、8 步 wheel 构建流程、配置系统四层架构与 File API 状态机 | 2026-07-04 | scikit-build-core、architecture、pep517、pep660、cmake、wheel |
| [项目目录结构与模块功能](learning/04-docs-markup-tooling/scikit-build-core-wiki/02-project-structure.md) | 逐模块解析 src/scikit_build_core/ 的 13 个顶层文件与 14 个子目录，标注源码锚点，覆盖 PEP 517 钩子、配置四层、CMake 三层、File API、元数据插件、可编辑安装、后端适配层 | 2026-07-04 | scikit-build-core、project-structure、modules、source-code |
| [核心 API 使用与配置详解](learning/04-docs-markup-tooling/scikit-build-core-wiki/03-core-api-and-config.md) | 系统讲解 scikit-build-core 的 PEP 517 构建后端钩子与 [tool.scikit-build] 配置项全集，含 Overrides 系统、动态元数据与 CMakeLists.txt 集成标准写法 | 2026-07-04 | scikit-build-core、api、configuration、pep517、pyproject-toml |
| [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md) | 提供三级递进实战路径：从 5 分钟最小 CMake 项目到真实 C++ 扩展包（pybind11/nanobind）再到发版 PyPI、交叉编译与 Stable ABI 高级配置 | 2026-07-04 | scikit-build-core、quickstart、tutorial、cmake、ninja、abi3 |
| [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md) | 汇总 scikit-build-core 真实项目常见问题与故障排查流程，覆盖 CI、Conda、迁移场景最佳实践与调试技巧 | 2026-07-04 | scikit-build-core、faq、best-practices、troubleshooting、ci、conda |
| [参考资料与扩展阅读](learning/04-docs-markup-tooling/scikit-build-core-wiki/06-resources.md) | 汇总 scikit-build-core 官方资源、教程资料、术语表与扩展阅读路径，含生态项目与进阶学习建议 | 2026-07-04 | scikit-build-core、resources、glossary、references、ecosystem |
| [WeasyPrint 教程总览](learning/04-docs-markup-tooling/weasyprint-wiki/00-overview.md) | WeasyPrint 是用 Python 编写的面向打印媒体的 HTML/CSS 渲染引擎，无需浏览器即可生成高质量 PDF。本教程从第一性原理出发，覆盖架构解析、安装配置、API 指南、CSS 分页特性、高级功能、源码导览、方案对比、最佳实践与常见问题。 | 2026-07-13 | weasyprint、pdf、html、css、rendering-engine、python、overview、tutorial |
| [第一性原理与核心定位](learning/04-docs-markup-tooling/weasyprint-wiki/01-first-principles-positioning.md) | PDF生成本质矛盾分析、现有5大方案痛点、WeasyPrint一句话定位、关键数据、核心特性矩阵、不支持的特性说明 | 2026-07-13 | weasyprint、first-principles、positioning |
| [架构深度解析：六步渲染管线](learning/04-docs-markup-tooling/weasyprint-wiki/02-rendering-pipeline.md) | WeasyPrint六步渲染管线深度解析：HTML解析→CSS解析→CSS应用→盒树构建→多遍布局→绘制输出，含各阶段源码入口和关键设计说明 | 2026-07-13 | weasyprint、architecture、pipeline、rendering |
| [核心依赖与技术栈](learning/04-docs-markup-tooling/weasyprint-wiki/03-tech-stack-dependencies.md) | WeasyPrint核心依赖解析：8个Python包依赖、3个系统C库、垂直工具链策略、依赖架构图 | 2026-07-13 | weasyprint、dependencies、tech-stack、cffi、cairo、pango |
| [安装与配置指南](learning/04-docs-markup-tooling/weasyprint-wiki/04-installation-cli.md) | WeasyPrint安装指南：Linux/macOS/Windows多平台方案对比、pip安装、验证方法、命令行完整用法、故障排查 | 2026-07-13 | weasyprint、installation、cli、setup、windows、gtk |
| [Python API 完全指南](learning/04-docs-markup-tooling/weasyprint-wiki/05-python-api-guide.md) | WeasyPrint Python API完全指南：5个核心类、多种输入源（文件/URL/字符串/文件对象）、自定义CSS、渲染选项详解、分步渲染、自定义URL获取器、PDF finisher后处理钩子 | 2026-07-13 | weasyprint、python-api、programming、code-examples |
| [CSS 分页与打印特性](learning/04-docs-markup-tooling/weasyprint-wiki/06-css-paged-media.md) | WeasyPrint CSS分页媒体特性：@page规则、16个边距盒位置、分页控制、交叉引用、计数器、脚注，含完整CSS代码示例 | 2026-07-13 | weasyprint、css、paged-media、@page、pagination |
| [高级功能详解](learning/04-docs-markup-tooling/weasyprint-wiki/07-advanced-features.md) | WeasyPrint高级功能：PDF/A/UA/X变体配置、图片缓存、自定义字体配置、SVG支持、CMYK色彩管理 | 2026-07-13 | weasyprint、pdf-variants、caching、fonts、svg、cmyk |
| [源码模块导览](learning/04-docs-markup-tooling/weasyprint-wiki/08-source-module-guide.md) | WeasyPrint源码模块完整导览：css/、formatting_structure/、layout/、draw/、pdf/、text/、svg/各目录职责和核心文件说明，提供源码阅读路径建议 | 2026-07-13 | weasyprint、source-code、modules、architecture |
| [九、方案对比与选型指南](learning/04-docs-markup-tooling/weasyprint-wiki/09-comparison-selection.md) | WeasyPrint与Pandoc/MyST/Puppeteer/Playwright/wkhtmltopdf/PrinceXML多维度对比、分层工具链定位、选型决策树 | 2026-07-13 | weasyprint、comparison、pandoc、myst、puppeteer、playwright、wkhtmltopdf、princexml、selection |
| [十、局限性与最佳实践](learning/04-docs-markup-tooling/weasyprint-wiki/10-limitations-best-practices.md) | WeasyPrint 5大核心局限性详解、10条生产级最佳实践（含CSS和Python代码示例） | 2026-07-13 | weasyprint、limitations、best-practices、production |
| [十一、常见问题与故障排查](learning/04-docs-markup-tooling/weasyprint-wiki/11-faq-troubleshooting.md) | WeasyPrint常见问题解答：Windows DLL缺失、中文乱码、图片不显示、表格跨页断裂、安装失败、PDF文件过大、页眉页脚不显示、counter(pages)显示为0等高频问题的原因分析和解决方案 | 2026-07-13 | weasyprint、faq、troubleshooting、debugging、windows |
| [十二、架构洞察与个人理解](learning/04-docs-markup-tooling/weasyprint-wiki/12-architecture-insights.md) | WeasyPrint架构深度洞察：自研CSS引擎的工程哲学、六步管线设计智慧、多遍分页本质（前向引用/不动点分析）、垂直工具链策略、开源+商业服务模型分析 | 2026-07-13 | weasyprint、architecture、design-philosophy、insights |
| [十三、相关资源链接](learning/04-docs-markup-tooling/weasyprint-wiki/13-resources.md) | WeasyPrint相关资源汇总：官方资源、CourtBouillon自有工具链（tinyhtml5/tinycss2/cssselect2/pydyf）、CSS分页媒体规范链接、实际应用场景清单 | 2026-07-13 | weasyprint、resources、links、specifications |
| [十四、Markdown 工作流实战：Pandoc & MyST 组合指南](learning/04-docs-markup-tooling/weasyprint-wiki/14-markdown-workflows.md) | Pandoc+WeasyPrint/MyST+WeasyPrint Markdown转PDF完整工作流实战，含Windows最简安装、CSS分页模板、Mermaid处理、封面页、Python构建脚本 | 2026-07-13 | weasyprint、pandoc、myst、markdown、workflow、best-practice、integration |
| [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md) | 学习分析《Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！》一文：Anime.js 4.5 推出官方 Three.js 适配器，通过适配器模式、API扁平化和前端语法糖，解决Three.js动画六大痛点，让3D动画写起来像CSS transform一样简单。 | 2026-07-04 | animejs、threejs、3d-animation、webgl、adapter-pattern、前端动画、javascript、动画库 |
| [MaineCoon 实时音视频基础模型与 Social World Model 范式](learning/05-ai-multimodal-content/mainecoon-social-world-model.md) | catnip.ai 发布的 22B 实时音视频基础模型 MaineCoon，定位为 Social World Model，在成本/速度/时长三大维度突破传统视频生成模型的三角困境，开启 AI 与人实时角色互动新范式。 | 2026-07-06 | mainecoon、catnip-ai、social-world-model、realtime-audiovideo、streaming-inference、ai-interaction、22b-model、三角困境、实时互动、多模态 |
| [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md) | 系统对比 DeepSeek V4、Kimi K2.7 Code、MiniMax M3、GLM 5.2 四款国产 AI 模型，按不写代码-文案类、不写代码-多模态资料、写代码、高并发批量任务四类人群给出推荐方案，并深入剖析国产模型信任问题，提出'能力是入场券，信任才是留下来的理由'核心洞察。 | 2026-07-04 | llm、domestic-model、model-comparison、glm、kimi、deepseek、minimax、coding、multi-modal、trust、scenario-recommendation、ai-agent |
| [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md) | 系统学习卢松松博客文章《Papi酱把公司全关了，只留七个人》，通过Papi酱十年创业完整时间线，解析\"把公司做小，把IP做大\"的创业新趋势，包含超级IP回归个人案例分析、个人IP vs 平台机构对比、小而美创业模式实践启示。 | 2026-07-04 | papi-jiang、个人IP、内容创业、MCN、创业趋势、小而美、商业模式、卢松松 |
| [AI变现完整指南：从技术到商业的全流程方法论](learning/06-business-trends-analysis/ai-monetization-wiki/00-overview.md) | AI变现完整指南总览，涵盖8大核心模块、3类应用场景与13章阅读路径 | 2026-07-03 | ai-monetization、overview、commercialization、business、guide |
| [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md) | AI变现核心术语界定，含标准定义、AI变现语境释义与示例 | 2026-07-03 | ai-monetization、concepts、terminology、pmf、ltv-cac、moat |
| [市场需求分析：识别与评估AI商业化机会](learning/06-business-trends-analysis/ai-monetization-wiki/02-market-analysis.md) | AI商业化机会识别与评估方法，含市场调研、用户需求挖掘、竞争格局、规模估算与场景适配性评估 | 2026-07-03 | ai-monetization、market-analysis、tam-sam-som、porter-five-forces、user-research |
| [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md) | AI产品9类盈利模式、价值主张设计、客户细分与商业模式选择决策树 | 2026-07-03 | ai-monetization、business-model、saas、pricing、canvas、freemium |
| [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md) | AI技术栈决策框架，含算法选型、算力配置、数据策略、部署方式与成本估算 | 2026-07-03 | ai-monetization、tech-selection、algorithm、compute、data-strategy、deployment |
| [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md) | AI产品开发流程，含原型设计、敏捷迭代、测试验证、数据飞轮与效果度量 | 2026-07-03 | ai-monetization、product-development、mlops、poc、data-flywheel、evaluation |
| [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md) | AI产品市场进入策略，含定位、渠道、传播、GTM节奏与冷启动 | 2026-07-03 | ai-monetization、gtm、marketing、positioning、cold-start、channel |
| [盈利策略：定价模型与规模化路径](learning/06-business-trends-analysis/ai-monetization-wiki/07-profitability-strategy.md) | AI产品定价模型、收入结构设计与规模化盈利路径，含单位经济模型优化 | 2026-07-03 | ai-monetization、pricing、revenue-structure、scaling、unit-economics |
| [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md) | ToB AI应用三类变现路径、成功案例剖析与行业挑战应对策略 | 2026-07-03 | ai-monetization、tob、enterprise、saas、customization、platform |
| [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md) | ToC AI应用三类变现路径、成功案例剖析与留存获客挑战应对 | 2026-07-03 | ai-monetization、toc、consumer、freemium、subscription、retention |
| [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md) | 医疗/金融/制造/教育/零售五大垂直行业AI变现路径、案例与挑战应对 | 2026-07-03 | ai-monetization、industry、vertical、healthcare、finance、manufacturing、education、retail |
| [实施步骤与关键成功因素](learning/06-business-trends-analysis/ai-monetization-wiki/11-implementation-steps.md) | AI变现六阶段实施路径与各阶段关键成功因素 | 2026-07-03 | ai-monetization、implementation、ksf、roadmap、stages |
| [风险提示与资源推荐](learning/06-business-trends-analysis/ai-monetization-wiki/12-risks-resources.md) | AI变现五大风险类别规避策略与实用资源推荐、术语速查表 | 2026-07-03 | ai-monetization、risks、resources、compliance、glossary |
| [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md) |  | 2026-07-04 | papi-jiang、个人IP、内容创业、MCN、创业趋势、小而美、商业模式、卢松松 |
| [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md) |  | 2026-07-04 | papi-jiang、个人IP、内容创业、MCN、创业趋势、时间线、papitube、泰洋川禾 |
| [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md) |  | 2026-07-04 | papi-jiang、个人IP、内容创业、核心观点、创业思维、商业模式、小而美 |
| [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md) |  | 2026-07-04 | papi-jiang、个人IP、罗永浩、李子柒、李佳琦、行业趋势、超级IP、MCN |
| [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md) |  | 2026-07-04 | papi-jiang、个人IP、MCN、模式对比、超级个体、平台机构、商业模式 |
| [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md) |  | 2026-07-04 | papi-jiang、个人IP、创业启示、小而美、实践要点、商业模式、创业建议 |
| [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md) |  | 2026-07-04 | papi-jiang、个人IP、总结、takeaway、创业趋势、核心要点 |
| [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md) |  | 2026-07-04 | papi-jiang、个人IP、FAQ、常见问题、创业疑问、MCN |
| [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md) |  | 2026-07-04 | papi-jiang、个人IP、资源链接、卢松松、参考资料、相关阅读 |
| [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md) |  | 2026-07-05 | 向日葵、sunlogin、Oray、贝锐科技、远程控制、智能硬件、产品学习、系列索引、AI执行基础设施、MCP、Skill、CLI、UI Locator |
| [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md) | TuyaOpen 是涂鸦开源的跨平台、跨芯片、跨操作系统的 AI-IoT SDK，核心目标是用一套灵活的 C/C++ SDK，结合涂鸦云的低延迟多模态 AI 能力，简化开放式 AI-IoT 生态的搭建。 | 2026-06-30 | tuya、tuyaopen、iot、sdk、ai、embedded、c、cpp、mcu、esp32、mcp、cloud、tkl、tal、tdd、tdl |
| [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md) | TuyaOpen-dev-skills 是面向 TuyaOpen 硬件开发流程的 AI Skills 仓库，以“最小 SKILL.md + references/ 按需加载 + scripts/ 可执行脚本”的三分结构，把环境搭建、编译、代码检查、烧录监控与调试闭环规范化。 | 2026-06-30 | tuya、tuyaopen、skills、agent-skills、cursor、claude、iot、embedded、workflow、ci |
| [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md) | 针对 external/TuyaOpen 工作区的可执行学习路线：先跑通 LINUX target 构建闭环，再进入硬件烧录与 AI 智能体硬件能力区。 | 2026-06-30 | tuyaopen、learning-path、iot、embedded、sdk、cli、tos |
| [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md) | 基于 external/WSL 源码（src/windows/wslc/ + doc/docs/）深度核实的 WSL CLI 命令树、参数定义、CLI 架构四层模型与官方架构 Mermaid 源图。修正先前学习计划中关于 CLI 命令短形态的误判——list/remove 才是主名，ls/ps/rm/delete 是别名。补充 interop binfmt 机制、systemd 启动流程、wslservice COM 接口、mini_init 多通道拓扑等技术细节。所有信息均有源码文件锚点可追溯。 | 2026-07-01 | wsl、wslc、cli、command-tree、argument-definitions、architecture、mermaid、interop、systemd、wslservice、com、binfmt、hvsocket、source-verification |
| [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md) | 基于 external/WSL 源码 + wsl.dev 开发者文档 + learn.microsoft.com 官方文档制定的系统学习计划，涵盖 Windows/Linux 三层架构、Linux 侧核心进程（mini_init/init/plan9/gns/relay）、Plan9/DrvFs 文件系统互操作、WSLC Container API 三语言投影（C/C#/C++ WinRT）、CMake 跨编译构建、组策略与诊断调试，包含 5 个实操练习、官方端到端示例、完整错误码表与 4 周学习路径。 | 2026-07-01 | wsl、learning-path、linux、windows、container、wslc、plan9、drvfs、cmake、sdk、diagnostics、hvsocket、gns、systemd、winrt、nuget、com、error-codes |
| [《你以为的自由是一种幻觉》第一性原理分析](learning/first-principles/15-cross-domain-cases/freedom-illusion-ai-era.md) | 以第一性原理六步法拆解公众号文章《你以为的自由是一种幻觉》，从认知局限、知识建构、人机协作出发，提炼AI时代保持认知主体性的六条公理与行动框架。 | 2026-07-13 | 第一性原理、AI时代认知、自由、认知悬浮、意图对齐、人机协作、知识建构 |

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。 | 2026-06-30 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
| [Frontmatter 路径与链接批量修复流程指南](operations/frontmatter-link-batch-repair-guide.md) | 大规模 frontmatter 路径与 Markdown 链接批量修复的完整流程指南：问题分类诊断、8 阶段分层修复策略、external 标记约定、LF 行尾保留、TOML source 覆盖问题处理，附 8 个自动化脚本的使用参考 | 2026-07-10 | frontmatter、链接修复、批量修复、check-links、路径规范化、external标记 |
| [HTML 正文提取操作指南](operations/html-body-extraction.md) | HTML 正文提取双方案：正则提取（首选）与边界标记索引截取法（兜底），含 HTML 清洗六步流程，适用于复杂嵌套 HTML 容器 | 2026-06-29 | html、正文提取、正则、索引截取、边界标记、html清洗、降级策略 |
| [关键路径工具失败降级矩阵](operations/tool-failure-degradation-matrix.md) | 关键路径工具失败的三级降级决策矩阵：网页内容获取、文件搜索、命令执行、子代理委派四类关键路径的降级策略、触发条件与决策流程 | 2026-07-06 | 工具降级、降级矩阵、webfetch、defuddle、浏览器mcp、关键路径、三级降级、标准化 |
| [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md) | 一条可落地执行、可观测验收的 Tuya IPC（网络摄像机）端-云-手机最小闭环跑通路径：先明确最小假设，再按步骤给出依赖/验收/排查，并附依赖关系图与闭环验收总表。 | 2026-06-30 | tuya、ipc、iot、闭环、配网、音视频、设备绑定、事件上报、联调、排查、验收 |
| [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md) | 当需要在 SpecWeave 中新增或使用 flexloop 相关功能时，基于三区域边界模型和四不原则的5种合规集成路径决策指南 | 2026-06-29 | vendor、flexloop、agentforge、submodule、集成方案、三区域模型、四不原则 |
| [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md) | 微信公众号文章内容提取双路径决策模型：defuddle CLI 与 PowerShell Invoke-WebRequest 互为兜底，含边界标记索引截取法作为正则失败时的兜底方案 | 2026-06-29 | 微信公众号、内容提取、defuddle、powershell、invoke-webrequest、html提取、反爬、降级策略 |
| [Windows平台兼容性手册：AI智能体执行任务陷阱系统化指南](operations/windows-platform-compatibility-guide.md) | 系统化记录 Windows 平台执行任务时的10类陷阱（编码、URL解析、路径分隔符、命令链接、引号差异、heredoc、管道、脚本扩展、行尾符、环境变量），整合项目已有4个Windows文档并提供统一索引与快速诊断流程 | 2026-07-06 | windows、powershell、platform-compatibility、url-parsing、encoding、path-separator、shell-differences、quoting、line-ending、ai-agent |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |
| [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md) | 记录 Windows PowerShell 下将 Python 中文 stdout 通过文本管道写入文件时可能发生的转码污染，以及推荐的安全写回方案 | 2026-06-30 | windows、powershell、encoding、utf-8、pipe、set-content、python、docs |
| [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md) | 系统性解决Windows终端中文乱码问题的完整指南，涵盖系统级/用户级/项目级三层配置方案 | 2026-07-01 | windows、powershell、cmd、utf-8、encoding、gbk、chcp、乱码 |

### reference

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [11、术语表](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/11-glossary.md) |  | 2026-07-13 | - |
| [12、常见问题与资源索引](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/12-faq-resources.md) |  | 2026-07-13 | - |
| [13、快速参考速查表（一页纸）](learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/13-quick-reference.md) |  | 2026-07-13 | - |

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
| [相对路径批量修复三类非直觉陷阱与修复方案](troubleshooting/relative-path-repair-pitfalls.md) | 记录批量修复 Markdown 相对路径断链时遇到的三类非直觉陷阱（replace_all 子串级联、归档目录深度误算、跨目录前缀误判）及各自的修复逻辑、验证方法与预防措施 | 2026-07-07 | relative-path、broken-links、replace-all、edit-tool、markdown、check-links、batch-repair、path-depth |
| [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md) | 记录在 submodule 目录内创建主项目文件导致 submodule 永久 dirty 的故障原因与解决方案，以及 submodule 元数据外置的最佳实践 | 2026-06-29 | git、submodule、vendor、dirty、modified-content |

### unknown

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [stage-guardrails-guide](stage-guardrails-guide.md) |  |  | - |
| [three-layer-routing](three-layer-routing.md) |  |  | - |
| [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md) |  |  | - |
| [L2 渐进式披露机制优化建议](best-practices/l2-progressive-disclosure-optimization.md) |  | 2026-07-12 | - |
| [L2 渐进式披露加载器性能优化：实测基线、优化建议与实施记录（P0+P1+P2完成）](best-practices/l2-progressive-disclosure-performance.md) |  | 2026-07-12 | - |
| [spec-loader-cold-start-storm-contingency](best-practices/spec-loader-cold-start-storm-contingency.md) |  |  | - |
| [spec-loader-config-guide](best-practices/spec-loader-config-guide.md) |  |  | - |
| [抖音 Vibecoding 人气赛道·执行行动计划](learning/douyin-vibecoding-action-plan.md) |  |  | vibecoding、抖音、执行计划、行动指南、TRAE大赛 |
| [SpecWeave 抖音VibeCoding图文·视觉设计规范](learning/douyin-vibecoding-design-spec.md) |  |  | vibecoding、抖音、设计规范、视觉设计、SpecWeave |
| [dspark-paper-wiki](learning/02-agent-engineering-methodology/dspark-paper-wiki.md) |  |  | - |
| [从 Prompt 到 Loop：四层工程打造稳定可控的 AI Agent](learning/02-agent-engineering-methodology/workbuddy-four-layers-seven-concepts-analysis.md) |  | 2026-07-14 | 七概念、Agent工程、Context Engineering、Harness Engineering、Loop Engineering、四层工程范式、事实核查通过 |
| [七概念×DeepTutor实践教程 - 概述](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/00-overview.md) |  | 2026-07-14 | 七概念、方法论、DeepTutor、教程 |
| [七概念×DeepTutor实践教程 - 术语表](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/glossary.md) |  | 2026-07-14 | 七概念、方法论、DeepTutor、教程、术语表 |
| [R - 复盘 (Retrospective)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/01-r-retrospective.md) |  | 2026-07-14 | 七概念、R、复盘、理论 |
| [I - 洞察 (Insight)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/02-i-insight.md) |  | 2026-07-14 | 七概念、I、洞察、理论 |
| [E - 萃取 (Extraction)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/03-e-extraction.md) |  | 2026-07-14 | 七概念、E、萃取、理论 |
| [C - 原子提交 (Atomic Commit)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/04-c-atomic-commit.md) |  | 2026-07-14 | 七概念、C、原子提交、理论 |
| [A - 原子化 (Atomization)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/05-a-atomization.md) |  | 2026-07-14 | 七概念、A、原子化、理论 |
| [F - 第一性原理 (First Principles)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/06-f-first-principles.md) |  | 2026-07-14 | 七概念、F、第一性原理、理论 |
| [V - 对抗性审查 (Adversarial Review)](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/07-v-adversarial-review.md) |  | 2026-07-14 | 七概念、V、对抗性审查、理论 |
| [DeepTutor项目简介](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/00-deeptutor-overview.md) |  | 2026-07-14 | DeepTutor、案例、简介 |
| [DeepTutor核心架构](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/01-core-architecture.md) |  | 2026-07-14 | DeepTutor、架构、案例 |
| [DeepTutor快速开始](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/03-quick-start.md) |  | 2026-07-14 | DeepTutor、快速开始、实践 |
| [DeepTutor优缺点评价](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/04-pros-cons.md) |  | 2026-07-14 | DeepTutor、分析、评价 |
| [Chat + Partners + My Agents 模块](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/02-modules/01-chat-partners-myagents.md) |  | 2026-07-14 | DeepTutor、模块、Chat、Partners |
| [Co-Writer + Book Engine 模块](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/02-modules/02-cowriter-book.md) |  | 2026-07-14 | DeepTutor、模块、Co-Writer、Book |
| [Knowledge Center + Learning Space 模块](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/02-modules/03-knowledge-learning.md) |  | 2026-07-14 | DeepTutor、模块、Knowledge、Learning |
| [Memory + Settings 模块](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/02-deeptutor-case/02-modules/04-memory-settings.md) |  | 2026-07-14 | DeepTutor、模块、Memory、Settings |
| [七概念×DeepTutor映射总览表](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/00-framework-mapping.md) |  | 2026-07-14 | 分析、映射、总览 |
| [R 复盘在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/01-r-in-deeptutor.md) |  | 2026-07-14 | 分析、R、复盘、映射 |
| [I 洞察在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/02-i-in-deeptutor.md) |  | 2026-07-14 | 分析、I、洞察、映射 |
| [E 萃取在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/03-e-in-deeptutor.md) |  | 2026-07-14 | 分析、E、萃取、映射 |
| [C 原子提交在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/04-c-in-deeptutor.md) |  | 2026-07-14 | 分析、C、原子提交、映射 |
| [A 原子化在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/05-a-in-deeptutor.md) |  | 2026-07-14 | 分析、A、原子化、映射 |
| [F 第一性原理在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/06-f-in-deeptutor.md) |  | 2026-07-14 | 分析、F、第一性原理、映射 |
| [V 对抗性审查在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/07-v-in-deeptutor.md) |  | 2026-07-14 | 分析、V、对抗性审查、映射 |
| [七概念组合工作流分析](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/08-combined-workflows.md) |  | 2026-07-14 | 分析、工作流、组合 |
| [分层次阅读路径指南](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/00-reading-guide.md) |  | 2026-07-14 | 学习路径、阅读指南 |
| [实践练习题](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/01-practice-exercises.md) |  | 2026-07-14 | 练习、实践 |
| [学习自检清单](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/02-self-checklist.md) |  | 2026-07-14 | 自检、清单、工具 |
| [延伸阅读与参考资源](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/03-further-reading.md) |  | 2026-07-14 | 延伸阅读、参考、资源 |
| [七概念方法论解析MonkeyCode开源Vibe Coding平台](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/00-overview.md) |  |  | 七概念、MonkeyCode、Vibe Coding、开源、私有化部署、AI编码 |
| [第一章 - 七概念知识框架](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/01-seven-concepts-framework.md) |  |  | 七概念、R-I-E-C-A-F-V、方法论、认知框架 |
| [第二章 - MonkeyCode产品深度解析](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/02-monkeycode-deep-analysis.md) |  |  | MonkeyCode、Vibe Coding、长亭科技、开源、私有化部署、安全审计 |
| [第三章 - 实践操作指南](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/03-practice-guide.md) |  |  | 实践指南、部署教程、MonkeyCode、私有化部署、Docker |
| [第四章 - 常见问题解答（FAQ）](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/04-faq.md) |  |  | FAQ、常见问题、MonkeyCode、故障排查、部署问题 |
| [第五章 - 资源扩展链接](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/05-resources.md) |  |  | 资源链接、MonkeyCode、Vibe Coding、开源项目、私有化部署 |
| [第六章 - 学习效果评估方法](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/06-assessment.md) |  |  | 学习评估、效果检验、知识测试、实践评估、七概念 |
| [第七章 - 附录：七概念应用案例](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/07-seven-concepts-applied.md) |  |  | 七概念应用、实战案例、R-I-E-C-A-F-V、产品分析 |
| [ian-xiaohei-illustrations](learning/05-ai-multimodal-content/ian-xiaohei-illustrations.md) |  |  | - |
| [微软Copilot成本困境与多模型时代产业变革深度分析报告](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/analysis-report.md) |  | 2026-07-09 | AI产业、微软Copilot、DeepSeek、多模型架构、成本分析、产业趋势、开源模型 |
| [cleaned-article](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/cleaned-article.md) |  |  | - |
| [Copilot发展历程与成本困境深度分析](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task2-copilot-analysis.md) |  |  | - |
| [DeepSeek V4技术优势与融资战略深度解析](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task3-deepseek-analysis.md) |  |  | - |
| [多模型时代四家典型产品策略系统对比分析](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task4-multimodel-comparison.md) |  |  | - |
| [从Copilot成本困境看多模型时代产业趋势转变深度洞察](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task5-industry-trends.md) |  |  | - |
| [task6-quality-assessment](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task6-quality-assessment.md) |  | 2026-07-09 | - |
| [个人理解与批判性思考](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task7-personal-insights.md) |  |  | - |
| [理论框架：七概念理论详解](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/01-theory-framework.md) |  | 2026-07-14 | - |
| [事件分析：印度塔塔电子泄密事件详解](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/02-event-analysis.md) |  | 2026-07-14 | - |
| [七概念理论应用指南](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/03-concepts-application.md) |  | 2026-07-14 | - |
| [学习路径与操作指南](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/04-learning-path.md) |  | 2026-07-14 | - |
| [常见问题与注意事项](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/05-faq-notes.md) |  | 2026-07-14 | - |
| [参考资料与附录](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/06-resources.md) |  | 2026-07-14 | - |
| [raw-content](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/raw-content.md) |  |  | - |
| [oray-official-website-core-notes](learning/07-vendor-product-learning/oray/oray-official-website-core-notes.md) |  |  | - |
| [跨文化对抗性审查标准与"反向语义漂移"防御机制](learning/first-principles/chinese-philosophy-parallels/00-cross-cultural-review-protocol.md) |  |  | - |
| [道家哲学核心概念：道、德、自然、无为](learning/first-principles/chinese-philosophy-parallels/01-daoism-core-concepts.md) |  |  | - |
| [儒家思想核心概念：本、体用、格物致知、诚](learning/first-principles/chinese-philosophy-parallels/02-confucianism-core-concepts.md) |  |  | - |
| [墨家方法论核心概念：三表法、类、故、理](learning/first-principles/chinese-philosophy-parallels/03-mohism-core-concepts.md) |  |  | - |
| [佛教因明学核心概念：现量、比量、宗因喻](learning/first-principles/chinese-philosophy-parallels/04-buddhist-logic-core-concepts.md) |  |  | - |
| [跨文化四维比较框架与比较矩阵](learning/first-principles/chinese-philosophy-parallels/05-cross-cultural-comparison-framework.md) |  |  | - |
| [与v1.0西方第一性原理的对比分析：共性、差异、互补与统一框架](learning/first-principles/chinese-philosophy-parallels/06-comparison-with-western-first-principles.md) |  |  | - |
| [跨文化第一性原理思维方法论与操作指南](learning/first-principles/chinese-philosophy-parallels/07-cross-cultural-methodology-framework.md) |  |  | - |
| [跨文化概念对照总表](learning/first-principles/chinese-philosophy-parallels/08-concept-mapping-table.md) |  |  | - |
| [术语统一表](learning/first-principles/chinese-philosophy-parallels/09-terminology-alignment.md) |  |  | - |
| [中西哲学根本性思维发展时间线](learning/first-principles/chinese-philosophy-parallels/10-timeline.md) |  |  | - |
| [来源验证日志](learning/first-principles/chinese-philosophy-parallels/11-source-validation-log.md) |  |  | - |
| [discourse-api-research](operations/discourse-api-research.md) |  |  | - |
| [knowledge-entry-template](templates/knowledge-entry-template.md) |  |  | - |

---

*索引自动生成于 2026-07-14 23:23:55*
