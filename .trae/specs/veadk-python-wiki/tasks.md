# VeADK-Python Wiki 知识库生成 - The Implementation Plan (Decomposed and Prioritized Task List)

> 方法论链路：知识沉淀场景 R→I→E→V（复盘事实采集→洞察本质分析→萃取模式与文档生成→对抗审查质量加固）

## [x] Task 1: R阶段 - 代码库全面扫描与事实清单采集
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 递归扫描 `veadk/` 目录下所有 Python 模块，建立完整的文件/目录结构清单
  - 读取 `pyproject.toml`，梳理所有依赖项和 optional-dependencies 分组
  - 提取每个核心模块（agent.py, runner.py, config.py, agent_builder.py 等）的公开类、方法、函数签名
  - 扫描 `examples/` 目录，建立示例清单（编号、名称、演示功能、核心文件）
  - 读取 `tests/` 目录下的关键测试文件，理解模块预期行为
  - 产出客观事实清单（存放于 supporting-analysis/ 目录），严格遵循 G1 质量门：不含"因为/所以/导致/错误"等因果判断词，纯客观描述
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实清单覆盖 veadk/ 下所有一级子目录（agents/, memory/, knowledgebase/, tools/, cli/, a2a/, cloud/, auth/, models/, configs/, 等）
  - `programmatic` TR-1.2: 核心类 Agent 的所有公开方法（__init__, model_post_init, update_model, load_skills 等）签名被记录
  - `human-judgement` TR-1.3: 事实清单中无因果推断词，纯客观描述（抽查 20 条事实）
  - `programmatic` TR-1.4: examples/ 目录下至少 10 个示例被记录（名称+功能+文件路径）
- **Notes**: 此任务仅采集事实，不做分析或判断；事实清单为后续阶段提供基础素材

## [x] Task 2: R阶段 - 核心模块深度阅读与架构事实采集
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 深度阅读 Agent 类完整实现（agent.py），记录初始化流程、工具挂载机制、回调机制、模型配置逻辑
  - 阅读 Runner 类（runner.py），理解运行时生命周期、会话管理、事件流
  - 阅读 agent_builder.py，理解 Builder 模式实现
  - 阅读 config.py 和 configs/ 目录，理解配置加载机制
  - 阅读 memory/ 模块（short_term_memory.py, long_term_memory.py），理解记忆机制
  - 阅读 knowledgebase/ 模块，理解 RAG 知识库实现
  - 阅读 tools/ 目录，梳理内置工具清单和工具注册机制
  - 补充事实清单中的架构细节
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: Agent.model_post_init 方法的执行流程被客观记录（模型初始化→tracer准备→工具依赖验证→知识库/记忆/技能/回调挂载）
  - `programmatic` TR-2.2: Runner 的公开方法和核心职责被记录
  - `human-judgement` TR-2.3: 架构事实描述准确，与代码逻辑一致（抽查 5 个关键流程）
- **Notes**: 重点关注模块间的协作关系和扩展点设计

## [x] Task 3: I阶段 - 架构洞察与设计模式分析
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 基于事实清单，分析 VeADK 与 Google ADK 的继承关系和扩展方式
  - 识别核心设计模式：继承扩展（Agent 继承 LlmAgent）、插件式工具注册、回调链（before/after_agent_callback, before/after_tool_callback）、Builder 模式、运行时策略模式（runtime="adk"/"codex"/"piagent"）
  - 分析模型配置策略（主模型+fallbacks、ArkLlm vs LiteLlm、Responses API 支持）
  - 分析工具依赖自动补全机制（如 video_generate/video_task_query 配对）
  - 分析技能加载机制（local/cloud/sandbox 三种模式）
  - 产出 ≥5 条核心洞察，每条严格遵循四元组格式：现象描述 + 根因分析（附代码证据行号）+ 影响评估 + 使用建议
  - 通过 G2 质量门：洞察四元组完整
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每条洞察包含完整四元组（现象/根因/影响/建议）
  - `programmatic` TR-3.2: 根因分析引用具体代码文件和行号（至少 3 条洞察有代码引用）
  - `human-judgement` TR-3.3: 洞察有实际指导价值，不是泛泛而谈
