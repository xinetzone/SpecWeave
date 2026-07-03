---
id: "subagent-atomic-task-template"
domain: "methodology"
layer: "methodology"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "basic"
source: "docs/retrospective/reports/task-reports/retrospective-tech-interface-wiki-20260703/insight-extraction.md#关键洞察3"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.toml"
rules: []
references: []
skills: []
related_patterns:
  - "spec-mode-doc-creation-workflow"
  - "multi-agent-parallel-execution"
  - "atomization-three-criteria-test"
  - "bilingual-prompt-engineering"
---
# 子代理原子任务描述模板：五要素精确委托法

## 模式概述

使用general_purpose_task委托子代理创建原子文档时，任务描述必须包含五个精确要素：**精确绝对路径 + 完整frontmatter模板 + 结构化章节大纲 + 导航一致性强约束 + 硬约束清单**。模糊的任务描述（如"帮我写API章节"）会导致子代理返回结果几乎必然需要重写——因为子代理不知道文件放哪、frontmatter要什么字段、章节结构是什么、导航链接写什么文件名、不能超过多少行。五要素模板通过消除所有歧义，让子代理一次做对，避免"委托→返回不满意→修改→再修改"的循环。

## 问题现象

子代理任务描述模糊的常见后果：

1. **文件路径错误**：子代理把文件写到根目录或错误子目录，需要移动文件并修正所有相对路径
2. **frontmatter字段缺失**：子代理省略必需字段（category/tags/status/author/summary），导致索引生成降级
3. **章节结构不一致**：每个子代理返回的章节结构不同，无法横向对比，需要统一重构
4. **导航文件名错误**：子代理猜测前后章文件名（如05-practice而非规划的05-comparison），导致链接断裂
5. **文件行数失控**：没有行数约束，子代理可能写出500+行单文件，违反原子化原则
6. **重复劳动**：主代理需要逐一修正上述问题，修正时间甚至超过自己写
7. **链式错误**：一个子代理的路径错误导致依赖它的其他子代理导航也出错

这些问题的共同根因是：主代理假设子代理"应该知道"项目规范、文件结构、命名约定——但子代理是无状态的，没有项目上下文，所有约束必须显式传递。

## 解决方案

### 五要素任务描述模板

使用general_purpose_task时，query参数必须包含以下五个要素：

#### 要素1：精确绝对路径（必须）

使用Windows绝对路径（从盘符开始），不要让子代理猜路径：

```
创建文件：d:\spaces\SpecWeave\docs\knowledge\learning\interface-api-abi-protocol-wiki\02-api.md
```

❌ 错误："在wiki目录下创建API章节"
✅ 正确："创建文件：d:\spaces\SpecWeave\docs\knowledge\learning\interface-api-abi-protocol-wiki\02-api.md"

#### 要素2：完整frontmatter模板（必须）

提供完整YAML frontmatter，所有字段预填好值，子代理只需写入文件：

```yaml
---
id: "api-chapter"
title: "API（应用程序编程接口）"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/interface-api-abi-protocol-wiki/02-api.toml"
source: "wiki:interface-api-abi-protocol"
category: "learning"
tags: ["api", "interface", "programming", "tutorial", "wiki"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "API章节，包含API定义、5种API类型对比、主流API案例、代码调用示例"
---
```

**关键字段必须预填**：
- id：唯一标识符
- title：章节标题（含中文全称和英文缩写）
- category：分类（如learning/best-practices等）
- tags：标签数组
- date：创建日期
- status：stable
- author：SpecWeave
- summary：一句话摘要

❌ 错误："frontmatter按项目规范来"（子代理不知道项目规范是什么）
✅ 正确：直接给出完整frontmatter代码块，子代理复制即可

#### 要素3：结构化章节大纲（必须）

提供到二级标题的大纲，明确每个章节要写什么内容、包含什么元素：

```
文件内容结构（严格遵循）：
# API（应用程序编程接口）

## 1. 定义
- API的标准定义
- API在软件分层中的位置
- 设计目的与核心价值

## 2. 核心特征
- 5个核心特征（每个2-3句解释）
- 必须包含：抽象性、契约性、语言无关性、版本管理、可发现性

## 3. API类型对比
- 表格对比5种主流API类型：REST/GraphQL/SOAP/gRPC/WebSocket
- 对比维度：协议、数据格式、适用场景、优缺点

## 4. 主流API案例
- GitHub REST API案例
- Stripe API案例
- GraphQL API案例
- 每个案例包含：简介、请求示例（curl或fetch）

## 5. 代码示例
- curl调用示例
- JavaScript fetch示例
- 代码块使用正确语言标注

## 6. 导航
- 上一章：[Interface（接口）](01-interface.md)
- 下一章：[ABI（应用二进制接口）](03-abi.md)
- 总览：[返回总览](00-overview.md)
- 对比分析：[查看对比分析](05-comparison.md)
```

