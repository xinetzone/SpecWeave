---
id: cloud-integration
title: 云服务集成指南
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 云服务集成指南

本文档介绍 VeADK 的云服务集成模式，以及如何扩展支持其他云服务提供商。VeADK 内置了火山引擎（Volcengine）系列云服务的集成，所有集成遵循统一的凭证管理和请求签名模式。

---

## 一、现有云服务集成概览

VeADK 在 `veadk/integrations/` 目录下提供了以下云服务集成模块：

| 模块 | 路径 | 功能 | 依赖SDK |
|---|---|---|---|
| VeFaaS函数计算 | [ve_faas/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas) | 代码打包上传、函数创建/更新、应用发布、容器镜像部署 | `volcenginesdkvefaas` |
| APIG API网关 | [ve_apig/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_apig) | Serverless网关管理、服务/路由/上游配置 | `volcenginesdkapig` |
| CR容器镜像仓库 | [ve_cr/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_cr) | VPC隧道配置（容器镜像拉取网络打通） | 通过VeFaaS调用 |
| TOS对象存储 | [ve_tos/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_tos) | 媒体文件上传、内联数据托管、技能文件下载 | `tos` Python SDK |
| TLS日志服务 | [ve_tls/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_tls) | 日志导出、Trace数据上报 | `volcenginesdktls` |
| VeIdentity身份认证 | [ve_identity/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_identity) | IAM凭证获取、OAuth2认证、MCP工具认证 | 内部HTTP API |
| AgentKit平台 | [agentkit/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit) | 应用托管、会话能力管理、评估反馈 | HTTP API |
| CozeLoop提示词平台 | [ve_cozeloop/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_cozeloop) | 提示词版本管理、PromptManager后端 | HTTP API |
| PromptPilot优化 | [ve_prompt_pilot/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_prompt_pilot) | 提示词优化集成 | HTTP API |
| VikingDB向量数据库 | [ve_viking_db_memory/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_viking_db_memory) | VikingDB长期记忆后端 | `vikinguav` |
| CodePipeline代码流水线 | [ve_code_pipeline/](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_code_pipeline) | 代码流水线集成 | HTTP API |

