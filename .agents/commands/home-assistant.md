---
id: "home-assistant"
title: "Home Assistant 集成指令集"
source: "AGENTS.md#home-assistant指令"
x-toml-ref: "../../.meta/toml/.agents/commands/home-assistant.toml"
---
# Home Assistant 集成指令集

## 可选模块说明

**本指令集为可选模块**：
- 不集成本指令集时，核心系统能正常运行且不受影响
- HA 连接不可用时，提供友好的错误提示和降级方案
- 采用条件加载机制，仅在配置了 HA 连接参数时激活

## 触发条件

- 用户请求控制智能家居设备（打开/关闭灯光、调节温度等）
- 用户请求查询设备状态（当前温度、灯光状态等）
- 用户请求调用 Home Assistant 服务
- 用户请求管理 HA 集成配置
- 用户明确请求使用 Home Assistant 功能

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| operation | string | 是 | 操作类型：`get`/`set`/`service`/`list`/`info` |
| entity_id | string | 否 | 实体ID（如 `light.living_room`） |
| service | string | 否 | 服务名（如 `light.turn_on`） |
| value | any | 否 | 设置值（如 `true`、`50`、`25`） |
| ha_url | string | 否 | Home Assistant URL（覆盖配置） |
| ha_token | string | 否 | API Token（覆盖配置） |
| dry_run | boolean | 否 | 试运行不提交（默认 false） |

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，拥有最终决策权，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| HA集成核心活动 | orchestrator | developer | tester | reviewer | architect |
|:---|:---:|:---:|:---:|:---:|:---:|
| 触发HA操作与参数校验 | **R/A** | C | I | C | I |
| 设备状态查询 | R | **A** | I | C | I |
| 设备控制（写操作） | R | **A** | C | C | I |
| 服务调用 | R | **A** | I | C | I |
| 集成配置管理 | R | C | I | **A** | C |
| 操作结果验证 | R | C | **R/A** | C | I |
| 错误处理与降级方案 | R | **A** | C | C | C |

### 审批权限边界

- **查询操作（get/list/info）**：developer负责执行，无需额外审批
- **控制操作（set/service）**：developer负责执行，需向用户展示dry-run结果并获得确认
- **集成配置变更**：reviewer负责审批，developer负责执行
- **错误处理方案变更**：architect参与技术评审，developer负责实施
- **HA连接不可用**：自动触发优雅降级，向用户提示友好信息

## 执行步骤

### 步骤 1：参数校验与准备

- 验证操作类型是否有效
- 检查必需参数是否完整
- 确认 HA 连接参数已配置
- 提示用户如未配置，进入优雅降级流程

### 步骤 2：执行操作

根据操作类型执行相应操作：

**查询操作（get/list/info）**：
- 调用 `ha_api.py` 执行查询
- 解析返回的 JSON 数据
- 向用户展示结果

**控制操作（set/service）**：
- 先执行 `--dry-run` 预览
- 向用户展示预览结果
- 获得用户明确确认后执行实际操作

### 步骤 3：结果验证

- 查询设备状态确认操作生效
- 处理错误和异常情况
- 提供友好的错误提示

### 步骤 4：优雅降级（条件触发）

- HA 连接不可用时，向用户展示友好提示
- 说明跳过 HA 操作，核心系统不受影响
- 不抛出致命错误，确保核心系统正常运行

## 输出规范

| 产出物 | 格式 | 存储位置 |
|--------|------|---------|
| 操作结果 | JSON/文本 | 控制台输出 |
| 操作日志 | 文本 | `.agents/scripts/logs/` |
| 集成配置 | .env 文件 | 项目根目录 |

## 质量验收

- 操作参数校验完整，拒绝无效输入
- 控制操作已执行 dry-run 预览并获得用户确认
- HA 连接不可用时已优雅降级，不影响核心系统
- 操作结果已验证，状态正确更新
- 日志记录完整，便于排障

## 约束条件

- 必须使用 `ha_api.py` 脚本执行操作，不得手动拼接 API 请求
- 写操作必须先执行 dry-run 预览，获得用户确认后再执行
- 敏感信息（API Token）不得硬编码，必须通过配置文件或环境变量提供
- HA 连接不可用时必须优雅降级，不得抛出致命错误
- 不负责 Home Assistant 服务器端的配置和维护

## 关联资源

- [Home Assistant 集成技能](../skills/home-assistant/SKILL.md)
- [HA API 自动化脚本](../scripts/ha_api.py)
- [Home Assistant 官方文档](https://www.home-assistant.io/docs/)
- [Home Assistant REST API 文档](https://developers.home-assistant.io/docs/api/rest/)