---
type: OKF
title: 儒家四书知识包 V 阶段对抗审查记录
description: 对 doc/bundles/think/confucian/four-books/ 知识包的对抗审查（Adversarial Review）记录：原文抽查、事实抽查、分层审查、格式抽查的样本、核对结果、发现与修复清单及通过结论
tags: [confucian, four-books, adversarial-review, verification]
generated:
  by: "agent:create-confucian-okf-wiki"
  at: "2026-08-31T00:00:00+08:00"
status: stable
---

# V 阶段对抗审查记录（Adversarial Review）

- **审查对象**：`projects/awesome-okf-xs/doc/bundles/think/confucian/four-books/`（21 个文件：facts.md、insights.md、log.md、concepts/9、examples/4、references/5）
- **核对底料**：`.trae/specs/create-confucian-okf-wiki/raw-texts.md`（双源核对原文：ctext.org 与 zh.wikisource.org）
- **审查日期**：2026-08-31
- **审查依据**：spec.md Requirement 与 checklist.md 对应四项审查任务
- **审查工具**：`review-check.py`（原文逐字比对）、`review-format.py`（frontmatter/kebab-case/断链自动检查）、WebFetch/WebSearch（信源验证）、Sphinx dummy build（构建回归）

## 一、原文抽查（examples vs raw-texts.md 逐字比对）

### 样本

| 来源 | 抽样方式 | 样本 |
|------|---------|------|
| examples/01-analects-close-reading.md | 随机抽 5 章（seed=20260831，从 40 章中抽） | 论语 12.17、14.24、15.24、4.16、6.11 |
| examples/02-four-books-selected-readings.md | 按任务指定 5 段 | 《大学》经一章、传五章朱熹补传、《中庸》首章、《中庸》第二十章、《孟子》浩然之气章 |

### 核对结果

| 样本 | 结果 | 字数 |
|------|------|------|
| 论语 12.17（季氏篇） | PASS 逐字一致 | 32 字 |
| 论语 14.24（宪问篇） | PASS 逐字一致 | 19 字 |
| 论语 15.24（卫灵公篇） | PASS 逐字一致 | 39 字 |
| 论语 4.16（里仁篇） | PASS 逐字一致 | 17 字 |
| 论语 6.11（雍也篇） | PASS 逐字一致 | 42 字 |
| 大学·经一章（2 段） | PASS 逐字一致 | 71+174 字 |
| 大学·传五章（朱熹补传） | PASS 逐字一致 | 12 字 |
| 中庸·第一章（首章） | PASS 逐字一致 | 132 字 |
| 中庸·第二十章（上、下 2 段） | PASS 逐字一致 | 300+674 字 |
| 孟子·公孙丑上第二章（浩然之气，节选） | PASS 逐字一致 | 245 字 |

**小计：12/12 全部逐字一致，无一处异文。** 比对方法为程序逐字比对（含标点），非人工目视。

## 二、事实抽查（facts.md 抽 10 条信源验证）

随机抽取 10 条：F-006、F-025、F-026、F-029、F-036、F-038、F-044、F-050、F-051、F-059。

