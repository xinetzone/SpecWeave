---
type: Concept
title: 测试模式
description: 掌握 Home Assistant pytest 配置、conftest fixtures（hass/hass_client/snapshot）、tests/common.py 测试工具、syrupy 快照测试、MockConfigEntry、enable_custom_integrations、禁网/DNS 限制与 verify_cleanup 资源泄漏检测
tags: [home-assistant, smart-home, testing, pytest, syrupy, snapshot, mock, fixtures, conftest, quality]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: tooling-source
    resource: "/references/tooling-source.md"
    title: Home Assistant 工具链源码
  - id: facts-tooling
    resource: "/references/facts-tooling.md"
    title: Home Assistant 工具链与测试事实清单
---

# 测试模式

Home Assistant 拥有极其严格的测试基础设施，这是管理 2000+ 集成质量的关键保障。测试基于 pytest + pytest-asyncio，配合丰富的 conftest fixtures、测试替身（test doubles）和 syrupy 快照测试。测试环境默认禁网、检测资源泄漏、自动清理残留任务和定时器。理解这些测试模式是开发高质量 HA 集成的必备技能。

## pytest 配置

pytest 配置位于 `pyproject.toml` 的 `[tool.pytest.ini_options]` 段（事实 #136-145）：

```toml
[tool.pytest.ini_options]
pythonpath = ["pylint/plugins"]
testpaths = ["tests"]
norecursedirs = [".git", "testing_config"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
asyncio_debug = true
filterwarnings = [
    "error::sqlalchemy.exc.SAWarning",
]
```

关键配置说明：

- **`asyncio_mode = "auto"`**：启用 pytest-asyncio 自动模式，无需 `@pytest.mark.asyncio` 装饰器即可编写异步测试函数。所有 `async def test_*` 函数自动被识别为异步测试。
- **`asyncio_default_fixture_loop_scope = "function"`**：每个测试函数使用独立的事件循环，测试间互不干扰。
- **`asyncio_debug = true`**：启用 asyncio 调试模式，检测未 await 的协程和阻塞调用。
- **`filterwarnings`**：将 SQLAlchemy SAWarning 升级为错误，防止 ORM 使用问题被忽略。
- **`pythonpath`**：将 pylint 插件目录加入 Python 路径。

自定义 pytest 选项（事实 #144）：
- `--dburl`：数据库连接 URL，默认 `sqlite://`（内存数据库）
- `--drop-existing-db`：删除已有数据库重建
- marker `no_fail_on_log_exception`：标记测试不因日志中的异常而失败（事实 #145）

测试依赖版本固定（事实 #255）：pytest==9.0.3、pytest-asyncio==1.4.0、pytest-aiohttp==1.1.1、pytest-xdist==3.8.0、pytest-cov==7.1.0、syrupy==5.3.2、freezegun==1.5.5、respx==0.23.1、pytest-socket==0.8.0。

## conftest.py 全局 fixtures

`tests/conftest.py` 是 HA 测试的核心，提供了大量自动和显式 fixtures。

### 导入时 Monkey-patch

conftest.py 在导入 HA 之前先导入三个 patch 模块进行 monkey-patch（事实 #146）：

- **`patch_json`**：替换 `json_helper.json_encoder_default`，检测 mock 对象序列化并抛出 TypeError；使用 `orjson.dumps` 替换 `json_bytes` 和 `json_bytes_sorted`（事实 #220-221）
- **`patch_time`**：提供 `HAFakeDate` 和 `HAFakeDatetime` 类，扩展 freezegun 以支持 `fold` 属性（事实 #222-223）
- **`patch_recorder`**：包装 `recorder_helper.session_scope` 为可 patch 的上下文管理器，必须在 recorder.util 导入前执行（事实 #224-225）

### 禁网与 DNS 限制

测试环境默认禁止网络访问（事实 #149-150）。`pytest_runtest_setup()` 中配置 pytest_socket：
- 仅允许连接 `127.0.0.1`（本地回环）
- 允许 Unix socket
- 其他所有 socket 连接被阻止

DNS 解析同样被限制：
- 仅允许 `localhost`、`127.0.0.1`、`::1`、`0.0.0.0` 等本地地址
- 其他主机名抛出 `RuntimeError("DNS resolution disabled in tests")`

