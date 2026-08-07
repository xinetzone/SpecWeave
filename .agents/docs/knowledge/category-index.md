# 分类总索引

- [返回知识库首页](README.md)
- [按标签检索](tags/README.md)

## 统计摘要

- **总条目数**：1138

| 分类 | 数量 |
|------|------|
| architecture | 1 |
| best-practices | 43 |
| case-study | 5 |
| decisions | 5 |
| docs | 8 |
| docs/knowledge/mdi/generated/case1 | 1 |
| docs/knowledge/mdi/generated/case3 | 1 |
| examples | 6 |
| knowledge | 55 |
| knowledge/best-practices | 1 |
| knowledge/learning | 5 |
| knowledge/learning/01-agent-protocols-interfaces | 8 |
| knowledge/learning/01-agent-protocols-interfaces/agent-communication-protocols | 12 |
| knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki | 15 |
| knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki | 16 |
| knowledge/learning/02-agent-engineering-methodology | 2 |
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
| knowledge/learning/llm-token-optimization | 1 |
| knowledge/learning/okr-wiki | 1 |
| knowledge/learning/okr-wiki/appendix | 1 |
| knowledge/learning/okr-wiki/concepts | 6 |
| knowledge/learning/okr-wiki/implementation | 6 |
| knowledge/learning/okr-wiki/methods | 4 |
| knowledge/learning/okr-wiki/scoring | 4 |
| knowledge/learning/okr-wiki/templates | 7 |
| knowledge/learning/okr-wiki/tools | 2 |
| learning | 422 |
| methods | 6 |
| operations | 19 |
| platform | 1 |
| reference | 3 |
| research | 1 |
| standards | 1 |
| tech | 29 |
| troubleshooting | 4 |
| unknown | 225 |

## 按类别浏览

### architecture

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | SpecWeave项目治理方法论体系的架构总览文档，定义了治理基建四层递进核心模型，以及围绕该模型形成的5个可复用元洞察模式，包含模式间关系、落地状态和自反性验证案例。 | 2026-06-30 | governance、architecture、methodology、stage-guardrails、patterns、four-layer-model、governance-loop、retrospective、meta-insights |

### best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [AI拟人化互动服务极端情绪干预机制技术实施方案](best-practices/ai-anthropomorphic-crisis-intervention-implementation.md) | 针对《人工智能拟人化互动服务管理暂行办法》第13条要求，设计极端情绪/自残自杀干预机制的完整技术实施方案，包含系统架构、识别引擎、分级干预、运营后台、测试验收和7天上线排期 | 2026-07-08 | AI合规、极端情绪干预、安全机制、拟人化互动、技术方案 |
| [异步生成接口'两段式'轮询模式](best-practices/api-async-polling-pattern.md) | 通用异步生成接口的'两段式'调用模式：前台提交任务获取 task/episode ID，后台轮询直到完成。涵盖执行模型、提交/轮询示例脚本、轮询参数表与完成/失败/超时处理。 | 2026-08-07 | API、异步、轮询、后台任务、curl、jq、两段式 |
| [API 错误处理与重试策略](best-practices/api-error-handling-retry-strategy.md) | 标准响应结构 {code,message,data} 契约、HTTP 状态码处理表、应用错误码表与分层重试策略（429 指数退避、5xx 重试、网络错误重试）。 | 2026-08-07 | API、错误处理、重试、HTTP状态码、指数退避、响应契约 |
| [API 集成模式组合实战示例：AI 播客自动生成](best-practices/api-integration-worked-example.md) | 以一个'从长文章自动生成 AI 播客'的业务场景为骨架，演示如何组合复用四项通用 API 集成模式（交互式参数收集、@file 长文本、异步两段式轮询、错误处理与重试），给出端到端编排与可运行脚本。 | 2026-08-07 | API、示例、工作流、播客、AskUserQuestion、异步轮询、@file、重试、端到端 |
| [AskUserQuestion 分步交互式收集参数模式](best-practices/api-interactive-parameter-collection.md) | 用 AskUserQuestion 分步交互式收集 API 参数的模式：一次一问、等回答、执行前确认、可回退；多选用 AskUserQuestion、自由文本用普通消息、依赖参数串行、独立参数可批量。 | 2026-08-07 | API、AskUserQuestion、交互、参数收集、多选、自由文本、会话 |
| [用 @file 传长文本请求体](best-practices/api-long-text-file-parameter.md) | 当请求体文本过长（如整篇文章）时，用 curl 的 -d @file 从临时文件读取请求体，绕过 shell 命令行参数长度限制。含何时使用、临时文件写法与用后清理。 | 2026-08-07 | API、curl、长文本、@file、临时文件、shell参数限制 |
| [归档搭配Wiki联动机制指南](best-practices/archive-wiki-linkage-guide.md) | SpecWeave项目中归档（retrospective）与Wiki（learning wiki）联动的标准化操作指南，明确定位区别、升级判定标准、双向关联机制、Wiki化SOP与模板结构，实现从过程记录到系统化知识的价值升华。 | 2026-07-31 | archive、wiki、knowledge-management、retrospective、learning-wiki、知识沉淀、归档升级、联动机制 |
| [Python AST静态分析实践：五类消歧法降低误报](best-practices/ast-static-analysis-disambiguation.md) | 基于并发安全检查器（六维检查法）开发实战，总结Python AST静态分析中降低误报的五类消歧策略，帮助开发者编写准确的代码检查工具。核心原则：宁可漏报，不可误报。 | 2026-07-08 | AST、static-analysis、python、false-positive、code-quality、automation |
| [Caffe-FFI Layer开发必查：param_propagate_down_初始化陷阱](best-practices/caffe-ffi-param-propagate-down-initialization.md) |  | 2026-08-03 | caffe-ffi、layer、backward、bug-pattern、c++、initialization、segfault、access-violation |
| [恒等层 COW 零拷贝分离原则（输入梯度与参数梯度分离）](best-practices/caffe-identity-layer-cow-separation.md) |  | 2026-08-04 | caffe-ffi、cow、zerocopy、scale、bias、eltwise、backward、grad、bug-pattern、c++、identity-layer |
| [Caffe层Backward验证标准工作流（L1-L2-L3三层法）](best-practices/caffe-layer-backward-validation-workflow.md) |  | 2026-08-03 | caffe-ffi、backward、testing、workflow、three-layer-validation、gradient-check、c++、numpy、numerical-gradient |
| [Caffe AVE Pooling梯度路由：均匀分配模式](best-practices/caffe-pooling-ave-gradient-routing.md) |  | 2026-08-03 | caffe-ffi、pooling、backward、gradient-routing、ave-pooling、c++、numpy、test-pattern |
| [Caffe MAX Pooling梯度路由：Winner-Takes-All模式](best-practices/caffe-pooling-max-gradient-routing.md) |  | 2026-08-03 | caffe-ffi、pooling、backward、gradient-routing、max-pooling、c++、numpy、test-pattern |
| [IDE Agent 环境下 CLI 工具配置操作手册](best-practices/cli-setup-in-agent-environment.md) | 针对团队新人的 IDE Agent（Trae/Claude Code 等）环境下 CLI 工具配置操作手册：基于 arkcli 安装配置实战，提炼通用方法论——安装验证→沙箱权限预判→非交互式认证→配置验证四步法，涵盖常见坑点、排错 Checklist 和决策矩阵。 | 2026-07-07 | cli、setup、agent-environment、sandbox、sso、non-interactive、arkcli、newbie-guide、npm |
| [CMake项目模块化重构最佳实践](best-practices/cmake-modularization-best-practices.md) |  | 2026-07-29 | CMake、modularization、build-system、refactoring、cross-platform、best-practice |
| [编译型Python包数据文件生命周期管理](best-practices/compiled-package-data-file-lifecycle.md) | 基于TVM .rly数据文件缺失修复实战复盘，提炼编译型Python包数据文件的完整生命周期管理方法：编译阶段显式复制、打包阶段完整性验证、运行阶段环境变量设置与文件校验。 | 2026-07-23 | Python、Nuitka、Cython、wheel、data-files、packaging、TVM、relay |
| [并发代码安全审查与Bug修复闭环指南](best-practices/concurrent-code-safety-review.md) | 基于多智能体冲突解决机制实现与死锁修复实战复盘，提炼并发模块安全审查六维检查法、调度类模块N-scaling测试矩阵、Bug修复1+N+1闭环公式等5个可复用洞察，提供原子提交前的完整Checklist模板。 | 2026-07-08 | concurrency、deadlock-prevention、code-review、defensive-programming、bug-fix、checklist、tdd |
| [conda-forge 交叉编译配置完整指南](best-practices/conda-forge-cross-compilation-guide.md) | conda-forge 交叉编译配置完整调研报告，覆盖从 linux-64 构建 osx-64/osx-arm64/win-64 平台包的完整方案：平台三元组、工具链包名清单、conda_build_config.yaml模板、meta.yaml依赖分离、build.sh交叉编译检测、CMAKE_ARGS变量传递、scikit-build-core适配、Wine运行时测试、常见陷阱与解决方案。 | 2026-07-30 | conda-forge、cross-compilation、conda-build、CMake、scikit-build-core、Docker、Wine、macOS、Windows、toolchain、RPATH |
| [配置文件放置治理与 .temp/ 临时文件约定](best-practices/config-file-placement-convention.md) | SpecWeave 项目关键配置文件的标准存放路径、放置决策树、Python 自动加载约定（sitecustomize.py / .pth / PYTHONPATH 关系）、sitecustomize.py 曾被错放根目录的根因分析，以及 .temp/ 临时文件的用途分类、命名规则、保留期与清理机制。 | 2026-07-18 | - |
| [DAG图变换算法验证最佳实践](best-practices/dag-graph-transform-verification.md) |  | 2026-08-01 | dag、graph-transform、visualization、verification、caffe、insert-splits、in-place |
| [DataLoader Pickle 序列化问题诊断 SOP](best-practices/dataloader-pickle-diagnosis-sop.md) | DataLoader pickle 序列化问题诊断标准流程，整合诊断指南与检查清单精华。5 步流程 + 6 种不可序列化模式 + 3 种修复方案 + 跨启动模式验证矩阵，适用于 Python 3.14 forkserver 兼容性排查。 | 2026-07-23 | Python、pickle、serialization、multiprocessing、DataLoader、diagnosis、SOP、checklist |
| [目录迁移五步法检查清单](best-practices/directory-migration-checklist.md) |  | 2026-07-18 | - |
| [Docker镜像更新的声明式优先原则](best-practices/docker-declarative-first-principle.md) | 基于xmnn-client Docker commit入口配置泄漏修复实战复盘，提炼Docker镜像更新的声明式优先原则：优先使用Dockerfile声明式构建，docker commit仅用于快速原型验证，避免运行时状态隐式继承导致的配置泄漏。 | 2026-07-23 | Docker、Dockerfile、docker-commit、declarative、image-build、containerization |
| [并发安全八维检查法技术规格](best-practices/eight-dimensions-concurrent-safety-spec.md) |  | 2026-07-08 | concurrent-safety、AST、static-analysis、eight-dimensions、check-rules、pre-commit |
| [文件 I/O 并发安全规范：原子写入、日志模板与重试策略](best-practices/file-io-concurrency-safety.md) | 基于原子写入重构实战（11个模块统一改造、46个测试覆盖、并发成功率82%→100%），提炼文件I/O并发安全三原则：写共享文件必须原子化、日志必须分阶段计时、重试必须有限次+退避。提供决策树、日志模板、重试参数规范和完整代码示例，作为所有涉及文件写入的脚本必须遵守的开发规范。 | 2026-07-12 | concurrency、file-io、atomic-write、logging、retry-pattern、windows、defensive-programming |
| [硬编码路径批量修复工具使用指南（fix-hardcoded-paths.py）](best-practices/fix-hardcoded-paths-guide.md) | 可复用硬编码路径批量修复工具使用指南：正则保留分隔符风格与盘符大小写，支持 .py/.ipynb 双处理与 dry-run/apply 双模式。 | 2026-08-07 | hardcoded-paths、refactor、python、path-migration、dry-run、ipynb、script |
| [浮点数精度测试技术指南](best-practices/float-precision-testing-guide.md) |  | 2026-08-02 | float32、precision、testing、ulp、numerical-gradient、c1-kink、sigmoid、elu、activation-functions |
| [链式pre-commit钩子架构实践指南](best-practices/git-hook-chain-architecture.md) | 基于敏感信息检测和并发安全检查两个pre-commit钩子的实战经验，总结链式pre-commit钩子架构模式——单Shell入口+Python链式主入口+独立检查模块，解决跨平台维护、检查顺序控制和扩展成本问题。 | 2026-07-08 | git-hooks、pre-commit、architecture、cross-platform、automation |
| [手算梯度已知值验证：Backward测试L1层方法论](best-practices/hand-computed-gradient-verification.md) |  | 2026-08-03 | testing、backward、gradient、verification、known-values、hand-computed、numpy、test-pattern、caffe-ffi |
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | SpecWeave 项目中 Mermaid 图表的一站式操作手册，涵盖起步模板、安全编码六规则、自动化检查工具详解、渲染问题排查流程和不同图表类型注意事项。 | 2026-06-29 | mermaid、图表、可视化、check-mermaid、安全编码、六规则、模板、ci |
| [模型调用环境变量脱敏模板（.env 字段清单）](best-practices/model-env-template.md) | 从 chaos/flexloop/models/.env 沉淀的脱敏环境变量模板：列出字段名与用途说明，所有值一律使用占位符，绝不含真实密钥或个人路径。 | 2026-08-07 | env、environment-variable、desensitization、glm、huggingface、zai |
| [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md) | 基于IDL Wiki章节拆分实战复盘的多文件编辑操作可靠性指南：涵盖章节拆分级联编号成本、Edit工具精确匹配陷阱、串行vs并行Edit策略、Windows管道稳定性四条核心经验，提供决策矩阵和操作Checklist。 | 2026-07-05 | edit、multi-file、reliability、serial-vs-parallel、windows-pipe、cascading-renumber、wiki-split、tool-pitfalls |
| [数值梯度诊断日志规范：从失败到根因的可观测性](best-practices/numerical-gradient-diagnostic-logging.md) |  | 2026-08-03 | debugging、numerical-gradient、logging、diagnostics、observability、grad-check、caffe-ffi、pytest |
| [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md) | 基于MDI项目parser.py（1465行）重构复盘的经验总结：处理半结构化数据（Markdown/自然语言/配置文件）的Parser应预留2-3倍于Generator的时间/代码量预算，遵循三层架构拆分，并先写20+边界case测试。 | 2026-07-03 | parser、复杂度预算、semi-structured-parsing、三层架构、边界case、TDD、checklist |
| [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md) | 分类处置决策树(Classification-Disposition Decision Tree)与三阶段渐进推广验证(Phased Rollout Validation)两个L2治理模式的第3次验证报告。验证场景为复盘模板v1.2批量标准化升级（61个项目），验证了模式在轻量级模板升级场景下的有效性，记录了P1批量执行后集中格式校验的新增实践。 | 2026-07-06 | pattern-validation、L2-pattern、phased-rollout、classification-disposition、batch-upgrade、governance、methodology-evolution |
| [从实战到工具：三段式PDF导出、Mermaid全量扫描与三个工程洞察](best-practices/pdf-export-mermaid-automation-insights.md) | 从一次Mermaid漏斗图重绘与PDF导出任务中萃取的工程经验：三段式中文Markdown+Mermaid PDF导出法、Mermaid全量扫描自动化、以及三个核心工程洞察（工具选择熟悉度偏差、无头浏览器DOM检测原则、自动化检查的免费质量提升）。 | 2026-07-11 | pdf导出、mermaid、playwright、pandoc、自动化、工程洞察、工具封装、质量保证 |
| [Python大版本升级破坏性变更检查清单](best-practices/python-version-upgrade-compatibility-check.md) | 基于xmnn-client Python 3.14迁移实战复盘，提炼Python大版本升级的破坏性变更检查清单，重点关注multiprocessing默认行为变更、弃用/移除模块、AST节点变更等隐蔽陷阱。 | 2026-07-23 | Python、version-upgrade、compatibility、multiprocessing、breaking-changes、checklist |
| [C/C++共享库符号可见性控制最佳实践](best-practices/symbol-visibility-control.md) | 基于TVM符号可见性控制修复实战复盘，提炼共享库符号可见性精确控制方法、--exclude-libs,ALL最佳实践、静态注册机制保护策略等核心洞察，提供完整的符号冲突诊断与修复指南。 | 2026-07-18 | C/C++、linker、symbol-visibility、shared-library、LLVM、TVM、CMake、anti-pattern |
| [测试基础设施性能优化最佳实践](best-practices/test-infra-performance-optimization.md) |  | 2026-08-03 | performance、gc、profiling、pytest、conftest、csv-buffering、observability、test-infrastructure、caffe-ffi |
| [TRAE Agent 沙箱配置与使用最佳实践指南](best-practices/trae-agent-sandbox-guide.md) |  | 2026-07-20 | sandbox、security、agent-environment、configuration、trae、best-practices、newbie-guide |
| [VsDevShell 模块 API 参考文档](best-practices/vsdevshell-api-reference.md) | VsDevShell.psm1 通用模块完整API参考，包含多策略VS安装发现、DevShell环境加载、PATH自动恢复等功能 | 2026-08-02 | powershell、visual-studio、msvc、build-tools、api-reference、module |
| [Windows环境零摩擦开发指南](best-practices/windows-zero-friction-development-guide.md) |  | 2026-08-01 | windows、compatibility、powershell、encoding、cross-platform、checklist |
| [Wrapper脚本注入模式](best-practices/wrapper-script-injection-pattern.md) | 基于xmnn Nuitka编译包Python 3.14兼容性修复实战复盘，提炼wrapper脚本注入模式：通过纯Python包装脚本在导入编译产物前注入运行时配置，实现不侵入源码的兼容性修复。 | 2026-07-23 | Python、wrapper、runpy、compiled-package、runtime-patch、compatibility |

