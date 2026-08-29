---
type: Concept
title: 认证与权限
description: 深入理解 Home Assistant 认证与权限体系，包括 AuthManager、User、RefreshToken、JWT 令牌机制、Permission 权限策略、Owner/Admin/User 角色，以及 auth_store 持久化
tags: [home-assistant, smart-home, auth, authentication, permissions, jwt, security, core]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: core-source
    resource: "/references/core-source.md"
    title: Home Assistant 核心框架源码
  - id: facts-core
    resource: "/references/facts-core.md"
    title: Home Assistant Core 事实清单
---

# 认证与权限

认证（Authentication）与权限（Authorization）是 Home Assistant 安全体系的两大支柱。认证确认"你是谁"，权限决定"你能做什么"。HA 的认证系统位于 `homeassistant/auth/` 包中，由 `AuthManager` 统一管理，支持多种登录提供者（密码、命令行、可信网络）、多因素认证（MFA）、JWT 访问令牌和细粒度权限策略。认证系统通过 `hass.auth` 访问。

## AuthManager：认证管理器

`AuthManager` 类定义于 `auth/__init__.py:176`，是整个认证子系统的入口和协调者。

### 创建与初始化

`AuthManager` 不直接实例化，而是通过工厂函数 `auth_manager_from_config()` 创建（`auth/__init__.py:48-97`）：

```python
async def auth_manager_from_config(hass, provider_configs, module_configs):
    store = auth_store.AuthStore(hass)
    providers = await async_load_provider(hass, store, provider_configs)
    mfa_modules = await async_load_modules(hass, store, module_configs)
    auth = AuthManager(hass, store, providers, mfa_modules)
    auth.login_flow = AuthManagerFlowManager(hass, auth)
    return auth
```

该函数加载认证提供者（auth providers）和 MFA 模块，构造 AuthManager。AuthManager 持有：

- `store`：`AuthStore` 实例，持久化用户和令牌
- `providers`：认证提供者列表（如 `homeassistant.auth.providers.homeassistant`）
- `mfa_modules`：多因素认证模块列表
- `login_flow`：`AuthManagerFlowManager`，管理登录流程

### 认证事件

AuthManager 发布以下事件（事实 #345）：

```python
EVENT_USER_ADDED = "user_added"
EVENT_USER_UPDATED = "user_updated"
EVENT_USER_REMOVED = "user_removed"
```

前端和集成可以监听这些事件以响应用户变更。

## User：用户模型

`User` 类定义于 `auth/models.py:56`，使用 `attr.s(slots=False)` 装饰。

### 用户属性

```python
@attr.s(slots=False)
class User:
    id: str                          # 唯一用户 ID
    name: str | None                 # 显示名称
    is_owner: bool                   # 是否为所有者
    is_active: bool                  # 是否激活
    system_generated: bool           # 是否系统生成
    local_only: bool                 # 是否仅允许本地访问
    groups: list[Group]              # 所属用户组
    credentials: list[Credentials]   # 登录凭证
    refresh_tokens: list[RefreshToken]  # 刷新令牌
    perm_lookup: PermLookup          # 权限查找缓存
```

### 用户类型

HA 区分两类用户：

**普通用户**（`async_create_user`，事实 #346）：
- 通过 UI 或 API 创建
- 第一个非系统用户自动成为 Owner
- 可以拥有凭证、刷新令牌和组成员资格

**系统用户**（`async_create_system_user`，事实 #347）：
- 由集成或系统内部创建（如 Supervisor、Hass.io 令牌）
- 不能登录 UI
- 只能拥有 `system` 类型的刷新令牌
- 用于服务间认证

### 用户创建与获取

```python
# 创建普通用户，首个用户自动成为 owner
user = await hass.auth.async_create_user("Alice")

# 创建系统用户
sys_user = await hass.auth.async_create_system_user("My Integration")

# 从凭证获取或创建用户（首次登录时）
user = await hass.auth.async_get_or_create_user(credentials)

# 链接凭证到现有用户
await hass.auth.async_link_user(user, new_credentials)
```

`async_deactivate_user()`（事实 #350）停用用户：Owner 不可停用；停用同时移除该用户的所有刷新令牌，立即吊销所有访问权限。

### 权限缓存

`is_owner`、`is_active`、`groups` 属性变更时自动触发 `invalidate_cache()`（事实 #362），清除权限缓存。这确保权限变更立即生效。

## Group：用户组与角色

`Group` 类使用 `attr.s(slots=True)`（事实 #365），包含 `name`、`policy`、`id`、`system_generated`。

### 系统组

HA 预定义三个系统组（事实 #374, #377）：

| 组 ID | 组名 | 权限 |
|-------|------|------|
| `system-admin` | Administrators | 管理员权限 |
| `system-users` | Users | 普通用户权限 |
| `system-read-only` | Read Only | 只读权限 |

### 角色层级

