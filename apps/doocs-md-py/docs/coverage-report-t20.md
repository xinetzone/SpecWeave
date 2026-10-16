---
title: T20 覆盖率门禁与性能基准报告
source: apps/doocs-md-py（spec.md AC-16/NFR-6、tasks.md Task 20；实测于 2026-10-15，Python 3.14.7 / Windows）
---

# T20 覆盖率门禁与性能基准报告

本报告归档 AC-16（覆盖率门槛）与 NFR-6（性能基准）的实测证据，供 TR-20.1 核查。

## 1. 门禁配置（两处，职责不同）

| 位置 | 门槛 | 作用 |
|---|---|---|
| `pyproject.toml` `[tool.coverage.report] fail_under` | 总覆盖率 ≥80% | pytest 运行内快速拦截，失败即非零退出 |
| `scripts/check_coverage.py` | 关键模块 per-module ≥90% | 消费 `--cov-report=json` 产物逐文件判定，是「关键模块 ≥90%」的唯一机械门禁 |

关键模块口径（`scripts/check_coverage.py` 顶部常量，与 AC-16 列举一致）：`render/`、`server/`、`uploaders/`、`mcp_server/` 四个前缀；入口 shim（`__init__.py` / `__main__.py`）不承担逻辑，不纳入判定。

## 2. 实测结果（分支口径 `--cov-branch`）

```
Required test coverage of 80.0% reached. Total coverage: 95.91%
1309 passed in 28.47s
总覆盖率 95.91%（门槛 80%）
关键模块 83/83 达标（门槛 90%）
AC-16 覆盖率门禁通过。
```

- 总覆盖率 **95.91%** ≥ 80%；
- 关键模块 **83/83** 全部 ≥90%，最低为 `render/extensions/alert.py` **90.30%**；
- 全量 ruff 零告警。

## 3. NFR-6 性能基准（`scripts/bench_render.py`，非 CI 红门）

```
[渲染] 样张 102431 字节 / 20 次采样 → P50 220.2ms，P95 355.7ms，MAX 358.3ms；阈值 P95 < 500ms → 达标
[同步] 每轮 100 篇文档 / 10 轮 → P50 7.9ms，P95 22.9ms，MAX 18.7ms；阈值 P95 < 1000ms → 达标
```

渲染样张含全部渲染扩展短样例（frontmatter / TOC / 提示块 / 容器块 / 注音 / 滑块 / Emoji / mermaid / plantuml / infographic / KaTeX / 高亮 / 下划线 / 波浪线 / 上标 / 脚注 / 表格 / 代码高亮），计时段为纯库调用 `render_markdown`；同步段为 `db.push_changes` 对 100 篇约 2KB 文档的批处理（每轮独立临时库，不含迁移耗时）。脚本仅用标准库计时（`time.perf_counter` + `statistics.quantiles`），阈值与样本数集中为模块顶部常量。

## 4. 双平台路径原语

- 本机 Windows：全量 `pytest --cov` 通过（上表）。
- WSL openKylin-3.0：`python3 scripts/check_coverage.py --json coverage.json` 在 Linux 侧消费 Windows 生成的报告（路径为反斜杠）输出同一结论——验证报告路径归一化不依赖平台分隔符。
- 说明：WSL 侧 Python 为 3.12，低于本仓 `requires-python >=3.14`，故 WSL 只跑与包无关的 JSON 消费脚本，未跑全量测试。

## 5. 已知不可达分支（未硬凑覆盖）

| 位置 | 说明 |
|---|---|
| `render/extensions/katex.py:143` | 块公式规则结尾强制 `(?:\n|$)`，显式注释为防御性复核，物理不可达 |
| `render/extensions/component.py:376` | `parse_tag` 入口已守卫 `src[1]` 为大写字母，而 `_read_component_name` 对字词字符必返回非空，`name` 为空分支不可达 |

## 6. 复现命令

```powershell
python -m pytest --cov --cov-report=json:coverage.json
python scripts/check_coverage.py
python scripts/bench_render.py
```
