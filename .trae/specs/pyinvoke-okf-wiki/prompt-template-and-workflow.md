---
type: Pattern
title: 源码学习→OKF Wiki生成 通用提示词模板与Workflow
description: 基于 seven-concepts 方法论（R→I→E→V→C），学习开源项目源码并生成 OKF v0.2 规范知识包的可复用提示词模板和工作流程
tags: [seven-concepts, okf, wiki, prompt-template, workflow, knowledge-precipitation]
generated: { by: reference_agent/trae-glm, at: 2026-08-21T14:00:00Z }
verified: { by: process:pattern-extraction, at: 2026-08-21T14:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: seven-concepts-methodology
    resource: /references/pyinvoke-source.md
    title: PyInvoke 源码学习实践（本模式萃取案例）
---

# 源码学习→OKF Wiki生成：通用提示词模板与Workflow

## 一、适用场景

当你需要**系统化学习一个开源项目/库的源码，并产出结构化的OKF规范Wiki教程**时，使用此模板和workflow。典型场景：

- 学习一个新的Python/JavaScript/Go库，需要深入理解其架构和API
- 为团队生成内部库的文档Wiki
- 对开源项目进行源码级知识沉淀
- 生成符合OKF v0.2规范的可溯源知识包

## 二、Workflow：R→I→E→V→C 五阶段

### R阶段（Retrospective/Read）：源码深度阅读与事实采集

**目标**：通读源码核心模块，提取可验证的事实清单，零推测。

**步骤**：
1. 列出源码目录结构，识别核心模块文件
2. 逐个阅读核心模块，对每个模块提取事实（类名、方法签名、关键参数、数据流、继承关系）
3. 所有事实编号为 F-xxx，每个事实必须指向具体文件和代码行
4. 事实清单写入 `.trae/specs/<task-name>/facts.md`
5. **禁止**：在R阶段做任何架构推断、设计评价、或"我认为"的判断

**事实采集清单模板**：
```
F-001: <模块名> - <类/函数名> 定义于 <文件路径:行号>，继承自 <父类>
F-002: <类>.<方法> 接受参数 (<参数列表>)，返回 <返回类型>，功能是 <一句话>
F-003: <模块A> 中的 <对象> 被 <模块B> 的 <方法> 引用，传递 <数据>
...
```

### I阶段（Insight）：架构洞察与知识结构设计

**目标**：从事实中提炼架构洞察，设计知识包的文档结构。

**步骤**：
1. 基于事实清单，提炼3-5个核心架构洞察（每个洞察包含四元组）：
   - **陈述**：一句话说清架构特征
   - **证据**：引用哪些F-xxx事实支持
   - **反常识**：为什么初学者会误解/这个设计的反直觉之处
   - **行动**：这对文档组织有什么指导意义
2. 设计知识地图：文档分组、依赖关系、学习路径
3. 确定每个概念文档覆盖哪些事实
4. 洞察写入 `.trae/specs/<task-name>/insights.md`

### E阶段（Extraction/Execution）：批量生成OKF文档

**目标**：按OKF v0.2规范生成所有文档。

**步骤**：
1. 创建Bundle目录结构：
   ```
   <bundle-name>/
   ├── index.md              # 根索引（含 okf_version frontmatter）
   ├── log.md                # 变更日志
   ├── concepts/             # 概念文档
   │   ├── index.md          # 概念索引（无frontmatter）
   │   ├── 00-xxx.md
   │   ├── 01-xxx.md
   │   └── ...
   ├── examples/             # 示例文档
   │   ├── index.md
   │   └── ...
   └── references/           # 信源登记
       ├── index.md
       └── <source>.md
   ```
2. 先生成 references/ 信源登记（这是所有sources字段的指向目标）
3. 再生成 concepts/ 概念文档（按学习路径顺序）
4. 然后生成 examples/ 示例文档（每个对应一个或多个概念）
5. 最后生成各级 index.md 导航文件
6. **文档生成可以分批并行**，每批5-7个文件，通过 general_purpose_task 委派

**文档frontmatter模板**：
```yaml
---
type: <Concept|Example|Reference|Pattern|Specification>
title: <文档标题>
description: <一句话描述，30-80字>
tags: [<标签1>, <标签2>, ...]
generated: { by: <生成者标识>, at: <ISO8601时间> }
verified: { by: process:seven-concepts-v, at: <ISO8601时间> }
status: <draft|stable|deprecated>
stale_after: <YYYY-MM-DD过期日期>
sources:
  - id: <信源ID>
    resource: /references/<source-file>.md
    title: <信源标题>
---
```

**文档内容规范**：
- 开头用1-2段概述这个概念/示例是什么
- 使用 ## 二级标题分节，不要使用 #（留给文件标题）
- 代码块标注语言（`python`/`bash`/`yaml`等）
- 每个文档结尾必须有 `## 相关概念` 章节，列出交叉链接
- 交叉链接使用 `/concepts/xxx.md` 或 `/examples/xxx.md` 的bundle-relative路径
- 中文撰写，英文技术术语首次出现时括号注释解释

### V阶段（Verification）：独立审查与修复

**目标**：验证所有文档的格式合规性、链接有效性、事实准确性。

**检查清单**：
1. **结构检查**：目录结构是否符合OKF规范，是否有遗漏文件
2. **Frontmatter检查**：每个文档是否有完整的type/title/description/tags/generated/verified/status/stale_after/sources字段
3. **链接检查**：所有交叉链接的目标文件是否存在
4. **事实溯源检查**：抽查10个关键事实声明，确认可追溯到源码
5. **代码示例检查**：代码示例是否语法正确、API调用是否与源码一致
6. **Index完整性检查**：各级index.md是否列出了所有对应目录的文件
7. **重复/矛盾检查**：不同文档间是否有矛盾描述

**修复原则**：
- 链接错误：修复链接路径
- 事实错误：回到R阶段核对源码，修正内容
- 格式错误：补齐frontmatter字段
- 遗漏内容：补充缺失的文档或章节

### C阶段（Commit）：模式萃取与沉淀

**目标**：将本次经验沉淀为可复用的提示词模板和workflow。

**步骤**：
1. 回顾整个流程，记录哪些步骤顺利、哪些遇到问题
2. 萃取通用提示词模板（见下方第三节）
3. 记录关键决策点和注意事项
4. 将模式沉淀到知识库（如 `.agents/docs/retrospective/patterns/`）
5. 生成 log.md 记录本次变更历史

## 三、通用提示词模板

### 模板1：项目初始化与R阶段

```
请帮我学习项目 `<源码路径>`，生成符合OKF v0.2规范的Wiki教程到 `<输出bundle路径>`，
遵循 `<规范文件路径>` 的格式要求。

请按以下步骤执行：

【R阶段：源码阅读与事实采集】
1. 首先列出源码目录结构，识别所有核心模块文件
2. 逐个阅读核心模块源码，提取可验证的事实（类定义、方法签名、参数、数据流、继承关系）
3. 所有事实编号为 F-xxx，写入 `<spec-dir>/facts.md`
4. 每个事实必须指向具体文件路径，禁止推测和编造

事实采集完成后，将事实清单提供给我确认，然后进入下一阶段。
```

### 模板2：I阶段架构洞察

```
基于 facts.md 中的 <N> 个事实，提炼架构洞察和知识结构：

1. 提炼3-5个核心架构洞察，每个包含：
   - 陈述：一句话说清架构特征
   - 证据：引用哪些F-xxx事实
   - 反常识：初学者容易误解的点
   - 行动：对文档组织的指导意义

2. 设计知识地图：
   - 概念文档分组（入门/核心/高级）
   - 文档间的依赖关系和学习路径
   - 每个概念文档覆盖哪些事实

3. 确定文档清单：
   - concepts/ 下需要哪些文档，每个的标题和一句话描述
   - examples/ 下需要哪些示例，每个覆盖哪些概念
   - references/ 下需要哪些信源登记

将洞察和知识地图写入 `<spec-dir>/insights.md`。
```

### 模板3：E阶段批量生成文档

```
请生成OKF规范的中文Markdown文档，遵循以下规则：

【格式规则】
- YAML frontmatter必须包含：type, title, description, tags, generated, verified, status, stale_after, sources
- generated: { by: "reference_agent/<agent-name>", at: "<ISO时间>" }
- verified: { by: "process:seven-concepts-v", at: "<ISO时间>" }
- status: "stable", stale_after: "<过期日期>"
- sources: 指向 references/ 下的信源文件
- 交叉链接使用 / 开头的bundle-relative路径
- 中文撰写，英文术语保留并首次解释
- 每个文档结尾有"## 相关概念"章节
- 代码块标注语言，API调用必须与源码一致
- 禁止虚构API或行为

【内容要求】
- 每个概念文档500-5000字，用 ## 分节
- 示例文档必须包含完整可运行代码
- 信源文档列出所有核心模块和版本信息

请生成以下文件：
<逐文件列出文件路径、type、title、description、应覆盖的事实编号>
```

### 模板4：V阶段验证

```
请对 `<bundle路径>` 下的所有文档执行独立审查：

1. 结构检查：目录结构是否完整，是否有遗漏
2. Frontmatter检查：每个文档是否有完整的必填字段
3. 链接检查：所有交叉链接的目标文件是否存在
4. 事实抽查：随机抽查10个关键声明，对照 `<源码路径>` 验证准确性
5. 代码检查：代码示例语法是否正确，API调用是否匹配源码
6. Index检查：各级index.md是否完整列出所有文件

输出检查报告，列出发现的问题，然后逐一修复。
```

## 四、关键注意事项

1. **R阶段零推测原则**：事实采集阶段只记录"代码里有什么"，不记录"我觉得这是做什么的"。后者属于I阶段。
2. **信源先行**：先生成 references/ 信源文件，再生成其他文档，避免sources字段指向不存在的文件。
3. **分批生成**：概念文档分2-3批生成（入门/核心/高级），每批5-7个文件，避免单次上下文过大导致质量下降。
4. **Index最后写**：所有内容文档生成完毕后，最后写各级index.md，确保条目完整。
5. **代码示例真实性**：所有代码示例必须基于实际源码API，禁止编造不存在的方法或参数。拿不准的API回到R阶段核对源码。
6. **交叉链接一致性**：交叉链接路径使用 `/` 开头的bundle-relative路径（如 `/concepts/02-task-basics.md`），不要使用相对路径（`../concepts/xxx.md`）。
7. **index文件无frontmatter**：除了根 index.md 可以有 `okf_version` frontmatter外，子目录的 index.md 不应该有frontmatter。

## 五、产出物清单

完成一次完整流程后的产出物：

| 产出物 | 路径 | 说明 |
|--------|------|------|
| 事实清单 | `.trae/specs/<name>/facts.md` | R阶段采集的全部源码事实 |
| 架构洞察 | `.trae/specs/<name>/insights.md` | I阶段提炼的洞察和知识地图 |
| 知识包 | `projects/<bundle-path>/` | E阶段生成的完整OKF bundle |
| 变更日志 | `<bundle>/log.md` | 各日期的变更记录 |
| 模式沉淀 | `.agents/docs/retrospective/patterns/` | C阶段萃取的通用模式 |

## 六、时间估算

基于PyInvoke（约15个核心模块，12个概念文档，5个示例文档）的实践：

| 阶段 | 预估时间 | 说明 |
|------|----------|------|
| R阶段 | 15-30分钟 | 取决于源码规模，每个核心模块约1-2分钟 |
| I阶段 | 5-10分钟 | 洞察提炼+知识地图设计 |
| E阶段 | 20-40分钟 | 分批并行生成，每批约5-10分钟 |
| V阶段 | 10-15分钟 | 检查+修复 |
| C阶段 | 5-10分钟 | 模式萃取+log生成 |
| **总计** | **55-105分钟** | 约1-1.5小时完成一个中型库的Wiki |
