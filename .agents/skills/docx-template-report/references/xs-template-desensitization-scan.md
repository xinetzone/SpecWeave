---
id: xs-template-desensitization-scan
date: 2026-08-29
type: scan-report
source: "templates/xs-sdk-guide-template.docx"
---

# XS SDK 指南模板脱敏扫描报告

> **结论摘要**：脱敏模板 `xs-sdk-guide-template.docx` **通过全部品牌资产检查**——
> 零水印、零媒体、零品牌关键词、零个人身份元数据、零悬空关系引用。
> 存在 3 项**低危工具链痕迹**（编辑器版本标识等，不含个人/组织身份），不构成
> 品牌泄露，列为可选增强项。渲染示例演示数据已全部虚构中立化（公司/人员/命令
> 均为假数据），渲染产物品牌词零命中；模板本身不含任何品牌内容。

---

## 1. 扫描对象与环境

| 对象 | 路径 | 角色 |
|---|---|---|
| 脱敏前基线 | 源文档（企业 SDK 使用指南，位于本地 `.chaos` 工作区，不入库；1,429,610 字节） | 脱敏前对照，仅用于差异比对 |
| 受检模板 | `templates/xs-sdk-guide-template.docx`（30,826 字节） | 本次扫描主对象 |
| 对照模板 | `templates/tech-guide-template.docx`（37,349 字节） | python-docx 原生构建模板，作阴性对照 |
| 渲染产物 | `examples/output/xs-template-example.docx`（31,781 字节） | 模板渲染结果，验证占位消费与产物洁净度 |

- 扫描环境：Windows + Python 3.14（`py -3.14`），zipfile/OPC 全包遍历
- 扫描时间：2026-08-29（模板更名后于 2026-08-30 复扫，结论不变）
- 受检模板 SHA256（前 16 位）：`b1a529bdf379beda`（更名仅改文件名，模板二进制内容不变）
- 扫描工具：
  - 规范工具 [`examples/scan-brand-residue.py`](../examples/scan-brand-residue.py)（六查：关键词 / r:embed / media / w:pict / media 关系 / 悬空引用）
  - 深度取证：OPC 全包逐部件扫描（部件清单、关键词逐部件命中、图形水印计数、docProps 元数据转储、关系完整性、占位标签计数）

## 2. 检查项与判定标准

依据脱敏方案（副本基底法三脱敏：图形脱敏 → 敏感关系删除 → 元数据清空），
对六类品牌/身份资产逐项检查：

| # | 检查项 | 合格标准 |
|---|---|---|
| C1 | VML 水印文字与元素（原品牌英文标识水印文字 / `PowerPlusWaterMark` / `v:textpath` / `w:pict`） | 全包计数为 0 |
| C2 | `mc:AlternateContent` 装饰图形 | 正文/页眉页脚计数为 0（settings.xml 中的良性兼容标记除外，见 §5.1） |
| C3 | logo 与正文截图（`word/media/`、`r:embed`、rels 指向 media） | 媒体文件 0 个、嵌入引用 0 处 |
| C4 | 品牌关键词（检测词表共 10 个：原品牌英文标识 / 公司简称 / 地域名 / 原产品代号 2 个 / 人员名与昵称 / 水印元素名；完整词表以 [`scan-brand-residue.py`](../examples/scan-brand-residue.py) KEYWORDS 为准） | 模板全部部件 0 命中 |
| C5 | WPS 私域数据（`customXml/` 校对缓存、`docProps/custom.xml` 内含 base64 WPS 用户 ID） | 部件不存在 |
| C6 | 核心元数据（`docProps/core.xml`：作者真名、修改者、标题、打印时间） | 身份字段为空 |
| C7 | OPC 关系完整性（`r:id`/`r:embed`/`r:link` 引用必须在对应 .rels 中存在） | 无悬空引用 |
| C8 | logo 占位标签（`{{ header_logo }}` / `{{ cover_logo }}`） | 模板中保留；渲染产物中 0 残留 |

## 3. 脱敏前后对照（源基线 → 受检模板）

