---
name: relationships-classics-okf-wiki-spec
version: 1.0.0
created: 2026-08-30
source: "六本公开出版的两性关系经典著作（受版权保护）→ 公开权威信源调研 + 原创中文转述解读"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V 链路
content-sensitivity: Public（公开出版物的书目信息与学术性解读）
---

# 两性关系经典著作 OKF Wiki 教程 — 产品需求文档

## Overview

- **Summary**：在 `projects/awesome-okf-xs/doc/bundles/think/` 下新建 `relationships/` 分组，为 6 本两性关系经典著作各生成一个符合 OKF v0.2 规范的知识包（bundle），每个知识包包含 concepts（概念解读）/examples（实践指引）/references（信源参考）三层结构，外加 facts.md（事实登记）与 insights.md（洞察与知识地图）。
- **Purpose**：将两性关系领域最具代表性的经典著作系统化、中文化为可导航、可核验、可实践的开源知识教程，填补 awesome-okf-xs 思想域（think/）在"亲密关系/情感"主题上的空白；与 psi（理论体系）、laozi（古典思想）构成"理论—古典—生活"的思想谱系。
- **Target Users**：希望系统理解亲密关系与婚恋情感的中文读者；OKF 知识包消费者（人类学习者与 AI 智能体）。

## Goals

- 以七概念方法论（R 事实采集 → I 洞察框架 → E 萃取生成 → V 对抗审查）完成 6 本著作的调研、解读与知识包生成。
- 每个知识包事实可溯源：书目元数据（作者、原版出版年、出版社、ISBN、章节结构）与核心理论陈述均基于公开权威信源核验。
- 内容以**原创中文转述与解读**为主体，直接引用限于合理使用范围的短句并标注出处，符合著作权法与开源发布要求。
- 全量通过 awesome-okf-xs 的质量门（`invoke gates.all`）与 Sphinx 构建（`invoke build`），索引体系完整更新。

## Non-Goals

- 不提供个性化情感/婚恋咨询建议，不对具体个人关系做价值判断；保持学术客观立场。
- 不收录 6 本之外的著作（分组结构预留扩展位，后续可追加）。
- 不提供电子书下载、盗版资源或任何侵权原文复制。
- 不修改 bundles 中既有知识包内容（仅对 `think/index.md` 与 `bundles/index.md` 做索引追加与统计更新）。
- 不主动执行 git commit（变更留在工作区，最终报告给出原子提交建议，由用户决定）。

## Background & Context

- **目标位置勘察结论**：bundles 现有 13 个技术域；`think/`（思想与理论）域含 `psi/`（4 束）与 `laozi/`（1 束）两个分组，是本主题的恰当归属。范式参照 `think/laozi/boshu-reading/`（7 concepts + 3 examples + 4 references + facts.md + insights.md + index.md + log.md）。
- **组织粒度（已与用户确认）**：每书一束——`think/relationships/<book-slug>/`，relationships 为 group，每本书为独立 bundle。
- **书目范围（已与用户确认：经典通识 6 本）**：

  | # | 中文常用名 | 原版书名 | 作者 | 拟定 bundle slug |
  |---|---|---|---|---|
  | 1 | 《亲密关系》 | Intimate Relationships | Rowland S. Miller | `intimate-relationships` |
  | 2 | 《爱的艺术》 | The Art of Loving | Erich Fromm | `art-of-loving` |
  | 3 | 《幸福的婚姻》 | The Seven Principles for Making Marriage Work | John M. Gottman & Nan Silver | `gottman-seven-principles` |
  | 4 | 《爱的五种语言》 | The 5 Love Languages | Gary Chapman | `five-love-languages` |
  | 5 | 《依恋》 | Attached | Amir Levine & Rachel Heller | `attached` |
  | 6 | 《男人来自火星，女人来自金星》 | Men Are from Mars, Women Are from Venus | John Gray | `mars-venus` |

- **版权约束（已与用户确认：转述为主 + 合理短引）**：6 本均为受版权保护的现代著作（区别于《老子》等公共领域文本）。处理原则：
  - 核心观点用原创中文系统转述、解释与对比，不整段复制原文；
  - 直接引用限于关键概念词与短句（单处直引 ≤30 汉字，每 bundle 直引处数克制），标注书名与章节；
  - 书目事实与信源在 facts.md / references 中登记，指向正版出版信息与公开权威资料。
- **信源可得性约束**：无法访问付费书籍全文。事实信源限于公开可核验资料：出版社/作者官方页面、Wikipedia（英文版优先）、WorldCat、Google Books 目录、权威书评、中文正版图书条目（豆瓣读书/当当/京东书目页）、学术数据库公开摘要。无法经两个独立信源核验的事实不写入 facts.md（或标注 status: draft 并降级处理）。
- **OKF 规范要点**（源自 awesome-okf-xs/.agents）：每个非保留 .md 须含可解析 YAML frontmatter 与非空 `type`；bundle 根 index.md 可带 `okf_version: "0.2"`；含子目录的 index.md 须以 `{toctree}` 引用全部内容文档；文件名 kebab-case 纯英文（NN- 数字前缀允许）；正文中文；交叉引用用相对路径，禁止 `file:///`；外部来源须在 frontmatter 标注 `sources`。

