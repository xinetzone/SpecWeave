---
status: "draft"
name: zhouyi-works-okf-bundle
version: 1.0.0
created: 2026-08-31
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（《周易》为先秦古典文献，公共领域）
source: 阮刻《十三经注疏·周易正义》今本系统 + 出土文献整理本（马王堆帛书/上博楚简/阜阳汉简/王家台秦简）+ 历代注本 + 现代学术注本；双源电子文本核对（ctext.org、zh.wikisource.org）
---

# 《周易》著作 OKF 知识包（权威原文 + 权威解读）— 产品需求文档

## Overview

- **Summary**：在 awesome-okf-xs 文档库 `think/`（思想与理论）域下新建 `zhouyi/` 分组与 `zhouyi-works/` 知识包（bundle），系统收录《周易》经传的**权威原文**与**权威解读**，以 OKF v0.2 格式发布为中文 wiki 教程。
- **Purpose**：《周易》为"群经之首、大道之源"，是 think 域现有 17 个分组中唯一缺席的核心先秦经典。现有 `think/confucius/works` 仅以一篇概念文档（05-zhouyi-yizhuan）处理"孔子与《周易》的关系"，不提供经传原文与注疏谱系；`think/yinyangjia` 处理邹衍学派辑佚，与《周易》文本本体不重叠。本任务填补该空白。
- **Target Users**：需要可靠《周易》文本与解读的中文读者、经典研读学习者、AI 智能体（OKF 知识包同时面向人类阅读与智能体检索）。

## Goals

- 提供**今本《周易》经文全本**（六十四卦卦辞、爻辞、用九用六，384 爻完整），以阮刻《十三经注疏·周易正义》为底本，经 ctext.org 与 zh.wikisource.org 双源逐字核对。
- 提供**十翼选读**：《系辞》上下、《说卦》《序卦》《杂卦》全录；《彖》《象》《文言》随乾坤二卦精读完整呈现；十翼全貌在概念文档中导览。
- 出土文献（马王堆帛书《周易》、上博楚简《周易》、阜阳汉简《周易》、王家台秦简《归藏》）的**存佚分层著录 + 关键异文选录**，残损范围显式说明，释文溯源正式整理本。
- **三线并收权威解读**：出土文献校注（文本层）→ 历代注本（义理/象数层）→ 现代学者注本（综合层），注家立场分开、分歧并列不仲裁。
- 按 seven-concepts 场景4 完成 R（事实采集）→ I（洞察）→ E（模式萃取）→ V（对抗审查）→ C（原子提交）闭环，质量门 G1-G4 全过。
- 通过 awesome-okf-xs 全部质量门（`invoke gates.bundles` 计数对账、`invoke gates.toctrees` 导航完整性、`invoke gates.utf8` 编码）。

## Non-Goals

- 不做《周易》全文白话翻译（解读以引用注本立场为主，不替代注本）。
- 不收录占卜/算命/风水/梅花易数等衍生术数应用内容（仅在易学流衍概览中标目，不展开）。
- 不重复 `confucius/works` 的"孔子与六经关系"专题（交叉链接，不复制）。
- 不收录《周易》译注的现代版权译文全文（仅著录书目、引用短例）。
- 不修改除 `think/index.md`、`bundles/index.md` 导航计数外的任何既有 bundle。

## Background & Context

- **位置决策**：新建分组 `doc/bundles/think/zhouyi/`，下挂 1 个知识包 `zhouyi-works/`。先例：`think/laozi/laozi-works/`（2026-08-30 由 `agent:seven-concepts-cmd` 生成，26 文件，结构与本任务同构）。
- **格式规范**：OKF v0.2（`meta/okf-spec`）；frontmatter 规范见子项目 `.agents/rules/frontmatter.md`（唯一必填 `type`；bundle 根 `index.md` 方可带 `okf_version: "0.2"`；`index.md`/`log.md` 为保留文件名）。
- **计数影响**：新增 1 组 1 束 → think 域 28 束/17 组变为 29 束/18 组；全库 324 束/61 组变为 325 束/62 组（以 `invoke gates.bundles` 三角校验输出为准，禁止手工估算）。
- **子模块纪律**：awesome-okf-xs 为 git submodule，存在并行会话写共享索引；提交前必须显式 `git add` 目标文件、`git show :<path>` 核验暂存 blob、`git checkout-index -a --prefix=$prefix` 导出暂存态快照跑双门。
- **用户决策（2026-08-31 澄清）**：① 原文范围＝经文全本＋十翼选读；② gates 通过后执行原子提交。

