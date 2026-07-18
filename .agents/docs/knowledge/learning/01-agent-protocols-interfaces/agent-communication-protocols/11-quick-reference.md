---
version: "1.0"
source: "../agent-communication-protocols-wiki.md#11-快速参考"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-communication-protocols/11-quick-reference.toml"
id: "quick-reference"
title: "11、快速参考速查表"
---
# 11、快速参考速查表

## 说明

本章是开发者速查卡，打印贴桌上即用。所有详细内容请参见对应章节。

---

## 四大协议一分钟速览

| 协议 | 一句话定位 | 何时用 | 类比 |
|------|-----------|--------|------|
| MCP | Agent连接工具/数据 | 需要调用外部API/工具/数据库时 | USB-C接口 |
| ACP | 本地Agent间P2P通信 | 同设备/局域网内多Agent低延迟协作 | 局域网Wi-Fi |
| A2A | 跨厂商Agent协作 | 跨组织/跨SaaS/跨平台Agent协作 | HTTP（互联网） |
| ANP | 去中心化Agent网络 | 开放公网Agent发现/信任/经济（早期） | 互联网协议层 |

---

## 协议选型Checklist

快速决策7问：

- **Q1**: 我需要让Agent调用外部工具/API吗？ → 是：加MCP
- **Q2**: Agent间需要在同一台机器/本地网络通信吗？ → 是：用ACP
- **Q3**: Agent需要与其他厂商/组织的Agent协作吗？ → 是：用A2A
- **Q4**: 需要在开放公网无中心发现和信任Agent吗？ → 是：关注ANP
- **Q5**: 任务执行时间超过1分钟且需要进度跟踪吗？ → 是：A2A的有状态Task模型更合适
- **Q6**: 部署环境有气隙/离线要求吗？ → 是：ACP更适合
- **Q7**: 需要零SDK/curl即可调试吗？ → ACP（REST原生）或A2A（JSON-RPC over HTTP可用curl）

---

## 核心API端点速查

### MCP（JSON-RPC 2.0）

| 方法 | 用途 | 传输 |
|------|------|------|
| initialize | 握手/能力协商 | stdio/HTTP |
| tools/list | 列出可用工具 | |
| tools/call | 调用工具 | |
| resources/read | 读取资源 | |
| prompts/list | 列出提示模板 | |

### A2A（JSON-RPC 2.0 over HTTP）

| 端点/方法 | 用途 |
|-----------|------|
| GET `/.well-known/agent.json` | 获取Agent Card |
| `tasks/send` | 提交任务（同步） |
| `tasks/sendSubscribe` | 提交任务（SSE流式） |
| `tasks/get` | 查询任务状态 |
| `tasks/cancel` | 取消任务 |
| POST `/webhook` | 推送通知（可选） |

### ACP（RESTful HTTP）

| 端点 | 方法 | 用途 |
|------|------|------|
| `/tasks` | POST | 创建任务 |
| `/tasks/{id}` | GET | 查询任务状态 |
| `/agents` | GET | 列出可用Agent（mDNS发现） |

---

## Agent Card最小模板

A2A Agent Card最小可用JSON示例：

```json
{
  "name": "MyAgent",
  "description": "一个示例A2A Agent",
  "url": "https://myagent.example.com",
  "version": "1.0.0",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "skills": [
    {
      "id": "greet",
      "name": "Greeting",
      "description": "向用户问好"
    }
  ]
}
```

**必填字段**：`name`、`url`、`version`、`capabilities`、`defaultInputModes`、`defaultOutputModes`、`skills`（至少一个）。

---

## 常见问题FAQ

**Q: MCP和A2A/ACP是竞争关系吗？**
A: 不是。MCP是纵向（Agent连工具），A2A/ACP是横向（Agent连Agent），互补使用。

**Q: 我应该选ACP还是A2A？**
A: 本地/边缘/低延迟/气隙选ACP，跨厂商/企业/互联网选A2A，两者可共存。

**Q: 一个Agent可以同时支持多个协议吗？**
A: 可以。一个Agent可以同时作为MCP Server、A2A Server和ACP节点。

**Q: MCP只能本地使用吗？**
A: 不是。MCP支持stdio（本地）和Streamable HTTP（远程），远程MCP Server也很常见。

**Q: A2A必须使用Google的平台吗？**
A: 不是。A2A是开放协议，捐赠给Linux基金会，任何平台都可以实现。

**Q: ANP现在可以生产使用吗？**
A: ANP规范尚在早期发展阶段，建议关注并实验，不建议生产环境核心依赖。

**Q: 用这些协议需要专门的SDK吗？**
A: MCP官方推荐SDK但可用JSON-RPC直接实现；ACP零SDK（REST原生curl即可）；A2A有SDK也可以直接HTTP+JSON-RPC。

**Q: 这些协议安全吗？**
A: MCP要求OAuth2.1、A2A支持OAuth2/mTLS/API Key、ACP支持DID/RBAC，安全性取决于正确配置。

---

## 章节导航

| 导航 | 链接 |
|------|------|
| 返回总览 | [Agent通信协议总览](../agent-communication-protocols-wiki.md) |
| 上一章 | [10、资源与参考链接](./10-resources.md) |
| **下一章** | 无（本章为最后一章）🎉 |