`HASocketBlockedError` 继承自 `pytest_socket.SocketBlockedError`，维护 `instances` 类变量计数（事实 #151）。需要网络访问的测试应使用 `respx`（HTTP mock）或 `aiohttp_client`（测试 HTTP 端点），而非真实网络调用。

### verify_cleanup：资源泄漏检测

`verify_cleanup` 是 `@pytest_asyncio.fixture(autouse=True)`，在每个测试后自动检查资源清理（事实 #157）：

- **残留任务**：检查事件循环中未完成的 asyncio Task
- **残留定时器**：检查未取消的 `TimerHandle`
- **残留线程**：检查未结束的线程
- **时区恢复**：验证默认时区恢复为 UTC
- **respx mock 清理**：验证 `respx.mock.routes` 为空，否则提示使用 `@respx.mock` 装饰器（事实 #160）
- **socket 连接**：检查未关闭的 socket 连接

当检测到 ≥2 个未停止 INSTANCES 时调用 `pytest.exit()` 中止测试运行（事实 #158）。`INSTANCES` 是 `tests/common.py` 中的全局列表，跟踪所有创建的 HA 测试实例（事实 #176）。

`expected_lingering_tasks` 和 `expected_lingering_timers` 是 autouse fixture（事实 #154），可通过 parametrize 设为 True 来绕过清理检查。非 platform 组件的 lingering timers 默认允许（事实 #155）。

### 其他 autouse fixtures

- **`garbage_collection`**（scope="module"）：在每个模块前后执行 `gc.collect()` 和 `gc.freeze()`（事实 #153）
- **`enable_event_loop_debug`**：启用事件循环调试（事实 #156）
- **`reset_globals`**：测试后重置 `_Hass` threading.local 和 frame helper 全局变量（事实 #161）
- **`bcrypt_cost`**（scope="session"）：将 bcrypt rounds 从 12 降为 4 以加速测试（事实 #162）
- **`caplog`**：被覆盖，设置日志级别为 DEBUG（事实 #152）

## hass fixture

`hass` 是最核心的 async fixture（事实 #167-168），创建一个测试用的 `HomeAssistant` 实例：

```python
async def test_something(hass: HomeAssistant) -> None:
    assert hass.state == CoreState.running
```

`hass` fixture 依赖 `hass_fixture_setup`、`load_registries`、`hass_config_dir`、`hass_storage`、`mock_recorder_before_hass`。它调用 `async_test_home_assistant()` 创建实例，设置异常处理器，预加载 homeassistant 翻译（事实 #167）。

`load_registries` fixture 控制是否加载注册表，可通过 `@pytest.mark.parametrize("load_registries", [False])` 跳过（事实 #164）。`hass_storage` fixture 包装 `mock_storage()` 上下文管理器（事实 #163）。

## HTTP 客户端 fixtures

- **`hass_client`**：返回已认证的 HTTP 客户端，自动携带 Bearer token（事实 #169）。用于测试需要认证的 API 端点。
- **`hass_client_no_auth`**：返回未认证的 HTTP 客户端（事实 #170）。用于测试公开端点或认证流程。
- **`aiohttp_client_cls`**：返回 `CoalescingClient` 类，模拟 WebSocket JS 客户端的消息合并行为（事实 #165）。
- **`aiohttp_client`**：覆盖 pytest-aiohttp 默认实现，支持 Application/BaseTestServer 参数（事实 #166）。

`CoalescingResponse` 模拟 WebSocket 客户端的 JSON 数组合并行为（事实 #233），确保测试与前端实际行为一致。

## snapshot：syrupy 快照测试

HA 使用 syrupy 进行快照测试，`snapshot` fixture 覆盖了 syrupy 默认实现，使用 `HomeAssistantSnapshotExtension` 扩展（事实 #173）。

### 基本用法

```python
async def test_entity_state(hass, snapshot):
    state = hass.states.get("light.kitchen")
    assert state == snapshot
```

首次运行时，syrupy 会将实际值序列化为快照文件（存放在 `snapshots/` 目录而非默认的 `__snapshots__/`，事实 #216）。后续运行比较实际值与快照，不匹配则测试失败。更新快照使用 `pytest --snapshot-update`。

