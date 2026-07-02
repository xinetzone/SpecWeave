---
source: "agent-skills-open-standard-wiki.md#九质量评估evals"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/agent-skills-wiki/08-evals.toml"
---
## 九、质量评估（Evals）

### 9.1 设计测试用例

一个测试用例有三部分：
- **Prompt**：真实用户消息——人们实际会输入的那种东西
- **预期输出**：成功是什么样子的人工可读描述
- **输入文件**（可选）：技能需要处理的文件

存储在 `evals/evals.json`：

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?",
      "expected_output": "A bar chart image showing the top 3 months by revenue, with labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"]
    }
  ]
}
```

**编写好的测试提示提示**：
- 从 2-3 个测试用例开始
- 变化提示：不同措辞、详细程度、正式程度
- 覆盖边界情况
- 使用真实上下文：文件路径、列名、个人上下文

### 9.2 运行评估

核心模式是每个测试用例运行两次：一次**使用技能**，一次**不使用它**（或与以前的版本对比）。这给你一个比较基线。

改进现有技能时，使用以前版本作为基线。编辑前快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），将基线运行指向快照，并保存到 `old_skill/outputs/` 而不是 `without_skill/`。

**工作区结构**：
```
csv-analyzer/
├── SKILL.md
└── evals/
    └── evals.json
csv-analyzer-workspace/
└── iteration-1/
    ├── eval-top-months-chart/
    │   ├── with_skill/
    │   │   ├── outputs/         # 运行产生的文件
    │   │   ├── timing.json      # Token和持续时间
    │   │   └── grading.json     # 断言结果
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    ├── eval-clean-missing-emails/
    │   ├── with_skill/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    └── benchmark.json           # 聚合统计
```

你手动编写的主要文件是 `evals/evals.json`。其他 JSON 文件（`grading.json`、`timing.json`、`benchmark.json`）在评估过程中产生。

#### 生成运行
每次评估运行应该从干净上下文开始——没有先前运行或技能开发过程的残留状态。在支持子智能体的环境中，这种隔离自然实现：每个子任务从头开始。

每次运行提供：
- 技能路径（或基线无技能）
- 测试提示
- 任何输入文件
- 输出目录

#### 捕获时间数据
时间数据让你比较技能相对于基线的时间和 token 成本——显著提高输出质量但使 token 使用量增加三倍的技能，与既更好又更便宜的技能是不同的权衡。每次运行完成时，记录 token 数和持续时间：

`timing.json`：
```json
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

### 9.3 编写断言

断言是关于输出应该包含或实现什么的可验证声明。在看到第一轮输出后添加它们。

**好的断言**：
- `"输出文件是有效的 JSON"` — 可编程验证
- `"条形图有标记的轴"` — 具体且可观察
- `"报告包含至少 3 条建议"` — 可计数

**弱断言**：
- `"输出很好"` — 太模糊无法评分
- `"输出使用完全短语 'Total Revenue: $X'"` — 太脆弱；不同措辞的正确输出会失败

### 9.4 评分输出

评分意味着根据实际输出评估每个断言并记录**PASS**或**FAIL**及具体证据。

`grading.json`：
```json
{
  "assertion_results": [
    {
      "text": "The output includes a bar chart image file",
      "passed": true,
      "evidence": "Found chart.png (45KB) in outputs directory"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  }
}
```

### 9.5 评分原则

- **PASS 需要具体证据**。不要给予怀疑的好处。
- **审查断言本身**，而不仅仅是结果。注意什么时候断言太容易、太难或无法验证。

对于比较两个技能版本，尝试**盲比较**：在不透露哪个来自哪个版本的情况下向 LLM 评判者呈现两个输出。评判者在自己的评分标准上对整体质量（组织、格式、可用性、完善度）打分，不受哪个版本"应该"更好的偏见影响。

### 9.6 聚合结果

迭代中的每个运行都评分后，计算每个配置的摘要统计并保存到评估目录旁的 `benchmark.json`：

`benchmark.json`：
```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.83, "stddev": 0.06 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0 },
      "tokens": { "mean": 3800, "stddev": 400 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.33, "stddev": 0.10 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0 },
      "tokens": { "mean": 2100, "stddev": 300 }
    },
    "delta": {
      "pass_rate": 0.50,
      "time_seconds": 13.0,
      "tokens": 1700
    }
  }
}
```

`delta` 告诉你技能的成本（更多时间、更多 token）和收益（更高通过率）。增加13秒但通过率提高50个百分点的技能可能值得。token 使用量翻倍但仅改进2个百分点的技能可能不值得。

### 9.7 分析模式

聚合统计可能隐藏重要模式。计算基准后：

- **移除或替换两种配置中总是通过的断言**。这些不告诉你任何有用信息——模型没有技能也能很好处理它们
- **调查两种配置中总是失败的断言**。要么断言有问题，要么测试用例太难，要么断言检查的是错误的东西
- **研究有技能通过但无技能失败的断言**。这是技能明确增值的地方。理解*为什么*——哪些指令或脚本起了作用？
- **当结果在运行间不一致时收紧指令**。如果相同评估有时通过有时失败（反映为高 `stddev`），评估可能不稳定，或技能指令可能有歧义
- **检查时间和 token 异常值**。如果一个评估花费其他3倍时间，阅读执行轨迹找到瓶颈

### 9.8 人工审查结果

断言评分和模式分析能捕获很多，但它们只检查你想到要写断言的内容。人工审查者带来新视角——捕获你没预料到的问题，注意输出技术上正确但没抓住要点，或发现难以表达为通过/失败检查的问题。

将具体反馈记录在工作区中（例如作为评估目录旁的 `feedback.json`）：

`feedback.json`：
```json
{
  "eval-top-months-chart": "图表缺少轴标签，月份按字母顺序而非时间顺序排列。",
  "eval-clean-missing-emails": ""
}
```

"图表缺少轴标签"是可操作的；"看起来不好"不是。空反馈意味着输出看起来没问题。

### 9.9 迭代循环

评分和审查后，你有三个信号来源：
- **失败的断言**指向具体差距
- **人工反馈**指向更广泛的质量问题
- **执行轨迹**揭示*为什么*出错

将这些信号转化为技能改进的最有效方法是将三者——连同当前 `SKILL.md`——提供给 LLM 并要求它提出更改。提示 LLM 时包括以下指南：
- **从反馈泛化**。技能将在许多不同提示中使用
- **保持技能精简**。更少、更好的指令往往优于详尽规则
- **解释原因**。基于推理的指令（"做 X 因为 Y 往往导致 Z"）比刚性指令效果更好
- **捆绑重复工作**。如果每次测试运行都独立编写类似的辅助脚本，这是将脚本捆绑到技能的 `scripts/` 目录的信号

**完整循环**：
1. 将评估信号和当前 `SKILL.md` 提供给 LLM 并要求提出改进建议
2. 审查并应用更改
3. 在新的 `iteration-<N+1>/` 目录中重新运行所有测试用例
4. 评分并聚合新结果
5. 人工审查。重复。

当你对结果满意、反馈始终为空，或者你不再看到迭代之间有意义的改进时停止。

> **自动化工具**：[`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) Skill 自动化此工作流的大部分——运行评估、评分、提出改进。