| 编号 | 事实摘要 | 信源 | 验证方式 | 结果 |
|------|---------|------|---------|------|
| F-006 | 阮元嘉庆间于南昌府学开雕《十三经注疏》附《校勘记》 | zh.wikipedia.org/十三經注疏 | WebSearch 多信源 | PASS 内容一致 |
| F-025 | 明永乐十三年（1415）颁行胡广等《四书大全》为科举定本 | zh.wikipedia.org/四書大全 | WebSearch | PASS 内容一致 |
| F-026 | 清光绪三十一年（1905）废科举 | zh.wikipedia.org/四書 | WebSearch | PASS 内容一致 |
| F-029 | 张禹合校鲁齐两论为《张侯论》；郑玄就鲁论参校齐古作注 | zh.wikipedia.org/論語 | WebSearch | PASS 内容一致 |
| F-036 | 《中庸》通行统计 3568 字 | zh.wikipedia.org/中庸 | WebSearch | PASS 内容一致 |
| F-038 | 《论语集解》所集八家：包咸、周氏、孔安国、马融、郑玄、陈群、王肃、周生烈 | zh.wikipedia.org/論語集解 | WebSearch | PASS 八家名单一致 |
| F-044 | 《论语集注》《孟子集注》汇集二程、张载及程门诸弟子之说 | zh.wikipedia.org/四書章句集注 | WebSearch | PASS 内容一致 |
| F-050 | 杨伯峻《孟子译注》中华书局 1960 年初版 | zh.wikipedia.org/楊伯峻 | WebSearch | PASS 内容一致 |
| F-051 | ctext.org 提供杨伯峻《论语》《孟子》现代汉语译文（/lunyu/zhs、/mengzi/zhs） | ctext.org/lunyu/zhs | WebFetch ×2（本次+前次会话） | **信源不可达**（ctext.org 地区访问限制，非判失败）；佐证：杨伯峻《论语译注》真实存在，搜索到的 12.1 译文"抑制自己，使言语行动都合于礼"与 02-ren.md 中引用的杨伯峻译文一致 |
| F-059 | 定州汉墓竹简《论语》为今见最早《论语》文本实物 | zh.wikipedia.org/論語 | WebSearch | PASS 内容一致 |

**小计：9 条验证一致，1 条信源不可达（按规则不判失败）。无虚构引证，注家归属无误。**

## 三、分层审查（concepts 三处核心概念）

| 文档 | 呈现的注家立场 | 层次分离情况 | 结论 |
|------|--------------|-------------|------|
| concepts/02-ren.md | 克己复礼章 5 家：马融（何晏《论语集解》引）、朱熹《论语集注》、刘宝楠《论语正义》、杨伯峻《论语译注》、钱穆《论语新解》；恕道章另给朱熹/杨伯峻两家 | "汉魏古注+清代考据（约身/修身）vs 朱熹理学（胜私欲）"两条路线明确对照；每家注明书名；对未收入双源核对范围的 12.22（樊迟问仁"爱人"）明确声明并指路核验 | PASS |
| concepts/05-zhongyong.md | "不偏之谓中" 5 家：程子（《中庸章句》解题引）、郑玄注《礼记正义》、孔颖达疏、焦循（参考）、杨伯峻（参考）；诚章给"朱熹以天理释诚 vs 汉唐旧训信实"两分 | 朱注（行为适度层）与旧注（心体未发层）分层陈述；标注"大意，据《礼记正义》所存郑注"，不冒充直引 | PASS |
| concepts/07-daxue-path.md | 格物致知 3 家：郑玄《礼记正义》注（训格为来）、朱熹《大学章句》（训格为至）、王阳明《传习录》《大学古本傍释》（训格为正）；亲民/新民之辨：朱熹 vs 王阳明 | 补传明确标注"朱熹拟作，并非《大学》原文"；经文引用均标篇名章序；注家表格含书名 | PASS |

**小计：三处均 ≥2 种注家立场且注明注家与书名；经文层/注疏层/现代解读层无混淆。** 另抽查确认：对无法双源核对的章句（如《论语》12.22、《论语·学而》1.13"礼之用和为贵"），文档主动标注"未收入本包双源核对章句范围，如需引用请以 ctext.org 对应页面核验"——诚实边界处理良好。

## 四、格式抽查

自动脚本全量检查（非抽样）21 个文件：

| 检查项 | 结果 |
|--------|------|
| frontmatter `type: OKF`（非 index/log 文档，共 18 个） | PASS 全部包含 |
| 文件名 kebab-case（含数字前缀模式） | PASS 全部合规，与库内其他 bundle 命名一致 |
| 交叉引用相对路径（初始 166 个链接） | 发现 3 处断链/链接语法损坏（见修复清单 #1-#3） |
| 根目录 index.md 存在性 | 初始缺失（见修复清单 #4） |
| think/confucian/index.md（上游 think/index.md 已引用） | 初始缺失（见修复清单 #5） |

