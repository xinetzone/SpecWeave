---
type: Spec
title: 《医心方》束视觉设计稿（R 阶段产出）
source: seven-concepts 方法论 R（事实勘察）阶段委托任务（2026-09-02）
bundle: projects/awesome-okf-xs/doc/bundles/yixue/medicine/ishinpo-reading/
facts_basis: facts.md（F-001~F-079）
---

# 《医心方》束视觉设计稿（R 阶段产出）

> 本稿为纯调研+写作产出，未修改束内任何文件。全部事实表述以束内 `facts.md`（F-001~F-079）与各篇正文为唯一依据；配图仅作氛围表达，不承载事实断言；Mermaid 图中每个含事实的节点/边标签均附 F-编号回溯。

## 一、统一视觉规范

### 1. 配图风格

- **基调**：暖米色宣纸底、水墨淡彩（ink-wash with light warm color）、东亚古典书斋/卷轴氛围；平安~江户时代装束。
- **图内洁净**：绝对无文字、无字母、无书法字符、无印章、无水印（AI 文字渲染不可靠，所有卷面/书页一律留白，批注仅用抽象朱点朱圈）。
- **内容安全**：卷二十八房内主题只用闭卷、卷轴、书斋、药囊等含蓄意象，禁止任何露骨人物呈现；禁止现代物品穿帮（唯一例外：第 7 张"现代校读"主题允许现代影印本、放大镜、书签、台灯，但仍以水墨淡画笔触表现）。
- **统一风格短语**（每张 prompt 必须逐字包含）：`warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals`

### 2. 尺寸

- 束首页 hero（第 1 张）：`landscape_16_9`。
- 其余 8 张内容图：`landscape_4_3`。

### 3. 图片存放与引用

- 存放目录：`doc/_static/bundles/yixue/medicine/ishinpo-reading/images/`（位于 awesome-okf-xs 子模块内）。
- 引用语法（Markdown 图片 + 站点根绝对路径）：

```markdown
![中文alt](/_static/bundles/yixue/medicine/ishinpo-reading/images/<kebab-case文件名>.png)
```

- 文件名一律 kebab-case 英文 + `.png`。

### 4. Mermaid 安全六规则（施工时逐字符自检）

1. mermaid 块内**无空行**（一行空行都不能有）；
2. 含中文/空格/特殊字符的节点文本必须**双引号**包裹；
3. 节点 ID 全英文；
4. 文本换行用 `<br/>`；
5. subgraph 写法 `subgraph EN_ID ["中文标题"]`；边标签写法 `-->|"标签"|`（管道与引号之间**不得有空格**——`-->|"标签"|` 在 mermaid 11.4.1 下解析报错；虚线边同理 `-.->|"标签"|`）；
6. 围栏必须小写 ```` ```mermaid ````；单图节点 ≤20、subgraph 嵌套 ≤2 层；节点内不得出现圆括号以外的特殊语法字符（书名号《》在双引号内安全）。

> 施工说明：本稿为避免 Markdown 围栏冲突，mermaid 代码用**四反引号**围栏展示；插入束文档时改用标准三反引号 ```` ```mermaid ```` 围栏包裹代码体。每张图前配一句引导语，图后不做事实扩写（FR-4）。

## 二、配图清单（9 张）

