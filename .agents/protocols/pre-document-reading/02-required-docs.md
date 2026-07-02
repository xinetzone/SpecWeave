---
id: "pdr-02"
title: "02 前置文档清单"
source: "protocols/pre-document-reading.md#02"
x-toml-ref: "../../../.meta/toml/.agents/protocols/pre-document-reading/02-required-docs.toml"
---

# 02 前置文档清单


各角色在进入对应阶段前，必须读取以下文档：

### 按阶段×角色的必读文档矩阵

| 阶段 | 负责角色 | 必须读取的前置文档 |
|------|---------|-------------------|
| ①需求接收 | orchestrator | 1. 用户需求原始描述<br>2. 项目 [README.md](../../../README.md)<br>3. 相关历史 spec（`.trae/specs/` 下关联主题） |
| ②方案设计 | architect | 1. 任务分解清单（orchestrator输出）<br>2. 项目技术栈文档<br>3. 现有架构文档（`.agents/` 下的模块定义）<br>4. 开发规范（[docs/development-standards.md](../../../docs/development-standards.md)） |
| ③任务分配 | orchestrator | 1. 技术方案文档（architect输出）<br>2. 角色能力矩阵（[.agents/roles/README.md](../../roles/README.md)） |
| ④代码实现 | developer | 1. 技术方案文档（architect输出）<br>2. 任务分解清单（orchestrator输出）<br>3. 开发规范（[docs/development-standards.md](../../../docs/development-standards.md)）<br>4. 相关模块现有代码（必须实际读取文件内容） |
| ⑤测试编写 | tester | 1. 需求文档（原始需求+验收标准）<br>2. 技术方案文档（architect输出）<br>3. 代码实现（developer提交的PR）<br>4. 测试规范（[.agents/workflows/testing.md](../../workflows/testing.md)） |
| ⑥代码审查 | reviewer | 1. 需求文档（原始需求+验收标准）<br>2. 技术方案文档（architect输出）<br>3. 代码实现（developer提交的PR）<br>4. 测试报告（tester输出）<br>5. 审查checklist |
| ⑦合并代码 | orchestrator | 1. 审查通过报告（reviewer输出）<br>2. CI检查结果 |
| ⑧完成确认 | orchestrator | 1. 合并结果<br>2. 测试报告<br>3. 验收标准清单（需求阶段定义） |

### 功能演进场景的补充读取

| 变更类型 | 额外必读文档 |
|---------|------------|
| 功能扩展 | 1. 待扩展功能的原始需求文档<br>2. 待扩展功能的技术方案<br>3. 待扩展功能的现有代码实现 |
| 功能重构 | 1. 待重构功能的全部历史文档（需求+方案+测试）<br>2. 影响范围内所有模块的代码<br>3. 相关历史BUG修复记录 |

---

---

## 相关模式

- [渐进式上下文披露](../../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/progressive-context-disclosure.md)
- [上下文恢复协议](../../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/context-recovery-protocol.md)
---

← 上一章: [01 核心原则](01-principles.md) | **[返回索引](../pre-document-reading.md)** | 下一章: [03 读取确认与缺失处理](03-confirmation-missing.md) →