```text
Owner（所有者）
  └─ 隐式拥有所有权限，不可被禁用或降权

Admin（管理员）
  └─ is_admin = is_owner OR (在 admin group 中 AND is_active)

User（普通用户）
  └─ 在 system-users 组中，受权限策略限制

Read Only（只读用户）
  └─ 在 system-read-only 组中，仅可读取状态和调用只读服务
```

`is_admin` 是缓存属性（事实 #364）：owner 返回 True；其他用户检查是否在 admin 组中且 active。

## Permission 权限系统

`permissions` 缓存属性（事实 #363）根据用户角色返回权限策略对象：

- **Owner**：返回 `OwnerPermissions`，无限制
- **其他用户**：合并所有所属 group 的策略（`policy` 字段）

权限策略是一个嵌套字典结构，支持按集成域、实体类别、操作类型细粒度控制。例如，可以配置一个用户只能控制 `light.` 域的实体，只能查看不能修改 `sensor.` 域。

### Unauthorized 异常

当用户执行未授权操作时，抛出 `Unauthorized` 异常（`exceptions.py:317-342`），携带上下文信息：

```python
class Unauthorized(HomeAssistantError):
    context: Context
    user_id: str | None
    entity_id: str | None
    config_entry_id: str | None
    perm_category: str | None
    permission: str | None
```

`UnknownUser(User)` 是其子类，当用户 ID 不存在时抛出。

## RefreshToken：刷新令牌

`RefreshToken` 是长期凭证，定义于 `auth/models.py:103`，使用 `attr.s(slots=True)`。

### 令牌类型

```python
TOKEN_TYPE_NORMAL = "normal"                # 普通刷新令牌（90天有效期）
TOKEN_TYPE_SYSTEM = "system"                # 系统令牌（不过期）
TOKEN_TYPE_LONG_LIVED_ACCESS_TOKEN = "llat"  # 长期访问令牌（不过期，10年）
```

### RefreshToken 属性

```python
@attr.s(slots=True)
class RefreshToken:
    id: str                              # 令牌 ID
    user: User                           # 所属用户
    client_id: str | None                # 客户端 ID（普通令牌必需）
    client_name: str | None              # 客户端名称（LLAT 必需）
    client_icon: str | None              # 客户端图标
    token_type: str                      # 令牌类型
    access_token_expiration: timedelta   # 访问令牌有效期
    created_at: datetime                 # 创建时间
    token: str                           # 令牌值（secrets.token_hex(64)）
    jwt_key: str                         # JWT 签名密钥（secrets.token_hex(64)）
    last_used_at: datetime | None        # 最后使用时间
    last_used_ip: str | None             # 最后使用 IP
    expire_at: float | None              # 过期时间戳
    credential: Credentials | None       # 关联凭证
    version: str                         # 令牌版本
```

`token` 和 `jwt_key` 都通过 `secrets.token_hex(64)` 生成（事实 #367），各 128 位十六进制字符串，确保密码学安全。

### 创建刷新令牌

`async_create_refresh_token()`（事实 #351-353）根据参数创建不同类型的令牌：

```python
# 普通刷新令牌（需要 client_id，90天有效期）
token = await hass.auth.async_create_refresh_token(
    user, client_id="https://my.app/callback"
)

# 长期访问令牌（需要 client_name）
token = await hass.auth.async_create_refresh_token(
    user, client_name="My Script", credential=cred,
    token_type=TOKEN_TYPE_LONG_LIVED_ACCESS_TOKEN,
)
```

约束规则：
- 系统用户只能创建 `system` 类型令牌
- 普通令牌需要 `client_id`，有效期 `REFRESH_TOKEN_EXPIRATION`（90 天）
- 长期访问令牌需要 `client_name`，每个 client_name 只能有一个 LLAT

### 令牌过期清理

AuthManager 通过 `_async_track_next_refresh_token_expiration()`（事实 #358）调度定时任务，在令牌过期时自动清理。过期令牌被吊销后，基于其签发的所有访问令牌立即失效。

## JWT：访问令牌

访问令牌（Access Token）是短期的 JWT（JSON Web Token），用于 API 认证。

### 创建访问令牌

`async_create_access_token()`（事实 #354）从刷新令牌创建 JWT：

```python
def async_create_access_token(
    self, refresh_token: RefreshToken, remote_ip: str | None = None
) -> str:
    # JWT 包含 iss（签发者）、iat（签发时间）、exp（过期时间）
    # 使用 HS256 算法签名，密钥为 refresh_token.jwt_key
```

JWT 的标准声明：
- `iss`：签发者（RefreshToken ID）
- `iat`：签发时间
- `exp`：过期时间（当前时间 + `ACCESS_TOKEN_EXPIRATION` = 30 分钟）
- `jti`：JWT 唯一 ID

访问令牌有效期为 30 分钟（事实 #371，`ACCESS_TOKEN_EXPIRATION = timedelta(minutes=30)`）。

### 验证访问令牌

`async_validate_access_token()`（事实 #355）执行两步验证：

