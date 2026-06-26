# .agents/conventions.md — 命名、代码与文档规范

## 文件命名规范

### 设计文档

所有设计文档统一存放于 `.agents/docs/superpowers/specs/` 目录：

```
{YYYY-MM-DD}-zhujian-wudao-{类型}-{编号范围}.md
```

- 日期格式：`2026-06-17`
- 项目名：`zhujian-wudao`（小写，连字符）
- 类型：`spec`（规格）| `review`（复盘）| `insights`（洞察）
- 编号范围：如 `01-30`、`31-52`

### 其他文件

- HTML 原型：`竹简悟道.html`（中文名，无日期前缀，仅含 HTML 结构）
- HTML 样式：`.agents/html/styles.css`（提取自原单文件）
- HTML 数据：`.agents/html/data.js`（dailyQuestions / aiResponses / bambooChapters）
- HTML 逻辑：`.agents/html/app.js`（所有交互逻辑，IIFE 包裹）
- 报名帖：`报名帖_竹简悟道.md`（中文 + 下划线）
- Agent 配置：`AGENTS.md`（全大写，根目录）
- Agent 模块：`.agents/*.md`（隐藏目录，小写文件名）

---

## 代码风格

### HTML / CSS / JS（竹简悟道.html）

**CSS 变量命名**：
- 前缀 `--`，kebab-case
- 分组前缀：`--bg-*`（背景）、`--text-*`（文字）、`--accent-*`（强调）、`--border-*`（边框）、`--shadow-*`（阴影）、`--font-*`（字体）、`--radius-*`（圆角）
- 颜色值用十六进制（`#F3E5C4`），不用 `rgb()` 或 `hsl()`

**JS 代码规范**：
- 整体包裹在 IIFE 中：`(function() { ... })()`
- 使用 `var` 声明（兼容旧环境）
- 类名 kebab-case（`chat-msg`、`scenario-tag`、`btn-outline`）
- 事件绑定用 `addEventListener`
- 函数暴露到全局用 `window.fnName = fnName`

### Markdown

- 标题层级：`#` → `####`，不超过四级
- 引用块 `>` 用于说明、引文、来源
- 代码块用 ` ``` ` 包裹
- 强调用 `**粗体**`
- 分隔线 `---` 用于大节分隔
- 列表用 `-` 或 `1.`

---

## 文档编写规范

### 洞察标准结构

```
## 洞察{N}：{标题}

**来源**：[§{章节}]

**核心内容**：

{简短摘要}

---

### 一、{第一子节}
...
### 七、{第七子节}
```

- 体道四法系统化手册必须为七节完整结构（见洞察 49/51/52/53）
- 非系统化洞察可以只有「来源 + 核心内容」基本结构
- 子节标题用中文数字：`一、二、三……七、`

### 交叉引用格式

所有跨文件引用必须使用**相对路径** + **行号定位**：

| 引用目标 | 格式 |
|----------|------|
| Spec 某节 | `[spec §5.2](docs/superpowers/specs/2026-06-17-zhujian-wudao-spec.md#L245-L263)` |
| 某条洞察 | `[洞察53](docs/superpowers/specs/2026-06-17-zhujian-wudao-insights-31-65.md#L1366-L1492)` |
| HTML 原型 | `[HTML](../竹简悟道_完整版.html#L710-L751)` |
| 报名帖 | `[报名帖](../报名帖_竹简悟道.md#L27)` |

⚠️ **重要**：洞察库第二部分文件名是 `insights-31-65.md`（R14已从31-52修正），包含洞察31-65共35条。所有引用必须使用正确的文件名。

### 洞察库头部声明

```markdown
# 洞察库·{层级名}（洞察{开始}-{结束}）

> **文件说明**：...
>
> **关联文件**：
> - [规格文档]({相对路径})
> - [洞察库{范围}]({相对路径})
>
> **统计**：本文件共{N}条洞察，{行数}行，{字节数}
>
> **三层结构**：
> - 产品层（1-15）：直接指导产品设计的洞察
> - 架构层（16-30）：支撑产品体系的底层洞察
```

### 统计数字需保持准确

每次编辑洞察库后必须更新头部的行数和洞察数。

---

## 洞察编号规则

- 全局递增，从 1 开始，当前最高 68
- 不能跳号、插号
- 按层级分段：1-15 产品层、16-30 架构层、31+ 哲学层
- 每条洞察的 Markdown 标题：`## 洞察{N}：{标题}`
- 标题不能同名（已知问题：洞察 16/17/18 均以"架构"开头，19/20 均以"命名"开头）

---

## HTML 功能模块约定

文件已拆分为三部分，加载顺序为 `data.js` → `app.js`：
- `.agents/html/styles.css` — 全部 CSS 变量及样式规则
- `.agents/html/data.js` — 三个全局变量：`dailyQuestions[]`、`aiResponses{}`、`bambooChapters[]`
- `.agents/html/app.js` — IIFE 包裹的应用逻辑，依赖上述全局变量

### 每日一问
- 问题数组 `dailyQuestions[]`，每项含 `quote`、`source`、`hint`
- 日期轮转：`dayIndex = today.getDate() % dailyQuestions.length`
- AI 回复使用 `aiResponses.fallback[]`，`dayIndex % replies.length` 轮转
- 收尾语："明天，再来问一个问题——不是找答案，而是练习'问'本身。"

### 场景对话

双轨标签体系，以 `且问且行` 为独立全宽入口，虚线分隔后跟一行七枚标签。每枚标签以 Spec 心境状态为主名、HTML 场景处境为辅助小字：

```
[且问且行]
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
[决策前]   [迷茫时]   [冲突中]   [变革期]   [日常修养]  [团队管理]  [个人成长]
 重大决策    方向探索    人际关系    职业困惑    创作瓶颈    管理困境    编程困境
```

**键名映射**：

| data-scenario | 主标签 | 辅助标签 | aiResponses 键 |
|---|---|---|---|
| `flow` | 且问且行 | — | `flow`（独立全宽按钮） |
| `deciding` | 决策前 | 重大决策 | `deciding` |
| `lost` | 迷茫时 | 方向探索 | `lost` |
| `conflict` | 冲突中 | 人际关系 | `conflict` |
| `changing` | 变革期 | 职业困惑 | `changing` |
| `cultivate` | 日常修养 | 创作瓶颈 | `cultivate` |
| `team` | 团队管理 | 管理困境 | `team` |
| `growing` | 个人成长 | 编程困境 | `growing` |

- 场景标签以 `<button class="scenario-tag">` 实现，`data-scenario` 为上述键名
- 点击切换 `active-tag` 类
- AI 回复按 `aiResponses[scenarioId]` 数组索引匹配
- 每条回复用 `<div class="chat-msg ai">` 包裹

### 帛书浏览
- 以 `<div class="bamboo-chapter">` 为章节容器
- 每章含原文（`chapter-text`）、注释（`chapter-notes`）、解读（`chapter-interpretation`）、版本差异（`chapter-diff`）
- 当前仅实现 8 章（目标 81 章）
