---
type: Concept
title: 注册表
description: 理解 Home Assistant 注册表体系，包括 DeviceRegistry、EntityRegistry、AreaRegistry 的职责、RegistryStore 持久化机制、DeviceInfo 设备信息结构，以及唯一ID在设备-实体关联中的作用
tags: [home-assistant, smart-home, registry, device-registry, entity-registry, area-registry, core]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: helpers-util-source
    resource: "/references/helpers-util-source.md"
    title: Home Assistant Helpers 与 Util 源码
  - id: facts-helpers
    resource: "/references/facts-helpers.md"
    title: Home Assistant Helpers 事实清单
  - id: facts-core
    resource: "/references/facts-core.md"
    title: Home Assistant Core 事实清单
---

# 注册表

注册表（Registry）是 Home Assistant 中持久化用户自定义配置和元数据的核心子系统。与[状态机](/concepts/07-state-machine.md)保存实体的实时状态不同，注册表保存的是跨重启持久化的数据：设备名称、区域分配、实体禁用状态、自定义实体 ID 等。HA 启动时并行加载所有注册表（事实 #213），它们是用户与系统交互的持久化层。

## 注册表体系概览

HA 有多个注册表，每个负责一类元数据：

| 注册表 | 模块 | 职责 |
|--------|------|------|
| `EntityRegistry` | `helpers/entity_registry.py` | 实体注册信息：自定义ID、名称、区域、设备关联、启用/禁用 |
| `DeviceRegistry` | `helpers/device_registry.py` | 设备注册信息：名称、制造商、模型、固件、连接方式 |
| `AreaRegistry` | `helpers/area_registry.py` | 区域（房间/楼层）定义 |
| `FloorRegistry` | `helpers/floor_registry.py` | 楼层定义 |
| `LabelRegistry` | `helpers/label_registry.py` | 标签分类 |
| `CategoryRegistry` | `helpers/category_registry.py` | 分类管理 |
| `IssueRegistry` | `helpers/issue_registry.py` | 问题/修复追踪 |

所有注册表共享相同的基础设施——`BaseRegistry` 基类和 `Store` 持久化。

## BaseRegistry 基础设施

`BaseRegistry` 定义于 `helpers/registry.py`（事实 #69-80），是所有注册表的抽象基类。

### BaseRegistryItems

`BaseRegistryItems[_EntryT]` 是泛型集合类，管理注册表条目的内存索引：

```python
class BaseRegistryItems:
    def __init__(self):
        self._entries: dict[str, _EntryT] = {}
        self._index: dict[str, dict[str, str]] = {}

    def get(self, key: str) -> _EntryT | None: ...
    def values(self) -> ValuesView[_EntryT]: ...
    def items(self) -> ItemsView[str, _EntryT]: ...
    def __iter__(self) -> Iterator[str]: ...
```

它维护主字典（`id -> entry`）和反向索引（按别名/标识符查找 id）。子类通过实现特定索引方法支持按设备 ID、域名、唯一 ID 等维度快速查找。

### BaseRegistry

`BaseRegistry` 提供通用的数据加载、保存和调度逻辑：

- `async_load()`：从 `Store` 加载持久化数据到内存
- `async_shutdown()`：关闭注册表，保存待写入数据
- 子类实现 `_load_data()` 和 `_data_to_save()` 定制序列化格式
- 通过 `async_call_later` 调度延迟保存，避免频繁磁盘写入

### RegistryStore 持久化

注册表底层使用 `helpers/storage.py` 中的 `Store` 类（事实 #244-256）持久化到 `.storage/` 目录下的 JSON 文件。每个注册表有独立的存储键：

- EntityRegistry: `core.entity_registry`
- DeviceRegistry: `core.device_registry`
- AreaRegistry: `core.area_registry`

Store 的关键特性：

1. **延迟写入**：`async_delay_save()` 合并时间窗口内的多次保存请求，避免高频写入
2. **原子写入**：先写临时文件再重命名，确保数据完整性
3. **版本迁移**：支持主版本迁移（`async_migrate`）和次版本升级（`minor_version`）
4. **私有模式**：`private=True` 限制文件权限为当前用户可读
5. **内存缓存**：维护 `_data` 缓存，避免重复读盘

启动时 `async_load_base_functionality()` 并行加载 area、category、device、entity、floor、issue、label 七个注册表（事实 #213）。

## DeviceRegistry

DeviceRegistry 管理 HA 中所有已知设备的元数据。设备是物理或逻辑设备的抽象——一个灯泡、一个网关、一个软件服务。

### DeviceInfo

集成通过 `DeviceInfo` TypedDict 声明设备信息（事实 #55-68）：

