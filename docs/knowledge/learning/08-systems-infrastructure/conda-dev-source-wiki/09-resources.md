---
id: conda-dev-source-wiki-09-resources
title: "术语表与参考资料"
source: "spec:create-conda-dev-source-wiki-tutorial"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/09-resources.toml"
category: "learning"
tags: ["conda", "glossary", "reference", "resources", "reading-list"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda 源码学习术语表、权威参考链接与按难度分级的扩展阅读路线"
---
# 术语表与参考资料

本章提供 conda 源码学习所需的术语表、权威链接与分级阅读建议，术语均与 `conda/base/constants.py`、`conda/core/`、`conda/plugins/` 源码对应。

## 1. 术语表

| 术语 | 说明 |
|---|---|
| **package** | conda 可分发的软件单元，归档格式为 `.conda`（V2）与 `.tar.bz2`（V1，见 `CONDA_PACKAGE_EXTENSION_V2/V1`）。 |
| **channel** | 存放包与 repodata 的目录/URL；默认通道源指向 `https://repo.anaconda.com/pkgs/*`（`DEFAULT_CHANNELS`）。 |
| **subdir** | 通道下的平台子目录，如 `linux-64`、`osx-arm64`、`win-64`、`noarch`；全集见 `KNOWN_SUBDIRS`。 |
| **repodata** | 通道的包索引文件，默认名 `repodata.json`（`REPODATA_FN`）；conda 靠它构建求解索引。 |
| **repodata_fns** | 抓取索引的文件名序列，默认先试精简的 `current_repodata.json` 再回退 `repodata.json`。 |
| **MatchSpec** | 包匹配规格串，如 `numpy>=1.21`、`conda-forge::foo`；求解器以它表达请求与依赖。 |
| **prefix** | conda 环境根目录；`prefix-data` 即该目录下的已装包元数据。 |
| **PrefixData** | `conda/core/prefix_data.py::PrefixData`，读取 prefix 内 `conda-meta/` 下记录的对象。 |
| **SubdirData** | `conda/core/subdir_data.py::SubdirData`，按 subdir 查询/缓存 repodata 的对象。 |
| **PrefixRecord** | 单个已装包的元数据记录，`PrefixData` 内部以 `name -> PrefixRecord` 维护。 |
| **solver** | 把请求规格转为"增删哪些包"的逻辑；默认 `libmamba`，经典实现为 `classic`，入口 `conda/core/solve.py::BaseSolver`。 |
| **channel_priority** | 通道优先级策略，取值 `strict` / `flexible`（默认）/ `disabled`。 |
| **virtual package** | 以 `__` 前缀（如 `__cuda`、`__glibc`、`__archspec`、`__linux`、`__osx`、`__win`）描述宿主系统能力的假包，供求解器约束判断。 |
| **pinned package** | 被钉住版本的包，来源为 `pinned_packages` 配置或 `conda-meta/pinned` 文件。 |
| **hookspec** | pluggy 的 hook 规范，集中定义于 `conda/plugins/hookspec.py::CondaSpecs`。 |
| **hookimpl** | 插件实现注册装饰器 `conda.plugins.hookimpl`（pluggy `HookimplMarker`）。 |
| **notice** | 通道公告，默认服务端文件 `notices.json`；缓存读状态存于 `notices.cache`。 |
| **condarc** | conda 配置文件（`.condarc`），提供 `channels`、`channel_priority`、`ssl_verify`、`proxy_servers` 等参数。 |
| **environment.yml** | 描述环境（名称、通道、依赖）的 YAML 文件，用于 `conda env create/update`。 |
| **UnlinkLinkTransaction** | `conda/core/link.py::UnlinkLinkTransaction`，一次环境变更的卸载+链接交易，含 `verify()` 与 `execute()`。 |
| **CondaError** | conda 全部异常的基类（`conda/exceptions.py`），下游应借此捕获。 |

## 2. 权威参考资料链接

- **conda 官方文档**（配置、概念、故障排查）：<https://docs.conda.io>（主页 <https://conda.io>）
- **conda 主仓库源码**：<https://github.com/conda/conda>
- **conda 文档源码仓库**：<https://github.com/conda/conda-docs>
- **CEP（Conda Enhancement Proposal）规范**：<https://github.com/conda/ceps>（插件体系见 CEP-2，环境规格插件见 CEP-24 相关模块）
- **condarc 配置参考**：<https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/use-condarc.html>
- **通道概念**：<https://docs.conda.io/projects/conda/en/stable/user-guide/concepts/channels.html>
- **故障排查页**：<https://docs.conda.io/projects/conda/en/stable/user-guide/troubleshooting.html>
- **管理环境任务**：<https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html>
- **贡献指引**：<https://github.com/conda/conda/blob/main/CONTRIBUTING.md>

## 3. 按难度的扩展阅读建议

### 入门（先建立心智模型）
1. conda 官方文档的「Concepts」与「Manage environments」，理解 channel/subdir/repodata/prefix 的关系。
2. 常读 `conda config --show-sources` 与 `conda info` 输出，把术语和运行态对上。
3. 通读官方 config 页与 troubleshooting 页，建立"配置项—异常—定位"链路。

### 进阶（读懂关键代码路径）
1. `conda/base/context.py`：把 condarc 关键参数（`channel_priority`、`ssl_verify`、`proxy_servers`、`solver`）的默认值与说明读一遍。
2. `conda/core/solve.py`：追踪 `BaseSolver` 三个公开方法到 `_prepare` / `_run_sat` 的求解流程。
3. `conda/exceptions.py`：按继承关系梳理 `CondaError` 子类及各自的 guidance/hints 机制。

### 源码研究（深入机制与扩展）
1. `conda/plugins/hookspec.py` + `conda/plugins/types.py`：掌握 hookspec / hookimpl 与各 `Conda*` 类型契约。
2. `conda/gateways/disk/lock.py` 与 `conda/core/link.py`：研究文件锁、`UnlinkLinkTransaction` 交易与校验。
3. `conda/core/subdir_data.py`：研究 repodata 抓取、缓存与 sharded repodata（`repodata_use_shards`）。
4. `conda/models/match_spec.py` 与 `conda/resolve.py`：深入 MatchSpec 解析与经典 SAT 求解的交互。

---

**上一章**：[08-best-practices.md](08-best-practices.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[README.md](README.md)