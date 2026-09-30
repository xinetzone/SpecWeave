---
name: knowledge-pack-builder
description: 把七概念知识沉淀（R→I→E→V→C）的产出落成本仓规范的原子化知识包——编号事实表、四元组洞察、可迁移模式、四视角 V 审查、信源台账、YAML frontmatter、toctree 与校验脚本。当用户要求把调研/对比/研究沉淀为知识包、知识入库、在 docs/knowledge 下建包时使用；纯问答、单篇报告或不准备长期复用的一次性写作不要使用。
---

# knowledge-pack-builder

把一次七概念知识沉淀（场景 4，链路 R→I→E→V→C）的产出，落成符合 SpecWeave 仓库规范、可审计、可复用的**原子化知识包**。本技能沉淀自四次同构交付：openKylin 全面调研（62 事实）、openKylin 文档站导读（44 事实/237 文档）、Python agent harness 全景（45 事实）、openEuler vs openKylin 对比（35 事实+12 跨包锚点）。

**与 seven-concepts-cmd 的分工**：方法论编排（场景识别、概念链路、质量门顺序、CMD-LOG）由 seven-concepts-cmd 负责；本技能只管一件事——**每个阶段的产出"写成什么文件、放在哪、长什么样、如何校验"**。两者配套使用，不互相替代。

## 0. 触发与边界

**使用**：用户明确要求"沉淀为知识包/知识入库/建包/把调研落盘"，或七概念场景 4 执行到 C（入库）阶段。

**不使用**：① 随口问答与概念解释；② 用户只要单篇文章/报告（走 doc-writing-guide/report-page）；③ 私域内容未判级就落盘；④ 主题尚无 ≥20 条可溯源事实（证据不足，先补 R 阶段）；⑤ 代码任务交付（走 spec-task-ifavc-delivery 或 TDD）。

## 1. 阶段 0：落盘前四查（不通过不建目录）

1. **读 AGENTS.md 启动协议**：以磁盘 `AGENTS.md` 原文为准（内联副本可能过期），确认文档边界条款：根 `docs/` 是唯一文档中心，`.agents/docs/` 已废止禁止写入。
2. **内容敏感度判级**：公开内容（公开网页/开源/官方文档）→ 规划可在 `.trae/specs/`，产出入根 `docs/knowledge/<域>/<bundle-id>/`；私域内容（内网、带 token/code 链接、个人笔记、商业培训）→ 跳过公共规划区，入 `playground/` 或用户指定目录。不确定就高判私域或问用户。
3. **查重与定位**：Glob `docs/knowledge/**/index.md` 与同级目录，确认是否已有同主题包——**优先扩包/合包**（openkylin 包即由独立目录合并而来），其次才新建；新目录名用 kebab-case 纯英文、主题词而非日期。
4. **冻结 session 与信源时点**：session 号 `sc-YYYYMMDD-<topic>`；每个包在 frontmatter 与正文标注采集时点；引用既有本地包时写明"事实时点冻结在对方包的日期"。

## 2. 标准目录骨架（默认形态，按需增减）

```text
<bundle-id>/
├── index.md                      # 必需：frontmatter + 导航 + 事实表 + I 摘要 + E 摘要 + V 摘要 + 质量门 + CMD-LOG + 隐藏 toctree
├── concepts/                     # 按"读者问题域"拆分，不按信源或官方目录拆
│   ├── 00-overview.md            # 一分钟画像 + 术语辨析（对比类必备）
│   ├── 01-<question>.md
│   └── 05-selection-guide.md     # 选型/行动类主题以决策页收尾
└── references/
    ├── source-inventory.md       # 必需：信源台账（键、URL、支撑事实编号、分级、采集缺口）
    └── adversarial-review.md     # V 审查全记录（意见/裁定/回归确认）
```

规则：① 一文件一职责，每篇可独立验证；② 概念页按学习者问题组织（"我想 X → 读哪篇"导航表），禁止镜像官方目录结构；③ 纯机械附录（完整目录、长台账、实测日志）入 references/；④ 单包控制在 8—14 个文件，过大先按子主题分包。新建文件照抄 `assets/` 四份模板起步。

## 3. frontmatter 与 index 规范

- 仅 index.md 带 YAML frontmatter（与本仓既有包一致），概念页/参考页纯 Markdown 起始即可。
- 字段照模板：`type: Reference`、`id`（= 目录名）、`title`、`category`（如 tech）、`tags`、`date/last_updated`、`status: verified`、`author: "SpecWeave Agent（方法论编排 session <id>）"`、`summary`（含事实数/洞察数/模式与成熟度/包结构）、`security_level: public`、`knowledge_type`、`validation_status`、`source`（一手/二手/本地包引用与采集日期）。
- index.md 末尾放隐藏 toctree，列出本包全部子页：

````markdown
```{toctree}
:maxdepth: 1
:hidden:

concepts/00-overview
references/source-inventory
```
````

同时在上层索引（如 `docs/knowledge/tech/index.md`）的 toctree 中登记一行 `<bundle-id>/index`；**改 toctree 只追加，不重排既有行**。

## 4. R 阶段事实工程（G1 的写作纪律）

