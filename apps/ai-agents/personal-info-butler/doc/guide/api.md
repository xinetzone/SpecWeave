---
id: api
---

# 接口契约

所有接口前缀 `/api`，请求与响应均为 JSON。
设置了 `APP_TOKEN` 时，必须携带 `X-App-Token: <token>` 或 `Authorization: Bearer <token>`。

## BYOK 请求头

| 头 | 说明 |
|---|---|
| `X-LLM-Base-Url` | 覆盖服务端 `LLM_BASE_URL` |
| `X-LLM-Api-Key` | 覆盖服务端密钥；**有此头 BYOK 才生效** |
| `X-LLM-Model` | 覆盖服务端 `LLM_MODEL` |

这三个头只在当次请求的内存里生效，不落盘、不写日志。

## 端点一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 存储模式、模型就绪状态（含页面 BYOK）、是否需要鉴权 |
| POST | `/api/llm/test` | 用请求级 BYOK 打一次最小探针，验证凭据是否正确 |
| GET | `/api/items` | 列表与关键词检索 |
| POST | `/api/items` | 录入（分类 / 摘要 / 标签 / 关联 / 派生待办） |
| GET | `/api/items/{id}` | 读取单条 |
| PATCH | `/api/items/{id}` | 局部更新 |
| DELETE | `/api/items/{id}` | 删除 |
| GET | `/api/items/{id}/links` | 该条目的关联关系 |
| POST | `/api/ask` | 智能问答，返回答案与引用 |
| POST | `/api/extract` | 重点信息提取（Markdown） |
| GET | `/api/todos` | 待办整理（去重、分组、建议） |
| GET | `/api/summary` | 历史总结列表 |
| POST | `/api/summary` | 生成阶段总结并存档 |
| GET | `/api/tags` | 标签云与统计 |

## 关键请求

录入（唯一必填字段是 `content`）：

```text
POST /api/items
{ "content": "下周三前要把定价方案发给客户，另外记得看那份行业报告 https://..." }
```

响应：

```json
{
  "item": { "id": "...", "kind": "todo", "title": "发送定价方案", "tags": ["定价", "客户"] },
  "todos": [ { "title": "发送定价方案", "priority": 2, "due_date": "2026-10-21" } ],
  "links": [ { "id": "...", "title": "客户访谈纪要", "score": 0.31, "reason": "共享标签：客户" } ]
}
```

检索：

```
GET /api/items?q=定价&kind=todo&status=open&limit=20
```

问答：

```text
POST /api/ask
{ "question": "我在定价方案上做过哪些判断？", "limit": 8 }
```

## 验证 BYOK 凭据

```text
POST /api/llm/test
X-LLM-Base-Url: https://api.deepseek.com/v1
X-LLM-Api-Key: sk-...
X-LLM-Model: deepseek-chat
```

```json
{ "ok": true, "model": "deepseek-chat", "reason": "" }
```

这个端点**永远返回 200**，验证结论放在响应体的 `reason` 里：

| reason | 含义 |
|---|---|
| `API Key 无效（端点返回 401）` | Key 错了或已失效 |
| `地址或模型名不对（端点返回 404）` | Base URL 或模型名填错 |
| `被限流了（429），稍后再试` | 账户限速 |
| `连不上这个地址（ConnectError）` | Base URL 不可达 |

填错凭据是**用户输入错误**而不是服务端故障：若用状态码表达，页面就只能显示
「服务器出错」，用户也就无从下手。探针只发一条 `max_tokens=1` 的请求，
代价可忽略；它走 chat 而非 `/models`，因为只有 chat 能同时验出「Key 有效」
与「模型名存在」。

> 该端点继承 `APP_TOKEN` 鉴权：探针会真实发起一次模型调用，不鉴权就等于
> 给公网开了一个免费代理。

## 错误语义

| 状态码 | 含义 |
|---|---|
| 401 | `APP_TOKEN` 已设置但请求未提供或不匹配 |
| 404 | 条目不存在 |
| 422 | 请求体校验失败（如 `content` 为空） |
| 503 | 云端存储不可达或返回错误 |

大模型故障**不产生错误状态码**——它会退化为启发式结果返回，
响应体里的 `source` 字段标明实际走的分支：`llm` / `heuristic` / `error` / `none`。
这是刻意的：模型抖动不该让「随手记」这件事失败。
