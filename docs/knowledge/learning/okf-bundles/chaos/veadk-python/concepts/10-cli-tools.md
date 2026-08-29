---
type: Concept
title: CLI 工具集
description: veadk 命令行工具的 16 个子命令全景，覆盖项目创建、初始化、部署、评估、知识库、Web 服务等开发生命周期
tags: [veadk, cli, command-line, click, deploy, eval]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# CLI 工具集

veadk-python 通过 `veadk` 控制台脚本提供命令行界面（CLI），入口为 `veadk.cli.cli:veadk` [F-008]。CLI 基于 Click 框架构建，注册了 16 个子命令，覆盖 Agent 项目从创建、开发、评估到云部署的完整生命周期。prog_name 为 `"Volcengine Agent Development Kit (VeADK)"` [F-074]。

## 命令全景

| 命令 | 模块 | 用途 |
|------|------|------|
| `create` | `cli_create.py` | 生成新 Agent 项目脚手架 |
| `init` | `cli_init.py` | 交互式配置部署参数 |
| `deploy` | `cli_deploy.py` | 部署到火山引擎 FaaS/APIG |
| `eval` | `cli_eval.py` | 运行 Agent 评估 |
| `web` | `cli_web.py` | 启动 Web 服务（含 OAuth2） |
| `prompt` | `cli_prompt.py` | Prompt 管理 |
| `kb` | `cli_kb.py` | 知识库管理 |
| `frontend` | `cli_frontend.py` | 前端管理 |
| `studio` | `cli_frontend.py` | Studio 模式 |
| `pipeline` | `cli_pipeline.py` | 流水线管理 |
| `uploadevalset` | `cli_uploadevalset.py` | 上传评估集 |
| `update` | `cli_update.py` | 更新工具 |
| `clean` | `cli_clean.py` | 清理资源 |
| `agentkit` | `cli_agentkit.py` | AgentKit 管理 |
| `harness` | `cli_harness.py` | Harness 扩展管理 |
| `rl` | `cli_rl.py` | 强化学习命令组 |

来源：[F-075]

## 全局选项

```bash
veadk --version
```

`--version` 输出版本号，prog_name 为 `"Volcengine Agent Development Kit (VeADK)"` [F-074]。

### 云提供商预引导

`_bootstrap_serve_provider` 函数在命令模块加载前执行 [F-076]：

- 检测 `frontend`/`studio` 命令的 `--provider` 参数
- 设置 `AGENTKIT_CLOUD_PROVIDER` 和 `CLOUD_PROVIDER` 环境变量
- 支持 `volcengine`（默认）和 `byteplus` 两个提供商

这使得同一 CLI 可以管理火山引擎国内站和 BytePlus 海外站的资源。

## create：创建项目

`veadk create` 生成新的 Agent 项目文件 [F-077]：

生成的文件包括：
- `.env`：包含 `MODEL_AGENT_API_KEY={ark_api_key}`
- `__init__.py`：Python 包初始化
- `agent.py`：创建名为 `root_agent` 的 Agent 实例

命令会提示用户输入 ARK API Key，或选择稍后配置。

```bash
veadk create
```

## init：初始化部署配置

`veadk init` 交互式收集部署配置 [F-078]：

- FaaS 应用名
- API Gateway 实例名、服务名、上游名
- 部署模式选择：
  - `1`：A2A/MCP Server
  - `2`：VeADK Web/Google ADK Web
- 认证方式：
  - ADK Web 模式：None 或 OAuth2
  - A2A 模式：None 或 API key

## deploy：部署

`veadk deploy` 将 Agent 部署到火山引擎云平台 [F-079]。

参数：

