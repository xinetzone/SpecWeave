---
id: cloud-module
title: 云部署集成
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 云部署集成

## 概述

VeADK 提供了与火山引擎（Volcengine）云服务的完整集成，支持一键部署 Agent 到云端。集成模块覆盖了函数计算、容器镜像、API 网关、对象存储、日志服务、身份认证、评估服务、向量数据库等核心云服务，实现从代码到生产环境的全自动化部署流程。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/)

---

## 云服务集成模块总览

| 模块 | 目录 | 功能 |
|------|------|------|
| VeFaaS | `ve_faas/` | 函数计算部署与管理 |
| VeCR | `ve_cr/` | 容器镜像服务（构建、推送） |
| VeAPIG | `ve_apig/` | API 网关配置 |
| VeTOS | `ve_tos/` | 对象存储服务 |
| VeTLS | `ve_tls/` | 日志服务 |
| VeIdentity | `ve_identity/` | 身份认证与 OAuth2 |
| AgentKit | `agentkit/` | AgentKit 平台集成（评估等） |
| VeCodePipeline | `ve_code_pipeline/` | CI/CD 流水线集成 |
| VeCozeloop | `ve_cozeloop/` | CozeLoop 可观测性集成 |
| VePromptPilot | `ve_prompt_pilot/` | Prompt 优化服务 |
| VeVikingDBMemory | `ve_viking_db_memory/` | VikingDB 向量数据库记忆存储 |

---

## VeFaaS - 函数计算部署

`VeFaaS` 类封装了火山引擎函数计算服务的操作，支持函数创建、代码上传、应用管理等功能，是 VeADK 云部署的核心模块。

> 源码位置：[ve_faas/ve_faas.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py)

### 类定义

```python
class VeFaaS:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        session_token: str = "",
        region: str = "cn-beijing",
        project_name: str = "default",
    ):
```

### 初始化参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `access_key` | 火山引擎 Access Key | - |
| `secret_key` | 火山引擎 Secret Key | - |
| `session_token` | STS 临时凭证 Token | "" |
| `region` | 部署区域 | `cn-beijing` |
| `project_name` | 项目名称 | `default` |

### 核心功能

**1. 创建函数 (`_create_function`)**
- 运行时：`native-python3.12/v1`
- 内存：2048 MB
- 超时：1800 秒（30分钟）
- 启动命令：`./run.sh`
- 自动注入环境变量（从 `veadk.config.veadk_environments`）
- 支持 IAM 角色配置

```python
def _create_function(self, function_name: str, path: str):
    envs = []
    for key, value in veadk.config.veadk_environments.items():
        envs.append(EnvForCreateFunctionInput(key=key, value=value))

    res = self.client.create_function(
        volcenginesdkvefaas.CreateFunctionRequest(
            command="./run.sh",
            name=function_name,
            runtime="native-python3.12/v1",
            request_timeout=1800,
            envs=envs,
            memory_mb=2048,
            role=getenv("IAM_ROLE", None, allow_false_values=True),
        )
    )
```

**2. 代码上传 (`_upload_and_mount_code`)**
- 将本地项目目录打包为 ZIP
- 获取上传临时地址
- PUT 上传到 TOS 临时桶
- 调用回调挂载代码到函数实例

```python
def _upload_and_mount_code(self, function_id: str, path: str):
    code_zip_data, code_zip_size, error = zip_and_encode_folder(path)
    response = self.client.get_code_upload_address(...)
    # PUT upload to TOS
    requests.put(url=upload_url, data=code_zip_data, headers={"Content-Type": "application/zip"})
    # Mount code
    signed_request(ak=self.ak, sk=self.sk, target="CodeUploadCallback", body={"FunctionId": function_id}, ...)
```

**3. 创建应用 (`_create_application`)**
- 创建 VeFaaS Application（包含函数、网关配置）
- 自动配置 APIG 网关
- 支持 API Key 认证开关
- 支持 MCP Session