- **Notes**: 洞察应回答"为什么这样设计"和"使用时需要注意什么"

## [x] Task 4: I阶段 - 模块依赖关系与扩展点分析
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 分析核心模块间的依赖关系图（Agent→Tools/Memory/KnowledgeBase/Skills/Tracers/Auth）
  - 识别公开扩展点：自定义工具、自定义 RunProcessor（认证/日志/监控）、自定义 Tracer、自定义 PromptManager、自定义记忆后端、自定义知识库后端、A2UI 组件、Tunnel 扩展、Feishu 等 Channel 扩展
  - 分析云部署集成（agentkit、vefaas、ve_cr、ve_apig、ve_tos、ve_identity、ve_tls）
  - 分析 A2A（Agent2Agent）协议实现
  - 补充洞察清单
  - 产出 Mermaid 模块关系图
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-4.1: 扩展点清单完整，覆盖主要自定义场景
  - `programmatic` TR-4.2: Mermaid 图语法正确，可渲染
  - `human-judgement` TR-4.3: 模块依赖关系分析符合代码实际 import 关系
- **Notes**: 此任务为 E 阶段的"扩展开发指南"提供素材

## [x] Task 5: E阶段 - Wiki 目录结构创建与术语表/首页生成
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 创建 Wiki 根目录：`.agents/docs/knowledge/learning/veadk-python/`
  - 创建原子化子目录结构（按模块组织）
  - 生成术语表 glossary.md（≥15 个核心术语，如 Agent、Runner、Tool、Memory、KnowledgeBase、A2A、MCP、Skill、A2UI、LlmAgent、Flow、Callback、Tracer、KnowledgeBase、Session 等），每个术语包含英文原名、中文解释、一句话通俗说明
  - 生成首页 index.md：项目介绍、功能特性、适用场景、文档导航链接、快速链接
  - 所有 Markdown 文件使用正确的 YAML frontmatter（包含 id, title, source 等 MDI 必填字段）
  - 文件名遵循 kebab-case 纯英文规范
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 目录结构创建成功，子目录划分合理（getting-started/, architecture/, modules/, examples/, extensions/, references/）
  - `programmatic` TR-5.2: glossary.md 包含 ≥15 个术语，每个术语有中文解释
  - `programmatic` TR-5.3: 文件名全部为 kebab-case，无中文，运行文件名检查脚本通过
  - `human-judgement` TR-5.4: 首页导航清晰，可快速跳转到各章节
- **Notes**: 参考现有知识库目录格式，遵循格式一致性优先原则

## [x] Task 6: E阶段 - 快速入门与安装配置文档生成
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 生成 getting-started/installation.md：安装方式（PyPI、源码构建）、系统要求、uv 使用说明
  - 生成 getting-started/configuration.md：config.yaml 配置说明（模型配置、API Key 获取、最小配置示例、完整配置参考）
  - 生成 getting-started/quickstart.md：Hello World 示例（从 import Agent 到 asyncio.run 的完整可运行代码）、代码逐行解释、预期输出
  - 生成 getting-started/agentkit-app.md：AgentKit 应用工厂使用指南
  - 代码引用全部使用绝对路径链接
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `human-judgement` TR-6.1: 快速入门步骤清晰，新开发者可按文档在 30 分钟内跑通 Hello World（无需真实 API Key 的部分可先行验证）
  - `programmatic` TR-6.2: 安装命令、配置示例、代码片段与 README.md 和 pyproject.toml 一致
  - `programmatic` TR-6.3: 所有代码引用链接格式正确（file:/// 绝对路径）
- **Notes**: 此部分是 Wiki 访问量最高的内容，必须准确、简洁、可操作

