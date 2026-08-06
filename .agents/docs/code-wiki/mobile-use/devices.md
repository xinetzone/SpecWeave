---
source: d:\AI\.chaos\libs\mobile-use
---

# 设备适配层

## 双层适配器架构

mobile-use 的设备适配层采用 **Controller + Client** 双层设计，严格分离"高层操作语义"和"底层通信协议"：

```
┌─────────────────────────────────────────────────────┐
│                    Tool Layer                       │
│  tap / swipe / input / launch_app / ...             │
└─────────────────────┬───────────────────────────────┘
                      │ 调用统一接口
┌─────────────────────▼───────────────────────────────┐
│              Controller Layer (控制器层)             │
│  MobileDeviceController (抽象基类)                   │
│  ├─ AndroidController                               │
│  ├─ iOSController                                   │
│  ├─ LimrunAndroidController / LimrunIosController   │
│  └─ UnifiedController                               │
│  职责：翻译高层操作为平台特定指令序列                  │
└─────────────────────┬───────────────────────────────┘
                      │ 调用底层协议
┌─────────────────────▼───────────────────────────────┐
│               Client Layer (客户端层)                │
│  Android: UIAutomatorClient + AdbClient (adbutils)  │
│  iOS 模拟器: IdbClientWrapper (fb-idb)              │
│  iOS 真机: WdaClientWrapper (WebDriverAgent)        │
│  云设备: LimrunClient / BrowserStackClientWrapper   │
│  职责：封装具体通信协议（ADB/HTTP/WebSocket）        │
└─────────────────────────────────────────────────────┘
```

## Controller 层详解

### MobileDeviceController 抽象基类

所有控制器实现统一接口（`controllers/device_controller.py`），核心方法包括：

| 方法 | 说明 |
|---|---|
| `tap(x, y)` | 点击坐标 |
| `long_press(x, y, duration)` | 长按 |
| `swipe(start_x, start_y, end_x, end_y, duration)` | 滑动 |
| `input_text(text)` | 输入文本 |
| `clear_text()` | 清除文本 |
| `press_back()` | 返回键 |
| `press_key(keycode)` | 按键 |
| `launch_app(package_name)` | 启动App |
| `stop_app(package_name)` | 停止App |
| `screenshot()` | 截图 |
| `get_ui_hierarchy()` | 获取UI层级（XML/JSON） |
| `get_screen_size()` | 获取屏幕分辨率 |
| `get_current_app()` | 获取前台App包名 |

### 各平台控制器

| 控制器 | 文件 | 支持平台 | 底层客户端 |
|---|---|---|---|
| `AndroidController` | `android_controller.py` | Android真机/模拟器 | UIAutomatorClient + adbutils |
| `iOSController` | `ios_controller.py` | iOS真机/模拟器 | IdbClientWrapper / WdaClientWrapper |
| `LimrunAndroidController` | `limrun_controller.py` | Limrun云Android | WebSocket API |
| `LimrunIosController` | `limrun_controller.py` | Limrun云iOS | WebSocket API |
| `UnifiedController` | `unified_controller.py` | 统一门面 | 代理到具体控制器 |

### Controller Factory

控制器通过工厂模式创建，根据设备类型自动选择实现：

```python
# controllers/controller_factory.py 伪代码
def create_controller(platform, device_id, ...):
    if platform == ANDROID:
        if is_limrun_device:
            return LimrunAndroidController(...)
        return AndroidController(...)
    elif platform == IOS:
        if is_limrun_device:
            return LimrunIosController(...)
        return iOSController(...)
```

## Client 层详解

### Android 客户端

| 客户端 | 文件 | 职责 | 通信方式 |
|---|---|---|---|
| `UIAutomatorClient` | `ui_automator_client.py` | 获取UI层级、执行UI操作 | uiautomator2 库（ATX Agent） |
| `AdbClient` (adbutils) | adbutils 第三方库 | ADB连接、安装APK、截图、shell命令 | ADB协议 |
| `AdbTunnel` | `adb_tunnel.py` | ADB over WiFi 隧道管理 | TCP 5555端口转发 |

**Android UI 层级获取流程**：
1. 通过 `uiautomator dump` 命令或 uiautomator2 库获取当前界面的 XML
2. 解析为 `list[dict]` 结构（bounds/text/resource-id/class/content-desc等）
3. 注入到 State.latest_ui_hierarchy，供 Cortex 分析

### iOS 客户端

| 客户端 | 文件 | 适用场景 | 通信方式 |
|---|---|---|---|
| `IdbClientWrapper` | `idb_client.py` | iOS模拟器 | fb-idb companion（本地TCP） |
| `WdaClientWrapper` | `wda_client.py` | iOS真机 | WebDriverAgent（HTTP） |
| `WdaLifecycle` | `wda_lifecycle.py` | WDA启动/停止管理 | xcodebuild / subprocess |
| `IosClientWrapper` | `ios_client.py` | iOS统一门面 | 根据DeviceType分发到IDB/WDA/Limrun/BrowserStack |

