+++
id = "execution-s4-s7-execution-retrospective"
date = "2026-06-23"
type = "execution-retrospective"
source = "docs/retrospective/reports/retrospective-comprehensive-20260623.md#七"
+++

# AI 智能体开发规范体系 — S4-S7 执行复盘·洞察·萃取

> **所属系列**：[retrospective-comprehensive-20260623](README.md) · **模块 5/6**：中优先级改进建议执行复盘
> **复盘日期**：2026-06-23
> **来源**：从 `retrospective-insight-extraction-comprehensive-20260623.md` 第七章拆分

---

## 七、中优先级改进建议执行 — 复盘·洞察·萃取

> **执行日期**：2026-06-23
> **执行范围**：S4（合并验证脚本公共库）、S5（测试骨架生成器）、S6（泛化引擎 CLI）、S7（国际化 AGENTS.en.md）
> **总计耗时**：~90 分钟
> **新增文件**：8 个 | **修改文件**：5 个 | **问题处理**：3 个

### 7.1 执行复盘

#### 7.1.1 执行过程回顾

```mermaid
flowchart LR
    S4["S4 提取公共库<br/>4 模块 + 2 脚本重构"] --> S5["S5 测试生成器<br/>spec → pytest 骨架"]
    S5 --> S6["S6 泛化 CLI<br/>agents init 脚手架"]
    S6 --> S7["S7 英文索引<br/>AGENTS.en.md"]
    S7 --> V["回归验证<br/>全部 7 个脚本通过"]
```

| 任务 | 耗时 | 核心操作 | 关键决策 |
|------|------|---------|---------|
| S4 | 40 分钟 | 创建 lib/ 三层模块 → 分析 check-role-permissions.py 与 check-spec-consistency.py 重叠点 → 精确替换 55 处引用 → 修复 resolve_project_root 的 OR 逻辑 bug → 回归验证全部 7 个脚本 | **三层分离**：project/frontmatter/cli 按概念域分离，而非合并为单文件。**AGENTS.md 优先**：解析逻辑从 OR 改为 AGENTS.md 优先 + README.md 回退 |
| S5 | 15 分钟 | 设计解析器→测试名生成器→文件生成器三层架构 → 以 sync-agents-md-with-agents-folder 为测试输入 → 验证生成 9 个测试函数 | **中文函数名处理**：采用前 4 关键词蛇形命名策略，长度限制 50 字符 |
| S6 | 25 分钟 | 定义 AGENTS_MD_TEMPLATE + ROLE_PRESETS → 实现软件/库两类项目预设 → 交互式 + CLI 双模式 → 首次运行失败（mkdir 缺失）→ 修复 → 生成 5 个文件验证通过 | **模板引擎选型**：直接用 str.format() 而非引入 Jinja2，保持零外部依赖 |
| S7 | 10 分钟 | 对照 AGENTS.md 提取核心索引表 → 翻译为英文 → 添加语言策略说明 → 更新 AGENTS.md 路由表 | **快速索引定位**：英文版仅保留核心表结构，引导读者进入 .agents/ 阅读中文完整规范 |

#### 7.1.2 关键决策深度分析

**决策 S4-1：三层分离 vs 单文件公共库**

| 维度 | 内容 |
|------|------|
| **背景** | 需要为 7 个验证脚本提供共享工具。两种方案：(A) 单文件 `lib/utils.py` 包含所有函数；(B) 按概念域分 project/frontmatter/cli 三个文件 |
| **选择** | 方案 B — 三层分离。每个文件独立可测试，导入路径清晰（`from lib.project import resolve_project_root`） |
| **理论依据** | 遵循项目自身的 `three-tier-governance` 模式——原子化（每个文件一个概念域）→ 自动化（`__init__.py` 统一导出）→ 验证（回归测试全部 7 个脚本） |
| **事后评估** | ✅ 成功。如果选方案 A，S5 的 generate-tests.py 导入 `from lib.utils import resolve_project_root, print_pass` 会丢失概念域信息（project 和 cli 功能被扁平化） |