## [x] Task 7: E阶段 - 架构概览文档生成
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 生成 architecture/overview.md：VeADK 整体架构设计、与 Google ADK 的关系、核心组件一览
  - 生成 architecture/agent-lifecycle.md：Agent 初始化流程（model_post_init 逐阶段解析）、运行时流程、事件流
  - 生成 architecture/design-patterns.md：核心设计模式解析（继承扩展、插件注册、回调链、Builder、策略模式）
  - 生成 architecture/module-dependencies.md：模块依赖关系图（Mermaid）、各层职责划分
  - 嵌入 Mermaid 架构图
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-7.1: Mermaid 图表语法正确
  - `human-judgement` TR-7.2: 架构描述与代码实现一致，无臆测内容
  - `human-judgement` TR-7.3: 设计模式分析准确，每个模式有对应的代码位置引用
- **Notes**: 架构文档侧重"为什么这样设计"和"整体如何协作"

## [x] Task 8: E阶段 - Agent 核心模块文档生成
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 生成 modules/agent.md：Agent 类完整 API 参考
    - 类签名与继承关系
    - 所有公开属性列表（name, description, instruction, model_name, tools, sub_agents, knowledgebase, short_term_memory, long_term_memory, tracers, skills, runtime, enable_a2ui, enable_tunnel 等）
    - 核心方法：__init__ 参数说明、model_post_init 初始化流程、update_model、load_skills 等
    - 回调机制说明（before/after_agent_callback, before/after_tool_callback）
    - RunProcessor 扩展点说明
    - 使用示例
  - 生成 modules/runner.md：Runner 类 API 参考
  - 生成 modules/agent-builder.md：AgentBuilder 使用指南
  - 生成 modules/config.md：配置系统详解
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-8.1: Agent 类所有公开方法和属性都有文档覆盖
  - `programmatic` TR-8.2: 方法签名（参数名、类型、默认值）与代码中定义完全一致（抽查 10 个方法）
  - `human-judgement` TR-8.3: 每个核心方法有使用示例片段
- **Notes**: Agent 是最核心的类，此文档必须详尽准确

## [x] Task 9: E阶段 - Memory 与 KnowledgeBase 模块文档生成
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 生成 modules/memory.md：记忆系统详解
    - ShortTermMemory（短期/会话记忆）
    - LongTermMemory（长期/跨会话记忆）
    - 支持的后端（PostgreSQL、MySQL、Redis、Mem0、VikingDB）
    - auto_save_session 自动保存机制
    - 使用示例
  - 生成 modules/knowledgebase.md：知识库（RAG）详解
    - KnowledgeBase 类 API
    - 支持的向量数据库后端（Milvus、OpenSearch、Redis、VikingDB、OpenViking）
    - 文档加载与检索流程
    - enable_profile 查询画像功能
    - 使用示例
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-9.1: 记忆后端列表与 pyproject.toml 中 database/extensions 依赖分组对应
  - `human-judgement` TR-9.2: 知识库使用流程描述清晰
  - `programmatic` TR-9.3: 类和方法签名与代码一致
- **Notes**: 记忆和知识库是 Agent 应用的核心能力

## [x] Task 10: E阶段 - Tools 与 Skills 模块文档生成
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 生成 modules/tools.md：工具系统详解
    - 工具注册机制（直接传 tools 列表 vs 自动挂载）
    - 内置工具清单（knowledgebase load、memory load、video generate/query、ghostchar、a2ui、tunnel 等）
    - 工具依赖自动补全机制
    - 自定义工具开发指南
  - 生成 modules/skills.md：技能系统详解
    - Skills 加载模式（local/skills_sandbox/aio_sandbox）
    - 技能清单机制
    - 动态技能加载
    - SkillsToolset 使用方式
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-10.1: 内置工具清单与 agent.py 中挂载的工具对应
  - `human-judgement` TR-10.2: 自定义工具开发步骤清晰可操作
  - `programmatic` TR-10.3: 技能三种模式与代码中 skills_mode 判断逻辑一致