### HomeAssistantSnapshotSerializer

自定义序列化器 `HomeAssistantSnapshotSerializer`（tests/syrupy.py:76）处理 HA 特殊数据类型，自动将动态值替换为 `ANY`（事实 #205-214）：

| 数据类型 | 替换为 ANY 的字段 |
|----------|-------------------|
| `State` | `context`、`last_changed`、`last_reported`、`last_updated` |
| `ConfigEntry` | `entry_id`；移除 `created_at`/`modified_at` |
| `DeviceEntry` | `config_entries`、`id`、`via_device_id`、`primary_config_entry` |
| `EntityRegistryEntry` | `config_entry_id`、`device_id`、`id` |
| `AreaEntry` | `id` |
| `IssueEntry` | `created` |
| `FlowResult` | `flow_id` |

这种设计解决了快照测试最常见的脆弱性问题——动态 ID 和时间戳导致每次运行快照都不同。序列化器还支持：
- `vol.Schema` 通过 `voluptuous_serialize.convert()` 序列化（事实 #213）
- dataclass 通过 `dataclasses.asdict()`（事实 #214）
- attrs 类通过 `attrs.asdict()`（事实 #214）
- `_IntFlagWrapper` 规范化 IntFlag 的 repr，消除 Python 3.10/3.11 差异（事实 #215）

`VERSION = "1"` 是序列化格式版本，变更序列化逻辑时需 bump（事实 #217）。`override_syrupy_finish()` 覆盖 syrupy 默认 finish 方法以支持 pytest-xdist 并行测试的快照合并（事实 #218）——xdist worker 将结果写入 `.pytest_syrupy_<worker>_result` JSON 文件，controller 合并后删除（事实 #219）。

## tests/common.py 测试工具

`tests/common.py` 模块文档为 `"Test the helper method for writing tests."`（事实 #175），提供了丰富的测试工具和替身。

### MockConfigEntry

`MockConfigEntry` 继承自 `config_entries.ConfigEntry`，提供测试默认值（事实 #192）：

```python
from tests.common import MockConfigEntry

entry = MockConfigEntry(
    domain="my_integration",
    title="Test Device",
    data={"host": "192.168.1.1", "api_key": "test"},
    unique_id="device-123",
)
entry.add_to_hass(hass)
await hass.config_entries.async_setup(entry.entry_id)
```

默认值为 `domain="test"`、`title="Mock Title"`、`source=SOURCE_USER`。关键方法：

- **`add_to_hass(hass)`**：将条目直接添加到 `hass.config_entries._entries`（事实 #193）
- **`mock_state(state)`**：调用 `_async_set_state()` 设置条目状态（如 LOADED/SETUP_ERROR）（事实 #194）
- **`start_reauth_flow()`**：启动重新认证流程（事实 #195）
- **`start_reconfigure_flow()`**：启动重新配置流程（事实 #195）

### async_test_home_assistant

`async_test_home_assistant()` 是创建测试 HA 实例的核心异步函数（事实 #182）。通常通过 `hass` fixture 间接使用，但在需要自定义配置时可直接调用。

### 模拟工具

- **`async_mock_service(hass, domain, service)`**：异步注册模拟服务并返回调用记录列表（事实 #183）。用于验证服务是否被调用及调用参数。
- **`mock_component(hass, domain)`**：标记集成为已加载（通过设置 `hass.data[DATA_COMPONENTS]`）（事实 #188）
- **`mock_registry()`/`mock_area_registry()`/`mock_device_registry()`**：创建模拟注册表（事实 #189）
- **`mock_storage()`**：上下文管理器模拟存储层，返回存储数据字典（事实 #199）
- **`flush_store(hass)`**：异步刷新 Store 数据（事实 #200）
- **`mock_restore_cache()`/`mock_restore_cache_with_extra_data()`**：模拟状态恢复缓存（事实 #197）

### 时间测试

- **`async_fire_time_changed_exact(hass, datetime)`**：在精确时间触发时间变更事件（事实 #184）
- **`async_fire_time_changed(hass, datetime)`**：触发时间变更事件，用于测试定时器和调度逻辑（事实 #184、#229）

```python
from tests.common import async_fire_time_changed
from datetime import timedelta

async def test_coordinator_refresh(hass, coordinator):
    await coordinator.async_refresh()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=5))
    await hass.async_block_till_done()
```

