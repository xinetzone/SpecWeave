# Minitap.ai 网站内容整理

> 数据采集日期：2026-07-07
> 来源页面：主页、Benchmark页面、博客列表、3篇核心博客文章

---

## 1. 产品概述

### 公司定位
- Minitap（品牌名：mini）是一个AI驱动的移动端测试平台
- 使命：让移动开发速度提升10倍
- 核心产品：**minitest** - 完全自主的AI QA工程师，用于移动端测试
- 创始人：Luc & Nico，从18岁开始共同构建移动应用
- 成立背景：曾用两年时间构建首个病毒式移动应用FueGo，深刻体会到移动开发速度瓶颈

### 产品核心理念
- 测试的单元应该是应用要完成的"任务"(job)，而不是绑定在某个界面上的脚本
- 代理(agent)应该拥有测试套件的所有权，无需人工编写或维护脚本
- "零编写、零维护" - 测试能适应任何重构
- 基于结果的意图，而非脆弱的选择器(selectors)
- 测试套件会随着应用变化自动更新

### 产品解决的问题
- 当前AI编码工具（Cursor、Claude Code）让Web开发速度提升了10倍，但移动端完全无法受益
- Web热修复几小时上线，移动端修复需要通过App Store审核，可能需要数天
- 脚本化E2E测试（Maestro、Appium、Playwright、Cypress）维护成本高，容易失效
- 工程师大量时间花在手动QA上，每个版本发布都有回归风险

---

## 2. 核心功能

### minitest 核心能力
1. **完全自主测试**
   - 从源代码构建应用
   - 像真实用户一样运行任务
   - 自动设计、运行和维护测试套件
   - 可选添加QA工程师进行人工审核

2. **四类问题检测**
   - **功能问题**：任务无法完成或完成不正确
   - **数据和内存问题**：泄漏、保留分配、CPU峰值、主线程工作过载
   - **UI/UX问题**：布局回归、可访问性问题、文本溢出、掉帧
   - **AI功能问题**：产品中模型驱动部分的非确定性行为

3. **失败报告**
   - 完整会话回放(session replay)
   - 运行时日志
   - 重现步骤(repro steps)
   - Cursor/Claude可用的修复提示(fix prompt)
   - 预期vs实际对比
   - 报告前自动重试，QA工程师审核后才送达用户

4. **高级场景处理**
   - 离线和不稳定网络
   - 文件和媒体上传
   - 用户角色(Personas)
   - 运行时日志（CPU/内存）

### 与传统测试方式对比

| 环节 | 手动QA | E2E测试(Maestro/Appium/Playwright/Cypress) | 代理式QA | mini (Minitap) |
|------|--------|-------------------------------------------|----------|----------------|
| 设计测试套件 | 人工 | 人工 | 人工 | 代理 |
| 编写测试 | 人工 | 人工 | 共享 | 代理 |
| 随产品变化更新 | 人工 | 人工 | 共享 | 代理 |
| 分类失败 | 人工 | 人工 | 人工 | 代理 |
| 决定发布 | 人工 | 人工 | 人工 | 人工 |

### 实际能力演示案例
- **自动注册账号**：在未配置测试账号的情况下，mini自动完成：
  - 反编译APK
  - grep JS bundle查找认证相关代码
  - 逆向工程后端API
  - 通过公开端点注册账号
  - 使用临时邮箱拦截验证邮件
  - 通过UI登录完成测试
  - 过程中发现2个真实bug：UX错误信息误导、注册端点无速率限制

---

## 3. 技术指标

### AndroidWorld Benchmark 成绩
- **任务成功率：100%**（全球第一，移动代理新纪录）
- 完成116个多样化任务，覆盖20个真实Android应用
- 超越Google DeepMind、ByteDance、Microsoft、Alibaba
- 开源代理mobile-use在40天内登顶排行榜
- 评估的平台数量：10个
- 开源仓库GitHub星标：2,500+（截至2026年5月）

### 覆盖的应用类型
AndroidWorld基准测试覆盖20个真实应用，包括：
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

### 测试执行效率
- 完整回归运行时间：30-60分钟（无人值守）
- 从连接仓库到首次可发布运行：5小时
- 支持每天15次发布（某移动应用工作室客户案例）
- 7个应用同时测试零维护脚本

### 测试可靠性数据
- Google测试数据：脚本测试flake（不稳定）消耗2-16%的测试计算资源，约1.5%的测试运行受影响
- minitest架构设计目标：零维护成本、零flake问题

---

## 4. 集成生态

### CI/CD 集成
- 直接运行在用户的CI中
- 结果作为PR上的绿/红检查标记
- 支持Slack通知

### 工具集成
- **已支持**：GitHub、Slack、Gmail
- **即将支持**：Jira、Linear、Bitbucket、GitLab、Notion

### 移动技术栈支持
- React Native
- Flutter
- Swift（原生iOS）
- Kotlin（原生Android）

### 框架无关性
- 与团队现有工具链兼容
- 无需替换现有开发流程

---

## 5. 支持平台

### 运行平台
- **iOS**：包含虚拟设备
- **Android**：包含虚拟设备
- **Web**：响应式Web应用

### 路线图
- 移动端先行
- Web和桌面端在路线图上
- 架构本身不局限于移动，可扩展到其他平台

---

## 6. 客户案例

### 客户Logo展示
企业客户（20+）：
- OpenAI
- Weights & Biases
- Datadog
- Snowflake
- EY-Parthenon
- Brex
- Memrise
- Radar
- LangChain
- Box
- J.P. Morgan
- Luciq
- Worldcoin
- Better Angle
- Inovexus
- mymuesli
- Felyx
- Hugging Face
- Last.fm
- Adjust
- SumUp
- FlixBus

