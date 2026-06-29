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
| [check-and-restore.md](check-and-restore.md) | 检查函数状态恢复模式：检测前保存状态→优先就地检测→必要时导航后恢复URL，遵循CQS原则 | L2 已验证 | 浏览器自动化状态检查、API客户端、数据库操作 |

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