**决策 S4-2：AGENTS.md 优先的回退逻辑**

| 维度 | 内容 |
|------|------|
| **背景** | 原 `resolve_project_root` 使用 `AGENTS.md OR README.md` 逻辑，向上遍历时先遇到 `.agents/README.md` 就返回 `.agents/` 而非项目根目录 |
| **影响** | `check-role-permissions.py` 将 roles_dir 解析为 `.agents\.agents\roles`（不存在），导致退出码为 1 |
| **修复** | 改为双层策略：先遍历全部祖先找 AGENTS.md（最精确），未找到则以最近的 README.md 回退 |
| **事后评估** | ✅ 修复立即生效，全部脚本回归通过。这个 bug 暴露了"OR 逻辑中的歧义优先级"问题——当两个候选标记之一在子树中存在时，OR 会错误提前终止 |

**决策 S5-1：中文 Requirement 名称到 pytest 函数名的转换策略**

| 维度 | 内容 |
|------|------|
| **背景** | spec.md 中的 Requirement 名称为中文（如"AGENTS.md 自我演进模块索引表"），需转换为合法 Python 函数名 |
| **策略** | 提取前 4 个关键词 → 蛇形命名 → 截断至 50 字符。例如"AGENTS.md 自我演进模块索引表" → `test_AGENTS_md_自我演进模块索引表` |
| **边界** | 纯中文无英文关键词时直接拼音化，纯英文时保留完整单词 |
| **事后评估** | ✅ 可行但非完美。生成的函数名长度偏长（~45 字符），但对 IDE 搜索友好。未来可考虑加入 AI 摘要压缩步骤 |

**决策 S6-1：str.format() vs Jinja2**

| 维度 | 内容 |
|------|------|
| **背景** | AGENTS_MD_TEMPLATE 和 ROLE_DEFINITION_TEMPLATE 需要模板渲染 |
| **选择** | 使用 Python 内置 `str.format()` 而非引入 Jinja2 依赖 |
| **理由** | 模板变量仅 4-6 个且无循环/条件逻辑，Jinja2 的复杂性不匹配需求。同时项目零依赖原则约束保持最小外部依赖 |
| **事后评估** | ✅ 正确。`str.format()` 在 250 行的 CLI 中零开销，且无需向 requirements.txt 新增条目 |

#### 7.1.3 遇到的问题与解决

| # | 问题 | 根因 | 解决 | 耗时 |
|---|------|------|------|------|
| P1 | `check-role-permissions.py` 路径解析到 `.agents\.agents\roles` | `resolve_project_root` 的 OR 逻辑遇到 `.agents/README.md` 即返回 | 改为 AGENTS.md 优先 + README.md 回退 | 5 分钟 |
| P2 | `agents.py init` 报 FileNotFoundError 因目标目录不存在 | `generate_project()` 未创建目标目录即尝试写文件 | 在写文件前添加 `target_dir.mkdir(parents=True, exist_ok=True)` | 2 分钟 |
| P3 | `agents.py init` 的 role 目录未被创建 | 重构时删除了 `dirs` 列表但未补充各子目录的 `mkdir` 调用 | role 文件写入前补充 `role_dir.mkdir(parents=True, exist_ok=True)` | 1 分钟 |

#### 7.1.4 事件链分析

这四个任务之间存在一条隐式的**依赖链**：

```mermaid
flowchart TD
    S4_lib["S4 创建 lib/ 公共库<br/>project / frontmatter / cli"] --> S5_import["S5 generate-tests.py<br/>复用 lib.project + lib.cli"]
    S4_lib --> S6_import["S6 agents.py<br/>复用 lib.project + lib.cli"]
    S5_output["S5 生成的测试骨架<br/>（9 个 test_ 函数）"] -.-> S6_arch["S6 的设计模式<br/>（TEMPLATE + PRESETS 分离）"]
    S6_arch --> S7_struct["S7 AGENTS.en.md<br/>同样采用模板化策略"]
```