```python
from homeassistant.helpers.device import DeviceInfo

device_info = DeviceInfo(
    identifiers={("hue", "00:17:88:01:02:aa:bb:cc")},
    connections={("mac", "00:17:88:01:02:aa:bb:cc")},
    name="Living Room Lamp",
    manufacturer="Signify",
    model="Hue White A19",
    sw_version="1.50.2",
    hw_version="rev 3",
    suggested_area="Living Room",
    via_device=(DOMAIN, bridge_id),
    configuration_url="http://192.168.1.100",
    entry_type=DeviceEntryType.SERVICE,
    serial_number="ABC123",
)
```

关键字段：

- **identifiers**：`set[tuple[str, str]]`，集成内部唯一标识符元组集合，格式为 `(integration_domain, unique_id)`。这是设备匹配的主要依据
- **connections**：`set[tuple[str, str]]`，设备连接元组集合，如 MAC 地址、网络连接
- **via_device**：父设备标识符（网关/桥接器），构建设备拓扑
- **manufacturer / model / sw_version / hw_version**：设备硬件和固件元数据
- **suggested_area**：建议的区域名称（首次发现时使用，不覆盖用户设置）
- **configuration_url**：设备配置页面链接，可为字符串或 ConfigEntry
- **entry_type**：设备条目类型（`DeviceEntryType` 枚举）

### 设备匹配与合并

DeviceRegistry 使用 identifiers 和 connections 进行设备匹配：

1. 集成首次上报设备时，通过 identifiers 查找已有设备
2. 若找到，更新设备信息（合并字段）
3. 若未找到，创建新设备条目
4. connections 用于跨集成匹配同一物理设备（如 Hue 集成和 ZHA 集成都看到同一 MAC 地址）

`async_device_info_to_dr_device_info()` 函数（事实 #57）将集成声明的 DeviceInfo TypedDict 转换为设备注册表内部格式。

### 设备查询辅助函数

`helpers/device.py` 提供常用查询函数（事实 #60-63）：

```python
from homeassistant.helpers import device_registry as dr

# 根据实体 ID 查找关联的设备条目
device = dr.async_entries_for_config_entry(hass, config_entry_id)

# 获取配置条目关联的所有设备
devices = dr.async_entries_for_config_entry(hass, entry.entry_id)

# 从 HA 中移除设备（清理注册表和实体）
await dr.async_remove_device_from_hass(hass, device_id)

# 根据实体 ID 获取设备信息条目
device_entry = dr.async_entity_device_info_entry(hass, entity_id)

# 获取实体所属配置条目 ID
entry_id = dr.async_entity_config_entry_id(hass, entity_id)
```

## EntityRegistry

EntityRegistry 跟踪每个具有 `unique_id` 的实体。它保存用户对实体的自定义修改，这些修改独立于集成代码。

### 注册流程

当实体平台添加实体时：

1. 实体提供 `unique_id`（必须在同一域名和配置条目内唯一）
2. EntityRegistry 查找 `(domain, unique_id, config_entry_id)` 匹配的已有条目
3. 若存在，恢复用户自定义的 entity_id、名称、区域等
4. 若不存在，创建新条目，使用实体建议的 ID 和名称

### EntityRegistryEntry

注册表条目存储以下信息（通过 `helpers/entity_registry.py`）：

- `entity_id`：当前实体 ID（用户可能已自定义）
- `unique_id`：集成提供的稳定唯一标识
- `platform`：所属平台域名
- `name`：用户自定义名称（None 表示使用集成建议值）
- `icon`：用户自定义图标
- `device_id`：关联的设备 ID
- `area_id`：区域 ID
- `disabled_by`：禁用来源（用户/集成/配置条目）
- `hidden_by`：隐藏来源
- `entity_category`：实体分类（config/diagnostic）
- `config_entry_id`：所属配置条目
- `original_name` / `original_icon`：集成提供的原始值
- `capabilities` / `supported_features`：实体能力快照
- `translation_key`：翻译键

### 关键操作

```python
from homeassistant.helpers import entity_registry as er

# 获取注册表实例
ent_reg = er.async_get(hass)

# 按 entity_id 查找条目
entry = ent_reg.async_get("light.living_room")

# 按 unique_id 查找
entry = ent_reg.async_get_entity_id("light", "hue", "00:17:88:01:aa:bb:cc")

# 更新实体（修改名称、区域、禁用等）
ent_reg.async_update_entity(
    "light.living_room",
    name="My Light",
    area_id="living_room",
    new_entity_id="light.lamp",
)

# 移除条目
ent_reg.async_remove("light.old_entity")
```

### 实体禁用与启用

实体可以被多方禁用：

- 用户手动禁用（`disabled_by=user`）
- 集成通过配置禁用
- 配置条目卸载时禁用相关实体

被禁用的实体不会被创建，状态机中不存在对应记录。

## AreaRegistry

