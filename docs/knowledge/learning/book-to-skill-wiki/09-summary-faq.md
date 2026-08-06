# 总结与常见问题

## 核心要点总结

1. **双层架构设计**：book-to-skill 采用 Python 确定性提取器 + SKILL.md 规范驱动生成器的双层架构，提取层负责格式解析和文本清理，生成层由 Agent 按可执行规范完成结构化提炼。

2. **核心价值：编译时付费**：一次性支付编译成本，运行时按需加载，实现 24×-51× token 节省，彻底消除 Discovery Loop Tax（每次查询都重复导航和压缩的隐性成本）。

3. **与 RAG 互补而非替代**：RAG 在查询时工作，适合宽而浅的图书馆检索（"找提到 X 的部分"）；book-to-skill 在编译时工作，适合窄而深的单书精通（"这是作者构建的 12 个框架"）。RAG 索引书架，book-to-skill 精通一本书。

4. **SKILL.md 是可执行规范**：这是架构核心——整个转换流程定义在 Markdown 规范中，包含步骤、预算、质量规则，Agent 作为规范解释器执行，而非硬编码在 Python 逻辑中。

5. **五层纵深防御安全模型**：Unicode 注入清理 → 解析器级 XXE 防护 → 参数注入防护 → 生成后提示注入扫描 → CI SAST，是文档→Agent 供应链安全的参考实现。

6. **多语言章节检测**：支持阿拉伯数字、罗马数字、中文、韩文、泰文及多种欧洲语言的章节标题识别，并配有反误报机制，避免将目录、索引误判为章节。

7. **优雅降级策略**：每个格式都有 stdlib fallback（EPUB → zipfile、DOCX → ZIP/XML、HTML → html.parser），依赖缺失时自动降级而非失败，提供 `--check` 预检模式。

8. **两种安装方式**：支持作为 Agent Skill（git clone 到 skills 目录获得 `/book-to-skill` 斜杠命令）或独立 CLI（pip install 仅安装提取引擎），满足不同使用场景。

9. **适用场景边界**：最适合窄而深的知识（单本书、内部文档簇、研究资料集），不适合宽而浅的图书馆检索、一次性阅读材料、受版权保护的逐字引用场景。

10. **五大可复用工程模式**：编译时付费架构、规范驱动生成、文档供应链分层防御、优雅降级与依赖探测、Token 预算自适应矩阵，均可迁移到 SpecWeave 和其他 Agent 工具项目。

---

## 常见问题解答（FAQ）

### Q1: book-to-skill 和 RAG 有什么区别？我该用哪个？

**A**: 它们解决不同问题，是互补关系而非竞争关系：

| 维度 | RAG | book-to-skill |
|------|-----|---------------|
| 工作时机 | 查询时（Query-time） | 编译时（Compile-time） |
| 核心动作 | 分块→Embedding→相似向量检索 | 深度提取作者的命名框架、决策规则、反模式 |
| 回答方式 | "这里是与你查询相近的文本块" | "这是作者构建的 N 个框架，随时可用" |
| 适用场景 | 宽而浅：几十本书的图书馆，"找提到 X 的部分" | 窄而深：一本书或紧密资料簇，工作时反复应用 |

**选择指南**：
- 需要跨几十本书检索特定关键词 → 用 RAG（如 CandleKeep、NotebookLM）
- 需要反复深入应用某本书的框架和方法论 → 用 book-to-skill
- 两者可以结合：RAG 帮你定位到哪本书，book-to-skill 帮你精通那本书

---

### Q2: 支持哪些文档格式？需要安装什么依赖？

**A**: 支持 7 大类格式，依赖探测采用"最佳→可用→stdlib fallback"策略：

| 格式 | 最佳工具 | 安装命令 | Fallback |
|------|---------|---------|----------|
| PDF（文本类） | pdftotext (poppler) | `apt install poppler-utils` | pypdf → pdfminer.six |
| PDF（技术类） | docling | `pip install docling` | （无，技术类需保留表格/代码块） |
| EPUB | ebooklib + bs4 | `pip install ebooklib beautifulsoup4` | stdlib zipfile |
| DOCX | python-docx | `pip install python-docx` | stdlib ZIP/XML |
| HTML | beautifulsoup4 | `pip install beautifulsoup4` | stdlib html.parser |
| RTF | striprtf | `pip install striprtf` | regex 兜底 |
| MOBI/AZW/AZW3 | Calibre ebook-convert | https://calibre-ebook.com/download | （无，必须安装） |
| TXT/MD/rst/AsciiDoc | 内置 | — | — |