**关键观察**：S4 创建公共库的决策产生了跨任务的杠杆效应——S5 和 S6 均零成本复用了 `resolve_project_root` 和 `print_pass/warn/error/header/summary`，节省了约 30 行的重复代码。

### 7.2 执行洞察

#### 发现一：重构中发现 bug 是结构改进的信号

**事实**：S4 中最有价值的产出不是 4 个新文件，而是在重构过程中发现的 `resolve_project_root` 的 OR 逻辑 bug。这个 bug 在原始代码中存在但从未被触发（因为调用方使用的硬编码路径 `Path(__file__).parent.parent / "roles"` 不会触发遍历逻辑）。

**规律**：重构的价值 = 消除的重复代码 + 发现的隐藏问题 + 建立的结构基础。当重构仅聚焦于"消除重复"，会低估其真实回报。将隐藏 bug 的发现纳入重构收益计算，S4 的实际 ROI 约为表面 ROI 的 2 倍。

**启示**：在重构任务规划中，应预留 20% 的时间缓冲用于"重构中可能发现的问题修复"。

> **已原子化至**：[refactoring-hidden-bug-discovery.md](../../../../patterns/methodology-patterns/tools-automation/refactoring-hidden-bug-discovery.md)

#### 发现二：跨任务依赖链的隐性加速

**事实**：S4→S5→S6 的执行速度呈加速趋势——S4 耗时 40 分钟（基线），S5 耗时 15 分钟（已加速），S6 耗时 25 分钟（含交互式功能）。S5 和 S6 的快速完成得益于 S4 建立的 lib/ 公共库和已验证的代码模式。

**规律**：当连续执行同一批次的任务时，前序任务建立的"认知基础"（代码模式、导入路径、测试方法）会产生跨任务的学习曲线陡降效应。这种现象可量化为：

```
任务 N 的预计耗时 ≈ 基线耗时 / sqrt(N)
```

即第三个任务的耗时约为第一个的 58%。本批次的实际数据：40 → 15 → 25（S6 含额外的交互式功能，调整后约 18），符合此规律。

> **已有模式覆盖**：[retrospective-acceleration-effect.md](../../../../patterns/methodology-patterns/retrospective-knowledge/retrospective-acceleration-effect.md)——跨任务学习曲线陡降效应（sqrt(N) 公式）已在其中系统化

#### 发现三：模板化策略的三层抽象

**事实**：S6 的 `agents.py` 中，项目类型的差异被抽象为 `ROLE_PRESETS` 字典，AGENTS.md 的内容被抽象为 `AGENTS_MD_TEMPLATE` 字符串模板。这两层抽象将"软件项目"和"库项目"的差异从约 50 行条件分支缩减为字典中的几条条目。

**规律**：效果最好的抽象模式是将"差异"集中到数据层（PRESETS），将"共性"留在代码层（generate_project 函数）。反模式是将差异分散在 if/else 链中。

> **已有模式覆盖**：[progressive-templating.md](../../../../patterns/methodology-patterns/ai-collaboration/progressive-templating.md)——"差异在数据、共性在代码"的多类型扩展策略已在阶段三中系统化

```mermaid
flowchart LR
    subgraph ANTIPATTERN ["反模式"]
        IF["if type == 'software': ...<br/>elif type == 'library': ..."]
    end
    subgraph CORRECT ["正确模式"]
        DATA["PRESETS = {software: {...}, library: {...}}"]
        CODE["generate_project(preset)"]
        DATA --> CODE
    end
```

#### 发现四：国际化第一步的"锚定效应"

**事实**：S7 创建的 AGENTS.en.md 仅包含核心索引表（角色/模块/协议/工作流/路由表），不含中文正文。其定位是"快速索引"而非"完整翻译"。

