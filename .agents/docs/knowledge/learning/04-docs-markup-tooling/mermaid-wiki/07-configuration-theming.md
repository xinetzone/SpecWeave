---
id: "mermaid-wiki-07-configuration-theming"
title: "Mermaid 配置与主题（Configuration & Theming）"
source: "https://mermaid.js.org/"
category: "learning"
tags: ["mermaid","configuration","theming","theme","themeVariables","securityLevel","dagre","elk","markup"]
date: "2026-08-06"
status: "stable"
author: "SpecWeave"
summary: "Mermaid 配置与主题完整指南：配置来源三层（默认/站点级 initialize/frontmatter）、mermaid.initialize 与 startOnLoad 与 configApi.reset、5 个内置主题（default/neutral/dark/forest/base）、securityLevel 四级安全、dagre/elk 渲染器，以及 themeVariables 与各图表专项主题变量，每个关键配置均附带 HTML 与 YAML frontmatter 代码示例。"
---
# Mermaid 配置与主题（Configuration & Theming）

Mermaid 的配置与主题系统决定了图表的**渲染行为**（加载方式、渲染器、安全级别）与**视觉外观**（配色、字体、边框）。本教程所有事实均以 Mermaid 官方文档（https://mermaid.js.org/）为准。

主题配置分两个层面：**站点级**（通过 `mermaid.initialize` 一次性全局配置）与**单图级**（通过图表顶部的 YAML frontmatter 配置）。动态、集成式的主题配置从 Mermaid v8.7.0 引入。

## 配置来源三层

Mermaid 的配置来源有三个层次，按优先级从低到高排列：

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1（最低） | 默认配置 | Mermaid 内置的出厂默认值 |
| 2 | 站点级 `initialize`（siteConfig） | 站内集成者在站点级的覆盖，`mermaid.initialize(config)` |
| 3（最高） | 图前 frontmatter | 单个图表顶部的 YAML 块（v10.5.0+），仅覆盖选定参数 |

**render config** 即最终用于渲染的配置，由三层按优先级合并得出。图前的 frontmatter 可以覆盖「除 secure 配置外几乎所有配置」。

> **directives 已弃用**：早期通过图内指令（directives）配置的方式已被 frontmatter 取代，新写法请使用图表顶部的 YAML 块。

## mermaid.initialize 与 startOnLoad

`mermaid.initialize(config)` 用于在**站点级**覆盖默认配置。集成者只应调用**一次**，通常放在页面加载时。

```html
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({
        startOnLoad: true,
        theme: 'base',
        securityLevel: 'loose'
    });
</script>
```

关键参数：

- `startOnLoad: true`：页面加载完成后自动查找 `class="mermaid"` 的 `<div>` 或 `<pre>` 标签并渲染为 SVG。
- `theme`：指定内置主题名（见下文 5 个内置主题）。
- `securityLevel`：指定安全级别（见下文 securityLevel）。

### configApi.reset

`mermaid.configApi.reset` 将某个图表的配置**重置为站点级配置**。Mermaid 在**每次渲染前都会调用一次** reset，确保单个图表通过 frontmatter 覆盖的配置不会泄漏污染后续图表的渲染。

## 5 个内置主题

Mermaid 内置 5 个主题，其中 **`base` 是唯一可修改的主题**，作为自定义配色方案的基础：

| 主题 | 特点 |
|------|------|
| `default` | **所有图的默认主题** |
| `neutral` | 适合黑白/打印文档，中性配色 |
| `dark` | 适合深色元素/深色模式；需结合 `darkMode: true` 使用（dark 主题改的是 schema 本身，`darkMode` 设背景） |
| `forest` | 绿色系 |
| `base` | **唯一可修改的主题**，作为自定义的基础 |

> **dark 主题与 darkMode 的区别**：选用 `dark` 主题改变的是图表 schema 本身（整体深色配色）；而 `darkMode: true` 这个主题变量设置的是**背景色**。因此深色模式下通常需要二者配合。

## 安全级别 securityLevel

`securityLevel` 控制图表可访问的 DOM/交互能力，取值如下：

| 取值 | 说明 |
|------|------|
| `strict` | **默认值**；严格模式，**禁用 click 交互**（如 `click nodeId callback`） |
| `loose` | 宽松模式，允许 click 回调等交互 |
| `antiscript` | 反脚本模式 |
| `sandbox` | 沙箱模式，在沙箱 iframe 中渲染图表，安全性最高，但会牺牲部分交互功能 |

