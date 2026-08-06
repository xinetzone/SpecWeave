# book-to-skill 总览

> 将任意技术书籍、文档文件夹或多源资料转换为统一的 Agent Skill —— 可按需加载、无幻觉、24×-51× token 节省

## 这是什么？

**book-to-skill** 是一个开源知识工程工具，它解决一个非常具体的痛点：你买了一本好书，读了一遍，三个月后完全不记得第七章讲了什么。

传统的解决方案都不够好：
- 📄 "我直接搜 PDF" → 得到一堆页码，不是答案
- 🧠 "我让 AI 回答关于这本书的问题" → 要么幻觉，要么说没有内容
- 📝 "我边读边记笔记" → 最后得到一个 200 行的文档再也没打开过

book-to-skill 的解决方案：**把书籍编译成结构化的 Agent Skill，你的 AI 助手按需加载正确章节，从真实内容回答，无幻觉。**

## 核心价值主张

| 维度 | 上下文 Dump | Discovery Loop | book-to-skill |
|------|------------|----------------|---------------|
| Token 消耗（单问） | 119K-256K | 12K-78K | ~5K |
| 节省倍数（vs dump） | 1× | — | **24×-51×** |
| 节省倍数（vs loop） | — | 1× | **2.4×-15.6×** |
| 幻觉风险 | 中 | 高 | 低（基于真实提取内容） |
| 每轮重复付费 | ✅ 是 | ❌ 一次付费 | ❌ **一次编译，永久使用** |

> 数据来源：[tools/discovery_tax.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/discovery_tax.py) 在三本书上的实测结果。

## 为什么这不是 RAG？

这是最常见的误解。RAG 和 book-to-skill 解决的是不同问题：

| | RAG | book-to-skill |
|---|-----|---------------|
| **工作时机** | 查询时（Query-time） | 编译时（Compile-time） |
| **核心动作** | 分块 → Embedding → 相似向量检索 | 深度分析提取作者的命名框架、决策规则、反模式 |
| **回答方式** | "这里是与你查询相近的文本块" | "这是作者构建的 12 个框架，随时可以用来推理" |
| **适用场景** | 宽而浅：几十本书的图书馆，"找提到 X 的部分" | 窄而深：一本书或紧密相关的资料簇，工作时反复应用的框架 |

它们是互补的，不是竞争的：RAG 索引书架，book-to-skill 精通一本书。

## 支持的格式

- **PDF**：pdftotext（poppler，最快）→ pypdf → pdfminer.six（文本类）；Docling（技术类，保留表格/代码块）
- **EPUB**：ebooklib + beautifulsoup4（最佳）→ stdlib zipfile（兜底）
- **DOCX**：python-docx → stdlib ZIP/XML
- **HTML**：beautifulsoup4 → stdlib html.parser
- **RTF**：striprtf → regex 兜底
- **MOBI/AZW/AZW3**：Calibre ebook-convert（必需，无兜底）
- **纯文本**：TXT、Markdown、reStructuredText、AsciiDoc（无需额外依赖）

## Wiki 导航

| 章节 | 内容 |
|------|------|
| [01 核心架构](01-core-architecture.md) | 双层架构设计：Python 提取器 + SKILL.md 规范驱动生成器 |
| [02 提取器深度解析](02-extractor-deep-dive.md) | 格式支持矩阵、多语言章节检测、优雅降级策略 |
| [03 SKILL.md 生成规范](03-skill-md-spec.md) | 4 种操作模式、10 步流程、Token 预算矩阵、文件模板 |
| [04 Token 经济学](04-token-economics.md) | Discovery Loop Tax 原理、性能基准、大书访问策略 |
| [05 安全模型](05-security-model.md) | 文档→Agent 供应链攻击面、5 层防御体系 |
| [06 安装与使用](06-installation-usage.md) | 两种安装方式、Skill 位置、基本示例、环境预检 |
| [07 扩展开发](07-extending-development.md) | 新增格式、自定义生成行为、工具脚本说明 |
| [08 可复用模式](08-transferable-patterns.md) | 5 个可迁移到 SpecWeave 的工程模式 |
| [09 总结与 FAQ](09-summary-faq.md) | 核心要点、常见问题、延伸阅读 |

## 适用场景

- ✅ **技术书籍深度学习**：编程书、架构指南、方法论著作
- ✅ **内部文档折叠**：把整个 docs/ 文件夹变成一个可查询的 Skill
- ✅ **品牌/设计系统**：语音指南、组件原则，团队查询替代翻 60 页 PDF
- ✅ **研究资料簇**：多篇论文+笔记合并成统一技能，新材料持续更新
- ✅ **规范/标准**：RFC、API 合同、合规文档

## 不适用场景

- ❌ 一次性阅读的材料（直接用大窗口/RAG 即可）
- ❌ 几十本书的宽域检索（用专门的 RAG 工具如 CandleKeep）
- ❌ 需要逐字引用受版权保护的全文（book-to-skill 提取结构而非复制原文）

---

**事实来源**：本章节基于以下事实编号 F-002, F-003, F-005, F-030
