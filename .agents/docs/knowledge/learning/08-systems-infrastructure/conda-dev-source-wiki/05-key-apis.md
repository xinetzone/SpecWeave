---
id: conda-dev-source-wiki-05-key-apis
title: "关键 API 使用方法"
source: "spec:create-conda-dev-source-wiki-tutorial"
category: "learning"
tags: [conda, api, matchspec, channel, prefixdata, subdirdata, context, history, exports]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "基于真实源码讲解 conda.api、MatchSpec/Channel/Version、核心数据类、Context、History、exports 与 conda-docs 的用法与签名。"
---

# 关键 API 使用方法

本章聚焦 conda 可编程接口。所有签名均取自当前仓库真实源码。

> ⚠️ **重要变化**：当前版本的 `conda/api.py` 已不再包含历史上的 `create()`/`install()`/`remove()`/`update()` 顶层函数（上一代公开 API）。`conda.api` 现在只暴露 4 个 **Beta** 类：`Solver`、`SubdirData`、`PackageCacheData`、`PrefixData`，它们是 `conda.core.*` 内部实现的薄封装。命令式安装/删除逻辑移到了 CLI 层（见 1.2）。

## 1. `conda.api` —— 高层求解与数据访问

### 1.1 `Solver`（Beta）

`conda.api.Solver` 是求解逻辑的高层入口，内部委托给 `context.plugin_manager.get_cached_solver_backend()`（默认为 `conda.core.solve.Solver`）。

```python
class Solver:
    def __init__(self, prefix, channels, subdirs=(), specs_to_add=(), specs_to_remove=()):
        ...
    def solve_final_state(self, update_modifier=NULL, deps_modifier=NULL,
                          prune=NULL, ignore_pinned=NULL, force_remove=NULL):
        ...
    def solve_for_diff(self, update_modifier=NULL, deps_modifier=NULL, prune=NULL,
                       ignore_pinned=NULL, force_remove=NULL, force_reinstall=False):
        ...
    def solve_for_transaction(self, update_modifier=NULL, deps_modifier=NULL, prune=NULL,
                              ignore_pinned=NULL, force_remove=NULL, force_reinstall=False):
        ...
```

三个方法的区别：`solve_final_state` 返回最终状态的 `tuple[PackageRef]`；`solve_for_diff` 返回 `(待移除, 待新增)` 二元组；`solve_for_transaction` 返回可直接 `execute()` 的 `UnlinkLinkTransaction`。

```python
from conda.api import Solver
from conda.base.context import context

prefix = context.conda_prefix
solver = Solver(prefix, channels=tuple(context.channels), subdirs=(context.subdir,),
                specs_to_add=("python=3.11",))
txn = solver.solve_for_transaction()
txn.print_transaction_summary()
# 示意：正式执行需 txn.download_and_extract() 后 txn.execute()
```

### 1.2 命令式安装的真实位置

`create/install/update` 共享同一个核心函数：

```python
# conda/cli/install.py
def install(args, parser, command="install"): ...
```

`command` 取值 `"create" | "install" | "update"`，通过 `Environment.from_cli_with_file_envs(...)` 解析 specs，向 `context.plugin_manager.get_cached_solver_backend()` 传参，最终 `handle_txn(...)` 执行事务。`remove` 则走 `conda/cli/main_remove.py::execute(args, parser)`。程序化调用时通常通过 `conda.cli.main_*` 的 `execute()` 或 `conda run` 子进程实现，而非旧的 `conda.api.create()`。

### 1.3 三个数据访问封装（Beta）

```python
from conda.api import SubdirData, PackageCacheData, PrefixData

sd = SubdirData("https://repo.anaconda.com/pkgs/main/linux-64")  # 必须带 subdir
recs = sd.query("python>=3.11")        # -> tuple[PackageRecord]
recs = SubdirData.query_all("numpy", channels=None, subdirs=None)  # 跨所有频道/subdir

pcd = PackageCacheData.first_writable()  # -> PackageCacheData
hit = pcd.get(some_package_ref, default=None)  # -> PackageCacheRecord

pd = PrefixData("/path/to/env")
recs = pd.query("numpy")                # -> tuple[PrefixRecord]
for rec in pd.iter_records():
    print(rec.name, rec.version)
```

## 2. `MatchSpec` / `Channel` / `Version`

### 2.1 MatchSpec —— conda 的包查询语言

```python
# conda/models/match_spec.py
class MatchSpec(metaclass=MatchSpecType):
    FIELD_NAMES = ("channel", "subdir", "name", "version", "build", "build_number",
                   "track_features", "features", "url", "md5", "sha256", "license",
                   "license_family", "fn", "when", "extras", "flags")
    def __init__(self, optional=False, target=None, **kwargs): ...
    def match(self, rec: PackageRecord | dict) -> bool: ...
    def get(self, field_name, default=None): ...
    def get_exact_value(self, field_name): ...
    @classmethod
    def merge(cls, match_specs, union=False): ...
    @classmethod
    def from_dist_str(cls, dist_str): ...
```

