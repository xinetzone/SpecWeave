# 《周易》著作 OKF 知识包 — 实施计划（tasks.md）

> 方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C。工作目录：`projects/awesome-okf-xs/doc/bundles/think/zhouyi/`。
> 任务依赖：T1→T2→T3/T4/T5/T6（可并行）→T7→T8→T9→T10→T11。

## Task 1: 建立分组与 bundle 骨架
- **Status**: pending
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `think/zhouyi/` 分组目录与 `zhouyi-works/` bundle 目录及五个子目录 `concepts/`、`text/`、`examples/`、`commentaries/`、`references/`
  - 生成分组索引 `think/zhouyi/index.md`（frontmatter：`okf_version: "0.2"`、`type: group`、title/description；含知识包列表表与 toctree）
  - 生成 bundle 根 `index.md`（`okf_version: "0.2"`、`type: OKF`、title/description/tags/version/source/generated/status/stale_after；快速导航 + Bundle 定位 + toctree 引用全部子目录与工作文档）
  - 生成 `log.md`（Creation 条目，日期 `2026-08-31`，倒序）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: 目录结构清单逐项存在（含五个子目录）；证据：Glob 文件列表
  - `rule` TR-1.2: 根 index.md frontmatter 含 `okf_version: "0.2"` 与 `type: OKF`，toctree 覆盖全部计划文档；证据：文件内容
- **Notes**: 内容文档可后建，toctree 先列全（T8 gates 前必须全部落盘）。

## Task 2: R 阶段 — 权威信源调研与事实采集（G1）
- **Status**: pending
- **Priority**: high
- **Depends On**: T1
- **Description**:
  - 网络调研核实四大出土文本系统关键事实：马王堆帛书《周易》（1973 长沙马王堆三号汉墓；经文《六十四卦》+《二三子问》《系辞》《衷》《要》《缪和》《昭力》；释文公布载体与整理本，如《文物》1984 释文、《长沙马王堆汉墓简帛集成》2014 中华书局）、上博楚简《周易》（1994 购藏、马承源主编《上博战国楚竹书（三）》2003 上海古籍、存 34 卦残简）、阜阳汉简《周易》（1977 双古堆一号汉墓、韩自强整理、《道家文化研究》第 18 辑）、王家台秦简《归藏》（1993 江陵王家台 15 号秦墓）
  - 核实历代注本事实：王弼/韩康伯注·孔颖达《周易正义》（阮刻十三经注疏）、李鼎祚《周易集解》、程颐《伊川易传》、朱熹《周易本义》、李光地等《周易折中》（康熙五十四年 1715）
  - 核实现代注本事实：高亨《周易古经今注》《周易大传今注》、李镜池《周易通义》《周易探源》、金景芳/吕绍刚《周易全解》、黄寿祺/张善文《周易译注》、刘大钧《周易概论》、廖名春帛书研究、李零相关论述
  - 核实经传结构事实：64 卦（上经 30/下经 34）、384 爻、用九用六、十翼 7 种 10 篇、《汉志》"人更三圣世历三古"、欧阳修《易童子问》、数字卦（张政烺）
  - 生成 `references/index.md` + 三份信源登记（权威底本与电子双源、出土文献整理本、注本分级与交叉引用），每条含可核查 resource
  - 生成 `facts.md`（F 编号连续、零因果推断词，通过 G1）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: facts.md 事实条目 ≥50 条，编号连续，抽检无"因为/导致/所以"因果词；证据：文件 + 关键词检索
  - `rule` TR-2.2: references 每条信源含可核查 resource（ISBN/出版社年份/机构 URL）；证据：文件内容
  - `rule` TR-2.3: 出土四系统、历代 5 注本、现代 ≥7 注家关键事实（年代/出版）经网络检索核实；证据：facts.md + log.md 检索记录

## Task 3: 概念文档（concepts/，6 文件）
- **Status**: pending
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - `concepts/index.md`
  - `01-zhouyi-overview.md`：《周易》名实（易/周易/易经）、经传结构、成书年代诸说（西周初/西周末/战国）、"人更三圣"传统说与现代研究
  - `02-text-systems.md`：今本系统（十三经注疏）、出土系统（帛书/楚简/阜阳简/王家台归藏）、古三易（连山/归藏/周易）存佚
  - `03-core-concepts.md`：阴阳、八卦（经卦）、六十四卦（别卦）、卦爻辞体例、象数、时位、中正当位、占筮与大衍之数
  - `04-shiyi-ten-wings.md`：十翼 7 种 10 篇结构、内容分工、孔子作十翼传统说与欧阳修以来辨伪
  - `05-yixue-lineage.md`：历代易学谱系——汉易象数（孟喜京房/郑玄/虞翻）、王弼义理、唐正义与集解、宋易图书与程朱、清代朴学（惠栋/张惠言）、现代学术
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 5 篇概念文档 + index 齐全，每篇 frontmatter 含非空 type；事实性论断带脚注溯源；证据：文件列表 + 抽查
  - `rubric` TR-3.2: 概念准确性与可读性；scale 1-5；anchors 1=硬伤/臆说，3=准确但平铺，5=准确且成体系、诸说并置；threshold ≥4；证据：独立审查

