---
id: "retrospective-reports-index"
title: "复盘报告分类索引"
x-toml-ref: "../../../.meta/toml/docs/retrospective/reports/README.toml"
---
# 复盘报告分类索引

> 本文档为 `docs/retrospective/reports/` 目录下全部复盘报告的完整分类索引，提供按主题、日期、关键词和报告类型的多维度快速查找功能。

## 一、分类标准

复盘报告按内容主题划分为 10 个一级分类，各分类的定义与边界如下：

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
| `project-reports/` | 项目级独立报告 | 以单文件 Markdown 形式交付的完整复盘报告（非原子化子目录结构），以及独立的项目结项复盘、规范度量批量报告。关注"简洁交付的项目级总结"。 |
| `task-reports/` | 任务执行复盘 | 单任务执行过程的完整复盘报告，包含Spec Mode流程回顾、问题处理、经验沉淀。关注"单次任务执行的全过程复盘与可复用模式提取"。 |

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

### insight-extraction/（31 份原子化报告 + 5 份独立洞察卡片）

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

#### external-learning/（6 份）— 外部开源项目与技术文章学习

对外部优秀开源项目、竞品、技术文章的分析与学习复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/` | 竹简悟道 Specs 文档体系深度分析，含文档五层架构、洞察两档结构等 9 个核心元洞察 |
| `external-learning/retrospective-deer-flow-2-learning-20260625/` | DeerFlow 2.0 学习复盘，含 Super Agent Harness 架构范式、Markdown Skills 系统等 4 个可复用架构模式 |
| `external-learning/retrospective-ai-code-assistant-project-analysis-20260625/` | AI 编程学习助手项目代码分析，含 AI 应用 MVP 最小架构、提示词分层设计等模式萃取 |
| `external-learning/retrospective-firecrawl-learning-20260629/` | Firecrawl 系统学习复盘：AI 网页数据接口的技术架构、商业模式与战略洞察 |
| `external-learning/retrospective-architecture-priority-20260629/` | 架构优先级评估与重构路线图：基于 Firecrawl 8 洞察 |
| `external-learning/retrospective-skills-article-learning-20260629/` | Skills 技术文章学习复盘，含Agent知识喂给范式演进等5项核心洞察 |

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

#### standalone/（5 份独立洞察卡片）

独立洞察卡片（单文件形式，不属于特定原子化报告）。

| 文件 | 简要说明 |
|---|---|
| `standalone/insight-temp-file-discipline-20260701.md` | 临时文件路径规范执行卡点洞察 |
| `standalone/insight-tuyaopen-folder-20260630.md` | TuyaOpen 目录洞察报告 |
| `standalone/insight-windows-git-encoding-20260701.md` | Windows Git 非 ASCII 提交信息编码陷阱洞察 |
| `standalone/insight-dockerfile-caching-20260703.md` | Dockerfile 层缓存与开发环境镜像构建七条深层洞察 |
| `retrospective-myst-unified-ecosystem-phase1-20260705/` | MyST统一化生态体系阶段1核心洞察索引：3洞察+4经验+3问题+2模式+4机会+4行动项，可复用知识库检索入口 |

### spec-system/（9 份）

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

### roles-teams/（3 份）

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-report-cofounder-improvement-execution/` | 联合创始改进建议执行复盘，含声明即校验模式与知识形态三阶跃迁 |
| `retrospective-report-cofounder-role-marker/` | 联合创始角色特殊标记复盘，含零侵入扩展范式与双点一致原则 |
| `retrospective-report-teams-module/` | 团队管理模块创建复盘，含约定驱动创建、规范层纵深防御、自举规范 |

### project-governance/（36 份 + 1 独立报告）

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
| `reports-duplication-optimization-report.md` | 复盘报告体系重复内容优化报告（独立报告，无对应目录） |

