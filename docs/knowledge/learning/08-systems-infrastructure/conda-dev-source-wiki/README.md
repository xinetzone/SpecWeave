---
type: Wiki Tutorial
title: "conda 源码与 conda-docs 文档 Wiki 教程"
---

# conda 源码与 conda-docs 文档 Wiki 教程

本教程系统性学习 conda 包管理器源码（`external/libs/conda-dev/conda`）与 conda 官方文档站点源码（`external/libs/conda-dev/conda-docs`），帮助读者从整体架构到模块细节循序渐进地理解 conda 的内部实现与文档构建方式。

## 📄 章节列表

1. [00-overview.md](00-overview.md) — 教程总览与导航索引：引言、分层定位图、章节导航、目标读者与阅读路径
2. [01-architecture.md](01-architecture.md) — conda/conda-docs 整体架构：源码目录树、分层依赖、conda-docs 构建架构与两套文档体系对比
3. [02-core-modules.md](02-core-modules.md) — 核心求解与安装模块（core/）
4. [03-base-common.md](03-base-common.md) — 基础常量与通用工具层（base/ + common/）
5. [04-models.md](04-models.md) — 数据模型层（models/）
6. [05-gateways.md](05-gateways.md) — 网关与 I/O 层（gateways/）
7. [06-cli.md](06-cli.md) — 命令行接口层（cli/）
8. [07-plugins.md](07-plugins.md) — 插件与扩展体系（plugins/）
9. [08-env-notices.md](08-env-notices.md) — 环境管理与通知（env/ + notices/）
10. [09-resources.md](09-resources.md) — 术语表与参考资料

> 章节 02–09 为规划章节，将逐步补全；当前可直接阅读 00、01 两章。

## 目标读者

适合对 conda 有基本使用经验（`conda install/create/activate`）并希望深入其实现的学习者——从初学者建立分层心智模型，到进阶读者理解模块协作，再到源码研究者沿目录精读，均可按需取用。

---

- [🏠 返回系统基础设施目录](../README.md)