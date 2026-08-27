---
id: "agents-readme-template"
title: ".agents 目录说明（模板）"
source: "extract-agent-workspace-template"
---

# .agents 目录说明

本目录是项目 AI 智能体规范的容器，存放角色定义、规则、协议、工作流、模板与自动化脚本。所有智能体在执行任务前，应先通过项目根目录的 `AGENTS.md` 进行上下文路由，再进入本目录加载对应规范。

## 目录结构

```
.agents/
├── ONBOARDING.md             # [Core] Agent Onboarding 入门指南（L0 入口）
├── capability-registry.md    # [Core] 能力注册中心（L1 静态索引）
├── global-core-rules.md      # [Core] 全局核心规则
├── context-routing.md        # [Core] 上下文路由表
├── roles/                    # [Core] 角色定义
├── rules/                    # [Core] 规则体系
├── tools/                    # [Core] 工具规范（规范层，非实现）
├── workflows/                # [Core] 标准工作流
├── protocols/                # [Core] 协作协议
├── templates/                # [Core] 模板资产
├── teams/                    # [Core] 团队管理
├── modules/                  # [Core] 自我演进模块
├── commands/                 # [Core] 标准化指令集
├── checklists/               # [Core] 标准化检查清单
├── docs/                     # [Core] 人类可读文档（knowledge/retrospective 等）
├── scripts/                  # [Tools] 验证与自动化脚本
├── skills/                   # [Tools] Skill 技能门面
└── config/                   # [Tools] 工具配置文件
```

> 标记说明：`[Core]` = 核心规范层（稳定规则/协议/定义），`[Tools]` = 执行工具层（脚本/实现/配置）。

## 各子目录职责说明

| 目录 | 分层 | 职责 |
|---|---|---|
| roles/ | Core | 智能体角色定义与协作场景 |
| rules/ | Core | 规则体系（阶段守卫/硬编码治理/数据安全/内容敏感度/AI编码准则等） |
| tools/ | Core | 工具规范（文件操作/代码执行/搜索/通信，规范层非实现） |
| workflows/ | Core | 标准工作流（功能开发/代码审查/测试流程） |
| protocols/ | Core | 协作协议（会话启动/任务交接/消息传递/冲突解决/前置阅读/路由等） |
| templates/ | Core | 模板资产（任务模板/交接模板等） |
| teams/ | Core | 团队管理（团队创建/权限分配/专项团队） |
| modules/ | Core | 自我演进模块定义 |
| commands/ | Core | 标准化指令集（复盘/洞察/萃取/原子提交/对抗审查等） |
| checklists/ | Core | 标准化检查清单 |
| docs/ | Core | 人类可读文档（技术知识库/复盘体系/可复用模式） |
| scripts/ | Tools | 自动化脚本（验证/生成/CI 工具，含 tests/ 与 shared lib/） |
| skills/ | Tools | Skill 技能门面（对 commands/ 的 Skill 封装） |
| config/ | Tools | 外部工具配置文件 |

## 规范分层治理（Core vs Tools）

`.agents/` 内采用 **Core（核心规范）/ Tools（执行工具）** 双层治理模型：

| 维度 | Core 层（规范核心） | Tools 层（执行工具） |
|------|---------------------|----------------------|
| 定位 | 定义"应该怎么做"的稳定规范 | 实现"具体怎么做"的可执行工具 |
| 依赖方向 | 不依赖 Tools 层 | 必须遵循 Core 层规范 |
| 面向对象 | Agent 认知层（决策依据） | Agent 执行层（操作实现） |

依赖方向单向（Tools → Core），避免循环依赖。

## 与 AGENTS.md 的关系

- `AGENTS.md` 是精简入口文件，定义启动协议与核心规范入口导航，是智能体启动时首先读取的最高优先级契约。
- `.agents/` 是详细规范容器，承载各角色、规则、协议、流程、模板与工具的具体内容。
- 两者关系为「入口 ↔ 容器」：`AGENTS.md` 负责路由与全局约束，`.agents/` 负责具体规范与可执行细节。
- 信息架构遵循 L0/L1/L2 渐进式披露：AGENTS.md + ONBOARDING.md(L0) → capability-registry.md + context-routing.md + skills/(L1) → 详细规范文档(L2)。