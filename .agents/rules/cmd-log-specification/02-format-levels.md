---
id: "cmd-log-format-levels"
title: "日志格式与级别约定"
source: "cmd-log-specification.md#02-format-levels"
x-toml-ref: "../../../.meta/toml/.agents/rules/cmd-log-specification/02-format-levels.toml"
---
# 日志格式与级别约定

## 3. 日志格式

### 3.1 统一格式

```
[CMD-LOG] | level=<LEVEL> | cmd=<CMD_NAME> | step=<STEP_ID> | event=<EVENT> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

### 3.2 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|-----|------|------|
| `[CMD-LOG]` | ✅ | 日志前缀标识，grep时一行命令即可过滤命令集日志 | `[CMD-LOG]` |
| `level` | ✅ | 日志级别：DEBUG/INFO/WARN/ERROR | `INFO` |
| `cmd` | ✅ | 命令集标识，固定值见上表 | `retrospective` |
| `step` | ✅ | 当前执行步骤编号，格式 `S<N>` | `S3` |
| `event` | ✅ | 事件类型，大写下划线风格，见各命令集事件表 | `CMD_START` |
| `session` | ✅ | 会话ID，格式：`<prefix>-YYYYMMDD-<topic>` | `retr-20260629-firecrawl` |
| `msg` | ✅ | 中文人类可读消息，不依赖工具即可理解 | `开始复盘：project...` |
| `ctx` | ❌ | 压缩JSON上下文（单行无换行），键名使用英文 | `{"scope":"project",...}` |

### 3.3 分隔符约定

使用 `|` 作为字段分隔符，原因：
- `|` 在自然语言文本中出现频率极低，不易产生歧义
- 视觉上清晰分隔各字段
- 正则匹配简单：`([^|]+?)\s*` 即可提取字段值

### 3.4 Session ID格式规范

| 命令集 | 前缀 | 完整格式 | 示例 |
|--------|------|---------|------|
| retrospective | `retr-` | `retr-YYYYMMDD-<topic>` | `retr-20260629-firecrawl` |
| insight | `insgt-` | `insgt-YYYYMMDD-<topic>` | `insgt-20260629-architecture` |
| export-report | `exprt-` | `exprt-YYYYMMDD-<topic>` | `exprt-20260629-firecrawl-report` |
| atomization | `atom-` | `atom-YYYYMMDD-<filename>` | `atom-20260629-insight-export` |
| atomic-commit | `cmt-` | `cmt-YYYYMMDD-<short-hash>` | `cmt-20260629-a3f2b1` |
| mermaid | `merm-` | `merm-YYYYMMDD-<topic>` | `merm-20260630-architecture` |
| pattern-extraction | `ptrn-` | `ptrn-YYYYMMDD-<pattern-name>` | `ptrn-20260701-markdown-as-interface` |


## 4. 日志级别约定

| 级别 | 标识 | 使用场景 | 是否入交接文档 |
|------|------|---------|-------------|
| DEBUG | 🔍 | 细粒度调试（元数据提取、内容迁移细节、单项检查通过） | 否 |
| INFO | ℹ️ | 正常流程节点（命令开始/完成、步骤进入/完成、文件创建、提交执行） | 否 |
| WARN | ⚠️ | 异常但可恢复（数据不足、断链发现、无关文件、过度拆分警告） | **是** |
| ERROR | ❌ | 严重错误（源文件无效、敏感文件检测、提交失败、验证阻塞） | **是** |


---

## 相关模式

- - [阶段守卫规范](../stage-guardrails.md)
- - [PDR前置文档读取协议](../../protocols/pre-document-reading.md)
- - [结构化轻量日志格式](../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md)

← 上一章: [概述与适用范围](01-overview-scope.md) | **[返回索引](../cmd-log-specification.md)** | 下一章 → [通用事件、步骤编号与命令集特有事件](03-events-steps.md)
