---
id: "mermaid-safe-coding-rules"
source: "../../reports/project-governance/documentation-governance/retrospective-mermaid-rendering-fix-20260626/insight-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.toml"
---
# Mermaid 安全编码五规则

## 模式概述

在 Markdown 文档中使用 Mermaid 图表时，遵循五条安全编码规则可系统性避免 95% 以上的渲染失败问题。该模式从一次大规模渲染故障修复中萃取，覆盖空行、文本引号、列表触发、Subgraph 格式、边标签等核心陷阱，并已通过自动化检查脚本（check-mermaid.py）在全项目 653+ Markdown 文件上验证有效，且已集成至 CI 流水线。

## 成熟度

**L3（标准化+工具检查）** - 已满足以下条件：
- 在 SpecWeave 项目 653+ Markdown 文件上验证有效
- 已有自动化检查脚本 `.agents/scripts/check-mermaid.py`（覆盖空行、引号、列表触发、换行符等6类问题）
- 已有安全模板目录 `.agents/templates/mermaid-templates/`
- 待完成：CI 强制集成（L3→L4 跃迁条件）

## 核心规则

### 规则 1：禁止空行

Mermaid 代码块（```` ```mermaid ... ``` ````）内部**禁止使用任何空行**。空行会被部分渲染器（如飞书）解析为代码块结束，导致后续内容渲染失败。

**错误示例：**
```
flowchart LR
    A --> B

    B --> C
    style A fill:#ffcccc
```

**正确示例：**
```mermaid
flowchart LR
    A --> B
    B --> C
    style A fill:#ffcccc
```

**适用范围**：所有 Mermaid 图表类型（flowchart、sequenceDiagram、classDiagram、stateDiagram 等）。空行在 flowchart 中已确认导致解析中断，在其他图类型中行为未明，统一禁止最安全。

### 规则 2：文本引号原则

包含以下情况的节点标签、边标签、subgraph 标题，一律用双引号 `"..."` 包裹：

- 含中文字符
- 含特殊字符（`@`、`:`、`.`、`(`、`)`、`-`、空格等）
- 含英文短语（超过一个单词）

**必须加引号：**
```mermaid
flowchart LR
    A["中文节点"] --> B{"判断节点"}
    A -->|"@role 角色标签"| C["Hello World"]
    subgraph S1 ["子图标题"]
        N1["节点1"]
    end
```

**可以省略引号（纯英文单词/标识符）：**
```mermaid
flowchart LR
    A[Start] --> B[orchestrator]
    C[myNode] --> D[my-node]
```

> ⚠️ **重要区分**：双引号解决的是 Mermaid **语法层**解析问题（告诉解析器这是一个完整文本），但引号内的文本仍会被 Mermaid 内置的 Markdown 渲染器处理。
>
> **两阶段解析模型**：Mermaid 文本解析分两阶段独立运作——①语法解析阶段：引号帮助识别节点/标签边界；②Markdown渲染阶段：引号无穿透效果，内部文本照常进行 Markdown 解析（列表、加粗、链接等）。因此加引号不能阻止列表触发，必须从内容层面消除触发模式。

### 规则 2b：避免 Markdown 列表触发

节点文本中避免使用以下 Markdown 列表触发模式，即使已用双引号包裹也会触发解析：

| 禁止模式 | 错误示例 | 正确写法 |
|---------|---------|---------|
| 数字+英文句点+空格 | `A["1. 启动协议"]` | `A["1：启动协议"]`（中文冒号） |
| 短横线+空格（无序列表） | `A["- 项目A"]` | `A["-项目A"]` 或 `A["·项目A"]` |
| 星号+空格（无序列表） | `A["* 注意"]` | `A["*注意"]` 或 `A["⚠ 注意"]` |

**正确示例：**
```mermaid
flowchart TB
    S1["①语法结构层"] --> S2["②Subgraph层"]
    S2 --> S3["③节点文本层"]
    START("1：开始") --> CHECK{"判断：条件成立？"}
```

**根本原则**：Mermaid 节点文本中不要使用 Markdown 列表语法。需要编号时使用中文冒号（`1：`）、全角句点（`1．`）、圈号数字（`①`）等不触发列表的格式。

