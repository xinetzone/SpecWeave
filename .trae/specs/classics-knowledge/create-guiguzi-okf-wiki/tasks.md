# Tasks — 《鬼谷子》OKF 知识包教程

方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C。
产出根目录：`projects/awesome-okf-xs/doc/bundles/think/guiguzi/guiguzi/`
规范前置：实现前先读 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与 `.agents/global-core-rules.md`。

- [x] Task 1: R — 信源采集与事实登记（G1）
  - [x] 1.1 Web 核对原文：以正统道藏陶弘景注本、ctext.org《鬼谷子》、维基文库《鬼谷子》双源逐字核对现存篇目全文（十二篇 + 本经阴符七术 + 中经 + 持枢残篇），登记关键异文
  - [x] 1.2 采集中书志著录源流（《史记》苏秦/张仪列传鬼谷先生记载、《汉书·艺文志》未著录、《隋书·经籍志》三卷皇甫谧注、《新唐书·艺文志》乐壹/尹知章注、道藏本流变）
  - [x] 1.3 采集作者与成书年代学说及依据（苏秦托名说、后人伪托说、旧本流传说；钱穆、余嘉锡等考证）
  - [x] 1.4 采集注家谱系（皇甫谧、陶弘景、尹知章、乐壹；现代许富宏《鬼谷子集校集注》、陈蒲清《鬼谷子详解》等）与现代研究文献
  - [x] 1.5 产出 `.trae/specs/classics-knowledge/create-guiguzi-okf-wiki/facts.md`：≥30 条编号事实（实际 42 条），纯客观描述（禁因果词），每条带信源 URL
- [x] Task 2: I — 洞察提炼（G2），依赖 Task 1
  - [x] 2.1 产出 `.trae/specs/classics-knowledge/create-guiguzi-okf-wiki/insights.md`：4 条四元组洞察（现象+根因+影响+建议），覆盖"托名层/文本层之分"与"纵横术与兵家/道家关系"
- [x] Task 3: E — 模式萃取（G3），依赖 Task 2
  - [x] 3.1 萃取 2 个可复用阅读模式（"双源逐字核读法""托名文本三层判读框架"），各含触发场景/核心步骤/反模式/迁移示例，落入 insights.md
- [x] Task 4: 创建 bundle 骨架与索引，依赖 Task 1
  - [x] 4.1 新建 `bundles/think/guiguzi/index.md`（分组 index + toctree）
  - [x] 4.2 新建 `bundles/think/guiguzi/guiguzi/index.md`（bundle 根：导航/定位/快速开始/学习路径 + toctree）
  - [x] 4.3 建立 `concepts/`、`examples/`、`references/` 目录与各自 index.md（含 toctree）
  - [x] 4.4 更新 `bundles/think/index.md`（分组表行 + toctree）与 `bundles/index.md`（`total_bundles`/`groups` 统计、think 域描述与分组表行）
- [x] Task 5: 生成 concepts/ 7 篇核心概念，依赖 Task 1/2/3（各篇可并行）
  - [x] 5.1 00-what-is-guiguzi：定位、「鬼谷子」其人、「鬼谷」地望与书名含义
  - [x] 5.2 01-text-transmission：版本源流（书志著录隋书/新唐书、道藏本卷次、传世本流变）
  - [x] 5.3 02-authorship-debate：作者与成书之争（托名层/文本层区分）
  - [x] 5.4 03-full-text：原文全录与现存篇目分段 + 亡佚篇目存目（逐字双源核对稿）
  - [x] 5.5 04-core-concepts：核心概念解读（捭阖/反应/内揵/抵巇/飞箝/忤合/揣摩权谋决/符言）
  - [x] 5.6 05-commentaries：历代注家与立场（皇甫谧→陶弘景→尹知章/乐壹→现代）
  - [x] 5.7 06-influence：鬼谷子与纵横家/兵家/道家关系及历史影响（苏秦张仪、《战国纵横家书》互证、本经阴符七术与阴符经）
- [x] Task 6: 生成 examples/ 2 篇实操，依赖 Task 5
  - [x] 6.1 01-baihe-reading：捭阖篇逐句精读（多注家立场对照）
  - [x] 6.2 02-reading-plan：通读计划（含注本选用、篇目顺序建议）
- [x] Task 7: 生成 references/ 3 篇信源登记，依赖 Task 1（可与 Task 5 并行）
  - [x] 7.1 core-texts.md：权威底本清单（道藏本/ctext/维基文库/四库本/集校集注 + 信源 URL）
  - [x] 7.2 commentaries.md：注本分级表（入门/进阶/研究级）
  - [x] 7.3 cross-ref.md：关联 laozi 系 bundle（boshu-reading）、阴符经相关（待考标注）、ctext/维基文库/马王堆纵横家书等外部资源
- [x] Task 8: V — 对抗审查，依赖 Task 5/6/7
  - [x] 8.1 原文抽查：对照 ctext.org 正统道藏/四部丛刊本逐字复核捭阖/反應/抵巇等篇原文（≥7 处关键段落）
  - [x] 8.2 事实抽查：facts.md 22-42 条核对 ctext.org 信源，杜绝虚构引证
  - [x] 8.3 立场标注审查：托名/史实分层无混淆；无据注家评语均已标注"待考"，未虚构
- [x] Task 9: C — 质量门与原子提交，依赖 Task 8
  - [x] 9.1 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`（utf8 + toctrees）：guiguzi bundle 0 错误；整体 29 处失败均来自其它在建 bundle（buddhism/confucian/yinyangjia），非本 bundle 原因
  - [ ] 9.2 用 atomic-commit-cmd 在子模块仓库内原子提交（`docs(bundles): 新增鬼谷子知识包教程`）——待用户确认后执行（工作区存在多 agent 并行提交，需谨慎界定提交范围）

# Task Dependencies

- Task 2/3 依赖 Task 1（事实先行）
- Task 4 依赖 Task 1；Task 5/7 依赖 Task 1/2/3；Task 6 依赖 Task 5
- Task 5 与 Task 7 可并行
- Task 8 依赖 Task 5/6/7 全部完成；Task 9 依赖 Task 8