---
id: "retrospective-reports-index"
title: "复盘报告分类索引"
x-toml-ref: "../../../../.meta/toml/.agents/docs/retrospective/reports/README.toml"
---
# 复盘报告分类索引

> 本文档为 `docs/retrospective/reports/` 目录下全部复盘报告的完整分类索引，提供按主题、日期、关键词和报告类型的多维度快速查找功能。

## 一、分类标准

复盘报告按内容主题划分为 20 个一级分类，各分类的定义与边界如下：

| 分类目录 | 主题 | 定义与边界 |
|---|---|---|
| `atomization/` | 原子化与文档重构 | 内容拆分、模块化、README 原子化、复盘文档重构、角色协作场景迁移、子代理提取。关注"如何将大型文档拆解为可维护的原子化单元"的方法论与实践。 |
| `insight-extraction/` | 洞察与萃取 | 知识发现、方法论提炼、优化循环、跨项目元分析、README 演进分析、独立洞察卡片。关注"从已有实践中提取可复用知识与模式"的过程与成果。 |
| `spec-system/` | 规范体系建设 | Agents Spec System、规范一致性检查、成熟度标准创建、模式自动化与闭合、事实表述修正、文件命名规范、Vendor子模块协同。关注"规范体系的建设、验证与自我演化"的系统工程。 |
| `roles-teams/` | 角色与团队管理 | co-founder 角色标记与改进执行、团队管理模块创建。关注"多智能体协作体系中角色定义与团队治理"的组织设计。 |
| `project-governance/` | 项目治理 | 应用目录创建、系统规划、Code Wiki 生成、建议执行与模式导入、工具熵优化、导出卡片、报告重复优化、Skill门面化与编码鲁棒性、Agent Skills开放标准采用。关注"项目整体层面的架构决策、流程优化与质量保障"的治理实践。 |
| `competitive-analysis/` | 竞品分析 | 外部赛事设计分析、竞品策略洞察、增长模型研究、产品学习与技术分析、开源项目Wiki学习。关注"对外部产品/赛事/活动/开源项目的结构性分析，提炼可借鉴策略与风险信号"的竞争情报实践。 |
| `knowledge-content/` | 知识内容建设 | Agent通信协议、技术Wiki等知识库内容的创建与原子化教程。关注"技术知识体系化建设与结构化交付"的内容工程实践。 |
| `standards-tools/` | 标准与工具评估 | Markdown语法标准（MyST）、规范迁移可行性、工具链技术评估。关注"外部标准与工具在Agent Spec开发中的可迁移性评估与决策支持"。 |
| `incident-reports/` | 事件复盘 | 针对明确失败事件、目标未达成、决策错误、流程断裂或方法论错配的 incident 复盘。关注"发生了什么、为什么出错、如何避免再次发生"的事件级闭环。 |
| `project-reports/` | 项目级独立报告 | 以单文件 Markdown 形式交付的完整复盘报告（非原子化子目录结构），以及独立的项目结项复盘、规范度量批量报告。关注"简洁交付的项目级总结"。 |
| `task-reports/` | 任务执行复盘 | 单任务执行过程的完整复盘报告，包含Spec Mode流程回顾、问题处理、经验沉淀。关注"单次任务执行的全过程复盘与可复用模式提取"。 |
| `iteration-reports/` | 迭代复盘 | 迭代/阶段级别的完整复盘报告，包含 Spec 模式七阶段工作流、系统性验证、PARTIAL 修复闭环。关注"迭代/阶段交付的全过程复盘与质量保障机制验证"。 |
| `documentation-governance/` | 文档治理 | Sphinx/MyST 文档工程治理、toctree 目录树完整性、index.md 结构规范、文档构建警告治理、invocations 构建封装。关注"文档体系的导航结构与构建质量保障"的工程实践。 |
| `adversarial-reviews/` | 对抗审查 | 对抗性评审产出（魔鬼代言人/新人/老板/未来四视角攻击记录），对方案、报告与决策的多视角证伪加固。关注"通过对抗审查暴露方案盲区与隐含假设"的验证实践。 |
| `bug-fix/` | 故障修复 | 具体故障/缺陷的根因分析与修复复盘，含工具增强、Docker 构建修复、PyTorch 集成等。关注"Bug 定位→修复→预防→闭环"的问题处置实践。 |
| `bugfix/` | 修复类复盘 | 修复类复盘报告（CI 质量门、Docker entrypoint、TVM/LLVM 符号可见性、VTA 硬编码等）。与 `bug-fix/` 同属修复域，历史命名差异保留。 |
| `build-engineering/` | 构建工程 | Docker/DevContainer 镜像构建、conda 环境、Nuitka 编译、CMake 工程、发布流水线、构建性能优化。关注"构建/打包/发布环节的工程实践与质量保障"。 |
| `code-optimization/` | 代码优化 | 算子优化、性能调优、FFI 边界重构、内存零拷贝、精度修正、代码库提取。关注"运行时性能与代码质量的双重优化实践"。 |
| `environment-setup/` | 环境搭建 | WSL/Docker/GPU 环境配置、系统级环境迁移、桌面/系统设置修复、conda free-threading 环境。关注"开发环境与系统环境的搭建与排障"。 |
| `feature-development/` | 功能开发 | 新功能开发完整复盘（如 CaffeProto L2Norm 算子、Skill 自动加载器）。关注"从需求到交付的功能开发全流程"。 |

## 二、报告清单

### atomization/（13 份）

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-atomization-execution-s1-7-20260624/` | 原子化执行复盘（S1-S7），覆盖完整执行链路的阶段划分与经验总结 |
| `retrospective-atomization-modularization-comprehensive-report-20260623/` | 原子化模块化综合报告，横切与纵切双阶段加工策略的完整实践 |
| `retrospective-meta-atomization-full-chain-20260624/` | 全链元级原子化复盘，对原子化过程自身的元级反思 |
| `retrospective-report-readme-atomization/` | README.md 原子化拆分复盘，含三要素模型与收益递减曲线 |
| `retrospective-report-reports-atomization-comprehensive-20260624/` | reports/ 目录全面原子化复盘，含 81 处断链修复、路径深度规则、三层验证模型 |
| `retrospective-report-refactor-retrospective-docs/` | 复盘文档体系重构，含三层架构模型与原子性判断标准 |
| `retrospective-report-readme-collab-scenario-migration/` | 角色协作场景迁移，含内容迁移工作流模式 |
| `retrospective-report-readme-subagent-extraction/` | 子代理提取复盘，含提取任务三段式方法论 |
| `retrospective-entry-detail-migration-20260624/` | 入口文件去技术细节与体系深化，含入口-容器分离原则 |
| `retrospective-report-atomization-structure-optimization-20260624/` | atomization 目录结构系统性优化复盘，四阶段渐进式重构消除三层冗余（源.md重复/project-overview重叠/连接器重复），文件总数减少32%、溯源链从3层缩短至2层 |
| `retrospective-meta-atomization-ian-xiaohei-insights-20260625/` | insight-extraction.md 原子化归档元级复盘，7项洞察→7个模式文件原子化，信息增殖257%、三级分类决策、批次去重审核等5项核心发现 |
| `retrospective-large-file-atomization-batch-20260703/` | 大规模批量文件原子化拆分复盘，14个大文件模块化，三段式拆分架构验证，原子提交三查法萃取 |
| `retrospective-full-lifecycle-report-atomization-20260705/` | 全生命周期复盘报告原子化重构：execution时间二分+L3报告概览详情分离两种模式验证，2大文件精简55%，"概览表+详情文件"模式升级为L2 |

### insight-extraction/（38 份原子化报告 + 5 份独立洞察卡片）

按内容主题划分为 4 个子目录 + 1 个独立洞察卡片目录：

#### meta-methodology/（13 份）— 元方法论与复盘体系自省

关于知识管理体系本身的方法论、跨项目元分析、文档规范治理、优化循环模式与执行闭环验证。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `meta-methodology/retrospective-insight-extraction-comprehensive-20260623/` | 洞察萃取综合报告，系统化萃取方法论与可复用模式 |
| `meta-methodology/retrospective-insight-create-apps-directory-meta-analysis/` | 单项目全流程协作元洞察，分析从需求到交付的完整协作链路 |
| `meta-methodology/retrospective-insight-optimization-cycle/` | 优化循环洞察报告，从 45 个原子提交中提取六大元模式 |
| `meta-methodology/retrospective-insight-extraction-worlds-collaboration-environment/` | 世界协作环境洞察，分析多智能体并行执行的组织模式 |
| `meta-methodology/retrospective-meta-analysis-cross-project/` | 跨项目元分析报告，含高频模式识别与演化趋势分析 |
| `meta-methodology/retrospective-report-insight-execution/` | 洞察→执行闭环复盘，验证 5 项行动建议全部落地执行 |
| `meta-methodology/retrospective-report-insight-opportunities-implementation/` | 洞察机会实施复盘，含五类资产覆盖原则的实践验证 |
| `meta-methodology/retrospective-session-insight-extraction-readme-evolution-20260624/` | README 演进洞察（10 轮会话分析），追踪 README 文档的长期演化轨迹 |
| `meta-methodology/retrospective-comprehensive-extraction-20260626/` | SpecWeave 项目全面萃取报告，系统性盘点全部知识资产 |
| `meta-methodology/retrospective-xinet-chaos-multiproject-analysis-20260625/` | xinet 混沌多项目聚合目录复盘洞察，37个嵌套Git仓库的结构勘察 |
| `meta-methodology/retrospective-frontmatter-metadata-unification-20260702/` | MyST学习与Frontmatter元数据规范统一迁移复盘，150+文件批量迁移 |
| `meta-methodology/retrospective-export-suggestions-execution-20260702/` | 导出建议执行复盘：验证优先执行、过度抽象判断、规范沉淀优于checklist |
| `meta-methodology/retrospective-directory-theme-reorganization-20260703/` | insight-extraction目录主题划分复盘：30+报告重组为4个主题子目录，211文件路径更新，Rename-Update冲突解决 |

#### external-learning/（19 份）— 外部开源项目与技术文章学习

对外部优秀开源项目、竞品、技术文章的分析与学习复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/` | 竹简悟道 Specs 文档体系深度分析，含文档五层架构、洞察两档结构等 9 个核心元洞察 |
| `external-learning/retrospective-deer-flow-2-learning-20260625/` | DeerFlow 2.0 学习复盘，含 Super Agent Harness 架构范式、Markdown Skills 系统等 4 个可复用架构模式 |
| `external-learning/retrospective-ai-code-assistant-project-analysis-20260625/` | AI 编程学习助手项目代码分析，含 AI 应用 MVP 最小架构、提示词分层设计等模式萃取 |
| `external-learning/retrospective-firecrawl-learning-20260629/` | Firecrawl 系统学习复盘：AI 网页数据接口的技术架构、商业模式与战略洞察 |
| `external-learning/retrospective-architecture-priority-20260629/` | 架构优先级评估与重构路线图：基于 Firecrawl 8 洞察 |
| `external-learning/retrospective-skills-article-learning-20260629/` | Skills 技术文章学习复盘，含Agent知识喂给范式演进等5项核心洞察 |
| `external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/` | Vibe Coding两大神级Prompt学习分析复盘：第一性原理+对抗式审查闭环逻辑、微信公众号文章defuddle提取降级链、Task 1+2合并委派策略、7个核心洞察+4个可复用模式 |
| `external-learning/retrospective-agency-deep-learning-analysis-20260706/` | Agency Agents 深度学习技术研究与分析复盘，含原子化设计原则、配置驱动开发、组合模式优于继承等4个核心洞察，AI Engineer与GeoAI/ML Engineer两个Agent文件更新 |
| `external-learning/retrospective-volcengine-mobile-use-agent-learning-20260707/` | 火山引擎Mobile Use Agent学习复盘：Web内容提取工具降级链、学习类wiki双产出结构、短指令模式第5次验证 |
| `external-learning/retrospective-volcengine-cua-learning-20260707/` | 火山引擎Computer Use Agent学习复盘：Spec模式深度分析工作流验证、子代理委派分而治之、UI自动化三代范式演进、7个核心洞察+4个可复用模式 |
| `external-learning/retrospective-volcengine-mua-skill-api-guide-20260707/` | 火山引擎MUA Skill与API技术实现指南复盘：产品概览→技术实现双层文档结构、多URL提取内容聚合、Spec主题选择决策、6个核心洞察+5个可复用模式 |
| `external-learning/retrospective-bonsai-canvas-agent-analysis-20260707/` | BonsAI无限画布+Agent协作工具深度分析，含可视化Agent编排、无限画布知识图谱、上下文流式传输等架构洞察 |
| `external-learning/retrospective-deep-code-analysis-20260707/` | Deep Code编程知识自动化提取引擎分析，含静态分析+大模型双路架构、知识三元组抽取等技术洞察 |
| `external-learning/retrospective-karpathy-agent-fallacy-20260707/` | Andrej Karpathy「Agent谬误」文章分析，含vibe coding批判、上下文窗口工程、Agent组合而非单体等核心观点 |
| `external-learning/retrospective-linus-fireside-chat-20260707/` | Linus Torvalds炉边谈话项目管理智慧分析，含维护者责任、代码品味、社区治理等管理洞察 |
| `external-learning/retrospective-md2card-indie-dev-20260707/` | MD2Card独立开发者公众号深度分析，含P0-P2三级改进方案、SpecWeave对比分析 |
| `external-learning/retrospective-skillopt-analysis-20260707/` | SkillOpt技能自动优化框架分析，含技能自我优化闭环、A/B测试评估、进化算法搜索等技术洞察 |
| `external-learning/retrospective-tutti-analysis-20260707/` | Tutti多智能体协作工作空间分析，含共享白板、多Agent实时协作、Artifact中心化设计等架构模式 |
| `external-learning/retrospective-first-principles-comprehensive-research-20260709/` | 第一性原理全面资料搜集与系统化归档：哲学起源+物理学应用+商业创新案例跨领域知识档案，验证对抗性审查协议、知识档案四层架构、可信度双轨制3个L2方法论模式，77.3%一级来源、78.5% A级可信度 |

