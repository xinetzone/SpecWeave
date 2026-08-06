---
id: "code-patterns-readme"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/README.toml"
---
# 代码模式索引（code-patterns）

本目录存放代码级可复用模式，聚焦于具体代码编写、文件操作、编辑策略等微观层面的最佳实践。

## 模式清单

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [safe-table-edit.md](safe-table-edit.md) | Markdown 表格安全修改策略，整表替换优先、局部替换仅限文本修改 | L1 实验性 | Markdown 表格结构修改 |
| [mermaid-safe-coding-rules.md](mermaid-safe-coding-rules.md) | Mermaid 安全编码五规则，覆盖空行/引号/列表触发/Subgraph/边标签，配套自动化检查脚本 | L4 标准化 | Mermaid 图表编写（防渲染失败） |
| [mermaid-trap-cheatsheet.md](mermaid-trap-cheatsheet.md) | Mermaid 8 类常见陷阱速查表，快速排查渲染问题 | L4 标准化 | Mermaid 渲染故障快速排查 |
| [ngram-mixed-language-matching.md](ngram-mixed-language-matching.md) | 中英文混合文本n-gram滑动窗口子串匹配法，不依赖分词零额外依赖，支持正/负关键词双向计分；含完整Python实现、ngram_size选择指南 | L2 已验证 | 规则引擎关键词匹配、文本分类、中英文混合搜索 |
| [relative-depth-adjustment.md](relative-depth-adjustment.md) | 相对路径深度自动校正算法，±3级调整`../`层数配合存在性校验，零误报率 | L2 已验证 | 目录重构/原子化后的批量链接修复 |
| [fix-priority-chain.md](fix-priority-chain.md) | 自动修复优先级链设计，精确修复优先、模糊修复兜底，无法修复明确报告人工 | L2 已验证 | 多策略自动修复工具 |
| [periodic-check-caching.md](periodic-check-caching.md) | 定期检查类工具缓存机制，可配置TTL/--no-cache/--clear-cache，HTTP请求从10-20秒降至<1秒 | L1 实验性 | CLI检查工具、外部资源访问工具、CI脚本 |
| [parallel-subprocess-observability.md](parallel-subprocess-observability.md) | 并行子进程全链路可观测模式：命令参数精简+ThreadPoolExecutor并行+三阶段日志+加速比自证，子模块检查耗时↓68% | L2 已验证 | 多目标批量检查CLI、子模块管理工具、多服务健康检查、批量文件处理 |
| [dual-channel-tiered-logging.md](dual-channel-tiered-logging.md) | 分级日志双轨输出模式：控制台INFO+文件DEBUG，含语义化日志函数、静态资源过滤、Handler级别控制 | L2 已验证 | CLI工具、自动化脚本、浏览器自动化 |
| [bash-unified-structured-logging.md](bash-unified-structured-logging.md) | Bash脚本统一结构化日志库：独立lib/logging.sh通过source加载，支持text/json双格式+log/metric/event/summary四类API+级别过滤+上下文字段，适配监控平台采集 | L2 已验证 | Bash/Shell部署脚本、CI/CD流水线脚本、WSL/Linux运维脚本、需要JSON Lines输出的自动化工具 |
| [tuyaopen-tos-cli-command-registry.md](tuyaopen-tos-cli-command-registry.md) | 单入口 + 子命令注册表模式（click + 字典注册），便于工具链多子命令扩展 | L1 实验性 | 工具链CLI、脚手架CLI、多子命令程序 |
| [check-and-restore.md](check-and-restore.md) | 检查函数状态恢复模式：检测前保存状态→优先就地检测→必要时导航后恢复URL，遵循CQS原则 | L2 已验证 | 浏览器自动化状态检查、API客户端、数据库操作 |
| [cpp-nullstream-logging.md](cpp-nullstream-logging.md) | C++ NullStream零开销日志：NullStream模板吸收所有<<输出+组件标签宏+编译期开关+运行时级别控制，禁用时编译通过且零开销 | L1 候选 | C++轻量日志系统（不引入spdlog/glog等第三方库）、深度学习框架、条件编译调试 |
| [cross-platform-backtrace-leak-diagnosis.md](cross-platform-backtrace-leak-diagnosis.md) | 跨平台堆栈回溯泄漏源定位：构造时捕获调用栈+析构TRACE输出+Windows DbgHelp/Linux execinfo双平台+编译期开关零开销，形成检测→定位完整诊断闭环 | L2 已验证 | C++原生扩展FFI项目内存泄漏诊断、跨平台C++开发、需要精确定位泄漏源的调试场景 |
| [cpp-object-wrapper-lazy-init-check.md](cpp-object-wrapper-lazy-init-check.md) | C++对象包装延迟初始化防御：公共方法入口第一行检查!defined()/!valid()，首次初始化作为独立分支处理，避免空指针解引用 | L1 候选 | 包装第三方值类型对象(TVM Tensor/optional/FFI句柄)、默认构造+延迟初始化模式 |
| [cpp-iife-assertion-macro.md](cpp-iife-assertion-macro.md) | C++ IIFE+AssertHelper流式断言宏：IIFE表达式+临时对象析构抛异常+operator<<链式消息，替代do-while模式实现gtest风格CHECK宏，含5个GOTCHA陷阱（移动构造/noexcept(false)/引用捕获/括号保护/宏重定义） | L2 已验证 | C++自定义断言/CHECK宏、测试框架断言、生产环境检查宏、需要<<流式消息的宏封装 |
| [cross-platform-encoding-enforcement.md](cross-platform-encoding-enforcement.md) | 跨平台输出编码三层防御体系：入口编码设置+防御性能力检测+Unicode/ASCII适配输出，避免Windows GBK终端崩溃 | L2 已验证 | Python CLI工具、跨平台脚本、subprocess调用 |
| [defensive-attribute-access.md](defensive-attribute-access.md) | 外部对象防御性属性访问：getattr→callable→try-except三层防护，应对属性不存在/None/不可调用/抛异常场景 | L2 已验证 | CLI工具库、stream操作、插件接口、mock环境下的防御性编程 |
| [direct-file-write-over-shell-pipe.md](direct-file-write-over-shell-pipe.md) | 文档生成直写文件优先：避免 Windows PowerShell 文本管道在落盘阶段污染中文内容 | L1 实验性 | README/报告生成、Markdown导出、知识库条目写回 |
| [temporary-syspath-modification.md](temporary-syspath-modification.md) | 临时sys.path修改条件导入：try前insert→finally恢复，不污染全局导入路径，Optional返回优雅降级 | L2 已验证 | 可选依赖导入、vendor子模块引用、插件系统 |
| [path-anchor-semantization.md](path-anchor-semantization.md) | 路径锚点语义化：每级parent赋予语义变量名，避免链式.parent.parent计算差一级的常见bug | L1 实验性 | 项目内路径计算、脚本路径定位、包根目录查找 |
| [async-setup-future-deduplication.md](async-setup-future-deduplication.md) | 装配并发去重：以组件key维护Future并复用，确保并发装配一致结果/一致失败 | L1 实验性 | 插件/组件装配、依赖闭包、并发初始化 |
| [bulk-replace-zero-omission-verify.md](bulk-replace-zero-omission-verify.md) | 批量替换零遗漏验证：replace_all后全局Grep旧字符串确认零匹配，低成本高收益质量门禁（ROI>60x） | L2 已验证 | 全局重命名/重构、跨文件格式统一、配置项变更后 |
| [dockerfile-python-code-safe-embedding.md](dockerfile-python-code-safe-embedding.md) | Dockerfile中Python代码安全嵌入：RUN中禁止多行缩进Python代码块，提供单行格式/临时脚本/COPY+RUN三种方案 | L2 已验证 | Dockerfile内嵌Python验证代码、Docker模板编写、构建时ldd/import/功能测试 |
| [skill-three-part-structure.md](skill-three-part-structure.md) | 技能三分结构：SKILL最小入口 + references按需长文档 + scripts可执行动作 | L1 实验性 | AI Skills 设计、工作流知识包、可执行SOP沉淀 |
| [script-json-output-contract.md](script-json-output-contract.md) | 脚本可编排输出契约：统一 --json 输出字段与退出码，避免输出不可解析 | L1 实验性 | CLI脚本、Agent编排、CI工具 |
| [session-file-externalization.md](session-file-externalization.md) | 会话外部化：用 session file 解耦多命令状态，支持跨进程协同 | L1 实验性 | start/tail/stop 工具、后台守护脚本 |
| [path-traversal-guard.md](path-traversal-guard.md) | 路径越界防护：realpath/resolve + 前缀校验，阻断任意路径访问 | L1 实验性 | 接受路径参数的脚本、批量检查/修复工具 |
| [pre-kill-identity-verification.md](pre-kill-identity-verification.md) | 停止前身份校验：kill 前先校验 cmdline 属于目标进程，避免误杀 | L2 已验证 | stop/kill 类脚本、后台监控工具 |
| [example-driven-test-generation.md](example-driven-test-generation.md) | 示例驱动测试生成：从文档代码块提取真实测试数据，配合检查清单→断言转换，解决文档漂移 | L1 实验性 | API文档→测试代码生成、接口测试自动化 |
| [framework-parameter-semantics-verification.md](framework-parameter-semantics-verification.md) | 框架参数语义验证：DL算子测试前必查源码确认参数行为（广播/默认值/维度语义），防止凭直觉写错误参考实现 | L2 已验证 | DL框架(Caffe/PyTorch/TF)算子正确性测试、API行为验证 |
| [structured-doc-diff-semver.md](structured-doc-diff-semver.md) | 结构化文档Diff与SemVer建议：字段级对比→严重性分级→影响分析→版本建议 | L1 实验性 | IDL/配置Schema版本管理、API变更审查 |
| [directive-state-machine-parsing.md](directive-state-machine-parsing.md) | Directive参数状态机解析：首行匹配→选项行状态机→正文识别三阶段解析MyST扩展语法，避免巨型正则 | L1 实验性 | Markdown自定义扩展语法解析、多类型directive统一解析框架 |
| [checklist-to-assertion-conversion.md](checklist-to-assertion-conversion.md) | 检查清单→断言转换：关键词分类（前置/断言/后置/注释）+专项正则提取，将人类验收标准转为测试步骤 | L1 实验性 | 文档驱动测试生成、Docs-as-Tests工具链 |
| [profile-auto-detection.md](profile-auto-detection.md) | Profile自动检测：五级优先级信号源分层匹配（显式声明→强特征→路径特征→内容特征→默认值），零配置类型识别 | L1 实验性 | 多格式/多Schema解析器、约定优于配置的CLI工具 |
| [data-model-extraction-signal.md](data-model-extraction-signal.md) | 数据模型提取信号：models.py出现标志代码从"脚本集合"跨越到"类型安全应用"，frozen dataclass三重价值 | L1 实验性 | 脚本模块化、API边界定义、配置管理、测试数据构造 |
| [docker-container-session-raii.md](docker-container-session-raii.md) | Docker 容器会话 RAII 模式：上下文管理器封装容器生命周期，确保异常也不泄漏资源 | L1 实验性 | 容器化构建流水线、CI/CD任务、多步容器操作 |
| [content-hash-build-cache.md](content-hash-build-cache.md) | 内容哈希构建缓存：基于 git HEAD 哈希的智能构建跳过，比时间戳更可靠 | L1 实验性 | 编译构建缓存、数据处理管道、模型训练预处理 |
| [cli-as-api-design.md](cli-as-api-design.md) | CLI即API设计：多格式输出（table/json/yaml/wide）+结构化错误+退出码约定+会话持久化，同时服务人类和机器 | L1 实验性 | CLI工具设计、AI原生工具、DevOps工具、脚本自动化 |
| [cli-json-pipeline.md](cli-json-pipeline.md) | CLI-JSON管道模式：全局--json标志+stdout/stderr分离+camelCase序列化+Rich表格双消费者支持 | L1 实验性 | 脚本/CI流水线/AI Agent编程式调用的CLI工具 |
| [ci-integration-three-interface.md](ci-integration-three-interface.md) | CI集成三接口模式：run/run_check/run_ci_check三接口共享核心检查逻辑，适配命令行/pre-commit/CI三场景 | L2 已验证 | 新增检查项需集成到命令行+pre-commit+CI的场景 |
| [module-level-snapshot-side-effect-defense.md](module-level-snapshot-side-effect-defense.md) | 模块级快照防御自身副作用污染：在副作用import前捕获_INITIAL_*快照，检测逻辑基于快照判定避免自污染 | L1 实验性 | 检测脚本本身会修改被检测状态的场景（如编码检测、sitecustomize验证） |
| [ci-oidc-keyless-auth.md](ci-oidc-keyless-auth.md) | CI-OIDC无密钥认证模式：GitHub OIDC短期JWT+audience绑定+后端claims验证+API Key备选 | L1 实验性 | GitHub Actions与第三方服务集成 |
| [credential-multi-source-priority.md](credential-multi-source-priority.md) | 凭证多源优先级模式：TOKEN>API_KEY>OAuth三级优先级+自动刷新+0o600权限存储 | L1 实验性 | 多认证方式CLI工具设计 |
| [env-var-five-layer-protection.md](env-var-five-layer-protection.md) | 环境变量安全五重保护：Masked掩码+单值Reveal+Read-Merge-Write+--yes确认+--dry-run预览 | L1 实验性 | CLI工具敏感配置管理 |
| [dependency-update-risk-control.md](dependency-update-risk-control.md) | 依赖更新风控模式：14天冷却+周中开窗+风险分级自动合并+并发限制 | L1 实验性 | Renovate/Dependabot依赖更新项目 |
| [cli-skill-pair-sync.md](cli-skill-pair-sync.md) | CLI-Skill配对同步模式：Skill权威源+配对PR同步+--agent原始输出+动态数据实时获取 | L1 实验性 | 支持人类和AI Agent的CLI工具 |
| [selective-testing-strategy.md](selective-testing-strategy.md) | 选择性测试模式：PR事件受影响测试+主分支全量+依赖变更强制全量+退出码5成功处理 | L1 实验性 | 中大型Python项目CI测试优化 |
| [playbook-onboarding-guide.md](playbook-onboarding-guide.md) | Playbook引导Onboarding模式：init命令输出结构化playbook+环境检测+7步引导流程 | L1 实验性 | 功能丰富、工作流复杂的CLI工具首次使用引导 |
| [python-script-three-layer-arch.md](python-script-three-layer-arch.md) | Python脚本三层架构：主脚本+数据模块+模板分离，解决500行限制，数据视图解耦 | L2 已验证 | Python生成/转换脚本超过500行时的模块化拆分 |
| [css-grid-visualization-zero-dimension.md](css-grid-visualization-zero-dimension.md) | CSS Grid/Flex可视化容器零尺寸陷阱：min-height/min-width:0修复白屏无报错问题 | L2 已验证 | vis-network/ECharts/D3/Three.js等JS可视化库集成 |
| [overflow-protruding-element-isolation.md](overflow-protruding-element-isolation.md) | 溢出元素结构隔离：wrapper+定位模式解决overflow:hidden裁剪凸出元素矛盾，z-index无法穿透裁剪边界 | L2 已验证 | 侧边栏拉手/tooltip/下拉菜单/徽章等需凸出容器的元素 |
| [regex-markdown-parsing.md](regex-markdown-parsing.md) | 正则驱动的Markdown解析：通用章节/任务列表解析器，替换正则模式适配不同格式 | L1 实验性 | 结构化Markdown文档解析工具开发 |
| [defensive-config-cache-deepcopy.md](defensive-config-cache-deepcopy.md) | 防御性配置缓存：所有返回路径统一深拷贝，防止调用方修改污染全局缓存 | L2 已验证 | 全局配置缓存、可变对象缓存返回 |
| [ring-buffer-streaming-output.md](ring-buffer-streaming-output.md) | 环形缓冲流式输出：Popen上下文管理器+64KB尾部缓冲，避免OOM且保留错误上下文 | L2 已验证 | 编译器/构建工具调用、长时运行子进程 |
| [dynamic-path-derivation.md](dynamic-path-derivation.md) | 动态路径推导：基于__file__的可移植默认路径，禁止硬编码开发者绝对路径 | L2 已验证 | 项目内资源定位、工具链路径配置 |
| [exception-precision-guards.md](exception-precision-guards.md) | 异常精确性守卫：只捕获可恢复异常，TypeError/AttributeError等编程错误自然抛出 | L2 已验证 | 配置加载、IO操作、库函数异常处理 |
| [idempotent-shell-config.md](idempotent-shell-config.md) | Shell幂等配置修改：先删后增+set -euo pipefail+原子替换，重复执行结果一致 | L2 已验证 | 系统配置修改、安装脚本、Dockerfile配置 |
| [command-injection-prevention.md](command-injection-prevention.md) | 命令构造防注入：列表形式优先，必须shell时shlex.quote每个嵌入变量 | L2 已验证 | subprocess调用外部命令、docker/ssh/git等 |
| [shell-nested-quote-file-based-strategy.md](shell-nested-quote-file-based-strategy.md) | 多层命令嵌套的文件化规避策略：写入脚本文件→挂载到容器→执行→文件系统读取输出，避免>3层引号转义和sandbox输出过滤 | L1 实验性 | CI/CD/sandbox环境多层命令嵌套、跨PowerShell/bash/docker执行 |
| [lightweight-multi-dimensional-recommender.md](lightweight-multi-dimensional-recommender.md) | 无依赖轻量级多维度推荐算法：4维加权评分+字符bigram Jaccard+类型相容性矩阵，<500节点规模Top1准确率100% | L2 已验证 | 知识图谱关联推荐、标签推荐、相关文档推荐、中小规模实体匹配 |
| [configurable-by-default-principle.md](configurable-by-default-principle.md) | 可配置性默认原则：业务规则/阈值/关键词通过构造函数注入，提供合理默认值但允许覆盖，避免硬编码 | L2 已验证 | 仲裁/调度/评分类核心机制、可复用库、多环境适配模块 |
| [git-bundle-offline-clone.md](git-bundle-offline-clone.md) | Git Bundle离线克隆五步法：预检→SHA256校验→分支预览→并行克隆→状态验证，配套PowerShell一键脚本 | L1 实验性 | 离线代码交付、网络受限环境、U盘/移动硬盘介质交付、代码审计 |
| [python-ast-compatibility.md](python-ast-compatibility.md) | Python AST版本兼容模式：版本检测+_const()/_index()兼容函数封装+ast.Constant统一替代，三步法支持Python 3.8-3.14跨版本 | L1 实验性 | 需要跨多个Python版本运行且涉及AST操作的代码生成/静态分析/DSL项目 |
| [static-registration-compile-config.md](static-registration-compile-config.md) | 静态注册依赖代码的编译配置五步法：识别注册宏→禁LTO→禁符号隐藏→确认源文件编译→运行时验证注册表，应对LTO/DCE丢弃注册代码陷阱 | L1 实验性 | TVM/LLVM/OpenCV等使用C++静态注册（全局对象构造函数）的框架编译 |
| [compiled-wheel-runtime-image-build.md](compiled-wheel-runtime-image-build.md) | 编译型Python Wheel运行时镜像构建模式：RPATH锁定构建环境→以构建镜像为基础镜像→分层安装依赖→ldconfig配置→.pth文件自初始化，应对RPATH不匹配导致的动态库缺失 | L1 实验性 | Nuitka/Cython编译的含C扩展的wheel创建Docker运行时镜像 |
| [python-implicit-dependency-detection.md](python-implicit-dependency-detection.md) | Python包隐式依赖检测四步法：静态扫描import→逐层import测试→检查安装状态→分层安装策略，应对Python import惰性链式触发的"洋葱式发现" | L1 实验性 | Python wheel运行时镜像构建、新环境依赖验证、pyproject.toml隐式依赖排查 |
| [docker-commit-config-reset.md](docker-commit-config-reset.md) | docker commit 入口配置显式重置：--change清空ENTRYPOINT/CMD，避免保活配置泄漏到提交镜像 | L1 实验性 | docker commit增量更新镜像、热修复镜像 |
| [shell-cleanup-non-blocking.md](shell-cleanup-non-blocking.md) | Shell脚本清理操作非阻塞模式：三种清理策略（非致命/延迟/root级），应对sticky bit+set -e组合导致的脚本中断 | L1 实验性 | Shell脚本文件清理、Docker导出脚本、set -e脚本 |
| [codegen-triple-safety.md](codegen-triple-safety.md) | 代码生成三保险模式：工具版本锁+多路径一次生成+运行时闭环验证，应对编译器版本漂移、多副本不一致、编译成功但运行时失败三类陷阱 | L1 实验性 | Protobuf/gRPC/FlatBuffers/Thrift等IDL代码生成、GraphQL codegen、ORM自动生成、数据库迁移脚本 |
| [api-reference-verification.md](api-reference-verification.md) | API参考验证三步法：查参考实现→查API签名→查调用示例，消除基于经验假设引入的冗余transpose/reshape操作 | L2 已验证 | DL框架算子使用、数据处理库axis参数、通道顺序处理、数学库矩阵布局 |
| [try-prepare-merge.md](try-prepare-merge.md) | TryPrepare判定准备合并模式：_try_prepare_X()函数一次完成校验+参数计算，返回参数元组或None元组，消除判定函数与准备函数的重复计算 | L2 已验证 | 格式转换、条件编译、可选优化、类型转换、快路径尝试+回退逻辑 |
| [tvm-ffi-python-wrapper-dual-mode.md](tvm-ffi-python-wrapper-dual-mode.md) | TVM-FFI Python Wrapper双模式包装五要素：继承Object+_type_key+__slots__+__new__初始化+_is_native双模式分发，解决C++返回对象绕过__init__导致的属性缺失 | L1 候选 | TVM-FFI/Pybind11 C++对象Python绑定、FFI包装类、双模式（原生+纯Python后备）对象 |
| [conda-custom-channels-mirror.md](conda-custom-channels-mirror.md) | Conda镜像源精确映射：custom_channels逐channel显式声明替代channel_alias全局替换，避免镜像服务路径结构调整导致的静默404 | L2 已验证 | Docker构建conda环境、CI/CD流水线、开发机condarc配置、企业内网镜像 |
| [conda-build-scikit-build-core-native.md](conda-build-scikit-build-core-native.md) | conda-build + scikit-build-core原生扩展打包六步法：依赖分层→editable清理→参数隔离→$ORIGIN RPATH→符号双重验证→路径门禁，解决build/host/run划分错误、CMAKE_ARGS污染、Placeholder too short、wheel符号缺失等五层陷阱 | L3 方法论 | 含C/C++原生扩展（pybind11/nanobind）的conda包、有跨包依赖的原生库conda打包、嵌套子项目构建 |
| [conda-package-clean-verification.md](conda-package-clean-verification.md) | Conda包干净环境五维验证法：预清理editable四件套→全新环境→路径验证→ldd+nm双重依赖检查→环境配置→全量单元测试，确保"开发机能跑、用户机也能跑"，避免四类假成功陷阱 | L3 方法论 | Conda包交付前验证、CI打包验证流水线、有原生扩展的Python包发布前检查、防止editable残留污染验证 |
| [python-314-multiprocessing-fork-compat.md](python-314-multiprocessing-fork-compat.md) | Python 3.14 Multiprocessing Fork兼容模式：wrapper脚本注入+set_start_method强制fork，应对forkserver默认变更导致lambda不可pickle | L1 实验性 | Python 3.14+项目迁移、DataLoader worker启动失败、编译型包兼容性修复 |
| [pickle-serialization-source-fix.md](pickle-serialization-source-fix.md) | Pickle序列化源码层修复模式：模块级命名类替换lambda，从源头消除不可pickle对象（治本），与运行时兼容层互补 | L2 已验证 | 可改源码的lambda/闭包pickle修复、DataLoader transform序列化、Python 3.14 forkserver兼容 |
| [python-package-version-standard-api.md](python-package-version-standard-api.md) | Python包版本验证标准API：使用importlib.metadata.version()替代__version__属性访问，应对PEP 517/518/621新构建后端不再注入__version__的兼容性问题 | L2 已验证 | Dockerfile包验证、CI安装验证、跨Python版本项目、安装脚本/healthcheck |
| [shared-lib-symbol-dual-layer-control.md](shared-lib-symbol-dual-layer-control.md) | 共享库符号双层控制模式：编译期-fvisibility-inlines-hidden隐藏内联/模板弱符号+链接期--exclude-libs,ALL隐藏静态库符号，解决C++模板密集型第三方库（LLVM/Boost/Eigen）的WEAK符号泄漏 | L1 实验性 | C/C++共享库构建、第三方库符号隔离、静态链接隐藏、ELF符号可见性控制 |
| [env-var-alias-backward-compat.md](env-var-alias-backward-compat.md) | 环境变量别名向后兼容：检查新变量是否仍为Dockerfile ENV默认值（而非检查是否为空），解决旧变量名在重命名后静默失效的问题 | L2 已验证 | Docker镜像ENTRYPOINT脚本、配置文件迁移、CLI选项重命名 |
| [docker-ssh-noninteractive-path-fix.md](docker-ssh-noninteractive-path-fix.md) | Docker+SSH非交互会话PATH修复：三层配置（ENV+environment+profile.d），解决SSH非交互会话不继承Dockerfile ENV的通用陷阱 | L2 已验证 | 含SSH服务的Docker镜像、virtualenv/conda自定义PATH、远程命令执行 |
| [docker-image-offline-export-distribution.md](docker-image-offline-export-distribution.md) | Docker镜像离线构建-验证-导出-分发六步标准流程：环境预检→构建→G1功能验证→导出+校验→G3删除-加载-再验证→交付，三重质量门确保离线分发包可用 | L2 已验证 | Docker镜像离线分发、内网隔离环境部署、CI镜像归档、新机器交付 |
| [wsl-docker-command-safety.md](wsl-docker-command-safety.md) | WSL环境下Docker操作安全命令模式：简单命令直传避免bash -c嵌套、路径统一/mnt/格式、复杂操作脚本化，解决PowerShell→wsl→bash三层变量展开陷阱 | L2 已验证 | Windows+WSL2 Docker操作、wsl.exe跨层调用Docker、PowerShell执行Docker命令 |
| [powershell-wsl-cross-shell-wrapper.md](powershell-wsl-cross-shell-wrapper.md) | PowerShell→WSL跨Shell包装器模式：自动检测wsl.exe+发行版自动选择+Windows↔WSL路径转换+Docker预检+参数透传+退出码传递，消除"先进入WSL终端"的认知负担 | L2 已验证 | WSL2部署脚本Windows入口、CI/CD Windows runner调用Linux工具链、跨环境自动化脚本 |
| [ps5-compat-preflight.md](ps5-compat-preflight.md) | PS5.1兼容性三级预检Checklist：P0阻断项8项（PS7语法/WMI/workflow/Add-PSSnapin/pwsh.exe/iex/class/Add-Type）+P1高危项9项（编码/TLS/自动变量/COM/.NET/irm|iex/ExecutionPolicy/BOM/全局状态恢复）+P2建议项10项，含一键预检脚本，适用于AI生成PS脚本/CI门禁/代码审查 | L1 | `powershell` `powershell-5.1` `preflight` `compatibility` `ci-gate` `clm` `checklist` |
| [ps5-security-audit.md](ps5-security-audit.md) | PS5.1安全代码审查6维度Checklist：CLM兼容性6项+命令注入防护6项+凭证处理5项+执行策略4项+编码安全4项+防御性编程6项，含P0/P1/P2分级和评分模板，适用于AI生成脚本审计/上线前安全审查 | L1 | `powershell` `security-audit` `code-review` `clm` `command-injection` `credential` `defensive-programming` |
| [ps5-safe-defaults.md](ps5-safe-defaults.md) | PS5.1生产级安全默认值头：完整版8段安全头（错误处理/状态保存/UTF-8编码/TLS-bor追加非覆盖/组策略检测/CLM检测/自动变量防护/finally恢复）+精简版短脚本头+并行处理Runspace模板（CLM/EDR兼容），含V阶段18个加固点 | L1 | `powershell` `safe-defaults` `security-header` `tls` `encoding` `try-finally` `runspace` `clm` |
| [ps7-to-ps5-translation.md](ps7-to-ps5-translation.md) | PS7→PS5语法降级转换四映射表：运算符映射11项（?:/??/??=/&&/||/?./-Parallel/class）+API映射13项（WMI→CIM/workflow/pwsh.exe/SkipCertificateCheck等）+行为差异映射8项（编码/TLS/CIM协议等）+并行降级5方案对照表+自动转换辅助脚本 | L1 | `powershell` `version-migration` `syntax-translation` `compatibility` `downgrade` `code-conversion` |
| [wsl2-docker-selection-decision.md](wsl2-docker-selection-decision.md) | WSL2 Docker方案决策模式：11项实测性能基准+7种场景决策矩阵+文件系统性能提示+常见陷阱（credential helper/9p协议/systemd），解决Docker Desktop vs 原生Docker选型困惑 | L2 已验证 | WSL2部署指南Docker环境章节、Windows开发环境搭建、DevOps环境选型、CI/CD runner配置 |
| [docker-buildtime-vs-runtime-config.md](docker-buildtime-vs-runtime-config.md) | Dockerfile构建时与运行时配置分离原则：RUN层处理静态安装/编译/复制，ENTRYPOINT处理动态密钥/配置/权限，验证服务必须经过ENTRYPOINT完整启动链 | L2 已验证 | 多阶段Dockerfile设计、容器化服务镜像、SSH/TLS密钥安全、ENTRYPOINT脚本编写 |
| [flat-nested-hybrid-scan.md](flat-nested-hybrid-scan.md) | 扁平+嵌套混合目录扫描：嵌套优先→扁平回退，避免"两层结构假设"导致静默失败（输出0/0但不报错） | L2 已验证 | 目录扫描器/索引生成器、Spec看板、文档导航表、结构迁移过渡期 |
| [zero-copy-batch-inference-defense.md](zero-copy-batch-inference-defense.md) | 深度学习零拷贝分批推理防御：pad→forward→copy=True→slice四步法+单样本一致性校验，解决DLPack/zero-copy view在下一批forward后被静默覆盖的陷阱 | L2 已验证 | DL推理API无自动批处理、C++推理引擎Python绑定、Caffe/ONNX Runtime/TensorRT分批推理 |
| [pretrained-model-download-validation.md](pretrained-model-download-validation.md) | 预训练模型多源下载与多级验证：≥3源URL fallback+大小预估+magic bytes检测+加载验证+准确率校验，应对GitHub LFS pointer/截断文件/HTML错误页 | L2 已验证 | .caffemodel/.pth/.onnx/.safetensors下载、CI模型获取、不可靠网络环境、教学模型获取 |
| [cross-language-three-layer-logging.md](cross-language-three-layer-logging.md) | 跨语言三层协调日志：C++ RAII Logger+编译期零开销闸门+FFI薄桥接+Python统一配置入口，一个setup_debug()同时控制两层日志粒度 | L3 可复用 | C/C++/Rust原生扩展+Python绑定、pybind11/tvm-ffi/PyO3跨语言项目、深度学习框架 |
| [resource-counter-primitive-binding.md](resource-counter-primitive-binding.md) | 资源计数器原语绑定（RAII资源追踪）：计数器增减绑定到最低层Alloc/Free原语，而非高层业务代码，原子操作+调用点日志+线程安全，杜绝高层遗漏导致的计数偏差 | L2 已验证 | FFI原生扩展内存管理、RAII资源生命周期追踪、跨语言内存泄漏检测基础设施 |
| [zero-copy-tensor-verification.md](zero-copy-tensor-verification.md) | 零拷贝张量访问四维验证：类型/形状一致→写入回读→拷贝隔离→持久共享，确保DLPack/FFI张量视图的内存共享语义正确而非意外拷贝或悬挂指针 | L2 已验证 | DLPack/FFI零拷贝张量共享、C++/Python跨语言张量视图、tvm-ffi/pybind11/PyO3张量绑定、in-place修改语义验证 |
| [ffi-intrusive-refcount-zerocopy.md](ffi-intrusive-refcount-zerocopy.md) | FFI侵入式引用计数零拷贝别名模式：利用TVM FFI Tensor/ObjectPtr已有的侵入式refcount，通过句柄赋值实现Blob/NDArray间零拷贝共享，无需自定义引用计数或内存池 | L2 已验证 | Layer间张量传递、Blob/NDArray数据共享、DLPack跨框架互操作、in-place优化（ReLU/Dropout）、梯度共享、C++ FFI原生扩展 |
| [ffi-zerocopy-tensor-dual-mode.md](ffi-zerocopy-tensor-dual-mode.md) | FFI边界零拷贝Tensor交互双模式选择：协议模式(np.from_dlpack默认安全)与裸指针模式(ctypes精确引用计数)二选一，裸指针模式五步安全清单+4个反模式（含ctypes临时指针引用循环陷阱） | L2 已验证 | Python/C++ FFI边界numpy数组转换、COW引用计数敏感场景、pybind11/TVM FFI/C数组封装、需要精确use_count的零拷贝交互 |
| [ffi-memory-leak-autouse-fixture.md](ffi-memory-leak-autouse-fixture.md) | FFI内存测试自动泄漏检测：pytest autouse fixture通过基线对比（字节数+对象数双维度）+强制GC+opt-out机制，零侵入自动检测原生内存泄漏 | L2 已验证 | C/C++/Rust原生扩展Python绑定测试、FFI层内存泄漏CI门禁、RAII正确性验证 |
| [conversion-point-debug-tracing.md](conversion-point-debug-tracing.md) | 数据转换点调试追踪：关键边界插入shape+dtype+值范围日志，快速定位精度丢失/shape mismatch/静默截断 | L2 已验证 | 数据预处理管道、模型推理链路、类型转换密集代码 |
| [structured-lightweight-logging.md](structured-lightweight-logging.md) | 结构化轻量日志：字段固定顺序+管道符分隔+一行一事件，grep/awk可直接分析，无需日志框架 | L1 实验性 | CLI工具、Shell脚本、性能敏感路径日志 |
| [three-layer-performance-optimization.md](three-layer-performance-optimization.md) | 三层性能优化方法论：算法→工程→编译逐级优化，先profiling再优化，避免过早优化陷阱 | L1 实验性 | 性能调优、计算密集型代码优化 |
| [build-failure-layered-triage.md](build-failure-layered-triage.md) | 构建失败分层排查法：L0环境层(30秒)→L1工具链层(2分钟)→L2项目层(5分钟+)三层递进排查，含决策树+PowerShell/Bash检查脚本+8语言迁移表 | L2 已验证 | C/C++/Rust/CUDA等编译型语言构建失败排查、跨平台/跨环境构建问题、编译器内部错误诊断 |
| [cmake-four-layer-modular-architecture.md](cmake-four-layer-modular-architecture.md) | CMake四层模块化架构：选项→依赖→函数→目标分层拆分，两轮重构策略（物理拆分+逻辑抽象），include顺序即依赖声明 | L1 实验性 | CMakeLists.txt超过100行的C/C++项目模块化，多目标（库+测试+示例）构建 |
| [cmake-list-removal-diagnostic-output.md](cmake-list-removal-diagnostic-output.md) | CMake列表变更诊断输出：REMOVE_ITEM/FILTER后必打message(STATUS)输出列表长度+内容+排除原因，消除"隐形文件排除"，含简单/条件/过滤三套模板 | L2 已验证 | CMake GLOB收集后排除文件、条件分支排除源文件/测试、CI构建日志可观测性 |
| [cmake-public-target-config-function.md](cmake-public-target-config-function.md) | CMake公共目标配置函数：封装target_*为带VISIBILITY参数+完整参数校验的function()，消除跨文件重复配置 | L1 实验性 | 多目标CMake项目重复编译配置消除，PUBLIC/PRIVATE/INTERFACE可见性控制 |
| [cmake-platform-specific-operation-encapsulation.md](cmake-platform-specific-operation-encapsulation.md) | CMake平台特定操作封装：平台专用文件+细粒度函数+聚合函数+通用工具三级API，统一参数校验宏 | L1 实验性 | Windows DLL复制、macOS rpath设置、跨平台构建操作封装 |
| [const-cow-trigger.md](const-cow-trigger.md) | const重载驱动的写时复制触发模式：通过cpu_data()/cpu_mutable_data()分离const/non-const访问路径，在non-const方法中检查refcount>1时触发克隆，实现安全的零拷贝共享+写入隔离 | L2 已验证 | Blob/Tensor写时复制、零拷贝别名后的写入安全、N≥2 fan-out场景、Split/Concat等多输出层优化 |
| [cow-shared-state-refcount-dual-semantics.md](cow-shared-state-refcount-dual-semantics.md) | COW共享状态标志与引用计数双重语义：IsDataShared()查询用双条件(data_shared_&&use_count>1)区分Owner/Borrower角色，COW触发只用use_count>1保守安全，七步实现+7反模式（含Owner写入保护） | L2 已验证 | 侵入式引用计数COW实现、FFI原生扩展内存管理、Owner/Borrower角色区分、零拷贝别名写入安全 |
| [platform-aware-dependency-detect.md](platform-aware-dependency-detect.md) | 平台感知的CMake依赖检测模式：两阶段验证（头文件→库文件）+已知前缀推导（conda前缀→Library/include）+平台路径差异化处理，解决Windows conda Library/前缀与Linux系统路径不一致问题 | L2 已验证 | 跨平台CMake依赖检测、conda环境依赖查找、Windows/Linux/macOS路径差异处理、第三方库自动发现 |
| [preflight-checks-script.md](preflight-checks-script.md) | 构建预检脚本前置模式：编译前执行环境检查脚本，主动检测TypeTraits冲突/DLL缺失/符号重复等常见陷阱，输出可操作错误信息而非晦涩编译错误 | L2 已验证 | C++/Python混合项目构建、CMake/native extension编译前环境验证、CI/CD流水线质量门禁、开发者环境快速诊断 |
| [progressive-interface-extension.md](progressive-interface-extension.md) | 框架接口渐进式扩展三阶段：默认存根（WARN/THROW非纯虚）→分批按优先级实现子类→调用路径激活时切换为强制，避免N个子类同时编译失败的大爆炸 | L1 候选 | C++基类虚方法添加、插件系统新API、SDK版本升级、框架功能分期上线、影响≥3个子类的接口变更 |
| [single-pass-perf-instrumentation.md](single-pass-perf-instrumentation.md) | 单次遍历性能统计日志埋点三原则：计算+统计单次遍历融合（禁止O(2N)二次遍历cache miss）、栈上零分配、循环外日志输出；结构化[TAG]标签+固定字段顺序+k=v格式 | L1 候选 | 深度学习算子/数值计算/图像处理/音频DSP/数据库扫描/ETL等大数组计算密集场景的性能监控埋点 |
| [ffi-fallback-diagnostics.md](ffi-fallback-diagnostics.md) | FFI降级路径结构化诊断：_FFIInitDiagnostics诊断对象+record_*方法分类记录+入口预设状态+公开get_init_diagnostics() API+CAFFE_FFI_STRICT_INIT严格模式，消除原生扩展静默降级反模式 | L2 已验证 | pybind11/tvm-ffi/nanobind/cffi等C/C++原生扩展Python绑定的初始化降级诊断、CI验证原生扩展加载 |
| [python-editable-import-isolation.md](python-editable-import-isolation.md) | Python editable install三层导入隔离：meta_path editable finder清理 + sys.path真实源码目录移除 + sys.modules缓存清除，配合subprocess隔离进程，解决scikit-build-core/setuptools/hatchling finder绕过sys.path问题 | L2 已验证 | 测试原生扩展缺失降级行为、CI验证wheel而非editable行为、最小化Python环境集成测试 |
| [protobuf-text-minimal-parser.md](protobuf-text-minimal-parser.md) | Protobuf文本格式最小解析器：5种Token类型(str/num/ident/{/})Tokenizer + 深度计数嵌套跳过 + 目标字段提取，约140行零依赖解析prototxt拓扑结构 | L1 实验性 | prototxt/pbtxt拓扑提取、DAG可视化验证工具、零依赖CI脚本、不需要完整protobuf语义的调试场景 |
| [numpy-reference-first.md](numpy-reference-first.md) | Numpy参考实现先行：写C++/框架测试前先用numpy实现纯Python参考版本，独立验证参考正确性后再对比目标实现，防止"测试本身写错" | L2 已验证 | 深度学习算子测试、数值计算函数测试、跨框架一致性验证、所有涉及浮点正确性的单元测试 |
| [three-layer-test-validation.md](three-layer-test-validation.md) | 三层测试验证法：known values精确验证 + 随机数据numpy匹配 + repeated forward确定性验证，从点到面覆盖正确性 | L2 已验证 | 深度学习算子forward测试、数学库验证、数值计算函数测试 |
| [explicit-split-multi-consumer.md](explicit-split-multi-consumer.md) | 多消费者显式Split：zero-copy/COW极简数据流框架中，同一blob被>1个layer消费时必须显式插入Split层，遵循框架命名约定 | L2 已验证 | caffe-ffi等极简DL框架测试、Rust所有权系统、显式内存管理数据流引擎 |
| [perf-trace-instrumentation.md](perf-trace-instrumentation.md) | perf_trace性能埋点集成：上下文管理器封装关键阶段，自动采集Δtime/Δmem/Δblobs，[PERF]统一前缀+固定字段顺序+结构化k=v | L2 已验证 | pytest测试套件、性能基准测试、FFI原生扩展测试、需要细粒度性能剖析的测试 |
| [separate-nets-independent-ops.md](separate-nets-independent-ops.md) | 独立操作分离Net：同一层的不同参数变体/独立操作各自创建独立Net实例，提取公共构造函数+参数化测试，避免blob消费冲突和状态污染 | L2 已验证 | DL框架算子对比测试、参数组合遍历测试、有单消费/状态副作用的框架测试 |
| [multi-strategy-auto-discovery.md](multi-strategy-auto-discovery.md) | 多策略自动发现：策略注册表→候选收集→有效性验证→版本匹配→名称偏好→兜底返回，解决跨机器环境路径差异问题 | L2 已验证 | 跨机器可移植脚本、构建工具环境自动发现、Conda/VS/JDK等外部依赖定位 |
| [version-priority-sorting.md](version-priority-sorting.md) | 版本优先级排序：版本号归一化→发行渠道优先级→多键排序→有效性过滤，解决多版本工具共存时的版本选择问题 | L2 已验证 | 多版本开发工具共存（VS/Python/JDK）、构建工具链版本选择、SDK版本管理 |
| [path-length-recovery.md](path-length-recovery.md) | PATH长度自动恢复：首次尝试→失败检测→环境快照→PATH精简→重试加载→路径合并→日志记录，解决Windows cmd.exe 8191字符限制 | L2 已验证 | Windows MSVC/Intel/CUDA等大型开发环境加载、DevShell初始化、批处理脚本命令行超长 |
| [thin-wrapper-pattern.md](thin-wrapper-pattern.md) | 薄包装模式：通用核心抽取→极薄参数映射层→参数透传→共享模块→约定优于配置，实现N个项目共用一套构建逻辑 | L2 已验证 | 多项目构建脚本、微服务部署脚本、CI/CD流水线模板、相似工具链配置 |
| [editable-install-stale-so.md](editable-install-stale-so.md) | Editable安装stale .so处理：重编译后对比build/与源码树editable路径的.so符号并显式复制刷新，应对editable install不自动更新编译产物 | L1 实验性 | C++/Cython扩展+editable install开发、重新编译后测试行为未跟随、scikit-build-core构建 |
| [cxx-build-regression-verification.md](cxx-build-regression-verification.md) | C++扩展构建回归验证：环境确认→宏/符号验证(strings)→全量回归→日志归档，应对错误环境/宏脱节/结果不归档三类静默假成功 | L1 实验性 | 跨平台C++项目(CMake+scikit-build)构建/重构回归验证、"编译产物可配置特性"回归、CI里程碑闭环 |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 候选 | 仅 1 次成功案例，标记为candidate待验证 | 验证次数 = 1，等待第二案例 |
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../README.md#模式成熟度评估标准)。

## 使用方式

1. 根据场景查找匹配模式
2. 阅读模式正文了解规则与正反例
3. 按模式规则执行操作
4. 验证后更新模式成熟度（若适用）
