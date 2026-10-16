---
id: "doocs-md-py-rule-engineering-redlines"
title: "工程红线、依赖白名单与质量门禁"
source: "../../AGENTS.md#P0 约束速览"
---

# 工程红线、依赖白名单与质量门禁

> **适用范围**：新增依赖、改构建后端、改覆盖率门槛、新增文件命名、跨平台与落盘位置等工程侧改动。
> **权威事实源**：[../../pyproject.toml](../../pyproject.toml)（构建后端 / 依赖 / ruff / 覆盖率门禁的唯一事实源）、[../../scripts/check_coverage.py](../../scripts/check_coverage.py)、[../../tests/test_no_future_annotations.py](../../tests/test_no_future_annotations.py)。
> 父级规范回退：[../../../../AGENTS.md](../../../../AGENTS.md)（开发规范：提交规范、路径引用、Mermaid、修复闭环）。

## §1 运行时与语法红线

- **Python 版本下限 `>=3.14`**，由 `pyproject.toml` 的 `requires-python` 声明；代码与测试均以 3.14 为运行基线。
- **禁止 `from __future__ import annotations`（PEP 563）**。理由：3.14 起 PEP 649 默认惰性注解，该 import 冗余且语义有别。
  - 机械拦截位点：[../../tests/test_no_future_annotations.py](../../tests/test_no_future_annotations.py)（AST 守护测试）。**新增或修改 Python 文件后必须保证该测试为绿**。
  - 相关陷阱：移除该 import 后，**类体内自引用注解**会在类体执行期触发 `NameError`（类名尚未绑定）；**模块级注解引用的类型**必须顶层直接导入（不得只放 `TYPE_CHECKING` 块）。若确需延迟求值，须用导入时版本守卫规避，并配套注释说明。
- **泛型书写**：3.14 直接使用内置泛型（`list[str]`、`dict[str, Any]`），无需 `typing.List` 等兼容写法（本项目不承担 3.8/3.9 兼容目标）。

## §2 依赖白名单与克制

- 运行期依赖**白名单**（共 8 项）：`fastapi`、`uvicorn`、`python-multipart`、`markdown-it-py`、`nh3`、`PyJWT`、`httpx`、`pyyaml`。**不含 `mcp`** —— stdio JSON-RPC 2.0 传输层与 13 工具注册表为**本仓手写**（`mcp_server/stdio.py`、`mcp_server/tools.py`）；`mcp` 2.3.0 对 Python 3.14 不兼容，已按 [../../docs/contract-differences.md](../../docs/contract-differences.md) 的 `CD-21` 删除该依赖（口径以 [../../pyproject.toml](../../pyproject.toml) 为唯一事实源）。
- **签名与加密一律标准库手写**（`hmac`/`hashlib`/`base64` 等），**禁止引入 `boto3`、`cryptography`** —— 前者体积与动机不符，后者与"标准库自足"原则冲突，且替换会破坏已验证的测试向量（见 [uploaders-dual-path.md](uploaders-dual-path.md) §3）。
- **FastAPI 结构化请求参数强约束**：凡使用 `Form()` / `File()` / `UploadFile` 的路由，其所需依赖（如 `python-multipart`）必须**在 `pyproject.toml` 显式声明**。历史教训：依赖缺失在洁净环境注册路由时抛 `RuntimeError`，而旧环境因间接依赖侥幸通过。**配套要求：静态门禁测试**防止漏声明。
- **新增依赖的判定**：默认答案是"不新增"。提出者必须回答：
  1. 标准库能否实现（能则不得引入）；
  2. 现有白名单依赖能否覆盖（能则不得引入）；
  3. 体积 / 许可 / 供应链风险是否可接受；
  4. 是否可用**测试向量**证明替换不改变已验证行为。
  未通过上述四问的依赖一律拒绝。

## §3 scikit-build-core 构建后端

- 主仓主权区 Python 子项目**默认统一使用 scikit-build-core** 作为 PEP 517 构建后端。本应用的 `pyproject.toml` 必须声明：

  ```
  [build-system]
  requires = ["scikit-build-core>=0.9"]
  build-backend = "scikit_build_core.build"
  ```

  并在 `[tool.scikit-build]` 下声明 `wheel.packages`、`build-dir = "build/{wheel_tag}"`、`minimum-version = "0.9"`。
- 本应用为**纯 Python 包**（无原生扩展、无 `CMakeLists.txt`），因此**不写 `[tool.scikit-build.cmake]` 段**。
- 包名 `doocs_md_py`；控制台脚本名 `mdpy`。改名等同契约变更，须先更新 [../../README.md](../../README.md) 与 [../../docs/architecture.md](../../docs/architecture.md)。
- **禁止**改用 setuptools / pdm 后端（豁免场景仅限 `vendor/` 第三方与已发布到 PyPI 的外部项目，本应用不属于其列）。

## §4 命名、元数据与溯源

