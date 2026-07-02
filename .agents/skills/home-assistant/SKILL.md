---
name: home-assistant
version: 1.1.0
description: "Home Assistant智能家居系统集成。当用户需要控制智能家居设备、查询设备状态、调用HA服务、管理HA集成配置、使用ha_api脚本时，必须使用此技能。支持通过REST API与Home Assistant交互，实现设备控制、状态查询、服务调用等核心功能。本技能为可选模块，不集成本技能时核心系统能正常运行。"
argument-hint: "<操作类型> [实体ID/服务名]"
user-invocable: true
paths:
  - ".agents/scripts/ha_api.py"
  - ".agents/commands/home-assistant.md"
---

# Home Assistant 智能家居集成 (Home Assistant Integration)

> ⚠️ **本Skill是可选集成模块（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<200行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/home-assistant.md](../../commands/home-assistant.md)（完整规范+RACI矩阵+错误处理）
>
> 📌 **可选模块**：不集成本技能时核心系统正常运行；HA连接不可用时优雅降级。

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

> **为什么优先使用 ha_api.py？** 脚本方案支持配置化参数、错误处理和重试机制，比手动构造 API 请求更可靠，且内置dry-run防误操作。

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
├─ 需要控制设备？ → ha_api.py set/服务调用（先dry-run！）
├─ 需要获取实体列表？ → ha_api.py list
└─ HA连接不可用？ → 提示配置HA参数（优雅降级）
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `ha-YYYYMMDD-<entity>`）：
```
[CMD-LOG] | level=INFO | cmd=home-assistant | step=S0 | event=CMD_START | session=ha-... | msg=开始HA操作：<操作简述> | ctx={"operation":"...","entity_id":"...","dry_run":true/false}
```

> **为什么决策前记录日志？** 设备控制是写操作，错误操作可能导致设备状态异常；CMD_START记录原始参数，便于操作失误后回溯排查。

## 5. 核心步骤（快速开始）

```
步骤1：确认HA连接参数已配置（HA_URL、HA_TOKEN）
步骤2：读取L2文档了解完整参数和RACI责任
步骤3：查询类操作 → ha_api.py get/list/info
步骤4：控制类操作 → 先 --dry-run 预览 → 获得用户确认 → 正式执行
步骤5：验证执行结果（状态查询确认）
```

> 完整RACI矩阵、输入规范、错误码表见L2文档 [commands/home-assistant.md](../../commands/home-assistant.md)。

## 6. 常用命令速查

脚本路径：[ha_api.py](../../scripts/ha_api.py)

```bash
cd d:\spaces\SpecWeave

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
```

## 7. 安全检查清单（逐项确认）

- [ ] HA 连接参数已配置（HA_URL、HA_TOKEN）
- [ ] **写操作已 dry-run 预览**（`--dry-run`）
- [ ] 实体ID已确认正确（避免操作错误设备）
- [ ] 操作内容已向用户展示并获得**明确确认**
- [ ] 敏感信息（Token）未硬编码到代码中
- [ ] 操作完成后验证了结果（状态查询确认）
- [ ] HA 连接不可用时已优雅降级（友好提示）

## 8. 执行日志（CMD-LOG）

执行HA操作时按精简CMD-LOG规范输出：
- `cmd=home-assistant`，session前缀 `ha-YYYYMMDD-<entity_or_topic>`
- 步骤编号 S0-S5（启动→连接检查→dry-run→执行→验证→完成）
- 关键事件：`DRY_RUN_OK`、`CONNECTION_FAILED`、`ENTITY_NOT_FOUND`、`OPERATION_VERIFIED`

> 写操作（set/service）必须输出S0和S5验证日志；只读操作（get/list/info）可简化日志。

## 9. 常见错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| HA_001 | 连接失败 | 检查 HA_URL 是否正确，HA 实例是否运行 |
| HA_002 | 认证错误 | 检查 HA_TOKEN 是否有效，权限是否足够 |
| HA_003 | 实体不存在 | 确认 entity_id 正确，使用 list 命令查看可用实体 |
| HA_006 | HA 不可用 | 提示用户检查 HA 实例，优雅降级不影响核心系统 |

> 完整错误码表（HA_001~HA_006）见L2文档。

## 10. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **HA API需要长期访问令牌**：认证不能使用Web界面登录密码，必须在HA用户配置页面（点击左下角用户名→滚动到底部→"长期访问令牌"）创建。令牌生成后只显示一次，请妥善保存；令牌权限等同于创建它的用户权限。
- **实体ID格式为domain.object_id**：标准格式是`domain.object_id`（如`light.living_room`、`sensor.temperature`），domain和object_id之间是点号不是下划线，且整个entity_id大小写敏感。通过list命令可以查看所有实体的准确ID。
- **服务调用需domain+service完整格式**：调用服务时不能只写服务名（如`turn_on`），必须使用完整格式`domain.service`（如`light.turn_on`、`switch.turn_off`）。不同domain的同名服务（如light.turn_on和switch.turn_on）是不同的服务。
- **状态查询返回字符串不是布尔值**：HA REST API返回的实体状态`state`字段始终是字符串类型。灯的开/关是`"on"`/`"off"`字符串，不是布尔值`true`/`false`，比较时必须用字符串相等判断，不能直接当布尔值用。
- **REST API默认端口8123**：HA默认在8123端口提供HTTP API，不是80或443。确保HA实例正在运行，且防火墙/网络策略允许访问8123端口；如果配置了HTTPS，URL需要使用`https://`开头。

## 11. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数） | L2 | [commands/home-assistant.md](../../commands/home-assistant.md) | 每次使用必读 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式参考 |
| ha_api.py 脚本 | 工具 | [ha_api.py](../../scripts/ha_api.py) | 脚本参数、调试 |

## 12. Changelog

- **v1.1.0** (2026-07-01): 遵循markdown-as-interface v2.0六要素标准升级：删除废弃字段disable-model-invocation；添加L0/L1/L2三层架构引用块（标注可选模块定位）；决策前添加CMD_START强制日志；添加精简CMD-LOG执行日志章节；修复命令示例路径错误（d:\AI→d:\spaces\SpecWeave）；补充L2路径到frontmatter；添加关键参考索引表；版本对齐v2.0规范。
- **v1.0.0** (2026-06-30): 初始版本，支持设备状态查询、设备控制、服务调用、实体列表、HA状态检查；遵循可选模块设计原则；支持配置化参数和优雅降级机制。
