+++
id = "finding-ai-data-security-three-specifics"
date = "2026-06-29"
type = "insight"
scope = "ai-security,data-security,domain-specific,prompt-pii,conversation-history,model-output"
source = "../insight-extraction.md#洞察4ai场景数据安全的三个特殊性"
archived_to = "domain-specific finding, not a generic pattern"
+++

# 发现1：AI场景数据安全三个特殊性

## 事件事实

编写数据分类分级和脱敏规范时发现，AI智能体互联场景下的数据安全与传统Web/企业数据安全有三个本质区别。

## 三特殊性详细分析

### 1. Prompt中可能包含PII

用户发送给AI的prompt是自由文本，可能无意中包含身份证号、手机号、地址等个人信息。

- **传统数据安全**：先分级再处理，数据进入系统前已标注敏感级别
- **AI场景差异**：prompt是动态输入，无法预先分级标注
- **专门防护**：动态PII检测与脱敏（prompt发出前自动扫描）

### 2. Conversation history是新的数据类型

多轮对话历史是AI场景特有的数据形式，它可能累积大量上下文信息。

- **聚合风险**：单独看每条消息可能不敏感，但聚合后可能推断出敏感信息（如根据对话推断健康状况、财务状况）
- **专门防护**：对话历史分级管理（按轮次/时长/敏感度分级存储和清理）
- **关联规则文档**：conversation-history-management规则

### 3. 模型输出可能泄露训练数据

第三方模型（尤其是境外模型）的输出可能包含其训练数据中的记忆信息。

- **双重风险**：训练数据污染和知识产权风险；输出内容也可能被用于反向推断输入数据
- **专门防护**：输出内容过滤与审计（检测模型输出中的敏感信息泄露）
- **关联规则文档**：model-output-audit规则

## 洞察结论

AI场景数据安全不能简单套用传统数据安全框架，必须针对这三个特殊性设计专门的防护措施。这是domain-specific发现，不是通用规律——每个垂直领域（AI、IoT、区块链等）在套用通用治理框架时都需要识别其特殊性。

## 关联洞察

- [law-02-compliance-driven-rule-building.md](law-02-compliance-driven-rule-building.md) — 场景映射步骤需要识别领域特殊性
- [law-05-governance-building-five-steps.md](law-05-governance-building-five-steps.md) — 步骤①需求解构时识别特殊性

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
