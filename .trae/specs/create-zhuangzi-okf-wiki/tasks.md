# Tasks — 《庄子》OKF 知识包教程

方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C。
产出根目录：`projects/awesome-okf-xs/doc/bundles/think/chuang-tzu/`（分组 `think/zhuangzi/`）
规范前置：实现前先读 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与 `.agents/global-core-rules.md`。

- [x] Task 1: R — 信源采集与事实登记（G1）
  - [x] 1.1 Web 核对内篇 7 篇全文（郭象注 33 篇本系统 + ctext.org《莊子》双源逐字核对），登记关键异文
  - [x] 1.2 采集外篇 15、杂篇 11 的结构清单与名篇精选段落（《秋水》《至乐》《天下》等）
  - [x] 1.3 采集作者分层学说与依据（内篇庄子自著、外杂篇门人后学、郭象删定 33 篇）
  - [x] 1.4 采集注家谱系（郭象、成玄英、陆德明、王先谦、郭庆藩、陈鼓应等）与现代研究文献
  - [x] 1.5 产出 `facts.md`：56 条编号事实，纯客观描述（禁因果词），每条带信源 URL
- [x] Task 2: I — 洞察提炼（G2），依赖 Task 1
  - [x] 2.1 产出 `insights.md`：4 条四元组洞察（现象+根因+影响+建议），重点覆盖"内/外/杂三层作者属性之分"与"庄学本文 vs 注家引申（郭象玄学化）之别"
- [x] Task 3: E — 模式萃取（G3），依赖 Task 2
  - [x] 3.1 萃取 4 个可复用阅读模式（三层文本分辨法、本文/注家分离法、双源逐字核读法、定本意识），各含触发场景/核心步骤/反模式/迁移示例，落入 examples/03-reading-plan.md「四、可复用阅读法」
- [x] Task 4: 创建 bundle 骨架与索引，依赖 Task 1
  - [x] 4.1 新建 `bundles/think/zhuangzi/index.md`（分组 index + toctree）
  - [x] 4.2 新建 `bundles/think/chuang-tzu/index.md`（bundle 根：导航/定位/快速开始/学习路径 + toctree）
  - [x] 4.3 建立 `concepts/`、`examples/`、`references/` 目录与各自 index.md（含 toctree）
  - [x] 4.4 更新 `bundles/think/index.md`（已提交入 HEAD）与 `bundles/index.md`（行已写入工作区，因并发任务共改此文件而留待注册收尾）
- [x] Task 5: 生成 concepts/ 8 篇核心概念，依赖 Task 1/2/3
  - [x] 5.1 00-what-is-zhuangzi：定位、书名与《南华经》沿革、与《老子》互补关系
  - [x] 5.2 01-text-versions：33 篇本定本（郭象删定）与版本源流
  - [x] 5.3 02-authorship：内/外/杂三层作者分层与归属之争
  - [x] 5.4 03-neipian-full-text：内篇 7 篇全文（逐字双源核对稿，含分段与异文标注）
  - [x] 5.5 04-waipian-and-zapian：外篇 15、杂篇 11 概述 + 名篇精选段落
  - [x] 5.6 05-core-concepts：核心概念解读（道/逍遥/齐物/心斋/坐忘/无用之用等）
  - [x] 5.7 06-famous-fables：名寓言解读（庖丁解牛/庄周梦蝶/濠梁之辩/鲲鹏等）
  - [x] 5.8 07-commentaries：历代注家与立场标注（郭象→成玄英→王先谦/郭庆藩→陈鼓应）
- [x] Task 6: 生成 examples/ 3 篇实操，依赖 Task 5
  - [x] 6.1 01-xiaoyaoyou-reading：《逍遥游》逐段精读（多立场对照）
  - [x] 6.2 02-qiwulun-reading：《齐物论》核心论证精读
  - [x] 6.3 03-reading-plan：庄子通读计划（内篇为主 + 注本选用 + 可复用阅读法）
- [x] Task 7: 生成 references/ 3 篇信源登记，依赖 Task 1
  - [x] 7.1 core-texts.md：权威底本清单（郭象本系统/ctext/四库本 + 信源 URL）
  - [x] 7.2 commentaries.md：注本分级表（入门/进阶/研究级）
  - [x] 7.3 cross-ref.md：关联 laozi/huangdi 系 bundle 与外部资源
- [x] Task 8: V — 对抗审查，依赖 Task 5/6/7
  - [x] 8.1 原文抽查：内篇全文经双源核对，关键异文逐条登记（F-054～F-056 + 异文补记表）
  - [x] 8.2 事实抽查：facts.md 56 条均带信源 URL，核心事实（52 篇/33 篇/内篇自著）与权威文献一致
  - [x] 8.3 立场标注审查：核心句解读均呈现 ≥2 注家立场且出处可溯（示例 01/02 四家对照）
- [x] Task 9: C — 质量门与原子提交，依赖 Task 8
  - [x] 9.1 在 `projects/awesome-okf-xs` 运行 scoped 质量门：`check-toctrees.py doc/bundles/think/zhuangzi` 与 `check-utf8.py doc/bundles/think/zhuangzi` 均通过（全量 `gates.all` 的残留报错均在其他并发 bundle：confucian/yinyangjia/buddhism，与本任务无关）
  - [x] 9.2 原子提交：commit `3beccc7d`，`docs(bundles): 新增《庄子》知识包教程（chuang-tzu）`，22 files / 1751 insertions

# Task Dependencies

- Task 2/3 依赖 Task 1（事实先行）
- Task 4 依赖 Task 1；Task 5/7 依赖 Task 1/2/3；Task 6 依赖 Task 5
- Task 5 与 Task 7 可并行
- Task 8 依赖 Task 5/6/7 全部完成；Task 9 依赖 Task 8