- **Notes**: 工具扩展是 VeADK 的主要扩展方式之一

## [x] Task 11: E阶段 - CLI 与其他核心模块文档生成
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 生成 modules/cli.md：命令行工具参考（veadk 命令及其子命令：init, create, deploy, web, kb, eval, harness, frontend, update, clean 等）
  - 生成 modules/a2a.md：Agent2Agent (A2A) 协议支持详解
  - 生成 modules/cloud.md：云部署集成（AgentKit、VeFaaS、CR、APIG、TOS、TLS、Identity）
  - 生成 modules/auth.md：认证与凭证服务
  - 生成 modules/models.md：模型配置（ArkLLM、LiteLLM、fallbacks、Responses API）
  - 生成 modules/tracing.md：可观测性与 Tracing（OpenTelemetry、APMPlus、CozeLoop、TLS Exporter）
  - 生成 modules/multimodal.md：多模态能力
  - 生成 modules/prompts.md：Prompt 管理与优化
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-11.1: CLI 子命令列表与 veadk/cli/cli.py 中定义的命令组对应
  - `human-judgement` TR-11.2: 各模块文档描述与代码实现一致（抽查 3 个模块）
- **Notes**: 按模块重要性排序，CLI 和 A2A 优先级较高

## [x] Task 12: E阶段 - 示例代码解析文档生成
- **Priority**: medium
- **Depends On**: Task 8, Task 9, Task 10
- **Description**: 
  - 生成 examples/quickstart.md：01_quickstart 示例解析（最小 Agent）
  - 生成 examples/custom-tools.md：02_custom_tools 示例解析（自定义工具）
  - 生成 examples/memory.md：03_short_term_memory 和 09_long_term_memory 示例解析
  - 生成 examples/knowledgebase.md：05_knowledgebase_rag 示例解析
  - 生成 examples/multi-agent.md：06_multi_agent 示例解析（多智能体协作）
  - 生成 examples/structured-output.md：07_structured_output 示例解析
  - 生成 examples/model-config.md：08_model_config 示例解析
  - 生成 examples/a2ui.md：a2ui_agent 示例解析（Agent 驱动 UI）
  - 生成 examples/tracing.md：11_tracing 示例解析
  - 每个示例解析包含：示例功能介绍、核心代码展示、关键代码行解释、运行前置条件、预期效果
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-12.1: 至少覆盖 8 个代表性示例
  - `human-judgement` TR-12.2: 示例解释准确，关键代码行的解释能帮助理解 VeADK 的使用方式
- **Notes**: 示例是最好的学习材料，解析应侧重"这个示例演示了什么"和"关键代码为什么这样写"

## [x] Task 13: E阶段 - 扩展开发指南与 FAQ 生成
- **Priority**: medium
- **Depends On**: Task 10, Task 11
- **Description**: 
  - 生成 extensions/custom-tool.md：自定义工具开发完整指南（步骤、代码模板、最佳实践）
  - 生成 extensions/custom-extension.md：自定义 Extension 开发（参考 feishu_channel.py）
  - 生成 extensions/custom-run-processor.md：自定义 RunProcessor 开发（认证、日志、监控场景）
  - 生成 extensions/cloud-integration.md：云服务集成说明
  - 生成 faq/best-practices.md：最佳实践与常见反模式（基于洞察阶段的分析）
  - 生成 faq/troubleshooting.md：常见问题排查（API Key 配置、模型连接、依赖安装等）
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `human-judgement` TR-13.1: 扩展开发步骤清晰，有完整代码模板
  - `human-judgement` TR-13.2: 反模式列表有实际指导价值（基于代码分析，如 skills_mode='local' 已弃用等）
- **Notes**: 扩展指南面向希望深度定制 VeADK 的开发者

