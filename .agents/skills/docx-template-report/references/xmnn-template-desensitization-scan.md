---
id: xmnn-template-desensitization-scan
date: 2026-08-29
type: scan-report
source: "templates/xmnn-sdk-guide-template.docx"
---

# XMNN SDK 指南模板脱敏扫描报告

> **结论摘要**：脱敏模板 `xmnn-sdk-guide-template.docx` **通过全部品牌资产检查**——
> 零水印、零媒体、零品牌关键词、零个人身份元数据、零悬空关系引用。
> 存在 3 项**低危工具链痕迹**（编辑器版本标识等，不含个人/组织身份），不构成
> 品牌泄露，列为可选增强项。渲染产物中出现的品牌词全部来自演示 context 数据，
> 模板本身不含任何品牌内容。

---

## 1. 扫描对象与环境

| 对象 | 路径 | 角色 |
|---|---|---|
| 脱敏前基线 | 源文档 `XMNN_SDK_使用指南v1.1.0.docx`（1,429,610 字节） | 脱敏前对照，仅用于差异比对 |
| 受检模板 | `templates/xmnn-sdk-guide-template.docx`（30,826 字节） | 本次扫描主对象 |
| 对照模板 | `templates/tech-guide-template.docx`（37,349 字节） | python-docx 原生构建模板，作阴性对照 |
| 渲染产物 | `examples/output/xmnn-template-example.docx`（31,851 字节） | 模板渲染结果，验证占位消费与产物洁净度 |

- 扫描环境：Windows + Python 3.14（`py -3.14`），zipfile/OPC 全包遍历
- 扫描时间：2026-08-29
- 受检模板 SHA256（前 16 位）：`b1a529bdf379beda`
- 扫描工具：
  - 规范工具 [`examples/scan-brand-residue.py`](../examples/scan-brand-residue.py)（六查：关键词 / r:embed / media / w:pict / media 关系 / 悬空引用）
  - 深度取证：OPC 全包逐部件扫描（部件清单、关键词逐部件命中、图形水印计数、docProps 元数据转储、关系完整性、占位标签计数）

## 2. 检查项与判定标准

依据脱敏方案（副本基底法三脱敏：图形脱敏 → 敏感关系删除 → 元数据清空），
对六类品牌/身份资产逐项检查：

| # | 检查项 | 合格标准 |
|---|---|---|
| C1 | Xmsilicon VML 水印（`PowerPlusWaterMark` / `v:textpath` / `w:pict`） | 全包计数为 0 |
| C2 | `mc:AlternateContent` 装饰图形 | 正文/页眉页脚计数为 0（settings.xml 中的良性兼容标记除外，见 §5.1） |
| C3 | logo 与正文截图（`word/media/`、`r:embed`、rels 指向 media） | 媒体文件 0 个、嵌入引用 0 处 |
| C4 | 品牌关键词（Xmsilicon / 芯劢微 / 浙江 / XMNN / XMNPU / 新伟 / 水之心 / 张振宇 / 刘新伟） | 模板全部部件 0 命中 |
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
| `docProps/custom.xml` | 存在（base64 内含 WPS 用户 ID，详见[契约](xmnn-sdk-guide-template.md) §6.1） | 不存在 | ✅ C5 |
| `w:pict` 元素 | 5（3 处 VML 水印 + 装饰图形） | 0 | ✅ C1 |
| `PowerPlusWaterMark` | 3 | 0 | ✅ C1 |
| `v:textpath`（水印艺术字） | 3 | 0 | ✅ C1 |
| `mc:AlternateContent`（正文/页眉） | 6 | 0 | ✅ C2 |
| `w:drawing` 真实图形 | 18（logo + 截图） | 0（§5.1 说明字符串误报） | ✅ C2/C3 |
| `r:embed` 媒体引用 | 14 | 0 | ✅ C3 |
| 品牌关键词总命中 | document.xml 60 处、3 个页眉各 2–4 处、core.xml 4 处、customXml/item3.xml 3 处 | **全包 0 处** | ✅ C4 |
| `dc:creator`（作者） | `新伟 刘` | 空字符串 | ✅ C6 |
| `cp:lastModifiedBy`（修改者） | `水之心` | 空字符串 | ✅ C6 |
| `dc:title`（标题） | `芯劢微XMNPU工具链使用指南` | 空字符串 | ✅ C6 |
| `cp:lastPrinted`（打印时间） | `2025-12-26T08:07:00Z` | 已移除 | ✅ C6 |
| 悬空关系引用 | 无（源文档本身完整） | 无 | ✅ C7 |