| 序号 | 文件名 | 目标文档（相对束根） | 插入位置 | 中文 alt（≤30字） | 画面 prompt 要点（英文短语） |
|------|--------|----------------------|----------|-------------------|------------------------------|
| 1 | hero-heian-scroll-library.png | index.md | H1「# 《医心方》阅读教程」标题之后、首段正文前（全宽 hero） | 平安时代书库中堆积的汉文卷子本与油灯暖光 | Heian-period Japanese imperial library interior at night; tall wooden shelves stacked with hundreds of horizontal hand-copied Chinese scrolls (kansubon) in bundles; lacquered scroll boxes; a single bronze oil lamp casting warm amber glow; faint incense smoke; deep shadows; scrolls receding into depth; wide cinematic composition; serene scholarly atmosphere; 10th-century classical East Asian setting; no people; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; no modern objects; no electric light |
| 2 | lost-scroll-fragments-rejoined.png | concepts/00-why-ishinpo.md | 「## 辑佚价值：失而复得的中华医籍渊薮」小节标题之后、该节首段前 | 残破卷轴碎片在书案上重新拼合微光浮动 | torn fragments of ancient hand-scrolls lying on a wooden writing desk; broken pieces gently realigning and rejoining into whole scrolls as if by invisible hands; soft golden light glowing from the rejoined seams; dust motes in a beam of warm light; close-up still life; metaphor of lost texts rediscovered; no people; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; no modern objects |
| 3 | tanba-yasuyori-writing-scroll.png | concepts/01-author-and-book.md | H1 标题之后、首段正文前 | 老年平安朝医官在书斋伏案书写卷子 | elderly Heian-court medical officer with white beard; formal Japanese court dress: black lacquered kanmuri cap and sokutai robes with sash; seated at a low wooden writing desk in a classical study; holding a brush and writing on a long unrolled hand-scroll; stacked scrolls, brush stand, inkstone, oil lamp beside him; serene focused expression; three-quarter view; 10th-century Japan; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; blank scroll surfaces; no modern objects |
| 4 | qing-scholar-reconstructing-fragments.png | concepts/02-lost-books.md | 「### 叶德辉与《双梅景闇丛书》」小节标题之后、该节首段前 | 清代学者书斋中从类书勾稽残卷散页 | late-Qing-dynasty Chinese scholar in long robes and skullcap at a desk in a traditional book-lined study; comparing thread-bound encyclopedic books (leishu) with loose manuscript leaves and closed scrolls; carefully transcribing fragments onto paper with a brush; red editorial slips; tea bowl; shelves of thread-bound volumes; quiet restrained mood; scholarly reconstruction scene only; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; blank pages; no modern objects; no suggestive content; no figures in intimate scenes |
| 5 | manuscripts-crossing-the-sea.png | concepts/03-editions-transmission.md | H1 标题之后、首段正文前（篇首） | 卷轴乘船渡海，多份抄本随书籍之路传承 | allegorical scene of an ancient wooden trading ship sailing gentle misty waves at dawn; carrying sealed wooden scroll boxes and bundled hand-copied scrolls; distant coastlines of two lands; seabirds; warm golden morning light; the book-road across the sea metaphor; faint ghost-images of scrolls being copied along the route; traditional East Asian maritime scene pre-17th century; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; no modern ships; no modern objects |
| 6 | edo-igakkan-scholars-collating.png | concepts/04-research-lineage.md | H1 标题之后、首段正文前（篇首） | 江户时代儒医围绕卷子校勘影写 | Edo-period Japanese medical academy hall; several Confucian physicians in kimono and hakama with samurai-style topknots gathered around a long low table; comparing hand-copied scrolls and tracing facsimile copies with brushes; open scrolls and paper sheets; wooden academy interior with scroll boxes; focused collaborative atmosphere; 19th-century Edo setting; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; blank scroll surfaces; no modern objects |
| 7 | modern-desk-collated-editions.png | concepts/05-choosing-editions.md | H1 标题之后、首段正文前 | 现代书案上影印本校注本与放大镜书签 | modern scholar's reading desk rendered in warm ink-wash painterly style; cloth-bound modern facsimile reprint volumes and annotated critical editions stacked with a half-unrolled ancient scroll facsimile beside them; brass magnifying glass resting on an open book; paper bookmarks; reading glasses; a warm modern desk lamp; still life composition; 20th-century objects allowed but rendered in traditional ink-wash brushwork; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; blank book covers and spines |
| 8 | close-reading-with-vermilion-brush.png | examples/01-close-reading.md | H1 标题之后、首段正文前 | 古人展卷细读，手持朱笔批注 | ancient East Asian scholar in loose robes seated at a desk unrolling a long hand-scroll; holding a vermilion cinnabar-red brush and adding small abstract red dots and circle marks as reading punctuation on the scroll; brush rest, inkstone, oil lamp; intimate quiet study; scroll surface blank except for abstract red marks (no characters); restrained and tasteful; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; no modern objects; no suggestive content |
| 9 | reading-path-unrolling-scrolls.png | examples/02-reading-plan.md | H1 标题之后、首段正文前 | 书灯照亮层层展开的卷轴如山路径 | allegorical ink landscape: hand-scrolls unrolling layer upon layer to form a winding mountain path with stone steps ascending toward distant warm light; a small glowing reading lantern at the path's beginning; misty mountains in light ink wash; golden glow at the summit; metaphor of a staged reading journey; no people; warm rice-paper texture background, traditional East Asian ink-wash painting with light warm colors, classical manuscript aesthetic, soft warm lighting, no text, no letters, no calligraphy, no watermark, no seals; no modern objects |

