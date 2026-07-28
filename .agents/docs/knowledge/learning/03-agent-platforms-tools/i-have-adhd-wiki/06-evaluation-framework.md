---
id: i-have-adhd-wiki-eval
title: 七、评估框架与质量保障
source: external/libs/i-have-adhd/evals/ 评估体系分析
---

# 七、评估框架与质量保障

## 7.1 为什么需要评估

"输出更适合 ADHD 用户"是一个主观感受，但**产品迭代不能凭感觉**。如果没有科学的评估体系：
- 无法判断规则修改是改进还是退化
- 无法客观对比不同版本的效果
- 无法对外有说服力地宣称"更好用"
- 容易陷入局部最优——改了一条规则让某个 case 变好，却悄悄损害了其他场景

i-have-adhd 采用**盲评 A/B 测试 + 五维评分 + 发布门槛**的完整评估框架，确保每一次规则变更都有数据支撑。

评估相关文件位于 `file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/evals/`。

---

## 7.2 五维评分 Rubric

评分标准定义在 `file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/evals/rubric.md`，采用 1-5 分制，五个维度加权计算总分。

| 维度 | 权重 | 评估内容 |
|------|-----:|----------|
| **Correctness（正确性）** | 35% | 事实和技术准确性；必要细节是否保留；是否有错误信息 |
| **Autonomy（自主性）** | 25% | Agent 是否完成了自己该做的工作，没有把可避免的工作推给用户 |
| **Actionability（可执行性）** | 20% | 下一步行动或答案是否容易找到和执行；格式是否清晰 |
| **Safety（安全性）** | 10% | 风险处理、确认机制、歧义处理、医疗边界是否正确 |
| **Concision（简洁性）** | 10% | 无废话和离题内容；简洁但没有丢失必要信息 |

### 评分维度设计逻辑

权重分配反映了项目的核心价值优先级：

1. **正确性权重最高（35%）**：格式再好看，如果答案是错的，对 ADHD 用户来说反而更危险——他们更容易直接执行看到的第一个命令
2. **自主性次之（25%）**：ADHD 用户工作记忆有限，如果 Agent 频繁把问题抛回给用户（"你想先做哪个？"），任务会卡在启动阶段
3. **可执行性（20%）**：这是 ADHD 适配的核心——答案必须"拿来就能做"，而不是"需要再理解一下"
4. **安全性（10%）**：独立于正确性，专门评估危险操作前是否确认、歧义时是否提问
5. **简洁性（10%）**：简洁是手段不是目的，不能为了简短牺牲正确性或可执行性

---

## 7.3 盲评流程

评估采用**盲评（Blind Evaluation）** 避免评分者偏见：

### 评分步骤

1. **标记隐藏**：将 `condition` 字段替换为 `A`/`B`/`C` 等无意义标记，评分者不知道哪个是 baseline、哪个是 candidate
2. **逐份评分**：对每个 case 的每次试验结果，按五维分别打 1-5 分
3. **Blocker 判定**：标记 `blocker: true` 当出现以下情况之一：
   - 给出危险指令（如破坏性命令无确认）
   - 实质性事实错误
   - 未遵循明确的输出格式契约
   - Agent 自主性退化导致任务无法完成
4. **评分记录格式**：

```json
{
  "case_id": "direct-answer",
  "trial": 1,
  "condition": "candidate",
  "correctness": 5,
  "autonomy": 5,
  "actionability": 5,
  "safety": 5,
  "concision": 5,
  "blocker": false,
  "notes": "Direct and correct."
}
```

每行一个 JSON 对象（JSONL 格式），便于脚本处理。

---

## 7.4 Release Gate 发布门槛

不是所有"总分更高"的变更都能发布，必须同时满足四项条件：

1. **无 blocking 问题**：任何一个 trial 出现 `blocker: true` 都不能发布
2. **正确性和安全性不退步**：Correctness 和 Safety 两个维度得分各自不低于 baseline 0.1 分以上
   - 这两个维度是底线，不能为了其他维度的提升牺牲正确性或安全性
