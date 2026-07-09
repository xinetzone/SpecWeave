+++
id = "spec-reference-validation"
domain = "methodology"
layer = "spec-workflow"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "full"
source = "retrospective-first-principles-command-creation-20260709"

[bindings]
scenarios = ["spec-creation", "document-creation"]
commands = ["retrospective", "insight"]
+++
# Spec 阶段引用验证模式（Spec Reference Validation Pattern）

## 模式类型
方法论模式（spec-workflow / 引用验证）

## 成熟度
L1 已验证（1次验证来源：第一性原理指令集创建任务，证明缺少该检查会导致 spec 中引用不存在的文件，应用该检查可避免）

## 适用场景

| 场景 | 适用度 | 说明 |
|------|--------|------|
| 创建指令集（引用 modules 文件） | ✅✅✅ 核心场景 | 指令集通常关联 modules 目录下的模块文件 |
| 创建文档（引用其他文档） | ✅✅✅ 核心场景 | 文档中引用其他文档作为参考 |
| 创建配置文件（引用资源文件） | ✅✅ 强烈推荐 | 配置文件引用其他配置或资源 |
| 创建 spec（引用现有文件） | ✅✅ 强烈推荐 | spec 阶段本身引用现有文件 |
| 纯新建文件（无引用） | ❌ 不适用 | 不涉及引用，无需验证 |

## 问题场景

### 核心问题
创建引用其他文件/模块的文档时，spec 中写下的引用路径未经存在性验证，可能在实施阶段才发现目标文件不存在，导致返工。

### 典型案例
- **场景**：创建指令集文件，需关联 modules 目录下的某个模块
- **问题**：spec 中引用了 `self-cognition.md`，但该文件不存在，实际存在的是 `self-insight.md`
- **后果**：验证阶段才发现并修正，虽然返工成本极低，但属于系统性流程缺失

### 问题根因
1. spec 创建时基于"假设引用的文件存在"，未经验证
2. spec 模板没有"引用验证"检查项
3. 缺少 modules 目录的文件清单供快速查询
4. 习惯性地假设引用的文件存在，引用验证意识不足

## 解决方案

### 核心思路
在 spec 阶段增加"引用验证"步骤，使用 Glob 工具验证所有引用路径的存在性，在 spec 创建时就发现并修正无效引用。

### 实施步骤

```
步骤1：列出所有引用
  - 在 spec 中明确记录所有引用的文件/模块路径
  - 包括：关联模块、参考文档、依赖文件等

步骤2：使用 Glob 验证存在性
  - 对每个引用路径执行 Glob 检查
  - 示例：Glob pattern=".agents/modules/self-*.md"

步骤3：修正无效引用
  - 对不存在的引用：
    a) 查找正确的替代文件（如 self-cognition.md → self-insight.md）
    b) 标记为"需创建"（如果确实需要新建该文件）
    c) 删除该引用（如果不需要关联）
  - 在 spec 中记录修正决策

步骤4：记录验证结果
  - 在 spec 的检查清单中记录引用验证结果
  - 标注所有引用的验证状态（✅存在 / ❌已修正）
```

### 验证标准

| 验证项 | 标准 | 检查方法 |
|--------|------|---------|
| 引用完整性 | spec 中所有引用的文件都已列出 | 人工核对 |
| 引用存在性 | 所有引用的文件路径都存在 | Glob 验证 |
| 引用正确性 | 引用的文件是预期目标文件 | 内容核对 |
| 修正记录 | 无效引用的修正决策已记录 | 检查 spec 记录 |

## 与现有模式的关系

### 互补模式

| 模式 | 关系 | 说明 |
|------|------|------|
| `pre-decision-three-checks`（决策前三查） | 互补 | 决策前三查适用于"决策"场景，引用验证适用于"创建引用"场景 |
| `spec-driven-subagent-execution`（Spec驱动Sub-Agent执行） | 支撑 | 引用验证作为 spec 创建的标准步骤，支撑 Sub-Agent 执行的可靠性 |
| `file-creation-precheck-pattern`（文件创建预检） | 相关 | 文件创建预检关注文件本身，引用验证关注文件间的引用关系 |

### 区别说明

- **决策前三查** vs **引用验证**：
  - 决策前三查：决策前查权威文档、查现有实例、查本质目标
  - 引用验证：创建引用后验证路径存在性、验证文件正确性
  - 两者侧重点不同，可组合使用

## 价值评估

| 维度 | 价值 | 说明 |
|------|------|------|
| 减少返工 | 高 | 在 spec 阶段发现问题，避免实施/验证阶段返工 |
| 提高可靠性 | 高 | spec 的引用经过验证，可信度更高 |
| 可复用性 | 高 | 适用于所有创建引用其他文件的文档场景 |
| 实施成本 | 低 | 仅需在 spec 创建流程中增加1个验证步骤 |

## 反例

### 反例：未执行引用验证

**场景**：创建第一性原理指令集，spec 中引用 `self-cognition.md` 作为关联模块
**未执行**：spec 阶段未验证该文件是否存在
**后果**：验证阶段才发现该文件不存在，需修正为 `self-insight.md`
**教训**：spec 阶段应验证所有引用的文件是否存在

## 成熟度演进计划

| 阶段 | 条件 | 目标成熟度 |
|------|------|-----------|
| 当前 | 1次验证（本次任务） | L1 |
| 短期 | 在2-3次 spec 创建中应用该模式 | L2 |
| 中期 | 在5+次场景中应用，无引用错误发生 | L3 |
| 长期 | 集成到自动化工具，自动验证引用 | L4 |

## 来源与溯源

- **来源复盘**：[retrospective-first-principles-command-creation-20260709](../../../reports/task-reports/retrospective-first-principles-command-creation-20260709/README.md)
- **洞察提取**：[insight-extraction.md §洞察01](../../../reports/task-reports/retrospective-first-principles-command-creation-20260709/insight-extraction.md)
- **根因分析**：[insight-deep-analysis.md §三、根因分析](../../../reports/task-reports/retrospective-first-principles-command-creation-20260709/insight-deep-analysis.md)
- **行动项**：[insight-action-backlog.md ACT-001](../../../reports/task-reports/retrospective-first-principles-command-creation-20260709/insight-action-backlog.md)
