# 《老子文化生态圈》OKF Wiki 教程 - 任务清单

> 方法论链路：seven-concepts 场景4（知识沉淀）R（事实采集）→ I（骨架与知识拆分）→ E（信源先行生成）→ V（对抗审查与门禁）→ C（原子提交，待用户指令）。
> 目标目录：`projects/awesome-okf-xs/doc/bundles/guoxue/laozi/laozi-culture-ecosystem/`

## [x] Task 1: R 阶段 - 事实采集与核验（G1 质量门）

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 采集事实清单 `facts.md`，编号 F-001 起，连续无跳号；事实须客观、无因果推断词（"因为/导致/所以"），可追溯到公开来源。
  - 双体系事实：①**帛书老子文本与学术**（马王堆甲乙本、德经在前道经在后、避讳断代、关键异文如「有静/不争」「大器免成/晚成」「弗/不」「恒/常」、核心章句原文）；②**市场机制与商业通识**（价格发现与信息入价、套利与一价定律、交易成本、信息不对称与信号、市场失灵、EMH 三形态与 AMH 要点，作为机制层引用）。
  - 建立 S 编号信源登记：老子文本与学术信源（高明校注、出土整理本、版本学著作）+ 市场机制信源（与 efficient-markets 的信源体系同口径，不重复登记已有来源）。
  - P0 核验：章序与异文用字、避讳断代结论、机制定义与提出者/年份，逐类对照，结论写入 `references/02-verification.md`。
  - 口径留痕与放弃核验清单：老子章序（81/79 章差异）、异文并列不混称、商业算例参数标「教学算例」；放弃核验项（真实平台费率、实时行情、个体机构数据）。
- **Verification**: G1 门——事实条目连续无跳号、无因果推断词、每条挂 S 编号、数字/制度类事实已 P0 核验。
- **产出物**: `facts.md` + `references/02-verification.md`（核验记录骨架）

## [x] Task 2: I 阶段 - 骨架判定与知识拆分（G2 质量门）

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 操作可复现性两问：①是否有可照做的计算流程？②是否有可复算的输入输出？两问皆「是」→ 设 `examples/`（算例轨）。
  - 三层知识拆分：总论（00 生态圈定义 / 01 帛书老子基线）→ 三条现金流机制（02 流量变现 / 03 渠道变现 / 04 利他现金流）→ 场域与边界（05 有效场域 / 06 多形态商业圈与闭环 / 07 效率边界与失灵 / 08 与 EMH 对话 / 09 治理合规）。
  - 每篇采用统一骨架：「是什么 → 机制 → 与老子思想的映射 → 算例/数字指路 → 常见误读 → 小结 → 事实卡」。
  - 提炼 ≥3 条四元组洞察（陈述/证据 F 编号/反常识/行动），写入 `insights.md`，维度互不重叠。
  - 萃取 ≥1 个可迁移模式（如「利他现金流飞轮」或「最小干预生态治理」），含触发场景、核心步骤、≥3 反模式、迁移示例。
- **Verification**: G2 门——洞察 ≥3 条且四元组完整、有反常识性；模式结构完整、反模式 ≥3、有跨场景迁移示例；理论轨与算例轨分工明确。
- **产出物**: 知识骨架图 + `insights.md`

## [x] Task 3: E 阶段 - 信源先行生成（G3 质量门）

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 先写 `facts.md`、`references/01-sources.md`、`references/02-verification.md`（信源先行）。
  - 再写 10 篇 `concepts/`（00–09），逐篇交叉引用 efficient-markets 对应概念页（相对路径）。
  - 再写 4 篇 `examples/`（算例轨），每个算例给出显式假设、逐步计算、结果与教学声明。
  - 最后写 `concepts/index.md`、`examples/index.md`、`references/index.md`、根 `index.md`、`log.md`。
  - frontmatter 完整：根 `type: OKF` + `okf_version: "0.2"` + `version` + `sources` + `generated` + `status` + `stale_after`；子文档 `type: Concept/Example/Reference/Facts/Insights` + `source`。
  - 全文具体声明引用 F 编号；观点与争议入 `insights.md` 或加限定语；帛书与通行本异文并列标注。
- **Verification**: G3 门——模式可迁移（触发 + 步骤 + 反模式 + 迁移验证齐备）；每篇要素完整；算例可复算。
- **产出物**: 23 个 Markdown 文档（7 根 + 10 concepts + 4 examples + 2 references，含 3 个 index）