> 源码位置：[ve_faas.py#L52-L200](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py#L52-L200)

### 项目模板

VeFaaS 集成提供了两种 Cookiecutter 项目模板：

1. **template** - 标准 Agent 模板
   - 位置：`ve_faas/template/`
   - 包含：`src/agent/agent.py`、`app.py`、`deploy.py`、`run.sh`、`config.yaml.example`
   - 示例：weather-reporter（天气查询 Agent）

2. **web_template** - Web 应用模板
   - 位置：`ve_faas/web_template/`
   - 包含：Flask Web 应用、静态文件、模板、Dockerfile
   - 示例：simple-blog（简单博客）

> 模板位置：[ve_faas/template/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/template/)

---

## VeCR - 容器镜像服务

`VeCR` 类封装了火山引擎容器镜像服务（Container Registry），支持镜像仓库实例创建、命名空间管理、仓库管理等操作。

> 源码位置：[ve_cr/ve_cr.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_cr/ve_cr.py)

### 类定义

```python
class VeCR:
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-beijing"):
```

### 支持区域

- `cn-beijing`（北京）
- `cn-guangzhou`（广州）
- `cn-shanghai`（上海）

### 核心功能

**1. 创建实例 (`_create_instance`)**
- 检查实例是否存在
- 不存在则创建
- 等待实例状态变为 `Running`
- 自动添加 `provider: veadk` 标签

```python
def _create_instance(self, instance_name: str = DEFAULT_CR_INSTANCE_NAME) -> str:
    status = self._check_instance(instance_name)
    if status != "NONEXIST":
        return instance_name
    response = ve_request(..., action="CreateRegistry", service="cr", ...)
    while True:
        status = self._check_instance(instance_name)
        if status == "Running":
            break
        time.sleep(30)
```

**2. 创建命名空间 (`_create_namespace`)**
- 在指定实例下创建命名空间

**3. 检查实例状态 (`_check_instance`)**
- 返回状态：`NONEXIST`、`Running`、`Failed`、`Starting` 等

### 默认配置

| 配置项 | 默认值 | 环境变量 |
|--------|--------|----------|
| 实例名 | `veadk-user-instance` | - |
| 命名空间 | `veadk-user-namespace` | - |
| 仓库名 | `veadk-user-repo` | - |
| API 版本 | `2022-05-12` | - |

> 源码位置：[ve_cr.py#L28-L150](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_cr/ve_cr.py#L28-L150)

---

## VeAPIG - API 网关配置

`APIGateway` 类封装了火山引擎 API 网关服务，支持网关实例、服务、上游、路由的创建与管理。

> 源码位置：[ve_apig/ve_apig.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_apig/ve_apig.py)

### 类定义

```python
class APIGateway:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str = "cn-beijing",
        session_token: str = "",
    ):
```

### 核心功能

**1. 网关管理**
- `list_gateways()`: 列出所有网关
- `find_serverless_gateway()`: 查找可用的 Serverless 网关（优先 Running 状态）
- `create_serverless_gateway()`: 创建 Serverless 网关
  - 规格：2 副本，1c2g 实例，small_1 CLB
  - 公网访问，按流量计费

```python
def create_serverless_gateway(self, instance_name: str) -> str:
    request = CreateGatewayRequest(
        name=instance_name,
        region=self.region,
        type="serverless",
        resource_spec=ResourceSpecForCreateGatewayInput(
            replicas=2,
            instance_spec_code="1c2g",
            clb_spec_code="small_1",
            public_network_billing_type="traffic",
            network_type={"EnablePublicNetwork": True, "EnablePrivateNetwork": False},
        ),
    )
```

**2. 服务管理**
- `create_gateway_service()`: 创建网关服务（域名）
  - 支持 HTTP/HTTPS 协议

**3. 上游管理**
- `create_vefaas_upstream()`: 创建 VeFaaS 函数上游

> 源码位置：[ve_apig.py#L24-L150](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_apig/ve_apig.py#L24-L150)

---

## VeTOS - 对象存储集成

`VeTOS` 类封装了火山引擎对象存储服务（TOS），支持文件上传、下载、删除等操作，可用于持久化存储 Agent 数据、多媒体文件等。

> 源码位置：[ve_tos/ve_tos.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_tos/ve_tos.py)

### 类定义

```python
class VeTOS:
    def __init__(
        self,
        ak: str = "",
        sk: str = "",
        session_token: str = "",
        region: str = "",
        bucket_name: str = "",
    ) -> None:
```

### 初始化参数

| 参数 | 环境变量回退 | 说明 |
|------|-------------|------|
| `ak` | `VOLCENGINE_ACCESS_KEY` | Access Key |
| `sk` | `VOLCENGINE_SECRET_KEY` | Secret Key |
| `session_token` | `VOLCENGINE_SESSION_TOKEN` | STS Token |
| `region` | `REGION` / `DATABASE_TOS_REGION` | 区域 |
| `bucket_name` | `DATABASE_TOS_BUCKET` | Bucket 名称 |

### 云服务商适配

VeTOS 自动根据 `CLOUD_PROVIDER` 环境变量适配端点：

| 服务商 | 二级域名 | 默认区域 |
|--------|---------|---------|
| volcengine（默认） | `volces.com` | `cn-beijing` |
| byteplus | `bytepluses.com` | `ap-southeast-1` |

端点格式：`tos-{region}.{sld}.com`

### 依赖要求

使用 VeTOS 需要安装 TOS SDK：
```bash
pip install tos
```

> 源码位置：[ve_tos.py#L33-L100](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_tos/ve_tos.py#L33-L100)

---

## VeTLS - 日志服务

`VeTLS` 类封装了火山引擎日志服务（TLS），支持日志项目创建、日志主题管理、日志写入与查询，用于 Agent 运行日志收集与分析。

> 源码位置：[ve_tls/ve_tls.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_tls/ve_tls.py)

### 类定义

```python
class VeTLS:
    def __init__(
        self,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str = "cn-beijing",
    ):
```

### 核心功能

**1. 日志项目管理**
- `get_project_id_by_name(project_name)`: 根据名称查找日志项目 ID
- `create_log_project(project_name)`: 创建日志项目

**2. 端点**
- 默认端点：`https://tls-{region}.volces.com`

### 默认配置

| 配置项 | 默认值 |
|--------|--------|
| 日志项目名 | `veadk-log-project` |
| Tracing 实例名 | `veadk-tracing-instance` |

### 依赖要求

使用 VeTLS 需要安装火山引擎 SDK：
```bash
pip install volcengine
```

> 源码位置：[ve_tls.py#L23-L100](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_tls/ve_tls.py#L23-L100)

---

## VeIdentity - 身份认证服务

`ve_identity` 模块提供了与火山引擎 VeIdentity 身份认证服务的集成，支持 OAuth2、API Key、Workload 认证等多种认证方式，并提供了与 Agent 工具结合的认证中间件。

> 源码位置：[ve_identity/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_identity/)

### 核心组件

| 组件 | 说明 |
|------|------|
| `IdentityClient` | 身份服务 API 底层客户端 |
| `WorkloadTokenManager` | Workload 访问令牌管理（带缓存） |
| `AuthRequestProcessor` | OAuth2 流程处理器（对话中认证） |
| `VeIdentityFunctionTool` | 支持认证的函数工具装饰器 |
| `VeIdentityMcpTool` | 支持认证的 MCP 工具 |
| `VeIdentityMcpToolset` | 支持认证的 MCP 工具集 |

### 认证配置类型

| 配置函数 | 类型 | 说明 |
|----------|------|------|
| `api_key_auth()` | `ApiKeyAuthConfig` | API Key 认证 |
| `oauth2_auth()` | `OAuth2AuthConfig` | OAuth2 认证（用户联邦） |
| `workload_auth()` | `WorkloadAuthConfig` | Workload 身份认证 |

### 使用示例

```python
from veadk.integrations.ve_identity import (
    VeIdentityFunctionTool,
    oauth2_auth,
)

async def get_github_repos(access_token: str):
    """获取用户的 GitHub 仓库列表"""
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return resp.json()

github_tool = VeIdentityFunctionTool(
    func=get_github_repos,
    auth_config=oauth2_auth(
        provider_name="github",
        scopes=["repo", "user"],
        auth_flow="USER_FEDERATION",
    ),
    into="access_token",  # 将获取的 token 注入到 access_token 参数
)
```

### OAuth2 流程

1. 用户调用需要认证的工具
2. `AuthRequestProcessor` 检测到需要认证，返回授权链接
3. 用户点击链接完成授权
4. 系统轮询获取 token
5. Token 自动注入工具参数执行
6. Token 缓存供后续使用

> 源码位置：[ve_identity/__init__.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_identity/__init__.py)

---

## AgentKit - AgentKit 平台集成

`agentkit` 模块提供了与火山引擎 AgentKit 平台的集成，主要支持评估功能。

> 源码位置：[agentkit/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/)

### 目录结构

```
agentkit/
├── __init__.py
├── app.py                    # FastAPI 应用集成
├── session_capabilities.py   # 会话能力配置
└── evaluation/
    ├── __init__.py
    ├── client.py             # 评估客户端
    └── feedback.py           # 反馈收集
```

### 评估客户端 (`evaluation/client.py`)

提供与 AgentKit 评估服务交互的客户端，支持：
- 评估任务创建
- 评估结果查询
- 数据集上传

### FastAPI 应用集成 (`app.py`)

提供 FastAPI 路由，可以挂载到现有应用中提供 AgentKit 兼容的 API 端点。

---

## VeCodePipeline - CI/CD 流水线

`ve_code_pipeline` 模块封装了火山引擎 Code Pipeline 服务，支持创建 CI/CD 流水线实现代码变更自动部署。

> 源码位置：[ve_code_pipeline/ve_code_pipeline.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_code_pipeline/ve_code_pipeline.py)

流水线工作流程：
1. 监听 GitHub 代码推送
2. 自动拉取源码
3. 使用 VeADK 基础镜像构建
4. 推送镜像到 VeCR
5. 更新 VeFaaS 函数部署

主要用于 CLI `pipeline` 命令的后端实现。

---

## VeCozeloop - CozeLoop 可观测性

`ve_cozeloop` 模块提供了与 CozeLoop（火山引擎可观测性平台）的集成，用于：
- LLM 调用 Tracing
- Prompt 版本管理
- 评估数据集管理
- 指标收集

> 源码位置：[ve_cozeloop/ve_cozeloop.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_cozeloop/ve_cozeloop.py)

主要用于 Tracing 模块的 CozeLoop Exporter 和 Prompt 模块的 CozeloopPromptManager。

---

## VePromptPilot - Prompt 优化服务

`ve_prompt_pilot` 模块集成了火山引擎 PromptPilot 服务，支持系统提示词的自动化优化。

> 源码位置：[ve_prompt_pilot/ve_prompt_pilot.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_prompt_pilot/ve_prompt_pilot.py)

主要功能：
- 分析现有 Prompt
- 提供优化建议
- 自动生成优化版本
- A/B 测试对比

用于 CLI `prompt` 命令的后端实现。

---

## VeVikingDBMemory - VikingDB 向量记忆

`ve_viking_db_memory` 模块提供了基于火山引擎 VikingDB 向量数据库的长期记忆存储实现。

> 源码位置：[ve_viking_db_memory/ve_viking_db_memory.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_viking_db_memory/ve_viking_db_memory.py)

特点：
- 支持高维向量存储与检索
- 持久化记忆存储
- 适用于生产环境大规模部署
- 与 VeADK 记忆系统无缝集成

---

## 一键部署流程

VeADK 部署（`veadk deploy` 命令）自动化了以下流程：

```
本地代码
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 环境检查与配置加载                                         │
│    - 验证 AK/SK                                             │
│    - 加载 .env / config.yaml                                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. VeAPIG 网关准备                                           │
│    - 查找或创建 Serverless 网关                              │
│    - 创建网关服务（域名）                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. VeFaaS 函数创建                                           │
│    - 创建函数（Python 3.12 运行时）                          │
│    - 注入环境变量                                            │
│    - 配置 IAM 角色（如指定）                                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 代码打包上传                                              │
│    - ZIP 压缩本地项目                                        │
│    - 获取 TOS 临时上传地址                                   │
│    - PUT 上传代码包                                          │
│    - 回调挂载代码到函数                                      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. APIG 路由配置                                             │
│    - 创建 VeFaaS 上游                                        │
│    - 创建路由（关联服务与上游）                              │
│    - 配置认证（API Key / OAuth2，如启用）                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. VeFaaS 应用创建                                           │
│    - 关联函数与网关配置                                      │
│    - 等待应用就绪                                            │
│    - 输出访问端点                                            │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
  部署完成 ✓
    - 应用 URL
    - （可选）A2A 端点: /.well-known/agent.json
    - （可选）Web UI 端点
```

### 认证配置选项

部署时支持三种认证模式：

| 模式 | 说明 | 配置 |
|------|------|------|
| `none` | 无认证，公开访问 | `--auth-method none`（默认） |
| `api-key` | API Key 认证 | `--auth-method api-key` |
| `oauth2` | VeIdentity OAuth2 认证 | `--auth-method oauth2 --user-pool-name X --client-name Y` |

### 记忆后端选项

| 后端 | 说明 | 适用场景 |
|------|------|---------|
| `local` | 内存存储（默认） | 开发测试，单实例 |
| `mysql` | MySQL 持久化 | 生产环境，多实例 |

---

## 目录结构

```
veadk/integrations/
├── __init__.py
├── agentkit/                      # AgentKit 平台集成
│   ├── __init__.py
│   ├── app.py
│   ├── session_capabilities.py
│   └── evaluation/
│       ├── __init__.py
│       ├── client.py
│       └── feedback.py
├── ve_apig/                       # API 网关
│   ├── __init__.py
│   ├── ve_apig.py
│   └── ve_apig_utils.py
├── ve_code_pipeline/              # CI/CD 流水线
│   ├── __init__.py
│   └── ve_code_pipeline.py
├── ve_cozeloop/                   # CozeLoop 可观测性
│   ├── __init__.py
│   └── ve_cozeloop.py
├── ve_cr/                         # 容器镜像服务
│   ├── __init__.py
│   └── ve_cr.py
├── ve_faas/                       # 函数计算
│   ├── __init__.py
│   ├── ve_faas.py
│   ├── ve_faas_utils.py
│   ├── template/                  # Agent 项目模板
│   └── web_template/              # Web 应用模板
├── ve_identity/                   # 身份认证
│   ├── __init__.py
│   ├── auth_config.py
│   ├── auth_mixins.py
│   ├── auth_processor.py
│   ├── function_tool.py
│   ├── identity_client.py
│   ├── mcp_tool.py
│   ├── mcp_toolset.py
│   ├── models.py
│   ├── token_manager.py
│   └── utils.py
├── ve_prompt_pilot/               # Prompt 优化
│   ├── __init__.py
│   └── ve_prompt_pilot.py
├── ve_tls/                        # 日志服务
│   ├── __init__.py
│   ├── utils.py
│   └── ve_tls.py
├── ve_tos/                        # 对象存储
│   └── ve_tos.py
└── ve_viking_db_memory/           # VikingDB 向量记忆
    ├── __init__.py
    └── ve_viking_db_memory.py
```
