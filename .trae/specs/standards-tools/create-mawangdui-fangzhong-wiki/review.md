# 马王堆房中简帛 OKF wiki 教程 — 独立对抗评审报告（七概念 V 阶段）

> 评审时间：2026-08-31 ｜ 评审模式：只读（未修改 bundle 任何文件）
> 评审对象：`projects/awesome-okf-xs/doc/bundles/think/sexology/mawangdui-fangzhong-reading/`（22 个文件：index/facts/insights/log + concepts 9 + examples 4 + references 5）
> 评审依据：spec.md、checklist.md、frontmatter.md（awesome-okf-xs/.agents/rules/）、事实底座（.temp/mawangdui-fangzhong-facts.md 127 条 + insights 7 条）

## 一、评审范围

1. 通读全部 22 个文件（文件清单经目录枚举核实，与任务声明一致）
2. 四视角对抗评审：事实准确性 / 新人可入门性 / 定位与边界 / 时效与规范
3. 质量门脚本复验：toctree 完整性、相对链接可达性、UTF-8 编码（无 BOM）、索引计数

## 二、四视角逐项结论

### 视角 1：事实准确性 — pass

- **抽查条目（≥15 条）**：抽查 F-BG-001（1972—1974 发掘，S3）、F-BG-007（墓主利豨说矛盾，S22）、F-BG-012（帛书 47 种/12 万余字与 28 种/20 余万字两说并列，S2/S7/S8）、F-TXT-024（竹简定名异说，S39）、F-TXT-028（54/56 篇口径差异，S54）等 15+ 条，均与事实底座一致，信源编号标注完整。
- **基准事实核对**：前 168 年下葬（墓葬封闭年代）、1972—1974 发掘、2014 年《集成》初版、2024 年修订本、五十余种/13 万字量级——全部与 spec 基准事实清单吻合。
- **【待核验】标注保留**：墓主利豨说（F-BG-007）、房内记分合问题、篇题拟题说明、周贻谋版次、海外丛书信息、篇数口径（F-TXT-028）等争议条目均保留【待核验】标注，且 log/facts 声明"不得直接用于学术引用"。
- **因果词检查**：对 facts.md 全文检索「因为/导致/所以/因此/由于」，0 命中（F-TXT-024 中的"因"系引述信源原文，非作者因果推断）。G1 质量门通过。
- **结论**：事实底座 127 条全部带信源编号（S1—S54），分歧处并列两说，无静默采信、无虚构条目。

### 视角 2：新人可入门性 — pass

- **入门路径**：index.md 提供快速导航 + 分读者画像路径（零基础/有文献学基础/研究者），经 examples/01-first-book.md 落地；零基础读者可从出土背景（concepts/00）→ 文本群总览（concepts/01）→ 七损八益（concepts/02）循序进入。
- **链接可达性**：脚本核验 77 个相对链接，0 断链；相对路径层级全部正确。
- **学习路径闭环**：index.md → concepts（9 篇按序编号）→ examples（入门/精读示范/阅读计划）→ references（四类信源）形成闭环；examples/03-reading-plan.md 提供分阶段计划，闭环可执行。
- **结论**：无孤立文档，无死路。

### 视角 3：定位与边界 — pass

- **专题定位**：明确为"马王堆房中简帛专题阅读教程"（出土文本为经、研究著作为纬），与 classics-reading（性学经典通览）、fangzhong-bajia-reading（《汉书·艺文志》房中八家传世文献专题）边界清晰、不重复——本 bundle 聚焦出土简帛与整理出版史，八家 bundle 聚焦传世著录，交叉处通过 references/cross-references.md 互链而非内容复制。
- **内容合规**：全文以文献学/医学史学术口径呈现，无越界露骨描写；性养生内容均置于出土文献释读与学术研究史框架内。
- **术语口径**：七损八益、合阴阳、房内等术语均以文献学/中医史口径定义，未采用现代性学或通俗猎奇口径。
- **结论**：定位准确，边界干净。

### 视角 4：时效与规范 — pass

- **frontmatter 合法性**：抽查 index.md 及各文档，含 type: OKF、title、description、tags、version、source（归因至六维度调研事实登记）、generated、verified、status: draft、stale_after: 2027-08-31、okf_version: "0.2"，符合 frontmatter.md 规范。
- **文件名**：22 个文件全部 kebab-case（含数字前缀编号），无中文文件名、无空格。
- **toctree 完整性**：定向脚本核验，所有 toctree 条目指向的文件均存在，0 缺失；全部 22 个文件均被上级 toctree 引用，无孤儿文件。
- **索引计数**：bundles/index.md `total_bundles: 291` ✔；think 分组「10 束」✔；sexology 分组「3 束」✔（含本 bundle）；sexology/index.md 已登记本 bundle 条目与 toctree 引用。
- **编码**：22 个文件全部通过 UTF-8 解码校验，无 BOM、无乱码。
- **结论**：规范项全部达标。

## 三、问题清单

| 编号 | 严重度 | 位置 | 问题描述 | 修复建议 |
|---|---|---|---|---|
| — | — | — | 无 | — |

**fail 项：0 ｜ warn 项：0**

## 四、总体结论

**通过（PASS）**。马王堆房中简帛 OKF wiki 教程 bundle 在事实准确性、新人可入门性、定位与边界、时效与规范四个视角全部通过对抗评审：127 条事实全部带信源且争议处并列两说、【待核验】标注完整保留；77 个相对链接零断链、学习路径闭环；与既有两个性学 bundle 边界清晰无重复、内容合规；frontmatter/命名/toctree/索引计数/编码全部达标。无需修复即可进入下一阶段（C 原子提交）。
