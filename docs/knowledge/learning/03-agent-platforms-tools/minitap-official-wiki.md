---
title: "Minitap.ai 官方Wiki完整学习教程：零脚本AI QA工程师minitest深度解析、AndroidWorld 100%基准测试、开源mobile-use SDK与移动端测试革命"
category: "learning"
source: "external: 不存在-Minitap官网（https://www.minitap.ai/）、GitHub开源仓库、Forbes报道、学术论文"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitap-official-wiki.toml"
date: "2026-07-07"
status: "published"
summary: "深度解析Minitap.ai AI驱动的移动端测试平台，核心产品minitest作为完全自主的AI QA工程师，在AndroidWorld基准测试中达到100%任务成功率（全球第一），实现零脚本、零维护、零flake的移动端测试范式革命。涵盖技术架构、集成生态、客户案例、成本效益分析及开源mobile-use SDK。"
tags: ["minitap", "minitest", "mobile-use", "ai-qa", "mobile-testing", "androidworld", "e2e-testing", "agent-testing", "zero-script", "ai-agent", "mobile-automation"]
---
# Minitap.ai 官方Wiki完整学习教程

> **官网**: https://www.minitap.ai/
> **核心产品**: minitest - 完全自主的AI QA工程师
> **开源仓库**: https://github.com/minitap-ai/mobile-use
> **学术论文**: https://arxiv.org/abs/2602.07787
> **数据采集日期**: 2026-07-07

---

## 📋 目录导航