| 指标 | 脱敏前源文档 | 脱敏后模板 | 判定 |
|---|---|---|---|
| 文件体积 | 1,429,610 字节（约 1.40 MB） | 30,826 字节（约 30 KB，降至 2.2%） | ✅ |
| 包部件总数 | 51 | 19 | ✅ |
| `word/media/` 媒体文件 | 12 个（11 张 PNG + 1 张 JPEG，含 logo 与正文截图） | 0 个 | ✅ C3 |
| `customXml/` 部件 | 11 个（item1–3 校对/形状缓存） | 0 个 | ✅ C5 |
| `docProps/custom.xml` | 存在（base64 内含 WPS 用户 ID，详见[契约](xs-sdk-guide-template.md) §6.1） | 不存在 | ✅ C5 |
| `w:pict` 元素 | 5（3 处 VML 水印 + 装饰图形） | 0 | ✅ C1 |
| `PowerPlusWaterMark` | 3 | 0 | ✅ C1 |
| `v:textpath`（水印艺术字） | 3 | 0 | ✅ C1 |
| `mc:AlternateContent`（正文/页眉） | 6 | 0 | ✅ C2 |
| `w:drawing` 真实图形 | 18（logo + 截图） | 0（§5.1 说明字符串误报） | ✅ C2/C3 |
| `r:embed` 媒体引用 | 14 | 0 | ✅ C3 |
| 品牌关键词总命中 | document.xml 60 处、3 个页眉各 2–4 处、core.xml 4 处、customXml/item3.xml 3 处 | **全包 0 处** | ✅ C4 |
| `dc:creator`（作者） | 源文档作者真名（人员姓名） | 空字符串 | ✅ C6 |
| `cp:lastModifiedBy`（修改者） | 源文档修改者昵称（人员昵称） | 空字符串 | ✅ C6 |
| `dc:title`（标题） | 含原品牌标识与产品代号的文档标题 | 空字符串 | ✅ C6 |
| `cp:lastPrinted`（打印时间） | `2025-12-26T08:07:00Z` | 已移除 | ✅ C6 |
| 悬空关系引用 | 无（源文档本身完整） | 无 | ✅ C7 |

### 3.1 源文档关键词命中分布（脱敏前实况，按词类归并）

> 下表对命中按词类归并计数（公司简称/地域名/原产品代号/人员名/水印标识），
> 不再逐字罗列敏感词原文；逐字词表以扫描工具 KEYWORDS 为准。

| 部件 | 命中明细（词类 × 次数） |
|---|---|
| `word/document.xml` | 公司简称×2、地域名×1、原产品代号×49、人员名×7 |
| `word/header1.xml` | 水印英文标识×1、PowerPlusWaterMark×1、公司简称×1、地域名×1 |
| `word/header2.xml` | 水印英文标识×1、PowerPlusWaterMark×1 |
| `word/header3.xml` | 水印英文标识×1、PowerPlusWaterMark×1、公司简称×1、地域名×1 |
| `docProps/core.xml` | 公司简称×1、产品标识×1、人员名/昵称×2 |
| `customXml/item3.xml` | 原产品代号×3（WPS 校对缓存） |

> 水印位于三个页眉部件中——若只扫描 `word/document.xml` 会完全漏检，
> 这正是深度扫描遍历全包所有 `.xml`/`.rels` 部件的原因。

## 4. 受检模板扫描结果明细

### 4.1 包结构（19 部件）

```
[Content_Types].xml、_rels/.rels、
word/document.xml、word/settings.xml、word/styles.xml、
word/numbering.xml、word/theme/theme1.xml、
word/fontTable.xml、word/webSettings.xml、
word/header1.xml、word/header2.xml、word/header3.xml、
word/footer1.xml、word/footer2.xml、word/footer3.xml、
word/_rels/document.xml.rels（+ 页眉/页脚各自 .rels）、
docProps/core.xml、docProps/app.xml
```

- **无** `word/media/` 目录、**无** `customXml/` 目录、**无** `docProps/custom.xml`
- 样式表（86 样式）、多级编号链、主题色、页眉页脚布局均完整保留（高保真基础）

### 4.2 关键词扫描

