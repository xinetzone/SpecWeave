---
id: "markdown-as-interface"
source: "../../../reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/insights/insight-b-markdown-as-interface.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/markdown-as-interface.toml"
---
# Markdown即接口：用Markdown同时承载人类阅读与机器调用

## 模式类型
方法论模式 / AI协作

## 成熟度
L4 已验证（14个SKILL验证，7次复用，已集成check-pattern-quality.py/check-skill-quality.py自动化验证）

## 适用场景

- **AI Skill开发**：为Agent设计可调用能力时必须使用
- **指令集封装**：将高频操作脚本封装为Agent可调用入口
- **工具门面化**：CLI工具需要AI友好接口时
- **跨Agent协作**：Agent之间传递任务时的标准化接口
- **可复用模式文档**：pattern文档本身也遵循L0/L1/L2三层架构
- **方法论模板沉淀**：如blockquote-rendering-fix等修复模板

## 问题背景

Markdown文档天然是叙事结构（章节→段落→解释），适合人类线性阅读，但Agent需要接口结构（触发词→输入→输出→错误处理→检查清单→执行日志）。两者不是同一维度——把Markdown文档改得再好也无法自动变成可调用服务。

具体痛点表现：
- Agent需要读取整个文档才能提取执行步骤
- 触发条件散落在正文中，难以精确匹配
- 安全检查点没有结构化标记，容易遗漏
- 多份文档之间没有统一的接口格式
- 执行过程没有可追溯日志，分支决策无法回溯
- L1文档复制L2详细内容，导致长度膨胀超过500行限制
- 所有触发词权重相同，无法区分信号强弱导致误加载

## 核心规则：六要素模型

SKILL.md 作为Markdown即接口的标准载体，必须包含六要素（v2.0演进）：

| 要素 | 作用 | 机器可解析 | 演进版本 |
|------|------|----------|---------|
| **Trigger-Ready Description** | 触发词+使用场景+强制措辞，让Agent能精确匹配 | ✅ description字段+触发词列表+分级信号 | v1.0 |
| **Decision Tree** | 明确的分支判断逻辑，选择正确的模式/参数 | ✅ 结构化Mermaid/编号列表 | v1.0 |
| **Progressive Disclosure** | L0速查→L1索引→L2深度文档三层架构 | ✅ 链接指向L2深度文档 | v1.0 |
| **Why-Explanation** | 设计决策的原因解释，帮助Agent理解约束 | ❌ 人类理解为主，但影响边界决策 | v1.0 |
| **Safety Checklist** | 执行前后的验证点，防止误操作 | ✅ checkbox清单 | v1.0 |
| **Execution Log (CMD-LOG)** | 结构化执行日志规范+决策前参数记录，支持可追溯性 | ✅ 统一键值对+JSON ctx格式 | v2.0新增 |

### 标准SKILL.md结构模板（v2.0）

```markdown
---
name: <skill-name>
version: <semver>
description: "当用户提到'<触发词1>'、'<触发词2>'时，必须使用此技能。<一句话功能描述+为什么用本Skill而非手动操作>。"
argument-hint: "<参数提示>"
user-invocable: <true|false>
paths:
  -   - "<相关文件路径列表>"
---

# <Skill名称>

> ⚠️ **本Skill是<类型>（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：<L2深度文档路径>（完整规范/事件表/知识库）

## 1. Skill ID
`<skill-id>`

## 2. 功能描述
<!-- 表格说明方案选择、优势对比、为什么用本Skill -->

## 3. 何时使用本技能
<!-- 触发词列表，推荐使用分级触发信号（T0弱/T1中/T2强） -->

## 4. 方案选择决策树
<!-- Mermaid flowchart或结构化编号列表 -->

### ⚠️ 强制：触发时必须记录输入参数日志
<!-- 决策树前输出CMD_START日志，记录7个ctx字段 -->

## 5. 核心步骤（快速开始）
<!-- 编号步骤，每步对应可执行操作，推荐□ checkbox格式 -->

## 6. 安全检查清单
- [ ] 检查项1
- [ ] 检查项2

## 7. 执行日志（CMD-LOG）
<!-- 引用L2规范，仅内联最常用的日志示例；命令集类Skill必须有此章节 -->
```

### 三层渐进式披露架构（L1门面模式）

```
L0（<100行）：ONBOARDING.md 入口速查
  ↓ Agent匹配后加载
L1（<500行，推荐<200行）：SKILL.md 核心决策+步骤+安全清单+CMD-LOG引用
  ↓ 需要深度参考时（按需加载）
L2（不限行数）：commands/*.md / rules/*.md / patterns/*.md 完整规范
```

> **为什么需要L1门面原则？** L1只放"决策需要的信息"，不放"参考需要的信息"。详细事件表、完整参数说明、边界case处理、FAQ等一律放L2，L1通过链接引用。v1.2.x系列6个命令集Skill实践证明：此模式可将SKILL.md从300+行压缩到120-170行，同时保持完整功能。