## Functional Requirements

- **FR-1**：在 `think/zhouyi/zhouyi-works/` 下建立符合 OKF v0.2 的 bundle，含根 `index.md`（带 `okf_version: "0.2"`）、`log.md`，及 `concepts/`、`text/`、`examples/`、`commentaries/`、`references/` 五个子目录（各含 `index.md`），另有 `usage.md`、`facts.md`、`insights.md`、`patterns.md`。
- **FR-2**：`text/` 提供今本经文全本：上经 30 卦（乾→离）、下经 34 卦（咸→未济），每卦含卦名、卦辞、全部爻辞（含乾用九、坤用六），共 64 卦 384 爻无缺漏。
- **FR-3**：`text/` 提供十翼选读全文：《系辞上传》《系辞下传》《说卦传》《序卦传》《杂卦传》；《彖传》《象传》《文言传》在 `examples/` 乾坤精读中完整收录；`text/index.md` 显式说明选录范围与未全录篇目的权威信源指引。
- **FR-4**：`text/unearthed-variants.md` 著录四大出土文本系统（马王堆帛书、上博楚简、阜阳汉简、王家台秦简《归藏》）：出土时间地点、抄写年代、整理本、存佚范围、卦序/异文要点；释文片段溯源正式出版物，残损显式标注，不编造释文。
- **FR-5**：`concepts/` 至少 5 篇概念文档：①《周易》名实与经传结构（含成书年代诸说）；②文本系统（今本/出土/古三易）；③核心概念（阴阳、八卦、卦爻、象数、时位、占筮与大衍之数）；④十翼结构与归属；⑤历代易学谱系（象数/义理/图书/考据）。
- **FR-6**：`commentaries/` 三线并收：出土校注（帛书/楚简整理组、张政烺、于豪亮、廖名春等）、历代注本（王弼/韩康伯注·孔颖达正义、李鼎祚集解、程颐《伊川易传》、朱熹《周易本义》、李光地《周易折中》）、现代注本（高亨、李镜池、金景芳/吕绍刚、黄寿祺/张善文、刘大钧、李零等），每条含注家姓名、著作名、成书/出版信息与立场；争议（成书年代、孔子与十翼、卦序、经传关系）设独立文档显式化。
- **FR-7**：`examples/` 至少 2 篇精读：乾坤二卦经传合读（经文＋《彖》《象》《文言》全录＋≥2 注家立场对照）、代表卦选讲（泰否、谦、既济/未济等）。
- **FR-8**：`references/` 为信源登记簿，每条信源含可核查 `resource`（ISBN/正式出版信息/机构 URL）；正文事实性论断以脚注逐声明归因；`facts.md` 为零因果推断事实清单。
- **FR-9**：导航更新：`think/zhouyi/index.md`（分组索引）、`think/index.md`（分组表行＋toctree＋描述）、`bundles/index.md`（frontmatter 计数、域计数行、think 分组表行、生态概览/入门路径图标签）。

## Non-Functional Requirements

- **NFR-1（原文准确性）**：经文与十翼选录文本须与权威底本逐字一致，异体字/通假字从底本，不改写；双源核对痕迹可查。
- **NFR-2（学术诚实）**：凡有学术分歧处并列呈现诸说并标注争议状态，不做单一确定性断言；不伪造出土释文、不虚构注家观点。
- **NFR-3（规范合规）**：全部文件 UTF-8 无 BOM；非保留 `.md` 均含可解析 YAML frontmatter 与非空 `type`；相对路径交叉引用，禁止 `file:///` 绝对路径。
- **NFR-4（可审计）**：R/I/E/V/C 各阶段产出物与质量门记录留痕于 `facts.md`、`insights.md`、`patterns.md`、`log.md` 与独立审查报告。

