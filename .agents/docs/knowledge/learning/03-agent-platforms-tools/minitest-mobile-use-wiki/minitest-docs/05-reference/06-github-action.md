---
title: "GitHub Action参考"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/reference/minitest-trigger-action"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/06-github-action.toml"
date: "2026-07-07"
tags: ["minitest", "github-action", "ci", "github-actions", "参考"]
summary: "minitest-trigger GitHub Action的完整参考文档，包括输入输出、配置示例、构建路径要求、Web运行配置和取消先前运行机制。"
---
> 来源：https://www.minitap.ai/docs/minitest/reference/minitest-trigger-action

# GitHub Action参考

**[`minitap-ai/minitest-trigger`](https://github.com/minitap-ai/minitest-trigger)** GitHub Action是miniTest的CI界面。它通过GitHub OIDC进行身份验证，上传您的构建（或要求Mini构建一个）并启动运行 — 即发即弃。结果通过提交上的GitHub Check Run返回。

有关工作流设置演练，请参阅[触发运行 → 从CI](https://www.minitap.ai/docs/minitest/runs/triggering-a-run)。

## 最小用法

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
```

这就足够了。Mini为两个平台在头部提交上构建您的应用，运行每个故事，并将判定结果发布到PR。

## 先决条件

工作流必须具有用于OIDC身份验证的`id-token: write`权限：

```yaml
permissions:
  id-token: write
```

并且`MiniTest GitHub App`必须已安装在组织上 — 请参阅[GitHub集成](https://www.minitap.ai/docs/minitest/integrations/github)。

## 输入

| 输入 | 必需 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `app-slug` | 是 | — | miniTest应用slug。在 **App Settings → General** 中找到它。 |
| `run-ios` | 否 | `true` | 包含iOS通道。当未给出`ios-build-path`时，Mini构建应用。 |
| `run-android` | 否 | `true` | 包含Android通道。当未给出路径时，Mini构建应用。 |
| `ios-build-path` | 否 | — | 预构建的iOS bundle，可以是模拟器`.app`目录或`.ipa`文件。 |
| `android-build-path` | 否 | — | 预构建的Android `.apk`。必须针对x86-64。 |
| `user-story-types` | 否 | — | 要运行的[故事类型](https://www.minitap.ai/docs/minitest/suite/anatomy)的逗号分隔列表（例如`login,checkout`）。 |
| `run-web` | 否 | `false` | 包含Web通道。对于链接到GitHub仓库的Web应用，Mini构建并提供此工作流运行的提交并针对它进行测试，无需`web-url`。对于仅配置了URL的Web应用，它测试该URL。请参阅[Web运行](#web运行)。 |
| `web-targets` | 否 | — | 显式Web目标，作为`<browser>:<viewport>`规范的逗号分隔列表（例如`chrome:desktop,safari:mobile`）。自行包含Web通道。设置此参数或`run-web`，不要两者都设置。 |
| `web-url` | 否 | — | 每次运行的Web URL，例如PR预览部署。设置后，Web通道测试此URL而不是构建提交。在设置`run-web`或`web-targets`时适用。 |
| `tenant-id` | 否 | — | 仅当仓库链接到多个工作区时必需。 |
| `cancel-previous-runs` | 否 | `true` | 当同一源分支匹配配置的发布模式时，取消正在进行的CI运行。请参阅[取消先前运行](#取消先前运行)。 |
| `api-url` | 否 | `https://testing-service.app.minitap.ai` | 覆盖API基础URL。您通常不需要这个。 |

## 输出

| 输出 | 说明 |
| --- | --- |
| `batch-id` | 触发运行的ID。 |
| `status` | 触发运行的初始状态。 |

## 构建路径和要求

如果您不传递构建路径，Mini会在触发提交时为该平台构建您的应用（使用[提供应用构建](https://www.minitap.ai/docs/minitest/runs/builds)中配置的任何内容）。如果您传递构建路径，Action会上传该产物而不是要求Mini构建。

### iOS

| 格式 | 说明 |
| --- | --- |
| `.app` | 模拟器bundle目录。上传前自动打包成`.ipa`。 |
| `.ipa` | 按原样上传。必须是模拟器构建。 |

模拟器的典型`xcodebuild`命令行：

```shellscript
xcodebuild build \
  -scheme MyApp \
  -sdk iphonesimulator \
  -configuration Debug \
  -derivedDataPath ./build
# 输出: ./build/Build/Products/Debug-iphonesimulator/MyApp.app
```

### Android

仅限`.apk`，并且它必须包含`x86_64`的原生库。Action会检查APK，如果仅存在`arm64-v8a`或`armeabi-v7a`则会失败并给出明确错误。

配置`app/build.gradle`：

```groovy
android {
  defaultConfig {
    ndk { abiFilters 'x86_64' }
  }
}
```

然后构建：

```shellscript
./gradlew assembleDebug
# 输出: app/build/outputs/apk/debug/app-debug.apk
```

## Web运行

`run-ios`、`run-android`和Web输入各自选择一个通道。通道是叠加的：您可以只运行Web通道、只运行一个原生通道，或任何组合。Web目标指向URL而不是上传的产物，有一个例外：链接到GitHub仓库的Web应用构建并提供此工作流运行的提交。请参阅[构建提交](#构建提交)。

有两种方式包含Web通道：

- **`run-web: true`**运行应用配置的默认Web目标，在仪表板中按应用设置。这是默认值标记：它扩展为您在那里设置的任何浏览器和视口。链接仓库的应用针对构建的提交运行它们；仅URL应用针对其配置的Web URL运行它们。
- **`web-targets`**运行显式列表。每个规范是`<browser>:<viewport>`，逗号分隔。设置`web-targets`会自行包含Web通道。

设置`run-web`或`web-targets`，不要两者都设置。一个选择应用默认值，另一个选择显式列表。

Web应用可以在移动设备的浏览器上测试，因此`<browser>:<viewport>`映射到具体目标：

| 规范 | 运行位置 |
| --- | --- |
| `safari:mobile` | iOS设备上的Safari（移动Web） |
| `chrome:mobile` | Android设备上的Chrome（移动Web） |
| `chrome:desktop`、`firefox:desktop` | 桌面Web |

Action解析`<browser>:<viewport>`，后端验证组合。

浏览器支持为桌面端的`chrome`和`firefox`，加上iOS移动Web的`safari`。桌面Safari（`safari:desktop`）不是有效的Web目标。

每个通道不会静默忽略任何内容：`web-url`和`web-targets`仅在Web通道开启时适用，`ios-build-path`仅在`run-ios`开启时适用，`android-build-path`仅在`run-android`开启时适用。在该通道关闭时传递通道的输入会被拒绝，因此拼写错误不会悄悄丢弃您的构建或URL。

### 构建提交

如果您的Web应用链接到GitHub仓库（在**App Settings**中设置），`run-web: true`会在此工作流运行的提交上构建您的前端，在测试环境中提供它，并针对该构建运行您的Web故事。不需要`web-url`。即使应用也配置了Web URL，这也成立：链接仓库通道测试提交，而不是部署。仅当您想测试单独部署的URL（例如PR预览）而不是提交时，才提供`web-url`。

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-web: true # 为链接仓库的Web应用构建并提供此提交
```

### 使用web-url的每次运行URL

常见的CI情况是测试PR预览部署。将`web-url`设置为部署的URL，它会覆盖该次运行的应用配置Web URL：

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-web: true
    web-url: https://pr-142.preview.example.com
```

这会针对预览URL运行Web通道，以及启用的任何原生通道。

CI是允许每次运行覆盖Web目标和Web URL的两个界面之一；另一个是仪表板中的**Run tests**面板。CLI、MCP工具和Slack可以选择Web通道，但不能覆盖其目标或URL。

## 示例

### 默认 — Mini为两个平台构建

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
```

### 仅iOS

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-android: false
```

### 仅Android，使用您自己的构建

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-ios: false
    android-build-path: ./app/build/outputs/apk/debug/app-debug.apk
```

### 自带iOS构建，让Mini构建Android

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    ios-build-path: ./build/Build/Products/Debug-iphonesimulator/MyApp.app
```

### 限制为特定故事类型

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    user-story-types: login,checkout,onboarding
```

### Web应用，配置的默认值

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-web: true
```

### Web应用，显式目标

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    web-targets: chrome:desktop,safari:mobile
    web-url: https://pr-142.preview.example.com
```

### 移动浏览器上的Web应用

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    web-targets: safari:mobile,chrome:mobile
```

### 多工作区设置

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    tenant-id: tenant_abc123
```

## 取消先前运行

当您反复推送到同一发布分支时 — 例如，使用修复重新打开发布PR — 仍在等待或运行的旧运行会堆积。使用`cancel-previous-runs: true`（默认值），服务器在启动新运行之前取消匹配同一源分支的正在进行的运行。

取消的范围：

- **仅限同一源分支** — 在PR头分支（`pull_request`事件）或`push` / `workflow_dispatch` / `schedule` / `merge_group`的分支引用上匹配。
- **仅限发布分支** — 分支必须匹配应用配置的发布分支模式之一（gitignore风格；在仪表板中按应用配置）。
- **仅限CI触发** — 仅取消由此Action启动的运行。仪表板、Slack或CLI运行不受影响。

以下情况为空操作：

- 标签推送（`refs/tags/*`）。
- 不匹配配置发布模式的分支。
- 无法确定分支的事件。

使用`cancel-previous-runs: false`选择退出。

## 工作原理

1. **OIDC认证。** Action请求范围限定为Minitap API的GitHub OIDC令牌。您这边无需管理任何内容。
2. **验证构建。** 如果您提供了任何构建路径，Action会检查产物（仅模拟器iOS，x86-64 Android）。
3. **上传构建。** 您提供的任何内容都会上传到miniTest。`.app` bundle首先打包成`.ipa`。
4. **触发运行。** 对于任何没有提供构建的启用平台，Mini为触发提交构建应用。这包括链接仓库Web应用的Web通道：Mini构建并提供提交，除非您将`web-url`指向已部署的URL。
5. **即发即弃。** Action立即退出。结果通过提交上的GitHub Check Run返回。

---

> **返回参考文档总览**：[参考文档总览 →](00-overview.md)