### 执行日志（CMD-LOG）规范

命令集类Skill（涉及状态变更/文件操作/决策分支）必须包含CMD-LOG章节，遵循[cmd-log-specification.md](../../../../../rules/cmd-log-specification.md)：

1. **决策前日志（S0强制）**：进入决策树前必须输出CMD_START，记录7个ctx字段（trigger_phrase/operation_type/source/pattern_name/user_explicit/dry_run/auto_classify）
2. **L1引用原则**：L1只放日志格式概要+关键日志示例+排查命令，完整事件表定义放L2
3. **特有事件定义**：每个Skill定义自己的特有事件，在L2文档中完整说明，L1引用

```
[CMD-LOG] | level=INFO | cmd=<cmd-name> | step=S0 | event=CMD_START | session=<prefix-YYYYMMDD-name> | msg=开始<操作>：<简述> | ctx={<完整JSON上下文>}
```

> **为什么决策前必须记录日志？** 涉及多层分类/分支决策的Skill，如果后续发现选错了分支，没有触发时的输入参数日志就无法回溯"当时为什么选了这个分支"。CMD_START在决策前输出，记录原始输入，是排查分支逻辑问题的关键证据。

### 分级触发信号（高级特性）

对于触发场景复杂的Skill，推荐使用三级触发信号替代扁平列表：

| 信号级别 | 触发条件 | 行为 |
|---------|---------|------|
| **T0（弱信号）** | 用户提到相关领域但未明确指令 | 建议性提示，不自动加载Skill |
| **T1（中信号）** | 用户明确提到触发词/操作 | 自动加载Skill，进入决策树 |
| **T2（强信号）** | 用户明确指定使用本Skill+参数 | 直接跳过决策树，执行指定操作 |

## 正例

### 案例1：forum-posting Skill（首发验证，v1.0五要素）
forum-posting是第一个完整实现五要素模型的Skill：
- Description中明确列出触发词"发帖"、"编辑帖子"、"论坛内容"
- 决策树区分dry-run预览/正式发帖/更新帖子三种模式
- 安全清单包含幂等性检查、dry-run强制预览
- L1 SKILL.md <500行，L2包含Playwright脚本详情
- **待升级**：缺失L0/L1/L2引用块，计划在v1.2.x重构时补齐

### 案例2：5个脚本门面Skill（第二批验证，v1.0）
link-check-cmd、atomization-finalize-cmd、docgen-cmd、ci-check-cmd、check-duplication-cmd全部遵循此模式，均通过check-skill-quality.py验证，作为现有Python脚本的门面化封装。

### 案例3：7大命令集Skill门面化（第三批验证，v2.0六要素+L1门面）
atomic-commit-cmd、atomization-cmd、export-report-cmd、insight-cmd、mermaid-cmd、retrospective-cmd、pattern-extraction-cmd是v2.0六要素+L1门面模式的完整实践：
- 全部包含六要素，平均长度125行（最短117行，最长175行）
- CMD-LOG章节全部采用L1引用模式（概要+L2链接），而非复制完整事件表
- 6个v1.2.x版本CMD-LOG章节精简为概要+L2规范引用，相比v1.1.x减少约50行
- pattern-extraction-cmd作为高决策复杂度Skill，采用"L1内联核心事件表+L2补充"的混合模式（317行，仍在<500限制内）
- 关键规则后均有 `> **为什么？**` 解释

### 案例4：pattern-extraction-cmd（v2.0完整参考实现）
六要素最完整的参考实现：
- 决策树前强制CMD_START日志（S0步骤），记录7个ctx字段
- CMD-LOG章节内联完整的9个特有事件定义+日志示例+排查命令
- 12项安全检查清单覆盖从三标准判断到成熟度统计的全流程
- 三阶段版本演进：v1.0.0（五要素基础）→ v1.1.0（+CMD-LOG决策前日志）→ v1.2.0（L1门面化）

### 案例5：mermaid-cmd（分级触发信号创新）
创新实践三级触发信号：
- T0弱信号：用户提到"画图"、"可视化"
- T1中信号：用户提到"mermaid"、"流程图"、"时序图"
- T2强信号：用户明确说"画一个mermaid流程图"
- 实现Keyless渐进式披露——无需明确关键词匹配，根据信号强度决定加载深度

### 案例6：blockquote-rendering-fix模式文档（L1+L2双层架构）
模式文档本身也遵循Markdown即接口原则：
- L1入口（blockquote-code-block-rendering-fix.md）：规则+模板+检查清单（145行）
- L2深度文档（blockquote-code-block-rendering-usage-guide.md）：5种变体+8组正反例+10条最佳实践
- L1开头显式标注L2链接，读者可按需加载深度内容

## 反例警示

