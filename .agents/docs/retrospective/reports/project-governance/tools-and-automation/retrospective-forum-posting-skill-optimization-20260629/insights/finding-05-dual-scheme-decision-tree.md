---
id: "finding-dual-scheme-decision-tree"
title: "发现5：双方案共存需要\"决策树\"而非\"并列罗列\""
source: "../insight-extraction.md#发现5双方案共存需要决策树而非并列罗列"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/finding-05-dual-scheme-decision-tree.toml"
---
# 发现5：双方案共存需要"决策树"而非"并列罗列"

→ 整合进：[skill-five-elements-model.md](../../../../../patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md) 要素2（Decision Tree）

## 事件发现

初版只列了MCP方案（单方案无选择困难），但加入forum-bot.py后面临"什么时候用哪个"的问题。最初想做个表格对比两个方案，但最终决定提供**决策树**而非并列对比，显著降低了Agent方案选择错误。

## 设计决策

不是简单列个表格对比两个方案，而是提供明确的决策逻辑：
```
首次使用未登录？→ 先执行login
需要独立运行/CI/dry-run/幂等检查？→ 用forum-bot.py脚本
在IDE内临时操作/即时预览？→ 用integrated_browser MCP
```

## 深层含义

当 Skill 提供多种执行方案时，Agent 需要明确的**选择逻辑**而非仅仅是**选项列表**：
- 并列罗列选项 → Agent随机选择或凭偏好选择，场景适配性差
- 决策树 → 按条件分支自动选择，降低决策负担，减少选择错误

## 决策维度

浏览器自动化双方案决策的典型维度：
1. 运行环境（IDE内/CI/命令行独立运行）
2. 是否需要可重复执行
3. 是否需要dry-run/预览/幂等检查
4. 登录状态管理需求
5. 操作复杂度（简单点击vs复杂表单填写+文件上传）

## 关联洞察

- [law-01-skill-five-elements-model.md](law-01-skill-five-elements-model.md) — Skill五要素模型
- [law-03-browser-automation-general-pattern.md](law-03-browser-automation-general-pattern.md) — 浏览器自动化五层模式

---
*来源：[forum-posting Skill优化复盘](../README.md)*
