# 提取器深度解析

Python 提取器是 book-to-skill 的确定性基础——它不理解内容，但它把各种格式的文档**可靠地**变成干净的纯文本。

## 格式支持矩阵

| 格式 | 首选提取器 | 备选1 | 备选2 | 必需外部依赖 |
|------|-----------|-------|-------|-------------|
| **PDF (technical)** | Docling | pdftotext 链 | — | docling (pip) |
| **PDF (text)** | pdftotext (poppler) | pypdf | pdfminer.six | poppler-utils (apt) 或 pip 包 |
| **EPUB** | ebooklib + bs4 | stdlib zipfile | — | ebooklib, beautifulsoup4 (pip) |
| **DOCX** | python-docx | stdlib ZIP/XML | — | python-docx (pip) |
| **HTML** | beautifulsoup4 | stdlib html.parser | — | beautifulsoup4 (pip) |
| **RTF** | striprtf | regex 兜底 | — | striprtf (pip) |
| **MOBI/AZW/AZW3** | Calibre ebook-convert | — | — | Calibre (外部应用) |
| **TXT/MD/RST/ADOC** | 内置读取 | — | — | 无 |

> 来源：[config.py#L16-L24](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L16-L24)、[dependencies.py#L14-L68](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L14-L68)

## 提取器优先级链设计

核心逻辑在 [extract_single_file()](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L410-L599) 中。设计原则是**最佳工具优先，链式优雅降级**：

### PDF 提取逻辑

```python
if extraction_mode == "technical":
    text = extract_with_docling(input_str)  # ~1.5s/页，保留表格/代码
    if not text:
        extraction_mode = "text"  # 自动降级到文本模式

if extraction_mode == "text":
    text = extract_with_pdftotext(input_str)  # 最快，系统级
    if not text:
        text = extract_with_pypdf(input_str)   # 纯Python
        if not text:
            text = extract_with_pdfminer(input_str)  # 最后兜底
```

**关键洞察**：
- technical 模式优先使用 Docling，因为它能保留 Markdown 表格和代码块（这对技术书籍至关重要）
- Docling 不可用时自动降级到文本模式链，不中断流程
- 每一步失败只打印信息并尝试下一个，不抛出异常（直到所有都失败）

### EPUB 提取逻辑

```python
text = extract_with_ebooklib(input_str)
if text and text.strip():
    method = "ebooklib"
else:
    text = extract_with_zipfile(input_str)  # stdlib兜底，无需任何依赖
    if text and text.strip():
        method = "zipfile"
    else:
        raise ExtractionError(...)
```

这种设计保证：**只要有 Python 标准库，EPUB 至少能提取出内容**（质量可能差一些，但不会完全失败）。

## Magic Bytes 文件类型探测

文件扩展名不可信时，提取器会读取文件头判断真实类型：

```python
with open(input_str, "rb") as f:
    header = f.read(8)
if header[:4] == b"%PDF":
    ext = ".pdf"
elif header[:2] == b"PK":  # ZIP-based formats
    with zipfile.ZipFile(input_str) as zf:
        names = set(zf.namelist())
        if "mimetype" in names and zf.read("mimetype").startswith(b"application/epub"):
            ext = ".epub"
        elif "word/document.xml" in names:
            ext = ".docx"
```

> 来源：[utils.py#L421-L448](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L421-L448)

## 多语言章节检测

这是提取器中最精巧的部分之一——支持 7 种语言的章节标题自动检测，代码在 [utils.py#L59-L124](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L59-L124)。

### 显式章节正则（核心模式）

```python
_EXPLICIT_CHAPTER = re.compile(
    r"^\s*(?:chapter|chapitre|kapitel|cap[ií]tulo|capitolo|hoofdstuk|ch\.?)\s*"
    r"(?:(\d{1,2})|(?P<roman>[IVXLCDMivxlcdm]{1,7}))\b(?P<rest>.*)$",
    re.IGNORECASE,
)
```

支持的语言关键词：

| 语言 | 关键词 | 示例 |
|------|--------|------|
| 英语 | Chapter, Ch. | Chapter 5, Ch. 3 |
| 法语 | Chapitre | Chapitre 5 |
| 德语 | Kapitel | Kapitel 5 |
| 西班牙语/葡萄牙语 | Capítulo / Capítulo | Capítulo 5 |
| 意大利语 | Capitolo | Capitolo 5 |
| 荷兰语 | Hoofdstuk | Hoofdstuk 5 |

### 罗马数字检测

```python
_ROMAN_HEAD = re.compile(r"^\s*([IVXLCDM]+)\s*[:.]\s+[A-ZÀ-Þ0-9\"“(]")
```

支持：`I: Loomings`、`II. The Carpet-Bag` 这类白鲸记风格的章节标题。

### 中文章节检测

```python
_CN_CHAPTER = re.compile(rf"^\s*第\s*([0-9{_FW_DIGITS}{_CN_NUM_CLASS}]+)\s*[章回卷节篇讲]")
_MD_CN_HEADING = re.compile(rf"^#{{1,6}}\s+第?\s*([{_FW_DIGITS}{_CN_NUM_CLASS}]+)\s*[·、.:：章回卷节篇讲]")
```

支持：
- 标准格式：`第三章`、`第 3 回`、`第十二节`、`第一讲`
- Markdown 标题：`## 一 · 缘起`、`## 第一讲`
- 全角数字：`第１章`（日文排版常见）
- 中文数字解析：[cn_numeral_to_int()](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L214-L229) 支持到 999

### 泰语和韩语章节检测

```python
# 泰语: บทที่ 3, ตอนที่ ๑๒
_TH_CHAPTER = re.compile(rf"^\s*(?:#{{1,6}}\s+)?(?:บทที่|ตอนที่|ภาคที่|บท|ตอน|ภาค)\s*([0-9{_TH_DIGITS}]+)\b")

# 韩语: 제1장 총칙, ## 제4장 근로시간과 휴식 (支持"의2"分支章节)
_KO_CHAPTER = re.compile(r"^\s*(?:#{1,6}\s+)?제\s*([0-9]+)\s*[장편절관](?:\s*의\s*[0-9]+)?(?:\s*$|[.:\-]|\s+\S)")
```

### 标题尾部验证（关键反误判机制）

这是防止把正文中的交叉引用误判为章节标题的关键：

```python
_HEADING_TAIL = re.compile(r"^\s*$|^\s*[.:\-—–]|^\s+[A-ZÀ-Þ0-9\"“(]")
```

**规则**：章节编号后面必须是：
- 行尾（下一行是标题）
- 标点符号（`. : - — –`）
- 大写字母开头的标题词（重音大写如 À-Þ 也支持德语等）

这样 `Chapter 6 explores...`（小写开头，是正文交叉引用）不会被误判为章节标题。

### 结构性章节检测（兜底）

当找不到"Chapter N"格式的标题时，回退到 Markdown/AsciiDoc/RST 结构性标题检测：
- [structural_chapter_count()](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L151-L211)
- 识别 ATX 标题（`# Title`、`== Section`）和 Setext 下划线标题（`===`/`---`）
- 跳过 fenced code block 内的标题
- 拒绝纯数字开头（`## 5 Setup`）和纯标点（`=====`表格边框）
- 选择"第一个有≥2个不同标题的层级"作为章节层级（处理"# 书名 / ## 章节"的常见布局）

## 依赖探测与优雅降级

[dependencies.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py) 实现了一套非常完善的可选依赖处理机制：

### 三态安装模式

```python
def normalize_install_mode(argv: list[str]) -> str:
    mode = os.environ.get("BOOK_SKILL_INSTALL_MISSING", "ask").lower()
    if "--no-install-missing" in argv:
        return "no"
    if "--install-missing" in argv:
        # 支持 --install-missing yes/no/ask 或 无参数=yes
        ...
    # 环境变量也可控制：1/true/y/yes → yes; 0/false/n/no → no
```

| 模式 | 行为 |
|------|------|
| `yes` | 自动安装缺失依赖 |
| `no` | 不安装，直接使用兜底 |
| `ask`（默认） | 交互询问用户（TTY时），非交互时用兜底 |

### 依赖组定义

每个格式的依赖都有明确的满足条件：

```python
{
    "label": "PDF (text-heavy)",
    "modules": ["pypdf", "pdfminer"],
    "any_of_modules": True,       # 任意一个Python包即可
    "any_tool_suffices": True,    # 系统工具或Python包任一即可
    "system": [("pdftotext", "poppler-utils", "sudo apt install poppler-utils")],
    "note": "any one of pdftotext / pypdf / pdfminer is enough",
}
```

满足语义：
- `any_tool_suffices=True`：任意一个工具（Python模块或系统命令）可用即可
- `any_of_modules=True`：列出的 Python 模块至少一个可用
- 否则：所有列出的模块和系统工具都必须可用

### --check 预检命令

`book-to-skill --check` 输出一份完整的环境报告：

```
book-to-skill — dependency check

  PDF (text-heavy)
      ✓ system: pdftotext (poppler-utils)
      → ready — any one of pdftotext / pypdf / pdfminer is enough

  PDF (technical: tables, code, formulas)
      ✗ python: docling
      → fallback available (install for best quality) — needed only for --mode technical
  ...
```

> 这个命令不需要处理任何文件，用户可以在转换书籍前先检查环境。

## 批量处理容错

单源失败是**非致命的**：

```python
for file_path in input_files:
    try:
        res = extract_single_file(file_path, extraction_mode, install_mode)
    except ExtractionError as exc:
        print(f"WARNING: Skipping {file_path.name}: {exc}", file=sys.stderr)
        errors.append((file_path, str(exc)))
        continue  # 继续处理下一个文件
    extracted_sources.append(res)
```

关键设计：
- 一个坏文件不会导致整个批处理失败
- 错误被收集，最后统一报告
- 只要至少有一个文件成功，就继续生成合并输出

## 输出格式

提取器在临时目录生成两个文件：

### full_text.txt

所有源合并，每个源用明确分隔符标记：

```
================================================================================
SOURCE: book.pdf (Path: /path/to/book.pdf)
================================================================================

<提取的文本内容>

================================================================================
SOURCE: notes.txt (Path: /path/to/notes.txt)
================================================================================

<笔记内容>
```

### metadata.json

```json
{
  "source_file": "Consolidated from multiple sources",
  "total_sources": 2,
  "pages": 244,
  "words": 45000,
  "estimated_tokens": 60000,
  "chapters_detected": 19,
  "has_toc": true,
  "sources": [
    {
      "filename": "book.pdf",
      "format": "pdf",
      "extraction_method": "pdftotext",
      "pages": 244,
      "estimated_tokens": 58000,
      "chapters_detected": 19
    }
  ]
}
```

---

**事实来源**：本章节基于以下事实编号 F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-034, F-035