### 反模式1：纯叙事文档
```markdown
# 链接检查工具
本工具用于检查Markdown文件中的链接有效性。
使用方法很简单，运行python check-links.py即可。
它支持多种模式...（长篇叙述，无结构化字段）
```
问题：Agent无法快速定位触发条件、参数选项、安全检查点。

### 反模式2：过度结构化到不可读
```markdown
---
apiVersion: skill/v1
kind: Skill
metadata:
  name: link-check
spec:
  triggers: ["链接检查", "check links"]
  ...（YAML配置长达200行）
---
```
问题：机器解析友好但人类几乎不读，失去Markdown的双重价值。

### 反模式3：缺少Why解释
只写"怎么做"不写"为什么"，导致Agent在边界场景下做出错误决策。例如不解释"为什么禁止git add ."，Agent可能在其他场景下认为可以git add .。

### 反模式4：L1复制L2内容
```markdown
## 执行日志（CMD-LOG）
<!-- 错误做法：在L1 SKILL.md中内联50+行完整事件表 -->
| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| ...（20行表格）|
```
问题：SKILL.md长度膨胀到300+行，核心决策信息被淹没，Agent加载L1时需要处理大量非决策必需信息。正确做法是放L2，L1只放概要+引用链接。

### 反模式5：缺少决策前日志
进入决策树后才记录日志，或者干脆不记录触发参数。
问题：当决策分支选错时，无法回溯"当时输入是什么、为什么选了这个分支"。S0 CMD_START必须在决策树判断**之前**输出。

### 反模式6：扁平触发词列表
```markdown
## 何时使用
- 画图
- 流程图
- 可视化
- mermaid
- 画个图
- 生成图表
...（20个扁平触发词）
```
问题：所有触发词权重相同，Agent无法区分"用户只是随便提到画图"和"用户明确要求画mermaid流程图"，导致误加载或漏加载。

## 实施检查清单

创建或更新SKILL.md时逐项验证：

- [ ] frontmatter包含name/version/description/argument-hint/user-invocable/paths字段
- [ ] description中包含明确触发词和"必须使用此技能"强制措辞
- [ ] 开头有L0/L1/L2三层架构引用块，明确标注本文件层级定位
- [ ] 决策树结构清晰（Mermaid或编号列表），覆盖主要分支
- [ ] 涉及分支决策的Skill，决策树前有CMD_START强制日志说明
- [ ] 核心步骤采用编号+□ checkbox格式，每步对应可执行操作
- [ ] 安全检查清单包含≥3项 `- [ ]` 格式的可执行检查项
- [ ] 关键规则后有 `> **为什么？**` 解释设计意图（≥3处）
- [ ] 命令集类Skill包含CMD-LOG章节（L1引用L2规范，不复制完整事件表）
- [ ] L1长度控制在<200行（脚本门面类<300行，高复杂度<500行）
- [ ] 触发场景复杂时使用分级触发信号（T0/T1/T2）替代扁平列表
- [ ] 无file:///绝对路径，所有内部链接使用相对路径

## 与现有模式的关系

- **被skill-five-elements-model细化**：五要素模型是Markdown即接口的v1.0核心实现规范，v2.0已升级为六要素
- **与progressive-context-disclosure配合**：三层披露架构决定了L0/L1/L2如何分层，L1门面模式是其最佳实践
- **与skill-three-layer-value-model互补**：三层价值模型解释了为什么要分层
- **应用于task-type-precheck-bias-defense**：任务类型预检依赖SKILL.md的description字段精确触发
- **与blockquote-rendering-fix配合**：SKILL.md中引用块内需要展示结构化步骤时，使用blockquote-rendering-fix避免代码块嵌套导致链接失效
- **cmd-log-specification提供支撑**：CMD-LOG要素的统一格式规范来源

## 演进历史

| 版本 | 时间 | 核心变化 | 验证Skill数 |
|------|------|---------|------------|
| v1.0 | 2026-06-29 | 初始五要素模型（Trigger/Decision Tree/Progressive Disclosure/Why/Safety） | 1（forum-posting首发） |
| v1.1 | 2026-06-29 | +CMD-LOG执行日志要素，7大命令集添加日志章节 | 8 |
| v2.0 | 2026-07-01 | 六要素正式确立+L1门面模式+决策前S0日志+分级触发信号 | 14 |

## 边界与选型

Markdown即接口适用于"半结构化"场景——需要人读也需要机读。如果是纯机器API（如REST API、MCP工具），应使用OpenAPI/JSON Schema等更严格的接口定义语言。如果是纯人读文档（如教程、博客），不需要加结构化约束。

判断信号：
- ✅ 文档需要被AI Agent"发现→决策→执行"
- ✅ 文档有明确的触发条件和执行步骤
- ✅ 文档需要安全检查和验证点
- ✅ 文档需要执行可追溯性（决策分支可回溯）
- ❌ 纯参考文档/API参考/教程类内容
- ❌ 纯机器消费的API定义（用OpenAPI/JSON Schema）
