+++
id = "markdown-as-interface"
domain = "methodology"
layer = "ai-collaboration"
maturity = "L3"
validation_count = 3
reuse_count = 2
documentation_level = "detailed"
source = "docs/retrospective/reports/insight-extraction/retrospective-architecture-priority-20260629/insights/insight-b-markdown-as-interface.md"

[bindings]
rules = []
references = []
skills = ["forum-posting", "link-check-cmd", "atomization-finalize-cmd", "docgen-cmd", "ci-check-cmd", "check-duplication-cmd"]
related_patterns = ["skill-five-elements-model", "progressive-context-disclosure", "skill-three-layer-value-model"]
+++

# Markdown即接口：用Markdown同时承载人类阅读与机器调用

## 模式概述

Markdown文档天然是叙事结构（章节→段落→解释），适合人类线性阅读，但Agent需要接口结构（触发词→输入→输出→错误处理→检查清单）。两者不是同一维度——把Markdown文档改得再好也无法自动变成可调用服务。Markdown即接口模式通过特定的结构化约定，让一个Markdown文件同时满足人类可读和机器可调用。

## 问题现象

指令集文档（如retrospective/insight/atomization）写得很好，但Agent只能"阅读理解后执行"，无法"直接调用"。具体表现为：
- Agent需要读取整个文档才能提取执行步骤
- 触发条件散落在正文中，难以精确匹配
- 安全检查点没有结构化标记，容易遗漏
- 多份文档之间没有统一的接口格式

## 解决方案：五要素模型

SKILL.md 作为Markdown即接口的标准载体，必须包含五要素：

| 要素 | 作用 | 机器可解析 |
|------|------|----------|
| **Trigger-Ready Description** | 触发词+使用场景，让Agent能精确匹配 | ✅ description字段+触发词列表 |
| **Decision Tree** | 明确的分支判断逻辑，选择正确的模式/参数 | ✅ 结构化Mermaid/编号列表 |
| **Progressive Disclosure** | L0速查→L1索引→L2深度文档三层架构 | ✅ 链接指向L2深度文档 |
| **Why-Explanation** | 设计决策的原因解释，帮助Agent理解约束 | ❌ 人类理解为主 |
| **Safety Checklist** | 执行前后的验证点，防止误操作 | ✅ checkbox清单 |

### 标准SKILL.md结构模板

```markdown
# <Skill名称>

**Description:** <触发词+一句话功能描述——这是Agent匹配的第一入口>

## 1. Skill ID
`<skill-id>`

## 2. 功能描述
<!-- 表格说明方案选择、优势对比 -->

## 3. 何时使用本技能
<!-- 触发词列表 -->

## 4. 方案选择决策树
<!-- Mermaid flowchart或结构化编号列表 -->

## 5. 快速开始
<!-- 编号步骤，每步对应可执行操作 -->

## 6. 安全检查清单
- [ ] 检查项1
- [ ] 检查项2

## 7. 执行日志（CMD-LOG）
<!-- 结构化日志规范 -->
```

### 三层渐进式披露架构

```
L0（<100行）：ONBOARDING.md 入口速查
  ↓ Agent匹配后加载
L1（<500行）：SKILL.md 核心决策+步骤+安全清单
  ↓ 需要深度参考时
L2（不限行数）：commands/*.md / rules/*.md 完整规范文档
```

## 适用场景

- **AI Skill开发**：为Agent设计可调用能力时必须使用
- **指令集封装**：将高频操作脚本封装为Agent可调用入口
- **工具门面化**：CLI工具需要AI友好接口时
- **跨Agent协作**：Agent之间传递任务时的标准化接口

## 实际案例

### 案例1：forum-posting Skill（首发验证）
forum-posting是第一个完整实现五要素模型的Skill：
- Description中明确列出触发词"发帖"、"编辑帖子"、"论坛内容"
- 决策树区分dry-run预览/正式发帖/更新帖子三种模式
- 安全清单包含幂等性检查、dry-run强制预览
- L1 SKILL.md <500行，L2包含Playwright脚本详情

### 案例2：5个命令集Skill门面化（第二批验证）
link-check-cmd、atomization-finalize-cmd、docgen-cmd、ci-check-cmd、check-duplication-cmd全部遵循此模式，均通过check-skill-quality.py验证。

## 反模式

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

## 与其他模式的关系

- **被skill-five-elements-model细化**：五要素模型是Markdown即接口的核心实现规范
- **与progressive-context-disclosure配合**：三层披露架构决定了L0/L1/L2如何分层
- **与skill-three-layer-value-model互补**：三层价值模型解释了为什么要分层
- **应用于task-type-precheck-bias-defense**：任务类型预检依赖SKILL.md的description字段精确触发

## 边界与选型

Markdown即接口适用于"半结构化"场景——需要人读也需要机读。如果是纯机器API（如REST API、MCP工具），应使用OpenAPI/JSON Schema等更严格的接口定义语言。如果是纯人读文档（如教程、博客），不需要加结构化约束。

判断信号：
- ✅ 文档需要被AI Agent"发现→决策→执行"
- ✅ 文档有明确的触发条件和执行步骤
- ✅ 文档需要安全检查和验证点
- ❌ 纯参考文档/API参考/教程类内容
