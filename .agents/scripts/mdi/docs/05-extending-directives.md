---
id: "mdi-extending-directives"
title: "扩展指南：新增Directive类型"
source: "PATTERN-APPLICATION.md#扩展指南新增directive类型"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/docs/05-extending-directives.toml"
---

# 扩展指南：新增Directive类型

假设要在webapi profile中新增`{websocket}`directive支持WebSocket端点。

## Step 1：确定Directive语法

````markdown
```{websocket} /ws/chat
:summary: 实时聊天WebSocket连接
:query token: string - 认证token (required)
:message ChatMessage: 发送消息格式
:message UserTyping: 用户输入中状态
:close 1000: 正常关闭
:close 1008: 认证失败
```
````

## Step 2：使用通用状态机解析

**不需要修改**`_parse_directive_content()`！该函数返回的通用结构已经足够：

```python
options, body = self._parse_directive_content(content, start_line)
# options = {
#   "summary": "实时聊天WebSocket连接",
#   "query": [("token", "string", "认证token", False)],
#   "message": [("ChatMessage", "发送消息格式"), ("UserTyping", ...)],
#   "close": [("1000", "正常关闭"), ("1008", "认证失败")],
# }
# body = 空行后的正文内容
```

## Step 3：在特定解析层处理新类型

在endpoint解析逻辑处添加websocket分支：

```python
if directive_name == "websocket":
    return self._parse_websocket_directive(args, options, body)
```

创建`_parse_websocket_directive()`处理`:message :close`等特定选项。

## Step 4：更新Validator规则

在webapi_profile的validation_rules中添加websocket验证规则。

## Step 5：更新Generators

在生成器（openapi_gen、typescript_gen等）中添加WebSocket端点的代码生成逻辑。
