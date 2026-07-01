---
source: "agent-skills-open-standard-wiki.md#四skillmd-格式规范"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/agent-skills-wiki/03-skill-md-format.toml"
---
# 四、SKILL.md 格式规范

## 4.1 文件结构

`SKILL.md` 必须包含 **YAML frontmatter**（由 `---` 包裹），后跟 **Markdown 正文**：

```markdown
---
name: skill-name
description: 描述技能功能和触发时机（1-1024字符）
---

# 技能标题

指令正文（Markdown 格式）...
```

> **源码锚点**：frontmatter 解析逻辑见 [parser.py:30-64](../../../../prompt_extraction/input/parser.py#L30-L64)

## 4.2 Frontmatter 字段规范

| 字段 | 必填 | 约束 | 说明 |
|------|------|------|------|
| `name` | ✅ | 1-64字符，Unicode小写字母+数字+连字符，不能以连字符开头/结尾，不能有连续连字符，必须与文件夹名一致（NFKC规范化后） | 技能标识符 |
| `description` | ✅ | 1-1024字符，非空 | 描述技能功能和触发时机 |
| `license` | ❌ | - | 许可证名称或或许可证文件引用 |
| `compatibility` | ❌ | 1-500字符 | 环境要求（目标产品、系统包、网络访问等） |
| `allowed-tools` | ❌ | 空格分隔的工具模式字符串 | 预批准使用的工具（实验性功能） |
| `metadata` | ❌ | 键值对映射 | 自定义元数据（客户端特定属性） |

> **源码锚点**：字段约束常量见 [validator.py:10-22](../../../../.agents/scripts/mdi/validator.py#L10-L22)

### 4.2.1 `name` 字段详解

**有效示例**：
```yaml
name: pdf-processing
name: data-analysis
name: code-review
name: 技能          # 中文名称（支持 Unicode）
name: мой-навык     # 俄文名称（支持 Unicode）
```

**无效示例**：
```yaml
name: PDF-Processing    # ❌ 不允许大写
name: -pdf              # ❌ 不能以连字符开头
name: pdf-              # ❌ 不能以连字符结尾
name: pdf--processing   # ❌ 不允许连续连字符
name: pdf_processing    # ❌ 不允许下划线（仅允许字母、数字、连字符）
```

**重要说明**：
- 支持 Unicode 国际字符（中文、俄文等），但必须是**小写**形式
- 名称经过 **NFKC 规范化**后与目录名比较（解决预组合/分解字符问题，如 `café` 的两种 Unicode 表示）

> **源码锚点**：name 验证逻辑见 [validator.py:25-67](../../../../.agents/scripts/mdi/validator.py#L25-L67)；NFKC 测试见 [test_validator.py:267-290](file:///d:/spaces/SpecWeave/.temp/libs/agentskills/skills-ref/tests/test_validator.py#L267-L290)

### 4.2.2 `description` 字段详解

**好的示例**：
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**不好的示例**：
```yaml
description: Helps with PDFs.    # ❌ 太模糊
```

**写作原则**：
- 使用命令式语气："Use this skill when..." 而非 "This skill does..."
- 关注用户意图，而非实现细节
- 明确列出适用场景，包括用户未直接提及领域名称的情况
- 保持简洁（硬限制 1024 字符）

> **源码锚点**：description 验证见 [validator.py:70-84](../../../../.agents/scripts/mdi/validator.py#L70-L84)

### 4.2.3 完整 Frontmatter 示例

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill PDF forms, merge documents. Use when working with PDFs, filling forms, or extracting document content, even if the user doesn't explicitly say "PDF".
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv
metadata:
  author: example-org
  version: "1.2"
allowed-tools: Bash(python:*) Bash(uv:*) Read
---
```

## 4.3 正文内容规范

Markdown 正文没有严格的格式限制，但推荐遵循以下原则：

**推荐内容结构**：
- 分步工作流指令
- 输入输出示例
- 常见边界情况（Gotchas）
- 可用脚本列表
- 验证/检查步骤

**长度建议**：
- 推荐控制在 **500 行以内**，**5000 tokens 以下**
- 详细参考资料移至 `references/` 目录，并在正文中明确说明何时加载

> **规范锚点**：推荐限制见 [specification.mdx §Progressive disclosure](file:///d:/spaces/SpecWeave/.temp/libs/agentskills/docs/specification.mdx)