## 五、发现与修复清单

**大问题（原文不一致/虚构事实）：0 条。**

**发现并修复的问题：5 条（均为链接/结构级小问题，无内容层修改）**

| # | 文件 | 问题 | 级别 | 处置 |
|---|------|------|------|------|
| 1 | concepts/03-li-junzi.md:13 | `[四书事实清单](../facts.md）` 全角右括号损坏 Markdown 链接语法（渲染不出链接） | 小（断链类） | 已修复：`）`→`)` |
| 2 | concepts/07-daxue-path.md:13 | 同上，全角右括号损坏链接 | 小（断链类） | 已修复：`）`→`)` |
| 3 | examples/01-analects-close-reading.md:622 | `[四书通读计划](../03-reading-plan.md)` 路径错误：目标文件在同级 examples/ 目录而非上级目录，构成真断链 | 小（断链类） | 已修复：改为 `03-reading-plan.md` |
| 4 | four-books/index.md | 知识包根入口 index.md 缺失（任务规格声明"目录含 index.md"；同库所有同级行 bundle 如 neijing-reading、amitabha-sutra 等均有根 index） | 结构断链 | 已修复：创建 index.md，内容（frontmatter、导航、toctree）全部取自现有文档的 title/description，不引入新事实，模式对齐 neijing-reading/index.md |
| 5 | think/confucian/index.md | 域级 index 缺失，而上游 think/index.md 第 17 行导航表格与第 35 行 toctree 均已引用 `confucian/index`，构成站点级真实断链 | 结构断链 | 已修复：创建域级导航 index.md（模式对齐 huangdi-neijing/index.md），登记 four-books 唯一 bundle |

**登记不改的问题：0 条。**

## 六、修复后回归验证

1. **格式脚本复验**：199 个链接全部有效，0 问题；4 个 index.md（根 + concepts/examples/references）齐全。
2. **Sphinx dummy 构建回归**（`sphinx-build -b dummy -E doc _build/dummy` 于 projects/awesome-okf-xs）：exit=0；构建日志中 `bundles/think/confucian/index` 与 `bundles/think/confucian/four-books/` 下全部 23 个文档正常读取/写入，**无任何 WARNING/ERROR**——新建的两个 index.md 未引入构建问题，think/index.md 的 toctree 引用断链已消除。

## 七、审查结论

| 维度 | 结果 |
|------|------|
| 原文抽查 | 12/12 逐字一致 |
| 事实抽查 | 9/9 验证一致 + 1 信源不可达（F-051，不判失败） |
| 分层审查 | 3/3 通过（≥2 种注家立场、注家书名俱全、三层不混淆） |
| 格式抽查 | 修复后全量通过（199 链接 0 断链） |
| 大问题 | 0 |
| 小问题（已修复） | 5 |
| 登记不改 | 0 |

### 结论：**通过（PASS）**

儒家四书知识包的内容层（原文转录、事实登记、注家归属、分层呈现）经对抗审查未发现任何硬错误；发现的 5 处问题全部为链接语法与导航结构层面的小问题，均已修复并通过格式脚本与 Sphinx 构建双重回归验证。知识包可进入 C（固化/发布）阶段。

### 遗留事项（非缺陷，供 C 阶段参考）

- F-051 的 ctext.org 信源在当前网络位置不可达（反爬地区限制），待可访问环境（如更换网络或机构订阅）时可补一次直证；
- `references/cross-refs.md` 中登记的"confucian 组未来增量规划（five-classics/xunzi/chuanxilu）"属规划信息，后续新增 bundle 时需同步更新 `think/confucian/index.md` 的知识包列表。