**DeviceType 枚举**：
```python
class DeviceType(Enum):
    SIMULATOR = "simulator"      # 本地模拟器（IDB）
    PHYSICAL = "physical"        # 真机（WDA）
    BROWSERSTACK = "browserstack" # BrowserStack云设备
    LIMRUN = "limrun"            # Limrun云设备
```

### 云设备客户端

| 客户端 | 文件 | 说明 |
|---|---|---|
| `LimrunClient` | `limrun_client.py` | Limrun云真机API（基于AsyncLimrun SDK） |
| `LimrunFactory` | `limrun_factory.py` | Limrun客户端工厂（创建/释放设备实例） |
| `BrowserStackClientWrapper` | `browserstack_client.py` | BrowserStack App Automate API |
| `CloudMobileService` | `sdk/services/cloud_mobile.py` | Minitap Cloud Mobile服务 |
| `PlatformService` | `sdk/services/platform.py` | Minitap Platform API服务 |

## 设备自动探测

`platform_specific_commands_controller.py` 中的 `get_first_device()` 实现设备自动探测：

**探测顺序**：
1. 检查是否有 Limrun 配置（环境变量/配置文件）
2. 通过 ADB 查找连接的 Android 设备（`adb devices`）
3. 通过 xcrun 查找启动的 iOS 模拟器（`xcrun simctl list devices booted`）
4. 如果都没找到，抛出 `DeviceNotFoundError`

## 设备上下文 DeviceContext

`MobileUseContext.device` 字段是 `DeviceContext` 类型，包含设备的静态信息：

| 字段 | 类型 | 说明 |
|---|---|---|
| `host_platform` | `str` | 宿主机平台（LINUX/WINDOWS/MACOS） |
| `mobile_platform` | `DevicePlatform` | 移动平台（ANDROID/IOS） |
| `device_id` | `str` | 设备序列号/标识符 |
| `device_width` | `int` | 屏幕宽度（像素） |
| `device_height` | `int` | 屏幕高度（像素） |

## 平台差异与统一处理

| 操作 | Android实现 | iOS实现 | Controller层统一 |
|---|---|---|---|
| 返回键 | `press_key(KEYCODE_BACK)` | 界面左滑/辅助功能手势 | `press_back()` |
| 启动App | `am start -n package/activity` | `idb launch` / WDA session | `launch_app(package)` |
| 安装App | `adb install` | `idb install` / Limrun上传 | `install_app(path)` |
| UI层级 | uiautomator dump XML | XCUITest accessibility tree | `get_ui_hierarchy()` |
| 坐标系统 | 屏幕绝对坐标 | 屏幕绝对坐标（WDA/IDB统一） | 直接传递x,y |
| 文本输入 | `adb shell input text` | IDB/WDA input | `input_text(text)` |

> **设计洞察**：为什么 Controller 和 Client 要分层？
>
> - **Controller 处理语义差异**：iOS 没有物理返回键，Controller 要把 `press_back()` 翻译成左滑手势——这是"操作语义"的适配
> - **Client 处理协议差异**：ADB 是 USB/TCP 协议，IDB 是 gRPC，WDA 是 HTTP——这是"通信协议"的适配
> - 分层后新增平台（如 HarmonyOS）只需：1）实现一个 Client 处理协议；2）实现一个 Controller 处理语义；工具层零修改

## 云设备模式差异

云设备（Limrun/BrowserStack/Minitap Cloud）与本地设备的关键区别：

| 维度 | 本地设备 | 云设备 |
|---|---|---|
| 初始化速度 | 即时连接 | 需要启动/等待虚拟机就绪（30-120秒） |
| App安装 | ADB直接安装 | 上传APK到云存储→虚拟机下载安装 |
| 截图/UI层级 | 本地命令，低延迟 | HTTP/WebSocket获取，有网络延迟 |
| 计费 | 免费（自己的设备） | 按时长/按次计费 |
| 视频录制 | 设备原生录屏 | 服务端录制+多模态分析 |
| 任务执行 | Agent在本地运行 | Agent在本地运行，操作通过API转发到云端 |
| 并发 | 单机1-2台 | Minitap Cloud支持大规模并发 |

> **源码参考**:
> - [controllers/device_controller.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/controllers/device_controller.py) - 控制器抽象基类
> - [controllers/android_controller.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/controllers/android_controller.py) - Android实现
> - [controllers/ios_controller.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/controllers/ios_controller.py) - iOS实现
> - [clients/ui_automator_client.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/clients/ui_automator_client.py) - Android UI客户端
> - [clients/ios_client.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/clients/ios_client.py) - iOS统一客户端
