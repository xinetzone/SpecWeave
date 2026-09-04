# Tasks

方法论链路：R（调研采集事实）→ I（洞察组织）→ E（萃取成包）→ V（对抗审查自查）→ C（原子提交，用户确认后）。

- [x] Task 1: 调研采集养生经典事实（R 阶段）
  - [x] SubTask 1.1: Web 调研核心 6 部经典（黄帝内经、养生论、千金要方养性篇、遵生八笺、老老恒言、寿亲养老新书）的作者/成书/版本/卷次/核心篇目
  - [x] SubTask 1.2: Web 调研扩展脉络（食疗本草、饮膳正要、导引图、八段锦、黄庭经等）及权威整理本/现代注本信息
  - [x] SubTask 1.3: 汇总产出 `facts.md`（编号条目、零推测、无因果词，G1 自查）
- [x] Task 2: 组织知识架构洞察（I 阶段）
  - [x] SubTask 2.1: 提炼养生思想谱系与知识地图，产出 `insights.md`（现象+根因+影响+建议四元组，G2 自查）
- [x] Task 3: 创建 yangsheng 分组与知识包骨架（E 阶段·结构）
  - [x] SubTask 3.1: 创建 `think/yangsheng/index.md` 分组索引与 `yangsheng-classics-reading/` 目录骨架（根 index、concepts/examples/references 子目录 index，frontmatter 合规）
- [x] Task 4: 撰写概念文档（E 阶段·内容）
  - [x] SubTask 4.1: concepts 总览篇（00-why-yangsheng：为什么读养生经典 + 阅读价值定位）
  - [x] SubTask 4.2: concepts 经典逐部要义（5 篇：01-黄帝内经、02-养生论、03-千金方养性、04-遵生八笺、05-老老恒言+寿亲养老）
  - [x] SubTask 4.3: concepts 谱系篇（06-schools-lineage：医家/道家/文人/食养/导引五脉源流）
  - [x] SubTask 4.4: concepts 方法篇（07-choosing-editions：如何选读版本与注本）
- [x] Task 5: 撰写示例与信源文档（E 阶段·内容）
  - [x] SubTask 5.1: examples 原文选读对照（01-suwen-shanggu-tianzhen：《上古天真论》三段选读+白话解读+注家视角）
  - [x] SubTask 5.2: examples 阅读计划（02-reading-plan：零基础四周入门路线）
  - [x] SubTask 5.3: references 信源登记（core-editions / modern-studies / extended-reading 3 篇）
- [x] Task 6: 更新导航与统计
  - [x] SubTask 6.1: 更新 `think/index.md`（分组表 + toctree + 域描述）与 `doc/bundles/index.md`（287 束/33 组、域行 6 束 3 组、yangsheng 锚点条目）
- [x] Task 7: 质量门验证与修复
  - [x] SubTask 7.1: `check-utf8.py` 退出码 0（5821 文件）；`check-toctrees.py` 全库扫描中 yangsheng 范围零问题（两次全库运行输出均不含 yangsheng 条目）；全库退出码 1 的全部 14 项问题均位于 `think/sexology`、`think/classics`（其他会话并行进行中的工作，超出本 spec 范围，按规范不干预）
  - [x] SubTask 7.2: 对照 checklist.md 逐项自查（facts 无因果词 G1=0、insights 四元组 5×4、frontmatter 齐备、相对路径零断链、并发命名冲突已统一修复）
- [x] Task 8: 原子提交（用户跳过逐项确认后按推荐方案执行；每 commit 显式列文件，UTF-8 无乱码）
  - [x] SubTask 8.1: commit `37755d28`（detached HEAD，awesome-okf-xs 子模块）：仅 `doc/bundles/think/yangsheng/` 20 文件 +1238 行；经 `git cat-file -p` 验证中文无乱码（stdin 字节流提交规避 GBK 陷阱）
  - [x] SubTask 8.2: 两个导航 index（混入并行会话 classics/sexology 变更）按单职责原则留给并行会话合并提交；commit body 中已注明

# Task Dependencies

- Task 2 依赖 Task 1；Task 3 依赖 Task 2（或与 Task 2 并行后补洞察）；Task 4、5 依赖 Task 3（骨架）；Task 4 与 Task 5 内部各篇可并行；Task 6 依赖 Task 3-5；Task 7 依赖 Task 6；Task 8 依赖 Task 7 通过。
- 可并行：SubTask 1.1 / 1.2；SubTask 4.1-4.4；SubTask 5.1-5.3。
