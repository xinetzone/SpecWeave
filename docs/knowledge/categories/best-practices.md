---
type: Reference
title: "分类索引：best-practices"
---

# 分类索引：best-practices

- [返回分类总索引](../category-index.md)
- [返回知识库首页](../README.md)
- [按标签检索](../tags/README.md)

> 本分片收录 **1** 个子分类，共 **48** 条条目。

## best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [AI拟人化互动服务极端情绪干预机制技术实施方案](../best-practices/ai-anthropomorphic-crisis-intervention-implementation.md) | 针对《人工智能拟人化互动服务管理暂行办法》第13条要求，设计极端情绪/自残自杀干预机制的完整技术实施方案，包含系统架构、识别引擎、分级干预、运营后台、测试验收和7天上线排期 | 2026-07-08 | AI合规、极端情绪干预、安全机制、拟人化互动、技术方案 |
| [异步生成接口'两段式'轮询模式](../best-practices/api-async-polling-pattern.md) | 通用异步生成接口的'两段式'调用模式：前台提交任务获取 task/episode ID，后台轮询直到完成。涵盖执行模型、提交/轮询示例脚本、轮询参数表与完成/失败/超时处理。 | 2026-08-07 | API、异步、轮询、后台任务、curl、jq、两段式 |
| [API 错误处理与重试策略](../best-practices/api-error-handling-retry-strategy.md) | 标准响应结构 {code,message,data} 契约、HTTP 状态码处理表、应用错误码表与分层重试策略（429 指数退避、5xx 重试、网络错误重试）。 | 2026-08-07 | API、错误处理、重试、HTTP状态码、指数退避、响应契约 |
| [API 集成模式组合实战示例：AI 播客自动生成](../best-practices/api-integration-worked-example.md) | 以一个'从长文章自动生成 AI 播客'的业务场景为骨架，演示如何组合复用四项通用 API 集成模式（交互式参数收集、@file 长文本、异步两段式轮询、错误处理与重试），给出端到端编排与可运行脚本。 | 2026-08-07 | API、示例、工作流、播客、AskUserQuestion、异步轮询、@file、重试、端到端 |
| [AskUserQuestion 分步交互式收集参数模式](../best-practices/api-interactive-parameter-collection.md) | 用 AskUserQuestion 分步交互式收集 API 参数的模式：一次一问、等回答、执行前确认、可回退；多选用 AskUserQuestion、自由文本用普通消息、依赖参数串行、独立参数可批量。 | 2026-08-07 | API、AskUserQuestion、交互、参数收集、多选、自由文本、会话 |
| [用 @file 传长文本请求体](../best-practices/api-long-text-file-parameter.md) | 当请求体文本过长（如整篇文章）时，用 curl 的 -d @file 从临时文件读取请求体，绕过 shell 命令行参数长度限制。含何时使用、临时文件写法与用后清理。 | 2026-08-07 | API、curl、长文本、@file、临时文件、shell参数限制 |
| [归档搭配Wiki联动机制指南](../best-practices/archive-wiki-linkage-guide.md) | SpecWeave项目中归档（retrospective）与Wiki（learning wiki）联动的标准化操作指南，明确定位区别、升级判定标准、双向关联机制、Wiki化SOP与模板结构，实现从过程记录到系统化知识的价值升华。 | 2026-07-31 | archive、wiki、knowledge-management、retrospective、learning-wiki、知识沉淀、归档升级、联动机制 |
| [Python AST静态分析实践：五类消歧法降低误报](../best-practices/ast-static-analysis-disambiguation.md) | 基于并发安全检查器（六维检查法）开发实战，总结Python AST静态分析中降低误报的五类消歧策略，帮助开发者编写准确的代码检查工具。核心原则：宁可漏报，不可误报。 | 2026-07-08 | AST、static-analysis、python、false-positive、code-quality、automation |
| [书籍转 Web 教程的原创重写与适当引用编写规范](../best-practices/book-to-web-tutorial-citation-guide.md) | 将受版权保护的书籍（PDF/EPUB）制作为公开 Web 教程时，走'原创重写 + 适当引用'合规路线的可执行编写规范：法律基础速查、文件级溯源模板、五条内容硬规则、六类引用格式示例、禁止写法对照与发布前自查清单。 | 2026-09-11 | 著作权、合理使用、适当引用、markdown、web教程、原创重写、引用规范、合规 |
| [Caffe-FFI Layer开发必查：param_propagate_down_初始化陷阱](../best-practices/caffe-ffi-param-propagate-down-initialization.md) |  | 2026-08-03 | caffe-ffi、layer、backward、bug-pattern、c++、initialization、segfault、access-violation |
| [恒等层 COW 零拷贝分离原则（输入梯度与参数梯度分离）](../best-practices/caffe-identity-layer-cow-separation.md) |  | 2026-08-04 | caffe-ffi、cow、zerocopy、scale、bias、eltwise、backward、grad、bug-pattern、c++、identity-layer |
| [Caffe层Backward验证标准工作流（L1-L2-L3三层法）](../best-practices/caffe-layer-backward-validation-workflow.md) |  | 2026-08-03 | caffe-ffi、backward、testing、workflow、three-layer-validation、gradient-check、c++、numpy、numerical-gradient |
| [Caffe AVE Pooling梯度路由：均匀分配模式](../best-practices/caffe-pooling-ave-gradient-routing.md) |  | 2026-08-03 | caffe-ffi、pooling、backward、gradient-routing、ave-pooling、c++、numpy、test-pattern |
| [Caffe MAX Pooling梯度路由：Winner-Takes-All模式](../best-practices/caffe-pooling-max-gradient-routing.md) |  | 2026-08-03 | caffe-ffi、pooling、backward、gradient-routing、max-pooling、c++、numpy、test-pattern |
| [IDE Agent 环境下 CLI 工具配置操作手册](../best-practices/cli-setup-in-agent-environment.md) | 针对团队新人的 IDE Agent（Trae/Claude Code 等）环境下 CLI 工具配置操作手册：基于 arkcli 安装配置实战，提炼通用方法论——安装验证→沙箱权限预判→非交互式认证→配置验证四步法，涵盖常见坑点、排错 Checklist 和决策矩阵。 | 2026-07-07 | cli、setup、agent-environment、sandbox、sso、non-interactive、arkcli、newbie-guide、npm |
| [CLI 工具选型二分法：任务编排（invoke）vs 用户接口（typer）](../best-practices/cli-task-vs-user-interface-invoke-typer.md) | invoke 与 typer 并非同类竞争工具——invoke 是任务执行器（对标 Make/Rake），typer 是 CLI 解析框架（对标 Click/argparse）。本文沉淀“任务编排 vs 用户接口”二分选型法：按使用对象拆分需求、按层级映射工具、Windows 平台冒烟测试三件套（编码/子进程/颜色输出），含 4 个反模式与跨领域迁移示例。 | 2026-08-21 | - |
| [CMake项目模块化重构最佳实践](../best-practices/cmake-modularization-best-practices.md) |  | 2026-07-29 | CMake、modularization、build-system、refactoring、cross-platform、best-practice |
| [编译型Python包数据文件生命周期管理](../best-practices/compiled-package-data-file-lifecycle.md) | 基于TVM .rly数据文件缺失修复实战复盘，提炼编译型Python包数据文件的完整生命周期管理方法：编译阶段显式复制、打包阶段完整性验证、运行阶段环境变量设置与文件校验。 | 2026-07-23 | Python、Nuitka、Cython、wheel、data-files、packaging、TVM、relay |
| [并发代码安全审查与Bug修复闭环指南](../best-practices/concurrent-code-safety-review.md) | 基于多智能体冲突解决机制实现与死锁修复实战复盘，提炼并发模块安全审查六维检查法、调度类模块N-scaling测试矩阵、Bug修复1+N+1闭环公式等5个可复用洞察，提供原子提交前的完整Checklist模板。 | 2026-07-08 | concurrency、deadlock-prevention、code-review、defensive-programming、bug-fix、checklist、tdd |
| [conda-forge 交叉编译配置完整指南](../best-practices/conda-forge-cross-compilation-guide.md) | conda-forge 交叉编译配置完整调研报告，覆盖从 linux-64 构建 osx-64/osx-arm64/win-64 平台包的完整方案：平台三元组、工具链包名清单、conda_build_config.yaml模板、meta.yaml依赖分离、build.sh交叉编译检测、CMAKE_ARGS变量传递、scikit-build-core适配、Wine运行时测试、常见陷阱与解决方案。 | 2026-07-30 | conda-forge、cross-compilation、conda-build、CMake、scikit-build-core、Docker、Wine、macOS、Windows、toolchain、RPATH |
| [配置文件放置治理与 .temp/ 临时文件约定](../best-practices/config-file-placement-convention.md) | SpecWeave 项目关键配置文件的标准存放路径、放置决策树、Python 自动加载约定（sitecustomize.py / .pth / PYTHONPATH 关系）、sitecustomize.py 曾被错放根目录的根因分析，以及 .temp/ 临时文件的用途分类、命名规则、保留期与清理机制。 | 2026-07-18 | - |
| [DAG图变换算法验证最佳实践](../best-practices/dag-graph-transform-verification.md) |  | 2026-08-01 | dag、graph-transform、visualization、verification、caffe、insert-splits、in-place |
| [DataLoader Pickle 序列化问题诊断 SOP](../best-practices/dataloader-pickle-diagnosis-sop.md) | DataLoader pickle 序列化问题诊断标准流程，整合诊断指南与检查清单精华。5 步流程 + 6 种不可序列化模式 + 3 种修复方案 + 跨启动模式验证矩阵，适用于 Python 3.14 forkserver 兼容性排查。 | 2026-07-23 | Python、pickle、serialization、multiprocessing、DataLoader、diagnosis、SOP、checklist |
| [目录迁移五步法检查清单](../best-practices/directory-migration-checklist.md) |  | 2026-07-18 | - |
| [Docker镜像更新的声明式优先原则](../best-practices/docker-declarative-first-principle.md) | 基于xmnn-client Docker commit入口配置泄漏修复实战复盘，提炼Docker镜像更新的声明式优先原则：优先使用Dockerfile声明式构建，docker commit仅用于快速原型验证，避免运行时状态隐式继承导致的配置泄漏。 | 2026-07-23 | Docker、Dockerfile、docker-commit、declarative、image-build、containerization |
| [并发安全八维检查法技术规格](../best-practices/eight-dimensions-concurrent-safety-spec.md) |  | 2026-07-08 | concurrent-safety、AST、static-analysis、eight-dimensions、check-rules、pre-commit |
| [文件 I/O 并发安全规范：原子写入、日志模板与重试策略](../best-practices/file-io-concurrency-safety.md) | 基于原子写入重构实战（11个模块统一改造、46个测试覆盖、并发成功率82%→100%），提炼文件I/O并发安全三原则：写共享文件必须原子化、日志必须分阶段计时、重试必须有限次+退避。提供决策树、日志模板、重试参数规范和完整代码示例，作为所有涉及文件写入的脚本必须遵守的开发规范。 | 2026-07-12 | concurrency、file-io、atomic-write、logging、retry-pattern、windows、defensive-programming |
| [硬编码路径批量修复工具使用指南（fix-hardcoded-paths.py）](../best-practices/fix-hardcoded-paths-guide.md) | 可复用硬编码路径批量修复工具使用指南：正则保留分隔符风格与盘符大小写，支持 .py/.ipynb 双处理与 dry-run/apply 双模式。 | 2026-08-07 | hardcoded-paths、refactor、python、path-migration、dry-run、ipynb、script |
| [浮点数精度测试技术指南](../best-practices/float-precision-testing-guide.md) |  | 2026-08-02 | float32、precision、testing、ulp、numerical-gradient、c1-kink、sigmoid、elu、activation-functions |
| [Git 提交中文乱码排查：显示层 vs 存储层分离验证法](../best-practices/git-commit-mojibake-diagnosis.md) | Windows 环境下 git 提交中文信息在终端显示乱码，但存储字节可能完全正确——显示层乱码 ≠ 存储层乱码。本文沉淀「双层分离验证法」：用 git cat-file 原始字节 + Python 字节级比对判定存储是否正确，避免因误判而做无谓的 reset 重提。含根因分析、4 反模式与可靠重提方案。 | 2026-08-21 | - |
| [链式pre-commit钩子架构实践指南](../best-practices/git-hook-chain-architecture.md) | 基于敏感信息检测和并发安全检查两个pre-commit钩子的实战经验，总结链式pre-commit钩子架构模式——单Shell入口+Python链式主入口+独立检查模块，解决跨平台维护、检查顺序控制和扩展成本问题。 | 2026-07-08 | git-hooks、pre-commit、architecture、cross-platform、automation |
| [Git推送被拒绝（fetch first）问题解决指南](../best-practices/git-push-rejected-resolution.md) | 基于SpecWeave项目实际遇到的git push被拒绝问题（远端有本地没有的提交+本地有目录大重构），总结系统化的解决流程——诊断→安全备份→选择合并策略→执行→验证，特别涵盖目录重构场景下rebase失败的处理方案。 | 2026-08-14 | git、push、conflict、merge、rebase、directory-restructure、troubleshooting |
| [手算梯度已知值验证：Backward测试L1层方法论](../best-practices/hand-computed-gradient-verification.md) |  | 2026-08-03 | testing、backward、gradient、verification、known-values、hand-computed、numpy、test-pattern、caffe-ffi |
| [Mermaid 图表操作指南](../best-practices/mermaid-guide.md) | SpecWeave 项目中 Mermaid 图表的一站式操作手册，涵盖起步模板、安全编码六规则、自动化检查工具详解、渲染问题排查流程和不同图表类型注意事项。 | 2026-06-29 | mermaid、图表、可视化、check-mermaid、安全编码、六规则、模板、ci |
| [模型编译 config 输入布局核验与修正规范（NCHW/NHWC）](../best-practices/model-config-input-layout-convention.md) | 从 palmDet 模型编译失败修复沉淀的规范：工具链强制按 NCHW 解包输入 shape，config 输入布局必须与模型（Caffe/ONNX）实际布局一致；提供布局判定、修正方案、新模型接入核验检查清单与配套算子转换修复。 | 2026-08-12 | model-compile、config、input-layout、NCHW、NHWC、NV12、onnx2pytorch、tvm、adaround、checklist、caffe、onnx |
| [模型调用环境变量脱敏模板（.env 字段清单）](../best-practices/model-env-template.md) | 从 chaos/flexloop/models/.env 沉淀的脱敏环境变量模板：列出字段名与用途说明，所有值一律使用占位符，绝不含真实密钥或个人路径。 | 2026-08-07 | env、environment-variable、desensitization、glm、huggingface、zai |
| [多文件编辑操作可靠性指南](../best-practices/multi-file-edit-reliability.md) | 基于IDL Wiki章节拆分实战复盘的多文件编辑操作可靠性指南：涵盖章节拆分级联编号成本、Edit工具精确匹配陷阱、串行vs并行Edit策略、Windows管道稳定性四条核心经验，提供决策矩阵和操作Checklist。 | 2026-07-05 | edit、multi-file、reliability、serial-vs-parallel、windows-pipe、cascading-renumber、wiki-split、tool-pitfalls |
| [数值梯度诊断日志规范：从失败到根因的可观测性](../best-practices/numerical-gradient-diagnostic-logging.md) |  | 2026-08-03 | debugging、numerical-gradient、logging、diagnostics、observability、grad-check、caffe-ffi、pytest |
| [Parser 复杂度预算 Checklist](../best-practices/parser-complexity-budget.md) | 基于MDI项目parser.py（1465行）重构复盘的经验总结：处理半结构化数据（Markdown/自然语言/配置文件）的Parser应预留2-3倍于Generator的时间/代码量预算，遵循三层架构拆分，并先写20+边界case测试。 | 2026-07-03 | parser、复杂度预算、semi-structured-parsing、三层架构、边界case、TDD、checklist |
| [方法论模式第3次验证报告：模板批量升级场景](../best-practices/pattern-validation-v3-template-batch-upgrade.md) | 分类处置决策树(Classification-Disposition Decision Tree)与三阶段渐进推广验证(Phased Rollout Validation)两个L2治理模式的第3次验证报告。验证场景为复盘模板v1.2批量标准化升级（61个项目），验证了模式在轻量级模板升级场景下的有效性，记录了P1批量执行后集中格式校验的新增实践。 | 2026-07-06 | pattern-validation、L2-pattern、phased-rollout、classification-disposition、batch-upgrade、governance、methodology-evolution |
| [从实战到工具：三段式PDF导出、Mermaid全量扫描与三个工程洞察](../best-practices/pdf-export-mermaid-automation-insights.md) | 从一次Mermaid漏斗图重绘与PDF导出任务中萃取的工程经验：三段式中文Markdown+Mermaid PDF导出法、Mermaid全量扫描自动化、以及三个核心工程洞察（工具选择熟悉度偏差、无头浏览器DOM检测原则、自动化检查的免费质量提升）。 | 2026-07-11 | pdf导出、mermaid、playwright、pandoc、自动化、工程洞察、工具封装、质量保证 |
| [Python大版本升级破坏性变更检查清单](../best-practices/python-version-upgrade-compatibility-check.md) | 基于xmnn-client Python 3.14迁移实战复盘，提炼Python大版本升级的破坏性变更检查清单，重点关注multiprocessing默认行为变更、弃用/移除模块、AST节点变更等隐蔽陷阱。 | 2026-07-23 | Python、version-upgrade、compatibility、multiprocessing、breaking-changes、checklist |
| [C/C++共享库符号可见性控制最佳实践](../best-practices/symbol-visibility-control.md) | 基于TVM符号可见性控制修复实战复盘，提炼共享库符号可见性精确控制方法、--exclude-libs,ALL最佳实践、静态注册机制保护策略等核心洞察，提供完整的符号冲突诊断与修复指南。 | 2026-07-18 | C/C++、linker、symbol-visibility、shared-library、LLVM、TVM、CMake、anti-pattern |
| [测试基础设施性能优化最佳实践](../best-practices/test-infra-performance-optimization.md) |  | 2026-08-03 | performance、gc、profiling、pytest、conftest、csv-buffering、observability、test-infrastructure、caffe-ffi |
| [TRAE Agent 沙箱配置与使用最佳实践指南](../best-practices/trae-agent-sandbox-guide.md) |  | 2026-07-20 | sandbox、security、agent-environment、configuration、trae、best-practices、newbie-guide |
| [VsDevShell 模块 API 参考文档](../best-practices/vsdevshell-api-reference.md) | VsDevShell.psm1 通用模块完整API参考，包含多策略VS安装发现、DevShell环境加载、PATH自动恢复等功能 | 2026-08-02 | powershell、visual-studio、msvc、build-tools、api-reference、module |
| [Windows环境零摩擦开发指南](../best-practices/windows-zero-friction-development-guide.md) |  | 2026-08-01 | windows、compatibility、powershell、encoding、cross-platform、checklist |
| [Wrapper脚本注入模式](../best-practices/wrapper-script-injection-pattern.md) | 基于xmnn Nuitka编译包Python 3.14兼容性修复实战复盘，提炼wrapper脚本注入模式：通过纯Python包装脚本在导入编译产物前注入运行时配置，实现不侵入源码的兼容性修复。 | 2026-07-23 | Python、wrapper、runpy、compiled-package、runtime-patch、compatibility |

---

*索引自动生成于 2026-09-11 16:52:20*