## Constraints

- **Technical**：遵循 OKF v0.2 与子项目 frontmatter 规范；Sphinx + myst_parser 构建兼容（裸日期由 conf.py 钩子处理）；文件名 kebab-case 英文、正文中文。
- **Business**：《周易》原文为公共领域文献；现代注本仅著录与短引（合理使用），不收录版权译文。
- **Dependencies**：ctext.org / zh.wikisource.org 可访问（双源核对）；子项目 Python 环境可运行 `invoke gates.*`；网络检索用于信源核实。

## Assumptions

- 阮刻《十三经注疏》本《周易正义》经注文本与 ctext.org、维基文库文本在经文层面一致（个别异体字以底本为准、异文出校）。
- 出土文献释文以正式出版整理本为最高权威，网络转写仅作线索；无法核实的释文不录。
- 新增分组计数为 think 域 +1 组 +1 束（zhouyi-works 为单束，非锚点组）。

## Acceptance Criteria

### AC-1: Bundle 结构与 OKF 合规
- **Type**: `rule`
- **Given**：任务完成后的 `projects/awesome-okf-xs/doc/bundles/think/zhouyi/` 目录
- **When**：检查目录结构与全部 `.md` 文件 frontmatter
- **Then**：存在 `zhouyi-works/index.md`（frontmatter 含 `okf_version: "0.2"` 与 `type: OKF`）、`log.md`、`usage.md`、`facts.md`、`insights.md`、`patterns.md`，及 `concepts/`、`text/`、`examples/`、`commentaries/`、`references/` 五个子目录且各含 `index.md`；每个非保留 `.md` 含可解析 YAML frontmatter 与非空 `type`
- **Pass Condition**：结构清单逐项存在；frontmatter 解析零错误
- **Evidence**：目录列表 + `invoke gates.toctrees` 输出 + frontmatter 抽查记录

### AC-2: 经文全本完整准确
- **Type**: `rule`
- **Given**：`text/jing-shang.md` 与 `text/jing-xia.md`
- **When**：核对卦数、爻数与文本
- **Then**：上经 30 卦（乾至离）、下经 34 卦（咸至未济）共 64 卦；每卦卦辞与 6 爻爻辞齐全（乾用九、坤用六在列），共 384 爻；文本经 ctext.org 与 zh.wikisource.org 双源核对，无脱漏、无臆改
- **Pass Condition**：64 卦/384 爻计数齐全；抽查 20 卦文本双源一致
- **Evidence**：文件内卦爻计数声明 + 双源核对脚注 + 审查抽查记录

### AC-3: 十翼选读范围明确且全文完整
- **Type**: `rule`
- **Given**：`text/` 十翼文件与 `examples/qian-kun-jingdu.md`
- **When**：检查收录范围
- **Then**：《系辞》上下、《说卦》《序卦》《杂卦》全录且首尾完整；《彖》上下、《象》上下、《文言》随乾坤精读完整呈现；`text/index.md` 显式说明选录范围并给出未全录篇目的权威电子信源链接
- **Pass Condition**：已全录篇目首尾章句与底本一致；选录范围声明存在
- **Evidence**：text/index.md 范围声明 + 审查抽查

### AC-4: 出土文献著录权威诚实
- **Type**: `rule`
- **Given**：`text/unearthed-variants.md` 与 `concepts/02-text-systems.md`、`references/` 出土信源
- **When**：核对四大出土文本系统条目
- **Then**：马王堆帛书（1973）、上博楚简（1994 购藏/2003 公布）、阜阳汉简（1977）、王家台秦简《归藏》（1993）各有条目，含出土信息、抄写年代、整理本、存佚范围；所引释文片段可溯源至正式出版物，残损处显式标注
- **Pass Condition**：四系统条目齐全；每条释文有出版信源；无"全文"式编造
- **Evidence**：文档条目 + references 信源登记 + facts.md 对应事实编号

