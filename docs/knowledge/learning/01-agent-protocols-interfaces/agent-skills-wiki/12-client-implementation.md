---
source: "agent-skills-open-standard-wiki.md#十三客户端实现完整指南"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/12-client-implementation.toml"
id: "agent-skills-wiki-client-implementation"
title: "技术上无效的 YAML——冒号破坏了解析"
---
## 十三、客户端实现完整指南

对于想要在自己的 AI 智能体或开发工具中添加 Agent Skills 支持的开发者，以下是完整的5步集成指南。

### 13.1 核心原则：渐进式披露

每个兼容 Skills 的智能体遵循相同的三层加载策略：

| 层级 | 加载内容 | 时机 | Token 成本 |
|------|---------|------|-----------|
| 1. 目录（Catalog） | Name + description | 会话开始 | ~50-100 tokens/技能 |
| 2. 指令（Instructions） | 完整 `SKILL.md` 正文 | 技能激活时 | <5000 tokens（推荐） |
| 3. 资源（Resources） | 脚本、参考、资产 | 指令引用时 | 按需 |

模型从一开始就看到目录，知道有哪些技能可用。当它决定某个技能相关时，加载完整指令。如果指令引用支持文件，模型根据需要单独加载它们。

### 13.2 步骤 1：发现技能

会话启动时，找到所有可用技能并加载其元数据。

#### 扫描位置

根据智能体环境扫描目录。大多数本地运行的智能体至少扫描两个范围：

| 范围 | 路径 | 用途 |
|------|------|------|
| 项目 | `<project>/.<your-client>/skills/` | 你的客户端原生位置 |
| 项目 | `<project>/.agents/skills/` | 跨客户端互操作 |
| 用户 | `~/.<your-client>/skills/` | 你的客户端原生位置 |
| 用户 | `~/.agents/skills/` | 跨客户端互操作 |

`.agents/skills/` 路径已成为跨客户端技能共享广泛采用的约定。扫描 `.agents/skills/` 意味着其他兼容客户端安装的技能对你的客户端自动可见，反之亦然。

许多实现还扫描 `.claude/skills/`（项目级和用户级）以实现实用兼容性，同时考虑 XDG 配置目录、git 根目录向上的祖先目录等。

#### 扫描内容

在每个技能目录中，查找**包含名为 `SKILL.md` 的文件的子目录**：

```
~/.agents/skills/
├── pdf-processing/
│   ├── SKILL.md          ← 发现
│   └── scripts/
│       └── extract.py
├── data-analysis/
│   └── SKILL.md          ← 发现
└── README.md             ← 忽略（不是技能目录）
```

实用扫描规则：
- 跳过不包含技能的目录，如 `.git/` 和 `node_modules/`
- 可选地尊重 `.gitignore` 以避免扫描构建产物
- 设置合理边界（例如最大深度 4-6 级，最多 2000 个目录）以防止大型目录树中的失控扫描

#### 处理名称冲突
当两个技能共享相同的 `name` 时，应用确定性优先规则：**项目级技能覆盖用户级技能**。发生冲突时记录警告。

#### 信任考虑
项目级技能来自正在处理的仓库，可能不受信任。考虑对项目级技能加载进行信任检查——仅当用户将项目文件夹标记为受信任时才加载它们。

### 13.3 步骤 2：解析 SKILL.md 文件

对于每个发现的 `SKILL.md`，提取元数据和正文内容。

#### Frontmatter 提取
`SKILL.md` 文件有两部分：`---` 分隔符之间的 YAML frontmatter，以及结束分隔符后的 Markdown 正文。解析：
1. 在文件开头找到开头的 `---` 和其后的结束 `---`
2. 解析它们之间的 YAML 块。提取 `name` 和 `description`（必填），以及任何可选字段
3. 结束 `---` 之后修剪后的所有内容是技能的正文内容

#### 处理格式错误的 YAML
为其他客户端编写的技能文件可能包含技术上无效但它们的解析器碰巧接受的 YAML。最常见问题是包含冒号的未加引号值：
```yaml
# 技术上无效的 YAML——冒号破坏了解析
description: Use this skill when: the user asks about PDFs
```
考虑回退方案，在重试之前将此类值包装在引号中或转换为 YAML 块标量。

#### 宽松验证
对问题发出警告但在可能时仍加载技能：
- Name 与父目录名不匹配 → 警告，仍加载
- Name 超过 64 字符 → 警告，仍加载
- Description 缺失或为空 → 跳过技能（描述对披露至关重要），记录错误
- YAML 完全无法解析 → 跳过技能，记录错误

