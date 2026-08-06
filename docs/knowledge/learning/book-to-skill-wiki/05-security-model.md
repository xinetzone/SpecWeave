# 安全模型

## 文档→Agent 供应链攻击面

book-to-skill 的核心安全挑战是**文档→Agent 供应链（document→agent supply chain）**攻击面：不受信任的文档首先流入提取器，其内容进入 Agent 的上下文窗口；Agent 根据这些内容生成 Skill 文件；最终生成的 Skill 被加载到其他 Agent 中执行。这形成了一条完整的信任传递链，恶意文档可以通过不可见字符、注入指令等方式在多个环节实现攻击。

为了应对这一攻击面，book-to-skill 采用了**五层纵深防御体系（defense in depth）**，从文本提取到 Skill 生成再到 CI 门禁，每一层都有独立的安全控制。

---

## 五层防御体系

### Layer 1: Unicode 清理（Unicode Sanitization）

**核心目标**：在文本提取阶段移除用于**文档来源提示注入（document-borne prompt injection）**的不可见 Unicode 字符。

**实现位置**：[file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/sanitize.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/sanitize.py)

**防御机制**：
- **零宽字符（zero-width characters）**：移除 `U+200B`（零宽空格）、`U+200C`（零宽非连接符）、`U+200D`（零宽连接符）、`U+2060`（词连接符）、`U+FEFF`（零宽不换行空格/BOM）
- **Unicode 标签块（Unicode tag block）**：移除 `U+E0000` 到 `U+E007F` 范围内的所有标签字符

这些字符在视觉上不可见，但可以嵌入到正常文本中携带隐藏指令，绕过 Agent 的上下文审查。

**核心代码**：
```python
_ZERO_WIDTH_CODEPOINTS = frozenset({0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF})
_TAG_BLOCK_START = 0xE0000
_TAG_BLOCK_END = 0xE007F

def sanitize_extracted_text(text: str) -&gt; tuple[str, int]:
    """Remove invisible code points used for document-borne prompt injection."""
    kept: list[str] = []
    removed = 0
    for character in text:
        codepoint = ord(character)
        if (codepoint in _ZERO_WIDTH_CODEPOINTS
                or _TAG_BLOCK_START &lt;= codepoint &lt;= _TAG_BLOCK_END):
            removed += 1
            continue
        kept.append(character)
    return "".join(kept), removed
```

**调用时机**：所有解析器输出后、指标统计或写入 `full_text.txt` 之前（[utils.py:568](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L568-L568)）。

**附加安全措施**：
- 统计并报告移除的字符数量
- 如果清理后文本无可见内容，直接拒绝该源文件（防止全由隐写字符组成的恶意文档）

---

### Layer 2: DOCX XXE/Billion-Laughs 防护

**核心目标**：防止 DOCX 文件中的 XML 外部实体注入（XXE, XML External Entity）和 XML 实体扩展攻击（Billion Laughs/XML Entity Expansion）。

**实现位置**：[file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/docx.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/docx.py) 中的 `validate_docx_xml_safety` 函数（第 71-92 行）

**防御机制**：在解析 DOCX 内的任何 XML 文件之前，扫描所有 `.xml` 和 `.rels` 文件，检查是否包含：
- `&lt;!DOCTYPE`：DTD（文档类型定义）声明
- `&lt;!ENTITY`：实体声明

**核心代码**：
```python
def validate_docx_xml_safety(docx_path: str) -&gt; None:
    """Scan all XML files in the DOCX zip archive to prevent XML Entity Expansion (Billion Laughs) and XXE injections."""
    try:
        with zipfile.ZipFile(docx_path) as zf:
            for name in zf.namelist():
                if name.endswith(".xml") or name.endswith(".rels"):
                    xml_bytes = zf.read(name)
                    for encoding in ("utf-8", "utf-16", "utf-16le", "utf-16be", "utf-32"):
                        try:
                            content = xml_bytes.decode(encoding, errors="ignore").upper()
                        except LookupError:
                            continue
                        if "&lt;!DOCTYPE" in content or "&lt;!ENTITY" in content:
                            raise ExtractionError(
                                f"Security validation failed: XML file '{name}' in DOCX archive contains forbidden DTD or entity declarations."
                            )
    except zipfile.BadZipFile as e:
        raise ExtractionError(f"Invalid DOCX file: {e}")
```

