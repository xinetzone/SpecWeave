# Tasks

> 链路：seven-concepts 场景4（知识沉淀）R→I→E→V→C。所有产物位于 `projects/awesome-okf-xs/doc/bundles/think/yinyangjia/`（子模块内开发）。

- [x] Task 1: R 阶段——信源采集与事实登记（G1）
  - [x] SubTask 1.1: 采集书志源流信源：《汉书·艺文志》阴阳家著录全目（二十一家三百六十九篇逐家登记）、《史记·孟子荀卿列传》邹衍传、司马谈《论六家要旨》阴阳家评述（ctext.org + 维基文库双源）
  - [x] SubTask 1.2: 采集佚文信源：马国翰《玉函山房辑佚书》辑《邹子》《邹子终始》佚文（含原始引书出处，如《文选》李善注、《艺文类聚》《太平御览》所引），双源逐字核对并登记异文
  - [x] SubTask 1.3: 采集传世文献信源：《吕氏春秋·应同》、《管子·四时/五行/幼官》、《礼记·月令》、《淮南子·天文训》相关段落（双源核对，标注归属层级 A/B/C）
  - [x] SubTask 1.4: 采集解读谱系信源：古代评述（班固、司马谈）+ 现代研究（顾颉刚、梁启超、冯友兰、吕思勉等公开文献），登记每条的作者/文献/立场
  - [x] SubTask 1.5: 汇总为 `facts.md`：≥30 条编号事实（F-001 起），无因果推断词，每条含信源 URL；G1 自检通过后推进（实际 64 条事实 + 23 处异文 + 18 项未能核对项）
- [x] Task 2: I 阶段——跨源共性洞察（G2）
  - [x] SubTask 2.1: 基于 facts.md 提炼 ≥3 条洞察，每条含四元组（陈述/证据引用 F-xxx/反常识/行动）（实际 4 条）
  - [x] SubTask 2.2: 输出 `insights.md`，覆盖维度至少含：文本存佚结构（为何亡佚却影响巨大）、归属判定方法、解读立场差异
- [x] Task 3: E 阶段——可复用阅读模式萃取（G3）
  - [x] SubTask 3.1: 萃取 ≥2 个可复用阅读模式（候选：亡佚学派文本三层阅读法、辑佚文献溯源阅读法），每个含触发场景/核心步骤/≥3 反模式/检验标准/跨领域迁移示例
  - [x] SubTask 3.2: 模式文档含 YAML frontmatter，登记到 bundle 结构中
- [x] Task 4: V 阶段——对抗审查（强制）
  - [x] SubTask 4.1: 四视角审查（魔鬼代言人/新人/老板/未来）：重点抽查 10 条 facts.md 事实与信源一致性、A/B/C 三层标注是否被混用、佚文是否被夸大为"完整原文"（审查记录见本目录 review.md）
  - [x] SubTask 4.2: 审查意见 ≥5 条且具体，至少采纳 2 条修正产物，记录审查与修正过程（Q-01～Q-07，06-legacy.md 第五节含 Q-07 显式决策段）
- [x] Task 5: 生成 bundle 内容文档
  - [x] SubTask 5.1: 创建 `bundles/think/yinyangjia/yinyangjia/index.md`（bundle 根：定位 + 存佚总览 + 学习路径 + toctree）
  - [x] SubTask 5.2: 撰写 `concepts/` 7 篇：what-is-yinyangjia（学派定位与六家要旨评述）/ bibliography-and-survival（艺文志著录与亡佚考证）/ zou-yan（邹衍生平与学说）/ wude-zhongshi（五德终始说解读）/ surviving-texts（传世文献中的阴阳家材料）/ reconstruction-history（辑佚史与历代考据）/ legacy（影响与流变）
  - [x] SubTask 5.3: 撰写 `examples/` 2 篇：yingtong-reading（《吕氏春秋·应同》逐句精读）/ reading-plan（阴阳家文献通读计划）
  - [x] SubTask 5.4: 撰写 `references/` 3 篇：sources（权威底本与信源登记）/ scholarship（辑佚本与现代研究分级表）/ cross-ref（与 laozi、guiguzi 等束交叉引用）
  - [x] SubTask 5.5: 汇总 `facts.md`/`insights.md`/`log.md` 入束，所有文档带 OKF v0.2 frontmatter
- [x] Task 6: 索引更新
  - [x] SubTask 6.1: 更新 `think/index.md`：新增 yinyangjia 分组行 + toctree 条目 + 域描述
  - [x] SubTask 6.2: 更新 `bundles/index.md`：`total_bundles`/`groups` 数字（以仓库实际状态为基准 +1）、think 域「束/组」计数、mermaid 图 think 节点标注
- [x] Task 7: C 阶段——质量门与原子提交（G4）
  - [x] SubTask 7.1: 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`（UTF-8 + toctree），失败则修复后重跑（阴阳家知识包零告警； gates.all 整体失败项均来自并行会话在途目录 confucian/、buddhism/heart-sutra，不属本 spec 范围）
  - [x] SubTask 7.2: 子模块内原子提交（Conventional Commits，中文描述"为什么"，Windows UTF-8 方案防乱码）；如主仓 gitlink 变更需同步提交（子模块 cf70f93b：23 文件 +2163 行；主仓 a1b23c6a8 gitlink 同步）

# Task Dependencies

- Task 2 依赖 Task 1（洞察必须引用事实编号）
- Task 3 依赖 Task 2（先洞察再萃取）
- Task 5 依赖 Task 1–4（内容文档使用已核对事实与已审查结论）
- Task 6 依赖 Task 5（索引引用已存在的文档）
- Task 7 依赖 Task 5–6（提交包含全部产物）
- Task 4 依赖 Task 1–3（审查已有产出），可在 Task 5 撰写前完成抽查、Task 5 后对新文档补充复审
