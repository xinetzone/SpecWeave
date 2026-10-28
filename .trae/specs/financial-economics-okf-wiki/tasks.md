# 金融经济通识 OKF 知识包 - 任务清单

> 方法论链路：R（事实采集）→ I（骨架与知识拆分）→ E（信源先行生成）→ V（对抗审查与门禁）→ C（原子提交，待用户指令）。
> 执行日期：2026-10-28。

## R 阶段：事实采集与核验

- [x] 确定主题边界：金融体系、货币信用、利率估值、金融机构、金融市场、宏观框架、货币政策、国际金融、风险危机、中国金融、数字金融、金融素养。
- [x] 建立 12 个主题小节、F-001–F-104 连续事实编号。
- [x] 登记 S1–S45 信源：教科书 5 部、经典论文/学术著作 14 项、国际组织标准 12 项、中国官方机构 12 项。
- [x] P0 核验：日期、比率、制度安排、统计口径、历史节点逐类对照，结论写入 `references/02-verification.md`。
- [x] 口径留痕：M1 2025 口径修订、社融 vs M2、排名时间性、财政乘数/QE 争议、房地产参数动态性。
- [x] 放弃核验清单：实时行情、产品费率、高频统计、草案政策、个体机构评级。

## I 阶段：骨架判定与知识拆分

- [x] 操作可复现性两问：①有可照做的计算/分析流程？②有可复算的输入输出？两问皆「是」→ 设 `examples/`。
- [x] 三层知识拆分：总论与制度（00/09）→ 机制与工具（01–04/06–08/10）→ 宏观与个人（05/11）。
- [x] 每篇采用「是什么 → 机制 → 算例/数字 → 常见误读 → 小结 → 事实卡」骨架。
- [x] 示例设计：货币乘数、现值/债券、组合/CAPM、杠杆/挤兑，均为可手算/可表格复现。

## E 阶段：信源先行生成

- [x] 先写 `facts.md`、`references/01-classics-and-authorities.md`、`references/02-verification.md`。
- [x] 再写 11 篇 `concepts/` 与 4 篇 `examples/`。
- [x] 最后写 `concepts/index.md`、`examples/index.md`、`references/index.md`、根 `index.md`、`insights.md`、`log.md`。
- [x] 所有具体声明引用 F 编号；观点与争议入 `insights.md` 或正文限定语。
- [x] frontmatter 完整：根 `type: OKF` + `okf_version` + `version` + `sources` + `generated` + `verified` + `status` + `stale_after`；子文档 `type: Concept/Example/Reference/Facts/Insights`。

## V 阶段：对抗审查与门禁

- [x] 事实溯源：F 编号 104 条连续无跳号；全文引用 F 编号均 ≤104；无 F 之外的硬数字。
- [x] 结构规范：每个 `index.md` 含 `{toctree}`；根 toctree 收录 concepts/examples/references/facts/insights/log。
- [x] 链接可达：全部 Markdown 相对链接逐一检查，零缺失；无 `file:///`、无本机绝对路径。
- [x] UTF-8 严格解码：25 个 .md 文件全部通过，无 BOM、无替换字符、无繁体混入。
- [x] 索引计数：`bundles/index.md` total 687→688、sheke 82→83、finance 3→4；`sheke/finance/index.md` total 3→4；`sheke/index.md` finance 行 3→4。
- [x] 门禁：`python scripts/check-bundles-index.py` 通过（9 域/63 组/688 束，五面一致）；`python scripts/check-toctrees.py` 通过（零断链、零孤立内容）。
- [x] 修正：示例 02 的 IRR 表由错误插值改为 NPV 21% +1.08 / 22% −0.58，IRR≈21.65%；F-001/F-008/F-015 信源清理；F-097 英文残留改为中文；05 篇「三驾马车」表述修正；07 篇误标 F-080 删除；11 篇「負面」「hygiene」修正。
- [ ] Sphinx dummy build：环境未安装 sphinx（`ModuleNotFoundError`），未运行；已用两条仓库门禁 + 手动等效清单替代，并在 log 注明。

## C 阶段：原子提交

- [ ] 子模块 `projects/awesome-okf-xs` 提交（bundle + 三处索引）——待用户显式指令。
- [ ] 主仓库提交 spec 与子模块指针——待用户显式指令。
- [ ] 不 push。

## 验收对照

| 验收项 | 结果 |
|--------|------|
| 目录文件数 25（1 根 index + 1 log + 1 facts + 1 insights + 12 concepts 含 index + 5 examples 含 index + 3 references 含 index） | ✅ |
| F-001–F-104 连续、每条有 S 编号 | ✅ |
| 概念/示例引用 F 编号全部存在 | ✅ |
| 三级索引计数一致 | ✅ |
| check-toctrees.py / check-bundles-index.py | ✅ |
| 无投资建议/产品推荐/收益承诺/市场预测 | ✅ |
| 示例均标注教学假设 | ✅ |