## [x] Task 14: E阶段 - 交叉引用修复与导航索引更新
- **Priority**: medium
- **Depends On**: Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13
- **Description**: 
  - 更新首页 index.md 的导航链接，确保所有文档可被索引
  - 检查并修复所有文档间的交叉引用（相对路径正确）
  - 为每个模块文档添加"相关资源"和"示例参考"链接
  - 生成 references/api-index.md：所有公开类/函数的快速索引表（类名→所在文件→文档链接）
  - 更新 glossary.md 中术语到对应章节的链接
  - 通过 docgen 或手动方式确保导航完整性
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-14.1: 首页导航链接覆盖所有生成的文档
  - `human-judgement` TR-14.2: 文档间交叉引用可跳转（抽查 20 个链接）
  - `programmatic` TR-14.3: 运行链接检查脚本，无内部断链
- **Notes**: 导航性是 Wiki 可用性的关键

## [x] Task 15: V阶段 - 对抗审查（多视角质量验证）
- **Priority**: high
- **Depends On**: Task 14
- **Description**: 
  - 从四个视角对完整 Wiki 进行对抗审查：
    - 🔴 **魔鬼代言人（逻辑攻击）**：寻找文档中的逻辑矛盾、遗漏的边界情况、错误的因果推断
    - 🔵 **新手开发者（可读性攻击）**：以刚接触 VeADK 的 Python 开发者视角，寻找看不懂的术语、缺少前置知识的跳跃、步骤缺失
    - 🟡 **成本敏感 CTO（ROI 攻击）**：评估文档完整性——是否有重要模块遗漏？是否花了过多篇幅在次要功能上？ROI 如何？
    - 🟢 **学术研究员（准确性攻击）**：抽查类/函数签名与实际代码的一致性、API 描述的准确性、代码示例的正确性
  - 每个视角产出 ≥3 条具体审查意见，总计 ≥10 条
  - 100% 修正 🔴 关键问题，≥30% 修正 🟡 问题
  - 记录审查意见和修正情况
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `human-judgement` TR-15.1: 每个视角至少 3 条具体审查意见（非"写得很好"类客套话）
  - `programmatic` TR-15.2: 至少抽查 20 个类/函数签名与代码对比，准确率 ≥95%
  - `human-judgement` TR-15.3: 关键问题（逻辑错误、签名错误）100% 修正
  - `human-judgement` TR-15.4: 新手视角审查后，快速入门部分可无前置知识理解
- **Notes**: V 阶段是质量保障的关键，不允许跳过

## [x] Task 16: V阶段 - 最终格式规范验证与收尾
- **Priority**: high
- **Depends On**: Task 15
- **Description**: 
  - 运行文件名规范检查脚本，确保所有文件名符合 kebab-case 纯英文
  - 检查所有 Markdown 文件的 frontmatter 完整性（id, title, source 等必填字段）
  - 运行链接检查，修复所有内部断链
  - 检查代码引用格式一致性（file:/// 绝对路径）
  - 检查术语表链接完整性
  - 产出最终交付物清单
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-16.1: 文件名检查脚本通过，无违规文件名
  - `programmatic` TR-16.2: frontmatter 检查通过，所有文件有正确的 YAML 头部
  - `programmatic` TR-16.3: 链接检查通过，无内部断链
  - `human-judgement` TR-16.4: 整体 Wiki 风格一致，术语统一
- **Notes**: 这是交付前的最后一道质量门

## 任务依赖关系图

```
Task 1 ──→ Task 2 ──→ Task 3 ──→ Task 4 ──┬──→ Task 5 ──→ Task 6 ──┐
                                            ├──→ Task 7 ──┘
                                            ├──→ Task 8
                                            ├──→ Task 9
                                            ├──→ Task 10
                                            ├──→ Task 11
                                            └──→ ...
```

- R 阶段（Task 1-2）：事实采集，串行
- I 阶段（Task 3-4）：洞察分析，串行
- E 阶段（Task 5-13）：文档生成，Task 5 先完成，Task 6-13 在 Task 5 完成后可部分并行（模块文档间相对独立），Task 14 依赖所有 E 阶段任务完成
- V 阶段（Task 15-16）：审查收尾，串行
