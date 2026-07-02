---
id: "myst-migration-01-background"
title: "背景与上下文"
source: "report.md#1-背景与上下文"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/standards-tools/myst-to-agentspec-migration-analysis/01-background.toml"
---

## 1. 背景与上下文

### 1.1 项目现状

SpecWeave项目当前采用基于markdown-it-py 2.2.0的自定义解析器架构（file:///d:/spaces/SpecWeave/.agents/scripts/mdi/parser.py），用于解析Agent Spec文档（spec.md）和技能定义文档（SKILL.md）。根据Task 1基线数据分析，项目文档现状呈现以下特征：

**文档统计概况：**

| 文档类型 | 数量 | 表格密度（个/文档） | 代码块密度（个/文档） | YAML frontmatter覆盖率 | Directive使用率 |
|---|---|---|---|---|---|
| spec.md | 52 | 0.67 | 0.06 | 26.9% | 0% |
| SKILL.md | 14 | 3.79 | 4.43 | 100% | 0% |

**现有解析器架构特征：**

1. **插件配置（第171-172行）**：当前仅启用`front_matter_plugin`和`tasklists_plugin`，`colon_fence`插件虽可用但未启用
2. **Directive正则定义（第112-113行）**：
   - `_DIRECTIVE_RE = re.compile(r'^\{(\w[\w-]*)\}\s*(.*)$')`：识别`{name}`形式的指令标识符
   - `_OPTION_LINE_RE = re.compile(r'^:([\w][\w\s\-]*?)(\??)\s*:\s*(.*)$')`：仅支持`:key: value`格式的选项
3. **Admonition类型集合（第115行）**：预定义9种提示框类型（note/warning/danger/tip/important/caution/hint/info/seealso）
4. **围栏处理逻辑（第377-421行）**：仅支持反引号（```` ``` ````）围栏，不支持冒号（`:::`）围栏
5. **Directive内容解析（第641-672行）**：`_parse_directive_content()`方法实现options和body的分离，但仅支持`:key: value`单行格式
6. **接口提取逻辑（第1124-1225行）**：`_extract_interfaces_from_directives()`专门处理接口定义类指令
7. **参数与响应解析（第1227-1272行）**：`_parse_directive_param()`和`_parse_directive_response()`实现特定领域的结构化提取
8. **Frontmatter处理（第248-341行）**：内嵌YAML frontmatter解析和TOML引用加载，无独立frontmatter.py模块

**关键发现：** 现有解析器在代码层面已预留Directive扩展点，但存量文档中Directive使用率为0%，表格仍是事实上的核心结构化载体。这形成了一个有意思的张力——解析能力先行但使用习惯滞后，为本次评估提供了独特的观察窗口。

### 1.2 MyST核心概念简述

MyST（Markedly Structured Text）是CommonMark Markdown的超集，源自Executable Books项目，在完全兼容标准Markdown的基础上，引入了两大核心扩展机制：

**Directives（指令）**——块级扩展容器：

Directives是多行块级结构，用于表达提示框、图片、代码块、表格、图表、卡片、折叠面板等复杂内容。完整的Directive结构包含五个组成部分：

1. **围栏标记**：支持两种语法
   - 冒号围栏（`:::`）：适用于包含Markdown内容的指令，降级显示效果好
   - 反引号围栏（```` ``` ````）：适用于代码/公式/图表类内容
2. **标识符**：`{directivename}`形式，指定指令类型
3. **参数**：紧跟标识符后的主要输入（如图片路径、代码语言）
4. **选项**：三种写法支持不同复杂度场景
   - `:key: value`键值对格式（简单场景）
   - `---`包裹的YAML块格式（多选项场景）
   - 大括号内`.class`/`#label`/`key="value"`内联格式
5. **内容主体**：指令承载的实际内容

**Roles（角色）**——行内扩展机制：

Roles是单行内联扩展，语法为`{rolename}`content``，用于在行内插入缩写、上下标、数学公式、交叉引用、文献引用等语义标记。与Directives的块级特性不同，Roles不产生新的文档块，而是在文本流中插入语义增强。

**嵌套机制：** MyST通过增加围栏符号数量实现嵌套（如外层`:::::`包裹内层`::::`），每嵌套一层符号数至少加1，支持冒号围栏与反引号围栏混合嵌套。

MyST的设计哲学在于"渐进式结构化"——标准Markdown内容随处可用，而在需要精确语义表达时，可逐步引入Directives和Roles，学习曲线平缓。

---
