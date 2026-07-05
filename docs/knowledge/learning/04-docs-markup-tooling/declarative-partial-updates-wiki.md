---
title: "Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析"
source: "微信公众号文章《HTML 最值得关注的一次升级：声明式局部更新》（作者：认真努力的小四子）"
date: "2026-07-04"
tags: ["html", "declarative-partial-updates", "streaming", "partial-rendering", "web-standards", "chrome", "declarative-shadow-dom", "ssr"]
---

# Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析

> **原文参考**: https://mp.weixin.qq.com/s/MpJSwf9wbB14uVlNo6YyWA
> **Chrome 官方文档**: https://developer.chrome.com/blog/declarative-partial-updates?hl=zh-cn

---

## 📋 目录导航

- [一、技术概述：HTML 十年来最值得关注的升级](#一技术概述html-十年来最值得关注的升级)
- [二、痛点分析：传统 JavaScript 局部更新的链路过长](#二痛点分析传统-javascript-局部更新的链路过长)
- [三、核心机制详解：声明式局部更新的工作原理](#三核心机制详解声明式局部更新的工作原理)
- [四、乱序流式更新：慢模块不再拖死整页](#四乱序流式更新慢模块不再拖死整页)
- [五、与现有技术对比：不是 SSE 也不是 WebSocket](#五与现有技术对比不是-sse-也不是-websocket)
- [六、框架影响分析：不会成为框架杀手](#六框架影响分析不会成为框架杀手)
- [七、Declarative Shadow DOM 关联：HTML 重新变强的趋势](#七declarative-shadow-dom-关联html-重新变强的趋势)
- [八、内容评估：准确性、权威性与实用性](#八内容评估准确性权威性与实用性)
- [九、个人理解与见解](#九个人理解与见解)
- [十、常见问题解答（FAQ）](#十常见问题解答faq)
- [十一、相关资源链接](#十一相关资源链接)

---

## 一、技术概述：HTML 十年来最值得关注的升级

这是过去十年里，HTML 最值得关注的一次升级。不是新增一个标签，也不是补一个属性，而是 HTML 可能要开始接管一件原本属于 JavaScript 的事：**页面局部更新**。

### 1.1 核心定位

Declarative Partial Updates（声明式局部更新）是 Chrome 正在推进的一项新能力。如果这个能力真正落地，很多前端页面的写法都会变。以前我们默认：

- 页面动起来 = JavaScript 接管
- 数据更新 = fetch 请求
- 局部刷新 = DOM patch

但这次不一样。浏览器正在尝试让 HTML 自己完成局部更新：**服务端直接流式输出 HTML 片段，浏览器收到后自动把内容补到页面指定位置**。不用 `fetch()`，不用 `querySelector()`，不用 `innerHTML`，甚至不需要额外的客户端 runtime。

### 1.2 核心价值

它听起来像是一个小语法提案，但背后其实是一个很大的方向变化：

> **HTML 不再只是首屏外壳，它开始重新参与 UI 更新。**

这意味着 HTML 这个最古老的 Web 标记语言，正在重新参与到动态 UI 渲染的链路中。它不再只是首屏渲染完成后就交给 JavaScript 接管，而是拥有了持续接收、应用局部更新的原生能力。这是 Web 平台演进方向上的一个重要信号。

---

## 二、痛点分析：传统 JavaScript 局部更新的链路过长

要理解 Declarative Partial Updates 的价值，首先要看清传统局部更新方式存在的本质问题。

### 2.1 传统更新流程

举个最常见的场景：一个订单详情页，要更新支付状态。以前基本是这套流程：

```
服务端查数据库
↓
返回 JSON
↓
前端 fetch()
↓
JS 解析数据
↓
查找 DOM
↓
手动更新页面
```

### 2.2 传统代码示例

代码大概长这样：

```javascript
const res = await fetch('/api/order/status');
const data = await res.json();

document.querySelector('#status').innerHTML = `
  <strong>${data.status}</strong>
  <span>${data.time}</span>
`;
```

这段代码当然能跑。但问题是：只是为了更新一小块 HTML，却绕了一整圈。

### 2.3 三个核心问题

**问题 1：链路过长**

数据在服务端。HTML 也可以由服务端生成。最后却要先变成 JSON，再交给 JavaScript 拼回 HTML。原本可以一步到位的事情，被强行拆成了多个环节：数据序列化、网络传输、客户端解析、DOM 查找、HTML 字符串拼接、DOM 替换。每一个环节都是潜在的出错点，也都是性能损耗点。

**问题 2：Web 页面变重**

这就是过去很多 Web 页面变重的原因。**不是业务本身复杂，而是页面更新链路被拉长了**。为了支持这套更新模式，前端必须引入：

- 网络请求库（fetch / axios）
- 状态管理库（管理 loading、error、data 三态）
- DOM 操作或虚拟 DOM 库
- 序列化/反序列化逻辑
- 客户端路由与组件管理

这些"胶水代码"在大多数业务页面中并非真正必要，只是为了弥补浏览器原生能力不足而被迫引入的。

**问题 3：客户端 runtime 依赖**

传统模式下，页面一旦加载完成，所有后续更新都依赖客户端 JavaScript runtime。这意味着：

- 客户端必须下载并执行完整的 JS 包
- 弱网或低端设备上首屏交互受影响
- 必须维护一套与 HTML 分离的状态同步逻辑
- 服务端渲染（SSR）虽然能解决首屏，但后续更新仍要"水合"为客户端接管

这正是 Declarative Partial Updates 想要打破的循环：**让 HTML 在服务端生成片段的同时，也能直接由浏览器原生化地应用到对应位置**。

---

## 三、核心机制详解：声明式局部更新的工作原理

Declarative Partial Updates 的思路很直接：**页面先返回骨架，慢数据后面再补**。整个机制由三个核心部分组成。

### 3.1 机制 1：声明式更新区域（`<?start?>` / `<?end?>`）

页面在一开始先输出一个占位区域：

```html
<section>
  <h2>订单状态</h2>

  <?start name="order-status"?>
    <p>查询中...</p>
  <?end?>
</section>
```

这里的 `<?start?>` 和 `<?end?>` 可以理解成一个**可更新区域**。它通过 `name` 属性给这个区域起了一个标识符，浏览器先把 "查询中..." 渲染出来，用户不用等所有数据准备完。

### 3.2 机制 2：template patch（`<template for="...">`）

等服务端查完支付状态之后，不需要前端再发请求，而是在同一个 HTML 响应流里继续输出：

```html
<template for="order-status"?>
  <p><strong>已支付</strong></p>
  <p>支付时间：10:32</p>
</template>
```

浏览器解析到 `<template for="order-status"?>` 就会自动找到前面叫 `order-status` 的区域，然后把占位内容替换掉。整个过程完全由浏览器原生完成，不需要任何 JavaScript 介入。

### 3.3 机制 3：流式输出

Declarative Partial Updates 的精髓在于流式：

```
一个 request
一个 response
HTML 响应体持续流式输出
浏览器边接收边解析边 patch
```

服务端先把页面骨架 flush 给浏览器，让用户立刻看到页面结构。后面哪个模块数据准备好了，就继续往这个响应里写对应的 HTML 片段。浏览器收到后，自动把内容补到指定位置。整个过程在同一个 HTTP 响应里完成，不需要建立额外的通信通道。

### 3.4 完整代码示例：订单状态更新过程

完整的更新过程可以分解为两个阶段：

**阶段 1：服务端返回页面骨架（带占位）**

```html
<!DOCTYPE html>
<html>
<body>
  <section>
    <h2>订单状态</h2>
    <?start name="order-status"?>
      <p>查询中...</p>
    <?end?>
  </section>
</body>
</html>
```

此时浏览器已经渲染出"订单状态 - 查询中..."，用户可见。

**阶段 2：服务端继续在同一个响应中输出 patch**

```html
<template for="order-status"?>
  <p><strong>已支付</strong></p>
  <p>支付时间：10:32</p>
</template>
```

浏览器收到这段后，自动把 `order-status` 区域的内容替换为"已支付 - 支付时间：10:32"。

### 3.5 新旧路径对比

核心变化就一句话：

| 模式 | 更新链路 |
|------|---------|
| **以前** | 服务端 → JSON → JavaScript → DOM |
| **现在** | 服务端 → HTML patch → 浏览器自动更新 |

这条路径短了很多。这也是它真正炸的地方：**它把原本三步的链路压缩成了一步**，服务端直接生成最终要呈现的 HTML，浏览器直接应用，中间没有数据格式转换、没有客户端解析、没有 DOM 手动操作。

---

## 四、乱序流式更新：慢模块不再拖死整页

真实业务里，一个页面慢，通常不是所有内容都慢，而是几个模块拖后腿。这是 Declarative Partial Updates 最实用的能力。

### 4.1 真实业务场景

例如一个后台详情页：

```
基础信息：很快
支付状态：一般
风控结果：较慢
操作日志：最慢
```

不同模块的数据查询耗时差异巨大。如果等所有数据都查完再返回，首屏会非常慢；如果拆成多个接口，前端逻辑会非常复杂。

### 4.2 传统两个选择的痛点

以前你只有两个选择：

**选择 1：服务端等全部数据查完再返回**

- 后果：首屏变慢
- 用户体验：长时间白屏或转圈

**选择 2：前端拆成多个接口**

- 后果：自己维护一堆 loading、错误状态、重试逻辑、DOM 更新
- 用户体验：好一些，但前端代码复杂度急剧上升

两种方案都不理想，要么牺牲首屏速度，要么牺牲代码可维护性。

### 4.3 第三种方式：谁先准备好，谁先补上

Declarative Partial Updates 给了第三种方式：**页面先出来，模块谁先准备好，谁先补上**。

页面骨架可以先这样返回：

```html
<section>
  <h2>支付状态</h2>
  <?start name="payment"?>
    <p>支付状态加载中...</p>
  <?end?>
</section>

<section>
  <h2>风控结果</h2>
  <?start name="risk"?>
    <p>风控结果加载中...</p>
  <?end?>
</section>
```

### 4.4 多模块代码示例

如果风控先完成，服务端先发：

```html
<template for="risk"?>
  <p><strong>低风险</strong></p>
  <p>已通过自动审核</p>
</template>
```

如果支付后完成，再继续发：

```html
<template for="payment"?>
  <p><strong>已支付</strong></p>
  <p>交易号：TXN-2026-001</p>
</template>
```

浏览器会把它们分别 patch 到正确位置。注意这里的关键点：

1. **patch 顺序与页面位置无关**：风控模块在页面下方，但它的 patch 可以先到达；支付模块在页面上方，但它的 patch 可以后到达。浏览器根据 `name` 属性匹配，与到达顺序无关。
2. **每个模块独立完成**：哪个模块数据准备好，就立即发送对应的 patch，不需要等其他模块。
3. **用户感知提升**：用户先看到页面结构（所有占位都显示 "加载中"），然后内容一块一块长出来，体验流畅自然。

### 4.5 业务价值

这意味着：

> **慢模块不再拖死整页。用户先看到页面结构，然后内容一块一块长出来。**

对于以下场景，这个能力非常实用：

| 适用场景 | 典型页面 |
|---------|---------|
| 后台详情页 | 订单管理、用户管理、商品管理 |
| 订单页 | 电商订单详情、支付状态追踪 |
| 商品页 | 商品详情、库存状态、评论 |
| 评论区 | 文章评论、社区帖子 |
| 搜索结果页 | 搜索结果分批加载 |
| 文档导航 | 文档目录、内容索引 |
| CMS 模块 | 内容管理系统的多模块页面 |

这些场景很多时候并不需要完整客户端应用，它们只是需要服务端把 HTML 片段补上。Declarative Partial Updates 完美契合这种"以服务端为主、客户端轻量"的页面模式。

---

## 五、与现有技术对比：不是 SSE 也不是 WebSocket

很多人看到"服务端继续发内容"，第一反应会想到：SSE？WebSocket？HTTP/2 Server Push？轮询？

**都不是**。这是理解 Declarative Partial Updates 时最容易混淆的地方。

### 5.1 本质差异

Declarative Partial Updates 本质上还是**一次普通的 HTML 请求**：

```
一个 request
一个 response
HTML 响应体持续流式输出
浏览器边接收边解析边 patch
```

它不是建立持久通信通道，不是双向实时通信，也不是服务端主动推送。它就是一次普通的 HTTP 请求，只不过响应体是流式输出的，浏览器在响应完成之前就开始解析和应用 patch。

### 5.2 技术对比表

| 技术 | 通信模式 | 协议 | 使用场景 | 复杂度 |
|------|---------|------|---------|--------|
| **Declarative Partial Updates** | 单次请求 + 流式响应 | HTTP（HTML 流） | 页面局部内容补全 | 低（纯 HTML） |
| **SSE（Server-Sent Events）** | 服务端单向持续推送 | HTTP（EventSource） | 实时通知、消息流 | 中（需 JS 处理） |
| **WebSocket** | 全双工持久通信 | WS 协议 | 实时聊天、协作编辑 | 高（需 JS 处理 + 状态管理） |
| **HTTP/2 Server Push** | 服务端主动推送资源 | HTTP/2 | 资源预加载（已被多数浏览器废弃） | 中（需服务端配置） |
| **轮询（Polling）** | 客户端定时请求 | HTTP | 简单数据刷新 | 低（但效率低） |
| **长轮询（Long Polling）** | 客户端请求挂起等待 | HTTP | 早期实时方案 | 中 |

### 5.3 关键区别

**与 SSE 的区别**：
- SSE 需要客户端通过 `EventSource` 建立专门的事件通道，并用 JavaScript 处理事件
- Declarative Partial Updates 是在普通 HTML 响应中流式输出，浏览器原生解析，无需 JS

**与 WebSocket 的区别**：
- WebSocket 是全双工持久连接，适合双向实时通信（聊天、协作）
- Declarative Partial Updates 是单次请求-响应，适合页面初始加载和内容补全

**与 HTTP/2 Server Push 的区别**：
- HTTP/2 Server Push 是推送额外资源（CSS、JS、图片），不直接更新 DOM 内容
- Declarative Partial Updates 是直接更新页面内容片段

### 5.4 重点不是"实时通信"

> **重点不是"实时通信"。重点是：HTML 文档本身开始支持后续 patch。**

这是 HTML 交付方式的升级。以前一个 HTML 响应必须在响应结束时才是"完整的"；现在一个 HTML 响应可以是渐进式的，浏览器在响应过程中就能不断应用 patch。这打破了"一次请求对应一次完整渲染"的传统模型。

---

## 六、框架影响分析：不会成为框架杀手

这个能力没必要理解成"哪个框架要被替代"。这是对它最常见也是最大的误解。

### 6.1 前端框架解决的工程问题

前端框架解决的是一整套工程问题：

- **组件组织**：组件化、复用、组合
- **状态管理**：跨组件状态共享、响应式更新
- **路由**：客户端路由、动态加载
- **构建**：打包、tree-shaking、代码分割
- **复用**：组件库、设计系统
- **复杂交互**：表单、拖拽、动画、手势
- **团队协作**：代码规范、类型系统、工程化工具链

这些不是一个 HTML 提案能直接吃掉的。一个声明式的局部更新语法，无法替代 React 的虚拟 DOM diffing、Vue 的响应式系统、Angular 的依赖注入——这些都是为了解决复杂应用工程化问题而存在的。

### 6.2 真正改变的是什么

Declarative Partial Updates 真正改变的是另一件事：

> 过去很多页面局部更新能力，是框架和库在替浏览器补课。

服务端明明已经生成了一段 HTML，但浏览器不知道这段 HTML 应该更新到哪里。于是开发者只能：

- 写 JS 去请求这段 HTML
- 用 `querySelector` 定位目标位置
- 用 `innerHTML` 或 `insertAdjacentHTML` 替换内容
- 或者引入额外运行时（HTMX、Stimulus、Alpine.js 等）来完成这件事

这是浏览器原生能力的缺失，框架只是在"补课"。

### 6.3 新提案想做的事

现在这个提案想把这条路径缩短：

```
HTML 声明更新位置
template 携带更新内容
浏览器原生完成 patch
```

### 6.4 客观结论

> **这不会让复杂前端消失。但会吃掉一部分纯胶水代码。**

尤其是那些只是为了"把服务端内容塞回页面"的代码。对于：

- 中后台管理页面（CRUD 为主）
- 内容展示页（资讯、文档、博客）
- 详情页（订单、商品、用户）
- 简单的动态加载场景

这些场景未来可能不再需要引入完整的客户端框架，Declarative Partial Updates + 服务端渲染就能覆盖大部分需求。但对于：

- 复杂的 SPA 应用（Figma、Notion、Linear）
- 重交互场景（拖拽编辑器、可视化工具）
- 需要客户端状态管理的应用
- 大型团队协作的复杂工程

框架依然是不可替代的。Declarative Partial Updates 和框架是**互补关系**，不是替代关系。

---

## 七、Declarative Shadow DOM 关联：HTML 重新变强的趋势

这不是浏览器第一次把能力还给 HTML。另一个已经落地的能力叫：**Declarative Shadow DOM**。理解它有助于看清 Declarative Partial Updates 背后的更大趋势。

### 7.1 传统 JavaScript 创建 Shadow DOM

以前创建 Shadow DOM，需要写 JavaScript：

```javascript
element.attachShadow({ mode: 'open' });
```

这种方式存在的问题：

- 必须依赖 JavaScript 才能创建 Shadow DOM
- 在 SSR（服务端渲染）场景下，服务端无法生成带 Shadow DOM 的 HTML
- 组件封装能力被绑定在客户端运行时上
- 首屏渲染需要等待 JS 加载执行

### 7.2 声明式 Shadow DOM 代码示例

现在可以直接写 HTML：

```html
<price-card>
  <template shadowrootmode="open">
    <style>
      .price {
        font-weight: bold;
        font-size: 20px;
      }
    </style>

    <slot name="price"></slot>
  </template>

  <span slot="price">¥199</span>
</price-card>
```

浏览器会直接解析这个 `template`，并创建对应的 Shadow Root。不需要任何 JavaScript 介入，不需要 `attachShadow` 调用，不需要等待 hydration。

### 7.3 这件事的意义

这件事的意义不只是少写几行 JS。它说明一个趋势：

| 能力 | 作用 |
|------|------|
| **Declarative Shadow DOM** | 让组件封装回到 HTML |
| **Declarative Partial Updates** | 让局部更新回到 HTML |

**一个解决组件结构，一个解决内容更新。**

### 7.4 趋势分析

这两个能力放在一起看，能看出一个清晰的方向：

1. **从命令式到声明式**：把"做什么"从 JS 代码中抽离出来，放到 HTML 声明中
2. **从客户端到服务端**：让服务端能够生成完整的 HTML 结构，包括 Shadow DOM 和更新区域
3. **从框架到平台**：把框架补课的能力下沉到浏览器平台原生支持

这两个能力的出现，标志着 HTML 正在重新变强。它不再只是首屏的静态外壳，而是开始拥有原生的组件化和动态更新能力。

---

## 八、内容评估：准确性、权威性与实用性

本节从三个维度对原文内容进行评估，帮助读者判断信息的可靠程度和适用范围。

### 8.1 准确性评估

**评估维度**：

| 评估项 | 评估结果 |
|--------|---------|
| 是否引用 Chrome 官方文档 | ✅ 是，引用了 developer.chrome.com |
| 语法示例是否准确 | ✅ `<?start?>`/`<?end?>`、`<template for>` 符合官方说明 |
| 流程描述是否准确 | ✅ 流式输出、浏览器自动 patch 的描述与官方一致 |
| 技术对比是否准确 | ✅ 与 SSE/WebSocket/Server Push 的区分正确 |

**结论**：准确性高。原文的技术细节与 Chrome 官方文档一致，没有出现明显的概念错误或误导性描述。

### 8.2 权威性评估

**评估维度**：

| 评估项 | 评估结果 |
|--------|---------|
| 技术来源 | Chrome 官方推进的能力 |
| 引用文档 | developer.chrome.com 官方博客 |
| 浏览器厂商背书 | Google Chrome 团队 |
| 标准化状态 | 处于提案/实验阶段 |

**结论**：权威性高。来源是 Chrome 官方推进的 Web 平台能力，引用的是 Chrome 官方开发者博客，具有较高的可信度。但需要注意：该能力目前仍处于实验阶段，相关语法和 API 可能在未来调整。

### 8.3 实用性评估

**评估维度**：

| 评估项 | 评估结果 |
|--------|---------|
| 当前是否可用于生产环境 | ❌ 否，处于开发者测试阶段 |
| 是否需要实验性 flag | ✅ 需要，Chrome 通过实验性 flag 开启 |
| 概念预研价值 | ✅ 高，对未来 Web 架构选型有参考意义 |
| 是否影响当前技术决策 | ⚠️ 有限，需等待标准化和浏览器兼容性成熟 |

**结论**：概念预研价值高，但当前实用性有限。开发者可以了解和预研，但短期内在生产环境仍需使用现有方案（如 HTMX、SSR + 客户端 hydration 等）。

### 8.4 原文优缺点分析

**优点**：

1. **通俗易懂**：用订单状态更新的具体场景讲清了抽象概念，非专业读者也能理解
2. **对比清晰**：新旧路径对比、与 SSE/WebSocket 的对比让读者快速把握差异
3. **趋势洞察**：从单个能力延伸到"HTML 重新变强"的更大趋势，视野开阔
4. **场景具体**：列举了后台详情页、订单页、商品页等具体适用场景，便于读者对号入座

**不足**：

1. **缺少兼容性说明**：未详细说明各浏览器的支持情况，读者难以判断实际可用性
2. **无性能数据**：未提供首屏时间、TTFB、内存占用等量化数据支撑论点
3. **服务端改造细节缺失**：未说明服务端如何实现流式 HTML 输出（如 Node.js 流、HTTP chunked encoding 等）
4. **错误处理未覆盖**：未说明 patch 失败、网络中断、超时等异常场景的处理方式

---

## 九、个人理解与见解

本节提出六个维度的个人见解，尝试从更宏观的视角解读 Declarative Partial Updates 的意义。

### 9.1 浏览器平台化能力下沉趋势

**核心观点**：浏览器平台把框架层能力下沉到 HTML 标准是长期趋势。

回顾 Web 平台演进历史，可以看到一条清晰的脉络：很多最初由框架引入的能力，最终都被标准化并下沉到浏览器原生支持。

| 框架能力 | 浏览器原生替代 |
|---------|---------------|
| jQuery DOM 操作 | `querySelector`、`addEventListener` |
| React 组件 | Web Components、Declarative Shadow DOM |
| Vue 响应式 | `MutationObserver`、`ResizeObserver` |
| 前端路由 | History API |
| 局部更新 | **Declarative Partial Updates（提案中）** |

这不是偶然，而是平台演进的必然规律。框架是创新的试验场，验证成功后会被标准化。Declarative Partial Updates 正在走这条路——从 HTMX 等"声明式 HTML 增强"框架中汲取灵感，逐步进入 Web 平台标准。

### 9.2 声明式 > 命令式的设计哲学回归

**核心观点**：从 JS 命令式回到 HTML 声明式，是设计哲学的回归。

Web 的最初设计哲学就是声明式的——HTML 描述"是什么"，而不是"怎么做"。但过去十年，受前端框架影响，我们习惯了命令式思维：手动 fetch、手动 setState、手动 patch DOM。

Declarative Partial Updates 让我们重新思考：**很多场景下，我们真正需要的不是命令式的控制权，而是声明式的简洁**。

```
命令式（JS）：fetch → parse → querySelector → innerHTML
声明式（HTML）：<?start?> + <template for>
```

声明式的好处：

- 代码更短、意图更清晰
- 浏览器可以做更多优化（因为知道你要做什么）
- 减少出错点（少了中间环节）
- 更符合 Web 的原始设计哲学

### 9.3 "浏览器补课"现象

**核心观点**：过去很多框架能力本质是弥补浏览器原生能力不足。

有一个值得反思的现象：很多被我们当作"框架价值"的东西，本质上是"浏览器补课"。

- React 的虚拟 DOM diff → 浏览器原本不会局部更新
- HTMX 的 `hx-*` 属性 → 浏览器原本不支持声明式请求
- Stimulus 的 controllers → 浏览器原本没有原生交互增强
- 各种 SSR 方案 → 浏览器原本不支持流式 HTML patch

这些都不是真正的"业务复杂度"，而是"平台能力不足"导致的工程负担。当浏览器原生补上这些能力后，这部分"框架价值"就会消失。

**真正属于框架的核心价值是什么？** 是组件组织、状态管理、工程化协作——这些是任何标准都难以完全覆盖的，因为它们解决的是"人和代码的协作问题"，而不是"浏览器能力问题"。

### 9.4 对前端工程的影响

**核心观点**：简单场景可能不再需要引入完整框架。

如果 Declarative Partial Updates 落地，前端工程的"准入门槛"会发生分化：

**轻量场景**：
- 中后台 CRUD 页面、内容展示页、详情页
- 不再需要 React/Vue 完整框架
- 服务端渲染 HTML + Declarative Partial Updates 即可
- 包体积从 MB 级降到 KB 级

**重度场景**：
- 复杂 SPA、可视化编辑器、协作工具
- 依然需要完整框架
- 但局部更新部分可以利用浏览器原生能力减少胶水代码

**对开发者的影响**：
- 技术选型需要更精准地判断场景复杂度
- "默认上 React"的思维定式需要调整
- 服务端开发能力重新变得重要（HTML 片段生成）
- 需要理解浏览器原生能力，避免重复造轮子

### 9.5 对后端渲染的重新审视

**核心观点**：服务端渲染 HTML 可能迎来复兴。

过去十年，前端工程的重心从服务端转向客户端，"前后端分离"成为主流。但 Declarative Partial Updates 提供了一个新的视角：

**服务端渲染 HTML 不一定是"倒退"，可能是更优解。**

| 维度 | 客户端渲染（CSR） | 服务端渲染（SSR）+ Declarative Partial Updates |
|------|------------------|------------------------------------------------|
| 首屏速度 | 慢（需下载 JS） | 快（HTML 即首屏） |
| 局部更新 | 依赖 JS fetch + patch | 原生 HTML patch |
| 客户端复杂度 | 高（需状态管理） | 低（浏览器原生） |
| SEO | 差（需 SSR 兜底） | 好（HTML 完整） |
| 包体积 | 大（JS bundle） | 小（少量 JS） |

这并不是说 CSR 要被取代，而是：**对于内容展示类页面，SSR + Declarative Partial Updates 可能是更自然的选择**。服务端生成 HTML 片段、流式输出、浏览器原生 patch——这套链路天然适合内容驱动型应用。

### 9.6 当前局限性的客观认识

**核心观点**：实验阶段、标准化不确定、浏览器兼容性未知。

尽管前景可期，但必须保持冷静：

**1. 实验阶段**：
- 目前仅在 Chrome 中可通过 flag 开启测试
- 距离生产可用还有相当长的路要走
- 语法和 API 可能调整

**2. 标准化不确定**：
- 仍处于提案阶段，未进入 HTML 规范
- 能否成为标准，何时成为标准，都不确定
- Firefox、Safari 是否跟进支持未知

**3. 浏览器兼容性未知**：
- 即使 Chrome 落地，跨浏览器兼容性可能需要数年
- 旧浏览器无法支持
- 在过渡期可能需要 polyfill 或渐进增强策略

**4. 工程化生态缺失**：
- 服务端流式 HTML 输出的框架支持有限
- 调试工具、性能监控、错误处理方案都不成熟
- 开发者社区需要时间积累最佳实践

**建议**：当前阶段适合"了解和预研"，不适合"投入生产"。建议关注 Chrome 官方博客和 W3C/WHATWG 的标准化进展，等待至少 1-2 年再评估生产可行性。

---

## 十、常见问题解答（FAQ）

**Q: Declarative Partial Updates 现在能在生产环境使用吗？**

A: 不能。该能力目前仍处于开发者测试阶段，仅能在 Chrome 中通过实验性 flag 开启测试。语法和 API 可能调整，浏览器兼容性也未确定，**强烈不建议在生产环境使用**。建议持续关注 Chrome 官方博客和标准化进展，等待能力成熟。

---

**Q: 它和 SSE/WebSocket 有什么区别？**

A: 本质区别在于通信模式：

- **Declarative Partial Updates**：单次 HTTP 请求 + 流式响应，浏览器原生解析 HTML patch，无需 JS
- **SSE**：服务端单向持续推送，需要客户端 `EventSource` + JavaScript 处理事件
- **WebSocket**：全双工持久通信，适合实时双向交互

Declarative Partial Updates 不是为"实时通信"设计的，而是为"页面初始加载和内容补全"设计的。它在一次响应内完成所有 patch，响应结束后连接关闭。

---

**Q: 它会替代 React/Vue 等前端框架吗？**

A: 不会。Declarative Partial Updates 解决的是"服务端 HTML 片段如何应用到页面"这一个问题，而前端框架解决的是组件组织、状态管理、路由、构建、复用、复杂交互、团队协作等一整套工程问题。

它可能吃掉一部分"纯胶水代码"——那些只是为了把服务端内容塞回页面的简单场景。但对于复杂 SPA、可视化编辑器、协作工具等，框架依然是不可替代的。**两者是互补关系，不是替代关系**。

---

**Q: 如何在 Chrome 中开启实验性测试？**

A: 开启步骤（基于 Chrome 实验性功能 flag 机制）：

1. 在 Chrome 地址栏输入 `chrome://flags`
2. 搜索 "Declarative Partial Updates" 或相关关键词
3. 将对应选项设置为 "Enabled"
4. 重启 Chrome 浏览器

**注意**：实验性 flag 可能随版本变化，具体名称请参考 Chrome 官方文档。开启实验性功能可能影响浏览器稳定性，建议在测试环境使用。

---

**Q: 服务端需要做什么改造？**

A: 服务端需要支持流式 HTML 输出（chunked transfer encoding）。具体改造包括：

1. **响应头设置**：使用 `Transfer-Encoding: chunked` 或合适的 streaming 响应模式
2. **骨架优先 flush**：先输出页面骨架（含 `<?start?>`/`<?end?>` 占位区域），立即 flush 到客户端
3. **后续 patch 流式输出**：各模块数据准备好后，依次输出 `<template for="...">` 片段
4. **响应结束**：所有模块 patch 输出完毕后，正常结束响应

不同后端框架的实现方式不同：Node.js 可用 `response.write()` 流式输出；Python Flask/Django 可用 streaming response；Go 可用 `http.Flusher`。具体方案需要参考所使用后端框架的流式响应文档。

---

**Q: 它和 HTMX 等现有方案有什么关系？**

A: HTMX 是通过 `hx-*` 属性增强 HTML 的声明式请求方案，让 HTML 可以发起 AJAX 请求并局部更新。两者的核心相似点和区别：

| 维度 | HTMX | Declarative Partial Updates |
|------|------|------------------------------|
| 实现 | JavaScript 库 | 浏览器原生 |
| 请求模式 | 多次请求（每次更新一次） | 单次请求 + 流式响应 |
| 是否需要 JS | 需要（HTMX 本身是 JS） | 不需要（原生支持） |
| 标准化 | 第三方库 | Web 标准提案 |

可以理解为：**HTMX 验证了"声明式 HTML 局部更新"的需求真实存在，Declarative Partial Updates 是这种思路的标准化和原生化**。在 Declarative Partial Updates 成熟前，HTMX 仍是可行的过渡方案。

---

**Q: 浏览器兼容性如何？**

A: 目前兼容性较差：

- **Chrome**：实验性支持（需开启 flag）
- **Firefox**：未明确表态
- **Safari**：未明确表态
- **Edge**：基于 Chromium，预计跟随 Chrome

在能力正式标准化并落地前，**不建议依赖浏览器原生支持**。过渡期可以考虑：

1. 检测浏览器支持（feature detection）
2. 不支持时降级到传统 fetch + DOM patch 方案
3. 或使用 HTMX 等库作为 polyfill

跨浏览器兼容可能需要 2-3 年时间，请密切关注 Can I Use 和 MDN 的兼容性数据。

---

**Q: 与服务端渲染（SSR）是什么关系？**

A: Declarative Partial Updates 与 SSR 是互补关系，而非替代关系：

**传统 SSR 的问题**：
- 服务端生成完整 HTML，但后续更新仍需"水合"为客户端接管
- 客户端需要重新建立数据通道（fetch API）来获取后续更新
- SSR 主要解决首屏，不解决持续更新

**Declarative Partial Updates 的补充**：
- 让服务端渲染可以"流式"进行——骨架先出，模块按需补全
- 不需要客户端 hydration 接管
- 后续 patch 也在同一个响应内完成

**结合使用**：
- SSR 负责首屏 HTML 骨架
- Declarative Partial Updates 负责流式补全内容
- 两者结合可以构建"无需客户端 JS"的动态页面

这是对 SSR 模式的增强，让服务端渲染从"一次性"变为"渐进式"。

---

## 十一、相关资源链接

### 11.1 官方资源

- **Chrome 官方博客（中文）**：https://developer.chrome.com/blog/declarative-partial-updates?hl=zh-cn
- **Chrome 官方博客（英文）**：https://developer.chrome.com/blog/declarative-partial-updates
- **Chromium 项目**：https://www.chromium.org/

### 11.2 原文与延伸阅读

- **原文链接**：https://mp.weixin.qq.com/s/MpJSwf9wbB14uVlNo6YyWA
- **作者**：认真努力的小四子

### 11.3 Declarative Shadow DOM 相关资源

- **MDN - Declarative Shadow DOM**：https://developer.mozilla.org/en-US/docs/Web/API/ShadowRoot/delegatesFocus
- **Chrome 博客 - Declarative Shadow DOM**：https://developer.chrome.com/docs/css-ui/declarative-shadow-dom
- **Web.dev - Declarative Shadow DOM**：https://web.dev/declarative-shadow-dom

### 11.4 Web Platform Features 相关文档

- **Chrome 实验性功能（chrome://flags）**：在 Chrome 地址栏输入 `chrome://flags` 查看
- **Web Platform Status**：https://web.dev/feature/
- **Can I Use**：https://caniuse.com/（查询浏览器兼容性）
- **MDN Web Docs**：https://developer.mozilla.org/

### 11.5 流式 HTML 输出相关技术资料

- **HTTP/1.1 Chunked Transfer Encoding**：RFC 7230 Section 4.1
- **Node.js Stream API**：https://nodejs.org/api/stream.html
- **HTML Living Standard - Streaming**：https://html.spec.whatwg.org/
- **WHATWG HTML Spec**：https://html.spec.whatwg.org/

### 11.6 相关替代方案（过渡期参考）

- **HTMX**：https://htmx.org/（声明式 HTML 增强，可作为 polyfill）
- **Stimulus**：https://stimulus.hotwired.dev/（轻量级 JS 框架）
- **Alpine.js**：https://alpinejs.dev/（轻量级响应式框架）
- **Turbo（Hotwire）**：https://turbo.hotwired.dev/（Rails 的流式 HTML 方案）

---

**文档版本**: v1.0
**更新日期**: 2026-07-04
**来源**: 微信公众号文章 + Chrome 官方文档 + 个人分析
**重要提示**: Declarative Partial Updates 当前处于实验阶段，本文内容仅供技术预研参考，不建议用于生产环境。请持续关注 Chrome 官方博客获取最新进展。