## [x] Task 4: 索引导航与计数同步

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - `doc/bundles/guoxue/laozi/index.md`：知识包列表新增 `laozi-culture-ecosystem/` 行 + `{toctree}` 追加条目。
  - `doc/bundles/guoxue/index.md`：「老子」分组行简介增补「文化生态圈·现金流闭环」定位。
  - `doc/bundles/index.md`：`total_bundles` 694→695、guoxue 节标题 49→50 束、laozi 行束数 4→5 与简介、mermaid guoxue 节点「（49 束）」→「（50 束）」。
  - 同步 `doc/index.md` 与 `README.md` 中的库规模数字（三处一致，以 `invoke gates.assetbaseline` 口径为准）。
  - 不改动 efficient-markets 与老子分组既有 4 束的任何正文。
- **Verification**: `invoke gates.toctrees` 与 `invoke gates.bundles` 通过；`invoke gates.assetbaseline` 通过（规模数字三处一致）。
- **产出物**: 已更新的索引文件

## [x] Task 5: V 阶段 - 对抗审查（V 质量门）

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 4 视角对抗审查（魔鬼代言人 / 新人 / 老板 / 未来），写入 `review.md` 的 Review History。
  - 重点攻击：①「用老子思想论证商业机制」是否存在伪因果/穿凿附会；②帛书异文是否被误用（如把「有静」直接等同通行本「不争」）；③机制层对 efficient-markets 的引用是否失真、是否把假说写成定律；④算例假设是否自洽、是否隐含收益承诺；⑤合规边界是否完备。
  - 采纳 ≥2 条意见修正产出，并记录采纳项与未采纳理由。
- **Verification**: V 门——审查意见 ≥5 条、采纳 ≥2 条；伪因果检查与合规边界检查各有明确结论。
- **产出物**: `review.md` 审查记录 + 修正后的知识包

## [x] Task 6: 门禁与工程验证

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 运行 `invoke gates.all`（utf8 + toctrees + bundles + assetbaseline + redline）。
  - 逐文件 UTF-8 严格解码（无 BOM、无替换字符、无繁体混入）；无 `file:///`、无本机绝对路径；所有 Markdown 相对链接逐一检查零缺失。
  - 事实编号连续性校验与「全文引用 F 编号 ≤ 最大编号」校验；确认无 F 之外的硬数字。
  - 若环境缺 sphinx，则以两条仓库门禁 + 手动等效清单替代并在 `log.md` 注明。
- **Verification**: 全部门禁通过；链接零断链；编号连续。
- **产出物**: 门禁运行记录（写入 `log.md`）

## [x] Task 7: V 阶段 - 独立审查（全新上下文，只读）

- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 由全新上下文的审查者对照 `spec.md` 与本 spec 的验收标准，独立复核 `review.md` 全部检查点，给出 `pass` / `fail` / `blocked` 结论与证据。
  - `fail` 时每条可行动发现固化为本文件的 pending 修复 issue，回到实施；`blocked` 时记录阻塞并请求解决。
- **Verification**: 独立审查结论为 `pass`，每条 AC 有独立证据。
- **产出物**: `review.md` 独立审查记录

## [x] Task 8: C 阶段 - 原子提交（G4 质量门）

- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 三查暂存法确认变更文件清单（bundle 23 文档 + 4~5 处索引）。
  - 子模块 `projects/awesome-okf-xs` 提交（Conventional Commits：`docs(bundles): 新增老子文化生态圈 OKF 知识包`）。
  - 主仓库提交 spec 目录与子模块指针更新。
  - **不 push**；等待用户显式指令。
- **Verification**: G4 门——单一职责、预提交验证通过、提交信息符合规范。
- **产出物**: 两次原子提交（子模块 + 主仓库）

# Task Dependencies

- Task 2 依赖 Task 1（洞察须基于事实）
- Task 3 依赖 Task 2（信源先行生成须基于骨架）
- Task 4 依赖 Task 3（索引须引用已生成文档）
- Task 5 依赖 Task 4（审查对象为完整包 + 索引）
- Task 6 依赖 Task 5（门禁在修正后运行）
- Task 7 依赖 Task 6（独立审查在队列清空后）
- Task 8 依赖 Task 7（仅 Review 通过后交付）
- **可并行**：Task 3 中 `concepts/`（00–09）各篇在骨架确定后可并行撰写；`examples/` 4 篇在机制章定稿后可并行；Task 4 的三处索引可与 Task 3 收尾并行准备。
