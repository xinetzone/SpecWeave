# 📦 技术文档

本目录集中承载 **SpecWeave 本项目** 的技术相关文档。全部项目技术资产（包含项目介绍、快速开始、核心功能、贡献指南与变更日志）均位于本目录下，与同级 [通用知识](../general/index.md)（方法论、哲学等）完全隔离。

```{toctree}
:maxdepth: 2
:caption: 技术文档

intro
quickstart
features
contributing
changelog
```

:::{note}
这是文档骨架的初始版本，各文档内容将逐步完善。
:::

## 目录清单

| 路径 | 说明 |
|---|---|
| `intro.md` | 项目介绍与定位 |
| `quickstart.md` | 环境初始化与首次接入 |
| `features.md` | 核心功能与 `.agents/` 详解 |
| `contributing.md` | PR 流程、代码审查与规范遵循 |
| `changelog.md` | 项目级变更日志 |

## 边界

不放置：通用知识、设计哲学、深度研究等与本项目源码/工程化无直接关系的内容，请见同级目录 [`../general/`](../general/index.md) 和 [`../topics/`](../topics/index.md)。

## 接入约定

> 新增技术文档时：
>
> 1. 将文件放入本目录；
> 2. 在本 `index.md` 的 `toctree` 中追加对应文档名（无需 `tech/` 前缀）；
> 3. 如需反向链接到 `../general/` 或 `../topics/` 中的文档，使用相对路径。
