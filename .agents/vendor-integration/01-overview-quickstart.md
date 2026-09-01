---
id: "vendor-overview-quickstart"
title: "01 概述与快速入门"
source: "VENDOR-INTEGRATION.md#overview-quickstart"
x-toml-ref: "../../.meta/toml/.agents/vendor-integration/01-overview-quickstart.toml"
---
# 01 概述与快速入门

## 第1章 概述

flexloop（对外品牌名 AgentForge）是一个 AI Agent 协作基础设施项目，提供角色体系、协作协议、自我演进模块、验证脚本等完整的智能体协作框架实现。

flexloop 是 SpecWeave 团队**自有协作子模块**，SpecWeave 团队对 flexloop 拥有完全修改权限，可在子模块内直接开发并向上游贡献。

采用 git submodule 方式引入的原因：
- **保持项目独立性**：flexloop 是一个完整的独立 Git 仓库，有自己的版本历史、issue 跟踪和发布节奏
- **支持双向开发迭代**：允许在子模块内开发，修改可直接 push 到 flexloop 远程仓库，实现双向协作
- **版本可追溯**：通过 gitlink 精确锁定到具体 commit，确保构建可重现
- **避免源码合并**：不将源码直接合入主仓库，保持主仓库整洁

两个项目的关系：
- SpecWeave 是元规范框架，定义角色、协议、工作流、验证体系等抽象规范
- flexloop/AgentForge 是 SpecWeave 规范体系的落地参考实现，同时也是超集扩展（包含更多工程化能力）
- 两者是"规范-实现"关系，SpecWeave 提供抽象定义，flexloop 提供可运行的工程化参考

依赖方向：严格单向 SpecWeave → flexloop。SpecWeave 可以引用、参考、萃取 flexloop 的内容，SpecWeave 团队对 flexloop 拥有完全修改权限，但 flexloop 对 SpecWeave 无任何依赖。

## 第2章 快速入门

克隆仓库后初始化子模块：

```bash
git submodule update --init vendor/flexloop
```

检查子模块当前状态：

```bash
git submodule status vendor/flexloop
```

基本目录结构：

```
SpecWeave/
├── vendor/
│   ├── README.md              # SpecWeave 维护的 vendor 元数据总览
│   ├── VERSION.md             # SpecWeave 维护的版本清单（含锁定 commit）
│   └── flexloop/              # git submodule（flexloop 主权区，自有协作，允许开发）
│       ├── .git/              # submodule 独立 Git 仓库
│       ├── AGENTS.md          # flexloop 自身的智能体入口
│       ├── apps/chaos/        # flexloop 主应用目录（含 uv 环境和测试）
│       └── ...
└── .agents/
    ├── VENDOR-INTEGRATION.md  # 本文档（协同规范）
    ├── cases/
    │   └── agentforge-adoption.md  # AgentForge 案例引用
    └── scripts/               # 从 flexloop 萃取的脚本（标注来源）
```
---

## 相关模式

- [双模式子模块治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md)
- [Vendor生命周期治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md)
- [子模块元数据外部化](../../docs/retrospective/patterns/architecture-patterns/submodule-metadata-externalization.md)
---

**[返回索引](../VENDOR-INTEGRATION.md)** | 下一章: [02 边界划分与协作原则](02-boundaries-principles.md) →
