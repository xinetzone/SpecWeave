---
id: "containers-rule-shared-package"
title: "jpman_common 组内共享包治理规则"
source: "../../shared/pyproject.toml + ../../shared/src/jpman_common/ + ../../client/AGENTS.md#C14"
---
# 规则：jpman_common 组内共享包治理（G1/G2 权威定义）

> 本文件是组级约束 **G1（共享层唯一事实源）** 与 **G2（安装顺序）** 的权威定义。
> 成员文件（client AGENTS C14、builder AGENTS 项目概述）中的相关表述与本文件冲突时，
> 以本文件 + `shared/` 源代码为准。

## 1. 包定位（事实基线）

| 项 | 值 |
|----|----|
| 目录 | `apps/containers/shared/` |
| 发行名 / 版本 | `jpman-common` / 0.1.0 |
| import 名 | `jpman_common` |
| Python | `>=3.14` |
| 构建后端 | scikit-build-core（纯 Python wheel：`wheel.cmake = false`，无 cmake 段；`build-dir = "build/{wheel_tag}"`） |
| 硬依赖 | `invoke>=2.0` |
| 可选依赖 | `[sdk]` → `podman>=5.0.0`（缺失时连接层走 `yield None` 降级语义） |
| 消费者 | jupyter-podman-rootless（`jpman_builder`）与 jupyter-podman-client（`jpman_client`），两端 pyproject 均声明 `dependencies = ["jpman-common"]` |

## 2. 模块边界（什么该进 shared，什么不该）

`src/jpman_common/` 现有 5 个模块 + 测试：

| 模块 | 职责 | 备注 |
|------|------|------|
| `connection.py` | **podman SDK 连接层唯一事实源**：`get_client()` 上下文管理器、`sdk_base_url_candidates`、`host_runtime_uid`、`podman_sock_path`、`ensure_host_podman_socket`、`sdk_available`、`APIError`/`PodmanNotFound` 再导出等 | **全组唯一允许 `import podman` 的模块**（经 `[sdk]` extra 可选安装） |
| `platform_paths.py` | 跨平台路径：`to_posix_path` / `normalize_path_str` | Dimension A（卷挂载路径） |
| `proc.py` | 进程执行与运行时探测：`run_cmd` / `detect_runtime` / `check_runtime_ready` / `generate_random_string` | |
| `containers.py` | **只读**容器状态探测（CLI 路径）：`container_exists` / `container_running` | 仅 `ps --filter`，无任何写操作 |
| `_win32_transcode.py` | Windows 输出转码（UTF-16 LE 等） | |

**准入判据（全部满足才可放入 shared）**：

1. 两端（builder + client）存在实际调用方，或属于连接层/只读工具的自然组成
2. 零栈知识：不出现 quant / xmnn / monetize 或任一具体工作负载栈的常量、路径、任务名
3. 无写操作编排（启停/构建/栈编排属成员任务层，不进 shared）
4. 不依赖成员包（shared 不得 import `jpman_builder` / `jpman_client`，依赖方向只能单向向上）

**明确不属于 shared 的易错点**：

- `ContainerConfig`（rootless 三必需的数据载体）定义在消费端
  [client/src/jpman_client/tasks/utils.py](../../client/src/jpman_client/tasks/utils.py)，
  **不在** `jpman_common/containers.py`——后者只有只读探测两个函数。引用时不得张冠李戴。
- 工作负载栈编排内核 `overlay_core.py`、`StackSpec` 属 client 任务层（栈消费者仅 client 一端）。
- rootless 三必需的**代码事实源**有三处（构建端 manage.py、消费端 ContainerConfig、三栈公共
  base-rootless.yaml），shared 不持有该配置；G3 契约的索引在组级 AGENTS.md。

## 3. 垫片消费契约（两端如何使用 shared）

- 消费端：`client/src/jpman_client/tasks/client_core.py` 再导出连接层符号；`utils.py`
  再导出通用能力并保留 client 专属（ContainerConfig / 透传 spec / WSL 桥接等）。
- 构建端：`jupyter-podman-rootless/src/jpman_builder/tasks/client.py` 再导出连接层符号，
  并保留 builder 专属的 `compose_available` / `compose_unavailable_reason`（ntpath 特判）
  与 `sdk_run_kwargs` / `sdk_build_kwargs`。
- **禁止复制实现**：成员包需要连接层/只读工具时只能再导出或直接 import `jpman_common`；
  发现重复实现一律抽回 shared（对照根仓库 check-duplication 纪律）。
- 成员专属差异保留在成员侧，不得为消除差异而把单端逻辑灌入 shared（违反准入判据 1）。

## 4. 安装与开发顺序（G2）

```bash
cd apps/containers
pip install -e shared                 # 必须先装；两端依赖名 jpman-common 由本地 editable 提供
pip install -e jupyter-podman-rootless   # 构建端（按需 extras: [sdk]/[compose]/[full]/[model]）
pip install -e client                    # 消费端（按需 [compose] 启用工作负载栈）
```

- 三成员均为 src 布局 + scikit-build-core，editable 安装；构建产物入各成员 `build/` 目录，不得入库。
- shared 自身测试：`cd shared && pytest`（testpaths=tests；conftest + connection/containers/platform_paths/proc/win32_transcode 五个测试模块，daemon-free）。

## 5. 变更回归纪律（修复即闭环的组级具体化）

修改 `shared/` 任何公开符号（`__init__.py` 的 `__all__` 与 `connection.py` 导出面）时：

1. **双端回归**：必须在 `shared/tests/` 补/改测试，并分别在 builder 与 client 两端跑通
   各自 `tests/`（垫片再导出面断裂会静默退化为成员内本地实现）。
2. **导出面登记**：新增公开 API 必须同步 `jpman_common/__init__.py` docstring 与
   `__all__`（连接层符号经 `connection.py` 自身导出面管理）。
3. **可选依赖守卫**：新增 podman 符号必须保证未装 `[sdk]` 时 import 顶层包不报错
   （延迟 import / 降级语义不回退）。
4. **文档同步**：行为变更同步本文件 §2 模块表；影响安装/连接排障的，同步两端 docs 与
   组级 `docs/01-getting-started.md`；按 G4 禁止把成员文档复制进组层。
5. **单向依赖守卫**：PR 中出现 shared 反向 import 成员包或栈常量，直接打回。

## 6. 反模式

- ❌ 在 client 或 builder 任务模块直接 `import podman` 新写连接分支（必须经 connection.py）。
- ❌ 把 quant/xmnn/monetize 的 compose 路径、端口、镜像名下沉到 shared"方便复用"。
- ❌ 先装 client 后装 shared，靠 PYTHONPATH 偶然命中（G2 安装顺序）。
- ❌ 为 shared 引入第三个消费者之外的用途而不加准入论证（如被 apps/ 其它分组直接依赖——
  届时应先升级为 apps 级共享资产，而非原地扩张）。
