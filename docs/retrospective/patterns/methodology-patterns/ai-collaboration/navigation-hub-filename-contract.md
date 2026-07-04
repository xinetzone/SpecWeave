---
id: "navigation-hub-filename-contract"
domain: "methodology"
layer: "methodology"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "basic"
source: "docs/retrospective/reports/project-reports/idl-wiki-tutorial-retro-20260704.md#洞察1+洞察4"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/navigation-hub-filename-contract.toml"
rules: []
references: []
skills: []
related_patterns:
  - "subagent-atomic-task-template"
  - "spec-mode-doc-creation-workflow"
  - "bidirectional-navigation-links"
  - "link-decay-laws"
---
# 导航枢纽文件名契约模式：全局清单 vs 局部清单

## 模式概述

在并行 sub-agent 创建多文件教程时，**导航枢纽文件**（如 `00-overview.md`，需引用全部章节）的 sub-agent prompt 必须包含**完整的文件名清单**作为不可变更的全局契约，而非仅传递前后章的局部契约。sub-agent 没有项目上下文，收到章节标题时会自行推断文件名，而导航枢纽文件需要引用 N 个章节，推断错误概率随 N 线性放大——1 个推断错误导致 1 处断链，N 个章节全部推断错误会导致 N 处断链集中爆发在单一文件。

本模式是 [subagent-atomic-task-template](subagent-atomic-task-template.md) 要素4（导航一致性强约束）的**全局版补充**：要素4 解决单文件局部导航（前后章文件名锁定），本模式解决导航枢纽文件的全局导航（全部章节文件名锁定）。

## 问题现象

并行 sub-agent 创建多文件教程时的典型失败链：

1. **主 agent 仅传递章节标题**：在分派 `00-overview.md` 任务时，prompt 中列出"9 章导航表"的章节号和标题（如"02 - IDL 基本语法结构"），但未明确锁定文件名
2. **sub-agent 自行推断文件名**：sub-agent 根据"IDL 基本语法结构"推断为 `02-syntax-structure.md`，而实际创建文件的 sub-agent 遵循 spec 约定使用 `02-syntax-basics.md`
3. **断链集中爆发**：导航枢纽文件引用全部 N 章，每章推断错误产生 1-2 处断链，N=9 时单文件断链数可达 10+
4. **修复成本可控但累积**：单次修复 6 次 `Edit replace_all` 约 2 分钟，但如果未运行链接检查则会带病提交

**关键特征**：断链**全部集中在导航枢纽文件**，其他分章文件（01-08）的链接全部正确——因为分章文件只引用相邻章节（局部契约），而导航枢纽文件需要引用全部章节（全局契约）。

## 解决方案

### 全局文件名清单契约

在分派导航枢纽文件的 sub-agent 任务时，prompt 中必须包含**完整的文件名清单**作为不可变更的契约：

```
⚠️ 全局文件名契约（导航枢纽文件专用）：

本文件需要引用以下全部章节，文件名必须严格使用以下清单，不得自行推断或改名：

| 章节号 | 文件名（严格使用） | 章节标题 |
|--------|-------------------|---------|
| 00 | 00-overview.md | 概念总览（本章） |
| 01 | 01-what-is-idl.md | IDL 定义与作用 |
| 02 | 02-syntax-basics.md | IDL 基本语法结构 |
| 03 | 03-major-idl-specs.md | 主要 IDL 规范介绍 |
| 04 | 04-comparison.md | IDL 规范对比 |
| 05 | 05-toolchain.md | IDL 编译流程与工具链 |
| 06 | 06-use-cases.md | 实际应用案例与最佳实践 |
| 07 | 07-vs-modern-formats.md | 与现代接口描述方式对比 |
| 08 | 08-resources.md | 学习资源与参考资料 |

❌ 禁止：根据章节标题自行推断文件名（如把"02 - 基本语法结构"推断为 02-syntax-structure.md）
✅ 正确：严格使用上表文件名列的名称
```

### 与局部契约的区别

| 契约类型 | 适用文件 | 传递内容 | 失败规模 |
|---------|---------|---------|---------|
| **局部契约**（要素4） | 分章文件（01-08） | 仅前后章文件名（2 个） | 1-2 处断链 |
| **全局契约**（本模式） | 导航枢纽文件（00） | 全部章节文件名（N 个） | N 处断链集中爆发 |

