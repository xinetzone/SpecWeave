---
type: Concept
title: OpenClaw 云 API
description: 涂鸦 OpenClaw 智能控制技能，基于 2C 终端用户 API，覆盖设备控制/家庭管理/天气/通知/统计/IPC 抓拍与实时消息
tags: [tuya, openclaw, cloud, api, rest, websocket, smart-home, saas, mcp]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuya-skills-source
    resource: "/references/tuya-skills-source.md"
    title: TuyaOpen 技能与生态源码
  - id: facts-tuya-skills-ecosystem
    resource: "/references/facts-tuya-skills-ecosystem.md"
    title: 技能与生态事实清单
---

# OpenClaw 云 API

OpenClaw 是涂鸦智能的云 API 开放平台，`tuya-openclaw-skills` 仓库提供了名为 `tuya-smart-control` 的 Agent Skill，使 AI 助手能够通过自然语言控制涂鸦生态中的智能设备。该技能基于涂鸦 2C 终端用户 API（End User API），覆盖 3000+ 智能硬件品类，支持 7 个全球数据中心，提供设备控制、家庭管理、天气服务、消息通知、数据统计、IPC 云抓拍和实时设备消息订阅等 10 大功能模块。

## 基本信息

| 项目 | 说明 |
|------|------|
| 技能名称 | tuya-smart-control |
| 版本 | 1.0.0 |
| 认证方式 | HTTP Header `Authorization: Bearer {Api-key}` |
| 凭据来源 | 环境变量 `TUYA_API_KEY` |
| 数据中心 | 7 个（自动从 API Key 前缀推断） |
| Python 依赖 | requests>=2.28.0, websockets>=12.0 |
| 源码仓库 | https://github.com/tuya/tuya-openclaw-skills |

## 数据中心映射

API Key 以 `sk-` 开头，其后的前两个字符决定数据中心：

| 前缀 | 区域 | Base URL |
|------|------|----------|
| AY | 中国数据中心 | https://openapi.tuyacn.com |
| AZ | 美西数据中心 | https://openapi.tuyaus.com |
| EU | 中欧数据中心 | https://openapi.tuyaeu.com |
| IN | 印度数据中心 | https://openapi.tuyain.com |
| UE | 美东数据中心 | https://openapi-ueaz.tuyaus.com |
| WE | 西欧数据中心 | https://openapi-weaz.tuyaeu.com |
| SG | 新加坡数据中心 | https://openapi-sg.iotbing.com |

API Key 获取渠道：
- 中国大陆用户：https://tuyasmart.com/
- 国际用户：https://tuya.ai/

不同区域使用不同的 API 服务域名，必须与账户注册区域匹配。可通过设置 `TUYA_BASE_URL` 环境变量覆盖自动检测。

## 统一请求/响应格式

### 请求格式

所有 API 使用 Base URL 拼接路径：

```text
GET  {base_url}/v1.0/end-user/homes/all
POST {base_url}/v1.0/end-user/devices/{device_id}/shadow/properties/issue
```

认证通过 `Authorization: Bearer {Api-key}` 请求头自动处理。

### 响应格式

成功响应：
```json
{
  "success": true,
  "t": 1710234567890,
  "result": { }
}
```

错误响应：
```json
{
  "success": false,
  "code": 1108,
  "msg": "uri path invalid"
}
```

- `success` 为 `true` 时，结果在 `result` 字段
- `success` 为 `false` 时，错误详情在 `code` 和 `msg` 字段
- HTTP 429 和临时 5xx 响应自动退避重试

## 十大功能模块

### 1. 家庭管理（Home Management）

- **列出所有家庭**：`GET /v1.0/end-user/homes/all`
- **列出家庭中的房间**：获取家庭下的空间/房间结构
- 家庭数据包含 `latitude`/`longitude` 坐标字段（格式为 `{"Value": "30.3"}`），可用于天气查询

### 2. 设备查询（Device Query）

- **列出所有设备**：`GET /v1.0/end-user/devices`
- **按家庭筛选**：`--home <home_id>`
- **按房间筛选**：`--room <room_id>`（每次只能指定一个范围）
- **设备详情**：`GET /v1.0/end-user/devices/{device_id}`，包含当前属性状态（`properties`）、在线状态（`online`）、品类（`category_name`）

### 3. 设备控制（Device Control）

- **查询物模型**：获取设备支持的属性列表，`result.model` 是 JSON 字符串需二次解析
- **下发属性指令**：`POST /v1.0/end-user/devices/{device_id}/shadow/properties/issue`
- `properties` 字段必须是 JSON 字符串（双重序列化），如 `{"properties": "{\"switch_led\":true}"}`

支持的属性类型：

| 类型 | 说明 | 示例 |
|------|------|------|
| bool | 布尔开关 | 开灯/关灯、开/关空调、开/关插座 |
| enum | 枚举选择 | 空调模式（自动/制冷/制热）、风速（低/中/高） |
| value | 数值 | 亮度（0-1000）、温度（16-30） |
| string | 字符串 | 设置设备显示文本 |

