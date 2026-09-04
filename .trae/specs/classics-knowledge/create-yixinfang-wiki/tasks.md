# Tasks

方法论链路：R（调研采集事实）→ I（洞察组织）→ E（萃取成包）→ V（对抗审查自查）→ C（原子提交，用户确认后）。

- [x] Task 1: 调研采集《医心方》相关著作事实（R 阶段）
  - [x] SubTask 1.1: Web 调研《医心方》本体：丹波康赖生平家学、成书奏进年代、三十卷分类结构、征引书目规模、现存卷次
  - [x] SubTask 1.2: Web 调研亡佚引书重点：房中养生类（素女经/洞玄子/玉房秘诀/玉房指要）、医方类（小品方/深师方/范汪方/集验方等）、辑佚价值定位
  - [x] SubTask 1.3: Web 调研版本流传与研究史：古写本系统、安政刊本、清末回传中国路径、现代影印/整理本、中日研究史要点
  - [x] SubTask 1.4: 调研中间产物写入 `.temp/`（事实草稿与信源清单），汇总产出 `facts.md`（编号条目、零推测、无因果词，G1 自查）——79 条（F-001—F-079）
- [x] Task 2: 组织知识架构洞察（I 阶段）
  - [x] SubTask 2.1: 提炼《医心方》文献学知识地图，产出 `insights.md`（现象+根因+影响+建议四元组 ≥4 条，G2 自查）——4 条四元组
- [x] Task 3: 创建 medicine 分组与知识包骨架（E 阶段·结构）
  - [x] SubTask 3.1: 创建 `think/medicine/index.md` 分组索引与 `ishinpo-reading/` 目录骨架（根 index、concepts/examples/references 子目录 index、log.md，frontmatter 合规）
- [x] Task 4: 撰写概念文档（E 阶段·内容）
  - [x] SubTask 4.1: concepts 总览篇（00-why-ishinpo：为什么读《医心方》+ 辑佚价值定位 + 与养生/性学教程的关系）
  - [x] SubTask 4.2: concepts 成书篇（01-author-and-book：丹波家族、成书背景、三十卷结构导读）
  - [x] SubTask 4.3: concepts 辑佚篇（02-lost-books：亡佚引书分类——房中养生/医方/服食，辑佚方法）
  - [x] SubTask 4.4: concepts 版本篇（03-editions-transmission：写本系统、安政本、回传中国史）
  - [x] SubTask 4.5: concepts 研究篇（04-research-lineage：日本考证学派、中国辑佚学利用、现代研究视角）
  - [x] SubTask 4.6: concepts 方法篇（05-choosing-editions：如何选读整理本与影印本）
- [x] Task 5: 撰写示例与信源文档（E 阶段·内容）
  - [x] SubTask 5.1: examples 辑佚文选读对照（01-close-reading：选取养生卷或房中卷公开辑佚文 2-3 段，白话解读 + 文献学注释）——3 段（养生大要/素女经两段）
  - [x] SubTask 5.2: examples 阅读计划（02-reading-plan：零基础分阶段入门路线）——四阶段
  - [x] SubTask 5.3: references 信源登记（写本刊本登记 / 现代整理本登记 / 研究文献登记 3 篇）
- [x] Task 6: 更新导航与交叉引用
  - [x] SubTask 6.1: 更新 `think/index.md`（分组表 + toctree + 域描述）与 `doc/bundles/index.md`（统计 292 束/36 组、think 域 11 束 6 组、medicine 锚点条目、两处 mermaid 节点）
  - [x] SubTask 6.2: 在 `sexology/classics-reading/concepts/01-ancient-china.md` 追加指向新包的延伸阅读交叉链接（仅追加一行，不改既有文字）
- [x] Task 7: 质量门验证与对抗审查（V 阶段）
  - [x] SubTask 7.1: `check-utf8.py` 退出码 0（5922 文件）；`check-toctrees.py` 全库退出码 0（medicine 范围零问题，sexology 包回归零新增断链）
  - [x] SubTask 7.2: 对照 checklist.md 逐项自查；对抗审查完成：修复 7 项（frontmatter 补齐 2 文件、.temp 相对路径改为包内/Web 锚点信源、《小品方》"永徽元年"疑误与森立之生卒年加【待核验】标注）；史实抽查 8 项全部与调研信源一致
  - [x] SubTask 7.3: 清理 `.temp/` 中间产物（3 份调研笔记已删除）
- [x] Task 8: 原子提交（C 阶段）
  - [x] SubTask 8.1: awesome-okf-xs 子模块原子提交 `2dd6b1ed`（20 文件 +1431 行：medicine 知识包 19 文件 + sexology 交叉引用 1 文件；共享导航 index 因混有并行会话（马王堆）登记变更按单职责排除，提交正文注明；UTF-8 stdin 字节流提交，`git cat-file -p` 验证无乱码）
  - [x] SubTask 8.2: 根仓库 gitlink 更新提交 `542476223`（16d6a5143→2dd6b1edd；因 gitlink 单 SHA 特性一并纳入并行会话的 b3916da3 pin，提交正文注明；仅暂存 gitlink 文件，未触碰其他并行任务 spec 文件）

# Task Dependencies

- Task 2 依赖 Task 1；Task 3 依赖 Task 2；Task 4、5 依赖 Task 3（骨架）；Task 4 与 Task 5 内部各篇可并行；Task 6 依赖 Task 3-5；Task 7 依赖 Task 6；Task 8 依赖 Task 7 通过。
- 可并行：SubTask 1.1 / 1.2 / 1.3；SubTask 4.1-4.6；SubTask 5.1-5.3。
