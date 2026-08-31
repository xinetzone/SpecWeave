# Checklist

## 内容忠实性
- [x] 《大学》《中庸》全文经双独立信源（ctext.org + Wikisource/中华书局整理本）逐字核对，异文显式标注
- [x] 《论语》精选 30–40 章、《孟子》精选 15–20 章原文经双源核对
- [x] 每处关键异文在 facts.md 登记编号事实与信源 URL
- [x] 经文层/注疏层/现代解读层三层显式区分，传统归属说法不作史实陈述（如"《论语》为弟子纂录"标注为传统共识）

## 解读多元性
- [x] 核心概念（仁/礼/义/中庸/性善/格物致知）解读呈现 ≥2 种注家立场
- [x] 注家覆盖五条脉络：汉学（何晏/赵岐）、宋学（朱熹）、清代考据（刘宝楠/焦循）、心学（王阳明）、现代（杨伯峻/钱穆）
- [x] 每处注家引用注明注家与出处

## OKF 格式与构建
- [x] 所有非 index/log 文档含 `type: OKF` YAML frontmatter（含 source/generated/status/stale_after）
- [x] 仅 bundle 根 index.md 含 `okf_version: "0.2"`；分组根含 `type: group` frontmatter
- [x] bundle 根 index.md 的 `{toctree}` 引用全部内容文档（concepts/examples/references/facts/insights/log），无孤立文档
- [x] 所有子目录含 index.md 且 toctree 完整
- [x] 文件名全部 kebab-case 纯英文，正文中文
- [x] Markdown 交叉引用使用相对路径，无断链
- [x] `invoke gates.all` 在 `projects/awesome-okf-xs` 全部通过（UTF-8 无 BOM + toctree 完整性）— exit 0，UTF-8 6279 文件通过，toctree 六项自检全通过

## 索引一致性
- [x] `bundles/index.md` frontmatter：total_bundles=319、groups=56（原计划 287/33 因并行会话推进基线而更新）
- [x] `bundles/index.md` 正文 think 域显示 "23 束 · 12 组"，分组表含 confucian 行
- [x] `think/index.md` 含 confucian 分组行与 toctree 条目，域描述更新
- [x] `think/confucian/index.md` 知识包列表与实际 bundle 一致

## 方法论闭环（seven-concepts 场景4）
- [x] facts.md ≥40 条编号事实，每条含信源 URL（67 条）
- [x] facts.md 全文无因果推断词（因为/导致/所以），G1 通过
- [x] insights.md ≥4 条四元组洞察（陈述/证据/反常识/行动），G2 通过（5 条）
- [x] ≥2 个可复用经典阅读模式（触发场景/核心步骤/反模式/迁移示例），G3 通过（2 个：双源核对阅读法、注家分层选用法）
- [x] V 对抗审查完成：≥10 处原文双源重核 + 10 条事实抽查 + 3 处分层审查，记录核对结果（12/12 原文一致、9/9+1 事实一致、3/3 分层通过，记录见 review.md）
- [x] log.md 含初始条目（2026-08-30，日期分组倒序格式）

## 交付
- [x] 原子提交在 awesome-okf-xs 子模块仓库内完成（单一职责，Conventional Commits）— commit `1d2060f4`，23 文件 +2953 行，仅含 doc/bundles/think/confucian/
- [x] git add 路径参数使用正斜杠（git-commit-utf8.py 集合比较要求）
- [x] 提交后 `git status`/`git diff` 核对变更实际写入
- [x] SpecWeave 主仓 specs 三件套勾选状态同步更新
- [ ] 共享索引对账提交（`bundles/index.md`、`think/index.md` 混入并行会话 fangzhong/huangdi-neijing 变更，依仓库对账提交惯例留待对账）
