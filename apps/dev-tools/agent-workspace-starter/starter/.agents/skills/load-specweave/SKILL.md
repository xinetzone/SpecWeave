---
id: "load-specweave"
name: "load-specweave"
title: "装载工作区（Skill 示例）"
description: "装载本工作区子体系并建立技能触发就绪状态。当用户说'请装载 SpecWeave'、'初始化工作区环境'或要求按 AGENTS.md 启动协议装载时调用。装载后可用触发词调用子体系技能（复盘/洞察/mermaid/导出报告等）。"
source: ".agents/skills/load-specweave/SKILL.md"
---

# 装载工作区（Skill 示例）

装载本工作区子体系，并建立技能触发就绪状态。之后可用触发词调用子体系内技能（复盘/洞察/mermaid/导出报告等）。

## 步骤1：装载子体系

1. 确认工作区根目录包含 `AGENTS.md`。
2. 按 [AGENTS.md](../../../AGENTS.md) 的 PRIORITY ZERO 启动协议执行：读取 AGENTS.md 全文 → 读取 [.agents/context-routing.md](../../context-routing.md) 确定本次任务所需规范文件并完成内容敏感度预检 → 按上下文路由表读取对应规范 → 自检（方法论资产预检、敏感度预检、入口读取、Skill 加载判断）→ 自检通过后方可加载 Skill 或生成产出物。

## 步骤2：技能触发就绪

装载完成后，报告可用角色与技能门面，并给出常用触发词清单（如："给我做个复盘"→retrospective-cmd、"分析这个问题原因"→insight-cmd、"画个架构图/流程图"→mermaid-cmd、"导出报告"→export-report-cmd、"帮我提交代码"→atomic-commit-cmd、"检查断链"→link-check-cmd 等）。

## 步骤3：就绪报告

以如下格式报告："✅ 工作区装载完成，已就绪。📂 位置：<工作区根目录>。🎭 可用角色：<列出角色名称>。⚡ 可用技能：<列出技能名称>。📖 下一步：直接告诉我您的任务。"