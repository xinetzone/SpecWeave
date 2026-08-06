# 核心架构

book-to-skill 采用**双层架构**设计：确定性的 Python 提取器 + 规范驱动的 Agent 生成器。这种分离是理解整个项目的关键。

## 架构全景

```
            ┌─────────────────────────── EXTRACTOR (Python, 确定性) ──┐
 documents  │  scripts/extract.py (shim)  →  book_to_skill/            │
 (pdf/epub/ │    ├─ cli.py · utils.py   CLI解析 · 多源处理 · 运行器     │
  docx/...) │    ├─ config.py           支持扩展名 · 路径 · 依赖映射    │
     │      │    ├─ dependencies.py     可选依赖探测 · --check报告     │
     ▼      │    ├─ sanitize.py         移除不可见/零宽Unicode         │
 ───────────│    └─ parsers/            pdf · epub · docx · html ·     │
            │                             rtf · calibre · text         │
            │                             (最佳工具优先，链式回退)      │
            │  输出 → <tempdir>/book_skill_work/                       │
            │    full_text.txt   (所有源合并，带源标记)                 │
            │    metadata.json   (页数/词数/tokens/章节/目录)           │
            └─────────────────────────────────────────────────────────┘
                                   │
                                   ▼
            ┌─────────────────────────── GENERATOR (Agent, 遵循SKILL.md) ┐
            │  Step 1.5  询问内容类型 → BOOK_TYPE (technical | text)      │
            │  Step 2/2.5 提取 · 成本估算 · 用户确认                     │
            │  Step 2.6  大书REPL式探测 (grep/sed，不全量读取)            │
            │  Step 3    分析结构 (标题/作者/章节/目录)                  │
            │  Step 4    询问用途 → DEPTH (reference | study)            │
            │  Step 7    逐章摘要 (预算 = BOOK_TYPE × DEPTH)             │
            │  Step 8    glossary · patterns · cheatsheet                │
            │  Step 9/9.5 SKILL.md核心 + 索引 + 安全扫描                │
            └──────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                <SKILLS_HOME>/<slug>/  ← 按宿主选择:
                  ~/.copilot/skills/      GitHub Copilot CLI
                  ~/.agents/skills/       Copilot CLI/Amp (跨Agent)
                  ~/.claude/skills/       Claude Code
                  .github|.claude|.agents/skills/  项目本地
                  SKILL.md         核心框架 + 章节/主题索引 (~4K tokens)
                  chapters/*.md    按需加载，不常驻
                  glossary.md      术语表
                  patterns.md      技术/模式
                  cheatsheet.md    决策规则/决策树/权衡/信号
```