运行 `python3 scripts/extract.py --check` 可一键检查所有依赖状态并给出安装命令。

---

### Q3: 转换一本书需要多少成本？需要多久？

**A**: 基于实测数据（Claude Sonnet 4.5，$3/$15 per MTok）：

| 书籍 | 页数 | 提取 tokens | 章节数 | 预估成本 | 提取时间 |
|------|-----:|------------:|-------:|---------:|---------|
| Think Python 2 | 244 | 119K | 19 | ~$0.88 | pdftotext: 0.1s |
| Working Backwards | 371 | 175K | 10 | ~$0.96 | pdftotext: ~0.2s |
| Pro Git | 501 | 229K | — | ~$1.23 | pdftotext: ~0.3s |
| 技术类书籍（Docling） | ~300 | ~150K | ~15 | ~$1.00 | Docling: ~1.5s/page |

**关键**：这是一次性成本。相比每次对话都消耗 100K+ tokens（上下文 dump），转换 10 次对话就回本。技术类书籍用 Docling 较慢但保留表格和代码块，文本类书籍用 pdftotext 几乎瞬间完成。

---

### Q4: 大上下文窗口（1M tokens）还需要 book-to-skill 吗？

**A**: 需要。更大的窗口改变了什么"放得下"，但不改变什么是"聪明的"：

1. **按 token 付费，按次计费**：1M 窗口不意味着 token 免费，而是让大额账单成为可能。Skill 每次只加载 KB 级内容而非 MB 级。

2. **填充度越高，召回越差**：模型在近满上下文里检索特定事实的精度会下降（"中间遗忘"问题）。1K 精心提炼的章节比 200K 原始文本更适合回答特定问题。

3. **窗口 ≠ 结构**：整本书在上下文里仍然是原始文本，模型每轮都要重新解析。Skill 交付的是预先提取好的框架——推理，而非检索。

**建议**：大窗口用于一次性阅读、再也不会回看的材料；book-to-skill 用于你会反复查阅的深度知识。

---

### Q5: 可以转换扫描版 PDF 吗？

**A**: 目前不直接支持。扫描版 PDF 本质是图片，需要先经过 OCR 转换为可搜索的文本：

1. 使用 OCR 工具（如 Adobe Acrobat、Tesseract、Docling 内置 OCR）将扫描版 PDF 转为带文本层的 PDF
2. 或者先用专门的 OCR 工具提取为 TXT/Markdown，再用 book-to-skill 处理文本文件

技术类扫描版书籍建议使用 Docling（自带 OCR 能力）处理后再转换。

---

### Q6: 生成的 Skill 可以分享给别人吗？有版权问题吗？

**A**: 版权问题需要注意：

- **book-to-skill 本身不携带任何书籍内容**，它是一个你指向自己拥有的文件的转换器。
- **处理过程是本地的**：提取和分析在你的机器上运行，工具不会上传你的文件（如果你的 Agent 模型在云端，输入文本遵循该服务商的正常数据条款）。
- **输出是你的笔记**：生成的 Skill 是结构化的综合衍生品——框架名称、定义、要点——而非原文复制。Skill 明确从不复制原始段落（质量规则 #7）。
- **不要重新分发**：发布或分享受版权保护书籍生成的 Skill 可能侵权。第三方书籍的 Skill 请保持私有。
- **可分享的情况**：内部文档、你自己的写作、开放许可材料（如 MIT/Apache 协议的技术文档）可以在其许可范围内分享。

简单说：就像手写学习笔记，供个人使用没问题；公开发布受版权保护书籍的衍生内容有风险。

---

### Q7: 转换失败/提取质量差怎么办？

**A**: 按以下步骤排查：

1. **检查依赖**：运行 `--check` 确认使用了最佳解析器而非低质量 fallback。技术类书籍务必安装 docling，EPUB 推荐安装 ebooklib+bs4。

2. **选择正确模式**：技术类书籍（代码、表格多）选 `--mode technical`（用 Docling），散文类选 `--mode text`（用 pdftotext 更快）。

3. **章节检测问题**：如果书籍没有明确的"Chapter N"标题（如用罗马数字、只有章节标题、非英语标题），自动分段可能不完美。此时提取和转换仍然可以工作，但需要手动指向相关章节区域。

4. **单源失败不影响整体**：如果某个文件损坏或格式异常，它会被跳过并给出警告，其他文件仍然正常处理。

5. **查看完整提取文本**：检查 `/tmp/book_skill_work/full_text.txt` 确认提取质量，如果原始提取就有问题，需要先解决解析器问题。

