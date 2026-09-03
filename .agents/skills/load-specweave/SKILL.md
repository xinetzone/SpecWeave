---
source: "镜像自 Trae IDE builtin（源镜像已清理，原路径 skills/load-specweave/SKILL.md）"
name: "load-specweave"
description: "装载 SpecWeave Agent Workspace Hub 子体系并建立技能触发就绪状态。当用户说'请装载 SpecWeave'、'初始化 SpecWeave 环境'或要求按 client/sdk/AI/AGENTS.md 启动协议装载时调用。装载后可用触发词调用子体系技能（复盘/洞察/mermaid/导出报告等）。"
---


# 装载 SpecWeave

装载 SpecWeave Agent Workspace Hub 子体系，并建立技能触发就绪状态。之后可用触发词调用子体系内技能（复盘/洞察/mermaid/导出报告等）。

请严格按以下步骤执行，每步完成后报告进度：

## 步骤1：装载子体系

1. 确认子体系项目根位于 `d:\spaces\SpecWeave` 目录。
2. 按 `d:\spaces\SpecWeave\AGENTS.md` 的 PRIORITY ZERO 启动协议执行：
   - 步骤1：读取 [d:\spaces\SpecWeave\AGENTS.md](d:\spaces\SpecWeave\AGENTS.md) 全文；
   - 步骤2：读取 [d:\spaces\SpecWeave\.agents\context-routing.md](d:\spaces\SpecWeave\.agents\context-routing.md) 确定本次任务所需规范文件，并完成内容敏感度预检；
   - 步骤3：按上下文路由表读取对应规范（角色/技能/命令门面等）；
   - 步骤3.5：自检（vendor 方法论资产预检、敏感度预检、入口读取、Skill 加载判断）；
   - 步骤4：自检通过后方可加载 Skill 或生成产出物。

## 步骤2：技能触发就绪

装载完成后，报告子体系可用角色与技能门面，并给出常用触发词清单（如："给我做个复盘"→retrospective-cmd、"分析这个问题原因"→insight-cmd、"画个架构图/流程图"→mermaid-cmd、"导出报告"→export-report-cmd、"帮我提交代码"→atomic-commit-cmd、"检查断链"→link-check-cmd 等）。

## 步骤3：就绪报告

以如下格式报告：

"✅ SpecWeave 装载完成，已就绪。
📂 位置：d:\spaces\SpecWeave\
🎭 可用角色：<列出角色名称>
⚡ 可用技能：<列出技能名称>
📖 下一步：直接告诉我您的任务，或使用上述触发词调用技能。"