## Task 4: 经文全本（text/ 经文，3 文件）
- **Status**: pending
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - `text/index.md`（原文区索引，显式说明收录范围与底本/双源）
  - `text/jing-shang.md`：上经 30 卦（乾→离）卦辞爻辞全本
  - `text/jing-xia.md`：下经 34 卦（咸→未济）卦辞爻辞全本
  - 每卦格式统一：卦名（卦画）→ 卦辞 → 爻辞（初九/初六…上九/上六）；乾卦含用九、坤卦含用六
  - 文本以阮刻《十三经注疏·周易正义》为底本，经 ctext.org 与 zh.wikisource.org 双源逐字核对；异体/通假字从底本，不入传文
  - 文件尾附计数声明（卦数/爻数）与双源链接
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 64 卦齐全（上 30/下 34）、384 爻 + 用九用六无缺漏；证据：脚本化计数（卦名/爻题 grep 计数）
  - `rule` TR-4.2: 抽查 20 卦文本与 ctext/维基文库双源逐字一致；证据：双源比对记录写入 log.md
  - `rule` TR-4.3: frontmatter 合规、无传文窜入经文；证据：文件检查

## Task 5: 十翼选读与出土异文（text/ 传文，4 文件）
- **Status**: pending
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - `text/zhuan-xici.md`：《系辞上传》《系辞下传》全录（底本同经，双源核对）
  - `text/zhuan-shuogua.md`：《说卦传》全录
  - `text/zhuan-xu-za.md`：《序卦传》《杂卦传》全录
  - `text/unearthed-variants.md`：四大出土文本系统的存佚著录 + 关键异文/卦序选录（如帛书八宫卦序、帛书《系辞》无"大衍之数"章、上博简残字、阜阳简卜辞格式、王家台《归藏》佚文对应），所有释文片段标注整理本出处，残损显式说明
  - 《彖》《象》《文言》不在 text/ 全录，随 T6 乾坤精读完整呈现；text/index.md 显式声明选录范围并给出未录篇目的 ctext/维基文库链接
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 系辞上下/说卦/序卦/杂卦首尾完整（首末章句与底本一致）；证据：抽查 + 双源比对记录
  - `rule` TR-5.2: unearthed-variants 四系统条目齐全，每条释文有出版信源脚注，残损范围有显式声明；证据：文件检查
  - `rule` TR-5.3: text/index.md 选录范围声明存在且含未录篇目信源链接；证据：文件内容

## Task 6: 精读示例（examples/，3 文件）
- **Status**: pending
- **Priority**: high
- **Depends On**: T2, T4
- **Description**:
  - `examples/index.md`
  - `examples/qian-kun-jingdu.md`：乾、坤二卦经传合读——经文 +《彖传》《象传》（大象/小象）《文言传》完整收录 + ≥2 注家立场对照（如王弼义理 vs 高亨古经今注视角），爻题体例示范
  - `examples/key-gua-jingdu.md`：代表卦选讲——泰/否、谦、既济/未济等 4-6 卦，每卦经文摘引 + 卦义解读 + 注家分歧并置
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 乾坤精读含《彖》《象》《文言》对应乾坤的全部传文且与底本一致；证据：双源比对
  - `rubric` TR-6.2: 解读质量（注家立场可辨、分歧并置、不作单一断言）；scale 1-5；threshold ≥4；证据：独立审查

## Task 7: 权威解读三线（commentaries/，5 文件）
- **Status**: pending
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - `commentaries/index.md`
  - `unearthed-collation.md`：出土文献校注线——马王堆/上博/阜阳整理组与张政烺、于豪亮、廖名春、濮茅左等的校释成果与关键结论
  - `historical-commentaries.md`：历代注本线——王弼/韩康伯注、孔颖达正义、李鼎祚集解（汉易集成）、程颐《伊川易传》（义理）、朱熹《周易本义》（占筮本义）、李光地《周易折中》（集大成），各列成书背景、解易立场、代表观点短引
  - `modern-commentaries.md`：现代注本线——高亨、李镜池、金景芳/吕绍刚、黄寿祺/张善文、刘大钧、廖名春、李零等，各列著作出版信息与解易特色
  - `controversies.md`：争议显式化——①经文成书年代（西周初/西周末/战国）；②孔子与十翼关系；③经传关系与读法分歧；④卦序问题（通行序/帛书八宫序/先天后天）；⑤《周易》性质（占筮书/哲学书）；分歧并列不仲裁
- **Acceptance Criteria Addressed**: AC-5, AC-8
- **Test Requirements**:
  - `rule` TR-7.1: 三线专篇齐全；规定注家/学者全覆盖；每条含时代/出版信息与立场标签；证据：文件检查对照 facts.md
  - `rule` TR-7.2: controversies 含 ≥5 个争议点，每点 ≥2 种立场并置；证据：文件检查