#### iot-ecosystem/（9 份）— IoT 智能家居生态

TuyaOpen、Home Assistant 全系列（官方/第三方/Core/集成）、IPC 规格等 IoT 生态相关复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `iot-ecosystem/retrospective-tuyaopen-analysis-20260630/` | TuyaOpen 开源 IoT SDK 深度分析，含四层架构模型、TAL/TKL 双层抽象等 4 个可复用模式 |
| `iot-ecosystem/retrospective-tuyaopen-folder-20260630/` | TuyaOpen 目录全链路复盘：export.* + tos.py 统一入口、非交互构建约束 |
| `iot-ecosystem/retrospective-tuya-home-assistant-learning-20260630/` | Tuya HA 集成学习复盘（已废弃），含分层文档体系、设备分类矩阵等 4 个核心模式 |
| `iot-ecosystem/retrospective-smart-life-learning-20260630/` | Smart Life HA 集成学习复盘（已废弃），含二维码授权模式、实体基类统一等 4 个核心模式 |
| `iot-ecosystem/retrospective-home-assistant-tuya-official-20260630/` | HA 官方 Tuya 集成分析（当前官方方案），含官方集成标准化模式等 3 个核心模式 + 4 个代码级模式 |
| `iot-ecosystem/retrospective-home-assistant-integration-20260630/` | HA 智能家居系统集成模块复盘，含可选模块设计模式、dry-run 安全机制等 4 个核心模式 |
| `iot-ecosystem/retrospective-home-assistant-core-analysis-20260630/` | Home Assistant Core 源码复盘：启动链路、分阶段集成加载、装配并发去重 |
| `iot-ecosystem/retrospective-tuya-ipc-spec-and-xlsx-learning-20260701/` | Tuya IPC 规格落地 + Excel 测试报告学习，含规格前置知识交付等 5 条可复用洞察 |
| `iot-ecosystem/retrospective-tuya-projects-for-xlsx-agentization-20260701/` | Tuya 项目 XLSX Agent 化改造，含发布门控测试报告 |

#### toolchain-dev/（3 份）— 内部工具链与开发环境

XMNPU 工具链相关的开发环境构建、权限修复等复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `toolchain-dev/retrospective-xmnn-folder-20260701/` | XMNN 目录复盘：Nuitka 预编译 wheel + 离线交付结构审计，install-only 打包模式 |
| `toolchain-dev/retrospective-llvm-dev-env-and-build-20260702/` | LLVM Dev 环境与构建任务复盘：clang→gcc 构建策略、去版本号命名重构、镜像链路闭合 |
| `toolchain-dev/retrospective-llvm-dev-mount-permission-fix-20260702/` | LLVM Dev 挂载权限修复复盘：绑定挂载零漂移、非 root 权限验证、工具泛化与兼容迁移 |

#### standalone/（独立洞察卡片 + 原子化补充目录）

独立洞察卡片（单文件形式，不属于特定原子化报告），以及少量以子目录形式补充的专题化原子报告入口。

| 文件 | 简要说明 |
|---|---|
| `standalone/insight-temp-file-discipline-20260701.md` | 临时文件路径规范执行卡点洞察 |
| `standalone/insight-tuyaopen-folder-20260630.md` | TuyaOpen 目录洞察报告 |
| `standalone/insight-windows-git-encoding-20260701.md` | Windows Git 非 ASCII 提交信息编码陷阱洞察 |
| `standalone/insight-dockerfile-caching-20260703.md` | Dockerfile 层缓存与开发环境镜像构建七条深层洞察 |
| `standalone/first-principles-learning-mode/` | 学习模式第一性原理分析原子化报告目录入口，收录按章节拆分的专题分析 |
| `retrospective-myst-unified-ecosystem-phase1-20260705/` | MyST统一化生态体系阶段1核心洞察索引：3洞察+4经验+3问题+2模式+4机会+4行动项，可复用知识库检索入口 |

### spec-system/（10 份）

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-report-agents-spec-system/` | 智能体开发规范体系项目复盘（初版），含 Spec-driven 流程与并行子代理模式验证 |
| `retrospective-report-agents-spec-system-comprehensive/` | 智能体开发规范体系全面复盘（深度版），含方法论萃取与行动指南 |
| `retrospective-report-check-spec-consistency/` | 规格文档一致性检查工具复盘，含三段式检查工具架构 |
| `retrospective-report-maturity-standard-creation/` | 成熟度标准创建复盘，含 L1-L4 量化标准定义 |
| `retrospective-report-pattern-maturity-automation-closure/` | 模式成熟度自动化闭合复盘，含自动化扫描与升级规则 |
| `retrospective-report-fact-statement-correction/` | 事实表述修正复盘，含事实表述一致性闭环方法论 |
| `retrospective-report-file-naming-convention/` | 文件命名规范复盘，含目录命名决策矩阵与实施验证 |
| `retrospective-report-specs-theme-task-board-system-20260626/` | Specs 主题任务看板体系构建复盘，含三层看板架构（全局看板+主题看板+主题模板）、看-管-建三动作模型、递进式需求澄清策略、Mermaid 分层可视化、模板收尾自维护闭环 4 个可复用模式 |
| `retrospective-vendor-submodule-collaboration-20260629/` | Vendor外部子模块协同框架复盘，flexloop git submodule协同集成框架建立，三区域边界划分、固定commit锁定、repo-check.py vendor --deep自动化验证、pytest路径隔离、4步子模块更新机制、VENDOR-INTEGRATION.md协同操作指南（10章），13文件+1249行交付 |
| `retrospective-universal-prd-template-extraction-20260709/` | 通用PRD/项目Spec模板萃取项目复盘，第一性原理提炼+Dogfooding自验证，萃取第一性原理模板提炼法、Dogfooding自验证法、规范双轨制、规范四要素模型4个可复用模式，13文件2804行交付，双格式Spec规范体系建成 |

### roles-teams/（3 份）

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-report-cofounder-improvement-execution/` | 联合创始改进建议执行复盘，含声明即校验模式与知识形态三阶跃迁 |
| `retrospective-report-cofounder-role-marker/` | 联合创始角色特殊标记复盘，含零侵入扩展范式与双点一致原则 |
| `retrospective-report-teams-module/` | 团队管理模块创建复盘，含约定驱动创建、规范层纵深防御、自举规范 |