> **安全建议**：对外部用户开放的站点，Mermaid 会尝试净化输入代码，并支持在沙箱 iframe 中渲染的更高安全级别；`strict` 下 chart 内的 `click` 交互将被禁用。

通过 frontmatter 指定安全级别：

```yaml
---
config:
    securityLevel: strict
---
```

## 渲染器：dagre 与 elk

流程图（flowchart）的布局渲染器有两个：

| 渲染器 | 说明 |
|--------|------|
| `dagre` | **默认渲染器**，基于 dagre-d3 |
| `elk` | **实验性**，v9.4+ 可用；更适合大型/复杂图 |

通过配置项 `flowchart.defaultRenderer: "elk"` 切换：

```yaml
---
config:
    flowchart:
        defaultRenderer: "elk"
---
```

## 主题变量 themeVariables

通过 `themeVariables` 可以自定义主题，但**仅 `base` 主题可修改**。部分变量默认值由其他变量推导（例如 `primaryBorderColor` 由 `primaryColor` 推导，会做反色/色调变化/加减 10% 等调整）。

### 常用全局主题变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `darkMode` | `false` | 深色模式背景 |
| `background` | `#f4f4f4` | 图表背景色 |
| `fontFamily` | `trebuchet ms, verdana, arial` | 字体族 |
| `fontSize` | `16px` | 字号 |
| `primaryColor` | `#fff4dd` | 主色 |
| `primaryTextColor` | 由 darkMode 推导 | 主文本色 |
| `secondaryColor` | — | 次级色 |
| `primaryBorderColor` | 由 primaryColor 推导 | 主边框色 |
| `noteBkgColor` | `#fff5ad` | 注释背景色 |
| `noteTextColor` | `#333` | 注释文本色 |
| `noteBorderColor` | — | 注释边框色 |
| `lineColor` / `textColor` | — | 连线色 / 文本色 |
| `mainBkg` | — | 主背景色 |
| `errorBkgColor` / `errorTextColor` | — | 错误背景 / 错误文本色 |

### 各图表专项变量

不同的图表类型还有各自专有的主题变量：

- **Flowchart**：`nodeBorder`、`clusterBkg`、`clusterBorder`、`defaultLinkColor`、`titleColor`、`edgeLabelBackground`、`nodeTextColor`
- **Sequence**：`actorBkg`、`actorBorder`、`actorTextColor`、`actorLineColor`、`signalColor`、`signalTextColor`、`labelBoxBkgColor`、`labelBoxBorderColor`、`labelTextColor`、`loopTextColor`、`activationBorderColor`、`activationBkgColor`、`sequenceNumberColor`
- **Pie**：`pie1`–`pie12`、`pieTitleTextSize`、`pieSectionTextSize`、`pieLegendTextSize`、`pieStrokeColor`、`pieStrokeWidth`、`pieOpacity`
- **State**：`labelColor`、`altBackground`
- **Class**：`classText`
- **Journey**：`fillType0`–`fillType7`

### 主题引擎只识别十六进制颜色

> **重要**：主题引擎**只识别十六进制颜色**（如 `#ff0000`），**不识别颜色名**（如 `red`）。自定义 `themeVariables` 时颜色一律写十六进制。

## 代码示例

### 站点级 initialize（HTML）——切换 base 主题并自定义配色

```html
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({
        startOnLoad: true,
        theme: 'base',
        themeVariables: {
            darkMode: true,
            background: '#1e1e1e',
            fontFamily: 'Arial, sans-serif',
            fontSize: '14px',
            primaryColor: '#ff0000',
            noteBkgColor: '#333333'
        }
    });
</script>
```

### 单图 frontmatter（YAML）——forest 主题 + 自定义主色

```yaml
---
config:
    theme: forest
    themeVariables:
        primaryColor: "#ff0000"
        fontFamily: "Arial"
---
flowchart TB
    A["开始"] --> B["处理"]
    B --> C["结束"]
```

### 单图 frontmatter——指定 dark 主题与深色模式

```yaml
---
config:
    theme: dark
    themeVariables:
        darkMode: true
---
flowchart TB
    A["登录"] --> B["校验"]
    B --> C["进入主页"]
```

### 专项变量示例——自定义时序图 actor 配色

```yaml
---
config:
    theme: base
    themeVariables:
        actorBkg: "#e0f0ff"
        actorBorder: "#336699"
        signalColor: "#336699"
        noteBkgColor: "#fff5ad"
---
sequenceDiagram
    participant A as "客户端"
    participant B as "服务端"
    A->>B: "发送请求"
    B-->>A: "返回结果"
```

---

**下一章**：[第 8 章 — 集成与生态 →](08-integrations-ecosystem.md)