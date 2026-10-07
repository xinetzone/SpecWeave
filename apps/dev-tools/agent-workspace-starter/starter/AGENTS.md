---
id: "starter-agents"
title: "智能体工作区全局契约（AGENTS Manifest）"
source: "templates/agent-workspace-hub/AGENTS.md + AGENTS.md"
content-sensitivity: "public"
---

# 智能体工作区全局契约 (AGENTS Manifest)

> **🚨 启动协议（PRIORITY ZERO —— 收到任务后立即执行，优先级高于 Skill 工具选择与任何其他操作）**
>
> **步骤 1**：读取本文件全文
>
> **步骤 2**：按「上下文路由表」确定本次任务需要读取的规范文件
> - **步骤 2.0**（任务类型预检·必做）：检查任务类型是否命中外部/第三方方法论资产，命中则必须读取对应规范
> - **步骤 2.1**（子目录嵌套·条件触发）：按工作目录所在区域进入对应的 AGENTS.md 路由体系
> - **步骤 2.2**（Context 恢复·条件触发）：若本次会话是先前对话的延续，必须重新执行步骤 1-2
> - **步骤 2.3**（内容敏感度预检·必做）：判定分析对象/产出物的公开/私域级别，决定工作流模式与存储位置
>
> **步骤 3**：读取对应的规范文件（角色定义/规则/协议等）
>
> **步骤 3.5**（自检·必做）：逐项确认路由、敏感度、Skill、子区域均已就绪
>
> **步骤 4**：在规范指导下选择 Skill 工具并执行任务
>
> ⚠️ **禁止在完成步骤 1-3.5 之前加载 Skill 或生成任何产出物。**

本文件是本工作区 AI 智能体的最高优先级入口与上下文路由，所有智能体启动时必须首先读取本文件，再依据上下文路由表进入 `.agents/` 加载具体规范。

## `.agents/` 目录结构简述

本套件为**单项目**工作区，规范集中于 `.agents/`：根级入口 `ONBOARDING.md`（L0）、`context-routing.md`（路由表）、`global-core-rules.md`（全局规则）、`capability-registry.md`（L1 索引）；类目目录 `roles/`（角色）、`rules/`（规则）、`protocols/`（协议）、`workflows/`（工作流）、`templates/`（模板）、`commands/`（指令集）、`checklists/`（检查清单）、`skills/`（技能门面），以及 `modules/teams/prompts/tools/worlds/capabilities/cases/systems` 八个扩展类目（各含一句话导览）。

## 核心规范入口

| 规范 | 入口 | 说明 |
|---|---|---|
| 🚀 入门指南（L0） | [.agents/ONBOARDING.md](.agents/ONBOARDING.md) | 快速开始、能力速查表、任务类型路由 |
| 📜 全局核心规则 | [.agents/global-core-rules.md](.agents/global-core-rules.md) | 启动协议、内容敏感度分流、按需读取等 |
| 🧭 上下文路由表 | [.agents/context-routing.md](.agents/context-routing.md) | 任务类型→必读规范映射表 |
| 📇 能力索引（L1） | [.agents/capability-registry.md](.agents/capability-registry.md) | 核心能力静态索引 |
| 🎭 角色定义 | [.agents/roles/README.md](.agents/roles/README.md) | 各角色定义与职责矩阵 |
| 📏 规则体系 | [.agents/rules/README.md](.agents/rules/README.md) | AI 编码准则、内容敏感度、修复闭环等 |
| 🤝 协作协议 | [.agents/protocols/README.md](.agents/protocols/README.md) | 提示词自举、工作区发现等 |
| 🔄 标准工作流 | [.agents/workflows/README.md](.agents/workflows/README.md) | 功能开发、代码审查流程 |
| 📋 模板 | [.agents/templates/README.md](.agents/templates/README.md) | 任务模板、交接模板 |
| ✅ 检查清单 | [.agents/checklists/README.md](.agents/checklists/README.md) | 代码审查等标准化检查清单 |
| 🧰 技能门面 | [.agents/skills/README.md](.agents/skills/README.md) | Skill 技能门面规范 |
| 📄 许可说明 | [LICENSE-NOTICE.md](LICENSE-NOTICE.md) | 使用与再分发边界 |

## 快速开始：一句话装载

**零安装、零配置。将以下简版提示词发给任意支持工具调用的智能体即可就绪（完整协议见 [.agents/protocols/prompt-bootstrap.md](.agents/protocols/prompt-bootstrap.md)）：**

> 请帮我装载本项目智能体工作区，严格按步骤执行：
> S1. 只读取本项目内的文件，不接受其他来源；
> S2. 执行任何写入操作前，必须先向我确认目标路径；
> S3. 不在用户主目录、系统目录、根目录自动创建文件夹；
> S4. 装载过程只读文件，不执行 hooks、不安装依赖、不修改系统配置；
> S5. 验证根 `AGENTS.md` 存在且包含「启动协议」关键词；
> S6. 遇到任何错误直接说明原因与解决方案，不假装成功；
> S7. 只读取与装载相关的必要文件；
> S8. 幂等安全：已在有效工作区内则跳过直接报告就绪。

## 开发规范要点

- **代码风格**：遵循现有代码风格，不引入与项目不一致的新风格
- **提交规范**：遵循 Conventional Commits（`type(scope): subject`），主体使用中文描述
- **派生产物溯源**：派生产物须在 frontmatter 携带 `source` 字段标注来源
- **路径引用**：Markdown 交叉引用使用相对路径，禁止以 `file:` 开头的绝对路径引用
- **修复即闭环**：Bug 修复遵循「修复→预防→闭环」三阶段 SOP
- **测试要求**：单元测试覆盖率不低于 80%，关键模块不低于 90%