### 识别导航枢纽文件

以下文件属于导航枢纽文件，必须使用全局契约：

1. **总览文件**（`00-overview.md`）：引用全部章节的导航表
2. **索引文件**（`README.md`、`index.md`）：引用全部子页面
3. **对比文件**（`04-comparison.md`）：引用被对比的多个规范章节
4. **资源文件**（`08-resources.md`）：交叉引用全部相关 wiki
5. **任何引用 ≥3 个其他文件的章节**：均应视为导航枢纽

### 完整 sub-agent 任务模板（导航枢纽文件专用）

```python
general_purpose_task(
    description="创建导航枢纽文件 00-overview.md",
    query="""创建文件：d:\\spaces\\SpecWeave\\docs\\knowledge\\learning\\{wiki-name}\\00-overview.md

[完整 frontmatter 模板]

# {教程标题} - 总览

[引言内容]

## N 章导航表

| 章节 | 标题 | 内容简述 |
| --- | --- | --- |
| 00 | [概念总览（本章）](00-overview.md) | ... |
| 01 | [章节标题](01-xxx.md) | ... |
| 02 | [章节标题](02-xxx.md) | ... |
[...全部章节...]

⚠️ 全局文件名契约（导航枢纽文件专用）：

本文件需要引用以下全部章节，文件名必须严格使用以下清单，不得自行推断：
[完整文件名清单表格]

❌ 禁止：根据章节标题自行推断文件名
✅ 正确：严格使用清单中的文件名

硬约束：
1. 文件总行数 < 300 行
2. 导航表必须包含全部 N 章
3. 所有链接使用相对路径
4. 返回完成后报告文件行数
""",
    response_language="中文"
)
```

## 适用场景

- ✅ 并行 sub-agent 创建多文件教程，存在导航枢纽文件（00-overview/index/README）
- ✅ 导航枢纽文件需要引用 ≥3 个其他 sub-agent 创建的文件
- ✅ 主 agent 在分派任务时已确定全部文件名清单（spec 阶段已锁定）
- ✅ 文件名包含缩写、简称或非直观命名（如 `02-syntax-basics.md` 而非 `02-syntax.md`）
- ❌ 串行创建文件（主 agent 自己写导航枢纽文件，无需契约传递）
- ❌ 文件名完全遵循"章节号-标题全拼.md"模式且无歧义（sub-agent 推断正确率高）
- ❌ 单文件任务（无导航枢纽概念）

## 实际案例

### 案例1：IDL Wiki 教程创建（本次验证）

**任务背景**：9 个并行 sub-agent 创建 `idl-wiki/` 目录下 9 个 wiki 文件（00-08）

**失败过程**：
- 主 agent 分派 `00-overview.md` 任务时，prompt 中提供了"9 章导航表"的章节号和标题
- sub-agent 根据标题自行推断 6 个文件名：
  - `02-syntax-structure.md`（实际：`02-syntax-basics.md`）
  - `03-major-specs.md`（实际：`03-major-idl-specs.md`）
  - `04-spec-comparison.md`（实际：`04-comparison.md`）
  - `05-compiler-toolchain.md`（实际：`05-toolchain.md`）
  - `06-cases-and-practices.md`（实际：`06-use-cases.md`）
  - `07-modern-comparison.md`（实际：`07-vs-modern-formats.md`）
- 链接检查捕获 10 个断链，全部集中在 `00-overview.md`
- 修复：6 次 `Edit replace_all` 替换错误文件名，约 2 分钟

**对比反事实估计**：如果主 agent 在 prompt 中传递了完整的文件名清单（本模式），sub-agent 会直接使用清单中的文件名，断链数为 0，无需修复。

**验证数据**：
- 导航枢纽文件（00-overview.md）断链数：10
- 分章文件（01-08）断链数：0
- 断链集中率：100%（全部在导航枢纽文件）

### 案例2：Interface/API/ABI/Protocol Wiki（对照案例）