- 文件名 **kebab-case、纯英文**，禁止中文字符；新增后运行 `python .agents/scripts/check-filename-convention.py` 自检。
- Markdown frontmatter 统一 **YAML（`---` 包裹）**，遵循 MDI v1.0；**派生产物必须携带 `source` 字段**标注来源（本目录各规则文件的 `source` 指向 [../../AGENTS.md](../../AGENTS.md) 对应锚点）。
- 文档交叉引用**一律相对路径**，禁止 `file:///` 绝对路径；**禁止引用 `.temp/` 内任何路径**（按保留期自动清理，引用必然失效）。
- 项目根目录**不得新增散落文件**；新文件先确定归属目录（本应用内：`src/` / `tests/` / `scripts/` / `docs/` / `.agents/`）。

## §5 测试与覆盖率双门禁

- 两处门禁**同时生效**，缺一不可：
  1. **总覆盖率 ≥ 80%** —— 由 `pyproject.toml` 的 `[tool.coverage.report] fail_under` 强制；
  2. **关键模块 per-module ≥ 90%** —— 由 [../../scripts/check_coverage.py](../../scripts/check_coverage.py) 强制。
- 关键模块口径（模块前缀四选一）：`render/`、`server/`、`uploaders/`、`mcp_server/`。**入口 shim 不纳入**关键模块口径（如 `__main__.py`、CLI 薄封装）。
- 复现基线（历史实测，仅作参照，**以当次实跑为准**）：总覆盖率 95.91%；关键模块 83/83 达标（最低约 90.30%）。详见 [../../docs/coverage-report-t20.md](../../docs/coverage-report-t20.md)。
- **禁止**为达标而降低阈值、扩大排除清单，或把关键模块挪出入口口径。放宽门槛属于口径级变更（同 §3 的"改名"级别），须用户批准。

## §6 静态检查与平台约束

- **ruff 零告警**为提交前提；ruff 版本在 `pyproject.toml` 固定（避免规则集漂移使门禁意外变红）。修复按安全分级：无歧义规则自动修复优先；语义相关改动逐行人工验证，避免悬空引用。
- **Windows 平台事项**：
  - 所有 `.ps1` 脚本须用 **PowerShell 7.4+（pwsh7）** 执行，**禁止 Windows PowerShell 5.1**（`vendor/`、`projects/` 豁免）；
  - 本机 PATH 被裁剪，调用 `wsl` / `podman` / `ssh` / `git` 等外部命令**必须使用全路径**（如 `D:\Program Files\Git\mingw64\bin\git.exe`、`$env:WINDIR\System32\OpenSSH\ssh.exe`）。
- **跨平台路径原语**：生产代码与测试统一使用 `os.path` / `pathlib` 原语；**测试侧禁止硬编码固定盘符路径**（历史教训：测试侧 POSIX 路径硬编码导致平台性失败，且修复时**只允许改测试期望**，不得改生产代码逻辑）。
- **大体积落盘纪律**（C/D 盘紧张）：
  - 依赖安装、前端构建产物、模型权重等大体积内容优先放 `/mnt/ai`（openKylin WSL2 内 drvfs 挂载）；
  - 使用前**必须验证挂载**：确认 mount 表存在且 `ls /mnt/ai | wc -l` > 0（断连时呈现空目录）；
  - **禁止**因 WSL 根分区 `df` 显示容量大而把大文件写入 WSL 根（其写入上限受宿主盘空闲约束）；
  - 代码工作仍在仓库本体 `d:\AI` 内进行，版本控制与项目结构不迁移。

## §7 反模式（出现即打回）

| # | 反模式 | 后果 |
|---|--------|------|
| A1 | 引入 `from __future__ import annotations` | AST 守护测试变红，违反技术红线 |
| A2 | 引入 `boto3` / `cryptography` 或其它白名单外依赖而不走四问 | 供应链与体积失控 |
| A3 | 用 `Form()`/`File()` 却未在 `pyproject.toml` 声明相应依赖 | 洁净环境启动即 `RuntimeError` |
| A4 | 为凑覆盖率而降低阈值 / 扩大排除 / 挪出入口口径 | 门禁失去意义 |
| A5 | 测试中硬编码盘符或 POSIX 路径串 | 跨平台失败，且诱发"改生产代码"的错误修复 |
| A6 | 在 WSL 根分区或 C/D 盘放大体积中间产物 | 磁盘告警，且违反存储偏好 |
| A7 | 中文文件名 / 非 kebab-case / 缺 `source` 溯源 | 命名与元数据门禁失败 |

## 变更纪律

- 本文档只增不删；依赖白名单、构建后端、覆盖率门槛三者变更均属**口径级变更**，须用户批准并同步 [../../pyproject.toml](../../pyproject.toml)、[../../README.md](../../README.md) 与 [../CHANGELOG.md](../CHANGELOG.md)。
