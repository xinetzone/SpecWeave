---
source: "agent-skills-open-standard-wiki.md#八优化技能描述触发准确率"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/07-description-optimization.toml"
id: "agent-skills-wiki-description-optimization"
title: "此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用"
---
## 八、优化技能描述（触发准确率）

### 8.1 技能触发工作原理

智能体使用渐进式披露来管理上下文。在启动时，它们只加载每个可用技能的 `name` 和 `description`——刚好够决定何时可能相关。当用户的任务匹配描述时，智能体将完整的 `SKILL.md` 读入上下文并遵循其指令。

这意味着描述承担了触发的全部负担。如果描述没有传达技能何时有用，智能体就不会知道使用它。

**重要细微差别**：智能体通常仅针对需要超出其独自处理能力的知识或能力的任务咨询 Skills。像"读取这个 PDF"这样简单的单步请求可能不会触发 PDF 技能，即使描述完美匹配，因为智能体可以用基本工具处理它。涉及专业知识的任务——不熟悉的 API、领域特定工作流或不常见格式——是写得好的描述可以发挥作用的地方。

### 8.2 设计触发评估查询

要测试触发，你需要一组评估查询——标记为应该或不应该触发你的技能的真实用户提示。

`evals/trigger_queries.json`：
```json
[
  {
    "query": "I've got a spreadsheet in ~/data/q4_results.xlsx with revenue in col C and expenses in col D — can you add a profit margin column and highlight anything under 10%?",
    "should_trigger": true
  },
  {
    "query": "whats the quickest way to convert this json file to yaml",
    "should_trigger": false
  }
]
```

目标是约 20 个查询：8-10 个应该触发，8-10 个不应该触发。

#### Should-trigger 查询
这些测试描述是否捕获了技能的范围。沿几个轴变化它们：
- **措辞**：一些正式，一些随意，一些有拼写错误或缩写
- **明确性**：一些直接命名技能领域（"分析这个 CSV"），其他描述需求而不命名（"我老板想要这个数据文件的图表"）
- **细节**：将简短提示与上下文丰富的提示混合
- **复杂性**：变化步骤数和决策点数量

最有用的 should-trigger 查询是那些技能会有帮助但从查询本身看不明显的情况。

#### Should-not-trigger 查询
最有价值的否定测试用例是**近似失误**——与你的技能共享关键词或概念但实际需要不同东西的查询。这些测试描述是否精确，而不仅仅是宽泛。

**弱否定示例**（太容易）：
- `"Write a fibonacci function"` — 明显不相关
- `"What's the weather today?"` — 无关键词重叠

**强否定示例**（有价值）：
- `"I need to update the formulas in my Excel budget spreadsheet"` — 共享"电子表格"和"数据"概念，但需要 Excel 编辑，而非 CSV 分析
- `"can you write a python script that reads a csv and uploads each row to our postgres database"` — 涉及 CSV，但任务是数据库 ETL，而非分析

#### 真实感提示
真实用户提示包含通用测试查询缺乏的上下文。包括：
- 文件路径（`~/Downloads/report_final_v2.xlsx`）
- 个人上下文（`"my manager asked me to..."`）
- 特定细节（列名、公司名、数据值）
- 随意语言、缩写和偶尔的拼写错误

### 8.3 测试触发率

#### 多次运行
模型行为是非确定性的——相同的查询可能在一次运行中触发技能，但在另一次运行中不触发。每个查询运行多次（3次是合理的起点）并计算**触发率**：技能被调用的运行比例。

- should-trigger 查询通过率：触发率 > 0.5（默认阈值）
- should-not-trigger 查询通过率：触发率 < 0.5

#### 自动化测试脚本示例

```bash
#!/bin/bash
QUERIES_FILE="${1:?Usage: $0 <queries.json>}"
SKILL_NAME="my-skill"
RUNS=3

# 此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用
check_triggered() {
  local query="$1"
  claude -p "$query" --output-format json 2>/dev/null \
    | jq -e --arg skill "$SKILL_NAME" \
    'any(.messages[].content[]; .type == "tool_use" and .name == "Skill" and .input.skill == $skill)' \
    > /dev/null 2>&1
}

count=$(jq length "$QUERIES_FILE")
for i in $(seq 0 $((count - 1))); do
  query=$(jq -r ".[$i].query" "$QUERIES_FILE")
  should_trigger=$(jq -r ".[$i].should_trigger" "$QUERIES_FILE")
  triggers=0

  for run in $(seq 1 $RUNS); do
    check_triggered "$query" && triggers=$((triggers + 1))
  done

  jq -n \
    --arg query "$query" \
    --argjson should_trigger "$should_trigger" \
    --argjson triggers "$triggers" \
    --argjson runs "$RUNS" \
    '{query: $query, should_trigger: $should_trigger, triggers: $triggers, runs: $runs, trigger_rate: ($triggers / $runs)}'
done | jq -s '.'
```

20个查询 × 3次运行 = 60次调用。建议脚本化此过程。

### 8.4 训练/验证集拆分避免过拟合

如果你针对所有查询优化描述，你风险过拟合——为这些特定措辞精心设计的描述，但在新查询上失败。解决方案是拆分查询集：

- **训练集（~60%）**：用于识别失败和指导改进的查询
- **验证集（~40%）**：留出仅用于检查改进是否通用的查询

确保两个集合都包含 should-trigger 和 should-not-trigger 查询的比例混合。随机打乱并在迭代中保持拆分固定，以便进行同类比较。

### 8.5 优化循环

1. **在训练集和验证集上评估**当前描述。训练结果指导你的更改；验证结果告诉你这些更改是否通用。
2. **识别训练集中的失败**：哪些 should-trigger 查询没有触发？哪些 should-not-trigger 查询误触发了？
3. **修改描述**。专注于泛化：
   - 如果 should-trigger 查询失败，描述可能太窄。扩大范围或添加关于技能何时有用的上下文
   - 如果 should-not-trigger 查询误触发，描述可能太宽泛。添加关于技能*不*做什么的特异性，或澄清此技能与相邻能力之间的边界
   - 避免从失败查询中添加特定关键词——这是过拟合。相反，找到那些查询代表的一般类别或概念并解决它
   - 保持描述在 1024 字符限制以下——描述在优化过程中往往会增长
4. **重复**步骤 1-3，直到所有*训练集*查询通过或你不再看到有意义的改进。
5. **通过验证集通过率选择最佳迭代**——验证集中通过的查询比例。注意：最佳描述可能不是你生产的最后一个。

通常五次迭代就够了。

> **自动化工具**：[`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) Skill 端到端自动化此循环：拆分评估集、并行评估触发率、使用 Claude 提出描述改进，并生成实时 HTML 报告。

### 8.6 优化前后对比

```yaml
# 之前
description: Process CSV files.

# 之后
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

改进后的描述更具体地说明了技能做什么（汇总统计、派生列、图表、清理），并且更广泛地说明了何时适用（CSV、TSV、Excel；即使没有显式关键词）。