### case-study

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Awesome OKF 深度分析 - 事实清单（R阶段）](learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-analysis/01-facts.md) |  | 2026-08-06 | okf、awesome-okf、事实、retrospective |
| [Awesome OKF 深度分析 - 本质洞察（I+F阶段）](learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-analysis/02-insights.md) |  | 2026-08-06 | okf、awesome-okf、洞察、insight、first-principles |
| [Awesome OKF 深度分析 - 模式萃取（E阶段）](learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-analysis/03-patterns.md) |  | 2026-08-06 | okf、awesome-okf、模式、pattern、extraction |
| [Awesome OKF 深度分析 - 对抗性审查（V阶段）](learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-analysis/04-adversarial-review.md) |  | 2026-08-06 | okf、awesome-okf、对抗审查、adversarial-review、v-stage |
| [Awesome OKF 深度分析 - 原子行动项（A阶段）](learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-analysis/05-action-items.md) |  | 2026-08-06 | okf、awesome-okf、行动项、action-items、atomization |

### decisions

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由 | 2026-06-23 | architecture、naming、directory、vendor、convention |
| [ADR: VsDevShell通用模块提取与NativeBuild推广决策](decisions/nativebuild-vsdevshell-module-extraction.md) | 记录NativeBuild模块在vendor/flexloop推广评估中的三项关键决策：NativeBuild不直接推广到vendor、Conda逻辑不适配uv、提取VsDevShell为独立通用模块 | 2026-08-02 | native-build、powershell、module-design、visual-studio、conda、uv、decoupling |
| [SpecWeave 外部代理资产绑定边界](decisions/p0-04-specweave-binding-decision.md) | 记录 chaos 与 SpecWeave 的跨工作区代理资产绑定决策，包括绑定路径、用途、访问顺序、适用边界和维护规则。 |  | - |
| [已批准治理 Specs 稳定决策集合](decisions/p0-08-governance-specs-decisions.md) | 从 7 个已批准治理 specs 中提炼的稳定决策结论集合，覆盖协作文档三件套基线、临时知识库管道、归档自动化、SpecWeave 外部绑定、任务分类骨架、待办治理口径与归档优先级分级。 |  | - |
| [DAO Apps 商业计划书结论摘要](decisions/p1-12-daoapps-business-plan.md) | DAO Apps 商业计划书结论，定义以「道法自然」为哲学基石的 AI 智能体应用生态，包含产品矩阵、商业模式、市场定位与 500 万元融资需求。 |  | - |

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

### docs/knowledge/mdi/generated/case1

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [用户管理 API](mdi/generated/case1/user-management-api.md) |  | 2026-07-02 | - |

### docs/knowledge/mdi/generated/case3

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [文件操作 CLI 工具](mdi/generated/case3/file-cli.md) |  | 2026-07-02 | - |

### examples

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [文件操作 CLI 工具](mdi/examples/file-cli.md) |  | 2026-07-02 | - |
| [数据生成 API](mdi/examples/generate-api.md) |  | 2026-07-02 | - |
| [博客平台 GraphQL API](mdi/examples/graphql-blog-cn.md) |  | 2026-07-02 | - |
| [Blog GraphQL API](mdi/examples/graphql-blog.md) |  | 2026-07-02 | - |
| [Todo API](mdi/examples/todo-api.md) |  | 2026-07-02 | - |
| [用户管理 API](mdi/examples/user-api.md) |  | 2026-07-02 | - |

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
| [AI硬件设计工具生态深度洞察报告——基于《10个AI硬件设计常用网站》的系统分析](learning/06-business-trends-analysis/ai-hardware-design-tools-wiki/analysis-report.md) |  | 2026-08-01 | ai-hardware、eda、pcb-design、circuit-design、ai-tools、hardware-startup、maker |
| [LLM Token节省机制研究文档 V阶段对抗审查记录](learning/llm-token-optimization/07-adversarial-review.md) |  | 2026-08-01 | LLM、Token、Optimization、Adversarial-Review、V-Gate |
| [LLM Token优化知识体系元分析](learning/llm-token-optimization/08-meta-analysis.md) |  | 2026-08-01 | LLM、Token、Optimization、Meta-Analysis、Taxonomy、Evolution |
| [Token优化禁止事项清单（约束驱动）](learning/llm-token-optimization/09-constraints.md) |  | 2026-08-01 | LLM、Token、Optimization、Constraints、Anti-Patterns、Guardrails |
| [Token优化快速参考卡（3分钟速查）](learning/llm-token-optimization/10-quick-reference.md) |  | 2026-08-01 | LLM、Token、Optimization、Quick-Reference、Cheat-Sheet |
| [LLM Token 优化术语表](learning/llm-token-optimization/glossary.md) |  | 2026-08-01 | - |
| [LLM Token 优化参考文献](learning/llm-token-optimization/references.md) |  | 2026-08-01 | - |
| [大语言模型Token优化第一性原理分析](learning/llm-token-optimization/01-principles/01-first-principles.md) |  | 2026-08-01 | LLM、Token、First-Principles、Transformer、Self-Attention、KV-Cache、Optimization |
| [LLM Token优化工具与框架调研报告](learning/llm-token-optimization/03-tools/01-tool-survey.md) |  |  | LLM、Token优化、推理引擎、Prompt缓存、Token压缩 |
| [Token优化决策框架总览](learning/llm-token-optimization/06-decision-framework/00-framework-overview.md) |  | 2026-08-01 | LLM、Token、Optimization、Decision-Framework、Best-Practices |
| [Token优化场景决策树](learning/llm-token-optimization/06-decision-framework/01-decision-tree.md) |  | 2026-08-01 | LLM、Token、Optimization、Decision-Tree、Scenarios |
| [Token优化技术选型矩阵](learning/llm-token-optimization/06-decision-framework/02-selection-matrix.md) |  | 2026-08-01 | LLM、Token、Optimization、Selection-Matrix、ROI |
| [Token优化可复用最佳实践模式](learning/llm-token-optimization/06-decision-framework/03-patterns.md) |  | 2026-08-01 | LLM、Token、Optimization、Patterns、Best-Practices、G3-Verified |
| [Token优化反模式与常见误区](learning/llm-token-optimization/06-decision-framework/04-anti-patterns.md) |  | 2026-08-01 | LLM、Token、Optimization、Anti-Patterns、Pitfalls |
| [Token优化快速启动Checklist](learning/llm-token-optimization/06-decision-framework/05-quick-checklist.md) |  | 2026-08-01 | LLM、Token、Optimization、Checklist、Launch、Preflight |
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
| [Protobuf Wiki - 总览](learning/01-agent-protocols-interfaces/protobuf-wiki/00-overview.md) |  | 2026-07-23 | - |
| [Protobuf Wiki - 版本演进时间轴](learning/01-agent-protocols-interfaces/protobuf-wiki/01-version-timeline.md) |  | 2026-07-23 | - |
| [Protobuf Wiki - 三版对比矩阵](learning/01-agent-protocols-interfaces/protobuf-wiki/02-version-comparison.md) |  | 2026-07-23 | - |
| [Protobuf Wiki - 核心功能演进](learning/01-agent-protocols-interfaces/protobuf-wiki/03-feature-evolution.md) |  | 2026-07-23 | - |
| [Protobuf Wiki - 选型决策指南](learning/01-agent-protocols-interfaces/protobuf-wiki/04-selection-guide.md) |  | 2026-07-23 | - |
| [Protobuf Wiki - 迁移指南](learning/01-agent-protocols-interfaces/protobuf-wiki/05-migration-guide.md) |  | 2026-07-23 | - |

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

