---
id: "volcengine-arkcli-core-notes"
title: "火山引擎方舟 Ark CLI 核心笔记"
source: "https://www.volcengine.com/docs/82379/2536875?lang=zh"
extracted: "2026-07-07"
product: "火山引擎方舟 Ark CLI（AI原生命令行工具，含Ark Docs MCP配套服务）"
tags: ["火山引擎", "方舟", "Ark CLI", "arkcli", "命令行工具", "AI Agent", "MCP", "AI开发工具", "Claude Code", "Cursor", "Trae"]
---

# 火山引擎方舟 Ark CLI 核心笔记

> **来源**: https://www.volcengine.com/docs/82379/2536875?lang=zh
> **提取日期**: 2026-07-07
> **产品**: 火山引擎方舟 Ark CLI（AI原生命令行工具，负责操作执行层；配套Ark Docs MCP负责知识检索层，构成双层Agent架构）
> **说明**: 控制台页面（https://console.volcengine.com/ark/region:cn-beijing/arkcli）需登录认证无法直接访问，本文档基于官方公开使用指南及控制台内补充链接整理。

---

Ark CLI 是火山方舟平台官方命令行工具，支持在本地终端快速完成认证与资源管理，并可将能力安装到常用 AI Agent 中，通过自然语言触发模型调用、推理接入点管理、内容生成与用量账单查询等操作。

## 快速开始

环境要求： Node.js >= 16

### 1. 安装并登录 Ark CLI

安装 Ark CLI：
```bash
# 1. 通过 NPM 安装
npm install -g @volcengine/ark-cli

# 2. 验证安装
arkcli --version
```

登录 Ark CLI：
```bash
# 登录方式 1：火山 SSO 浏览器登录 (推荐)
arkcli auth login volc-sso

# 登录方式 2：火山 SSO 无浏览器登录 / 远程终端登录
arkcli auth login --no-browser

# 查看登录状态
arkcli auth status

# 装 skill 到你常用的 AI Agent (Claude Code / Cursor / trae / Gemini CLI 等)
arkcli +connect
```

将下方提示词复制给 AI Agent（Claude Code、Codex、Cursor、Trae 等），它会自动完成安装：
"根据下面命令帮我安装 Ark CLI：https://lf3-static.bytednsdoc.com/obj/eden-cn/psjryh/ljhwZthlaukjlkulzlp/intro/volc.md"

注意：如果需要卸载 Skill, 在终端执行命令：arkcli +connect uninstall

### 2. 使用 Ark CLI

配置完成后，重启 AI Agent 即可开始使用。可以直接在 AI Agent 用自然语言说出你的需求，可参考以下示例：

| 你想做什么 | 在 AI Agent 发送 |
|---|---|
| 查询模型 | 帮我看下 doubao / seedream 相关模型 |
| 查询用量 | 看下这个账号今天 / 这周用了多少 token |
| 查询账单 | 帮我查一下最近账单和费用明细 |
| 查询套餐 | 看下当前 Agent Plan / Coding Plan 套餐和 seat 情况 |
| 换 API key | 帮我给测试 profile 换一个可用 key |
| 文本对话 | 用 doubao 模型回答一句：北京今天适合带伞吗 |
| 图片理解 | 帮我描述这张图片里有什么 |
| 文档理解 | 帮我抽取这个 PDF 的重点信息 |
| 生成图片 | 生成一张柴犬在樱花树下奔跑的图片 |
| 生成视频 | 生成一段 5 秒猫跳跃的视频 |
| 部署 Endpoint | 帮我部署一个测试 Endpoint，并告诉我怎么调用 |
| 生成代码 | 给我一段 Python 调 seed 2.0 的代码 |
| 清理资源 | 把刚才创建的测试 Endpoint / gen task / chat response 清理掉 |

## 核心能力

| 领域 | 能力说明 | 命令入口 |
|---|---|---|
| 认证与身份 | 支持登录方舟平台、查看认证状态、查看当前身份、生成与切换 API Key、多 Profile 切换与管理等。 | arkcli auth、arkcli profile |
| 对话与推理 | 多模态对话、多轮对话、流式输出、思考相关参数调节等。 | arkcli +chat |
| 图片/视频生成 | 文生图、图生图、文生视频、图生视频、参考素材生成等。 | arkcli +gen |
| 多模态理解 | 支持对图片、文档、视频、音频等输入进行理解。 | arkcli +understand |
| 模型发现 | 支持基础模型查询、模型搜索、模型详情、可用参数、可用资源查看等。 | arkcli models |
| 推理资源与部署 | 支持创建推理接入点、查询、更新、启动、停止等能力，提供基于指定模型快速部署推理接入点。 | arkcli infer、arkcli +deploy |
| 模型精调 | 支持创建与管理精调任务，覆盖 SFT、LoRA、DPO 及 RL 训练流程；提供数据校验、超参与费用预览，支持产物导出部署等。 | arkcli train |
| 文档检索 | 支持检索方舟文档、按 URL 获取方舟文档内容、分页列出文档页面等。 | arkcli docs |
| 用量统计 | 支持查询推理用量、免费额度或资源包余额、订阅套餐用量、分模型用量明细和团队席位用量。 | arkcli usage |
| 账单与定价 | 支持查询Ark分账账单明细，并按账期、接入点、API Key 或产品维度拆账；支持查询模型价格与套餐价格。 | arkcli billing、arkcli pricing |
| 套餐与席位 | 支持查询、购买和续费 Agent Plan / Coding Plan，查看套餐支持的模型，并管理个人或团队套餐。 | arkcli plans |
| Agent 集成与接入 | 支持自动检测本机 AI Agent，并安装、查看或卸载 Ark CLI skills；提供多语言代码示例等。 | arkcli +connect、arkcli +code-example |

