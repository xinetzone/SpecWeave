---
id: "law-browser-automation-general-pattern"
title: "规律3：浏览器自动化Skill的五层通用模式"
source: "../insight-extraction.md#规律3浏览器自动化-skill-的通用模式"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/law-03-browser-automation-general-pattern.toml"
---
# 规律3：浏览器自动化Skill的五层通用模式

→ 状态：⏸️ 待后续更多浏览器自动化Skill案例验证后正式入库

## 核心规律

从 forum-posting 的双方案设计中，可以提炼出浏览器自动化类 Skill 的通用五层设计模式：

| 层级 | 职责 | 关键实践 |
|-----|------|---------|
| **1. 检测层** | 状态检测 | 多信号组合检测（登录/页面就绪/元素存在），不依赖单一选择器；增加多信号冗余防止选择器失效 |
| **2. 操作层** | 原子操作 | 封装原子操作函数（设置内容、点击按钮、等待导航），内联错误处理；在browser_evaluate中封装可复用JS工具函数 |
| **3. 安全层** | 防误操作 | dry-run预览 + diff确认 + 幂等检查，多层防护防止误操作；写操作必须有dry-run机制 |
| **4. 验证层** | 结果确认 | 操作后刷新/snapshot验证结果，不假设操作一定成功；验证失败要有明确的错误码和恢复指引 |
| **5. 清理层** | 副作用处理 | 自动清理副作用（如Discourse自动草稿）；操作失败时回滚或清理中间状态 |

## 决策树设计原则

浏览器自动化常存在多种方案（MCP/脚本/API），需要提供决策树而非并列罗列，决策维度包括：
- 运行环境（IDE内/CI/命令行独立运行）
- 是否需要可重复执行
- 是否需要dry-run/预览
- 登录状态管理需求
- 操作复杂度（简单点击vs复杂表单填写+文件上传）

## 关联洞察

- [finding-05-dual-scheme-decision-tree.md](finding-05-dual-scheme-decision-tree.md) — 双方案决策树设计
- [law-01-skill-five-elements-model.md](law-01-skill-five-elements-model.md) — 五要素模型中的安全检查清单要素

---
*来源：[forum-posting Skill优化复盘](../README.md)*
