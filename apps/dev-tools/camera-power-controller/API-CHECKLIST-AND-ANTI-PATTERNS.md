---
id: "guide-20260803-iot-api-verification"
title: "智能硬件API可控性验证检查清单与反模式代码示例"
date: "2026-08-03"
type: "guide"
status: "completed"
source: "七概念方法论 sc-20260803-iot-checklist-examples，基于里程碑复盘RETROSPECTIVE.md"
tags: ["iot", "hardware-selection", "anti-patterns", "code-examples", "checklist"]
---

# 智能硬件API可控性验证检查清单与反模式代码示例

**版本**：V1.1（经对抗审查修正）  
**日期**：2026-08-03  
**依据**：摄像头通断电自动化测试项目里程碑复盘核心洞察1与萃取模式  
**参考**：涂鸦IoT平台 https://developer.tuya.com

---

## 目录

1. [第一部分：硬件API可控性验证检查清单](#第一部分硬件api可控性验证检查清单)
2. [第二部分：5个IoT控制反模式代码示例](#第二部分5个iot控制反模式代码示例)

---

# 第一部分：硬件API可控性验证检查清单

> **核心洞察**：自动化场景中，智能硬件选型的第一决策标准是"是否有开放API支持直接脚本控制"，功能丰富度是第二优先级。本检查清单用于在选型阶段做一票否决式验证。

## 使用说明

- 本清单分为**P0一票否决项**（必须全部满足才能进入候选）和**P1/P2评分项**（用于候选方案比较）
- P0任意一项不通过→直接淘汰，不进入功能比较阶段
- P1/P2项用于在满足P0的候选方案中打分排序

---

## P0 一票否决项（必须全部满足）

| 检查项 | 验证方法 | 通过标准 | 验证结果 |
|-------|---------|---------|---------|
| **P0-1 有公开API文档** | 访问厂商开发者平台，查找API文档 | 可下载/在线阅读完整的REST API文档，包含鉴权、设备列表、设备控制、状态查询等接口 | ☐ 通过 / ☐ 不通过 |
| **P0-2 支持个人开发者注册** | 尝试注册开发者账号 | 个人/企业均可注册，不需要企业认证或付费才能开通API权限 | ☐ 通过 / ☐ 不通过 |
| **P0-3 支持电源开关控制API** | 查阅API文档，查找设备控制接口 | 存在可直接下发开关指令的API（如POST /devices/{id}/commands），明确支持switch/power类**DP点（Data Point，设备功能点，IoT平台术语）**控制 | ☐ 通过 / ☐ 不通过 |
| **P0-4 支持实时状态查询API** | 查阅API文档，查找设备状态接口 | 存在可查询设备当前开关状态的API（如GET /devices/{id}/status），返回实时状态而非缓存 | ☐ 通过 / ☐ 不通过 |
| **P0-5 支持设备在线状态查询** | 查阅API文档，设备列表/详情接口返回字段 | 接口返回包含online字段或设备在线状态标识，可在控制前判断设备是否离线 | ☐ 通过 / ☐ 不通过 |
| **P0-6 不需要官方APP中转** | 验证API调用链路 | API调用直接到云端→设备，不需要先模拟操作APP（如UI自动化、ADB控制手机等曲线方案） | ☐ 通过 / ☐ 不通过 |
| **P0-7 API调用可脚本化** | 编写简单HTTP请求脚本测试 | 不依赖厂商提供的闭源二进制工具/APP/SDK，仅用curl/requests等标准HTTP客户端即可完成token获取→设备列表→控制→状态查询完整流程 | ☐ 通过 / ☐ 不通过 |

> **⚠️ 淘汰规则**：以上7项任意一项为"不通过"，该硬件直接淘汰，不需要再比较功能参数。

---

## P1 重要加分项（满足越多越好）

| 检查项 | 验证方法 | 通过标准 | 权重 |
|-------|---------|---------|-----|
| **P1-1 本地局域网控制支持** | 查阅文档是否支持LAN API/局域网控制 | 支持局域网内直接控制（不依赖公网），或提供本地MQTT/CoAP接入 | 3分 |
| **P1-2 Webhook/事件推送** | 查阅是否支持设备状态变化推送 | 状态变化时主动推送回调（Webhook/MQTT），不需要轮询 | 2分 |
| **P1-3 错误码文档完善** | 查阅API错误码文档 | 有完整的错误码列表，区分"参数错误/鉴权失败/设备离线/限流/服务器错误"等 | 2分 |
| **P1-4 DP点/属性可查询** | 验证是否能查询设备支持的功能点 | API可返回设备实际支持的properties/DP点列表，不需要硬编码猜测 | 2分 |
| **P1-5 非官方SDK示例代码** | 查找社区/官方多语言示例 | 有Python/Go/Java等至少2种语言的示例代码或开源SDK | 1分 |
| **P1-6 接口限流宽松** | 查阅限流规则或测试 | 单IP/QPS限流≥5次/秒，满足自动化轮询需求 | 1分 |
| **P1-7 批量控制接口** | 查阅是否支持多设备同时控制 | 支持一次API调用控制多个设备，减少请求次数 | 1分 |

---

## P2 功能参考项（最后比较）

| 检查项 | 说明 |
|-------|------|
| P2-1 单孔/多孔独立控制 | 多孔插线板每个插孔是否可独立控制 |
| P2-2 电量统计 | 是否支持功率/电压/用电量查询 |
| P2-3 本地定时 | 是否支持设备本地定时（断网也能执行） |
| P2-4 温柔关机/延时断电 | 是否支持先软关机再断电（针对电脑主机场景） |
| P2-5 4G/网线联网 | 是否支持4G或有线（非仅WiFi） |
| P2-6 价格 | 单路成本 |

> **P2比较原则**：P0全部通过、P1打分接近的前提下，再比较P2功能项。功能多但API不开放的硬件（如本项目中的向日葵P1Pro）在P0阶段即淘汰，不进入P2比较。

---

## 选型决策流程

```
开始硬件选型
   ↓
列出候选硬件清单
   ↓
逐个做P0一票否决检查（7项）
   ├─ 任一P0不通过 → 淘汰
   ↓ P0全部通过
计算P1加权总分
   ↓
按P1分数排序取前2-3名
   ↓
比较P2功能项和价格
   ↓
最终选型
```

---

## 本项目实际验证结果（供参考）

| 硬件 | P0结果 | P1得分 | 结论 |
|-----|-------|-------|-----|
| **涂鸦智能插座** | ✅ 7/7通过 | ~10/12 | ✅ 选用 |
| **向日葵P1Pro** | ❌ P0-6不通过（无硬件控制API，只能通过APP或MCP控制电脑，不能直接控制插孔） | - | ❌ 淘汰 |
| **向日葵C2** | ❌ P0-3/P0-4不通过（无开放插座控制API） | - | ❌ 淘汰 |

---

# 第二部分：5个IoT控制反模式代码示例

> **萃取模式**：IoT设备控制"指令-验证-重试"闭环范式，包含5个来自实际项目教训的反模式。每个反模式提供：
> - ❌ **错误代码示例**：展示反模式的典型写法
> - 🐛 **问题说明**：解释为什么这样写会出问题
> - ✅ **正确代码示例**：展示符合闭环范式的写法
>
> **注意**：代码示例中使用的涂鸦API路径和参数格式为演示用途，实际接入时请以厂商官方API文档为准。核心逻辑模式（指令→验证→重试）可迁移到任意IoT平台。

```python
# 所有代码示例通用依赖导入
import time
import random
import requests
from typing import Literal, Optional
from http import HTTPStatus
```

---

## 反模式1：信任API返回值——返回success就认为操作成功

### ❌ 错误示例

```python
import requests

def bad_power_on(device_id: str, token: str) -> bool:
    """反模式：仅依赖API返回值判断成功"""
    url = f"https://openapi.tuyacn.com/v1.0/devices/{device_id}/commands"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {"commands": [{"code": "switch_1", "value": True}]}
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    result = response.json()
    
    # 反模式：只看API返回的success字段，认为返回true就成功了
    if result.get("success"):
        print(f"设备 {device_id} 开机成功")
        return True
    else:
        print(f"开机失败: {result.get('msg')}")
        return False
```

### 🐛 问题说明

`result["success"]=true` 仅表示**云端服务器成功接收并接受了指令**，不代表：
1. 设备在线并收到了指令
2. 设备实际执行了开关动作
3. 设备状态已经改变

云端→设备之间存在网络延迟、设备离线、DP点错误、信号差等多个失败点。历史经验（Node.js涂鸦项目）证明这种写法会导致"UI显示成功但设备实际没动"的静默失败。

### ✅ 正确示例（闭环验证）

```python
import time
import requests
from typing import Literal

PowerState = Literal["ON", "OFF", "UNKNOWN"]

class TuyaController:
    def __init__(self, token: str, region: str = "cn"):
        self.token = token
        self.base_url = f"https://openapi.tuya{region}.com/v1.0"
        self.headers = {"Authorization": token, "Content-Type": "application/json"}
    
    def get_device_state(self, device_id: str) -> PowerState:
        """查询真实设备状态"""
        url = f"{self.base_url}/devices/{device_id}/status"
        resp = requests.get(url, headers=self.headers, timeout=10)
        data = resp.json()
        if not data.get("success"):
            return "UNKNOWN"
        for item in data.get("result", []):
            if item.get("code") == "switch_1":
                return "ON" if item.get("value") else "OFF"
        return "UNKNOWN"
    
    def power_on(self, device_id: str, timeout: float = 30.0, interval: float = 1.0) -> bool:
        """正确做法：指令下发 + 状态轮询验证 + 超时"""
        # 步骤1：发送指令（不等待返回值判断成功）
        url = f"{self.base_url}/devices/{device_id}/commands"
        payload = {"commands": [{"code": "switch_1", "value": True}]}
        requests.post(url, json=payload, headers=self.headers, timeout=10)
        
        # 步骤2：轮询验证真实状态
        start = time.time()
        while time.time() - start < timeout:
            state = self.get_device_state(device_id)
            if state == "ON":
                print(f"设备 {device_id} 开机成功（已验证状态）")
                return True
            time.sleep(interval)
        
        print(f"超时：{timeout}秒内未检测到设备开机")
        return False
```

---

## 反模式2：硬编码DP点映射——靠猜写DP code

### ❌ 错误示例

```python
def bad_control_channel(device_id: str, channel: int, value: bool, token: str):
    """反模式：硬编码DP点映射规则，不验证设备实际支持的属性"""
    # 反模式：凭"经验"硬编码通道号→DP点映射关系
    # 猜：channel 1 = switch_1, channel 2 = switch_2, USB = switch_usb1...
    if channel == 6:  # 猜这是USB口
        dp_code = "switch_usb1"
    else:
        dp_code = f"switch_{channel + 1}"  # 猜通道n对应switch_{n+1}
    
    url = f"https://openapi.tuyacn.com/v1.0/devices/{device_id}/commands"
    headers = {"Authorization": token}
    payload = {"commands": [{"code": dp_code, "value": value}]}
    requests.post(url, json=payload, headers=headers)
    print(f"已发送指令到 {dp_code}")
    # 问题：下发到不存在的DP点，API可能返回success但设备完全无反应！
```

### 🐛 问题说明

不同厂商、不同型号的智能插座，DP点命名规则差异很大：
- 有的用 `switch_1` 到 `switch_4`
- 有的USB口叫 `switch_usb` 不是 `switch_usb1`
- 有的总开关叫 `switch` 不带数字

硬编码推导规则在设备型号变化时会"静默失败"——指令发送到不存在的DP点，API返回success（因为只是格式校验通过），但设备完全不执行动作。

### ✅ 正确示例（启动时校验DP点）

```python
class TuyaController:
    def __init__(self, token: str, device_config: dict):
        self.token = token
        self.base_url = "https://openapi.tuyacn.com/v1.0"
        self.headers = {"Authorization": token}
        # 设备配置：显式指定每个通道对应的正确DP code
        # 配置来自discover命令查询结果，不是硬编码推导
        self.device_map = {}
        for name, cfg in device_config.items():
            self.device_map[name] = {
                "device_id": cfg["device_id"],
                "switch_code": cfg.get("switch_property", "switch_1"),
                "_validated": False
            }
    
    def discover_device_properties(self, device_id: str) -> set:
        """查询设备实际支持的所有DP点code"""
        url = f"{self.base_url}/devices/{device_id}/specifications"
        resp = requests.get(url, headers=self.headers, timeout=10)
        data = resp.json()
        supported_codes = set()
        for func in data.get("result", {}).get("functions", []):
            supported_codes.add(func.get("code"))
        for status in data.get("result", {}).get("status", []):
            supported_codes.add(status.get("code"))
        return supported_codes
    
    def validate_device_config(self, camera_name: str) -> bool:
        """启动时校验配置的DP点在设备上真实存在"""
        dev = self.device_map[camera_name]
        supported = self.discover_device_properties(dev["device_id"])
        
        if dev["switch_code"] not in supported:
            raise ValueError(
                f"配置错误：设备 {camera_name} ({dev['device_id']}) "
                f"不支持DP点 '{dev['switch_code']}'。"
                f"设备实际支持的DP点：{sorted(supported)}。"
                f"请修正配置文件中的switch_property字段。"
            )
        dev["_validated"] = True
        print(f"✓ {camera_name} DP点校验通过: {dev['switch_code']}")
        return True
    
    def validate_all_devices(self):
        """启动时校验所有设备配置，不合格直接报错"""
        for name in self.device_map:
            self.validate_device_config(name)
```

---

## 反模式3：本地缓存状态——控制完就更新缓存，查询返回缓存

### ❌ 错误示例

```python
class BadCachedController:
    def __init__(self):
        self._state_cache = {}  # 反模式：本地缓存状态字典
        self.token = None
    
    def power_on(self, device_id: str):
        # 发送指令...
        requests.post(...)
        # 反模式：发送成功就直接更新本地缓存，认为状态已经改变
        self._state_cache[device_id] = True
        print("开机成功（缓存已更新）")
    
    def get_state(self, device_id: str) -> bool:
        # 反模式：直接返回本地缓存，不查询云端真实状态
        if device_id in self._state_cache:
            state = self._state_cache[device_id]
            print(f"查询到状态（来自缓存）: {state}")
            return state
        return False  # 默认关
```

### 🐛 问题说明

本地缓存会在以下场景与真实状态分叉：
1. **设备被手动控制**：用户按了插座上的物理按钮
2. **其他客户端控制**：手机APP、其他脚本也控制了这个设备
3. **设备断电重启**：停电恢复后状态可能变化
4. **指令实际失败**：如反模式1所述，API返回success但设备没动
5. **网络延迟导致状态滞后**：设备已经变了但云端状态还没更新

此时上层脚本读到的是"假状态"，测试逻辑基于假状态运行，会导致各种诡异bug。

### ✅ 正确示例（不缓存，每次实时查询）

```python
class ReliableController:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://openapi.tuyacn.com/v1.0"
        self.headers = {"Authorization": token}
        # 注意：没有_state_cache字典！不做本地状态缓存
        
        # 可选：只缓存"不可变"的元数据（DP点映射、设备ID等）
        self._device_meta_cache = {}  # 只缓存启动时校验过的元数据
    
    def get_device_state(self, device_id: str) -> dict:
        """每次查询都调用真实API，不使用缓存"""
        url = f"{self.base_url}/devices/{device_id}/status"
        resp = requests.get(url, headers=self.headers, timeout=10)
        data = resp.json()
        
        if not data.get("success"):
            return {"online": False, "switch": None, "_source": "api_error"}
        
        result = {}
        for item in data.get("result", []):
            result[item["code"]] = item["value"]
        
        return {
            "online": True,  # 能查到状态说明在线
            "switch": result.get("switch_1"),
            "_source": "realtime_api",  # 明确标记状态来源
            "_query_time": time.time()
        }
    
    def wait_for_state_change(self, device_id: str, expected: bool,
                              timeout: float = 30.0) -> bool:
        """轮询等待，每次都是实时查询"""
        start = time.time()
        while time.time() - start < timeout:
            state = self.get_device_state(device_id)
            if not state["online"]:
                print("设备离线，终止等待")
                return False
            if state["switch"] == expected:
                return True
            time.sleep(1.0)
        return False
```

> **补充**：如果确实需要短期缓存（如避免频繁请求触发限流），缓存TTL不得超过2秒，且必须标记`_source="cache"`和`_cache_time`，上层逻辑知道这是可能过期的缓存值。

---

## 反模式4：无超时无限等待——轮询不设超时

### ❌ 错误示例

```python
def bad_wait_until_on(device_id: str, controller):
    """反模式：无限轮询，永远不超时"""
    print("等待设备开机...")
    while True:  # 反模式：while True没有break条件和超时
        state = controller.get_device_state(device_id)
        if state.get("switch") == True:
            print("设备已开机")
            return True
        time.sleep(1)
        # 问题：如果设备离线、故障、DP点错误，这里永远循环下去
        # CI流水线卡住、测试脚本挂死、无法定位问题
```

### 🐛 问题说明

无超时的无限轮询在异常场景下会导致：
1. 测试脚本永久挂起，CI/CD流水线阻塞
2. 无法区分"设备还在启动中"和"设备故障永远起不来"
3. 出问题时没有错误信息，难以排查根因
4. 如果上层有重试逻辑，会叠加重试造成无限循环风暴

### ✅ 正确示例（所有等待都有超时+超时错误明确）

```python
class WaitTimeoutError(Exception):
    """明确的超时异常类型，上层可以针对性处理"""
    pass

def wait_for_state(device_id: str, controller, expected_switch: bool,
                   timeout: float = 30.0, interval: float = 1.0,
                   check_online: bool = True) -> bool:
    """
    等待设备状态达到期望值，带超时保护
    
    Args:
        timeout: 最长等待时间（秒），默认30秒
        interval: 轮询间隔（秒）
        check_online: 是否先检查设备在线状态
    
    Raises:
        WaitTimeoutError: 超时未达到期望状态
        DeviceOfflineError: 设备离线
    """
    start_time = time.time()
    last_state = None
    online_check_done = False
    
    while True:
        elapsed = time.time() - start_time
        
        # 强制超时检查，每次循环都判断
        if elapsed > timeout:
            raise WaitTimeoutError(
                f"等待设备 {device_id} 状态变为 {expected_switch} 超时。\n"
                f"已等待 {elapsed:.1f} 秒，最后已知状态：{last_state}\n"
                f"可能原因：设备离线、DP点配置错误、网络故障、设备启动异常"
            )
        
        state = controller.get_device_state(device_id)
        last_state = state
        
        # 可选：检查在线状态
        if check_online and not state.get("online", True):
            raise DeviceOfflineError(
                f"设备 {device_id} 离线，请检查电源和网络"
            )
        
        if state.get("switch") == expected_switch:
            print(f"状态已达到：{expected_switch}（耗时{elapsed:.1f}s）")
            return True
        
        time.sleep(interval)


class DeviceOfflineError(Exception):
    pass
```

---

## 反模式5：所有错误都重试——参数/配置错误也重试

### ❌ 错误示例

```python
def bad_control_with_retry(device_id: str, value: bool, token: str, max_retries=10):
    """反模式：任何错误都重试，不区分错误类型"""
    url = f"https://openapi.tuyacn.com/v1.0/devices/{device_id}/commands"
    headers = {"Authorization": token}
    payload = {"commands": [{"code": "switch_1", "value": value}]}
    
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            result = resp.json()
            if result.get("success"):
                return True
            # 反模式：不管什么错误码都重试
            print(f"第{attempt+1}次尝试失败，重试中...")
            time.sleep(1)
        except Exception as e:
            # 反模式：捕获所有异常都重试
            print(f"异常: {e}，重试中...")
            time.sleep(1)
    
    return False
    # 问题：
    # 1. token错误/无效→重试10次还是错误，浪费时间
    # 2. DP点不存在→重试多少次都没用
    # 3. 设备ID写错→重试永远不会成功
    # 4. 还可能触发API限流/封禁
```

### 🐛 问题说明

错误分为可重试错误和不可重试错误，盲目重试所有错误：
- **浪费时间**：参数错误重试多少次都不会成功
- **触发限流**：无效请求过多触发API限流，影响正常请求
- **掩盖问题**：配置错误本应该在开发阶段就暴露，重试把问题拖到运行时
- **日志污染**：大量无效重试日志淹没真正的问题

### ✅ 正确示例（错误分类，选择性重试）

```python
import requests
from http import HTTPStatus
from typing import Optional

class RetryableError(Exception):
    """可重试错误：网络问题、服务端临时故障"""
    pass

class NonRetryableError(Exception):
    """不可重试错误：配置问题、参数错误、鉴权失败"""
    pass

class AuthExpiredError(NonRetryableError):
    """token过期特殊处理：刷新token后重试一次"""
    pass


def classify_error(status_code: int, tuya_code: Optional[int], msg: str) -> Exception:
    """根据HTTP状态码和涂鸦错误码分类错误类型"""
    
    # 4xx错误都是客户端/配置错误，不可重试
    if status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND):
        if "not support" in msg.lower() or "code" in msg.lower():
            return NonRetryableError(f"DP点不存在或设备不支持该指令：{msg}")
        return NonRetryableError(f"请求参数错误：{msg}")
    
    if status_code == HTTPStatus.UNAUTHORIZED or tuya_code == 1010:
        return AuthExpiredError(f"Token过期或无效，请刷新token")
    
    if status_code == HTTPStatus.FORBIDDEN:
        return NonRetryableError(f"权限不足：{msg}")
    
    if status_code == HTTPStatus.TOO_MANY_REQUESTS:
        return RetryableError(f"限流，等待后可重试")
    
    # 5xx是服务端错误，可重试
    if status_code >= 500:
        return RetryableError(f"服务端临时故障：HTTP {status_code}")
    
    # 网络错误、超时等连接问题，可重试
    return RetryableError(f"连接异常：{msg}")


def power_on_with_smart_retry(device_id: str, controller, 
                               max_retries: int = 3, 
                               refresh_token_callback=None) -> bool:
    """
    智能重试：区分可重试和不可重试错误
    
    - 网络错误、5xx错误、限流→重试（最多3次）
    - token过期→刷新token后重试1次
    - 参数错误、DP点不存在、权限错误→直接失败，不重试
    """
    url = f"{controller.base_url}/devices/{device_id}/commands"
    payload = {"commands": [{"code": "switch_1", "value": True}]}
    
    token_refreshed = False
    
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, json=payload, 
                               headers=controller.headers, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("success"):
                    # 指令发送成功，继续状态验证
                    return controller.wait_for_state(device_id, True, timeout=30)
            
            # 错误分类
            tuya_code = result.get("code") if 'result' in locals() else None
            err = classify_error(resp.status_code, tuya_code, 
                               result.get("msg", "") if 'result' in locals() else "")
            
            if isinstance(err, AuthExpiredError) and not token_refreshed:
                # 特殊处理：token过期，刷新一次再试
                if refresh_token_callback:
                    print("Token过期，尝试刷新...")
                    new_token = refresh_token_callback()
                    controller.headers["Authorization"] = new_token
                    token_refreshed = True
                    continue
            
            if isinstance(err, NonRetryableError):
                # 配置/参数错误：直接抛出，不重试
                raise err
            
            if isinstance(err, RetryableError):
                if attempt < max_retries:
                    # 指数退避 + 随机抖动（避免并发场景雷群效应）
                    base_wait = 2 ** attempt
                    jitter = random.uniform(0, base_wait * 0.5)  # 0~50%随机抖动
                    wait = base_wait + jitter
                    print(f"可重试错误: {err}，{wait:.1f}秒后第{attempt+1}次重试...")
                    time.sleep(wait)
                    continue
                raise err
        
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                base_wait = 2 ** attempt
                time.sleep(base_wait + random.uniform(0, base_wait * 0.5))
                continue
            raise RetryableError(f"请求超时，重试{max_retries}次后仍失败")
        
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries:
                base_wait = 2 ** attempt
                time.sleep(base_wait + random.uniform(0, base_wait * 0.5))
                continue
            raise RetryableError(f"网络连接失败：{e}")
    
    return False
```

---

## 附录：反模式速查表

| 反模式 | 核心问题 | 一句话修复原则 |
|-------|---------|-------------|
| 1. 信任API返回值 | 返回成功≠执行成功 | 每次操作后查询真实状态验证 |
| 2. 硬编码DP点映射 | 不同设备DP规则不同 | 启动时拉取设备spec校验配置 |
| 3. 本地缓存状态 | 状态会被外部改变 | 每次查询实时API，不缓存 |
| 4. 无超时无限等待 | 异常场景永久挂起 | 所有等待都必须有超时时间 |
| 5. 所有错误都重试 | 参数错误重试也没用 | 错误分类：可重试才重试，配置错误直接报错 |

---

**文档生成时间**：2026-08-03  
**依据**：里程碑复盘[RETROSPECTIVE.md](file:///d:/AI/apps/camera-power-controller/RETROSPECTIVE.md)中的核心洞察与萃取模式  
**代码示例语言**：Python 3（核心逻辑模式可迁移到任意语言）

---

## V审查记录

经方法论编排V阶段（4视角对抗审查），共发现4个问题并修正：

| 视角 | 发现问题 | 修正情况 |
|-----|---------|---------|
| 🔴 魔鬼代言人 | P0-7"50行以内"太主观，API路径为凭记忆编写 | ✅ P0-7改为"不依赖闭源工具/SDK，标准HTTP可实现"；添加API路径示例说明 |
| 🔴 魔鬼代言人 | 指数退避无抖动，并发场景有雷群效应 | ✅ 添加0~50%随机抖动 |
| 🟢 新人视角 | "DP点"术语未解释 | ✅ 首次出现添加术语注释 |
| 🟢 新人视角 | 无参考链接 | ✅ 添加涂鸦IoT平台参考链接 |

**版本**：V1.1（对抗审查修正版）
