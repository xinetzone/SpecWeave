---
id: "harness-engineering-wiki-05"
title: "行业标杆地图"
source: "https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/harness-engineering-wiki/05-industry-benchmarks.toml"
date: "2026-07-04"
category: "learning"
---

# 行业标杆地图

## 标杆对比总表

| 团队/产品 | 最有辨识度的Harness选择 | 启示 |
|-----------|------------------------|------|
| Anthropic / Claude Code | Initializer+Executor双阶段、Workspace持久层 | 规划与执行分离，用文件而非Context做状态传递 |
| LangChain / Deep Agents | 自我验证+追踪+工具签名优化，不换模型冲进Terminal Bench Top5 | Harness优化对效果的提升可能比换模型更大 |
| Mitchell Hashimoto / Ghostty | AGENTS.md作为宪法，每条规则对应真实失败，能机器化不留在自然语言 | 规则从失败中来，到Linter中去 |
| Cursor / Cline | 内置反馈回路（Linter/TypeCheck/Test）自动闭环，错误信息写给Agent看 | 反馈回路要自动化，错误信息本身是上下文工程 |
| 悟空AI招聘（本文案例） | 2 Agent + N Skill专才架构、三层硬护栏、RPA事务边界 | 生产级Agent必须有护栏、状态持久化、事务边界 |

---

## Anthropic / Claude Code

### 核心实践

1. **双阶段架构**：
   - Initializer理解用户需求，写出详细plan.md
   - Executor读取plan.md执行，不共享Init阶段的Context
   - 跨Context接力通过Workspace文件完成

2. **Workspace持久层**：
   - 所有状态写入文件系统
   - Context Window只是当前"工作台"
   - 支持断点续传、会话恢复

3. **启示**：
   - 不要让一个Agent既规划又执行，Context会膨胀
   - 文件是最可靠的状态传递机制
   - 规划即文档，plan.md本身就是可审计的决策记录

---

## LangChain / Deep Agents

### 核心实践

1. **不换模型冲Top5**：
   - Terminal Bench从第30名→第5名（52.8→66.5分）
   - 模型没换，只优化Harness
   - 证明了Harness Engineering的ROI可能高于模型升级

2. **优化点**：
   - **工具签名优化**：每个参数都有清晰的description，说明何时用/何时不用
   - **自我验证**：Agent执行完后自己检查结果
   - **追踪（Tracing）**：完整记录每次执行的链路，便于debug
   - **迭代式提示优化**：根据失败case持续调整系统提示

3. **启示**：
   - 不要一上来就怪模型不行，先检查你的Harness
   - 工具签名不是小事，它直接影响工具调用准确率
   - 可观测性（Tracing）是生产级Agent的必备能力

---

## Mitchell Hashimoto / Ghostty

### 核心实践

Mitchell Hashimoto（HashiCorp创始人，Vagrant、Terraform作者）在Ghostty项目中实践的Agent方法论：

1. **AGENTS.md作为宪法**：
   - 不是写给人看的，是写给Agent看的"项目基本法"
   - 每条规则背后都对应一个**真实发生过的失败案例**
   - 不是"应该怎么做"，而是"因为之前踩过X坑，所以必须这么做"

2. **能机器化的不留在自然语言**：
   - 每条规则先问：能不能写成Linter/CI检查？
   - 只有确实无法自动化的原则，才写进AGENTS.md
   - 自然语言是最后手段，不是第一选择

3. **启示**：
   - 规则不要凭空写，要从真实失败中总结
   - Linter/CI比文档可靠100倍
   - AGENTS.md要精，不要长——800行的AGENTS.md没人看（包括Agent）

---

## Cursor / Cline

### 核心实践

AI编程IDE的代表产品，它们的Harness设计值得学习：

1. **内置反馈回路自动闭环**：
   - Agent写完代码→自动运行Linter→有错误→自动回传给Agent修正→再Lint→直到通过
   - 不需要人介入，Agent自己闭环
   - TypeCheck、Test同理

2. **错误信息写给Agent看**：
   - 不是只给人看的报错
   - 错误信息包含：哪里错了、为什么错、建议怎么改
   - Linter输出本身是高质量的上下文

3. **启示**：
   - 反馈回路要自动化，不要让人当中间件
   - 错误信息也是Prompt工程的一部分
   - 快速失败、快速反馈、快速修正

---

## 作为自查镜子：你的团队最缺哪一格？

| 能力维度 | 检查问题 | 如果缺了会怎样 |
|---------|---------|---------------|
| 双阶段规划执行 | 你的Agent是先规划再执行，还是边想边做？ | 边想边做容易走偏、Context膨胀、死循环 |
| Workspace状态持久化 | 状态写文件还是塞Context？ | 塞Context会失忆、难断点续传、难debug |
| 专才Agent分工 | 是一个万能Agent还是多个专才Agent？ | 万能Agent工具选错率高、Context炸 |
| 工具签名质量 | 工具参数有清晰的"何时用/何时不用"说明吗？ | Agent经常选错参数、用错工具 |
| Linter/CI硬护栏 | 规则是写在文档里还是写成代码检查？ | 文档规则经常被违反、事故频发 |
| 自动反馈回路 | 错误能自动回传修正吗，还是要人肉看？ | 同样的错误反复犯、人成了中间件 |
| Agent Reviewer | 有第二个Agent审稿吗？ | 自我评估有偏见、低级错误发出去 |
| 熵管理/文档园丁 | 有定期清理机制吗？ | 文档过期、架构漂移、技术债越积越多 |
| Tracing可观测性 | 能回溯每次执行发生了什么吗？ | Bug难复现、问题难定位 |
