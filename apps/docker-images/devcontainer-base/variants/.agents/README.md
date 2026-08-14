---
id: "variants-agents-readme"
title: "镜像变体系列 AI资产容器"
source: "AGENTS.md"
---
# devcontainer-base/variants - .agents 目录

本目录是 devcontainer-base 镜像变体系列的 AI 协作者资产容器，存放变体管理子系统特有的规则和指南。

## 目录结构

```
.agents/
├── README.md                    ← 本文件（目录索引）
└── rules/                       ← 变体管理子系统规则
    ├── build-orchestration.md   ← 构建编排规范（build.sh、VARIANTS格式、拓扑排序、日志计时）
    ├── variant-conventions.md   ← 变体共享约定（FROM模式、PATH优先级、禁止覆盖项、[TIMER]）
    ├── testing.md               ← 测试规范（6层测试策略、脚本模板、验证命令vs完整测试）
    └── new-variant-guide.md     ← 新增变体操南（7步流程、模板替换、注册清单）
```

## 五层路由加载顺序

```
第1层（根级）：SpecWeave 全局规范 → ../../../../.agents/global-core-rules.md
第2层（应用级）：apps/ 区域路由 → ../../../AGENTS.md
第3层（项目级）：devcontainer-base 项目规范 → ../../.agents/rules/
第4层（子系统级）：变体管理规范 → 本目录 rules/
第5层（变体级）：单个变体特有规则 → ../<variant>/.agents/rules/dockerfile.md
```

## 必读规则文件（按任务类型路由）

| 任务场景 | 必读规则文件 | 核心关注点 |
|---------|-------------|-----------|
| 修改/理解 build.sh | [rules/build-orchestration.md](rules/build-orchestration.md) | VARIANTS数组格式、`|`分隔符、拓扑排序、构建参数、[TIMER]解析、逐条验证 |
| 编写/修改变体Dockerfile | [rules/variant-conventions.md](rules/variant-conventions.md) | FROM模式、SHELL重置、禁止覆盖项、PATH优先级、缓存挂载、[VALIDATION CHECKPOINT] |
| 编写/运行测试脚本 | [rules/testing.md](rules/testing.md) | L1-L6测试分层、脚本模板、pass/fail辅助函数、结果汇总 |
| 新增镜像变体 | [rules/new-variant-guide.md](rules/new-variant-guide.md) | _template/复制、7步流程、占位符替换、注册清单、验证检查 |
| 修改共享日志库 | [../../.agents/rules/dockerfile.md](../../.agents/rules/dockerfile.md) | 日志库在项目级共享，回退到父级规范 |
| 基础镜像Dockerfile规范 | [../../.agents/rules/dockerfile.md](../../.agents/rules/dockerfile.md) | 父级定义基础镜像构建规范 |
| 全局规则（提交/沟通） | [../../../../AGENTS.md](../../../../AGENTS.md) | 回退到 SpecWeave 根工作区 |

## 规则文件 frontmatter 规范

每个规则文件必须包含以下 frontmatter：
```yaml
---
id: "唯一标识符（kebab-case）"
title: "规则标题"
source: "内容来源（文件路径或AGENTS.md）"
---
```

## 父级继承

- 子系统路由：[../AGENTS.md](../AGENTS.md)（variants/ 入口）
- 项目级规则：[../../.agents/](../../.agents/)（devcontainer-base 项目规则）
- 应用级路由：[../../../AGENTS.md](../../../../AGENTS.md)（apps/ 区域路由）
- 全局规则：[../../../../.agents/global-core-rules.md](../../../../../.agents/global-core-rules.md)
- 全局 Skill：[../../../../.agents/skills/](../../../../../.agents/skills/)
- 七概念指令集：[../../../../.agents/commands/](../../../../../.agents/commands/)

## 变体级规则

每个变体可在自身 `.agents/rules/` 目录下定义特有规则：

| 变体 | 规则文件 |
|------|---------|
| conda | [../conda/.agents/rules/dockerfile.md](../conda/.agents/rules/dockerfile.md) |
| conda-llvm | [../conda-llvm/.agents/rules/dockerfile.md](../conda-llvm/.agents/rules/dockerfile.md) |
| _template | [../_template/.agents/rules/dockerfile.md](../_template/.agents/rules/dockerfile.md) |

## 变更日志

- 2026-08-07 | feat | 初始化 variants/.agents/ 目录，原子化4个规则文件