AreaRegistry 管理区域——房屋中的物理空间（客厅、卧室、厨房）。

### AreaEntry

区域条目包含：

- `id`：slug 格式的区域标识
- `name`：区域显示名称
- `floor_id`：所属楼层 ID
- `icon`：区域图标
- `aliases`：别名集合（用于语音助手匹配）
- `picture`：区域图片

### 区域与设备/实体的关联

区域分配是多对一关系：

- 设备可以分配到区域（`DeviceEntry.area_id`）
- 未关联设备的实体可以单独分配到区域（`EntityRegistryEntry.area_id`）
- 通过 `ServiceTarget(area_id="living_room")` 可以一次性对区域内所有实体调用服务

启动时 AreaRegistry 是最早加载的注册表之一，因为 DeviceRegistry 和 EntityRegistry 都引用它。

## DeviceConnection 与 DeviceIdentifier

设备匹配使用两种元组类型（事实 #58-59）：

```python
# 连接：(连接类型, 标识符)
DeviceConnection = tuple[str, str]
# 如 ("mac", "aa:bb:cc:dd:ee:ff")
# 如 ("zigbee", "00:11:22:33:44:55:66:77")

# 标识符：(集成域名, 唯一ID)
DeviceIdentifier = tuple[str, str]
# 如 ("hue", "00:17:88:01:02:aa:bb:cc")
# 如 ("zwave_js", "32-49-52-15")
```

`identifiers` 是集成内部的设备主键，`connections` 支持跨集成设备识别。一个设备可以同时拥有多个 identifier（来自不同集成）和多个 connection。

## 唯一ID 的重要性

`unique_id` 是连接实体模型与注册表的关键桥梁。它必须满足：

1. **稳定性**：同一设备的同一实体重启后 unique_id 不变
2. **唯一性**：在同一 `(domain, platform)` 或 `(domain, config_entry_id)` 范围内唯一
3. **持久性**：不依赖可能变化的因素（如 IP 地址）

没有 unique_id 的实体：
- 不会被 EntityRegistry 跟踪
- 用户无法自定义实体 ID、名称或区域
- 重启后用户自定义设置丢失
- 在 hassfest 质量检查中，`entity-unique-id` 是 BRONZE 等级要求

好的 unique_id 示例：设备序列号 + 端点编号、MAC 地址 + 通道号。差的示例：设备名称、IP 地址。

## 注册表与启动流程

注册表在启动的基础功能阶段并行加载（事实 #213）：

```python
async def async_load_base_functionality(hass):
    await asyncio.gather(
        area_registry.async_load(hass),
        category_registry.async_load(hass),
        device_registry.async_load(hass),
        entity_registry.async_load(hass),
        floor_registry.async_load(hass),
        issue_registry.async_load(hass),
        label_registry.async_load(hass),
    )
```

加载顺序无依赖要求——各注册表独立读取自己的存储文件。但加载完成后，设备注册表和实体注册表之间存在逻辑关联（实体引用设备 ID）。

启动过程中还有 15 个存储键被预加载以加速启动（事实 #215，`PRELOAD_STORAGE`）。

## 注册表信号与更新

注册表数据变更时，会通过 dispatcher 发送信号：

- `EntityRegistry`：`SIGNAL_ENTITY_REGISTRY_UPDATED`
- `DeviceRegistry`：`SIGNAL_DEVICE_REGISTRY_UPDATED`

前端通过 WebSocket API 监听这些信号，实时更新 UI。集成也可以监听注册表变更以响应实体/设备的修改。

## 测试中的注册表

测试框架提供模拟注册表的工具（事实 #189）：

```python
from tests.common import mock_registry, mock_device_registry, mock_area_registry

# 创建模拟实体注册表
ent_reg = mock_registry(hass, {
    "light.test": RegistryEntry(entity_id="light.test", ...),
})

# 创建模拟设备注册表
dev_reg = mock_device_registry(hass, {
    "device_id": DeviceEntry(id="device_id", ...),
})
```

snapshot 测试中，序列化器会将 entry 的 `id`、`config_entry_id`、`device_id` 等替换为 `ANY`（事实 #206-209），避免因 UUID 变化导致快照不稳定。

## 延伸阅读

- [实体模型](/concepts/09-entity-model.md)
- [状态机](/concepts/07-state-machine.md)
- [配置管理](/concepts/05-configuration.md)
- [启动流程](/concepts/04-bootstrap-lifecycle.md)

## 相关概念

- [实体模型](/concepts/09-entity-model.md) — Entity 的 unique_id 与 EntityRegistry 关联，实现实体管理
- [配置系统](/concepts/05-configuration.md) — 注册表数据持久化在 .storage/ 目录的 JSON 文件中
- [配置流](/concepts/15-config-flow.md) — ConfigEntry 为设备和实体提供配置入口关联