### competitive-analysis/（28 份）

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
| `retrospective-mopmonk-wiki-20260704/` | MopMonk安全Agent Wiki教程创建与原子化复盘，安全Agent开源项目wiki教程原子化拆分与知识沉淀 |
| `retrospective-sunlogin-bootbox-analysis-20260704/` | 向日葵开机盒子K3/K4产品深度分析项目复盘报告，开机盒子产品系统性学习与深度分析 |
| `retrospective-sunlogin-camera-su1-wiki-20260704/` | 向日葵USB远程摄像头SU1 Wiki教程项目复盘报告，USB远程摄像头产品系统性学习与深度洞察Wiki教程创建 |
| `retrospective-sunlogin-p4-p1pro-comparison-20260704/` | 向日葵P4/P1Pro对比学习Wiki项目复盘报告，智能插线板P4（4G版）与P1Pro（WiFi版）系统性对比学习与深度洞察分析 |
| `retrospective-sunlogin-pdu-hardware-wiki-20260704/` | 向日葵智能PDU硬件Wiki教程项目复盘报告，智能PDU（P8一代WiFi版/P8二代4G版）产品系统性学习与洞察分析Wiki教程创建 |
| `retrospective-sunlogin-security-wiki-20260704/` | 向日葵远程控制安全产品Wiki教程项目复盘报告，远程控制安全产品页面系统性学习与深度洞察Wiki教程创建 |
| `retrospective-sunlogin-smart-socket-wiki-20260704/` | 向日葵智能插座Wiki教程项目复盘报告，智能插座C1Pro/C2/C4三款产品系统性学习Wiki教程创建 |
| `retrospective-text-to-cad-learning-20260704/` | text-to-cad开源项目学习Wiki教程创建复盘，开源项目介绍文章学习、结构化wiki教程创建与知识库归档 |

### project-reports/（3 份独立报告 + 4 份原子化复盘）

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

### task-reports/（5 份）

任务执行复盘目录，存放以单文件或原子化目录形式交付的单次任务完整复盘报告。

| 文件/目录 | 简要说明 | 日期 | 类型 |
|---|---|---|---|
| `retrospective-best-practice-docs-20260705/` | 最佳实践文档整理复盘：将TVM FFI复盘中的两个洞察（高层文档优先研究法L2、工具故障三级降级策略L1）整理为模式库独立文档，2个新模式文档+3个索引更新，验证"复盘洞察→模式库平滑转化法"流程 | 2026-07-05 | task |
| `retrospective-tvm-ffi-wiki-tutorial-20260705/` | TVM FFI跨语言FFI框架Wiki教程创建任务复盘，在Shell管道耗尽/WebFetch超时/Read超时三重基础设施故障下，通过Vendor AGENTS.md高层文档优先+4个并行子代理分组写作完成17个文档（约5870行）交付，提炼"高层文档优先研究法""工具故障三级降级""主题分组并行写作"3个可复用模式，其中2个达到L2成熟度（2次验证）。 | 2026-07-05 | task |
| [2026-07-04 贝锐AI产品矩阵分析任务复盘](task-reports/2026-07-04-oray-ai-analysis-retrospective.md) | 对贝锐20周年AI产品矩阵系统性分析任务的完整复盘，包含Spec Mode执行流程回顾、403访问问题处理、1309行分析报告产出总结，沉淀了"外部网站分析信息源分层兜底策略"可复用模式。 | 2026-07-04 | task |
| [2026-07-04 知识沉淀工作流元复盘](task-reports/2026-07-04-knowledge-sedimentation-workflow-retrospective.md) | 对"复盘→洞察→萃取→导出→提交"完整知识沉淀工作流的元复盘，分析子代理越权提交、暂存区污染、导出验证发现9个问题等关键事件，提炼子代理"三不准"规范、增强版知识沉淀SOP、Git暂存区卫生五步法，新建2个L1模式+1个L2模式更新。 | 2026-07-04 | task |
| `retrospective-tech-interface-wiki-20260703/` | 技术接口概念Wiki教程创建复盘（已归入knowledge-content/，此处保留历史记录） | 2026-07-03 | task |

### knowledge-content/（2 份）

知识库内容建设目录，存放技术Wiki、通信协议教程等知识体系化内容的创建复盘。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `retrospective-tvm-ffi-wiki-tutorial-20260705/` | TVM FFI跨语言FFI框架Wiki教程复盘，17个文档/约5870行交付，Shell管道耗尽/WebFetch超时/Read超时三重故障下完成，Vendor高层文档优先研究法、工具故障三级降级、主题分组并行写作3个可复用模式萃取（2个P0/L2） |
| `retrospective-agent-proto-wiki-20260703/` | Agent通信协议Wiki教程复盘，13个文档/4286行/34个Mermaid图交付，Spec Mode三段式（PRD→tasks→checklist）零章节遗漏验证，子agent自包含约束、类比锚点教学法等6个可复用模式萃取 |