**调用时机**：`extract_docx` 函数入口处（[docx.py:96](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/docx.py#L96-L96)），在任何 XML 解析之前执行。

---

### Layer 3: 子进程参数注入防护

**核心目标**：防止以 `-` 开头的文件名被外部命令（`pdftotext`、`pdfinfo`、`ebook-convert`）当作命令行 flag 解析，导致参数注入。

**实现位置**：
- PDF 解析器：[file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/pdf.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/pdf.py) 第 54 行、第 127 行
- Calibre 解析器：[file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/calibre.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/calibre.py) 第 15 行

**防御机制**：在调用子进程之前，使用 `os.path.abspath()` 将文件路径转换为绝对路径。绝对路径以盘符（Windows）或 `/`（Unix）开头，不会被误判为 flag。

**攻击场景示例**：如果用户有一个名为 `-output=/tmp/malware.txt` 的文件，直接传给 `pdftotext` 会被解析为设置输出路径的参数；转换为绝对路径后变为 `/path/to/-output=/tmp/malware.txt`，此时 `-` 不再位于参数开头，不会被当作 flag。

**核心代码**（以 pdftotext 为例）：
```python
def extract_with_pdftotext(pdf_path: str) -&gt; str | None:
    if not shutil.which("pdftotext"):
        return None
    try:
        pdf_path = os.path.abspath(pdf_path)  # 关键：路径绝对化
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        ...
```

同样的模式也应用于 `pdfinfo`（[pdf.py:127](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/pdf.py#L127-L127)）和 `ebook-convert`（[calibre.py:15](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/calibre.py#L15-L15)）。

---

### Layer 4: 生成 Skill 扫描（Generated-Skill Scan）

**核心目标**：在 Agent 生成 Skill 后、发布/加载前，进行**建议性扫描（advisory scan）**，检测提示注入、权限提升、数据外泄等可疑模式。

**实现位置**：[file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/scan_generated_skill.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/scan_generated_skill.py)

**调用时机**：SKILL.md 生成流程中的 Step 9.5。

#### 扫描范围

扫描以下文件：
- `SKILL.md`（主文件）
- `glossary.md`、`patterns.md`、`cheatsheet.md`（支持文件）
- `chapters/*.md`（所有分章文件）

#### 7 类 Prompt 注入检测规则

| 规则 ID | 模式描述 | 检测内容 |
|---------|----------|----------|
| `prompt.ignore_previous` | 指令覆盖短语 | 匹配 `ignore (all/any/the)? (previous/prior) (instructions/prompts/rules/messages)` |
| `prompt.disregard_system` | 系统指令覆盖 | 匹配 `disregard (the)? (system/developer)` |
| `prompt.role_reassignment` | 角色重分配 | 匹配 `you are now` |
| `prompt.fake_system_prefix` | 伪造系统消息前缀 | 匹配行首的 `system:` 或 `developer:`（带可选列表标记） |
| `prompt.system_tag` | 系统消息标签 | 匹配 `&lt;system&gt;`/`&lt;/system&gt;` 类标签 |
| `prompt.chat_template_tag` | 模型对话模板分隔符 | 匹配 `&lt;|im_start|&gt;`（ChatML）或 `[INST]`（Llama 格式） |
| `prompt.tool_call_tag` | 工具调用控制标记 | 匹配 `tool_call`/`tool-call`/`tool call` |

**正则表达式实现**：
```python
_CONTENT_RULES = (
    (
        "prompt.ignore_previous",
        re.compile(
            r"\bignore\s+(?:(?:all|any|the)\s+)?(?:previous|prior)\s+"
            r"(?:instructions?|prompts?|rules?|messages?)\b",
            re.IGNORECASE,
        ),
        "contains an instruction-override phrase",
    ),
    (
        "prompt.disregard_system",
        re.compile(r"\bdisregard\s+(?:the\s+)?(?:system|developer)\b", re.IGNORECASE),
        "contains a system-instruction override phrase",
    ),
    (
        "prompt.role_reassignment",
        re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
        "contains a role-reassignment phrase",
    ),
    (
        "prompt.fake_system_prefix",
        re.compile(r"^\s*(?:[-*]\s*)?(?:system|developer)\s*:", re.IGNORECASE),
        "contains a system-like message prefix",
    ),
    (
        "prompt.system_tag",
        re.compile(r"&lt;\s*/?\s*system\b[^&gt;]*&gt;", re.IGNORECASE),
        "contains a system-message tag",
    ),
    (
        "prompt.chat_template_tag",
        re.compile(r"&lt;\|\s*im_start\s*\|&gt;|\[\s*INST\s*\]", re.IGNORECASE),
        "contains a model chat-template delimiter",
    ),
    (
        "prompt.tool_call_tag",
        re.compile(r"\btool[_ -]?call\b", re.IGNORECASE),
        "contains a tool-call control token",
    ),
)
```

#### 其他检测项

除了 7 类注入模式外，扫描器还检查：

1. **残留不可见 Unicode（unicode.invisible）**：再次检查零宽字符和标签块，防止生成过程中引入
2. **数据外泄形状检测（tool.exfiltration_shape）**：
   - 匹配 `exfiltrate`/`exfiltration` 等外泄关键词
   - 同时匹配出站操作（`curl`/`wget`/`send`/`post`/`upload`/`transmit`/`http://`/`https://`）和敏感数据关键词（`.env`/`base64`/`secret`/`credential`/`api_key`/`api-key`）
3. **Frontmatter 权限检查**：
   - `frontmatter.allowed_tools`：检测是否声明或扩大工具权限
   - `frontmatter.model_invocation_enabled`：检测是否显式启用模型调用
4. **符号链接防护**：Skill 目录、SKILL.md、支持文件、chapters 目录都不能是符号链接（防止路径穿越和文件替换攻击）
5. **大小限制**：
   - 单文件最大 2MB
   - 总大小最大 20MB
   - 最多 1000 个 Markdown 文件
6. **编码检查**：所有文件必须是有效的 UTF-8（带 BOM 也接受）

**安全设计原则**：扫描结果只报告规则 ID 和文件位置，**绝不输出匹配的文本内容**，防止恶意文本通过扫描报告本身泄露或再次触发注入。

---

### Layer 5: CI 防护（Continuous Integration Hardening）

**核心目标**：在代码合并和发布流程中进行自动化安全门禁。

**实现位置**：GitHub Actions CI 配置

**防护组件**：
- **CodeQL**：GitHub 官方静态代码分析（SAST, Static Application Security Testing），检测代码中的安全漏洞
- **Bandit**：Python 专用安全 linter，HIGH 级别问题作为门禁阻断合并
- **Zizmor**：GitHub Actions 工作流安全扫描，防止 CI/CD 配置漏洞
- **依赖 CVE 审查**：在 PR（Pull Request）阶段审查依赖项的已知 CVE（Common Vulnerabilities and Exposures，通用漏洞披露）

---

## 纵深防御设计理念

五层防御遵循**纵深防御（defense in depth）**原则：

1. **分层独立**：每一层都可以独立工作，即使某一层被绕过，其他层仍能提供保护
2. **默认拒绝**：对于 DOCX DTD/ENTITY、符号链接等高风险特性，采用默认拒绝策略
3. **最小权限**：生成的 Skill 默认不声明额外工具权限，不启用模型调用
4. **可审计**：Unicode 清理报告移除数量，扫描器输出结构化发现，便于人工审查
5. **建议性扫描**：Skill 扫描是 advisory（建议性）而非阻断性的——规则故意设计得较宽泛，可能误报合法的 AI/LLM 主题文本，需要人工上下文审查；但所有发现都会被标记提醒人工复核

**重要安全边界声明**：book-to-skill 是本地转换工具，不进行网络上传、不回连、不运行网络服务。主要安全面是 Python 提取代码（解析不受信任的文档文件）和可选依赖安装过程。用户最佳实践是只转换自己信任且有权处理的文档。

---

**事实来源**：本章节基于以下事实编号 F-031, F-032, F-033, F-034, F-035