### project-governance/（37 份 + 1 独立报告）

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-daily-20260629-full-day/` | **2026-06-29单日全面复盘**（元复盘）：71次提交/41279行净增/7大主题全景，含五波次时间线、治理四层递进模型、二次暴露治理闭环、波次式工作日节奏等5个元洞察 |
| `retrospective-session-agents-md-violation-20260624/` | AGENTS.md 启动协议违反复盘，含系统级提示与项目级协议的优先级竞争分析、表层修正循环诊断、多 Skill 执行路径竞争机制 |
| `retrospective-report-create-apps-directory/` | apps/ 应用开发工作空间创建复盘，含双区开发模型 |
| `retrospective-report-system-planning/` | README 系统规划章节新增复盘，含四层闭环架构洞察 |
| `retrospective-report-code-wiki-generation/` | Code Wiki 生成任务复盘，含知识库自动化构建实践 |
| `retrospective-report-suggestion-execution-and-pattern-import/` | 建议执行与模式导入复盘，含外部建议的评估、采纳与内化流程 |
| `retrospective-report-tool-entropy-nonlinear-optimization/` | 工具熵非线性优化复盘，含自动化规模不经济规律与优化策略 |
| `retrospective-report-four-topic-structure-optimization-20260624/` | 复盘报告四主题结构优化推广复盘，24个project-overview合并、23个连接器删除 |
| `retrospective-export-20260623/` | 导出卡片，知识资产的清单化导出与复用指南 |
| `retrospective-comprehensive-20260623/` | 综合复盘系列（6 子模块），覆盖 S1-S7 全阶段的多维度综合复盘 |
| `retrospective-readme-sync-and-brand-naming-20260624/` | README 同步与 SpecWeave 品牌命名复盘，含数据一致性修复与品牌定位升级 |
| `retrospective-project-comprehensive-20260625/` | **项目级全面复盘**：400 文件规模统计、3 天演进时间线、5 大核心发现（自指涉方法论/临界质量效应/复盘加速效应/规范自举/定位漂移修正）、8 条改进建议与战略路线图 |
| `retrospective-specweave-demo-production-flow-20260625/` | SpecWeave Demo 制作流程探索复盘，含 70% 完成度判断、资产盘点表、差距分析、3 项关键决策、5 步制作流程、HTML 交互增强清单、自指涉证据闭环三层模型 |
| `retrospective-zhujian-wudao-apps-archiving-20260625/` | 竹简悟道参赛作品归档至 apps/ 复盘，含选择性归档模式、自包含验证前置模式、工作流协议骨架与门禁分离原则、参赛作品归档 5 步法方法论 |
| `retrospective-xinet-content-extraction-archiving-20260625/` | xinet 目录系统性内容萃取与归档复盘，54151文件扫描分类 |
| `retrospective-insights-reorg-20260626/` | 竹简悟道洞察库重组复盘，含四层结构拆分法、交叉引用更新三步法、结构债务渐进积累模式、标题层级健康度指标 4 条可复用洞察 |
| `retrospective-mermaid-rendering-fix-20260626/` | Mermaid 渲染兼容性问题修复复盘，含 subgraph 空行解析问题、节点文本隐式 Markdown 解析、特殊字符引号保护规则 |
| `retrospective-link-fix-depth-adjustment-20260626/` | **断链修复与链接自动校正工具增强复盘**：14个断链根因分析、相对路径深度自动校正算法、修复优先级链设计、dry-run安全修改模式、3个可复用模式（路径层级校正/修复优先级链/dry-run优先），含CI集成与看板自动生成行动计划 |
| `retrospective-scripts-shared-lib-extraction-20260626/` | 检查脚本共享库提取复盘，重复发现、重构bug发现、概念域分离、Powershell编码陷阱 |
| `retrospective-report-document-dedup-insights-20260626/` | 文档去重洞察复盘，识别报告体系重复内容来源与优化策略 |
| `retrospective-specweave-full-project-comprehensive-20260626/` | **SpecWeave 项目结项全面复盘**（10章标准版）：229次提交/29个Spec全闭环/796文档/46模式/4天完整历程，含六阶段时间线、十大关键决策、六类问题深度分析、五维雷达评分（9.4/10）、AI协作规范体系构建11步方法论、10大成功要素、5大认知升级、短/中/长期战略路线图 |
| `retrospective-mermaid-rendering-regression-20260629/` | Mermaid渲染回归治理失效复盘，识别规范落地断裂、工具覆盖盲区、点修复偏误 |
| `retrospective-mermaid-governance-closure-20260629/` | Mermaid治理闭环执行复盘，安全模板、注释感知修复、一站式操作指南，治理成熟度L3 |
| `retrospective-test-plan-and-atomic-commit-20260629/` | 测试计划与原子提交复盘 |
| `retrospective-forum-bot-logging-20260629/` | 论坛自动化脚本开发与日志增强复盘 |
| `retrospective-forum-posting-skill-optimization-20260629/` | 论坛发帖Skill优化复盘，含五要素模型、三层路由任务预检、可用性启发式结构守卫等6个元洞察 |
| `retrospective-forum-automation-full-workflow-20260629/` | 论坛自动化全流程复盘，含发帖、编辑、回复等场景的完整自动化实践 |
| `retrospective-vendor-flexloop-governance-adjustment-20260629/` | flexloop子模块从第三方只读升级为自有协作模式复盘，建立双模式子模块治理框架，萃取5个可复用模式 |
| `retrospective-stage-guardrails-logging-20260629/` | 阶段守卫机制落地复盘，提取3个可复用模式（流程合规治理） |
| `retrospective-ai-agent-data-security-governance-20260629/` | AI智能体互联数据安全治理体系建设复盘，五层架构10份规则文档交付（流程合规治理） |
| `retrospective-raci-governance-matrix-20260629/` | RACI治理责任矩阵落地复盘，5个指令集69行RACI标准化，五层审批模型修正（流程合规治理） |
| `retrospective-daily-review-and-forum-posting-20260630/` | 2026-06-29全日复盘+论坛跟帖发布任务复盘，Ember composer框架感知操作、同名按钮消歧、SPA自动化模式萃取、4个可复用模式、3个元洞察 |
| `retrospective-git-local-clone-bug-20260701/` | Windows 本地路径 `git clone` 触发 Git refs 事务内部异常（`BUG: refs/files-backend.c:3174`），沉淀最小破坏处置协议与 `--no-local` 规避路径 |
| `retrospective-short-command-context-rehydration-20260701/` | 短指令在新会话中的上下文重建与参数澄清复盘，沉淀“对象/交付”二槽位与跨会话澄清守则 |
| `retrospective-skill-facades-encoding-robustness-20260701/` | Skill命令门面化与编码鲁棒性修复复盘，5个高频脚本Skill化封装、50+单元测试、28个性能基准、6个Windows编码边界问题修复，防御性属性访问L2模式萃取 |
| `agent-skills-standards-adoption-20260702/` | Agent Skills开放标准采用复盘，wiki v1.2（15章原子化）+13技能合规检查100%通过+CI集成+60个evals测试用例+Gotchas章节全覆盖，Learn-Validate-Adopt治理模式沉淀 |
| `retrospective-risk-interceptor-logging-fix-20260728/` | 风险拦截器日志测试与跨平台兼容性修复复盘：-vv白盒测试发现4项逻辑缺陷+Windows三生态5种危险模式+编码回退链+format正则修复，11项问题修复+2条开发标准落地，萃取默认静默日志架构、严重度平方加权、展示层二元组去重、跨Shell危险命令检测、多编码回退链、首Bug主动闭环6个候选模式 |
| `reports-duplication-optimization-report.md` | 复盘报告体系重复内容优化报告（独立报告，无对应目录） |

### competitive-analysis/（52 份）

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-trae-contest-faq-analysis-20260624/` | TRAE AI 创造力大赛 FAQ 复盘，含 SWOT 分析、AARRR 体验链路、5 项风险识别与增长战略洞察 |
| `retrospective-specweave-contest-advantage-analysis-20260624/` | 竹简悟道 + SpecWeave 双作品参赛策略分析（v12），含 15 项优势/洞察、双作品策略、全流程行动清单、SpecWeave 报名帖草稿 |
| `retrospective-trae-contest-demo-generation-learning-20260625/` | TRAE AI 创造力大赛·产品 Demo 生成学习资料复盘，含飞书文档动态加载特性、TRAE 产品定位演进、参赛 5 步法与 SpecWeave 方法论映射、多源情报迭代法第 3 次验证 |
| `retrospective-trae-contest-preliminary-guide-learning-20260625/` | TRAE AI 创造力大赛·初赛参赛指南学习复盘，含人气分计算公式（评论×2 权重）、Session ID 获取方式、信息源消化成熟度模型、SSR vs CSR 工具选择判断 |
| `retrospective-ian-xiaohei-illustrations-learning-20260625/` | Ian Xiaohei Illustrations 开源 AI Skill 学习复盘，含认知锚点可视化、角色驱动设计系统、风格克制力量、原子化视觉思维、AI Skill 三层价值模型 5 洞察 + 5 可复用模式 |
| `retrospective-ian-xiaohei-source-analysis-20260625/` | Ian Xiaohei Illustrations 仓库源码深度分析综合报告，35个文件完整源码架构解析，7项架构/方法论模式萃取，双接口仓库设计、渐进式上下文披露、输出行为规约等可复用模式 |
| `retrospective-claude-tag-article-learning-20260629/` | Claude Tag 文章学习·知识捕获复盘，含团队共享 AI 同事模式、Ambient Mode 主动介入、异步执行 Agent 化、企业统一入口战略、权限隔离多身份 5 洞察 + 3 可复用模式（Invoke-WebRequest 获取法、索引截取兜底、团队共享 AI 模式） |
| `retrospective-specforge-insight-20260629/` | SpecForge 竞品洞察复盘：TRAE社区精华帖《SpecForge：让不懂代码的人也能用AI做出完整项目》分析，13个Skill全流程分享，提炼可借鉴的设计模式与SpecWeave差异化定位 |
| `retrospective-tuyaopen-dev-skills-learning-20260630/` | TuyaOpen-dev-skills 仓库学习复盘（复盘+洞察+萃取+导出）：聚焦技能三分结构（SKILL/references/scripts）、脚本可编排输出契约（--json）、会话外部化与安全护栏设计 |
| `retrospective-tuyaopen-learning-report-optimization-20260630/` | TuyaOpen学习报告优化流程规范复盘，修复文件放置与命名规范问题，提炼三层Spec约束、二维文档治理等规律与文件创建预检、Spec可发现性保障模式 |
| `retrospective-wsl-learning-plan-20260701/` | WSL 系统学习计划归档与官方文档整合复盘（复盘+洞察+萃取+导出）：聚焦源码+wsl.dev+learn.microsoft.com 三源三角验证、preview API 渐进式学习策略、CLI 短形态惯例、Windows-Linux 通信通道拓扑抽象、API 投影分层模型 5 洞察 + 3 规律认知 |
| `retrospective-wslc-vs-podman-comparison-20260701/` | 微软WSL Containers（wslc）与Red Hat Podman容器方案全维度对比复盘，隔离模型、rootless、CNI/OCI标准、契约匹配、选型决策树等多维度分析 |
| `retrospective-karpathy-multica-tutorial-20260702/` | Karpathy LLM编程准则教程Multica生态扩充复盘，基于local external/multica-ai/multica和multica-cli两个开源仓库进行生态学习与准则扩充 |
| `retrospective-viitorvoice-tts-learning-20260703/` | ViiTorVoice AI语音技术文章学习复盘，语音合成/克隆相关技术与产品分析 |
| `retrospective-sunlogin-offline-hardware-20260704/` | 向日葵五款无网远程控制硬件（控控2/Q1/Q2Pro/Q0.5/Q5Pro）深度解析Wiki任务复盘（复盘+洞察+萃取+导出+原子提交）：33维度横向对比、3大可复用技术架构模式（IPKVM旁路/多模网络冗余/USB-HID仿真）、价格梯度158元→5G专业级产品线策略分析、原子化Wiki结构最佳实践 |
| `retrospective-sunlogin-mouse-bm110-mm110-20260704/` | 向日葵智能远控鼠标MM110/BM110深度解析Wiki任务复盘（复盘+洞察+萃取+导出+原子提交）：双产品矩阵策略、40倍功耗差异量化、SaaS硬件三层漏斗转化模型、办公/教育双场景设计范式、818行13章产品分析教程 |
| `retrospective-agnes-free-api-learning-20260704/` | Agnes AI免费模型实操指南学习深度分析复盘，微信公众号文章系统性分析与洞察萃取 |
| `retrospective-claude-code-context-injection-learning-20260704/` | Claude Code上下文注入机制深度分析学习复盘，系统讲解7种上下文注入机制与Dynamic Workflows动态工作流 |
| `retrospective-eve-framework-learning-20260704/` | Vercel Eve前端Agent框架深度学习行业趋势洞察复盘，Vercel发布的前端Agent框架Eve技术架构与生态影响分析 |
| `retrospective-headroom-wiki-20260704/` | Headroom上下文压缩中间件Wiki学习与深度分析复盘，AI Agent上下文压缩开源项目结构化wiki教程创建与洞察分析 |
| `retrospective-longcat-agent-learning-20260704/` | LongCat-2.0 Agent Wiki创建任务复盘（复盘+洞察+萃取+导出）：美团1.6T MoE模型深度学习，原子化决策前置、格式参照优先、自动化验证全链路3大改进，整体耗时减少30%，5条核心洞察，3个模式升级/新建 |
| `retrospective-mopmonk-wiki-20260704/` | MopMonk安全Agent Wiki教程创建与原子化复盘，安全Agent开源项目wiki教程原子化拆分与知识沉淀 |
| `retrospective-sunlogin-bootbox-analysis-20260704/` | 向日葵开机盒子K3/K4产品深度分析项目复盘报告，开机盒子产品系统性学习与深度分析 |
| `retrospective-sunlogin-camera-su1-wiki-20260704/` | 向日葵USB远程摄像头SU1 Wiki教程项目复盘报告，USB远程摄像头产品系统性学习与深度洞察Wiki教程创建 |
| `retrospective-sunlogin-p4-p1pro-comparison-20260704/` | 向日葵P4/P1Pro对比学习Wiki项目复盘报告，智能插线板P4（4G版）与P1Pro（WiFi版）系统性对比学习与深度洞察分析 |
| `retrospective-sunlogin-pdu-hardware-wiki-20260704/` | 向日葵智能PDU硬件Wiki教程项目复盘报告，智能PDU（P8一代WiFi版/P8二代4G版）产品系统性学习与洞察分析Wiki教程创建 |
| `retrospective-sunlogin-security-wiki-20260704/` | 向日葵远程控制安全产品Wiki教程项目复盘报告，远程控制安全产品页面系统性学习与深度洞察Wiki教程创建 |
| `retrospective-sunlogin-smart-socket-wiki-20260704/` | 向日葵智能插座Wiki教程项目复盘报告，智能插座C1Pro/C2/C4三款产品系统性学习Wiki教程创建 |
| `retrospective-sunlogin-cli-wiki-20260706/` | 向日葵企业CLI（awesun-cli）命令行工具Wiki创建复盘报告，官方CLI文档学习、1537行10章教程创建、AI产品矩阵从两大扩展为三大组件（MCP+CLI+OrayClaw），CLI即API/归一化坐标/三层能力开放3个L1模式萃取 |
| `retrospective-text-to-cad-learning-20260704/` | text-to-cad开源项目学习Wiki教程创建复盘，开源项目介绍文章学习、结构化wiki教程创建与知识库归档 |
| `retrospective-yct-onionhead-wiki-update-20260706/` | 洋葱头（YCT）官网深度学习与Wiki系统性更新复盘，四层信息采集漏斗验证、格式锚点策略、素材预整理委派模式、增量更新边界显式化4项核心洞察萃取，Wiki章节信息量提升183% |
| `retrospective-zleap-agent-harness-learning-20260704/` | Zleap-Agent Harness设计学习分析复盘（复盘+洞察+萃取+导出）：Workspace-first上下文治理、Agent记忆三层治理、多模型协作路由3个模式候选，Prompt→Loop→Harness三层演进定律，harness差异18个百分点数据沉淀，双路径获取模型第四次复用验证 |
| `retrospective-domestic-llm-comparison-learning-20260704/` | 国产大模型对比文章学习分析复盘（复盘+洞察+萃取+导出）：系统学习微信公众号文章整理学习笔记，Sub-Agent报告路径保真度问题、验证Sub-Agent路径盲区、Spec路径弹性vs规范遵从、PowerShell URL陷阱第二次验证、知识库索引自动生成机制5条洞察萃取 |
| `retrospective-papi-jiang-wiki-20260706/` | Papi酱关闭公司回归个人IP创业趋势观察Wiki教程创建复盘，卢松松博客微信公众号文章学习、672行9章商业趋势类Wiki教程创建，验证wiki生产流水线跨领域通用性、八章结构商业领域适配、人工验证兜底降级策略，零返工顺畅交付 |
| `retrospective-dspark-wiki-20260704/` | DSpark论文学习Wiki创建任务复盘（复盘+洞察+萃取+导出）：DeepSeek DSpark论文10个核心概念系统化学习，Spec Mode+并行子代理委派，WebFetch失败降级defuddle、子代理格式质量门、验证脚本容错、单文件wiki适合强耦合主题5条核心洞察萃取 |
| `retrospective-open-code-review-wiki-20260704/` | Open Code Review Wiki教程创建复盘（复盘+洞察+萃取+导出）：阿里开源AI代码评审工具11章节1035行原子化wiki教程创建，Spec阶段前置原子化决策验证、并行子代理批量创建章节文件模式萃取、四层漏斗模型第3次验证、Windows PowerShell URL处理陷阱识别7条核心洞察 |
| `retrospective-kickart-product-learning-20260706/` | 火山引擎KickArt一站式营销创作平台产品分析复盘，六大核心能力完整解析、四大场景详解、7个可复用产品模式、AIDA转化漏斗UX分析 |
| `retrospective-hsk-cli-install-hosting-20260706/` | HSK CLI安装与托管相关学习复盘 |
| `retrospective-oray-comprehensive-analysis-20260706/` | 贝锐向日葵 comprehensive 综合产品分析复盘 |
| `retrospective-orca-ide-analysis-20260706/` | Orca IDE 产品分析复盘 |
| `retrospective-papi-jiang-wiki-20260706/` | Papi酱商业趋势观察Wiki教程创建复盘 |
| `retrospective-sunlogin-cli-wiki-20260706/` | 向日葵企业CLI Wiki创建复盘，1537行10章教程、CLI即API/归一化坐标/三层能力开放3个模式萃取 |
| `retrospective-sunlogin-comprehensive-analysis-20260706/` | 向日葵产品综合分析复盘 |
| `retrospective-yct-onionhead-wiki-update-20260706/` | 洋葱头官网深度学习与Wiki更新复盘，四层信息采集漏斗验证、Wiki章节信息量提升183% |
| `retrospective-volcengine-sandbox-learning-20260706/` | 火山引擎沙箱产品学习复盘 |
| `retrospective-volcengine-searchinfinity-learning-20260706/` | 火山引擎SearchInfinity搜索产品学习复盘 |
| `retrospective-volcengine-viking-ai-search-rec-learning-20260706/` | 火山引擎维京AI搜索推荐产品学习复盘 |
| `retrospective-wps-comate-analysis-20260706/` | WPS Comate AI编程助手产品分析复盘 |
| `retrospective-hiagent-platform-learning-20260707/` | 火山引擎HiAgent一站式数字员工派遣站产品分析复盘，八大优势+十大场景深度解析，"数字员工"产品隐喻创新、安全前置设计、企业级全生命周期闭环、动态网页提取工具选择范式、7个核心洞察+6个可复用模式 |
| `retrospective-volcengine-ark-introduction-20260707/` | 火山引擎ARK大模型服务平台介绍学习复盘 |
| `retrospective-volcengine-dual-product-learning-20260707/` | 火山引擎双产品联合学习复盘 |
| `retrospective-volcengine-acep-learning-20260707/` | 火山引擎ACEP云手机产品学习复盘，七段式认知递进信息架构模式萃取（L2），外部网站分析兜底策略第8次验证 |
| `retrospective-volcengine-mua-learning-20260707/` | 火山引擎MUA大模型升级服务产品学习复盘：710行技术指南笔记+5个原始提取文件+1份分析报告，7个任务全部完成34个检查点通过 |
| `retrospective-trae-v3-3-74-release-analysis-20260708/` | TRAE v3.3.74版本发布分析复盘：Browser配置聚合页、Windows MSSDK接入两大核心更新分析，5个核心洞察+2个新模式萃取 |