### Fixture 文件工具

- **`get_test_config_dir()`**：返回 `tests/testing_config` 路径（事实 #180）
- **`get_fixture_path(integration, filename)`**：返回测试 fixture 文件路径，支持 `integration` 参数定位 `tests/components/<integration>/` 下的 fixture（事实 #185）
- **`load_fixture(filename, integration)`**/`**load_fixture_bytes()`**：读取 fixture 文件内容（事实 #186）
- **`load_json_value_fixture()`/`load_json_array_fixture()`/`load_json_object_fixture()`**：加载 JSON 标量/数组/对象 fixture（事实 #187）

### Mock 类

- **`MockGroup`** 和 **`MockUser`**：auth 模型的测试替身（事实 #190）
- **`MockModule`** 和 **`MockPlatform`**：模拟集成模块和平台（事实 #191）
- **`MockEntity`**：实体测试基类（事实 #198）
- **`StoreWithoutWriteLoad`**：不写入不加载的 Store 测试替身（事实 #181）
- **`threadsafe_callback_factory()`/`threadsafe_coroutine_factory()`**：将回调/协程转换为线程安全版本（事实 #179）

### 其他工具

- **`assert_setup_component(domain, config)`**：上下文管理器，验证组件设置次数（事实 #196）
- **`patch_yaml_files(files)`**：上下文管理器临时替换 YAML 文件内容（事实 #201）
- **`CLIENT_ID`/`CLIENT_REDIRECT_URI`**：OAuth 测试常量（事实 #177）
- **`QualityScaleStatus`**：StrEnum，值为 done/exempt/todo（事实 #178）

`tests/components/common.py` 还提供了 `target_entities()` 辅助函数，创建关联 area/device/label 的测试实体（事实 #202），以及 `parametrize_target_entities()` 返回参数化测试数据，覆盖 entity_id/label_id/area_id/floor_id 等目标类型（事实 #203）。

## enable_custom_integrations

`enable_custom_integrations` fixture（事实 #171）通过清除 `DATA_CUSTOM_COMPONENTS` 缓存启用测试目录中的自定义集成。集成测试通常需要此 fixture：

```python
async def test_custom_integration(hass, enable_custom_integrations):
    assert await async_setup_component(hass, "my_custom", {})
```

其他默认返回 False 的开关 fixture（可通过 parametrize 启用，事实 #172）：
- `enable_statistics`
- `enable_missing_statistics`
- `enable_schema_validation`
- `enable_nightly_purge`

## 典型测试模式

### ConfigEntry 测试

```python
from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.const import Platform

async def test_setup_entry(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain="my_integration",
        data={"host": "192.168.1.1"},
        unique_id="abc123",
    )
    entry.add_to_hass(hass)

    with patch("my_integration.MyAPI.connect") as mock_connect:
        mock_connect.return_value = AsyncMock()
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert "my_integration" in hass.config.components
```

### 平台实体测试

```python
async def test_light_entity(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain="my_integration", data={...})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("light.test_light")
    assert state is not None
    assert state.state == STATE_OFF

    await hass.services.async_call(
        Platform.LIGHT,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_light"},
        blocking=True,
    )
    assert hass.states.get("light.test_light").state == STATE_ON
```

### ConfigFlow 测试

```python
async def test_flow_user(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        "my_integration", context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with patch("my_integration.config_flow.validate_input", return_value={"title": "Test"}):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"host": "192.168.1.1", "api_key": "key"}
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test"
```

### 快照测试

```python
async def test_diagnostics(hass: HomeAssistant, hass_client, snapshot) -> None:
    entry = MockConfigEntry(domain="my_integration", data={...})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    client = await hass_client()
    response = await client.get(f"/api/diagnostics/config_entry/{entry.entry_id}")
    assert response.status == 200
    data = await response.json()
    assert data == snapshot
```

### 网络 Mock

使用 `respx` mock HTTP 请求（事实 #160 要求使用 `@respx.mock` 装饰器）：

```python
import respx

@respx.mock
async def test_api_call(hass: HomeAssistant) -> None:
    route = respx.get("https://api.example.com/status").mock(
        return_value=httpx.Response(200, json={"online": True})
    )
    # ... 测试逻辑
    assert route.called
```

