---
id: "pytest-factory-fixture-pattern"
title: "pytest工厂Fixture模式"
type: "code-pattern"
date: "2026-08-22"
maturity: "L2-validated"
source: "pytest-jupyter v0.12.0 (jp_start_kernel, jp_configurable_serverapp, jp_fetch, jp_ws_fetch, jp_create_notebook 等5个工厂fixture)"
related_patterns:
  - "ffi-memory-leak-autouse-fixture"
  - "configurable-by-default-principle"
  - "destruction-protection-isolation"
tags: ["testing", "pytest", "fixture", "factory", "resource-management", "async-testing", "cleanup", "closure"]
validation_count: 1
reuse_count: 0
---

# pytest工厂Fixture模式

## 触发场景

- pytest测试中需要fixture返回**可调用的工厂函数**而非直接资源实例，以便测试函数动态创建多个资源、传入不同配置
- 工厂创建的资源（内核、服务器、文件、连接等）需要在测试结束时自动清理，避免资源泄漏
- 同一测试中需要创建同一类型资源的多个实例（如多个kernel、多个WebSocket连接）
- 资源创建参数需要在测试函数内部动态决定，fixture阶段无法预知
- 需要在一个fixture中封装复杂的初始化+清理逻辑，让测试代码专注于断言

**不适用于**：
- 每个测试只需要一个固定配置的资源实例（直接返回资源即可，不需要工厂）
- 资源创建无参数、无需多实例（普通fixture足够）
- 资源无需清理（简单值fixture如字符串、数字）

## 核心做法

### 模式结构

```python
import pytest

@pytest.fixture
def my_factory_fixture(dependency_fixture1, dependency_fixture2):
    """工厂fixture的标准结构"""
    # 1. 准备阶段：创建资源追踪容器
    created_resources = []

    # 2. 定义内部工厂函数（闭包捕获外层依赖和追踪容器）
    def inner(*args, **kwargs):
        # a. 使用依赖fixture创建资源
        resource = create_resource(*args, **kwargs)
        # b. 将资源加入追踪列表
        created_resources.append(resource)
        # c. 返回资源给测试使用
        return resource

    # 3. yield工厂函数给测试（这是关键——测试拿到的是inner函数）
    yield inner

    # 4. 清理阶段：yield之后执行，销毁所有追踪的资源
    for resource in created_resources:
        cleanup_resource(resource)
```

### 关键要点

1. **外层fixture负责依赖注入和资源追踪**：通过pytest的fixture依赖注入机制获取其他fixture（如事件循环、临时目录）
2. **内层函数（inner）是工厂**：测试调用它时传入参数，创建并返回资源
3. **闭包捕获**：inner函数通过闭包访问外层的依赖fixture和资源追踪列表
4. **yield分割创建与清理**：yield之前是准备阶段（返回工厂给测试），yield之后是清理阶段
5. **多实例追踪**：created_resources列表跟踪所有通过工厂创建的实例，确保全部清理

## pytest-jupyter中的实际案例

### 案例1：jp_start_kernel（内核启动工厂）

```python
@pytest.fixture
def jp_start_kernel(jp_environ, jp_asyncio_loop):
    # 追踪所有创建的KernelManager
    kms = []

    async def start_kernel(
        kernel_name=NATIVE_KERNEL_NAME,
        **kwargs
    ) -> Tuple[KernelManager, KernelClient]:
        km = KernelManager(kernel_name=kernel_name)
        await km.start_kernel(**kwargs)
        kc = km.client()
        kc.start_channels()
        await kc.wait_for_ready()
        kms.append(km)  # 追踪
        return km, kc

    yield start_kernel

    # 清理所有启动的内核
    for km in kms:
        await km.shutdown_kernel(now=True)
        await km.cleanup()
```

**使用方式**：
```python
async def test_two_kernels(jp_start_kernel):
    km1, kc1 = await jp_start_kernel("echo")      # 第一个内核
    km2, kc2 = await jp_start_kernel("python3")   # 第二个内核
    assert km1.is_alive()
    assert km2.is_alive()
    # 测试结束后两个内核都被自动shutdown
```

### 案例2：jp_configurable_serverapp（ServerApp工厂）

```python
@pytest.fixture
def jp_configurable_serverapp(
    jp_asyncio_loop,
    jp_web_app,
    jp_server_config,
    jp_root_dir,
    jp_template_dir,
    jp_argv,
    jp_http_port,
    jp_logging_stream,
    jp_env_config_path,
):
    apps = []

    def _serverapp(config=None, base_url="/", root_dir=""):
        # 合并配置
        c = Config()
        c.merge(jp_server_config)
        if config:
            c.merge(config)

        app = ServerApp.instance(
            config=c,
            base_url=base_url,
            root_dir=root_dir or jp_root_dir,
            port=jp_http_port,
            log=jp_logging_stream,
            # ...更多配置
        )
        app.initialize(jp_argv)
        apps.append(app)
        return app

    yield _serverapp

    # 清理所有ServerApp实例
    for app in apps:
        app.remove_server()
        ServerApp.clear_instance()
```

### 案例3：jp_fetch / jp_ws_fetch（HTTP客户端工厂）

HTTP/Ws客户端工厂略有不同——它们不yield，因为客户端本身无状态（每次fetch创建新的HTTP请求），不需要显式清理：