### incident-reports/（2 份）

事件复盘目录，存放有明确触发事件、影响范围与根因闭环的 incident 类报告。

| 文件/目录 | 简要说明 | 日期 | 类型 |
|---|---|---|---|
| `retrospective-first-principles-analogy-error-20260709/` | Markdown 链接格式决策错误事件复盘：13个文件误改、18分钟闭环修正，沉淀“决策前三查”检查点 | 2026-07-09 | incident |
| `retrospective-ui-beautification-failure-20260714/` | UI美化连续两轮未达预期事件复盘：工程优化与视觉美化错位、文本 AI 视觉盲飞、反馈闭环缺失 | 2026-07-14 | incident |

### project-reports/（3 份独立报告 + 5 份原子化复盘）

项目级独立复盘报告目录，存放以单文件 Markdown 形式交付的完整复盘报告（区别于原子化子目录结构）。

| 文件/目录 | 简要说明 |
|---|---|
| `frontmatter-migration-retro-20260701.md` | YAML frontmatter 批量迁移复盘报告 |
| `retrospective-mdi-project-completion-20260702/` | MDI 项目结项复盘 |
| `retrospective-myst-unified-ecosystem-phase1-20260704/` | MyST Markdown 统一化接口生态体系 阶段1 复盘：14文件/1770行，11个概念标准化定义，四层分类架构，7类关系映射，4个并行Agent协同，spec-driven-batch-doc-generation模式验证 |
| `retrospective-spec-adoption-tools-frontmatter-governance-20260702/` | 规范度量工具增强与Frontmatter治理闭环复盘，132文件变更/4436行新增，.agents/frontmatter合规率68.5%→98.5%，check-spec-adoption.py增强+check-metadata-layering.py+add-agents-frontmatter.py三个工具交付 |
| `spec-adoption-batch-report.md` | 规范落地度量批量对比报告，全局加权评分83.7/100（B级），.agents 91.3分/A级、docs 82.8分/B级、scripts 61.9分/D级，含三目录详细问题明细与权重配置 |
| `dockerfile-optimization-retro-20260703.md` | Dockerfile 全面优化复盘：层缓存重排（构建速度提升400倍）、.dockerignore 创建、错误处理统一、兼容性保障，含变化频率分层原则等6条最佳实践 |
| `retrospective-scikit-build-core-wiki-20260705/` | scikit-build-core Wiki 教程创建复盘：7章2864行教程交付、模式反馈环延迟分析、分层行数治理验证、cross-wiki-reference-directory-first L2升级（validation_count 2→3） |
| `retrospective-first-principles-knowledge-system-20260710/` | 第一性原理知识体系v1.0→v1.7构建项目系统性复盘：9个文件（4主报告+5支撑分析，v1.2），完整时间线（8版本/15commit/35文件/4609行）、12核心决策5-Whys分析、10个问题深度复盘、14个方法论应用、10条关键洞察（9条高度普适）、7条改进建议、7个元洞察、SOP模板v1.3沉淀、元复盘checklist（`.agents/checklists/meta-retrospective-checklist.md`）创建，行动项100%闭环，验证"做事→复盘→元复盘→修复→方法论迭代"完整闭环 |

### task-reports/（26 份）

任务执行复盘目录，存放以单文件或原子化目录形式交付的单次任务完整复盘报告。

| 文件/目录 | 简要说明 | 日期 | 类型 |
|---|---|---|---|
| `retrospective-alipay-aipay-windows-install-20260723.md` | 支付宝AI Pay Skill Windows安装任务复盘（R→I→E→Export）：alipay-cli跨平台兼容性断裂/Agent沙箱网络限制/多组件安装分层验证3条核心洞察，萃取Windows环境Unix-only CLI安装处理/沙箱联网命令预授权/多组件安装状态分层验证3个L1可复用模式，G1-G3质量门全部通过 | 2026-07-23 | task |
| `retrospective-caffe-ffi-conv-v4-milestone-20260805.md` | Conv v4 OpenMP并行优化里程碑复盘（R→I→V→E→C）：Conv层沿M维度分块并行优化、CPU推理OpenMP双层并行隔离配置模式、16种OMP抖动诊断组合，3条核心洞察+1个L1可复用模式，G1-G4质量门全部通过 | 2026-08-05 | task |
| `retrospective-xmnn-container-health-fix-20260812.md` | xmnn 容器 unhealthy 误报诊断与修复复盘（F→V→C→R→I→E）：健康探针与部署形态错配导致 4 容器系统性误报，注入 ENABLE_SSH=no/ENABLE_DOCKER=no 修复，萃取探针-部署模式对齐模式，3条核心洞察+1个可复用模式，G1-G4质量门全部通过 | 2026-08-12 | task |
| `retrospective-chaos-epub-books-classification-20260819.md` | EPUB电子书分类任务里程碑复盘（R→I→V→E→C）：2121本散放EPUB归类为19个类别，两轮递进分类（强关键词+正则模式）将分类率从68.6%提升至81.8%，萃取"先强后弱两级匹配分类模式"，3条核心洞察+1个L1可复用模式，G1-G4质量门全部通过 | 2026-08-19 | task |
| `okf-spec-bundle-review-fix-retrospective-20260821.md` | OKF-Spec Bundle 对抗审查+修复+双原子提交里程碑复盘（R→I→V→E→C）：对19个含status文档执行四视角对抗审查，识别P1（信任元数据真实化：登记process:seven-concepts-v进程+统一20处verified指向）与P2（溯源自包含：18文档resource改bundle-relative）两类缺口，经双原子提交（a58146b+2b62350）落地，萃取信任元数据真实化/溯源自包含2个L1可复用模式，G1-G4质量门全部通过 | 2026-08-21 | task |
| `retrospective-pickle-sedimentation-20260723/` | Pickle序列化知识沉淀R→I→E链路复盘：方法论编排场景4知识沉淀，3份源材料→2个新文档（源码层修复模式+诊断SOP）+2个索引更新，形成四位一体知识闭环，G1-G4质量门全部通过 | 2026-07-23 | task |
| `retrospective-sidebar-ui-beautification-20260714.md` | 竹简悟道右侧侧边栏UI美化七概念复盘（R→I→F→E→C）：Tailwind v4动态className检测盲区根因分析、内联样式保底模式/CSS渲染诊断五步/书斋清供侧边栏设计参数3个可复用模式萃取，frontend-design Skill视觉闭环验证 | 2026-07-14 | task |
| `retrospective-mermaid-funnel-redesign-pdf-export-20260711/` | Mermaid五品漏斗图重绘与PDF导出任务复盘：修正"工艺品→公益品"笔误、重绘五品漏斗Mermaid图（5层信任分层+直线连接+渐变色系）、开发并完善三段式PDF导出脚本（Pandoc+Mermaid.js+Playwright），萃取"三段式中文PDF导出法"L1可复用模式 | 2026-07-11 | task |
| `retrospective-mermaid-automation-toolchain-20260711/` | Mermaid自动化工具链+会议分析全流程复盘：从一画开天会议记录分析出发，问题驱动迭代交付2个自动化脚本（export-md-to-pdf.py+mermaid-full-scan.py，552行）、1个人工修复指南（1089行），自动修复67处Mermaid语法错误，完成私密报告目录迁移；核心洞察：工具链建设是问题驱动的自然演化而非预先规划 | 2026-07-11 | task |
| `retrospective-session-20260708-overview/` | 会话全面复盘（2026年7月7日-8日）：涵盖差异化分析维度模板库建设、工程模式沉淀、Pre-flight预探索实践、两阶段并行机制轻量化等多项任务，50+次git提交，产出100+文件 | 2026-07-08 | session |
| `retrospective-generate-readme-tool-20260709/` | generate-readme.py目录README自动生成工具开发复盘：P0手动→P1批量→P2全覆盖渐进式开发、标记区域增量更新机制（--update）、端到端测试验证、203行使用文档；萃取标记区域增量更新、渐进式工具开发三阶段、端到端真实场景测试法3个可复用模式 | 2026-07-09 | task |
| `retrospective-report-standardization-20260708/` | 复盘报告结构标准化与内容校验更新复盘：两份复盘报告（并发安全检查器+冲突解决机制）三文件结构标准化，修正报告-代码漂移（六维→八维），补全frontmatter，建立方法论演进交叉引用链；萃取文档更新三查法、session continuation恢复三查法、cross_refs双向链接3个可复用模式 | 2026-07-08 | task |
| `retrospective-conflict-resolution-mechanism-20260708/` | 多智能体冲突解决机制实现与死锁风险修复复盘：ConflictResolver三类冲突13条仲裁规则实现，代码审查发现8个问题（2高/3中/3低）全部修复，39个单元测试通过；萃取并发安全审查六维检查法（后续扩展为八维自动化工具）、N-scaling测试矩阵、修复即闭环SOP | 2026-07-08 | task |
| `retrospective-concurrent-safety-checker-20260708/` | 并发模块安全检查器（八维检查法）开发与pre-commit集成复盘：Python AST静态分析引擎实现（visitor+scanner+cli三层架构，初始六维在TDD验证中扩展为八维：新增DEADLOCK死锁顺序、LEAK资源泄漏）、48个单元测试覆盖五件套、链式pre-commit钩子集成，沉淀信号识别四步法/AST消歧五法/链式钩子/三层信任/TDD五件套5个L2可复用模式 | 2026-07-08 | task |
| `retrospective-concurrent-report-atomization-20260708/` | 并发安全检查器复盘报告原子化与数据漂移修正复盘：将八维规则详表独立为eight-dimensions-concurrent-safety-spec.md技术规格文件（后迁移至知识库best-practices），重构报告为标准五段式结构（264→187行），修正7处报告-代码量化数据漂移（visitor行数465→840、测试数33→48等）；萃取技术规格与叙述报告分离原则、文档更新四查法（三查+数值验证）、编辑-验证分离模式3个可复用模式 | 2026-07-08 | task |
| `retrospective-analysis-dimension-template-library-20260708/` | 差异化分析维度模板库建设复盘：创建5个分析维度模板（CLI/Tool、CI/Integration、Infrastructure/Config、Example/Demo、Skills/Plugin）+1个README索引，6个文件650行，含关键实体标记规范和L0/L1/L2三层质量检查清单 | 2026-07-08 | task |
| `retrospective-vendor-check-module-20260707/` | vendor检查模块开发与测试覆盖增强复盘：lib/checks/vendor.py合规检查模块实现（521行）、--debug调试日志设计、Windows跨平台路径bug修复、测试从36个扩充到59个全部通过，提炼CLI调试日志设计模式、跨平台路径检测模式、代码分支覆盖分析法3个可复用模式 | 2026-07-07 | task |
| `retrospective-ark-cli-submodule-integration-20260707/` | ark-cli Git子模块集成任务复盘：将@volcengine/ark-cli集成为vendor/ark-cli Git子模块，调整.gitignore策略为白名单模式，同步更新5个关联规范文档，沉淀子模块集成涟漪效应验证方法论 | 2026-07-07 | task |
| `retrospective-arkcli-setup-20260707/` | @volcengine/ark-cli安装与SSO配置复盘：npm全局安装、OAuth/SSO四步流程、CLI可执行文件名验证（package.json bin字段）、IDE Agent沙箱文件写入权限处理，沉淀CLI配置操作手册（cli-setup-in-agent-environment.md） | 2026-07-07 | task |
| `retrospective-codex-article-analysis-20260706/` | Codex产品哲学文章分析与归档复盘：微信公众号文章解析、外部学习洞察萃取、文章归档至insight-extraction/external-learning/目录 | 2026-07-06 | task |
| `retrospective-l0l3-template-design-20260706/` | L0-L3模板设计复盘：目录结构冲突评估、阶段守卫探测豁免规则文档更新、149个阶段守卫测试全部通过、E2E测试验证（34个用例） | 2026-07-06 | task |
| `retrospective-mainecoon-article-analysis-20260706/` | MaineCoon文章分析与归档复盘 | 2026-07-06 | task |
| `retrospective-zhihu-637007780-analysis-20260706/` | 知乎问题637007780系统性学习与知识萃取任务复盘：知乎反爬机制（40362+JS challenge+登录墙）下6种策略失败、第7种（agent-browser + `--disable-blink-features=AutomationControlled` + 桌面UA）突破，获取3/23回答（覆盖率13%）完成三层分析降级，提炼反爬策略决策树（L1→L2升级）、小样本分析方法论（L1新建）、三层框架适用性边界等5个洞察 | 2026-07-06 | task |
| `retrospective-best-practice-docs-20260705/` | 最佳实践文档整理复盘：将TVM FFI复盘中的两个洞察（高层文档优先研究法L2、工具故障三级降级策略L1）整理为模式库独立文档，2个新模式文档+3个索引更新，验证"复盘洞察→模式库平滑转化法"流程 | 2026-07-05 | task |
| `retrospective-tvm-ffi-wiki-tutorial-20260705/` | TVM FFI跨语言FFI框架Wiki教程创建任务复盘，在Shell管道耗尽/WebFetch超时/Read超时三重基础设施故障下，通过Vendor AGENTS.md高层文档优先+4个并行子代理分组写作完成17个文档（约5870行）交付，提炼"高层文档优先研究法""工具故障三级降级""主题分组并行写作"3个可复用模式，其中2个达到L2成熟度（2次验证）。 | 2026-07-05 | task |
| [2026-07-04 贝锐AI产品矩阵分析任务复盘](task-reports/2026-07-04-oray-ai-analysis-retrospective.md) | 对贝锐20周年AI产品矩阵系统性分析任务的完整复盘，包含Spec Mode执行流程回顾、403访问问题处理、1309行分析报告产出总结，沉淀了"外部网站分析信息源分层兜底策略"可复用模式。 | 2026-07-04 | task |
| [2026-07-04 知识沉淀工作流元复盘](task-reports/2026-07-04-knowledge-sedimentation-workflow-retrospective.md) | 对"复盘→洞察→萃取→导出→提交"完整知识沉淀工作流的元复盘，分析子代理越权提交、暂存区污染、导出验证发现9个问题等关键事件，提炼子代理"三不准"规范、增强版知识沉淀SOP、Git暂存区卫生五步法，新建2个L1模式+1个L2模式更新。 | 2026-07-04 | task |
| `retrospective-tech-interface-wiki-20260703/` | 技术接口概念Wiki教程创建复盘（已归入knowledge-content/，此处保留历史记录） | 2026-07-03 | task |
| `retrospective-analyze-wechat-article-3dnk-20260706.md` | Codex相关微信公众号文章分析（独立报告） | 2026-07-06 | task |
| `retrospective-first-principles-knowledge-link-20260709.md` | 第一性原理指令集与知识库双向关联建立复盘：轻量级任务四步法复盘，验证"对应性前提"（first-principles是唯一有系统性资料档案的指令集主题），提炼3条洞察（对应性前提L1候选/路径风格入乡随俗/先例查询验证），4项行动项 | 2026-07-09 | task |