### AC-5: 三线解读与争议显式化
- **Type**: `rule`
- **Given**：`commentaries/` 四篇文档
- **When**：检查注家覆盖与争议处理
- **Then**：出土校注、历代注本（王弼/孔颖达、李鼎祚、程颐、朱熹、李光地）、现代注本（高亨、李镜池、金景芳/吕绍刚、黄寿祺/张善文、刘大钧、李零等）三线均有专篇，每条含注家、著作、时代/出版信息与立场；争议独立成篇，分歧并列不仲裁
- **Pass Condition**：三线专篇存在；规定注家全部覆盖；争议文档含≥4 个争议点
- **Evidence**：commentaries 文档 + facts.md 注本事实

### AC-6: 信源溯源与 G1 事实质量
- **Type**: `rule`
- **Given**：`references/` 与 `facts.md`
- **When**：检查溯源与事实清单
- **Then**：references 每条含可核查 resource；正文事实性论断有脚注归因；`facts.md` 事实编号连续、无因果推断词（"因为/导致/所以"）、无主观评价
- **Pass Condition**：信源登记可核查；facts.md 通过 G1（零因果词抽检通过）
- **Evidence**：references 文档 + facts.md + G1 检查记录

### AC-7: 导航与质量门
- **Type**: `rule`
- **Given**：更新后的 `think/zhouyi/index.md`、`think/index.md`、`bundles/index.md`
- **When**：运行子项目质量门
- **Then**：`invoke gates.bundles`（束/组/域三角计数）、`invoke gates.toctrees`（无断链/无孤立文档/bundle 根 index 完整）、`invoke gates.utf8` 全部通过；新增 bundle 在三层导航均可达
- **Pass Condition**：三条 gates 命令退出码 0 且无 zhouyi 相关报错
- **Evidence**：命令输出日志

### AC-8: 方法论闭环（G2/G3/V）
- **Type**: `rule`
- **Given**：`insights.md`、`patterns.md`、`log.md` 与争议文档
- **When**：检查七概念产出物
- **Then**：`insights.md` 含≥3 条四元组洞察（现象+根因+影响+建议，G2）；`patterns.md` 含≥2 个可复用模式（触发场景+核心步骤+反模式+迁移验证，G3）；V 阶段对抗审查结论记录于 `log.md` 并在争议文档留痕
- **Pass Condition**：G2/G3 要素逐项齐备；V 记录可查
- **Evidence**：三份文档 + log.md

### AC-9: 原文与解读质量评分
- **Type**: `rubric`
- **Dimension**：内容学术质量（原文准确性、注家立场区分度、争议呈现诚实度、教程可读性）
- **Scale**: 1-5
- **Anchors**：1 = 存在臆造文本/注家观点或硬性史实错误；3 = 文本准确但解读笼统、争议处理单薄；5 = 文本逐字可靠、三线注家立场清晰可辨、争议完整并置、阅读路径实用
- **Pass Threshold**: >= 4
- **Evidence**：独立审查抽查（经文 20 卦、十翼 3 篇、注家 10 家）与评分记录

### AC-10: 独立审查与原子提交
- **Type**: `rule`
- **Given**：全部内容完成、gates 通过
- **When**：fresh context 独立审查通过后执行提交
- **Then**：独立审查结论为 pass（无未处理 actionable finding）；提交前显式 `git add` 目标文件、`git show :<path>` 核验暂存 blob、暂存态快照跑双门通过；Conventional Commits 中文提交信息、单一职责
- **Pass Condition**：review.md 记录 pass；提交后 `git status` 干净、子模块指针变更可见
- **Evidence**：review.md + 暂存核验输出 + git log

## Open Questions

- 无（原文范围与提交方式已经用户 2026-08-31 澄清确认）。