不支持的操作（安全或复杂类型）：
- 门锁控制（安全敏感）
- 实时视频流拉取（支持云端抓拍/短视频）
- 图片操作
- 复杂数据类型控制（raw/bitmap/struct/array）
- 固件 OTA 升级
- 设备配网/移除

### 4. 设备管理（Device Management）

- **重命名设备**：修改设备显示名称

### 5. 天气服务（Weather Service）

- **当前天气和预报**：根据经纬度查询
- 坐标范围验证：纬度 [-90, 90]，经度 [-180, 180]
- 坐标可从家庭信息获取，或由用户提供城市名转换

### 6. 消息通知（Notifications）

四种通知方式，均为自发自收（只能发送给当前登录用户）：

| 类型 | CLI 命令 | 必需参数 |
|------|---------|---------|
| 短信 | `sms` | 消息内容 |
| 语音电话 | `voice` | 消息内容 |
| 邮件 | `mail` | 主题 + 内容 |
| App 推送 | `push` | 主题 + 内容 |

从设备事件触发通知时，强制实施最小 30 分钟冷却节流。

### 7. 数据统计（Data Statistics）

- **统计配置查询**：确认设备是否具备统计能力
- **统计数据查询**：按小时查询设备数据（如能耗/功率）
- 时间格式：`yyyyMMddHH`（如 `2024010100` 表示 2024 年 1 月 1 日 00:00）
- 单次请求时间范围不超过 24 小时，更长范围需多次请求聚合

### 8. IPC 云抓拍（IPC Cloud Capture）

为网络摄像头提供云端抓拍和短视频录制：

- **图片抓拍（PIC）**：可选抓拍张数 1-5
- **短视频录制（VIDEO）**：时长 1-60 秒，默认 10 秒
- 一键式方法自动处理 分配→等待→轮询→重试 全流程
- 返回解密后的 URL：`decrypt_image_url` / `decrypt_video_url`

### 9. 设备消息订阅（Device Message Subscription）

通过 WebSocket 实时订阅设备事件：

- **属性变化事件**（`on_property_change`）：设备功能属性实时变化
- **在线/离线状态事件**（`on_online_status`）：设备上下线通知
- 使用同一个 `TUYA_API_KEY` 认证，WebSocket URI 自动从 Key 前缀推断
- 支持订阅所有设备或指定设备 ID 列表
- 属性代码与物模型代码对应，可通过 REST API 查询属性名称和值范围

### 10. 错误处理（Error Handling）

- 统一错误码和恢复策略
- CLI 退出码：`2` 表示用法/验证错误，`1` 表示运行时/API/网络错误
- HTTP 429 和 5xx 自动退避重试

## 三种使用方式

### 方式一：命令行（推荐）

```bash
python3 tuya_api.py homes
python3 tuya_api.py devices
python3 tuya_api.py control <device_id> '{"switch_led":true}'
python3 tuya_api.py weather 39.90 116.40
python3 tuya_api.py ipc_pic_fetch <device_id> 1
python3 tuya_api.py ipc_video_fetch <device_id> 10 1
```

### 方式二：Python SDK

```python
from tuya_api import TuyaAPI

api = TuyaAPI()
homes = api.get_homes()
result = api.issue_properties("device_id", {"switch_led": True})
capture = api.ipc_ai_capture_pic_allocate_and_fetch("device_id")
```

### 方式三：WebSocket 实时订阅

```python
from tuya_device_mq_client import TuyaDeviceMQClient

client = TuyaDeviceMQClient(api_key=os.environ["TUYA_API_KEY"])

@client.on_property_change
async def on_prop(device_id, properties):
    for prop in properties:
        print(f"{device_id}: {prop['code']} = {prop['value']}")

await client.connect()
```

## 典型工作流

### 设备控制流程

1. 定位设备（按房间+品类 → 按名称 → 歧义消歧）
2. 获取当前状态（检查 `online` 和 `properties`）
3. 查询物模型（解析 `model` JSON 字符串，检查 `accessMode`：ro/wr/rw）
4. 映射指令（bool/enum/value 类型，相对调节计算 ±10% 或指定值，范围校验 min/max/step）
5. 下发命令（SDK 自动处理 JSON 双重序列化）
6. 验证结果（等待 1-2 秒后重新读取设备状态）

### 事件驱动自动化

结合 WebSocket 订阅和 REST API 控制：
1. 订阅触发设备的属性变化
2. 当满足触发条件时，调用 REST API 控制执行设备
3. 如需通知，实施 30 分钟冷却节流

## 安全注意事项

1. 永远不要在输出中记录或显示 `TUYA_API_KEY` 的值
2. 门锁等安全敏感操作不通过此技能开放
3. 通知只能自发自收，防止滥发
4. WebSocket 客户端仅在服务端运行
5. API Key 与数据中心区域绑定，不可跨区使用

## 相关概念

- [AI 开发技能体系](/concepts/11-dev-skills.md)
- [Home Assistant 集成](/concepts/13-ha-integration.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
- [TuyaOpen IoT 框架概览](/concepts/00-overview.md)
