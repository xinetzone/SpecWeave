---
type: Concept
title: 设备控制抽象层
description: MobileDeviceController Protocol、Android/iOS平台实现、Factory工厂函数、UnifiedMobileController门面与坐标系统
tags: [mobile-use, device, controller, protocol, android, ios, adb, wda, idb]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: mobile-use-source
    resource: "/references/mobile-use-source.md"
    title: mobile-use 源码
  - id: facts
    resource: "/references/facts.md"
    title: mobile-use 事实清单
---

# 设备控制抽象层

设备控制层是 mobile-use 与物理/虚拟移动设备交互的基础。它通过三层抽象——Protocol 接口定义、平台具体实现、UnifiedController 门面——为上层 Agent 和工具提供统一的跨平台设备操作 API，同时隔离 Android 和 iOS 的底层差异。

## 三层抽象架构

```text
┌─────────────────────────────────────────┐
│        UnifiedMobileController          │  门面层：高级操作（tap_element等）
├─────────────────────────────────────────┤
│     create_device_controller() 工厂     │  工厂层：平台选择
├──────────────┬──────────────────────────┤
│ AndroidDevice│  iOSDeviceController     │  实现层：Protocol 实现
│ Controller   │  (IDB / WDA 适配)        │
├──────────────┴──────────────────────────┤
│   MobileDeviceController (Protocol)     │  抽象层：18个方法签名
└─────────────────────────────────────────┘
```

## MobileDeviceController Protocol

`MobileDeviceController` 是一个 Python `Protocol`（结构子类型协议），定义了设备控制器必须实现的 18 个抽象方法 [F-100]。与抽象基类（ABC）不同，Protocol 不需要显式继承——任何实现了匹配方法签名的对象都自动满足该协议，这使得云设备控制器可以无缝替换本地控制器。

### 方法清单

| 方法 | 返回类型 | 用途 |
|------|---------|------|
| `tap(coords, long_press, long_press_duration)` | `TapOutput` | 点击/长按指定坐标 |
| `swipe(start, end, duration)` | `str \| None` | 滑动操作 |
| `screenshot()` | `str` | 截图（原始图片数据） |
| `input_text(text)` | `bool` | 在当前焦点输入文本 |
| `launch_app(package_or_bundle_id)` | `bool` | 启动应用 |
| `terminate_app(package_or_bundle_id)` | `bool` | 终止应用 |
| `open_url(url)` | `bool` | 打开 URL |
| `press_back()` | `bool` | 返回键 |
| `press_home()` | `bool` | Home 键 |
| `press_enter()` | `bool` | 回车/确认键 |
| `get_ui_hierarchy()` | `list[dict]` | 获取 UI 元素层级 |
| `find_element(ui_hierarchy, resource_id, text, index)` | `tuple` | 在层级中查找元素 |
| `cleanup()` | `None` | 清理资源 |
| `erase_text(nb_chars)` | `bool` | 删除字符 |
| `get_screen_data()` | `ScreenDataResponse` | 获取屏幕完整数据 |
| `get_compressed_b64_screenshot(image_base64, quality)` | `str` | 压缩截图 |
| `start_video_recording(max_duration_seconds)` | `VideoRecordingResult` | 开始录屏 |
| `stop_video_recording()` | `VideoRecordingResult` | 停止录屏 |

### ScreenDataResponse

`ScreenDataResponse` 是 `get_screen_data()` 的返回类型，封装一次屏幕快照的全部信息 [F-101]：

- `base64: str`：截图的 base64 编码
- `elements: list`：UI 元素列表
- `width: int`：屏幕宽度
- `height: int`：屏幕高度
- `platform: str`：平台标识（"android" 或 "ios"）

## AndroidDeviceController

`AndroidDeviceController` 实现 MobileDeviceController Protocol，通过 ADB 和 uiautomator2 控制 Android 设备 [F-107]。

### 构造与依赖

```python
AndroidDeviceController(
    device_id: str,
    adb_client: AdbClient,
    ui_adb_client: UIAutomatorClient,
    device_width: int,
    device_height: int,
)
```

控制器持有两个客户端：`adb_client`（adbutils 库的 ADB 连接，用于 shell 命令和应用管理）和 `ui_adb_client`（uiautomator2 封装，用于 UI 层级和截图）。`device` 属性懒加载 `AdbDevice` 实例 [F-109]。

### tap 实现

Android 的 tap 操作通过 ADB shell 命令实现 [F-108]：

- 普通点击：`input tap x y`
- 长按：`input swipe x y x y duration`（通过在同一坐标执行 swipe 模拟长按）

UIAutomatorClient 在连接前会检查并卸载 Maestro 包（`dev.mobile.maestro`），因为 Maestro 与 uiautomator2 存在冲突 [F-246]。文本输入使用 FastInputIME 以支持特殊字符 [F-247]。

## iOSDeviceController

`iOSDeviceController` 同样实现 Protocol，通过 `IosClientWrapper` 抽象控制 iOS 设备 [F-110]。构造函数通过 `isinstance(ios_client, IdbClientWrapper)` 判断底层使用 IDB 还是 WDA。

### IDB vs WDA

iOS 控制有两种后端：

- **IDB（fb-idb）**：用于 iOS 模拟器，由 `IdbClientWrapper` 封装，通过 idb-companion 进程通信
- **WDA（WebDriverAgent）**：用于物理 iOS 设备，由 `WdaClientWrapper` 封装 facebook-wda 库