## Functional Requirements

- **FR-1（分组与骨架）**：新建 `think/relationships/` 分组目录及 `index.md`（type: group，含分组导言、6 束导航表、toctree）；新建 6 个 bundle 目录骨架。
- **FR-2（事实层 facts.md）**：每个 bundle 含 facts.md，登记 30–50 条零推测事实（书目元数据、章节结构、核心理论与概念的客观陈述），每条事实带信源标识（脚注引用 sources[].id）；G1 质量门——事实陈述不含因果推断与主观评价词。
- **FR-3（概念层 concepts/）**：每个 bundle 含 5–6 篇概念文档，覆盖：著作背景与定位、核心理论框架、关键概念（2–3 篇）、实践方法论；每篇含 frontmatter（type/title/description/tags/sources）。
- **FR-4（实践层 examples/）**：每个 bundle 含 2 篇实践文档，如自评工具/自测题、典型场景应用、阅读与实践路径；内容为基于原书框架的**原创编排**，不冒充原书测试量表全文。
- **FR-5（信源层 references/）**：每个 bundle 含 2 篇信源文档：著作版本与出版信息（原版/中译本、ISBN 占位以核验结果为准）、延伸阅读与相关研究；仅收录正版与公开权威信源。
- **FR-6（洞察层 insights.md）**：每个 bundle 含 insights.md，含 3–5 条四元组洞察（现象/陈述 + 证据 + 反常识点 + 行动启示）；分组层面提供 6 书理论对比知识地图（Mermaid），书间建立交叉引用。
- **FR-7（索引与日志）**：每个 bundle 含 index.md（bundle 入口 + toctree）与 log.md（YYYY-MM-DD 更新记录）；更新 `think/index.md`（分组表 + toctree）与 `bundles/index.md`（think 域统计 5 束/2 组 → 11 束/3 组、总量 280 → 286、分组 32 → 33、导航表新增行、Mermaid 图 think 标签、toctree 不变）。
- **FR-8（溯源 frontmatter）**：bundle 根 index.md 与各内容文档 frontmatter 携带 `sources`（id/resource/title/author），`generated.by` 使用 `reference_agent/<model>` 约定。

## Non-Functional Requirements

- **NFR-1（事实准确性）**：书目元数据与核心理论名称（如戈特曼"末日四骑士/Four Horsemen"、查普曼"五种爱语"、依恋三类型"安全/焦虑/回避"、斯滕伯格爱情三元论作为背景对照等）须与权威信源一致，P0 事实（书名、作者、原版年、核心理论归属）须两个独立信源交叉核验。
- **NFR-2（版权合规）**：无整段原文复制；单处直引 ≤30 汉字且标注出处；无盗版/电子书资源链接。
- **NFR-3（构建合规）**：`invoke gates.all`（UTF-8 + toctree）通过；`invoke clean && invoke build` 零错误且不新增警告（基线：当前构建 0 警告）。
- **NFR-4（规范一致性）**：文件名 kebab-case 纯英文；所有路径引用为相对路径；frontmatter 日期按 OKF v0.2 裸写（conf.py 钩子自动处理）。
- **NFR-5（立场与表述）**：中文书面语，客观中立；对存在学术争议的著作（如 mars-venus 的性别差异论述、five-love-languages 的实证基础）须呈现学界评价与争议，不做无条件背书。

## Constraints

- **Technical**：Markdown + MyST（Sphinx 构建）；OKF v0.2 frontmatter；Windows 环境；Invoke 任务链（`invoke gates.all` / `invoke build`，工作目录 `projects/awesome-okf-xs`）。
- **Business/Legal**：著作权法合理使用边界；开源仓库公开发布；不得包含侵权内容。
- **Dependencies**：WebSearch/WebFetch 公开信源可达；awesome-okf-xs 子模块已初始化且当前构建为绿（记忆显示 2026-08-29 刚完成 0 警告修复）。
- **方法论**：seven-concepts-cmd 场景 4 链路 R→I→E，叠加 V 对抗审查（事实/版权/格式三视角）；G1（事实无因果词）、G2（洞察四元组）、G3（模式可迁移/框架可复用）质量门强制。

## Assumptions

- 用户认可 6 本书的中文书名以主流通行中译本名称为准（如《幸福的婚姻》《爱的五种语言》《依恋：为什么我们爱得如此不安？》等，具体以核验到的正版中译本信息为准）。
- 公开信源足以核验书目元数据与核心理论框架（这些均为长销经典，公开资料充分）。
- 每个 bundle 的内容规模参照 boshu-reading 范式（concepts 5–7 篇、examples 2–3 篇、references 2–4 篇）。

## Acceptance Criteria

