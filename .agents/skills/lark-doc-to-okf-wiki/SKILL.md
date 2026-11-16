---
name: lark-doc-to-okf-wiki
version: 1.0.0
description: "把飞书/Lark 云文档连同其画板（whiteboard）、评论与附件一起，转化为可溯源的 OKF v0.2 知识包。流程：敏感度预检分流 → lark-cli 取正文与评论 → whiteboard 导出结构化节点与预览图 → F 编号事实台账 → 七件套结构与原子化写作 → 链接/计数双门验收。当用户给出 larkoffice 或 feishu 的 docx/wiki 链接并要求转知识包、生成 OKF wiki、拆解文档结构、学习其写作法或画板，或说『把这篇飞书文档做成教程/知识库』时必须使用此技能。不用于公开网页文章（用 blog-article-to-okf-wiki）、公众号文章（用 wechat-public-okf）、扫描书（用 scanned-book-to-okf-wiki）、加密 PDF（用 private-encrypted-pdf-to-okf-wiki）、源码（用 source-code-to-okf-wiki）。"
argument-hint: "<飞书文档 URL 或 token> [输出目录]"
user-invocable: true
disable-model-invocation: false
paths:
  - "playground/study/**"
  - "docs/knowledge/**"
source: "会话 sc-20261116-trae-camp-01-writing-wiki 里程碑复盘萃取，首例为一份含 6 块画板的内部课程文档"
x-toml-ref: "../../../.meta/toml/.agents/skills/lark-doc-to-okf-wiki/SKILL.toml"
---

# 飞书文档 + 画板 → OKF 知识包

飞书文档的价值往往不在正文，而在**画板**：正文给动机与细节，画板给骨架与范围。只抓正文会丢掉一半信息，所以本技能把"图文双源判读"设为强制步骤。

## 1. 适用边界

适用于：飞书 docx / wiki 文档（含 whiteboard、评论、附件、多媒体）的转化、结构拆解与写作法萃取。

不适用于：公开网页文章（`blog-article-to-okf-wiki`）、公众号文章（`wechat-public-okf`）、扫描书与加密 PDF（`scanned-book-to-okf-wiki` / `private-encrypted-pdf-to-okf-wiki`）、源码项目（`source-code-to-okf-wiki`）、纯格式转换（用 lark-cli 直接导出即可）。

> **为什么必须先判断技能边界？** 飞书文档常同时具备"私域 + 富媒体 + 评论"三个特征，而相邻技能各自假设了不同的信源形态与落盘位置；选错会导致产物进了公开 `docs/` 或漏掉画板。

## 2. 决策树：先分流，再采集

```text
第一步：内容敏感度（启动协议步骤 2.3）
├─ 企业内域名 / 需登录 / 内部培训材料 → 私域：跳过 .trae/specs/，产物入 playground/（或用户指定目录）
└─ 公开可访问的无访问控制文档      → 公开：Spec 目录 + 产物入 docs/

第二步：任务形态
├─ 要"学习它的写法/画板" → 产出写作法知识包（结构分析型）
├─ 要"提炼它的内容"       → 产出主题知识包（知识总结型）
└─ 两者都要               → 双包：主包存内容，写作法单独成包并回链
```

判定为私域时，产出物 frontmatter 标 `sensitivity: private`；不建公共索引。

> **为什么先判敏感度再采集？** 采集本身会把全文落到本地临时文件；先分流能避免私域内容在错误的目录里留下副本。

## 3. 七步流水线

| 步 | 动作 | 产物 | 门 |
|---|---|---|---|
| S0 | 敏感度预检 + 变体判定（公开/私域、内容型/结构型） | 分流结论 | 启动协议 2.3 |
| S1 | 拉正文与评论 | `raw.md` | 确认字节数与行数 |
| S2 | 导出全部画板 | `raw` JSON + `preview` 图 | 画板数量与正文 token 数一致 |
| S3 | 判读画板 | 每块图的类型、主标题、要素清单 | 每块能用一个问句概括 |
| S4 | 建 F 编号事实台账 | `_spec/facts.md` | 事实 ≥20、无因果词 |
| S5 | 搭七件套并原子化写作 | `index/quickstart/concepts/examples/references/_spec/assets` | 每篇单一主题 |
| S6 | 双门验收 | 链接门 0 断链 + 计数机械比对 | 全部通过 |

详细命令与参数见 [references/pipeline-commands.md](references/pipeline-commands.md)。

## 4. S1 采集：正文 + 评论

```bash
lark-cli docs +fetch \
  --doc "<doc-url-or-token>" \
  --doc-format markdown > raw.md
```

要点：

- 用 `--doc-format markdown` 取可读文本；返回体含 `reference_map.comments`（评论 sidecar），**评论是读者摩擦点的第一手证据**，不要丢。
- 需要定位块级结构时改 `--doc-format xml --detail with-ids`；`markdown` 与 `with-ids` 不兼容（会给出告警）。
- 记录 `document_id` 与 `revision_id`，写进知识包 frontmatter，用于版本锚定。

## 5. S2 画板：结构化节点 + 预览图双源

```bash
# 结构化节点（文本 + 坐标 + 类型）
lark-cli whiteboard +export --whiteboard-token <token> --output-type raw

# 预览图（扩展名必须与返回格式一致）
lark-cli whiteboard +export --whiteboard-token <token> \
  --output-type preview --output ./wb01.jpg --overwrite
```

判读方法：

