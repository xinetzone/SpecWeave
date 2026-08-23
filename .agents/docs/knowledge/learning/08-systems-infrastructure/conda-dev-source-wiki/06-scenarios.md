---
id: conda-dev-source-wiki-06-scenarios
title: "典型应用场景"
source: "spec:create-conda-dev-source-wiki-tutorial"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/06-scenarios.toml"
category: "learning"
tags: [conda, scenarios, api, matchspec, subdirdata, virtual-packages, plugins, docs]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "用 7 个真实场景串起 conda.api、MatchSpec、SubdirData、虚拟包、插件、文档构建与自定义下载的实践用法。"
---
# 典型应用场景

本章用 7 个场景把前两章的组件串起来。所有签名均基于真实源码，代码「示意」处已标注。

## 场景 1：程序化环境创建与包安装（conda.api）

**背景**：需要在脚本里创建环境并装包，而不是敲命令行。

**步骤**：
1. 用 `conda.api.Solver` 求解（内部走 `context.plugin_manager.get_cached_solver_backend()`）。
2. `solve_for_transaction()` 得到事务，`download_and_extract()` 再 `execute()`。

**示例（示意，真实签名）**：

```python
from conda.api import Solver
from conda.base.context import context

# 目标前缀可自定义
prefix = r"D:\envs\demo"   # Windows 示例；POSIX 用 /opt/envs/demo
solver = Solver(
    prefix,
    channels=(*[c for c in context.channels], "conda-forge"),
    subdirs=(context.subdir,),
    specs_to_add=("python=3.11", "numpy"),
)
txn = solver.solve_for_transaction()
txn.download_and_extract()
txn.execute()
print("done:", prefix)
```

**预期结果**：新前缀下出现 `conda-meta/`、`python`/`numpy` 及其依赖；`conda-meta/history` 记录本次操作。

> 注意：`solve_final_state`/`solve_for_diff` 只给「解」不落地；真正修改磁盘的是 `UnlinkLinkTransaction`。若需要完整的 create 语义（默认包、channel 优先级、history 写盘），应复用 `conda.cli.install.install(args, parser, command="create")`。

## 场景 2：MatchSpec 匹配与依赖解析

**背景**：批量判断一批包记录是否符合用户约束。

**步骤**：用 `MatchSpec.match(rec)`，`rec` 既可为 `PackageRecord` 也可为 dict。

**示例（可运行）**：

```python
from conda.models.match_spec import MatchSpec

records = [
    {"name": "python", "version": "3.12.1", "build": "h123_0", "channel": "conda-forge"},
    {"name": "numpy",  "version": "1.26.4", "build": "py312h456_0"},
]
spec = MatchSpec("conda-forge::python>=3.11,<3.13")
for r in records:
    print(r["name"], spec.match(r))
```

**预期结果**：`python True`、`numpy False`（numpy 未限定频道但 spec 要求 `conda-forge::`）。

## 场景 3：SubdirData 与 repodata 索引

**背景**：想在本地直接查询某个频道的可用包版本，而不走完整求解。

**步骤**：实例化 `conda.core.subdir_data.SubdirData`（或 `conda.api.SubdirData`）查询。

**示例（可运行）**：

```python
from conda.core.subdir_data import SubdirData
from conda.models.channel import Channel

sd = SubdirData(Channel("conda-forge/linux-64"))
lst = [r.version for r in sd.query("python") if r.version.startswith("3.11")]
print(lst[:5])
```

**预期结果**：输出 conda-forge 的 linux-64 下所有 `3.11.x` 的 python 版本列表。

> 说明：经典 conda 求解器索引的是 `repodata.json`（及 `current_repodata.json`、shards/zst 等变体），并不像 libmamba 求解器那样直接读写 `.solv` 文件——分片/压缩格式的切换在 `gateways/repodata` 中通过 `get_repo_interface()` 完成。

## 场景 4：虚拟包与 CUDA / archspec 检测

**背景**：conda 用「虚拟包」（`__cuda`、`__archspec`、`__unix` 等）表达系统能力，供求解器约束依赖。

**步骤**：直接调检测函数，或取聚合结果。

**示例（可运行）**：

