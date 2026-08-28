---
type: Example
title: "Wiki Markup 模板使用示例"
description: "演示如何使用 jira-syntax 技能的 Bug 报告和特性请求模板，包括 wiki markup 语法填充、验证和提交流程。"
tags: ["jira", "wiki-markup", "templates", "syntax", "validation", "bug-report"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/official-docs.md"
    type: "official-docs"
    trust: high
---

# Wiki Markup 模板使用示例

本示例演示如何正确填充 jira-syntax 技能提供的模板，使用 Jira wiki markup 语法撰写格式规范的工单内容，并在提交前进行语法验证。

## 模板位置

jira-syntax 技能提供两个模板文件：

```text
skills/jira-syntax/templates/
├── bug-report-template.md       # Bug 报告模板
└── feature-request-template.md  # 特性请求模板
```

## Bug 报告模板填充

### 模板结构

Bug 报告模板包含以下章节：

1. **环境信息**：Jira 版本、浏览器、操作系统等
2. **重现步骤**：编号列表
3. **预期行为**：应该发生什么
4. **实际行为**：实际发生了什么
5. **错误信息**：日志和截图
6. **技术备注**：附加信息

### 填充示例

以下是一个使用 Jira wiki markup 正确填充的 Bug 报告：

```text
h2. 环境信息

|| 项目 | 值 ||
| Jira 版本 | 9.12.0 Data Center |
| 浏览器 | Safari 17.2 (macOS 14.2) |
| 插件版本 | jira-skill v3.29.0 |

h2. 重现步骤

# 打开终端，进入 skills/jira-communication/ 目录
# 执行命令：
{code:bash}
uv run scripts/core/jira-issue.py get PROJ-123 --fields "description"
{code}
# 观察输出

h2. 预期行为

命令应返回工单 PROJ-123 的描述字段，格式化为可读文本。

h2. 实际行为

描述字段中包含 ADF（Atlassian Document Format）JSON 而非纯文本，
导致输出难以阅读。

h2. 错误信息

{noformat}
TypeError: expected string, got dict
  at extract_adf_text (output.py:42)
{noformat}

h2. 技术备注

* 影响版本：v3.28.0 及以上
* 根因：Cloud 实例返回 ADF 格式，Server 返回 wiki markup
* 相关工单：PROJ-100、PROJ-105
```

### 语法要点

| 语法 | 用途 | 注意事项 |
|------|------|----------|
| `h2. 标题` | 二级标题 | 句点后必须有空格 |
| `\|\| Header \|\|` | 表头单元格 | 使用双竖线 |
| `\| Cell \|` | 普通单元格 | 使用单竖线 |
| `# 列表项` | 有序列表 | `#` 后必须有空格 |
| `* 粗体*` | 粗体文本 | 不要与 Markdown 的 `**` 混淆 |
| `{code:bash}` | 代码块 | 需要闭合 `{code}` |
| `{noformat}` | 无高亮代码块 | 需要闭合 `{noformat}` |
| `[PROJ-100]` | 工单链接 | 自动识别 issue key |

## 特性请求模板填充

### 填充示例

```text
h2. 业务价值

当前批量操作需要多次调用单个命令，效率低下。
增加批量创建能力可将 N 次 API 调用压缩为 1 次，显著减少网络往返。

h2. 用户故事

作为 QA 工程师，
我希望能够通过一条命令批量创建多个测试工单，
以便快速准备测试数据。

h2. 验收标准

* 支持从 JSON 文件读取工单列表
* 支持 --dry-run 预览
* 单条失败不影响其他工单创建
* 创建完成后输出成功/失败汇总

h2. 需求分级

|| 维度 | 级别 | 说明 ||
| 优先级 | P1 | 阻塞当前迭代测试工作 |
| 复杂度 | 中 | 需处理部分失败和回滚 |
| 工作量 | 3d | 含测试和文档 |

h2. 成功指标

* 批量创建 10 个工单耗时 < 5 秒
* 错误报告准确率 100%
* 文档覆盖所有用法
```

## 语法验证

### 使用验证脚本

jira-syntax 技能提供 shell 验证脚本：

```bash
# 验证文件
bash skills/jira-syntax/scripts/validate-jira-syntax.sh bug-report-filled.md

# 验证 stdin 内容
cat my-content.md | bash skills/jira-syntax/scripts/validate-jira-syntax.sh
```

### 验证检查项

脚本检查以下问题：

1. **宏平衡**：`{code}`、`{noformat}`、`{panel}`、`{quote}` 等块级标签必须成对闭合
2. **Markdown 泄漏**：检测常见的 Markdown 语法是否被误用到 wiki markup 中
3. **不支持的语言**：代码块中声明的语言必须在支持列表内

### 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 验证通过（可能有警告） |
| 1 | 存在错误，必须修复 |

### 常见错误与修复

#### 错误1：使用 Markdown 粗体

```text
✗ Markdown bold detected: **text**. Use *text* instead.
```

修复：将 `**粗体**` 改为 `*粗体*`。

#### 错误2：未闭合的代码块

```text
✗ Unclosed macro: {code}
```

修复：确保每个 `{code:language}` 都有对应的 `{code}` 闭合标签。

#### 错误3：CLI 标志的连字符触发删除线

```text
✗ Possible strikethrough: --foo. Escape as \-\-foo
```

在 wiki markup 中，`--text--` 会被渲染为删除线。CLI 标志如 `--dry-run` 中的 `--` 会被误解析。修复方式：转义连字符为 `\-\-dry-run`，或将命令放入 `{code}` 块内（代码块内不会解析 wiki 标记）。

#### 错误4：不支持的代码语言

```text
✗ Unsupported language: typescript. Supported: ...
```

Jira 内置的代码高亮支持有限的语言列表。`typescript`、`rust`、`kotlin` 等不在支持列表中。修复：使用最接近的支持语言（如 `javascript` 代替 `typescript`），或使用 `{noformat}` 代替 `{code}`。

## 提交工作流

将模板内容通过 CLI 提交到 Jira 的完整流程：

```bash
# 第1步：填充模板并保存到文件
# （使用编辑器编辑 bug-report-filled.md）

# 第2步：验证语法
bash skills/jira-syntax/scripts/validate-jira-syntax.sh bug-report-filled.md

# 第3步：验证通过后，创建工单（使用 --dry-run 预览）
uv run scripts/workflow/jira-create.py issue PROJ "Safari 登录页面崩溃" \
  --type Bug \
  --priority High \
  --description "$(cat bug-report-filled.md)" \
  --dry-run

# 第4步：确认无误后实际创建
uv run scripts/workflow/jira-create.py issue PROJ "Safari 登录页面崩溃" \
  --type Bug \
  --priority High \
  --description "$(cat bug-report-filled.md)"
```

> **重要**：验证步骤必须作为独立步骤运行，不要使用 `&&` 将验证命令和创建命令链式连接。这是为了确保即使验证脚本返回警告（退出码 0），用户也能看到输出并做出判断。

## @提及用户

在评论或描述中提及用户时，使用 `[~username]` 语法：

```text
h2. 指派说明

请 [~john.doe] 审查此修复。[~jane.smith] 请协助 QA 验证。
```

提交时，`jira-comment.py add` 会自动调用 `verify_mentions()` 检查这些用户是否存在：

- Cloud 实例使用 `accountId` 标识用户
- Server/DC 实例使用 `username` 标识用户

如果提及的用户不存在，命令会输出错误并终止，防止创建无效提及。

## 相关概念

- [jira-syntax 技能详解](/concepts/05-jira-syntax.md)：完整语法参考
- [jira-communication 技能](/concepts/04-jira-communication.md)：API 提交方式
- [基础 CLI 使用示例](/examples/basic-cli-usage.md)：创建工单命令
- [官方文档信源](/references/official-docs.md)：Wiki Markup 官方参考
