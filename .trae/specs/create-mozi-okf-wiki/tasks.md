# Tasks — 《墨子》OKF 知识包教程

方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C。
产出根目录：`projects/awesome-okf-xs/doc/bundles/think/mozi/mozi-reading/`
规范前置：实现前先读 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与 `.agents/global-core-rules.md`。

- [x] Task 1: R — 信源采集与事实登记（G1）
  - [x] 1.1 Web 核对原文：以孙诒让《墨子间诂》定本系统与 ctext.org《墨子》电子文本双源逐字核对《兼爱上》《非攻上》《公输》三篇全文，登记异文（ctext.org 因 CAPTCHA 未及，改用古诗文网/百科/汉典古籍网等 ≥3 独立信源逐字核对）
  - [x] 1.2 采集全书 53 篇篇目表：每篇标注分类归属（卷首杂论/十论/墨经六篇/言行录五篇/城守十一篇）与存亡状态（存/亡/阙）
  - [x] 1.3 采集"十论"上中下三篇结构与墨家三派（相里氏/相夫氏/邓陵氏，据《韩非子·显学》）文本差异
  - [x] 1.4 采集墨经六篇（经上/经下/经说上/经说下/大取/小取）逻辑与自然科学内容要旨
  - [x] 1.5 采集城守十一篇清单及"是否墨家著述"争议依据
  - [x] 1.6 采集注家谱系：毕沅《墨子注》、孙诒让《墨子间诂》、梁启超《墨子学案》/《墨经校释》、吴毓江《墨子校注》、高亨《墨经校诠》、谭戒甫《墨辩发微》及现代译注本（王焕镳/李小龙/方勇/孙波等）
  - [x] 1.7 产出 `.trae/specs/create-mozi-okf-wiki/facts.md`：60 条编号事实，纯客观描述（禁因果词），每条带信源 URL
- [x] Task 2: I — 洞察提炼（G2），依赖 Task 1
  - [x] 2.1 产出 `.trae/specs/create-mozi-okf-wiki/insights.md`：≥3 条四元组洞察（现象+根因+影响+建议），重点覆盖"文本分层/托名层"与"上中下三篇差异→墨离为三"
- [x] Task 3: E — 模式萃取（G3），依赖 Task 2
  - [x] 3.1 萃取 ≥2 个可复用阅读模式（如"双源逐字核读法""托名/分层文本三层判读框架"），各含触发场景/核心步骤/反模式/迁移示例，落入 examples 或 concepts 对应章节
- [x] Task 4: 创建 bundle 骨架与索引，依赖 Task 1
  - [x] 4.1 新建 `bundles/think/mozi/index.md`（分组 index + toctree）
  - [x] 4.2 新建 `bundles/think/mozi/mozi-reading/index.md`（bundle 根：导航/定位/快速开始/学习路径 + toctree）
  - [x] 4.3 建立 `concepts/`、`examples/`、`references/` 目录与各自 index.md（含 toctree）
  - [x] 4.4 更新 `bundles/think/index.md`（分组表行 + toctree）与 `bundles/index.md`（统计数字、think 域行、描述句、mermaid 节点）
- [x] Task 5: 生成 concepts/ 9 篇核心概念，依赖 Task 1/2/3（各篇可并行）
  - [x] 5.1 00-who-is-mozi：墨子其人（生平、与儒之辩、工匠出身、止楚攻宋）
  - [x] 5.2 01-text-versions：《墨子》版本源流与注本谱系（道藏本→毕沅→孙诒让）
  - [x] 5.3 02-structure-53-chapters：全书 53 篇结构与分类（篇目表全覆盖 + 一句话提要 + 存亡标注）
  - [x] 5.4 03-ten-doctrines：十论核心概念（兼爱/非攻/尚贤/尚同/天志/明鬼/非命/非乐/节用/节葬）与上中下三篇差异
  - [x] 5.5 04-mohist-canons：墨经逻辑与科学（名实/类故/光学/力学/几何）
  - [x] 5.6 05-defensive-warfare：城守十一篇军事防御技术及归属争议
  - [x] 5.7 06-anecdotes：墨子言行录（耕柱/贵义/公孟/鲁问/公输）
  - [x] 5.8 07-school-rise-fall：墨学兴衰与"墨离为三"（相里氏/相夫氏/邓陵氏）
  - [x] 5.9 08-commentaries：历代注家与注本立场标注
- [x] Task 6: 生成 examples/ 4 篇实操，依赖 Task 1/5
  - [x] 6.1 01-jian-ai-shang：《兼爱上》原文全录 + 逐字双源核对 + 解读
  - [x] 6.2 02-fei-gong-shang：《非攻上》原文全录 + 逐字双源核对 + 解读
  - [x] 6.3 03-gong-shu：《公输》原文全录 + 逐字双源核对 + 解读
  - [x] 6.4 04-ten-doctrines-reading-plan：十论"上"篇通读计划（含注本选用）
- [x] Task 7: 生成 references/ 3 篇信源登记，依赖 Task 1（可与 Task 5 并行）
  - [x] 7.1 core-texts.md：权威底本清单（道藏本/《墨子间诂》定本/ctext.org + 信源 URL）
  - [x] 7.2 commentaries.md：注本分级表（入门/进阶/研究级）
  - [x] 7.3 cross-ref.md：关联 think 域 laozi/psi bundle 与外部资源
- [x] Task 8: V — 对抗审查，依赖 Task 5/6/7
  - [x] 8.1 原文抽查：随机抽取三篇原文 10 处对照双信源逐字复核
  - [x] 8.2 事实抽查：随机抽取 facts.md 10 条核对信源 URL，杜绝虚构引证
  - [x] 8.3 分层诚实性审查：十论三篇差异、墨经后学、城守争议均明确标注，未作墨子本人手笔史实陈述
- [x] Task 9: C — 质量门与原子提交，依赖 Task 8
  - [x] 9.1 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`，修复 toctrees/utf8 问题直至通过
  - [x] 9.2 用 atomic-commit-cmd 在子模块仓库内原子提交（`docs(bundles): 新增《墨子》知识包教程`），同步主仓 gitlink 变更（如适用）
- [x] Task 10: 扩展十论通读计划至现存 23 篇（增量，依赖 Task 1/6.4）
  - [x] 10.1 重写 `examples/04-ten-doctrines-reading-plan.md`：由「上篇 8 篇」扩展为「十论现存 23 篇」完整通读路径（23 篇篇目总表 + 四阶段阅读顺序：兼爱非攻→尚贤尚同→节用节葬非乐→天志明鬼非命 + 亡佚 7 篇提示 + 墨离为三文本分层提示）
  - [x] 10.2 全文所据篇目/存佚/主张均回溯 facts.md F-030~F-046，未补造事实；明确标注「通读向导非逐字总录」边界
  - [x] 10.3 原子提交至子模块，同步主仓 gitlink（如适用）

# Task Dependencies

- Task 2/3 依赖 Task 1（事实先行）
- Task 4 依赖 Task 1；Task 5/7 依赖 Task 1/2/3；Task 6 依赖 Task 1/5
- Task 5 与 Task 7 可并行；Task 5 内部各篇可并行
- Task 8 依赖 Task 5/6/7 全部完成；Task 9 依赖 Task 8