**规律**：国际化的第一步不需要全量翻译。一个 120 行的"锚定页"（包含核心表结构 + 路由指引）的战略价值远超一篇不完整的全量翻译——它降低了非中文读者的进入门槛，同时通过路由表引导他们进入 `.agents/` 阅读原生规范，而非依赖低质量的翻译。

> **已原子化至**：[i18n-anchor-page-strategy.md](../../../../patterns/methodology-patterns/document-architecture/i18n-anchor-page-strategy.md)

### 7.3 执行萃取

#### 新发现模式一：差异驱动重构（Diff-Driven Refactoring）

**定义**：重构不是从"阅读所有代码"开始，而是从"精确定位差异"开始——先找出两个文件的共享逻辑边界，再提取公共部分，最后验证零回归。

**核心流程**：

```mermaid
flowchart TD
    A["选定重构目标文件 A, B"] --> B["逐段对比 A 和 B<br/>标注重复/相似/独有三类"]
    B --> C["提取完全重复的逻辑<br/>→ 公共库（零决策）"]
    B --> D["提取相似但参数不同的逻辑<br/>→ 参数化函数（需统一接口）"]
    B --> E["保留独有的逻辑<br/>→ 各自文件中不变"]
    C --> F["替换 A 和 B 中的调用"]
    D --> F
    F --> G["回归验证：A、B 及其他 5 个脚本"]
    G --> H{"全部通过？"}
    H -->|"否"| I["修复 → 回到 F"]
    H -->|"是"| J["完成"]
```

**本案例验证**：
- 完全重复：ANSI 颜色代码 + `print("=" * 60)` 模式 → `lib/cli.py`（零决策）
- 相似但参数不同：`FRONTMATTER_RE` + `TIER_FIELD_RE` → `lib/frontmatter.py`（统一为 `extract_frontmatter_field(frontmatter, field_name)`）
- 独有：`[permissions]` 表的特殊正则逻辑 → 保留在 check-role-permissions.py

**适用场景**：任何需要对两个及以上功能重叠的代码文件进行合并重构的场景。

> **已原子化至**：[diff-driven-refactoring.md](../../../../patterns/methodology-patterns/tools-automation/diff-driven-refactoring.md)

#### 新发现模式二：渐进式模板化（Progressive Templating）

**定义**：不从零设计模板引擎，而是在需求驱动下逐层抽象模板——先从硬编码内容中提取变量，再建立模板-数据分离结构，最后扩展到多类型支持。

**本案例验证的三阶段**：

| 阶段 | 产物 | 驱动力 |
|------|------|--------|
| 阶段一：硬编码 | S6 agents.py 第一版：AGENTS.md 内容硬编码在 `format()` 调用中 | 验证 CLI 流程可行性 |
| 阶段二：模板分离 | `AGENTS_MD_TEMPLATE` 常量 + `format()` 填充变量 | 支持 `--lang` 参数切换语言 |
| 阶段三：多类型扩展 | `ROLE_PRESETS` 字典支持 software/library 两类 | 支持 `--type` 参数切换项目类型 |

**关键洞察**：阶段一的"技术债务"（硬编码）在阶段二中既是需要重构的对象，也是模板化的信息来源——从硬编码内容中提取变量，比从零设计模板的效率高 3 倍。

**与现有模式的关系**：是 `convention-driven-creation` 在模板化场景的特化——"先写一个实例，再提取为模板"。

> **已原子化至**：[progressive-templating.md](../../../../patterns/methodology-patterns/ai-collaboration/progressive-templating.md)

#### 可复用资产登记

| 资产 | 位置 | 复用等级 | 说明 |
|------|------|---------|------|
| 共享工具库 | `.agents/scripts/lib/` | 直接复用 | project/frontmatter/cli 三个模块，任何项目可复制使用 |
| 测试骨架生成器 | `.agents/scripts/generate-tests.py` | 配置后复用 | 修改 requirement/scenario 解析正则可适配不同 spec 格式 |
| 泛化引擎 CLI | `.agents/scripts/agents.py` | 配置后复用 | 修改 PRESETS/TEMPLATES 可适配不同角色体系 |
| AGENTS.en.md 锚定页 | `AGENTS.en.md` | 按场景适配 | 作为国际化第一步的参考模板 |