#### 存储内容
每个技能记录至少需要三个字段：

| 字段 | 描述 |
|------|------|
| `name` | 来自 frontmatter |
| `description` | 来自 frontmatter |
| `location` | `SKILL.md` 文件的绝对路径 |

存储在内存中以 `name` 为键的映射中，以便在激活期间快速查找。

### 13.4 步骤 3：向模型披露可用技能

告诉模型存在哪些技能而不加载其完整内容。

#### 构建技能目录
对于每个发现的技能，以适合你技术栈的任何结构化格式（XML、JSON 或项目符号列表）包含 `name`、`description` 和可选的 `location`：

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extract PDF text, fill forms, merge files. Use when handling PDFs.</description>
    <location>/home/user/.agents/skills/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```

每个技能向目录添加约 50-100 tokens。即使安装了数十个技能，目录也保持紧凑。

#### 放置位置
两种常见方法：
- **系统提示部分**：将目录作为系统提示中的标记部分添加，前面是关于如何使用技能的简要说明
- **工具描述**：将目录嵌入专用技能激活工具的描述中

#### 行为指令
在目录旁边包含一个简短的指令块，告诉模型如何以及何时使用技能：

**如果模型通过读取文件激活技能：**
```
以下技能为特定任务提供专门指令。当任务匹配技能的描述时，
使用你的文件读取工具加载列出位置处的 SKILL.md，然后再继续。
当技能引用相对路径时，相对于技能目录（SKILL.md 的父目录）解析它们，
并在工具调用中使用绝对路径。
```

**如果模型通过专用工具激活技能：**
```
以下技能为特定任务提供专门指令。当任务匹配技能的描述时，
调用 activate_skill 工具并传入技能名称以加载其完整指令。
```

#### 过滤
某些技能应从目录中排除：用户在设置中禁用的技能、权限系统拒绝访问的技能、选择退出模型驱动激活的技能。**完全隐藏**过滤后的技能，而不是列出它们并在激活时阻止。

### 13.5 步骤 4：激活技能

当模型或用户选择技能时，将完整指令传递到对话上下文中。

#### 模型驱动激活
大多数实现依赖模型自身的判断作为激活机制。两种实现模式：

- **文件读取激活**：模型使用其标准文件读取工具调用目录中的 `SKILL.md` 路径。不需要特殊基础设施——智能体现有的文件读取能力就足够了
- **专用工具激活**：注册一个工具（例如 `activate_skill`），接受技能名称并返回内容。优点包括：控制返回什么内容、在结构化标签中包装内容、列出捆绑资源、强制执行权限、跟踪激活以进行分析

#### 用户显式激活
用户也应该能够直接激活技能，例如通过斜杠命令（`/skill-name`）或聊天界面中的技能选择器。

#### 模型接收什么
加载技能时，将完整的 `SKILL.md` 内容（或剥离 frontmatter 的正文）注入对话。如果使用专用工具，考虑用结构化标签包装返回的内容：
```xml
<skill name="pdf-processing">
  <location>/path/to/pdf-processing</location>
  <instructions>
    <!-- SKILL.md 正文内容在这里 -->
  </instructions>
  <bundled_resources>
    <resource>scripts/extract.py</resource>
    <resource>references/API-REFERENCE.md</resource>
  </bundled_resources>
</skill>
```

#### 权限白名单
如果支持 `allowed-tools` frontmatter 字段，激活技能时将工具使用限制为列出的模式。

### 13.6 步骤 5：随时间管理技能上下文

#### 保护技能内容免受上下文压缩
如果你的智能体实现了上下文压缩或摘要，确保活动技能的指令不会被压缩掉。技能内容应被视为高优先级上下文。

#### 重复数据删除激活
跟踪当前会话中已激活哪些技能，避免多次加载同一技能。如果技能在同一会话中再次被引用，则可以重用先前加载的内容。

#### 子智能体委托（可选）
对于复杂任务，考虑让技能在独立的子智能体中运行，该子智能体接收技能指令和任务特定上下文，但不污染主对话上下文。这对于可能产生大输出或长中间步骤的技能特别有用。

### 13.7 参考实现
- [skills-ref](../../../../../external/agentskills/skills-ref/) 库中的 `to_prompt` 函数展示了提示格式
- 官方文档：[agentskills.io/client-implementation/adding-skills-support](https://agentskills.io/client-implementation/adding-skills-support)
