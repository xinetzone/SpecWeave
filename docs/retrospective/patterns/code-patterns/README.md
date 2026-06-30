+++
description = "代码模式索引 - 可复用的代码级解决方案模式"
layer = "code"
+++

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
| [dual-channel-tiered-logging.md](dual-channel-tiered-logging.md) | 分级日志双轨输出模式：控制台INFO+文件DEBUG，含语义化日志函数、静态资源过滤、Handler级别控制 | L2 已验证 | CLI工具、自动化脚本、浏览器自动化 |
| [tuyaopen-tos-cli-command-registry.md](tuyaopen-tos-cli-command-registry.md) | 单入口 + 子命令注册表模式（click + 字典注册），便于工具链多子命令扩展 | L1 实验性 | 工具链CLI、脚手架CLI、多子命令程序 |
| [check-and-restore.md](check-and-restore.md) | 检查函数状态恢复模式：检测前保存状态→优先就地检测→必要时导航后恢复URL，遵循CQS原则 | L2 已验证 | 浏览器自动化状态检查、API客户端、数据库操作 |
| [cross-platform-encoding-enforcement.md](cross-platform-encoding-enforcement.md) | 跨平台输出编码强制设置：包装器设置PYTHONIOENCODING=utf-8，避免Windows GBK终端UnicodeEncodeError，ASCII安全输出策略 | L2 已验证 | Python CLI工具、跨平台脚本、subprocess调用 |
| [temporary-syspath-modification.md](temporary-syspath-modification.md) | 临时sys.path修改条件导入：try前insert→finally恢复，不污染全局导入路径，Optional返回优雅降级 | L2 已验证 | 可选依赖导入、vendor子模块引用、插件系统 |
| [path-anchor-semantization.md](path-anchor-semantization.md) | 路径锚点语义化：每级parent赋予语义变量名，避免链式.parent.parent计算差一级的常见bug | L1 实验性 | 项目内路径计算、脚本路径定位、包根目录查找 |
| [async-setup-future-deduplication.md](async-setup-future-deduplication.md) | 装配并发去重：以组件key维护Future并复用，确保并发装配一致结果/一致失败 | L1 实验性 | 插件/组件装配、依赖闭包、并发初始化 |
| [skill-three-part-structure.md](skill-three-part-structure.md) | 技能三分结构：SKILL最小入口 + references按需长文档 + scripts可执行动作 | L1 实验性 | AI Skills 设计、工作流知识包、可执行SOP沉淀 |
| [script-json-output-contract.md](script-json-output-contract.md) | 脚本可编排输出契约：统一 --json 输出字段与退出码，避免输出不可解析 | L1 实验性 | CLI脚本、Agent编排、CI工具 |
| [session-file-externalization.md](session-file-externalization.md) | 会话外部化：用 session file 解耦多命令状态，支持跨进程协同 | L1 实验性 | start/tail/stop 工具、后台守护脚本 |
| [path-traversal-guard.md](path-traversal-guard.md) | 路径越界防护：realpath/resolve + 前缀校验，阻断任意路径访问 | L1 实验性 | 接受路径参数的脚本、批量检查/修复工具 |
| [pre-kill-identity-verification.md](pre-kill-identity-verification.md) | 停止前身份校验：kill 前先校验 cmdline 属于目标进程，避免误杀 | L1 实验性 | stop/kill 类脚本、后台监控工具 |

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