### standards-tools/（1 份）

标准与工具评估目录，存放Markdown语法标准、规范迁移可行性、工具链技术评估等分析报告。

| 报告名称（原子化目录） | 简要说明 |
|---|---|
| `myst-to-agentspec-migration-analysis/` | MyST Directives/Roles系统在Agent Spec开发中的可迁移性技术评估（v1.2.0），66份存量文档统计分析、解析器代码审计、六维技术支持评估（MDI/API/ABI/MCP/ACP/A2A）、LLM×Sphinx生态融合7个创新场景、MyST-NB可执行文档专题、保守/平衡/激进三方案对比，12章原子化交付 |

## 三、文件组织规则

`docs/retrospective/reports/` 目录下的文件组织遵循以下规则：

### 3.1 主题子文件夹

10 个主题子文件夹分别存放对应主题的复盘报告。各文件夹内以原子化子目录为主；`insight-extraction/` 下额外包含 `standalone/` 子目录存放独立洞察卡片（单文件形式，不属于特定原子化报告）；`project-reports/` 以独立单文件报告为主。

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

1. **判定归属分类**：根据报告主题，对照「一、分类标准」表格确定应归入的一级分类目录。若现有 8 个分类均无法覆盖，应先讨论是否新增分类，而非直接放入根目录。
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
| 2026-07-05 | `retrospective-scikit-build-core-wiki-20260705/` | project-reports |
| 无日期后缀 | 其余全部报告（在文件名中以 `retrospective-report-*` 或 `retrospective-insight-*` 命名） | 各分类 |

### 4.2 按关键词查找

