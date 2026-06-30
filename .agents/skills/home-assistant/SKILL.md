---
name: home-assistant
version: 1.0.0
description: "Home Assistant智能家居系统集成。当用户需要控制智能家居设备、查询设备状态、调用HA服务、管理HA集成配置、使用ha_api脚本时，必须使用此技能。支持通过REST API与Home Assistant交互，实现设备控制、状态查询、服务调用等核心功能。本技能为可选模块，不集成本技能时核心系统能正常运行。"
argument-hint: "<操作类型> [实体ID/服务名]"
disable-model-invocation: false
user-invocable: true
paths:
  - .agents/scripts/ha_api.py
---

# Home Assistant 智能家居集成 (Home Assistant Integration)

## 1. Skill ID
`home-assistant`

## 2. 功能描述

与 Home Assistant 智能家居系统交互的技能，支持通过 REST API 实现以下核心功能：

| 功能 | 说明 |
|------|------|
| **设备状态查询** | 获取指定实体的当前状态（开关、亮度、温度等） |
| **设备控制** | 控制设备状态（打开/关闭灯光、调节亮度、设置温度等） |
| **服务调用** | 调用 Home Assistant 服务（如 `light.turn_on`、`climate.set_temperature`） |
| **实体列表** | 获取所有已注册实体列表 |
| **HA状态** | 检查 Home Assistant 连接状态和版本信息 |

> **为什么？** Home Assistant 是智能家居领域最流行的开源平台，通过标准化 API 交互可实现跨品牌设备的统一控制。本技能将复杂的 API 调用封装为简单的指令，降低使用门槛。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "控制设备"、"打开灯光"、"关闭插座"、"调节亮度"、"设置温度"
- "查询状态"、"设备状态"、"当前温度"、"灯光状态"
- "调用服务"、"HA服务"、"Home Assistant"、"智能家居"
- "ha_api"、"HA集成"、"智能家居控制"

> **关于触发**：即使没有明确说"用 skill"，只要涉及 Home Assistant 操作就应该使用本技能，不要自己手动拼接 API 请求。

## 4. 方案选择决策

```
需要操作Home Assistant？
├─ 需要查询状态？ → ha_api.py status/get
├─ 需要控制设备？ → ha_api.py set/服务调用
├─ 需要获取实体列表？ → ha_api.py list
└─ HA连接不可用？ → 提示配置HA参数（优雅降级）
```

> **为什么优先使用 ha_api.py？** 脚本方案支持配置化参数、错误处理和重试机制，比手动构造 API 请求更可靠。

## 5. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| operation | string | 是 | - | `status`/`get`/`set`/`service`/`list`/`info` |
| entity_id | string | 否 | - | 实体ID（如 `light.living_room`） |
| service | string | 否 | - | 服务名（如 `light.turn_on`） |
| value | any | 否 | - | 设置值（如 `true`、`50`、`25`） |
| dry_run | boolean | 否 | false | 试运行不提交（**写操作强烈建议先开**） |
| ha_url | string | 否 | - | Home Assistant URL（覆盖配置） |
| ha_token | string | 否 | - | API Token（覆盖配置） |

## 6. 可选模块说明

**本技能为可选模块**：
- 不集成本技能时，核心系统能正常运行且不受影响
- HA 连接不可用时，提供友好的错误提示和降级方案
- 采用条件加载机制，仅在配置了 HA 连接参数时激活

## 7. 依赖与前置准备

- **脚本依赖**：Python 3.8+，`requests` 库（`pip install requests`）
- **配置文件**：`.env` 文件（或环境变量）配置 HA_URL 和 HA_TOKEN
- **HA API 权限**：Long-lived Access Token（在 HA 中创建：用户配置 → 安全 → 长期访问令牌）

配置示例：
```bash
# .env 文件或环境变量
HA_URL=http://homeassistant.local:8123
HA_TOKEN=your_long_lived_access_token_here
```

> **为什么需要 Long-lived Token？** Home Assistant 不支持永久 Token，Long-lived Token 是最常用的认证方式，有效期可设置为一年或更长。

## 8. 常用命令速查

脚本路径：[ha_api.py](../../scripts/ha_api.py)