## Task 8: 阅读指南、洞察与模式（usage/insights/patterns）
- **Status**: pending
- **Priority**: medium
- **Depends On**: T3, T4, T5, T6, T7
- **Description**:
  - `usage.md`：阅读路径指南（入门→进阶→研究三级）、注本选用决策树、怎么查卦、怎么读经传
  - `insights.md`：≥3 条四元组洞察（现象+根因+影响+建议，通过 G2），如"出土帛书卦序改写易学谱系认知""十翼非一人一时之作决定读法分层"等
  - `patterns.md`：≥2 个可复用模式（触发场景+核心步骤+反模式+迁移验证，通过 G3），如"经典双源逐字核对法""出土/传世文本存佚分层著录法"
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-8.1: insights 每条含四元组四要素；patterns 每条含四要素且迁移验证指向其他经典 bundle；证据：文件检查

## Task 9: 父级导航与总索引更新
- **Status**: pending
- **Priority**: high
- **Depends On**: T1
- **Description**:
  - 更新 `think/index.md`：分组导航表追加 zhouyi 行、toctree 追加 `zhouyi/index`、frontmatter description 与域简介补周易
  - 更新 `bundles/index.md`：frontmatter `total_bundles`/`groups` 计数、think 域节标题计数（29 束/18 组）与分组表行、生态概览与入门路径 mermaid 标签补 zhouyi（以 gates 三角校验输出为准，禁止手工估算）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-9.1: 三层导航（bundles 总索引→think 域→zhouyi 分组→bundle）可达；证据：链接检查
  - `rule` TR-9.2: gates.bundles 计数对账通过后计数行与脚本输出一致；证据：命令输出

## Task 10: V 阶段对抗审查 + gates 质量门
- **Status**: pending
- **Priority**: high
- **Depends On**: T3, T4, T5, T6, T7, T8, T9
- **Description**:
  - 对抗审查四视角攻击：①文献学者视角（史实/年代/出版信息硬伤）；②注家立场视角（有无把一家之言写成定论）；③文本校勘视角（经文脱漏/窜入/异体字）；④普通读者视角（阅读路径是否可用）
  - 修复发现的问题，结论记入 log.md 与 controversies 文档
  - 运行 `invoke gates.bundles`、`invoke gates.toctrees`、`invoke gates.utf8`（在 projects/awesome-okf-xs 目录），全部通过
  - frontmatter YAML 可解析性全量检查；文件零空文件核验
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-10.1: 三条 gates 命令退出码 0 且无 zhouyi 相关报错；证据：命令输出
  - `rule` TR-10.2: V 四视角审查记录成文，发现问题均已修复并留痕；证据：log.md 条目

## Task 11: 独立审查（Review 阶段，fresh context）
- **Status**: pending
- **Priority**: high
- **Depends On**: T10
- **Description**:
  - 委派全新上下文的只读独立审查员，按 review 合同核验全部 AC（结构合规、64 卦 384 爻完整、双源一致性、出土著录、三线注家、争议呈现、gates 证据、方法论闭环）
  - 生成 `.trae/specs/zhouyi-works-okf-bundle/review.md`；pass 则收尾，fail 则将 actionable findings 落为 Issue 任务回 T 阶段修复后重新审查
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `rule` TR-11.1: review.md 记录每个 checkpoint 证据与最终 Result；证据：review.md
  - `rubric` TR-11.2: AC-9 内容质量评分 ≥4；证据：审查员评分与抽查记录

## Task 12: C 阶段 — 暂存核验、快照双门与原子提交
- **Status**: pending
- **Priority**: high
- **Depends On**: T11
- **Description**:
  - 在 awesome-okf-xs 子模块内显式 `git add` 本任务目标文件（zhouyi/ 全部 + think/index.md + bundles/index.md），`git show :<path>` 核验暂存 blob 含目标内容
  - `git checkout-index -a --prefix=$prefix` 导出暂存态快照，在快照上跑 check-bundles-index.py + check-toctrees.py 双门（PowerShell 中 prefix 用变量形式）
  - 按 Conventional Commits 中文提交（如 `feat(bundles): 新增 think/zhouyi 周易著作知识包（经文全本+十翼选读+三线注本）`）
  - 主仓库确认子模块指针变更可见，`git status` 干净
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-12.1: 暂存 blob 核验通过、快照双门退出码 0；证据：命令输出
  - `rule` TR-12.2: 提交完成且 git log 可见单一职责提交；证据：git log/show

# Task Dependencies

- T2 依赖 T1；T3/T4/T5/T6/T7 依赖 T2（事实与信源先行）；T6 另依赖 T4（精读引经文）
- T8 依赖 T3-T7 全部完成；T9 依赖 T1（可与 T3-T7 并行收尾）
- T10 依赖 T3-T9；T11 依赖 T10；T12 依赖 T11（独立审查 pass）
- 并行建议：T3、T4、T5、T7 可按信息边界委派并行；T6 待 T4 经文落盘后进行