1. **节点取文案**：按 `(y, x)` 排序后抽取 `text.text`，得到"阅读顺序近似"的文本序列，可用于引用原文短句。
2. **计数做密度**：非空文本节点数 = 该图信息密度，可用于横向比较哪块图信息最重。
3. **预览看版式**：颜色分区、同构卡片、箭头与虚线、图例位置，只能从预览图读。
4. **归类**：地图图（导航）/ 解剖图（结构）/ 操作图（执行），每块图必须能用一句问句概括。

节点字段结构、抽取命令与判读清单见 [references/whiteboard-reading.md](references/whiteboard-reading.md)。

> **为什么必须双源？** 只看文本会把"户型图"读成一张清单，丢掉分区与流向；只看预览图会把颜色当装饰，读不出"红格是唯一例外"这类设计意图。

## 6. S5 结构：OKF 七件套

```text
<package>/
├── index.md              # Bundle frontmatter + 阅读路径 + 洞察/结论 + toctree
├── quickstart.md         # 5 分钟速查：骨架 / 清单 / 五个坑
├── concepts/             # N 篇，每篇一个模式或主题，index.md 做索引
├── examples/             # 可直接套用的模板、对照、蓝图
├── references/           # 原文结构台账 + 核验口径
├── _spec/                # facts.md（R 阶段工作稿）+ log.md（链路与质量门）
└── assets/               # 画板预览图等本地素材
```

写作纪律：

- 每篇单一主题，首段给"事实底座：F-xxx"回链。
- 结论性判断集中在 `index.md` 的洞察段，四元组齐全（陈述/证据/反常识/行动）。
- 不复制整段原文，只摘短句并标注来源。
- 派生产物 frontmatter 必带 `source` 与 `sensitivity`。

模板与 frontmatter 样例见 [references/okf-structure.md](references/okf-structure.md)。

## 7. S4 事实台账与 S6 门禁

**F 编号规则**

- 一行一条，客观陈述，禁用"因为/导致/所以/错误"等因果或判断词。
- 每条标注核验来源：正文 / 画板（📐）/ 评论（💬）。
- 文件末尾放**计数核对表**：标题数、画板块数、表格数、代码块数、媒体数、事实条数。

**双门**

```bash
python .agents/scripts/check-links.py --path <package-dir>
# 关键计数逐项机械比对：正文 / 索引 / 事实台账三处必须一致
```

> **为什么计数要单列一张表？** 结构分析类文档最常错的不是观点而是数字（章节数、图数、行数）；三处口径漂移会让审查退化成逐字挑错，结论不可复核。

## 8. Gotchas（陷阱与反直觉行为）

1. `--output-type source` 只对含 Mermaid/PlantUML 代码块的画板有效；纯原生画板返回 `no code blocks found`，此时改用 `raw`，不要以为导出失败。
2. 预览图实际返回 `.jpg`；输出路径写 `.png` 会报 `failed_precondition` 并中断批量导出。
3. `--doc-format markdown` 与 `--detail with-ids` 不兼容，传了也只会拿到 markdown 并附告警。
4. 画板 raw 节点的 `y` 坐标单位与 `width/height` 不一致，排序可用但不能当像素布局。
5. 评论 sidecar 里的图片与用户名属于读者个人信息，引用时只保留现象，去掉昵称。
6. `playground/` 独立仓库的 `.gitignore` 忽略全部图片；知识包引用的画板图默认不入库，交付时须显式说明（或经批准调整忽略规则）。
7. 私域文档的 URL 与 revision 会变；知识包必须写死 `revision_id` 并在 references 里给复核触发条件。
8. 同一份文档可能同时支持"内容型"与"结构型"两个知识包，但不要混装在一个包里——读者与检索意图完全不同。
9. 评论里的报错（如 404/401）是读者单方陈述，可作"摩擦点存在"的证据，不能当根因结论。
10. 画板块在正文中的位置（章节开头 vs 章节结尾）本身就是设计信号，采集时按出现顺序记录，不要事后重排。

## 9. 安全检查清单

- [ ] 已完成敏感度预检，产出路径与级别匹配（私域→playground）
- [ ] 已记录 `document_id`、`revision_id` 与采集时间
- [ ] 画板数量与正文中的 whiteboard 块数量一致，无漏导
- [ ] 每块画板同时拿到 `raw` 与 `preview`，且 preview 扩展名正确
- [ ] 事实台账无因果词，且每条可追溯到正文/画板/评论
- [ ] 评论引用已去昵称与个人信息，截图类证据未直接嵌入
- [ ] 未复制整段原文，仅摘短句并标注来源
- [ ] 链接门 0 断链，计数核对表三处一致
- [ ] 图片是否入库已明确处理并在交付报告中说明

## 10. 参考文件

| 文件 | 何时读 |
|---|---|
| [references/pipeline-commands.md](references/pipeline-commands.md) | 执行 S1/S2，需要完整命令、参数与输出样例时 |
| [references/whiteboard-reading.md](references/whiteboard-reading.md) | 判读画板节点、抽取文案、归类与自检时 |
| [references/okf-structure.md](references/okf-structure.md) | 搭七件套、写 frontmatter、建事实台账时 |
| [evals/evals.json](evals/evals.json) | 回归测试触发与产出结构时 |

## 11. Changelog

- **v1.0.0** (2026-11-16)：初始版本。七步流水线、画板双源判读、F 编号台账与双门验收，萃取自 `sc-20261116-trae-camp-01-writing-wiki` 里程碑复盘（首例含 6 块画板与 32 条评论）。