## 命令语法参考

Ark CLI 遵循以下命令结构：

```bash
# 快捷命令
arkcli +<shortcut> [flags]

# 领域命令
arkcli <domain> <resource> <verb> [flags]

# 领域快捷命令
arkcli <domain> +<shortcut> [flags]

# 原始 API 调用
arkcli api <registered-action> --params '{...}'
```

使用 --help 查看任意命令的详细用法：
```bash
arkcli --help
arkcli +chat --help
arkcli models search --help
arkcli train finetune create --help
```

## 全局标志

| Flag | 说明 |
|---|---|
| --api-key <key> | 覆盖默认的 API Key |
| --base-url <url> | 自定义数据面 API Base URL |
| --debug | 输出请求/响应调试信息 |
| --dry-run | 预览模式，仅展示请求元信息，不实际执行 |
| --page-all | 自动拉取所有分页数据 |
| --page-delay | 翻页时的延迟，默认 200 毫秒。 |
| --page-limit <n> | 配合 --page-all 使用，限制最大拉取页数（默认 10） |
| --profile <name> | 指定使用的 Profile |
| --project-name <name> | 覆盖当前 Project |
| --format json | 输出格式指定为 JSON（默认） |
| --region <region> | 覆盖当前 Region |
| --transform <path> | 使用 GJSON 表达式对输出做数据处理 |

最近更新时间：2026.07.03 11:28:43

---

## 补充文档：方舟文档 MCP

> **补充说明**：本章节内容来自控制台内链接（Ark Docs MCP），为火山引擎官方提供的远程知识库服务，作为Ark CLI的配套补充工具。

# 方舟文档 MCP

Ark Docs MCP 是由火山引擎官方提供的远程知识库服务，目前处于公测阶段。通过标准化配置，开发者可将火山引擎大模型平台的最新技术文档、API规范及代码示例无缝集成至支持MCP的AI编程助手（如OpenClaw、Trae、Claude Code、Cursor、Windsurf、VS Code等）。

## 核心优势
1. 准确的代码生成：AI可直接读取火山引擎最新的OpenAPI规范和官方SDK示例，避免因使用过时参数或虚构SDK导致的调用错误
2. 沉浸式开发体验：在IDE对话上下文中直接完成问题排查、文档检索和接口查询，减少工具间切换
3. 数据实时同步：实时获取方舟文档更新、模型及接口信息，确保AI助手使用最新数据

## 一键安装
支持一键安装到：TRAE CN（中国版）、TRAE（国际版）、VS Code、Cursor、Windsurf

OpenClaw等AI Agent安装配置：
```json
{
  "mcpServers": {
    "ark-docs-mcp": {
      "url": "https://sd6j8o9hu8aldae0o6es0.apigateway-cn-beijing.volceapi.com/mcp"
    }
  }
}
```

## 四大核心场景
1. **技术文档检索与排障**：调用ark_search_docs语义检索，ark_fetch_doc获取完整页面。示例："火山引擎Ark平台支持哪些流式输出的模型？"
2. **规范化API调用与代码生成**：调用ark_list_apis、ark_get_spec获取JSON Schema，ark_search_examples获取官方示例。示例："使用Python编写调用DeepSeek模型的流式返回代码"
3. **模型信息查询**：调用ark_list_models、ark_get_model获取模型元数据和计费策略。示例："doubao seed 2.0模型的最大上下文窗口是多少？"
4. **高级技能发现**：调用ark_list_skills查询最佳实践模板。示例："Ark平台提供了哪些代码Review的提示词模板？"

## MCP底层工具列表
- **ark_search_docs**：语义检索方舟技术文档
- **ark_fetch_doc**：获取完整文档页面内容
- **ark_list_apis**：列出可用API接口
- **ark_get_spec**：获取API的JSON Schema规范
- **ark_search_examples**：搜索官方代码示例
- **ark_list_models**：列出可用模型
- **ark_get_model**：获取模型详细信息（元数据、计费策略等）
- **ark_list_skills**：查询最佳实践模板/技能

## 提示词编写建议
- 指定数据来源："请使用已配置的ark docs mcp检索以下信息..."
- 强调遵循规范："在生成代码前，请务必使用ark docs mcp先查阅最新的OpenAPI Spec规范"
- 要求参考示例："请在工具中搜索Go语言的官方Example"
