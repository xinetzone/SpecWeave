---
title: wechat-mp-content-archiver Task 14 验收证据包索引
source: .trae/specs/wechat-mp-content-archiver/tasks.md（Task 14 / TR-14.2）
generated: 2026-09-28
---

# 验收证据包（Task 14）

本目录是 TR-14.2 要求的**验收证据包**，覆盖 Task 14 所引用的验收条件
AC-4 / AC-5 / AC-6 / AC-7 / AC-8 / AC-9 / AC-17。

## 文件索引

| 文件 | 对应要求 | 内容 |
|---|---|---|
| [acceptance-evidence.md](acceptance-evidence.md) | TR-14.2 | **证据包正文**：逐条 AC 的 Given/When/Then 对照、断言期望值与实测值对照表、结论与挂起项 |
| [e2e-acceptance.txt](e2e-acceptance.txt) | TR-14.2 | AC-4/5/6/7/8 端到端用例的命令级原始输出（6 例逐例 PASSED）与用例↔AC 对照 |
| [pytest-coverage.txt](pytest-coverage.txt) | TR-14.1 | 全仓库 pytest 原始输出（`302 passed`）与逐模块覆盖率表（TOTAL 96%） |
| [credential-scan.txt](credential-scan.txt) | TR-14.1 / AC-9 | `git ls-files` 与 `git grep` 凭证扫描原始输出 |

## 复现命令

以下命令均在 `apps/dev-tools/wechat-mp-archiver` 目录、PowerShell 7.4+ 下执行
（`git` 不在本机 shell PATH 上，凭证扫描用 `D:\Program Files\Git\mingw64\bin\git.exe`）。

```powershell
# 1) 端到端验收（AC-4/5/6/7/8）——注意 addopts="-q" 会抵消 -v，需用 -o addopts="" 还原逐例清单
.venv\Scripts\python.exe -m pytest tests/test_acceptance_e2e.py -v -o addopts="" --no-header

# 2) 全仓库 pytest + 覆盖率（TR-14.1）
$env:COVERAGE_FILE="$env:TEMP\mp14.coverage"     # 落在系统临时目录，避免污染仓库
.venv\Scripts\python.exe -m pytest --cov=src/mp_archiver --cov-report=term-missing

# 3) 凭证扫描（AC-9）
& "D:\Program Files\Git\mingw64\bin\git.exe" ls-files apps/dev-tools/wechat-mp-archiver |
  Select-String -Pattern "\.env$|\.env\.|/data/|\.db$|/archive/|/exports/"
& "D:\Program Files\Git\mingw64\bin\git.exe" grep -n -I -E 'appmsg_token|pass_ticket|app_secret|MCP_TOKEN|EXPORTER_TOKEN|WECHAT_KEY|WXUIN' -- apps/dev-tools/wechat-mp-archiver
```

## 取证纪律

- 所有端到端用例以 `httpx.MockTransport` 路由到内联 fixture，**零真实网络请求**；
  被测入口 `run_pipeline` 与真实 CLI `mp-archiver run --full` 为同一编排函数。
  其中 `test_acceptance_ac7_cli_run_without_credentials_exits_zero` 从 `cli.main` 进入并跑完
  真实两阶段编排（仅补 `client_factory` 的薄转发），用于锁定「整体退出码 0」而非由打印层推论。
- 数据库与归档目录均落 pytest `tmp_path`，取证过程无外部副作用。
- 本机无 Docker/容器运行时、无真实订阅号扫码条件，凡依赖真机的验收点一律**显式挂起**
  而非以推理代替实测，挂起清单见 [acceptance-evidence.md](acceptance-evidence.md) 第 9 节。