### 设备注册表测试

```python
from homeassistant.helpers import device_registry as dr

async def test_device_registration(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain="my_integration", data={...})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(
        identifiers={("my_integration", "device-123")}
    )
    assert device is not None
    assert device.manufacturer == "Example Inc."
```

## 测试目录结构

每个集成的测试位于 `tests/components/<domain>/`：

```text
tests/components/my_integration/
├── __init__.py
├── conftest.py          # 集成级 fixtures（可选）
├── test_config_flow.py  # ConfigFlow 测试
├── test_init.py         # async_setup_entry 测试
├── test_light.py        # light 平台测试
├── test_sensor.py       # sensor 平台测试
├── snapshots/           # syrupy 快照文件
│   ├── test_config_flow.ambr
│   └── test_light.ambr
└── fixtures/            # 测试数据文件（可选）
    └── device_response.json
```

hassfest 的 codeowners 验证器如果发现 `tests/components/<domain>/__init__.py` 存在，会同时生成测试目录的 CODEOWNERS 条目（事实 #120）。

## CI 中的测试

CI 工作流（`.github/workflows/ci.yaml`）将测试分为 10 个组并行运行（事实 #265）。变更仅涉及单个集成时，仅运行相关集成测试（`test_group_count=1`），不运行 MariaDB/PostgreSQL 矩阵（事实 #263）；核心文件变更或 full 输入触发全量测试（10 个分组，所有数据库版本，事实 #264）。

MariaDB 测试矩阵包含 6 个版本，PostgreSQL 包含 2 个版本（事实 #266-267）。CI 环境变量设置 `PYTHONASYNCIODEBUG=1`、`HASS_CI=1`、`SQLALCHEMY_WARN_20=1`（事实 #259）。

## 最佳实践

1. **使用 hass fixture，不要手动创建 HomeAssistant**：`hass` fixture 配置了正确的异常处理器、存储 mock 和清理逻辑。
2. **异步测试无需装饰器**：`asyncio_mode = "auto"` 使 `async def test_*` 自动成为异步测试。
3. **调用 `await hass.async_block_till_done()`**：在触发服务调用、状态变更后，等待所有待处理任务完成。
4. **网络访问必须 mock**：使用 `respx` mock HTTP 请求，不要依赖真实网络。测试环境禁网。
5. **快照测试不硬编码 ID**：序列化器自动替换 entry_id/device_id/时间戳为 ANY，直接 `assert result == snapshot` 即可。
6. **使用 MockConfigEntry**：不要手动构造 ConfigEntry，使用 MockConfigEntry 并调用 `add_to_hass(hass)`。
7. **测试后自动清理**：`verify_cleanup` autouse fixture 会检测残留任务/定时器/线程，确保测试隔离。
8. **时间逻辑用 async_fire_time_changed**：不要用 `freezegun` 直接冻结时间（HA 有自己的 `patch_time` 扩展），使用 `async_fire_time_changed` 推进时间。
9. **ConfigFlow 测试覆盖所有步骤**：测试 user、discovery、reauth、reconfigure 流程，以及错误和中止情况。
10. **使用 `@respx.mock` 装饰器**：不要手动创建/清理 respx mock，装饰器自动管理生命周期。

## 延伸阅读

- [hassfest 工具链](/concepts/17-hassfest-tooling.md)
- [集成架构](/concepts/14-component-architecture.md)
- [配置流](/concepts/15-config-flow.md)
- [平台开发模式](/concepts/16-platform-pattern.md)
- [启动流程](/concepts/04-bootstrap-lifecycle.md)

## 相关概念

- [集成架构](/concepts/14-component-architecture.md) — 测试 async_setup_entry、async_unload_entry 等集成生命周期函数
- [配置流](/concepts/15-config-flow.md) — 使用 MockConfigEntry 测试 ConfigFlow 的各步骤和迁移逻辑
- [平台开发模式](/concepts/16-platform-pattern.md) — 测试各平台 Entity 的状态更新、服务调用和 supported_features
- [hassfest 工具链](/concepts/17-hassfest-tooling.md) — hassfest 验证测试文件完整性，与 pytest 共同构成质量保障体系