> 图 4 与图 8 均服务于辑佚/房内主题，prompt 已显式加入 `closed scrolls / no suggestive content / no figures in intimate scenes / abstract red marks only` 等含蓄约束；图 7 是唯一允许现代物品者，prompt 已约束书脊封面留白（`blank book covers and spines`）防止 AI 生成乱码文字。

## 三、Mermaid 清单（5 张）

### M1：三十卷结构分组图

- **目标文档与插入位置**：`concepts/01-author-and-book.md`，§三「三十卷分类结构导读」内——"用广州中医药大学医史馆的分卷概要说"八条分块 bullet 列表之后、「### 几个值得留意的细目」之前。
- **引导语（图前一句）**：`下图按分卷概要把三十卷归纳为六个功能板块，便于先建立结构地图：`
- **图类型与方向**：flowchart TD（含 5 个 subgraph，嵌套 1 层；共 11 个节点）。

````mermaid
flowchart TD
    ROOT["《医心方》三十卷<br/>按部（门）分类"]
    subgraph G1 ["总论与针灸"]
        V1["卷一 治病大体部（总论）"]
        V2["卷二 忌针灸部（针灸孔穴）"]
    end
    subgraph G2 ["临床各科（卷三至卷十八）"]
        V3["卷三 中风部（风病证候治方）"]
        V418["卷四至卷十八<br/>头面四肢·脏腑·时行伤寒·外科"]
    end
    subgraph G3 ["服石（卷十九至卷二十）"]
        V1920["卷十九至卷二十<br/>服石部·服石诸病部"]
    end
    subgraph G4 ["妇产与小儿（卷二十一至卷二十五）"]
        V2124["卷二十一至卷二十四<br/>妇人·产妇·治无子（含占候）"]
        V25["卷二十五 小儿部"]
    end
    subgraph G5 ["养生诸术（卷二十六至卷三十）"]
        V2627["卷二十六至卷二十七<br/>延年断谷·大体养性"]
        V28["卷二十八 房内部"]
        V2930["卷二十九至卷三十<br/>饮食部·证类部（食疗本草）"]
    end
    ROOT --> V1
    ROOT --> V2
    ROOT --> V3
    ROOT --> V418
    ROOT --> V1920
    ROOT --> V2124
    ROOT --> V25
    ROOT --> V2627
    ROOT --> V28
    ROOT --> V2930
````

**事实依据表**：

| 节点/标签 | 事实依据 |
|-----------|----------|
| ROOT「三十卷按部（门）分类」 | F-011（文化厅解说"三十部門"） |
| 卷一 治病大体部（总论） | F-012（部名）、F-016（卷一为总论） |
| 卷二 忌针灸部（针灸孔穴） | F-012、F-016（卷二论针灸） |
| 卷三 中风部（风病证候治方） | F-012、F-016（卷三论风病证候及治风方剂） |
| 卷四至卷十八 头面四肢·脏腑·时行伤寒·外科 | F-016（卷四至卷十八分块概要）、F-012（各部名） |
| 卷十九至卷二十 服石部·服石诸病部 | F-012、F-016（论服丹石所致疾病方药） |
| 卷二十一至卷二十四 妇人·产妇·治无子（含占候） | F-012（卷二十一至卷二十四部名）、F-016（妇产科、治无子与占候） |
| 卷二十五 小儿部 | F-012、F-016 |
| 卷二十六至卷二十七 延年断谷·大体养性 | F-012、F-016、F-051（卷二十七养生总纲） |
| 卷二十八 房内部 | F-012、F-014（房内三十目）、F-017 |
| 卷二十九至卷三十 饮食部·证类部（食疗本草） | F-012、F-015（卷二十九调食、卷三十五谷五果五肉五菜）、F-016 |

### M2：亡佚→保存→辑佚链路图