```python
from conda.models.match_spec import MatchSpec

ms = MatchSpec("conda-forge::python>=3.9,<3.12")
print(ms.name, ms.get("version"))   # python >=3.9,<3.12
print(str(ms))                       # 规范化的字符串

rec = {"name": "python", "version": "3.11.8", "build": "hb_child_0"}
print(MatchSpec("python>=3.9").match(rec))   # True
print(MatchSpec("python==3.10").match(rec))  # False
```

### 2.2 Channel —— 频道对象

```python
# conda/models/channel.py
class Channel:
    def __init__(self, scheme=None, auth=None, location=None, token=None,
                 name=None, platform=None, package_filename=None): ...
    @staticmethod
    def from_url(url: str) -> Channel: ...
    @staticmethod
    def from_value(value: str | None) -> Channel: ...
    @property
    def canonical_name(self) -> str: ...
    @property
    def subdir(self) -> str | None: ...      # 即 platform
    def url(self, with_credentials: bool = False) -> str | None: ...
```

```python
from conda.models.channel import Channel, get_channel_objs

c = Channel("conda-forge/linux-64")
print(c.canonical_name, c.subdir)  # conda-forge linux-64

from conda.base.context import context
for ch in get_channel_objs(context):
    print(ch.canonical_name, ch.base_url if hasattr(ch, "base_url") else ch.urls())
```

### 2.3 Version —— 版本解析与比较

```python
# conda/models/version.py
def normalized_version(version: str) -> VersionOrder: ...
class VersionOrder(metaclass=SingleStrArgCachingType):
    def __init__(self, vstr: str): ...
    def startswith(self, other) -> bool: ...
class VersionSpec(BaseSpec):
    def __init__(self, vspec): ...
class BuildNumberMatch(BaseSpec):
    def __init__(self, vspec): ...
```

```python
from conda.models.version import VersionOrder, VersionSpec, normalized_version

print(VersionOrder("1.10") > VersionOrder("1.9"))  # True（分段比较，非字符串比较）
print(normalized_version("1.0.0rc1"))
print(VersionSpec(">=1.5,<2.0").match("1.9.2"))
```

## 3. 核心数据类（`conda.core.*`）

### 3.1 PrefixData —— 已安装前缀

```python
# conda/core/prefix_data.py
class PrefixData(metaclass=PrefixDataType):
    def __init__(self, prefix_path, pip_interop_enabled=None): ...
    @classmethod
    def from_name(cls, name: str, **kwargs) -> PrefixData: ...
    def get(self, package_name: str, default=NULL): ...           # -> PrefixRecord
    def iter_records(self) -> Iterable[PrefixRecord]: ...
    def iter_records_sorted(self): ...
    def query(self, package_ref_or_match_spec): ...
    def get_conda_packages(self) -> list[PrefixRecord]: ...
    def get_python_packages(self) -> list[PrefixRecord]: ...
    def get_environment_env_vars(self) -> dict: ...
    def set_environment_env_vars(self, env_vars): ...
    def get_pinned_specs(self) -> tuple[MatchSpec]: ...
    def is_writable(self) -> bool | None: ...
```

```python
from conda.core.prefix_data import PrefixData
pd = PrefixData(context.conda_prefix)
print(sorted(r.name for r in pd.iter_records()))
print(pd.get("python").version)
```

### 3.2 SubdirData —— 频道子目录 repodata

```python
# conda/core/subdir_data.py
class SubdirData(metaclass=SubdirDataType):
    def __init__(self, channel: Channel, repodata_fn="repodata.json", ...): ...
    @staticmethod
    def query_all(package_ref_or_match_spec, channels=None, subdirs=None): ...
    def query(self, package_ref_or_match_spec): ...   # -> tuple[PackageRecord]
    def iter_records(self) -> Iterator[PackageRecord]: ...
    def reload(self): ...
    @property
    def repodata_fn(self): ...
```

```python
from conda.core.subdir_data import SubdirData
from conda.models.channel import Channel
sd = SubdirData(Channel("conda-forge/linux-64"))
print(len(tuple(sd.iter_records())))
print([r.version for r in sd.query("python", exact_name=True) if r.version.startswith("3.11")])
```

### 3.3 PackageCacheData —— 本地包缓存

```python
# conda/core/package_cache_data.py
class PackageCacheData(metaclass=PackageCacheType):
    def __init__(self, pkgs_dir): ...
    def get(self, package_ref: PackageRecord, default=NULL): ...   # -> PackageCacheRecord
    def remove(self, package_ref, default=NULL): ...
    def query(self, package_ref_or_match_spec): ...
    def iter_records(self): ...
    @classmethod
    def query_all(cls, package_ref_or_match_spec, pkgs_dirs=None): ...
    @classmethod
    def first_writable(cls, pkgs_dirs=None): ...
    def get_entry_to_link(self, package_ref): ...
    @property
    def is_writable(self): ...
```

```python
from conda.core.package_cache_data import PackageCacheData
pcd = PackageCacheData.first_writable()
print(pcd.pkgs_dir, pcd.is_writable)
print(len(tuple(pcd.iter_records())))
```

