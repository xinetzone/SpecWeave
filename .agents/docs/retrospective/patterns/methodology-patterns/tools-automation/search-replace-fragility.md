---
id: "search-replace-fragility"
source: "../../../reports/competitive-analysis/retrospective-specweave-contest-advantage-analysis-20260624/retrospective-v11-iteration/insight-extraction.md#洞察-1"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/tools-automation/search-replace-fragility.toml"
---
# SearchReplace 并发脆弱性与大块替换策略

## 核心原则

当对同一文件执行多轮 SearchReplace 编辑时，工具的可靠性随轮次**指数级下降**——第一轮替换成功后文件内容已改变，后续 `old_str` 基于的是编辑前的文件状态，匹配必然失败。大块内容替换（>50 行）应优先使用**整体读写策略**（读取→截取头部→拼接新尾部→整体写入），而非多轮局部搜索替换。

## 成熟度评估

| 维度 | 评估 | 依据 |
|------|------|------|
| 实践验证 | 中 | 2 次独立触发（export-suggestions.md 断裂修复 + insight-extraction.md anchor text 过时） |
| 可复用性 | 高 | 适用于所有涉及同文件多处编辑的场景 |
| 通用性 | 高 | 不限于特定领域——任何使用 SearchReplace 类工具的编辑流程均可复用 |

## 问题刻画

```mermaid
flowchart LR
    A["第 1 轮 SearchReplace<br/>old_str=原始文件内容"] --> B["替换成功 ✓"]
    B --> C["文件内容已改变"]
    C --> D["第 2 轮 SearchReplace<br/>old_str=原始文件内容"]
    D --> E["匹配失败 ✗<br/>search content not found"]
    E --> F["文件处于混合状态：<br/>部分新内容 + 部分旧内容"]
```

### 触发信号

| 信号 | 说明 |
|------|------|
| 多轮编辑计划 | 规划中涉及同一文件 ≥ 2 处互不重叠的 SearchReplace |
| 替换量 > 50 行 | 单次替换涉及大块内容迁移或重写 |
| 前后依赖 | 后续替换的 `old_str` 包含前序替换的目标区域 |
| 已有失败先例 | 同一文件在本次会话中已发生过一次 SearchReplace 失败 |

## 替换策略决策矩阵

| 替换规模 | 编辑轮次 | 推荐策略 | 原因 |
|---------|---------|---------|------|
| < 20 行 | 任意 | SearchReplace（多轮可接受） | 小范围替换容易锚定上下文，失败后修复成本低 |
| 20-50 行 | 1 轮 | SearchReplace | 单轮无并发问题 |
| 20-50 行 | ≥ 2 轮 | **整体读写** | 多轮替换的 old_str 匹配可靠性已显著下降 |
| > 50 行 | 任意 | **整体读写** | 大块替换必须走整体读写，多轮 SearchReplace 禁止使用 |

## 整体读写策略

### 操作流程

```
① Read 读取源文件全文，确认编辑边界
② 截取保留头部的行数（如 head = lines[0:168]）
③ Write 新尾部内容（包含所有修改）
④ 拼接 head + tail 写入目标文件
⑤ 验证行数与内容完整性
```

### 适用场景

- 文件后半部分需要整体重写
- 同一文件需要插入多个独立章节
- 从文件中移除大段旧内容并替换为新内容

### 不适用场景

- 文件全篇散在分布的微小修改（用 Grep 定位 + SearchReplace 逐点修改）
- 仅追加内容（用 SearchReplace 在文件末尾追加即可）

## 防范措施

### 预防

1. **编辑前评估**：规划编辑时先判断替换量是否 > 50 行，若是则直接选择整体读写策略
2. **多轮校验**：必须使用多轮 SearchReplace 时，每轮完成后立即 Read 验证文件状态，再计算下一轮的 old_str
3. **回滚备份**：> 50 行替换前在 `.temp/` 保存原始文件副本（关联 `file-operations.md` 约束 12）

### 恢复

当文件已处于混合状态（断裂）：

```
① Read 全文确认断裂边界（新旧内容的分界行号）
② 截取已完成的新内容部分（断裂边界之前）
③ Write 剩余的新内容（断裂边界之后）
④ 拼接写入
⑤ 验证全文完整性
```

## 与其他方法论的关系

| 方法论 | 关系 |
|--------|------|
| `path-discipline.md` | 路径纪律模式中的"幂等性纪律"维度与本模式互补——本模式解决编辑策略选择，路径纪律解决操作环境安全 |
| `file-operations.md` 约束 10 | 本模式是约束 10 的理论基础与触发条件详解 |

> 来源：来自 SpecWeave v11 迭代中 export-suggestions.md 断裂修复和 insight-extraction.md anchor text 过时两次 SearchReplace 失败事件
> 关联模块：`path-discipline.md`、`.agents/tools/file-operations.md`
