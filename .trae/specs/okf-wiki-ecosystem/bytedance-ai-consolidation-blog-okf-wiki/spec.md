---
status: "draft"
version: "1.0"
---

# 字节 AI 业务整合博文 → OKF Wiki 教程 Spec

## Why

微信公众号文章《字节把TRAE、扣子都并进豆包，图什么？》（公众号"窥见比特"，作者"比特一哥"，2026-08-27，收录于"科技前沿"）分析了 2026 年 8 月字节跳动 AI 业务整合（TRAE、扣子团队并入豆包），涉及资本开支数据、竞争格局（腾讯 WorkBuddy、阿里千问办公）、豆包工作产品战略。按 blog-article-to-okf-bundle 模式转化为 OKF 知识包，归入 ai/trae/ 分组（用户指定），作为 TRAE 战略背景资讯收录。

## 归属判定

**结论：`ai/trae/bytedance-ai-consolidation/`**（用户指定）

- 文章主线为字节 AI 组织整合，TRAE 是被整合的三个产品之一
- trae 分组现有 12 个 bundle 均为源码教程；本 bundle 为该分组首个资讯/战略背景类 bundle，需在 frontmatter 与已知边界中明确"非源码教程、商业分析性质"
- coze 分组虽也涉及，但用户指定 trae，且 TRAE IDE/CLI 保留为豆包品牌下编程子产品是文章关键结论

## What Changes

- 新增 OKF bundle：`ai/trae/bytedance-ai-consolidation/`
  - index.md + log.md + concepts/（3 篇 + index）+ references/（2 篇 + index）
  - 不设 examples/（商业分析无可运行示例）
- 更新 `ai/trae/index.md`：束数 12→13，新增导航条目与 toctree
- 更新 `bundles/index.md`：total_bundles 269→270、trae 分组 12→13、ai 域 96→97
- 不修改 external/ 任何内容

## 事实基础（博文 F-001 起）

- F-001: 2026-08-24 字节 AI 业务整合，TRAE 和扣子团队整体并入豆包，产品运营统一向豆包负责人赵祺汇报
- F-002: 距上一轮调整仅 25 天；2026-07-30 飞书产品团队并入豆包，销售团队划给火山引擎
- F-003: 一个月内飞书、TRAE、扣子三支队伍全部收进豆包
- F-004: 字节以前信奉赛马机制，TRAE/扣子/豆包由此而来
- F-005: 2025 年字节全年资本开支超 1500 亿元，约 900 亿 AI 算力采购，700 亿数据中心基建；AI 投入接近上一年两倍
- F-006: 2026 年 AI 基础设施预算从 1600 亿上调至 2000 亿元（约 300 亿美元），约 850 亿专项 AI 芯片采购
- F-007: 彭博社报道字节内部讨论过将资本开支推高至 700 亿美元（约 4767 亿元）
- F-008: 字节 2026 年 AI 算力中心资本支出相当于 2025 年利润的 60%
- F-009: 雅虎财经报道字节 2025 年利润因 AI 投入暴跌超 70%
- F-010: 腾讯 WorkBuddy 跑出百万级日活和千万级月访问量
- F-011: 梁汝波 8 月全员会：核心业务三块（AI/信息平台/交易服务），希望豆包成为像抖音一样的主干 AI 业务
- F-012: 飞书补企业协同和权限管理，TRAE 补编程和任务执行，扣子补多 Agent 协作和智能体搭建
- F-013: 豆包 8.17-21 连续上线远程控制电脑、Windows 虚拟桌面、云电脑、侧边工作台、技能商店、连接器
- F-014: 豆包最快本周推出独立 AI 办公产品；TRAE Work 和扣子办公能力与豆包工作场景深度融合
- F-015: TRAE IDE 和 CLI 继续保留，变为豆包品牌下的编程子产品
- F-016: 腾讯 WorkBuddy 已跑通、阿里千问办公已整合完，字节需集中 AI 能力竞争 AI 办公赛道
- F-017: 文章作者标注"个人观点，仅供参考"

## ADDED Requirements

### Requirement: Bundle 根索引
index.md frontmatter 含 sources（博文 URL + 公众号/作者/日期），明确标注"商业分析/战略资讯，非源码教程"。已知边界声明：个人观点性质、资本开支数字多引自外媒（彭博/雅虎）需核验、资讯时效性。

### Requirement: 概念文档（concepts/，3 篇）
- 00-consolidation-timeline.md：整合时间线（8.24 TRAE/扣子并入、7.30 飞书并入、一个月三次调整）与组织架构变化（赵祺汇报线）
- 01-cost-driven-rationale.md：算力成本驱动的组织变革——赛马机制在 AI 时代失效（人力成本 vs 算力成本）、2025-2026 资本开支数据、利润影响
- 02-competitive-landscape.md：AI 办公竞争格局——腾讯 WorkBuddy、阿里千问办公、豆包能力矩阵（飞书+TRAE+扣子协同）、TRAE IDE/CLI 保留为编程子产品

### Requirement: 信源登记簿（references/）
- article-source.md：F-001~F-017 博文事实登记 + 轻量核验记录（资本开支数字、WorkBuddy 数据、梁汝波全员会等可核验项）
- 明确标注哪些为作者观点（F-004/F-016 解读类）、哪些为外媒转述（F-007/F-009）

### Requirement: 索引更新
ai/trae/index.md 束数 12→13、bundles/index.md 计数同步。

## 约束
- 本文为个人观点商业分析，非技术教程；不设 examples/；不编造未在博文中出现的数据
- 外媒引用数据（彭博/雅虎财经）需在核验阶段尝试 WebSearch 验证，不可验证则标注"仅博文单源转述"
- 交叉引用 trae 分组内其他 bundle 用相对路径

<!-- changelog -->
<!--
- 2026-08-28 | initial | 按 blog-article-to-okf-bundle 模式转化字节AI整合博文
-->