## 4. `Context` —— 全局配置读取

`conda.base.context.Context` 的全局单例 `context` 汇集了 condarc、环境变量与命令行参数解析后的所有配置，以属性方式读取：

```python
from conda.base.context import context

print(context.channels)          # 当前激活的频道列表
print(context.subdir)            # 当前平台，如 linux-64 / osx-arm64 / win-64
print(context.subdirs)           # 优先子目录列表
print(context.target_prefix)     # 本次操作的目标前缀
print(context.root_prefix, context.conda_prefix)  # root 与 base 环境
print(context.pkgs_dirs, context.envs_dirs)
print(context.json, context.quiet, context.dry_run, context.offline)
print(context.ssl_verify)        # True / False / "truststore"
print(context.proxy_servers)     # 代理配置
print(context.solver)            # 求解器后端名
print(context.repodata_use_zst, context.repodata_use_shards)
print(context.remote_max_retries, context.remote_backoff_factor)
```

`context` 的属性值在导入后由 `reset_context()` 初始化（见 `conda/exports.py` 末尾 `reset_context()` 调用），修改环境变量后可调 `reset_context()` 重读。

## 5. `History` —— 环境变更历史

```python
# conda/history.py
class History:
    def __init__(self, prefix: PathType): ...
    def parse(self) -> list[tuple[str, set[str], list[str]]]: ...
    def get_user_requests(self): ...               # 用户请求记录列表
    def get_requested_specs_map(self): ...         # {包名: MatchSpec}
    def get_state(self, rev=-1): ...               # 指定 revision 的包集合
    def construct_states(self): ...
    def object_log(self): ...
    def write_specs(self, remove_specs=(), update_specs=(), neutered_specs=()): ...
    def write_changes(self, last_state, current_state): ...
```

```python
from conda.history import History
h = History(context.conda_prefix)
for item in h.get_user_requests():
    print(item["date"], item.get("cmd"), item.get("action"))
print(h.get_requested_specs_map())
```

## 6. `conda.exports` —— 向后兼容重导出

`conda/exports.py` 顶部注明「Backported exports for conda-build」，为老式脚本提供稳定命名，再从内部模块重导出：

```python
from conda.exports import Channel, MatchSpec, Resolve, VersionOrder, normalized_version
from conda.exports import get_index, package_cache, linked_data, linked, is_linked, download
from conda.exports import context, reset_context
```

注意其中不少符号（如 `Solver`、`CondaError`、`CondaHTTPError`）已用 `deprecated.constant(...)` 标记为待废弃，调用会发出 DeprecationWarning；新代码应直接面向 `conda.api` / `conda.models.*` / `conda.exceptions.*`。`get_index(channel_urls=(), prepend=True, platform=None, use_local=False, use_cache=False, unknown=None, prefix=None)` 返回 `{Dist: PackageRecord}` 字典，是快速本地查询的便捷入口。

## 7. conda-docs 的 Sphinx 构建

conda-docs 仓库（`external/libs/conda-dev/conda-docs`）的文档配置核心在 `docs/source/conf.py`：

- `sys.path.insert(0, os.path.abspath("../.."))` —— 保证 Sphinx 能 import conda。
- `extensions` 注册了 `sphinx.ext.autodoc`、`sphinx.ext.autosummary`、`sphinx.ext.graphviz`、`sphinx.ext.ifconfig`、`sphinx.ext.inheritance_diagram`、`sphinx_sitemap`、`sphinx_design`、`sphinx_reredirects`。
- `html_theme = "conda_sphinx_theme"`；`html_baseurl = "https://docs.conda.io/"`；`redirects` 把旧页面重定向到 `docs.conda.io`。
- `source_suffix = ".rst"`、`master_doc = "index"`、`modindex_common_prefix = ["conda."]`。

构建入口：`docs/Makefile` 的 `SPHINXBUILD = python3 -msphinx`、`SOURCEDIR = source`、`BUILDDIR = build`，`make html` 即可在本地生成 HTML。依赖在 `requirements.txt`（`conda-sphinx-theme==0.4.0`、`sphinx-sitemap`、`sphinx-design`、`sphinx-reredirects`）。CI 走 `.readthedocs.yml`（ubuntu-24.04 / Python 3.14，输出 htmlzip）。

> ⚠️ **事实核查**：任务清单曾提到 `docs/source/_extensions/conda_umls.py` 与 `nav_glossary.py` 两个 Sphinx 扩展。经核对，**当前检出版本的 conda-docs 中不存在 `_extensions/` 目录**，`docs/source/` 下唯一的 Python 文件是 `conf.py`（`nav_glossary`/`conda_umls` 属于 conda 官方文档的其它历史分支/衍生仓库，不在本仓库内）。因此本文不臆造这两个文件的函数名与签名，后续若需要可另行核对对应分支。

---

**上一章**：[04-gateways-plugins-env.md](04-gateways-plugins-env.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[06-scenarios.md](06-scenarios.md)