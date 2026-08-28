# Concepts

本目录包含 book-to-skill 知识 Wiki 的核心概念章节。

| 文件 | 类型 | 说明 |
|------|------|------|
| [01-core-architecture.md](/concepts/01-core-architecture.md) | Concept | 双层架构设计：Python 确定性提取器 + SKILL.md 规范驱动生成器 |
| [02-extractor-deep-dive.md](/concepts/02-extractor-deep-dive.md) | Concept | 格式支持矩阵、提取器优先级链、多语言章节检测、优雅降级 |
| [03-skill-md-spec.md](/concepts/03-skill-md-spec.md) | Reference | 四种操作模式、十步生成流程、Token 预算矩阵、章节模板 |
| [04-token-economics.md](/concepts/04-token-economics.md) | Concept | Discovery Loop Tax 原理、24×-51× 节省基准、大书访问策略 |
| [05-security-model.md](/concepts/05-security-model.md) | Concept | 文档→Agent 供应链攻击面、五层纵深防御体系 |
| [06-installation-usage.md](/concepts/06-installation-usage.md) | Tutorial | 两种安装方式、可选依赖、Skill 位置优先级、基本示例 |
| [07-extending-development.md](/concepts/07-extending-development.md) | Tutorial | 新增格式支持、修改生成行为、工具脚本详解 |
| [08-transferable-patterns.md](/concepts/08-transferable-patterns.md) | Pattern | 五个可迁移工程模式：编译时付费、规范驱动、分层防御等 |

```{toctree}
:maxdepth: 2

01-core-architecture
02-extractor-deep-dive
03-skill-md-spec
04-token-economics
05-security-model
06-installation-usage
07-extending-development
08-transferable-patterns
```