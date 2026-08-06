---
title: "BrowserAct 官网完整学习教程：Cloud+Local双模式Agent浏览器平台"
source: "BrowserAct官方网站 https://www.browseract.com/?co-from=QD"
date: "2026-08-03"
tags: ["browseract", "ai-agent", "browser-automation", "web-scraping", "cloud", "skillhub", "data-api", "zapier", "n8n", "residential-proxy"]
---

# BrowserAct 官网完整学习教程：Cloud+Local双模式Agent浏览器平台

> **官网地址**: https://www.browseract.com/?co-from=QD
> **相关教程**: [公众号版BrowserAct教程](browseract-wiki.md)（介绍CLI核心能力）

---

## 📋 目录导航

- [一、产品概览：从CLI到双模式平台](#一产品概览从cli到双模式平台)
- [二、Cloud vs Local：双模式架构对比](#二cloud-vs-local双模式架构对比)
- [三、7大核心功能详解](#三7大核心功能详解)
- [四、完整工作流程演示](#四完整工作流程演示)
- [五、4大使用场景](#五4大使用场景)
- [六、产品生态：SkillHub与平台能力](#六产品生态skillhub与平台能力)
- [七、集成生态](#七集成生态)
- [八、快速开始指南](#八快速开始指南)
- [九、完整资源导航](#九完整资源导航)

---

## 一、产品概览：从CLI到双模式平台

> "Build reusable web scrapers in the cloud, or give your local Agent a browser."

BrowserAct从早期的AI Agents CLI工具，已经发展为**Cloud+Local双模式平台**，为不同场景提供完整的浏览器自动化解决方案。

### 1.1 一句话定位

BrowserAct让你**从自然语言提示词构建可复用的网页爬虫（云端）**，或**为你的本地AI Agent配备一个真实可用的浏览器（本地）**。

### 1.2 核心价值主张

> **No code, no selectors, no maintenance**
>
> 无需代码、无需选择器、无需维护

传统网页爬虫需要你手写代码、调试CSS选择器、持续维护以适应页面改版。BrowserAct通过AI Agent自动处理这一切——你只需要用自然语言描述你想要什么数据。

### 1.3 社区影响力

BrowserAct曾拿下Product Hunt日榜第一，在开发者和AI Agent社区获得广泛关注，GitHub开源项目也积累了大量Star，是当前Agent浏览器自动化领域的标杆产品之一。

---

## 二、Cloud vs Local：双模式架构对比

BrowserAct提供两种使用模式，满足不同场景需求：

| 对比维度 | BrowserAct Cloud | Local Agent（AI Agents CLI） |
|---------|-----------------|------------------------------|
| **部署方式** | 云端运行，无需本地环境 | 本地安装，运行在你的机器上 |
| **安装要求** | 无需安装，浏览器直接访问 | 需要安装Skill到本地Agent |
| **存储位置** | 云端存储，不占用本地空间 | 本地文件系统，数据在本地 |
| **入口按钮** | Start in the cloud | Copy to agent |
| **核心能力** | 从提示词构建可复用爬虫/Bots | 给本地Agent提供浏览器能力 |
| **连接状态** | 云端自动管理 | 实时显示连接状态 |
| **浏览器复用** | 云端浏览器实例 | 支持本地Chrome复用 |
| **适用场景** | 数据采集、批量任务、定时运行 | 开发调试、日常Agent使用、本地工作流 |
| **典型用户** | 数据分析师、市场研究、运营人员 | 开发者、AI Agent用户、工程师 |

### 2.1 BrowserAct Cloud特点

- **无需安装**：打开浏览器就能用，不需要配置任何环境
- **无本地存储**：所有数据和任务在云端处理，不占用本地资源
- **任意位置运行**：只要有网络，任何设备都能访问和管理任务
- **可复用爬虫**：一次构建，多次运行，支持定时执行
- **适合批量任务**：大规模数据采集、多地区代理轮换

### 2.2 Local Agent（AI Agents CLI）特点

- **本地安装**：以Skill形式安装到Claude Code/Codex/Cursor等本地AI Agent
- **浏览器能力赋能**：给原本无法操作浏览器的本地Agent配备真实浏览器
- **Copy to agent入口**：一键复制安装指令，发送给Agent即可完成安装
- **实时连接状态**：明确显示浏览器连接状态，让你知道Agent是否就绪
- **本地Chrome复用**：可以复用你本地Chrome已有的登录态，避免重复登录
- **适合开发调试**：开发者可以在本地快速测试和迭代浏览器自动化流程

### 2.3 Local模式工作流

使用Local模式时，整个流程就像和一个真实的助手协作：

```
Your local Agent
    ↓ "You: Get the top 20 competitor listings..."
BrowserAct(local browser)
    ↓ "└ Connected · browser ready."
Browser(search results × 3 pages)
    ↓ "└ Pages opened · extraction verified."
Extract(listings × 20)
    ↓ "└ Price, rating, stock, and seller resolved."
Task complete
    ↓ "└ 20 rows written to listings.csv."
```

每一步都有清晰的状态反馈，你可以实时看到Agent在做什么，就像看着一个真人助手在浏览器里操作一样。

---

## 三、7大核心功能详解

BrowserAct围绕网页自动化和数据采集，提供了7大核心功能：

### 3.1 From prompt to reusable scraper（从提示词到可复用爬虫）

只需要用自然语言描述你需要的数据，不需要写任何代码，不需要手动找CSS选择器，也不需要持续维护页面适配。

Agent会自动完成：
- 理解你的数据需求
- 分析目标网站结构
- 构建数据提取逻辑
- 测试爬虫可用性
- 持续维护，适应页面变化

第一次构建完成后，这个爬虫就可以重复运行，还可以分享给团队其他人使用。

### 3.2 Choose the right browser（选择合适浏览器）

根据你的使用场景，可以选择两种浏览器模式：

- **Private（隐私浏览器）**：每次启动都是全新的干净环境，用完即弃，不留下任何痕迹。适合临时任务、公开数据采集、批量抓取。
- **Standard（标准浏览器）**：可以保留登录态、Cookie、浏览历史，适合需要登录的任务、长期运营的工作流。

选对浏览器模式，可以让你的任务执行更顺畅、更安全。

### 3.3 Keep going when pages change（自适应页面变化）

网页不是一成不变的——网站会改版、会做A/B测试、会调整布局。传统爬虫遇到这些变化就会失效，需要人工重新调试选择器。

BrowserAct的Agent具备自适应能力：
- 页面布局变化时，自动重新识别数据位置
- A/B测试导致的元素差异，智能判断正确目标
- 即使选择器失效，Agent也能通过语义理解找到正确内容
- 不会因为页面小改版就中断任务

这意味着你构建的爬虫可以长期稳定运行，不需要频繁维护。

### 3.4 Reach protected pages（访问受保护页面）

很多有价值的数据不在公开页面，而是在登录后、或者有反爬机制保护的页面。

BrowserAct内置能力：
- **Stealth browsing（隐身浏览）**：浏览器指纹伪装，降低被识别为机器人的概率
- **CAPTCHA handling（验证码处理）**：自动处理常见的验证码类型
- **登录态支持**：支持手动登录后保持会话，或者复用已有登录态
- **人机接力**：遇到无法自动处理的验证（如扫码、短信验证码），可以临时让人工介入，完成后继续执行

有了这些能力，你可以采集到更多真实、有价值的数据。

### 3.5 Plugs into your stack（接入你的工作流）

你构建完成并发布的Bots，可以直接在主流自动化平台中运行，无缝接入你现有的工作流：

- Make（原Integromat）
- n8n（开源自动化平台）
- Zapier（连接5000+应用）

不需要重新开发，不需要写API对接，在自动化平台中添加BrowserAct节点，就能运行你已有的爬虫，数据采集完成后自动触发后续流程。

### 3.6 High-quality residential proxies（高质量住宅代理）

大规模数据采集时，单一IP很容易被封禁。BrowserAct内置了跨地区的高质量住宅代理IP池：

- **多地区支持**：可以选择不同国家/地区的IP
- **住宅IP**：真实家庭宽带IP，不是机房IP，封禁风险低
- **自动轮换**：自动切换IP，避免单一IP访问频率过高
- **动态配置**：每个任务可以单独配置代理地区

这让你可以稳定采集不同地区的数据，降低被目标网站封禁的风险。

### 3.7 Get ready-to-use data（获取即用型数据）

BrowserAct输出的数据是经过清洗和结构化的，拿到就能直接用：

- **结构化数据**：CSV/JSON格式，字段清晰，可以直接导入Excel、数据库、BI工具
- **文件下载**：自动下载页面上的文件（PDF、图片、表格等）
- **运行日志**：完整的执行日志，方便排查问题和审计
- **API访问**：通过Data API可以直接获取采集结果，集成到你的系统中

不需要额外的数据清洗，不需要手动整理格式，任务完成后直接拿结果。

---

## 四、完整工作流程演示

让我们以**Amazon无线耳机采集**为例，展示BrowserAct的完整工作流程。

### 示例任务

> 收集Amazon排名前20的无线耳机数据，返回价格、评分、库存和来源URL，使用美国私有代理。

### 步骤1：输入提示词

在BrowserAct Cloud的输入框中，直接用自然语言描述你的需求：

```
Collect the top 20 Amazon wireless headphones. Return price, rating, stock, and source URL. Private US proxy.
```

不需要写代码，不需要画流程图，一句话说清楚你要什么。

### 步骤2：环境准备

Agent收到你的指令后，自动准备运行环境：

```
Environment ready. Starting now with a private browser and a dynamic US proxy.
```

- 自动启动一个全新的隐私浏览器实例
- 自动配置美国动态住宅代理
- 所有环境准备工作都是自动完成的，你不需要手动设置代理、配置浏览器指纹等。

### 步骤3：页面验证

打开目标网站后，Agent自动处理各种验证：

```
Page verification passed. Continuing the task.
```

包括自动处理"I'm not a robot"复选框、Cloudflare验证、其他反爬机制。如果遇到无法自动处理的验证（如复杂验证码、扫码），会触发人机接力让你协助完成。

### 步骤4：执行提取

验证通过后，Agent开始真正的数据采集工作：
- 自动翻页浏览Amazon搜索结果
- 智能识别商品卡片区域
- 逐个提取价格、评分、库存信息
- 记录商品来源URL
- 自动处理延迟加载、滚动加载等动态内容

整个过程不需要人工干预，Agent会像真人一样浏览页面、识别信息。

### 步骤5：输出结果

采集完成后，你会看到执行完成的提示：

```
Done — 20 products collected in 18 seconds.
```

生成的结果文件：
- `amazon-headphones.csv`（20 rows CSV）
- 包含字段：product name, price, rating, stock status, source URL
- 数据已经过清洗和结构化，可以直接打开使用

### Local Agent模式的状态日志

如果你使用Local Agent模式，状态日志会更贴近终端风格，实时反馈每一步进展：

```
**BrowserAct(local browser)** └ Connected · browser ready.
**Browser(search results × 3 pages)** └ Pages opened · extraction verified.
**Extract(listings × 20)** └ Price, rating, stock, and seller resolved.
**Task complete** └ 20 rows written to listings.csv.
```

每一步都清晰明了，你可以准确知道Agent当前在做什么，进展到哪一步了。

---

## 五、4大使用场景

BrowserAct适用于四大类数据采集和网页自动化场景：

### 5.1 Products & Suppliers（产品与供应商研究）

**核心价值**：持续追踪产品和供应链信息，掌握市场动态。

你可以：
- 追踪产品信息、价格变动、评分变化、促销活动
- 收集卖家信息、供应商数据、MOQ（最小起订量）
- 监控多个电商平台的同款产品价格
- 收集供应商的联系方式、产品目录、资质信息

**典型数据点**：产品名称、价格、原价、折扣比例、评分、评论数、库存状态、卖家名称、卖家评分、联系方式、MOQ、交货时间。

**适用人群**：电商运营、采购、供应链管理、品类经理。

### 5.2 Customers & Competitors（客户与竞品研究）

**核心价值**：了解市场声音，掌握竞品动态，做出更好的产品和市场决策。

你可以：
- 收集社交媒体帖子、用户评论、产品评分
- 监控竞品价格变动、产品更新、营销活动
- 抓取竞品的来源URL、流量渠道信息
- 收集用户反馈、痛点、需求点

**典型数据点**：评论内容、评分、发布时间、用户ID、竞品价格、产品功能对比、上新时间、促销活动、广告投放、帖子互动数据。

**适用人群**：市场研究、产品经理、竞品分析、用户研究员、品牌营销。

### 5.3 Lead Generation & Business Data（线索生成与商业数据）

**核心价值**：批量构建企业和潜在客户列表，助力销售和市场拓展。

你可以：
- 构建企业列表：企业名称、分类、地点、评分
- 提取公开联系方式、官网链接、社交媒体账号
- 收集特定行业的企业名录
- 抓取B2B平台上的供应商和采购商信息

**典型数据点**：企业名称、行业分类、地址、所在城市、评分、评论数、联系电话、邮箱、官网URL、LinkedIn主页、成立时间、员工规模。

**适用人群**：销售、BD、市场拓展、外贸、增长黑客。

### 5.4 Creators, Launches & Jobs（创作者、新品发布与就业市场）

**核心价值**：追踪内容生态和行业动态，捕捉新机会。

你可以：
- 追踪创作者动态、内容发布、粉丝增长
- 监控新品发布、众筹项目、Product Hunt等平台的新产品
- 跟踪广告投放、营销活动案例
- 监控职位发布信息，了解行业招聘需求和薪资水平

**典型数据点**：创作者名称、内容标题、发布时间、互动数据、新品名称、发布日期、众筹金额、职位名称、公司名称、薪资范围、工作地点、要求技能。

**适用人群**：内容创作者、HR招聘、行业观察者、投资人、自媒体、求职者。

---

## 六、产品生态：SkillHub与平台能力

BrowserAct不仅仅是一个单一工具，它已经发展成一个完整的产品生态：

### 6.1 核心产品入口

- **BrowserAct Cloud**：云端爬虫构建平台，核心产品入口。在浏览器中直接使用，从提示词构建可复用爬虫，适合大多数数据采集场景。
- **AI Agents CLI**：本地Agent浏览器能力，给Claude Code、Cursor、Codex等工具配备真实浏览器。适合开发者日常使用、本地工作流自动化。

### 6.2 SkillHub：技能市场

SkillHub是Skill Forge的进化形态——一个可发现和分享可复用爬虫技能的市场。

- **发现技能**：你可以在SkillHub上找到别人已经构建好的爬虫技能，直接拿来用，不需要自己从零开始构建
- **分享技能**：你自己构建好的爬虫，可以发布到SkillHub分享给社区，或者私享给团队成员
- **技能复用**：避免重复造轮子，社区共同维护高质量的爬虫技能
- **版本管理**：技能支持版本更新，适应网站变化

### 6.3 Templates：模板库

Templates提供即用型爬虫模板，覆盖常见的采集场景：
- 电商平台商品采集模板
- 社交媒体信息采集模板
- 企业名录采集模板
- 招聘信息采集模板

不需要从零描述需求，选择对应的模板，填入简单参数就能直接运行。

### 6.4 Data API：数据API接口

Data API提供程序化访问能力：
- 通过API直接触发已发布的Bot运行
- 获取任务运行状态和结果数据
- 集成到你自己的应用、系统、工作流中
- 支持Webhook回调，任务完成后主动通知你的系统

有了Data API，BrowserAct的数据采集能力可以成为你技术栈的一部分。

### 6.5 专项工具

- **Multi-Account Social**：多账号社交管理能力。支持同时管理多个社交媒体账号，每个账号独立环境、独立代理、独立指纹，适合社媒运营人员。
- **LinkedIn专属工具**：
  - **Linkedin Profile Scraper**：LinkedIn个人资料采集，批量获取用户的职位、公司、教育背景、技能等信息
  - **Linkedin Comments Scraper**：LinkedIn评论采集，收集帖子下的评论内容、评论者信息，用于社交聆听和用户研究

### 6.6 其他模块

- **Affiliate**：联盟计划。推广BrowserAct给其他人使用，可以获得收益分成。适合内容创作者、KOL、工具推荐博主。
- **Pricing**：定价页面。官网目前未展示具体价格，需要联系官方或注册后查看详细套餐信息。

---

## 七、集成生态

BrowserAct可以与你现有的工具和工作流无缝集成，打通数据采集到后续处理的完整链路。

### 7.1 自动化平台集成

已发布的Bots可以直接在主流自动化平台中运行：

- **Zapier**：连接5000+应用的自动化平台。在Zapier中添加BrowserAct节点，运行你的爬虫，采集完成后自动将数据发送到Google Sheets、Airtable、CRM、邮件等应用。
- **n8n**：开源自动化平台。可以私有化部署n8n，在工作流中集成BrowserAct节点，数据完全可控，适合企业内部使用。
- **Make（原Integromat）**：可视化自动化平台。强大的工作流编排能力，配合BrowserAct的数据采集，可以构建复杂的自动化业务流程。

### 7.2 本地Agent支持

Local Agent模式支持主流AI编程工具：

- **Claude Code**：Anthropic的AI编程工具。安装BrowserAct Skill后，Claude Code就具备了浏览器操作能力，可以帮你完成网页相关的任务。
- **Codex**：OpenAI的代码生成模型。通过BrowserAct，Codex可以操作真实浏览器，执行网页自动化任务。
- **Cursor**：AI代码编辑器。在Cursor中安装BrowserAct Skill，让AI编辑器助手帮你处理网页相关工作。

### 7.3 云合作伙伴（8家）

BrowserAct与主流云厂商合作，提供稳定可靠的基础设施：

- **AWS**（Amazon Web Services）
- **Microsoft Azure**
- **Google Cloud**
- **Oracle**
- **Alibaba Cloud（阿里云）**
- **Huawei Cloud（华为云）**
- **BytePlus（字节跳动火山引擎）**
- **Baidu AI Cloud（百度智能云）**

多云部署保证了服务的高可用性和全球覆盖能力，代理IP资源也更加丰富。

### 7.4 集成价值

将BrowserAct的数据采集能力无缝接入你现有的自动化工作流，可以实现：
- 数据采集完成后**自动存入CRM**，更新客户信息
- 价格监控数据**自动发送通知**，当竞品降价时及时提醒
- 采集到的线索**自动导入邮件营销系统**，启动培育流程
- 监控到新品发布时**自动生成报表**，发送到Slack/企业微信
- 招聘信息采集后**自动汇总到表格**，辅助HR筛选

不需要人工导出导入数据，整个流程完全自动化，真正实现"数据采集→数据处理→后续动作"的闭环。

---

## 八、快速开始指南

BrowserAct提供两种使用方式，你可以根据自己的需求选择：

### 8.1 方式一：BrowserAct Cloud（云端使用）

适合大多数用户，不需要安装任何东西，打开浏览器就能用。

**步骤：**

1. **访问官网**：打开 https://www.browseract.com/?co-from=QD
2. **进入云端**：点击页面上的"Start in the cloud"按钮
3. **描述需求**：在输入框中用自然语言描述你需要什么数据（比如"收集前20个Amazon无线耳机的价格和评分"）
4. **选择浏览器模式**：根据任务类型选择Private（隐私浏览器，适合临时采集）或Standard（标准浏览器，适合需要登录的任务）
5. **选择代理地区**：如果需要特定地区的IP，选择对应的代理位置（比如美国、日本等）
6. **构建运行**：点击构建按钮，Agent会自动构建并运行Bot
7. **获取结果**：任务完成后，下载结构化数据输出（CSV/JSON等），或者通过API获取

整个过程简单直观，第一次使用也能快速上手。

### 8.2 方式二：Local Agent（本地CLI）

适合开发者和需要本地浏览器能力的AI Agent用户。

**步骤：**

1. **访问官网**：打开 https://www.browseract.com/?co-from=QD
2. **复制指令**：点击"Copy to agent"按钮，自动复制安装指令到剪贴板
3. **打开本地Agent**：启动你的本地AI Agent（Claude Code/Codex/Cursor中的任意一个）
4. **粘贴安装**：把复制好的指令粘贴到Agent对话框，发送出去
5. **自动安装**：Agent会识别这是BrowserAct的安装指令，自动完成Skill的下载和安装
6. **开始使用**：安装完成后，你就可以直接让Agent执行网页任务了，BrowserAct会在底层提供浏览器能力
7. **参考详细教程**：本地Skill安装的详细命令和使用方法，可以参考[公众号版教程](browseract-wiki.md)

本地模式安装完成后，你就可以在日常开发中随时让Agent帮你操作浏览器——查资料、导数据、填表单、跑自动化流程都可以。

---

## 九、完整资源导航

### 9.1 官方资源

- **官网**：https://www.browseract.com/?co-from=QD
- **文档（Docs）**：官网页脚Docs链接，包含详细使用指南和API文档
- **博客（Blog）**：官网页脚Blog链接，发布产品更新、使用教程、案例分享

### 9.2 产品入口

- **BrowserAct Cloud**：官网首页"Start in the cloud"按钮
- **AI Agents CLI**：官网首页"Copy to agent"按钮
- **SkillHub**：技能市场入口
- **Pricing**：定价页面（注册后查看详细套餐）

### 9.3 专项工具

- **Data API**：数据API接口，程序化访问采集能力
- **Multi-Account Social**：多账号社交管理
- **Templates**：模板库，即用型爬虫模板
- **Linkedin Profile Scraper**：LinkedIn个人资料采集
- **Linkedin Comments Scraper**：LinkedIn评论采集

### 9.4 社交与联系

- **邮箱**：s****@***********（商务合作、技术支持、问题反馈）
- **X (Twitter)**：官网社交链接，关注产品更新和公告
- **LinkedIn**：官网社交链接，关注公司动态
- **Discord**：社区讨论，和其他用户交流使用经验
- **YouTube**：视频教程，可视化学习使用方法

### 9.5 法律

- **Terms of Service（服务条款）**：使用服务前请阅读
- **Privacy Policy（隐私政策）**：了解数据处理和隐私保护措施

### 9.6 交叉参考

- [BrowserAct 公众号版教程](browseract-wiki.md)——基于早期微信公众号文章，重点介绍CLI核心能力、人机接力、Skill Forge等概念，适合想要深入了解本地Agent模式和底层原理的用户。

---