参考：[云部署集成模块清单](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/12-extension-points.md#L170-L184)

---

## 二、火山引擎集成模式

所有火山引擎云服务集成遵循高度一致的设计模式（参考[架构洞察9](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L263-L311)）。

### 2.1 统一凭证初始化模式

**参考实现**：[VeFaaS.__init__()](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py#L52-L89)

所有集成类的构造函数接收相同的凭证四元组：

```python
class VeFaaS:
    def __init__(
        self,
        access_key: str,           # Access Key ID
        secret_key: str,           # Secret Access Key
        session_token: str = "",   # STS临时Token（IAM角色场景）
        region: str = "cn-beijing", # 区域
        project_name: str = "default",
    ):
        self.ak = access_key
        self.sk = secret_key
        self.session_token = session_token
        self.region = region
        self.project_name = project_name

        # 1. 创建SDK Configuration对象
        configuration = volcenginesdkcore.Configuration()
        configuration.ak = self.ak
        configuration.sk = self.sk
        configuration.session_token = self.session_token
        configuration.region = region
        configuration.client_side_validation = True

        # 2. 设置为全局默认配置
        volcenginesdkcore.Configuration.set_default(configuration)

        # 3. 初始化具体服务的API客户端
        self.client = volcenginesdkvefaas.VEFAASApi(
            volcenginesdkcore.ApiClient(configuration)
        )

        # 4. 可链式初始化关联服务客户端
        self.apig_client = APIGateway(
            self.ak, self.sk, self.region,
            session_token=self.session_token,
        )
```

### 2.2 签名请求工具：ve_request()

对于SDK未覆盖的OpenAPI接口，统一使用 [ve_request()](file:///d:/AI/.chaos/libs/veadk-python/veadk/utils/volcengine_sign.py#L341-L393) 函数发送SigV4签名请求：

```python
from veadk.utils.volcengine_sign import ve_request

response = ve_request(
    request_body={
        "Name": "my-application",
        "Config": {...},
    },
    action="CreateApplication",     # API Action名称
    ak=access_key,
    sk=secret_key,
    service="vefaas",              # 服务标识
    version="2021-03-03",          # API版本
    region="cn-beijing",
    host="open.volcengineapi.com", # API域名
    session_token=session_token,   # STS Token（可选）
)
```

### 2.3 凭证链获取模式

凭证获取遵循统一的优先级链（参考[架构洞察7](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L193-L231)）：

```python
from veadk.auth.veauth.utils import get_credential_from_vefaas_iam
import os

def get_credentials():
    """获取云服务凭证：环境变量优先 → IAM角色兜底。"""
    ak = os.getenv("VOLCENGINE_ACCESS_KEY")
    sk = os.getenv("VOLCENGINE_SECRET_KEY")
    session_token = ""

    if not (ak and sk):
        # 云端VEFAAS环境：从IAM角色自动获取临时凭证
        credential = get_credential_from_vefaas_iam()
        ak = credential.access_key_id
        sk = credential.secret_access_key
        session_token = credential.session_token

    return ak, sk, session_token
```

内置工具中的凭证链（参考[web_search.py:40-65](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L40-L65)）更加完善：

```
1. 工具专属环境变量（TOOL_WEB_SEARCH_ACCESS_KEY）
2. ToolContext状态中的凭证
3. 全局环境变量（VOLCENGINE_ACCESS_KEY）
4. VEFAAS IAM角色临时凭证
```

### 2.4 BytePlus跨云兼容

VeADK 自动映射 BytePlus 环境变量到火山引擎环境变量（[config.py:54-61](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L215)）：

- `BYTEPLUS_ACCESS_KEY` → `VOLCENGINE_ACCESS_KEY`
- `BYTEPLUS_SECRET_KEY` → `VOLCENGINE_SECRET_KEY`
- 通过 `CLOUD_PROVIDER` 环境变量切换API域名：
  - `volcengine`（默认）：国内API `*.volcengineapi.com`
  - `byteplus`：海外API `*.byteplusapi.com`

### 2.5 日志脱敏模式

输出日志时必须对敏感信息脱敏，参考 [ve_faas.py:252-263](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L301) 的正则脱敏模式：

```python
import re

def mask_secrets(text: str) -> str:
    """脱敏日志中的密钥、Token等敏感信息。"""
    patterns = [
        (r'(?i)(access["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9]{16,})', r'\1******'),
        (r'(?i)(secret["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9]{16,})', r'\1******'),
        (r'(?i)(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9._-]{16,})', r'\1******'),
        (r'(?i)(password["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r'\1******'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text
```

---

## 三、自定义云服务集成步骤

新增其他云服务（如阿里云、腾讯云、AWS）集成时，建议遵循以下步骤。

### 步骤1：创建集成模块目录结构

在 `veadk/integrations/` 下创建新目录：

```
veadk/integrations/
└── my_cloud_provider/
    ├── __init__.py
    ├── my_cloud_client.py    # 核心API客户端
    └── utils.py              # 辅助函数（如有）
```

### 步骤2：实现核心客户端类

参考 VeFaaS 的实现模式，统一构造函数签名：

```python
from __future__ import annotations
import os
from typing import Any

from veadk.utils.logger import get_logger

logger = get_logger(__name__)


class MyCloudService:
    """自定义云服务客户端。"""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        session_token: str = "",
        region: str = "default-region",
        **kwargs,
    ):
        """
        Args:
            access_key: 云服务Access Key。
            secret_key: 云服务Secret Key。
            session_token: STS临时Token（可选）。
            region: 区域。
            **kwargs: 其他服务特定配置。
        """
        self.ak = access_key
        self.sk = secret_key
        self.session_token = session_token
        self.region = region

        # 初始化SDK客户端或HTTP客户端
        self._init_client()

    def _init_client(self):
        """初始化云服务SDK客户端。"""
        # 方式1：如果有官方Python SDK，使用SDK
        # import my_cloud_sdk
        # config = my_cloud_sdk.Config(
        #     ak=self.ak, sk=self.sk, region=self.region,
        #     security_token=self.session_token,
        # )
        # self.client = my_cloud_sdk.Client(config)

        # 方式2：使用requests + 手动签名
        import requests
        self.session = requests.Session()
        self._signer = self._create_signer()

    @classmethod
    def from_env(cls) -> "MyCloudService":
        """从环境变量创建客户端实例（便捷工厂方法）。"""
        ak = os.getenv("MY_CLOUD_ACCESS_KEY")
        sk = os.getenv("MY_CLOUD_SECRET_KEY")
        token = os.getenv("MY_CLOUD_SESSION_TOKEN", "")
        region = os.getenv("MY_CLOUD_REGION", "default-region")

        if not (ak and sk):
            # 尝试从默认凭证链获取（如实例角色）
            ak, sk, token = cls._get_default_credentials()

        return cls(ak, sk, session_token=token, region=region)

    @staticmethod
    def _get_default_credentials() -> tuple[str, str, str]:
        """从默认凭证链获取凭证（实例角色、配置文件等）。"""
        # 实现你的默认凭证获取逻辑
        # 例如从云厂商元数据服务获取临时凭证
        raise ValueError(
            "No credentials found. Set MY_CLOUD_ACCESS_KEY/MY_CLOUD_SECRET_KEY "
            "or configure instance role."
        )

    def call_api(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """调用云服务API。"""
        # 实现API调用逻辑
        # 1. 构造请求
        # 2. 签名
        # 3. 发送请求
        # 4. 处理响应
        # 5. 错误处理
        ...
```

### 步骤3：实现SDK签名请求（如果无官方SDK）

如果云服务没有Python SDK，需要手动实现签名请求：

```python
import hashlib
import hmac
import datetime
import requests


def my_cloud_sign_request(
    method: str,
    host: str,
    path: str,
    query: dict,
    body: str,
    ak: str,
    sk: str,
    region: str,
    service: str,
    session_token: str = "",
) -> requests.Response:
    """发送签名请求（以类似SigV4的模式为例）。

    根据你的云服务厂商的签名算法文档实现。
    """
    now = datetime.datetime.utcnow()
    date_stamp = now.strftime("%Y%m%d")
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")

    # 1. 创建规范请求
    canonical_uri = path
    canonical_querystring = "&".join(
        f"{k}={v}" for k, v in sorted(query.items())
    )

    payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()

    headers = {
        "host": host,
        "x-date": amz_date,
        "x-content-sha256": payload_hash,
        "content-type": "application/json",
    }
    if session_token:
        headers["x-security-token"] = session_token

    signed_headers = "host;x-content-sha256;x-date"
    canonical_headers = "\n".join(
        f"{k}:{v}" for k, v in sorted(headers.items()) if k in signed_headers
    )

    canonical_request = "\n".join([
        method,
        canonical_uri,
        canonical_querystring,
        canonical_headers + "\n",
        signed_headers,
        payload_hash,
    ])

    # 2. 创建待签名字符串
    algorithm = "HMAC-SHA256"
    credential_scope = f"{date_stamp}/{region}/{service}/request"
    string_to_sign = "\n".join([
        algorithm,
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
    ])

    # 3. 计算签名
    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    k_date = sign(sk.encode("utf-8"), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, "request")
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    # 4. 添加Authorization头
    headers["authorization"] = (
        f"{algorithm} Credential={ak}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    # 5. 发送请求
    url = f"https://{host}{path}"
    response = requests.request(
        method=method,
        url=url,
        params=query,
        data=body,
        headers=headers,
        timeout=(10, 60),
    )
    response.raise_for_status()
    return response.json()
```

参考火山引擎签名实现：[volcengine_sign.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/utils/volcengine_sign.py#L100-L222)

### 步骤4：凭证管理模式

建议你的云服务集成支持以下凭证来源（优先级从高到低）：

1. **显式传参**：构造函数直接传入 ak/sk
2. **服务专属环境变量**：如 `MY_CLOUD_ACCESS_KEY`
3. **通用环境变量**：如 `ACCESS_KEY_ID`/`SECRET_ACCESS_KEY`
4. **实例角色/元数据服务**：云服务器实例角色临时凭证
5. **配置文件**：`~/.mycloud/credentials` 等

```python
def resolve_credentials(
    access_key: str | None = None,
    secret_key: str | None = None,
) -> tuple[str, str, str]:
    """解析凭证，返回(ak, sk, session_token)。"""
    # 1. 显式传参优先级最高
    if access_key and secret_key:
        return access_key, secret_key, ""

    # 2. 服务专属环境变量
    ak = os.getenv("MY_CLOUD_ACCESS_KEY")
    sk = os.getenv("MY_CLOUD_SECRET_KEY")
    token = os.getenv("MY_CLOUD_SESSION_TOKEN", "")

    if ak and sk:
        return ak, sk, token

    # 3. 实例元数据服务（云端部署时自动获取）
    try:
        return _get_instance_role_credentials()
    except Exception:
        pass

    raise ValueError(
        "MyCloud credentials not found. Please set MY_CLOUD_ACCESS_KEY and "
        "MY_CLOUD_SECRET_KEY environment variables, or pass them explicitly."
    )
```

### 步骤5：与Agent集成（作为Tool）

云服务能力通常以Tool形式暴露给Agent使用：

```python
from google.adk.tools import ToolContext


def my_cloud_operation(
    resource_id: str,
    action: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """在我的云服务上执行操作。

    当需要操作云资源（创建实例、查询状态、管理存储等）时使用此工具。

    Args:
        resource_id: 资源ID。
        action: 要执行的操作，如"describe"、"start"、"stop"。

    Returns:
        操作结果。
    """
    try:
        client = MyCloudService.from_env()
        result = client.call_api(action, {"ResourceId": resource_id})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
```

---

## 四、集成模式总结

### 火山引擎集成模式清单

| 模式 | 实现方式 | 参考 |
|---|---|---|
| 构造函数签名 | `(ak, sk, session_token="", region="cn-beijing")` | [ve_faas.py:52-65](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py#L52-L65) |
| SDK初始化 | `volcenginesdkcore.Configuration()` → `set_default()` → `ApiClient()` → 具体API实例 | [ve_faas.py:67-78](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py#L67-L78) |
| 非SDK API调用 | 使用 `ve_request()` 发送签名请求 | [ve_faas.py:186-210](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py#L186-L210) |
| 凭证获取 | 环境变量 → `get_credential_from_vefaas_iam()` | [web_search.py:52-63](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L52-L63) |
| BytePlus兼容 | `CLOUD_PROVIDER` 环境变量切换域名，自动映射AK/SK环境变量 | [config.py:54-61](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L215) |
| 日志脱敏 | 正则替换 key/secret/token/password 字段 | 架构洞察9建议 |
| 模块间依赖 | VeFaaS自动创建VeAPIG实例，一站式部署 | [ve_faas.py:80-85](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py#L80-L85) |

### 最佳实践

1. **统一构造函数签名**：遵循 `(ak, sk, session_token="", region=...)` 模式，降低学习成本
2. **提供from_env()工厂方法**：方便用户从环境变量快速创建实例
3. **支持链式服务初始化**：关联服务可自动初始化（如VeFaaS自动创建VeAPIG）
4. **日志脱敏**：所有日志输出必须脱敏敏感信息
5. **超时设置**：HTTP请求设置合理超时，避免无限等待（参考 `DEFAULT_REQUEST_TIMEOUT = (10, 60)`）
6. **错误处理**：捕获异常并提供有意义的错误信息
7. **延迟导入**：云SDK依赖较重，采用延迟导入避免强制依赖
8. **from __future__ import annotations**：使用类型注解的延迟求值

---

## 五、CloudAgentEngine 部署引擎

VeADK 提供 `CloudAgentEngine` 类用于通过Python SDK部署Agent到VeFaaS，这是云集成的高级应用。

参考：[vefaas.mdx文档](file:///d:/AI/.chaos/libs/veadk-python/docs/content/docs/framework/vefaas.mdx#L183-L315)

```python
from veadk.cloud.cloud_agent_engine import CloudAgentEngine

# 凭证从环境变量自动获取
engine = CloudAgentEngine()

# 部署应用
cloud_app = engine.deploy(
    application_name="my-python-agent",
    path="./path/to/agent/project",
    gateway_name="my-agent-gateway",
    use_adk_web=False,
)

print(f"Endpoint: {cloud_app.vefaas_endpoint}")
```

`CloudApp` 实例用于与已部署的应用交互：

```python
from veadk.cloud.cloud_app import CloudApp
import asyncio

app = CloudApp(vefaas_application_name="my-python-agent")

async def main():
    response = await app.message_send(
        "你好", session_id="test", user_id="user1"
    )
    print(response)

asyncio.run(main())
```