### knowledge-content/（2 份）

知识库内容建设目录，存放技术Wiki、通信协议教程等知识体系化内容的创建复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-tvm-ffi-wiki-tutorial-20260705/` | TVM FFI跨语言FFI框架Wiki教程复盘，17个文档/约5870行交付，Shell管道耗尽/WebFetch超时/Read超时三重故障下完成，Vendor高层文档优先研究法、工具故障三级降级、主题分组并行写作3个可复用模式萃取（2个P0/L2） |
| `retrospective-agent-proto-wiki-20260703/` | Agent通信协议Wiki教程复盘，13个文档/4286行/34个Mermaid图交付，Spec Mode三段式（PRD→tasks→checklist）零章节遗漏验证，子agent自包含约束、类比锚点教学法等6个可复用模式萃取 |
| `retrospective-pickle-sedimentation-20260723/` | Pickle序列化知识沉淀R→I→E链路复盘：3份源材料→2个新文档（源码层修复模式+诊断SOP）+2个索引更新，形成「运行时兼容层+源码层修复+升级检查+诊断SOP」四位一体知识闭环，G1-G4质量门全部通过 |

### standards-tools/（1 份）

标准与工具评估目录，存放Markdown语法标准、规范迁移可行性、工具链技术评估等分析报告。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `myst-to-agentspec-migration-analysis/` | MyST Directives/Roles系统在Agent Spec开发中的可迁移性技术评估（v1.2.0），66份存量文档统计分析、解析器代码审计、六维技术支持评估（MDI/API/ABI/MCP/ACP/A2A）、LLM×Sphinx生态融合7个创新场景、MyST-NB可执行文档专题、保守/平衡/激进三方案对比，12章原子化交付 |

### documentation-governance/（3 份）

文档治理目录，存放 Sphinx/MyST 文档工程治理、toctree 目录树完整性、index.md 结构规范相关的复盘与洞察报告。

| 报告名称（目录/文件） | 简要说明 |
|---|---|
| `retrospective-sphinx-toctree-clear-20260824/` | awesome-okf-xs Sphinx toctree 警告清零里程碑复盘：4888 个 toc.not_included 警告根因分析、自动化修复脚本开发、867 文件变更与 2 个原子提交，萃取 OKF bundle 目录树完整性修复工作流与 toctree 动态验证法 |
| `retrospective-invocations-bundle-okf-update-20260824/` | invocations bundle OKF 更新复盘：invocations Collection 封装 Sphinx 构建、任务入口统一与参数收敛、CI/本地命令一致性 |
| `insight-index-structure-duality-20260824.md` | **index.md 两种结构洞察报告**：okf-spec 风格（层级路由）vs trae-skills 风格（扁平索引）的本质差异、判别框架与反模式，R→I→E→V 四阶段分析 |

### iteration-reports/（2 份）

迭代复盘目录，存放迭代/阶段级别的完整复盘报告（Spec 模式七阶段工作流、系统性验证、PARTIAL 修复闭环）。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-config-file-placement-governance-20260718/` | 配置文件放置治理迭代复盘：配置文件组织规范的制定与实施闭环 |
| `weekly-2026-07-20/` | 2026-07-20 周迭代复盘 |

### adversarial-reviews/（29 份）

对抗审查目录，存放对抗性评审产出（魔鬼代言人/新人/老板/未来四视角攻击记录），对方案、报告与决策的多视角证伪加固。

| 报告名称 | 简要说明 |
|---|---|
| `adversarial-review-20260713T*.md`（5 份） | 2026-07-13 对抗性评审记录：方案/报告的魔鬼代言人与多视角证伪攻击 |
| `adversarial-review-20260718T*.md`（3 份） | 2026-07-18 对抗性评审记录 |
| `adversarial-review-20260719T*.md`（6 份） | 2026-07-19 对抗性评审记录 |
| `adversarial-review-20260729T*.md`（3 份） | 2026-07-29 对抗性评审记录 |
| `adversarial-review-20260810T*.md`（1 份） | 2026-08-10 对抗性评审记录 |
| `adversarial-review-20260814T*.md`（8 份） | 2026-08-14 对抗性评审记录 |
| `adversarial-review-20260819T*.md`（3 份） | 2026-08-19 对抗性评审记录 |

### bug-fix/（7 项）

故障修复目录，存放具体故障/缺陷的根因分析与修复复盘（工具增强、Docker 构建修复、PyTorch 集成、COW 语义修复等）。

| 报告名称（目录/文件） | 简要说明 |
|---|---|
| `cow-blob-cow-semantics-fix-20260801.md`（+ charts html） | COW blob 写时复制语义修复复盘：OverlayFS Copy-on-Write 语义纠正与镜像体积优化 |
| `docker-build/`（5 个子报告） | Docker 构建修复合集：caffe docker 运行时、caffe ops 正确性测试、conda 构建修复、xmnn Nuitka docker 运行时、xmnn wheel 打包数据目录 |
| `retrospective-xmnn-pytorch-integration-20260723/` | XMNN PyTorch 集成复盘：PyTorch 集成方案设计与落地 |

### bugfix/（5 份）

修复类复盘目录，存放 CI 质量门、Docker entrypoint、TVM/LLVM 符号可见性、VTA 硬编码等修复类复盘。与 `bug-fix/` 同属修复域，历史命名差异保留。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-ci-quality-gates-path-migration-20260718/` | CI 质量门路径迁移修复复盘 |
| `retrospective-docker-commit-entrypoint-fix-20260718/` | Docker commit/entrypoint 修复复盘 |
| `retrospective-tvm-llvm-weak-symbol-leak-fix-20260721/` | TVM/LLVM 弱符号泄漏修复复盘 |
| `retrospective-tvm-symbol-visibility-fix-20260718/` | TVM 符号可见性修复复盘 |
| `retrospective-vta-hw-path-hardcode-fix-20260717/` | VTA 硬件路径硬编码修复复盘 |

### build-engineering/（29 份原子化 + 8 份独立报告）

构建工程目录，存放 Docker/DevContainer 镜像构建、conda 环境、Nuitka 编译、CMake 工程、发布流水线、构建性能优化等复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-agents-atomization-seven-docker-projects-20260807/` | 七个 Docker 项目原子化构建复盘 |
| `retrospective-ai-dev-variant-bugfix-logging-20260813/` | AI dev 变体镜像日志修复复盘 |
| `retrospective-caffe-ffi-jupyter-dev-docker-20260729/` | caffe-ffi Jupyter dev docker 构建复盘 |
| `retrospective-caffe-ffi-logging-python-wrapper-20260728/` | caffe-ffi logging python wrapper 复盘 |
| `retrospective-caffe-ffi-protobuf7-build-20260728/` | caffe-ffi protobuf7 构建复盘 |
| `retrospective-caffe-ffi-tests-enable-20260801/` | caffe-ffi 测试启用构建复盘 |
| `retrospective-caffe-ffi-wsl-tooling-20260729/` | caffe-ffi WSL 工具链构建复盘 |
| `retrospective-caffe-jupyter-docker-build-export-20260727/` | caffe Jupyter docker 构建导出复盘 |
| `retrospective-caffe-standalone-caffex-removal-20260727/` | caffe standalone caffex 移除复盘 |
| `retrospective-chaos-ai-portable-docker-20260811/` | chaos AI 便携 docker 镜像复盘 |
| `retrospective-chaos-ai-portable-slim-20260811/` | chaos AI 便携 slim 镜像复盘 |
| `retrospective-cmake-atomization-caffe-ffi-round2-20260729/` | caffe-ffi CMake 原子化第二轮复盘 |
| `retrospective-devcontainer-agents-atomization-verify-20260807/` | DevContainer agents 原子化验证复盘 |
| `retrospective-devcontainer-base-seven-concepts-20260807/` | DevContainer 基础镜像七概念构建复盘 |
| `retrospective-devcontainer-base-seven-concepts-v2-20260819/` | DevContainer 基础镜像七概念 v2 构建复盘 |
| `retrospective-devcontainer-conda-libmamba-ft-v2.1-20260814/` | DevContainer conda libmamba free-threading v2.1 复盘 |
| `retrospective-devcontainer-slim-images-20260819/` | DevContainer slim 镜像瘦身复盘 |
| `retrospective-devcontainer-v221-conda-perf-20260814/` | DevContainer v2.2.1 conda 性能复盘 |
| `retrospective-jupyter-ssh-base-seven-concepts-20260807/` | Jupyter SSH 基础镜像七概念构建复盘 |
| `retrospective-llama-cpp-python-cuda-build-20260820/` | llama-cpp-python CUDA 构建复盘 |
| `retrospective-nativebuild-automation-20260802/` | 原生构建自动化复盘 |
| `retrospective-pycaffe-full-build-scripts-20260727/` | pycaffe 完整构建脚本复盘 |
| `retrospective-standalone-finalize-docker-save-20260727/` | standalone 收尾 docker save 复盘 |
| `retrospective-xmnn-docker-gpu-variant-20260727/` | xmnn docker GPU 变体镜像复盘 |
| `retrospective-xmnn-docker-timezone-20260727/` | xmnn docker 时区配置复盘 |
| `retrospective-xmnn-four-layer-release-pipeline-20260810/` | xmnn 四层发布流水线复盘 |
| `retrospective-xmnn-pyproject-deps-audit-20260727/` | xmnn pyproject 依赖审计复盘 |
| `retrospective-xmnn-runtime-docker-optional-pytorch-20260727/` | xmnn runtime docker 可选 PyTorch 复盘 |
| `retrospective-xmnn-wheel-scikit-build-nuitka-20260726/` | xmnn wheel scikit-build-nuitka 打包复盘 |

