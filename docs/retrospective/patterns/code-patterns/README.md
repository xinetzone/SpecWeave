---
id: "code-patterns-readme"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/README.toml"
---
# 代码模式索引（code-patterns）

本目录存放代码级可复用模式，聚焦于具体代码编写、文件操作、编辑策略等微观层面的最佳实践。

## 模式清单

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [safe-table-edit.md](safe-table-edit.md) | Markdown 表格安全修改策略，整表替换优先、局部替换仅限文本修改 | L1 实验性 | Markdown 表格结构修改 |
| [mermaid-safe-coding-rules.md](mermaid-safe-coding-rules.md) | Mermaid 安全编码五规则，覆盖空行/引号/列表触发/Subgraph/边标签，配套自动化检查脚本 | L4 标准化 | Mermaid 图表编写（防渲染失败） |
| [mermaid-trap-cheatsheet.md](mermaid-trap-cheatsheet.md) | Mermaid 8 类常见陷阱速查表，快速排查渲染问题 | L4 标准化 | Mermaid 渲染故障快速排查 |
| [relative-depth-adjustment.md](relative-depth-adjustment.md) | 相对路径深度自动校正算法，±3级调整`../`层数配合存在性校验，零误报率 | L2 已验证 | 目录重构/原子化后的批量链接修复 |
| [fix-priority-chain.md](fix-priority-chain.md) | 自动修复优先级链设计，精确修复优先、模糊修复兜底，无法修复明确报告人工 | L2 已验证 | 多策略自动修复工具 |
| [periodic-check-caching.md](periodic-check-caching.md) | 定期检查类工具缓存机制，可配置TTL/--no-cache/--clear-cache，HTTP请求从10-20秒降至<1秒 | L1 实验性 | CLI检查工具、外部资源访问工具、CI脚本 |
| [parallel-subprocess-observability.md](parallel-subprocess-observability.md) | 并行子进程全链路可观测模式：命令参数精简+ThreadPoolExecutor并行+三阶段日志+加速比自证，子模块检查耗时↓68% | L2 已验证 | 多目标批量检查CLI、子模块管理工具、多服务健康检查、批量文件处理 |
| [dual-channel-tiered-logging.md](dual-channel-tiered-logging.md) | 分级日志双轨输出模式：控制台INFO+文件DEBUG，含语义化日志函数、静态资源过滤、Handler级别控制 | L2 已验证 | CLI工具、自动化脚本、浏览器自动化 |
| [tuyaopen-tos-cli-command-registry.md](tuyaopen-tos-cli-command-registry.md) | 单入口 + 子命令注册表模式（click + 字典注册），便于工具链多子命令扩展 | L1 实验性 | 工具链CLI、脚手架CLI、多子命令程序 |
| [check-and-restore.md](check-and-restore.md) | 检查函数状态恢复模式：检测前保存状态→优先就地检测→必要时导航后恢复URL，遵循CQS原则 | L2 已验证 | 浏览器自动化状态检查、API客户端、数据库操作 |
| [cross-platform-encoding-enforcement.md](cross-platform-encoding-enforcement.md) | 跨平台输出编码三层防御体系：入口编码设置+防御性能力检测+Unicode/ASCII适配输出，避免Windows GBK终端崩溃 | L2 已验证 | Python CLI工具、跨平台脚本、subprocess调用 |
| [defensive-attribute-access.md](defensive-attribute-access.md) | 外部对象防御性属性访问：getattr→callable→try-except三层防护，应对属性不存在/None/不可调用/抛异常场景 | L2 已验证 | CLI工具库、stream操作、插件接口、mock环境下的防御性编程 |
| [direct-file-write-over-shell-pipe.md](direct-file-write-over-shell-pipe.md) | 文档生成直写文件优先：避免 Windows PowerShell 文本管道在落盘阶段污染中文内容 | L1 实验性 | README/报告生成、Markdown导出、知识库条目写回 |
| [temporary-syspath-modification.md](temporary-syspath-modification.md) | 临时sys.path修改条件导入：try前insert→finally恢复，不污染全局导入路径，Optional返回优雅降级 | L2 已验证 | 可选依赖导入、vendor子模块引用、插件系统 |
| [path-anchor-semantization.md](path-anchor-semantization.md) | 路径锚点语义化：每级parent赋予语义变量名，避免链式.parent.parent计算差一级的常见bug | L1 实验性 | 项目内路径计算、脚本路径定位、包根目录查找 |
| [async-setup-future-deduplication.md](async-setup-future-deduplication.md) | 装配并发去重：以组件key维护Future并复用，确保并发装配一致结果/一致失败 | L1 实验性 | 插件/组件装配、依赖闭包、并发初始化 |
| [skill-three-part-structure.md](skill-three-part-structure.md) | 技能三分结构：SKILL最小入口 + references按需长文档 + scripts可执行动作 | L1 实验性 | AI Skills 设计、工作流知识包、可执行SOP沉淀 |
| [script-json-output-contract.md](script-json-output-contract.md) | 脚本可编排输出契约：统一 --json 输出字段与退出码，避免输出不可解析 | L1 实验性 | CLI脚本、Agent编排、CI工具 |
| [session-file-externalization.md](session-file-externalization.md) | 会话外部化：用 session file 解耦多命令状态，支持跨进程协同 | L1 实验性 | start/tail/stop 工具、后台守护脚本 |
| [path-traversal-guard.md](path-traversal-guard.md) | 路径越界防护：realpath/resolve + 前缀校验，阻断任意路径访问 | L1 实验性 | 接受路径参数的脚本、批量检查/修复工具 |
| [pre-kill-identity-verification.md](pre-kill-identity-verification.md) | 停止前身份校验：kill 前先校验 cmdline 属于目标进程，避免误杀 | L2 已验证 | stop/kill 类脚本、后台监控工具 |
| [example-driven-test-generation.md](example-driven-test-generation.md) | 示例驱动测试生成：从文档代码块提取真实测试数据，配合检查清单→断言转换，解决文档漂移 | L1 实验性 | API文档→测试代码生成、接口测试自动化 |
| [structured-doc-diff-semver.md](structured-doc-diff-semver.md) | 结构化文档Diff与SemVer建议：字段级对比→严重性分级→影响分析→版本建议 | L1 实验性 | IDL/配置Schema版本管理、API变更审查 |
| [directive-state-machine-parsing.md](directive-state-machine-parsing.md) | Directive参数状态机解析：首行匹配→选项行状态机→正文识别三阶段解析MyST扩展语法，避免巨型正则 | L1 实验性 | Markdown自定义扩展语法解析、多类型directive统一解析框架 |
| [checklist-to-assertion-conversion.md](checklist-to-assertion-conversion.md) | 检查清单→断言转换：关键词分类（前置/断言/后置/注释）+专项正则提取，将人类验收标准转为测试步骤 | L1 实验性 | 文档驱动测试生成、Docs-as-Tests工具链 |
| [profile-auto-detection.md](profile-auto-detection.md) | Profile自动检测：五级优先级信号源分层匹配（显式声明→强特征→路径特征→内容特征→默认值），零配置类型识别 | L1 实验性 | 多格式/多Schema解析器、约定优于配置的CLI工具 |
| [data-model-extraction-signal.md](data-model-extraction-signal.md) | 数据模型提取信号：models.py出现标志代码从"脚本集合"跨越到"类型安全应用"，frozen dataclass三重价值 | L1 实验性 | 脚本模块化、API边界定义、配置管理、测试数据构造 |
| [docker-container-session-raii.md](docker-container-session-raii.md) | Docker 容器会话 RAII 模式：上下文管理器封装容器生命周期，确保异常也不泄漏资源 | L1 实验性 | 容器化构建流水线、CI/CD任务、多步容器操作 |
| [content-hash-build-cache.md](content-hash-build-cache.md) | 内容哈希构建缓存：基于 git HEAD 哈希的智能构建跳过，比时间戳更可靠 | L1 实验性 | 编译构建缓存、数据处理管道、模型训练预处理 |
| [cli-as-api-design.md](cli-as-api-design.md) | CLI即API设计：多格式输出（table/json/yaml/wide）+结构化错误+退出码约定+会话持久化，同时服务人类和机器 | L1 实验性 | CLI工具设计、AI原生工具、DevOps工具、脚本自动化 |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../README.md#模式成熟度评估标准)。

## 使用方式

1. 根据场景查找匹配模式
2. 阅读模式正文了解规则与正反例
3. 按模式规则执行操作
4. 验证后更新模式成熟度（若适用）