- [一、产品概述与核心定位](#一产品概述与核心定位)
- [二、核心价值主张（零脚本QA）](#二核心价值主张零脚本qa)
- [三、minitest产品功能详解](#三minitest产品功能详解)
- [四、技术优势与基准测试（AndroidWorld 100%）](#四技术优势与基准测试androidworld-100)
- [五、QA方式对比分析（表格）](#五qa方式对比分析表格)
- [六、集成生态](#六集成生态)
- [七、支持平台与技术栈](#七支持平台与技术栈)
- [八、客户案例与使用场景](#八客户案例与使用场景)
- [九、成本效益分析](#九成本效益分析)
- [十、融资与媒体报道](#十融资与媒体报道)
- [十一、最新动态与博客文章](#十一最新动态与博客文章)
- [十二、相关资源与交叉引用](#十二相关资源与交叉引用)

---

## 一、产品概述与核心定位

Minitap（品牌名：**mini**）是一家AI驱动的移动端测试平台公司，其使命是**让移动开发速度提升10倍**。核心产品**minitest**是一款完全自主的AI QA工程师，专门用于移动端自动化测试。

### 1.1 创始背景

公司由 **Luc & Nico** 联合创立，两人从18岁开始共同构建移动应用。他们曾用两年时间构建首个病毒式移动应用FueGo，在这一过程中深刻体会到移动开发速度的瓶颈——特别是测试环节严重拖慢了发布节奏。

> **来源**: [Minitap官网 - 关于我们](https://www.minitap.ai/)

### 1.2 行业痛点

当前AI编码工具（Cursor、Claude Code）已经让Web开发速度提升了10倍，但移动端完全无法受益于这一效率提升：

| 痛点 | Web端 | 移动端 |
|------|-------|--------|
| **修复上线周期** | 热修复几小时上线 | 需要通过App Store审核，可能需要数天 |
| **测试维护成本** | E2E测试相对稳定 | 脚本化E2E测试（Maestro、Appium、Playwright、Cypress）维护成本极高，容易失效 |
| **QA人力投入** | 相对较少 | 工程师大量时间花在手动QA上，每个版本发布都有回归风险 |

> **来源**: [Minitap官网 - 产品页](https://www.minitap.ai/)

### 1.3 测试范式演进

Minitap认为软件测试正在经历代际演进，而Rich Sutton 2019年的文章《The Bitter Lesson》验证了这一方向——利用计算的通用方法最终击败了试图编码人类知识的方法：

| 年代 | 测试范式 | 代表技术 |
|------|----------|----------|
| 1970年 | 瀑布模型 | QA团队编写文档测试 |
| 1990年代中期 | 测试驱动开发(TDD) | JUnit |
| 2006年 | 行为驱动开发(BDD) | RSpec、Cucumber |
| 2010年 | 持续交付 | 测试金字塔 |
| 2025-2026年 | AI代理自主测试 | **minitest** |

> **来源**: [Minitap博客](https://www.minitap.ai/blog)

---

## 二、核心价值主张（零脚本QA）

minitest的核心理念是**测试的单元应该是应用要完成的"任务"(job)，而不是绑定在某个界面上的脚本**。这一理念带来了革命性的价值主张：

### 2.1 四大核心原则

1. **代理拥有测试套件所有权**：代理(agent)应该拥有测试套件的所有权，无需人工编写或维护脚本
2. **零编写、零维护**："Zero script, zero maintenance" - 测试能适应任何重构
3. **基于意图而非选择器**：基于结果的意图，而非脆弱的选择器(selectors)
4. **自动更新**：测试套件会随着应用变化自动更新

### 2.2 对"AI测试AI代码"质疑的回应

Minitap独立验证用户面向的行为，测试规范来自用户试图执行的产品行为，而非底层实现。代理运行用户会运行的任务并报告结果，与代码由谁编写无关。

> **来源**: [Minitap官网](https://www.minitap.ai/)

### 2.3 核心价值量化

| 价值维度 | 传统方式 | minitest |
|----------|----------|----------|
| **脚本编写** | 需要人工编写 | 完全自动化 |
| **脚本维护** | 每次UI变更需要更新 | 零维护，自动适应 |
| **Flake问题** | Google数据显示2-16%测试计算资源浪费在flake上 | 架构设计目标：零flake |
| **回归风险** | 每个版本发布都有风险 | 30-60分钟完整回归，无人值守 |

> **来源**: [Minitap Benchmark页面](https://www.minitap.ai/benchmark)

---

## 三、minitest产品功能详解

minitest作为完全自主的AI QA工程师，具备四大核心能力模块：

### 3.1 完全自主测试能力

minitest能够端到端地完成整个测试流程：

- **从源代码构建应用**：自动拉取代码并编译
- **像真实用户一样运行任务**：模拟真实用户交互行为
- **自动设计、运行和维护测试套件**：无需人工干预
- **可选QA工程师人工审核**：关键环节可加入人工审核节点

### 3.2 四类问题自动检测

minitest能够检测四大类移动端常见问题：

| 问题类型 | 检测内容 |
|----------|----------|
| **功能问题** | 任务无法完成或完成不正确 |
| **数据和内存问题** | 内存泄漏、保留分配、CPU峰值、主线程工作过载 |
| **UI/UX问题** | 布局回归、可访问性问题、文本溢出、掉帧 |
| **AI功能问题** | 产品中模型驱动部分的非确定性行为 |

### 3.3 智能失败报告

当测试失败时，minitest提供完整的调试信息：

- **完整会话回放(session replay)**：完整视频记录
- **运行时日志**：详细的系统和应用日志
- **重现步骤(repro steps)**：清晰的bug复现路径
- **Cursor/Claude可用的修复提示(fix prompt)**：直接可用于AI编码工具的修复建议
- **预期vs实际对比**：直观的结果差异展示
- **报告前自动重试**：减少误报
- **QA工程师审核后送达**：确保报告质量

### 3.4 高级场景处理

minitest能够处理复杂的真实世界场景：

- 离线和不稳定网络环境
- 文件和媒体上传
- 用户角色(Personas)模拟
- 运行时日志采集（CPU/内存性能数据）

### 3.5 惊人能力演示：自动注册账号

在未配置测试账号的情况下，mini自主完成了以下复杂操作：

1. 反编译APK
2. grep JS bundle查找认证相关代码
3. 逆向工程后端API
4. 通过公开端点注册账号
5. 使用临时邮箱拦截验证邮件
6. 通过UI登录完成测试
7. **过程中发现2个真实bug**：UX错误信息误导、注册端点无速率限制

> **来源**: [Minitap博客 - When our QA agent made its own account](https://www.minitap.ai/blog/when-our-qa-agent-made-its-own-account)（2026-05-17）

---

## 四、技术优势与基准测试（AndroidWorld 100%）

minitest在Google DeepMind的AndroidWorld基准测试中取得了历史性突破。

### 4.1 AndroidWorld基准测试成绩

| 指标 | 成绩 |
|------|------|
| **任务成功率** | **100%**（全球第一，移动代理新纪录） |
| **完成任务数** | 116个多样化任务 |
| **覆盖应用数** | 20个真实Android应用 |
| **超越对手** | Google DeepMind、ByteDance、Microsoft、Alibaba |
| **开源代理登顶时间** | mobile-use在40天内登顶排行榜 |
| **评估平台数量** | 10个 |
| **GitHub星标** | 2,500+（截至2026年5月） |

> **来源**: [Minitap Benchmark页面](https://www.minitap.ai/benchmark)、[Forbes报道](https://www.forbes.com/sites/charliefink/2025/12/01/startup-minitap-tops-deepminds-mobile-ai-benchmark-raises-41-million-seed-round/)

### 4.2 覆盖的20个真实应用类型

AndroidWorld基准测试覆盖以下真实应用场景：

- Calendar（日历）
- Notes（笔记）
- Maps（地图）
- VLC（播放器）
- Messages（短信）
- Settings（设置）
- Web Browser（浏览器）
- Audio Recorder（录音）
- Camera（相机）
- Clock（时钟）
- Contacts（联系人）
- Expense Tracker（费用追踪）
- 以及其他8个应用

> **来源**: [AndroidWorld官方仓库](https://github.com/google-research/android_world)

### 4.3 测试执行效率指标

| 指标 | 数据 |
|------|------|
| **完整回归运行时间** | 30-60分钟（无人值守） |
| **从连接仓库到首次可发布运行** | 5小时 |
| **每日最大发布次数** | 15次（某移动应用工作室客户案例） |
| **并行测试应用数** | 7个应用同时测试零维护脚本 |

### 4.4 技术架构核心

minitest的技术架构建立在开源项目**mobile-use**之上，该SDK提供了：

- 规范化坐标抽象（Normalized Coordinate Abstraction）
- 多代理闭环执行（Multi-agent Closed-loop Execution）
- 跨平台统一交互接口

> **相关技术深度分析**:
> - [mobile-use-deep-learning-analysis.md](mobile-use-deep-learning-analysis.md) - mobile-use SDK深度学习分析
> - [multi-agent-closed-loop-execution.md](../../../retrospective/patterns/architecture-patterns/multi-agent-closed-loop-execution.md) - 多代理闭环执行架构
> - [normalized-coordinate-abstraction.md](../../../retrospective/patterns/architecture-patterns/normalized-coordinate-abstraction.md) - 规范化坐标抽象技术
> - [mobile-use深度学习复盘](../../../../.trae/specs/retrospectives-insights/mobile-use-deep-learning-analysis/) - mobile-use深度学习复盘

---

## 五、QA方式对比分析（表格）

### 5.1 四种QA方式全链路对比

| 环节 | 手动QA | E2E脚本测试<br>(Maestro/Appium/Playwright/Cypress) | 代理式QA | **mini (Minitap)** |
|------|--------|--------------------------------------------------|----------|---------------------|
| **设计测试套件** | 人工 | 人工 | 人工 | **代理** |
| **编写测试** | 人工 | 人工 | 共享 | **代理** |
| **随产品变化更新** | 人工 | 人工 | 共享 | **代理** |
| **分类失败** | 人工 | 人工 | 人工 | **代理** |
| **决定发布** | 人工 | 人工 | 人工 | 人工 |

> **来源**: [Minitap官网产品对比](https://www.minitap.ai/)

### 5.2 测试可靠性对比

| 维度 | 脚本测试 | minitest |
|------|----------|----------|
| **Flake率** | Google数据：约1.5%测试运行受影响，消耗2-16%测试计算资源 | 架构设计目标：0% |
| **维护成本** | 每次UI重构需要重写脚本 | 零维护 |
| **选择器依赖** | 强依赖CSS/XPath/Accessibility ID等脆弱选择器 | 基于用户任务意图，不依赖选择器 |
| **重构适应能力** | 脚本几乎必然失效 | 自动适应UI变化 |

> **来源**: [Minitap Benchmark页面](https://www.minitap.ai/benchmark)

### 5.3 A/B测试场景对比

以onboarding流程CTA按钮重命名的A/B测试为例：

| 测试方式 | 表现 |
|----------|------|
| 传统脚本测试 | 会失败，因为选择器或文本断言不匹配 |
| **Minitest** | **套件全程保持绿色**，因为测试的是用户任务而非选择器 |

> **来源**: [Minitap客户案例](https://www.minitap.ai/)

---

## 六、集成生态

minitest设计为框架无关（framework-agnostic），与团队现有工具链深度兼容，无需替换现有开发流程。

### 6.1 CI/CD集成

- **直接运行在用户的CI中**：不改变现有CI基础设施
- **结果作为PR上的绿/红检查标记**：与GitHub/GitLab等代码托管平台深度集成
- **Slack实时通知**：失败时带视频时间戳和修复提示

### 6.2 工具集成

| 状态 | 工具 |
|------|------|
| **✅ 已支持** | GitHub、Slack、Gmail |
| **🔄 即将支持** | Jira、Linear、Bitbucket、GitLab、Notion |

### 6.3 集成工作流

典型的集成工作流如下：

1. 开发者提交PR
2. minitest自动在CI中运行完整回归测试
3. 测试通过：PR显示绿色检查标记，可安全合并
4. 测试失败：
   - Slack实时通知
   - 包含会话回放视频（带时间戳）
   - 提供Cursor/Claude可直接使用的修复提示
   - QA工程师审核后送达开发者
5. 绿色构建时工程师可以安心下班

> **来源**: [Minitap官网集成文档](https://www.minitap.ai/)

---

## 七、支持平台与技术栈

### 7.1 当前支持平台

| 平台 | 支持状态 | 包含虚拟设备 |
|------|----------|--------------|
| **iOS** | ✅ 全面支持 | ✅ |
| **Android** | ✅ 全面支持 | ✅ |
| **Web** | ✅ 支持响应式Web应用 | - |

### 7.2 移动技术栈支持

minitest支持所有主流移动端开发技术栈：

| 技术栈 | 支持状态 |
|--------|----------|
| **React Native** | ✅ |
| **Flutter** | ✅ |
| **Swift（原生iOS）** | ✅ |
| **Kotlin（原生Android）** | ✅ |

### 7.3 产品路线图

- **移动端先行**：当前聚焦iOS和Android
- **Web和桌面端在路线图上**：架构本身不局限于移动
- **可扩展架构**：核心代理架构设计可扩展到其他平台

> **来源**: [Minitap官网](https://www.minitap.ai/)

---

## 八、客户案例与使用场景

### 8.1 企业客户矩阵（20+）

Minitap已拥有超过20家企业客户，涵盖多个行业：

| 行业 | 客户Logo |
|------|----------|
| **AI/ML** | OpenAI、Hugging Face、LangChain、Weights & Biases |
| **云基础设施/监控** | Datadog、Snowflake、Box |
| **金融科技** | Brex、J.P. Morgan、SumUp |
| **咨询** | EY-Parthenon |
| **移动出行** | FlixBus、Felyx |
| **语言学习** | Memrise |
| **广告/营销科技** | Adjust、Radar |
| **音乐/媒体** | Last.fm |
| **加密/Web3** | Worldcoin |
| **消费品牌** | mymuesli、Luciq、Better Angle、Inovexus |

> **来源**: [Minitap官网客户展示](https://www.minitap.ai/)

### 8.2 案例一：移动应用工作室（高频发布）

某移动应用工作室客户的使用场景：

| 指标 | 数据 |
|------|------|
| **同时运行应用数** | 7个应用 |
| **每日发布次数** | 15次 |
| **测试维护** | 零维护测试脚本 |
| **通知方式** | 失败时Slack实时通知，带视频时间戳和修复提示 |
| **工程师体验** | 绿色构建时可以安心下班 |

### 8.3 案例二：A/B测试场景

某客户在进行onboarding流程A/B测试时：

- **操作**：CTA按钮重命名
- **传统脚本测试**：会失败（文本断言不匹配）
- **Minitest表现**：套件全程保持绿色
- **原因**：测试的是用户任务（完成注册/登录），而非UI选择器或文本

> **来源**: [Minitap客户案例](https://www.minitap.ai/)

---

## 九、成本效益分析

### 9.1 时间成本节约量化

| 场景 | 年节约工程师时间 | 计算依据 |
|------|------------------|----------|
| **典型场景** | **720小时/年** | 每个版本手动QA时间累计 |
| **高频发布场景（每月12次）** | **2,160小时/年** | 发布频率提升后节约最大化 |

### 9.2 经济成本节约

| 成本项 | 金额 | 计算依据 |
|--------|------|----------|
| **年度成本节约（典型）** | **$46,800/年** | 工程师成本$3,900/月 × 12月 |
| **时薪基准** | $65/小时 | 美国QA职位中位数 × 1.3负担系数 |
| **单次版本QA时间** | 1-8小时 | 客户团队报告范围 |

> **来源**: [Minitap官网成本计算器](https://www.minitap.ai/)

### 9.3 成本模型对比

| 测试方式 | 成本模型 | 与发布频率关系 |
|----------|----------|----------------|
| **手动QA** | 时间随发布频率线性增长 | 每月12次发布时达到2,160小时/年 |
| **minitest** | **接近0小时** | 与发布频率无关，无人值守运行 |

### 9.4 ROI关键洞察

- **固定成本替代可变成本**：minitest将测试从随发布次数增长的可变人力成本，转变为固定的平台订阅成本
- **机会成本节约**：工程师从重复的手动QA中解放出来，专注于产品创新
- **发布速度提升**：从"数天一个版本"到"每天15次发布"，带来显著的竞争优势
- **回归风险降低**：完整回归测试每次发布都运行，减少线上bug带来的用户流失和品牌损失

---

## 十、融资与媒体报道

### 10.1 种子轮融资详情

| 融资项 | 详情 |
|--------|------|
| **融资轮次** | 种子轮（Seed Round） |
| **融资规模** | **$410万美元** |
| **宣布日期** | 2025年12月1日 |
| **领投/参投机构** | Moxxie Ventures、Mercuri、EWOR、Tekton Ventures、Amigos Venture Capital |

### 10.2 天使投资人阵容（6位独角兽创始人）

| 投资人 | 背景 | 公司估值/退出价 |
|--------|------|-----------------|
| **Thomas Wolf** | Hugging Face联合创始人 | 估值$45亿 |
| **Stefan Glanzer & Michael Breidenbrucker** | Last.fm联合创始人 | - |
| **Paul Muller** | Adjust联合创始人 | 退出价 > $10亿 |
| **Petter Made** | SumUp联合创始人 | 估值$80亿 |
| **Daniel Krauss, Jochen Engert & André Schwämmlein** | FlixBus联合创始人 | 估值$30亿 |
| **Saturnin Pugnet** | Worldcoin | - |

> **来源**: [Forbes报道](https://www.forbes.com/sites/charliefink/2025/12/01/startup-minitap-tops-deepminds-mobile-ai-benchmark-raises-41-million-seed-round/)、[Minitap融资公告](https://www.minitap.ai/blog/raise-announcement)

### 10.3 Forbes媒体报道

| 报道项 | 详情 |
|--------|------|
| **媒体** | Forbes（福布斯） |
| **标题** | 《Startup Minitap tops DeepMind's mobile AI benchmark, raises $4.1 million seed round》 |
| **发布日期** | 2025年12月1日 |
| **作者** | Charlie Fink |
| **链接** | [forbes.com/sites/charliefink/2025/12/01/...](https://www.forbes.com/sites/charliefink/2025/12/01/startup-minitap-tops-deepminds-mobile-ai-benchmark-raises-41-million-seed-round/) |
| **核心要点** | 1. Minitap在DeepMind AndroidWorld基准测试中获得最高分<br>2. 完成$410万美元种子轮融资<br>3. 聚焦AI代理在移动开发和测试中的应用 |

---

## 十一、最新动态与博客文章

### 11.1 产品发布里程碑

| 日期 | 事件 | 核心内容 |
|------|------|----------|
| **2026年5月5日** | **minitest正式发布** | "the agent owns the suite now" - 完全自主的移动AI QA工程师，无需脚本、无需维护、无flake |
| **2025年** | **mobile-use SDK开源** | 6个月内达到2,500 GitHub星标 |

> **来源**: [Minitap产品发布公告](https://www.minitap.ai/blog/announcing-minitest-the-agent-owns-the-suite-now)

### 11.2 核心博客文章

| 发布日期 | 标题 | 阅读时长 | 链接 | 核心内容 |
|----------|------|----------|------|----------|
| **2026-05-05** | Announcing minitest: the agent owns the suite now | 12分钟 | [链接](https://www.minitap.ai/blog/announcing-minitest-the-agent-owns-the-suite-now) | minitest正式发布，介绍零脚本QA理念 |
| **2026-05-17** | When our QA agent made its own account | 8分钟 | [链接](https://www.minitap.ai/blog/when-our-qa-agent-made-its-own-account) | 记录mini在无测试账号情况下自动注册并发现bug的惊人案例 |
| **2025-12-01** | Raise announcement | - | [链接](https://www.minitap.ai/blog/raise-announcement) | $410万种子轮融资公告 |

### 11.3 学术成果

| 类型 | 详情 |
|------|------|
| **论文标题** | mobile-use: Open-Source Mobile Agent SDK |
| **发布平台** | arXiv |
| **链接** | [arxiv.org/abs/2602.07787](https://arxiv.org/abs/2602.07787) |
| **开源仓库** | [github.com/minitap-ai/mobile-use](https://github.com/minitap-ai/mobile-use)（2.5k星标） |

---

## 十二、相关资源与交叉引用

### 12.1 官方资源

| 资源类型 | 链接 |
|----------|------|
| **官网** | [https://www.minitap.ai/](https://www.minitap.ai/) |
| **Benchmark页面** | [https://www.minitap.ai/benchmark](https://www.minitap.ai/benchmark) |
| **博客** | [https://www.minitap.ai/blog](https://www.minitap.ai/blog) |
| **Demo页面** | [https://www.minitap.ai/demo](https://www.minitap.ai/demo) |
| **预约演示** | [cal.com/team/minitap/minitap-get-access](https://cal.com/team/minitap/minitap-get-access?overlayCalendar=true) |

### 12.2 开源与学术资源

| 资源类型 | 链接 |
|----------|------|
| **GitHub开源仓库** | [github.com/minitap-ai/mobile-use](https://github.com/minitap-ai/mobile-use)（2.5k星标） |
| **学术论文** | [arxiv.org/abs/2602.07787](https://arxiv.org/abs/2602.07787) |
| **AndroidWorld基准** | [github.com/google-research/android_world](https://github.com/google-research/android_world) |

### 12.3 竞争对手参考（Benchmark页面）

在AndroidWorld基准测试中，Minitap超越了以下平台：

- AGI-0（The AGI Company）
- askui
- Surfer 2（H Company）
- gbox.ai
- Z.AI

### 12.4 交叉引用文档

本Wiki内容与以下内部深度分析文档密切相关，建议结合阅读：

| 文档 | 内容说明 | 链接 |
|------|----------|------|
| **mobile-use深度学习分析** | mobile-use开源SDK的技术架构、核心模块、实现细节深度解析 | [mobile-use-deep-learning-analysis.md](mobile-use-deep-learning-analysis.md) |
| **mobile-use深度学习复盘** | mobile-use技术研究过程的完整复盘、关键洞察与经验总结 | [mobile-use-deep-learning-analysis/](../../../../.trae/specs/retrospectives-insights/mobile-use-deep-learning-analysis/) |
| **多代理闭环执行架构** | minitest多代理协作的闭环执行机制、任务规划与验证流程 | [multi-agent-closed-loop-execution.md](../../../retrospective/patterns/architecture-patterns/multi-agent-closed-loop-execution.md) |
| **规范化坐标抽象** | mobile-use中跨平台坐标系统一抽象技术细节 | [normalized-coordinate-abstraction.md](../../../retrospective/patterns/architecture-patterns/normalized-coordinate-abstraction.md) |

### 12.5 关键信息来源汇总

| 信息类别 | 来源 |
|----------|------|
| **产品定位与功能** | [Minitap官网](https://www.minitap.ai/) |
| **基准测试数据** | [Minitap Benchmark页面](https://www.minitap.ai/benchmark)、[AndroidWorld官方仓库](https://github.com/google-research/android_world) |
| **融资信息** | [Forbes报道](https://www.forbes.com/sites/charliefink/2025/12/01/startup-minitap-tops-deepminds-mobile-ai-benchmark-raises-41-million-seed-round/)、[Minitap融资公告](https://www.minitap.ai/blog/raise-announcement) |
| **技术博客** | [Minitap博客](https://www.minitap.ai/blog) |
| **开源代码与论文** | [GitHub仓库](https://github.com/minitap-ai/mobile-use)、[arXiv论文](https://arxiv.org/abs/2602.07787) |

---

> **本Wiki最后更新**: 2026-07-07
> **数据来源**: Minitap官网、GitHub、Forbes、arXiv
> **状态**: published
