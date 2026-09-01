---
id: "mdi-pattern-directive-state-machine"
title: "模式一：Directive参数状态机解析"
source: "PATTERN-APPLICATION.md#模式一directive参数状态机解析"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/docs/01-pattern-directive-state-machine.toml"
---

# 模式一：Directive参数状态机解析

> **模式文档**：[directive-state-machine-parsing.md](../../../../docs/retrospective/patterns/code-patterns/directive-state-machine-parsing.md)

## MDI中的实现位置

| 文件 | 函数/类 | 职责 |
|------|---------|------|
| [parser.py](../parser.py) | `_parse_directive_content()` (L649-L726) | 通用directive三阶段状态机解析 |
| [parser.py](../parser.py) | `_DIRECTIVE_RE` (L25) | 首行匹配正则 |
| [parser.py](../parser.py) | `_OPTION_LINE_RE` (L27) | 选项行匹配正则 |
| [parser.py](../parser.py) | `BlockType.DIRECTIVE` | Directive块类型枚举 |

## MDI中支持的Directive类型

| Directive | 所属Profile | 选项键 | 说明 |
|-----------|-------------|--------|------|
| `{endpoint}` | webapi | `:summary :query :path :body :response` | REST API端点定义 |
| `{command}` | clitool | `:summary :arg :flag :option :exit` | CLI命令定义 |
| `{note}/{warning}/{tip}` | 通用 | `:warning:（可选标记）` | 提示块 |

## 实际应用示例

以user-api.md中的endpoint directive为例：

````markdown
```{endpoint} POST /auth/login
:summary: 用户登录获取access_token
:body username: string - Username or email (required)
:body password: string - Account password (required)
:response 200: AuthToken - Authentication successful
:response 401: ErrorResponse - Invalid credentials
```
````

解析过程：

1. **首行匹配**：`_DIRECTIVE_RE`匹配`{endpoint}`，提取`directive_name="endpoint"`，`args="POST /auth/login"`
2. **选项状态机**：逐行处理
   - 行`:summary: 用户登录...` → `options["summary"] = "用户登录获取access_token"`
   - 行`:body username: string - ...` → `options["body"]`列表追加参数
   - 行`:response 200: AuthToken - ...` → `options["response"]`列表追加响应
3. **空行结束**：遇到空行后body_start标记位置，剩余行拼接为body

## 新增Directive类型的正确做法

```python
# 在parser.py中特定directive处理部分添加新类型
def _parse_endpoint_directive(options, body):
    """webapi endpoint特定解析"""
    method, path = args.split(None, 1)
    # 处理:query/:path/:body前缀
    # 处理?可选标记
    return EndpointDirective(method=method, path=path, ...)

# 通用状态机不修改，保持三阶段结构
```

## 常见陷阱

❌ **错误**：修改`_parse_directive_content`通用状态机加入endpoint特定逻辑
```python
# 不要这样做！违反单一职责
if key == "body" and directive_name == "endpoint":
    # endpoint特定的body处理...
```

✅ **正确**：在状态机返回通用`(options, body)`后，由调用方做特定directive类型的二次解析

❌ **错误**：用单个大正则匹配所有内容
```python
# 不要这样做！无法处理多行、空行分隔、可选标记
_BAD_DIRECTIVE_RE = re.compile(
    r"^{(\w+)}\s+(\w+)\s+(\S+)\s+"
    r"((?::[\w]+\??:\s*.*\n)+)"  # 这无法正确处理边界
)
```

✅ **正确**：首行用简单正则，选项逐行状态机处理