❌ 错误："写API的定义、特征、案例"（太模糊）
✅ 正确：列出每个二级标题，说明每个标题下要包含的具体内容和元素

#### 要素4：导航一致性强约束（必须）

**特别强调**导航链接中的文件名必须与规划一致，这是最易出错的点：

```
⚠️ 关键约束：导航链接文件名必须严格使用以下名称（与tasks.md规划一致）：
- 前一章：01-interface.md（不要写成interface.md或chapter1.md）
- 后一章：03-abi.md（不要写成abi.md或chapter3.md）
- 总览：00-overview.md
- 对比章：05-comparison.md（⚠️特别注意：不是05-practice.md或comparison.md）
- 参考资料章：06-resources.md
```

❌ 错误："加上前后章导航"（子代理会猜文件名）
✅ 正确：列出每个导航链接的准确文件名，特别是容易猜错的对比章/总结章名称

#### 要素5：硬约束清单（必须）

列出不可违反的硬性规则：

```
硬约束：
1. 文件总行数严格 < 300行（含frontmatter），超过请精简内容
2. 禁止添加任何文件中未提及的额外章节
3. 代码示例必须使用正确的markdown代码块语法（```language）
4. 所有markdown表格必须对齐美观
5. 不要添加注释（<!-- -->形式的HTML注释也不要加）
6. 所有本地链接使用相对路径，不要用绝对路径
7. Mermaid代码块使用```mermaid标记（如需要）
```

❌ 错误："遵循项目规范"（子代理不知道项目规范）
✅ 正确：逐条列出不可违反的规则，特别是行数限制和禁止事项

### 完整模板示例

```python
general_purpose_task(
    description="创建API章节文档",
    query="""创建文件：d:\\spaces\\SpecWeave\\docs\\knowledge\\learning\\interface-api-abi-protocol-wiki\\02-api.md

以下是完整的文件内容要求，严格按照要求创建，不要添加额外内容：

---
id: "api-chapter"
title: "API（应用程序编程接口）"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/interface-api-abi-protocol-wiki/02-api.toml"
source: "wiki:interface-api-abi-protocol"
category: "learning"
tags: ["api", "interface", "programming", "tutorial", "wiki"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "API章节，包含API定义、5种API类型对比、主流API案例、代码调用示例"
---

# API（应用程序编程接口）

[...按照要素3的结构化大纲写正文内容...]

## 导航
- 上一章：[Interface（接口）](01-interface.md)
- 下一章：[ABI（应用二进制接口）](03-abi.md)
- 总览：[返回总览](00-overview.md)
- 对比分析：[查看对比分析](05-comparison.md)

⚠️ 导航文件名约束：必须严格使用上述文件名，不要改名。对比章是05-comparison.md（不是05-practice.md）。

硬约束：
1. 文件总行数 < 300行（含frontmatter）
2. 禁止添加额外章节
3. 代码块使用正确语言标注（bash/typescript/python等）
4. 不要添加HTML注释
5. 所有链接使用相对路径
6. 返回完成后报告文件行数""",
    response_language="中文"
)
```

### 子代理返回验证

子代理完成后，立即验证：
1. 读取文件确认frontmatter完整
2. 检查文件行数<300（check-file-size.py）
3. 检查导航链接中的文件名是否正确（特别是容易猜错的文件名）
4. 运行check-links.py确认链接有效

```
子代理返回
    │
    ▼
┌─────────────────────┐
│ 快速验证（30秒）     │
│ 1. 读文件确认结构    │
│ 2. 检查行数          │
│ 3. 核对导航文件名    │
│ 4. 运行check-links  │
└─────────────────────┘
    │
    ├── 通过 ──→ 继续下一个任务
    │
    └── 失败 ──→ 立即修正（不要积累到最后）
```

## 适用场景

- ✅ 使用general_purpose_task委托子代理创建原子markdown文档
- ✅ 一个子代理负责一个文件的场景
- ✅ 多文件并行创建（多个独立子代理同时工作）
- ✅ 文档有统一的frontmatter规范和导航约定
- ✅ 对文件大小有明确约束（如<300行）
- ❌ 子代理负责多步操作（如"创建目录+写三个文件+运行验证"）——应拆成多个单文件任务
- ❌ 非文档任务（如代码重构、数据分析）——本模式专为文档创建设计
- ❌ 简单的单句查询（不需要五要素，直接问即可）

## 实际案例

### 案例1：Interface/API/ABI/Protocol技术Wiki子代理委托（本次验证）

