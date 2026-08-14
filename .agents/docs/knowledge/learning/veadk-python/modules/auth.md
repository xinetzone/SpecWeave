---
id: auth-module
title: 认证与凭证服务
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 认证与凭证服务

## 概述

VeADK 提供了完整的认证与凭证管理体系，支持多种认证方式，包括 API Key、OAuth2、请求签名、VeFaaS IAM 角色等。认证模块设计了清晰的优先级机制，并提供凭证服务用于安全地存储和管理用户凭证，同时内置了日志凭证脱敏功能以防止敏感信息泄露。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/](#)

---

## 认证机制概述

VeADK 的认证体系分为三层：

```
┌─────────────────────────────────────────────────────────────┐
│  应用层认证 (Application Auth)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VeCredentialService - 用户凭证存储与管理            │   │
│  │  OAuth2 中间件 - Web 服务 OAuth2 认证                │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  服务认证 (Service Auth)                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VeAuth 体系 - 各云服务 Token 获取                   │   │
│  │  (Ark/Speech/OpenSearch/Viking/PostgreSQL 等)       │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  请求签名 (Request Signing)                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Volcengine Sign V4 - 火山引擎 API 请求签名          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## API Key 四级优先级机制

VeADK 在获取各类服务 API Key 时遵循严格的四级优先级机制（以模型 API Key 为例）：

### 优先级从高到低

| 优先级 | 来源 | 说明 | 示例（MODEL_AGENT_API_KEY） |
|--------|------|------|----------------------------|
| **1（最高）** | 显式环境变量 | 直接设置的对应服务 API Key | `MODEL_AGENT_API_KEY=xxx` |
| **2** | 指定名称的 ARK Key | 通过 API Key 名称从 ARK 获取 | `MODEL_AGENT_API_KEY_NAME=my-key` |
| **3** | 默认 ARK Key | 账户中的第一个 ARK API Key | 调用 `ListApiKeys` 取第一项 |
| **4（最低）** | VeFaaS IAM 角色 | 运行在 VeFaaS 时从实例角色获取 | 自动从 IAM 角色获取临时凭证 |

### Ark Token 获取逻辑

`get_ark_token()` 函数实现了完整的优先级链：

```python
def get_ark_token(
    region: str = "cn-beijing",
    api_key_name: str | None = None,
    *,
    access_key: str | None = None,
    secret_key: str | None = None,
    session_token: str | None = None,
) -> str:
    # 1. 显式传入参数优先
    access_key = access_key or os.getenv("VOLCENGINE_ACCESS_KEY")
    secret_key = secret_key or os.getenv("VOLCENGINE_SECRET_KEY")
    session_token = session_token or os.getenv("VOLCENGINE_SESSION_TOKEN")

    # 2. 如无 AK/SK，尝试从 VeFaaS IAM 获取
    if not (access_key and secret_key):
        cred = get_credential_from_vefaas_iam()
        access_key = cred.access_key_id
        secret_key = cred.secret_access_key
        session_token = cred.session_token

    # 3. 云服务商适配
    provider = os.getenv("CLOUD_PROVIDER")
    host = "open.volcengineapi.com"
    if provider and provider.lower() == "byteplus":
        region = "ap-southeast-1"
        host = "open.byteplusapi.com"

    # 4. 分页查询 API Keys
    def _list_api_keys(page_number: int) -> dict:
        res = ve_request(
            request_body={"ProjectName": "default", "Filter": {"AllowAll": True}},
            query={"PageNumber": str(page_number), "PageSize": "10"},
            action="ListApiKeys",
            ak=access_key, sk=secret_key,
            service="ark", version="2024-01-01",
            region=region, host=host,
        )
        return res["Result"]

    # 5. 按名称查找或取第一个
    if api_key_name:
        # 分页遍历查找指定名称的 Key
        ...
    else:
        items = _list_api_keys(1).get("Items", [])
        target_id = items[0]["Id"]  # 默认取第一个

    # 6. 获取原始 API Key
    res = ve_request(..., action="GetRawApiKey", ...)
    return res["Result"]["ApiKey"]
```

> 源码位置：[veauth/ark_veauth.py#L31-L149](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/veauth/ark_veauth.py#L31-L149)

### 各服务 Token 对应的环境变量

| 服务 | 显式 Key 环境变量 | 名称环境变量 | 兜底来源 |
|------|-----------------|-------------|---------|
| Agent 模型 | `MODEL_AGENT_API_KEY` | `MODEL_AGENT_API_KEY_NAME` | ARK 默认 Key |
| Embedding 模型 | `MODEL_EMBEDDING_API_KEY` | - | `MODEL_AGENT_API_KEY` → ARK 默认 |
| Realtime 语音 | `MODEL_REALTIME_API_KEY` | - | Speech Token |
| Speech | - | - | Speech 服务 Token |

> 源码位置：[configs/model_configs.py#L31-L104](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L31-L104)

---

## VeCredentialService - 凭证服务

`VeCredentialService` 是 VeADK 的用户凭证管理服务，扩展自 Google ADK 的 `BaseCredentialService`，支持按应用和用户维度安全存储凭证。

> 源码位置：[ve_credential_service.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/ve_credential_service.py)

### 存储结构

凭证以三层嵌套字典结构存储：

```python
{
    "app_name_1": {
        "user_id_1": {
            "credential_key_1": AuthCredential(...),
            "credential_key_2": AuthCredential(...),
        },
        "user_id_2": { ... }
    },
    "app_name_2": { ... }
}
```

### 类定义

```python
class VeCredentialService(BaseCredentialService):
    def __init__(self):
        super().__init__()
        self._credentials: dict[str, dict[str, dict[str, AuthCredential]]] = {}
```

### 核心方法

**1. set_credential() - 直接设置凭证**

```python
async def set_credential(
    self,
    app_name: str,
    user_id: str,
    credential_key: str,
    credential: AuthCredential,
) -> None:
```

无需 CallbackContext，适用于中间件和请求拦截器场景。

**2. get_credential() - 直接获取凭证**

```python
async def get_credential(
    self,
    app_name: str,
    user_id: str,
    credential_key: str,
) -> Optional[AuthCredential]:
```

直接按 app_name、user_id、credential_key 三层键查找，返回 `None` 表示不存在。

**3. save_credential() / load_credential() - ADK 标准接口**

```python
async def save_credential(
    self,
    auth_config: AuthConfig,
    callback_context: CallbackContext,
) -> None:

async def load_credential(
    self,
    auth_config: AuthConfig,
    callback_context: CallbackContext,
) -> Optional[AuthCredential]:
```

兼容 Google ADK 标准接口，从 CallbackContext 自动提取 app_name 和 user_id，委托给 set/get_credential。

### 使用示例

```python
from veadk.auth.ve_credential_service import VeCredentialService
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes

service = VeCredentialService()

# 存储用户 OAuth2 Token
await service.set_credential(
    app_name="my_app",
    user_id="user123",
    credential_key="github_oauth",
    credential=AuthCredential(
        auth_type=AuthCredentialTypes.BEARER_TOKEN,
        bearer_token="ghp_xxxxxxxxxxxx",
        refresh_token="ghr_xxxxxxxxxxxx",
        expires_at=1735689600,
    )
)

# 获取凭证
credential = await service.get_credential(
    app_name="my_app",
    user_id="user123",
    credential_key="github_oauth"
)
if credential:
    print(f"Token: {credential.bearer_token}")
```

> 源码位置：[ve_credential_service.py#L36-L203](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/ve_credential_service.py#L36-L203)

---

## VeAuth 体系 - 云服务认证

VeAuth 是 VeADK 对各类火山引擎云服务认证的抽象基类和实现集合，统一处理 AK/SK 配置、Token 获取和缓存。

> 源码位置：[veauth/](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/veauth/)

### 目录结构

```
veauth/
├── __init__.py
├── base_veauth.py           # VeAuth 抽象基类
├── ark_veauth.py            # ARK 大模型服务认证
├── speech_veauth.py         # 语音服务认证
├── opensearch_veauth.py     # OpenSearch 搜索引擎认证
├── viking_mem0_veauth.py    # VikingDB + Mem0 认证
├── vesearch_veauth.py       # VeSearch 向量搜索认证
├── postgresql_veauth.py     # PostgreSQL 数据库认证
├── cozeloop_veauth.py       # CozeLoop 可观测性认证
├── apmplus_veauth.py        # APMPlus 监控认证
├── mse_veauth.py            # MSE 微服务引擎认证
├── prompt_pilot_veauth.py   # PromptPilot 认证
└── utils.py                 # 工具函数（IAM 凭证获取等）
```

### BaseVeAuth 基类

所有 VeAuth 实现的抽象基类，统一处理 AK/SK 的加载逻辑。

```python
class BaseVeAuth(ABC, BaseAuth):
    volcengine_access_key: str
    volcengine_secret_key: str

    def __init__(
        self,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        super().__init__()

        # AK/SK 优先级：显式参数 > 环境变量
        final_ak = access_key or os.getenv("VOLCENGINE_ACCESS_KEY")
        final_sk = secret_key or os.getenv("VOLCENGINE_SECRET_KEY")

        assert final_ak, "Volcengine access key cannot be empty."
        assert final_sk, "Volcengine secret key cannot be empty."

        self.access_key = final_ak
        self.secret_key = final_sk
        self._token: str = ""

    @abstractmethod
    def _fetch_token(self) -> None: ...

    @property
    def token(self) -> str: ...
```

**AK/SK 加载优先级：**
1. 构造函数显式传入的 `access_key`/`secret_key`
2. 环境变量 `VOLCENGINE_ACCESS_KEY`/`VOLCENGINE_SECRET_KEY`

> 源码位置：[veauth/base_veauth.py#L21-L50](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/veauth/base_veauth.py#L21-L50)

### Ark 认证 (ark_veauth.py)

`get_ark_token()` 函数用于获取火山引擎方舟（Ark）大模型服务的 API Key，是模型调用的核心认证函数。详见前文「API Key 四级优先级机制」。

### 工具函数 (utils.py)

`utils.py` 提供了关键的辅助功能：

**get_credential_from_vefaas_iam()**

从 VeFaaS 运行环境的 IAM 角色获取临时凭证，是云端部署时 AK/SK 的兜底来源。

```python
def get_credential_from_vefaas_iam():
    """
    当代码运行在 VeFaaS 函数实例中时，自动从 IAM 角色获取临时凭证。
    返回包含 access_key_id、secret_access_key、session_token 的对象。
    """
```

这使得部署到 VeFaaS 的 Agent 无需显式配置 AK/SK，通过 IAM 角色即可安全访问其他云服务。

---

## OAuth2 支持

VeADK 通过 `ve_identity` 集成模块和 OAuth2 中间件提供完整的 OAuth2 认证支持。

### OAuth2 中间件

`auth/middleware/oauth2_auth.py` 提供了 FastAPI OAuth2 认证中间件，可用于保护 Web 端点。

> 源码位置：[middleware/oauth2_auth.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/middleware/oauth2_auth.py)

### VeIdentity OAuth2 集成

`veadk.integrations.ve_identity` 模块提供了 OAuth2 认证配置和工具：

- `oauth2_auth()`: 创建 OAuth2 认证配置
- `VeIdentityFunctionTool`: 自动处理 OAuth2 流程的工具装饰器
- `AuthRequestProcessor`: 对话中 OAuth2 授权流程处理器

详细使用方式参见 [cloud.md - VeIdentity 身份认证服务](cloud.md#veidentity---身份认证服务)。

### OAuth2 认证流程

```
用户调用工具
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 工具检测到需要 OAuth2 认证                                   │
│ AuthRequestProcessor 拦截调用                                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 返回授权链接给用户                                           │
│ 用户点击链接跳转至 OAuth2 授权页                              │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 用户完成授权                                                 │
│ 系统轮询 VeIdentity 获取 Access Token                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Token 存入 VeCredentialService（按 app+user 隔离）           │
│ 自动注入工具参数，执行原始调用                                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
  返回工具执行结果
```

---

## 请求签名

VeADK 内置了火山引擎 V4 签名算法实现，用于对 OpenAPI 请求进行签名认证。

### volcengine_sign 模块

`veadk.utils.volcengine_sign` 提供了 `ve_request()` 函数，封装了完整的 V4 签名流程：

```python
def ve_request(
    request_body: dict,
    ak: str,
    sk: str,
    service: str,
    version: str,
    region: str,
    host: str,
    action: str,
    method: str = "POST",
    query: dict | None = None,
    header: dict | None = None,
) -> dict:
```

### V4 签名流程

1. 构建规范请求（Canonical Request）
2. 构建待签名字符串（String to Sign）
3. 计算签名密钥（Signing Key）
4. 计算签名（Signature）
5. 构建 Authorization 头

签名过程自动处理：
- 时间戳生成（UTC 格式）
- 请求体 SHA256 哈希
- Header 规范化和排序
- Query 参数排序和编码
- 多区域/服务密钥派生

### Session Token 支持

当使用 STS 临时凭证时，自动在请求头中添加 `X-Security-Token`。

> 签名实现可参考 A2A Registry Client 中的 `_volc_sign_v4()` 函数：
> [registry_client.py#L750-L816](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L750-L816)

---

## 日志凭证脱敏

VeADK 在日志输出时自动对敏感凭证信息进行脱敏处理，防止 API Key、Token、Secret 等敏感信息意外泄露到日志中。

### 脱敏原则

1. **不记录完整凭证**：Token、API Key、Secret 等值在日志中被替换为 `***` 或截断显示
2. **Debug 级别谨慎**：即使在 DEBUG 级别，敏感字段也不会完整输出
3. **结构化脱敏**：在日志输出前对字典/对象中的敏感键名进行递归脱敏

### 敏感字段名称

自动识别并脱敏的字段名（不区分大小写）包括：
- `api_key` / `apikey`
- `access_key` / `accesskey`
- `secret_key` / `secretkey`
- `token` / `bearer_token` / `access_token` / `refresh_token`
- `password` / `passwd`
- `authorization`
- `session_token` / `security_token`
- `client_secret`

### 示例

```python
# VeFaaS 创建函数时的日志输出
logger.debug(
    f"Function creation in {res.project_name} project with ID {res.id}"
    # 注意：不打印 envs 内容，因为可能包含敏感信息
)
```

> 源码位置参考：[ve_faas.py#L165-L168](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_faas/ve_faas.py#L165-L168)

---

## BaseAuth 基类

认证类的最顶层抽象基类：

```python
class BaseAuth:
    def __init__(self) -> None: ...

    def _fetch_token(self) -> str | dict: ...

    @property
    def token(self) -> str | dict: ...
```

- `_fetch_token()`: 抽象方法，子类实现实际的 Token 获取逻辑
- `token` 属性: 获取当前 Token，通常带缓存机制

---

## 目录结构

```
veadk/auth/
├── __init__.py
├── base_auth.py                    # Auth 抽象基类
├── ve_credential_service.py        # VeCredentialService 凭证服务
├── middleware/
│   ├── __init__.py
│   └── oauth2_auth.py             # OAuth2 FastAPI 中间件
└── veauth/                        # 各云服务认证实现
    ├── __init__.py
    ├── base_veauth.py             # VeAuth 抽象基类
    ├── ark_veauth.py              # ARK 大模型认证
    ├── speech_veauth.py           # 语音服务认证
    ├── opensearch_veauth.py       # OpenSearch 认证
    ├── viking_mem0_veauth.py      # VikingDB+Mem0 认证
    ├── vesearch_veauth.py         # VeSearch 认证
    ├── postgresql_veauth.py       # PostgreSQL 认证
    ├── cozeloop_veauth.py         # CozeLoop 认证
    ├── apmplus_veauth.py          # APMPlus 认证
    ├── mse_veauth.py              # MSE 认证
    ├── prompt_pilot_veauth.py     # PromptPilot 认证
    └── utils.py                   # 工具函数（IAM 凭证等）
```

---

## 配置示例

### 本地开发环境 (.env)

```bash
# 方式一：直接设置模型 API Key（最高优先级）
MODEL_AGENT_API_KEY=ark-xxxxxxxxxxxxxxxxxxxxxxxx

# 方式二：设置 ARK Key 名称，自动从 ARK 查找
# MODEL_AGENT_API_KEY_NAME=my-production-key

# 方式三：设置 AK/SK，自动获取第一个 ARK Key
VOLCENGINE_ACCESS_KEY=AKLTxxxxxxxxxxxxxxxx
VOLCENGINE_SECRET_KEY=Wlxxxxxxxxxxxxxxxxxxxxxxxxxx
VOLCENGINE_REGION=cn-beijing
```

### VeFaaS 云端部署

无需配置 AK/SK 和 API Key，通过 IAM 角色自动获取凭证：

1. 在部署时通过 `--iam-role` 指定具有 Ark 访问权限的 IAM 角色
2. 函数运行时自动通过 `get_credential_from_vefaas_iam()` 获取临时凭证
3. 使用临时凭证调用 ARK ListApiKeys/GetRawApiKey 获取 API Key
4. 全程无需在代码或环境变量中存储长期凭证
