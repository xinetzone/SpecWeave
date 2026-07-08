---
title: "MCP工具参考"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/reference/mcp-tools"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/04-mcp-tools.toml"
date: "2026-07-07"
tags: ["minitest", "mcp", "mcp-tools", "model-context-protocol", "参考"]
summary: "miniTest MCP服务器暴露的所有工具的API级参考文档，包括发现、用户故事、运行、构建、配置和文档工具。"
---
> 来源：https://www.minitap.ai/docs/minitest/reference/mcp-tools

# MCP工具参考

miniTest MCP服务器暴露一组工具，您的编码代理使用这些工具浏览应用、创建和编辑用户故事、触发运行、读取结果和搜索文档。本页在API级别记录每个工具，以便您知道您的代理可以访问什么。

有关安装步骤和代理提示，请参阅[Cursor和Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)。

## 工具

### 发现（Discovery）

| 工具 | 说明 |
| --- | --- |
| `get_user_apps` | 获取认证用户有权访问的所有应用。首先使用此工具发现其他工具所需的有效`app_id`值。 |

### 用户故事（User stories）

| 工具 | 说明 |
| --- | --- |
| `list_user_stories` | 列出应用的用户故事。使用`type_filter`缩小到：`login`、`registration`、`checkout`、`onboarding`、`search`、`settings`、`navigation`、`form`、`profile`或`other`。 |
| `get_user_story` | 通过ID获取用户故事，包括其验收标准。 |
| `create_user_story` | 创建带有验收标准的新用户故事。每个标准是AI代理在设备上验证的纯文本断言。标准必须是视觉可观察的，因此避免仅后端断言。有效类型：`login`、`registration`、`checkout`、`onboarding`、`search`、`settings`、`navigation`、`form`、`profile`、`other`。 |
| `update_user_story` | 更新现有用户故事。仅更改提供的字段。当提供`acceptance_criteria`时，整个列表被替换。也接受`depends_on`来连接故事依赖关系（全部替换：传递`[]`清除，省略保持不变）。 |
| `delete_user_story` | 删除用户故事及其关联的验收标准。 |

### 运行（Runs）

| 工具 | 说明 |
| --- | --- |
| `create_run` | 为用户故事创建故事运行并排队执行。传递`ios_build_id`、`android_build_id`或`run_web=true`中的至少一个来选择执行哪些目标。当`run_web=true`时，运行使用应用上配置的Web目标（Web URL加上浏览器和视口对）。使用`get_run_status`轮询完成。 |
| `create_batch_runs` | 为应用的**所有**用户故事创建故事运行并排队执行。传递`ios_build_id`、`android_build_id`或`run_web=true`中的至少一个。Web运行从应用的Web配置获取其目标。 |
| `get_run_status` | 获取故事运行的当前状态（`pending`、`running`、`completed`、`failed`）。 |
| `get_run_results` | 获取已完成故事运行的验收标准结果。返回每个标准的通过/失败状态及失败原因，加上总体摘要。 |

### 构建（Builds）

| 工具 | 说明 |
| --- | --- |
| `list_builds` | 列出应用的构建。可选择按平台过滤（`android`或`ios`）。构建仅限移动端。Web运行没有构建；它们的URL、浏览器和视口来自应用的设置。 |
| `upload_build` | **尚不支持通过MCP。** 请改用[minitest CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)：`minitest build upload <file>`。 |

### 维护（Maintenance）

| 工具 | 说明 |
| --- | --- |
| `maintenance_check` | 确认已针对提交审查了测试。在进行代码更改后、打开或更新PR之前调用。如果应用启用了维护检查，GitHub Check Run会翻转为✅。 |

### 应用配置（App configuration）

| 工具 | 说明 |
| --- | --- |
| `set_app_test_config` | 为应用配置[配置文件](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles)。在运行时用于向代理提供登录凭据。要设置Mini的记忆（上下文），请改用`set_app_knowledge`。 |
| `set_app_knowledge` | 设置关于应用的额外上下文（测试数据、导航模式、应用特定行为）。创建新的版本化提示；先前版本保留。 |
| `get_app_test_config` | 获取应用的测试配置。返回带有解密凭据的配置，用于测试流程。 |
| `delete_app_test_config` | 删除应用的测试配置。 |

### 文档（Documentation）

这两个工具代理Mintlify托管的公共文档MCP。

| 工具 | 说明 |
| --- | --- |
| `search_docs` | 跨公共miniTest文档的语义搜索。在生成用户故事模板或猜测如何触发运行**之前**调用。优先使用"how to X"查询。 |
| `read_docs` | 读取miniTest文档页面的完整内容。当搜索摘要不够时，在`search_docs`**之后**使用。支持类shell只读查询（`rg`、`grep`、`ls`、`cat`、`head`）。 |

## 运行结果payload

`get_run_results`返回：

```jsonc
{
  "run_id": "<uuid>",
  "status": "pending | running | completed | failed | cancelled",
  "summary": {
    "total":         <int>,
    "passed":        <int>,
    "failed":        <int>,
    "unprocessable": <int>
  },
  "results": [
    {
      "id":                   "<uuid>",
      "criterion_version_id": "<uuid>",
      "platform":             "ios | android | web",
      "browser":              "<str | null>",
      "viewport":             "<str | null>",
      "label":                "<str>",
      "status":               "success | failed | unprocessable | skipped",
      "success":              <bool>,
      "fail_reason":          "<str | null>",
      "rca_prompt":           "<str | null>"
    }
  ]
}
```

对于移动平台，`browser`和`viewport`为`null`，`label`读作`iOS`或`Android`。对于Web，`label`读作`Chrome · Mobile`、`Firefox · Desktop`等。相同的三个字段出现在`get_run_status`返回的`platforms`数组的每个条目上。

MCP响应故意**不**包含视频URL。录像存在于运行内部引用的存储路径；它在仪表板的运行详情页面中渲染。如果您需要从仪表板外部访问视频，请提交请求。

## 认证

MCP服务器使用OAuth（PKCE）。首次调用触发浏览器登录；会话在本地缓存。没有静态API密钥。

---

> **下一章**：[Mini命令参考 →](05-mini-commands.md)
