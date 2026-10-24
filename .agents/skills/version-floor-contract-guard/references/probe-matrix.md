# 探测矩阵：如何实测出真实版本门槛

本文件记录一次已核验的门槛探测，方法可迁移到任何"manifest 声明了最低版本"的依赖。

## 1. 案例背景

- 仓库：`projects/xuanspace`
- 依赖：`scikit-build-core`（PEP 517 构建后端）
- 触发能力：PEP 639 元数据，即 `project.license` 写成 SPDX 字符串（如 `"Apache-2.0"`）并配合 `project.license-files`
- 旧声明：`scikit-build-core>=0.10` 与 `minimum-version = "0.10"`
- 实际门槛：`0.11.0`

## 2. 探测方法

对每个候选版本重复同一套动作：

1. 在隔离环境安装该精确版本。若不想污染主环境，用 `pip download --no-deps` 取轮子后解包，或建临时 venv。
2. 准备最小夹具：一份被解析的 `pyproject.toml`，包含 `[project]` 名、版本、`license` 字段，以及需要的 `license-files`。
3. 调真实消费者：用该版本自带的元数据解析入口解析夹具，而不是执行 `pip show` 或读取模块 `__version__`。
4. 记录每种能力形态的结果，包含异常类型与消息片段。

最小矩阵应同时覆盖成功形态与失败形态，例如：

| 形态 | 夹具 |
|---|---|
| `spdx_str` | `license = "Apache-2.0"`，无 `license-files` |
| `spdx_plus_lf` | `license = "Apache-2.0"` + `license-files = ["LICENSE"]` |
| `legacy_file` | `license = { file = "LICENSE" }` |

并且每个形态都跑两遍：`LICENSE` 文件存在、`LICENSE` 文件缺失。文件缺失分支专门暴露"声明了但打包时找不到"的问题。

## 3. 已核验结果

`scikit-build-core` + PEP 639 能力矩阵（探测环境为 Python 3.14 环境，解析入口为该包 vendored 的 `pyproject_metadata`）：

| 版本 | `spdx_str` | `spdx_plus_lf` | `legacy_file`（有 LICENSE） | 结论 |
|---|---|---|---|---|
| 0.9.10 | FAIL | FAIL | OK | 不接受 SPDX 字符串 |
| 0.10.0 | FAIL | FAIL | OK | 不接受 SPDX 字符串 |
| 0.11.0 | OK | OK | OK | 第一个全绿版本，门槛 |
| 0.11.1 | OK | OK | OK | 上界验证通过 |
| 0.11.2 | OK | OK | OK | 上界验证通过 |
| 1.0.0 | OK | OK | OK | 上界验证通过 |

失败时的典型消息：

```text
ConfigurationError: Field "project.license" has an invalid type,
expecting a dictionary of strings (got "Apache-2.0")
```

文件缺失分支的行为：

- `spdx_plus_lf` 在 `LICENSE` 不存在时报 `Every pattern in "project.license-files" must match at least one file`
- `legacy_file` 在 `LICENSE` 不存在时报 `License file not found ("LICENSE")`

结论：门槛是 `0.11.0`。声明写成 `>=0.11` 或 `>=0.11.0` 都达标（语义等价）；写成 `>=0.10` 则失真。

## 4. 探测中实际踩到的两个坑

### 4.1 内部导入路径不是 API

第一次按记忆导入：

```python
from scikit_build_core.metadata import StandardMetadata
```

结果：

```text
ImportError: cannot import name 'StandardMetadata' from 'scikit_build_core.metadata'
```

`standard_metadata` 同样不存在。真实入口是该包 vendor 的 `pyproject_metadata`。正确做法是先列包内模块再决定入口，或直接走公开构建入口，不猜内部路径。

> **为什么不能靠记忆写探测脚本？** 探测脚本的价值在于"它真的消费了这个版本"。导入路径猜错会立刻报错，尚可见；更危险的是猜对了一个仍存在但语义已变的旧路径，矩阵会显示假绿。

### 4.2 包内 `__version__` 会过期

安装 0.11.2 后读取 `<包>/_version.py`，内容显示：

```text
__version__ = "0.9.1"
```

有效版本应以 `importlib.metadata.version("scikit-build-core")` 或包管理器为准。用模块属性判断版本，会把探测对象标错。

## 5. 迁移到其他生态

同一流程可直接换消费路径：

| 生态 | 隔离安装 | 真实消费者 |
|---|---|---|
| Python 构建后端 | venv + 精确 pin | 该后端解析 `pyproject.toml` 的入口 |
| Node CLI / 库 | `npm pack` 后本地安装 | 该库的配置文件解析或 `--check` 子命令 |
| 容器基础镜像 | 指定 tag 拉取 | 镜像内实际运行的服务启动命令 |
| Python 运行时 | 指定 minor 版本 | 目标脚本/库的真实导入与自检 |

报告时写清：候选版本、安装来源、有效版本确认方式、每条能力的原始消息片段。没有这些，矩阵不可复跑。

## 6. 判定表

| 观测 | 结论 |
|---|---|
| 某个版本所有必需能力全绿，下一个更低版本至少一项红 | 该版本即门槛 |
| 最低全绿版本之上再验一个版本仍全绿 | 边界稳定，可写入断言 |
| 几个版本结果随机波动 | 探测环境不干净或能力依赖外部状态，先复现再下结论 |
| 只有 happy path 全绿、缺失分支未测 | 不足以定门槛，补齐分支 |
| 结果只来自 changelog 或经验 | 不是证据，不能写进完成判据 |