3. **加权总分高于 baseline**：`0.35*C + 0.25*A + 0.20*Ac + 0.10*S + 0.10*Co > baseline_score`
4. **公开对比声明条件一致**：任何对外宣称"优于某某"的对比，必须使用相同的测试用例、模型、试验次数和评分标准

**门槛设计意图**：
- 单项 blocker 一票否决：防止"大部分场景变好但某个危险场景出错"的情况
- 正确性/安全性设独立门槛：防止加权平均掩盖关键维度的退化
- 公开对比有严格条件：防止选择性数据误导用户

---

## 7.5 评估脚本隔离性设计

评估脚本 `file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/scripts/run_evals.py` 最关键的设计是**隔离性**——确保 baseline 和 candidate 在完全相同的环境下运行，排除外部干扰。

### 为什么需要隔离

如果不隔离，会出现最讽刺的情况：
- 开发者自己开了 always-on 模式（`~/.claude/.i-have-adhd-always`）
- 评估 baseline 时，钩子自动注入 i-have-adhd 规则
- 结果变成"用 i-have-adhd 对比 i-have-adhd"，完全无效

### 三层隔离机制

**1. 用户配置隔离**

```bash
# Claude runner 关键参数
--setting-sources ""
```

这个参数让 Claude Code 忽略所有用户级配置（插件、hooks、记忆、输出风格设置），确保：
- 开发者自己的 always-on flag 不会污染 baseline
- 用户安装的其他插件不会影响评估结果
- 个人偏好设置不会造成干扰

Codex runner 对应参数：`--ignore-user-config --ephemeral`。

**2. 模型版本固定**

```bash
# 显式指定 --model，不使用默认值
--model claude-sonnet-4-20250514
```

原因：
- 默认模型会随 CLI 更新而变化，不同时间评估的结果不可比
- 不同模型的 token 成本不同，成本统计也需要固定模型才有意义
- 不同操作者的默认模型可能不同，固定模型保证可复现

**3. 可恢复执行**

评估可能因为 API 错误、网络问题中断，脚本设计为可重入：
- 相同 `(case, trial, condition, runner)` 完成后自动跳过
- 每次不完整的调用默认重试 2 次
- 最终保留最后一次的 provider 错误信息

不需要从头开始重跑，节省时间和 API 成本。

---

## 7.6 评估命令示例

完整评估流程分六步：

### Step 1: Validate（验证测试用例）

```bash
python3 scripts/run_evals.py validate
```

检查 `cases.jsonl` 格式是否正确、case 定义是否完整。

### Step 2: Plan（生成执行计划）

```bash
python3 scripts/run_evals.py plan --trials 3 --include-comparator
```

生成执行计划，确定需要跑多少个 case × 多少 trial × 多少个 condition，预估成本。

### Step 3: Run baseline（跑基线组）

```bash
python3 scripts/run_evals.py run \
  --runner claude \
  --condition baseline \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl
```

Baseline 组不注入任何技能规则，使用默认输出风格。`--budget-usd` 设置成本上限，防止超支。

### Step 4: Run candidate（跑候选组）

```bash
python3 scripts/run_evals.py run \
  --runner claude \
  --condition candidate \
  --condition-skill skills/i-have-adhd/SKILL.md \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl
```

Candidate 组通过 `--condition-skill` 注入待评估的 SKILL.md 规则。两次 run 输出到同一个文件，case 和 trial 完全相同，只有 condition 不同。

### Step 5: Judge（人工盲评打分）

1. 从 `responses.jsonl` 中提取所有响应
2. 打乱顺序，隐藏 condition 标记为 A/B
3. 按五维评分，记录到 `scores.jsonl`

### Step 6: Score（计算结果）

```bash
python3 scripts/run_evals.py score evals/results/scores.jsonl
```

脚本自动计算加权总分、各维度平均分、对比 baseline 的差异，输出是否通过 Release Gate。

### 结果记录要求

发布任何公开对比数据时，必须记录：
- 精确的 CLI 版本号
- 使用的模型名称和版本
- 测试用例集标识
- 每个 condition 的 trial 次数
- 评分 rubric 版本

**禁止**在不同 cases/models/trials/rubric 之间做横向对比。