### 具体客户案例
1. **移动应用工作室**
   - 在7个应用上运行Minitest
   - 每天发布15次
   - 零维护测试
   - 失败时在Slack实时通知，带视频时间戳和修复提示
   - 绿色构建时工程师可以安心下班

2. **A/B测试客户**
   - 在进行onboarding A/B测试时CTA按钮重命名
   - 传统脚本测试会失败
   - Minitest套件全程保持绿色，因为测试的是用户任务而非选择器

---

## 7. 成本数据

### 成本节约量化
- **每年节省工程师时间**：720小时（每个版本手动QA时间）
- **年度成本节约**：$46,800/年
  - 计算依据：工程师成本$3,900/月 × 12月
  - 时薪：$65/小时（美国QA职位中位数 × 1.3负担系数）
  - 每个版本手动QA时间范围：1-8小时（客户团队报告）
- **最大时间节约**：2,160小时/年（发布频率每月12次时）

### 测试方式成本对比
- 手动QA：时间随发布频率线性增长，每月12次发布时达到2,160小时/年
- minitest：接近0小时，无人值守，与发布频率无关

---

## 8. 最新动态

### 产品发布
- **2026年5月5日**：minitest正式发布 - "the agent owns the suite now"
  - 完全自主的移动AI QA工程师
  - 无需脚本、无需维护、无flake

### 技术博客
- **2026年5月17日**：《When our QA agent made its own account》
  - 记录mini在无测试账号情况下自动注册并发现bug的案例

### 融资动态
- **2025年12月1日**：完成$410万美元种子轮融资
  - 投资方：Moxxie Ventures、Mercuri、EWOR、Tekton Ventures、Amigos Venture Capital
  - 天使投资人：6位独角兽创始人
    - Thomas Wolf（Hugging Face，估值$45亿）
    - Stefan Glanzer & Michael Breidenbrucker（Last.fm）
    - Paul Muller（Adjust，退出价>$10亿）
    - Petter Made（SumUp，估值$80亿）
    - Daniel Krauss, Jochen Engert & André Schwämmlein（FlixBus，估值$30亿）
    - Saturnin Pugnet（Worldcoin）

### 开源进展
- 2025年开源mobile-use SDK
- 6个月内达到2,500 GitHub星标
- 发布学术论文：[arxiv.org/abs/2602.07787](https://arxiv.org/abs/2602.07787)

---

## 9. 媒体报道

### Forbes 报道（2025年12月1日）
- 标题：《Startup Minitap tops DeepMind's mobile AI benchmark, raises $4.1 million seed round》
- 链接：[forbes.com/sites/charliefink/2025/12/01/...](https://www.forbes.com/sites/charliefink/2025/12/01/startup-minitap-tops-deepminds-mobile-ai-benchmark-raises-41-million-seed-round/)
- 报道要点：
  - Minitap在DeepMind AndroidWorld基准测试中获得最高分
  - 完成$410万美元种子轮融资
  - 聚焦AI代理在移动开发和测试中的应用

---

## 10. 资源链接

### 官方资源
- 官网：[https://www.minitap.ai/](https://www.minitap.ai/)
- Benchmark页面：[https://www.minitap.ai/benchmark](https://www.minitap.ai/benchmark)
- 博客：[https://www.minitap.ai/blog](https://www.minitap.ai/blog)
- Demo页面：[https://www.minitap.ai/demo](https://www.minitap.ai/demo)
- 预约演示：[cal.com/team/minitap/minitap-get-access](https://cal.com/team/minitap/minitap-get-access?overlayCalendar=true)

### 博客文章
- [Announcing minitest: the agent owns the suite now](https://www.minitap.ai/blog/announcing-minitest-the-agent-owns-the-suite-now)（2026-05-05，12分钟阅读）
- [When our QA agent made its own account](https://www.minitap.ai/blog/when-our-qa-agent-made-its-own-account)（2026-05-17，8分钟阅读）
- [Raise announcement](https://www.minitap.ai/blog/raise-announcement)（2025-12-01）

### 开源与学术
- GitHub开源仓库：[github.com/minitap-ai/mobile-use](https://github.com/minitap-ai/mobile-use)（2.5k星标）
- 学术论文：[arxiv.org/abs/2602.07787](https://arxiv.org/abs/2602.07787)
- AndroidWorld基准：[github.com/google-research/android_world](https://github.com/google-research/android_world)

### 竞争对手对比（Benchmark页面）
- AGI-0（The AGI Company）
- askui
- Surfer 2（H Company）
- gbox.ai
- Z.AI

---

## 补充：关键引用与观点

### "The Bitter Lesson" 应用
Rich Sutton 2019年的文章《The Bitter Lesson》核心论点：在AI研究的每个主要领域，利用计算的通用方法最终击败了试图编码人类知识的方法。Minitap认为软件测试正在经历同样的转变。

### 测试的代际演进
1. 1970年：瀑布模型，QA团队编写文档测试
2. 1990年代中期：测试驱动开发(TDD)，JUnit
3. 2006年：行为驱动开发(BDD)，RSpec、Cucumber
4. 2010年：持续交付，测试金字塔
5. 2025-2026年：AI代理自主测试（minitest）

### 对"AI测试AI代码"质疑的回应
Minitap独立验证用户面向的行为，测试规范来自用户试图执行的产品行为，而非底层实现。代理运行用户会运行的任务并报告结果，与代码由谁编写无关。