**任务背景**：7 个并行 sub-agent 创建 `interface-api-abi-protocol-wiki/` 目录下 7 个 wiki 文件

**部分成功**：主 agent 在分派 `00-overview.md` 时提供了部分文件名约束，但仍有一处导航文件名偏差（`05-practice` vs `05-comparison`），主进程在即时验证阶段 10 秒修正。

**对比分析**：该案例主 agent 部分使用了全局契约（列出了文件名但未完整覆盖），断链数 1；IDL Wiki 案例未使用全局契约，断链数 10。断链数与契约完整度负相关。

## 反模式

### 反模式1：仅传递章节标题不传递文件名

```
query: "创建 00-overview.md，包含 9 章导航表：00 概念总览、01 IDL 定义、02 基本语法、03 主要规范..."
```

sub-agent 会根据标题推断文件名，导航枢纽文件引用全部章节，推断错误率随章节数线性增长。

**正确做法**：传递完整的文件名清单表格，明确每个章节的文件名。

### 反模式2：仅传递局部契约（前后章）

```
query: "创建 00-overview.md，下一章是 01-what-is-idl.md"
```

主 agent 误以为"00 的下一章是 01"就够了，但 00 作为导航枢纽需要引用 01-08 全部章节，局部契约不够。

**正确做法**：导航枢纽文件必须使用全局契约（全部章节文件名），而非局部契约（仅前后章）。

### 反模式3：传递文件名但允许 sub-agent 改名

```
query: "创建 00-overview.md，参考以下章节标题写导航表（文件名你可以自己定）"
```

允许 sub-agent 自行命名会导致全局不一致——其他 sub-agent 创建的文件名与本文件引用的文件名不匹配。

**正确做法**：文件名是主 agent 在 spec 阶段锁定的不可变更契约，sub-agent 必须严格使用，不得改名。

### 反模式4：跳过链接检查

主 agent 传递了完整的文件名清单，但 sub-agent 在写入时手误打错（如 `02-syntax-basics.md` 写成 `02-syntax-basic.md`），如果不运行 `check-links.py` 无法发现。

**正确做法**：即使使用了全局契约，提交前仍必须运行 `check-links.py` 作为最后一道防线（参见 [spec-mode-doc-creation-workflow](spec-mode-doc-creation-workflow.md) 阶段4）。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [subagent-atomic-task-template.md](subagent-atomic-task-template.md) | 互补 | 要素4（局部契约）解决单文件前后章导航，本模式（全局契约）解决导航枢纽文件的全局导航，两者形成完整契约体系 |
| [spec-mode-doc-creation-workflow.md](spec-mode-doc-creation-workflow.md) | 上位 | 本模式是 Spec Mode 文档创建工作流阶段3（原子执行）的子模式，专门解决导航枢纽文件的 sub-agent 委托问题 |
| [bidirectional-navigation-links.md](../document-architecture/bidirectional-navigation-links.md) | 支撑 | 双向导航三链路（prev/next/目录）是导航枢纽文件的链接结构基础，本模式确保这些链接的文件名正确 |
| [link-decay-laws.md](../document-architecture/link-decay-laws.md) | 相关 | 链接衰变四规律中"跨目录最脆弱"与本模式的"导航枢纽集中爆发"互相印证——枢纽文件链接数最多，衰变概率最高 |

## 边界与选型

**何时使用本模式**：
- 并行 sub-agent 创建 ≥3 个相互引用的文件
- 存在导航枢纽文件（00-overview/index/README/对比章/资源章）
- 文件名包含非直观命名（缩写、简称、特殊后缀）
- 主 agent 已在 spec 阶段锁定全部文件名

**何时不需要本模式**：
- 串行创建文件（主 agent 自己写导航枢纽文件）
- 文件数 ≤2（无导航枢纽概念）
- 文件名完全遵循"章节号-标题全拼.md"模式且无歧义
- 单文件任务

**与 [subagent-atomic-task-template](subagent-atomic-task-template.md) 要素4 的协同**：
- 分章文件（01-08）：使用要素4 的局部契约（前后章文件名）
- 导航枢纽文件（00）：使用本模式的全局契约（全部章节文件名）
- 两者共同构成完整的 sub-agent 文件名契约体系
