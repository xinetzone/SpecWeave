# 《帛书老子注读》Wiki 教程 - 实施计划

> 方法论链路：seven-concepts 场景4（知识沉淀）R→I→E→V→C
> 章节文件存放：`docs/knowledge/learning/boshu-laozi-wiki/`

## [x] Task 1: R 阶段 - 事实采集（G1 质量门）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 采集帛书老子公共领域事实清单（≥15 条），编号 F-001 起
  - 核心事实：1973 年马王堆三号汉墓出土；甲乙本抄写时代（甲本刘邦称帝前、乙本称帝后避"邦"讳）；德经在前道经在后；"大器免成"vs"大器晚成"；高明《帛书老子校注》以王弼本为主校本；秦复观《帛书老子注读》成书背景（东方出版社 2022-12）
  - 事实须客观、无因果推断词、可追溯到公开来源
- **Verification**: G1 检查——事实≥15 条、无因果词、可追溯
- **产出物**: 事实清单（写入各章节的事实引用基础 + `.trae/specs/classics-knowledge/boshu-laozi-wiki/` 下留档）

## [x] Task 2: I 阶段 - 核心洞察（G2 质量门）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 提炼 ≥3 条洞察，每条含完整四元组（陈述/证据F编号/反常识/行动）
  - 洞察方向：①帛书本并非"更正确"而是"更早"，二者是演进关系非优劣关系；②德经在前的结构差异暗示老子思想重心；③出土文献阅读需要"版本批判"思维，不能盲信任一传本
- **Verification**: G2 检查——洞察≥3 条、四元组完整、有反常识性
- **产出物**: 洞察内容映射到教程章节（03/04/05 章素材）

## [x] Task 3: E 阶段 - 可复用模式萃取（G3 质量门）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 萃取 ≥2 个可迁移模式：①"版本对照阅读法"（多版本并读→差异定位→差异归因）；②"出土文献认知框架"（近古必存真→版本批判→价值重估）
  - 每个模式含：触发场景（适用于/不适用于）、核心步骤 3-7 步、≥3 反模式、迁移示例
- **Verification**: G3 检查——模式结构完整、反模式≥3、有跨场景迁移示例
- **产出物**: 06 章"可复用模式"

## [x] Task 4: 生成 00-overview.md 总览章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 帛书老子是什么、为何重要、教程结构与学习目标
  - 说明资料来源（DRM 说明 + 公共领域方案）
  - 文档导航表
- **Verification**: 文件存在、定位清晰、导航完整

## [x] Task 5: 生成 01-background.md 历史背景与出土
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 马王堆三号汉墓发现史（1973 年）
  - 甲乙本抄写时代判定（避讳学证据）
  - 帛书老子的历史意义（近古必存真）
- **Verification**: 事实引用与公共共识一致

## [x] Task 6: 生成 02-version-comparison.md 版本体系对照
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 版本谱系：帛书甲乙本 → 王弼本 → 河上公本 → 竹简/郭店
  - 结构差异：德经在前 vs 道经在前
  - 文字差异精选：大器免成/晚成、邦/国、恒/常、弗/不 等
- **Verification**: 对照准确、含对比表格

## [x] Task 7: 生成 03-core-concepts.md 核心概念解读
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 道、德、无为、自然、反（返）、弱 等核心概念
  - 帛书用字差异带来的义理差异
  - 引用《德经》《道经》代表性原文（公共领域）
- **Verification**: 概念解读准确、原文引用无误

## [x] Task 8: 生成 04-reading-methodology.md 注读方法论
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 秦复观《帛书老子注读》的注读方法（底本选择→对照→断句修正→白话→逐句解读）
  - 高明校注的学术方法（校本体系）
  - 读者自主阅读帛书本的操作路径
- **Verification**: 方法论描述与公开介绍一致

## [x] Task 9: 生成 05-key-insights.md 核心洞察
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 3-5 条带四元组的核心洞察
  - 洞察与事实编号的映射表
- **Verification**: G2 质量门复核（每条四元组完整）

## [x] Task 10: 生成 06-patterns.md 可复用模式
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 模式1：版本对照阅读法
  - 模式2：出土文献认知框架
  - 每个模式含触发场景/核心步骤/反模式/迁移示例
- **Verification**: G3 质量门复核

## [x] Task 11: 生成 07-faq-resources.md FAQ 与资源
- **Priority**: low
- **Depends On**: Task 1
- **Description**:
  - 常见问题（帛书 vs 通行本哪个好？为何帛书是"注读"非"校注"？）
  - 推荐资源（高明校注、秦复观注读、公开文本）
  - 版权声明与来源说明
- **Verification**: FAQ 覆盖常见疑问、资源真实

## [x] Task 12: 生成 README.md 目录索引并更新导航
- **Priority**: high
- **Depends On**: Task 4-11
- **Description**:
  - 生成 README.md（含文档索引表）
  - 更新 `docs/knowledge/learning/README.md` 导航（标记区域由 docgen 处理）
  - 运行 generate-readme.py / docgen 校验索引
- **Verification**: 导航可点击、无断链

## [x] Task 13: V 阶段 - 对抗审查（V 质量门）
- **Priority**: high
- **Depends On**: Task 4-12
- **Description**:
  - 4 视角对抗审查（魔鬼代言人/新人/老板/未来）
  - 重点攻击：事实准确性、反常识洞见是否成立、模式可迁移性、断链
  - 采纳 ≥2 条意见修正产出
- **Verification**: V 门——审查意见≥5 条、采纳≥2 条修正

## [x] Task 14: C 阶段 - 原子提交入库（G4 质量门）
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 三查暂存法确认变更文件清单
  - 预提交验证：链接检查（link-check）、格式检查
  - Conventional Commits 原子提交（`docs(knowledge): 新增帛书老子注读 wiki 教程`）
- **Verification**: G4——单一职责、预提交验证通过、提交信息符合规范

# Task Dependencies

- Task 2 依赖 Task 1（洞察须基于事实）
- Task 3 依赖 Task 2（模式萃取须基于洞察）
- Task 4-11 依赖 Task 1-3 的素材
- Task 12 依赖 Task 4-11
- Task 13 依赖 Task 4-12
- Task 14 依赖 Task 13
- **可并行**：Task 4/5/6 在 Task 1 完成后可并行；Task 7/8/9 在 Task 2 后可并行；Task 10 在 Task 3 后可并行