- **目标文档与插入位置**：`concepts/02-lost-books.md`，「## 四、辑佚方法要点」之前（§三养生服食类结束之后）。
- **引导语（图前一句）**：`这些佚书从亡佚到重见天日的完整链路，可概括为下图：`
- **图类型与方向**：flowchart LR（7 个节点，无 subgraph）。

````mermaid
flowchart LR
    SRC["中国隋唐以前医籍<br/>《素女经》《小品方》《养生要集》等"]
    LOST["中土亡佚<br/>宋人已无由得见"]
    ISH["984年《医心方》征引保存<br/>不改原文·标明出处"]
    DIS["江户至清末学者发现<br/>杨守敬《日本访书志》著录"]
    JI1["叶德辉1908年<br/>《双梅景闇丛书》辑房中五书"]
    JI2["高文柱1983年<br/>《小品方辑校》"]
    JI3["现代辑本<br/>范行准《全汉三国六朝唐宋方书辑稿》等"]
    SRC -->|"中土亡佚"| LOST
    LOST -->|"佚文保存于海外写本"| ISH
    ISH -->|"清末回传后发现"| DIS
    DIS --> JI1
    DIS --> JI2
    DIS --> JI3
````

**事实依据表**：

| 节点/边标签 | 事实依据 |
|-------------|----------|
| SRC 隋唐以前医籍（《素女经》《小品方》《养生要集》） | F-023、F-030（素女经）、F-038（小品方）、F-052（养生要集） |
| LOST 中土亡佚/宋人已无由得见 | F-030（"宋人已无由得见"）、F-040（小品方北宋初失传） |
| ISH 984年《医心方》征引保存·不改原文·标明出处 | F-001（984撰进）、F-010（不改原文直接引用、均标明出处）、F-023、F-028 |
| DIS 江户至清末学者发现·杨守敬《日本访书志》 | F-071（杨守敬与《日本访书志》）、F-072（卷十著录安政本、辑佚价值最早系统认识） |
| JI1 叶德辉1908年《双梅景闇丛书》辑房中五书 | F-036（1908刊行、五种古籍）、F-017（1908年从卷二十八辑录） |
| JI2 高文柱1983年《小品方辑校》 | F-041（1982辑校、1983天津科技出版） |
| JI3 现代辑本·范行准《全汉三国六朝唐宋方书辑稿》 | F-047（2019年中医古籍出版社，11册）；另参 F-049（集验方辑本）、F-050（经心录辑本） |

### M3：版本流传谱系图

- **目标文档与插入位置**：`concepts/03-editions-transmission.md`，篇首总览——首段（"理解这条版本链……前提。"）之后、「## 一、三抄本源头」之前。
- **引导语（图前一句）**：`三抄本源头及其千年流变、清末回传路径如下图所示（虚线表示校勘关系，非传承关系）：`
- **图类型与方向**：flowchart TD（3 个 subgraph 分表三系统，嵌套 1 层；共 12 个节点）。

````mermaid
flowchart TD
    ORIGIN["984年成书<br/>抄录三部"]
    subgraph S1 ["御本系统（献皇室）"]
        GYOBON["御本（秘府本）"]
        NAKARAI["半井家本<br/>现存最古全帙·1984年国宝"]
        ANSEI["安政本<br/>1854年借校·1860年刊行"]
    end
    subgraph S2 ["宇治本系统（献藤原赖通）"]
        UJI["宇治本"]
        NINNA["仁和寺本（再抄本）<br/>残卷5帖·1952年国宝"]
        KANSEI["1791年宽政影写本<br/>医学馆·红叶山文库各一部"]
        UJILOST["宇治本原本已佚"]
    end
    subgraph S3 ["医家本系统（丹波家自留）"]
        IKA["医家本"]
        IKALOST["原本已佚<br/>多纪家旧藏零本存卷二·卷八"]
    end
    YANG["杨守敬清末访书<br/>《日本访书志》回传中国"]
    MODERN["现代整理本<br/>人卫1955影印·华夏1993与2023·学苑2001校释"]
    ORIGIN --> GYOBON
    ORIGIN --> UJI
    ORIGIN --> IKA
    GYOBON -->|"1145年点注·后赐半井家"| NAKARAI
    NAKARAI -->|"底本"| ANSEI
    UJI -->|"再抄本传世"| NINNA
    UJI -->|"原本失传"| UJILOST
    NINNA -->|"1791年影写两部"| KANSEI
    NINNA -.->|"主校本"| ANSEI
    IKA -->|"原件已佚"| IKALOST
    ANSEI -->|"清末回传"| YANG
    YANG --> MODERN
