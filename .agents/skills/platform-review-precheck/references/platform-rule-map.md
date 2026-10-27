# 平台审核规则与接口映射表

> 观测于 2026-10-26。来源：微信官方《小程序用户隐私保护指引内容介绍》与
> 《关于小程序隐私保护指引设置的公告》。官方会随版本增补，**改本表前先核对原文**。

## 1. 审核拦截的判定逻辑

官方原文（关于小程序隐私保护指引设置的公告）：

> 自 2023 年 9 月 15 日起，对于涉及处理用户个人信息的小程序开发者，
> 微信要求，仅当开发者主动向平台同步用户已阅读并同意了小程序的隐私保护指引等信息处理规则后，
> 方可调用微信提供的隐私接口。
>
> 开发者首先需确定小程序是否涉及处理用户个人信息，如涉及，则需配置用户隐私授权弹窗，
> 且**仅有在平台《小程序用户隐私保护指引》中声明了所处理的用户个人信息，
> 才可以调用平台提供的对应接口或组件**。若未声明，对应接口或组件将无法调用成功。

审核时平台做的是**逐项比对**：

```
本次提审版本的隐私接口调用情况  ⊆  隐私保护指引中声明的「处理的信息」类型
```

**推论**：协议清单的唯一事实来源是代码实际调用，不是开发者主观认为。

## 2. 提审时在哪里填

| 入口 | 路径 | 作用范围 |
|---|---|---|
| 入口1 | 账号设置 → 服务内容声明 → 用户隐私保护指引 → 去完善 | 现网版本 |
| **入口2** | **管理 → 版本管理 → 提交代码审核 → 信息填写页面** | **本次提审版本** |

官方原文：

> 开发者每次提交代码审核时，平台默认拉取小程序现网版本隐私协议，
> 作为开发版本的隐私协议进入平台审核。**若提交审核的开发版本，
> 其隐私接口调用情况与隐私协议内容有出入，或隐私协议内容为空，则在提审时会提醒开发者进行更新。**
>
> 注意：**若提审版本时被拦截，请在当前入口，即入口2对隐私协议内容进行更新。**

> ⚠️ 被拦截后**改入口1 无效**——入口1 只作用于现网版本。这是最高频的返工点。

## 3. 接口 → 处理的信息 映射（官方原文表）

| 处理的信息 | 接口或组件 |
|---|---|
| 收集你的昵称、头像 | `<button open-type="chooseAvatar">`、`<input type="nickname">`、`wx.getUserInfo`（已回收）、`wx.getUserProfile`（已回收）、`<button open-type="userInfo">`（已回收） |
| 收集你的位置信息 | `wx.authorize({scope:'scope.userLocation'})`、`scope.userLocationBackground`、`scope.userFuzzyLocation`、`wx.getLocation`、`wx.startLocationUpdate`、`wx.startLocationUpdateBackground`、`wx.getFuzzyLocation`、`MapContext.moveToLocation` |
| 收集你选择的位置信息 | `wx.choosePoi`、`wx.chooseLocation` |
| 收集你的地址 | `wx.chooseAddress` |
| 收集你的发票信息 | `wx.chooseInvoiceTitle`、`wx.chooseInvoice` |
| 收集你的微信运动步数 | `wx.authorize({scope:'scope.werun'})`、`wx.getWeRunData` |
| 收集你的手机号 | `<button open-type="getPhoneNumber">`、`<button open-type="getRealtimePhoneNumber">` |
| 收集你的车牌号 | `wx.chooseLicensePlate` |
| **收集你选中的照片或视频信息** | **`wx.chooseImage`、`wx.chooseMedia`、`wx.chooseVideo`** |
| 收集你选中的文件 | `wx.chooseMessageFile` |
| 访问你的麦克风 | `wx.authorize({scope:'scope.record'})`、`wx.startRecord`、`RecorderManager.start`、`<live-pusher>`、`wx.joinVoIPChat` |
| 访问你的摄像头 | `wx.authorize({scope:'scope.camera'})`、`wx.createVKSession`、`<camera>`、`<live-pusher>`、`<voip-room>` |
| 访问你的蓝牙 | `wx.authorize({scope:'scope.bluetooth'})`、`wx.openBluetoothAdapter`、`wx.createBLEPeripheralServer` |
| 使用你的相册（仅写入）权限 | `wx.authorize({scope:'scope.writePhotosAlbum'})`、`wx.saveImageToPhotosAlbum`、`wx.saveVideoToPhotosAlbum` |
| 使用你的通讯录（仅写入）权限 | `wx.authorize({scope:'scope.addPhoneContact'})`、`wx.addPhoneContact` |
| 使用你的日历（仅写入）权限 | `wx.authorize({scope:'scope.addPhoneCalendar'})`、`wx.addPhoneCalendar`、`wx.addPhoneRepeatCalendar` |
| 调用你的加速传感器 | `wx.startAccelerometer` |
| 调用你的磁场传感器 | `wx.startCompass` |
| 调用你的方向传感器 | `wx.startDeviceMotionListening` |
| 调用你的陀螺仪传感器 | `wx.startGyroscope` |
| 读取你的剪切板 | `wx.setClipboardData`、`wx.getClipboardData` |

> **易错点**：「使用你的相册（仅写入）权限」与「收集你选中的照片或视频信息」是**两个不同类型**。
> 只声明前者（因为用了 `saveImageToPhotosAlbum`）而不声明后者（用了 `chooseMedia`）→ 仍被拦。

## 4. 授权相关的三个接口

| 接口 | 作用 | 缺失后果 |
|---|---|---|
| `wx.getPrivacySetting` | 查询用户是否已同意隐私协议 | 无法判断是否需要先授权 |
| `wx.onNeedPrivacyAuthorization` | 响应平台抛出的授权请求事件 | 平台授权面板无人响应 |
| `wx.requirePrivacyAuthorize` | 主动触发授权流程 | 用户未同意时接口**静默失败** |

> 2023-09-15 之后隐私功能**默认开启**，`app.json` 里的 `__usePrivacyCheck__` 已不再是开关；
> 但显式写上不影响功能，可作为意图声明。

## 5. 声明正文的必填板块

官方模板要求的板块（缺哪个由审核决定，但「开发者处理的信息」是硬性必填）：

1. 引导语
2. **开发者处理的信息**（必填，含用途描述）
3. 第三方插件信息（引用了插件才有）
4. 第三方服务商信息（代开发才有）
5. 用户权益（联系方式为必填）
6. 开发者对信息的存储（存储期限）
7. 信息的使用规则
8. 信息对外提供
9. 联系方式
10. 补充文档（可选，txt，≤100KB）
11. 日期（更新日期 + 生效日期）

> 「用途描述」会被平台审核——写「用于上传活动封面」这类**具体动作**，
> 不要写「用于改善体验」这类空话。
