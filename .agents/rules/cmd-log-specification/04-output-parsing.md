---
id: "cmd-log-output-parsing"
title: "输出要求、日志解析与过滤分析"
source: "cmd-log-specification.md#04-output-parsing"
x-toml-ref: "../../../.meta/toml/.agents/rules/cmd-log-specification/04-output-parsing.toml"
---
# 输出要求、日志解析与过滤分析

## 8. 输出要求

1. **即时输出**：事件发生时立即输出，不得延迟到步骤结束批量输出
2. **单行输出**：每条日志必须在一行内，ctx JSON压缩为单行（无换行、无额外空格）
3. **中文消息**：msg字段使用中文，ctx键名使用英文
4. **不替代交互**：日志是辅助排查工具，不替代面向用户的正式输出
5. **ctx精简**：ctx只记录对排查问题有用的关键数据，不输出大段内容
6. **错误必记**：所有ERROR级别事件必须记录，且ctx中必须包含recovery_hint


## 9. 日志解析

一条正则即可解析所有CMD-LOG日志：

```python
import re
import json

CMD_LOG_RE = re.compile(
    r'\[CMD-LOG\]\s*\|\s*'
    r'level=(\w+)\s*\|\s*'
    r'cmd=(\w+(?:-\w+)?)\s*\|\s*'
    r'step=(S\d+)\s*\|\s*'
    r'event=(\w+)\s*\|\s*'
    r'session=([^|]+?)\s*\|\s*'
    r'msg=([^|]+?)(?:\s*\|\s*ctx=(.+))?$'
)

def parse_cmd_log(line: str) -> dict | None:
    m = CMD_LOG_RE.match(line.strip())
    if not m:
        return None
    result = {
        'level': m.group(1),
        'cmd': m.group(2),
        'step': m.group(3),
        'event': m.group(4),
        'session': m.group(5),
        'msg': m.group(6),
        'ctx': {}
    }
    ctx_str = m.group(7)
    if ctx_str:
        try:
            result['ctx'] = json.loads(ctx_str)
        except json.JSONDecodeError:
            result['ctx'] = {'_raw': ctx_str}
    return result
```

ctx字段用 `json.loads()` 解析，失败时降级为raw存储。


## 10. 过滤与分析命令

常用日志分析命令：

```bash
# 过滤所有CMD-LOG日志
grep "\[CMD-LOG\]" output.log

# 过滤某个命令集的日志
grep "\[CMD-LOG\].*cmd=retrospective" output.log

# 过滤某个会话的完整执行链路
grep "session=retr-20260629-firecrawl" output.log

# 过滤所有错误事件
grep "\[CMD-LOG\].*level=ERROR" output.log

# 过滤所有警告事件
grep "\[CMD-LOG\].*level=WARN" output.log

# 统计各命令集执行次数
grep "event=CMD_START" output.log | grep -oP 'cmd=\K[^|]+' | sort | uniq -c

# 查看某个会话的耗时
grep "session=retr-20260629-firecrawl.*event=CMD_COMPLETE" output.log | grep -oP 'ctx=\{.*"duration":"[^"]+"'
```


---

## 相关模式

- - [阶段守卫规范](../stage-guardrails.md)
- - [PDR前置文档读取协议](../../protocols/pre-document-reading.md)
- - [结构化轻量日志格式](../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md)

← 上一章: [通用事件、步骤编号与命令集特有事件](03-events-steps.md) | **[返回索引](../cmd-log-specification.md)** | 下一章 → [检查清单、日志集成关系与Changelog](05-checklist-integration-changelog.md)