### 3.1 源文档关键词命中分布（脱敏前实况）

| 部件 | 命中明细 |
|---|---|
| `word/document.xml` | 芯劢微×2、浙江×1、XMNN×48、XMNPU×1、新伟×2、张振宇×3、刘新伟×2 |
| `word/header1.xml` | Xmsilicon×1、PowerPlusWaterMark×1、芯劢微×1、浙江×1 |
| `word/header2.xml` | Xmsilicon×1、PowerPlusWaterMark×1 |
| `word/header3.xml` | Xmsilicon×1、PowerPlusWaterMark×1、芯劢微×1、浙江×1 |
| `docProps/core.xml` | 芯劢微×1、XMNPU×1、新伟×1、水之心×1 |
| `customXml/item3.xml` | XMNN×3（WPS 校对缓存） |

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

占位机制说明见[使用说明](xmnn-template-usage-guide.md) §5.1；传入 logo 时
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

对 `xmnn-template-example.docx`（由 [`examples/xmnn-render-example.py`](../examples/xmnn-render-example.py)
以演示 context 渲染）扫描：

- 结构：19 部件、0 媒体、0 customXml、0 `w:pict`、0 水印标记、无悬空引用；
- Jinja 占位标签 `{{ }}`：**0 残留**（全部正确消费）；
- 关键词命中：document.xml 与 header1/header3 中出现「芯劢微/浙江/XMNN/XMNPU/
  新伟/张振宇/刘新伟」——**全部来自演示 context**（封面 `doc_title`、
  `company`、修订表作者等字段），模板本身不含这些内容。

> **品牌中立责任边界**：模板保证"出厂零品牌"；渲染产物的品牌内容 100% 由
> 调用方传入的 context 决定。正式交付前应使用调用方自有数据渲染并运行
> [`scan-brand-residue.py`](../examples/scan-brand-residue.py) 自检，
> 确认产物品牌信息与交付主体一致。

## 7. 验收结论

| 资产类别 | 结论 |
|---|---|
| Xmsilicon VML 水印 / 装饰图形 | ✅ 已彻底移除 |
| logo 与正文截图媒体 | ✅ 12 个媒体全部排除，零 `r:embed` |
| 品牌关键词（组织名/产品名/人名） | ✅ 模板全包 0 命中 |
| WPS 校对缓存与用户 ID（customXml/custom.xml） | ✅ 部件已删除 |
| 作者/修改者/标题/打印时间元数据 | ✅ 身份字段已清空 |
| OPC 关系完整性 | ✅ 无悬空引用 |
| logo 按需注入占位 | ✅ 保留且渲染零残留 |
| 低危工具链痕迹 | ⚠️ 3 项（§5.1–5.2），不泄露身份，列可选增强 |

**总评：脱敏模板通过品牌中立验收，可作为高保真通用模板投入使用。**

## 8. 复现方法

```powershell
# 快速六查扫描（在技能目录下）
py -3.14 examples\scan-brand-residue.py

# 渲染产物后自检产物洁净度（脚本自动扫描输出文件）
py -3.14 examples\xmnn-render-example.py
```

深度全包取证（部件清单 / 关键词逐部件 / 元数据转储 / 关系完整性）方法见
[契约文档](xmnn-sdk-guide-template.md) §6 脱敏章节与
[排查指南](troubleshooting.md) §8 品牌资产残留排查。

## 9. 相关文档

| 文档 | 用途 |
|---|---|
| [xmnn-sdk-guide-template.md](xmnn-sdk-guide-template.md) | 模板数据契约与脱敏机制（维护者视角） |
| [xmnn-template-usage-guide.md](xmnn-template-usage-guide.md) | 模板使用说明（使用者视角，含 logo 注入） |
| [troubleshooting.md](troubleshooting.md) §8 | 品牌资产残留排查清单 |
| [../SKILL.md](../SKILL.md) | docx-template-report 技能入口 |