### 规则 2c：节点换行使用 `<br/>`

Mermaid 节点文本内的换行**统一使用 HTML 的 `<br/>` 标签**，禁止使用 `\n` 转义字符。

**为什么？** `\n` 在 flowchart/stateDiagram 节点中不会被解释为换行（部分渲染器显示为字面文本，部分压缩为单行）；虽然 `\n` 在 sequenceDiagram 的 Note 和消息文本中可以换行，但统一使用 `<br/>` 可以避免记忆上下文差异。

**错误示例：**
```
flowchart LR
    A["第一行\n第二行\n第三行"]
```

**正确示例：**
```mermaid
flowchart LR
    A["第一行<br/>第二行<br/>第三行"]
```

```mermaid
sequenceDiagram
    participant A as "开发者"
    Note over A: 第一行<br/>第二行
    A->>B: "消息文本<br/>可以换行"
```

**记忆口诀**：Mermaid 中换行一律用 `<br/>`，不要用 `\n`。

### 规则 3：Subgraph 安全格式

Subgraph 必须使用英文 ID + 显式中文标题格式：

```
subgraph EN_ID ["中文标题"]
    ...
end
```

**格式要点：**
- **ID 必须为英文标识符**：字母开头，不含中文、全角字符、特殊符号（含全角冒号 `：`）
- **中文标题放在双引号内**：格式为 `["标题文本"]`
- **ID 与方括号之间有空格**，方括号与引号之间无空格
- **Subgraph 块之间禁止空行**（参见规则1）

**错误写法：**
```
subgraph 感知层
subgraph 角色：架构师
subgraph S1["感知层"]
```

**正确写法：**
```mermaid
flowchart TB
    subgraph SENSE ["感知层"]
        N1["数据采集"]
    end
    subgraph ARCH ["角色：架构师"]
        N2["架构决策"]
    end
    N1 --> N2
```

### 规则 4：边标签格式

边标签统一使用 `-->|"标签"|目标` 格式，含中文/特殊字符的标签必须双引号包裹，纯英文标识符标签可省略引号。

**格式要点：**
- **含中文/特殊字符的标签**：双引号包裹，放在 `||` 内，如 `-->|"标签"|B`
- **纯英文标识符标签**：可省略引号，如 `-->|untagged|B`
- **标签与箭头之间无空格**：`-->|"标签"|` 是正确的，`--> |"标签"|` 是错误的
- **无边标签的箭头**：直接使用 `-->` 即可

**错误写法对照：**
| 错误写法 | 问题 | 正确写法 |
|---------|------|---------|
| `-->|数据|B` | 中文标签未加引号 | `-->|"数据"|B` |
| `-->|@role|B` | 特殊字符未加引号 | `-->|"@role"|B` |
| `--> |"标签"| B` | 箭头与标签间有空格 | `-->|"标签"|B` |

**正确示例：**
```mermaid
flowchart LR
    A -->|"带中文标签"| B
    A -->|"@特殊字符"| C
    A -->|untagged| D
    D --> E
```

### 规则 5：分层排查验证法

Mermaid 渲染错误存在"分层屏蔽"效应——结构层错误会阻止解析器到达内容层，修复结构错误后内容层错误才会显现。修复时应按五层顺序逐层排查，并预期错误会"层层暴露"。

```mermaid
flowchart TB
    S1["①语法结构层<br/>括号闭合/无空行"] --> S2["②Subgraph层<br/>ID合法/标题格式"]
    S2 --> S3["③节点文本层<br/>Markdown触发检查"]
    S3 --> S4["④边标签层<br/>特殊字符引号"]
    S4 --> S5["⑤Style层<br/>颜色值/样式语法"]
    style S1 fill:#d4edda
    style S5 fill:#f8d7da
```

| 层级 | 检查内容 | 典型错误 |
|------|---------|---------|
| ①语法结构层 | 括号/引号/direction 闭合、有无空行 | 空行截断、括号不匹配 |
| ②Subgraph层 | ID 合法性、标题格式 | 中文裸ID、全角冒号在ID中 |
| ③节点文本层 | 是否触发 Markdown 解析 | `数字. `、`- ` 触发列表 |
| ④边标签层 | 特殊字符是否加引号 | `@role`、中文标签无引号 |
| ⑤Style层 | 颜色值、样式语法 | 颜色名错误、fill格式错误 |