| 独立报告（单文件） | 简要说明 |
|---|---|
| `docker-build-verification-caffe-ffi-20260801.md` | caffe-ffi docker 构建验证 |
| `insight-jupyter-kernel-expose-host-ide-20260814.md` | Jupyter kernel 暴露宿主 IDE 洞察 |
| `insight-onnx-quantization-benchmark-analysis-20260808.md` | ONNX 量化基准分析洞察 |
| `insight-palmdet-compile-failure-20260812.md` | PalmDet 编译失败洞察 |
| `retrospective-docker-buildkit-observability-20260807.md` | Docker BuildKit 可观测性复盘 |
| `retrospective-onnx-quantize-kit-test-coverage-20260816.md` | ONNX 量化套件测试覆盖复盘 |
| `summary-palmdet-compile-fix-20260812.md` | PalmDet 编译修复摘要 |
| `troubleshooting-devcontainer-jupyter-gil-20260819.md` | DevContainer Jupyter GIL 排障 |

### code-optimization/（22 份）

代码优化目录，存放算子优化、性能调优、FFI 边界重构、内存零拷贝、精度修正、代码库提取等复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `report-batch-hardening-float-precision-20260802/` | 批处理加固浮点精度报告 |
| `report-c1-kink-protection-rollout-20260802/` | C1 kink 防护推广报告 |
| `report-pooling-backward-gradient-routing-20260803/` | pooling 反向梯度路由报告 |
| `retrospective-blob-shape-tvm-ffi-refactor-20260727/` | blob shape TVM FFI 重构复盘 |
| `retrospective-caffe-ffi-cpp-py-boundary-fix-20260801/` | caffe-ffi C++/Python 边界修复复盘 |
| `retrospective-caffe-ffi-deconv-neuron-zerocopy-20260801/` | caffe-ffi deconv neuron 零拷贝复盘 |
| `retrospective-caffe-ffi-p3b-test-milestone-20260731/` | caffe-ffi P3B 测试里程碑复盘 |
| `retrospective-caffe-ffi-p3c-activation-logging-20260731/` | caffe-ffi P3C 激活日志复盘 |
| `retrospective-caffe-ffi-viz-insert-splits-20260801/` | caffe-ffi 可视化插入 splits 复盘 |
| `retrospective-caffe-ffi-win32-dll-assert-helper-module-20260801/` | caffe-ffi win32 DLL assert helper 模块复盘 |
| `retrospective-caffe-ops-library-extraction-20260727/` | caffe ops 代码库提取复盘 |
| `retrospective-caffe-rmsnorm-transpose-removal-20260721/` | caffe RMSNorm transpose 消除复盘 |
| `retrospective-caffe-slim-batch-inference-mnist-20260727/` | caffe-slim MNIST 批量推理复盘 |
| `retrospective-caffe-slim-bvlc-compat-20260727/` | caffe-slim BVLC 兼容性复盘 |
| `retrospective-caffe-slim-bvlc-logging-20260727/` | caffe-slim BVLC 日志复盘 |
| `retrospective-caffe-slim-inference-notebook-20260727/` | caffe-slim 推理 notebook 复盘 |
| `retrospective-caffe-slim-tvm-ffi-20260723/` | caffe-slim TVM FFI 复盘 |
| `retrospective-demo-ffi-math-ops-boundary-perf-20260728/` | demo FFI math ops 边界性能复盘 |
| `retrospective-float-precision-elu-kink-20260802/` | 浮点精度 ELU kink 修复复盘 |
| `retrospective-pycaffe-image-preprocessing-20260723/` | pycaffe 图像预处理复盘 |
| `retrospective-split-zerocopy-cow-milestone-20260731/` | split 零拷贝 COW 里程碑复盘 |
| `retrospective-task11-cow-fix-20260801/` | task11 COW 修复复盘 |

### environment-setup/（4 份原子化 + 1 份独立报告 + 1 资产目录）

环境搭建目录，存放 WSL/Docker/GPU 环境配置、系统级环境迁移、桌面/系统设置修复、conda free-threading 环境等复盘。

| 报告名称（目录/文件） | 简要说明 |
|---|---|
| `retrospective-docker-cache-to-wsl-migration-20260818/` | Docker 镜像缓存迁移 WSL 复盘 |
| `retrospective-windows-desktop-icons-missing-20260819/` | Windows 桌面图标缺失修复复盘 |
| `retrospective-wsl-docker-gpu-fix-20260815/` | WSL Docker GPU 修复复盘 |
| `retrospective-wsl-ubuntu2604-install-migration-20260722/` | WSL Ubuntu 26.04 安装迁移复盘 |
| `retrospective-py314t-conda-freethreading-20260819.md` | Python 3.14t conda free-threading 环境复盘 |
| `retrospective-py314t-conda-freethreading-20260819-assets/` | free-threading 环境搭建资产目录（scan-gil.json 等） |

### feature-development/（2 份）

功能开发目录，存放新功能开发完整复盘（从需求到交付的全流程）。

| 报告名称 | 简要说明 |
|---|---|
| `retrospective-caffeproto-l2norm-20260721.md` | CaffeProto L2Norm 算子功能开发复盘 |
| `retrospective-skill-auto-loader-20260807.md` | Skill 自动加载器功能开发复盘 |

## 三、文件组织规则

`docs/retrospective/reports/` 目录下的文件组织遵循以下规则：

### 3.1 主题子文件夹

20 个主题子文件夹分别存放对应主题的复盘报告。各文件夹内以原子化子目录为主；`insight-extraction/` 下额外包含 `standalone/` 子目录存放独立洞察卡片（单文件形式，不属于特定原子化报告）；`project-reports/` 以独立单文件报告为主；`incident-reports/` 聚焦事件型目录复盘。

### 3.2 四文件标准结构

每个原子化子目录通常包含 4 个 .md 文件；如有跨项目迁移验证或专题补充，可扩展为 5 个或更多文件：

| 模块文件 | 说明 |
|---|---|
| `README.md` | 项目概览（背景、任务输入、交付物清单）+ 子模块导航 + 关联报告 |
| `execution-retrospective.md` | 执行过程复盘，含阶段划分、关键决策与问题分析 |
| `insight-extraction.md` | 洞察萃取，提炼可复用的方法论、模式与经验 |
| `export-suggestions.md` | 导出建议，含行动项、改进方向与后续跟进事项 |
| `*-case-study*.md`（可选） | 跨项目迁移案例、专项复用验证或方法论落地追记 |

### 3.3 洞察原子化扩展（insights/ 子目录）

当 `insight-extraction.md` 包含多条独立洞察（通常 ≥5 条）时，可将其原子化为 `insights/` 子目录：

| 路径 | 说明 |
|---|---|
| `insights/README.md` | 原子洞察索引（含清单表、成熟度统计） |
| `insights/xxx.md` | 单条洞察独立文件（含 frontmatter、完整论述） |
| `insight-extraction.md` | 降级为导航索引（保留 frontmatter + 洞察链接表 + 原子化说明） |

已采用此结构的报告：
- `competitive-analysis/retrospective-specweave-contest-advantage-analysis-20260624/retrospective-meta-20260625/insights/`（6条元洞察）
- `insight-extraction/external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/insights/`（9条核心元洞察）

### 3.4 特殊结构

`retrospective-comprehensive-20260623/` 采用六模块结构：

| 模块文件 | 说明 |
|---|---|
| `project-retrospective.md` | 项目整体复盘 |
| `insight-extraction.md` | 洞察萃取 |
| `improvement-suggestions.md` | 改进建议 |
| `execution-s1-s3.md` | 执行阶段 S1-S3 详细记录 |
| `execution-s4-s7.md` | 执行阶段 S4-S7 详细记录 |
| `meta-closure.md` | 元级闭合分析 |

### 3.5 独立报告

`project-governance/reports-duplication-optimization-report.md` 为独立报告，无对应的原子化子目录。该报告分析了复盘报告体系中重复内容的来源与优化策略。

### 3.6 连接器文件与子目录的对应关系

全部 6 个主题的源 `.md` 连接器文件已合并至各自子目录的 `README.md` 中。`README.md` 的 `source` 字段现直指原始报告，溯源链缩短为"原始报告 → README → 子模块"。
- **无 source 字段的报告**：连接器即为原始报告本身（无更深源头），对应 README 不保留 `source` 字段。
- **独立报告**：`project-governance/reports-duplication-optimization-report.md` 为独立报告，无对应原子化子目录。

### 3.7 新增报告归类规则

**禁止在 `reports/` 根目录下直接放置报告目录或独立 `.md` 文件。** 所有新增报告必须遵循以下流程：

1. **判定归属分类**：根据报告主题，对照「一、分类标准」表格确定应归入的一级分类目录。若现有 20 个分类均无法覆盖，应先讨论是否新增分类，而非直接放入根目录。
2. **放入对应子目录**：将报告目录放入对应的分类子目录下（如 `project-governance/xxx/`、`competitive-analysis/xxx/`）。
3. **更新索引**：在本文档中同步更新以下三处：分类报告清单（第二节）、按日期查找表（四.1）、按关键词查找表（四.2）。若报告类型在四.3 中无对应条目，一并补充。
4. **运行验证**：执行 `.agents/scripts/check-report-categorization.py` 确认无未归类报告。

> **反例**：直接将报告目录放在 `reports/xxx/` 而非 `reports/<分类>/xxx/`，或直接在 `reports/` 下创建独立 `.md` 文件（README.md 自身除外）。

## 四、快速查找指南

### 4.1 按日期查找

