# Tasks — 《黄帝阴符经》OKF 知识包教程

方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C。
产出根目录：`projects/awesome-okf-xs/doc/bundles/think/huangdi/yinfujing/`
规范前置：实现前先读 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与 `.agents/global-core-rules.md`。

- [x] Task 1: R — 信源采集与事实登记（G1）
  - [x] 1.1 Web 核对原文：以正统道藏本/《中华道藏》整理本与 ctext.org《陰符經》双源逐字核对四百余字三章本全文，登记三百字本差异
  - [x] 1.2 采集成书年代学说与依据（寇谦之说、李筌自著说、北朝末期说、王明《〈阴符经〉考》、朱熹《阴符经考异》论断）
  - [x] 1.3 采集注家谱系（六家注、朱熹、俞琰、夏元鼎、现代注本萧登福/任法融等）与现代研究文献
  - [x] 1.4 产出 `.trae/specs/create-yinfujing-okf-wiki/facts.md`：≥30 条编号事实，纯客观描述（禁因果词），每条带信源 URL
- [x] Task 2: I — 洞察提炼（G2），依赖 Task 1
  - [x] 2.1 产出 `.trae/specs/create-yinfujing-okf-wiki/insights.md`：≥3 条四元组洞察（现象+根因+影响+建议），重点覆盖"托名层/文本层之分"与"丹道/兵机双线解读"
- [x] Task 3: E — 模式萃取（G3），依赖 Task 2
  - [x] 3.1 萃取 ≥2 个可复用阅读模式（如"双源逐字核读法""托名文本三层判读框架"），各含触发场景/核心步骤/反模式/迁移示例，落入 examples 或 concepts 对应章节
- [x] Task 4: 创建 bundle 骨架与索引，依赖 Task 1
  - [x] 4.1 新建 `bundles/think/huangdi/index.md`（分组 index + toctree）
  - [x] 4.2 新建 `bundles/think/huangdi/yinfujing/index.md`（bundle 根：导航/定位/快速开始/学习路径 + toctree）
  - [x] 4.3 建立 `concepts/`、`examples/`、`references/` 目录与各自 index.md（含 toctree）
  - [x] 4.4 更新 `bundles/think/index.md`（分组表行 + toctree）与 `bundles/index.md`（统计数字、think 域行、描述句）
- [x] Task 5: 生成 concepts/ 7 篇核心概念，依赖 Task 1/2/3（各篇可并行）
  - [x] 5.1 00-what-is-yinfujing：定位、书名含义、与道德经互补关系
  - [x] 5.2 01-text-versions：四百余字本/三百字本源流与差异
  - [x] 5.3 02-authorship-debate：成书与作者之争（托名层/文本层区分）
  - [x] 5.4 03-full-text：原文全录与上中下三章分段（逐字双源核对稿）
  - [x] 5.5 04-core-concepts：核心概念解读（观天之道/五贼/三才相盗/生克/食其时）
  - [x] 5.6 05-commentaries：历代注家与立场标注（六家注→宋→现代）
  - [x] 5.7 06-vs-daodejing：阴符经与道德经异同互补
- [x] Task 6: 生成 examples/ 2 篇实操，依赖 Task 5
  - [x] 6.1 01-shangpian-reading：上篇逐句精读（多立场对照）
  - [x] 6.2 02-seven-day-plan：七日通读计划（含注本选用）
- [x] Task 7: 生成 references/ 3 篇信源登记，依赖 Task 1（可与 Task 5 并行）
  - [x] 7.1 core-texts.md：权威底本清单（道藏本/中华道藏/ctext/四库本 + 信源 URL）
  - [x] 7.2 commentaries.md：注本分级表（入门/进阶/研究级）
  - [x] 7.3 cross-ref.md：关联 laozi 系 bundle（boshu-reading、主仓 laozi-lineage）与外部资源
- [x] Task 8: V — 对抗审查，依赖 Task 5/6/7
  - [x] 8.1 原文抽查：随机抽取原文 10 处对照双信源逐字复核
  - [x] 8.2 事实抽查：随机抽取 facts.md 10 条核对信源 URL，杜绝虚构引证
  - [x] 8.3 立场标注审查：核心句解读均 ≥2 注家立场且出处可溯
- [x] Task 9: C — 质量门与原子提交，依赖 Task 8
  - [x] 9.1 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`，修复 toctrees/utf8 问题直至通过（范围化验证通过；全局 gate 余留问题均属其他并行会话未完成 bundle，不属本任务范围）
  - [x] 9.2 用 atomic-commit-cmd 在子模块仓库内原子提交（`docs(bundles): 新增黄帝阴符经知识包教程`），同步主仓 gitlink 变更（如适用）——子模块提交 `195fc2b5` 完成（19 文件/1592 行）；主仓 gitlink 同步经用户确认跳过，指针变更保留在工作区

# Task Dependencies

- Task 2/3 依赖 Task 1（事实先行）
- Task 4 依赖 Task 1；Task 5/7 依赖 Task 1/2/3；Task 6 依赖 Task 5
- Task 5 与 Task 7 可并行
- Task 8 依赖 Task 5/6/7 全部完成；Task 9 依赖 Task 8