`WdaClientWrapper` 在初始化时自动检查/启动 iproxy（端口转发）和 WDA（通过 xcodebuild 构建运行），然后创建 WDA session [F-251]。它将 WDA 返回的 XML 源码解析为扁平元素列表，元素包含 type、value、label、frame（x/y/width/height）、enabled、visible 等字段 [F-255]。

iOS 的 tap 操作直接委托给 `self.ios_client.tap(x, y, duration)` [F-111]，底层根据客户端类型调用 IDB 或 WDA 的对应方法。

## 工厂函数

`create_device_controller(ctx: MobileUseContext) -> MobileDeviceController` 是设备控制器的工厂函数 [F-112]。它根据 `ctx.device.mobile_platform` 选择实现：

**Android 路径**：
1. 若 `ctx.limrun_android_controller` 不为 None（云设备），直接返回该控制器
2. 否则检查 `adb_client` 和 `ui_adb_client` 是否已初始化
3. 创建并返回 `AndroidDeviceController`

**iOS 路径**：
1. 检查 `ios_client` 是否已初始化
2. 创建并返回 `iOSDeviceController`

`get_controller(ctx)` 是 `create_device_controller` 的别名 [F-113]。

工厂函数的设计使得上层代码（Agent、工具）无需知道目标平台——它们只面向 MobileDeviceController Protocol 编程。云手机控制器（LimrunAndroidController）只要实现了相同的方法签名，就能直接注入，无需修改任何上层代码。

## UnifiedMobileController

`UnifiedMobileController` 是设备控制器的门面（Facade），封装底层 `MobileDeviceController` 实例并提供更高级的操作方法 [F-114]。它通过 `get_controller(ctx)` 获取底层控制器。

### 坐标操作方法

| 方法 | 用途 |
|------|------|
| `tap_at(x, y, long_press, long_press_duration)` | 绝对像素坐标点击 |
| `tap_percentage(x_percent, y_percent, ...)` | 百分比坐标点击（0-100） |
| `swipe_coords(start_x, start_y, end_x, end_y, duration)` | 绝对坐标滑动 |
| `swipe_percentage(...)` | 百分比坐标滑动 |
| `swipe_request(request: SwipeRequest)` | 通过 SwipeRequest 对象滑动 |

百分比坐标通过设备宽高自动转换：`PercentagesSelectorRequest(x_percent, y_percent).to_coords(width, height)` [F-105]。

### 元素操作方法

`tap_element(resource_id, text, index, long_press, long_press_duration)` 是最常用的高级方法 [F-115]，它封装了三步操作：

1. 调用 `get_ui_hierarchy()` 获取当前 UI 层级
2. 调用 `find_element(ui_hierarchy, resource_id, text, index)` 查找元素
3. 提取元素边界（Bounds），计算中心点，调用 `tap(center)`

### 委托方法

UnifiedMobileController 还将以下方法直接委托给底层控制器：

- `type_text(text)` → `input_text(text)`
- `take_screenshot()` → `screenshot()`
- `launch_app(package)` / `terminate_app(package)` / `open_url(url)`
- `go_back()` → `press_back()`
- `go_home()` → `press_home()`
- `press_enter()` / `erase_text(nb_chars)`
- `get_ui_elements()` → `get_ui_hierarchy()`
- `cleanup()`

## 坐标与元素类型系统

controllers/types.py 定义了设备控制的核心数据类型：

### TapOutput

点击操作的返回类型，仅有一个 `error: str | None = None` 字段 [F-102]。None 表示成功，非 None 包含错误信息。

### Bounds

表示元素边界矩形，字段为 `x1, y1, x2, y2` [F-103]。`get_center()` 方法返回 `CoordinatesSelectorRequest`（中心点坐标）。

### CoordinatesSelectorRequest

绝对坐标请求，配置 `extra="forbid"`（禁止额外字段），字段为 `x: int, y: int` [F-104]。

### PercentagesSelectorRequest

百分比坐标请求，字段为 `x_percent: int`（0-100）、`y_percent: int`（0-100）[F-105]。`to_coords(width, height)` 方法将百分比转换为绝对像素坐标。

### SwipeRequest

滑动请求，配置 `extra="forbid"`，字段为 [F-106]：
- `swipe_mode`：`SwipeStartEndCoordinatesRequest` 或 `SwipeStartEndPercentagesRequest`
- `duration: int | None`：滑动时长（1-10000 毫秒）

## 云设备控制器

除了本地 Android 和 iOS 控制器，mobile-use 还支持云设备控制器：

- **LimrunAndroidController / LimrunIosController**：通过 Limrun API 控制云设备，实现 MobileDeviceController Protocol
- **BrowserStackClientWrapper**：BrowserStack 云 iOS 设备

这些控制器通过 `AgentConfigBuilder` 的 `with_limrun_android_controller()`、`with_limrun_ios_controller()` 或 `for_browserstack()` 方法注入，工厂函数会优先使用它们而非创建本地控制器 [F-197]。

## ADB WebSocket 隧道

`AdbTunnel` 类通过 WebSocket 桥接本地 TCP 连接到远程 ADB 服务器，用于云设备场景 [F-240]。它在独立线程中运行 asyncio 事件循环，实现双向数据转发（tcp_to_ws 和 ws_to_tcp），缓冲区大小 32KB，心跳间隔 30 秒 [F-244]。`adb_tunnel(remote_url, token)` 异步上下文管理器封装了隧道的 start/stop 生命周期 [F-243]。

## 相关概念

- [多 Agent 协作架构](/concepts/01-multi-agent-architecture.md)
- [工具系统与执行节点](/concepts/03-tools-system.md)
- [SDK 双层 API 与生命周期](/concepts/05-sdk-layer.md)
- [mobile-use 项目概览](/concepts/00-overview.md)
