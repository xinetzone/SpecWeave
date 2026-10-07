---
id: "agent-workspace-starter-guide-00-overview"
title: "00 概览（10 分钟）——什么是智能体工作区"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 00 概览（10 分钟）

**本段目标**：建立「智能体工作区 = 一份根契约 + 一个规范容器」的心智地图，并能说出 starter 里各规范类目的作用。

**前置**：无。这是路径起点，只需要你打开本套件目录。

## 1. 什么是「智能体工作区」

一个「智能体工作区」不是一堆提示词，而是**两层结构**：

- **根契约 `AGENTS.md`**：放在项目根目录，是智能体进入项目时读到的第一份文件。它声明「启动协议」——智能体收到任务后先做什么、按什么规则路由、在哪落盘。它让智能体对同一个项目的行为可预测。
- **规范容器 `.agents/`**：与 `AGENTS.md` 并列的目录，把规范拆成类目：角色、规则、协议、工作流、模板、指令、检查清单、技能。根契约负责「指路」，`.agents/` 负责「提供内容」。

```
你的项目/
├── AGENTS.md          ← 根契约：启动协议 + 路由（智能体第一入口）
└── .agents/           ← 规范容器：分门别类的规范资产
    ├── ONBOARDING.md  ← 入门指南
    ├── rules/         ← 规则
    ├── protocols/     ← 协议
    └── ...
```

这套结构的关键好处：**智能体不需要你每次重复交代偏好**，项目里已经写清「怎么开工、按什么标准、产出放哪」。你写的规范越清晰，智能体的行为越稳定。

## 2. starter 结构地图（类目导览）

把 `starter/` 拷进项目后，它长这样：

| 位置 | 类目 | 一句话作用 |
|---|---|---|
| [../starter/AGENTS.md](../starter/AGENTS.md) | 根契约 | 启动协议 + 单项目路由，智能体第一入口 |
| [../starter/.agents/ONBOARDING.md](../starter/.agents/ONBOARDING.md) | 入门 | 能力速查表：任务类型 → 该读哪份规范 |
| [../starter/.agents/context-routing.md](../starter/.agents/context-routing.md) | 路由 | 任务类型到必读规范的映射表 |
| [../starter/.agents/global-core-rules.md](../starter/.agents/global-core-rules.md) | 全局规则 | 启动协议、内容分流、按需读取 |
| [../starter/.agents/capability-registry.md](../starter/.agents/capability-registry.md) | 索引 | 全量资产的静态索引骨架 |
| [../starter/.agents/roles/](../starter/.agents/roles/) | 角色 | 开发者 / 审查者 / 测试者等角色定义 |
| [../starter/.agents/rules/](../starter/.agents/rules/) | 规则 | AI 编码准则、修复闭环、Spec 写作 |
| [../starter/.agents/protocols/](../starter/.agents/protocols/) | 协议 | 一句话装载、工作区发现 |
| [../starter/.agents/workflows/](../starter/.agents/workflows/) | 工作流 | 功能开发、代码审查流程 |
| [../starter/.agents/templates/](../starter/.agents/templates/) | 模板 | 任务模板、交接模板 |
| [../starter/.agents/commands/](../starter/.agents/commands/) | 指令 | 可复用的指令集（如 Mermaid 图表） |
| [../starter/.agents/checklists/](../starter/.agents/checklists/) | 检查清单 | 提交前核对项 |
| [../starter/.agents/skills/](../starter/.agents/skills/) | 技能 | Skill 门面示例（装载技能） |
| [../starter/.agents/modules/](../starter/.agents/modules/) 等 | 导览 | modules / teams / prompts / tools / worlds / capabilities / cases / systems |

> 更细的类目说明见 [../starter/.agents/README.md](../starter/.agents/README.md) 与 [../starter/.agents/ONBOARDING.md](../starter/.agents/ONBOARDING.md)。

## 3. 为什么 1 小时能上手

「1 小时」不是营销口号，而是有实测内容基线支撑的：

- **入口层天然轻量**：`.agents/` 根级的 9 份 Markdown 合计 503 行，最长一份 120 行；仓库根 `AGENTS.md` 121 行。你要先读的入口层总量只有数百行，完全够在 10~15 分钟内消化。
- **体量主体被挡在门外**：完整 `.agents/` 有 6850 文件 / 134.5 MB，其中技能与脚本两类按体积占约 97.6%（按文件数占约 93.3%）。它们是「执行体」而非入门物料。starter 采用「类目代表文件 + 一句话导览」，只取各类目的 README 与 1~2 份代表文件，把这个庞然大物挡在门外。
- **预算硬约束**：教程 ≤900 行、演练 ≤600 行、合计 ≤1500 行，正是「60 分钟可消化」的刻度。

换句话说：1 小时不是让你读完整个体系，而是让你读**入口层**、装好工作区、跑通**一个**小任务。

## 4. 本段动手（5 分钟）

1. 打开 [../starter/AGENTS.md](../starter/AGENTS.md)，找到「启动协议」这个标题块——它是整套结构的锚点。
2. 打开 [../starter/.agents/ONBOARDING.md](../starter/.agents/ONBOARDING.md)，浏览「能力速查表」，随便挑一行，看它把你指向哪个文件。
3. 回到上表，遮住「一句话作用」列，尝试自己说出 5 个类目的作用。

## 完成检查点

- [ ] 能用自己的话复述「根契约 + 规范容器」两层结构。
- [ ] 能在 `../starter/AGENTS.md` 中指出「启动协议」标题块的位置。
- [ ] 能说出 ≥5 个规范类目的作用。
- [ ] 理解「入口层轻量、执行体在门外」是 1 小时上手的前提。

---

下一段 → [01-bootstrap.md](01-bootstrap.md)（装载，15 分钟）