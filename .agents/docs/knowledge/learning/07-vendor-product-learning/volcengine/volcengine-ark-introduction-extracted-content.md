---
id: "volcengine-ark-introduction-extracted-content"
title: "火山引擎方舟入门文档原始内容提取"
source: "https://console.volcengine.com/ark/region:cn-beijing/docs/82379/1099455?lang=zh"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/volcengine-ark-introduction-extracted-content.toml"
extracted: "2026-07-07"
updated: "2026-06-23"
product: "火山引擎方舟/Volcengine Ark"
type: "raw-content-extraction"
tags: ["火山引擎", "火山方舟", "大模型平台", "原始内容", "SDK示例", "Doubao"]
---
# 火山引擎方舟入门

## 目录

- [快速入门](#快速入门)
- [模型浏览](#模型浏览)
- [基础使用](#基础使用)
- [进阶使用](#进阶使用)
- [导航链接](#导航链接)

---

## 快速入门

完成首次 API 调用，请参见 [快速入门](https://console.volcengine.com/docs/82379/1399008)

### Python SDK

```python
import os

from volcenginesdkarkruntime import Ark

client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    # Get API Key: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.getenv('ARK_API_KEY'),
)

response = client.responses.create(
    model="doubao-seed-2-1-pro-260628",
    input="hello", # Replace with your prompt
    # thinking={"type": "disabled"}, # Manually disable deep thinking
)

print(response)
```

### Curl

```bash
# Get API Key: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
curl https://ark.cn-beijing.volces.com/api/v3/responses \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2-1-pro-260628",
    "input": "hello"
  }'
```

### Go SDK

```go
package main

import (
    "context"
    "fmt"
    "os"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime/model/responses"
)

func main() {
    client := arkruntime.NewClientWithApiKey(
        // Get API Key: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
        os.Getenv("ARK_API_KEY"),
        arkruntime.WithBaseUrl("https://ark.cn-beijing.volces.com/api/v3"),
    )
    ctx := context.Background()
    resp, err := client.CreateResponses(ctx, &responses.ResponsesRequest{
        Model: "doubao-seed-2-1-pro-260628",
        Input: &responses.ResponsesInput{Union: &responses.ResponsesInput_StringValue{StringValue: "hello"}}, // Replace with your prompt
        // Thinking: &responses.ResponsesThinking{Type: responses.ThinkingType_disabled.Enum()}, // Manually disable deep thinking
    })
    if err != nil {
        fmt.Printf("response error: %v\n", err)
        return
    }
    fmt.Println(resp)
}
```

### Java SDK

```java
package com.ark.sample;

import com.volcengine.ark.runtime.service.ArkService;
import com.volcengine.ark.runtime.model.responses.request.*;
import com.volcengine.ark.runtime.model.responses.response.ResponseObject;

public class demo {
    public static void main(String[] args) {
        // Get API Key: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
        String apiKey = System.getenv("ARK_API_KEY");
        // The base URL for model invocation
        ArkService arkService = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.cn-beijing.volces.com/api/v3").build();
        CreateResponsesRequest request = CreateResponsesRequest.builder()
            .model("doubao-seed-2-1-pro-260628")
            .input(ResponsesInput.builder().stringValue("hello").build()) // Replace with your prompt
            // .thinking(ResponsesThinking.builder().type(ResponsesConstants.THINKING_TYPE_DISABLED).build()) // Manually disable deep thinking
            .build();
        ResponseObject resp = arkService.createResponse(request);
        System.out.println(resp);
        arkService.shutdownExecutor();
    }
}
```

### OpenAI SDK

```python
import os

from openai import OpenAI

client = OpenAI(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    # Get API Key: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.getenv('ARK_API_KEY'),
)

response = client.responses.create(
    model="doubao-seed-2-1-pro-260628",
    input="hello", # Replace with your prompt
    extra_body={
        # "thinking": {"type": "disabled"}, # Manually disable deep thinking
    },
)

print(response)
```

---

## 模型浏览

完整模型列表：[模型列表](https://console.volcengine.com/docs/82379/1330310)

![](https://aka.doubaocdn.com/s/dewC1wjUCU)

### Doubao Seed 2.1

**豆包旗舰级 Agent 通用模型**

面向生产级任务，全面升级编程、智能体与多模态能力

![](https://aka.doubaocdn.com/s/98921wjUCU)

### Doubao Seedance 2.0

**豆包最强视频生成模型**

极致拟真的视听稳定，赋予创作者如同导演般的掌控权

![](https://aka.doubaocdn.com/s/ZTHY1wjUCU)

### Doubao Seedream 5.0

**豆包最强图片生成模型**

搭载联网检索，增强知识广度、参考一致性及专业场景生成质量

---

## 基础使用

了解模型使用方法、限制以及常见场景的示例代码。

| 功能 | 说明 |
|------|------|
| **深度思考** | 先思考再回答，质量显著提升 |
| **图片理解** | 接收图片，根据图片信息回复 |
| **视频理解** | 接收视频，根据视频信息回复 |
| **文档理解** | 接收 PDF，根据文档信息回复 |
| **视频生成** | 生成高清流畅的影视级视频 |
| **图片生成** | 基于图文，生成高质量图片 |
| **联网搜索** | 联网获取实时知识 |
| **函数调用** | 调用自定义工具，增强模型能力 |

---

## 进阶使用

了解如何拓展模型能力、提升性能、降低成本

| 功能 | 说明 |
|------|------|
| **续写模式** | 预填部分 assistant 消息内容，引导和控制模型输出 |
| **视觉定位** | 在图片中找到对应的目标，并返回目标的坐标 |
| **文件输入** | 使用 File API 上传并预处理视频、图片、PDF |
| **3D 生成** | 快速生成具备多边形面片与 PBR 材质的高精度 3D 资产 |
| **批量推理** | 大幅提升吞吐，降低成本，适合无需即时响应的任务 |
| **上下文缓存** | 缓存固定上下文，减少重复计算开销，降低成本 |
| **云部署 MCP** | 调用各类垂直领域 MCP 工具，增强模型能力 |
| **GUI 任务处理** | 在计算机等真实 GUI 环境中完成自动化任务 |

---

## 导航链接

- [快速入门](https://console.volcengine.com/ark/region:cn-beijing/docs/82379/1399008?lang=zh)
- [下一篇](https://console.volcengine.com/ark/region:cn-beijing/docs/82379/1399008?lang=zh)