### AC-1: 分组与 6 个 bundle 结构完整
- **Type**: `rule`
- **Given**: 任务完成后的 `doc/bundles/think/` 目录
- **When**: 检查 `relationships/` 分组及其下 6 个 bundle 目录
- **Then**: `relationships/index.md` 存在；6 个 bundle（intimate-relationships、art-of-loving、gottman-seven-principles、five-love-languages、attached、mars-venus）每个均含 `index.md`、`log.md`、`facts.md`、`insights.md` 及 `concepts/`、`examples/`、`references/` 三个子目录（各含 `index.md` 与规定数量内容文档：concepts 5–6 篇、examples 2 篇、references 2 篇）
- **Pass Condition**: 目录树逐一核对全部存在，文档数量达标
- **Evidence**: 目录列表 + 文件计数

### AC-2: frontmatter 与 OKF v0.2 合规
- **Type**: `rule`
- **Given**: 所有新增 .md 文件
- **When**: 解析每个非保留文件的 YAML frontmatter
- **Then**: 每个非 index/log 保留文件含非空 `type`；bundle 根 index.md 携带 `sources` 与 `okf_version: "0.2"`；内容文档含 sources 溯源；无 `file:///` 绝对路径链接
- **Pass Condition**: 逐文件检查（可用脚本扫描 frontmatter）全部通过
- **Evidence**: 扫描脚本输出/人工核对记录

### AC-3: toctree 与质量门通过
- **Type**: `rule`
- **Given**: 全部新增与修改的文档
- **When**: 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **Then**: UTF-8 检查与 toctree 完整性检查（无断链、无孤立文档、bundle 根 index 完整）全部通过
- **Pass Condition**: 命令退出码 0 且无错误输出
- **Evidence**: 命令输出日志

### AC-4: Sphinx 构建零错误零新增警告
- **Type**: `rule`
- **When**: 运行 `invoke clean && invoke build`
- **Then**: 构建成功，0 错误；警告数为 0（基线为 0）
- **Pass Condition**: 构建输出无 warning/error
- **Evidence**: 构建日志

### AC-5: 事实可溯源且 P0 事实经交叉核验
- **Type**: `rule`
- **Given**: 6 个 bundle 的 facts.md
- **When**: 抽查每本书至少 5 条事实（含作者、原版出版年、出版社、1 个核心理论名称）回溯信源
- **Then**: 每条事实在 references/sources 中有对应公开信源；P0 事实有两个独立信源支撑；facts.md 陈述无因果推断词（G1）
- **Pass Condition**: 30 条抽查事实全部可溯源，P0 事实双信源一致
- **Evidence**: 抽查记录表（信源 URL + 核验结论）

### AC-6: 版权合规
- **Type**: `rule`
- **Given**: 全部新增内容文档
- **When**: 扫描直接引用（引号块/直引句）
- **Then**: 无单处超过 30 汉字的未标注直引；所有直引均标注书名与章节；无整段原文复制；references 无盗版/电子书下载链接
- **Pass Condition**: 扫描与人工复核全部通过
- **Evidence**: 引用清单（位置 + 字数 + 出处）

### AC-7: 上层索引一致更新
- **Type**: `rule`
- **When**: 检查 `think/index.md` 与 `bundles/index.md`
- **Then**: think/index.md 分组表含 relationships 行且 toctree 含 `relationships/index`；bundles/index.md 的 think 域导航表新增 relationships 行、统计数字更新（束 280→286、组 32→33）、Mermaid think 节点标签包含 relationships、正文 think 域描述同步
- **Pass Condition**: 两处索引与实际目录结构一致
- **Evidence**: 文件 diff 核对

### AC-8: 内容准确性（观点归属无错误）
- **Type**: `rubric`
- **Dimension**: 核心理论、概念、引言与作者的归属正确性；无张冠李戴、无时代错置、无虚构书名/人物
- **Scale**: 1-5
- **Anchors**: 1 = 存在事实性硬错误（理论归错作者/书）；3 = 主要事实正确但有个别表述模糊；5 = 全部理论归属准确，争议点呈现公允
- **Pass Threshold**: >= 4
- **Evidence**: 独立评审逐 bundle 核对记录

### AC-9: 解读深度与实践可用性
- **Type**: `rubric`
- **Dimension**: concepts 不是目录搬运而是有概念澄清与理论脉络；examples 提供可操作的原创实践指引；insights 四元组完整（G2）
- **Scale**: 1-5
- **Anchors**: 1 = 仅书目信息罗列；3 = 有解读但停留在复述层面；5 = 解读有结构、有对比、有可落地实践
- **Pass Threshold**: >= 4
- **Evidence**: 独立评审抽样阅读

### AC-10: 知识地图与跨书联结
- **Type**: `rubric`
- **Dimension**: 分组导言与 insights 提供 6 书理论谱系对比（如学术实证—哲学经典—通俗实用三层定位、依恋理论 vs 爱语 vs 火星金星的互补/张力关系）；bundle 间存在有意义的交叉引用
- **Scale**: 1-5
- **Anchors**: 1 = 6 束相互孤立；3 = 有分组导言但跨书对比浅；5 = 对比地图清晰、交叉引用准确有洞见
- **Pass Threshold**: >= 4
- **Evidence**: relationships/index.md 与各 insights.md

## Open Questions

- 无（书目范围、组织粒度、原文处理方式三项关键边界已经用户确认；中译本具体版本信息以 R 阶段核验结果为准，不阻塞开工）。