对 10 个品牌/身份关键词遍历包内全部 `.xml`/`.rels` 部件：**0 命中**。
规范工具 `scan-brand-residue.py` 同步输出「关键词残留: 无」。

### 4.3 水印与图形

| 标记 | 正文 | 三个页眉 | 三个页脚 | 判定 |
|---|---|---|---|---|
| `PowerPlusWaterMark` | 0 | 0 | 0 | ✅ |
| `v:textpath` | 0 | 0 | 0 | ✅ |
| `w:pict`（VML 图形） | 0 | 0 | 0 | ✅ |
| 真实 `w:drawing` 图形 | 0 | 0 | 0 | ✅ |
| `r:embed`（媒体嵌入） | 0 | 0 | 0 | ✅ |

### 4.4 元数据（`docProps/core.xml`）

| 字段 | 值 | 判定 |
|---|---|---|
| `dc:creator`（作者） | 空 | ✅ 已清空 |
| `cp:lastModifiedBy`（最后修改者） | 空 | ✅ 已清空 |
| `dc:title`（标题） | 空 | ✅ 已清空 |
| `dc:subject` / `dc:description` / `cp:category` | 空 | ✅ 已清空 |
| `cp:lastPrinted`（打印时间戳） | 不存在 | ✅ 已移除 |
| `dc:keywords` | 不存在 | ✅ |
| `cp:revision`（修订计数） | `59` | ⚠️ 低危痕迹，见 §5.2 |

`docProps/custom.xml`（WPS 自定义属性，含 base64 用户 ID）：**部件已删除** ✅

### 4.5 OPC 关系完整性

逐部件校验 `r:id`/`r:embed`/`r:link` 引用与对应 `.rels` 声明：**无悬空引用**，
Word 打开不会触发「文档已损坏/需要修复」。

### 4.6 logo 占位与渲染行为

| 检查点 | 模板 | 渲染产物（未传 logo） |
|---|---|---|
| `{{ cover_logo }}`（封面位） | document.xml 保留 1 处 | 0 残留（渲染为空，位置留空） |
| `{{ header_logo }}`（页眉位） | 页眉保留 2 处 | 0 残留（渲染为空，位置留空） |
| `word/media/` 文件 | 0 | 0（不传 InlineImage 时产物零媒体） |

占位机制说明见[使用说明](xs-template-usage-guide.md) §5.1；传入 logo 时
python-docx 在包层去重为共享 image part，页眉与封面共用同一媒体部件。

## 5. 深度扫描的三个良性发现（低危，不阻断结论）

深度取证会报出两个"形似残留"的字符串命中，经人工复核均为**误报或良性痕迹**，
此处完整披露以保证报告可审计：

### 5.1 settings.xml 的 `AlternateContent`/`drawing` 字符串（误报）

- 字符串 `AlternateContent` 在 `word/settings.xml` 出现 2 次（一开一闭），
  实际是一个 `<mc:AlternateContent>` 包裹的
  `<wpsCustomData:typoFeatureVersion val="1"/>`——WPS 写入的**排版特性版本
  兼容标记**，无文本、无图片、无品牌内容，Word 打开时自动忽略。
- 字符串 `<w:drawing` 出现 2 次，实际是
  `<w:drawingGridHorizontalSpacing>` 与 `<w:drawingGridVerticalSpacing>`
  （文档网格设置），**不是图形元素**。
- 判定：非品牌资产，无需处理。

### 5.2 `docProps/app.xml` 与 `cp:revision` 工具链痕迹（低危）

- `docProps/app.xml` 的 `Application` 字段仍为
  `WPS Office_12.1.0.28043_<GUID片段>`——编辑器版本与安装实例标识，
  **不含个人姓名、组织名或文档内容**；
- `docProps/core.xml` 的 `cp:revision` 为 `59`（编辑次数计数），无身份信息。

风险评级：**低**。不泄露任何个人或组织身份，仅暴露"该文档曾由 WPS 编辑"这一
工具链事实。如未来交付场景要求编辑器指纹也完全中立，可在渲染后增加一步
重写 `app.xml` Application 与清空 `cp:revision`（列为可选增强，不影响本次
脱敏验收）。

