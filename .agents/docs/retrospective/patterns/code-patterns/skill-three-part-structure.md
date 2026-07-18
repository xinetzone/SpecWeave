---
id: "skill-three-part-structure"
source: "../../reports/competitive-analysis/retrospective-tuyaopen-dev-skills-learning-20260630/insight-extraction.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/skill-three-part-structure.toml"
---
# 技能三分结构：SKILL / references / scripts

## 模式概述

当目标是“让 AI 助手可靠执行工作流”而不是“回答问题”时，单一的长提示词文件容易同时触发两类失败：

- 上下文成本过高，默认加载后挤占关键推理空间
- 操作步骤不可复现（步骤漏掉、顺序漂移、参数不稳定）

技能三分结构将同一能力拆分为三个载体，以不同成本承载不同信息密度：

- `SKILL.md`：最小入口（触发词 + 关键命令 + 最小示例）
- `references/`：长文档参考（按需加载）
- `scripts/`：可执行脚本（把建议固化为动作）

## 触发条件

- 需要在多个项目/仓库复用同一套工作流
- 工作流包含多步命令、参数选择、错误处理
- 内容存在“短入口 + 长参考”两类信息密度
- 需要让智能体在低上下文预算下仍保持正确率

## 结构模板

推荐目录结构：

```text
<skill>/
├── SKILL.md
├── references/
│   └── <topic>.md
└── scripts/
    └── <tool>.py
```

## 规则与约束

### 规则 1：SKILL.md 必须可最小闭环

SKILL.md 至少包含：

- 触发条件与边界
- 最小可用命令集合（含参数示例）
- 关键路径上的失败处理提示（但不展开长解释）

### 规则 2：长文档只能进 references/

当内容满足任一条件，优先放到 references/：

- 超过 200 行仍不可删减
- 主要用于查询而非每次执行都需要
- 以表格、错误码、参数参考为主

### 规则 3：可重复执行的动作必须脚本化

当某个步骤满足任一条件，优先放到 scripts/：

- 需要上层编排（例如非阻塞监控、批量检查、生成清单）
- 需要稳定的机器可读输出（建议提供 `--json`）
- 对路径、权限、进程管理有安全风险，需要护栏

## 最小验收清单

- [ ] `SKILL.md` 能在不读 references 的情况下跑通关键路径
- [ ] `references/` 中的内容不会被默认加载仍能被准确引用
- [ ] `scripts/` 对外提供稳定接口（参数、输出字段、退出码）
- [ ] 具备最小回归测试点（至少覆盖路径/环境变量/会话状态等不确定因素）