1. **编号方案**：每包独立前缀（如 F/O），三位数字，在 index 事实表集中登记；引用另一个本地包不复制事实，用**锚点表**（如 K-001 → 对方包 F-003）并给出相对链接。
2. **客观陈述**：每条只写可验证事实（日期、版本号、数字、URL、文件路径、原文措辞），**禁用因果词**（因为/所以/导致/从而/使得/推动了）；因果解释属于 I 阶段。
3. **口径四件套**：每个规模/份额/性能数字同时标注统计对象、时点、发布方、原始或转引层级；厂商大会口径、第三方机构口径、官网实时统计口径分行分列。
4. **矛盾并列**：多源日期或数字不一致时全部保留并注明取数页面，不取均值、不择一、不"约等于"；官网动态数据两次抓取有差异时给区间不给点值。
5. **官方口径标注**：性能倍数、能效提升、兼容率等无第三方复测的数字，句中内联"官方口径待复测"，禁止进入容量/采购模型。
6. **信源分级**：一手官方 / 厂商官方 / 媒体转引 / 三级参考（百科）四级，台账中注明使用纪律；单一信源事实显式标注"单点口径"。
7. **数量门槛**：事实 ≥20 条、分组（起源治理/版本/技术/生态等），低于门槛回 R 补采，不靠形容词凑数。

## 5. I/E/V 写作要点

- **I 洞察（≥3 条，维度独立）**：每条四元组齐全——**陈述 / 证据（编号引用）/ 反常识 / 行动**；"反常识"必须写出直觉判断与证据结论的冲突点，"行动"给出可执行清单或评估问题。index 放全文，概念页承载证据展开。
- **E 模式（G3 要素一个不缺）**：4—8 字中文模式名 + 一句话定义 + 适用于 / 不适用于边界 + 3—7 步核心步骤 + 检验标准 + ≥3 反模式 + ≥1 跨域迁移 + 成熟度（L1-draft/L1/L2 与升级条件）。**默认不直接写入 `docs/retrospective/patterns/`**：先在知识包内成型，只有用户明确要求"模式入库"时才独立化并双向加链接。
- **V 审查（4 视角全覆盖）**：魔鬼代言人（口径、样本、营销话术、反事实）、新人（术语、最小路径、我该选谁）、老板（SLA、合规、成本、测评主体）、未来（版本窗口、协议更替、复查触发器）。意见 ≥5 且具体，每条有裁定（采纳/部分采纳/不采纳+理由），采纳项必须**回归确认**（写明在哪份文件改了什么），全部关闭才过 V 门。

## 6. 落盘后校验（G4，按顺序执行）

1. **文件名规范**（本机 `python` 不在 PATH，用全路径；务必加 `--directory` 限定，否则全仓扫描含 submodule 耗时极长）：

```powershell
& "C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe" .agents/scripts/check-filename-convention.py --directory docs/knowledge/<域>/<bundle-id>
```

2. **链接检查**（新包首验必跑，修完重跑到"所有链接均有效"）：

```powershell
& "<python 全路径>" .agents/scripts/check-links.py --path docs/knowledge/<域>/<bundle-id>
```

易错点：知识包在 `docs/knowledge/<域>/<bundle>/` 三层深，引用 `docs/retrospective/` 用 `../../../retrospective/...`；references/ 子页引用兄弟知识包要再多一层（`../../<sibling>/...`）。Markdown 内一律相对路径，禁止 `file:///` 与 `.temp/` 引用。
3. **结构自检**：index 隐藏 toctree 条目数 = 子页数；上层索引已登记；表格改行列数时整表替换；frontmatter 为 YAML（---包裹）。
4. 有 Mermaid 图时跑 `check_mermaid.py`（遵守安全编码六规则）。

## 7. C 阶段收尾纪律

- 默认**只给 Conventional Commits 提交提案，不执行 git commit/push**，等用户明确指示；信息用中文，形如 `docs(knowledge): 新增 <主题>知识包——<一句话价值>（七概念R-I-E-V-C）`。
- 提交范围单一：新包文件 + 上层 toctree 一行，不夹带无关变更。
- index 质量门表逐行填 PASS 与证据（事实数、洞察数、模式成熟度、V 意见数/采纳数、文件数），并在代码块内保留完整 CMD-LOG（S0/S2/G1/G2/G3/V/S99，格式见模板）。
- 局限声明必写：信源结构偏差、未取证项、采集时点、复查触发器（如新版本/新协议出现时的复查时间点）。

## 8. 反模式（四次实战真实教训）

1. 事实表写因果推断——G1 必挂，洞察和事实混成一锅无法审计。
2. 用对方社区的规模数字比大小——统计口径不对齐（注册用户 vs 装机 vs 出货），跨社区比较结论一律不成立。
3. 镜像官方文档目录建概念页——复制官方结构等于复制它的结构缺陷；按读者问题重组。
4. 转引数据当原始数据——白皮书未取得原文就写"据白皮书 X%"，必须标"媒体转引"并在台账登记缺口。
5. 模式当场要求入模式库——越权扩大范围；先在包内 L1-draft 成型，用户明确要求再独立化。
6. 新建同主题平行包——先查重，能合入既有包就做原子化合并并入链修复（openkylin 先例 15 处入链同步）。
7. 凭记忆写相对路径——三层目录深度下数错层级是断链首因，落盘后必须跑链接脚本实证。
8. 私域内容误落 docs/——阶段 0 判级没做就开工，事后迁移成本高。
