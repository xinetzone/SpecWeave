---
id: "vendor-integration"
title: "flexloop (AgentForge) 子模块协同规范"
source: ".agents/VENDOR-INTEGRATION.md"
x-toml-ref: "../.meta/toml/.agents/VENDOR-INTEGRATION.toml"
---
# flexloop (AgentForge) 子模块协同规范


# flexloop (AgentForge) 子模块协同规范

本文档是跨项目子模块协同规范的权威版本，定义SpecWeave与vendor子模块的边界划分、交互接口、版本管理。

本文档定义 SpecWeave 与通过 git submodule 引入的 flexloop (AgentForge) 项目之间的边界划分、交互接口、版本管理与操作规范。


## 文档导航

| 章节 | 说明 |
|------|------|
| [01 概述与快速入门](vendor-integration/01-overview-quickstart.md) | 概述与快速入门（子模块概念、依赖方向、初始化命令、目录结构） |
| [02 边界划分与协作原则](vendor-integration/02-boundaries-principles.md) | 边界划分与协作四原则（三区划分、可编辑/条件引/跟分支/沙箱护） |
| [03 交互接口规范](vendor-integration/03-interfaces.md) | 交互接口规范（文档引用、脚本萃取、条件导入、沙箱运行、禁止行为） |
| [04 版本控制与子模块流程](vendor-integration/04-versioning-workflows.md) | 版本控制与子模块流程（版本标识、更新4步法、贡献代码流程） |
| [05 测试隔离与模式萃取](vendor-integration/05-testing-extraction.md) | 测试隔离与模式萃取（环境隔离、贡献vs萃取决策树、6步萃取流程） |
| [06 常见问题与故障排查](vendor-integration/06-troubleshooting.md) | 常见问题与故障排查（modified content、空目录、冲突、脚本运行、CI配置） |
| [07 检查清单与体系定位](vendor-integration/07-checklist-architecture.md) | 检查清单与体系定位（9项快速检查清单、三层.agents架构、哲学层待观察） |

---

## 相关模式

- [双模式子模块治理](docs/retrospective/patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md)
- [Vendor生命周期治理](docs/retrospective/patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md)
- [子模块元数据外部化](docs/retrospective/patterns/architecture-patterns/submodule-metadata-externalization.md)