> 架构图来源：[ARCHITECTURE.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md#L7-L45)

## 两层职责边界

### 第一层：Python 提取器（确定性）

提取器的职责**纯粹且有限**：把各种格式的文档变成干净的纯文本 + 元数据。

**它做什么：**
- 文件格式解析（PDF/EPUB/DOCX/HTML/RTF/MOBI/TXT）
- 多源文件合并（带明确的源分隔标记）
- 文本清理（移除不可见 Unicode 字符）
- 结构检测（章节数量、目录存在性）
- 依赖探测和优雅降级
- 输出元数据（页数、词数、token 估算、章节数）

**它不做什么：**
- ❌ 不理解书籍内容
- ❌ 不生成摘要
- ❌ 不提取框架/模式
- ❌ 不写 SKILL.md
- ❌ 不做任何 LLM 调用

关键代码：
- CLI 入口：[cli.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/cli.py#L1-L16) — 强制 UTF-8 输出
- 核心运行器：[utils.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L612-L735) — `main()` 函数
- 配置常量：[config.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L1-L38)

### 第二层：SKILL.md 生成规范（Agent 执行）

**这才是 book-to-skill 的核心创新。** 生成逻辑不是写在 Python 代码里，而是写在一个 600+ 行的 Markdown 文件 [SKILL.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md) 里。

Agent（Claude/Copilot/Amp）读取 SKILL.md 后，会严格按照其中定义的步骤执行生成流程。SKILL.md 本身就是 Agent Skill 格式，所以：
- 修改生成行为不需要改 Python 代码
- 天然跨 Agent 宿主兼容（所有遵循 Agent Skills 标准的宿主都能执行）
- 规范即文档，文档即程序

## 组件职责表

| 路径 | 职责 | 确定性 |
|------|------|--------|
| [scripts/extract.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/scripts/extract.py) | 薄入口 shim → `book_to_skill.cli` | ✅ |
| [book_to_skill/cli.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/cli.py) | UTF-8 编码强制 + 入口转发 | ✅ |
| [book_to_skill/utils.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py) | CLI 解析、多源解析、章节/目录检测、主运行器 | ✅ |
| [book_to_skill/config.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py) | 支持扩展名、输出路径、依赖映射、token 换算 | ✅ |
| [book_to_skill/dependencies.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py) | 可选依赖探测、`--check` 报告、自动安装提示 | ✅ |
| [book_to_skill/sanitize.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/sanitize.py) | 移除零宽字符和 Unicode 标签块（安全防护） | ✅ |
| [book_to_skill/exceptions.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/exceptions.py) | ExtractionError 异常定义（批量模式下单源失败不致命） | ✅ |
| [book_to_skill/parsers/](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/) | 格式专用解析器（pdf/epub/docx/html/rtf/calibre/text） | ✅ |
| [tools/discovery_tax.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/discovery_tax.py) | 测量 token 成本 vs 上下文 dump/discovery loop | ✅ |
| [tools/validate_skill.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/validate_skill.py) | 检查生成的 SKILL.md 是否符合宿主规则 | ✅ |
| [tools/scan_generated_skill.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/scan_generated_skill.py) | 生成 Skill 的安全扫描（prompt 注入检测） | ✅ |
| [SKILL.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md) | **生成器规范**：Steps 0-10 + 更新工作流 + 8条质量规则 | ❌ Agent 执行 |

## 数据流详解

### 阶段 1：输入解析与验证

```
用户输入: /book-to-skill <paths...> [slug]
    ↓
Step 0: 范围检查（无参数则报错）
    ↓
Step 1: 输入验证
    ├─ 解析参数：路径列表 + 可选 slug
    ├─ 展开目录和 glob 模式
    ├─ 过滤支持的扩展名
    ├─ 检查是否为已有 Skill（触发更新模式）
    └─ 无支持文件则清晰报错
```

关键实现：[parse_arguments()](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L326-L359)、[resolve_input_files()](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L362-L407)

### 阶段 2：提取与合并

```
Step 1.5: 询问内容类型 (technical/text)
    ↓
Step 2: 运行提取脚本
    ├─ 对每个源文件：
    │   ├─ 探测文件类型（magic bytes 兜底）
    │   ├─ prepare_dependencies() 检查/提示安装依赖
    │   ├─ 按格式选择提取器链（最佳优先，链式回退）
    │   ├─ sanitize_extracted_text() 移除不可见字符
    │   └─ 单源失败 → 警告+跳过，不中断批量处理
    ├─ 合并文本：每源用 = 80分隔符标记
    ├─ 写入 full_text.txt
    └─ 写入 metadata.json（含每源详情）
```

关键实现：[extract_single_file()](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L410-L599)

### 阶段 3：成本估算与确认

```
Step 2.5: 读取 metadata.json
    ↓
展示成本估算：
    ├─ 源文件列表和格式
    ├─ 合并页数/词数/token数
    ├─ 输入/输出 token 估算
    ├─ 估算时间
    └─ 等待用户确认（或 "analyze only"）
```

### 阶段 4：大书 REPL 式访问（>50K tokens）

这是一个重要的设计决策——对于大书，Agent **不应该**一次性把 full_text.txt 全部读入上下文。

```bash
# 先看大小
wc -w "$FULL_TEXT_PATH"

# 找章节偏移，不全量读取
grep -n -E "^\s*(Chapter|CHAPTER)\s+[0-9]+" "$FULL_TEXT_PATH" | head -40

# 只拉取需要的章节（行范围）
sed -n '<start>,<end>p'

# 验证框架确实被提及再写入 SKILL.md
grep -c -i "westrum\|dora" "$FULL_TEXT_PATH"
```

> 设计原理：一本 200 页的书约 75K tokens，如果每章重读一遍（28 次）就是 ~2M 输入 tokens；用 grep+sed 按需拉取使生成成本与输出成正比，而非与源大小成正比。
> 来源：[SKILL.md Step 2.6](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L210-L236)

### 阶段 5：分析与生成

这部分完全在 SKILL.md 规范中定义，由 Agent 执行：
1. **Step 3**：分析书籍结构（标题、作者、章节、目录）
2. **Step 4**：询问使用目的 → 推导 DEPTH
3. **Step 5**：确定 Skill 名称和目标路径
4. **Step 6**：创建目录结构
5. **Step 7**：逐章生成摘要（按 token 预算矩阵）
6. **Step 8**：生成 glossary/patterns/cheatsheet
7. **Step 9**：生成主 SKILL.md（≤4000 tokens，内容前置）
8. **Step 9.5**：安全扫描
9. **Step 10**：清理临时文件 + 报告

## 关键设计原则

来自 [README 设计原则](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/README.md#L232-L240) 和 [ARCHITECTURE.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md#L47-L58)：

1. **提取结构，而非摘要** —— 捕获命名框架、决策规则、反模式；永远不复制原始段落
2. **编译时付费，而非运行时** —— 导航/结构化成本一次付清；查询时只加载相关章节
3. **章节按需加载** —— SKILL.md 保持精简；章节文件只有被读时才消耗 tokens
4. **SKILL.md 内容前置** —— 最重要的内容放最前面（压缩从末尾截断）
5. **优雅降级** —— 每种格式都有 stdlib 兜底；一个坏源被跳过，不致命

---

**事实来源**：本章节基于以下事实编号 F-006, F-009, F-010, F-019, F-023, F-024, F-029, F-035
