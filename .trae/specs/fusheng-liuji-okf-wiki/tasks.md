# Tasks：《浮生六记》OKF wiki 教程知识包

# 任务总览
- [x] Task 1: 建 bundle 骨架与根文档（index.md / facts.md / insights.md / log.md）
  - [x] 1.1: 创建目录 think/classics/fusheng-liuji-reading/{concepts,examples,references}
  - [x] 1.2: 编写 index.md（frontmatter type: OKF + 快速导航 + 快速开始 + 学习路径 + toctree）
  - [x] 1.3: 编写 facts.md（R 阶段产物，≥40 条 F 编号零推测事实，分域编号，G1 质量门）
  - [x] 1.4: 编写 insights.md（I 阶段产物，≥4 条四元组洞察 + 知识地图 + 学习路径）
  - [x] 1.5: 编写 log.md（创建日志，含七概念编排事件与日期 2026-08-30）

- [x] Task 2: 概念文档（concepts/ 7 篇 + index.md）
  - [x] 2.1: 00-why-read.md — 为什么读《浮生六记》
  - [x] 2.2: 01-author-and-era.md — 沈复其人与其时代
  - [x] 2.3: 02-six-records-structure.md — 六记结构与读法
  - [x] 2.4: 03-yun-niang.md — 芸娘形象与女性书写
  - [x] 2.5: 04-textual-history.md — 版本流传
  - [x] 2.6: 05-forgery-case.md — "足本"伪书公案
  - [x] 2.7: 06-life-aesthetics.md — 闲情雅趣与生活美学
  - [x] 2.8: concepts/index.md（导航表 + toctree 覆盖 7 篇）

- [x] Task 3: 实践示例（examples/ 3 篇 + index.md）
  - [x] 3.1: 01-close-reading.md — 名篇精读（童趣/藏粥/七夕镌章/芸论李杜/回煞：原文+注+赏析）
  - [x] 3.2: 02-reading-plan.md — 阅读路径与版本选择（零基础计划 + 注本/译本分级推荐）
  - [x] 3.3: 03-lost-records.md — 佚卷追寻（钱泳《记事珠》卷五佚文始末 + "足本"读法）
  - [x] 3.4: examples/index.md（导航表 + toctree）

- [x] Task 4: 信源登记（references/ 4 篇 + index.md）
  - [x] 4.1: 01-primary-editions.md — 原典与版本信源
  - [x] 4.2: 02-scholarship.md — 研究文献
  - [x] 4.3: 03-translations.md — 译介传播
  - [x] 4.4: 04-adaptations.md — 衍生与跨媒介
  - [x] 4.5: references/index.md（导航表 + toctree）

- [x] Task 5: 三级导航登记
  - [x] 5.1: 新建 think/classics/index.md（group 索引 + toctree）
  - [x] 5.2: 更新 think/index.md（分组表新增 classics + toctree + 描述）
  - [x] 5.3: 更新 bundles/index.md（think 域 5 束·2 组 → 6 束·3 组 + 分组表行）

- [x] Task 6: 质量验证（gates + 手动等价检查）
  - [x] 6.1: 运行 invoke gates.toctrees（或手动验证无断链/无孤立文档）
  - [x] 6.2: 运行 invoke gates.utf8（或等价 UTF-8 检查）
  - [x] 6.3: frontmatter 全量抽查（type/title/description/tags/generated/status/stale_after/sources）
  - [x] 6.4: 确认无 file:/// 绝对路径链接

- [x] Task 7: 独立对抗审查（V 阶段）
  - [x] 7.1: 委派独立审查者（新鲜上下文）按 spec 的 AC-1..AC-6 复核
  - [x] 7.2: 按审查结果修复可行动问题并复验
  - [x] 7.3: 记录审查结论于 log.md 与 spec 评审记录

# 依赖关系
- Task 1 是所有 Task 的前置（先建骨架与根文档）
- Task 2/3/4 相互独立，可并行
- Task 5 依赖 Task 2/3/4 完成（登记需知 bundle 内文件）
- Task 6 依赖 Task 2/3/4/5 完成
- Task 7 依赖 Task 6 完成
