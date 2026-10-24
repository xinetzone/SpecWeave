# 守卫实现与夹具

本文件给出把下限写成断言的最小实现骨架，以及源案例中已跑通的夹具期望。

## 1. 断言规则

对每个被扫描的 manifest：

| 条件 | 判定 |
|---|---|
| 目标需求项不存在 | 报错：缺少该构建依赖 |
| 需求项存在但无版本下限 | 报错：未声明版本下限，应写为 `<pkg>>=<floor>` |
| 下限低于门槛 | 报错：下限低于 `<floor>`，并说明驱动能力 |
| 第二声明面缺失 | 报错：缺少该字段，应为 `<floor>` 或哨兵 |
| 第二声明面低于门槛 | 报错：当前值低于 `<floor>` |
| 第二声明面等于哨兵 | 放行（由需求项派生） |
| 全部达标 | 通过 |

> **为什么下限要归一化后再比较？** `0.11`、`0.11.0`、`v0.11` 在语义上等价，字符串比较会把它们判成三个不同值。归一化补位后再比较，才能避免"达标被误报"与"低版本漏报"两种错误。

比较函数的最小形态：

```python
import re

FLOOR = (0, 11)

def parse_version(text: str) -> tuple[int, ...] | None:
    m = re.fullmatch(r"[vV]?([0-9]+(?:\.[0-9]+)*)", text.strip())
    return tuple(int(p) for p in m.group(1).split(".")) if m else None

def normalized(v: tuple[int, ...], width: int) -> tuple[int, ...]:
    return v + (0,) * max(0, width - len(v))

def lower_bound(req: str) -> tuple[int, ...] | None:
    m = re.search(r"(?:>=|==|~=)\s*([0-9][0-9.]*)", req)
    return parse_version(m.group(1)) if m else None

def meets(req: str) -> bool:
    bound = lower_bound(req)
    return bound is not None and normalized(bound, len(FLOOR)) >= normalized(FLOOR, len(bound))
```

断言要输出三类信息：文件相对路径、当前值、门槛值。缺一项，CI 红的时候就得回头翻代码。

## 2. 扫描面：按 `.gitmodules` 判定子模块

脆弱写法：

```python
def is_submodule(project_dir: Path) -> bool:
    return (project_dir / ".git").exists()
```

问题：主仓直接追踪、但目录内残留 `.git` 的路径会被误判成子模块而被静默排除。源案例中 `libs/caffe-ffi`、`libs/demo-ffi` 正是这种情况，扫描面 10 个，漏了 2 个。

稳健写法：从仓库根的 `.gitmodules` 读取声明的 `path`，只排除这些前缀。

```python
import subprocess
from pathlib import Path

def submodule_paths(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "config", "--file", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return []
    return [line.split(maxsplit=1)[1].strip() for line in out.stdout.splitlines() if line.strip()]

def is_declared_submodule(root: Path, project_dir: Path, paths: list[str]) -> bool:
    rel = project_dir.relative_to(root).as_posix()
    return any(rel == p or rel.startswith(p.rstrip("/") + "/") for p in paths)
```

前置条件：在 git 仓库内执行；`.gitmodules` 不存在时返回空列表，即"没有子模块可排除"，这比"有目录内 `.git` 就排除"更保守，也更接近事实。

> **为什么不能只信目录结构？** `.git` 的存在只说明"这里曾经或现在是一个仓库边界"，不说明父仓如何追踪它。`.gitmodules` 才是父仓的声明面。

审计动作：

1. 打印扫描到的文件数与完整路径列表
2. 与预期集合（第一方 manifest 全量）对账
3. 逐个目检被排除的路径，确认每个都在 `.gitmodules` 中
4. 记录前后计数差

## 3. 夹具清单与期望

在临时目录搭仓库同形结构，直接调用真实检查器。源案例的六组夹具：

| # | 类别 | 夹具内容 | 期望 |
|---|---|---|---|
| 1 | 负向：低于门槛 | `requires = ["scikit-build-core>=0.10"]`，`minimum-version = "0.10"` | 退出码 1，2 条错误 |
| 2 | 负向：无下限 | `requires = ["scikit-build-core"]` | 退出码 1，1 条错误 |
| 3 | 负向：缺第二声明面 | 有 `>=0.11`，无 `minimum-version` | 退出码 1，1 条错误 |
| 4 | 正向：恰好门槛 | `requires = ["scikit-build-core>=0.11"]`，`minimum-version = "0.11"` | 退出码 0 |
| 5 | 正向：补丁位 + 哨兵 | `requires = ["scikit-build-core>=0.11.0"]`，`minimum-version = "build-system.requires"` | 退出码 0 |
| 6 | 语义：非子模块残留 `.git` | 在 `.gitmodules` 之外建目录并放 `.git` 目录，manifest 合法 | 仍被扫描，退出码 0 |

已观测到的报错原文（源案例）：

```text
[pyproject.toml]
  - [build-system].requires 的 'scikit-build-core>=0.10' 下限低于 0.11（PEP 639 元数据所需）
  - [tool.scikit-build].minimum-version 为 '0.10'，应 >= "0.11" 或 "build-system.requires"
```

```text
  - [build-system].requires 的 'scikit-build-core' 未声明版本下限，应写为 scikit-build-core>=0.11
  - [tool.scikit-build] 缺少 minimum-version，应为 "0.11" 或 "build-system.requires"
```

断言要求：

- 精确退出码（0 或 1），不只看输出里有"错误"字样
- 负向夹具的报错条数与文案片段匹配
- 正向夹具不得有 warning 级"失败"
- 夹具目录内保留相对路径与同级文件，否则检查器的根推导会失配

> **为什么夹具不能只测负向？** 只测红，无法排除"守卫恒红"这种最坏情况。正负双向才能证明它既拦得住也放得过。

## 4. CI 接线核查

```bash
grep -rn 'check_pyproject_style\|check_.*\.py' .github/workflows/
grep -rn 'continue-on-error' .github/
```

三项都要确认：

1. 工作流确实调用该脚本（记录文件与行号）
2. 该步骤没有 `continue-on-error: true`
3. 脚本非零退出会让作业失败

> **为什么"有校验脚本"不等于"有门禁"？** 脚本存在但没人调用，或调用处允许继续，等同于没有断言。下限失真的根因往往不是没写检查，而是检查没有接在会变红的路径上。

## 5. 报告模板

| 项 | 内容 |
|---|---|
| 门槛 | X.Y.Z，来自能力 × 版本矩阵（见 probe-matrix） |
| 声明面 | 实例 N、模板 N、生成器 N、文档 N、配方 N |
| 守卫改动 | 文件路径 + 新增断言摘要 |
| 真实仓结果 | 扫描 N 个，退出码 0 |
| 夹具结果 | 正向 N 组退出 0；负向 N 组退出 1（条数） |
| 扫描面 | 修复前 N → 修复后 N，新纳入路径列表 |
| CI | 工作流文件行号，无 `continue-on-error` |
| 未做 | 提交、推送、跨仓同步（均需单独授权） |