| 参数 | 说明 |
|------|------|
| `--volcengine-access-key` | 火山引擎 AK |
| `--volcengine-secret-key` | 火山引擎 SK |
| `--vefaas-app-name` | FaaS 应用名（必填） |
| `--veapig-instance-name` | APIG 实例名 |
| `--veapig-service-name` | APIG 服务名 |
| `--veapig-upstream-name` | APIG 上游名 |
| `--short-term-memory-backend` | 短期记忆后端（`local`/`mysql`） |
| `--use-adk-web` | 使用 ADK Web 模式（flag） |
| `--auth-method` | 认证方式（`none`/`api-key`/`oauth2`） |
| `--user-pool-name` | VeIdentity 用户池名（OAuth2） |
| `--client-name` | VeIdentity 客户端名（OAuth2） |
| `--path` | 项目路径（默认 `.`） |
| `--iam-role` | IAM 角色 |

部署使用 cookiecutter 模板生成 FaaS 函数和 APIG 配置。

## eval：评估

`veadk eval` 运行 Agent 评估 [F-080]：

```bash
veadk eval \
  --agent-dir . \
  --evalset-file eval_set.json \
  --evaluator adk
```

参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--agent-dir` | `.` | Agent 目录，须导出 `root_agent` |
| `--agent-a2a-url` | — | 远程 A2A 部署 URL |
| `--evalset-file` | （必填） | Google ADK 格式评估集 |
| `--evaluator` | — | `adk` 或 `deepeval` |
| `--judge-model-name` | `doubao-1-5-pro-256k-250115` | 评判模型 |
| `--volcengine-access-key` | — | 火山引擎 AK |
| `--volcengine-secret-key` | — | 火山引擎 SK |

## web：Web 服务

`veadk web` 启动 Web 服务 [F-081]。该命令包含两个猴子补丁：

**_patch_adkwebserver_oauth2**：为 AdkWebServer 添加 OAuth2 认证中间件，集成 VeIdentity User Pool，实现用户登录和令牌验证。

**patch_adkwebserver_disable_openapi**：禁用 OpenAPI 文档端点（`/openapi.json`、`/docs`、`/redoc`），用于生产环境安全加固。

## kb：知识库管理

`veadk kb` 命令（`cli_kb.py`）提供知识库的命令行管理能力，包括创建索引、上传文档、查询等操作。

## prompt：Prompt 管理

`veadk prompt` 命令（`cli_prompt.py`）用于 Prompt 的管理，与 CozeloopPromptManager 等 Prompt 管理器配合使用。

## 其他命令

### pipeline

`veadk pipeline`（`cli_pipeline.py`）管理 CI/CD 流水线。

### uploadevalset

`veadk uploadevalset`（`cli_uploadevalset.py`）将本地评估集上传到云端。

### clean

`veadk clean`（`cli_clean.py`）清理部署产生的临时文件和云资源。

### update

`veadk update`（`cli_update.py`）更新 veadk 工具或相关资源。

### agentkit

`veadk agentkit`（`cli_agentkit.py`）管理 AgentKit 工具和技能。

### harness

`veadk harness`（`cli_harness.py`）管理 Harness 扩展配置，与 `HarnessExtension` 配合使用。

### rl

`veadk rl`（`cli_rl.py`）是强化学习相关的命令组，包含 RL 训练模板（Ark 和 Lightning 两种后端）。模板文件位于 `cli/templates/rl/` 目录。

### frontend / studio

`veadk frontend` 和 `veadk studio` 管理前端界面和 Studio 模式，包含沙箱管理、代码生成、技能创建等子功能。

## 开发生命周期映射

```text
create → init → (开发) → eval → deploy → (监控)
  │         │                    │         │
  │         │                    │         └── web (生产服务)
  │         │                    └── uploadevalset (评估数据上传)
  │         └── kb (知识库准备)
  └── 生成项目脚手架
```

典型工作流：

1. `veadk create` 创建项目
2. 编写 Agent 代码和工具
3. `veadk kb` 准备知识库
4. `veadk eval` 评估 Agent 质量
5. `veadk init` 配置部署参数
6. `veadk deploy` 部署到云端
7. `veadk web` 启动 Web 服务

## 相关概念

- [veadk-python 概览](/concepts/00-overview.md)
- [配置系统](/concepts/04-configuration.md)
- [评估系统](/concepts/09-evaluation.md)
- [高级特性](/concepts/11-advanced.md)
- [快速开始示例](/examples/quickstart.md)