```bash
cd d:\AI

# 检查HA连接状态
python .agents/scripts/ha_api.py info

# 获取实体列表
python .agents/scripts/ha_api.py list

# 查询设备状态
python .agents/scripts/ha_api.py get light.living_room

# 控制设备（先dry-run预览！）
python .agents/scripts/ha_api.py set light.living_room --value true --dry-run
python .agents/scripts/ha_api.py set light.living_room --value true

# 设置亮度（0-255）
python .agents/scripts/ha_api.py set light.living_room --brightness 128

# 调用服务
python .agents/scripts/ha_api.py service light.turn_on --entity-id light.living_room

# 详细输出
python .agents/scripts/ha_api.py --verbose get sensor.temperature
```

## 9. 脚本内置安全机制

- **dry-run**：所有写操作支持 `--dry-run`，展示请求但不提交——防止误操作的最重要防线
- **配置化参数**：支持 .env 文件和环境变量，避免硬编码敏感信息
- **错误处理**：连接失败、认证错误等场景提供明确错误信息
- **优雅降级**：HA 连接不可用时返回友好提示，不影响核心系统
- **日志记录**：详细操作日志，便于排障

## 10. 操作步骤

### 10.1 查询设备状态 (get)

```
步骤1: 确认HA连接参数已配置
步骤2: 执行 ha_api.py get <entity_id>
步骤3: 解析返回的JSON数据，提取状态信息
步骤4: 向用户展示状态结果
```

### 10.2 控制设备 (set)

> **为什么要先dry-run？** 设备控制是写操作，错误操作可能导致设备状态异常（如关闭重要设备）。dry-run 在不实际执行的情况下展示完整请求，是成本最低的防误操作手段。

```
步骤1: 确认HA连接参数已配置
步骤2: 执行 ha_api.py set <entity_id> --value <value> --dry-run
步骤3: 向用户展示dry-run结果，获得明确确认
步骤4: 执行 ha_api.py set <entity_id> --value <value>
步骤5: 验证设备状态是否已更新
```

### 10.3 调用服务 (service)

```
步骤1: 确认HA连接参数已配置
步骤2: 执行 ha_api.py service <service> --entity-id <entity_id> --dry-run
步骤3: 向用户展示dry-run结果，获得明确确认
步骤4: 执行 ha_api.py service <service> --entity-id <entity_id>
步骤5: 验证服务执行结果
```

## 11. 安全检查清单（逐项确认）

- [ ] HA 连接参数已配置（HA_URL、HA_TOKEN）
- [ ] **写操作已 dry-run 预览**（`--dry-run`）
- [ ] 实体ID已确认正确（避免操作错误设备）
- [ ] 操作内容已向用户展示并获得**明确确认**
- [ ] 敏感信息（Token）未硬编码到代码中
- [ ] 操作完成后验证了结果（状态查询确认）
- [ ] HA 连接不可用时已优雅降级（友好提示）

## 12. 常见错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| HA_001 | 连接失败 | 检查 HA_URL 是否正确，HA 实例是否运行 |
| HA_002 | 认证错误 | 检查 HA_TOKEN 是否有效，权限是否足够 |
| HA_003 | 实体不存在 | 确认 entity_id 正确，使用 list 命令查看可用实体 |
| HA_004 | 参数错误 | 检查参数格式，查看 --help 获取详细说明 |
| HA_005 | 服务调用失败 | 检查服务名和参数是否正确 |
| HA_006 | HA 不可用 | 提示用户检查 HA 实例，优雅降级不影响核心系统 |

## 13. 实体类型速查

| 实体类型 | 示例 | 常用操作 |
|---------|------|---------|
| light | light.living_room | turn_on/turn_off, set brightness/color |
| switch | switch.smart_socket | turn_on/turn_off |
| sensor | sensor.temperature | get state |
| climate | climate.thermostat | set temperature, set mode |
| fan | fan.bedroom_fan | turn_on/turn_off, set speed |
| cover | cover.garage_door | open/close |

## 14. Changelog

- **v1.0.0** (2026-06-30): 初始版本，支持设备状态查询、设备控制、服务调用、实体列表、HA状态检查；遵循可选模块设计原则；支持配置化参数和优雅降级机制。