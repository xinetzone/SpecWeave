# 摄像头通断电自动化测试系统方案说明书

**版本**：V1.0  
**日期**：2026-07-06  
**状态**：方案评审

---

## 目录

1. [项目背景与目标](#1-项目背景与目标)
2. [整体架构设计](#2-整体架构设计)
3. [硬件选型方案](#3-硬件选型方案)
4. [软件模块设计](#4-软件模块设计)
5. [核心流程设计](#5-核心流程设计)
6. [可靠性保障机制](#6-可靠性保障机制)
7. [测试场景与用例](#7-测试场景与用例)
8. [使用方式](#8-使用方式)
9. [实施计划](#9-实施计划)
10. [风险评估与应对](#10-风险评估与应对)
11. [方案优势对比](#11-方案优势对比)

---

## 1. 项目背景与目标

### 1.1 背景

在摄像头设备的研发与测试过程中，通断电测试是验证设备稳定性、冷启动可靠性、异常恢复能力的重要环节。传统手动插拔电源的方式存在以下问题：

- **效率低下**：手动操作无法支持长时间压力测试和批量设备测试
- **不可重复**：人工操作时序不一致，测试结果难以复现
- **无法量化**：缺乏准确的时间记录和成功率统计
- **人力成本高**：压力循环测试需要人员值守

### 1.2 建设目标

基于涂鸦智能插座OpenAPI构建一套完整的摄像头通断电自动化测试系统，实现：

| 目标 | 说明 |
|-----|------|
| **自动化控制** | 通过API远程控制智能插座开关，替代手动插拔电源 |
| **状态可验证** | 双层验证机制：电源状态验证 + 摄像头业务就绪检测 |
| **过程可追溯** | 结构化日志记录所有操作，测试结果可导出JSON报告 |
| **场景全覆盖** | 支持冷启动、压力循环、批量测试、异常断电等标准场景 |
| **框架可扩展** | 支持pytest集成，可作为fixture嵌入现有自动化测试体系 |
| **结果可量化** | 自动统计成功率、失败次数、平均耗时等关键指标 |

### 1.3 适用范围

- 摄像头冷启动测试
- 电源稳定性压力测试
- 异常断电恢复测试
- 多设备批量回归测试
- 长时间老化测试
- 上电时序兼容性测试

---

## 2. 整体架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                     测试执行层 (pytest / CLI / Python API)          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  冷启动测试   │  │  压力循环测试  │  │ 多摄像头批量  │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                  │                      │
│  ┌──────┴─────────────────┴──────────────────┴───────┐             │
│  │              测试基类 + 结果统计 + JSON报告       │             │
│  └──────────────────────┬────────────────────────────┘             │
├─────────────────────────┼───────────────────────────────────────────┤
│                         │                                           │
│  ┌──────────────────────┴────────────────────────────┐             │
│  │  核心控制层 (CameraPowerController)                │             │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │             │
│  │  │ 电源控制   │  │ 状态验证   │  │ 就绪检测   │   │             │
│  │  │ on/off/cyc │  │ 轮询等待   │  │ 钩子机制   │   │             │
│  │  └────────────┘  └────────────┘  └────────────┘   │             │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │             │
│  │  │ 异常处理   │  │ 重试机制   │  │ 结构化日志 │   │             │
│  │  └────────────┘  └────────────┘  └────────────┘   │             │
│  └──────────────────────┬────────────────────────────┘             │
├─────────────────────────┼───────────────────────────────────────────┤
│  ┌──────────────────────┴────────────────────────────┐             │
│  │           通信层 (Tuya OpenAPI SDK)                │             │
│  │  HMAC-SHA256签名 · 自动区域检测 · HTTP超时重试     │             │
│  └──────────────────────┬────────────────────────────┘             │
└─────────────────────────┼───────────────────────────────────────────┘
                          │ HTTPS (Internet)
                          ▼
              ┌───────────────────────┐
              │    涂鸦云 OpenAPI     │
              └───────────┬───────────┘
                          │ WiFi 2.4GHz
                          ▼
         ┌────────┐  ┌────────┐  ┌────────┐
         │ 插座 1 │  │ 插座 2 │  │ 插座 N │
         └───┬────┘  └───┬────┘  └───┬────┘
             │           │           │
             ▼           ▼           ▼
         ┌───────┐   ┌───────┐   ┌───────┐
         │摄像头1│   │摄像头2│   │摄像头N│
         └───────┘   └───────┘   └───────┘
```

### 2.2 架构分层说明

| 层级 | 名称 | 职责 |
|-----|------|-----|
| L4 | 测试执行层 | 具体测试场景实现、pytest fixture、CLI命令入口 |
| L3 | 测试框架层 | 测试基类、结果统计、JSON报告生成 |
| L2 | 核心控制层 | 电源控制、状态验证、就绪检测钩子、异常处理、日志 |
| L1 | 通信层 | 涂鸦云OpenAPI封装（已有SDK，无需修改） |
| L0 | 硬件层 | 涂鸦智能插座 + 摄像头设备 |

---

## 3. 硬件选型方案

### 3.1 智能插座选型

| 选型维度 | 推荐方案 | 说明 |
|---------|---------|------|
| **生态** | 涂鸦生态（Tuya） | OpenAPI开放、成熟稳定、社区资源丰富 |
| **联网方式** | WiFi版（2.4GHz） | 无需网关、成本低、API直连延迟低 |
| **插孔数量** | 单孔插座（优先） | 一个插座对应一个摄像头，灵活独立控制 |
| **品类码** | category = 'cz'（插座） | 标准品类，API兼容性最好 |
| **计量功能** | 可选（非必须） | 需要功耗分析时选计量版，贵约10-20元 |
| **参考价格** | 20-40元/个 | 涂鸦生态单孔WiFi智能插座 |
| **推荐品牌** | 涂鸦智选、公牛涂鸦版、贝锐向日葵C2等 | 均兼容涂鸦标准API |

### 3.2 硬件清单

| 物品 | 要求 | 数量 |
|-----|------|-----|
| 涂鸦智能WiFi插座 | 单孔、2.4GHz、支持涂鸦OpenAPI | 与摄像头数量一致 |
| 涂鸦End User API Key | sk-开头，从涂鸦IoT平台获取 | 1个 |
| 测试执行机 | Windows/Linux/macOS、Python 3.8+、可访问外网 | 1台 |
| 摄像头设备 | 支持上电自动启动（或测试不要求业务验证） | 按需 |

### 3.3 硬件准备步骤

1. 插座通电，指示灯进入待配网状态
2. 使用「涂鸦智能」APP完成WiFi配网（仅支持2.4GHz WiFi）
3. 确认APP中可以正常手动控制插座开关
4. 在涂鸦IoT平台创建云开发项目，获取API Key
5. 将设备绑定到API Key对应的账号下
6. 运行discover命令验证设备可被API发现

---

## 4. 软件模块设计

### 4.1 模块清单

| 模块文件 | 职责 | 状态 |
|---------|------|------|
| `camera_power.py` | 核心控制类，包含电源控制、状态验证、重试逻辑 | **已有基础，需增强** |
| `test_framework.py` | 测试基类、标准测试场景、结果统计、报告生成 | **新建** |
| `logger.py` | 结构化日志模块（控制台彩色输出 + 文件输出） | **新建** |
| `conftest.py` | pytest fixture示例 | **新建** |
| `config.example.json` | 配置文件模板 | **已有，需更新** |
| `test_examples.py` | 使用示例代码 | **已有，需更新** |
| `README.md` | 使用文档 | **新建** |

### 4.2 核心类设计

#### CameraPowerController（核心控制类）

```python
class CameraPowerController:
    """摄像头电源控制器 - 核心控制类"""
    
    def __init__(self, api_key: str, config_path: str = None):
        """初始化控制器，加载配置，校验设备DP点"""
        
    def power_on(self, camera_name: str, wait: bool = True, 
                 wait_time: float = None) -> bool:
        """开启摄像头电源，wait=True时等待状态验证通过"""
        
    def power_off(self, camera_name: str, wait: bool = True,
                  wait_time: float = None) -> bool:
        """关闭摄像头电源"""
        
    def power_cycle(self, camera_name: str, off_time: float = 5.0,
                    on_wait_time: float = None) -> bool:
        """冷启动：断电→等待off_time→上电→等待就绪"""
        
    def get_device_state(self, camera_name: str) -> PowerState:
        """查询真实电源状态（调用API实时查询，非缓存）"""
        
    def wait_for_state(self, camera_name: str, target_state: PowerState,
                       timeout: float = None) -> bool:
        """轮询等待电源状态达到目标状态"""
        
    def register_ready_check(self, camera_name: str, 
                             check_func: Callable[[], bool]):
        """注册摄像头业务就绪检测回调函数"""
        
    def power_on_and_wait_ready(self, camera_name: str) -> bool:
        """上电并等待摄像头业务就绪（电源ON + 就绪检测通过）"""
        
    def discover_plugs(self) -> List[dict]:
        """发现账号下所有可用智能插座，列出支持的properties"""
```

#### 测试基类与标准用例

```python
class CameraPowerTest:
    """摄像头电源测试基类"""
    
    def setup(self):
        """前置检查：设备在线、配置正确"""
        
    def teardown(self):
        """后置清理：确保所有设备断电（可选）"""
        
    def run(self) -> TestResult:
        """执行测试，返回结构化结果"""

class ColdBootTest(CameraPowerTest):
    """冷启动测试：断电→等待→上电→等待就绪"""

class StressTest(CameraPowerTest):
    """压力循环测试：N次通断电循环，统计成功率"""

class MultiCameraTest(CameraPowerTest):
    """多摄像头批量测试：顺序/错开启动多个摄像头"""
```

### 4.3 配置文件设计

配置文件采用JSON格式，支持环境变量覆盖敏感信息：

```json
{
  "api_key": "",
  "default_timeout": 30,
  "retry_count": 3,
  "retry_interval": 1.0,
  "off_wait_time": 5.0,
  "boot_wait_time": 30.0,
  "log_level": "INFO",
  "log_file": "camera_power.log",
  "cameras": {
    "camera-01": {
      "device_id": "vdevo1234567890abcdef",
      "switch_property": "switch_1",
      "ip_address": "192.168.1.101",
      "ready_timeout": 60
    }
  }
}
```

**环境变量优先级高于配置文件**：
- `TUYA_API_KEY`：覆盖api_key
- `TUYA_CONFIG_PATH`：指定配置文件路径

---

## 5. 核心流程设计

### 5.1 单次上电流程（含状态验证）

```
开始
  ↓
检查设备online状态
  ├─ 离线 → 抛出DeviceOfflineError → 记录ERROR日志 → 结束（失败）
  ↓ 在线
发送power_on指令
  ↓
等待状态轮询开始
  ↓
循环（最多retry_count次）：
  ├─ 调用get_device_state()查询真实状态
  ├─ 状态=ON → 验证通过 → 记录INFO日志 → 结束（成功）
  ├─ 状态=OFF → 等待retry_interval
  └─ 达到重试次数 → 记录WARNING → 重发控制指令
  ↓
达到超时时间 → 记录ERROR日志 → 结束（失败）
```

### 5.2 冷启动测试流程

```
开始冷启动测试
  ↓
[前置检查] 设备在线？配置正确？
  ↓
执行power_off，等待电源状态=OFF
  ↓
等待off_time（默认5秒，模拟完全断电）
  ↓
执行power_on
  ↓
等待电源状态=ON（最长boot_wait_time）
  ├─ 超时 → 记录失败 → 结束
  ↓
是否注册了ready_check？
  ├─ 是 → 轮询调用check_func()，等待返回True
  │        ├─ 超时 → 记录失败 → 结束
  │        └─ 返回True → 记录成功
  └─ 否 → 直接记录成功
  ↓
统计本次耗时 → 输出结果 → 结束
```

### 5.3 压力循环测试流程

```
开始压力测试（N次循环）
  ↓
初始化统计：passed=0, failed=0, failures=[]
  ↓
循环 i = 1 到 N:
  ├─ 打印进度：Cycle i/N
  ├─ 执行一次power_cycle（冷启动流程）
  ├─ 成功 → passed += 1，记录耗时
  └─ 失败 → failed += 1，记录失败原因到failures
  ↓
计算统计：成功率 = passed/N × 100%，平均耗时，总耗时
  ↓
输出控制台结果
  ↓
生成JSON测试报告
  ↓
结束
```

### 5.4 摄像头就绪检测钩子机制

框架不内置具体的摄像头业务检测逻辑，而是通过回调钩子支持用户自定义：

| 检测方式 | 实现方式 | 适用场景 |
|---------|---------|---------|
| ICMP Ping | 内置提供`ping_camera(ip)`函数 | 验证网络层启动完成 |
| HTTP接口探测 | 用户自定义回调，请求摄像头HTTP API | 验证应用层启动完成 |
| RTSP流检测 | 用户自定义回调，尝试连接RTSP端口 | 验证视频流可用 |
| 图像识别 | 用户自定义回调，分析画面内容 | 验证图像输出正常 |

**钩子函数签名**：
```python
def my_ready_check() -> bool:
    """返回True表示摄像头就绪，False表示未就绪"""
    # 自定义检测逻辑
    return True

# 注册回调
controller.register_ready_check("camera-01", my_ready_check)
```

---

## 6. 可靠性保障机制

基于涂鸦API的历史经验教训，框架在设计上重点解决以下可靠性问题：

### 6.1 常见问题与应对策略

| 问题现象 | 根因分析 | 应对策略 |
|---------|---------|---------|
| API返回success但设备未动作 | 云端接收指令但设备离线/指令未达 | ✅ **强制状态验证**：每次操作后轮询查询真实状态，不依赖返回值 |
| token过期导致请求失败 | token有效期有限，SDK未自动刷新 | ✅ 认证错误时清空token重试一次，失败则明确报错 |
| 网络波动导致指令丢失 | WiFi/公网不稳定 | ✅ HTTP层3次自动重试，控制层状态验证不通过则重发指令 |
| DP点配置错误 | switch_property填错，下发到不存在的DP点 | ✅ 启动时查询设备真实properties，校验配置是否合法 |
| 设备离线指令静默失败 | 插座断电/断网，API不报错 | ✅ 每次操作前先检查online字段，离线直接抛出异常 |
| 无限等待挂起 | 异常场景下状态一直不匹配 | ✅ 所有等待操作都有超时时间（可配置），超时明确失败 |

### 6.2 重试策略设计

| 错误类型 | 是否重试 | 重试次数 | 说明 |
|---------|---------|---------|------|
| 网络超时/连接错误 | ✅ 是 | 3次 | 网络波动是临时问题，重试有效 |
| HTTP 5xx错误 | ✅ 是 | 3次 | 服务端临时故障 |
| HTTP 401未授权 | ✅ 是（刷新token） | 1次 | 清空token重新获取后重试 |
| HTTP 4xx参数错误 | ❌ 否 | 0次 | 参数错误重试也没用，直接报错 |
| 设备离线 | ❌ 否 | 0次 | 需要人工排查设备问题 |
| DP点不存在 | ❌ 否 | 0次 | 配置错误，需要修正配置 |

### 6.3 超时配置建议

| 超时项 | 默认值 | 说明 |
|-------|-------|------|
| HTTP请求超时 | 10秒 | 单次API请求超时 |
| 电源状态切换等待 | 30秒 | 继电器动作+状态上报到云端的时间 |
| 摄像头启动等待 | 60秒 | 从上电到业务就绪的时间（根据摄像头启动速度调整） |
| 重试间隔 | 1秒 | 两次重试之间的等待 |

---

## 7. 测试场景与用例

### 7.1 标准测试场景

#### 场景1：冷启动测试（Cold Boot Test）

| 项 | 说明 |
|---|------|
| **测试目的** | 验证摄像头断电后重新上电能否正常启动 |
| **测试流程** | 断电 → 等待5秒 → 上电 → 等待启动 → 验证就绪 |
| **关键指标** | 启动成功率、平均启动时间 |
| **适用阶段** | 功能验证、回归测试 |

#### 场景2：压力循环测试（Stress Test）

| 项 | 说明 |
|---|------|
| **测试目的** | 验证多次通断电循环下的稳定性，发现偶现启动失败问题 |
| **测试流程** | 重复执行N次冷启动流程（如100次、1000次） |
| **关键指标** | 累计成功率、失败次数、失败原因分布、P95启动耗时 |
| **适用阶段** | 稳定性测试、老化测试 |

#### 场景3：多摄像头批量测试（Multi-Camera Test）

| 项 | 说明 |
|---|------|
| **测试目的** | 同时验证多个摄像头的电源控制，支持批量回归 |
| **测试流程** | 顺序（或错开间隔）执行多台设备的冷启动测试 |
| **关键指标** | 单台成功率、总耗时、批量执行稳定性 |
| **适用阶段** | 批量回归测试 |

#### 场景4：异常断电测试（Abnormal Power Cut）

| 项 | 说明 |
|---|------|
| **测试目的** | 模拟不同断电时长、运行中突然断电等异常场景 |
| **测试流程** | 随机断电时长（1s/3s/5s/10s/30s）、运行中断电 |
| **关键指标** | 不同断电时长下的恢复成功率 |
| **适用阶段** | 兼容性测试、边界测试 |

### 7.2 测试报告输出

测试完成后输出JSON格式报告，示例结构：

```json
{
  "test_name": "stress_test_camera-01",
  "test_type": "stress_test",
  "start_time": "2026-07-06T10:00:00",
  "end_time": "2026-07-06T10:30:00",
  "duration_seconds": 1800,
  "target_camera": "camera-01",
  "config": {
    "cycles": 100,
    "off_time": 5,
    "boot_timeout": 60
  },
  "statistics": {
    "total_cycles": 100,
    "success_count": 98,
    "failure_count": 2,
    "success_rate": 98.0,
    "avg_boot_time_seconds": 23.5,
    "min_boot_time_seconds": 18.2,
    "max_boot_time_seconds": 45.1
  },
  "failures": [
    {
      "cycle": 23,
      "phase": "wait_ready",
      "reason": "ready check timeout after 60s",
      "timestamp": "2026-07-06T10:07:45"
    },
    {
      "cycle": 67,
      "phase": "power_on",
      "reason": "state verification timeout: state still OFF after 30s",
      "timestamp": "2026-07-06T10:20:12"
    }
  ]
}
```

---

## 8. 使用方式

### 8.1 CLI命令行使用

```bash
# 1. 生成配置模板
python camera_power.py --init-config config.json

# 2. 发现设备（获取device_id和支持的DP点）
set TUYA_API_KEY=sk-xxxxxx
python camera_power.py --discover

# 3. 编辑config.json填入设备信息

# 4. 基础控制
python camera_power.py --config config.json --on camera-01
python camera_power.py --config config.json --off camera-01
python camera_power.py --config config.json --cycle camera-01
python camera_power.py --config config.json --status

# 5. 冷启动测试
python camera_power.py --config config.json --cold-boot camera-01

# 6. 压力循环测试
python camera_power.py --config config.json --stress-test camera-01 --cycles 100

# 7. 输出JSON报告
python camera_power.py --config config.json --stress-test camera-01 --cycles 100 --json-output result.json
```

### 8.2 Python API使用

```python
from camera_power import CameraPowerController, PowerState

# 初始化
controller = CameraPowerController(
    api_key="sk-xxxxxx",
    config_path="config.json"
)

# 简单上电
controller.power_on("camera-01", wait=True)

# 冷启动
controller.power_cycle("camera-01", off_time=5.0)

# 自定义就绪检测
def check_camera_ready():
    import subprocess
    return subprocess.run(["ping", "-c", "1", "192.168.1.101"],
                          capture_output=True).returncode == 0

controller.register_ready_check("camera-01", check_camera_ready)
controller.power_on_and_wait_ready("camera-01")
```

### 8.3 pytest集成使用

```python
# conftest.py中配置fixture
import pytest
from camera_power import CameraPowerController

@pytest.fixture(scope="session")
def camera_controller():
    controller = CameraPowerController(api_key="sk-xxxxxx")
    yield controller
    controller.power_off_all()  # 测试结束后断电

# 测试文件中使用
def test_camera_cold_boot(camera_controller):
    """测试摄像头冷启动功能"""
    # 冷启动
    assert camera_controller.power_cycle("camera-01")
    # 这里继续执行业务测试...
```

---

## 9. 实施计划

项目基于已有[camera_power.py](file:///d:/AI/apps/camera-power-controller/camera_power.py)基础代码增强，预计分3个阶段实施：

### 阶段一：核心控制层增强（预计1-2天）

- 增强状态验证逻辑：操作后轮询验证真实状态
- 添加设备在线检查、DP点校验
- 完善异常分类和重试策略
- 实现结构化日志模块

### 阶段二：测试框架与标准场景（预计1-2天）

- 实现测试基类和结果统计
- 实现冷启动、压力循环、批量测试标准用例
- 实现就绪检测钩子机制（含内置ping）
- 实现JSON报告输出
- CLI命令增强

### 阶段三：pytest集成与文档（预计1天）

- pytest fixture示例
- 单元测试编写
- 使用文档和README
- 端到端验证

**总工期预计：3-5个工作日**

---

## 10. 风险评估与应对

| 风险项 | 可能性 | 影响 | 应对措施 |
|-------|-------|-----|---------|
| 涂鸦API限流/封禁 | 低 | 中 | 控制请求频率（间隔≥1秒），不短时间大量请求 |
| 插座离线率高 | 中 | 中 | 测试前前置检查设备在线状态，离线明确报错提示排查 |
| WiFi不稳定导致指令延迟 | 中 | 低 | 延长超时时间配置，增加重试次数 |
| 摄像头启动时间过长 | 中 | 低 | ready_timeout配置项可调，根据实际设备调整 |
| 涂鸦API变更/不兼容 | 低 | 高 | 锁定API版本，接口变更时适配SDK层 |
| 多设备同时上电导致跳闸 | 低 | 中 | 批量测试时支持stagger_seconds错开启动 |

---

## 11. 方案优势对比

### 11.1 与其他方案对比

| 方案 | 可靠性 | 成本 | 开发量 | 可扩展性 | 推荐度 |
|-----|-------|-----|-------|---------|-------|
| **涂鸦智能插座 + OpenAPI（本方案）** | ⭐⭐⭐⭐⭐ | 低（20-40元/路） | 小（已有70%基础） | ⭐⭐⭐⭐⭐ | ✅ 推荐 |
| 向日葵P1Pro + ADB曲线控制 | ⭐⭐⭐ | 中（~35元/路） | 大（需ADB+UI自动化） | ⭐⭐ | ❌ 不推荐 |
| 向日葵MCP/CLI直接控制 | ⭐⭐⭐⭐⭐ | 中 | 无（等官方开放） | ⭐⭐⭐ | ⏳ 等待官方API |
| 继电器模块 + 串口/USB控制 | ⭐⭐⭐⭐ | 中 | 大（需硬件开发） | ⭐⭐ | 适合嵌入式场景 |
| 手动插拔电源 | ⭐ | 极低 | 无 | ⭐ | ❌ 不适合自动化 |

### 11.2 本方案核心优势

1. **✅ 成熟可靠**：涂鸦OpenAPI是经过大规模验证的成熟方案
2. **✅ 成本低廉**：单路成本20-40元，批量部署成本低
3. **✅ 开发快速**：已有基础代码，增强即可使用，3-5天可完成
4. **✅ 框架完善**：内置重试、状态验证、日志、报告、pytest集成
5. **✅ 易于扩展**：就绪检测钩子机制支持任意摄像头型号
6. **✅ 避免踩坑**：基于历史经验设计，针对性解决了"返回成功但未动作"等常见问题

---

## 附录

### 参考文档

- 涂鸦智能开放平台：https://developer.tuya.com
- 现有基础代码：[camera_power.py](file:///d:/AI/apps/camera-power-controller/camera_power.py)
- 涂鸦SDK封装：[tuya_api.py](file:///d:/AI/.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py)

### 文档变更记录

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| V1.0 | 2026-07-06 | 初始版本，完成方案设计 |