### 5.3 对照模板 tech-guide 的 customXml（阴性对照说明）

`tech-guide-template.docx` 含 `customXml/item1.xml`，内容为空的 APA 书目
容器（`<b:Sources ... StyleName="APA"/>`，无任何条目），系 python-docx
默认模板的标准产物；其 `dc:creator` 为 `python-docx`、`Application` 为
`Microsoft Macintosh Word`，均为工具生成标记，非品牌资产。对照模板关键词、
媒体、水印扫描全部为 0，与受检模板结论一致。

## 6. 渲染产物扫描与品牌责任边界

对 `xs-template-example.docx`（31,781 字节，由
[`examples/xs-render-example.py`](../examples/xs-render-example.py)
以**全部虚构中立**的演示 context 渲染）扫描：

- 结构：19 部件、0 媒体、0 customXml、0 `w:pict`、0 水印标记、无悬空引用；
- Jinja 占位标签 `{{ }}`：**0 残留**（全部正确消费）；
- 品牌关键词全包扫描：**0 命中**。自 v1.3.4 品牌中立化更名起，演示 context
  全部采用虚构中立数据——文档标题为「XS SDK 用户使用指南」，公司名为
  「示例科技有限公司」，人员名为「张三/李四/王五」，命令与包名为
  `xsenv`/`xs.yaml`/`xs_sdk`/`xs:latest`，均不对应任何真实组织或产品；
  规范工具 `scan-brand-residue.py` 对渲染产物输出「关键词残留: 无」。
  （更名前的历史演示数据曾含真实品牌词，渲染产物命中均来自演示 context
  而非模板本身；该问题已随演示数据中立化彻底消除。）

> **品牌中立责任边界**：模板保证"出厂零品牌"；渲染产物的品牌内容 100% 由
> 调用方传入的 context 决定。技能自带示例虽已使用虚构中立数据，正式交付时
> 仍应使用调用方自有数据渲染并运行
> [`scan-brand-residue.py`](../examples/scan-brand-residue.py) 自检，
> 确认产物品牌信息与交付主体一致。

## 7. 验收结论

| 资产类别 | 结论 |
|---|---|
| VML 品牌水印 / 装饰图形 | ✅ 已彻底移除 |
| logo 与正文截图媒体 | ✅ 12 个媒体全部排除，零 `r:embed` |
| 品牌关键词（组织名/产品名/人名） | ✅ 模板全包 0 命中 |
| WPS 校对缓存与用户 ID（customXml/custom.xml） | ✅ 部件已删除 |
| 作者/修改者/标题/打印时间元数据 | ✅ 身份字段已清空 |
| OPC 关系完整性 | ✅ 无悬空引用 |
| logo 按需注入占位 | ✅ 保留且渲染零残留 |
| 渲染产物品牌词自检 | ✅ 演示数据虚构中立化后全包 0 命中（§6） |
| 低危工具链痕迹 | ⚠️ 3 项（§5.1–5.2），不泄露身份，列可选增强 |

**总评：脱敏模板通过品牌中立验收，可作为高保真通用模板投入使用。**

## 8. 复现方法

```powershell
# 快速六查扫描（在技能目录下）
py -3.14 examples\scan-brand-residue.py

# 渲染产物后自检产物洁净度（37 项断言 + 自动产物扫描）
py -3.14 examples\xs-render-example.py
```

深度全包取证（部件清单 / 关键词逐部件 / 元数据转储 / 关系完整性）方法见
[契约文档](xs-sdk-guide-template.md) §6 脱敏章节与
[排查指南](troubleshooting.md) §8 品牌资产残留排查。

## 9. 相关文档

| 文档 | 用途 |
|---|---|
| [xs-sdk-guide-template.md](xs-sdk-guide-template.md) | 模板数据契约与脱敏机制（维护者视角） |
| [xs-template-usage-guide.md](xs-template-usage-guide.md) | 模板使用说明（使用者视角，含 logo 注入） |
| [troubleshooting.md](troubleshooting.md) §8 | 品牌资产残留排查清单 |
| [../SKILL.md](../SKILL.md) | docx-template-report 技能入口 |
