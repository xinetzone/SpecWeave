# 孔子相关著作 OKF 知识包 - 实施计划

> 方法论链路：seven-concepts 场景4（知识沉淀）R→I→E→V→C
> 产出位置：`projects/awesome-okf-xs/doc/bundles/think/confucius/works/`（子模块内）

## Task 1: R 阶段 - 事实采集与双信源核对（G1 质量门）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 采集孔子相关著作公共领域事实清单（≥30 条），编号 F-001 起
  - 覆盖：孔子生平与「述而不作」出处（《论语·述而》）；六经次序（今古文经）；《春秋》亲作说与现代辨伪；《诗经》"删诗"说存疑；《尚书》今古文与清华简；《礼》与《乐》正乐/亡佚；《易》韦编三绝与《易传》十翼归属；《论语》成书（弟子辑录、张侯论、郑玄注）；出土文献（定州汉简《论语》、郭店/上博/清华简）；权威注本（阮元、杨伯峻、高亨、程俊英、程树德）
  - 每条事实登记信源 URL/出处，关键原文经至少两个独立信源逐字核对
- **Verification**: G1——事实≥30 条、无因果词、可追溯
- **产出物**: facts.md（写入 bundle 的 facts.md 基础）

## Task 2: I 阶段 - 核心洞察（G2 质量门）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 提炼 ≥3 条洞察，每条含完整四元组（陈述/证据F编号/反常识/行动）
  - 方向：①「述而不作」非谦虚而是史实，孔子对六经是"传承整理"非"原创著作"；②《论语》作为最直接信源却非孔子手写，读孔子须区分"其言"与"其行被记录"；③今古文经与出土文献证明传世文本经历多次层累，读经典须有版本批判思维
- **Verification**: G2——洞察≥3 条、四元组完整、有反常识性
- **产出物**: insights.md

## Task 3: E 阶段 - 可复用阅读模式萃取（G3 质量门）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 萃取 ≥2 个可迁移模式：①「归属辨析法」（先辨亲作/整理/辑录/存疑，再读其义）；②「经典版本对照阅读法」（多底本并读→差异定位→差异归因）；③「双信源核验法」（引用原文必双源逐字核对）
  - 每个模式含：触发场景（适用于/不适用于）、核心步骤 3-7 步、≥3 反模式、跨场景迁移示例
- **Verification**: G3——模式结构完整、反模式≥3、有迁移示例
- **产出物**: 写入 references/ 与 examples/ 相关章节

## Task 4: 创建分组与 bundle 骨架
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `think/confucius/index.md`（分组索引：孔子分组简介 + 知识包列表 + toctree）
  - 创建 `think/confucius/works/index.md`（bundle 根：定位 + 归属矩阵 + 学习路径 + toctree 引用全部内容文档）
  - 创建子目录 `concepts/`、`examples/`、`references/` 及各 index.md
- **Verification**: 目录结构完整、toctree 无断链

## Task 5: 生成 concepts 核心概念篇
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 01-述而不作：孔子与六经的关系总纲
  - 02-春秋：亲作、笔削义例、三传注疏
  - 03-诗经：删诗说、风雅颂、注本
  - 04-尚书：今古文、清华简、要义
  - 05-礼与乐：仪礼、正乐、乐亡佚
  - 06-周易与易传：韦编三绝、十翼归属存疑
  - 07-论语：成书、张侯论、郑玄注、定州汉简
  - 08-版本源流：六经次序、今古文经、出土文献
  - 09-归属矩阵与辨伪：宋以来辨伪史（欧阳修《易童子问》等）
- **Verification**: 各篇含选录原文（双源核对）+权威解读+sources 字段
- **产出物**: concepts/ 9 篇

## Task 6: 生成 examples 精读示例篇
- **Priority**: medium
- **Depends On**: Task 3, Task 5
- **Description**:
  - 01-春秋笔法精读（如「郑伯克段于鄢」三传对照）
  - 02-论语选读（学而/为政/述而 代表章句逐句解读）
  - 03-诗书选读（诗经代表性篇目 + 尚书代表性篇章）
- **Verification**: 精读示例可操作、含今译与注家出处

## Task 7: 生成 references 信源登记篇
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 01-权威底本（阮元十三经注疏、中华书局点校本、ctext.org）
  - 02-注本分级（一阶注疏/二阶现代注译/三阶普及读本）
  - 03-信源登记与交叉引用（与 laozi/huangdi 及 SpecWeave 主仓 laozi-lineage 互链）
- **Verification**: 底本/注本真实、URL 有效

## Task 8: 生成 facts.md / insights.md / log.md
- **Priority**: medium
- **Depends On**: Task 1, Task 2
- **Description**: 将 R 事实清单写为 facts.md、I 洞察写为 insights.md、log.md 记录变更历史
- **Verification**: G1/G2 复核通过

## Task 9: 更新导航索引
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 更新 `think/index.md`（新增 confucius 分组行 + toctree）
  - 更新 `bundles/index.md`（frontmatter 统计数字 total_bundles/groups、think 域描述、十三域分组导航表新增行）
- **Verification**: 导航可点击、统计数字一致

## Task 10: V 阶段 - 对抗审查（V 质量门）
- **Priority**: high
- **Depends On**: Task 4-9
- **Description**:
  - 4 视角对抗审查（魔鬼代言人/新人/老板/未来）
  - 重点：归属陈述是否夸大（易传/春秋辨伪）、选录原文逐字正确性、注家出处真实、断链、新人可读性
  - 采纳 ≥2 条意见修正产出
- **Verification**: V 门——审查意见≥5 条、采纳≥2 条修正

## Task 11: C 阶段 - 质量门与原子提交（G4 质量门）
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 在子模块内运行 `invoke gates.all`（UTF-8 + toctree 完整性）
  - 三查暂存法确认变更文件清单
  - Conventional Commits 原子提交（子模块仓库内）
- **Verification**: G4——单一职责、质量门通过、提交信息符合规范

# Task Dependencies

- Task 2 依赖 Task 1（洞察基于事实）
- Task 3 依赖 Task 2（模式萃取基于洞察）
- Task 4 依赖 Task 1
- Task 5 依赖 Task 1、Task 2
- Task 6 依赖 Task 3、Task 5
- Task 7 依赖 Task 1
- Task 8 依赖 Task 1、Task 2
- Task 9 依赖 Task 4
- Task 10 依赖 Task 4-9
- Task 11 依赖 Task 10
- **可并行**：Task 4/7 在 Task 1 完成后可并行；Task 5 各篇在 Task 1/2 完成后可并行