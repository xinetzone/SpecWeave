---
id: cli-module
title: CLI命令行工具参考
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# CLI命令行工具参考

## 概述

VeADK 提供了完整的命令行工具 `veadk`，用于项目初始化、创建、部署、Web 服务启动、知识库管理、评估、Harness 部署等全生命周期管理。CLI 基于 Click 框架构建，提供一致的命令行体验。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli.py)

---

## veadk命令总览

`veadk` 是命令行入口，通过子命令方式组织功能。执行 `veadk --help` 可查看所有可用命令。

### 命令组列表

| 命令 | 用途 | 源码位置 |
|------|------|----------|
| `init` | 初始化可部署到火山引擎 FaaS 的新项目 | [cli_init.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_init.py) |
| `create` | 创建本地 VeADK Agent 项目 | [cli_create.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_create.py) |
| `deploy` | 部署项目到火山引擎 FaaS | [cli_deploy.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_deploy.py) |
| `update` | 更新已部署云应用的函数代码 | [cli_update.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_update.py) |
| `clean` | 删除云端 VeFaaS 应用 | [cli_clean.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_clean.py) |
| `web` | 启动 ADK Web 服务器（支持内存集成） | [cli_web.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_web.py) |
| `frontend` | 启动 A2UI Web UI + Agent API 服务器 | [cli_frontend.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_frontend.py) |
| `studio` | 启动 VeADK Studio 管理界面 | [cli_frontend.py#L803-L869](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_frontend.py#L803-L869) |
| `kb` | 知识库管理（添加文件等） | [cli_kb.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_kb.py) |
| `eval` | 使用评估数据集评估 Agent | [cli_eval.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_eval.py) |
| `harness` | Harness 服务器创建、配置、部署 | [cli_harness.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_harness.py) |
| `agentkit` | AgentKit 兼容命令（invoke 等） | [cli_agentkit.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_agentkit.py) |
| `pipeline` | 集成火山引擎 Code Pipeline 实现 CI/CD | [cli_pipeline.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_pipeline.py) |
| `prompt` | 使用 PromptPilot 优化系统提示词 | [cli_prompt.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_prompt.py) |
| `rl` | RL 强化学习脚手架命令组 | [cli_rl.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_rl.py) |
| `uploadevalset` | 上传数据集到 CozeLoop 评估集 | [cli_uploadevalset.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_uploadevalset.py) |

> 命令注册位置：[cli.py#L77-L92](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli.py#L77-L92)

---

## 子命令详解

### 1. init - 初始化云部署项目

初始化一个可部署到火山引擎 FaaS 的新项目，通过交互式引导收集配置信息。

```bash
veadk init [--vefaas-template-type template|web_template]
```

**主要参数：**
- `--vefaas-template-type`: 模板类型
  - `template`（默认）：标准 Agent 模板（weather-reporter 示例）
  - `web_template`: Web 应用模板（simple-blog 示例）

**交互式配置项：**
- Volcengine FaaS 应用名称
- API Gateway 实例/服务/上游名称
- 部署模式：A2A/MCP Server 或 VeADK Web
- 认证方式：None / API Key / OAuth2
- VeIdentity 用户池/客户端名称（OAuth2 时配置）

**生成项目结构：**
```
project-name/
├── src/
│   └── agent/
│       └── agent.py      # Agent 定义
├── deploy.py             # 部署脚本
├── config.yaml.example   # 配置示例
└── requirements.txt
```

> 源码位置：[cli_init.py#L123-L214](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_init.py#L123-L214)

---

### 2. create - 创建本地 Agent 项目

创建一个简单的本地 Agent 项目，包含 `.env`、`__init__.py` 和 `agent.py`。

```bash
veadk create [AGENT_NAME] [--ark-api-key KEY]
```

**主要参数：**
- `AGENT_NAME`: Agent 名称（目录名），不能包含 `-`（用 `_` 替代）
- `--ark-api-key`: ARK API Key，如不提供将交互式询问

**生成文件：**
```
agent_name/
├── .env              # MODEL_AGENT_API_KEY=xxx
├── __init__.py       # from . import agent
└── agent.py          # root_agent = Agent(...)
```

> 源码位置：[cli_create.py#L116-L168](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_create.py#L116-L168)

---

### 3. deploy - 部署到 FaaS

将本地项目部署到火山引擎函数计算 VeFaaS。

```bash
veadk deploy --vefaas-app-name NAME [OPTIONS]
```

**主要参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--vefaas-app-name` | VeFaaS 应用名称（必填） | - |
| `--volcengine-access-key` | 火山引擎 Access Key | 环境变量 `VOLCENGINE_ACCESS_KEY` |
| `--volcengine-secret-key` | 火山引擎 Secret Key | 环境变量 `VOLCENGINE_SECRET_KEY` |
| `--veapig-instance-name` | APIG 实例名 | "" |
| `--veapig-service-name` | APIG 服务名 | "" |
| `--veapig-upstream-name` | APIG 上游名 | "" |
| `--short-term-memory-backend` | 短期记忆后端 | `local` / `mysql` |
| `--use-adk-web` | 启用 ADK Web 界面 | False |
| `--auth-method` | 认证方式 | `none` / `api-key` / `oauth2` |
| `--user-pool-name` | VeIdentity 用户池名 | "" |
| `--client-name` | VeIdentity 客户端名 | "" |
| `--path` | 本地项目路径 | `.` |
| `--iam-role` | VeFaaS 函数 IAM 角色 | None |

> 源码位置：[cli_deploy.py#L71-L233](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_deploy.py#L71-L233)

---

### 4. update - 更新云函数代码

更新已部署应用的函数代码，不改变端点和其他资源。

```bash
veadk update --vefaas-app-name NAME [OPTIONS]
```

**主要参数：**
- `--vefaas-app-name`: 要更新的云应用名称（必填）
- `--volcengine-access-key`: Access Key
- `--volcengine-secret-key`: Secret Key
- `--path`: 本地代码路径，默认 `.`

> 源码位置：[cli_update.py#L44-L108](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_update.py#L44-L108)

---

### 5. clean - 删除云应用

清理并删除指定的 VeFaaS 应用，删除前会要求用户确认。

```bash
veadk clean --vefaas-app-name NAME [OPTIONS]
```

**主要参数：**
- `--vefaas-app-name`: 要删除的 VeFaaS 应用名称（必填）
- `--volcengine-access-key`: Access Key
- `--volcengine-secret-key`: Secret Key

> 源码位置：[cli_clean.py#L37-L87](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_clean.py#L37-L87)

---

### 6. web - 启动 Web 服务器

启动集成 VeADK Agent 和内存功能的 Web 服务器，基于 Google ADK Web Server。

```bash
veadk web [OPTIONS] [-- ADK_WEB_OPTIONS...]
```

**主要参数：**
- `--oauth2-user-pool`: VeIdentity 用户池名称（启用 OAuth2）
- `--oauth2-user-pool-client`: VeIdentity 客户端名称
- `--oauth2-redirect-uri`: OAuth2 回调 URI，默认 `http://{host}:{port}/oauth2/callback`

**支持传递给 ADK Web 的额外参数：**
- `--host`: 监听地址，默认 `127.0.0.1`
- `--port`: 监听端口，默认 `8000`
- `--log_level`: 日志级别，默认 `ERROR`

**功能特性：**
- 自动检测 VeADK Agent 类型（普通 Agent / 工作流 Agent）
- 自动配置短期记忆和长期记忆服务
- 支持 OAuth2 认证中间件
- 禁用 OpenAPI 文档端点（安全考虑）

> 源码位置：[cli_web.py#L102-L246](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_web.py#L102-L246)

---

### 7. frontend - 启动 A2UI Web UI

启动 A2UI 前端界面与 Agent API 服务器的一体化服务。

```bash
veadk frontend [OPTIONS]
```

**主要参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--agents-dir` | Agent 应用目录 | `.` |
| `--frontend-dir` | 覆盖内置 React UI 目录 | 内置 `veadk/webui` |
| `--site-logo` | Studio Logo（路径或URL） | 环境变量 `VEADK_SITE_LOGO` |
| `--site-title` | Studio 标题（最多6字符） | 环境变量 `VEADK_SITE_TITLE` |
| `--host` | 监听地址 | `127.0.0.1` |
| `--port` | 监听端口 | `8000` |
| `--provider` | 云服务商 | `volcengine` / `byteplus` |
| `--dev` | 加载本地 Agent（而非云端运行时） | False |
| `--vite` | Vite 热重载模式（仅 API，CORS 允许） | False |
| `--oauth2-user-pool` | VeIdentity 用户池名 | None |
| `--oauth2-user-pool-client` | VeIdentity 客户端名 | None |
| `--auth-mode` | 认证模式 | `frontend` / `gateway` |
| `--open/--no-open` | 启动后自动打开浏览器 | False |

**运行模式：**
- **默认模式**：同时服务 API 和内置 React UI（单进程，无跨域问题）
- `--vite` 模式：仅服务 API，允许 Vite 开发服务器跨域（`http://localhost:5173`）
- `--dev` 模式：Agent 选择器从本地 Agent 加载（而非云端运行时）

> 源码位置：[cli_frontend.py#L739-L800](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_frontend.py#L739-L800)

---

### 8. studio - 启动 VeADK Studio

启动 VeADK Studio 管理界面，专注于 Agent 添加和管理功能。与 `frontend` 是同一服务器，但 UI 功能裁剪后默认进入添加 Agent 页面。

```bash
veadk studio [OPTIONS]
```

参数与 `veadk frontend` 相同。Studio 模式下聊天/搜索/技能中心/历史记录功能被隐藏。

> 源码位置：[cli_frontend.py#L803-L869](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_frontend.py#L803-L869)

---

### 9. kb - 知识库管理

知识库管理命令组，目前包含 `add` 子命令用于添加文件到知识库。

```bash
veadk kb add --backend BACKEND --path PATH [OPTIONS]
```

**子命令 `add` 参数：**
| 参数 | 说明 | 必填 |
|------|------|------|
| `--backend` | 知识库后端类型 | ✅ |
| | `local`: 本地 SQLite 存储 | |
| | `opensearch`: OpenSearch 搜索引擎 | |
| | `viking`: 火山引擎 Viking 向量数据库 | |
| | `redis`: Redis 向量搜索 | |
| `--path` | 知识文件或目录路径 | ✅ |
| `--app_name` | 应用名称（用于隔离数据） | "" |
| `--index` | 知识库索引名称 | "" |

**示例：**
```bash
# 添加单个文件
veadk kb add --backend local --path ./docs/intro.md

# 添加整个目录
veadk kb add --backend viking --app_name my_app --index kb1 --path ./docs/
```

> 源码位置：[cli_kb.py#L21-L110](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_kb.py#L21-L110)

---

### 10. eval - 评估 Agent

使用评估数据集对 Agent 进行评估，支持本地评估和远程 A2A 评估两种模式。

```bash
veadk eval --evalset-file FILE [OPTIONS]
```

**主要参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--evalset-file` | Google ADK 格式评估集文件路径（必填） | - |
| `--agent-dir` | 待评估 Agent 本地目录（需含 `agent.py` 导出 `root_agent`） | `.` |
| `--agent-a2a-url` | 待评估 Agent 的 A2A 部署 URL | None |
| `--evaluator` | 评估器类型 | `adk` / `deepeval` |
| `--judge-model-name` | DeepEval 评判模型名称 | `doubao-1-5-pro-256k-250115` |
| `--volcengine-access-key` | 火山引擎 Access Key | 环境变量 |
| `--volcengine-secret-key` | 火山引擎 Secret Key | 环境变量 |

**评估模式：**
- **本地评估**：从 `--agent-dir` 加载 Agent 源码
- **远程评估**：通过 `--agent-a2a-url` 连接已部署的 A2A Agent
- 两者同时提供时，`--agent-a2a-url` 优先

**评估器：**
- `adk`: Google ADK 评估器，使用内置指标
- `deepeval`: DeepEval 评估器，支持 GEval 和 ToolCorrectnessMetric

> 源码位置：[cli_eval.py#L58-L215](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_eval.py#L58-L215)

---

### 11. harness - Harness 服务器管理

Harness 是云原生 Agent 运行时，支持通过 `harness.yaml` 配置文件进行声明式部署。

```bash
veadk harness SUBCOMMAND [OPTIONS]
```

**子命令：**

| 子命令 | 用途 |
|--------|------|
| `create <dir>` | 创建可部署的 Harness 目录脚手架 |
| `add` | 向 `harness.yaml` 写入 Agent 参数 |
| `show` | 显示已配置的 Agent 参数和可覆盖项 |
| `deploy` | 将 Harness 部署为 AgentKit 运行时（云端构建，无本地 Docker） |
| `invoke` | 调用已部署的 Harness 并输出结果 |

**harness create 示例：**
```bash
veadk harness create my-harness
cd my-harness
veadk harness add \
  --harness-name my-harness \
  --model-name doubao-seed-1-6-250615 \
  --tools web_search \
  --system-prompt "You are a helpful assistant."
cp .env.example .env  # 填写 VOLCENGINE_ACCESS_KEY/SECRET_KEY
veadk harness deploy
```

**harness invoke 示例：**
```bash
veadk harness invoke --name my-harness --message "你好"
veadk harness invoke -m "今天天气如何" --tools web_search
```

> 源码位置：[cli_harness.py#L293-L963](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_harness.py#L293-L963)

---

### 12. agentkit - AgentKit 兼容命令

AgentKit 兼容命令组，重新导出 AgentKit CLI 的子命令，并增强了 `invoke` 命令以支持 HarnessApp 运行时。

```bash
veadk agentkit SUBCOMMAND [OPTIONS]
veadk agentkit invoke [MESSAGE] [OPTIONS]
```

**invoke 主要参数：**
- `--config-file`: 配置文件路径
- `--payload/-p`: JSON 请求体
- `--headers/-h`: JSON 请求头
- `--runtime-id/-r`: 运行时 ID
- `--endpoint/-e`: 端点 URL
- `--region`: 区域
- `--a2a`: A2A 模式
- `--show-reasoning`: 显示推理过程
- `--raw`: 原始输出
- `--apikey/-ak`: API Key
- `--harness`: Harness 名称（用于 HarnessApp 运行时）
- `--model-id`: 一次性模型覆盖
- `--tools`: 逗号分隔的一次性工具覆盖
- `--skills`: 逗号分隔的一次性技能覆盖
- `--system-prompt`: 一次性系统提示词覆盖
- `--user-id`: 用户 ID
- `--session-id`: 会话 ID

> 源码位置：[cli_agentkit.py#L29-L185](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_agentkit.py#L29-L185)

---

### 13. pipeline - CI/CD 流水线集成

集成火山引擎 Code Pipeline，实现代码推送时自动构建、容器化和部署。

```bash
veadk pipeline --github-url URL --github-branch BRANCH --github-token TOKEN [OPTIONS]
```

**主要参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--veadk-version` | VeADK 基础镜像版本 | 当前 VERSION |
| `--github-url` | GitHub 仓库 URL（必填） | - |
| `--github-branch` | GitHub 分支名（必填） | - |
| `--github-token` | GitHub Token（必填） | - |
| `--volcengine-access-key` | Access Key | 环境变量 |
| `--volcengine-secret-key` | Secret Key | 环境变量 |
| `--region` | 火山引擎区域 | `cn-beijing` |
| `--cr-instance-name` | 容器镜像服务实例名 | `veadk-user-instance` |
| `--cr-namespace-name` | CR 命名空间 | `veadk-user-namespace` |
| `--cr-repo-name` | CR 仓库名 | `veadk-user-repo` |
| `--vefaas-function-id` | 已有 VeFaaS 函数 ID | 自动创建 |

**流水线工作流：**
1. 代码推送到 GitHub 触发流水线
2. 自动拉取指定分支源码
3. 使用指定 VeADK 基础镜像构建 Docker 镜像
4. 推送镜像到火山引擎容器镜像服务
5. 更新 VeFaaS 函数使用新镜像

> 源码位置：[cli_pipeline.py#L138-L286](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_pipeline.py#L138-L286)

---

### 14. prompt - 提示词优化

使用火山引擎 PromptPilot 服务优化 Agent 系统提示词。

```bash
veadk prompt [OPTIONS]
```

**主要参数：**
- `--path`: Agent 文件路径，需包含全局变量 `agent=...`，默认 `.`
- `--feedback`: 优化建议反馈
- `--api-key`: PromptPilot API Key
- `--workspace-id`: PromptPilot 工作区 ID（必填）
- `--model-name`: 用于优化的模型名称，默认 `doubao-1.5-pro-32k-250115`

> 源码位置：[cli_prompt.py#L30-L86](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_prompt.py#L30-L86)

---

### 15. rl - 强化学习命令组

RL（强化学习）相关命令，目前支持初始化 RL 脚手架项目。

```bash
veadk rl init --platform PLATFORM --workspace NAME [--overwrite]
```

**子命令 `init` 参数：**
- `--platform/-p`: 平台类型（必填）
  - `ark`: 火山引擎 Ark 平台
  - `lightning`: Lightning 平台
- `--workspace/-w`: 目标工作区目录名（必填）
- `--overwrite/-f`: 强制覆盖已存在目录

**示例：**
```bash
veadk rl init -p ark -w veadk_rl_ark_project
veadk rl init -p lightning -w veadk_rl_lightning_project
```

> 源码位置：[cli_rl.py#L29-L106](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_rl.py#L29-L106)

---

### 16. uploadevalset - 上传评估数据集

将评估数据集项从 JSON 文件上传到 CozeLoop 评估集。

```bash
veadk uploadevalset --file FILE [OPTIONS]
```

**主要参数：**
- `--file`: 包含数据集项的 JSON 文件路径（必填）
- `--cozeloop-workspace-id`: CozeLoop 工作区 ID
- `--cozeloop-evalset-id`: CozeLoop 评估集 ID
- `--cozeloop-api-key`: CozeLoop API Key（或环境变量 `COZELOOP_API_KEY`）

**环境变量回退：**
- `OBSERVABILITY_OPENTELEMETRY_COZELOOP_SERVICE_NAME` → workspace_id
- `OBSERVABILITY_OPENTELEMETRY_COZELOOP_EVALSET_ID` → evalset_id
- `OBSERVABILITY_OPENTELEMETRY_COZELOOP_API_KEY` → api_key

> 源码位置：[cli_uploadevalset.py#L31-L140](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli_uploadevalset.py#L31-L140)

---

## CLI配置与环境变量

### 环境变量

CLI 命令通过环境变量进行配置，常用环境变量包括：

| 环境变量 | 用途 | 相关命令 |
|----------|------|----------|
| `VOLCENGINE_ACCESS_KEY` | 火山引擎 Access Key | deploy, update, clean, pipeline 等 |
| `VOLCENGINE_SECRET_KEY` | 火山引擎 Secret Key | deploy, update, clean, pipeline 等 |
| `VOLCENGINE_REGION` | 火山引擎区域，默认 `cn-beijing` | deploy, pipeline |
| `MODEL_AGENT_API_KEY` | Agent 模型 API Key | web, frontend |
| `AGENTKIT_CLOUD_PROVIDER` | 云服务商 (`volcengine`/`byteplus`) | frontend, studio |
| `VEADK_SITE_LOGO` | Studio Logo | frontend, studio |
| `VEADK_SITE_TITLE` | Studio 标题 | frontend, studio |
| `VEADK_FRONTEND_AUTH_MODE` | 认证模式 (`frontend`/`gateway`) | frontend, studio |
| `HARNESS_URL` | Harness 默认 URL | agentkit invoke |
| `HARNESS_KEY` | Harness 默认 API Key | agentkit invoke |
| `COZELOOP_API_KEY` | CozeLoop API Key | uploadevalset |

### .env 文件支持

`veadk web` 和 `veadk frontend` 命令会自动加载当前目录或父目录中的 `.env` 文件（使用 python-dotenv）。

### 版本信息

执行 `veadk --version` 可查看当前 VeADK 版本，版本号定义在 `veadk/version.py`。

> 源码位置：[cli.py#L65-L67](file:///d:/AI/.chaos/libs/veadk-python/veadk/cli/cli.py#L65-L67)

---

## 快速开始示例

```bash
# 1. 创建本地 Agent 项目
veadk create my_agent
cd my_agent

# 2. 编辑 agent.py 配置 Agent

# 3. 本地 Web 调试
veadk web --port 8000

# 4. 或使用 A2UI 界面
veadk frontend --open

# 5. 初始化云部署项目
veadk init

# 6. 部署到云端
veadk deploy --vefaas-app-name my-agent-app

# 7. 评估 Agent
veadk eval --evalset-file eval.json --evaluator deepeval
```