| 日期区间 | 报告 | 分类 |
|---|---|---|
| 2026-06-23 | `retrospective-atomization-modularization-comprehensive-report-20260623/` | atomization |
| 2026-06-23 | `retrospective-insight-extraction-comprehensive-20260623/` | insight-extraction/meta-methodology |
| 2026-06-23 | `retrospective-comprehensive-20260623/` | project-governance |
| 2026-06-23 | `retrospective-export-20260623/` | project-governance |
| 2026-06-24 | `retrospective-atomization-execution-s1-7-20260624/` | atomization |
| 2026-06-24 | `retrospective-meta-atomization-full-chain-20260624/` | atomization |
| 2026-06-24 | `retrospective-report-reports-atomization-comprehensive-20260624/` | atomization |
| 2026-06-24 | `retrospective-entry-detail-migration-20260624/` | atomization |
| 2026-06-24 | `retrospective-session-insight-extraction-readme-evolution-20260624/` | insight-extraction/meta-methodology |
| 2026-06-24 | `retrospective-trae-contest-faq-analysis-20260624/` | competitive-analysis |
| 2026-06-24 | `retrospective-specweave-contest-advantage-analysis-20260624/` | competitive-analysis |
| 2026-06-24 | `retrospective-readme-sync-and-brand-naming-20260624/` | project-governance |
| 2026-06-24 | `retrospective-session-agents-md-violation-20260624/` | project-governance |
| 2026-06-25 | `retrospective-trae-contest-demo-generation-learning-20260625/` | competitive-analysis |
| 2026-06-25 | `retrospective-project-comprehensive-20260625/` | project-governance |
| 2026-06-25 | `retrospective-specweave-demo-production-flow-20260625/` | project-governance |
| 2026-06-25 | `retrospective-trae-contest-preliminary-guide-learning-20260625/` | competitive-analysis |
| 2026-06-25 | `retrospective-zhujian-wudao-apps-archiving-20260625/` | project-governance |
| 2026-06-25 | `retrospective-ai-code-assistant-project-analysis-20260625/` | insight-extraction/external-learning |
| 2026-06-25 | `retrospective-deer-flow-2-learning-20260625/` | insight-extraction/external-learning |
| 2026-06-25 | `retrospective-ian-xiaohei-illustrations-learning-20260625/` | competitive-analysis |
| 2026-06-25 | `retrospective-zhujian-wudao-specs-analysis-20260625/` | insight-extraction/external-learning |
| 2026-06-26 | `retrospective-insights-reorg-20260626/` | project-governance |
| 2026-06-26 | `retrospective-mermaid-rendering-fix-20260626/` | project-governance |
| 2026-06-26 | `retrospective-link-fix-depth-adjustment-20260626/` | project-governance |
| 2026-06-26 | `retrospective-report-specs-theme-task-board-system-20260626/` | spec-system |
| 2026-06-26 | `retrospective-specweave-full-project-comprehensive-20260626/` | project-governance |
| 2026-06-29 | `retrospective-claude-tag-article-learning-20260629/` | competitive-analysis |
| 2026-06-30 | `retrospective-tuyaopen-analysis-20260630/` | insight-extraction/iot-ecosystem |
| 2026-06-30 | `retrospective-tuyaopen-folder-20260630/` | insight-extraction/iot-ecosystem |
| 2026-06-30 | `retrospective-home-assistant-core-analysis-20260630/` | insight-extraction/iot-ecosystem |
| 2026-07-01 | `retrospective-tuya-ipc-spec-and-xlsx-learning-20260701/` | insight-extraction/iot-ecosystem |
| 2026-07-01 | `retrospective-xmnn-folder-20260701/` | insight-extraction/toolchain-dev |
| 2026-07-02 | `retrospective-llvm-dev-env-and-build-20260702/` | insight-extraction/toolchain-dev |
| 2026-07-02 | `retrospective-llvm-dev-mount-permission-fix-20260702/` | insight-extraction/toolchain-dev |
| 2026-07-02 | `retrospective-export-suggestions-execution-20260702/` | insight-extraction/meta-methodology |
| 2026-07-03 | `standalone/insight-dockerfile-caching-20260703.md` | insight-extraction/standalone |
| 2026-07-03 | `dockerfile-optimization-retro-20260703.md` | project-reports |
| 2026-07-03 | `retrospective-directory-theme-reorganization-20260703/` | insight-extraction/meta-methodology |
| 2026-07-01 | `retrospective-git-local-clone-bug-20260701/` | project-governance |
| 2026-06-29 | `retrospective-mermaid-rendering-regression-20260629/` | project-governance |
| 2026-06-29 | `retrospective-mermaid-governance-closure-20260629/` | project-governance |
| 2026-06-29 | `retrospective-test-plan-and-atomic-commit-20260629/` | project-governance |
| 2026-06-29 | `retrospective-forum-bot-logging-20260629/` | project-governance |
| 2026-06-29 | `retrospective-forum-posting-skill-optimization-20260629/` | project-governance |
| 2026-06-29 | `retrospective-forum-automation-full-workflow-20260629/` | project-governance |
| 2026-06-29 | `retrospective-vendor-flexloop-governance-adjustment-20260629/` | project-governance |
| 2026-06-29 | `retrospective-stage-guardrails-logging-20260629/` | project-governance |
| 2026-06-29 | `retrospective-ai-agent-data-security-governance-20260629/` | project-governance |
| 2026-06-29 | `retrospective-raci-governance-matrix-20260629/` | project-governance |
| 2026-06-29 | `retrospective-daily-20260629-full-day/` | project-governance |
| 2026-06-30 | `retrospective-daily-review-and-forum-posting-20260630/` | project-governance |
| 2026-07-01 | `retrospective-short-command-context-rehydration-20260701/` | project-governance |
| 2026-07-01 | `retrospective-wsl-learning-plan-20260701/` | competitive-analysis |
| 2026-07-01 | `retrospective-wslc-vs-podman-comparison-20260701/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-offline-hardware-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-mouse-bm110-mm110-20260704/` | competitive-analysis |
| 2026-07-04 | `2026-07-04-oray-ai-analysis-retrospective.md` | task-reports |
| 2026-07-04 | `2026-07-04-knowledge-sedimentation-workflow-retrospective.md` | task-reports |
| 2026-07-05 | `retrospective-best-practice-docs-20260705/` | task-reports |
| 2026-07-05 | `retrospective-tvm-ffi-wiki-tutorial-20260705/` | task-reports/knowledge-content |
| 2026-06-30 | `retrospective-specforge-insight-20260629/` | competitive-analysis |
| 2026-06-30 | `retrospective-firecrawl-learning-20260629/` | insight-extraction/external-learning |
| 2026-06-30 | `retrospective-xinet-chaos-multiproject-analysis-20260625/` | insight-extraction/meta-methodology |
| 2026-06-30 | `retrospective-architecture-priority-20260629/` | insight-extraction/external-learning |
| 2026-06-24 | `retrospective-report-atomization-structure-optimization-20260624/` | atomization |
| 2026-06-25 | `retrospective-meta-atomization-ian-xiaohei-insights-20260625/` | atomization |
| 2026-06-25 | `retrospective-ian-xiaohei-source-analysis-20260625/` | competitive-analysis |
| 2026-06-29 | `retrospective-vendor-submodule-collaboration-20260629/` | spec-system |
| 2026-06-30 | `retrospective-tuyaopen-learning-report-optimization-20260630/` | competitive-analysis |
| 2026-07-01 | `retrospective-skill-facades-encoding-robustness-20260701/` | project-governance |
| 2026-07-02 | `retrospective-karpathy-multica-tutorial-20260702/` | competitive-analysis |
| 2026-07-02 | `agent-skills-standards-adoption-20260702/` | project-governance |
| 2026-07-02 | `retrospective-spec-adoption-tools-frontmatter-governance-20260702/` | project-reports |
| 2026-07-02 | `spec-adoption-batch-report.md` | project-reports |
| 2026-07-02 | `myst-to-agentspec-migration-analysis/` | standards-tools |
| 2026-07-03 | `retrospective-viitorvoice-tts-learning-20260703/` | competitive-analysis |
| 2026-07-03 | `retrospective-agent-proto-wiki-20260703/` | knowledge-content |
| 2026-07-04 | `retrospective-agnes-free-api-learning-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-claude-code-context-injection-learning-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-eve-framework-learning-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-headroom-wiki-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-mopmonk-wiki-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-bootbox-analysis-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-camera-su1-wiki-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-p4-p1pro-comparison-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-pdu-hardware-wiki-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-security-wiki-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-sunlogin-smart-socket-wiki-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-text-to-cad-learning-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-zleap-agent-harness-learning-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-dspark-wiki-20260704/` | competitive-analysis |
| 2026-07-04 | `retrospective-vibe-coding-prompts-learning-analysis-20260704/` | insight-extraction/external-learning |
| 2026-07-05 | `retrospective-scikit-build-core-wiki-20260705/` | project-reports |
| 2026-07-06 | `retrospective-sunlogin-cli-wiki-20260706/` | competitive-analysis |
| 2026-07-06 | `retrospective-sunlogin-comprehensive-analysis-20260706/` | competitive-analysis |
| 2026-07-06 | `retrospective-oray-comprehensive-analysis-20260706/` | competitive-analysis |
| 2026-07-06 | `retrospective-yct-onionhead-wiki-update-20260706/` | competitive-analysis |
| 2026-07-06 | `retrospective-papi-jiang-wiki-20260706/` | competitive-analysis |
| 2026-07-06 | `retrospective-agency-deep-learning-analysis-20260706/` | insight-extraction/external-learning |
| 2026-07-06 | `retrospective-codex-article-analysis-20260706/` | task-reports/insight-extraction/external-learning |
| 2026-07-06 | `retrospective-l0l3-template-design-20260706/` | task-reports |
| 2026-07-06 | `retrospective-mainecoon-article-analysis-20260706/` | task-reports |
| 2026-07-06 | `retrospective-zhihu-637007780-analysis-20260706/` | task-reports |
| 2026-07-07 | `retrospective-hiagent-platform-learning-20260707/` | competitive-analysis |
| 2026-07-07 | `retrospective-volcengine-ark-introduction-20260707/` | competitive-analysis |
| 2026-07-07 | `retrospective-volcengine-dual-product-learning-20260707/` | competitive-analysis |
| 2026-07-07 | `retrospective-volcengine-acep-learning-20260707/` | competitive-analysis |
| 2026-07-07 | `retrospective-volcengine-mua-learning-20260707/` | competitive-analysis |
| 2026-07-07 | `retrospective-vendor-check-module-20260707/` | task-reports |
| 2026-07-07 | `retrospective-ark-cli-submodule-integration-20260707/` | task-reports |
| 2026-07-07 | `retrospective-arkcli-setup-20260707/` | task-reports |
| 2026-07-07 | `retrospective-volcengine-mobile-use-agent-learning-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-volcengine-cua-learning-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-volcengine-mua-skill-api-guide-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-bonsai-canvas-agent-analysis-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-deep-code-analysis-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-karpathy-agent-fallacy-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-linus-fireside-chat-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-md2card-indie-dev-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-skillopt-analysis-20260707/` | insight-extraction/external-learning |
| 2026-07-07 | `retrospective-tutti-analysis-20260707/` | insight-extraction/external-learning |
| 2026-07-08 | `retrospective-session-20260708-overview/` | task-reports |
| 2026-07-08 | `retrospective-report-standardization-20260708/` | task-reports |
| 2026-07-08 | `retrospective-conflict-resolution-mechanism-20260708/` | task-reports |
| 2026-07-08 | `retrospective-concurrent-safety-checker-20260708/` | task-reports |
| 2026-07-08 | `retrospective-concurrent-report-atomization-20260708/` | task-reports |
| 2026-07-08 | `retrospective-analysis-dimension-template-library-20260708/` | task-reports |
| 2026-07-08 | `retrospective-minitest-ecosystem-learning-20260707/` | competitive-analysis |
| 2026-07-08 | `retrospective-mobile-use-deep-learning-20260707/` | competitive-analysis |
| 2026-07-08 | `retrospective-ai-regulation-analysis-20260708/` | competitive-analysis |
| 2026-07-08 | `retrospective-trae-v3-3-74-release-analysis-20260708/` | competitive-analysis |
| 2026-07-09 | `retrospective-generate-readme-tool-20260709/` | task-reports |
| 2026-07-23 | `retrospective-alipay-aipay-windows-install-20260723.md` | task-reports |
| 2026-07-23 | `retrospective-pickle-sedimentation-20260723/` | task-reports |
| 2026-08-05 | `retrospective-caffe-ffi-conv-v4-milestone-20260805.md` | task-reports |
| 2026-08-12 | `retrospective-xmnn-container-health-fix-20260812.md` | task-reports |
| 2026-08-19 | `retrospective-chaos-epub-books-classification-20260819.md` | task-reports |
| 2026-08-22 | `retrospective-jupyter-okf-wiki-group-20260822/` | competitive-analysis |
| 2026-08-24 | `insight-index-structure-duality-20260824.md` | documentation-governance |
| 2026-07-13 | `adversarial-reviews/adversarial-review-20260713T070637Z.md` 等 5 份 | adversarial-reviews |
| 2026-07-18 | `adversarial-reviews/adversarial-review-20260718T070940Z.md` 等 3 份 | adversarial-reviews |
| 2026-07-19 | `adversarial-reviews/adversarial-review-20260719T004345Z.md` 等 6 份 | adversarial-reviews |
| 2026-07-29 | `adversarial-reviews/adversarial-review-20260729T121427Z.md` 等 3 份 | adversarial-reviews |
| 2026-08-10 | `adversarial-reviews/adversarial-review-20260810T000044Z.md` | adversarial-reviews |
| 2026-08-14 | `adversarial-reviews/adversarial-review-20260814T100023Z.md` 等 8 份 | adversarial-reviews |
| 2026-08-19 | `adversarial-reviews/adversarial-review-20260819T093126Z.md` 等 3 份 | adversarial-reviews |
| 2026-07-21 | `bug-fix/docker-build/retrospective-conda-build-fix-20260721/` | bug-fix |
| 2026-07-22 | `bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/` | bug-fix |
| 2026-07-22 | `bug-fix/docker-build/retrospective-xmnn-nuitka-docker-runtime-20260722/` | bug-fix |
| 2026-07-22 | `bug-fix/docker-build/retrospective-xmnn-wheel-packaging-data-dirs-20260722/` | bug-fix |
| 2026-07-23 | `bug-fix/retrospective-xmnn-pytorch-integration-20260723/` | bug-fix |
| 2026-07-27 | `bug-fix/docker-build/retrospective-caffe-ops-correctness-test-20260727/` | bug-fix |
| 2026-08-01 | `bug-fix/cow-blob-cow-semantics-fix-20260801.md` | bug-fix |
| 2026-07-17 | `bugfix/retrospective-vta-hw-path-hardcode-fix-20260717/` | bugfix |
| 2026-07-18 | `bugfix/retrospective-ci-quality-gates-path-migration-20260718/` | bugfix |
| 2026-07-18 | `bugfix/retrospective-docker-commit-entrypoint-fix-20260718/` | bugfix |
| 2026-07-18 | `bugfix/retrospective-tvm-symbol-visibility-fix-20260718/` | bugfix |
| 2026-07-21 | `bugfix/retrospective-tvm-llvm-weak-symbol-leak-fix-20260721/` | bugfix |
| 2026-07-26 | `build-engineering/retrospective-xmnn-wheel-scikit-build-nuitka-20260726/` | build-engineering |
| 2026-07-27 | `build-engineering/retrospective-xmnn-runtime-docker-optional-pytorch-20260727/` | build-engineering |
| 2026-07-28 | `build-engineering/retrospective-caffe-ffi-protobuf7-build-20260728/` | build-engineering |
| 2026-07-29 | `build-engineering/retrospective-cmake-atomization-caffe-ffi-round2-20260729/` | build-engineering |
| 2026-08-01 | `build-engineering/docker-build-verification-caffe-ffi-20260801.md` | build-engineering |
| 2026-08-02 | `build-engineering/retrospective-nativebuild-automation-20260802/` | build-engineering |
| 2026-08-07 | `build-engineering/retrospective-devcontainer-base-seven-concepts-20260807/` | build-engineering |
| 2026-08-07 | `build-engineering/retrospective-docker-buildkit-observability-20260807.md` | build-engineering |
| 2026-08-08 | `build-engineering/insight-onnx-quantization-benchmark-analysis-20260808.md` | build-engineering |
| 2026-08-10 | `build-engineering/retrospective-xmnn-four-layer-release-pipeline-20260810/` | build-engineering |
| 2026-08-11 | `build-engineering/retrospective-chaos-ai-portable-docker-20260811/` | build-engineering |
| 2026-08-12 | `build-engineering/summary-palmdet-compile-fix-20260812.md` | build-engineering |
| 2026-08-13 | `build-engineering/retrospective-ai-dev-variant-bugfix-logging-20260813/` | build-engineering |
| 2026-08-14 | `build-engineering/retrospective-devcontainer-conda-libmamba-ft-v2.1-20260814/` | build-engineering |
| 2026-08-16 | `build-engineering/retrospective-onnx-quantize-kit-test-coverage-20260816.md` | build-engineering |
| 2026-08-19 | `build-engineering/troubleshooting-devcontainer-jupyter-gil-20260819.md` | build-engineering |
| 2026-08-20 | `build-engineering/retrospective-llama-cpp-python-cuda-build-20260820/` | build-engineering |
| 2026-07-21 | `code-optimization/retrospective-caffe-rmsnorm-transpose-removal-20260721/` | code-optimization |
| 2026-07-23 | `code-optimization/retrospective-caffe-slim-tvm-ffi-20260723/` | code-optimization |
| 2026-07-27 | `code-optimization/retrospective-caffe-ops-library-extraction-20260727/` | code-optimization |
| 2026-07-28 | `code-optimization/retrospective-demo-ffi-math-ops-boundary-perf-20260728/` | code-optimization |
| 2026-07-31 | `code-optimization/retrospective-split-zerocopy-cow-milestone-20260731/` | code-optimization |
| 2026-08-01 | `code-optimization/retrospective-task11-cow-fix-20260801/` | code-optimization |
| 2026-08-02 | `code-optimization/report-batch-hardening-float-precision-20260802/` | code-optimization |
| 2026-08-03 | `code-optimization/report-pooling-backward-gradient-routing-20260803/` | code-optimization |
| 2026-07-22 | `environment-setup/retrospective-wsl-ubuntu2604-install-migration-20260722/` | environment-setup |
| 2026-08-15 | `environment-setup/retrospective-wsl-docker-gpu-fix-20260815/` | environment-setup |
| 2026-08-18 | `environment-setup/retrospective-docker-cache-to-wsl-migration-20260818/` | environment-setup |
| 2026-08-19 | `environment-setup/retrospective-windows-desktop-icons-missing-20260819/` | environment-setup |
| 2026-08-19 | `environment-setup/retrospective-py314t-conda-freethreading-20260819.md` | environment-setup |
| 2026-07-21 | `feature-development/retrospective-caffeproto-l2norm-20260721.md` | feature-development |
| 2026-08-07 | `feature-development/retrospective-skill-auto-loader-20260807.md` | feature-development |
| 2026-07-18 | `iteration-reports/retrospective-config-file-placement-governance-20260718/` | iteration-reports |
| 2026-07-20 | `iteration-reports/weekly-2026-07-20/` | iteration-reports |
| 无日期后缀 | 其余全部报告（在文件名中以 `retrospective-report-*` 或 `retrospective-insight-*` 命名） | 各分类 |