```python
@pytest.fixture
def jp_fetch(jp_serverapp, http_server_client, jp_auth_header, jp_base_url):
    def client_fetch(*parts, headers=None, params=None, **kwargs):
        # 构建URL（自动拼接base_url）
        path_url = url_escape(url_path_join(*parts), plus=False)
        base_path_url = url_path_join(jp_base_url, path_url)
        url = base_path_url + "?" + urllib.parse.urlencode(params or {})
        # 自动注入认证头（setdefault不覆盖用户传入的headers）
        for key, value in jp_auth_header.items():
            (headers or {}).setdefault(key, value)
        # 默认超时
        request_timeout = kwargs.pop("request_timeout", 20)
        return http_server_client.fetch(
            url, headers=headers, request_timeout=request_timeout, **kwargs
        )
    return client_fetch  # 无资源需清理，直接return
```

**关键差异**：当工厂创建的资源是无状态的（HTTP请求而非长连接），直接return即可，不需要yield+cleanup。但jp_ws_fetch创建WebSocket连接时，连接由tornado的IOLoop管理，fixture通过jp_server_cleanup统一清理。

### 案例4：jp_create_notebook（Notebook创建工厂）

```python
@pytest.fixture
def jp_create_notebook(jp_root_dir):
    nbs = []

    def inner(nbpath):
        nbpath = jp_root_dir.joinpath(nbpath)
        nb = new_notebook()  # 使用nbformat创建空notebook
        nbpath.write_text(nbformat.writes(nb))
        nbs.append(nbpath)
        return nb

    yield inner
    # 文件在tmp_path下，pytest自动清理临时目录，无需手动删除
```

## 反模式

### ❌ 反模式1：工厂忘记追踪资源

```python
@pytest.fixture
def bad_factory(jp_asyncio_loop):
    async def inner():
        km = KernelManager()
        await km.start_kernel()
        return km  # ❌ 没有append到追踪列表！
    yield inner
    # ❌ 测试结束后内核泄漏，不会被shutdown
```

**修复**：始终在inner函数中`created_resources.append(resource)`。

### ❌ 反模式2：清理阶段不使用await（异步资源）

```python
@pytest.fixture
def bad_async_factory(jp_asyncio_loop):
    kms = []
    async def inner():
        km = KernelManager()
        await km.start_kernel()
        kms.append(km)
        return km
    yield inner
    # ❌ 同步遍历，不await shutdown
    for km in kms:
        km.shutdown_kernel(now=True)  # 这是async方法！
```

**修复**：清理阶段使用`jp_asyncio_loop.run_until_complete()`：
```python
    for km in kms:
        jp_asyncio_loop.run_until_complete(km.shutdown_kernel(now=True))
```

### ❌ 反模式3：工厂fixture被session/module级别fixture依赖

```python
@pytest.fixture(scope="session")  # ❌ session级别
def session_resource(jp_start_kernel):  # 依赖function级别fixture
    ...
```

pytest会报错。工厂fixture应该是function scope（默认），每个测试独立创建和清理资源。

### ❌ 反模式4：直接返回资源而非工厂

```python
@pytest.fixture
async def single_kernel(jp_start_kernel):
    km, kc = await jp_start_kernel()
    return km, kc  # ❌ 这样就变成普通fixture了，无法在测试中多次创建
```

如果测试确实只需要一个实例，这是合理的；但如果你需要多实例或动态参数，应该保持工厂模式。

## 与普通Fixture的对比

| 维度 | 普通Fixture | 工厂Fixture |
|------|-----------|------------|
| 返回值 | 直接返回资源实例 | 返回创建资源的可调用函数 |
| 每测试实例数 | 1个 | 0..N个（测试自行决定） |
| 创建参数 | fixture阶段固定 | 测试调用时动态传入 |
| 清理时机 | yield之后 | yield之后遍历追踪列表 |
| 适用场景 | 单实例固定配置 | 多实例/动态配置 |
| 复杂度 | 简单 | 需要闭包+追踪列表 |

## 扩展变体

### 变体1：带配置默认值的工厂

jp_configurable_serverapp展示了这个变体——工厂参数有默认值，测试可选择性覆盖：

```python
def _serverapp(config=None, base_url="/", root_dir=""):
    c = Config()
    c.merge(jp_server_config)  # 基础配置（来自另一个fixture）
    if config:
        c.merge(config)         # 测试传入的覆盖配置
    ...
```

### 变体2：自动注册为autouse清理器

jp_server_cleanup展示了这个变体——autouse fixture确保清理逻辑每个测试都执行：

```python
@pytest.fixture(autouse=True)
def jp_server_cleanup(jp_asyncio_loop):
    yield
    # 每个测试后强制执行清理
    ServerApp.clear_instance()
```

### 变体3：无状态工厂（直接return）

jp_fetch展示了这个变体——工厂创建无状态资源（HTTP请求），无需追踪清理：

```python
@pytest.fixture
def jp_fetch(...):
    def client_fetch(...):
        return http_server_client.fetch(...)
    return client_fetch  # 不需要yield，无资源清理
```

## 迁移指南

如果你有现有的普通fixture想改造为工厂fixture：

1. 在fixture内部定义`created = []`列表
2. 将原来直接创建资源的代码包装到`def inner(...)`中
3. 在inner中`created.append(resource)`
4. 将原来的`return resource`改为`yield inner`
5. 在yield后添加清理循环

## 参考实例

- `pytest_jupyter/jupyter_client.py:jp_start_kernel` — 异步内核工厂
- `pytest_jupyter/jupyter_server.py:jp_configurable_serverapp` — ServerApp配置工厂
- `pytest_jupyter/jupyter_server.py:jp_fetch` — HTTP客户端工厂
- `pytest_jupyter/jupyter_server.py:jp_ws_fetch` — WebSocket工厂
- `pytest_jupyter/jupyter_server.py:jp_create_notebook` — 文件创建工厂