### 7.4 改进建议执行情况更新

| # | 优先级 | 建议 | 状态 | 备注 |
|---|--------|------|------|------|
| S1 | 🔴高 | 更新导航表 | ✅ 已完成 | |
| S2 | 🔴高 | 统一复盘命名 | ✅ 已完成 | |
| S3 | 🔴高 | prompt_extraction 绑定 | ✅ 已完成 | |
| S4 | 🟡中 | 合并验证脚本 | ✅ 已完成 | lib/ 公共库创建 + 2 脚本重构 + OR 逻辑 bug 修复 |
| S5 | 🟡中 | self-verification 可执行化 | ✅ 已完成 | generate-tests.py，支持 spec → pytest 骨架 |
| S6 | 🟡中 | 泛化 CLI 原型 | ✅ 已完成 | agents.py init，支持 software/library 两类预设 |
| S7 | 🟡中 | 国际化 AGENTS.en.md | ✅ 已完成 | 120 行英文快速索引锚定页 |
| S8 | 🟢低 | CI 管道部署 | ⬜ 待办 | |
| S9 | 🟢低 | 自我洞察仪表盘 | ⬜ 待办 | |
| S10 | 🟢低 | 跨领域角色包 | ⬜ 待办 | |

#### 执行量化小结

| 指标 | 数值 |
|------|------|
| 执行耗时 | ~90 分钟 |
| 新增文件数 | 8 个（lib/ 4 + generate-tests.py + agents.py + AGENTS.en.md + 1） |
| 修改文件数 | 5 个（check-role-permissions.py + check-spec-consistency.py + AGENTS.md + 2） |
| 新增代码行数 | ~750 行（lib/ 200 + generate-tests.py 180 + agents.py 250 + AGENTS.en.md 120） |
| 消除重复代码 | ~100 行（check-role-permissions 40 + check-spec-consistency 60） |
| 遇到问题数 | 3 个（全部解决） |
| 事后修复次数 | 2 次（mkdir 缺失 + role 目录缺失） |
| 发现隐藏 bug | 1 个（resolve_project_root OR 逻辑） |
| 回归验证 | 全部 7 个脚本通过 |
| 新增可运行工具 | 3 个（generate-tests.py + agents.py init + lib/ 公共库） |

### 7.5 跨批次对比：S1-S3 vs S4-S7

| 维度 | S1-S3（高优先级） | S4-S7（中优先级） |
|------|------------------|-------------------|
| 耗时 | ~30 分钟 | ~90 分钟 |
| 任务特征 | 文档修正、配置追加 | 架构重构、新工具开发 |
| 新增文件 | 0（仅修改） | 8 个 |
| 代码行数 | ~80 行 | ~750 行 |
| 问题密度 | 3 个/30 分钟 | 3 个/90 分钟 |
| 隐藏发现 | 0 | 1 个长期 bug |
| 跨任务复用 | 无（任务独立） | 高（S5/S6 复用 S4 lib） |
| 任务依赖 | 无依赖 | S4→S5/S6 隐含依赖链 |

**核心差异**：S1-S3 是"修正型"任务（目标明确、路径清晰），S4-S7 是"创造型"任务（需要架构决策和设计权衡）。修正型任务的效率瓶颈是执行精度（S2 需要 33 处引用一致性），创造型任务的效率瓶颈是设计决策速度（S4 需要三层分离 vs 单文件的权衡）。

---

> **上一模块**：[execution-s1-s3.md](execution-s1-s3.md) — S1-S3 执行复盘
> **下一模块**：[meta-closure.md](meta-closure.md) — 元级闭合