### knowledge/learning/llm-token-optimization

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [LLM Token节省策略实际应用案例集](learning/llm-token-optimization/04-cases/01-case-studies.md) |  | 2026-08-01 | - |

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
| [GraphQL 教程总览](learning/01-agent-protocols-interfaces/graphql-wiki/00-overview.md) | GraphQL 系统性技术教程总览，涵盖定义、核心概念、五大设计支柱、与 REST 对比、查询示例、章节导航与前置知识要求。 | 2026-08-05 | graphql、api、query-language、overview、tutorial |
| [GraphQL 核心概念](learning/01-agent-protocols-interfaces/graphql-wiki/01-core-concepts.md) | GraphQL 核心概念详解，涵盖查询语言与运行时组成、Schema Definition Language (SDL)、三种操作类型、字段与参数、解析器机制、设计原则及核心术语通俗解释。 | 2026-08-05 | graphql、api、query-language、core-concepts、sdl、resolver、schema |
| [GraphQL 查询语言](learning/01-agent-protocols-interfaces/graphql-wiki/02-queries.md) | GraphQL 查询语言完整指南，涵盖字段选择、参数、别名、片段、操作名称、变量、指令、变更操作和内联片段，每个语法点配有 Star Wars 主题的代码示例与 JSON 返回示例。 | 2026-08-05 | graphql、api、query-language、fields、arguments、aliases、fragments、variables、directives、mutations |
| [GraphQL Schema 与类型系统](learning/01-agent-protocols-interfaces/graphql-wiki/03-schema-types.md) | GraphQL Schema 与类型系统完整指南，涵盖标量类型、对象类型、根类型、枚举、接口、联合类型、输入类型、列表与非空修饰符，每个类型配有 Star Wars 主题的 SDL 代码示例。 | 2026-08-05 | graphql、api、schema、type-system、scalar-types、object-types、enums、interfaces、unions、input-types、lists、non-null |
| [GraphQL 验证与执行](learning/01-agent-protocols-interfaces/graphql-wiki/04-validation-execution.md) | GraphQL 验证与执行完整指南，涵盖执行流程、查询验证、Resolver 工作原理、执行策略、响应格式、错误处理、内省查询，并配有概念性 Resolver 示例。 | 2026-08-05 | graphql、api、validation、execution、resolver、introspection、error-handling、breadth-first |
| [GraphQL 客户端基础](learning/01-agent-protocols-interfaces/graphql-wiki/05-client-basics.md) | GraphQL 客户端基础完整指南，涵盖客户端库对比、原生 HTTP 请求方法、请求头设置、GraphiQL IDE 使用、curl 和 fetch 示例，以及客户端缓存与本地状态管理基础。 | 2026-08-05 | graphql、api、client、apollo-client、relay、urql、fetch、curl、graphiql、caching |
| [GraphQL 服务端核心概念](learning/01-agent-protocols-interfaces/graphql-wiki/06-server-concepts.md) | GraphQL 服务端开发基础完整指南，涵盖服务端架构概述、Schema 开发模式、Context 上下文、Resolver 最佳实践、错误处理、中间件、HTTP 集成、部署安全考虑，以及 Hello World 示例。 | 2026-08-05 | graphql、api、server、schema、resolver、context、dataloader、middleware、cors、n+1-problem |
| [Python GraphQL 生态](learning/01-agent-protocols-interfaces/graphql-wiki/07-python-ecosystem.md) | Python GraphQL 生态完整指南，涵盖主流服务端框架对比（Graphene、Strawberry、Ariadne）、Web 框架集成（FastAPI、Django、Flask）、客户端库（gql）、底层核心实现与测试工具，包含可运行的 Strawberry+FastAPI 服务端和 gql 客户端完整示例。 | 2026-08-05 | graphql、python、graphene、strawberry、ariadne、fastapi、django、flask、gql-client、graphql-core |
| [GraphQL 最佳实践](learning/01-agent-protocols-interfaces/graphql-wiki/08-best-practices.md) | GraphQL 全面最佳实践指南，涵盖 Schema 设计、性能优化、安全防护、错误处理、开发工具链以及常见反模式，包含 SDL 代码对比示例和可落地的工程实践建议。 | 2026-08-05 | graphql、best-practices、schema-design、performance、security、error-handling、anti-patterns |
| [GraphQL 术语表与参考资料](learning/01-agent-protocols-interfaces/graphql-wiki/11-glossary.md) | GraphQL 核心术语表与参考资料索引，包含26个核心术语的中文翻译与通俗解释，以及官方资源、Python工具链、推荐文章和社区资源汇总，同时回顾本教程覆盖的知识点并给出下一步学习建议。 | 2026-08-05 | graphql、glossary、reference、terminology、resources |
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
| [00 Knowledge Catalog概述与知识地图](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/00-overview.md) | Knowledge Catalog（原Dataplex）是Google Cloud推出的AI驱动数据目录与元数据管理平台，包含OKF开放知识格式、参考Agent实现、可视化工具链和示例数据集，为AI Agent提供语义层和业务上下文 | 2026-08-06 | Knowledge Catalog、Dataplex、OKF、知识目录、数据目录、知识图谱、AI Agent、wiki教程 |
| [01 核心概念与平台架构](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/01-core-concepts.md) | 深入解析Knowledge Catalog平台的三大设计哲学、核心概念体系、OKF格式规范要点、四层平台架构，以及组件间关系的可视化说明 | 2026-08-06 | Knowledge Catalog、OKF、知识管理、平台架构、Bundle、Attested Computation |
| [02 OKF开放知识格式规范深度解析](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/02-okf-specification.md) | 从knowledge-catalog参考实现视角深度解析OKF v0.2规范，覆盖Bundle结构、Frontmatter必填/推荐字段、链接规则、信任与来源机制、认证计算、合规性规则及版本变更，大量交叉链接指向okf-wiki完整教程 | 2026-08-06 | Knowledge Catalog、OKF、规范解析、Bundle、Frontmatter、Attested Computation、Conformance |
| [03 参考Agent实现原理与运行指南](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/03-reference-agent.md) | 从源码角度深度解析knowledge-catalog参考Agent的实现机制，包括两阶段工作流架构、enrich子命令完整参数说明、核心工具模块（bundle/source/web/context）、CLI使用示例、单概念迭代开发方法以及GCP凭证配置指南 | 2026-08-06 | Knowledge Catalog、OKF、Reference Agent、实现原理、CLI、BigQuery、Web Crawler、两阶段工作流 |
| [04 工具链与可视化系统](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/04-toolchain-and-visualization.md) | 系统讲解Knowledge Catalog可视化系统的功能特性与技术架构，包括力导向图谱、详情面板、反向链接、搜索筛选等交互功能；详解mdcode元数据即代码工具（语义层、BigQuery集成、MCP服务器、pull/push双向同步）和enrichment智能充实Agent；介绍GA4、Stack Overflow、比特币区块链三个官方样例项目 | 2026-08-06 | Knowledge Catalog、OKF、Visualization、Cytoscape.js、Toolchain、Metadata as Code、Enrichment Agent、MCP、BigQuery |
| [05 示例Bundle深度解析](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/05-samples-and-bundles.md) | 深度解析Google官方提供的4个OKF示例Bundle：GA4电商数据集演示单表+指标文档结构，Stack Overflow演示多表+joins+枚举引用，比特币区块链演示紧密关联表+跨表外键关系，Acme Retail演示企业级Attested Computation完整用法（metrics/computations/policies/skills/attesters）；同时详解okf/samples/目录下recipe配方与Bundle的对应关系，帮助读者通过实例掌握OKF规范 | 2026-08-06 | Knowledge Catalog、OKF、Bundle、Sample、GA4、Stack Overflow、Bitcoin、Acme Retail、Attested Computation、Recipe |
| [06 集成模式与最佳实践](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/06-integration-patterns.md) | 详解OKF在企业环境中的落地路径与集成模式：包括试点→团队级→企业级→生态的四阶段渐进式落地路径，数据目录同步、Agent知识库构建、企业Runbook/Playbook管理三种典型集成场景，与Unity Catalog/Collibra等现有数据目录的共存集成方案，Git工作流深度集成（PR评审、版本管理、知识演进），生产者-消费者解耦架构模式，扩展字段设计的最佳实践，以及10条核心最佳实践清单 | 2026-08-06 | Knowledge Catalog、OKF、Integration、Enterprise、Data Catalog、Git Workflow、Best Practices、Runbook、Agent Knowledge、Unity Catalog、Collibra |
| [07 架构决策与方案对比](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/07-architecture-decisions.md) | 客观呈现OKF/Knowledge Catalog作为早期方案的风险与局限性，详细对比传统RAG向量库、Notion/Obsidian文档工具、Unity Catalog、Collibra、Confluence、MkDocs、dbt docs、其他Agent知识方案共8种主流替代方案的优劣势与适用场景，提供架构选型决策树，并给出全面的风险评估与缓解策略，帮助技术决策者理性判断是否采用以及如何稳妥落地 | 2026-08-06 | Knowledge Catalog、OKF、Architecture Decision、Comparison、Risk Assessment、Data Catalog、Unity Catalog、Collibra、Confluence、dbt docs、RAG、Agent Knowledge |
| [08 资源与术语表](learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/08-resources-and-glossary.md) | 30+核心术语定义（覆盖Knowledge Catalog、OKF、参考Agent、工具链）、完整官方资源链接、项目内wiki交叉引用索引、学习路径建议 | 2026-08-06 | Knowledge Catalog、OKF、术语表、资源链接、Glossary、References、Dataplex、工具链 |
| [00 OKF概述与知识地图](learning/01-agent-protocols-interfaces/okf-wiki/00-overview.md) | OKF是Google Cloud 2026年6月发布的开放知识表示规范，定位为AI时代的HTML，采用Markdown+YAML纯文件格式，目标是成为Agent四层架构中独立的知识层标准 | 2026-08-05 | OKF、Open Knowledge Format、知识标准、Agent、知识层、wiki教程 |
| [01 核心概念与设计哲学](learning/01-agent-protocols-interfaces/okf-wiki/01-core-concepts.md) | 深入解析OKF的极简设计哲学：最少约定、生产者消费者解耦、格式而非平台；完整介绍Bundle/Concept/Frontmatter等核心概念和规范 | 2026-08-05 | OKF、设计原则、Frontmatter、Bundle、Concept |
| [02 5分钟快速入门](learning/01-agent-protocols-interfaces/okf-wiki/02-quickstart.md) | OKF零安装零依赖，6个步骤创建一个Agent工具知识库Bundle（3个工具Concept+index+log），5分钟完成并通过三规则验证 | 2026-08-05 | OKF、Quickstart、快速上手、实操、零依赖 |
| [03 使用模式与最佳实践](learning/01-agent-protocols-interfaces/okf-wiki/03-usage-patterns.md) | 覆盖数据目录、Agent知识库、团队Runbook三种典型场景，详解扩展字段、链接设计、渐进式文档化、自动化脚本、Git集成等最佳实践 | 2026-08-05 | OKF、使用场景、最佳实践、自动化、Git工作流 |
| [04 局限性与方案对比](learning/01-agent-protocols-interfaces/okf-wiki/04-limitations-and-comparison.md) | 客观呈现OKF的早期阶段风险、已知局限性，与8种常见知识管理方案做优劣势对比，提供选型决策树，帮助读者理性判断是否采用 | 2026-08-05 | OKF、局限性、风险、方案对比、选型 |
| [05 架构定位与Agent集成](learning/01-agent-protocols-interfaces/okf-wiki/05-architecture-and-integration.md) | OKF作为Agent四层架构独立知识层的定位，与MCP连接层、Skills程序层的互补关系，生产者消费者解耦架构，以及企业渐进式落地四阶段路径 | 2026-08-05 | OKF、Agent架构、MCP、Skills、知识层、企业落地 |
| [06 FAQ与最佳实践](learning/01-agent-protocols-interfaces/okf-wiki/06-faq-and-best-practices.md) | 收集12个最常见问题并给出简明解答，总结8条核心最佳实践，提供10项生产上线前检查清单 | 2026-08-05 | OKF、FAQ、常见问题、最佳实践、检查清单 |
| [07 资源与术语表](learning/01-agent-protocols-interfaces/okf-wiki/07-resources-and-glossary.md) | 20+核心术语定义，完整的官方资源链接、相关标准链接、本项目内相关wiki交叉引用索引 | 2026-08-05 | OKF、术语表、资源链接、Glossary、References |
| [01 OKF 生态资源图谱](learning/01-agent-protocols-interfaces/okf-wiki/okf-ecosystem-wiki/01-ecosystem-map.md) | OKF上游英文生态（awesome-okf/linyiru）的资源分类图谱与'awesome 列表批转合规范 bundle'的 dogfooding 工程实现原理 | 2026-08-06 | OKF、生态图谱、ecosystem、build-okf-bundle、awesome-okf |
| [02 OKF Bundle 分发注册机制](learning/01-agent-protocols-interfaces/okf-wiki/okf-ecosystem-wiki/02-bundle-registry.md) | OKF bundle 如何通过 registry.yaml 机器可读索引实现社区分发与消费，含字段schema、消费流程、校验规则与许可政策 | 2026-08-06 | OKF、bundle、registry、okf-kit、分发、awesome-okf-kit |
| [03 OKF Bundle 工程化发布模板](learning/01-agent-protocols-interfaces/okf-wiki/okf-ecosystem-wiki/03-bundle-template.md) | 把网站发布为自更新 OKF bundle 的工程化模板：CI 构建、每周同步、release 打包、注册表接入的完整工作流 | 2026-08-06 | OKF、bundle、template、okf-kit、github-actions、CI/CD |
| [Agent Skills（Addy Osmani）完整学习教程：谷歌Gemini团队的AI编程代理人工程技能库](learning/02-agent-engineering-methodology/agent-skills-wiki.md) | 谷歌Gemini团队主管Addy Osmani开源的AI编程代理人生产级工程技能库完整教程，GitHub星标1.9万+，围绕6阶段生命周期定义20个核心技能，配套7个斜杠命令，深度融入Google工程文化（Hyrum定律/测试金字塔/Chesterton栅栏/左移等）。 | 2026-07-08 | ai-agent、engineering-workflow、google-engineering、agent-skills、best-practices、addy-osmani、gemini |
| [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md) | 阿里技术发布的Harness Engineering深度文章学习笔记，系统讲解从Prompt Engineering到Context Engineering再到Harness Engineering的范式演进，包含四条反直觉铁律、六大工程模式、悟空AI招聘实战案例、行业标杆地图、未来趋势与六条心法。 | 2026-07-04 | Harness Engineering、Agent Engineering、AI Agent、多Agent系统、Prompt Engineering、Context Engineering |
| [Harness七大组件Wiki教程](learning/02-agent-engineering-methodology/harness-seven-components-wiki.md) |  | 2026-07-13 | harness、七大组件、agent、业务底座 |
| [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md) | 系统学习Headroom AI Agent上下文压缩中间件，掌握给Agent装'压缩层'的完整技术方案，实现1万Token压到1千且质量不降反升，涵盖六种压缩算法、CCR可逆机制、四种接入方式、跨Agent记忆与自动学习等核心特性。 | 2026-07-04 | headroom、context-compression、agent、middleware、token-optimization、ccr、ai-agent |
| [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md) | 源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则（编码前先思考/简约至上/精确编辑/目标驱动），一个CLAUDE.md文件管住AI编程最常犯的毛病。GitHub 61.6k星项目完整教程，包含背景故事、核心原则详解、真实代码正反例、四种分发格式安装指南（CLAUDE.md/Cursor Rules/SKILL.md/插件）、Multica平台架构与multica-cli Skill使用指南、仓库文件结构说明，以及在SpecWeave项目中的整合情况。本文档已原子化，详细内容见 karpathy-llm-coding-guidelines/ 子目录。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude、ai-programming、agentic-engineering、claude-code、cursor、skills、plugin、mdc、multica、multica-cli、managed-agents |
| [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md) | 基于郭震AI实测经验，系统学习美团LongCat-2.0（1.6T参数MoE模型）接入Claude Code的完整流程，涵盖架构解析、配置指南、BI数据看板项目实战、Token效率对比和Loop Engineering方法论。 | 2026-07-04 | longcat、agent、claude-code、moe、loop-engineering、ai-coding、meituan |
| [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md) | 学习分析卡兹克《Vibe Coding 两大神级 Prompt》一文：第一性原理(管生成)与对抗式审查(管验证)构成完整闭环,是 Vibe Coding 的两大基石。含本项目亲身践行验证案例（含反面教材）及元方法论自举验证。 | 2026-07-04 | vibe-coding、prompt、第一性原理、对抗式审查、ai-agent、代码审查、multi-agent、aihot、可复用模式、践行鸿沟、类比推理 |
| [Agent评测方法论：核心术语表](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/glossary.md) |  | 2026-08-05 | agent-evaluation、glossary、methodology |
| [知乎文章：别再给Agent跑分了——谈谈评测体系化建设](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/zhihu-article-agent-eval-methodology.md) | 面向知乎的Agent评测体系化建设科普文章，用痛点引入、生动案例、通俗类比讲解评测方法论，并分享Wiki创作经验。 | 2026-08-05 | zhihu-article、agent-evaluation、methodology、popularization |
| [知乎文章：用方法论编排，而不是靠灵感——我如何用seven-concepts-cmd产出了一整部Wiki教程](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/zhihu-article-seven-concepts-wiki-creation.md) | 复盘一次用seven-concepts-cmd方法论编排技能产出Agent评测方法论Wiki教程的完整过程：R建立事实清单、F从本质重构框架、I提炼反常识洞察、E有据撰写、V四视角对抗审查，以及五道质量门如何保证产出质量。分享方法论编排如何把'写教程'从'堆资料'变成'构建可复用的方法论体系'。 | 2026-08-05 | zhihu-article、seven-concepts、methodology、wiki-creation、creation-experience |
| [模块1：Agent评测方法论概述](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/01-overview/01-methodology-overview.md) | 界定Agent评测体系化建设的本质问题，阐明其业务价值，给出评测能力成熟度模型（0-5级），并剖析4个最常见的认知误区。 | 2026-08-05 | agent-evaluation、methodology、maturity-model、misconception、quality-loop |
| [模块2：核心评测框架对比](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/02-frameworks/02-core-frameworks.md) | 深度对比HELM、MT-Bench、AgentBench、AutoEval、τ-bench、AgentBoard六大评测框架，给出基于8个维度的横向对比表与选型决策树。 | 2026-08-05 | agent-evaluation、framework、helm、mt-bench、agentbench、auto-eval、tau-bench、agentboard、selection |
| [模块3.4：能力维度指标详解](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/03-metrics/03-metrics-capability.md) | 能力维度核心指标详解：任务完成率、推理规划、工具调用、记忆管理等16项指标，含定义、测量方法与参考阈值。 | 2026-08-05 | agent-evaluation、metrics、capability、task-success、tool-use、planning、memory |
| [模块3.5：效率维度指标详解](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/03-metrics/03-metrics-efficiency.md) | 效率维度指标详解：延迟、成本、Token消耗、吞吐量等12项指标，含定义、测量方法与参考阈值。 | 2026-08-05 | agent-evaluation、metrics、efficiency、latency、cost、token、throughput |
| [模块3.7：人本与商业维度指标详解](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/03-metrics/03-metrics-human-commercial.md) | 人本与商业维度指标详解：用户满意度、可解释性、转化留存、ROI等9项指标，含定义、测量方法与参考阈值。 | 2026-08-05 | agent-evaluation、metrics、human、csat、nps、roi、purchase、retention |
| [模块3：关键指标体系（总览）](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/03-metrics/03-metrics-overview.md) | Agent评测关键指标体系的四维总览，说明能力、效率、安全、人本与商业四大维度的定位、关系与北极星指标选取原则。 | 2026-08-05 | agent-evaluation、metrics、indicator-system、four-dimensions、overview |
| [模块3.6：安全维度指标详解](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/03-metrics/03-metrics-security.md) | 基于IETF提出的4层55项安全评估框架，详解输入/提示层、模型/推理层、工具/行动层、系统/治理层的安全指标架构与关键指标。 | 2026-08-05 | agent-evaluation、metrics、security、ietf、prompt-injection、privacy、compliance |
| [模块4：八阶段实施步骤](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/04-implementation/04-implementation-overview.md) | Agent评测体系落地的八阶段实施步骤，每阶段含输入/输出/工具/验收标准/常见坑，并给出0-8周落地清单。 | 2026-08-05 | agent-evaluation、implementation、eight-stage、landing-checklist、workflow |
| [模块5：8个行业案例分析](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/05-cases/05-cases-overview.md) | 解析OpenAI、LangChain、Similarweb、Nubank、AWS、JPMorgan、Harvey、IBM八大企业Agent评测实践，每案例含背景/做法/成果/方法论映射/反模式/可复用要点六要素，映射公理体系与四维指标。 | 2026-08-05 | agent-evaluation、cases、openai、langchain、nubank、aws、jpmorgan、harvey、ibm、similarweb |
| [模块6：常见问题解答](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/06-faq/06-faq-overview.md) | Agent评测落地中的常见问题解答，覆盖选型、实施、踩坑三大类共22条FAQ。 | 2026-08-05 | agent-evaluation、faq、troubleshooting、pitfalls |
| [V阶段：知乎文章四视角对抗审查与修订对比](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/appendices/adversarial-review-zhihu-article.md) | 对《用方法论编排，而不是靠灵感》知乎文章进行魔鬼代言人、新人、老板、未来四视角对抗审查，汇总意见分级，记录采纳修订的对比。 | 2026-08-05 | zhihu-article、adversarial-review、V-stage、four-perspectives、revision-log |
| [V阶段：四视角对抗审查与内容修订](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/appendices/adversarial-review.md) | 对Agent评测方法论Wiki内容进行魔鬼代言人、新人、老板、未来四视角对抗审查，汇总意见分级，并记录采纳修订的对比。 | 2026-08-05 | agent-evaluation、adversarial-review、V-stage、four-perspectives、revision-log |
| [创作过程记录：从资料收集到内容撰写](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/appendices/creation-process-record.md) | 记录Agent评测方法论Wiki教程从资料收集、框架搭建、内容撰写到审核修订的完整创作过程，包含各阶段的思考过程、决策依据与挑战解决方案。 | 2026-08-05 | creation-process、methodology、thinking-log、decision-record |
| [R阶段事实清单](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/appendices/fact-list.md) | Agent评测体系化建设方法论的客观事实清单，编号F-001起，作为后续洞察（I阶段）的证据基础。 | 2026-08-05 | agent-evaluation、methodology、fact-list、G1 |
| [F阶段第一性原理分析与I阶段核心洞察](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/appendices/first-principles-and-insights.md) | Agent评测体系化建设的第一性原理公理体系、假设剥离辨析，以及三条带完整四元组（陈述/证据/反常识/行动）的核心洞察。 | 2026-08-05 | agent-evaluation、first-principles、insight、G2 |
| [seven-concepts-cmd 实操避坑指南](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/appendices/seven-concepts-cmd-practical-guide.md) | 基于一次真实任务（用seven-concepts-cmd产出Agent评测方法论Wiki教程及知乎文章）的复盘，总结方法论编排的实操避坑指南：适用场景判断、五大高频坑、质量门实战检查、真实踩坑案例与快速自查表。 | 2026-08-05 | seven-concepts、practical-guide、anti-patterns、quality-gates、lessons-learned |
| [AI Agent 评测体系化建设方法论教程总览](learning/02-agent-engineering-methodology/agent-evaluation-wiki/00-overview.md) | AI Agent 评测体系化建设方法论系统性教程，涵盖评测理论基础、指标体系设计、基准测试构建、自动化评测框架、人工评估方法论、评测数据治理、行业实践案例、工具链选型、持续评测体系与参考资源。 | 2026-08-05 | agent-evaluation、evaluation-methodology、benchmark、metrics、overview、tutorial |
| [第1章：评测理论基础](learning/02-agent-engineering-methodology/agent-evaluation-wiki/01-theory-foundations.md) | 系统阐述AI Agent评测的理论基础，包括标准定义、与传统LLM评测的本质区别、发展时间线、能力维度框架、评测范式演进、信效度理论、伦理考虑与核心挑战。 | 2026-08-05 | agent-evaluation、evaluation-theory、benchmark、metrics、reliability、validity、ethics、timeline |
| [第2章：指标体系设计](learning/02-agent-engineering-methodology/agent-evaluation-wiki/02-metrics-design.md) | 系统阐述AI Agent评测指标体系设计，包括14大类指标分类、核心指标深度解析、AWS三层评估框架、指标计算方法与适用场景、指标选择指南。 | 2026-08-05 | agent-evaluation、metrics、pass-at-k、rag-metrics、agent-metrics、efficiency、safety、aws-framework |
| [第3章：基准测试构建](learning/02-agent-engineering-methodology/agent-evaluation-wiki/03-benchmark-construction.md) | 系统阐述AI Agent基准测试构建方法，包括主流基准详解（SWE-bench Verified重点）、基准污染问题、自定义任务集设计、对抗样本构造、基准维护策略与选型指南。 | 2026-08-05 | agent-evaluation、benchmark、swe-bench、gaia、webarena、agentbench、tau-bench、benchmark-contamination、adversarial-examples |
| [第4章：自动化评测框架](learning/02-agent-engineering-methodology/agent-evaluation-wiki/04-automated-evaluation.md) | 系统阐述AI Agent自动化评测框架，包括三大评测范式、6大主流框架深度对比、补充工具、评分聚合方法、报告生成模板与框架选型决策树。 | 2026-08-05 | agent-evaluation、llm-as-judge、automated-evaluation、langsmith、braintrust、deepeval、phoenix、openai-evals |
| [第5章：人工评估方法论](learning/02-agent-engineering-methodology/agent-evaluation-wiki/05-human-evaluation.md) | 系统阐述AI Agent人工评估方法论，包括人工评估的不可替代性、评估维度设计、标注规范制定、评估员培训、一致性检验方法、质量控制机制与人机协作策略。 | 2026-08-05 | agent-evaluation、human-evaluation、annotation、inter-rater-reliability、cohens-kappa、quality-control、human-in-the-loop |
| [第6章：评测数据治理](learning/02-agent-engineering-methodology/agent-evaluation-wiki/06-data-governance.md) | 系统阐述AI Agent评测数据治理方法，包括评测数据生命周期、数据采集策略、标注质量管理、版本管理、隐私保护、数据质量保障与数据集迭代策略。 | 2026-08-05 | agent-evaluation、data-governance、data-versioning、dvc、privacy、pii、data-quality、gold-set |
| [第7章：行业实践案例](learning/02-agent-engineering-methodology/agent-evaluation-wiki/07-industry-practices.md) | 系统阐述AI Agent评测的行业实践案例，包括Coding Agent、RAG Agent、多工具Agent、多Agent协作、生产环境CI/CD五大案例，以及7个常见反模式警示。 | 2026-08-05 | agent-evaluation、industry-practices、coding-agent、rag-agent、multi-tool-agent、multi-agent、aws-motorway、anti-patterns |
| [第8章：评测工具链选型](learning/02-agent-engineering-methodology/agent-evaluation-wiki/08-toolchain-selection.md) | 系统阐述AI Agent评测工具链选型方法，包括开源vs商用vs自研决策框架、开源工具对比、商用平台评估维度、自研框架设计、分阶段技术栈推荐与工具链集成方案。 | 2026-08-05 | agent-evaluation、toolchain、open-source、commercial、build-vs-buy、ci-cd-integration、mlflow、observability |
| [第9章：持续评测体系](learning/02-agent-engineering-methodology/agent-evaluation-wiki/09-continuous-evaluation.md) | 系统阐述AI Agent持续评测体系建设，包括Agent-Native CI/CD理念、五门质量门禁详解、五门流水线流程图、回归检测、版本对比、趋势可视化、评测驱动开发、落地路线图、中小团队快速上手方案与成熟度自评矩阵。 | 2026-08-05 | agent-evaluation、continuous-evaluation、ci-cd、five-gates、shadow-mode、ab-testing、evaluation-driven-development、maturity-model |
| [第10章：术语表与参考资源](learning/02-agent-engineering-methodology/agent-evaluation-wiki/10-resources.md) | AI Agent评测核心术语表、权威参考来源分类整理、按难度分级的扩展阅读建议、项目内相关wiki交叉引用，为持续深入学习提供索引。 | 2026-08-05 | agent-evaluation、glossary、references、resources、further-reading |
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
| [教程总览与知识地图](learning/03-agent-platforms-tools/echobird-wiki/00-overview.md) | EchoBird 教程体系全景：产品生态 Mermaid 图 + 12 章导航表 + 3 条阅读路径 + 与现有知识库的交叉引用矩阵 | 2026-08-04 | echobird、ai-agent、wiki教程、tauri、rust |
| [产品定位与核心价值](learning/03-agent-platforms-tools/echobird-wiki/01-product-positioning.md) | EchoBird 产品定位（解决 AI Agent 安装配置劝退问题）、核心价值（配置一次到处可用）、与传统流程的对比、与技术源码的对应关系 | 2026-08-04 | echobird、product-positioning、model-nexus |
| [技术架构深度解析](learning/03-agent-platforms-tools/echobird-wiki/02-architecture.md) | EchoBird 的 Tauri+Rust 前后端分层架构、前端页面/后端服务模块划分、入口 lib.rs 初始化流程、Cargo.toml 关键依赖清单 | 2026-08-04 | echobird、tauri、rust、architecture |
| [Model Nexus 模型中心](learning/03-agent-platforms-tools/echobird-wiki/03-model-nexus.md) | Model Nexus 模型中心的数据模型（modelDirectory.json 的 providers/relays 结构）、API Key AES-256-GCM 加密、配置一次到处可用的实现机制、官方端点恢复 | 2026-08-04 | echobird、model-nexus、model-directory、api-key |
| [四大核心场景](learning/03-agent-platforms-tools/echobird-wiki/04-core-scenarios.md) | EchoBird 四大核心场景（安装修复 Agent / 一键本地大模型 / 我的 AI 项目 / 应用管理器）的功能说明、操作流程、源码实现要点与应用价值，以及由 Model Nexus 串联的顺滑使用流程 | 2026-08-04 | echobird、core-scenarios、react-loop、agent-tools、local-llm、my-projects、app-manager |
| [本地大模型服务](learning/03-agent-platforms-tools/echobird-wiki/05-local-llm.md) | EchoBird 本地大模型服务的引擎选择（vLLM/SGLang/llama.cpp）、GPU 检测、三步操作流程、进程管理、模型仓库与本地代理实现 | 2026-08-04 | echobird、local-llm、vllm、sglang、llama.cpp、gpu |
| [Codex Proxy 协议转换](learning/03-agent-platforms-tools/echobird-wiki/06-codex-proxy.md) | EchoBird Codex Proxy 的协议转换能力：127.0.0.1:53682 本地服务绑定、Responses↔Chat 双向转换、SSE 流式处理、多厂商适配（GLM/MiMo/Qwen）、配置管理与会话追踪、Codex 二进制解析与工程价值 | 2026-08-04 | echobird、codex-proxy、protocol-conversion、responses-api、chat-completions、sse、tauri、rust |
| [工具注册表](learning/03-agent-platforms-tools/echobird-wiki/07-tool-registry.md) | EchoBird 工具注册表的 config.json/paths.json 结构、26+ 工具清单、已装工具检测、配置写入与官方端点恢复机制 | 2026-08-04 | echobird、tool-registry、config.json、paths.json、tool-manager |
| [高级功能模块](learning/03-agent-platforms-tools/echobird-wiki/08-advanced-pages.md) | EchoBird 高级功能模块（AiPulse/AiCareer/MotherAgent/Skills/SSH/用量查询/自更新）的实现要点 | 2026-08-04 | echobird、advanced、aipulse、aicareer、skills、ssh、usage |
| [快速上手指南](learning/03-agent-platforms-tools/echobird-wiki/09-quickstart.md) | EchoBird 四步快速上手：安装 EchoBird→安装 Agent→配置模型中心→绑定模型并启动，含可复制命令与易错点提示 | 2026-08-04 | echobird、quickstart、install、model-nexus、app-manager |
| [对比与趋势洞察](learning/03-agent-platforms-tools/echobird-wiki/10-comparison-trends.md) | EchoBird 与同类工具（Eve/Orca/LangGraph/官方 CLI）的对比、Agent 桌面化趋势洞察与技术选型建议 | 2026-08-04 | echobird、comparison、trends、agent-desktop、eve、langgraph |
| [FAQ 与术语表](learning/03-agent-platforms-tools/echobird-wiki/11-faq-glossary.md) | EchoBird 常见问题解答（FAQ）与核心术语词表（15+ 术语），帮助读者快速定位问题与理解概念 | 2026-08-04 | echobird、faq、glossary、terms |
| [教程总览与知识地图](learning/03-agent-platforms-tools/eve-wiki/00-overview.md) | Eve 教程体系全景：Eve 产品生态 Mermaid 图 + 10 章导航表 + 3 条阅读路径 + 知识库交叉引用矩阵（v1.1 已结合本地源码校准 API 细节） | 2026-08-04 | eve、vercel、agent-framework、wiki教程、nextjs-for-agents |
| [产品介绍与核心概念](learning/03-agent-platforms-tools/eve-wiki/01-product-intro.md) | Eve 产品定位（Next.js for Agents）、与 AI SDK/Agent Loop 的层次区分、以及'一个 Agent 就是一个目录'（filesystem-first）设计哲学。 | 2026-08-04 | eve、vercel、agent-framework、nextjs-for-agents、产品定位 |
| [目录结构与核心能力](learning/03-agent-platforms-tools/eve-wiki/02-directory-core-capabilities.md) | Eve 目录结构详解：agent.ts 模型/运行时配置（defineAgent）、instructions.md 指令、tools 工具、skills 技能、sandbox 沙箱（四后端）、lib/connections/evals 补充。 | 2026-08-04 | eve、vercel、agent-framework、instructions、tools、skills、sandbox |
| [生产级能力详解](learning/03-agent-platforms-tools/eve-wiki/03-production-capabilities.md) | Eve 六大生产级能力详解：durable execution（持久化执行）、人工审批（approval: always/once/never）、connections（defineMcpClientConnection）、channels（多渠道）、tracing（可观测）、evals（defineEval 评测）。 | 2026-08-04 | eve、vercel、agent-framework、durable-execution、sandbox、approvals、connections、channels、tracing、evals |
| [进阶能力：子 Agent、定时任务与多 Agent 协作](learning/03-agent-platforms-tools/eve-wiki/04-advanced-capabilities.md) | Eve 进阶能力详解：subagents（子 Agent 委派、defineDynamic 条件可用、隔离边界）、schedules（defineSchedule、markdown/run 两种形式）、多 Agent 协作实战模式。 | 2026-08-04 | eve、vercel、agent-framework、subagents、schedules、multi-agent |
| [快速上手指南](learning/03-agent-platforms-tools/eve-wiki/05-quickstart.md) | Eve 快速上手指南：官方九步上手流程、五步快速开始（agent.ts 定义模型、defineTool 定义工具）、最小指令先行、部署与本地开发说明。 | 2026-08-04 | eve、vercel、agent-framework、quickstart、npm、deploy |
| [竞品对比与选型](learning/03-agent-platforms-tools/eve-wiki/06-comparison-selection.md) | Eve vs Mastra vs LangGraph 多维对比、关键差异与适用团队边界、选型决策树与不适合的场景。 | 2026-08-04 | eve、vercel、agent-framework、mastra、langgraph、comparison、selection |
| [工程化理念与趋势洞察](learning/03-agent-platforms-tools/eve-wiki/07-engineering-philosophy-trends.md) | Demo 与生产的分野、Agent 工程化趋势（从模型竞争到工程底座竞争）、前端工程化经验向 AI 领域迁移的洞察。 | 2026-08-04 | eve、vercel、agent-framework、engineering、trends、frontend、ai-infra |
| [FAQ、适用范围与局限性](learning/03-agent-platforms-tools/eve-wiki/08-faq.md) | Eve 常见问题解答、适用团队范围与当前局限性。 | 2026-08-04 | eve、vercel、agent-framework、faq、limitations、scope |
| [术语表与参考资源](learning/03-agent-platforms-tools/eve-wiki/09-glossary-resources.md) | Eve 核心术语表（≥15 个）与参考资源清单（5 个来源 + 本地源码 + 官方文档 + 知识库交叉引用）。 | 2026-08-04 | eve、vercel、agent-framework、glossary、resources、references |
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
| [项目概述与核心定位](learning/03-agent-platforms-tools/orca-wiki/00-overview.md) | Orca 项目概述与核心定位：面向 100x 构建者的 AI 编排器，并排运行多个 Agent 于隔离 worktree，一段话核心价值 + 传统多 Agent 开发痛点 vs Orca 解决方案对照表 + 平台支持矩阵 | 2026-08-03 | orca、stablyai、ai-orchestrator、agent-ide、worktree、claude-code、codex、opencode、parallel-agents、multi-agent、yc |
| [核心架构与技术栈](learning/03-agent-platforms-tools/orca-wiki/01-core-architecture.md) | Orca 核心架构与技术栈：桌面端 Electron+React19+TS（非 Tauri）、xterm.js+node-pty 终端、ssh2 远程、8 大代码库集成、RN/Expo 移动端、sherpa-onnx 本地 STT，以及主进程/渲染进程/preload/relay/shared/cli 六层架构与 Mermaid 分层图。 | 2026-08-03 | orca、stablyai、electron、electron-vite、react、typescript、xterm.js、node-pty、ssh2、react-native、expo、sherpa-onnx、agent-browser、multi-agent、wiki教程 |
| [八大核心功能详解](learning/03-agent-platforms-tools/orca-wiki/02-core-features.md) | Orca 八大核心功能总览：移动 Companion、并行 Worktree、终端分屏、设计模式、GitHub&Linear 原生集成、SSH Worktree、注释 AI Diff、拖拽文件，每项含功能说明/操作流程/应用价值，并附附加功能速览。 | 2026-08-03 | orca、stablyai、ai-orchestrator、agent-ide、worktree、mobile-companion、ssh、design-mode、ai-diff、github、linear、terminal-splits、multi-agent |
| [Orca CLI 与多 Agent 编排](learning/03-agent-platforms-tools/orca-wiki/03-orca-cli-orchestration.md) | Orca CLI 命令面与多 Agent 编排机制详解：worktree/terminal/repo/automations/browser/linear/computer/orchestration 八大命令族、Run/Task/Dispatch/worker_done 核心编排概念、受监督工作流（task-create → worker-start → check --wait）与完整交接（full handoff）的区别、可直接复制的常用命令块。 | 2026-08-03 | orca、stablyai、cli、orchestration、worktree、terminal、automations、browser、linear、multi-agent、worker_done、dispatch、run、task |
| [支持的 Agent 清单](learning/03-agent-platforms-tools/orca-wiki/04-supported-agents.md) | Orca 支持任意 CLI Agent 的核心能力：25+ 款官方适配 Agent 清单、归属厂商与一句话说明、自带 Agent / 订阅理念、兼容性边界与排查建议。 | 2026-08-03 | orca、stablyai、ai-orchestrator、agent-ide、cli-agent、claude-code、codex、opencode、bring-your-own-agent、multi-agent |
| [快速上手指南](learning/03-agent-platforms-tools/orca-wiki/05-quickstart.md) | Orca 五步快速上手流程：第一种安装 Orca（macOS Homebrew / Arch AUR / Windows .exe）、第二步启动并登录接入 Agent 订阅、第三步添加连接 Agent（Claude Code、Codex 等）、第四步创建并分发 worktree（一个提示分发到多个隔离 worktree）、第五步并行监控与择优合并（终端分屏、移动端监控、diff 注释），全部命令可直接复制执行。 | 2026-08-03 | orca、stablyai、quickstart、安装、worktree、claude-code、codex、并行、多agent、入门 |
| [核心价值总结与行业趋势](learning/03-agent-platforms-tools/orca-wiki/06-value-and-trends.md) | Orca 核心价值总结与行业趋势：IDE 从代码编辑器向代理编排器演进的产品哲学、统一跟踪/并行隔离/结果择优三大核心价值、多 Agent 并行开发范式与 Git Worktree 一等公民趋势、自带 Agent 理念，以及与开篇定位的呼应 | 2026-08-03 | orca、stablyai、ai-orchestrator、agent-ide、worktree、parallel-agents、multi-agent、bring-your-own-agent、git-worktree、industry-trend、yc、wiki教程 |
| [FAQ 与术语表](learning/03-agent-platforms-tools/orca-wiki/07-faq-glossary.md) | Orca 常见问题解答（9 个覆盖开源协议/系统支持/Agent 支持/自带订阅/磁盘隔离/移动端/IDE 对比/中文本地化）+ 18 个核心术语一张表通俗解释，作为本教程速查手册。 | 2026-08-03 | orca、stablyai、ai-orchestrator、faq、glossary、worktree、orchestration、multi-agent、wiki教程 |
| [Agent Plan 共创计划：概述与学习目标](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/00-overview.md) |  | 2026-07-31 | volcengine、agent-plan、方舟、多模态、共创计划 |
| [产品详解：什么是Agent Plan](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/01-product-overview.md) |  | 2026-07-31 | volcengine、agent-plan、方舟、订阅产品、API Key |
| [贡献方向详解：五大类征集方向](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/02-contribution-directions.md) |  | 2026-07-31 | volcengine、agent-plan、共创计划、贡献方向、征集 |
| [参与指南：如何加入共创计划](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/03-participation-guide.md) |  | 2026-07-31 | volcengine、agent-plan、共创计划、参与指南、流程 |
| [回报与激励：套餐奖励与Cookbook收录](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/04-rewards-recognition.md) |  | 2026-07-31 | volcengine、agent-plan、共创计划、奖励、Cookbook |
| [快速开始与资源：官方链接汇总](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/05-quickstart-resources.md) |  | 2026-07-31 | volcengine、agent-plan、快速开始、资源、文档 |
| [跨模态范式洞察：从单模态解决问题到跨模态创造可能](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/06-crossmodal-paradigm.md) |  | 2026-07-31 | volcengine、agent-plan、跨模态、范式演进、Harness |
| [常见问题FAQ](learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/07-faq.md) |  | 2026-07-31 | volcengine、agent-plan、faq、常见问题 |
| [教程总览与知识地图](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/00-overview.md) | AgentKit 教程体系全景：4层产品生态Mermaid图 + 11章导航表 + 3条阅读路径 + 6个wiki交叉引用矩阵 | 2026-07-31 | AgentKit、VeADK、火山引擎、AI Agent、wiki教程 |
| [产品介绍与核心概念](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/01-product-intro.md) | AgentKit 企业级 AI Agent 基础设施平台产品定义、工程化痛点分析、9 大功能模块详解、4 大产品优势与产品发展时间线。 | 2026-07-31 | AgentKit、VeADK、火山引擎、AI Agent、wiki教程 |
| [产品架构与核心能力](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/02-core-architecture.md) | AgentKit Agent Ready 基础设施分层架构、动态 Harness 编排、Serverless 弹性底座、安全防护三层模型与评测可观测闭环详解。 | 2026-07-31 | AgentKit、VeADK、火山引擎、AI Agent、wiki教程 |
| [VeADK 智能体开发框架](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/03-veadk-framework.md) | VeADK（Volcengine Agent Development Kit）智能体开发框架详解：三语言 SDK 安装、与 Google ADK 兼容说明、VeADK Family 20+ 产品融合矩阵、DeepResearch 6 大构建特性、GitHub 开源仓库清单。 | 2026-07-31 | AgentKit、VeADK、火山引擎、SDK、开发框架 |
| [AgentKit SDK & CLI 工具链](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/04-agentkit-sdk-cli.md) | AgentKit SDK & CLI 工具链详解：装饰器式 API 设计与完整代码示例、Local/Hybrid/Cloud 三种部署模式对比表、CLI 五连命令（init/config/build/deploy/launch）使用指南、Tool/Service 接入流程图、VeADK 与 AgentKit SDK 的关系图。 | 2026-07-31 | AgentKit、SDK、CLI、装饰器API、部署模式 |
| [快速入门指南](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/05-quickstart.md) | AgentKit 快速入门五步法：前置条件清单、5 步标准 HelloWorld 流程（安装→初始化→配置→本地启动→云端部署）、3 个典型场景最小代码片段、5 条常见报错 FAQ 与下一步进阶路径推荐。 | 2026-07-31 | AgentKit、快速入门、HelloWorld、安装部署、FAQ |
| [应用场景与落地方案](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/06-application-scenarios.md) | AgentKit 企业智能体建设场景选型决策树、5大行业典型场景落地方案（背景/架构/组件/步骤/KPI）与3条场景最佳实践。 | 2026-07-31 | AgentKit、火山引擎、应用场景、落地案例、AI Agent |
| [核心功能深度解析](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/07-core-features-detailed.md) | AgentKit 治理外环 5 大核心模块深度解析：Identity 鉴权模型、Gateway 双轨接入、A2A 多 Agent 协作、Observability 三维信号、Evaluation 评测三角与发布闸门。 | 2026-07-31 | AgentKit、Identity、Gateway、A2A、Observability、Evaluation、深度解析 |
| [竞品对比与生态定位](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/08-comparison-ecosystem.md) | AgentKit 与 Dify、LangGraph、Coze、千帆平台、钉钉生态等 6 大竞品在 12 个维度的横向对比表、生态位四象限定位、开源-商业双轨策略、VeADK 家族 20+ 产品生态矩阵与选型决策建议。 | 2026-07-31 | AgentKit、竞品对比、生态定位 |
| [FAQ 与最佳实践](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/09-faq-best-practices.md) | AgentKit 生产化落地常见问题 FAQ（产品计费/开发调试/部署运维/安全治理/观测评测 5 大类共 15 个问题）、10 条最佳实践清单、生产上线前 20 项检查清单、避坑指南与技术支持渠道。 | 2026-07-31 | AgentKit、FAQ、最佳实践、生产化清单 |
| [术语表与参考资源](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/10-resources-glossary.md) | AgentKit 官方参考资源清单（产品/文档/社区/教程 4 大类）、30+ 专业术语表、12 个跨 Wiki 交叉引用链接、贡献者指南与版本更新日志。 | 2026-07-31 | AgentKit、术语表、参考资源、贡献指南 |
| [AgentKit Wiki 版本维护手册](learning/03-agent-platforms-tools/volcengine-agentkit-wiki/MAINTENANCE.md) | AgentKit Wiki 增量更新触发器（5类）+ 5步SOP + 版本标注规范 + 反模式清单 | 2026-07-31 | AgentKit、维护手册、版本更新、MAINTENANCE |
| [项目概述与核心定位](learning/03-agent-platforms-tools/zleap-agent-wiki/00-overview.md) | Zleap-Agent 项目概述与核心定位：workspace-first 的 Agent Harness，核心命题是'Agent 先知道自己身处哪个 Workspace，再只拿到该 Workspace 需要的上下文'，而非把所有工具/记忆/规则/历史塞进一个大 prompt。 | 2026-08-04 | zleap-agent、workspace-first、agent-harness、context、local-models |
| [核心架构与技术栈](learning/03-agent-platforms-tools/zleap-agent-wiki/01-core-architecture.md) | Zleap-Agent 核心架构与技术栈：pnpm monorepo、TypeScript、13 个 package 职责、PostgreSQL+pgvector 存储、四层架构分层（模型层/运行时/会话服务/网关/存储）。 | 2026-08-04 | zleap-agent、architecture、monorepo、pnpm、postgresql、pgvector、packages |
| [Workspace 隔离与上下文组装](learning/03-agent-platforms-tools/zleap-agent-wiki/02-workspace-context.md) | Zleap-Agent Workspace 隔离机制与上下文组装：main/work 空间、数据库为唯一真源、when/notFor 路由提示、persona、toolIds；Kernel 经 switchWorkspace 路由；Context 稳定/半稳定/可变三块组装与缓存断点不变量。 | 2026-08-04 | zleap-agent、workspace、context-assembly、cache-breakpoint、kernel、routing、main-space、work-space |
| [分区记忆系统](learning/03-agent-platforms-tools/zleap-agent-wiki/03-memory-system.md) | Zleap-Agent 分区记忆系统：person/event/experience 三类记忆、A 线（people notes）+ B 线（core records）双线、prefetch 快速读取与 recall 精排、RRF 多路径召回融合、抽取管线。 | 2026-08-04 | zleap-agent、memory、person-memory、event-memory、experience-memory、rrf、recall、postgresql、extraction |
| [Skill 与工具权限](learning/03-agent-platforms-tools/zleap-agent-wiki/04-skills-tools-permissions.md) | Zleap-Agent Skill 机制与工具权限：SKILL.md 入口、SkillRegistry、敏感性审计、token 预算、调用策略、信任状态；request_approval/full_access 权限模式；MCP Runtime 与 MCP Secrets。 | 2026-08-04 | zleap-agent、skill、skill-registry、sensitivity-audit、permission、approval、mcp、tool-policy |
| [模型提供方与运行时入口](learning/03-agent-platforms-tools/zleap-agent-wiki/05-model-providers-runtime.md) | Zleap-Agent 模型提供方与运行时入口：OpenAI-compatible/Anthropic 提供方抽象、ProviderRegistry/ModelRegistry、SSE 流式；Web UI 与 CLI 入口；ConversationService 作为所有触发统一入口与 inbound→reply→流式回传数据流。 | 2026-08-04 | zleap-agent、model-provider、openai-compatible、anthropic、sse、conversation-service、web-ui、cli、inbound、outbound |
| [IM 网关与定时任务](learning/03-agent-platforms-tools/zleap-agent-wiki/06-gateway-tasks.md) | Zleap-Agent IM 网关与定时任务：飞书/微信/飞书 CLI 适配器、ChannelSupervisor、worker、dedup；定时任务服务（cron/queue/worker/service）；二者如何接入 ConversationService。 | 2026-08-04 | zleap-agent、gateway、feishu、wechat、im、channel-supervisor、cron、tasks、worker |
| [快速上手指南](learning/03-agent-platforms-tools/zleap-agent-wiki/07-quickstart.md) | Zleap-Agent 快速上手指南：环境要求、安装依赖、启动 Web UI、配置模型、CLI 使用、一次性运行、常用命令与环境变量表。 | 2026-08-04 | zleap-agent、quickstart、install、setup、cli、web-ui、environment-variables、pnpm |
| [FAQ 与术语表](learning/03-agent-platforms-tools/zleap-agent-wiki/08-faq-glossary.md) | Zleap-Agent FAQ 与术语表：常见问题解答（适合用户、是否需要本地模型、与单一大 prompt 区别、Workspace 协作、飞书/微信接入、Skill 导入等）+ 核心术语通俗解释。 | 2026-08-04 | zleap-agent、faq、glossary、workspace、context、memory、rrf、mcp、gateway、turn-loop |
| [MDX + GraphQL 概述与核心概念](learning/04-docs-markup-tooling/mdx-graphql-guide/00-overview.md) | 理解可查询文档理念、MDX与GraphQL各自角色、技术栈选型理由、三层架构总览 | 2026-08-05 | mdx、graphql、overview、concepts、architecture |
| [MDX + GraphQL 5分钟快速上手](learning/04-docs-markup-tooling/mdx-graphql-guide/01-quickstart.md) | 从零开始：创建Next.js项目→配置MDX→定义GraphQL Schema→嵌入查询组件→运行验证，含完整可复制代码 | 2026-08-05 | mdx、graphql、quickstart、nextjs、tutorial |
| [MDX + GraphQL 查询组件开发](learning/04-docs-markup-tooling/mdx-graphql-guide/02-query-components.md) | 深入文档元数据Schema设计、Query组件模式、Fragment复用、静态生成vs运行时查询、服务端组件中的GraphQL | 2026-08-05 | mdx、graphql、components、schema、patterns |
| [MDX + GraphQL 最佳实践与FAQ](learning/04-docs-markup-tooling/mdx-graphql-guide/03-best-practices.md) | 性能优化、缓存策略、生产部署、安全考虑、与OKF开放知识协议集成方向、常见问题解答 | 2026-08-05 | mdx、graphql、best-practices、deployment、okf、faq |
| [Mermaid 教程总览](learning/04-docs-markup-tooling/mermaid-wiki/00-overview.md) | Mermaid 是基于 JavaScript 的图表绘制与可视化工具，用受 Markdown 启发的文本定义图表，核心目的是帮助文档跟上开发进度、解决文档与实际开发脱节（Doc-Rot）问题。本教程基于 Mermaid 官方文档（mermaid.js.org）系统梳理各图表类型语法、配置主题与集成方式，共 10 章。 | 2026-08-06 | mermaid、diagram、可视化、flowchart、sequenceDiagram、gantt、sankey、markdown、tutorial、overview |
| [Mermaid 入门与快速开始](learning/04-docs-markup-tooling/mermaid-wiki/01-introduction-quickstart.md) | 本章介绍 Mermaid 的核心概念（文本即图表、解决 Doc-Rot）、工作原理（JavaScript 将文本渲染为 SVG，依赖 d3 与 dagre-d3），并通过 mermaid.live 在线编辑器完成快速上手，最后概览本地集成（CDN、npm、mermaid.initialize 与 class=\"mermaid\"）。 | 2026-08-06 | mermaid、quickstart、入门、doc-rot、mermaid.live、cdn、npm、svg、tutorial |
| [Mermaid 基础图表：流程图（Flowchart）](learning/04-docs-markup-tooling/mermaid-wiki/02-flowchart.md) | Mermaid 流程图（Flowchart）完整指南：flowchart/graph 关键字与方向声明、十余种节点形状语法、特殊字符注意事项、九种连线类型、subgraph 分组与方向、classDef 样式与 default 类、click 交互，每个语法均附带可复现的完整 mermaid 代码示例。 | 2026-08-06 | mermaid、diagram、flowchart、graph、markup、visualization |
| [Mermaid 时序图（Sequence Diagram）](learning/04-docs-markup-tooling/mermaid-wiki/03-sequence-diagram.md) | Mermaid 时序图（Sequence Diagram）完整指南：participant/actor 声明与 as 别名、消息箭头类型、activate/deactivate 激活及其 +/ - 后缀、Note 注释、loop/alt/opt/par/break 块、autonumber 与 showSequenceNumbers 配置，每个语法均附带可复现的完整 mermaid 代码示例。 | 2026-08-06 | mermaid、diagram、sequence、sequenceDiagram、markup、visualization |
| [Mermaid 结构型图表：类图 / 状态图 / ER 图](learning/04-docs-markup-tooling/mermaid-wiki/04-class-state-er.md) | Mermaid 结构型图表（classDiagram 类图、stateDiagram-v2 状态图、erDiagram ER 图）完整指南：类定义与成员/可见性/泛型/8种关系/基数/注解/namespace，状态声明与转换/复合状态/选择/分叉/并发/Note，ER 实体属性块/crow's foot 基数/识别与非识别关系/方向，每个语法均附带可复现的完整 mermaid 代码示例。 | 2026-08-06 | mermaid、diagram、classDiagram、stateDiagram、erDiagram、markup、visualization、structure |
| [Mermaid 可视化图表：Gantt / Pie / Journey / Timeline / Sankey / QuadrantChart](learning/04-docs-markup-tooling/mermaid-wiki/05-aggregate-diagrams.md) | Mermaid 六种可视化图表完整指南：gantt 甘特图（dateFormat/section/任务元数据/时长单位/excludes）、pie 饼图（showData/donutHole/legendPosition）、journey 用户旅程图（task/score/actor）、timeline 时间线图（时间周期/事件/方向）、sankey 桑基图（source/target/value）、quadrantChart 象限图（x-axis/y-axis/quadrant-1..4/点），每种均附带可复现的完整 mermaid 代码示例。 | 2026-08-06 | mermaid、diagram、gantt、pie、journey、timeline、sankey、quadrantChart、markup、visualization |
| [Mermaid 进阶图表：GitGraph / Requirement / Mindmap / Block / C4 / Zenuml](learning/04-docs-markup-tooling/mermaid-wiki/06-advanced-diagrams.md) | Mermaid 六种进阶/专业图表完整指南：gitGraph Git 提交图（commit/branch/checkout/merge/cherry-pick）、requirementDiagram 需求图（requirement/element/relationship/风险/验证方法）、mindmap 思维导图（缩进层级/形状/icon/:::）、block 块图（列控制/复合块/形状/连接）、C4 架构图（Context/Container/Component/Dynamic/Deployment 与宏）、zenuml 增强时序图（participant/消息类型/嵌套/循环/条件），每种均附带可复现的完整 mermaid 代码示例。 | 2026-08-06 | mermaid、diagram、gitGraph、requirementDiagram、mindmap、block、c4、zenuml、markup、visualization |
| [Mermaid 配置与主题（Configuration & Theming）](learning/04-docs-markup-tooling/mermaid-wiki/07-configuration-theming.md) | Mermaid 配置与主题完整指南：配置来源三层（默认/站点级 initialize/frontmatter）、mermaid.initialize 与 startOnLoad 与 configApi.reset、5 个内置主题（default/neutral/dark/forest/base）、securityLevel 四级安全、dagre/elk 渲染器，以及 themeVariables 与各图表专项主题变量，每个关键配置均附带 HTML 与 YAML frontmatter 代码示例。 | 2026-08-06 | mermaid、configuration、theming、theme、themeVariables、securityLevel、dagre、elk、markup |
| [Mermaid 集成与生态（Integrations & Ecosystem）](learning/04-docs-markup-tooling/mermaid-wiki/08-integrations-ecosystem.md) | Mermaid 集成与生态完整指南：mermaid-cli 命令行工具（@mermaid-js/mermaid-cli、mmdc、JSON 配置）、mermaid.live 在线编辑器、CDN/npm 集成与 SVG 渲染、Markdown 与渲染器集成（GitHub/飞书/VS Code）、生态工具对比表，每个集成方式均附带命令或代码示例。 | 2026-08-06 | mermaid、integration、mermaid-cli、mmdc、mermaid-live、cdn、npm、ecosystem、markup |
| [Mermaid 常见问题与最佳实践（FAQ & Best Practices）](learning/04-docs-markup-tooling/mermaid-wiki/09-faq-best-practices.md) | Mermaid 常见问题与最佳实践：12 个高频渲染问题的现象/原因/解决方案（end 关键字、o/x 开头节点、pie 负值、中文乱码与引号、空行中断、subgraph 中文 ID、\\n 换行、版本差异、securityLevel、elk 渲染器等），8 条最佳实践，以及与项目安全编码六规则（mermaid-guide.md）的对接说明。 | 2026-08-06 | mermaid、faq、troubleshooting、best-practices、安全编码、check-mermaid、markup |
| [Mermaid 命令速查表（Cheatsheet）](learning/04-docs-markup-tooling/mermaid-wiki/10-cheatsheet.md) | Mermaid 命令速查表：覆盖全部 17 种图表类型（flowchart/sequenceDiagram/classDiagram/stateDiagram-v2/erDiagram/gantt/pie/journey/timeline/sankey/quadrantChart/gitGraph/requirementDiagram/mindmap/block/C4/zenuml）的关键字与核心语法行，常用配置速查（initialize/主题/securityLevel/渲染器），以及 mermaid.live 使用速查。 | 2026-08-06 | mermaid、cheatsheet、速查、flowchart、sequenceDiagram、classDiagram、stateDiagram、erDiagram、gantt、pie、journey、timeline、sankey、quadrantChart、gitGraph、requirementDiagram、mindmap、block、c4、zenuml、markup |
| [Mermaid 引号规则检查清单](learning/04-docs-markup-tooling/mermaid-wiki/mermaid-quote-rules-checklist.md) | Mermaid 各图表类型引号使用规则速查：16类图表引号矩阵、7条快速判断口诀、Top 5反模式、4步验证方法。解决Mermaid文档中最常见的引号误用问题（约70%语法错误源于引号）。 | 2026-08-06 | mermaid、checklist、quote-rules、syntax、best-practices、troubleshooting |
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
| [Anime.js 4.5+Three.js 适配器教程总览](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/00-overview.md) | Anime.js 4.5官方Three.js适配器系统性教程，涵盖快速开始、核心概念、五大核心特性、实战案例、最佳实践、常见问题与资源，让3D动画写起来像CSS transform一样直观。 | 2026-08-03 | animejs、threejs、3d-animation、wiki、overview |
| [快速开始](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/01-quickstart.md) |  | 2026-08-03 | animejs、threejs、quickstart、installation |
| [核心概念](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/02-core-concepts.md) |  | 2026-08-03 | animejs、threejs、core-concepts、adapter-pattern |
| [五大核心特性详解](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/03-five-features.md) |  | 2026-08-03 | animejs、threejs、features、property-mapping、transforms、instancing |
| [实战案例](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/04-practical-examples.md) |  | 2026-08-03 | animejs、threejs、examples、practice、demo |
| [最佳实践与常见陷阱](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/05-best-practices.md) |  | 2026-08-03 | animejs、threejs、best-practices、performance、tips |
| [常见问题解答](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/06-faq.md) |  | 2026-08-03 | animejs、threejs、faq、troubleshooting |
| [资源与术语表](learning/05-ai-multimodal-content/animejs-threejs-adapter-wiki/07-resources.md) |  | 2026-08-03 | - |
| [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md) | 系统对比 DeepSeek V4、Kimi K2.7 Code、MiniMax M3、GLM 5.2 四款国产 AI 模型，按不写代码-文案类、不写代码-多模态资料、写代码、高并发批量任务四类人群给出推荐方案，并深入剖析国产模型信任问题，提出'能力是入场券，信任才是留下来的理由'核心洞察。 | 2026-07-04 | llm、domestic-model、model-comparison、glm、kimi、deepseek、minimax、coding、multi-modal、trust、scenario-recommendation、ai-agent |
| [开源EMS能源管理系统深度分析Wiki](learning/06-business-trends-analysis/ems-energy-management-wiki.md) | 开源EMS能源管理系统energy-management深度分析：基于Vue3+SpringCloud Alibaba微服务架构，支持50+工业协议，ShardingSphere分片实现秒级5万条数据处理，全链路可视化配置，代码注释率>40%。含技术架构解析、四大核心亮点、部署门槛评估、6项风险识别和11项可借鉴要点。 | 2026-07-09 | EMS、能源管理、开源项目、工业互联网、微服务、ShardingSphere、工业协议、Vue3、SpringCloud |
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
| [背景与问题陈述——为什么 AI+PS5 是\"地狱难度\"](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/00-overview.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、compatibility、problem-statement、four-fractures |
| [PowerShell 5.1 vs 7+ 核心差异速查](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/01-ps5-ps7-differences.md) |  | 2026-07-31 | powershell、powershell-5.1、powershell-7、compatibility、differences、api、syntax |
| [三大领域 24 个 AI 失败案例集](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/02-ai-failure-cases.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、failure-cases、compatibility-errors、parsererror |
| [第一性原理本质矛盾分析](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/03-first-principles-analysis.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、first-principles、root-cause-analysis、axioms |
| [四大地狱维度结构化洞察](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/04-hell-dimensions.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、insights、root-cause、severity、four-dimensions |
| [防御性模式与最佳实践总览](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/05-defense-patterns.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、defensive-patterns、best-practices、reusable-patterns |
| [即用型Prompt模板库](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/06-prompt-templates.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、prompt-engineering、defensive-prompt、templates |
| [兼容性预检+安全审查Checklist](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/07-checklists.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、checklist、compatibility、security-audit、preflight |
| [陷阱与反模式清单](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/08-pitfalls-anti-patterns.md) |  | 2026-07-31 | powershell、powershell-5.1、ai-coding、pitfalls、anti-patterns、security-hardening、v-stage |
| [参考资料与延伸阅读](learning/08-systems-infrastructure/ai-powershell5-hell-wiki/09-resources-references.md) |  | 2026-07-31 | powershell、powershell-5.1、references、microsoft-docs、security、compatibility、resources |
| [Git 仓库类型与核心概念](learning/08-systems-infrastructure/git-advanced-wiki/00-overview.md) |  | 2026-07-31 | git、bare-repository、working-directory、git-directory、transport-protocol |
| [git clone 高级参数详解（--no-local --bare 重点）](learning/08-systems-infrastructure/git-advanced-wiki/01-git-clone-advanced.md) |  | 2026-07-31 | git、git-clone、--bare、--no-local、--mirror、advanced-usage |
| [WSL 概述与核心概念](learning/08-systems-infrastructure/wsl-wiki/00-overview.md) |  | 2026-07-20 | wsl、wsl2、overview、windows-subsystem-for-linux、introduction |
| [安装与发行版管理](learning/08-systems-infrastructure/wsl-wiki/01-installation.md) |  | 2026-07-20 | wsl、installation、setup、distribution、upgrade、wsl2 |
| [快速开始](learning/08-systems-infrastructure/wsl-wiki/02-quickstart.md) |  | 2026-07-20 | wsl、quickstart、getting-started、basic-commands、interop |
| [CLI 完整命令参考](learning/08-systems-infrastructure/wsl-wiki/03-cli-reference.md) |  | 2026-07-20 | wsl、wslc、cli、command-reference、wsl.exe、container-cli、alias |
| [核心架构与进程模型](learning/08-systems-infrastructure/wsl-wiki/04-architecture.md) |  | 2026-07-20 | wsl、wsl2、architecture、hvsocket、com、mini-init、plan9、gns、relay、mermaid |
| [文件系统互操作](learning/08-systems-infrastructure/wsl-wiki/05-filesystem-interop.md) |  | 2026-07-20 | wsl、filesystem、drvfs、plan9、interop、wsl$、namespace、permission |
| [WSL Container API 三语言编程接口](learning/08-systems-infrastructure/wsl-wiki/06-wslc-api.md) |  | 2026-07-20 | wsl、wslc、container-api、c-api、csharp-api、cpp-api、session、container、process、preview |
| [网络、配置管理与systemd](learning/08-systems-infrastructure/wsl-wiki/07-network-config-systemd.md) |  | 2026-07-20 | wsl、networking、wsl.conf、.wslconfig、systemd、gns、dns、nat、mirroring |
| [调试诊断与开发环境搭建](learning/08-systems-infrastructure/wsl-wiki/08-debugging-dev-env.md) |  | 2026-07-20 | wsl、debugging、diagnostics、development、vscode、gpu、cuda、docker、debug-shell |
| [最佳实践与FAQ](learning/08-systems-infrastructure/wsl-wiki/09-best-practices-faq.md) |  | 2026-07-20 | wsl、best-practices、faq、troubleshooting、performance、tips |
| [术语表与参考资料](learning/08-systems-infrastructure/wsl-wiki/10-glossary-references.md) |  | 2026-07-20 | wsl、glossary、references、terminology、cross-reference |
| [《你以为的自由是一种幻觉》第一性原理分析](learning/first-principles/15-cross-domain-cases/freedom-illusion-ai-era.md) | 以第一性原理六步法拆解公众号文章《你以为的自由是一种幻觉》，从认知局限、知识建构、人机协作出发，提炼AI时代保持认知主体性的六条公理与行动框架。 | 2026-07-13 | 第一性原理、AI时代认知、自由、认知悬浮、意图对齐、人机协作、知识建构 |
| [VeADK-Python 术语表](learning/veadk-python/glossary.md) | VeADK-Python 核心术语表，包含20+个常用术语的中英文对照和通俗解释 | 2026-08-05 | - |
| [VeADK-Python Wiki](learning/veadk-python/index.md) | VeADK-Python 开发知识库首页，提供项目介绍、核心特性、文档导航和学习路径 | 2026-08-05 | - |
| [架构详解：Agent 生命周期与执行流程](learning/veadk-python/architecture/agent-lifecycle.md) | VeADK-Python Agent 生命周期详解，包含 model_post_init 19步初始化流程、Runner执行流程、事件流转、运行时策略选择等核心机制 | 2026-08-05 | - |
| [架构模式：核心设计模式解析](learning/veadk-python/architecture/design-patterns.md) | VeADK-Python 7个核心设计模式深度解析：继承扩展模式、条件插件挂载、回调链、运行时策略、配置降级、RunProcessor装饰器链、凭证服务单例 | 2026-08-05 | - |
| [架构参考：模块依赖关系与分层约束](learning/veadk-python/architecture/module-dependencies.md) | VeADK-Python 模块依赖关系详解，包含核心模块依赖图、六层分层架构说明、Agent/Runner聚焦依赖图，以及单向依赖、核心层纯净等依赖规则 | 2026-08-05 | - |
| [架构概览：VeADK 整体架构设计](learning/veadk-python/architecture/overview.md) | VeADK-Python 整体架构设计文档，介绍与 Google ADK 的关系、六层分层架构、核心组件一览、能力扩展与设计哲学 | 2026-08-05 | - |
| [A2UI - Agent驱动UI示例](learning/veadk-python/examples/a2ui.md) |  | 2026-08-05 | - |
| [02 - 自定义工具示例](learning/veadk-python/examples/custom-tools.md) |  | 2026-08-05 | - |
| [05 - 知识库RAG示例](learning/veadk-python/examples/knowledgebase.md) |  | 2026-08-05 | - |
| [03 & 09 - 记忆示例（短期+长期）](learning/veadk-python/examples/memory.md) |  | 2026-08-05 | - |
| [08 - 模型配置示例](learning/veadk-python/examples/model-config.md) |  | 2026-08-05 | - |
| [06 - 多智能体协作示例](learning/veadk-python/examples/multi-agent.md) |  | 2026-08-05 | - |
| [01 - 最小Agent示例](learning/veadk-python/examples/quickstart.md) |  | 2026-08-05 | - |
| [07 - 结构化输出示例](learning/veadk-python/examples/structured-output.md) |  | 2026-08-05 | - |
| [11 - 链路追踪示例](learning/veadk-python/examples/tracing.md) |  | 2026-08-05 | - |
| [云服务集成指南](learning/veadk-python/extensions/cloud-integration.md) |  | 2026-08-05 | - |
| [自定义Extension开发指南](learning/veadk-python/extensions/custom-extension.md) |  | 2026-08-05 | - |
| [自定义RunProcessor开发指南](learning/veadk-python/extensions/custom-run-processor.md) |  | 2026-08-05 | - |
| [自定义工具开发完整指南](learning/veadk-python/extensions/custom-tool.md) |  | 2026-08-05 | - |
| [最佳实践与常见反模式](learning/veadk-python/faq/best-practices.md) |  | 2026-08-05 | - |
| [常见问题排查](learning/veadk-python/faq/troubleshooting.md) |  | 2026-08-05 | - |
| [AgentKit 应用工厂使用指南](learning/veadk-python/getting-started/agentkit-app.md) | AgentKit 应用工厂 create_agentkit_app 使用指南，介绍如何将 VeADK Agent 包装为生产级 Web 服务 | 2026-08-05 | - |
| [配置指南](learning/veadk-python/getting-started/configuration.md) | VeADK-Python 配置指南，涵盖配置优先级、最小配置、config.yaml参考、环境变量列表、API Key获取及配置降级策略 | 2026-08-05 | - |
| [安装指南](learning/veadk-python/getting-started/installation.md) | VeADK-Python 安装指南，涵盖系统要求、PyPI安装、uv安装、源码构建、验证安装及常见问题 | 2026-08-05 | - |
| [快速入门：Hello World](learning/veadk-python/getting-started/quickstart.md) | VeADK-Python 快速入门教程，5分钟创建你的第一个AI Agent，包含完整可运行代码和逐行解释 | 2026-08-05 | - |
| [Agent2Agent(A2A)协议支持](learning/veadk-python/modules/a2a.md) |  | 2026-08-05 | - |
| [AgentBuilder 使用指南](learning/veadk-python/modules/agent-builder.md) |  | 2026-08-05 | - |
| [Agent 类完整 API 参考](learning/veadk-python/modules/agent.md) |  | 2026-08-05 | - |
| [认证与凭证服务](learning/veadk-python/modules/auth.md) |  | 2026-08-05 | - |
| [CLI命令行工具参考](learning/veadk-python/modules/cli.md) |  | 2026-08-05 | - |
| [云部署集成](learning/veadk-python/modules/cloud.md) |  | 2026-08-05 | - |
| [配置系统详解](learning/veadk-python/modules/config.md) |  | 2026-08-05 | - |
| [知识库(RAG)详解](learning/veadk-python/modules/knowledgebase.md) |  | 2026-08-05 | - |
| [记忆系统详解（ShortTermMemory & LongTermMemory）](learning/veadk-python/modules/memory.md) |  | 2026-08-05 | - |
| [模型配置](learning/veadk-python/modules/models.md) |  | 2026-08-05 | - |
| [多模态能力](learning/veadk-python/modules/multimodal.md) |  | 2026-08-05 | - |
| [Prompt管理与优化](learning/veadk-python/modules/prompts.md) |  | 2026-08-05 | - |
| [Runner 类 API 参考](learning/veadk-python/modules/runner.md) |  | 2026-08-05 | - |
| [Skills 技能系统详解](learning/veadk-python/modules/skills.md) |  | 2026-08-05 | - |
| [Tools 工具系统详解](learning/veadk-python/modules/tools.md) |  | 2026-08-05 | - |
| [可观测性与Tracing](learning/veadk-python/modules/tracing.md) |  | 2026-08-05 | - |
| [VeADK-Python API 索引](learning/veadk-python/references/api-index.md) | VeADK-Python 核心公开类与函数快速索引表 | 2026-08-05 | - |
| [V阶段：对抗审查报告（多视角质量验证）](learning/veadk-python/supporting-analysis/14-adversarial-review.md) | VeADK-Python Wiki 四视角对抗审查报告，包含12个问题发现、关键问题修正记录、20个API签名抽查结果（准确率90%）及改进建议 | 2026-08-05 | VeADK、对抗审查、质量验证、文档审查、多视角 |
| [V阶段：最终交付清单](learning/veadk-python/supporting-analysis/15-final-delivery.md) | VeADK-Python Wiki V阶段最终交付物清单，包含完整文档列表、统计信息、结构树和遗留问题说明 | 2026-08-05 | VeADK、最终交付、验收清单、版本发布 |

### methods

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Token优化技术方法总览](learning/llm-token-optimization/02-methods/00-methods-overview.md) |  |  | overview、token-optimization、llm、methods |
| [提示词工程优化](learning/llm-token-optimization/02-methods/01-prompt-engineering.md) |  |  | prompt-engineering、token-optimization、llm |
| [上下文压缩技术](learning/llm-token-optimization/02-methods/02-context-compression.md) |  |  | context-compression、rag、summarization、llmlingua、token-optimization |
| [模型微调与蒸馏](learning/llm-token-optimization/02-methods/03-fine-tuning-distillation.md) |  |  | fine-tuning、lora、distillation、quantization、speculative-decoding、token-optimization |
| [增量推理与缓存](learning/llm-token-optimization/02-methods/04-inference-caching.md) |  |  | kv-cache、pagedattention、prefix-caching、semantic-cache、vllm、inference、token-optimization |
| [多轮对话管理](learning/llm-token-optimization/02-methods/05-dialog-management.md) |  |  | dialog-management、conversation-state、history-truncation、entity-tracking、sliding-window、token-optimization |

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。 | 2026-06-30 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
| [Frontmatter 路径与链接批量修复流程指南](operations/frontmatter-link-batch-repair-guide.md) | 大规模 frontmatter 路径与 Markdown 链接批量修复的完整流程指南：问题分类诊断、8 阶段分层修复策略、external 标记约定、LF 行尾保留、TOML source 覆盖问题处理，附 8 个自动化脚本的使用参考 | 2026-07-10 | frontmatter、链接修复、批量修复、check-links、路径规范化、external标记 |
| [HTML 正文提取操作指南](operations/html-body-extraction.md) | HTML 正文提取双方案：正则提取（首选）与边界标记索引截取法（兜底），含 HTML 清洗六步流程，适用于复杂嵌套 HTML 容器 | 2026-06-29 | html、正文提取、正则、索引截取、边界标记、html清洗、降级策略 |
| [临时知识库归档规则正文](operations/p0-02-knowledge-archive-rules.md) | 定义临时知识库与正式知识库的分层关系、分类规则、状态与优先级字段、最小元数据、自动归档触发条件、正式目录映射、保留与回退策略、索引结构、一致性校验项和异常修复闭环。 |  | - |
| [任务分类与追踪骨架说明](operations/p0-05-task-classification-skeleton.md) | 定义 tasks/ 目录的三维正式分类骨架（task-types / business-domains / project-stages）、使用原则、临时历史目录定位和查找入口。 |  | - |
| [Docker 镜像构建与运行手册摘要](operations/p1-06-docker-image-build-run.md) | Conda/Podman 镜像构建与运行手册，覆盖 Dockerfile 片段、构建命令、交互运行与挂载工作目录的标准操作。 |  | - |
| [测试依赖安装说明](operations/p1-07-test-deps-install.md) | 工作区测试环境的依赖安装命令，覆盖 tqdm、tensorboard、pytorch-ignite 等测试依赖的 pip 安装。 |  | - |
| [Windows 沙盒安装与配置操作手册摘要](operations/p1-08-windows-sandbox-guide.md) | Windows 沙盒从零到可用的安装与配置手册，覆盖版本检查、虚拟化启用、图形界面/PowerShell 启用、隔离验证、网络与共享策略、.wsb 一键启动模板及常见故障排查。 |  | - |
| [DaoMind 部署上线指南摘要](operations/p1-11-daomind-deployment-guide.md) | DaoMind 部署上线操作手册，覆盖 GitHub Pages 文档站部署、create-daomind CLI 的 npm 发布、部署验证、上线后监控与常见排错速查。 |  | - |
| [TVM VTA 容器构建与 Nuitka 打包流水线说明](operations/p2-14-tvm-vta-nuitka-pipeline.md) | hub/sync 本地附加分析说明，覆盖 TVM VTA 构建容器（Podman + Invoke）与 Nuitka wheel 打包流水线的目录导航、命令入口、跨平台连接方式与报告约定。 |  | - |
| [npm monorepo 包发布与 GitHub Release 操作流程](operations/p2-15-npm-github-release-guide.md) | TypeScript monorepo 项目使用 pnpm 工作区发布 npm 包并创建 GitHub Release 的完整操作流程与故障排查指南 |  | - |
| [关键路径工具失败降级矩阵](operations/tool-failure-degradation-matrix.md) | 关键路径工具失败的三级降级决策矩阵：网页内容获取、文件搜索、命令执行、子代理委派四类关键路径的降级策略、触发条件与决策流程 | 2026-07-06 | 工具降级、降级矩阵、webfetch、defuddle、浏览器mcp、关键路径、三级降级、标准化 |
| [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md) | 一条可落地执行、可观测验收的 Tuya IPC（网络摄像机）端-云-手机最小闭环跑通路径：先明确最小假设，再按步骤给出依赖/验收/排查，并附依赖关系图与闭环验收总表。 | 2026-06-30 | tuya、ipc、iot、闭环、配网、音视频、设备绑定、事件上报、联调、排查、验收 |
| [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md) | 当需要在 SpecWeave 中新增或使用 flexloop 相关功能时，基于三区域边界模型和四不原则的5种合规集成路径决策指南 | 2026-06-29 | vendor、flexloop、agentforge、submodule、集成方案、三区域模型、四不原则 |
| [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md) | 微信公众号文章内容提取双路径决策模型：defuddle CLI 与 PowerShell Invoke-WebRequest 互为兜底，含边界标记索引截取法作为正则失败时的兜底方案 | 2026-06-29 | 微信公众号、内容提取、defuddle、powershell、invoke-webrequest、html提取、反爬、降级策略 |
| [Windows平台兼容性手册：AI智能体执行任务陷阱系统化指南](operations/windows-platform-compatibility-guide.md) | 系统化记录 Windows 平台执行任务时的10类陷阱（编码、URL解析、路径分隔符、命令链接、引号差异、heredoc、管道、脚本扩展、行尾符、环境变量），整合项目已有4个Windows文档并提供统一索引与快速诊断流程 | 2026-07-06 | windows、powershell、platform-compatibility、url-parsing、encoding、path-separator、shell-differences、quoting、line-ending、ai-agent |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |
| [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md) | 记录 Windows PowerShell 下将 Python 中文 stdout 通过文本管道写入文件时可能发生的转码污染，以及推荐的安全写回方案 | 2026-06-30 | windows、powershell、encoding、utf-8、pipe、set-content、python、docs |
| [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md) | 系统性解决Windows终端中文乱码问题的完整指南，涵盖系统级/用户级/项目级三层配置方案 | 2026-07-01 | windows、powershell、cmd、utf-8、encoding、gbk、chcp、乱码 |

### platform

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [工作区代理治理基线摘要](platform/p0-01-agent-governance-baseline.md) | chaos 工作区的代理治理入口，定义角色分工、协作规则、权限边界、临时知识库摘要和 SpecWeave 外部绑定入口。 |  | - |

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

### tech

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [caffe-ffi Conv v4 OpenMP 并行优化技术总结](tech/caffe-ffi-conv-v4-optimization-summary.md) | caffe-ffi Conv 层 OpenMP 并行优化（v4）的技术总结，覆盖并行策略、环境变量配置、抖动诊断与生产部署指南，供团队内部分享。 |  | - |
| [GLM 大模型调用可复用示例（本地加载 + API 调用）](tech/glm-model-call-example.md) | 从 chaos/flexloop/models 沉淀的 GLM 大模型调用可复用示例：本地模型加载（transformers + torch）与 Z.AI 云端 API 调用（zai-sdk）两种方式，含脱敏代码与环境变量配置说明。 | 2026-08-07 | glm、llm、transformers、zai、huggingface、python |
| [ListenHub API 规范——Authentication（认证与基础 URL）](tech/listenhub-api-authentication.md) | 沉淀 ListenHub 开放平台的统一认证规范：环境变量 LISTENHUB_API_KEY、基础 URL、必备请求头（Authorization/Content-Type/X-Source）、curl 模板与安全注意事项。所有 Key 均以占位符表示。 | 2026-08-07 | listenhub、api、authentication、security、marswave |
| [ListenHub API 规范——Image Generation（AI 图片生成）](tech/listenhub-api-image.md) | 沉淀 ListenHub AI 图片生成接口规范：POST /images/generation，记录请求参数（provider/prompt/model/imageConfig/referenceImages）、宽高比表、参考图 URL/base64 两种格式、同步 base64 返回与调用要点。 | 2026-08-07 | listenhub、api、image-gen、image-generation、gemini、marswave |
| [ListenHub API 规范——Podcast（播客节目生成）](tech/listenhub-api-podcast.md) | 沉淀 ListenHub 播客生成接口规范：POST /podcast/episodes 创建节目、GET /podcast/episodes/{episodeId} 查询状态结果，记录接口用途、关键参数（speakers/query/sources/language/mode）与调用要点（异步轮询、两段式生成）。 | 2026-08-07 | listenhub、api、podcast、marswave |
| [ListenHub API 规范——Speakers（主播列表）](tech/listenhub-api-speakers.md) | 沉淀 ListenHub 主播列表接口规范：GET /speakers/list，记录查询参数（language/status）、响应字段（name/speakerId/demoAudioUrl/gender/language）与调用要点；含内置默认主播表。 | 2026-08-07 | listenhub、api、speakers、marswave |
| [ListenHub API 规范——Storybook（解说视频/故事本）](tech/listenhub-api-storybook.md) | 沉淀 ListenHub 解说视频（Storybook）接口规范：POST /v1/storybook/episodes 创建、GET 查询状态结果、POST /v1/storybook/episodes/{episodeId}/video 触发视频生成，记录参数（sources/speakers/language/mode）、mode 取值与调用要点。 | 2026-08-07 | listenhub、api、storybook、explainer、video、marswave |
| [ListenHub API 规范——TTS / Speech（文本转语音）](tech/listenhub-api-tts.md) | 沉淀 ListenHub 文本转语音（TTS）两套接口规范：/v1/tts（单声、低延迟、同步 MP3 流）与 /v1/speech（多角色脚本转音频），记录接口用途、关键参数与调用要点。 | 2026-08-07 | listenhub、api、tts、speech、marswave |
| [ListenHub 技能集总览——asr/tts/podcast/image-gen/content-parser/explainer 设计模式与共享规范](tech/listenhub-skill-set-overview.md) | 沉淀 flexloop chaos 技能库中 6 个内容生成类 AI 技能（asr/tts/podcast/image-gen/content-parser/explainer）的触发词、能力定位、API 依赖与共享通用模式（异步轮询/错误处理/@file/交互式参数收集），并说明已废弃的 listenhub 单体技能状态。 | 2026-08-07 | listenhub、skill、ai-skill、api-integration、design-pattern、marswave |
| [DaoMind 项目概览（道家哲学 TypeScript 框架）](tech/p1-09-daomind-project-overview.md) | DaoMind 是基于道家哲学宇宙论的现代化 TypeScript 框架，采用 pnpm monorepo 架构，核心包覆盖无/有/行动/应用/时序/道宇宙六层抽象，含函数式错误处理与 DaoUniverse 桥接体系。 |  | - |
| [道衍 DaoYan 项目概览（帛书道德经 AI 对话系统）](tech/p1-10-daoyan-project-overview.md) | 道衍是以马王堆帛书版《道德经》为权威底本的 AI 智慧对话系统，融合道家无为、佛家直心与 ψ=ψ(ψ) 万物理论，支持 5 大 AI 模型切换与 Agent API/MCP 开放接入。 |  | - |
| [DaoMind 2.0 哲学架构：无名/有名与 TypeScript 类型系统映射](tech/p1-13-daomind-philosophy-architecture.md) | DaoMind 2.0 将帛书《道德经》"无名/有名"哲学概念与 TypeScript 类型/值空间进行映射，建立了独特的哲学驱动架构设计模式 |  | - |
| [MCP 技能开发与 REST API 集成规范——以道衍为例](tech/p1-17-daoyan-mcp-skill-spec.md) | 以道衍（DaoYan）MCP Server 为例，说明 AI IDE 技能（Skill）定义、MCP 工具配置、REST API 调用与回答规范的完整模式 |  | - |
| [Reasonix 架构：Python AI Agent 分层设计模式](tech/p1-18-reasonix-architecture.md) | DeepSeek-Reasonix 是一个配置驱动、多模型协作的 AI Coding Agent，采用清晰的分层架构（组装器+Provider+Agent+Controller），是 Python AI Agent 项目的优秀架构参考 |  | - |
| [TVM Relax 前端 MLP 实验记录](tech/p2-13-tvm-relax-mlp-experiment.md) | TVM Relax 前端 nn.Module API 的最小 MLP 实验，展示从模型定义到 export 导出链路的验证样例，可作为 Relax 前端学习与回归参考。 |  | - |
| [TVM FFI 教程总览](tech/tvm-ffi-wiki/00-overview.md) | Apache TVM FFI 中文wiki教程总览 | 2026-07-28 | tvm-ffi、ffi、c++、python、ml-system |
| [项目结构说明](tech/tvm-ffi-wiki/01-project-structure.md) |  | 2026-07-28 | tvm-ffi、project-structure |
| [Any/AnyView 类型系统](tech/tvm-ffi-wiki/02-any-type.md) |  | 2026-07-28 | tvm-ffi、type-system、any、type-erasure |
| [Object 对象系统](tech/tvm-ffi-wiki/03-object-system.md) |  | 2026-07-28 | tvm-ffi、object、reference-counting、inheritance |
| [Function 函数与全局注册表](tech/tvm-ffi-wiki/04-function-registry.md) |  | 2026-07-28 | tvm-ffi、function、packed-func、registry |
| [Container 容器类型](tech/tvm-ffi-wiki/05-containers.md) |  | 2026-07-28 | tvm-ffi、container、array、map、tensor |
| [Reflection 反射系统](tech/tvm-ffi-wiki/06-reflection.md) |  | 2026-07-28 | tvm-ffi、reflection、dataclass、stubgen |
| [Module 模块系统](tech/tvm-ffi-wiki/07-module-system.md) |  | 2026-07-28 | tvm-ffi、module、dynamic-loading、dll |
| [C++ 开发指南](tech/tvm-ffi-wiki/08-cpp-guide.md) |  | 2026-07-28 | tvm-ffi、cpp、guide、cmake、build |
| [Python 开发指南](tech/tvm-ffi-wiki/09-python-guide.md) |  | 2026-07-28 | tvm-ffi、python、guide、cython |
| [构建与打包](tech/tvm-ffi-wiki/10-build-packaging.md) |  | 2026-07-28 | tvm-ffi、build、cmake、packaging、wheel |
| [实战案例](tech/tvm-ffi-wiki/11-examples.md) |  | 2026-07-28 | tvm-ffi、examples、tutorial、kernel |
| [常见问题解答 (FAQ)](tech/tvm-ffi-wiki/12-faq.md) |  | 2026-07-28 | tvm-ffi、faq、troubleshooting |
| [核心源码解析（进阶）](tech/tvm-ffi-wiki/13-source-analysis.md) |  | 2026-07-28 | tvm-ffi、source-code、internals、advanced |

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
| [caffe-ffi-perf-instrumentation-template](caffe-ffi-perf-instrumentation-template.md) |  |  | - |
| [stage-guardrails-guide](stage-guardrails-guide.md) |  |  | - |
| [three-layer-routing](three-layer-routing.md) |  |  | - |
| [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md) |  |  | - |
| [Caffe-Slim TVM FFI 环境调试与错误排查手册](best-practices/caffe-slim-tvm-ffi-troubleshooting.md) |  | 2026-07-27 | caffe-slim、tvm-ffi、troubleshooting、ffi、python-bindings、wsl、environment-debugging、dlpack |
| [L2 渐进式披露机制优化建议](best-practices/l2-progressive-disclosure-optimization.md) |  | 2026-07-12 | - |
| [L2 渐进式披露加载器性能优化：实测基线、优化建议与实施记录（P0+P1+P2完成）](best-practices/l2-progressive-disclosure-performance.md) |  | 2026-07-12 | - |
| [PowerShell NativeBuild 构建常见问题 FAQ](best-practices/powershell-nativebuild-faq.md) |  | 2026-08-02 | powershell、nativebuild、vsdevshell、msvc、conda、troubleshooting、build、windows、faq、hardcoded-paths |
| [NativeBuild 三层架构重构总结（团队学习文档）](best-practices/powershell-nativebuild-refactoring-summary.md) |  | 2026-08-02 | powershell、nativebuild、refactoring、three-layer-architecture、vsdevshell、conda、msvc、modularization、retrospective、team-learning |
| [PowerShell安全下载文件最佳实践——三重防御验证指南](best-practices/powershell-secure-download-verification.md) |  |  | PowerShell、HTTPS、文件下载、安全、证书验证、最佳实践、脚本工具 |
| [sensitive-info-desensitization-spec](best-practices/sensitive-info-desensitization-spec.md) |  |  | - |
| [spec-loader-cold-start-storm-contingency](best-practices/spec-loader-cold-start-storm-contingency.md) |  |  | - |
| [spec-loader-config-guide](best-practices/spec-loader-config-guide.md) |  |  | - |
| [文档标题](docs-separation-guide/DOC_TEMPLATE.md) |  |  | - |
| [格式规范指南](docs-separation-guide/FORMAT_GUIDE.md) |  |  | - |
| [文档分离方案知识库](docs-separation-guide/index.md) |  |  | - |
| [知识图谱示例](docs-separation-guide/KNOWLEDGE_GRAPH_EXAMPLE.md) |  |  | - |
| [维护指南](docs-separation-guide/MAINTENANCE_GUIDE.md) |  |  | - |
| [通用知识](docs-separation-guide/general/index.md) |  |  | - |
| [七概念方法论](docs-separation-guide/general/domain/index.md) |  |  | - |
| [第一性原理](docs-separation-guide/general/philosophy/index.md) |  |  | - |
| [变更日志](docs-separation-guide/tech/changelog.md) |  |  | - |
| [部署指南](docs-separation-guide/tech/deploy.md) |  |  | - |
| [核心功能](docs-separation-guide/tech/features.md) |  |  | - |
| [核心知识](docs-separation-guide/tech/index.md) |  |  | - |
| [项目概述](docs-separation-guide/tech/intro.md) |  |  | - |
| [快速开始](docs-separation-guide/tech/quickstart.md) |  |  | - |
| [API 参考](docs-separation-guide/tech/api/index.md) |  |  | - |
| [设计哲学](docs-separation-guide/topics/design-philosophy.md) |  |  | - |
| [深度研究](docs-separation-guide/topics/index.md) |  |  | - |
| [行业分析](docs-separation-guide/topics/industry-analysis.md) |  |  | - |
| [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/audiox-turbo-audio-generation-wiki.md) |  | 2026-07-04 | AudioX-Turbo、音频生成、音乐生成、视频配音、扩散模型、模型蒸馏、AI开源、多模态、Anything-to-Audio、Distribution-Matching-Distillation、师生蒸馏 |
| [抖音 Vibecoding 人气赛道·执行行动计划](learning/douyin-vibecoding-action-plan.md) |  |  | vibecoding、抖音、执行计划、行动指南、TRAE大赛 |
| [SpecWeave 抖音VibeCoding图文·视觉设计规范](learning/douyin-vibecoding-design-spec.md) |  |  | vibecoding、抖音、设计规范、视觉设计、SpecWeave |
| [dspark-paper-wiki](learning/02-agent-engineering-methodology/dspark-paper-wiki.md) |  |  | - |
| [从 Prompt 到 Loop：四层工程打造稳定可控的 AI Agent](learning/02-agent-engineering-methodology/workbuddy-four-layers-seven-concepts-analysis.md) |  | 2026-07-14 | 七概念、Agent工程、Context Engineering、Harness Engineering、Loop Engineering、四层工程范式、事实核查通过 |
| [zhihu-article-seven-concepts-wiki-creation-publish](learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/zhihu-article-seven-concepts-wiki-creation-publish.md) |  |  | - |
| [Headroom：概述与学习目标](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/00-overview.md) |  |  | - |
| [核心架构与设计理念](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/01-core-architecture.md) |  |  | - |
| [六种压缩算法详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/02-compression-algorithms.md) |  |  | - |
| [CCR可逆机制深度解析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/03-ccr-mechanism.md) |  |  | - |
| [四种接入方式详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/04-integration-methods.md) |  |  | - |
| [效果验证与数据分析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/05-performance-data.md) |  |  | - |
| [跨Agent记忆与自动学习](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/06-advanced-features.md) |  |  | - |
| [快速上手指南](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/07-quick-start.md) |  |  | - |
| [深度洞察与模式萃取](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/08-insights-patterns.md) |  |  | - |
| [常见问题与资源链接](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/09-faq-resources.md) |  |  | - |
| [总结与Takeaways](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/10-summary.md) |  |  | - |
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
| [七概念→DeepTutor映射总览表](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/00-framework-mapping.md) |  | 2026-07-14 | 分析、映射、总览 |
| [R复盘在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/01-r-in-deeptutor.md) |  | 2026-07-14 | 分析、R、复盘、Memory |
| [I洞察在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/02-i-in-deeptutor.md) |  | 2026-07-14 | 分析、I、洞察、Mastery Path |
| [E萃取在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/03-e-in-deeptutor.md) |  | 2026-07-14 | 分析、E、萃取、Knowledge Center |
| [C原子提交在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/04-c-in-deeptutor.md) |  | 2026-07-14 | 分析、C、原子提交、模式切换 |
| [A原子化在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/05-a-in-deeptutor.md) |  | 2026-07-14 | 分析、A、原子化、模块设计 |
| [F第一性原理在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/06-f-in-deeptutor.md) |  | 2026-07-14 | 分析、F、第一性原理、架构设计 |
| [V对抗性审查在DeepTutor中的体现](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/07-v-in-deeptutor.md) |  | 2026-07-14 | 分析、V、对抗性审查、Quiz、Mastery Path |
| [组合工作流分析](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/03-analysis/08-combined-workflows.md) |  | 2026-07-14 | 分析、工作流、组合、R-I-E、A-V-C、F-V-I |
| [分阶段阅读路径](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/00-reading-guide.md) |  | 2026-07-14 | 阅读路径、学习指南 |
| [实践练习](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/01-practice-exercises.md) |  | 2026-07-14 | 练习、实践 |
| [自学质量检查清单](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/02-self-checklist.md) |  | 2026-07-14 | 自检、清单、工具 |
| [延伸阅读](learning/02-agent-engineering-methodology/seven-concepts-deeptutor-wiki/04-learning-path/03-further-reading.md) |  | 2026-07-14 | 延伸阅读、资源 |
| [AReaL 2.0 官方实战教程：从安装到在线RL微服务部署](learning/03-agent-platforms-tools/areal-official-practical-wiki.md) |  | 2026-08-04 | areal、rl-training、agentic-rl、online-rl、llm-alignment、distributed-training、pytorch、sglang、vllm、fsdp、megatron |
| [BrowserAct 官网完整学习教程：Cloud+Local双模式Agent浏览器平台](learning/03-agent-platforms-tools/browseract-official-wiki.md) |  | 2026-08-03 | browseract、ai-agent、browser-automation、web-scraping、cloud、skillhub、data-api、zapier、n8n、residential-proxy |
| [LangGraph 生产级落地实施路线图](learning/03-agent-platforms-tools/langgraph-implementation-roadmap.md) |  | 2026-08-04 | - |
| [一、概述](learning/03-agent-platforms-tools/i-have-adhd-wiki/00-overview.md) |  |  | - |
| [二、设计理念](learning/03-agent-platforms-tools/i-have-adhd-wiki/01-design-philosophy.md) |  |  | - |
| [三、核心规则](learning/03-agent-platforms-tools/i-have-adhd-wiki/02-core-rules.md) |  |  | - |
| [四、例外场景与自检清单](learning/03-agent-platforms-tools/i-have-adhd-wiki/03-exceptions-and-checklist.md) |  |  | - |
| [五、跨平台安装指南](learning/03-agent-platforms-tools/i-have-adhd-wiki/04-installation-guide.md) |  |  | - |
| [六、持久化机制详解](learning/03-agent-platforms-tools/i-have-adhd-wiki/05-always-on-mechanism.md) |  |  | - |
| [七、评估框架与质量保障](learning/03-agent-platforms-tools/i-have-adhd-wiki/06-evaluation-framework.md) |  |  | - |
| [八、自定义开发与故障排查](learning/03-agent-platforms-tools/i-have-adhd-wiki/07-customization-and-troubleshooting.md) |  |  | - |
| [九、可复用模式萃取](learning/03-agent-platforms-tools/i-have-adhd-wiki/08-patterns-extracted.md) |  |  | - |
| [十、FAQ与资源汇总](learning/03-agent-platforms-tools/i-have-adhd-wiki/09-faq-and-resources.md) |  |  | - |
| [十一、行动优先输出范式深度解析](learning/03-agent-platforms-tools/i-have-adhd-wiki/10-action-first-paradigm.md) |  |  | - |
| [十二、逆向适配创新方法论](learning/03-agent-platforms-tools/i-have-adhd-wiki/11-reverse-adaptation-innovation.md) |  |  | - |
| [十三、设计取舍与技术写作借鉴](learning/03-agent-platforms-tools/i-have-adhd-wiki/12-design-tradeoffs-and-writing.md) |  |  | - |
| [七概念方法论解析MonkeyCode开源Vibe Coding平台](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/00-overview.md) |  |  | 七概念、MonkeyCode、Vibe Coding、开源、私有化部署、AI编码 |
| [第一章 - 七概念知识框架](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/01-seven-concepts-framework.md) |  |  | 七概念、R-I-E-C-A-F-V、方法论、认知框架 |
| [第二章 - MonkeyCode产品深度解析](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/02-monkeycode-deep-analysis.md) |  |  | MonkeyCode、Vibe Coding、长亭科技、开源、私有化部署、安全审计 |
| [第三章 - 实践操作指南](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/03-practice-guide.md) |  |  | 实践指南、部署教程、MonkeyCode、私有化部署、Docker |
| [第四章 - 常见问题解答（FAQ）](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/04-faq.md) |  |  | FAQ、常见问题、MonkeyCode、故障排查、部署问题 |
| [第五章 - 资源扩展链接](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/05-resources.md) |  |  | 资源链接、MonkeyCode、Vibe Coding、开源项目、私有化部署 |
| [第六章 - 学习效果评估方法](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/06-assessment.md) |  |  | 学习评估、效果检验、知识测试、实践评估、七概念 |
| [第七章 - 附录：七概念应用案例](learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/07-seven-concepts-applied.md) |  |  | 七概念应用、实战案例、R-I-E-C-A-F-V、产品分析 |
| [一、概述](learning/04-mathematics-foundations/pythagorean-theorem-wiki/00-overview.md) |  |  | - |
| [二、历史沿革](learning/04-mathematics-foundations/pythagorean-theorem-wiki/02-history.md) |  |  | - |
| [三、经典证明方法](learning/04-mathematics-foundations/pythagorean-theorem-wiki/03-proof-methods.md) |  |  | - |
| [四、勾股数](learning/04-mathematics-foundations/pythagorean-theorem-wiki/04-pythagorean-triples.md) |  |  | - |
| [五、推广与扩展](learning/04-mathematics-foundations/pythagorean-theorem-wiki/05-generalizations.md) |  |  | - |
| [六、应用领域](learning/04-mathematics-foundations/pythagorean-theorem-wiki/06-applications.md) |  |  | - |
| [七、文化意义](learning/04-mathematics-foundations/pythagorean-theorem-wiki/07-cultural-significance.md) |  |  | - |
| [八、常见问题与误解](learning/04-mathematics-foundations/pythagorean-theorem-wiki/08-faqs.md) |  |  | - |
| [九、学习资源](learning/04-mathematics-foundations/pythagorean-theorem-wiki/09-resources.md) |  |  | - |
| [一、概述](learning/05-academic-skills/thesis-writing-wiki/00-overview.md) |  |  | - |
| [二、全流程时间线](learning/05-academic-skills/thesis-writing-wiki/01-full-process-timeline.md) |  |  | - |
| [三、选题与开题](learning/05-academic-skills/thesis-writing-wiki/02-topic-selection-and-proposal.md) |  |  | - |
| [四、文献综述](learning/05-academic-skills/thesis-writing-wiki/03-literature-review.md) |  |  | - |
| [五、研究方法](learning/05-academic-skills/thesis-writing-wiki/04-research-methods.md) |  |  | - |
| [六、论文结构与各章写作](learning/05-academic-skills/thesis-writing-wiki/05-paper-structure.md) |  |  | - |
| [七、格式规范与排版](learning/05-academic-skills/thesis-writing-wiki/06-formatting-and-style.md) |  |  | - |
| [八、修改与润色](learning/05-academic-skills/thesis-writing-wiki/07-revision-and-polishing.md) |  |  | - |
| [九、答辩准备](learning/05-academic-skills/thesis-writing-wiki/08-defense-preparation.md) |  |  | - |
| [十、常见问题与避坑指南](learning/05-academic-skills/thesis-writing-wiki/09-faqs-and-pitfalls.md) |  |  | - |
| [十一、资源与工具](learning/05-academic-skills/thesis-writing-wiki/10-resources-and-tools.md) |  |  | - |
| [十二、社会语言学视频资源](learning/05-academic-skills/thesis-writing-wiki/11-sociolinguistics-video-resources.md) |  |  | - |
| [ian-xiaohei-illustrations](learning/05-ai-multimodal-content/ian-xiaohei-illustrations.md) |  |  | - |
| [cleaned-article](learning/06-business-trends-analysis/ai-hardware-design-tools-wiki/cleaned-article.md) |  |  | - |
| [微软Copilot成本困境与多模型时代产业变革深度分析报告](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/analysis-report.md) |  | 2026-07-09 | AI产业、微软Copilot、DeepSeek、多模型架构、成本分析、产业趋势、开源模型 |
| [cleaned-article](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/cleaned-article.md) |  |  | - |
| [Copilot发展历程与成本困境深度分析](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task2-copilot-analysis.md) |  |  | - |
| [DeepSeek V4技术优势与融资战略深度解析](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task3-deepseek-analysis.md) |  |  | - |
| [多模型时代四家典型产品策略系统对比分析](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task4-multimodel-comparison.md) |  |  | - |
| [从Copilot成本困境看多模型时代产业趋势转变深度洞察](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task5-industry-trends.md) |  |  | - |
| [task6-quality-assessment](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task6-quality-assessment.md) |  | 2026-07-09 | - |
| [个人理解与批判性思考](learning/06-business-trends-analysis/copilot-cost-multimodel-era-wiki/task7-personal-insights.md) |  |  | - |
| [开源EMS能源管理系统深度洞察分析报告](learning/06-business-trends-analysis/ems-energy-management-wiki/analysis-report.md) |  | 2026-07-09 | - |
| [支持 50 多种协议，终于开源了。](learning/06-business-trends-analysis/ems-energy-management-wiki/cleaned-article.md) |  | 2026-07-09 | - |
| [理论框架：七概念理论详解](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/01-theory-framework.md) |  | 2026-07-14 | - |
| [事件分析：印度塔塔电子泄密事件详解](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/02-event-analysis.md) |  | 2026-07-14 | - |
| [七概念理论应用指南](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/03-concepts-application.md) |  | 2026-07-14 | - |
| [学习路径与操作指南](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/04-learning-path.md) |  | 2026-07-14 | - |
| [常见问题与注意事项](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/05-faq-notes.md) |  | 2026-07-14 | - |
| [参考资料与附录](learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/06-resources.md) |  | 2026-07-14 | - |
| [raw-content](learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/raw-content.md) |  |  | - |
| [oray-official-website-core-notes](learning/07-vendor-product-learning/oray/oray-official-website-core-notes.md) |  |  | - |
| [百度网盘 Git 同步空间目录结构](learning/08-systems-infrastructure/git-baidu-sync/01-directory-structure.md) |  |  | - |
| [Git 跨平台配置最佳实践（网盘同步场景）](learning/08-systems-infrastructure/git-baidu-sync/02-cross-platform-config.md) |  |  | - |
| [Git 网盘仓库初始化与新设备加入工作流](learning/08-systems-infrastructure/git-baidu-sync/03-repo-init-workflow.md) |  |  | - |
| [Git 网盘同步锁机制设计与实现](learning/08-systems-infrastructure/git-baidu-sync/04-locking-mechanism.md) |  |  | - |
| [05-daily-sync-workflow](learning/08-systems-infrastructure/git-baidu-sync/05-daily-sync-workflow.md) |  |  | - |
| [Git 网盘同步冲突检测与处理](learning/08-systems-infrastructure/git-baidu-sync/06-conflict-detection.md) |  |  | - |
| [Git 网盘同步健康检查与诊断](learning/08-systems-infrastructure/git-baidu-sync/07-health-check.md) |  |  | - |
| [08-performance-optimization](learning/08-systems-infrastructure/git-baidu-sync/08-performance-optimization.md) |  |  | - |
| [Git 网盘同步备份与灾难恢复](learning/08-systems-infrastructure/git-baidu-sync/09-backup-recovery.md) |  |  | - |
| [Git 百度网盘同步 - 故障排查手册](learning/08-systems-infrastructure/git-baidu-sync/10-troubleshooting.md) |  |  | - |
| [Git 百度网盘同步 - 坑点与反模式](learning/08-systems-infrastructure/git-baidu-sync/11-pitfalls-anti-patterns.md) |  |  | - |
| [Caffe include/src 目录依赖关系系统性分析](learning/caffe-architecture-wiki/03-include-src-dependency-analysis.md) |  | 2026-07-23 | - |
| [Protocol Buffers proto2 与 proto3 语法区别系统性分析](learning/caffe-architecture-wiki/04-proto2-vs-proto3-serialization-analysis.md) |  | 2026-07-23 | - |
| [05-docker-pycaffe-standalone-build-postmortem](learning/caffe-architecture-wiki/05-docker-pycaffe-standalone-build-postmortem.md) |  |  | - |
| [06-examples-test-diff-analysis-report](learning/caffe-architecture-wiki/06-examples-test-diff-analysis-report.md) |  |  | - |
| [07-caffe-cpp-slim-tvm-ffi-modernization](learning/caffe-architecture-wiki/07-caffe-cpp-slim-tvm-ffi-modernization.md) |  |  | Caffe、C++、TVM、FFI、DLPack、现代化重构、依赖裁剪、Python绑定 |
| [08-eight-anti-patterns-defensive-templates](learning/caffe-architecture-wiki/08-eight-anti-patterns-defensive-templates.md) |  |  | Caffe、反模式、防御式编程、代码模板、依赖裁剪、C++、Python |
| [Caffe-Slim 全面架构分析与compat层零侵入替换机制](learning/caffe-architecture-wiki/09-caffe-slim-full-architecture-and-compat-zero-intrusion.md) |  | 2026-07-27 | - |
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
| [第1章 - 项目概述与快速开始](learning/intelligent-terminal-wiki/01-overview.md) |  | 2026-08-03 | - |
| [第2章 - 整体架构设计](learning/intelligent-terminal-wiki/02-architecture.md) |  | 2026-08-03 | - |
| [第3章 - WTA Rust 核心 - Master 多路复用器](learning/intelligent-terminal-wiki/03-wta-master.md) |  | 2026-08-03 | - |
| [第4章 - WTA Rust 核心 - Helper 与 TUI](learning/intelligent-terminal-wiki/04-wta-helper-tui.md) |  | 2026-08-03 | - |
| [第5章 - C++ 集成层](learning/intelligent-terminal-wiki/05-cpp-integration.md) |  | 2026-08-03 | - |
| [第6章 - 通信协议栈](learning/intelligent-terminal-wiki/06-protocols.md) |  | 2026-08-03 | - |
| [第7章 - wtcli 命令参考](learning/intelligent-terminal-wiki/07-wtcli-reference.md) |  | 2026-08-03 | - |
| [第8章 - wt-agent-hooks Shell 集成](learning/intelligent-terminal-wiki/08-agent-hooks.md) |  | 2026-08-03 | - |
| [第9章 - Autofix 自动错误检测与修复](learning/intelligent-terminal-wiki/09-autofix.md) |  | 2026-08-03 | - |
| [第10章 - 构建系统与开发环境](learning/intelligent-terminal-wiki/10-build-system.md) |  | 2026-08-03 | - |
| [第11章 - 日志系统与调试](learning/intelligent-terminal-wiki/11-logging-debugging.md) |  | 2026-08-03 | - |
| [第12章 - 配置与设置详解](learning/intelligent-terminal-wiki/12-configuration.md) |  | 2026-08-03 | - |
| [第13章 - 架构设计模式萃取](learning/intelligent-terminal-wiki/13-design-patterns.md) |  | 2026-08-03 | - |
| [大语言模型Token节省机制底层原理事实清单](learning/llm-token-optimization/01-principles/00-facts.md) |  | 2026-08-01 | LLM、Token、Tokenization、Transformer、KV-Cache、PagedAttention、Pricing |
| [01-metrics-framework](learning/llm-token-optimization/05-evaluation/01-metrics-framework.md) |  |  | - |
| [01-facts](learning/miaowu-ambassador-guide/01-facts.md) |  |  | - |
| [I - 洞察 (Insight) - 秒悟大使入驻关键洞察](learning/miaowu-ambassador-guide/02-insights.md) |  | 2026-07-30 | 七概念、I、洞察、秒悟大使、推广返佣 |
| [秒悟大使入驻指南（结构化版）](learning/miaowu-ambassador-guide/miaowu-ambassador-guide.md) |  | 2026-07-30 | 七概念、E、萃取、秒悟大使、入驻指南、推广返佣 |
| [秒悟Meoo实训案例 - 事实采集](learning/miaowu-meoo-practice-cases/archive/01-facts.md) |  | 2026-07-31 | 七概念、R、事实、秒悟、Meoo、实训案例 |
| [秒悟Meoo实训案例 - 核心洞察](learning/miaowu-meoo-practice-cases/archive/02-insights.md) |  | 2026-07-31 | 七概念、I、洞察、秒悟、Meoo |
| [3分钟快速参考卡](learning/trae-ide-token-optimization/04-quick-reference.md) |  | 2026-08-01 | - |
| [术语表](learning/trae-ide-token-optimization/glossary.md) |  | 2026-08-01 | - |
| [参考资料](learning/trae-ide-token-optimization/references.md) |  | 2026-08-01 | - |
| [事实数据采集](learning/trae-ide-token-optimization/01-principles/00-facts.md) |  | 2026-08-01 | - |
| [第一性原理分析](learning/trae-ide-token-optimization/01-principles/01-first-principles.md) |  | 2026-08-01 | - |
| [P-T-001: 静态减负模式](learning/trae-ide-token-optimization/02-patterns/P-T-001-static-reduction.md) |  | 2026-08-01 | - |
| [P-T-002: 对话清理模式](learning/trae-ide-token-optimization/02-patterns/P-T-002-chat-cleanup.md) |  | 2026-08-01 | - |
| [P-T-003: 模型分级模式](learning/trae-ide-token-optimization/02-patterns/P-T-003-model-tiering.md) |  | 2026-08-01 | - |
| [P-T-004: 输入精简模式](learning/trae-ide-token-optimization/02-patterns/P-T-004-input-concise.md) |  | 2026-08-01 | - |
| [P-T-005: 循环熔断模式](learning/trae-ide-token-optimization/02-patterns/P-T-005-loop-breaker.md) |  | 2026-08-01 | - |
| [快速检查清单](learning/trae-ide-token-optimization/03-decision-framework/01-quick-checklist.md) |  | 2026-08-01 | - |
| [veadk/ 目录结构清单](learning/veadk-python/supporting-analysis/01-module-inventory.md) |  |  | - |
| [Agent 类公开方法和属性签名提取](learning/veadk-python/supporting-analysis/02-agent-class-signatures.md) |  |  | - |
| [pyproject.toml 依赖清单](learning/veadk-python/supporting-analysis/03-dependencies.md) |  |  | - |
| [examples/ 目录示例清单](learning/veadk-python/supporting-analysis/04-examples-inventory.md) |  |  | - |
| [核心类清单](learning/veadk-python/supporting-analysis/05-core-classes-list.md) |  |  | - |
| [Agent 初始化流程事实记录](learning/veadk-python/supporting-analysis/06-agent-init-flow.md) |  |  | - |
| [Runner 类事实记录](learning/veadk-python/supporting-analysis/07-runner-facts.md) |  |  | - |
| [Memory 模块事实记录](learning/veadk-python/supporting-analysis/08-memory-facts.md) |  |  | - |
| [KnowledgeBase 模块事实记录](learning/veadk-python/supporting-analysis/09-knowledgebase-facts.md) |  |  | - |
| [Tools 注册表事实记录](learning/veadk-python/supporting-analysis/10-tools-registry-facts.md) |  |  | - |
| [VeADK架构洞察与设计模式分析](learning/veadk-python/supporting-analysis/11-architecture-insights.md) |  |  | - |
| [VeADK扩展点清单与注册机制](learning/veadk-python/supporting-analysis/12-extension-points.md) |  |  | - |
| [VeADK模块依赖关系与分层架构](learning/veadk-python/supporting-analysis/13-module-dependencies.md) |  |  | - |
| [Caffe Docker 容器构建与运行 SOP](operations/caffe-docker-sop.md) |  | 2026-07-22 | caffe、docker、sop、build、runtime、verification |
| [discourse-api-research](operations/discourse-api-research.md) |  |  | - |
| [SaaS云文档DOM提取多平台适配方案](operations/saas-doc-dom-extraction-multi-platform.md) |  |  | - |
| [找三个人杠一遍：对抗评审标准化SOP](quality-assurance/adversarial-review-sop.md) |  |  | - |
| [如何高效啃技术文档？七概念实战案例](quality-assurance/reading-tech-docs-case.md) |  |  | - |
| [知识评审清单模板（2份开箱即用）](quality-assurance/review-checklist-templates.md) |  |  | - |
| [没人帮你杠？四种自己给自己挑错的方法](quality-assurance/solo-review-methods.md) |  |  | - |
| [knowledge-entry-template](templates/knowledge-entry-template.md) |  |  | - |

---

*索引自动生成于 2026-08-07 15:46:04*