1. 先不解码验证地获取 issuer（RefreshToken ID）
2. 用对应 RefreshToken 的 `jwt_key` 验证 JWT 签名和有效期
3. 允许 10 秒 leeway（时间偏移容差，事实 #356）

这种两步设计避免了用单个全局密钥验证所有令牌，每个刷新令牌有独立的签名密钥。

### JWT 安全防护

`jwt_wrapper.py` 实现了多层安全措施（事实 #381-386）：

- **大小限制**：超过 8192 字节的 token 抛出 `DecodeError("Token too large")`
- **缓存优化**：`lru_cache(16)` 缓存未验证解码和密钥加载结果
- **必需声明**：要求 `exp` 和 `iat` 声明必须存在
- **单例验证器**：模块级 `verify_and_decode` 是配置好的 PyJWT 实例引用

### 令牌撤销

`async_register_revoke_token_callback()`（事实 #357）注册令牌撤销回调。当刷新令牌被删除或用户被停用时，已签发的 JWT 通过撤销机制失效。由于 JWT 本身是无状态的，撤销通过记录被撤销的 token ID 实现。

## AuthStore：持久化存储

`AuthStore` 类定义于 `auth/auth_store.py:44`（事实 #375-380），负责将认证数据持久化到磁盘。

### 存储配置

```python
STORAGE_VERSION = 1
STORAGE_KEY = "auth"
private = True
atomic_writes = True
```

- 数据存储在 `.storage/auth` 文件中
- `private=True` 限制文件权限，保护敏感凭证
- `atomic_writes=True` 确保写入完整性

### 内存索引

AuthStore 维护以下内存映射（事实 #379）：

- `_users`：`dict[str, User]`，用户 ID 到用户对象
- `_groups`：`dict[str, Group]`，组 ID 到组对象
- `_perm_lookup`：权限查找缓存
- `_token_id_to_user_id`：令牌 ID 到用户 ID 的反向映射

### 懒加载

AuthStore 是懒加载的（事实 #380）——构造时不读取磁盘，只有在首次调用需要数据的方法时才从存储加载。这加快了启动速度，因为认证数据通常在第一个 HTTP 请求到达时才需要。

### 首次加载延迟保存

`INITIAL_LOAD_SAVE_DELAY = 300`（5 分钟，事实 #378），首次加载后延迟保存以进行数据迁移。这给了系统时间来规范化旧格式数据，而不阻塞启动。

## 登录流程

`AuthManagerFlowManager` 继承自 `FlowManager`（事实 #359），使用数据录入流（data_entry_flow）框架管理多步登录：

1. 用户提交用户名密码 → 认证提供者验证
2. 若启用 MFA → 进入第二步验证（TOTP 等）
3. 验证通过 → 创建 RefreshToken
4. 返回 RefreshToken 和 AccessToken

`handler_key` 为 `(provider_type, provider_id)` 元组，支持同时配置多个认证提供者。

## 认证提供者与 MFA

### Auth Providers

认证提供者负责验证用户凭证。HA 内置：

- **Home Assistant Provider**：用户名+密码，密码使用 bcrypt 哈希存储
- **Trusted Networks Provider**：基于 IP 地址自动登录
- **Command Line Provider**：通过外部命令验证

每个提供者有独立的配置和 `Credentials` 对象。一个用户可以链接多个提供者的凭证（`async_link_user`），实现多种登录方式。

### MFA Modules

多因素认证模块在密码验证后增加第二层验证：

- **TOTP**：基于时间的一次性密码（Google Authenticator 等）
- **Notify**：通过通知推送验证码

MFA 会话有效期为 5 分钟（`MFA_SESSION_EXPIRATION`，事实 #372）。

## 令牌在 HTTP 层的使用

访问令牌通过 HTTP `Authorization` 头部传递：

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

- REST API：每次请求验证 Bearer token
- WebSocket API：连接时通过 `auth` 命令发送 access_token
- 长期访问令牌可直接用作 Bearer token（无需刷新流程）

测试中 `hass_client` fixture 自动携带认证 Bearer token（事实 #169），`hass_client_no_auth` 提供未认证客户端（事实 #170）。

## 异常层次

```text
HomeAssistantError
├── Unauthorized
│   └── UnknownUser
├── InvalidAuthError
└── ServiceValidationError
    └── ServiceNotFound
```

`InvalidAuthError` 和 `InvalidProvider` 是认证模块的具体异常（事实 #360）。

## 延伸阅读

- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [服务注册表](/concepts/08-service-registry.md)
- [启动流程](/concepts/04-bootstrap-lifecycle.md)
- [配置管理](/concepts/05-configuration.md)

## 相关概念

- [HomeAssistant 核心对象](/concepts/03-core-object.md) — AuthManager 作为 hass.auth 子系统挂载在核心对象上
- [配置系统](/concepts/05-configuration.md) — 认证数据存储在 .storage/auth，受 private 权限保护
- [注册表](/concepts/10-registries.md) — 用户、权限组与实体/设备注册表共同构成 HA 的访问控制基础
