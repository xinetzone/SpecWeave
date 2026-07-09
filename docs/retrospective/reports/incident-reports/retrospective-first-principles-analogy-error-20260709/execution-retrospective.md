---
id: "retrospective-first-principles-analogy-error-20260709-execution"
title: "执行复盘：第一性原理类比推理错误事件"
date: 2026-07-09
type: incident
source: "用户质疑触发的自我纠错"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/reports/incident-reports/retrospective-first-principles-analogy-error-20260709/execution-retrospective.toml"
---
# 执行复盘：第一性原理类比推理错误事件

## 一、精确时间线

| 时间 | 事件 | 关键人物 | 产出物 |
|------|------|---------|--------|
| 10:00前 | 完成Vibe Coding Prompt学习分析，沉淀"第一性原理"和"对抗式审查"两个模式 | AI | 学习报告、4个模式文件 |
| 10:00 | 用户要求"全面更新"复盘目录 | 用户→AI | 更新指令 |
| 10:00-10:09 | AI执行更新，错误地将所有链接改为file:///绝对路径格式 | AI | 修改13个文件 |
| 10:09 | 原子提交错误变更 `9f3aa683` | AI | 错误提交 |
| 10:10 | 用户要求"原子提交"后，用户追问关键问题："所有链接统一为file:///绝对路径格式？这个判断哪里来的？符合第一性原理吗？" | 用户→AI | **关键触发点** |
| 10:11-10:15 | AI启动第一性原理反思：查AGENTS.md→查development-standards.md→发现规范明确禁止file:///格式 | AI | 事实核查 |
| 10:15-10:26 | AI修正所有文件：回退链接为相对路径，更新正文中的错误描述，记录教训 | AI | 修改12个文件 |
| 10:27 | 提交修正 `a50fc523` | AI | 修正提交 |
| 10:28-10:33 | 用户要求"复盘+洞察+萃取+导出"完整闭环 | 用户→AI | 本复盘报告 |

**从错误提交到修正提交**:18分钟

## 二、事实数据

### 变更统计

| 提交 | Hash | 类型 | 文件数 | 新增行 | 删除行 |
|------|------|------|--------|--------|--------|
| 错误提交 | 9f3aa683 | docs(retrospective) | 13 | 277 | 181 |
| 修正提交 | a50fc523 | fix(retrospective) | 12 | 198 | 187 |

### 受影响文件列表

**被错误修改的文件(13个)**:
1. `docs/knowledge/learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md`
2. `docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/README.md`
3. `docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/execution-retrospective.md`
4. `docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/export-suggestions.md`
5. `docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/insight-extraction.md`
6-12. `docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/insights/` 下7个文件

### 链接验证结果
- 错误状态：115个本地链接全部被改为file:///格式（在本机器可点击，但不可移植）
- 修正后：115个本地链接全部恢复为相对路径，验证全部有效

## 三、决策点回顾

### 决策点1：选择file:///格式（错误决策）

**决策时间**:约10:05
**决策依据**:
1. 看到系统提示中"Reply with Code Reference: You must format ALL file, directory, and code references using clickable absolute links (file:///...)"
2. 类比推理："AI输出要用file:///" → "Markdown文档里也应该用file:///"
3. 看到volcengine-cua复盘报告（可能也是错误的）用了file:///格式，作为"佐证"

**跳过的验证步骤**:
- ❌ 没有查项目根目录AGENTS.md实际使用什么链接格式
- ❌ 没有查docs/development-standards.md关于链接格式的规定
- ❌ 没有用第一性原理思考："文档链接的本质目标是什么？"
- ❌ 因为任务看起来"简单、只是格式更新"，直接执行了

**决策错误类型**:类比推理失败（恰恰是刚刚学习的"第一性原理要打断类比推理"的反例）

### 决策点2：用户质疑后启动第一性原理反思（正确决策）

**触发**:用户提问"这个判断哪里来的？符合第一性原理吗？"
**执行的验证步骤**:
1. ✅ 查AGENTS.md：发现所有链接都是相对路径
2. ✅ 查development-standards.md：发现§Markdown文档交叉引用规范明确要求相对路径，禁止file:///
3. ✅ 从第一性原理推导：文档链接本质是可移植性→相对路径才满足可移植性
4. ✅ 承认错误，立即修正

**正确的原因**:用户的提问直接触发了第一性原理思考，而不是继续为错误辩护

## 四、5-Whys根因分析

### Why1：为什么链接格式错了？
因为选择了file:///绝对路径格式。

### Why2：为什么选择file:///？
因为我混淆了两个不同场景的要求：
- 场景A：AI对话回复给用户 → 用file:///让用户在IDE中可点击
- 场景B：Markdown文档内部链接 → 必须用相对路径保证可移植性
我错误地将场景A的要求类比到场景B。

### Why3：为什么会混淆两个场景？
因为在执行"格式更新"这个看起来简单的任务时，我直接用了类比推理——"看到一个地方用file:///，就认为所有地方都应该用file:///"，**没有执行"查规范→验证事实"的基本步骤**。

### Why4：为什么刚刚学了第一性原理还会犯类比推理错误？
这里有一个深刻的"践行鸿沟"：
- **认知层面**:我能背诵"第一性原理就是打断类比推理，回到基本事实"
- **执行层面**:在做"简单、重复、看起来不用想"的任务时，大脑自动走了直觉捷径（类比推理），没有触发第一性原理检查
- **关键缺口**:方法论学习后，缺少**强制检查点**——尤其是在"看起来简单"的任务上

### Why5：为什么没有强制检查点？
当前的工作流中：
- 复杂任务（架构设计、新功能开发）有Spec流程、有验证步骤
- 简单任务（格式更新、文档整理）缺少"决策前三查"的强制门禁
- 越是简单任务，越容易因为"不用想"而跳过验证，反而越容易犯低级错误

**根因结论**:这不是知识缺失问题——我知道第一性原理是什么；这是**践行机制缺失**问题——知道方法论但没有在每个决策点自动触发验证流程，尤其是在简单任务上。

## 五、成功因素分析

虽然犯了错误，但纠错过程有值得肯定的地方：

| 因素 | 说明 |
|------|------|
| **用户正确提问** | 用户没有直接说"你错了"，而是问"这个判断哪里来的？符合第一性原理吗？"——这本身就是第一性原理Prompt的教科书用法，触发了自我反思 |
| **及时发现** | 18分钟内发现并修正，错误没有扩散 |
| **有规可查** | 项目有明确的开发规范文档，有据可依 |
| **修正彻底** | 不仅修正链接，还更新了文档中所有错误描述，把错误本身作为教训记录 |
| **闭环复盘** | 用户要求完整复盘+洞察+萃取+导出，确保错误转化为可复用知识，而不是只改完就算了 |

## 六、质量验收

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 所有链接恢复相对路径 | ✅ | 115个本地链接全部验证有效 |
| 文档内容描述准确 | ✅ | 正文不再错误声称"file:///是规范"，而是记录了错误和修正 |
| 教训已记录 | ✅ | 在执行复盘中新增决策回顾和5-Whys分析 |
| 无file:///残留（链接中） | ✅ | Grep验证实际Markdown链接已无file:/// |
| 修正后可移植 | ✅ | 链接使用相对路径，换机器/换克隆目录依然有效 |