````

**事实依据表**：

| 节点/边标签 | 事实依据 |
|-------------|----------|
| ORIGIN 984年成书·抄录三部 | F-001、F-055 |
| 御本（秘府本，献皇室） | F-055 |
| 边标签「1145年点注·后赐半井家」 | F-056（天养二年/1145 点注校异）、F-057（御本下赐半井家，年代诸说并存故只标"后赐"） |
| 半井家本·现存最古全帙·1984年国宝 | F-058（最古且全三十卷齐备）、F-059（1984-06-06 指定国宝） |
| 安政本·1854年借校·1860年刊行 | F-060（安政元年1854借校、版木1859成、万延元年1860刊行） |
| 宇治本（献藤原赖通） | F-055（赖通/道通两说，图从正文主表述作藤原赖通） |
| 边「再抄本传世」→ 仁和寺本 | F-061（据宇治本誊抄的再抄本藏仁和寺） |
| 仁和寺本·残卷5帖·1952年国宝 | F-062（现存卷一、五、七、九、十共5帖；1952年指定国宝） |
| 边「1791年影写两部」→ 宽政影写本 | F-064（宽政三年/1791 多纪元悳等制影写本两部，分纳红叶山文库与医学馆） |
| 宇治本原本已佚 | F-061 |
| 虚线「主校本」（仁和寺本→安政本） | F-069（安政本以半井家本为底本、仁和寺本多纪家影写系统为主校本） |
| 医家本（丹波家自留）/ 原本已佚·零本存卷二卷八 | F-055、F-065 |
| 杨守敬清末访书·《日本访书志》回传 | F-071、F-072（卷十著录安政本）、F-073（还流统计） |
| 现代整理本（人卫1955·华夏1993/2023·学苑2001校释） | F-077 |

> 注：边「底本」与虚线「主校本」对应 F-069；下赐年代（1560/1573-1586/室町）诸说分歧，图中不标具体年份，只标"后赐半井家"，不做裁断。

### M4：研究史时间线图

- **目标文档与插入位置**：`concepts/04-research-lineage.md`，篇首——首段（"了解这条谱系……依据什么。"）之后、「## 一、多纪家考证学派与跻寿馆」之前。
- **引导语（图前一句）**：`《医心方》研究史上的关键年代节点与代表学者，按时间顺序梳理如下：`
- **图类型与方向**：flowchart LR（7 个节点，无 subgraph；T5 后分中日两支）。

````mermaid
flowchart LR
    T1["18世纪<br/>多纪家考证学派<br/>跻寿馆1765年·官办医学馆<br/>《医籍考》"]
    T2["1854-1860年<br/>安政本校刊群体<br/>多纪元坚·森立之等"]
    T3["1880年代<br/>杨守敬访日<br/>《日本访书志》著录回传"]
    T4["1908年<br/>叶德辉辑佚<br/>《双梅景闇丛书》"]
    T5["1985年<br/>马继兴引书统计<br/>204种·10877条"]
    T6["现代中国<br/>高文柱·沈澍农·范行准<br/>辑校与整理本"]
    T7["现代日本<br/>杉立义一写本52点八群<br/>真柳诚卷30与还流研究"]
    T1 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T5
    T5 --> T6
    T5 --> T7
````

**事实依据表**：

| 节点/标签 | 事实依据 |
|-----------|----------|
| T1 18世纪·多纪家考证学派·跻寿馆1765·医学馆·《医籍考》 | F-007（1765 跻寿馆、后改制官办医学馆）、F-075（多纪元德/元简/元胤/元坚三代著述，元胤《医籍考》，折衷派） |
| T2 1854-1860·安政本校刊群体·多纪元坚·森立之 | F-068（多纪元坚、元昕序，元琰、元佶续成）、F-069（校勘札记人员）、F-076（森立之在校刊职名中） |
| T3 1880年代·杨守敬访日·《日本访书志》 | F-071（访日收书三万余卷、《日本访书志》235种）、F-072 |
| T4 1908·叶德辉·《双梅景闇丛书》 | F-036 |
| T5 1985·马继兴·204种·10877条 | F-018（1985 年《日本医史学杂志》31:3；"又方""今案"单独计数口径）；280种等分歧口径不入图 |
| T6 现代中国·高文柱·沈澍农·范行准 | F-079（高文柱校点/校注本与《跬步集》、沈澍农符号标记研究与《医心方校释》）、F-047（范行准辑稿） |
| T7 现代日本·杉立义一52点八群·真柳诚卷30与还流 | F-066（1981年起十次报告、现存写本52点分八群；53种说不入图）、F-079（真柳诚卷30研究）、F-073（还流统计） |