### 4.2 按关键词查找

| 关键词 | 对应分类 | 匹配报告（示例） |
|---|---|---|
| 原子化、模块化、拆分、重构、迁移、提取、元级原子化、信息增殖、目录结构优化、三层冗余消除、四阶段渐进式重构 | `atomization/` | 全部 12 份报告 |
| 洞察、萃取、元分析、方法论、提炼、优化循环、演进、DeerFlow、Agent Harness、Super Agent、Sandbox、MCP、Sub-agents、架构对比、五层架构、两档结构、九节叙事弧、双受众萃取、体道链、文档熵增、Specs文档体系、TuyaOpen、IoT SDK、嵌入式AI、TAL/TKL、LLM适配器、消息总线、配置驱动、本地优先架构、Home Assistant、IoT集成、设备分类矩阵、数据中心映射、DP Code、多语言文档分离、Smart Life、二维码授权、Device Sharing SDK、实体基类、类型数据抽象、设备监听器、Cloud Push、官方集成标准化、渐进式设备支持、简化用户体验、device-handlers、诊断JSON、My Button、DeviceWrapper、事件驱动状态更新、MQTT推送、dispatcher机制、设备分类映射、Quirks扩展、设备处理程序、可选模块设计、dataclass、pathlib、dry-run、配置化参数、Tuya IPC、最小闭环、XLSX、测试报告学习、规格前置、Markdown 导出、XMNN、Nuitka、scikit-build-core、wheel、TVM/VTA 运行时、LLVM 21、离线部署、运行镜像、方法论迁移、迁移案例、复用验证、npu-project-hub、运行时基线、llvm-dev、挂载权限、零漂移、bind mount、非 root 验证、fix_mount_permissions、显式确认、导出建议执行、验证优先、过度抽象、消费者数量、规范沉淀、语义准确性、完成状态语义 | `insight-extraction/` | 全部 24 份报告 |
| 规范、Spec、一致性、成熟度、命名、事实表述、看板、任务清单、主题分类、三层架构、看管建、需求澄清、Mermaid可视化、模板闭环、Vendor子模块、flexloop、AGENTS路由嵌套、嵌套规范路由、三层路由 | `spec-system/` | 全部 9 份报告 |
| 角色、团队、co-founder、联合创始 | `roles-teams/` | 全部 3 份报告 |
| 项目治理、应用目录、系统规划、Code Wiki、工具熵、导出、启动协议、AGENTS、Demo、制作流程、交互增强、证据闭环、竹简悟道、归档、参赛作品、自包含验证、选择性归档、骨架门禁分离、洞察库重组、文件拆分、交叉引用、结构债务、标题层级、四层结构、Mermaid渲染、兼容性修复、断链修复、链接校验、路径校正、自动修复工具、dry-run、看板漂移、阶段守卫、SG-LOG、PDR-LOG、三路径分类、RACI、责任矩阵、审批模型、A唯一性、R≠A分离、双列设计、数据安全、分类分级、出境评估、脱敏加密、供应商管理、监控应急、五层治理架构、国标合规、论坛自动化、共享库、测试计划、单日复盘、波次节奏、四层递进、Git、本地克隆、refs、--no-local、短指令、上下文重建、参数澄清、Skill门面化、编码鲁棒性、ToolCall校验、防御性编程、Agent Skills开放标准、SKILL.md、A2A/MCP/ACP协议、三层架构（capabilities/tools/evals）、规范落地度量、Frontmatter治理闭环、全局加权评分、批量对比报告、规范健康度 | `project-governance/` | 全部 36 份 + 1 独立报告 |
| 竞品分析、赛事分析、Competitive、SWOT、增长飞轮、风险识别、参赛策略、差异化优势、学习资料、Demo 生成、初赛指南、人气分、Session ID、认知锚点、配图、AI Skill、角色设计、风格克制、原子化视觉、Claude Tag、SpecForge、WSL、wslc、Container API、hvsocket、plan9、drvfs、mini_init、三源三角验证、preview API、CLI 短形态、通信通道拓扑、API 投影分层、Podman、Docker 替代、容器方案对比、隔离模型、rootless、CNI、OCI 标准、契约匹配、选型决策树、向日葵、Sunlogin、IPKVM、无网远控、远程控制硬件、KVM、HDMI采集、USB仿真、4G/5G远控、物理隔离、BIOS级控制、远控鼠标、智能鼠标、MM110、BM110、智能PDU、智能插座、插线板、功耗差异、三层漏斗、双产品矩阵、逐行配图教程、插画设计、小黑宋、SpecForge结构化、涂鸦Open、报告优化、学习指南、语音合成、ViiTorVoice、TTS、实时生成、长文本优化、流式输出、Karpathy、multi-cast、多智能体、Claude Code、上下文注入、400K token、Context Engineering、Eve框架、移动开发、Text-to-CAD、生成式设计、免费API、Agnes AI、21个免费模型、PPIO、Headroom、实时视频AI、虚拟形象、MopMonk、硬件测试、系统测试、无网远控启动U盘、BootBox、离线远控U盘、4G智能摄像头、SU1、硬件对比评测、P4 vs P1Pro、安全风险、摄像头安全、智能插座、智能家居远程控制、开源项目Wiki、技术文档分析、贝锐、Oray、Zleap-Agent、Agent Harness、Workspace-first、本地小模型、Context Engineering、Agent Loop、记忆系统、多模型协作、Prompt→Loop→Harness、上下文治理、记忆三层治理、经验记忆脱敏、Channel Fracture、OpenClaw、Hermes Agent、WildClawBench、Agentic Harness Engineering | `competitive-analysis/` | 全部 25 份报告 |
| 知识内容、Wiki教程、Agent通信协议、A2A、MCP、ACP、技术文档、类比锚点、自包含约束、Spec Mode三段式、PRD→tasks→checklist、Mermaid图 | `knowledge-content/` | 全部 1 份报告 |
| 标准评估、工具评估、Markdown标准、MyST、reStructuredText、Directives、Roles、Sphinx、文档迁移、可行性评估、解析器审计、六维技术支持评估、MDI/API/ABI/MCP/ACP/A2A、LLM×Sphinx融合、MyST-NB、可执行文档、三方案对比 | `standards-tools/` | 全部 1 份报告 |
| 项目报告、独立报告、Dockerfile、层缓存、.dockerignore、构建速度优化、规范度量、批量对比、Frontmatter治理 | `project-reports/` | 全部 3 份独立报告 + 2 份原子化复盘 |
| 任务复盘、任务执行、Spec Mode、403处理、信息源兜底、外部网站访问障碍、贝锐、Oray、蒲公英、花生壳、洋葱头、OrayClaw、AI产品矩阵、MCP远程控制、AI网关、分层兜底策略、元复盘、知识沉淀工作流、子代理三不准、暂存区污染、Git提交卫生、子代理越权提交、原子提交、vendor管理、子模块、跨平台测试、调试日志、ark-cli、SSO配置、OAuth、CLI工具、测试覆盖、代码分支分析、README自动生成、标记区域、增量更新、文档覆盖、索引更新、docgen、caffe-ffi、OpenMP、Conv v4、并行优化、双层并行隔离、OMP抖动诊断、CV%、P99/P50、自适应线程数、环境变量自检、容器健康、unhealthy、健康探针、ENABLE_SSH、ENABLE_DOCKER、探针-部署模式对齐、supervisorctl | `task-reports/` | 全部 22 份报告 |
| 文档治理、toctree、toc.not_included、index.md 结构、okf-spec 风格、trae-skills 风格、层级路由、扁平索引、Sphinx构建、invocations、构建警告治理 | `documentation-governance/` | 全部 3 份报告 |
| 对抗审查、魔鬼代言人、证伪、对抗性评审、adversarial review、边界试探、反例搜索 | `adversarial-reviews/` | 全部 29 份报告 |
| COW、OverlayFS、Docker构建修复、conda构建、PyTorch集成、Nuitka运行时、数据目录、正确性测试 | `bug-fix/` | 全部 7 份报告 |
| CI质量门、Docker entrypoint、TVM/LLVM符号、VTA硬编码、弱符号泄漏、符号可见性 | `bugfix/` | 全部 5 份报告 |
| Docker、DevContainer、conda、Nuitka、CMake、scikit-build-core、发布流水线、镜像构建、Jupyter、GPU、free-threading镜像、LLM构建 | `build-engineering/` | 全部 37 份报告（29 原子化 + 8 独立） |
| 算子优化、零拷贝、FFI、精度、COW、卷积、池化、反向梯度、blob形状、ELU | `code-optimization/` | 全部 22 份报告 |
| WSL、Docker GPU、free-threading、conda 3.14t、桌面图标、缓存迁移、Ubuntu 26.04 | `environment-setup/` | 全部 5 份报告 |
| L2Norm算子、Skill自动加载器、功能开发、CaffeProto | `feature-development/` | 全部 2 份报告 |
| 迭代、周复盘、周报、weekly、配置放置治理 | `iteration-reports/` | 全部 2 份报告 |

### 4.3 按报告类型查找

| 报告类型 | 说明 | 涉及报告 |
|---|---|---|
| 项目结项复盘 | 针对具体项目的完整复盘，含项目概述、执行过程、洞察与导出建议 | 绝大多数报告（如 `retrospective-report-agents-spec-system/`、`retrospective-report-code-wiki-generation/` 等） |
| 综合复盘 | 多维度、多阶段的综合性回顾，模块数超过 4 个 | `retrospective-comprehensive-20260623/`（6 模块） |
| 元分析 | 对多个报告或跨会话数据进行元级分析 | `retrospective-meta-analysis-cross-project/`、`retrospective-meta-atomization-full-chain-20260624/` |
| 洞察报告 | 以知识萃取和方法论提炼为核心目标的报告 | `retrospective-insight-optimization-cycle/`、`retrospective-session-insight-extraction-readme-evolution-20260624/` |
| 导出卡片 | 将知识资产清单化，便于快速查阅与复用 | `retrospective-export-20260623/` |
| 优化报告 | 针对流程、工具或文档体系的专项优化分析 | `retrospective-report-tool-entropy-nonlinear-optimization/`、`reports-duplication-optimization-report.md` |
| 故障修复复盘 | 针对具体故障/问题的根因分析与修复过程复盘，含工具增强方案 | `retrospective-mermaid-rendering-fix-20260626/`、`retrospective-link-fix-depth-adjustment-20260626/`、`retrospective-llvm-dev-mount-permission-fix-20260702/` |
| 竞品分析报告 | 对外部产品、赛事或活动的结构化分析，含多维框架与策略洞察 | `retrospective-trae-contest-faq-analysis-20260624/` |