**心态要点**：不要因为修复后仍报错就认为方向错误，这是分层屏蔽效应——修复一个错误后暴露的是被屏蔽的旧错误，不是新引入的错误。继续逐层排查直到自动化工具报告 0 错误。

## 渲染器兼容性说明

不同 Markdown 渲染器对 Mermaid 的容错度不同。本地预览正常不能保证在所有渲染环境中正常。

| 平台 | Mermaid 版本 | 容错度 | 已知严格点 |
|------|-------------|--------|-----------|
| GitHub | 较新 | 宽松 | 一般问题都能渲染 |
| VS Code 预览 | 取决于插件 | 中等 | 空行可能不报错 |
| 飞书文档 | 定制版 | 严格 | 列表触发、空行零容忍 |
| GitLab | 较新 | 中等 | 部分语法有差异 |

**实践原则**：编写时就按照最严格渲染器的要求来，不要依赖容错；使用自动化脚本系统性扫描。

## 验证方法

### 自动化检查（推荐）

运行项目内置的 Mermaid 语法检查脚本：

```powershell
python .agents/scripts/check-mermaid.py
```

该脚本支持检测以下问题：
1. Mermaid 代码块内空行
2. Subgraph 中文裸 ID
3. 节点文本含列表触发模式（`数字. `、`- `、`* `）
4. 节点/边标签中文/特殊字符未加引号
5. 全角冒号在 Subgraph ID 中
6. 节点文本内使用 `\n` 换行（应使用 `<br/>`）
7. participant 别名含中文/空格未加引号（sequenceDiagram）
8. 迁移标签/状态描述含空格未加引号（stateDiagram）

支持 `--fix` 参数自动修复部分问题（空行、引号、`\n`→`<br/>`）。

### 分层环境验证

五层排查之外，建议按以下环境逐层验证：
1. **Mermaid Live Editor**：验证基本语法
2. **本地 Markdown 预览**：VS Code 等本地环境
3. **目标平台**：GitHub/GitLab/飞书等实际部署环境
4. **自动化脚本**：运行 `python .agents/scripts/check-mermaid.py`

## 相关资产

- **检查脚本**：`.agents/scripts/check-mermaid.py`
- **安全模板**：`.agents/templates/mermaid-templates/`（5种常用图表模板，内置安全格式）
- **开发规范**：`docs/development-standards.md`（Mermaid 编码规范章节）
- **陷阱速查表**：[mermaid-trap-cheatsheet.md](mermaid-trap-cheatsheet.md)
- **分层可视化模式**：[mermaid-layered-visualization.md](../methodology-patterns/document-architecture/mermaid-layered-visualization.md)
- **根因诊断模式**：[root-cause-diagnosis.md](../methodology-patterns/governance-strategy/root-cause-diagnosis.md)（分层错误屏蔽概念）

## 质量检查清单

编写 Mermaid 图表后，对照以下清单检查：

- [ ] 代码块内无任何空行
- [ ] 含中文/特殊字符/空格的节点文本已用双引号包裹
- [ ] 节点文本无「数字.空格」「- 空格」「* 空格」等列表触发模式
- [ ] 节点内换行统一使用 `<br/>`，未使用 `\n`
- [ ] Subgraph 使用 `ID ["标题"]` 格式，ID 为纯英文
- [ ] 边标签使用 `-->|"标签"|` 格式（中文/特殊字符加引号）
- [ ] participant 别名含中文/空格已加双引号（sequenceDiagram）
- [ ] Style 语句前无空行
- [ ] 运行 `check-mermaid.py` 无错误无警告

> 来源：Mermaid 渲染兼容性问题修复复盘（retrospective-mermaid-rendering-fix-20260626），Mermaid 渲染回归治理失效复盘（retrospective-mermaid-rendering-regression-20260629）补充规则2c换行符规范与自动化检查第6-8项。