### M5：四阶段阅读路线图

- **目标文档与插入位置**：`examples/02-reading-plan.md`，H1 之后——首段（"每个阶段给出目标……本包内相对路径。"）之后、「## 阶段一：总览入门（约 1 周）」之前。
- **引导语（图前一句）**：`四个阶段的阅读目标、周期与配套文档一览如下图：`
- **图类型与方向**：flowchart LR（4 个节点，无 subgraph）。

````mermaid
flowchart LR
    S1["阶段一 总览入门（约1周）<br/>00 为什么读《医心方》<br/>01 丹波康赖与成书始末"]
    S2["阶段二 结构地图（约1-2周）<br/>01 三十卷结构导读<br/>02 亡佚引书与辑佚价值"]
    S3["阶段三 辑佚文精读（约2-4周）<br/>01 辑佚文选读对照<br/>整理本通读卷二十七与卷二十八"]
    S4["阶段四 研究史进阶（按需·长期）<br/>03 版本流传与回传中国<br/>04 研究史与解读立场<br/>references 三份信源登记"]
    S1 --> S2
    S2 --> S3
    S3 --> S4
````

**事实依据表**（全部依据 `examples/02-reading-plan.md` 正文阶段一~四）：

| 节点 | 正文依据 |
|------|----------|
| S1 阶段一 总览入门（约1周）·00+01 | 「## 阶段一：总览入门（约 1 周）」：读 00 为什么读、01 丹波康赖与成书始末，浏览 facts 成书与结构 |
| S2 阶段二 结构地图（约1-2周）·三十卷结构+02亡佚引书 | 「## 阶段二：结构地图（约 1—2 周）」：对照 01 三十卷结构导读、记三个养生坐标、读 02 亡佚引书 |
| S3 阶段三 辑佚文精读（约2-4周）·辑佚文选读+整理本卷二十七/卷二十八 | 「## 阶段三：辑佚文精读（约 2—4 周）」：从 examples/01 三段示范入手、选整理本通读卷二十七卷二十八、练习回检 |
| S4 阶段四 研究史进阶（按需·长期）·03+04+references | 「## 阶段四：研究史进阶（按需，长期）」：读 03 版本流传、04 研究史，按需查三份信源登记 |

## 四、施工注意与风险提示

1. **M3 虚线边渲染**：`NINNA -.->|"主校本"| ANSEI` 为跨 subgraph 的虚线带标签边，mermaid 11.4.1 支持；施工后若个别渲染器不接受虚线+管道标签组合，降级写法为 `NINNA -. "主校本" .-> ANSEI`（语义不变）。
2. **图与 mermaid 的间距**：03、04、examples/02 三篇均为"篇首图（H1 后）+ 首段后 mermaid"，施工时确保图、引导段落、mermaid 块之间各有空行分隔，避免块粘连。
3. **分歧数据不裁断**：引书 204/280 种（F-018/F-020）、写本 52/53（F-066）、御本下赐年代（F-057）、982/984 撰进（F-008）等分歧，图中只采用束正文已采用的表述或径标"后""约"，未在图中裁断。
4. **AI 图不可承载事实**：9 张图均为写意氛围图，不模拟具体国宝文物（半井家本/仁和寺本实物不做复原），事实表达全部由 mermaid 与正文承担。
5. **子模块边界**：图片落盘与文档插入均在 `projects/awesome-okf-xs`（git submodule）内施工，提交走子模块流程；本设计稿存主权区 `.trae/specs/ishinpo-reading-figures/`。
6. **施工后验证**：mermaid 块插入后用 Sphinx 构建（`invoke build`，myst_fence_as_directive 渲染 mermaid 11.4.1）验证无 warning；图片路径验证无 "image not readable" 警告。
