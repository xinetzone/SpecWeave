---
source: d:\AI\.chaos\libs\mobile-use
---

# 故障排查

## 设备连接问题

### ❌ Android: adb devices 看不到设备

**症状**: `adb devices` 返回空列表或设备显示为 `unauthorized`

**排查步骤**:
1. 检查USB线是否支持数据传输（不是仅充电线）
2. 手机上是否弹出"允许USB调试"对话框，点击"始终允许"
3. 开发者选项中"USB调试"是否开启
4. 重启ADB服务：
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```
5. 换USB口/换线/换电脑（有些前置USB口供电不足）
6. Windows需安装对应手机厂商的USB驱动

### ❌ Android: UIAutomator dump 失败

**症状**: Agent卡住，日志显示 `uiautomator dump` 超时或错误

**常见原因与解决**:
- **当前页面是视频/游戏/安全页面**: 这些页面禁用UI自动化，可以尝试返回后重试
- **设备UI线程卡住**: 重启手机或重启 `uiautomator` 服务
- **页面有动画正在播放**: 等待动画结束再dump，或禁用动画：
  ```bash
  adb shell settings put global window_animation_scale 0
  adb shell settings put global transition_animation_scale 0
  adb shell settings put global animator_duration_scale 0
  ```
- **ADB版本不兼容**: 确保platform-tools版本与设备Android版本匹配

### ❌ iOS: WDA连接失败

**症状**: 无法连接到WDA，curl localhost:8100/status失败

**排查步骤**:
1. 确认WDA是否在设备上运行（看设备上是否有WebDriverAgent图标在前台）
2. 如果用tidevice：
   ```bash
   tidevice list  # 确认设备连接
   tidevice wdaproxy -B com.facebook.WebDriverAgentRunner.xctrunner
   ```
3. 检查端口8100是否被占用
4. iOS 16+需要开启"开发者模式"（设置 → 隐私与安全性 → 开发者模式）
5. 重新签名WDA：证书/描述文件过期会导致WDA闪退

### ❌ iOS: 元素点击无反应

**常见原因**:
- **坐标偏移**: WDA的坐标系统可能与屏幕实际坐标不一致，检查是否有缩放或刘海屏适配问题
- **元素被遮挡**: 检查是否有弹窗/键盘遮挡了目标元素
- **应用未响应**: 重启App或重启WDA会话

## Agent执行问题

### ❌ Agent一直在重复相同的动作（循环）

**症状**: Cortex反复做出相同决策，Executor反复点击同一个位置，max_steps耗尽

**诊断方法**:
1. 开启事件监听，观察Cortex决策内容：
   ```python
   def on_event(e):
       if e["event"] == "cortex_decision":
           print("决策:", e["data"].get("structured_decisions"))
           print("思考:", e["data"].get("thought"))
   ```
2. 检查state中的scratchpad是否记录了之前的尝试（Agent应该能看到自己的历史操作）

**常见原因与解决**:
- **元素识别错误**: 目标元素的resource-id/text与LLM认为的不一致 → 在goal中更精确描述元素特征（如"右上角带放大镜图标的搜索按钮"）
- **点击后页面无变化**: 点击无效（按钮不可点击、被遮挡）→ Agent没发现点击失败 → 检查是否需要滚动、是否有弹窗需要先关闭
- **页面加载等待不足**: 点击后页面还没加载完就开始下一步 → 可在工具层增加post-action等待
- **状态判断错误**: Convergence认为未完成但实际上已经完成 → 在goal中更明确描述完成标准

### ❌ Agent点击了错误的位置

**可能原因**:
1. **截图与UI层级不同步**: 截图是旧的但UI层级是新的（或反之）→ 增加操作后的等待时间
2. **屏幕旋转**: 横竖屏切换导致坐标系变化 → 锁定屏幕方向
3. **分辨率/密度问题**: 某些设备dp到px换算错误 → 检查 `get_screen_size()` 返回值是否正确
4. **键盘弹出**: 键盘弹出后UI树变化，元素位置上移但截图没更新 → 输入后先收起键盘再操作

### ❌ input_text 输入失败或输入乱码

**Android**:
- **ADB Keyboard未启用**: 确保初始化时ADB Keyboard被设置为默认输入法
- **中文输入问题**: 某些设备默认输入法不支持ADB输入中文，使用 `android_controller.py` 中的专用ADB Keyboard
- **焦点不在输入框**: 先tap_element点击输入框，等待键盘弹出后再input_text

**iOS**:
- **WDA输入限制**: WDA的typeText对某些特殊字符支持不好
- **安全输入框**: 密码输入框可能禁用自动化输入

### ❌ 任务经常因超时失败

优化方向:
1. **检查LLM响应速度**: 如果单步LLM调用超过10秒，考虑换更快的模型或检查网络
2. **减少不必要的工具调用**: 检查是否有工具执行太慢（尤其是screenshot和dump）
3. **配置fallback**: 主LLM超时时自动切到备用模型
4. **增大max_steps但也要设置单步超时**:
   ```python
   config = (
       Builders.AgentConfig()
       .with_step_timeout(30)  # 单步超时30秒
       .build()
   )
   ```

## LLM与配置问题

### ❌ LLM调用失败：401 Unauthorized

- 检查API Key是否正确，环境变量是否生效：
  ```python
  import os
  print(os.getenv("OPENAI_API_KEY"))  # 确认能读到key
  ```
- 检查API Key是否有余额/权限
- 如果是Azure/Azure OpenAI，检查AZURE_BASE_URL格式是否正确

### ❌ LLM调用失败：429 Rate Limit

- 触发了Provider的速率限制
- 解决：配置fallback模型，或在请求间增加延迟，或升级API套餐

### ❌ LLM返回格式错误（不是期望的JSON）

- 小模型（尤其是非gpt-4o级别的模型）可能不擅长严格的结构化输出
- 解决：
  1. Cortex和Planner使用能力强的模型（gpt-4o / claude-sonnet / gemini-pro）
  2. 配置中使用带fallback，主模型用强模型
  3. 开启重试机制

### ❌ 模型不支持工具调用（Tool Calling）

mobile-use 强依赖LLM的tool calling能力，如果使用不支持的模型会报错：
- 确保使用的模型明确支持function/tool calling
- 已知支持的模型：
  - ✅ OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo
  - ✅ Anthropic: claude-3-sonnet, claude-3-opus, claude-3.5-sonnet
  - ✅ Google: gemini-2.0-flash, gemini-1.5-pro/flash
  - ✅ MiniMax: abab6.5, MiniMax-M2.7
  - ❌ 不要用：GPT-3.5（工具调用不稳定）、小参数量本地模型（除非确认支持）

## Docker/部署问题

### ❌ Docker容器无法访问USB设备

Linux:
```bash
# 运行时添加privileged并挂载USB
docker run --privileged -v /dev/bus/usb:/dev/bus/usb ...
```

Windows/Mac:
- Docker Desktop默认不支持USB直通
- 推荐方案：在主机上运行ADB，容器内通过host.docker.internal:5037连接ADB：
  ```bash
  # 主机先启动ADB
  adb -a nodaemon server start&
  # 容器内设置ADB_SERVER_SOCKET
  docker run -e ADB_SERVER_SOCKET=tcp:host.docker.internal:5037 ...
  ```

### ❌ Docker内Android模拟器启动失败

- Docker中运行Android模拟器需要KVM加速（仅Linux支持）
- Windows/Mac上Docker内运行模拟器非常慢，建议直接用真机

## 诊断命令清单

遇到问题时按顺序执行以下命令收集信息：

```bash
# ===== Android =====
adb devices                          # 设备是否被识别
adb shell getprop ro.build.version.release  # Android版本
adb shell wm size                    # 屏幕分辨率
adb shell pm list packages | grep <keyword>  # 检查App是否安装
adb shell dumpsys window | grep mCurrentFocus  # 当前前台Activity
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml  # 手动dump UI树

# ===== iOS =====
tidevice list                        # 设备列表
tidevice applist                     # 已安装App
curl http://localhost:8100/status    # WDA状态
curl http://localhost:8100/source    # 获取UI层级

# ===== 通用 =====
# 检查Python环境
python -c "import minitap.mobile_use; print(minitap.mobile_use.__version__)"
# 检查LLM连接
python -c "
from minitap.mobile_use.services.llm import get_llm
from minitap.mobile_use.config import LLM
llm = get_llm(LLM(provider='openai', model='gpt-4o-mini'))
import asyncio
print(asyncio.run(llm.ainvoke('hi')))
"
```

## 获取帮助

如果以上排查都无法解决问题，收集以下信息后提Issue：
1. 设备型号、系统版本（Android/iOS版本号）
2. mobile-use版本号
3. 使用的LLM Provider和模型
4. 完整的错误日志（设置logging.DEBUG级别）
5. 复现步骤和目标任务goal
6. 如果可能，提供出问题时的截图和UI层级XML
