---
title: "提供应用构建"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/runs/builds"
date: "2026-07-07"
tags: ["minitest", "builds", "构建版本", "github", "cli", "web-preview"]
summary: "介绍提供应用构建的两种方式：GitHub自动构建和CLI手动上传，以及Web预览URL和环境变量配置。"
---

> 来源：https://www.minitap.ai/docs/minitest/runs/builds

# 提供应用构建

每次运行都使用您应用的真实构建，在虚拟设备上运行。有两种方式为Mini提供构建，您可以为每个应用混合使用。

## 方式一：GitHub自动构建

连接您的仓库，Mini为您完成构建。当运行需要新的构建产物时，它会拉取正确的提交，为iOS和Android编译，然后将二进制文件交给测试设备。

**要求：**

- 在组织上安装了 **MiniTest GitHub App**。请参阅[GitHub集成](https://www.minitap.ai/docs/minitest/integrations/github)。
- 应用编译所需的构建环境变量（见下文）。

支持Monorepo — 在 **App Settings（应用设置）→ Builds（构建）** 中将Mini指向包含您移动应用的子文件夹。

这是驱动[PR检查](https://www.minitap.ai/docs/minitest/runs/triggering-a-run)的路径：当PR打开时，Mini构建头部提交，运行套件，并将判定结果发布回PR。

对于Expo应用，Mini支持**repack构建** — 当只有JS bundle更改时，重用原生shell的增量重建。当天的第一次构建是完整构建；其余的都是快速构建。

### 构建环境变量

大多数移动构建至少需要一个环境变量才能干净编译：API基础URL、Sentry DSN、功能标志覆盖。Mini按应用存储它们，并在构建时注入。

在 **App Settings → Builds → Environment Variables** 中设置它们。添加、编辑或删除单个值。更改在下一次构建时生效。

```text
API_URL=https://staging.example.com
SENTRY_DSN=https://abc@sentry.io/123
FEATURE_FLAG_CHECKOUT_V2=true
```

值静态加密存储，仅在构建环境内部解密。它们不会出现在仪表板日志、运行报告或修复提示的副本中。

## 方式二：CLI手动上传

自己构建应用 — 在您的笔记本电脑上、在Bitrise上、在Codemagic上，在任何地方 — 然后使用[CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)推送构建产物：

```shellscript
minitest build upload ./path/to/build.ipa
# 或
minitest build upload ./path/to/app-debug.apk
```

CLI会打印一个构建ID，您可以从运行中定位它。最适合一次性检查和构建流水线在GitHub之外的应用。

构建环境变量在这里不适用 — 您的构建产物已经包含了它们。

## 为运行选择构建

当您从仪表板触发运行时，构建选择器允许您：

- 使用配置分支的**最新**构建（默认）。
- 选择**特定提交**或构建ID。

CI触发的运行始终使用触发提交产生的构建。当Mini正在门控PR时，没有手动选择。

## Web预览URL

当您运行Web构建时，Mini将其部署到您可以打开和共享的生成预览主机。主机如下所示：

```text
<preview_key>--<tenant_slug>.preview.minitap.ai
```

`<tenant_slug>`是您的Workspace slug，您可以在 **Settings → General** 中找到。`<preview_key>`是按构建派生的，因此您运行的每个构建在`preview.minitap.ai`上都有自己的主机。

### 注入的环境变量

构建会自动接收`MINITAP_PREVIEW_URL`，设置为该预览URL。您不需要自己添加此变量。当您需要在构建配置中使用主机时，引用占位符`{{MINITAP_PREVIEW_URL}}`，Mini会在构建时填充它。

```text
MINITAP_PREVIEW_URL=https://<preview_key>--<tenant_slug>.preview.minitap.ai
```

### OAuth和允许的重定向

如果您的Web应用使用OAuth或任何源允许列表，预览构建需要接受其主机。将下面的通配符域添加到您的提供程序，以便每个预览构建无需逐构建更改即可进行身份验证：

```text
*--<tenant_slug>.preview.minitap.ai
```

---

> **下一章**：[触发运行 →](02-triggering-runs.md)