| 关键词 | 对应分类 | 匹配报告（示例） |
|---|---|---|
| 原子化、模块化、拆分、重构、迁移、提取、元级原子化、信息增殖、目录结构优化、三层冗余消除、四阶段渐进式重构 | `atomization/` | 全部 12 份报告 |
| 洞察、萃取、元分析、方法论、提炼、优化循环、演进、DeerFlow、Agent Harness、Super Agent、Sandbox、MCP、Sub-agents、架构对比、五层架构、两档结构、九节叙事弧、双受众萃取、体道链、文档熵增、Specs文档体系、TuyaOpen、IoT SDK、嵌入式AI、TAL/TKL、LLM适配器、消息总线、配置驱动、本地优先架构、Home Assistant、IoT集成、设备分类矩阵、数据中心映射、DP Code、多语言文档分离、Smart Life、二维码授权、Device Sharing SDK、实体基类、类型数据抽象、设备监听器、Cloud Push、官方集成标准化、渐进式设备支持、简化用户体验、device-handlers、诊断JSON、My Button、DeviceWrapper、事件驱动状态更新、MQTT推送、dispatcher机制、设备分类映射、Quirks扩展、设备处理程序、可选模块设计、dataclass、pathlib、dry-run、配置化参数、Tuya IPC、最小闭环、XLSX、测试报告学习、规格前置、Markdown 导出、XMNN、Nuitka、scikit-build-core、wheel、TVM/VTA 运行时、LLVM 21、离线部署、运行镜像、方法论迁移、迁移案例、复用验证、npu-project-hub、运行时基线、llvm-dev、挂载权限、零漂移、bind mount、非 root 验证、fix_mount_permissions、显式确认、导出建议执行、验证优先、过度抽象、消费者数量、规范沉淀、语义准确性、完成状态语义 | `insight-extraction/` | 全部 24 份报告 |
| 规范、Spec、一致性、成熟度、命名、事实表述、看板、任务清单、主题分类、三层架构、看管建、需求澄清、Mermaid可视化、模板闭环、Vendor子模块、flexloop、AGENTS路由嵌套、嵌套规范路由、三层路由 | `spec-system/` | 全部 9 份报告 |
| 角色、团队、co-founder、联合创始 | `roles-teams/` | 全部 3 份报告 |
| 项目治理、应用目录、系统规划、Code Wiki、工具熵、导出、启动协议、AGENTS、Demo、制作流程、交互增强、证据闭环、竹简悟道、归档、参赛作品、自包含验证、选择性归档、骨架门禁分离、洞察库重组、文件拆分、交叉引用、结构债务、标题层级、四层结构、Mermaid渲染、兼容性修复、断链修复、链接校验、路径校正、自动修复工具、dry-run、看板漂移、阶段守卫、SG-LOG、PDR-LOG、三路径分类、RACI、责任矩阵、审批模型、A唯一性、R≠A分离、双列设计、数据安全、分类分级、出境评估、脱敏加密、供应商管理、监控应急、五层治理架构、国标合规、论坛自动化、共享库、测试计划、单日复盘、波次节奏、四层递进、Git、本地克隆、refs、--no-local、短指令、上下文重建、参数澄清、Skill门面化、编码鲁棒性、ToolCall校验、防御性编程、Agent Skills开放标准、SKILL.md、A2A/MCP/ACP协议、三层架构（capabilities/tools/evals）、规范落地度量、Frontmatter治理闭环、全局加权评分、批量对比报告、规范健康度 | `project-governance/` | 全部 36 份 + 1 独立报告 |
| 竞品分析、赛事分析、Competitive、SWOT、增长飞轮、风险识别、参赛策略、差异化优势、学习资料、Demo 生成、初赛指南、人气分、Session ID、认知锚点、配图、AI Skill、角色设计、风格克制、原子化视觉、Claude Tag、SpecForge、WSL、wslc、Container API、hvsocket、plan9、drvfs、mini_init、三源三角验证、preview API、CLI 短形态、通信通道拓扑、API 投影分层、Podman、Docker 替代、容器方案对比、隔离模型、rootless、CNI、OCI 标准、契约匹配、选型决策树、向日葵、Sunlogin、IPKVM、无网远控、远程控制硬件、KVM、HDMI采集、USB仿真、4G/5G远控、物理隔离、BIOS级控制、远控鼠标、智能鼠标、MM110、BM110、智能PDU、智能插座、插线板、功耗差异、三层漏斗、双产品矩阵、逐行配图教程、插画设计、小黑宋、SpecForge结构化、涂鸦Open、报告优化、学习指南、语音合成、ViiTorVoice、TTS、实时生成、长文本优化、流式输出、Karpathy、multi-cast、多智能体、Claude Code、上下文注入、400K token、Context Engineering、Eve框架、移动开发、Text-to-CAD、生成式设计、免费API、Agnes AI、21个免费模型、PPIO、Headroom、实时视频AI、虚拟形象、MopMonk、硬件测试、系统测试、无网远控启动U盘、BootBox、离线远控U盘、4G智能摄像头、SU1、硬件对比评测、P4 vs P1Pro、安全风险、摄像头安全、智能插座、智能家居远程控制、开源项目Wiki、技术文档分析、贝锐、Oray | `competitive-analysis/` | 全部 24 份报告 |
| 知识内容、Wiki教程、Agent通信协议、A2A、MCP、ACP、技术文档、类比锚点、自包含约束、Spec Mode三段式、PRD→tasks→checklist、Mermaid图 | `knowledge-content/` | 全部 1 份报告 |
| 标准评估、工具评估、Markdown标准、MyST、reStructuredText、Directives、Roles、Sphinx、文档迁移、可行性评估、解析器审计、六维技术支持评估、MDI/API/ABI/MCP/ACP/A2A、LLM×Sphinx融合、MyST-NB、可执行文档、三方案对比 | `standards-tools/` | 全部 1 份报告 |
| 项目报告、独立报告、Dockerfile、层缓存、.dockerignore、构建速度优化、规范度量、批量对比、Frontmatter治理 | `project-reports/` | 全部 3 份独立报告 + 2 份原子化复盘 |
| 任务复盘、任务执行、Spec Mode、403处理、信息源兜底、外部网站访问障碍、贝锐、Oray、蒲公英、花生壳、洋葱头、OrayClaw、AI产品矩阵、MCP远程控制、AI网关、分层兜底策略、元复盘、知识沉淀工作流、子代理三不准、暂存区污染、Git提交卫生、子代理越权提交、原子提交 | `task-reports/` | 全部 3 份报告 |

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