主进程创建00-overview.md、05-comparison.md、06-resources.md（核心和总览章节由主进程掌控），同时委托3个子代理并行创建01-interface.md、02-api.md、03-abi.md、04-protocol.md。

**子代理任务五要素**：
- 要素1 路径：如`d:\spaces\SpecWeave\docs\knowledge\learning\interface-api-abi-protocol-wiki\03-abi.md`
- 要素2 frontmatter：完整7字段模板直接给出
- 要素3 大纲：定义→核心特征→API vs ABI对比→代码案例→导航，二级标题明确
- 要素4 导航约束：明确指出前一章02-api.md、后一章04-protocol.md、对比章05-comparison.md
- 要素5 硬约束：<300行、必须有ctypes代码示例、禁止额外章节

**结果**：4个子代理返回的文件一次性通过frontmatter检查和链接检查，仅发现1处导航文件名偏差（05-practice vs 05-comparison），主进程在即时验证阶段10秒修正。无大规模重写。

**对比模糊委托的反事实估计**：如果只说"写ABI章节"，预计会出现：路径错误（需移动）、frontmatter缺3+字段（需补全）、缺少代码示例（需添加）、导航文件名错误（需修正），每个文件修正时间约3-5分钟，4个文件合计12-20分钟。

## 反模式

### 反模式1：一句话任务描述

```
query: "帮我写02-api.md，关于API的章节"
```

子代理需要猜路径、猜frontmatter字段、猜章节结构、猜导航文件名——几乎必然猜错至少2-3项。

**正确做法**：使用五要素模板，每个要素都明确给出。

### 反模式2：给参考文件但不提取规范

```
query: "参考01-interface.md的格式写02-api.md"
```

子代理可能参考了格式但遗漏了关键字段，或复制了01的标签但没改成API相关的标签，或导航链接保留了01的文件名而没更新。

**正确做法**：不要让子代理"参考"其他文件推断规范——直接把规范（frontmatter、大纲、导航、硬约束）显式写在任务描述里。

### 反模式3：一个子代理写多个文件

```
query: "帮我写01-interface.md、02-api.md、03-abi.md三个文件"
```

任务复杂度指数上升，子代理上下文过长容易出错，而且三个文件之间的导航一致性更难保证。出错后排查也更困难。

**正确做法**：一个general_purpose_task只委托一个文件，多个文件用多个并行子代理。

### 反模式4：省略导航约束（最常见错误）

主代理觉得"文件名不是很明显吗"，但子代理没有上下文，对比章可能叫05-comparison、05-compare、05-practice、05-summary、comparison.md等等——子代理猜对的概率很低。

**正确做法**：总是显式列出所有导航链接的准确文件名，特别标记容易猜错的名称。

### 反模式5：子代理返回后不验证

觉得"子代理应该做对了"，直接继续下一个任务。等所有文件写完才检查，发现4个文件有3个的frontmatter缺字段、2个的导航文件名错了，需要逐个文件修正。

**正确做法**：每个子代理返回后立即做30秒快速验证（读文件开头确认frontmatter、检查导航文件名、运行check-links），在上下文新鲜时修正。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [spec-mode-doc-creation-workflow.md](spec-mode-doc-creation-workflow.md) | 上位 | 本模式是Spec Mode工作流阶段3（原子执行）的子模式，专门解决子代理委托问题 |
| [multi-agent-parallel-execution.md](../../architecture-patterns/multi-agent-parallel-execution.md) | 配套 | 多个独立章节可用多代理并行，每个代理使用本模式的五要素模板 |
| [atomization-three-criteria-test.md](../document-architecture/atomization-three-criteria-test.md) | 前置 | 任务拆分到原子级别（一个任务=一个文件）是使用本模式的前提 |
| [bilingual-prompt-engineering.md](bilingual-prompt-engineering.md) | 相关 | 技术术语使用英文、解释使用中文的双语提示原则可应用于任务描述 |

## 边界与选型

**何时使用本模式**：
- 委托子代理创建单个markdown文档文件
- 项目有明确的frontmatter规范
- 文档有统一的导航约定
- 需要精确控制输出格式和内容范围

**何时不需要五要素完整模板**：
- 委托简单的搜索/查询任务 → 直接描述问题即可
- 委托代码编写（非文档） → 提供代码规范和接口定义即可，不需要frontmatter
- 委托分析/总结任务 → 描述分析目标和输出格式即可
- 主进程自己写文件 → 不需要委托，直接写

**任务复杂度升级策略**：
- 简单任务（搜索、查询）：一句话描述即可
- 单文件创建：使用本模式五要素模板
- 多文件创建：每个文件一个子代理，并行执行
- 多步复杂操作（创建+验证+提交）：拆分为多个顺序任务，每个任务仍遵循五要素
