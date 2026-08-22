---
title: "能力范围"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/reference/capabilities"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/01-capabilities.toml"
date: "2026-07-07"
tags: ["minitest", "capabilities", "能力范围", "limitations", "限制"]
summary: "诚实回答\"这对我的应用有效吗？\" — 详细说明Mini能做什么、即将推出什么、目前不能做什么以及不在路线图上的功能。"
---
> 来源：https://www.minitap.ai/docs/minitest/reference/capabilities

# 能力范围

对"这对我的应用有效吗？"的诚实回答。

## Mini能做什么

### 驱动任何iOS或Android应用

在云端模拟器上运行真实构建。点击、滑动、滚动、输入、等待、关闭系统对话框、接受权限、从意外屏幕恢复。如果人类能在手机上导航它，Mini就能。

### 为您编写套件

连接GitHub后，[Mini读取您的仓库](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite)来起草初始套件，在功能发布时添加故事，在功能消失时停用故事，并在屏幕更改时重写标准。配置文件和上传的设备文件保持手动。

### 为您构建应用

连接GitHub，Mini在自己的基础设施上构建应用 — 测试构建不需要单独的CI工作流。或者保留您现有的工作流并自己上传构建产物。两条路径都馈入相同的运行引擎。请参阅[提供应用构建](https://www.minitap.ai/docs/minitest/runs/builds)。

### 从您已经工作的任何地方运行

[CI](https://www.minitap.ai/docs/minitest/runs/triggering-a-run)、[仪表板](https://www.minitap.ai/docs/minitest/runs/triggering-a-run)、[Slack](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack)、[CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)，以及[Cursor或Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)。从Slack触发的运行与从CI触发的运行降落在相同的问题标签页中。

### 生成修复提示，而不仅仅是bug报告

当出现问题时，Mini交付不成立的标准、失败时刻的视频，以及您可以粘贴到Cursor或Claude中的[修复提示](https://www.minitap.ai/docs/minitest/runs/run-report#fix-prompt)。当设备日志有助于解释发生了什么时，它们会随之而来。

### 从Slack或仪表板分类

确认、标记为非bug、标记为已解决 — 无论界面如何，相同的操作、相同的状态。问题标签页是规范视图，但大多数分类发生在问题首次出现的Slack线程中。

### 按问题覆盖严重性

Mini在运行时推断严重性，但您有最终决定权。当默认值不符合您的业务实际时，按问题覆盖它。

### 捕获您没有编写测试的回归

[建议](https://www.minitap.ai/docs/minitest/triage/suggestions)显示看起来不对但与任何验收标准无关的东西 — 视觉回归、文案更改、损坏的导航。它们显示在仪表板的建议标签页中。

### 导航操作系统界面

Mini可以打开设置应用、接受通知提示、切换权限、切换到另一个应用（如用于OAuth的浏览器）并通过深度链接返回、控制网络条件以在慢连接下测试，并将设备日志拉入运行报告。

## 即将推出

### 定时运行

Cron风格的调度。目前的解决方法是按计划推送标签的GitHub Action。

### 硬件功能

云端模拟器处理大多数流程。相机、生物识别和推送通知的支持即将推出。

### 从Slack重试

`@mini retry`命令目前是存根。今天，使用仪表板的**Re-run**按钮或从CI重新触发。

## Mini目前不能做什么

当前产品中的实际限制。有些是暂时的，有些是永久的。

### 硬件传感器和物理输入

- **麦克风。** Mini不能对着麦克风说话或管道输入音频。语音驱动的流程不在范围内。
- **相机。** Mini不能将特定图像注入相机。QR扫描或文档拍摄需要不同的方法。
- **生物识别。** Touch ID / Face ID提示可以被关闭，但Mini不能注册或验证真实生物识别。
- **蓝牙、NFC、运动传感器。** 任何需要触摸输入以外的物理设备的东西。

### 应用外部

- **外部浏览器。** Mini停留在您的应用中。如果登录打开Safari/Chrome并通过深度链接跳回，那有效。停留在浏览器中不行。
- **电子邮件和SMS验证。** Mini可以从配置文件上的固定电子邮件地址读取最后一个代码（用于注册流程）。它不能打开真实收件箱、点击任意链接或读取SMS。

### 操作系统界面

- **VPN配置、蓝牙配对以及类似的超出应用范围的多步系统流程。**

### 测试架构

- **网络垫片。** Mini驱动与您实际后端通信的实际应用。没有拦截的网络调用，没有注入的响应，没有模拟的服务。
- **时间旅行。** Mini不能设置设备时钟。"1月1日会发生什么"需要在1月1日触发。
- **并发用户。** 一次运行，一个用户。多用户场景需要单独的顺序运行。

### 平台

- **桌面浏览器中的Web应用。** 该产品针对原生移动端。Mini可以驱动安装在手机上的PWA，但不能驱动在笔记本电脑上打开的网站。
- **平板特定布局。** Mini在手机大小的模拟器上运行。iPad和大屏幕平板UI不在覆盖范围内。
- **手表和电视应用。** 不在范围内。

## 不在路线图上

为了保持期望清晰：

- 您代码的单元测试和集成测试。使用您现有的工具。
- 负载测试和性能基准。Mini运行少数设备，不是舰队。
- 安全测试和渗透测试。
- 通用移动RPA平台。Mini为QA构建，不是为了自动化真实用户工作流。

如果您的愿望清单上的东西没有列在这里，请询问。路线图发展很快。

---

> **下一章**：[CLI命令参考 →](02-cli-commands.md)
