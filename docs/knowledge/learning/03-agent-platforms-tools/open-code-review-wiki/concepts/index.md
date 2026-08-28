# Concepts

- [安装与配置](01-installation.md) — OCR 安装与配置指南，涵盖 npm/npx/源码/Release 四种安装方式、状态目录结构、项目规则配置、自动更新、卸载方法与安装验证。
- [核心架构](03-architecture.md) — OCR 核心架构深度解析，涵盖六阶段流水线、Agent 模块、Subtask 两阶段执行、Main Loop、三区内存压缩、Diff/Scan 模块与 Manifest 可追溯性。
- [LLM 协议与 Provider](04-llm-providers.md) — OCR LLM 集成层详解，涵盖 LLMClient 接口契约、三种协议实现、19 个内置 Provider、四策略 Endpoint 解析链、Token 计数与自定义 Provider 扩展。
- [内置工具与 MCP 集成](05-tools-mcp.md) — OCR 工具系统详解，涵盖 Registry 注册机制、Provider 接口契约、6 个内置工具、code_comment 评论机制、MCP 集成与工具自定义扩展。
- [审查规则系统](06-review-rules.md) — OCR 审查规则系统解析，涵盖四层优先级合并、ProjectRule 结构、Glob 匹配语法、内置默认排除、系统规则映射、文件过滤算法与 ocr rules check 调试命令。
- [会话持久化、遥测与查看器](07-session-telemetry.md) — OCR 可观测性三件套详解，涵盖 JSONL 会话日志、Manifest 双边界状态机、会话恢复重放、OpenTelemetry Span/Metric 体系与嵌入式查看器。
- [集成与扩展](08-integrations.md) — OCR 集成生态梳理，涵盖 CI/CD 流水线、Agent 工具链、委托模式、Agent Skill、VS Code 扩展与 MCP 服务器集成方式。

```{toctree}
:maxdepth: 2

01-installation
03-architecture
04-llm-providers
05-tools-mcp
06-review-rules
07-session-telemetry
08-integrations
```