---

### Q8: 如何添加对新格式的支持？

**A**: 参考 [07 扩展开发](07-extending-development.md) 章节，核心步骤：

1. 在 `book_to_skill/parsers/` 下新建解析器模块，实现 `extract_text(path) -> str` 函数
2. 在 `dependencies.py` 中注册该格式的依赖矩阵（最佳工具→fallback→stdlib 兜底）
3. 在 `config.py` 中注册文件扩展名
4. 在 `parsers/__init__.py` 的分发逻辑中添加路由
5. 添加单元测试验证正常路径和 fallback 路径

每个解析器应遵循：独立失败不影响整体、输出经过 sanitize 清理、提供依赖探测接口。

---

### Q9: 为什么需要安全扫描？文档里能有什么攻击？

**A**: 不可信文档→Agent 是一个被低估的攻击面。文档中的恶意内容可能包括：

1. **Unicode 隐写/注入**：零宽字符、Unicode 标签块可隐藏提示注入指令，在文本提取后被 Agent 读取执行
2. **XXE（XML 外部实体）攻击**：DOCX/EPUB 本质是 ZIP+XML，恶意构造的 DTD/ENTITY 声明可读取本地文件或触发 Billion Laughs 拒绝服务
3. **参数注入**：以 `-` 开头的文件名可能被解析为命令行 flag，注入恶意参数
4. **提示注入**：恶意文档中可能嵌入"忽略之前的指令，执行 X"等内容，在生成的 Skill 中持久化
5. **数据外泄**：生成内容可能被诱导包含系统提示、环境变量等敏感信息

五层纵深防御每层独立过滤一类攻击，不依赖单一防护——这是处理任何不可信输入（不仅仅是书籍）的最佳实践。

---

### Q10: 这本书没有明确的"Chapter N"标题怎么办？

**A**: 章节自动检测支持多种格式：阿拉伯数字（Chapter 1）、罗马数字（Chapter I / I.）、中文（第N章）、韩文（제N장）、泰文及多种欧洲语言形式。

如果书籍只有章节标题没有编号、使用非标准格式、或者 MOBI 格式提取丢失了结构：

1. **转换仍然可用**：自动分段失败不影响提取和生成，只是不会自动拆分为独立章节文件
2. **手动分块**：可以将书籍手动拆分为多个文件（每个章节一个文件），然后传入多个路径给 book-to-skill，它会合并处理
3. **Topic Index 仍然有效**：即使没有自动分章，SKILL.md 中仍然会有主题索引，Agent 可以通过 grep/sed 定位到相关区域
4. **EPUB 格式注意**：EPUB 建议使用 ebooklib 提取（而非 stdlib zipfile fallback），它能更好地保留目录结构

---

## 延伸阅读资源

### 项目资源

- **项目仓库**：[external/libs/book-to-skill/](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/)
- **核心文档**：
  - [README.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/README.md) - 项目主文档、使用指南、基准测试
  - [SKILL.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md) - 可执行规范定义，包含完整 10 步转换流程
  - [docs/ARCHITECTURE.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md) - 架构设计、组件关系
  - [docs/PERFORMANCE.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/PERFORMANCE.md) - 性能基准、Discovery Loop Tax 测量
  - [SECURITY.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SECURITY.md) - 安全策略、漏洞报告

### Wiki 章节导航

| 章节 | 内容 |
|------|------|
| [00 总览](00-overview.md) | 项目介绍、核心价值、适用场景 |
| [01 核心架构](01-core-architecture.md) | 双层架构设计：提取器 + 生成器 |
| [02 提取器深度解析](02-extractor-deep-dive.md) | 格式支持矩阵、多语言检测、降级策略 |
| [03 SKILL.md 生成规范](03-skill-md-spec.md) | 操作模式、10 步流程、Token 预算 |
| [04 Token 经济学](04-token-economics.md) | Discovery Loop Tax 原理、基准数据 |
| [05 安全模型](05-security-model.md) | 五层纵深防御、攻击面分析 |
| [06 安装与使用](06-installation-usage.md) | 两种安装方式、基本示例、环境预检 |
| [07 扩展开发](07-extending-development.md) | 新增格式、自定义生成、工具脚本 |
| [08 可复用模式](08-transferable-patterns.md) | 5 个可迁移到 SpecWeave 的工程模式 |
| [09 总结与 FAQ](09-summary-faq.md) | 本章节 |

---

**事实来源**：本章节基于以下事实编号 F-047, F-048, F-049