```python
from conda.plugins.virtual_packages.cuda import cuda_version, cached_cuda_version
from conda.plugins.virtual_packages.archspec import archspec_build
from conda.base.context import context

print("cuda:", cuda_version())          # 首次会 spawn 子进程探测
print("cuda(cached):", cached_cuda_version())
print("archspec build:", archspec_build())
for vp in context.plugin_manager.get_virtual_package_records():
    print(vp.name, vp.version, vp.build)
```

**预期结果**：无 GPU 机器上 `cuda` 返回 `NULL`（内部哨兵，插件据此跳过该虚拟包）；`archspec` 返回如 `x86_64` / `skylake`；聚合列表列出 `__archspec`、`__unix`、`__cuda` 等。

## 场景 5：插件子命令开发（hookspec）

**背景**：给 conda 加一个 `conda hello` 子命令，用入口点（entry point）安装。

**步骤**：
1. 实现 `conda_subcommands()` hookimpl，产出 `CondaSubcommand`。
2. 通过 setuptools 入口点注册到 `conda` 组；conda 启动时 `load_entrypoints(APP_NAME)` 加载。

**示例（可运行，`hello_plugin/__init__.py`）**：

```python
from conda import plugins

def hello_command(args):
    print("Hello from a conda plugin!")

@plugins.hookimpl
def conda_subcommands():
    yield plugins.types.CondaSubcommand(
        name="hello",
        summary="A demo subcommand",
        action=hello_command,
    )
```

对应入口点配置：

```toml
[project.entry-points.conda]
hello = "hello_plugin"
```

**预期结果**：安装该包后运行 `conda hello` 输出 `Hello from a conda plugin!`；`conda plugins`（内置 `plugins` 子命令）能看到 `hello`。

## 场景 6：conda-docs 本地构建与文档贡献

**背景**：想在本地预览/修改 conda-docs 文档并提 PR。

**步骤**：
1. 安装依赖 `pip install -r requirements.txt`（`conda-sphinx-theme==0.4.0`、`sphinx-sitemap`、`sphinx-design`、`sphinx-reredirects`）。
2. 进入 `docs/` 执行构建 `make html`（`SPHINXBUILD = python3 -msphinx`，源目录 `source`，输出 `build/`）。
3. 新增/修改 `docs/source/*.rst`，确认 `conf.py` 的 `html_theme = "conda_sphinx_theme"` 与 8 个 `extensions` 已生效。

**示例（终端）**：

```powershell
cd d:\spaces\SpecWeave\external\libs\conda-dev\conda-docs\docs
python -m sphinx -M html source build
```

**预期结果**：`docs/build/html/index.html` 可本地打开；`make html` 收编在 `docs/Makefile` 的 catch-all 目标里。提交前用 `.readthedocs.yml`（ubuntu-24.04 / Python 3.14）口径自检没引入缺失导出。

## 场景 7：channel / adapter 自定义下载

**背景**：给 conda 增加对自定义协议（或指定频道的认证）下载支持。

**步骤 A（只用内置能力）**：`gateways.connection.download.download()` 已覆盖 http/https/ftp/s3/file 与 md5/sha256/size 校验、断点续传、代理与 SSL 配置（`context.ssl_verify` 等）。

**示例 A（可运行）**：

```python
from conda.gateways.connection.download import download

download(
    "https://repo.anaconda.com/pkgs/main/noarch/reprec_test_data-1.0-0.tar.bz2",
    target_full_path=r"D:\tmp\demo.tar.bz2",
    sha256=None,
)
```

**步骤 B（自定义协议更可控）**：实现 `DirectDownloadAdapter` 协议或继承适配器挂到 `CondaSession`。

**示例 B（示意）**：

```python
from conda.gateways.connection.session import CondaSession
# DirectDownloadAdapter 协议声明 direct_download(url, fileobj, progress_callback=None, size=None)
class MyAdapter:                      # 示意：真实实现需继承 BaseAdapter 并实现 send()
    def direct_download(self, url, fileobj, progress_callback=None, size=None):
        ...  # 直写 fileobj
```

**预期结果**：A 能直接落盘并自动校验；B 走 `download_inner` 里的 `isinstance(adapter, DirectDownloadAdapter)` 分支，绕开标准流式缓冲（参照 `S3Adapter.direct_download` 的实现）。

---

**上一章**：[05-key-apis.md](05-key-apis.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[07-faq.md](07-faq.md)