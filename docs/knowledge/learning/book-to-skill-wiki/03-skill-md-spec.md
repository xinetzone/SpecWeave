# SKILL.md 生成规范详解

SKILL.md 是 book-to-skill 的灵魂——它是一份 600+ 行的**可执行规范**，Agent 读取后会严格按照其中定义的步骤生成 Skill。

## 四种操作模式

| 模式 | 触发 | 执行步骤 | 输出 |
|------|------|---------|------|
| **1. 完整转换（默认）** | 用户提供路径无特殊说明 | Steps 0-9 全流程 | 完整 Skill（SKILL.md + chapters/ + glossary + patterns + cheatsheet） |
| **2. 仅分析** | 用户说 "analyze"、"just extract" | Steps 0-3 | 提取报告（框架/原则/技术/反模式列表），不生成文件 |
| **3. 从分析生成** | 用户有预先分析笔记 | Steps 4-9（跳过提取） | 从提供的分析生成 Skill 文件 |
| **4. 更新/折叠** | 目标路径是已有 Skill | Steps 0-2 → Update Workflow | 合并新内容到已有 Skill |

> 来源：[SKILL.md#L39-L62](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L39-L62)

## Skill 安装位置优先级

生成的 Skill 会写入以下位置之一（按宿主自动检测）：

| 宿主 | 个人 Skill 路径（按优先级探测） | 项目本地路径 |
|------|-------------------------------|-------------|
| **GitHub Copilot CLI** | `~/.copilot/skills/` → `~/.agents/skills/` | `.github/skills/` → `.claude/skills/` → `.agents/skills/` |
| **Amp** | `~/.agents/skills/` → `~/.config/agents/skills/` → `~/.config/amp/skills/` | `.agents/skills/` |
| **Claude Code** | `~/.claude/skills/` | `.claude/skills/` |

选择规则：
1. 恰好一个宿主根目录存在 → 直接使用，不询问
2. 都不存在 → 询问用户创建哪个
3. 用户明确要求项目本地 → 优先项目本地路径
4. 无法识别宿主 → 询问用户

> 来源：[SKILL.md#L65-L78](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L65-L78)、[SKILL.md#L303-L324](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L303-L324)

## 10 步生成流程

### Step 0：范围检查

无参数时直接报错退出：
```
book-to-skill requires a supported document path, folder, or glob pattern.
Usage: book-to-skill <path-to-document-folder-or-glob>... [skill-name-slug]
```

同时识别：
- 最后一个参数如果不像文件/目录/glob，且符合 slug 格式（小写连字符），作为 `SKILL_NAME`
- 其他参数作为 `INPUT_PATHS`
- 如果输入路径已有 SKILL.md + chapters/，或 SKILL_NAME 已存在 → 标记为 Mode 4（更新）

### Step 1：输入验证

- 展开目录和 glob，过滤支持的扩展名
- 无支持文件 → 清晰报错

### Step 1.5：识别内容类型（关键决策点）

**必须询问用户**：

> "What kind of content do these sources have?
> 1. **Technical** — has code blocks, tables, formulas (e.g. programming books)
> 2. **Text-heavy** — mostly prose, few tables/code (e.g. management, productivity)
> 3. **Not sure** — I'll use the fast method"

结果决定：
- Option 1 → `BOOK_TYPE=technical`（用 Docling，~1.5s/页）
- Option 2/3 → `BOOK_TYPE=text`（用 pdftotext，即时）

### Step 2：运行提取脚本

```bash
"$PYTHON_BIN" "$SCRIPT_PATH" $INPUT_PATHS --mode <BOOK_TYPE> --install-missing ask
```

脚本位置自动探测（按 Skill 路径顺序查找）。

提取前会自动检查依赖，缺失时提示安装或使用兜底。输出：
- `<tempdir>/book_skill_work/full_text.txt`
- `<tempdir>/book_skill_work/metadata.json`

### Step 2.5：成本估算（用户确认）

生成前**必须**展示估算并等待确认：

```
📖 Sources detected: 2 source(s)
   book.pdf (pdf, 244 pages)
   notes.txt (text)
📄 Combined Pages: ~244 | Words: ~45K | Total tokens: ~60K

💰 Estimated token cost:
   Input:  ~78K tokens
   Output: ~25K tokens
   Total:  ~103K tokens

   ⏱  Estimated time: ~3-5 minutes

➡  Proceed? (or "analyze only" to preview)
```

估算公式：
- Input ≈ `estimated_tokens × 1.3`（每章提示词开销）
- Output ≈ 章节数 × 每章预算 + 4000（SKILL.md）+ 4500（glossary+patterns+cheatsheet）

### Step 2.6：大书 REPL 式访问（>50K tokens）

**不全量读取 full_text.txt**，用 grep/sed 按需拉取：
- `wc -w` 先看大小
- `grep -n` 找章节偏移
- `sed -n start,endp` 只拉需要的章节
- `grep -c` 验证框架确实存在再写入

### Step 3：分析书籍结构

读取前 8000 字符识别：
- 书名、作者
- 章节结构（Chapter N、PART I、目录）
- 核心主题
- 大致章节数

Mode 2（仅分析）在此停止并输出提取报告。

### Step 4：询问使用目的

> "What should this skill help you do?
> 1. Apply the author's frameworks while working
> 2. Think with the author's mental models
> 3. Reference specific chapters and concepts
> 4. All of the above"

答案自动推导 `DEPTH`：
- 只选 3 → `DEPTH=reference`（精简快速查找）
- 选 1/2/4 → `DEPTH=study`（更深入，包含示例和推理）

### Step 5：确定 Skill 名称

- 有 SKILL_NAME 参数则直接使用
- 否则提供两个选项让用户选：
  - 作者-概念：`cialdini-influence`、`meadows-systems`
  - 标题派生：`designing-data-intensive-apps`

同时检测目标路径是否已存在 Skill：
1. Update/Fold-in（Mode 4）
2. Overwrite（删除重建）
3. Rename（加 `-2` 后缀）

### Step 6：创建目录

```bash
mkdir -p "$SKILLS_HOME/<skill_name>/chapters"
```

### Step 7：生成章节摘要（核心步骤）

#### Token 预算矩阵（自适应）

| | `DEPTH=reference` | `DEPTH=study` |
|---|---|---|
| `BOOK_TYPE=text` | 800–1,200 tokens | 1,000–1,800 tokens |
| `BOOK_TYPE=technical` | 1,200–1,800 tokens | 2,000–3,000 tokens |

**重要**：这是目标不是硬上限。密度优先于长度——不要为凑字数填充内容。

#### study 深度必须通过内容获得（不是靠注水）

要诚实地达到 study 预算，必须添加：
- **Worked Example**：复现作者的一个完整示例（这是最大的杠杆）
- 每个框架的"How"展开为明确步骤
- 1-2 个核心框架添加"Why it works / failure mode"说明

如果章节确实没有示例可展开，让它低于预算也无妨——并在 Core Idea 中标注该章较薄。

#### 章节模板

```markdown
# Chapter N: <Full Title>

## Core Idea
<1-2 句：本章教的最重要的一件事>

## Frameworks Introduced
- **<Framework Name>**: <精确表述，保留作者命名>
  - When to use: <具体场景>
  - How: <步骤或标准>

## Key Concepts
- **<Term>**: <1 句精确定义>
(5-10 个最重要术语)

## Mental Models
<2-4 个思维工具，用 "Use X when Y" 句式>

## Anti-patterns
- **<避免什么>**: <为什么失败>

## Code Examples (technical only)
\`\`\`<language>
<关键代码片段>
\`\`\`
- **What it demonstrates**: <一行说明>

## Reference Tables (technical only)
<对比矩阵、参数表、决策表>

## Worked Example (study only)
<复现作者的一个具体示例：样本文档、对话、填好的模板、决策过程>

## Key Takeaways
1. <可执行洞察>
2. <可执行洞察>
3. <可执行洞察>
(3-7 条实践者必须记住的要点)

## Connects To
- **Ch N**: <关联原因>
- **<Concept>**: <关联的外部概念>
```

> 来源：[SKILL.md#L367-L414](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L367-L414)

### Step 8：生成辅助文件

#### glossary.md（≤1500 tokens）
- 书中所有重要术语，按字母排序
- 格式：`**Term** — definition (Ch N)`

#### patterns.md（≤2000 tokens）
- 所有具体技术、设计模式、算法
- 格式：`## Pattern Name\n**When to use**: ...\n**How**: ...\n**Trade-offs**: ...`

#### cheatsheet.md（≤1200 tokens）—— **最具差异化的文件**

cheatsheet 不是关键词列表，而是作者的**判断力**：决策规则、决策树、权衡矩阵、阈值、信号/坏味道。

优先级：
1. **决策规则**："When X, do Y, because Z"
2. **决策树/流程图**：多分支选择用嵌套列表或小表格
3. **权衡矩阵**：多维度评分 competing options
4. **阈值/默认值**：作者明确给出的数字、比例、经验法则
5. **信号/坏味道**：快速识别情景的启发式

避免：纯术语→定义行（这是 glossary 的事）、散文段落（这是章节的事）。每一行都应该帮助读者**做决策**。

### Step 9：生成主 SKILL.md（≤4000 tokens，内容前置）

```markdown
---
name: <skill_name>
description: "Knowledge base from \"<Full Title>\" by <Author(s)>. Use when applying <author>'s frameworks for <key topics>..."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# <Full Title>
**Author**: <Author(s)> | **Pages**: ~<N> | **Chapters**: <N> | **Generated**: <YYYY-MM-DD>

## How to Use This Skill
- 无参数 → 加载核心框架
- 带主题 → 查找并解释相关主题
- 带章节 → 加载特定章节
- 浏览 → "what chapters do you have?"

---

## Core Frameworks & Mental Models
<!-- ~2000 tokens: 作者最重要的命名框架和原则 -->
<生成 2000 tokens 最关键的框架和洞察>

---

## Chapter Index
| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-<slug>.md) | <Title> | <framework1>, <framework2> |

## Topic Index
- **<Term>** → ch<N>[, ch<N>]

## Supporting Files
- [glossary.md](glossary.md)
- [patterns.md](patterns.md)
- [cheatsheet.md](cheatsheet.md)

---

## Scope & Limits
This skill covers the book content only...
```

**关键规则**：最重要的内容放最前面——压缩从末尾截断，Core Frameworks 必须在最前。

### Step 9.5：安全扫描（强制）

```bash
"$PYTHON_BIN" "$SKILL_CONVERTER_ROOT/tools/scan_generated_skill.py" "$SKILLS_HOME/<skill_name>"
```

扫描器退出非零时停止，要求人工审查发现的问题——不能静默重写生成文件。

### Step 10：清理与报告

- 删除临时工作目录
- 报告生成的文件列表、token 统计、使用方法

## 更新/折叠工作流（Mode 4）

向已有 Skill 添加新内容时：

1. **读取已有结构**：解析 SKILL.md 的章节索引、主题索引、元数据；列出现有章节文件找到最大编号
2. **匹配内容**：判断新内容是更新已有章节还是新增章节
3. **生成/更新章节**：新增章节从最大编号+1开始编号
4. **合并辅助文件**：
   - glossary：合并去重，术语多源时追加章节引用
   - patterns：追加新模式，保持≤2500 tokens
   - cheatsheet：整合新决策规则
5. **重新生成 SKILL.md**：更新元数据、Core Frameworks（保持≤4000 tokens）、追加新章节到索引、合并主题索引
6. **扫描、清理、报告**

## 8 条质量规则

1. **提取结构，而非摘要** —— 捕获命名框架、精确表述、反模式；不是章节复述
2. **保留作者精确命名** —— "The 5 Whys" ≠ "问多次为什么"；保留精确名称
3. **密度优于完整性** —— 1000-token 摘要胜过 10000-token 摘抄
4. **实践者语气** —— 写 "Use X when Y"，不是 "The book explains X"
5. **SKILL.md 内容前置** —— 压缩保留前 5000 tokens；最重要内容先出现
6. **章节文件按需加载** —— 不加载就不计入 Skill 预算
7. **永不复制原始文本** —— 始终合成、摘要、提取信号
8. **主题索引至关重要** —— 这是 Agent 导航到正确章节文件的方式

---

**事实来源**：本章节基于以下事实编号 F-010, F-011, F-024, F-025, F-026, F-027, F-028, F-031, F-032
